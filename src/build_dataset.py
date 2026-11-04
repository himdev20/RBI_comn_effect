"""Merge text scores, votes, decisions and market moves into member-, meeting- and
day-level analysis tables.

Inputs (column specs in DATA_GUIDE.md):
  processed/member_statements.csv, processed/meeting_texts.csv, processed/scores_*.csv
  raw/minutes_urls.csv      meeting_date, release_date, release_after_market, url
  raw/decisions.csv         meeting_date, decision_bp [, repo_after, stance, cpi_surprise, verified]
  raw/dissent_direction.csv optional hand-coding: meeting_date, member, dissent_dir (+1/-1), type (rate|stance)
  raw/resolution_scores.csv optional: meeting_date, hawk_resolution (else processed/scores_llm_resolution.csv)
  raw/market/yields.csv     date + any of config.TENOR_CANDIDATES (percent) + us10y, vix, brent
  raw/market/cpi_release_dates.csv  date

Key measurement choices (see docs/research_design.md):
  * Surprise (default 'gov'): mean hawkishness of the five non-Governor members minus the
    Governor's own minutes statement. Same document genre, and the Governor's view is already
    public on decision day (statement + press conference); what the minutes add is the rest of
    the committee.
  * Explicit dissent: a 'No' vote, a different magnitude in the vote table, or a stance dissent.
    All of this is PUBLIC on decision day (the resolution names dissenters) -- it is a control,
    not news, on minutes day.
  * Hidden dissent: among members who voted with the majority, the LLM 'lean' relative to the
    adopted decision (signed, -1..1) and 'reservation' (share with reservations).
  * Timing: minutes are published at 17:00 IST, when the G-sec market closes, so with
    release_after_market=1 the reaction day is the NEXT trading day. Global controls are
    measured over the same IST close-to-close window (US/Brent/VIX closes fall after the
    Indian close, so the change dated t-1 is the one Indian markets price on day t).
"""
import os
import logging
import numpy as np
import pandas as pd
from src import config

log = logging.getLogger("build")
SCORE_FILES = ["scores_llm", "scores_dictionary", "scores_finbert", "scores_vader"]


# ----------------------------------------------------------------------------- decisions
def load_decisions():
    dec = pd.read_csv(config.DECISIONS_CSV, dtype={"meeting_date": str})
    if "verified" in dec and (dec.verified.fillna(0).astype(int) == 0).any() \
            and not os.environ.get("RBI_ALLOW_UNVERIFIED"):
        bad = dec.loc[dec.verified.fillna(0).astype(int) == 0, "meeting_date"].tolist()
        raise SystemExit(f"decisions.csv has unverified rows {bad[:5]}... Check each against the RBI "
                         "resolution and set verified=1 (or export RBI_ALLOW_UNVERIFIED=1 for a dry run).")
    dec = dec.sort_values("meeting_date").reset_index(drop=True)
    dec["decision_dir"] = np.sign(dec.decision_bp)
    if "repo_after" not in dec or dec.repo_after.isna().all():
        dec["repo_after"] = config.REPO_START + dec.decision_bp.cumsum() / 100.0
    dec["repo_before"] = dec.repo_after - dec.decision_bp / 100.0
    dec["next_meeting_date"] = dec.meeting_date.shift(-1)
    dec["next_decision_bp"] = dec.decision_bp.shift(-1)
    dec["next_decision_dir"] = np.sign(dec.next_decision_bp)
    return dec


def pick_score(st):
    pref = os.environ.get("RBI_SCORE", "hawk_llm")
    for c in [pref, "hawk_llm", "hawk_dict"]:
        if c in st.columns and st[c].notna().any():
            return c
    raise SystemExit("No score column found - run a scorer first.")


# ----------------------------------------------------------------------------- member level
def member_level():
    st = pd.read_csv(config.PROC / "member_statements.csv", dtype={"meeting_date": str})
    for f in SCORE_FILES:
        p = config.PROC / f"{f}.csv"
        if p.exists():
            st = st.merge(pd.read_csv(p).drop(columns=["llm_model"], errors="ignore"), on="statement_id", how="left")
    col = pick_score(st)
    st["hawk"] = st[col].astype(float)
    dec = load_decisions()
    st = st.merge(dec[["meeting_date", "decision_bp", "decision_dir"]], on="meeting_date", how="left")
    for c in ["vote_yes", "vote_bp", "stance_vote_yes", "lean_llm", "reservation_llm", "pref_action_llm"]:
        if c not in st:
            st[c] = np.nan

    # --- explicit dissent (public on decision day)
    st["vote_bp_signed"] = st.vote_bp * st.decision_dir
    maj = st.groupby("meeting_date").vote_bp_signed.transform("median")
    mag = (st.vote_yes == 1) & st.vote_bp.notna() & (st.vote_bp_signed != maj)
    mag_dir = np.sign(st.vote_bp_signed - maj).where(mag)
    hand = pd.read_csv(config.DISSENT_CSV, dtype={"meeting_date": str}) if config.DISSENT_CSV.exists() else \
        pd.DataFrame(columns=["meeting_date", "member", "dissent_dir", "type"])
    if "type" not in hand:
        hand["type"] = "rate"
    hand["type"] = hand["type"].fillna("rate")
    for typ in ["rate", "stance"]:
        h = hand[hand.type == typ][["meeting_date", "member", "dissent_dir"]].rename(columns={"dissent_dir": f"hand_{typ}"})
        st = st.merge(h, on=["meeting_date", "member"], how="left")
    rate_no = st.vote_yes == 0
    llm_rate_dir = np.sign(st.pref_action_llm - st.decision_dir)
    rate_dir = st.hand_rate.where(st.hand_rate.notna(), llm_rate_dir).where(rate_no)
    stance_dis = (st.stance_vote_yes == 0) | st.hand_stance.notna()
    stance_dir = st.hand_stance.where(st.hand_stance.notna(), st.lean_llm).where(stance_dis)
    st["explicit_dissent"] = (rate_no | mag | stance_dis).astype(int)
    st["explicit_dir"] = rate_dir.fillna(mag_dir).fillna(stance_dir)
    st["dissent_kind"] = np.select([rate_no, mag, stance_dis], ["rate", "magnitude", "stance"], "")

    # --- hidden dissent: members who voted with the majority on everything
    yes_clean = (st.vote_yes == 1) & (st.explicit_dissent == 0)
    if st.lean_llm.notna().any():
        st["hidden_lean"] = st.lean_llm.where(yes_clean)
        st["hidden_res"] = (st.reservation_llm >= 1).astype(float).where(yes_clean & st.reservation_llm.notna())
        st.attrs["hidden_source"] = "llm"
    else:   # fallback without LLM: deviation from the Governor's statement on the dictionary scale
        gov = st[st.governor == 1].set_index("meeting_date").hawk
        dev = st.hawk - st.meeting_date.map(gov)
        thr = float(os.environ.get("RBI_HIDDEN_THR", 0.75))
        st["hidden_lean"] = (np.sign(dev) * (dev.abs() >= thr)).where(yes_clean & (st.governor == 0))
        st["hidden_res"] = (dev.abs() >= thr).astype(float).where(yes_clean & (st.governor == 0))
        st.attrs["hidden_source"] = f"FALLBACK_dict_dev_from_governor_thr{thr}"
    # --- legacy say-vote gap (kept for comparison with Trivedi & Ghosh 2025; mixes scales)
    st["vote_hawk"] = st.decision_dir + st.explicit_dir.fillna(0) * (st.explicit_dissent == 1)
    st["say_vote_gap"] = st.hawk - st.vote_hawk
    st.to_csv(config.PROC / "member_level.csv", index=False)
    return st, col, dec


# ----------------------------------------------------------------------------- meeting level
def meeting_level(st, dec):
    g = st.groupby("meeting_date")
    m = g.agg(mean_hawk=("hawk", "mean"), sd_hawk=("hawk", "std"), n_members=("member", "count"),
              n_dissent=("explicit_dissent", "sum"), hidden_signed=("hidden_lean", "mean"),
              hidden_share=("hidden_res", "mean"), mean_gap=("say_vote_gap", "mean")).reset_index()
    m["dissent_signed"] = g.explicit_dir.sum(min_count=1).reindex(m.meeting_date).fillna(0).values
    ng, gv = st[st.governor == 0], st[st.governor == 1]
    add = {"hawk_gov": gv.groupby("meeting_date").hawk.mean(),
           "mean_hawk_exgov": ng.groupby("meeting_date").hawk.mean(),
           "hawk_int_exgov": ng[ng.member_type == "internal"].groupby("meeting_date").hawk.mean(),
           "hawk_external": st[st.member_type == "external"].groupby("meeting_date").hawk.mean(),
           "hawk_dgmp": st[st.role == "DG_MP"].groupby("meeting_date").hawk.mean()}
    for c in ["unc_llm", "cond_llm", "next_move_llm", "sent_vader", "hawk_dict"]:
        if c in st:
            add[f"mean_{c}"] = st.groupby("meeting_date")[c].mean()
    for k, v in add.items():
        m[k] = m.meeting_date.map(v)
    m["surprise_gov"] = m.mean_hawk_exgov - m.hawk_gov
    m["surprise_int"] = m.hawk_int_exgov - m.hawk_gov
    m["surprise_ext"] = m.hawk_external - m.hawk_gov
    res = None
    if config.RESOLUTION_CSV.exists() and len(pd.read_csv(config.RESOLUTION_CSV)):
        res = pd.read_csv(config.RESOLUTION_CSV, dtype={"meeting_date": str})
    elif (config.PROC / "scores_llm_resolution.csv").exists():
        res = pd.read_csv(config.PROC / "scores_llm_resolution.csv", dtype={"meeting_date": str})
    if res is not None:
        m = m.merge(res, on="meeting_date", how="left")
        m["surprise_res"] = m.mean_hawk - m.hawk_resolution
    m = m.sort_values("meeting_date").reset_index(drop=True)
    m["surprise_roll"] = m.mean_hawk - m.mean_hawk.shift(1).rolling(4, min_periods=2).mean()
    choice = os.environ.get("RBI_SURPRISE", "gov")
    if choice == "gov" and m.surprise_gov.notna().mean() < 0.8:
        log.warning("Governor statement missing for >20%% of meetings; falling back to 'res'/'roll'")
        choice = "res" if "surprise_res" in m else "roll"
    if choice == "res" and "surprise_res" not in m:
        choice = "roll"
    m["surprise"] = m[f"surprise_{choice}"]
    m["surprise_type"] = {"gov": "exgov_members_minus_governor", "res": "members_minus_resolution",
                          "roll": "FALLBACK_minutes_minus_prior4_mean"}[choice]
    m["hidden_source"] = st.attrs.get("hidden_source", "")
    urls = pd.read_csv(config.URLS_CSV, dtype=str)
    m = m.merge(urls[["meeting_date", "release_date", "release_after_market"]], on="meeting_date", how="left")
    m = m.merge(dec, on="meeting_date", how="left")
    # next meeting's explicit dissent (from minutes of the next meeting, if parsed)
    nd = st.groupby("meeting_date").explicit_dissent.sum()
    m["next_n_dissent"] = m.next_meeting_date.map(nd)
    return m


# ----------------------------------------------------------------------------- market
def _asof(series, dates):
    """Value of a (date-indexed, sorted) series as of each date (last obs on or before)."""
    s = series.dropna()
    idx = s.index.searchsorted(pd.DatetimeIndex(dates), side="right") - 1
    vals = np.where(idx >= 0, s.values[np.clip(idx, 0, None)], np.nan)
    return pd.Series(vals, index=pd.DatetimeIndex(dates))


def _reaction_day(cal, d, after):
    pos = cal.searchsorted(pd.Timestamp(d), side="right" if after else "left")
    return cal[pos] if pos < len(cal) else pd.NaT


def daily_panel():
    """Daily close-to-close changes on the Indian trading calendar.
    Yields -> bp; price series (config.RETURN_SERIES) -> 100 x log change (percent)."""
    y = pd.read_csv(config.YIELDS_CSV, parse_dates=["date"]).sort_values("date").set_index("date")
    y = y[~y.index.duplicated(keep="last")]
    tenors = [c for c in config.TENOR_CANDIDATES if c in y and y[c].notna().sum() > 100]
    rets = [c for c in config.RETURN_SERIES if c in y and y[c].notna().sum() > 100]
    if config.REF_TENOR not in tenors:
        raise SystemExit(f"{config.REF_TENOR} missing from yields.csv")
    cal = y.index[y[config.REF_TENOR].notna()]
    L = pd.DataFrame(index=cal)
    for c in tenors:
        L[c] = y.loc[cal, c] * 100.0
    for c in rets:
        L[c] = 100.0 * np.log(y.loc[cal, c].where(y.loc[cal, c] > 0))
    D = pd.DataFrame({f"dy_{c}": L[c].diff() for c in L}, index=cal)
    prev = pd.Series(cal, index=cal).shift(1)
    for c in config.GLOBAL_CONTROLS:                            # IST close-to-close alignment
        if c in y and y[c].notna().any():
            a = _asof(y[c], cal - pd.Timedelta(days=1)).values
            b = _asof(y[c], prev.fillna(cal[0]) - pd.Timedelta(days=1)).values
            D[f"d_{c}"] = (a - b) * (100 if c == "us10y" else 1)
    D.iloc[0] = np.nan
    cpi = pd.to_datetime(pd.read_csv(config.CPI_DATES_CSV).date) if config.CPI_DATES_CSV.exists() else []
    cpi_react = {_reaction_day(cal, c, c < pd.Timestamp(config.CPI_4PM_FROM)) for c in cpi}
    D["cpi_day"] = D.index.isin(list(cpi_react)).astype(int)
    oth = set()
    if config.OTHER_EVENTS_CSV.exists():
        o = pd.read_csv(config.OTHER_EVENTS_CSV)
        if len(o):
            aft = o.get("after_market", pd.Series(0, index=o.index)).fillna(0).astype(int)
            oth = {_reaction_day(cal, d, a == 1) for d, a in zip(o.date, aft)}
    D["other_day"] = D.index.isin(list(oth)).astype(int)
    D["weekday"], D["year"] = D.index.weekday, D.index.year
    return D, L, cal, tenors + rets, y


def add_market(m):
    D, L, cal, tenors, Y = daily_panel()
    pos = {d: i for i, d in enumerate(cal)}
    after = m.release_after_market.astype(str).isin(["1", "1.0", "True", "true"])
    m["event_date"] = [_reaction_day(cal, rd, a) if isinstance(rd, str) and rd else pd.NaT
                       for rd, a in zip(m.release_date, after)]
    m["decision_day"] = [_reaction_day(cal, md, False) for md in m.meeting_date]

    def lvl(i, c):
        return L[c].iloc[i] if 0 <= i < len(cal) else np.nan
    rows = []
    for ev in m.event_date:
        r = {}
        i = pos.get(ev, -99)
        for c in tenors:
            r[f"dy1_{c}"] = lvl(i, c) - lvl(i - 1, c)
            r[f"dy2_{c}"] = lvl(i + 1, c) - lvl(i - 1, c)
            r[f"dypre_{c}"] = lvl(i - 1, c) - lvl(i - 2, c)
        for c in [c for c in D if c.startswith("d_")]:
            r[f"{c}_1"] = D[c].iloc[i] if i >= 0 else np.nan
            r[f"{c}_2"] = D[c].iloc[i:i + 2].sum(min_count=2) if i >= 0 else np.nan
            r[f"{c}_pre"] = D[c].iloc[i - 1] if i >= 1 else np.nan
        r["cpi_day_1"] = int(D.cpi_day.iloc[i]) if i >= 0 else 0
        r["cpi_day_2"] = int(D.cpi_day.iloc[i:i + 2].max()) if i >= 0 else 0
        r["cpi_day_pre"] = int(D.cpi_day.iloc[i - 1]) if i >= 1 else 0
        r["other_day_1"] = int(D.other_day.iloc[i]) if i >= 0 else 0
        r["other_day_2"] = int(D.other_day.iloc[i:i + 2].max()) if i >= 0 else 0
        short = next((c for c in ["ois_1y", "tbill_364d", "gsec_1y", "tbill_182d", "tbill_91d"] if c in tenors), None)
        r["mkt_path_tenor"] = short
        r["mkt_level_pre"] = lvl(i - 1, short) / 100 if short else np.nan     # back to percent
        r["mkt_level_post"] = lvl(i, short) / 100 if short else np.nan
        rows.append(r)
    m = pd.concat([m.reset_index(drop=True), pd.DataFrame(rows)], axis=1)
    # market-implied path: short rate at the close before / after the minutes, minus the repo in force
    m["mkt_path_pre"] = (m.mkt_level_pre - m.repo_after) * 100
    m["mkt_path_post"] = (m.mkt_level_post - m.repo_after) * 100
    ev, decd = set(m.event_date.dropna()), set(m.decision_day.dropna())
    D["minutes_day"] = D.index.isin(list(ev)).astype(int)
    D["decision_day"] = D.index.isin(list(decd)).astype(int)
    return m, D, tenors


def add_shocks(m):
    """Attach the decision-day surprises of the SAME meeting (known before the minutes)
    and of the NEXT meeting (the predictability target)."""
    p = config.PROC / "shocks.csv"
    if not p.exists():
        log.warning("processed/shocks.csv missing - run the 'shocks' stage for the combined design")
        return m
    sh = pd.read_csv(p, dtype={"meeting_date": str})
    cols = [c for c in sh if c not in ("meeting_date", "decision_day", "factor_set", "unscheduled", "decision_bp")]
    m = m.merge(sh[["meeting_date"] + cols], on="meeting_date", how="left")
    nxt = sh[["meeting_date"] + cols].rename(columns={"meeting_date": "next_meeting_date", **{c: f"next_{c}" for c in cols}})
    return m.merge(nxt, on="next_meeting_date", how="left")


def run():
    st, col, dec = member_level()
    m = meeting_level(st, dec)
    m, D, tenors = add_market(m)
    m = add_shocks(m)
    m.to_csv(config.PROC / "meeting_level.csv", index=False)
    D.to_csv(config.PROC / "daily_changes.csv", index_label="date")
    msg = (f"score: {col}; surprise: {m.surprise_type.iloc[0]}; hidden dissent: {m.hidden_source.iloc[0]}; "
           f"meetings: {len(m)}; with market data: {m[f'dy1_{config.REF_TENOR}'].notna().sum()}; tenors: {tenors}")
    print(msg); log.info(msg)
    return m


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO, format="%(message)s")
    run()

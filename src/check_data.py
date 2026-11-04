"""Check every input before any analysis. Writes outputs/tables/data_check.md and exits
non-zero if a hard problem is found. Run after each change to data/raw/.

  python run_pipeline.py check
"""
import sys
import numpy as np
import pandas as pd
from src import config

LINES, HARD = [], []


def say(level, msg):
    LINES.append(f"- **{level}** {msg}")
    if level == "FAIL":
        HARD.append(msg)


def check_meetings():
    if not config.DECISIONS_CSV.exists():
        return say("FAIL", "raw/decisions.csv missing")
    d = pd.read_csv(config.DECISIONS_CSV, dtype={"meeting_date": str})
    for c in ["meeting_date", "decision_bp"]:
        if c not in d:
            return say("FAIL", f"decisions.csv lacks column {c}")
    dt = pd.to_datetime(d.meeting_date, errors="coerce")
    if dt.isna().any():
        say("FAIL", f"unparseable meeting_date rows: {d.meeting_date[dt.isna()].tolist()}")
    if d.meeting_date.duplicated().any():
        say("FAIL", f"duplicate meetings: {d.meeting_date[d.meeting_date.duplicated()].tolist()}")
    if "verified" in d and (d.verified.fillna(0) == 0).any():
        say("FAIL", f"{int((d.verified.fillna(0) == 0).sum())} rows of decisions.csv not verified (verified=0)")
    if "repo_after" in d and d.repo_after.notna().all():
        implied = d.repo_after.diff() * 100
        bad = d[(implied.round() != d.decision_bp) & implied.notna()]
        if len(bad):
            say("FAIL", f"decision_bp inconsistent with repo_after changes at {bad.meeting_date.tolist()}")
    say("OK", f"{len(d)} meetings {d.meeting_date.min()} .. {d.meeting_date.max()}; "
              f"{int((d.decision_bp > 0).sum())} hikes, {int((d.decision_bp < 0).sum())} cuts")
    if not config.URLS_CSV.exists():
        return say("FAIL", "raw/minutes_urls.csv missing")
    u = pd.read_csv(config.URLS_CSV, dtype=str)
    miss = sorted(set(d.meeting_date) - set(u.meeting_date))
    if miss:
        say("WARN", f"meetings without a minutes row: {miss}")
    lag = (pd.to_datetime(u.release_date) - pd.to_datetime(u.meeting_date)).dt.days
    if ((lag < 13) | (lag > 18)).any():
        say("WARN", f"unusual minutes lag (days) for {u.meeting_date[(lag < 13) | (lag > 18)].tolist()}")
    if not u.release_after_market.isin(["0", "1"]).all():
        say("FAIL", "release_after_market must be 0/1")
    from src.parse_minutes import find_file
    nofile = [md for md in u.meeting_date if find_file(md) is None]
    (say("WARN", f"{len(nofile)} minutes files missing: {nofile[:8]}") if nofile else say("OK", "all minutes files present"))
    mt = config.PROC / "meeting_texts.csv"
    if mt.exists():
        t = pd.read_csv(mt, dtype={"meeting_date": str}).merge(d, on="meeting_date", how="left")
        bad6 = t[(t.n_statements != 6) | (t.n_votes != 6)]
        if len(bad6):
            say("WARN", f"parser did not find 6 statements/6 votes for {bad6.meeting_date.tolist()} (check by hand)")
        if "repo_after" in t:
            mis = t[t.repo_parsed.notna() & t.repo_after.notna() & ((t.repo_parsed - t.repo_after).abs() > 1e-6)]
            if len(mis):
                say("FAIL", f"repo in minutes text != repo_after for {mis.meeting_date.tolist()}")
        if "stance" in t:
            ms = t[t.stance_parsed.notna() & t.stance.notna() & (t.stance_parsed != t.stance.str.lower().str.strip())]
            if len(ms):
                say("WARN", f"stance in minutes text != decisions.csv stance for {ms.meeting_date.tolist()}")


def check_market():
    if not config.YIELDS_CSV.exists():
        return say("FAIL", "raw/market/yields.csv missing (run the 'market' stage)")
    y = pd.read_csv(config.YIELDS_CSV, parse_dates=["date"]).set_index("date").sort_index()
    if config.REF_TENOR not in y:
        say("FAIL", f"{config.REF_TENOR} column missing")
    for c in y:
        s = y[c].dropna()
        if s.empty:
            say("WARN", f"{c} empty"); continue
        big = s.diff().abs()
        thr = 0.5 if c in config.TENOR_CANDIDATES + ["us10y"] else s.abs().median() * 0.1
        say("OK", f"{c}: {s.index.min().date()}..{s.index.max().date()}, n={len(s)}, "
                  f"max |daily change|={big.max():.3f} on {big.idxmax().date() if len(big.dropna()) else '-'}")
        if (big > thr).sum() > 5:
            say("WARN", f"{c}: {int((big > thr).sum())} daily jumps > {thr:.2f} -- check roll-overs of the benchmark bond or bad prints")
    have_ois = sum(c in y for c in config.FACTOR_OIS)
    say("OK" if have_ois >= 3 else "WARN", f"OIS tenors available: {have_ois} (>=3 recommended for decision-day factors)")
    if "nifty" not in y:
        say("WARN", "no nifty column: the information-effect split (mp vs cbi) cannot be computed")
    for c in config.GLOBAL_CONTROLS:
        if c not in y:
            say("WARN", f"global control {c} missing")
    if config.DECISIONS_CSV.exists():
        d = pd.to_datetime(pd.read_csv(config.DECISIONS_CSV).meeting_date)
        cov = y[config.REF_TENOR].dropna().index if config.REF_TENOR in y else []
        if len(cov) and (d.min() < cov.min() + pd.Timedelta(days=95)):
            say("WARN", "yield history starts < 3 months before the first meeting (Bauer-Swanson predictors need 63 trading days)")
    if not config.CPI_DATES_CSV.exists():
        say("WARN", "cpi_release_dates.csv missing: CPI-day control off")


def check_text():
    p = config.PROC / "member_statements.csv"
    if not p.exists():
        return say("INFO", "not parsed yet")
    st = pd.read_csv(p)
    unk = st[st.member_type == "unknown"].member.unique().tolist()
    if unk:
        say("FAIL", f"unknown members (add to src/members.py): {unk}")
    say("OK", f"{len(st)} statements, median {int(st.n_words.median())} words; "
              f"{int((st.vote_yes == 0).sum())} 'No' votes, {int(st.vote_bp.notna().sum())} magnitude entries")
    for f in ["scores_llm", "scores_dictionary", "scores_vader"]:
        q = config.PROC / f"{f}.csv"
        if q.exists():
            s = pd.read_csv(q)
            say("OK", f"{f}: {len(s)} rows, {int(s.iloc[:, 1].isna().sum())} missing")


def run():
    LINES.clear(); HARD.clear()
    for name, fn in [("Meetings and minutes", check_meetings), ("Market data", check_market), ("Text", check_text)]:
        LINES.append(f"\n### {name}")
        fn()
    txt = "# Data check\n" + "\n".join(LINES)
    (config.TABLES / "data_check.md").write_text(txt)
    print(txt)
    if HARD:
        print(f"\n{len(HARD)} hard problem(s). Fix before running the analysis.")
    return not HARD


if __name__ == "__main__":
    sys.exit(0 if run() else 1)

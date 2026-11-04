"""Decision-day monetary policy surprises for every MPC meeting, 2016-2026.

All RBI decisions are announced while markets are open (10:00 IST in recent years,
earlier in the afternoon), so the daily window close(t-1) -> close(t) contains the
announcement. Daily windows are noisier than intraday ones; if you have intraday quotes
(Bloomberg/Refinitiv) save them as described in DATA_GUIDE.md and the intraday changes
replace the daily ones automatically.

Produces, per meeting (processed/shocks.csv):
  target, path      Gurkaynak-Sack-Swanson (2005) factors from short-rate changes:
                    target = factor moving the shortest rate (scaled to its bp change),
                    path   = orthogonal factor with no effect on the shortest rate
                             (scaled to the 1y change). Built from OIS 1m-2y if present,
                             otherwise from the 91d/182d/364d T-bill and 2y G-sec.
  rate_surprise     first principal component, scaled to the 1y change (bp)
  mp_pm, cbi_pm     Jarocinski-Karadi (2020) 'poor man's' split: rate and equity moving in
                    opposite directions = monetary policy shock; same direction = central
                    bank information shock.
  mp_rot, cbi_rot   JK rotational sign-restriction split (median admissible rotation),
                    in bp of the rate surprise (mp_rot + cbi_rot = rate_surprise).
  *_purged          Bauer-Swanson (2023)-style: residual after projecting the surprise on
                    information available before the announcement.
  survey_surprise   decision_bp minus the poll median (if raw/consensus.csv is supplied).
  stance_change     +1 more hawkish / -1 more dovish stance wording vs previous meeting.
"""
import logging
import numpy as np
import pandas as pd
import statsmodels.api as sm
from src import config
from src.build_dataset import daily_panel, load_decisions, _reaction_day

log = logging.getLogger("shocks")


def factor_set(D):
    ois = [c for c in config.FACTOR_OIS if f"dy_{c}" in D and D[f"dy_{c}"].notna().sum() > 100]
    if len(ois) >= 3:
        return ois, "OIS"
    fb = [c for c in config.FACTOR_FALLBACK if f"dy_{c}" in D and D[f"dy_{c}"].notna().sum() > 100]
    if len(fb) >= 3:
        log.warning("No OIS: building factors from T-bills/2y G-sec (noisier; liquidity-sensitive)")
        return fb, "TBILL_FALLBACK"
    raise SystemExit("Need >= 3 short tenors (OIS 1m-2y, or T-bill 91d/182d/364d + 2y G-sec) in yields.csv")


def intraday_changes(events, tenors):
    """Optional: raw/market/intraday.csv with columns datetime (IST), series, value (percent).
    Window: last quote at/before announce-15min to last quote at/before announce+45min."""
    p = config.MARKET_DIR / "intraday.csv"
    if not p.exists():
        return None
    q = pd.read_csv(p, parse_dates=["datetime"]).sort_values("datetime")
    out = {}
    for md, ts in events:
        if pd.isna(ts):
            continue
        row = {}
        for c in tenors + config.RETURN_SERIES:
            s = q[q.series == c].set_index("datetime").value
            pre, post = s[:ts - pd.Timedelta(minutes=15)], s[:ts + pd.Timedelta(minutes=45)]
            if len(pre) and len(post) and pre.index[-1].date() == ts.date():
                a, b = pre.iloc[-1], post.iloc[-1]
                row[c] = (b - a) * 100 if c not in config.RETURN_SERIES else 100 * np.log(b / a)
        out[md] = row
    return pd.DataFrame(out).T


def gss(X, target_col, path_col):
    """Gurkaynak-Sack-Swanson rotation of the first two principal components of X (T x k, bp)."""
    Z = (X - X.mean()) / X.std()
    U, S, Vt = np.linalg.svd(Z.values, full_matrices=False)
    F = U[:, :2] * np.sqrt(len(Z))                            # unit-variance, orthogonal scores
    expl = (S ** 2 / (S ** 2).sum())[:3]
    g = np.linalg.lstsq(F, X[target_col].values - X[target_col].mean(), rcond=None)[0]
    u1, u2 = g / np.linalg.norm(g), np.array([-g[1], g[0]]) / np.linalg.norm(g)
    f1, f2 = F @ u1, F @ u2                                   # f2 has zero loading on the target rate
    b1 = np.polyfit(f1, X[target_col].values, 1)[0]
    b2 = np.polyfit(f2, X[path_col].values, 1)[0]
    pc1 = F[:, 0] * np.polyfit(F[:, 0], X[path_col].values, 1)[0]
    return pd.DataFrame({"target": f1 * b1, "path": f2 * b2, "rate_surprise": pc1}, index=X.index), expl


def jk_rotation(i, s, grid=2000):
    """Jarocinski-Karadi rotational decomposition of (rate, stock) surprises.
    Returns mp, cbi in rate units (bp) and the share of admissible rotations."""
    Um = np.column_stack([i, s])
    P = np.linalg.cholesky(np.cov(Um.T, bias=True) + 1e-12 * np.eye(2))
    adm = []
    for th in np.linspace(0, np.pi, grid, endpoint=False):
        M = P @ np.array([[np.cos(th), -np.sin(th)], [np.sin(th), np.cos(th)]])
        M = M * np.sign(M[0, :])                              # normalise: both shocks raise the rate
        if M[1, 0] < 0 and M[1, 1] > 0:                       # mp: stocks fall; cbi: stocks rise
            adm.append(M)
    if not adm:
        return np.full(len(i), np.nan), np.full(len(i), np.nan), 0.0
    angles = [np.arctan2(M[1, 0], M[0, 0]) for M in adm]
    M = adm[int(np.argsort(angles)[len(adm) // 2])]
    e = np.linalg.solve(M, Um.T)
    return M[0, 0] * e[0], M[0, 1] * e[1], len(adm) / grid


def pre_info(dec, Yraw, cal):
    """Information available at the close before each announcement (Bauer-Swanson predictors)."""
    rows = []
    cpi = pd.read_csv(config.CPI_CSV, parse_dates=["release_date"]) if config.CPI_CSV.exists() else None
    if cpi is not None and cpi.empty:
        cpi = None
    for md in dec.meeting_date:
        t = _reaction_day(cal, md, False)
        r = {"meeting_date": md}
        pos = cal.searchsorted(t) if pd.notna(t) else -1
        if pos >= 64:
            a, b = cal[pos - 1], cal[pos - 64]
            for c, kind in [("gsec_10y", "d"), ("nifty", "l"), ("brent", "l"), ("us10y", "d"), ("usdinr", "l")]:
                if c in Yraw:
                    va, vb = Yraw[c].asof(a), Yraw[c].asof(b)
                    r[f"pre3m_{c}"] = (va - vb) * 100 if kind == "d" else 100 * np.log(va / vb)
            if "gsec_10y" in Yraw and "tbill_91d" in Yraw:
                r["pre_slope"] = (Yraw.gsec_10y.asof(a) - Yraw.tbill_91d.asof(a)) * 100
        if cpi is not None:
            last = cpi[cpi.release_date < pd.Timestamp(md)].sort_values("release_date").tail(1)
            if len(last):
                r["pre_cpi_gap"] = float(last.cpi_yoy.iloc[0]) - 4.0
                if "consensus_yoy" in last and last.consensus_yoy.notna().any():
                    r["pre_cpi_surprise"] = float(last.cpi_yoy.iloc[0] - last.consensus_yoy.iloc[0])
        rows.append(r)
    return pd.DataFrame(rows)


def stance_code(dec):
    if "stance" not in dec or dec.stance.isna().all():
        return pd.Series(np.nan, index=dec.index)
    o = dec.stance.str.lower().str.strip().map(config.STANCE_ORDER)
    unk = dec.stance.notna() & o.isna()
    if unk.any():
        log.warning("Stance labels not in config.STANCE_ORDER: %s", sorted(dec.stance[unk].unique()))
    return np.sign(o.diff())


def run():
    D, L, cal, outs, Yraw = daily_panel()
    dec = load_decisions()
    tenors, fset = factor_set(D)
    dec["decision_day"] = [_reaction_day(cal, md, False) for md in dec.meeting_date]
    X = D.reindex(dec.decision_day)[[f"dy_{c}" for c in tenors]]
    X.columns, X.index = tenors, dec.meeting_date
    eq = D.reindex(dec.decision_day).get("dy_nifty")
    if "announce_time" in dec:                                # optional intraday override
        at = dec.announce_time.astype(str).str.strip()
        ts = pd.to_datetime(dec.meeting_date + " " + at, errors="coerce").where(at.str.match(r"^\d{1,2}:\d{2}$"))
        intra = intraday_changes(list(zip(dec.meeting_date, ts)), tenors)
        if intra is not None and len(intra):
            for c in tenors:
                if c in intra:
                    X.loc[intra.index, c] = intra[c].combine_first(X.loc[intra.index, c])
            if "nifty" in intra and eq is not None:
                eq = pd.Series(eq.values, index=dec.meeting_date)
                eq.loc[intra.index] = intra["nifty"].combine_first(eq.loc[intra.index])
            fset += "+intraday"
    ok = X.notna().all(axis=1)
    path_col = next(c for c in ["ois_1y", "tbill_364d", "gsec_1y", tenors[-1]] if c in tenors)
    F, expl = gss(X[ok], tenors[0], path_col)
    out = dec[["meeting_date", "decision_day", "decision_bp"] + [c for c in ["unscheduled"] if c in dec]].copy()
    out = out.merge(F, left_on="meeting_date", right_index=True, how="left")
    out["factor_set"] = fset
    diag = {"factor_set": fset, "tenors": "+".join(tenors), "target_tenor": tenors[0], "path_tenor": path_col,
            "n_events": int(ok.sum()), "var_share_pc1": expl[0], "var_share_pc2": expl[1], "var_share_pc3": expl[2]}
    # information effect
    if eq is not None:
        s = pd.Series(np.asarray(eq, float), index=dec.meeting_date.values)
        out["d_equity"] = out.meeting_date.map(s)
        i, sv = out.rate_surprise, out.d_equity
        both = i.notna() & sv.notna()
        same = np.sign(i) * np.sign(sv) > 0
        out["mp_pm"] = np.where(both & ~same, i, 0.0); out["cbi_pm"] = np.where(both & same, i, 0.0)
        out.loc[~both, ["mp_pm", "cbi_pm"]] = np.nan
        mp, cbi, share = jk_rotation(i[both].values, sv[both].values)
        out.loc[both, "mp_rot"], out.loc[both, "cbi_rot"] = mp, cbi
        diag.update(jk_admissible_share=share, share_cbi_events_pm=float((both & same).sum() / both.sum()))
    else:
        log.warning("No 'nifty' column in yields.csv: information-effect split skipped")
    # survey surprise and stance
    if config.CONSENSUS_CSV.exists():
        c = pd.read_csv(config.CONSENSUS_CSV, dtype={"meeting_date": str})
        out = out.merge(c[["meeting_date", "consensus_bp"]], on="meeting_date", how="left")
        out["survey_surprise"] = out.decision_bp - out.consensus_bp
    out["stance_change"] = stance_code(dec).values
    # Bauer-Swanson purge
    pre = pre_info(dec, Yraw, cal)
    out = out.merge(pre, on="meeting_date", how="left")
    preds = [c for c in pre if c != "meeting_date" and pre[c].notna().mean() > .8]
    for v in [c for c in ["target", "path", "rate_surprise", "mp_rot"] if c in out]:
        d = out[[v] + preds].dropna()
        if len(d) < len(preds) + 10 or not preds:
            continue
        r = sm.OLS(d[v], sm.add_constant(d[preds])).fit(cov_type="HC3")
        out.loc[d.index, f"{v}_purged"] = r.resid
        diag[f"purge_r2_{v}"], diag[f"purge_F_p_{v}"] = r.rsquared, float(r.f_pvalue)
    diag["purge_predictors"] = "+".join(preds)
    out.drop(columns=[c for c in pre if c != "meeting_date"]).to_csv(config.PROC / "shocks.csv", index=False)
    pd.DataFrame([diag]).T.rename(columns={0: "value"}).to_csv(config.TABLES / "shock_diagnostics.csv")
    log.info("shocks: %d meetings, factor set %s", int(ok.sum()), fset)
    return out


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO, format="%(message)s")
    print(run().round(2).to_string())

"""Minutes-release event study.

Stage A (text-free): are yield changes more volatile on minutes-reaction days than on
  ordinary days? Variance ratio, Brown-Forsythe test, and a stratified permutation test
  (each minutes day matched to a random control day of the same year and weekday).
  Decision days are reported as a benchmark. Needs no text measure -> most robust result.
Stage B (directional): dy_tenor(window) on minutes surprise, hidden dissent, components;
  HC3 SEs, randomization inference (permute the text measure across events: exact under
  the sharp null, sensible with ~60 events), pairs bootstrap CI, Holm across tenors.
Stage C (uncertainty): |dy| on hidden-dissent share and cross-member dispersion.
Placebos: pre-event day (leakage / pre-trend) and random non-event days.
"""
import warnings
import numpy as np
import pandas as pd
import statsmodels.api as sm
from scipy import stats
from src import config

warnings.filterwarnings("ignore")
CTRL_BASE = ["d_us10y", "d_vix", "d_brent"]


def tenors_in(m):
    """Outcomes present: yields (bp) and config.RETURN_SERIES (% log change)."""
    return [t for t in config.TENOR_CANDIDATES + config.RETURN_SERIES
            if f"dy1_{t}" in m and m[f"dy1_{t}"].notna().sum() >= 15]


def controls(m, w):
    c = [f"{b}_{w}" for b in CTRL_BASE if f"{b}_{w}" in m and m[f"{b}_{w}"].notna().mean() > .5]
    c += [f"cpi_day_{w}"] if f"cpi_day_{w}" in m and m[f"cpi_day_{w}"].sum() > 0 else []
    return c + ([f"other_day_{w}"] if f"other_day_{w}" in m and m[f"other_day_{w}"].sum() > 0 else [])


def ols(d, y, xs):
    d = d[[y] + xs].dropna()
    if len(d) < len(xs) + 8:
        return None, d
    return sm.OLS(d[y], sm.add_constant(d[xs], has_constant="add")).fit(cov_type="HC3"), d


def rand_inf(d, y, x, xs, B=2000, seed=0):
    """Permutation p-value for the HC3 t-stat of x, permuting x across events."""
    rng = np.random.default_rng(seed)
    X = sm.add_constant(d[xs], has_constant="add")
    t0 = sm.OLS(d[y], X).fit(cov_type="HC3").tvalues[x]
    ts = np.empty(B)
    for b in range(B):
        Xb = X.copy(); Xb[x] = rng.permutation(Xb[x].values)
        ts[b] = sm.OLS(d[y], Xb).fit(cov_type="HC3").tvalues[x]
    return float((np.abs(ts) >= abs(t0)).mean())


def pairs_boot(d, y, x, xs, B=2000, seed=0):
    rng = np.random.default_rng(seed); b = []
    for _ in range(B):
        s = d.iloc[rng.integers(0, len(d), len(d))]
        try:
            b.append(sm.OLS(s[y], sm.add_constant(s[xs], has_constant="add")).fit().params[x])
        except Exception:
            pass
    return np.percentile(b, [2.5, 97.5])


def holm(p):
    p = np.asarray(p, float); o = np.argsort(p); adj = np.empty_like(p); run = 0
    for k, i in enumerate(o):
        run = max(run, min(1, (len(p) - k) * p[i])); adj[i] = run
    return adj


# ----------------------------------------------------------------------------- Stage A
def variance_test(D, tenors, B=5000, seed=3):
    rng = np.random.default_rng(seed)
    ev = D.index[D.minutes_day == 1]
    near = D.minutes_day.rolling(3, center=True, min_periods=1).max().astype(bool) | \
        D.decision_day.rolling(3, center=True, min_periods=1).max().astype(bool)
    ctrl_mask = ~near & (D.cpi_day == 0) & (D.get("other_day", 0) == 0)
    rows = []
    for t in tenors:
        y = D[f"dy_{t}"]
        ctrl = y[ctrl_mask].dropna()
        cdf = pd.DataFrame({"y": ctrl, "year": D.year[ctrl.index], "wd": D.weekday[ctrl.index]})
        pools = {k: v.y.values for k, v in cdf.groupby(["year", "wd"])}
        ypools = {k: v.y.values for k, v in cdf.groupby("year")}
        for name, mask in [("minutes", D.minutes_day == 1), ("minutes_ex_cpi", (D.minutes_day == 1) & (D.cpi_day == 0)),
                           ("decision", D.decision_day == 1)]:
            e = y[mask].dropna()
            if len(e) < 8:
                continue
            keys = [(D.year[d], D.weekday[d]) for d in e.index]
            sims = np.empty(B)
            for b in range(B):
                draw = [rng.choice(pools[k]) if k in pools and len(pools[k]) else rng.choice(ypools[k[0]]) for k in keys]
                sims[b] = np.mean(np.square(draw))
            obs = np.mean(np.square(e.values))
            rows.append(dict(tenor=t, days=name, n=len(e), rms_event_bp=np.sqrt(obs), rms_control_bp=np.sqrt(np.mean(ctrl ** 2)),
                             mean_abs_event_bp=e.abs().mean(), mean_abs_control_bp=ctrl.abs().mean(),
                             var_ratio=obs / np.mean(ctrl ** 2), p_brown_forsythe=stats.levene(e, ctrl, center="median").pvalue,
                             p_perm_matched=float((sims >= obs).mean()), n_control=len(ctrl)))
    out = pd.DataFrame(rows)
    out.to_csv(config.TABLES / "variance_test.csv", index=False)
    return out


# ----------------------------------------------------------------------------- Stage B/C
def specs(m):
    s = {"surprise": ["surprise"],
         "surprise_hidden": ["surprise", "hidden_signed"],
         "int_ext": ["surprise_int", "surprise_ext"],
         "with_shocks": ["surprise", "hidden_signed", "target", "path"],
         "levels": ["mean_hawk_exgov", "hawk_gov"] + (["hawk_resolution"] if "hawk_resolution" in m else []),
         "legacy_gap": ["mean_gap", "decision_dir"]}
    return {k: v for k, v in s.items() if all(c in m and m[c].notna().sum() >= 15 for c in v)}


def run(B=2000, n_placebo=1000, seed=1):
    m = pd.read_csv(config.PROC / "meeting_level.csv")
    D = pd.read_csv(config.PROC / "daily_changes.csv", parse_dates=["date"]).set_index("date")
    tenors = tenors_in(m)
    variance_test(D, tenors, B=max(B, 1000))
    rows = []
    for w in ["1", "2"]:
        ctl = controls(m, w)
        for t in tenors:
            y = f"dy{w}_{t}"
            for name, xs in specs(m).items():
                r, d = ols(m, y, xs + ctl)
                if r is None:
                    continue
                key = name in ("surprise", "surprise_hidden", "with_shocks")
                for x in xs:
                    ri = rand_inf(d, y, x, xs + ctl, B=B) if (key and x in ("surprise", "hidden_signed")) else np.nan
                    lo, hi = pairs_boot(d, y, x, xs + ctl, B) if (name == "surprise") else (np.nan, np.nan)
                    rows.append(dict(window=w, tenor=t, unit="%" if t in config.RETURN_SERIES else "bp",
                                     spec=name, var=x, coef_bp=r.params[x], se=r.bse[x],
                                     t=r.tvalues[x], p=r.pvalues[x], p_randinf=ri, boot_lo=lo, boot_hi=hi,
                                     n=int(r.nobs), r2=r.rsquared, controls="+".join(ctl)))
    res = pd.DataFrame(rows)
    for (w, sp, v), g in res.groupby(["window", "spec", "var"]):
        res.loc[g.index, "p_holm_tenors"] = holm(g.p.values)
    res.to_csv(config.TABLES / "event_study.csv", index=False)

    # Stage C: uncertainty channel, |dy| on hidden-dissent share and dispersion
    unc = []
    ctl = [c for c in controls(m, "1") if not c.startswith(("cpi", "other"))]
    mm = m.copy()
    for c in ctl:
        mm[c + "_abs"] = mm[c].abs()
    for t in tenors:
        mm[f"absdy_{t}"] = mm[f"dy1_{t}"].abs()
        for xs in (["hidden_share"], ["sd_hawk"], ["hidden_share", "sd_hawk"]):
            if not all(x in mm and mm[x].notna().sum() >= 15 for x in xs):
                continue
            r, _ = ols(mm, f"absdy_{t}", xs + [c + "_abs" for c in ctl])
            if r is None:
                continue
            for x in xs:
                unc.append(dict(tenor=t, spec="+".join(xs), var=x, coef_bp=r.params[x], se=r.bse[x], p=r.pvalues[x], n=int(r.nobs)))
    pd.DataFrame(unc).to_csv(config.TABLES / "uncertainty.csv", index=False)

    # Placebo 1: pre-event day (yields should NOT respond to minutes that are not out yet)
    pre = []
    ctl = controls(m, "pre")
    for t in tenors:
        for x in ["surprise", "hidden_signed"]:
            if x not in m:
                continue
            r, _ = ols(m, f"dypre_{t}", [x] + ctl)
            if r is not None:
                pre.append(dict(tenor=t, var=x, coef_bp=r.params[x], se=r.bse[x], p=r.pvalues[x], n=int(r.nobs)))
    pd.DataFrame(pre).to_csv(config.TABLES / "placebo_preday.csv", index=False)

    # Placebo 2: pair each meeting's surprise with random ordinary days
    ev = set(pd.to_datetime(m.event_date.dropna()))
    pool = D[(~D.index.isin(ev)) & (D.cpi_day == 0) & (D.decision_day == 0)].dropna(subset=[f"dy_{t}" for t in tenors])
    gctl = [c for c in ["d_us10y", "d_vix", "d_brent"] if c in pool and pool[c].notna().mean() > .5]
    pool = pool.dropna(subset=gctl)
    rng = np.random.default_rng(seed); pl = {}
    sub = m[["surprise"]].dropna()
    for t in tenors:
        bs = []
        for _ in range(n_placebo):
            draw = pool.iloc[rng.integers(0, len(pool), len(sub))]
            X = sm.add_constant(pd.DataFrame({"surprise": sub.surprise.values, **{c: draw[c].values for c in gctl}}))
            bs.append(sm.OLS(draw[f"dy_{t}"].values, X).fit().params["surprise"])
        pl[t] = np.array(bs)
    pd.DataFrame(pl).to_csv(config.TABLES / "placebo_coefs.csv", index=False)

    # Subsamples for the main spec (window 1)
    subs = []
    md = pd.to_datetime(m.meeting_date)
    cuts = {"full": md.notna(),
            "ex_covid": ~md.between(*config.COVID_WINDOW),
            "patel_2016_18": md < "2018-12-11", "das_2018_24": md.between("2018-12-11", "2024-12-10"),
            "malhotra_2024_": md > "2024-12-10",
            "mpc1_2016_20": md < "2020-10-01", "mpc2plus_2020_": md >= "2020-10-01"}
    ctl = controls(m, "1"); sp = specs(m); xs = sp.get("with_shocks", sp.get("surprise_hidden", ["surprise"]))
    for nm, mask in cuts.items():
        for t in tenors:
            r, _ = ols(m[mask], f"dy1_{t}", xs + ctl)
            if r is None:
                continue
            for x in xs:
                subs.append(dict(sample=nm, tenor=t, var=x, coef_bp=r.params[x], se=r.bse[x], p=r.pvalues[x], n=int(r.nobs)))
    pd.DataFrame(subs).to_csv(config.TABLES / "subsamples.csv", index=False)
    return res


if __name__ == "__main__":
    r = run()
    print(pd.read_csv(config.TABLES / "variance_test.csv").round(3).to_string())
    print(r.query("window=='1' and spec in ['surprise','surprise_hidden']").round(3).to_string())

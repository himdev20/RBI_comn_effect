"""Robustness of the headline result: minutes surprise -> short/medium OIS on the reaction day.

Each row re-estimates  dy1_tenor ~ surprise (+ decision-day shocks) + global controls
under one change, with HC3 SEs and randomization-inference p-values.
"""
import numpy as np
import pandas as pd
import statsmodels.api as sm
from src import config
from src.event_study import ols, rand_inf, controls


def _dict_surprise():
    st = pd.read_csv(config.PROC / "member_level.csv")
    ng = st[st.governor == 0].groupby("meeting_date").hawk_dict.mean()
    gv = st[st.governor == 1].groupby("meeting_date").hawk_dict.mean()
    return (ng - gv).rename("surprise_dict")


def run(B=1000, tenors=("ois_6m", "ois_1y", "ois_2y", "gsec_1y")):
    m = pd.read_csv(config.PROC / "meeting_level.csv")
    m = m.merge(_dict_surprise(), left_on="meeting_date", right_index=True, how="left")
    p = config.PROC / "shocks_ois.csv"
    if p.exists():
        o = pd.read_csv(p)[["meeting_date", "target", "path"]].rename(columns={"target": "target_ois", "path": "path_ois"})
        m = m.merge(o, on="meeting_date", how="left")
    ctl = controls(m, "1")
    md = pd.to_datetime(m.meeting_date)
    covid = md.between(*config.COVID_WINDOW)
    variants = [
        ("baseline: surprise + T-bill shocks", "surprise", ["target", "path"], m.index == m.index),
        ("no decision-day controls", "surprise", [], m.index == m.index),
        ("OIS-based decision-day shocks (2018-)", "surprise", ["target_ois", "path_ois"], m.index == m.index),
        ("ex-COVID (Mar 2020-Dec 2021)", "surprise", ["target", "path"], ~covid),
        ("drop unscheduled meetings", "surprise", ["target", "path"], m.unscheduled.fillna(0) == 0),
        ("dictionary tone instead of LLM", "surprise_dict", ["target", "path"], m.index == m.index),
        ("members minus resolution tone", "surprise_res", ["target", "path"], m.index == m.index),
        ("internal members only (minus Governor)", "surprise_int", ["target", "path"], m.index == m.index),
    ]
    rows = []
    for t in tenors:
        y = f"dy1_{t}"
        for name, x, sh, mask in variants:
            if x not in m or any(s not in m for s in sh):
                continue
            r, d = ols(m[mask], y, [x] + sh + ctl)
            if r is None:
                continue
            rows.append(dict(tenor=t, variant=name, coef_bp=r.params[x], se=r.bse[x], p=r.pvalues[x],
                             p_randinf=rand_inf(d, y, x, [x] + sh + ctl, B=B), n=int(r.nobs),
                             bp_per_sd=r.params[x] * d[x].std()))
        # influence: drop the 3 meetings with the largest |DFBETA| on the surprise
        r, d = ols(m, y, ["surprise", "target", "path"] + ctl)
        if r is not None:
            infl = r.get_influence() if hasattr(r, "get_influence") else sm.OLS(d[y], sm.add_constant(d[["surprise", "target", "path"] + ctl])).fit().get_influence()
            dfb = np.abs(infl.dfbetas[:, list(r.params.index).index("surprise")])
            drop = d.index[np.argsort(dfb)[-3:]]
            r2, d2 = ols(m.drop(index=drop), y, ["surprise", "target", "path"] + ctl)
            rows.append(dict(tenor=t, variant=f"drop 3 most influential ({', '.join(m.loc[drop, 'meeting_date'])})",
                             coef_bp=r2.params["surprise"], se=r2.bse["surprise"], p=r2.pvalues["surprise"],
                             p_randinf=rand_inf(d2, y, "surprise", ["surprise", "target", "path"] + ctl, B=B),
                             n=int(r2.nobs), bp_per_sd=r2.params["surprise"] * d2.surprise.std()))
    out = pd.DataFrame(rows)
    out.to_csv(config.TABLES / "robustness_main.csv", index=False)
    return out


if __name__ == "__main__":
    pd.set_option("display.width", 220)
    print(run().round(3).to_string())

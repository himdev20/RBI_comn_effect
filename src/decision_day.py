"""Validation of the decision-day surprise series (the 'first stage' table of the paper).

For each outcome (yields in bp; Nifty and USD/INR in % log change) on decision days:
  (a) dy ~ target + path
  (b) dy ~ mp_rot + cbi_rot          (information-effect split)
  (c) dy ~ survey_surprise           (if consensus.csv supplied)
  (d) dy ~ stance_change + target + path
HC3 standard errors; unscheduled meetings can be dropped with RBI_DROP_UNSCHEDULED=1.
Sanity checks to look for: target loads mostly on the short end, path on 1-5y, a hawkish
mp shock lowers equities and appreciates the rupee (usdinr falls), a cbi shock raises both
rates and equities.
"""
import os
import warnings
import numpy as np
import pandas as pd
import statsmodels.api as sm
from src import config
from src.build_dataset import daily_panel

warnings.filterwarnings("ignore")


def run():
    sh = pd.read_csv(config.PROC / "shocks.csv", parse_dates=["decision_day"])
    if os.environ.get("RBI_DROP_UNSCHEDULED") and "unscheduled" in sh:
        sh = sh[sh.unscheduled.fillna(0) == 0]
    D, L, cal, outs, _ = daily_panel()
    d = sh.merge(D, left_on="decision_day", right_index=True, how="left")
    specs = {"target_path": ["target", "path"], "info_split": ["mp_rot", "cbi_rot"],
             "survey": ["survey_surprise"], "stance": ["stance_change", "target", "path"],
             "purged": ["target_purged", "path_purged"]}
    rows = []
    for o in outs:
        y = f"dy_{o}"
        for name, xs in specs.items():
            if not all(x in d and d[x].notna().sum() >= 15 for x in xs) or (name == "stance" and d.stance_change.abs().sum() < 3):
                continue
            dd = d[[y] + xs].dropna()
            if len(dd) < len(xs) + 8:
                continue
            r = sm.OLS(dd[y], sm.add_constant(dd[xs])).fit(cov_type="HC3")
            for x in xs:
                rows.append(dict(outcome=o, unit="%" if o in config.RETURN_SERIES else "bp", spec=name, var=x,
                                 coef=r.params[x], se=r.bse[x], p=r.pvalues[x], r2=r.rsquared, n=int(r.nobs)))
    out = pd.DataFrame(rows)
    out.to_csv(config.TABLES / "decision_day.csv", index=False)
    return out


if __name__ == "__main__":
    print(run().round(3).to_string())

"""The tests that join the two halves of the paper (decision-day surprises x minutes text).

L1  What kind of decision day produces disagreement in the minutes?
      hidden_share / sd_hawk / mean uncertainty  ~  |mp_rot| + |cbi_rot|   (and |target| + |path|)
      Signed: hidden_signed ~ mp_rot + cbi_rot
L2  Is the minutes text news relative to the decision-day surprise?  (event_study.py, spec
      'with_shocks': dy1 ~ surprise + hidden_signed + target + path + controls)
L3  Are NEXT meeting's surprises predictable from the minutes?  Under rational, fully informed
      markets the next decision-day surprise is unpredictable from public information; the
      minutes are public 14 days after the meeting, so
      next_{target, path, rate_surprise, mp_rot}  ~  surprise + hidden_signed (+ minutes-day move)
      significant text coefficients = markets under-use the minutes. Randomization inference.
L4  Does the minutes-day market move itself forecast the next surprise in the right direction?
      next_path ~ dy1_<1y tenor> on minutes day.
"""
import warnings
import numpy as np
import pandas as pd
import statsmodels.api as sm
from src import config
from src.event_study import rand_inf

warnings.filterwarnings("ignore")


def _fit(m, y, xs, label, rows, ri=False, B=2000):
    if not all(x in m for x in xs + [y]):
        return
    d = m[[y] + xs].dropna()
    if len(d) < len(xs) + 10:
        return
    r = sm.OLS(d[y], sm.add_constant(d[xs], has_constant="add")).fit(cov_type="HC3")
    for x in xs:
        rows.append(dict(test=label, y=y, var=x, coef=r.params[x], se=r.bse[x], p=r.pvalues[x],
                         p_randinf=rand_inf(d, y, x, xs, B=B) if ri else np.nan, r2=r.rsquared, n=int(r.nobs)))


def run(B=2000):
    m = pd.read_csv(config.PROC / "meeting_level.csv")
    rows = []
    for c in ["mp_rot", "cbi_rot", "target", "path"]:
        if c in m:
            m[f"abs_{c}"] = m[c].abs()
    for y in ["hidden_share", "sd_hawk", "mean_unc_llm"]:
        _fit(m, y, ["abs_mp_rot", "abs_cbi_rot"], "L1 disagreement ~ |shock type|", rows)
        _fit(m, y, ["abs_target", "abs_path"], "L1 disagreement ~ |target|,|path|", rows)
    _fit(m, "hidden_signed", ["mp_rot", "cbi_rot"], "L1 signed hidden dissent ~ shocks", rows)
    short = next((t for t in ["ois_1y", "tbill_364d", "gsec_1y", "ois_6m", "tbill_182d"] if f"dy1_{t}" in m), None)
    for y in ["next_target", "next_path", "next_rate_surprise", "next_mp_rot", "next_survey_surprise",
              "next_target_purged", "next_path_purged"]:
        _fit(m, y, ["surprise", "hidden_signed"], "L3 next surprise ~ minutes text", rows, ri=True, B=B)
        if short:
            _fit(m, y, ["surprise", "hidden_signed", f"dy1_{short}"], "L3 + minutes-day move", rows, ri=True, B=B)
            _fit(m, y, [f"dy1_{short}"], "L4 next surprise ~ minutes-day move", rows)
    out = pd.DataFrame(rows)
    out.to_csv(config.TABLES / "linkage.csv", index=False)
    return out


if __name__ == "__main__":
    print(run().round(3).to_string())

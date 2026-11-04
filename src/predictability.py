"""Does the minutes text predict the NEXT MPC decision, and is that information priced?

  M0 persistence:            next_bp ~ decision_bp
  M1 + market (pre):         + mkt_path_pre   (short rate - repo at the close BEFORE the minutes)
  M2 + text:                 + surprise + hidden_signed (+ mean member next-move signal)
  M3 efficiency:             decision_bp + mkt_path_post + text
     -> text significant in M2 beyond M1: the minutes carry information about future policy.
     -> text still significant in M3 (after the market has seen the minutes): markets
        under-react to the minutes.
Also: does hidden dissent today predict explicit dissent at the next meeting?
Linear models (HC3, leave-one-out RMSE) are the main specification -- with ~60 meetings and
few hikes, the ordered probit (next direction) is reported as secondary.
"""
import warnings
import numpy as np
import pandas as pd
import statsmodels.api as sm
from statsmodels.miscmodels.ordinal_model import OrderedModel
from src import config

warnings.filterwarnings("ignore")


def loo_rmse(d, y, xs):
    X = sm.add_constant(d[xs], has_constant="add").values
    r = sm.OLS(d[y].values, X).fit()
    h = np.einsum("ij,jk,ik->i", X, np.linalg.pinv(X.T @ X), X)
    return float(np.sqrt(np.mean((r.resid / (1 - h)) ** 2)))


def run():
    m = pd.read_csv(config.PROC / "meeting_level.csv").sort_values("meeting_date")
    text = [c for c in ["surprise", "hidden_signed", "mean_next_move_llm"] if c in m and m[c].notna().sum() >= 15]
    extra = ["cpi_surprise"] if "cpi_surprise" in m and m.cpi_surprise.notna().sum() >= 15 else []
    mk_pre = ["mkt_path_pre"] if m.mkt_path_pre.notna().sum() >= 15 else []
    mk_post = ["mkt_path_post"] if m.mkt_path_post.notna().sum() >= 15 else []
    models = {"M0 persistence": ["decision_bp"],
              "M1 + market pre": ["decision_bp"] + mk_pre,
              "M2 + market pre + text": ["decision_bp"] + mk_pre + text,
              "M2b text only": ["decision_bp"] + text,
              "M3 market post + text": ["decision_bp"] + mk_post + text}
    rows = []
    for name, xs in models.items():
        xs = xs + extra
        d = m.dropna(subset=["next_decision_bp"] + xs)
        if len(d) < len(xs) + 10:
            continue
        r = sm.OLS(d.next_decision_bp, sm.add_constant(d[xs], has_constant="add")).fit(cov_type="HC3")
        row = dict(target="next_decision_bp", model=name, n=len(d), r2=r.rsquared, loo_rmse_bp=loo_rmse(d, "next_decision_bp", xs),
                   naive_rmse_bp=float(np.sqrt(np.mean((d.next_decision_bp - d.decision_bp) ** 2))))
        for x in xs:
            row[f"b_{x}"], row[f"p_{x}"] = r.params[x], r.pvalues[x]
        if len(text) and all(x in xs for x in text):
            row["p_joint_text"] = float(r.f_test(" = ".join(text[:1]) + " = 0" if len(text) == 1 else
                                                 ", ".join(f"{x} = 0" for x in text)).pvalue)
        rows.append(row)
    # next-meeting explicit dissent
    for xs in (["n_dissent"], ["n_dissent", "hidden_share"], ["n_dissent", "hidden_share", "sd_hawk"]):
        if not all(x in m for x in xs):
            continue
        d = m.dropna(subset=["next_n_dissent"] + xs)
        if len(d) < len(xs) + 10:
            continue
        r = sm.OLS(d.next_n_dissent, sm.add_constant(d[xs], has_constant="add")).fit(cov_type="HC3")
        row = dict(target="next_n_dissent", model="+".join(xs), n=len(d), r2=r.rsquared, loo_rmse_bp=loo_rmse(d, "next_n_dissent", xs))
        for x in xs:
            row[f"b_{x}"], row[f"p_{x}"] = r.params[x], r.pvalues[x]
        rows.append(row)
    # secondary: ordered probit for the next direction, leave-one-out accuracy
    for name in ["M0 persistence", "M2 + market pre + text"]:
        xs = models[name] + extra
        d = m.dropna(subset=["next_decision_dir"] + xs).reset_index(drop=True)
        if d.next_decision_dir.nunique() < 2 or len(d) < 20:
            continue
        def fit(dd):
            return OrderedModel(dd.next_decision_dir.astype(int), dd[xs], distr="probit").fit(method="bfgs", disp=False)
        try:
            r = fit(d)
        except Exception as e:
            rows.append(dict(target="next_decision_dir", model=name, note=str(e)[:80])); continue
        hits = []
        for i in range(len(d)):
            tr = d.drop(i)
            try:
                rr = fit(tr); p = rr.model.predict(rr.params, exog=d.loc[[i], xs])
                hits.append(int(np.sort(tr.next_decision_dir.astype(int).unique())[int(np.argmax(p))] == d.next_decision_dir[i]))
            except Exception:
                pass
        rows.append(dict(target="next_decision_dir", model=name + " (ordered probit)", n=len(d), pseudo_r2=r.prsquared,
                         loo_accuracy=np.mean(hits) if hits else np.nan,
                         baseline_same_dir_acc=(d.decision_dir == d.next_decision_dir).mean(),
                         baseline_modal_acc=d.next_decision_dir.value_counts(normalize=True).max()))
    out = pd.DataFrame(rows)
    out.to_csv(config.TABLES / "predictability.csv", index=False)
    return out


if __name__ == "__main__":
    print(run().T)

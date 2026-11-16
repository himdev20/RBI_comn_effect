"""Human validation of the text measures (do this BEFORE looking at any market result).

  python run_pipeline.py validate-draw   -> outputs/tables/human_sample.csv (60 statements,
                                            stratified by year and member type, seed fixed)
  Code columns human_hawk (-2..2), human_lean (-1/0/1), human_reservation (0/1/2) following
  docs/CODEBOOK.md, WITHOUT looking at the model scores. A second coder fills *_2 columns.
  python run_pipeline.py validate        -> outputs/tables/validation.csv
Reported: Pearson, Spearman, MAE, share within 1, quadratic-weighted kappa for every
machine score vs the human code; inter-coder kappa if a second coder exists.
"""
import numpy as np
import pandas as pd
from scipy.stats import spearmanr, pearsonr
from sklearn.metrics import cohen_kappa_score
from src import config

FIELDS = {"human_hawk": ["hawk_llm", "hawk_dict", "sent_vader", "hawk_finbert"],
          "human_lean": ["lean_llm"], "human_reservation": ["reservation_llm"]}


def draw_sample(n=60, seed=42):
    df = pd.read_csv(config.PROC / "member_statements.csv")
    df["year"] = df.meeting_date.str[:4]
    s = (df.groupby(["year", "member_type"], group_keys=False)
           .apply(lambda g: g.sample(min(len(g), max(1, round(n * len(g) / len(df)))), random_state=seed)))
    s = s.sample(frac=1, random_state=seed).head(n)[["statement_id", "meeting_date", "statement"]].copy()
    for c in list(FIELDS) + [f + "_2" for f in FIELDS]:
        s[c] = np.nan
    s.to_csv(config.TABLES / "human_sample.csv", index=False)
    return s


def draw_meetings(n_meetings=20, seed=42):
    """Whole-meeting sample: all six statements of 20 meetings (120 statements), stratified by
    year. Because the paper's regressor is a WITHIN-meeting gap (members minus Governor), coding
    whole meetings lets us validate the gap itself, not only statement-level scores. Statements
    are shuffled and member names masked so the coder cannot see who is the Governor."""
    from src.score_llm import mask
    df = pd.read_csv(config.PROC / "member_statements.csv")
    rng = np.random.default_rng(seed)
    md = pd.Series(sorted(df.meeting_date.unique()))
    yr = md.str[:4]
    pick = []
    for y, g in md.groupby(yr):                       # ~2 per year, then top up at random
        pick += list(rng.choice(g.values, size=min(len(g), 2), replace=False))
    pick = list(rng.choice(pick, size=min(n_meetings, len(pick)), replace=False))
    from src.score_llm import decision_text
    dec = pd.read_csv(config.DECISIONS_CSV, dtype={"meeting_date": str})
    dec["adopted_decision"] = [decision_text(b, s_) for b, s_ in zip(dec.decision_bp, dec.get("stance", [None] * len(dec)))]
    s = df[df.meeting_date.isin(pick)].merge(dec[["meeting_date", "adopted_decision"]], on="meeting_date", how="left")
    s = s.sample(frac=1, random_state=seed)[["statement_id", "adopted_decision", "statement"]].copy()
    s["statement"] = s.statement.map(mask)
    s.insert(0, "row", range(1, len(s) + 1))            # meeting dates are hidden; statement_id maps back
    for c in list(FIELDS) + [f + "_2" for f in FIELDS]:
        s[c] = np.nan
    s.to_csv(config.TABLES / "human_sample.csv", index=False)
    return s


def _gap_check(h):
    """Meeting-level: human gap (members minus Governor) vs LLM gap, for fully coded meetings."""
    st = pd.read_csv(config.PROC / "member_level.csv")[["statement_id", "meeting_date", "governor", "hawk_llm"]]
    d = st.merge(h[["statement_id", "human_hawk"]], on="statement_id").dropna(subset=["human_hawk"])
    full = d.groupby("meeting_date").filter(lambda g: len(g) >= 5 and g.governor.sum() == 1)
    if full.meeting_date.nunique() < 8:
        return None
    gap = lambda c: full[full.governor == 0].groupby("meeting_date")[c].mean() - full[full.governor == 1].groupby("meeting_date")[c].mean()
    a, b = gap("human_hawk"), gap("hawk_llm")
    return dict(human="gap_human", machine="gap_llm", n=len(a), pearson=pearsonr(a, b)[0], spearman=spearmanr(a, b)[0],
                mae=(a - b).abs().mean(), sign_agree=float((np.sign(a) == np.sign(b)).mean()))


def evaluate(path=None):
    h = pd.read_csv(path or config.TABLES / "human_sample.csv")
    g = _gap_check(h) if (config.PROC / "member_level.csv").exists() else None
    for f in ["scores_llm", "scores_dictionary", "scores_vader", "scores_finbert"]:
        p = config.PROC / f"{f}.csv"
        if p.exists():
            h = h.merge(pd.read_csv(p).drop(columns=["llm_model"], errors="ignore"), on="statement_id", how="left")
    rows = []
    for hc, machines in FIELDS.items():
        for mc in machines + ([hc + "_2"] if hc + "_2" in h else []):
            if mc not in h:
                continue
            d = h[[hc, mc]].dropna().astype(float)
            if len(d) < 10:
                continue
            r = dict(human=hc, machine=mc, n=len(d), pearson=pearsonr(d[hc], d[mc])[0],
                     spearman=spearmanr(d[hc], d[mc])[0], mae=(d[hc] - d[mc]).abs().mean(),
                     within1=((d[hc] - d[mc]).abs() <= 1).mean(), exact=(d[hc].round() == d[mc].round()).mean())
            if mc.endswith(("_llm", "_2")):
                r["kappa_quadratic"] = cohen_kappa_score(d[hc].round().astype(int), d[mc].round().astype(int), weights="quadratic")
            rows.append(r)
    if g:
        rows.append(g)
    out = pd.DataFrame(rows)
    out.to_csv(config.TABLES / "validation.csv", index=False)
    return out


if __name__ == "__main__":
    import sys
    print(draw_sample() if "--draw" in sys.argv else evaluate())

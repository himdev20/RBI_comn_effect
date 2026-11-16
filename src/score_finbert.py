"""FinBERT benchmark (optional; needs transformers+torch and HF access, run locally).
FinBERT measures financial *sentiment*, not hawkishness - kept as a benchmark that
is expected to transfer imperfectly. Score = 2*(P(pos)-P(neg)) (positive ~ dovish
is NOT assumed; sign is flipped so that negative sentiment ~ hawkish risk language
only if --flip is passed; default reports raw sentiment)."""
import sys, pandas as pd
from src import config
def run(path=None, flip=False):
    from transformers import pipeline
    clf = pipeline("text-classification", model="ProsusAI/finbert", top_k=None, truncation=True, max_length=512)
    df = pd.read_csv(path or config.PROC / "member_statements.csv")
    sc = []
    for t in df.statement:
        chunks = [t[i:i+1500] for i in range(0, len(t), 1500)]
        vals = []
        for c in chunks:
            p = {d["label"].lower(): d["score"] for d in clf(c)[0]}
            vals.append(2 * (p.get("positive", 0) - p.get("negative", 0)))
        v = sum(vals) / len(vals)
        sc.append(-v if flip else v)
    out = pd.DataFrame({"statement_id": df.statement_id, "hawk_finbert": sc})
    out.to_csv(config.PROC / "scores_finbert.csv", index=False); return out
if __name__ == "__main__": run(flip="--flip" in sys.argv)

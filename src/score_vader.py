"""VADER benchmark, the measure used by Sil et al. (2023/2024) for RBI 'implicit dissent'.
VADER scores general sentiment (compound in [-1, 1]); it is NOT a hawkishness measure.
Reported so the paper can show what an LLM stance measure adds over the prior literature.
Statement score = mean compound score over sentences, scaled to [-2, 2]."""
import re
import pandas as pd
from src import config


def run(path=None):
    from vaderSentiment.vaderSentiment import SentimentIntensityAnalyzer
    an = SentimentIntensityAnalyzer()
    df = pd.read_csv(path or config.PROC / "member_statements.csv")
    sc = []
    for t in df.statement:
        sents = [s for s in re.split(r"(?<=[.!?])\s+", t) if len(s.split()) > 3]
        sc.append(2 * sum(an.polarity_scores(s)["compound"] for s in sents) / max(len(sents), 1))
    out = pd.DataFrame({"statement_id": df.statement_id, "sent_vader": sc})
    out.to_csv(config.PROC / "scores_vader.csv", index=False)
    return out


if __name__ == "__main__":
    run()

"""Dictionary benchmark: hand-built hawk/dove lexicon (NOT Loughran-McDonald; a
transparent baseline you can extend). Score in [-2, 2] = 2*(H-D)/(H+D).
Whole-word matching (the earlier substring version counted 'ease' inside 'increase')
and a 3-word negation window ('not ... tighten' is not hawkish)."""
import re
import pandas as pd
from src import config

HAWK = ["inflation risk", "inflation risks", "upside risk", "upside risks", "price pressure", "price pressures",
        "tighten", "tightening", "hike", "hikes", "withdrawal of accommodation", "vigilant", "elevated inflation",
        "persistent inflation", "overheating", "second-round", "unanchored", "upside to inflation", "restrictive",
        "remove accommodation", "raise the policy rate", "stickiness", "sticky", "hawkish", "pre-emptive",
        "entrenched", "de-anchoring", "inflation expectations"]
DOVE = ["growth concern", "growth concerns", "downside risk", "downside risks", "downside to growth", "ease",
        "easing", "cut", "cuts", "reduce the policy rate", "accommodative", "accommodation", "support growth",
        "weak demand", "slack", "moderating inflation", "softening", "headroom", "policy space", "space for",
        "lower the policy rate", "dovish", "revive", "stimulus", "subdued", "undershoot", "disinflation",
        "front-load", "benign"]
NEG = re.compile(r"\b(not|no|nor|without|never|hardly)\b")
_PAT = {w: re.compile(rf"\b{re.escape(w)}\b") for w in HAWK + DOVE}


def _count(t, words):
    n = 0
    for w in words:
        for m in _PAT[w].finditer(t):
            window = " ".join(t[:m.start()].split()[-3:])
            if not NEG.search(window):
                n += 1
    return n


def score_text(t: str) -> float:
    t = t.lower()
    h, d = _count(t, HAWK), _count(t, DOVE)
    return 0.0 if h + d == 0 else 2.0 * (h - d) / (h + d)


def run(path=None):
    df = pd.read_csv(path or config.PROC / "member_statements.csv")
    df["hawk_dict"] = df.statement.map(score_text)
    out = df[["statement_id", "hawk_dict"]]
    out.to_csv(config.PROC / "scores_dictionary.csv", index=False)
    return out


if __name__ == "__main__":
    run()

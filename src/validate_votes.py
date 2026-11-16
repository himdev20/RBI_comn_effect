"""Validate the LLM measures against the RECORDED votes (no human coding needed).

1. preferred action: does the LLM's reading of each statement match the member's actual
   vote direction (the decision for Yes voters; the text-stated preference for No voters)?
2. explicit dissenters as a test set for 'reservation' and 'lean': a member who formally
   dissented should be read as having reservations (>=1) and leaning in the dissent direction.
3. the share of yes-voters with reservations ('hidden dissent') vs explicit dissent.
This complements, and does not replace, the human validation sample (validate.py).
"""
import numpy as np
import pandas as pd
from sklearn.metrics import roc_auc_score, cohen_kappa_score
from src import config


def run():
    st = pd.read_csv(config.PROC / "member_level.csv")
    rows = []
    # 1. preferred action vs actual vote
    actual = st.decision_dir.where(st.vote_yes == 1, st.rate_pref_text)
    d = pd.DataFrame({"llm": st.pref_action_llm, "actual": actual}).dropna()
    rows.append(dict(check="LLM preferred action = actual vote direction", n=len(d),
                     value=(d.llm == d.actual).mean(), kappa=cohen_kappa_score(d.actual, d.llm)))
    dn = d[st.loc[d.index, "vote_yes"] == 0]
    rows.append(dict(check="  ... among 'No' voters only", n=len(dn), value=(dn.llm == dn.actual).mean()))
    # 2. explicit dissenters: reservation and lean
    y = st.explicit_dissent
    ok = st.reservation_llm.notna()
    rows.append(dict(check="AUC: reservation score separates explicit dissenters", n=int(ok.sum()),
                     value=roc_auc_score(y[ok], st.reservation_llm[ok])))
    ed = st[st.explicit_dissent == 1]
    rows.append(dict(check="explicit dissenters read as reservation>=1", n=len(ed), value=(ed.reservation_llm >= 1).mean()))
    sd = ed.dropna(subset=["explicit_dir", "lean_llm"])
    sd = sd[sd.lean_llm != 0]
    rows.append(dict(check="lean sign = dissent direction (dissenters with nonzero lean)", n=len(sd),
                     value=(np.sign(sd.lean_llm) == np.sign(sd.explicit_dir)).mean()))
    yc = st[(st.vote_yes == 1) & (st.explicit_dissent == 0)]
    rows.append(dict(check="yes-voters with reservations (hidden dissent rate)", n=len(yc), value=(yc.reservation_llm >= 1).mean()))
    rows.append(dict(check="yes-voters with nonzero lean", n=len(yc), value=(yc.lean_llm != 0).mean()))
    rows.append(dict(check="formal dissent rate (all member-meetings)", n=len(st), value=st.explicit_dissent.mean()))
    # 3. tone vs decisions (face validity of hawkishness)
    for col in ["hawk_llm", "hawk_dict"]:
        g = st.groupby(st.decision_dir)[col].mean()
        rows.append(dict(check=f"mean {col} at cuts / holds / hikes", n=len(st),
                         value=np.nan, note=" / ".join(f"{g.get(k, np.nan):.2f}" for k in (-1, 0, 1))))
    rows.append(dict(check="corr(hawk_llm, hawk_dict)", n=len(st), value=st.hawk_llm.corr(st.hawk_dict)))
    rows.append(dict(check="corr(hawk_llm, VADER sentiment)", n=len(st), value=st.hawk_llm.corr(st.sent_vader)))
    out = pd.DataFrame(rows)
    out.to_csv(config.TABLES / "validation_votes.csv", index=False)
    return out


if __name__ == "__main__":
    print(run().round(3).to_string())

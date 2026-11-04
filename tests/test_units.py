"""Unit tests of individual functions on short literal inputs (no datasets are generated).
They check parsing rules and the algebra of the shock decompositions, nothing empirical."""
import numpy as np
import pandas as pd
from src.parse_minutes import parse_text, parse_decision, html_to_text
from src.members import canonical
from src.score_dictionary import score_text
from src.shocks import gss, jk_rotation
from src.event_study import holm

BODY = "The outlook for growth and inflation was reviewed in detail by the committee. " * 6
TXT = f"""The MPC adopted the resolution that is set out below.
The MPC decided to reduce the policy repo rate by 50 basis points to 5.50 per cent. The MPC also decided to change the stance to neutral.
Voting on the Resolution to reduce the policy repo rate
Member | Vote | Magnitude of policy repo rate reduction (basis points)
Dr. Nagesh Kumar | Yes | 50
Shri Saugata Bhattacharya | Yes | 25
Prof. Jayanth R. Varma | No
Statement by Dr. Nagesh Kumar
17. {BODY}
Statement by Shri Saugata Bhattacharya
22. {BODY}
Statement by Prof. Jayanth R. Varma
30. {BODY}
(Puneet Pancholy)
Chief General Manager
"""


def test_parse_real_layout():
    st, meet = parse_text(TXT, "2025-06-06")
    r = {x["member"]: x for x in st}
    assert set(r) == {"Nagesh Kumar", "Saugata Bhattacharya", "Jayanth Varma"}
    assert r["Saugata Bhattacharya"]["vote_bp"] == 25 and r["Nagesh Kumar"]["vote_bp"] == 50
    assert r["Jayanth Varma"]["vote_yes"] == 0
    assert "Chief General Manager" not in r["Jayanth Varma"]["statement"]
    assert meet["repo_parsed"] == 5.5 and meet["stance_parsed"] == "neutral"


def test_html_table_rows_kept_on_one_line():
    html = "<table><tr><td>Dr. Poonam Gupta</td><td>Yes</td><td>50</td></tr></table>"
    assert "Dr. Poonam Gupta | Yes | 50" in html_to_text(html)


def test_canonical_names_and_roles():
    assert canonical("Dr. Michael Debabrata Patra", "2019-02-07")[2] == "ED_MP"
    assert canonical("Dr. Michael Debabrata Patra", "2021-02-05")[2] == "DG_MP"
    assert canonical("Professor Ram Singh")[0] == "Ram Singh"
    assert canonical("Shri Indranil Bhattacharyya")[0] == "Indranil Bhattacharyya"
    assert canonical("Shri Saugata Bhattacharya")[0] == "Saugata Bhattacharya"
    assert canonical("Dr. Someone New")[1] == "unknown"


def test_parse_decision_hold():
    assert parse_decision("keep the policy repo rate unchanged at 6.50 per cent. The MPC also decided to "
                          "remain focused on withdrawal of accommodation.") == (6.5, "withdrawal of accommodation")


def test_dictionary_word_boundaries_and_negation():
    assert score_text("the increase in prices was a release") == 0          # no 'ease' inside words
    assert score_text("upside risks and persistent inflation") > 0
    assert score_text("there is no need to tighten") == 0
    assert score_text("space for easing to support growth") < 0


def test_gss_path_orthogonal_to_target():
    X = pd.DataFrame({"a": [5, -3, 0, 10, -8, 2, 1, -1, 4, -6],
                      "b": [6, -2, 3, 9, -9, 4, 0, -2, 7, -4],
                      "c": [4, 0, 6, 7, -7, 5, -2, -1, 8, -1]}, dtype=float)
    F, _ = gss(X, "a", "c")
    assert abs(np.corrcoef(F.path, X.a)[0, 1]) < 1e-8                      # path does not move the target rate
    assert abs(np.corrcoef(F.target, F.path)[0, 1]) < 1e-8
    assert abs(np.polyfit(F.target, X.a, 1)[0] - 1) < 1e-8                 # target scaled to bp of 'a'


def test_jk_rotation_adds_up_and_signs():
    i = np.array([5., -3, 2, 8, -6, 1, -2, 4, -1, 3])
    s = np.array([-1., 0.5, 0.8, -2, 1.5, 0.3, 0.2, -0.4, -0.6, 0.9])
    mp, cbi, share = jk_rotation(i, s)
    assert share > 0 and np.allclose(mp + cbi, i)


def test_holm_monotone():
    adj = holm([0.01, 0.04, 0.03])
    assert np.allclose(adj, [0.03, 0.06, 0.06])

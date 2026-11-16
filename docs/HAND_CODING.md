# Hand-coding guide (human validation of the LLM scores)

**Why this matters.** The paper's key regressor is an LLM score, and only one LLM is used.
A referee will ask whether a trained human reads the statements the same way. This exercise
answers that, and it validates the exact quantity used in the regressions: the *within-meeting
gap* between the other members and the Governor.

**What you code.** 120 statements = all six statements from 20 meetings (about two per year).
Names, years and months are masked and rows are shuffled, so you cannot tell who is the
Governor or when the meeting was. Budget **8–10 hours per coder** (3–5 minutes a statement).

## Step 1. Create the sheet
```
python run_pipeline.py validate-draw-meetings
```
This writes `outputs/tables/human_sample.csv` with columns
`row, statement_id, adopted_decision, statement, human_hawk, human_lean, human_reservation`
and three empty `_2` columns for the second coder. The draw is seeded, so it is reproducible.
Do **not** re-run it after coding starts.

## Step 2. Give each coder a private copy
- Copy the file twice: `human_sample_coderA.csv`, `human_sample_coderB.csv`.
- Open in Google Sheets (File → Import) or Excel (Data → From Text/CSV, encoding UTF-8).
  Turn on text wrapping for the `statement` column.
- Coders must not talk about individual statements until both have finished.
- Coders must **not** open `scores_llm.csv`, `member_level.csv`, or any results table first.
  Ideally at least one coder has never seen the regression results.

## Step 3. Read the rules once (docs/CODEBOOK.md), then code three numbers per row
1. **human_hawk** (−2, −1, 0, 1, 2): the policy stance the text argues for.
   −2 clearly wants easing; −1 leans easier; 0 balanced; +1 leans tighter; +2 clearly wants
   tightening. Judge the policy leaning, not whether the economy is described as strong.
2. **human_lean** (−1, 0, 1): compare the text with the `adopted_decision` column.
   0 = reasoning fits the decision; −1 = points looser than the decision; +1 = points tighter.
3. **human_reservation** (0, 1, 2): 0 full support; 1 supports but voices a reservation,
   condition or different emphasis; 2 argues against the decision or the stance.

Practical rules:
- Read the whole statement; the vote is usually in the last paragraph.
- Enter integers only. Leave nothing blank; if unsure, pick the closest value and put a note
  in a spare column called `note`.
- Do not look up what happened at later meetings.
- Do a **pilot of 10 rows** first (rows 1–10). Both coders compare *only their difficulties
  with the rules* (not their answers), the codebook is clarified if needed, and then rows
  11–120 are coded without further discussion. Report the pilot in the paper.
- Code in sessions of at most 20–25 statements; fatigue lowers agreement.

## Step 4. Combine the two coders
Rows are in the same order in both copies. In coder A's file, paste coder B's three columns
into `human_hawk_2`, `human_lean_2`, `human_reservation_2`. Save as **CSV (UTF-8)** to
`outputs/tables/human_sample.csv`. Keep the two original copies unchanged as the audit trail.

## Step 5. Compute agreement
```
python run_pipeline.py validate
```
Output: `outputs/tables/validation.csv`, with for every score: Pearson, Spearman, mean absolute
error, share within one point, exact agreement and quadratic-weighted kappa, for
(a) human vs LLM, (b) human vs dictionary and VADER, (c) coder A vs coder B, and
(d) the row `gap_human` vs `gap_llm`: the meeting-level gap (members minus Governor) from the
human codes against the LLM gap, with the share of meetings where the sign agrees.

## Step 6. How to read the result
| Statistic | Good | Worry |
|---|---|---|
| Coder A vs B, weighted kappa on `human_hawk` | ≥ 0.70 | < 0.60: the codebook is unclear; clarify and recode a fresh sample |
| Human vs LLM, weighted kappa on `human_hawk` | ≥ 0.65 (near the human–human figure) | well below human–human |
| `gap_human` vs `gap_llm` correlation (20 meetings) | ≥ 0.6, sign agreement ≥ 75% | < 0.4: the regressor itself is not validated |
| Human vs LLM on `human_reservation` | kappa ≥ 0.5 | hidden-dissent rates should then be reported with caution |

Report all numbers whatever they are. Only **after** `validate` has been run may the coders
discuss disagreements and add a `consensus` column (optional; used for a robustness row).

## Step 7. What goes in the paper
- Sample design (20 whole meetings, stratified by year, masked, shuffled), coder background,
  hours spent, the pilot, and the full `validation.csv` table.
- The headline regression re-estimated on the 20 coded meetings is not informative (n = 20);
  the validation is about measurement, not about the result.

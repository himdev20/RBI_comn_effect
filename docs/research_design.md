# Pre-analysis plan (freeze before running on real data)

**Working title:** *What the Minutes Reveal: Decision-Day Surprises, Hidden Dissent and the
Indian Yield Curve*

## Question
RBI announces decisions and named votes on decision day, then publishes each member's
attributed statement 14 days later. Does that later text carry news for markets *beyond the
decision-day surprise*? Does it reveal disagreement that predicts future policy surprises?

## Contribution (verify the novelty checks in CHECKLIST.md first)
1. A 2016–2026 RBI decision-day surprise series (target/path; monetary-policy vs
   information shocks; purged). The last public series found ends in December 2020.
2. The first systematic event study of MPC minutes releases in India, using member-level
   LLM measures (stance, lean vs the adopted decision, reservations) validated against
   human coding.
3. Linkage tests: which decision days generate disagreement, and whether the minutes make
   later surprises predictable.

## Measures
- **Decision-day surprises** (`shocks.py`):
  - GSS target and path factors from OIS 1m–2y (T-bill fallback);
  - Jarociński–Karadi split using Nifty;
  - Bauer–Swanson purge;
  - poll surprise;
  - stance change.
- **Minutes surprise** = mean hawkishness of the five non-Governor members − the Governor's
  own minutes statement. Same genre; the Governor's view is public on decision day.
- **Hidden dissent** among members who voted with the majority:
  - signed = mean LLM `lean` (−1/0/+1);
  - share = fraction with `reservation` ≥ 1.
- **Explicit dissent** (No votes, magnitude, stance) is public on decision day: a control,
  not news.

## Primary hypotheses and tests (fixed in advance)
| # | hypothesis | outcome | test |
|---|---|---|---|
| H1 | Minutes days are informative | daily changes of 1y OIS (or 364d T-bill) and 2y G-sec | variance ratio vs matched ordinary days, stratified permutation p |
| H2 | Hawkish minutes surprise raises short/medium yields beyond the decision-day surprise | dy1 of 1y OIS, 2y G-sec | `with_shocks` spec, randomization-inference p |
| H3 | Signed hidden dissent moves yields in its direction | same | same spec |
| H4 | Minutes text predicts next decision-day surprise (markets under-use minutes) | next target / path | `linkage` L3, randomization-inference p |

Primary tenor: **1y OIS** (if unavailable: 364d T-bill). Primary window: 1 day.
All other tenors, windows, equity/FX outcomes and specifications are **secondary** and
reported with Holm-adjusted p-values across tenors.

## Secondary / exploratory
- Uncertainty channel: |dy| on hidden-dissent share and dispersion.
- L1: information-type decision days → more disagreement in minutes.
- Next-decision predictability vs market pricing.
- Internal vs external members; DG in charge of monetary policy; governor eras; MPC
  compositions (2016–20, 2020–24, 2024–).

## Robustness (all pre-listed)
- 2-day window.
- Ex-COVID (Mar 2020–Dec 2021).
- Drop unscheduled meetings.
- Drop CPI/other-event overlap days.
- Dictionary and VADER instead of the LLM.
- `RBI_SURPRISE=res` / `roll`.
- Purged shocks.
- Pre-event-day placebo; random-day placebo.

## Threats
- **Small N (about 60).** Use exact/randomization inference, one primary tenor, and report
  nulls as nulls.
- **Daily windows contain other news.** Use global controls aligned to IST closes, a CPI
  flag and an other-events flag; intraday data is the long-run fix.
- **LLM look-ahead.** Names and dates are masked, the model is pinned, and results are
  compared with dictionary/VADER. A model whose training cutoff predates the sample's end
  could "know" outcomes; report the model id and its cutoff.
- **Benchmark roll-overs in yield series; FX intervention muting INR responses.**
- **Construct validity of "hidden dissent"** comes from human validation; kappa is reported.

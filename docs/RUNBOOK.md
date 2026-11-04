# Runbook: from raw data to results

All commands are run from the repository root. Every run is logged to `pipeline.log`.

## 0. Set up (once)
```bash
python -m venv .venv && source .venv/bin/activate      # Windows: .venv\Scripts\activate
pip install -r requirements.txt                          # torch/transformers only if you want FinBERT
python -m pytest -q tests                                # 8 unit tests should pass
```

## 1. Freeze the analysis plan
Read `docs/research_design.md` and change anything you disagree with **now**. Then commit it
(`git tag pre-analysis-plan`). From here on, any change of specification is reported as such.

## 2. Market data
1. Put the downloads in `data/raw/market/downloads/` and edit `data/raw/market/series_map.csv`.
2. `python run_pipeline.py market` prints the coverage per series. Check the first and last
   dates and that yields look like 4–9 (percent), not 400–900.

## 3. Minutes
1. Put the PDFs in `data/raw/minutes_html/` (or fill `url` and run `python run_pipeline.py scrape`).
2. `python run_pipeline.py parse --debug` prints each meeting's statement and vote count.
   **Every meeting should show 6 statements and 6 votes.** If an older meeting shows fewer:
   - Open `data/processed/meeting_texts.csv` and the PDF, and look at how statement headers
     and the vote table are written there.
   - Adjust `HEADER_RE` / `VOTE_HEAD_RE` in `src/parse_minutes.py`, or send me the
     header lines and I will adjust it.
   - Unknown member names are listed by `check`. Add them to `src/members.py`.

## 4. Verify the meeting table
1. Fill/verify `decisions.csv`, `minutes_urls.csv` (release dates), `dissent_direction.csv`.
2. `python run_pipeline.py check` lists every problem and writes `outputs/tables/data_check.md`.
   Repeat until there is no FAIL.

## 5. Text scores
```bash
python run_pipeline.py score --vader                     # dictionary + VADER (free, seconds)
export ANTHROPIC_API_KEY=...  RBI_LLM_MODEL=<exact model id>
python run_pipeline.py score --llm --limit=10            # smoke test: inspect data/processed/scores_llm.csv
python run_pipeline.py score --llm --vader               # full run (cached; safe to re-run)
```

## 6. Human validation (before looking at any market result)
1. `python run_pipeline.py validate-draw` writes `outputs/tables/human_sample.csv` (60 statements).
2. Code `human_hawk`, `human_lean`, `human_reservation` using `docs/CODEBOOK.md`, without
   looking at the machine scores. A second coder fills the `_2` columns.
3. `python run_pipeline.py validate` gives agreement statistics.
   Rule of thumb: quadratic-weighted kappa ≥ 0.6 for `hawk_llm` before relying on it.

## 7. Decision-day surprises
`python run_pipeline.py shocks` writes `data/processed/shocks.csv` and
`outputs/tables/shock_diagnostics.csv`. Look at:
- the factor set used (OIS or the T-bill fallback);
- the share of variance from the first two components;
- the share of "information" events;
- the purge R².

## 8. Build and analyse
```bash
python run_pipeline.py build
python run_pipeline.py analyze --B=5000      # randomization inference / bootstrap draws
python run_pipeline.py figures
python run_pipeline.py report                # outputs/summary.md
```
`python run_pipeline.py all --llm` runs parse → report in one go once everything above works.

## 9. What to send back for the analysis discussion
- `outputs/summary.md` (all key tables)
- `outputs/figures/*.png`
- `outputs/tables/*.csv`
- `pipeline.log`
- If something crashed: the full error message and the stage you ran.

## Switches
| variable | values | effect |
|---|---|---|
| `RBI_SCORE` | `hawk_llm` (default), `hawk_dict` | which hawkishness score drives the measures |
| `RBI_SURPRISE` | `gov` (default), `res`, `roll` | minutes surprise: others vs Governor / members vs resolution / vs prior 4 meetings |
| `RBI_DROP_UNSCHEDULED` | `1` | drop off-cycle meetings in decision-day regressions |
| `RBI_HIDDEN_THR` | e.g. `0.75` | threshold for the non-LLM hidden-dissent fallback |
| `RBI_ALLOW_UNVERIFIED` | `1` | dry runs only; never for reported results |

## Output map
| file | content |
|---|---|
| `tables/variance_test.csv` | Stage A: volatility on minutes days vs matched ordinary days (and decision days) |
| `tables/event_study.csv` | Stage B: directional effects by tenor, spec, window; HC3, randomization-inference, Holm p-values |
| `tables/uncertainty.csv` | Stage C: \|Δy\| on hidden-dissent share and dispersion |
| `tables/placebo_preday.csv`, `placebo_coefs.csv` | placebos |
| `tables/subsamples.csv` | ex-COVID, governors, MPC compositions |
| `tables/shock_diagnostics.csv`, `decision_day.csv` | decision-day surprise series and its validation |
| `tables/linkage.csv` | L1 (shock type → disagreement), L3/L4 (minutes → next surprise) |
| `tables/predictability.csv` | next decision vs persistence / market pricing |
| `tables/validation.csv` | human vs machine agreement |

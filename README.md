# What the Minutes Reveal: Decision-Day Surprises, Hidden Dissent and the Indian Yield Curve

**Status:** the code is complete and unit-tested on short literal inputs (8 tests). It has
**not yet been run on real data**, and no result about India exists yet.

## Design in one paragraph
For every MPC meeting from 2016 to 2026 we build a decision-day surprise series:
- GSS target and path factors from OIS (T-bill fallback);
- a Jarociński–Karadi split into monetary-policy and central-bank-information shocks;
- a Bauer–Swanson purge;
- a poll surprise and stance changes.

From the minutes, published 14 days later at 17:00 IST, we measure each member's statement
with an LLM, validated against human coding: stance, lean relative to the adopted decision,
and reservations among those who voted yes ("hidden dissent").

We then test four things:
1. **Stage A:** whether yields are more volatile on minutes-reaction days than on matched
   ordinary days.
2. **Stage B:** whether the minutes surprise and hidden dissent move the curve beyond the
   decision-day surprise.
3. **Stage C:** whether disagreement raises the size of moves.
4. **Linkage:** which kind of decision day produces disagreement, and whether the minutes
   make the *next* decision-day surprise predictable.

## Documents
| file | read it for |
|---|---|
| `docs/DATA_GUIDE.md` | every dataset: source, format, where it goes |
| `docs/RUNBOOK.md` | the commands, in order, and what to check after each |
| `docs/research_design.md` | pre-analysis plan: hypotheses, primary tests, robustness |
| `docs/CODEBOOK.md` | hand-coding rules for the validation sample |
| `docs/CHECKLIST.md` | novelty checks, data integrity, things easy to miss |

## Quick start
```bash
pip install -r requirements.txt && python -m pytest -q tests
python run_pipeline.py market      # after placing downloads + editing series_map.csv
python run_pipeline.py parse --debug
python run_pipeline.py check       # repeat until no FAIL
python run_pipeline.py score --llm --vader
python run_pipeline.py validate-draw   # hand-code, then: python run_pipeline.py validate
python run_pipeline.py shocks && python run_pipeline.py build
python run_pipeline.py analyze && python run_pipeline.py figures && python run_pipeline.py report
```

## Code map
| module | role |
|---|---|
| `src/assemble_market.py` | downloaded files → `yields.csv` |
| `src/scrape_minutes.py`, `src/parse_minutes.py` | minutes → statements, votes (incl. magnitude), resolution, parsed repo/stance |
| `src/members.py` | member registry and roles (Governor, DG in charge of MP, ED, external) |
| `src/score_llm.py`, `score_dictionary.py`, `score_vader.py`, `score_finbert.py` | text measures |
| `src/validate.py` | human vs machine agreement |
| `src/shocks.py`, `src/decision_day.py` | decision-day surprise series and its validation |
| `src/build_dataset.py` | member/meeting/day tables, timing, controls, hidden/explicit dissent |
| `src/event_study.py` | Stage A–C, placebos, subsamples |
| `src/linkage.py`, `src/predictability.py` | combined tests and next-decision prediction |
| `src/figures.py`, `src/report.py`, `src/check_data.py` | figures, `outputs/summary.md`, input checks |

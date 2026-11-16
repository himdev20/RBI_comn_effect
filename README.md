# Whose Words Move Rates? Attributed Member Statements in RBI Minutes and the Indian Yield Curve

India's Monetary Policy Committee publishes each member's signed statement 14 days after
every decision. This repository tests whether that text moves interest rates beyond the
decision itself, and whose words matter. It covers all 62 meetings from October 2016 to
October 2026 and runs end to end from raw public data.

**Status: working paper in progress.** Full results are in [`RESULTS.md`](RESULTS.md); the
draft is in [`paper/draft.md`](paper/draft.md).

## Findings

| Finding | Evidence | Status |
|---|---|---|
| When the other members sound more hawkish than the Governor, short OIS rates rise on minutes day | +2.0 bp (6-month, p = 0.003) and +2.3 bp (1-year, p = 0.015) per one-point gap; placebos null | Holds; weaker outside 2020–21; rests on one LLM |
| The effect comes from internal RBI members | Internal +3.5 bp vs external +0.2 bp on 1-year OIS; equality rejected (p = 0.025) | Holds for OIS |
| It is the gap to the Governor, not the tone level | Members +, Governor −, equal and opposite not rejected | Holds |
| Hidden dissent (yes-voters with reservations) is common but not priced | 15.1% of yes-votes vs 10.8% formal dissents | Null result |
| External members' dissent votes lead the repo rate by 3–4 meetings | +16 to +24 bp per net dissent in the full sample; absent outside COVID | Exploratory |

Relation to earlier work: Mahambare & Pathak (2021) regress next-day bond yields on tone
levels for 30 meetings and find external members matter more. We reproduce the flavour of
that result in their sample and show it does not carry over to the news measure, to OIS, or
to the later sample (`RESULTS.md`, section 8).

## What is not done yet
- Human validation of the LLM scores: [`docs/HAND_CODING.md`](docs/HAND_CODING.md).
- Same-model prompt and look-ahead checks: `python run_pipeline.py llm-checks`.

## Run it
```
pip install -r requirements.txt
python download_data.py                 # RBI minutes, FBIL rates, FRED series
# add the Investing.com files listed in docs/DATA_GUIDE.md to data_downloads/
python run_pipeline.py market
python run_pipeline.py parse
python run_pipeline.py check
$env:GEMINI_API_KEY = "..."             # PowerShell; never commit keys
$env:RBI_LLM_MODEL = "gemini-3.5-flash-lite"
python run_pipeline.py score --llm --vader
python run_pipeline.py llm-checks       # optional but recommended
python run_pipeline.py shocks
python run_pipeline.py build
python run_pipeline.py analyze
python run_pipeline.py figures
python run_pipeline.py report
python -m pytest -q tests
```
Details: [`docs/RUNBOOK.md`](docs/RUNBOOK.md), [`docs/DATA_GUIDE.md`](docs/DATA_GUIDE.md).

## Layout
| Path | Contents |
|---|---|
| `src/parse_minutes.py`, `members.py` | Minutes → attributed statements and votes |
| `src/score_llm.py`, `score_dictionary.py`, `score_vader.py` | Text measures; same-model checks |
| `src/shocks.py`, `decision_day.py` | Decision-day target/path and policy/information shocks |
| `src/event_study.py`, `robustness.py` | Minutes-day event study, placebos, robustness |
| `src/extensions.py` | News vs level, internal vs external, COVID interaction, Mahambare–Pathak replication, non-LLM measures, persistence, jackknife, forecasting tests |
| `src/validate.py`, `validate_votes.py` | Human-coding sheet and agreement; validation against votes |
| `outputs/tables`, `outputs/figures` | All results |
| `data/raw/decisions.csv`, `minutes_urls.csv` | Hand-verified decisions and release dates |

## Data and licences
Minutes are public RBI documents. Market data from Investing.com and FBIL are not
redistributed; `download_data.py` and `docs/DATA_GUIDE.md` rebuild them. Code: MIT licence.

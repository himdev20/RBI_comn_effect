# Whose Words Move Rates? Attributed Member Statements in RBI Minutes and the Indian Yield Curve

**Status (November 2026):** working paper in progress. The full pipeline runs end to end on
real data for all 62 Monetary Policy Committee (MPC) meetings from October 2016 to October 2026.
The headline result holds up under placebo and robustness tests. Human validation of the text
measure has not yet been done. Full numbers are in [`RESULTS.md`](RESULTS.md); the draft
paper is in [`paper/draft.md`](paper/draft.md).

Supervisor: Prof. Sanjiv Kumar, IIT Kanpur.

---

## 1. The question

The Reserve Bank of India announces each MPC decision and the named vote count on decision
day. Fourteen days later, at 17:00 IST (after Indian bond markets close), it publishes the
minutes. The minutes contain a **signed statement by each of the six members**: the Governor,
the Deputy Governor, an Executive Director, and three external members appointed by the
government. Only a handful of central banks attribute statements to named members this way.

The Governor explains the decision publicly on decision day, so his view is already known.
The new information in the minutes is **how far the other members stand from him**. The
project asks:

1. Does that gap move interest rates when the minutes come out?
2. Whose words matter: the RBI's own internal members or the external members?
3. Do members who vote with the majority but voice reservations ("hidden dissent") reveal
   anything the market prices?

## 2. How the project got here

| Stage | What happened |
|---|---|
| Starting point | An earlier version ("say vs vote") was built on mock data and focused on hidden dissent. |
| Gap search | A literature review found that hidden dissent in RBI minutes had already been measured (Sil et al. 2024; Kumar, Sil, Kurup and Paramanik 2025). The project was redirected to a minutes-day event study combined with an updated decision-day surprise series. |
| Real data | Minutes scraped from the RBI website; OIS, T-bill and FX rates from FBIL; G-sec yields, Nifty and India VIX from Investing.com; US 10-year, VIX and Brent from FRED. |
| Measurement | Statements parsed and scored by a name- and date-masked LLM (Gemini, temperature 0), with dictionary and VADER benchmarks. |
| First results | The members-minus-Governor gap moves short OIS rates; the effect comes from internal members. |
| Second literature check | Mahambare and Pathak (2021) had already regressed next-day bond yields on member tone for 30 meetings to August 2021. The "first minutes-day study in India" claim was dropped; the contribution was repositioned (section 6). |
| Extensions | News vs level, COVID interaction, leave-one-out, persistence, non-LLM measures, a Mahambare–Pathak replication, and exploratory forecasting tests. |
| Recheck | All results rebuilt from raw data. The forecasting result was found to be fragile and is now reported as exploratory. |
| Current | This repository: headline result, honest status of every claim, human-coding materials ready. |

## 3. Data

| Source | Series | Coverage | Events used |
|---|---|---|---|
| RBI website | MPC minutes (HTML), decisions, release dates | Oct 2016 – Oct 2026 | 62 meetings, 372 statements |
| FBIL | OIS 1m–5y, T-bills 91/182/364-day, USD/INR | OIS from Apr 2018 | 51–53 for OIS |
| Investing.com | G-sec 1/2/5/10-year, Nifty 50, India VIX | 2016 – 2026 | 62 |
| FRED | US 10-year yield, VIX, Brent | 2016 – 2026 | controls |

`data/raw/decisions.csv` has all 62 decisions, each checked by hand against the minutes text.
Licensed market data are **not** redistributed; `download_data.py` and
[`docs/DATA_GUIDE.md`](docs/DATA_GUIDE.md) rebuild them.

## 4. Method

**Parsing.** Each set of minutes is split into six attributed statements with the member's
vote (and dissent size, where stated). All 62 meetings parse to exactly six statements and
six votes.

**Text measure.** A temperature-zero LLM reads each statement with names, years and months
masked and returns hawkishness (−2 to +2), preferred action, lean relative to the adopted
decision, a reservation score, the signalled next move, and uncertainty and conditionality
scores. Every response is cached by a hash of the prompt and model for reproducibility.

**The regressor.** *Surprise* = mean hawkishness of the five non-Governor members minus the
Governor's. Split into internal (Deputy Governor, Executive Director) and external gaps.

**Decision-day shocks.** Gürkaynak–Sack–Swanson target and path factors from the yield curve
on decision days, split into policy and information shocks with Jarociński–Karadi sign
restrictions. These enter as controls, so the minutes-day effect is measured beyond what
the decision itself revealed.

**Event study.** Yield change on the first trading day after release on the surprise,
decision-day shocks, signed hidden dissent, US 10-year, VIX, Brent and a CPI-day dummy.
HC3 errors, randomisation inference, Holm correction across outcomes, pre-release-day and
random-day placebos, leave-one-meeting-out and leave-one-year-out.

## 5. Results

### 5.1 Measurement checks

- The LLM's preferred action equals the recorded vote in **369 of 369** cases.
- The reservation score separates the **40 formal dissenters** from the rest with an AUC of 0.977.
- The sign of the lean matches the dissent direction for 92.5% of dissenters.
- Mean LLM hawkishness at cuts / holds / hikes: −1.55 / 0.08 / 1.20.
- Hidden dissent: **15.1%** of yes-votes carry a reservation, against a 10.8% formal dissent rate.

### 5.2 Decision-day surprise series

- 62 events; first component explains 79% of the variance in decision-day yield changes.
- 42% of decisions have the sign pattern of an information effect.
- Used as controls in every minutes-day regression.

### 5.3 Status of every claim

| Claim | Evidence | Status |
|---|---|---|
| A hawkish members-minus-Governor gap raises short OIS rates on minutes day | Per 1-point gap: 6-month +2.0 bp (p = 0.003), 1-year +2.3 bp (p = 0.015), 2-year +2.0 bp (p = 0.049); 10-year G-sec +0.7 bp (p = 0.59) | **Holds** |
| The effect comes from internal RBI members | 1-year OIS: internal +3.5 bp (p = 0.006), external +0.2 bp (p = 0.68); equality rejected (p = 0.025). Mostly the Deputy Governor | **Holds for OIS**; in the 1-year G-sec the external gap is the significant one |
| It is the gap (news), not the tone level | Members +1.6, Governor −2.2 on 1-year OIS; equal-and-opposite not rejected (p = 0.54) | **Holds** |
| Hidden dissent is priced | No effect on short rates (1-year OIS p = 0.29) | **Not supported** |
| The minutes help predict the next decision | No improvement over a votes-only model | **Not supported** |
| External members' words forecast the repo rate 3–4 meetings ahead | +17 to +24 bp, p = 0.05–0.08; none outside COVID | **Fragile** |
| External members' formal dissent votes forecast the repo rate (no LLM needed) | +16.5 bp at 3 meetings (p = 0.025), +24 bp at 4 (p = 0.03); strong after 2022; none outside COVID | **Exploratory** |
| Markets under-use the minutes | No OIS drift to the next meeting (p = 0.44) | **Not supported** |

### 5.4 How robust is the headline?

| Check | Result |
|---|---|
| Day-before-release placebo | Null (1-year OIS −0.3 bp, p = 0.65) |
| Random-day placebo | Real 1-year coefficient beats 99.6% of draws |
| Randomisation inference | 1-year p = 0.007; 6-month p < 0.001 |
| Multiple testing (Holm, all outcomes) | Only the 6-month result survives (p = 0.043) |
| Drop any one meeting | 6-month and 1-year stay significant at 5% |
| Persistence | Cumulative 1-year response grows to about 3.4 bp after five days; no reversal |
| COVID window (2020–21) | 4.8 bp in the 11 COVID meetings vs 1.7 bp outside (p = 0.24); difference p = 0.10 |
| Other text measures | Dictionary and a vote-trained bag-of-words score do **not** reproduce it |
| Volatility | Minutes days are only mildly more volatile than normal days (1-year OIS variance ratio 1.75, p = 0.08): the text explains the direction of moves, not their size |

**Bottom line:** the result is real in the full sample and passes the timing and chance
tests, but it is concentrated in 2020–21 and depends on one LLM.

## 6. Contribution relative to existing work

| Paper | What they do | What this project adds |
|---|---|---|
| Mahambare and Pathak (2021), *Economics Letters* | Next-day G-sec yields on internal and external tone **levels**, 30 meetings to Aug 2021; external tone matters more | News measure (gap to the Governor), OIS, twice the sample, decision-day shock controls, placebos. Their pattern reproduces in their own sample and design (external +3.4 bp on the 2-year G-sec, p = 0.03) but not after Aug 2021 or with the news measure |
| Sil et al. (2024); Kumar, Sil, Kurup and Paramanik (2025) | Disagreement between statements and votes in RBI minutes | LLM measure validated against the vote record; shows hidden dissent is not priced |
| Lakdawala and Sengupta | RBI decision-day surprises to early 2023 | Target/path series with an information split extended to 2026 |
| FOMC and Riksbank minutes studies | Minutes-day reactions with unattributed or aggregate text | Prices the content of named members' statements |

## 7. What is done and what is not

**Done**
- Scraping, parsing and hand-verified decisions for all 62 meetings.
- LLM, dictionary and VADER scoring; validation against recorded votes.
- Decision-day surprise series with policy/information split.
- Minutes-day event study with full robustness, placebos and extensions.
- Mahambare–Pathak replication; exploratory forecasting and dissent tests.
- 8 unit tests (all pass); results generated straight into `RESULTS.md`.

**Built but not yet run on real data**
- `python run_pipeline.py llm-checks`: a second prompt with the same model (no decision
  context) and a date-guessing look-ahead probe. Tested only with a stub.
- `python run_pipeline.py validate-draw-meetings`: the 120-statement hand-coding sheet is
  generated and ready.

**Not done**
- Two-coder human validation (guide: [`docs/HAND_CODING.md`](docs/HAND_CODING.md)).
- A literature check on whether RBI dissent votes predicting policy is already known.
- Intraday OIS data for a tighter event window.
- Final reference list and author details (`LICENSE`, `CITATION.cff`).

## 8. Known limitations

- **One LLM.** The headline is not reproduced by non-LLM measures. The same-model checks and
  human validation are the planned remedy.
- **Small sample.** About 50 OIS events; many outcomes tested.
- **COVID concentration.** The effect is strongest in 2020–21.
- **Daily data.** Other news on the reaction day can add noise.
- **Look-ahead risk.** The LLM was trained after the sample; masking reduces but does not remove this.

## 9. Next steps

1. Two-coder hand validation of 120 statements.
2. Run `llm-checks` with the same Gemini model, then `analyze` again.
3. Search the literature on RBI dissent votes predicting policy before developing that section.
4. Finish the draft around the pricing result, with the forecasting work as a clearly
   exploratory section.
5. Target journal: *Emerging Markets Review* (primary).

## 10. How to run

```powershell
pip install -r requirements.txt
python download_data.py                       # RBI minutes, FBIL rates, FRED series
# put the Investing.com files listed in docs/DATA_GUIDE.md in data_downloads/
python run_pipeline.py market                 # assemble market data
python run_pipeline.py parse                  # minutes -> statements and votes
python run_pipeline.py check                  # fix any FAIL before going on
$env:GEMINI_API_KEY = "..."                   # never commit keys
$env:RBI_LLM_MODEL  = "gemini-3.5-flash-lite"
python run_pipeline.py score --llm --vader    # text scores (cached)
python run_pipeline.py llm-checks             # same-model robustness (optional)
python run_pipeline.py shocks                 # decision-day surprises
python run_pipeline.py build                  # merge everything
python run_pipeline.py analyze                # all regressions and tests
python run_pipeline.py figures
python run_pipeline.py report
python -m pytest -q tests
```

Hand validation:
```powershell
python run_pipeline.py validate-draw-meetings # creates outputs/tables/human_sample.csv
# code it following docs/HAND_CODING.md, then:
python run_pipeline.py validate               # writes outputs/tables/validation.csv
```

Step-by-step instructions: [`docs/RUNBOOK.md`](docs/RUNBOOK.md).

## 11. Repository layout

| Path | Contents |
|---|---|
| `run_pipeline.py` | Stage runner |
| `download_data.py` | Downloads RBI minutes, FBIL and FRED data |
| `src/parse_minutes.py`, `src/members.py` | Minutes → attributed statements and votes; member registry |
| `src/score_llm.py`, `score_dictionary.py`, `score_vader.py` | Text measures; same-model checks |
| `src/shocks.py`, `src/decision_day.py` | Decision-day target/path and policy/information shocks |
| `src/build_dataset.py` | Member-, meeting- and daily-level datasets |
| `src/event_study.py`, `src/robustness.py` | Minutes-day event study, placebos, robustness |
| `src/extensions.py` | News vs level, internal vs external, COVID interaction, Mahambare–Pathak replication, non-LLM measures, persistence, jackknife, forecasting and drift tests |
| `src/linkage.py`, `src/predictability.py` | Links to future decisions; forecasting the next decision |
| `src/validate.py`, `src/validate_votes.py` | Hand-coding sheet and agreement; validation against votes |
| `outputs/tables/`, `outputs/figures/` | All results |
| `RESULTS.md` | Every number in one place |
| `paper/draft.md` | Working draft |
| `docs/` | Data guide, runbook, codebook, hand-coding guide, research design |
| `tests/` | Unit tests |

## 12. Data and licence

RBI minutes are public documents. Investing.com and FBIL data are not redistributed.
Code is released under the MIT licence.

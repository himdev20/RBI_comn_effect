# Results: end-to-end run on real data (62 MPC meetings, Oct 2016 – Oct 2026)

Every number below is produced by `python run_pipeline.py analyze` and stored in
`outputs/tables/`. Yield changes are in basis points on the first trading day after the
minutes are released (minutes come out at 17:00, after the market closes). "Gap" or
"surprise" = mean LLM hawkishness (−2…+2) of the five non-Governor members minus the
Governor's. OIS data start in 2018, so OIS regressions use 51–53 meetings.

## 1. Status of each claim

| Claim | Status |
|---|---|
| The members-minus-Governor gap moves 6-month to 2-year OIS rates on minutes day | **Holds** in the full sample; survives placebos, randomisation inference and leave-one-out. Weaker outside 2020–21 and dependent on one LLM |
| The effect comes from internal RBI members, not external members | **Holds** for OIS (equality rejected at 5% for 6m–2y); in the 1-year G-sec the external gap is the significant one |
| It is the gap (news) rather than the tone level | **Holds**: members enter positively, the Governor negatively, equal-and-opposite not rejected |
| Hidden dissent is priced | **Not supported** at the short end |
| The text helps predict the next decision | **Not supported** |
| External members' words forecast the repo path 3–4 meetings ahead | **Exploratory, fragile**: borderline in the full sample, absent outside COVID |
| External members' formal dissent votes forecast the repo path (no LLM) | **Exploratory**: significant in the full sample and after 2022, absent outside COVID |
| Markets under-use the minutes (drift afterwards) | **Not supported** |

## 2. Measurement

- 62 minutes parsed into 372 attributed statements, six per meeting, all votes matched.
- LLM preferred action equals the recorded vote in 369 of 369 cases; the reservation score
  separates the 40 formal dissenters with AUC 0.977; the sign of the lean matches the dissent
  direction in 92.5%.
- Mean LLM hawkishness at cuts / holds / hikes: −1.55 / 0.08 / 1.20 (dictionary: −1.17 / −0.30 / 0.63).
- Hidden dissent: 15.1% of yes-votes carry a reservation, against a 10.8% formal dissent rate.
- **Human validation has not been done yet.** See `docs/HAND_CODING.md`.

## 3. Are minutes days different at all? (no text needed)

| tenor | n | variance ratio vs ordinary days | p (matched permutation) |
|---|---|---|---|
| ois_6m | 53 | 1.61 | 0.236 |
| ois_1y | 53 | 1.75 | 0.083 |
| ois_2y | 53 | 1.23 | 0.396 |
| gsec_10y | 62 | 1.40 | 0.193 |

Minutes days are only mildly more volatile than ordinary days. The result is in the
direction, not the size, of the moves.

## 4. Headline: gap → yields on minutes day

Controls: decision-day target and path shocks, signed hidden dissent, US 10-year, VIX, Brent, CPI-day dummy. HC3 errors.

| tenor | bp per 1-point gap | p | p (randomisation) | p (Holm, all outcomes) | n |
|---|---|---|---|---|---|
| ois_3m | 1.28 | 0.022 | 0.019 | 0.261 | 51 |
| ois_6m | 1.96 | 0.003 | 0.000 | 0.043 | 53 |
| ois_1y | 2.25 | 0.015 | 0.007 | 0.211 | 53 |
| ois_2y | 2.04 | 0.049 | 0.036 | 0.534 | 53 |
| ois_5y | 1.97 | 0.089 | 0.059 | 0.889 | 53 |
| gsec_1y | 4.33 | 0.020 | 0.006 | 0.254 | 62 |
| gsec_10y | 0.70 | 0.585 | 0.536 | 1.000 | 62 |

- Pre-release-day placebo: 6m 0.15 (p = 0.78), 1y −0.29 (p = 0.65), 2y 0.51 (p = 0.48).
- Random-day placebo: the 1-year coefficient exceeds 99.6% of 1,000 random-day draws.
- Only the 6-month result survives the Holm correction across all outcomes.

## 5. Internal versus external members

| sample | tenor | b_internal | p_internal | b_external | p_external | p_equal | n |
|---|---|---|---|---|---|---|---|
| full | ois_3m | 1.68 | 0.018 | 0.26 | 0.497 | 0.122 | 51 |
| full | ois_6m | 2.89 | 0.004 | 0.26 | 0.552 | 0.033 | 53 |
| full | ois_1y | 3.51 | 0.006 | 0.21 | 0.682 | 0.025 | 53 |
| full | ois_2y | 3.37 | 0.009 | 0.12 | 0.834 | 0.032 | 53 |
| full | ois_5y | 3.34 | 0.018 | 0.08 | 0.908 | 0.058 | 53 |
| full | gsec_1y | 1.66 | 0.329 | 2.63 | 0.033 | 0.649 | 62 |
| full | gsec_10y | 0.99 | 0.410 | 0.18 | 0.849 | 0.610 | 62 |
| ex-COVID | ois_3m | 1.28 | 0.351 | -0.06 | 0.881 | 0.331 | 40 |
| ex-COVID | ois_6m | 2.82 | 0.047 | -0.16 | 0.724 | 0.059 | 42 |
| ex-COVID | ois_1y | 3.27 | 0.115 | -0.38 | 0.505 | 0.095 | 42 |
| ex-COVID | ois_2y | 3.05 | 0.160 | -0.53 | 0.422 | 0.109 | 42 |
| ex-COVID | ois_5y | 2.98 | 0.207 | -0.51 | 0.512 | 0.164 | 42 |
| ex-COVID | gsec_1y | 1.87 | 0.310 | 1.43 | 0.350 | 0.864 | 51 |
| ex-COVID | gsec_10y | 0.57 | 0.736 | -0.42 | 0.701 | 0.653 | 51 |

## 6. News or tone level?

| tenor | b_members | p_members | b_governor | p_governor | p (members = −Governor) | n |
|---|---|---|---|---|---|---|
| ois_3m | 1.17 | 0.104 | -1.26 | 0.023 | 0.835 | 51 |
| ois_6m | 1.73 | 0.071 | -1.96 | 0.003 | 0.753 | 53 |
| ois_1y | 1.64 | 0.140 | -2.19 | 0.014 | 0.541 | 53 |
| ois_2y | 2.35 | 0.074 | -2.13 | 0.039 | 0.795 | 53 |
| ois_5y | 2.49 | 0.057 | -2.09 | 0.057 | 0.631 | 53 |
| gsec_1y | 4.55 | 0.032 | -4.36 | 0.017 | 0.859 | 62 |
| gsec_10y | 1.61 | 0.332 | -0.92 | 0.492 | 0.329 | 62 |

## 7. Robustness of the headline (1-year OIS)

| variant | coef_bp | p | p_randinf | n |
|---|---|---|---|---|
| baseline: surprise + T-bill shocks | 2.29 | 0.013 | 0.006 | 53 |
| no decision-day controls | 1.96 | 0.024 | 0.014 | 53 |
| OIS-based decision-day shocks (2018-) | 2.11 | 0.039 | 0.023 | 51 |
| ex-COVID (Mar 2020-Dec 2021) | 1.37 | 0.386 | 0.348 | 42 |
| drop unscheduled meetings | 2.11 | 0.019 | 0.007 | 50 |
| dictionary tone instead of LLM | -0.81 | 0.563 | 0.522 | 53 |
| members minus resolution tone | 2.21 | 0.045 | 0.030 | 53 |
| internal members only (minus Governor) | 3.69 | 0.003 | 0.002 | 53 |
| drop 3 most influential (2019-04-04, 2022-04-08, 2022-09-30) | 1.96 | 0.031 | 0.024 | 50 |

COVID interaction (instead of dropping the window):

| tenor | b_normal | p_normal | b_covid | p_covid | p_equal | n | n_covid |
|---|---|---|---|---|---|---|---|
| ois_3m | 0.72 | 0.414 | 3.06 | 0.001 | 0.071 | 51 | 11 |
| ois_6m | 1.68 | 0.087 | 3.84 | 0.001 | 0.161 | 53 | 11 |
| ois_1y | 1.66 | 0.242 | 4.76 | 0.000 | 0.096 | 53 | 11 |
| ois_2y | 1.38 | 0.391 | 4.97 | 0.004 | 0.135 | 53 | 11 |
| ois_5y | 1.59 | 0.343 | 5.06 | 0.001 | 0.104 | 53 | 11 |
| gsec_1y | 3.23 | 0.077 | 6.36 | 0.183 | 0.541 | 62 | 11 |

Leave-one-out:

| tenor | coef | min (drop 1 meeting) | max | share p<0.05 | min (drop 1 year) | max  | share p<0.10 |
|---|---|---|---|---|---|---|---|
| ois_6m | 1.99 | 1.73 | 2.25 | 1.00 | 1.73 | 2.42 | 1.00 |
| ois_1y | 2.29 | 1.86 | 2.64 | 1.00 | 1.96 | 2.70 | 0.89 |
| ois_2y | 2.10 | 1.64 | 2.48 | 0.81 | 1.56 | 2.53 | 0.67 |

Persistence of the 1-year OIS response (cumulative, days after the reaction day):

| days_after | coef_bp | p | n |
|---|---|---|---|
| 0.00 | 2.29 | 0.013 | 53 |
| 1.00 | 3.41 | 0.007 | 53 |
| 2.00 | 2.41 | 0.090 | 53 |
| 3.00 | 3.70 | 0.029 | 51 |
| 4.00 | 3.83 | 0.038 | 47 |
| 5 | 3.39 | 0.110 | 47 |

Other text measures (1-year OIS):

| measure | coef_bp | p | p_randinf | corr_with_llm_surprise | n |
|---|---|---|---|---|---|
| surprise | 2.29 | 0.013 | 0.006 | 1.00 | 53 |
| surprise_sup | 0.62 | 0.928 | 0.933 | 0.01 | 53 |
| surprise_combo | 1.58 | 0.044 | 0.041 | 0.73 | 53 |
| surprise_dict | -0.81 | 0.563 | 0.522 | -0.07 | 53 |
| surprise_lean | 7.04 | 0.010 | 0.005 | 0.61 | 53 |
| surprise_next | -0.67 | 0.674 | 0.667 | 0.39 | 53 |
| surprise_rank | 4.48 | 0.088 | 0.062 | 0.95 | 53 |
| surprise_sign | 1.56 | 0.100 | 0.074 | 0.83 | 53 |

`surprise_sup` is a non-LLM score (TF-IDF ridge trained on votes, leave-one-year-out).
At statement level it correlates 0.32 with the LLM, but its meeting-level gap does not
(0.01), and neither it nor the dictionary reproduces the result. **The headline rests on the LLM.**

## 8. Reconciling with Mahambare & Pathak (2021)

Their design: dictionary tone *levels* of internal and external members, government bond yields, 30 meetings to August 2021.

| sample | tenor | coef_bp_ext | coef_bp_int | p_ext | p_int |
|---|---|---|---|---|---|
| Sep 2021 onwards | gsec_10y | -0.47 | 0.79 | 0.759 | 0.580 |
| Sep 2021 onwards | gsec_2y | -3.03 | 2.02 | 0.236 | 0.453 |
| full | gsec_10y | 1.37 | -0.60 | 0.169 | 0.459 |
| full | gsec_2y | 1.83 | -1.80 | 0.173 | 0.224 |
| to Aug 2021 (M&P sample) | gsec_10y | 1.73 | -0.94 | 0.258 | 0.588 |
| to Aug 2021 (M&P sample) | gsec_2y | 3.43 | -3.39 | 0.030 | 0.072 |

In their sample and design, external tone has the larger effect on the 2-year G-sec; it
disappears afterwards. Our result differs because we measure the gap to the Governor, use
OIS, and have twice the sample.

## 9. Exploratory: who forecasts policy?

Dependent variable: change in the repo rate over the next h meetings (bp). Controls: current decision, 1-year OIS minus repo before the minutes. HAC errors.

Text gaps:

| sample | h | b_int | p_int | b_ext | p_ext | p_equal | p_randinf_ext | n |
|---|---|---|---|---|---|---|---|---|
| full | 3 | -21.85 | 0.087 | 16.68 | 0.075 | 0.045 | 0.114 | 50 |
| full | 4 | -20.93 | 0.256 | 23.90 | 0.052 | 0.088 | 0.105 | 49 |
| ex-COVID | 3 | -11.22 | 0.426 | 2.13 | 0.829 | 0.476 |  | 39 |
| ex-COVID | 4 | -8.50 | 0.646 | 4.07 | 0.693 | 0.588 |  | 38 |
| ex-2022 hiking cycle | 3 | -25.17 | 0.060 | 15.49 | 0.180 | 0.076 |  | 43 |
| ex-2022 hiking cycle | 4 | -25.63 | 0.146 | 22.80 | 0.143 | 0.116 |  | 42 |
| 2022 onwards | 3 | 41.24 | 0.005 | 24.32 | 0.007 | 0.228 |  | 27 |
| 2022 onwards | 4 | 58.26 | 0.005 | 31.20 | 0.013 | 0.196 |  | 26 |

Votes only (net signed formal dissent of external members; no LLM):

| sample | h | coef_bp | p | p_randinf | n | n_dissent_meetings | coef_words | p_words |
|---|---|---|---|---|---|---|---|---|
| full | 3 | 16.47 | 0.025 | 0.046 | 50 | 23 |  |  |
| full | 4 | 24.04 | 0.032 | 0.062 | 49 | 23 |  |  |
| ex-COVID | 3 | 6.29 | 0.443 | 0.495 | 39 | 18 |  |  |
| ex-COVID | 4 | 7.40 | 0.520 | 0.591 | 38 | 18 |  |  |
| ex-2022 hiking cycle | 3 | 15.53 | 0.101 | 0.153 | 43 | 19 |  |  |
| ex-2022 hiking cycle | 4 | 23.73 | 0.096 | 0.181 | 42 | 19 |  |  |
| 2022 onwards | 3 | 23.45 | 0.005 | 0.003 | 27 | 12 |  |  |
| 2022 onwards | 4 | 35.06 | 0.000 | 0.000 | 26 | 12 |  |  |
| full: words and votes together | 3 | 15.40 | 0.164 |  | 50 |  | 1.37 | 0.903 |
| full: words and votes together | 4 | 18.94 | 0.200 |  | 49 |  | 6.52 | 0.633 |

OIS drift from the reaction day to the eve of the next decision:

| tenor | b_int | p_int | b_ext | p_ext | sd_drift_bp | n |
|---|---|---|---|---|---|---|
| ois_6m | -0.01 | 0.998 | 2.74 | 0.265 | 22.69 | 52 |
| ois_1y | 0.03 | 0.994 | 1.95 | 0.435 | 24.74 | 52 |
| ois_2y | 0.23 | 0.958 | 1.65 | 0.506 | 27.45 | 52 |

Reading: external dissent votes lead the repo path by 3–4 meetings in the full sample and
strongly after 2022, but not once the COVID meetings are removed, and there is no drift.
Treat as a lead for further work, not a finding.

## 10. What is still missing

1. Human coding of 120 statements by two coders (`docs/HAND_CODING.md`).
2. Same-model checks: `python run_pipeline.py llm-checks` (second prompt without the
   decision context; date-guessing look-ahead probe), then `analyze` again → `ext_llm_checks.csv`.
3. A literature search on RBI dissent votes predicting policy before developing section 9.
4. Intraday OIS data would sharpen the event window.

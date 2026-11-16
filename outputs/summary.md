# Results summary

# Data check

### Meetings and minutes
- **OK** 62 meetings 2016-10-04 .. 2026-10-07; 9 hikes, 13 cuts
- **OK** all minutes files present

### Market data
- **OK** gsec_10y: 2016-01-01..2026-11-09, n=2661, max |daily change|=0.316 on 2017-02-08
- **OK** gsec_5y: 2016-01-01..2026-11-09, n=2655, max |daily change|=0.535 on 2020-05-04
- **OK** gsec_2y: 2016-01-01..2026-11-09, n=2656, max |daily change|=0.519 on 2021-02-01
- **OK** gsec_1y: 2016-01-01..2026-11-09, n=2655, max |daily change|=0.521 on 2020-03-27
- **OK** tbill_91d: 2016-01-01..2026-11-02, n=2643, max |daily change|=0.810 on 2020-03-27
- **OK** tbill_182d: 2017-08-23..2026-11-02, n=2224, max |daily change|=0.580 on 2022-05-06
- **OK** tbill_364d: 2016-01-01..2026-11-02, n=2628, max |daily change|=0.500 on 2020-03-24
- **OK** ois_1m: 2018-07-30..2026-11-02, n=1996, max |daily change|=0.530 on 2022-05-05
- **OK** ois_3m: 2018-07-30..2026-11-02, n=1996, max |daily change|=0.620 on 2022-05-05
- **OK** ois_6m: 2018-04-03..2026-11-02, n=2078, max |daily change|=0.840 on 2022-05-05
- **OK** ois_1y: 2018-04-03..2026-11-02, n=2078, max |daily change|=0.560 on 2022-05-05
- **OK** ois_2y: 2018-04-03..2026-11-02, n=2078, max |daily change|=0.440 on 2022-05-05
- **OK** ois_5y: 2018-04-03..2026-11-02, n=2078, max |daily change|=0.360 on 2020-03-27
- **OK** usdinr: 2018-07-10..2026-11-02, n=1998, max |daily change|=1.446 on 2026-04-02
- **OK** us10y: 1962-01-02..2026-11-06, n=16198, max |daily change|=0.750 on 1987-10-20
- **WARN** us10y: 8 daily jumps > 0.50 -- check roll-overs of the benchmark bond or bad prints
- **OK** vix: 1990-01-02..2026-11-06, n=9312, max |daily change|=24.860 on 2020-03-16
- **WARN** vix: 1425 daily jumps > 1.76 -- check roll-overs of the benchmark bond or bad prints
- **OK** brent: 1987-05-20..2026-11-03, n=9122, max |daily change|=20.690 on 2026-10-02
- **WARN** brent: 91 daily jumps > 5.27 -- check roll-overs of the benchmark bond or bad prints
- **OK** nifty: 2016-01-01..2026-11-09, n=2690, max |daily change|=1379.400 on 2024-06-04
- **OK** OIS tenors available: 5 (>=3 recommended for decision-day factors)

### Text
- **OK** 372 statements, median 705 words; 26 'No' votes, 30 magnitude entries
- **OK** scores_dictionary: 372 rows, 0 missing
- **OK** scores_vader: 372 rows, 0 missing

## Sample

meetings: 62; surprise measure: exgov_members_minus_governor; hidden dissent source: llm

| index         |   count |   mean |    std |     min |    25% |    50% |   75% |    max |
|:--------------|--------:|-------:|-------:|--------:|-------:|-------:|------:|-------:|
| mean_hawk     |      62 | -0.099 |  1.022 |  -2     | -0.833 |  0     | 0.625 |  1.833 |
| sd_hawk       |      62 |  0.783 |  0.439 |   0     |  0.516 |  0.632 | 1.084 |  1.722 |
| surprise      |      62 | -0.139 |  0.655 |  -1.8   | -0.6   | -0.2   | 0.2   |  1.4   |
| hidden_signed |      62 |  0.013 |  0.214 |  -0.4   | -0.167 |  0     | 0.167 |  0.667 |
| hidden_share  |      62 |  0.145 |  0.152 |   0     |  0     |  0.167 | 0.25  |  0.6   |
| n_dissent     |      62 |  0.645 |  0.77  |   0     |  0     |  0     | 1     |  2     |
| target        |      62 | -0     | 12.704 | -55.833 | -4.807 |  1.578 | 5.372 | 24.375 |
| path          |      62 | -0     |  3.557 | -11.363 | -2.175 |  0.369 | 1.886 |  7.957 |
| mp_rot        |      62 | -0.357 |  5.749 | -19.001 | -3.465 |  0.769 | 3.45  | 11.067 |
| cbi_rot       |      62 |  0.357 |  5.641 | -16.743 | -2.015 |  0.208 | 3.985 | 11.289 |

## Text validation against recorded votes

| check                                                        |   n |   value |   kappa | note                 |
|:-------------------------------------------------------------|----:|--------:|--------:|:---------------------|
| LLM preferred action = actual vote direction                 | 369 |   1     |       1 | nan                  |
| ... among 'No' voters only                                   |  23 |   1     |     nan | nan                  |
| AUC: reservation score separates explicit dissenters         | 372 |   0.977 |     nan | nan                  |
| explicit dissenters read as reservation>=1                   |  40 |   1     |     nan | nan                  |
| lean sign = dissent direction (dissenters with nonzero lean) |  40 |   0.925 |     nan | nan                  |
| yes-voters with reservations (hidden dissent rate)           | 332 |   0.151 |     nan | nan                  |
| yes-voters with nonzero lean                                 | 332 |   0.163 |     nan | nan                  |
| formal dissent rate (all member-meetings)                    | 372 |   0.108 |     nan | nan                  |
| mean hawk_llm at cuts / holds / hikes                        | 372 | nan     |     nan | -1.55 / 0.08 / 1.20  |
| mean hawk_dict at cuts / holds / hikes                       | 372 | nan     |     nan | -1.17 / -0.30 / 0.63 |
| corr(hawk_llm, hawk_dict)                                    | 372 |   0.479 |     nan | nan                  |
| corr(hawk_llm, VADER sentiment)                              | 372 |  -0.044 |     nan | nan                  |

## Text validation (human vs machine)

_not available_

## Decision-day surprise series: diagnostics

| Unnamed: 0              | value                                                        |
|:------------------------|:-------------------------------------------------------------|
| factor_set              | TBILL_FALLBACK                                               |
| tenors                  | tbill_91d+tbill_364d+gsec_2y                                 |
| target_tenor            | tbill_91d                                                    |
| path_tenor              | tbill_364d                                                   |
| n_events                | 62                                                           |
| var_share_pc1           | 0.7948071751815927                                           |
| var_share_pc2           | 0.13367664829539583                                          |
| var_share_pc3           | 0.07151617652301147                                          |
| jk_admissible_share     | 0.4935                                                       |
| share_cbi_events_pm     | 0.41935483870967744                                          |
| purge_r2_target         | 0.40340637010655767                                          |
| purge_F_p_target        | 0.04068502626529383                                          |
| purge_r2_path           | 0.3000019579868475                                           |
| purge_F_p_path          | 0.26324379709699974                                          |
| purge_r2_rate_surprise  | 0.3933978754533486                                           |
| purge_F_p_rate_surprise | 0.05390956776082134                                          |
| purge_r2_mp_rot         | 0.1888076897012394                                           |
| purge_F_p_mp_rot        | 0.4326330372098406                                           |
| purge_predictors        | pre3m_gsec_10y+pre3m_nifty+pre3m_brent+pre3m_us10y+pre_slope |

## Decision-day validation regressions

| outcome    | unit   | spec        | var     |   coef |    se |     p |    r2 |   n |
|:-----------|:-------|:------------|:--------|-------:|------:|------:|------:|----:|
| ois_1m     | bp     | target_path | target  |  0.681 | 0.068 | 0     | 0.76  |  51 |
| ois_1m     | bp     | target_path | path    | -0.759 | 0.274 | 0.006 | 0.76  |  51 |
| ois_1m     | bp     | info_split  | mp_rot  |  1.167 | 0.158 | 0     | 0.721 |  51 |
| ois_1m     | bp     | info_split  | cbi_rot |  0.994 | 0.169 | 0     | 0.721 |  51 |
| ois_3m     | bp     | target_path | target  |  0.565 | 0.086 | 0     | 0.761 |  51 |
| ois_3m     | bp     | target_path | path    | -0.511 | 0.239 | 0.033 | 0.761 |  51 |
| ois_3m     | bp     | info_split  | mp_rot  |  1.011 | 0.171 | 0     | 0.746 |  51 |
| ois_3m     | bp     | info_split  | cbi_rot |  0.781 | 0.177 | 0     | 0.746 |  51 |
| ois_6m     | bp     | target_path | target  |  0.521 | 0.101 | 0     | 0.648 |  53 |
| ois_6m     | bp     | target_path | path    | -0.615 | 0.294 | 0.036 | 0.648 |  53 |
| ois_6m     | bp     | info_split  | mp_rot  |  0.982 | 0.233 | 0     | 0.631 |  53 |
| ois_6m     | bp     | info_split  | cbi_rot |  0.67  | 0.24  | 0.005 | 0.631 |  53 |
| ois_1y     | bp     | target_path | target  |  0.551 | 0.094 | 0     | 0.536 |  53 |
| ois_1y     | bp     | target_path | path    | -0.626 | 0.35  | 0.074 | 0.536 |  53 |
| ois_1y     | bp     | info_split  | mp_rot  |  1.156 | 0.288 | 0     | 0.565 |  53 |
| ois_1y     | bp     | info_split  | cbi_rot |  0.594 | 0.255 | 0.02  | 0.565 |  53 |
| ois_2y     | bp     | target_path | target  |  0.565 | 0.111 | 0     | 0.557 |  53 |
| ois_2y     | bp     | target_path | path    | -0.743 | 0.343 | 0.03  | 0.557 |  53 |
| ois_2y     | bp     | info_split  | mp_rot  |  1.149 | 0.297 | 0     | 0.559 |  53 |
| ois_2y     | bp     | info_split  | cbi_rot |  0.645 | 0.272 | 0.018 | 0.559 |  53 |
| ois_5y     | bp     | target_path | target  |  0.573 | 0.087 | 0     | 0.554 |  53 |
| ois_5y     | bp     | target_path | path    | -0.501 | 0.371 | 0.177 | 0.554 |  53 |
| ois_5y     | bp     | info_split  | mp_rot  |  1.167 | 0.228 | 0     | 0.586 |  53 |
| ois_5y     | bp     | info_split  | cbi_rot |  0.651 | 0.163 | 0     | 0.586 |  53 |
| tbill_91d  | bp     | target_path | target  |  1     | 0.196 | 0     | 0.864 |  62 |
| tbill_91d  | bp     | target_path | path    | -0     | 0.192 | 1     | 0.864 |  62 |
| tbill_91d  | bp     | info_split  | mp_rot  |  1.501 | 0.312 | 0     | 0.864 |  62 |
| tbill_91d  | bp     | info_split  | cbi_rot |  1.654 | 0.307 | 0     | 0.864 |  62 |
| tbill_182d | bp     | target_path | target  |  0.695 | 0.073 | 0     | 0.83  |  56 |
| tbill_182d | bp     | target_path | path    |  0.743 | 0.158 | 0     | 0.83  |  56 |
| tbill_182d | bp     | info_split  | mp_rot  |  1.156 | 0.189 | 0     | 0.755 |  56 |
| tbill_182d | bp     | info_split  | cbi_rot |  1.038 | 0.19  | 0     | 0.755 |  56 |
| tbill_364d | bp     | target_path | target  |  0.646 | 0.079 | 0     | 0.951 |  62 |
| tbill_364d | bp     | target_path | path    |  1     | 0.077 | 0     | 0.951 |  62 |
| tbill_364d | bp     | info_split  | mp_rot  |  0.98  | 0.154 | 0     | 0.772 |  62 |
| tbill_364d | bp     | info_split  | cbi_rot |  1.02  | 0.154 | 0     | 0.772 |  62 |
| gsec_1y    | bp     | target_path | target  |  0.808 | 0.07  | 0     | 0.73  |  62 |
| gsec_1y    | bp     | target_path | path    |  0.352 | 0.342 | 0.303 | 0.73  |  62 |
| gsec_1y    | bp     | info_split  | mp_rot  |  1.077 | 0.161 | 0     | 0.727 |  62 |
| gsec_1y    | bp     | info_split  | cbi_rot |  1.464 | 0.137 | 0     | 0.727 |  62 |
| gsec_2y    | bp     | target_path | target  |  0.689 | 0.069 | 0     | 0.971 |  62 |
| gsec_2y    | bp     | target_path | path    | -1.464 | 0.067 | 0     | 0.971 |  62 |
| gsec_2y    | bp     | info_split  | mp_rot  |  1.196 | 0.22  | 0     | 0.755 |  62 |
| gsec_2y    | bp     | info_split  | cbi_rot |  1.026 | 0.218 | 0     | 0.755 |  62 |
| gsec_5y    | bp     | target_path | target  |  0.727 | 0.067 | 0     | 0.635 |  62 |
| gsec_5y    | bp     | target_path | path    | -0.921 | 0.23  | 0     | 0.635 |  62 |
| gsec_5y    | bp     | info_split  | mp_rot  |  1.436 | 0.238 | 0     | 0.613 |  62 |
| gsec_5y    | bp     | info_split  | cbi_rot |  0.876 | 0.235 | 0     | 0.613 |  62 |
| gsec_10y   | bp     | target_path | target  |  0.453 | 0.141 | 0.001 | 0.452 |  62 |
| gsec_10y   | bp     | target_path | path    | -0.698 | 0.222 | 0.002 | 0.452 |  62 |
| gsec_10y   | bp     | info_split  | mp_rot  |  0.917 | 0.294 | 0.002 | 0.422 |  62 |
| gsec_10y   | bp     | info_split  | cbi_rot |  0.528 | 0.298 | 0.077 | 0.422 |  62 |
| nifty      | %      | target_path | target  | -0.001 | 0.009 | 0.89  | 0.01  |  62 |
| nifty      | %      | target_path | path    |  0.028 | 0.052 | 0.593 | 0.01  |  62 |
| nifty      | %      | info_split  | mp_rot  | -0.123 | 0     | 0     | 1     |  62 |
| nifty      | %      | info_split  | cbi_rot |  0.122 | 0     | 0     | 1     |  62 |
| usdinr     | %      | target_path | target  |  0.005 | 0.004 | 0.207 | 0.051 |  50 |
| usdinr     | %      | target_path | path    |  0.003 | 0.017 | 0.868 | 0.051 |  50 |
| usdinr     | %      | info_split  | mp_rot  |  0.013 | 0.007 | 0.069 | 0.068 |  50 |
| usdinr     | %      | info_split  | cbi_rot |  0.003 | 0.009 | 0.717 | 0.068 |  50 |

## Stage A: volatility on minutes days

| tenor      | days           |   n |   rms_event_bp |   rms_control_bp |   mean_abs_event_bp |   mean_abs_control_bp |   var_ratio |   p_brown_forsythe |   p_perm_matched |   n_control |
|:-----------|:---------------|----:|---------------:|-----------------:|--------------------:|----------------------:|------------:|-------------------:|-----------------:|------------:|
| ois_1m     | minutes        |  51 |          1.95  |            3.498 |               1.529 |                 2.049 |       0.311 |              0.192 |            0.992 |        1567 |
| ois_1m     | minutes_ex_cpi |  51 |          1.95  |            3.498 |               1.529 |                 2.049 |       0.311 |              0.192 |            0.996 |        1567 |
| ois_1m     | decision       |  51 |         10.415 |            3.498 |               6.706 |                 2.049 |       8.865 |              0     |            0     |        1567 |
| ois_3m     | minutes        |  51 |          2.356 |            2.51  |               1.784 |                 1.669 |       0.881 |              0.665 |            0.706 |        1567 |
| ois_3m     | minutes_ex_cpi |  51 |          2.356 |            2.51  |               1.784 |                 1.669 |       0.881 |              0.665 |            0.725 |        1567 |
| ois_3m     | decision       |  51 |          8.508 |            2.51  |               6     |                 1.669 |      11.493 |              0     |            0     |        1567 |
| ois_6m     | minutes        |  53 |          3.561 |            2.803 |               2.226 |                 1.846 |       1.614 |              0.202 |            0.236 |        1633 |
| ois_6m     | minutes_ex_cpi |  53 |          3.561 |            2.803 |               2.226 |                 1.846 |       1.614 |              0.202 |            0.201 |        1633 |
| ois_6m     | decision       |  53 |          8.507 |            2.803 |               6.113 |                 1.846 |       9.211 |              0     |            0     |        1633 |
| ois_1y     | minutes        |  53 |          4.423 |            3.348 |               2.887 |                 2.261 |       1.746 |              0.073 |            0.083 |        1633 |
| ois_1y     | minutes_ex_cpi |  53 |          4.423 |            3.348 |               2.887 |                 2.261 |       1.746 |              0.073 |            0.089 |        1633 |
| ois_1y     | decision       |  53 |          9.729 |            3.348 |               6.623 |                 2.261 |       8.445 |              0     |            0     |        1633 |
| ois_2y     | minutes        |  53 |          4.428 |            4     |               3.302 |                 2.844 |       1.225 |              0.265 |            0.396 |        1633 |
| ois_2y     | minutes_ex_cpi |  53 |          4.428 |            4     |               3.302 |                 2.844 |       1.225 |              0.265 |            0.406 |        1633 |
| ois_2y     | decision       |  53 |          9.903 |            4     |               7.132 |                 2.844 |       6.129 |              0     |            0     |        1633 |
| ois_5y     | minutes        |  53 |          4.609 |            4.449 |               3.283 |                 3.286 |       1.074 |              0.994 |            0.524 |        1633 |
| ois_5y     | minutes_ex_cpi |  53 |          4.609 |            4.449 |               3.283 |                 3.286 |       1.074 |              0.994 |            0.516 |        1633 |
| ois_5y     | decision       |  53 |          9.8   |            4.449 |               7.019 |                 3.286 |       4.853 |              0     |            0     |        1633 |
| tbill_91d  | minutes        |  62 |          4.563 |            4.594 |               2.5   |                 2.88  |       0.987 |              0.411 |            0.303 |        2100 |
| tbill_91d  | minutes_ex_cpi |  62 |          4.563 |            4.594 |               2.5   |                 2.88  |       0.987 |              0.411 |            0.326 |        2100 |
| tbill_91d  | decision       |  62 |         13.919 |            4.594 |               7.984 |                 2.88  |       9.181 |              0     |            0     |        2100 |
| tbill_182d | minutes        |  56 |          3.951 |            5.455 |               2.786 |                 3.362 |       0.524 |              0.192 |            0.755 |        1753 |
| tbill_182d | minutes_ex_cpi |  56 |          3.951 |            5.455 |               2.786 |                 3.362 |       0.524 |              0.192 |            0.753 |        1753 |
| tbill_182d | decision       |  56 |          9.991 |            5.455 |               6.107 |                 3.362 |       3.354 |              0     |            0.025 |        1753 |
| tbill_364d | minutes        |  62 |          4.015 |            4.242 |               2.55  |                 2.587 |       0.896 |              0.933 |            0.237 |        2100 |
| tbill_364d | minutes_ex_cpi |  62 |          4.015 |            4.242 |               2.55  |                 2.587 |       0.896 |              0.933 |            0.233 |        2100 |
| tbill_364d | decision       |  62 |          9.197 |            4.242 |               6.374 |                 2.587 |       4.701 |              0     |            0     |        2100 |
| gsec_1y    | minutes        |  62 |          7.495 |            6.27  |               4.706 |                 3.763 |       1.429 |              0.152 |            0.162 |        2147 |
| gsec_1y    | minutes_ex_cpi |  62 |          7.495 |            6.27  |               4.706 |                 3.763 |       1.429 |              0.152 |            0.183 |        2147 |
| gsec_1y    | decision       |  62 |         12.115 |            6.27  |               8.103 |                 3.763 |       3.734 |              0     |            0     |        2147 |
| gsec_2y    | minutes        |  62 |          5.921 |            5.781 |               3.669 |                 3.171 |       1.049 |              0.426 |            0.608 |        2149 |
| gsec_2y    | minutes_ex_cpi |  62 |          5.921 |            5.781 |               3.669 |                 3.171 |       1.049 |              0.426 |            0.608 |        2149 |
| gsec_2y    | decision       |  62 |         10.344 |            5.781 |               7.815 |                 3.171 |       3.202 |              0     |            0     |        2149 |
| gsec_5y    | minutes        |  62 |          5.543 |            4.33  |               3.595 |                 2.801 |       1.639 |              0.065 |            0.175 |        2147 |
| gsec_5y    | minutes_ex_cpi |  62 |          5.543 |            4.33  |               3.595 |                 2.801 |       1.639 |              0.065 |            0.185 |        2147 |
| gsec_5y    | decision       |  62 |         12.215 |            4.33  |               9.221 |                 2.801 |       7.957 |              0     |            0     |        2147 |
| gsec_10y   | minutes        |  62 |          4.484 |            3.79  |               3.189 |                 2.562 |       1.4   |              0.086 |            0.193 |        2159 |
| gsec_10y   | minutes_ex_cpi |  62 |          4.484 |            3.79  |               3.189 |                 2.562 |       1.4   |              0.086 |            0.2   |        2159 |
| gsec_10y   | decision       |  62 |          9.339 |            3.79  |               7.103 |                 2.562 |       6.072 |              0     |            0     |        2159 |
| nifty      | minutes        |  62 |          0.954 |            1.043 |               0.679 |                 0.692 |       0.836 |              0.85  |            0.724 |        2101 |
| nifty      | minutes_ex_cpi |  62 |          0.954 |            1.043 |               0.679 |                 0.692 |       0.836 |              0.85  |            0.7   |        2101 |
| nifty      | decision       |  62 |          0.982 |            1.043 |               0.698 |                 0.692 |       0.886 |              0.936 |            0.375 |        2101 |
| usdinr     | minutes        |  51 |          0.241 |            0.296 |               0.176 |                 0.207 |       0.665 |              0.316 |            0.939 |        1570 |
| usdinr     | minutes_ex_cpi |  51 |          0.241 |            0.296 |               0.176 |                 0.207 |       0.665 |              0.316 |            0.933 |        1570 |
| usdinr     | decision       |  50 |          0.29  |            0.296 |               0.191 |                 0.207 |       0.96  |              0.605 |            0.544 |        1570 |

## Stage B: minutes-day directional effects (1-day window)

| tenor      | unit   | spec            | var           |   coef_bp |    se |     p |   p_randinf |   p_holm_tenors |   n |
|:-----------|:-------|:----------------|:--------------|----------:|------:|------:|------------:|----------------:|----:|
| ois_1m     | bp     | surprise        | surprise      |     0.171 | 0.579 | 0.767 |       0.765 |           1     |  51 |
| ois_1m     | bp     | surprise_hidden | surprise      |     0.191 | 0.601 | 0.75  |       0.746 |           1     |  51 |
| ois_1m     | bp     | surprise_hidden | hidden_signed |    -0.986 | 1.946 | 0.612 |       0.596 |           1     |  51 |
| ois_1m     | bp     | with_shocks     | surprise      |     0.262 | 0.657 | 0.69  |       0.683 |           1     |  51 |
| ois_1m     | bp     | with_shocks     | hidden_signed |    -0.925 | 2.263 | 0.683 |       0.675 |           1     |  51 |
| ois_3m     | bp     | surprise        | surprise      |     1.025 | 0.563 | 0.069 |       0.067 |           0.826 |  51 |
| ois_3m     | bp     | surprise_hidden | surprise      |     1.025 | 0.584 | 0.079 |       0.073 |           0.952 |  51 |
| ois_3m     | bp     | surprise_hidden | hidden_signed |     0.008 | 2.115 | 0.997 |       0.998 |           1     |  51 |
| ois_3m     | bp     | with_shocks     | surprise      |     1.277 | 0.556 | 0.022 |       0.019 |           0.261 |  51 |
| ois_3m     | bp     | with_shocks     | hidden_signed |     0.477 | 2.214 | 0.829 |       0.819 |           1     |  51 |
| ois_6m     | bp     | surprise        | surprise      |     1.68  | 0.622 | 0.007 |       0.004 |           0.103 |  53 |
| ois_6m     | bp     | surprise_hidden | surprise      |     1.619 | 0.619 | 0.009 |       0.004 |           0.133 |  53 |
| ois_6m     | bp     | surprise_hidden | hidden_signed |     2.502 | 4.003 | 0.532 |       0.523 |           1     |  53 |
| ois_6m     | bp     | with_shocks     | surprise      |     1.962 | 0.659 | 0.003 |       0     |           0.043 |  53 |
| ois_6m     | bp     | with_shocks     | hidden_signed |     3.205 | 4.07  | 0.431 |       0.394 |           1     |  53 |
| ois_1y     | bp     | surprise        | surprise      |     1.962 | 0.872 | 0.024 |       0.014 |           0.343 |  53 |
| ois_1y     | bp     | surprise_hidden | surprise      |     1.896 | 0.876 | 0.03  |       0.017 |           0.427 |  53 |
| ois_1y     | bp     | surprise_hidden | hidden_signed |     2.69  | 2.982 | 0.367 |       0.342 |           1     |  53 |
| ois_1y     | bp     | with_shocks     | surprise      |     2.254 | 0.927 | 0.015 |       0.007 |           0.211 |  53 |
| ois_1y     | bp     | with_shocks     | hidden_signed |     3.134 | 2.98  | 0.293 |       0.247 |           1     |  53 |
| ois_2y     | bp     | surprise        | surprise      |     1.757 | 0.898 | 0.05  |       0.046 |           0.654 |  53 |
| ois_2y     | bp     | surprise_hidden | surprise      |     1.636 | 0.908 | 0.072 |       0.057 |           0.93  |  53 |
| ois_2y     | bp     | surprise_hidden | hidden_signed |     4.987 | 3.554 | 0.161 |       0.141 |           1     |  53 |
| ois_2y     | bp     | with_shocks     | surprise      |     2.037 | 1.033 | 0.049 |       0.036 |           0.534 |  53 |
| ois_2y     | bp     | with_shocks     | hidden_signed |     5.995 | 3.398 | 0.078 |       0.052 |           1     |  53 |
| ois_5y     | bp     | surprise        | surprise      |     1.515 | 0.921 | 0.1   |       0.079 |           1     |  53 |
| ois_5y     | bp     | surprise_hidden | surprise      |     1.433 | 0.988 | 0.147 |       0.121 |           1     |  53 |
| ois_5y     | bp     | surprise_hidden | hidden_signed |     3.391 | 3.706 | 0.36  |       0.349 |           1     |  53 |
| ois_5y     | bp     | with_shocks     | surprise      |     1.968 | 1.156 | 0.089 |       0.059 |           0.889 |  53 |
| ois_5y     | bp     | with_shocks     | hidden_signed |     5.304 | 3.437 | 0.123 |       0.093 |           1     |  53 |
| tbill_91d  | bp     | surprise        | surprise      |    -0.338 | 0.85  | 0.691 |       0.729 |           1     |  62 |
| tbill_91d  | bp     | surprise_hidden | surprise      |    -0.332 | 0.874 | 0.704 |       0.741 |           1     |  62 |
| tbill_91d  | bp     | surprise_hidden | hidden_signed |    -0.473 | 2.563 | 0.853 |       0.873 |           1     |  62 |
| tbill_91d  | bp     | with_shocks     | surprise      |     0.099 | 0.8   | 0.901 |       0.919 |           1     |  62 |
| tbill_91d  | bp     | with_shocks     | hidden_signed |    -0.586 | 2.636 | 0.824 |       0.846 |           1     |  62 |
| tbill_182d | bp     | surprise        | surprise      |     1.084 | 0.702 | 0.123 |       0.122 |           1     |  56 |
| tbill_182d | bp     | surprise_hidden | surprise      |     1.072 | 0.723 | 0.138 |       0.13  |           1     |  56 |
| tbill_182d | bp     | surprise_hidden | hidden_signed |     0.728 | 2.514 | 0.772 |       0.763 |           1     |  56 |
| tbill_182d | bp     | with_shocks     | surprise      |     0.951 | 0.799 | 0.234 |       0.201 |           1     |  56 |
| tbill_182d | bp     | with_shocks     | hidden_signed |     1.369 | 3.283 | 0.677 |       0.693 |           1     |  56 |
| tbill_364d | bp     | surprise        | surprise      |     0.847 | 0.576 | 0.141 |       0.15  |           1     |  62 |
| tbill_364d | bp     | surprise_hidden | surprise      |     0.841 | 0.576 | 0.144 |       0.148 |           1     |  62 |
| tbill_364d | bp     | surprise_hidden | hidden_signed |     0.55  | 1.834 | 0.764 |       0.764 |           1     |  62 |
| tbill_364d | bp     | with_shocks     | surprise      |     1.038 | 0.646 | 0.108 |       0.091 |           0.974 |  62 |
| tbill_364d | bp     | with_shocks     | hidden_signed |     0.347 | 2.032 | 0.864 |       0.862 |           1     |  62 |
| gsec_1y    | bp     | surprise        | surprise      |     3.206 | 1.888 | 0.09  |       0.075 |           0.985 |  62 |
| gsec_1y    | bp     | surprise_hidden | surprise      |     3.202 | 1.907 | 0.093 |       0.071 |           1     |  62 |
| gsec_1y    | bp     | surprise_hidden | hidden_signed |     0.436 | 4.555 | 0.924 |       0.919 |           1     |  62 |
| gsec_1y    | bp     | with_shocks     | surprise      |     4.326 | 1.852 | 0.02  |       0.006 |           0.254 |  62 |
| gsec_1y    | bp     | with_shocks     | hidden_signed |    -0.032 | 5.055 | 0.995 |       0.99  |           1     |  62 |
| gsec_2y    | bp     | surprise        | surprise      |    -0.289 | 1.691 | 0.864 |       0.881 |           1     |  62 |
| gsec_2y    | bp     | surprise_hidden | surprise      |    -0.292 | 1.693 | 0.863 |       0.881 |           1     |  62 |
| gsec_2y    | bp     | surprise_hidden | hidden_signed |     0.251 | 3.726 | 0.946 |       0.955 |           1     |  62 |
| gsec_2y    | bp     | with_shocks     | surprise      |     0.156 | 1.718 | 0.928 |       0.927 |           1     |  62 |
| gsec_2y    | bp     | with_shocks     | hidden_signed |    -0.041 | 3.674 | 0.991 |       0.994 |           1     |  62 |
| gsec_5y    | bp     | surprise        | surprise      |     1.296 | 1.497 | 0.387 |       0.365 |           1     |  62 |
| gsec_5y    | bp     | surprise_hidden | surprise      |     1.233 | 1.483 | 0.406 |       0.374 |           1     |  62 |
| gsec_5y    | bp     | surprise_hidden | hidden_signed |     5.72  | 3.488 | 0.101 |       0.094 |           1     |  62 |
| gsec_5y    | bp     | with_shocks     | surprise      |     1.575 | 1.721 | 0.36  |       0.316 |           1     |  62 |
| gsec_5y    | bp     | with_shocks     | hidden_signed |     5.412 | 3.724 | 0.146 |       0.12  |           1     |  62 |

### 2-day window

| tenor      | unit   | spec        | var           |   coef_bp |    se |     p |   p_randinf |   n |
|:-----------|:-------|:------------|:--------------|----------:|------:|------:|------------:|----:|
| ois_1m     | bp     | with_shocks | surprise      |     1.15  | 0.424 | 0.007 |       0.009 |  51 |
| ois_1m     | bp     | with_shocks | hidden_signed |    -2.676 | 2.458 | 0.276 |       0.225 |  51 |
| ois_3m     | bp     | with_shocks | surprise      |     2.022 | 0.741 | 0.006 |       0.001 |  51 |
| ois_3m     | bp     | with_shocks | hidden_signed |     0.416 | 3.152 | 0.895 |       0.885 |  51 |
| ois_6m     | bp     | with_shocks | surprise      |     2.827 | 0.843 | 0.001 |       0     |  53 |
| ois_6m     | bp     | with_shocks | hidden_signed |     2.665 | 4.001 | 0.505 |       0.471 |  53 |
| ois_1y     | bp     | with_shocks | surprise      |     3.359 | 1.27  | 0.008 |       0.006 |  53 |
| ois_1y     | bp     | with_shocks | hidden_signed |     3.399 | 4.677 | 0.467 |       0.427 |  53 |
| ois_2y     | bp     | with_shocks | surprise      |     4.003 | 1.529 | 0.009 |       0.007 |  53 |
| ois_2y     | bp     | with_shocks | hidden_signed |     7.851 | 4.908 | 0.11  |       0.08  |  53 |
| ois_5y     | bp     | with_shocks | surprise      |     3.52  | 1.68  | 0.036 |       0.022 |  53 |
| ois_5y     | bp     | with_shocks | hidden_signed |     8.668 | 5.926 | 0.144 |       0.11  |  53 |
| tbill_91d  | bp     | with_shocks | surprise      |    -1.418 | 1.527 | 0.353 |       0.318 |  62 |
| tbill_91d  | bp     | with_shocks | hidden_signed |    -1.158 | 3.523 | 0.742 |       0.731 |  62 |
| tbill_182d | bp     | with_shocks | surprise      |    -0.004 | 0.804 | 0.996 |       0.991 |  56 |
| tbill_182d | bp     | with_shocks | hidden_signed |     1.609 | 2.946 | 0.585 |       0.537 |  56 |
| tbill_364d | bp     | with_shocks | surprise      |     1.019 | 1.446 | 0.481 |       0.439 |  62 |
| tbill_364d | bp     | with_shocks | hidden_signed |    -0.774 | 3.684 | 0.834 |       0.838 |  62 |
| gsec_1y    | bp     | with_shocks | surprise      |     2.639 | 2.21  | 0.232 |       0.183 |  62 |
| gsec_1y    | bp     | with_shocks | hidden_signed |     1.47  | 3.529 | 0.677 |       0.67  |  62 |
| gsec_2y    | bp     | with_shocks | surprise      |     1.683 | 2.083 | 0.419 |       0.411 |  62 |
| gsec_2y    | bp     | with_shocks | hidden_signed |     0.834 | 5.017 | 0.868 |       0.882 |  62 |
| gsec_5y    | bp     | with_shocks | surprise      |     2.294 | 2.08  | 0.27  |       0.239 |  62 |
| gsec_5y    | bp     | with_shocks | hidden_signed |     5.55  | 5.207 | 0.286 |       0.275 |  62 |
| gsec_10y   | bp     | with_shocks | surprise      |     1.097 | 1.7   | 0.519 |       0.484 |  62 |
| gsec_10y   | bp     | with_shocks | hidden_signed |     6.034 | 4.912 | 0.219 |       0.211 |  62 |
| nifty      | %      | with_shocks | surprise      |     0.154 | 0.265 | 0.561 |       0.531 |  61 |
| nifty      | %      | with_shocks | hidden_signed |     0.178 | 0.818 | 0.827 |       0.786 |  61 |
| usdinr     | %      | with_shocks | surprise      |    -0.018 | 0.085 | 0.832 |       0.813 |  51 |
| usdinr     | %      | with_shocks | hidden_signed |     0.044 | 0.297 | 0.883 |       0.854 |  51 |

## Robustness of the headline result

| tenor   | variant                                                      |   coef_bp |    se |     p |   p_randinf |   n |   bp_per_sd |
|:--------|:-------------------------------------------------------------|----------:|------:|------:|------------:|----:|------------:|
| ois_6m  | baseline: surprise + T-bill shocks                           |     1.995 | 0.66  | 0.003 |       0     |  53 |       1.37  |
| ois_6m  | no decision-day controls                                     |     1.68  | 0.622 | 0.007 |       0.004 |  53 |       1.154 |
| ois_6m  | OIS-based decision-day shocks (2018-)                        |     1.87  | 0.724 | 0.01  |       0.003 |  51 |       1.302 |
| ois_6m  | ex-COVID (Mar 2020-Dec 2021)                                 |     1.396 | 1.082 | 0.197 |       0.152 |  42 |       0.892 |
| ois_6m  | drop unscheduled meetings                                    |     1.796 | 0.624 | 0.004 |       0.002 |  50 |       1.262 |
| ois_6m  | dictionary tone instead of LLM                               |    -0.09  | 1.344 | 0.947 |       0.943 |  53 |      -0.052 |
| ois_6m  | members minus resolution tone                                |     2.076 | 1.084 | 0.055 |       0.033 |  53 |       1.306 |
| ois_6m  | internal members only (minus Governor)                       |     3.116 | 0.95  | 0.001 |       0.001 |  53 |       1.655 |
| ois_6m  | drop 3 most influential (2022-04-08, 2020-03-27, 2022-09-30) |     1.617 | 0.509 | 0.002 |       0.002 |  50 |       1.12  |
| ois_1y  | baseline: surprise + T-bill shocks                           |     2.286 | 0.92  | 0.013 |       0.006 |  53 |       1.57  |
| ois_1y  | no decision-day controls                                     |     1.962 | 0.872 | 0.024 |       0.014 |  53 |       1.347 |
| ois_1y  | OIS-based decision-day shocks (2018-)                        |     2.111 | 1.024 | 0.039 |       0.023 |  51 |       1.47  |
| ois_1y  | ex-COVID (Mar 2020-Dec 2021)                                 |     1.366 | 1.576 | 0.386 |       0.348 |  42 |       0.873 |
| ois_1y  | drop unscheduled meetings                                    |     2.112 | 0.898 | 0.019 |       0.007 |  50 |       1.484 |
| ois_1y  | dictionary tone instead of LLM                               |    -0.806 | 1.393 | 0.563 |       0.522 |  53 |      -0.469 |
| ois_1y  | members minus resolution tone                                |     2.207 | 1.099 | 0.045 |       0.03  |  53 |       1.389 |
| ois_1y  | internal members only (minus Governor)                       |     3.694 | 1.264 | 0.003 |       0.002 |  53 |       1.962 |
| ois_1y  | drop 3 most influential (2019-04-04, 2022-04-08, 2022-09-30) |     1.956 | 0.909 | 0.031 |       0.024 |  50 |       1.287 |
| ois_2y  | baseline: surprise + T-bill shocks                           |     2.098 | 1.031 | 0.042 |       0.032 |  53 |       1.441 |
| ois_2y  | no decision-day controls                                     |     1.757 | 0.898 | 0.05  |       0.046 |  53 |       1.207 |
| ois_2y  | OIS-based decision-day shocks (2018-)                        |     1.953 | 1.106 | 0.077 |       0.062 |  51 |       1.36  |
| ois_2y  | ex-COVID (Mar 2020-Dec 2021)                                 |     1.052 | 1.754 | 0.549 |       0.525 |  42 |       0.672 |
| ois_2y  | drop unscheduled meetings                                    |     1.899 | 0.966 | 0.049 |       0.041 |  50 |       1.334 |
| ois_2y  | dictionary tone instead of LLM                               |    -0.511 | 1.618 | 0.752 |       0.713 |  53 |      -0.298 |
| ois_2y  | members minus resolution tone                                |     2.633 | 1.167 | 0.024 |       0.022 |  53 |       1.657 |
| ois_2y  | internal members only (minus Governor)                       |     3.481 | 1.302 | 0.007 |       0.007 |  53 |       1.849 |
| ois_2y  | drop 3 most influential (2022-04-08, 2020-03-27, 2019-04-04) |     1.488 | 1.021 | 0.145 |       0.12  |  50 |       0.989 |
| gsec_1y | baseline: surprise + T-bill shocks                           |     4.325 | 1.816 | 0.017 |       0.006 |  62 |       2.835 |
| gsec_1y | no decision-day controls                                     |     3.206 | 1.888 | 0.09  |       0.075 |  62 |       2.102 |
| gsec_1y | OIS-based decision-day shocks (2018-)                        |     5.077 | 1.874 | 0.007 |       0.005 |  51 |       3.536 |
| gsec_1y | ex-COVID (Mar 2020-Dec 2021)                                 |     2.88  | 2.045 | 0.159 |       0.113 |  51 |       1.736 |
| gsec_1y | drop unscheduled meetings                                    |     4.123 | 1.959 | 0.035 |       0.026 |  59 |       2.753 |
| gsec_1y | dictionary tone instead of LLM                               |    -0.95  | 0.965 | 0.325 |       0.302 |  62 |      -0.663 |
| gsec_1y | members minus resolution tone                                |     2.151 | 1.481 | 0.146 |       0.13  |  62 |       1.321 |
| gsec_1y | internal members only (minus Governor)                       |     3.398 | 1.984 | 0.087 |       0.069 |  62 |       1.836 |
| gsec_1y | drop 3 most influential (2019-12-05, 2022-04-08, 2021-08-06) |     1.837 | 1.465 | 0.21  |       0.175 |  59 |       1.158 |

## Stage C: uncertainty channel (|dy|)

| tenor      | spec                 | var          |   coef_bp |    se |     p |   n |
|:-----------|:---------------------|:-------------|----------:|------:|------:|----:|
| ois_1m     | hidden_share         | hidden_share |    -2.267 | 1.154 | 0.049 |  51 |
| ois_1m     | sd_hawk              | sd_hawk      |     0.161 | 0.41  | 0.695 |  51 |
| ois_1m     | hidden_share+sd_hawk | hidden_share |    -2.239 | 1.163 | 0.054 |  51 |
| ois_1m     | hidden_share+sd_hawk | sd_hawk      |     0.086 | 0.407 | 0.833 |  51 |
| ois_3m     | hidden_share         | hidden_share |    -2.044 | 1.407 | 0.146 |  51 |
| ois_3m     | sd_hawk              | sd_hawk      |    -0.194 | 0.586 | 0.741 |  51 |
| ois_3m     | hidden_share+sd_hawk | hidden_share |    -2.129 | 1.457 | 0.144 |  51 |
| ois_3m     | hidden_share+sd_hawk | sd_hawk      |    -0.266 | 0.593 | 0.654 |  51 |
| ois_6m     | hidden_share         | hidden_share |    -0.852 | 2.299 | 0.711 |  53 |
| ois_6m     | sd_hawk              | sd_hawk      |    -1.388 | 0.844 | 0.1   |  53 |
| ois_6m     | hidden_share+sd_hawk | hidden_share |    -1.232 | 2.305 | 0.593 |  53 |
| ois_6m     | hidden_share+sd_hawk | sd_hawk      |    -1.424 | 0.878 | 0.105 |  53 |
| ois_1y     | hidden_share         | hidden_share |    -0.978 | 3.037 | 0.747 |  53 |
| ois_1y     | sd_hawk              | sd_hawk      |    -1.474 | 0.951 | 0.121 |  53 |
| ois_1y     | hidden_share+sd_hawk | hidden_share |    -1.383 | 3.137 | 0.659 |  53 |
| ois_1y     | hidden_share+sd_hawk | sd_hawk      |    -1.514 | 1.018 | 0.137 |  53 |
| ois_2y     | hidden_share         | hidden_share |     1.04  | 2.516 | 0.679 |  53 |
| ois_2y     | sd_hawk              | sd_hawk      |    -1.149 | 0.986 | 0.244 |  53 |
| ois_2y     | hidden_share+sd_hawk | hidden_share |     0.739 | 2.588 | 0.775 |  53 |
| ois_2y     | hidden_share+sd_hawk | sd_hawk      |    -1.127 | 1.021 | 0.269 |  53 |
| ois_5y     | hidden_share         | hidden_share |    -0.087 | 2.766 | 0.975 |  53 |
| ois_5y     | sd_hawk              | sd_hawk      |    -1.694 | 1.363 | 0.214 |  53 |
| ois_5y     | hidden_share+sd_hawk | hidden_share |    -0.544 | 2.895 | 0.851 |  53 |
| ois_5y     | hidden_share+sd_hawk | sd_hawk      |    -1.709 | 1.422 | 0.229 |  53 |
| tbill_91d  | hidden_share         | hidden_share |     0.621 | 3.371 | 0.854 |  62 |
| tbill_91d  | sd_hawk              | sd_hawk      |    -1.349 | 1.145 | 0.239 |  62 |
| tbill_91d  | hidden_share+sd_hawk | hidden_share |     0.586 | 3.474 | 0.866 |  62 |
| tbill_91d  | hidden_share+sd_hawk | sd_hawk      |    -1.347 | 1.153 | 0.242 |  62 |
| tbill_182d | hidden_share         | hidden_share |    -0.578 | 2.863 | 0.84  |  56 |
| tbill_182d | sd_hawk              | sd_hawk      |    -2.223 | 1.039 | 0.032 |  56 |
| tbill_182d | hidden_share+sd_hawk | hidden_share |    -0.874 | 2.639 | 0.74  |  56 |
| tbill_182d | hidden_share+sd_hawk | sd_hawk      |    -2.235 | 1.056 | 0.034 |  56 |
| tbill_364d | hidden_share         | hidden_share |    -3.331 | 3.006 | 0.268 |  62 |
| tbill_364d | sd_hawk              | sd_hawk      |    -0.183 | 1.189 | 0.878 |  62 |
| tbill_364d | hidden_share+sd_hawk | hidden_share |    -3.336 | 3.056 | 0.275 |  62 |
| tbill_364d | hidden_share+sd_hawk | sd_hawk      |    -0.193 | 1.174 | 0.87  |  62 |
| gsec_1y    | hidden_share         | hidden_share |     3.086 | 4.654 | 0.507 |  62 |
| gsec_1y    | sd_hawk              | sd_hawk      |    -3.271 | 1.801 | 0.069 |  62 |
| gsec_1y    | hidden_share+sd_hawk | hidden_share |     3.001 | 4.546 | 0.509 |  62 |
| gsec_1y    | hidden_share+sd_hawk | sd_hawk      |    -3.263 | 1.801 | 0.07  |  62 |
| gsec_2y    | hidden_share         | hidden_share |    -0.938 | 3.334 | 0.778 |  62 |
| gsec_2y    | sd_hawk              | sd_hawk      |    -1.71  | 0.944 | 0.07  |  62 |
| gsec_2y    | hidden_share+sd_hawk | hidden_share |    -0.983 | 3.323 | 0.767 |  62 |
| gsec_2y    | hidden_share+sd_hawk | sd_hawk      |    -1.713 | 0.973 | 0.078 |  62 |
| gsec_5y    | hidden_share         | hidden_share |    -0.376 | 3.557 | 0.916 |  62 |
| gsec_5y    | sd_hawk              | sd_hawk      |    -2.262 | 1.374 | 0.1   |  62 |
| gsec_5y    | hidden_share+sd_hawk | hidden_share |    -0.435 | 3.48  | 0.901 |  62 |
| gsec_5y    | hidden_share+sd_hawk | sd_hawk      |    -2.263 | 1.387 | 0.103 |  62 |
| gsec_10y   | hidden_share         | hidden_share |     2.933 | 2.928 | 0.316 |  62 |
| gsec_10y   | sd_hawk              | sd_hawk      |    -1.181 | 0.886 | 0.183 |  62 |
| gsec_10y   | hidden_share+sd_hawk | hidden_share |     2.903 | 2.903 | 0.317 |  62 |
| gsec_10y   | hidden_share+sd_hawk | sd_hawk      |    -1.172 | 0.875 | 0.18  |  62 |
| nifty      | hidden_share         | hidden_share |     0.569 | 0.61  | 0.351 |  62 |
| nifty      | sd_hawk              | sd_hawk      |    -0.067 | 0.155 | 0.666 |  62 |
| nifty      | hidden_share+sd_hawk | hidden_share |     0.567 | 0.612 | 0.354 |  62 |
| nifty      | hidden_share+sd_hawk | sd_hawk      |    -0.065 | 0.155 | 0.673 |  62 |
| usdinr     | hidden_share         | hidden_share |     0.042 | 0.144 | 0.773 |  51 |
| usdinr     | sd_hawk              | sd_hawk      |     0.021 | 0.073 | 0.779 |  51 |
| usdinr     | hidden_share+sd_hawk | hidden_share |     0.049 | 0.156 | 0.754 |  51 |
| usdinr     | hidden_share+sd_hawk | sd_hawk      |     0.022 | 0.076 | 0.771 |  51 |

## Placebo: day before release

| tenor      | var           |   coef_bp |      se |     p |   n |
|:-----------|:--------------|----------:|--------:|------:|----:|
| ois_1m     | surprise      |    -0.087 |   0.643 | 0.893 |  49 |
| ois_1m     | hidden_signed |    -2.335 |   2.268 | 0.303 |  49 |
| ois_3m     | surprise      |    -0.404 |   0.641 | 0.528 |  49 |
| ois_3m     | hidden_signed |    -2.271 |   1.851 | 0.22  |  49 |
| ois_6m     | surprise      |     0.15  |   0.541 | 0.781 |  51 |
| ois_6m     | hidden_signed |     1.612 |   1.537 | 0.294 |  51 |
| ois_1y     | surprise      |    -0.289 |   0.645 | 0.653 |  51 |
| ois_1y     | hidden_signed |     0.48  |   2.217 | 0.829 |  51 |
| ois_2y     | surprise      |     0.505 |   0.717 | 0.481 |  51 |
| ois_2y     | hidden_signed |     1.2   |   2.61  | 0.646 |  51 |
| ois_5y     | surprise      |    -0.434 |   0.715 | 0.543 |  51 |
| ois_5y     | hidden_signed |     1.843 |   3.186 | 0.563 |  51 |
| tbill_91d  | surprise      |     0.857 |   0.788 | 0.277 |  60 |
| tbill_91d  | hidden_signed |    -0.759 |   2.275 | 0.739 |  60 |
| tbill_182d | surprise      |     0.706 |   0.92  | 0.443 |  54 |
| tbill_182d | hidden_signed |    -0.182 |   3.633 | 0.96  |  54 |
| tbill_364d | surprise      |     0.174 |   0.479 | 0.716 |  60 |
| tbill_364d | hidden_signed |    -0.716 |   1.968 | 0.716 |  60 |
| gsec_1y    | surprise      |     0.207 |   1.721 | 0.904 |  62 |
| gsec_1y    | hidden_signed |    -0.276 |   3.106 | 0.929 |  62 |
| gsec_2y    | surprise      |     1.874 |   2.352 | 0.426 |  62 |
| gsec_2y    | hidden_signed |    -0.091 |   2.932 | 0.975 |  62 |
| gsec_5y    | surprise      |     0.393 |   0.63  | 0.533 |  62 |
| gsec_5y    | hidden_signed |     0.323 |   2.44  | 0.895 |  62 |
| gsec_10y   | surprise      |     0.376 |   0.465 | 0.419 |  62 |
| gsec_10y   | hidden_signed |     1.107 |   2.338 | 0.636 |  62 |
| nifty      | surprise      |     0.11  | inf     | 1     |  61 |
| nifty      | hidden_signed |     0.024 |   0.574 | 0.967 |  61 |
| usdinr     | surprise      |     0.121 |   0.071 | 0.087 |  49 |
| usdinr     | hidden_signed |     0.496 |   0.225 | 0.028 |  49 |

## Linkage tests (L1, L3, L4)

| test                                | y                  | var           |   coef |    se |     p |   p_randinf |    r2 |   n |
|:------------------------------------|:-------------------|:--------------|-------:|------:|------:|------------:|------:|----:|
| L1 disagreement ~ |shock type|      | hidden_share       | abs_mp_rot    | -0.005 | 0.007 | 0.425 |     nan     | 0.016 |  62 |
| L1 disagreement ~ |shock type|      | hidden_share       | abs_cbi_rot   |  0.004 | 0.011 | 0.682 |     nan     | 0.016 |  62 |
| L1 disagreement ~ |target|,|path|   | hidden_share       | abs_target    | -0.001 | 0.003 | 0.791 |     nan     | 0.02  |  62 |
| L1 disagreement ~ |target|,|path|   | hidden_share       | abs_path      |  0.009 | 0.01  | 0.351 |     nan     | 0.02  |  62 |
| L1 disagreement ~ |shock type|      | sd_hawk            | abs_mp_rot    |  0     | 0.016 | 0.998 |     nan     | 0.031 |  62 |
| L1 disagreement ~ |shock type|      | sd_hawk            | abs_cbi_rot   | -0.02  | 0.02  | 0.307 |     nan     | 0.031 |  62 |
| L1 disagreement ~ |target|,|path|   | sd_hawk            | abs_target    | -0.008 | 0.009 | 0.409 |     nan     | 0.051 |  62 |
| L1 disagreement ~ |target|,|path|   | sd_hawk            | abs_path      | -0.023 | 0.019 | 0.221 |     nan     | 0.051 |  62 |
| L1 disagreement ~ |shock type|      | mean_unc_llm       | abs_mp_rot    |  0.01  | 0.009 | 0.274 |     nan     | 0.026 |  62 |
| L1 disagreement ~ |shock type|      | mean_unc_llm       | abs_cbi_rot   |  0.002 | 0.012 | 0.885 |     nan     | 0.026 |  62 |
| L1 disagreement ~ |target|,|path|   | mean_unc_llm       | abs_target    |  0.007 | 0.002 | 0.003 |     nan     | 0.078 |  62 |
| L1 disagreement ~ |target|,|path|   | mean_unc_llm       | abs_path      |  0.01  | 0.011 | 0.353 |     nan     | 0.078 |  62 |
| L1 signed hidden dissent ~ shocks   | hidden_signed      | mp_rot        |  0.003 | 0.005 | 0.521 |     nan     | 0.01  |  62 |
| L1 signed hidden dissent ~ shocks   | hidden_signed      | cbi_rot       |  0.002 | 0.004 | 0.64  |     nan     | 0.01  |  62 |
| L3 next surprise ~ minutes text     | next_target        | surprise      | -3.129 | 2.403 | 0.193 |       0.208 | 0.076 |  61 |
| L3 next surprise ~ minutes text     | next_target        | hidden_signed | 13.695 | 6.912 | 0.048 |       0.038 | 0.076 |  61 |
| L3 + minutes-day move               | next_target        | surprise      | -4.4   | 3.193 | 0.168 |       0.142 | 0.067 |  52 |
| L3 + minutes-day move               | next_target        | hidden_signed |  5.602 | 7.728 | 0.469 |       0.441 | 0.067 |  52 |
| L3 + minutes-day move               | next_target        | dy1_ois_1y    |  0.485 | 0.794 | 0.541 |       0.531 | 0.067 |  52 |
| L4 next surprise ~ minutes-day move | next_target        | dy1_ois_1y    |  0.298 | 0.7   | 0.67  |     nan     | 0.011 |  52 |
| L3 next surprise ~ minutes text     | next_path          | surprise      |  0.669 | 0.553 | 0.227 |       0.227 | 0.023 |  61 |
| L3 next surprise ~ minutes text     | next_path          | hidden_signed |  1.466 | 1.933 | 0.448 |       0.418 | 0.023 |  61 |
| L3 + minutes-day move               | next_path          | surprise      |  0.651 | 0.641 | 0.31  |       0.292 | 0.046 |  52 |
| L3 + minutes-day move               | next_path          | hidden_signed | -0.309 | 2.238 | 0.89  |       0.889 | 0.046 |  52 |
| L3 + minutes-day move               | next_path          | dy1_ois_1y    |  0.092 | 0.254 | 0.717 |       0.702 | 0.046 |  52 |
| L4 next surprise ~ minutes-day move | next_path          | dy1_ois_1y    |  0.122 | 0.235 | 0.603 |     nan     | 0.029 |  52 |
| L3 next surprise ~ minutes text     | next_rate_surprise | surprise      | -2.043 | 1.509 | 0.176 |       0.184 | 0.076 |  61 |
| L3 next surprise ~ minutes text     | next_rate_surprise | hidden_signed |  8.542 | 4.409 | 0.053 |       0.042 | 0.076 |  61 |
| L3 + minutes-day move               | next_rate_surprise | surprise      | -2.846 | 2.001 | 0.155 |       0.133 | 0.068 |  52 |
| L3 + minutes-day move               | next_rate_surprise | hidden_signed |  3.577 | 4.888 | 0.464 |       0.439 | 0.068 |  52 |
| L3 + minutes-day move               | next_rate_surprise | dy1_ois_1y    |  0.299 | 0.484 | 0.537 |       0.524 | 0.068 |  52 |
| L4 next surprise ~ minutes-day move | next_rate_surprise | dy1_ois_1y    |  0.178 | 0.425 | 0.676 |     nan     | 0.01  |  52 |
| L3 next surprise ~ minutes text     | next_mp_rot        | surprise      | -0.659 | 1.116 | 0.554 |       0.541 | 0.02  |  61 |
| L3 next surprise ~ minutes text     | next_mp_rot        | hidden_signed |  3.318 | 3.529 | 0.347 |       0.355 | 0.02  |  61 |
| L3 + minutes-day move               | next_mp_rot        | surprise      | -0.708 | 1.348 | 0.599 |       0.583 | 0.009 |  52 |
| L3 + minutes-day move               | next_mp_rot        | hidden_signed |  1.776 | 3.898 | 0.649 |       0.63  | 0.009 |  52 |
| L3 + minutes-day move               | next_mp_rot        | dy1_ois_1y    |  0.039 | 0.276 | 0.888 |       0.885 | 0.009 |  52 |
| L4 next surprise ~ minutes-day move | next_mp_rot        | dy1_ois_1y    |  0.013 | 0.244 | 0.957 |     nan     | 0     |  52 |
| L3 next surprise ~ minutes text     | next_target_purged | surprise      | -1.28  | 2.016 | 0.525 |       0.547 | 0.037 |  61 |
| L3 next surprise ~ minutes text     | next_target_purged | hidden_signed |  8.068 | 5.7   | 0.157 |       0.158 | 0.037 |  61 |
| L3 + minutes-day move               | next_target_purged | surprise      | -1.518 | 2.423 | 0.531 |       0.497 | 0.021 |  52 |
| L3 + minutes-day move               | next_target_purged | hidden_signed |  4.416 | 7.573 | 0.56  |       0.554 | 0.021 |  52 |
| L3 + minutes-day move               | next_target_purged | dy1_ois_1y    | -0.104 | 0.338 | 0.758 |       0.749 | 0.021 |  52 |
| L4 next surprise ~ minutes-day move | next_target_purged | dy1_ois_1y    | -0.157 | 0.298 | 0.599 |     nan     | 0.005 |  52 |
| L3 next surprise ~ minutes text     | next_path_purged   | surprise      |  0.88  | 0.473 | 0.063 |       0.071 | 0.039 |  61 |
| L3 next surprise ~ minutes text     | next_path_purged   | hidden_signed |  0.279 | 1.412 | 0.843 |       0.821 | 0.039 |  61 |
| L3 + minutes-day move               | next_path_purged   | surprise      |  0.964 | 0.541 | 0.075 |       0.066 | 0.053 |  52 |
| L3 + minutes-day move               | next_path_purged   | hidden_signed | -0.716 | 2.064 | 0.729 |       0.739 | 0.053 |  52 |
| L3 + minutes-day move               | next_path_purged   | dy1_ois_1y    |  0.011 | 0.209 | 0.959 |       0.947 | 0.053 |  52 |
| L4 next surprise ~ minutes-day move | next_path_purged   | dy1_ois_1y    |  0.054 | 0.195 | 0.781 |     nan     | 0.007 |  52 |

## Predictability of the next decision

| target            | model                                   |   n |      r2 |   loo_rmse_bp |   naive_rmse_bp |   b_decision_bp |   p_decision_bp |   b_mkt_path_pre |   p_mkt_path_pre |   b_surprise |   p_surprise |   b_hidden_signed |   p_hidden_signed |   b_mean_next_move_llm |   p_mean_next_move_llm |   p_joint_text |   b_mkt_path_post |   p_mkt_path_post |   b_n_dissent |   p_n_dissent |   b_hidden_share |   p_hidden_share |   b_sd_hawk |   p_sd_hawk |   pseudo_r2 |   loo_accuracy |   baseline_same_dir_acc |   baseline_modal_acc |
|:------------------|:----------------------------------------|----:|--------:|--------------:|----------------:|----------------:|----------------:|-----------------:|-----------------:|-------------:|-------------:|------------------:|------------------:|-----------------------:|-----------------------:|---------------:|------------------:|------------------:|--------------:|--------------:|-----------------:|-----------------:|------------:|------------:|------------:|---------------:|------------------------:|---------------------:|
| next_decision_bp  | M0 persistence                          |  61 |   0.395 |        17.477 |          18.686 |           0.63  |           0     |          nan     |              nan |      nan     |      nan     |           nan     |           nan     |                nan     |                nan     |        nan     |           nan     |               nan |       nan     |       nan     |          nan     |          nan     |     nan     |     nan     |     nan     |        nan     |                 nan     |              nan     |
| next_decision_bp  | M1 + market pre                         |  52 |   0.559 |        16.311 |          19.328 |           0.315 |           0.024 |            0.265 |                0 |      nan     |      nan     |           nan     |           nan     |                nan     |                nan     |        nan     |           nan     |               nan |       nan     |       nan     |          nan     |          nan     |     nan     |     nan     |     nan     |        nan     |                 nan     |              nan     |
| next_decision_bp  | M2 + market pre + text                  |  48 |   0.6   |        16.699 |          19.459 |           0.212 |           0.275 |            0.202 |                0 |       -1.445 |        0.75  |             1.89  |             0.882 |                  9.118 |                  0.123 |          0.145 |           nan     |               nan |       nan     |       nan     |          nan     |          nan     |     nan     |     nan     |     nan     |        nan     |                 nan     |              nan     |
| next_decision_bp  | M2b text only                           |  56 |   0.475 |        17.477 |          18.922 |           0.435 |           0.013 |          nan     |              nan |       -0.267 |        0.953 |            -1.23  |             0.913 |                 10.216 |                  0.087 |          0.059 |           nan     |               nan |       nan     |       nan     |          nan     |          nan     |     nan     |     nan     |     nan     |        nan     |                 nan     |              nan     |
| next_decision_bp  | M3 market post + text                   |  48 |   0.605 |        16.602 |          19.459 |           0.206 |           0.288 |          nan     |              nan |       -1.733 |        0.699 |             1.758 |             0.889 |                  8.651 |                  0.127 |          0.183 |             0.215 |                 0 |       nan     |       nan     |          nan     |          nan     |     nan     |     nan     |     nan     |        nan     |                 nan     |              nan     |
| next_n_dissent    | n_dissent                               |  61 |   0.148 |         0.732 |         nan     |         nan     |         nan     |          nan     |              nan |      nan     |      nan     |           nan     |           nan     |                nan     |                nan     |        nan     |           nan     |               nan |         0.385 |         0.003 |          nan     |          nan     |     nan     |     nan     |     nan     |        nan     |                 nan     |              nan     |
| next_n_dissent    | n_dissent+hidden_share                  |  61 |   0.151 |         0.744 |         nan     |         nan     |         nan     |          nan     |              nan |      nan     |      nan     |           nan     |           nan     |                nan     |                nan     |        nan     |           nan     |               nan |         0.372 |         0.005 |           -0.292 |            0.665 |     nan     |     nan     |     nan     |        nan     |                 nan     |              nan     |
| next_n_dissent    | n_dissent+hidden_share+sd_hawk          |  61 |   0.151 |         0.756 |         nan     |         nan     |         nan     |          nan     |              nan |      nan     |      nan     |           nan     |           nan     |                nan     |                nan     |        nan     |           nan     |               nan |         0.362 |         0.019 |           -0.307 |            0.672 |       0.027 |       0.918 |     nan     |        nan     |                 nan     |              nan     |
| next_decision_dir | M0 persistence (ordered probit)         |  61 | nan     |       nan     |         nan     |         nan     |         nan     |          nan     |              nan |      nan     |      nan     |           nan     |           nan     |                nan     |                nan     |        nan     |           nan     |               nan |       nan     |       nan     |          nan     |          nan     |     nan     |     nan     |       0.275 |          0.738 |                   0.738 |                0.656 |
| next_decision_dir | M2 + market pre + text (ordered probit) |  48 | nan     |       nan     |         nan     |         nan     |         nan     |          nan     |              nan |      nan     |      nan     |           nan     |           nan     |                nan     |                nan     |        nan     |           nan     |               nan |       nan     |       nan     |          nan     |          nan     |     nan     |     nan     |       0.563 |          0.688 |                   0.771 |                0.646 |

## Subsamples (main spec, 1-day window)

| sample   | tenor      | var           |   coef_bp |    se |     p |   n |
|:---------|:-----------|:--------------|----------:|------:|------:|----:|
| full     | ois_1m     | surprise      |     0.262 | 0.657 | 0.69  |  51 |
| full     | ois_1m     | hidden_signed |    -0.925 | 2.263 | 0.683 |  51 |
| full     | ois_1m     | target        |     0.013 | 0.027 | 0.641 |  51 |
| full     | ois_1m     | path          |     0.076 | 0.095 | 0.425 |  51 |
| full     | ois_3m     | surprise      |     1.277 | 0.556 | 0.022 |  51 |
| full     | ois_3m     | hidden_signed |     0.477 | 2.214 | 0.829 |  51 |
| full     | ois_3m     | target        |     0.05  | 0.046 | 0.279 |  51 |
| full     | ois_3m     | path          |     0.163 | 0.126 | 0.198 |  51 |
| full     | ois_6m     | surprise      |     1.962 | 0.659 | 0.003 |  53 |
| full     | ois_6m     | hidden_signed |     3.205 | 4.07  | 0.431 |  53 |
| full     | ois_6m     | target        |     0.079 | 0.075 | 0.294 |  53 |
| full     | ois_6m     | path          |     0.147 | 0.192 | 0.445 |  53 |
| full     | ois_1y     | surprise      |     2.254 | 0.927 | 0.015 |  53 |
| full     | ois_1y     | hidden_signed |     3.134 | 2.98  | 0.293 |  53 |
| full     | ois_1y     | target        |     0.079 | 0.089 | 0.373 |  53 |
| full     | ois_1y     | path          |     0.277 | 0.261 | 0.289 |  53 |
| full     | ois_2y     | surprise      |     2.037 | 1.033 | 0.049 |  53 |
| full     | ois_2y     | hidden_signed |     5.995 | 3.398 | 0.078 |  53 |
| full     | ois_2y     | target        |     0.095 | 0.108 | 0.379 |  53 |
| full     | ois_2y     | path          |     0.093 | 0.232 | 0.689 |  53 |
| full     | ois_5y     | surprise      |     1.968 | 1.156 | 0.089 |  53 |
| full     | ois_5y     | hidden_signed |     5.304 | 3.437 | 0.123 |  53 |
| full     | ois_5y     | target        |     0.133 | 0.141 | 0.345 |  53 |
| full     | ois_5y     | path          |    -0.117 | 0.25  | 0.638 |  53 |
| full     | tbill_91d  | surprise      |     0.099 | 0.8   | 0.901 |  62 |
| full     | tbill_91d  | hidden_signed |    -0.586 | 2.636 | 0.824 |  62 |
| full     | tbill_91d  | target        |     0.1   | 0.048 | 0.039 |  62 |
| full     | tbill_91d  | path          |    -0.165 | 0.171 | 0.336 |  62 |
| full     | tbill_182d | surprise      |     0.951 | 0.799 | 0.234 |  56 |
| full     | tbill_182d | hidden_signed |     1.369 | 3.283 | 0.677 |  56 |
| full     | tbill_182d | target        |    -0.02  | 0.104 | 0.85  |  56 |
| full     | tbill_182d | path          |    -0.214 | 0.263 | 0.416 |  56 |
| full     | tbill_364d | surprise      |     1.038 | 0.646 | 0.108 |  62 |
| full     | tbill_364d | hidden_signed |     0.347 | 2.032 | 0.864 |  62 |
| full     | tbill_364d | target        |     0.049 | 0.089 | 0.58  |  62 |
| full     | tbill_364d | path          |     0.149 | 0.132 | 0.257 |  62 |
| full     | gsec_1y    | surprise      |     4.326 | 1.852 | 0.02  |  62 |
| full     | gsec_1y    | hidden_signed |    -0.032 | 5.055 | 0.995 |  62 |
| full     | gsec_1y    | target        |     0.264 | 0.111 | 0.018 |  62 |
| full     | gsec_1y    | path          |    -0.171 | 0.29  | 0.556 |  62 |
| full     | gsec_2y    | surprise      |     0.156 | 1.718 | 0.928 |  62 |
| full     | gsec_2y    | hidden_signed |    -0.041 | 3.674 | 0.991 |  62 |
| full     | gsec_2y    | target        |     0.108 | 0.068 | 0.113 |  62 |
| full     | gsec_2y    | path          |     0.09  | 0.278 | 0.746 |  62 |
| full     | gsec_5y    | surprise      |     1.575 | 1.721 | 0.36  |  62 |
| full     | gsec_5y    | hidden_signed |     5.412 | 3.724 | 0.146 |  62 |
| full     | gsec_5y    | target        |     0.084 | 0.15  | 0.573 |  62 |
| full     | gsec_5y    | path          |     0.194 | 0.209 | 0.353 |  62 |
| full     | gsec_10y   | surprise      |     0.702 | 1.286 | 0.585 |  62 |
| full     | gsec_10y   | hidden_signed |     6.049 | 3.439 | 0.079 |  62 |
| full     | gsec_10y   | target        |     0.023 | 0.097 | 0.815 |  62 |
| full     | gsec_10y   | path          |     0.033 | 0.184 | 0.859 |  62 |
| full     | nifty      | surprise      |     0.001 | 0.184 | 0.995 |  62 |
| full     | nifty      | hidden_signed |    -0.403 | 0.672 | 0.549 |  62 |
| full     | nifty      | target        |     0.007 | 0.012 | 0.578 |  62 |
| full     | nifty      | path          |    -0.013 | 0.036 | 0.727 |  62 |
| full     | usdinr     | surprise      |     0.052 | 0.059 | 0.383 |  51 |
| full     | usdinr     | hidden_signed |    -0.108 | 0.222 | 0.625 |  51 |
| full     | usdinr     | target        |    -0.002 | 0.003 | 0.4   |  51 |
| full     | usdinr     | path          |    -0.006 | 0.013 | 0.639 |  51 |

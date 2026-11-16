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
# Data guide: what to download, where to put it, what format

Sample: every MPC meeting with a decision, **October 2016 to October 2026** (about 62 meetings,
including the unscheduled meetings of March 2020, May 2020 and May 2022). The additional
meeting of 3 November 2022 (the report to the government on missing the target) had no
policy decision and is excluded.

Market data must start **by January 2016** (at least 63 trading days before the first meeting)
and run to the latest minutes release (21 October 2026 or later).

Everything goes under `data/raw/`. Templates with the right headers are already there.

---

## A. Essential

### A1. MPC minutes (all meetings) → `data/raw/minutes_html/`
- Source: RBI press releases titled *"Minutes of the Monetary Policy Committee Meeting, ..."*
  (rbi.org.in → Press Releases, or Monetary Policy → Monetary Policy Documents). Use the **PDF**.
- Save each as `<meeting_date>.pdf`, where `meeting_date` = the **decision day** (last day of
  the meeting), e.g. `2025-06-06.pdf`. `.html` and `.txt` also work.
- Alternatively, put the URLs in `minutes_urls.csv` and run `python run_pipeline.py scrape`
  from your own machine. If RBI blocks the request, download the PDFs by hand.

### A2. Meeting table → `data/raw/decisions.csv` (draft provided, **must be verified**)
| column | meaning |
|---|---|
| meeting_date | decision day, YYYY-MM-DD |
| decision_bp | change in policy repo rate, bp (−25, 0, +50 ...) |
| repo_after | repo rate after the decision, percent |
| stance | stance wording as in the resolution: `accommodative`, `neutral`, `withdrawal of accommodation`, `calibrated tightening` (other labels: add them to `STANCE_ORDER` in `src/config.py`) |
| unscheduled | 1 for off-cycle meetings |
| announce_time | optional `HH:MM` IST of the announcement (only used with intraday data) |
| verified | set to **1** after checking the row against the RBI resolution |

- The draft was written from memory and **every row is marked unverified**. The build stops
  until all rows are verified.
- The **April and June 2026 meetings are missing**. Add them.
- After `parse`, the `check` stage compares your `repo_after` and `stance` with what the
  parser read from each resolution (`data/processed/meeting_texts.csv`, columns
  `repo_parsed`, `stance_parsed`). Use that to speed up verification.

### A3. Minutes release dates → `data/raw/minutes_urls.csv` (draft provided)
- `release_date` is drafted as decision day + 14 days. **Replace it with the actual date of
  the minutes press release.** It moves when the 14th day is a holiday; e.g. the February 2021
  minutes came out on 22 February, not the 19th.
- `release_after_market` = 1. Minutes are published at 17:00 IST, when the G-sec market closes.
  If you find any release during market hours, set it to 0.
- `url` is optional (only for the scraper).

### A4. Hand-coded explicit dissent → `data/raw/dissent_direction.csv`
For every member who **voted No**, or **dissented on the stance**, one row:
`meeting_date, member, dissent_dir, type, notes`.
- `dissent_dir` is +1 if the member wanted tighter policy than the majority, −1 if looser.
- `type` is `rate` or `stance`.
- `member` must be spelled as in `src/members.py` (e.g. `Jayanth Varma`).
- The resolution names the dissenters and says what they voted for.
- Magnitude dissents (same direction, different size, e.g. 25 vs 50 bp in June 2025) are read
  automatically from the vote table and need no row.

### A5. Daily market data → `data/raw/market/downloads/` + `series_map.csv`
Download each series as a CSV/XLSX into `downloads/`. Then edit `series_map.csv` (file name,
date column, value column, units) and run `python run_pipeline.py market`. That builds
`data/raw/market/yields.csv`. **Yields must be in percent.**

| column name | what | required? | free source (examples) |
|---|---|---|---|
| gsec_10y | 10-year benchmark G-sec yield | **required** (defines the trading calendar) | FBIL G-sec par yields / CCIL / Investing.com |
| gsec_5y, gsec_2y, gsec_1y | G-sec yields | strongly recommended | FBIL par yield curve / Investing.com |
| tbill_91d, tbill_182d, tbill_364d | T-bill yields | strongly recommended (fallback factors if no OIS) | FBIL T-bill benchmarks |
| ois_1m, ois_3m, ois_6m, ois_1y, ois_2y, ois_5y | INR MIBOR OIS rates | **strongly recommended**: the decision-day factors are much cleaner with OIS | Bloomberg / Refinitiv (university terminal; search for the INR MIBOR OIS curve) |
| nifty | Nifty 50 close | **required** for the policy vs information split | NSE Indices historical data |
| bank_nifty | Nifty Bank close | optional | NSE Indices |
| usdinr | USD/INR (FBIL reference rate) | recommended | FBIL |
| us10y | US 10-year Treasury | recommended control | FRED `DGS10` |
| vix | CBOE VIX | recommended control | FRED `VIXCLS` |
| brent | Brent crude | recommended control | FRED `DCOILBRENTEU` |

Notes:
- **Benchmark roll-overs.** Generic "10-year yield" series jump when the benchmark bond
  changes. `check` flags large daily jumps. Inspect any that fall on or next to a
  minutes/decision day; a constant-maturity par yield (FBIL) avoids the problem.
- If you have no OIS at all, the decision-day factors are built from T-bills + 2y G-sec.
  This is noisier and sensitive to liquidity, and should be stated in the paper.
- **Licensed data (Bloomberg/Refinitiv) must not be published.** `.gitignore` already
  excludes the downloads.

### A6. CPI release dates → `data/raw/market/cpi_release_dates.csv`
One column `date`: the day each CPI print was released (MoSPI, normally the 12th of the month).
The code knows the release time moved from 17:30 to 16:00 IST on 12 Nov 2024 and shifts the
reaction day accordingly.

---

## B. Recommended (they strengthen identification)

### B1. Poll consensus → `data/raw/consensus.csv`
`meeting_date, consensus_bp, source, n_economists`: median expected change from the Reuters (or
Bloomberg/ET) poll published before each meeting. You can collect it by hand from news reports.
Gives a survey-based surprise that is independent of market data.

### B2. CPI prints → `data/raw/market/cpi.csv`
`reference_month, release_date, cpi_yoy, consensus_yoy`. Used to purge decision-day surprises
of predictable components (inflation gap) and as a control. `consensus_yoy` is optional.

### B3. Other same-day events → `data/raw/market/other_events.csv`
`date, after_market (0/1), label`. Add RBI OMO/VRR/CRR announcements outside MPC days, Union
Budget days, GDP releases and similar events. These days are flagged and controlled for,
and removed from the "ordinary day" comparison group.

---

## C. Optional

- **Intraday quotes** → `data/raw/market/intraday.csv` with `datetime` (IST), `series`
  (e.g. `ois_1y`, `nifty`), `value` (percent / index level), plus `announce_time` in
  decisions.csv. Decision-day surprises then use a 15-min-before to 45-min-after window. This
  is needed for a top-journal version; daily windows are fine for a first working paper.
- **FinBERT** benchmark needs `transformers` + `torch`.

---

## D. Not data, but needed

- **LLM access**: an Anthropic API key (`ANTHROPIC_API_KEY`) and a pinned model id
  (`RBI_LLM_MODEL`). About 380 statements + 62 resolutions, roughly 1–1.5 million input
  tokens in total. Responses are cached, so re-runs are free.
- **Human coding time**: 60 statements × about 4 minutes, ideally by two people (see
  `docs/CODEBOOK.md`).

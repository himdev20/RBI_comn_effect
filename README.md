# Whose Words Move Rates? Attributed Member Statements in RBI Minutes and the Indian Yield Curve

**Status (November 2026): working paper in progress.**
The full pipeline runs end to end on real data for all 62 meetings of India's Monetary
Policy Committee (MPC) from October 2016 to October 2026. The main result holds up under
placebo and robustness tests. Two planned checks on the text measure (human coding and
same-model LLM checks) are built but not yet run.

- Every number in one place: [`RESULTS.md`](RESULTS.md)
- Working draft: [`paper/draft.md`](paper/draft.md)
- Supervisor: Prof. Sanjiv Kumar, IIT Kanpur

This README is written so that someone new to the project can understand **what was done,
why each choice was made, what was found, and what is still open**. Each step has a short
"Why" note.

---

## Contents

1. [The question in plain words](#1-the-question-in-plain-words)
2. [Key terms](#2-key-terms)
3. [How the project evolved](#3-how-the-project-evolved)
4. [Data: what, from where, and why](#4-data-what-from-where-and-why)
5. [Step 1 – Turning the minutes into data](#5-step-1--turning-the-minutes-into-data)
6. [Step 2 – Measuring what each member says](#6-step-2--measuring-what-each-member-says)
7. [Step 3 – Checking the text measure against votes](#7-step-3--checking-the-text-measure-against-votes)
8. [Step 4 – Building the "news in the minutes" variable](#8-step-4--building-the-news-in-the-minutes-variable)
9. [Step 5 – Measuring decision-day surprises](#9-step-5--measuring-decision-day-surprises)
10. [Step 6 – The minutes-day event study](#10-step-6--the-minutes-day-event-study)
11. [Step 7 – Testing whether the result is real](#11-step-7--testing-whether-the-result-is-real)
12. [Step 8 – Extensions and new ideas tried](#12-step-8--extensions-and-new-ideas-tried)
13. [Results summary](#13-results-summary)
14. [How this relates to existing research](#14-how-this-relates-to-existing-research)
15. [What is done, built-but-not-run, and not done](#15-what-is-done-built-but-not-run-and-not-done)
16. [Limitations](#16-limitations)
17. [Next steps](#17-next-steps)
18. [How to run everything](#18-how-to-run-everything)
19. [Repository layout](#19-repository-layout)
20. [Data and licence](#20-data-and-licence)

---

## 1. The question in plain words

The Reserve Bank of India (RBI) sets its policy interest rate, the **repo rate**, through a
six-member Monetary Policy Committee:

| Member | Who appoints them | Called here |
|---|---|---|
| Governor (chairs, has a casting vote) | RBI | Governor |
| Deputy Governor in charge of monetary policy | RBI | internal |
| One RBI Executive Director | RBI | internal |
| Three outside experts | Government of India | external |

On **decision day** the RBI announces the decision, the vote count and who voted which way.
The Governor explains the decision in a statement and a press conference.

**Fourteen days later, at 17:00 IST**, the RBI publishes the **minutes**. They contain a
separate, signed statement by each member explaining their vote. Very few central banks
publish attributed statements like this (others include Sweden's Riksbank and the Czech
National Bank).

Because the Governor has already explained his view on decision day, the genuinely new
information in the minutes is **how far the other five members stand from him**. If the
other members sound more hawkish (more worried about inflation, keener on higher rates)
than the Governor, markets may conclude that future policy will be tighter than they
thought.

The project asks three questions:

1. **Does that gap move interest rates when the minutes are released?**
2. **Whose words matter:** the RBI's own internal members, or the external members?
3. **Do members who vote "yes" but voice reservations ("hidden dissent")** reveal anything
   markets price?

> **Why this matters.** Central banks spend heavily on communication. If the market reads
> the minutes, the RBI's choice of what members write, and who sits on the committee,
> affects interest rates. If it ignores them, a large part of the RBI's communication has no
> market effect.

---

## 2. Key terms

| Term | Meaning |
|---|---|
| **bp (basis point)** | 0.01 percentage point. A move from 6.50% to 6.52% is 2 bp. |
| **Hawkish / dovish** | Hawkish = favours higher rates to fight inflation. Dovish = favours lower rates to support growth. |
| **OIS (overnight indexed swap)** | A contract whose rate reflects the average overnight interest rate expected over its term. A 1-year OIS rate is a clean market forecast of the policy rate over the next year. |
| **G-sec** | Government of India bond. Its yield reflects expected policy rates plus extra compensation for risk and bond supply. |
| **T-bill** | Short-term government security (91, 182, 364 days). |
| **Event study** | Measures how prices change in a short window around an event, to isolate the event's effect. |
| **Placebo test** | Runs the same analysis where no effect should exist (the wrong day, random days). If an "effect" shows up there, the method is producing artefacts. |
| **p-value** | Roughly, how likely a result this large would be if there were no true effect. Below 0.05 is the conventional threshold for "significant". |
| **Explicit (formal) dissent** | A recorded "No" vote, or a vote for a different rate or stance. |
| **Hidden dissent** | A member votes "Yes" but their statement expresses reservations. |
| **Target and path shocks** | Two parts of a decision-day surprise: the surprise about today's rate (target) and about future rates (path). |
| **Information effect** | When a rate hike makes markets think the economy is stronger than they believed, so stocks rise instead of falling. It means the decision revealed the central bank's view of the economy, not just its policy. |
| **LLM** | Large language model. Here, Google's Gemini, used to read and score statements. |

---

## 3. How the project evolved

| Stage | What happened | Why |
|---|---|---|
| 1. Starting point | An earlier version ("say vs vote") was built on mock data, focused on hidden dissent. | The original idea: compare what members say with how they vote. |
| 2. First literature search | Found that hidden dissent in RBI minutes had already been measured (Sil et al. 2024; Kumar, Sil, Kurup and Paramanik 2025). | A paper must add something new; hidden dissent alone would not. |
| 3. Redirection | Combined two ideas: (a) a minutes-day event study, and (b) an updated decision-day surprise series to 2026. | (b) is needed anyway to separate decision-day news from minutes-day news, and existing public series stop in early 2023. |
| 4. Real data | Built scrapers and downloaders; no synthetic data is used anywhere. | Results on mock data cannot be published or trusted. |
| 5. Measurement | Parsed and scored all 372 statements. | Needed a number for "how hawkish is this statement". |
| 6. First results | The members-minus-Governor gap moves short OIS rates; the effect comes from internal members. | — |
| 7. Second literature search | Found Mahambare and Pathak (2021), who regressed next-day bond yields on member tone for 30 meetings to August 2021. | Dropped the claim of being "first"; repositioned the contribution (section 14). |
| 8. Extensions | Ten further tests (section 12), including a replication of Mahambare and Pathak. | To answer the questions a referee would ask, and to look for new results. |
| 9. Recheck | Rebuilt every result from raw data. One promising result (forecasting) turned out fragile and was downgraded to "exploratory". | Better to find weaknesses now than in peer review. |
| 10. Current | This repository. | — |

---

## 4. Data: what, from where, and why

| Source | Series | Coverage | Events usable |
|---|---|---|---|
| RBI website | Minutes (HTML), decisions, release dates | Oct 2016 – Oct 2026 | 62 meetings, 372 statements |
| FBIL (Financial Benchmarks India) | OIS 1 month – 5 years; T-bills 91/182/364 days; USD/INR | OIS from April 2018 | 51–53 for OIS |
| Investing.com | G-sec 1/2/5/10-year yields; Nifty 50; India VIX | 2016 – 2026 | 62 |
| FRED (St. Louis Fed) | US 10-year yield, US VIX, Brent oil | 2016 – 2026 | used as controls |

**Why these series**
- **OIS rates are the main outcome.** They measure expected policy rates almost directly and
  are less affected by government borrowing, bank liquidity and bond-market risk premia
  than G-sec yields. If the minutes change expectations about the repo rate, OIS is where it
  should show first. The cost is that FBIL's OIS series starts in 2018, so OIS regressions
  use about 51–53 of the 62 meetings.
- **G-secs and T-bills** cover the whole sample from 2016 and show whether effects reach
  longer maturities.
- **Nifty, India VIX, USD/INR** are used to tell policy news from information effects
  (section 9).
- **US 10-year, VIX and Brent** capture global shocks on the same day, which also move
  Indian rates.

**Why the decisions were checked by hand.** `data/raw/decisions.csv` holds all 62 decisions
(rate change, stance, votes), each checked against the minutes text and flagged
`verified = 1`. The pipeline refuses to run on unverified rows. A single wrong decision
would shift the regressors for that meeting.

**Why market data are not in the repository.** Investing.com and FBIL data are licensed.
`download_data.py` and [`docs/DATA_GUIDE.md`](docs/DATA_GUIDE.md) rebuild them.

**Timing details that matter**
- **Minutes come out at 17:00 IST**, after the Indian bond market closes, so the market
  reacts on the **next trading day**. That day is the "event day".
- **Global controls** use the previous calendar day's change, because US markets close after
  India's. Using the same-day US change would include news that arrived after Indian markets
  closed.
- **CPI release days** get a dummy variable. Indian CPI came out at 17:30 until 12 Nov 2024
  and at 16:00 since. Inflation data released close to the minutes would otherwise be
  confused with the minutes' effect.

---

## 5. Step 1 – Turning the minutes into data

**What:** Each set of minutes is split into six signed statements, and each member's vote is
recorded: yes or no, the rate they voted for, and any vote against the stance.
Code: `src/parse_minutes.py`, `src/members.py`.

**How:**
- The HTML is converted to text, keeping the vote tables intact.
- Statement headers ("Statement by Dr. Michael Debabrata Patra") mark where each statement starts.
- Names are matched to a registry of all 22 members since 2016, including role changes (for
  example, Michael Patra moved from Executive Director to Deputy Governor in January 2020).
- Votes come from the voting table; dissents about the stance come from the resolution text.

**Result:** all 62 meetings parse into exactly six statements and six votes (372 statements).

**Why:** Everything later depends on knowing who said what and how they voted. The parser
was checked against unusual layouts (missing titles, "Dr.Pami Dua" with no space, tables
nested inside tables) until every meeting parsed correctly.

---

## 6. Step 2 – Measuring what each member says

**What:** Each statement gets a set of scores. Code: `src/score_llm.py`,
`score_dictionary.py`, `score_vader.py`.

### 6.1 The main measure: an LLM

Gemini (`gemini-3.5-flash-lite`) reads each statement and returns:

| Field | Scale | Meaning |
|---|---|---|
| `hawkishness` | −2 to +2 | The policy stance the statement argues for |
| `preferred_action` | cut / hold / hike | What the member wants done now |
| `lean` | −1, 0, +1 | Looser, in line with, or tighter than the adopted decision |
| `reservation` | 0, 1, 2 | Full support, support with reservations, argues against |
| `next_move` | −1, 0, +1 | Direction the member signals for the next meeting |
| `uncertainty`, `conditionality` | 0–2 | How uncertain or conditional the language is |

**Choices and why:**
- **Why an LLM rather than a word list.** Central-bank language is subtle. "Growth is
  strong" can be hawkish (no need to cut) even though it sounds positive. A word list
  struggles with this; an LLM reads the argument. The validation below confirms the LLM is
  much closer to the votes than the alternatives.
- **Names, years and months are masked.** So the model judges the text, not the speaker's
  reputation, and cannot easily match the statement to events it knows happened later.
- **Temperature 0.** So the same statement always gets the same score.
- **The adopted decision is given in the prompt.** "Lean" and "reservation" only make sense
  relative to what was decided. (Section 15 describes a check that removes this.)
- **Every answer is cached** under a hash of the prompt and model name, so reruns
  reproduce the scores exactly without new API calls.
- **One LLM only** is a project constraint. Sections 15 and 17 describe how this is checked
  without a second model.

### 6.2 Benchmarks

- **Dictionary score:** counts hawkish and dovish words, matching whole words only and
  handling negation ("not raise"). *Why:* a transparent, standard method; shows what a
  simpler approach finds.
- **VADER sentiment:** general positive/negative sentiment. *Why:* to show that general
  sentiment is not the same as policy stance (it turns out to be almost unrelated:
  correlation −0.04 with the LLM).

---

## 7. Step 3 – Checking the text measure against votes

**What:** Before using the scores, check that they track something real. The recorded votes
are an objective benchmark. Code: `src/validate_votes.py`.

| Check | Result |
|---|---|
| LLM preferred action = recorded vote | **369 of 369** classifiable statements |
| Reservation score separates the 40 formal dissenters from the rest | AUC **0.977** (1 = perfect) |
| Sign of lean = direction of dissent, among dissenters | 92.5% |
| Average hawkishness at cuts / holds / hikes, LLM | −1.55 / 0.08 / 1.20 |
| Same, dictionary | −1.17 / −0.30 / 0.63 |
| Correlation LLM vs dictionary | 0.48 |
| Correlation LLM vs VADER | −0.04 |

**Hidden dissent** (yes-voters with reservation ≥ 1) appears in **15.1%** of yes-votes,
compared with a **10.8%** formal dissent rate.

**Why this check, and its limit.** Matching votes shows the LLM understands the basic
position. But the paper's regressor is *how much more hawkish* members are than the
Governor, which goes beyond the vote. Only human coding can validate that finer reading,
which is why the hand-coding exercise (section 15) matters.

---

## 8. Step 4 – Building the "news in the minutes" variable

**Definition:**

> **Surprise** = (average hawkishness of the five non-Governor members) − (Governor's hawkishness)

Also split into an **internal gap** (Deputy Governor and Executive Director minus Governor)
and an **external gap** (three external members minus Governor).

**Why the gap to the Governor, not the average tone:**
1. **The Governor's view is already public.** He explains the decision on decision day. What
   the market does not know until the minutes is where the others stand.
2. **Differencing removes common tone.** When the whole committee sounds hawkish because
   inflation is high, that is already known. The gap measures only relative positions.
3. **This is tested, not assumed** (section 12.2): entering members and Governor separately
   gives coefficients of opposite sign and similar size, which is what the gap implies.

**Why split internal and external:** internal members are RBI staff and may know more about
the RBI's own thinking; external members are appointed by the government and may have
different views. Earlier work (Mahambare and Pathak 2021) found the two groups' tone has
different market effects, so the split is a natural test.

---

## 9. Step 5 – Measuring decision-day surprises

**What:** For every decision day, measure how much of the decision was a surprise, and
whether the surprise was about policy or about the RBI's view of the economy.
Code: `src/shocks.py`, `src/decision_day.py`.

**How:**
1. **Target and path factors** (Gürkaynak, Sack and Swanson 2005). Take the decision-day
   change in rates across maturities and find the two main common factors with principal
   components. Rotate them so the "path" factor has no effect on the shortest rate.
   - *Target* = surprise about today's rate.
   - *Path* = surprise about future rates (forward guidance).
2. **Policy vs information split** (Jarociński and Karadi 2020). If rates rise and stocks
   fall, it is a policy shock. If rates rise and stocks also rise, the decision revealed good
   news about the economy: an information effect. Both a simple sign split and a full
   rotation method are computed.
3. **Predictability check** (Bauer and Swanson 2023). Test whether the surprises could be
   predicted from data available before the meeting.

**Results:**
- 62 events; the first factor explains 79% of decision-day rate changes.
- 42% of decisions show the information-effect pattern.
- The T-bill-based target surprise is partly predictable (R² 0.40, p = 0.04); the OIS-based
  one is not (p = 0.70).
- Decision days are 3–11 times more volatile than ordinary days, depending on maturity.

**Choices and why:**
- **Why build this at all.** Minutes tone is correlated with the decision. Without
  controlling for the decision-day surprise, the minutes would get credit for news the
  market already had two weeks earlier.
- **Why T-bills as the main factor set.** They cover all 62 meetings; OIS covers 51. The two
  target factors are closely related (correlation 0.84). An OIS-based version is a
  robustness check.
- **Why no consensus forecasts.** A survey-based surprise was tried, but market-based
  surprises are standard and do not depend on the survey's timing.

---

## 10. Step 6 – The minutes-day event study

**The regression (one per maturity):**

> Change in rate on the event day (bp) = a + **b × Surprise** + decision-day target and path
> shocks + signed hidden dissent + US 10-year + VIX + Brent + CPI-day dummy + error

**Choices and why:**

| Choice | Why |
|---|---|
| **One-day window** (the next trading day) | The narrowest window available with daily data, so least contaminated by other news. A two-day window is a robustness check. |
| **Decision-day shocks as controls** | So *b* measures news in the minutes beyond the decision. |
| **Signed hidden dissent as a control** | So the gap is not picking up the reservations of yes-voters. |
| **Global controls** | Indian rates move with US rates, risk appetite and oil. |
| **CPI-day dummy** | Inflation releases near the minutes would otherwise be attributed to them. |
| **HC3 standard errors** | Robust to unequal variance across events and suited to small samples. |
| **Several maturities** | A policy-expectations story predicts the effect is largest at the short end (6 months to 2 years) and fades at 10 years. That pattern is itself evidence. |

**Headline result (per 1-point gap):**

| Maturity | Effect (bp) | p-value | Events |
|---|---|---|---|
| 3-month OIS | +1.3 | 0.022 | 51 |
| 6-month OIS | +2.0 | 0.003 | 53 |
| **1-year OIS** | **+2.3** | **0.015** | 53 |
| 2-year OIS | +2.0 | 0.049 | 53 |
| 5-year OIS | +2.0 | 0.089 | 53 |
| 1-year G-sec | +4.3 | 0.020 | 62 |
| 10-year G-sec | +0.7 | 0.585 | 62 |

**How big is that?** The gap typically varies by a fraction of a point to about one point
across meetings, so a typical minutes release moves the 1-year rate by about 1–2 bp. Small,
but in line with minutes effects found for other central banks, and the effect does not
reverse (section 11).

**Over two days** the effect is larger: 6-month +2.8 bp (p = 0.001), 1-year +3.4 bp
(p = 0.008), 2-year +4.0 bp (p = 0.009).

---

## 11. Step 7 – Testing whether the result is real

A coefficient like this could come from chance, from something already happening before the
release, or from a few unusual meetings. Each test below targets one of these.

### 11.1 Placebo tests

**What a placebo is:** running the same regression where there should be no effect. If an
effect appears there, the method is producing it, not the minutes.

| Placebo | Why it is a good test | Result |
|---|---|---|
| **Day before release** | The market cannot know the tone before 17:00 on release day. An effect the day before would mean the gap is picking up a trend or leaked information. | Null: 1-year −0.3 bp (p = 0.65) |
| **1,000 random days** | Shows what coefficients look like by pure chance on days with no minutes. | The real 1-year coefficient beats 99.6% of random-day draws |

### 11.2 Other statistical checks

| Check | Why | Result |
|---|---|---|
| **Randomisation inference**: reshuffle the gap across meetings 1,000+ times | Does not rely on normal-distribution assumptions, which matter with ~50 events | 1-year p = 0.007; 6-month p < 0.001 |
| **Holm correction** across all maturities | Testing many maturities raises the chance of a false positive | Only 6-month survives (p = 0.043) |
| **Drop any one meeting** | Is one meeting driving it? | 6-month and 1-year stay significant at 5% in every case |
| **Drop any one year** | Is one year driving it? | 1-year stays significant at 10% in 89% of cases |
| **Persistence**: cumulative change over 5 days | If the market overreacted, it should reverse | No reversal; grows to about 3.4 bp |
| **Variance test**: are minutes days more volatile? | A basic test of whether minutes carry news at all, without text | Only mildly (1-year OIS variance ratio 1.75, p = 0.08). The text explains the direction of moves, not their size |

### 11.3 Robustness of the 1-year OIS result

| Variant | Why | Effect (bp) | p |
|---|---|---|---|
| Baseline | — | 2.29 | 0.013 |
| No decision-day controls | Do the controls change the story? | 1.96 | 0.024 |
| OIS-based decision-day shocks | Alternative surprise measure | 2.11 | 0.039 |
| Drop unscheduled meetings | Emergency meetings (e.g. COVID, May 2022) are unusual | 2.11 | 0.019 |
| Drop the 3 most influential meetings | Outlier check | 1.96 | 0.031 |
| Members minus resolution tone | Benchmark against the official resolution instead of the Governor | 2.21 | 0.045 |
| Internal members only | — | 3.69 | 0.003 |
| **Exclude COVID (Mar 2020 – Dec 2021)** | Is the result a COVID episode? | **1.37** | **0.386** |
| **Dictionary tone instead of LLM** | Does a simpler text measure find it? | **−0.81** | **0.563** |

The last two rows are the two real weaknesses: the effect is concentrated in 2020–21, and
only the LLM measure finds it.

---

## 12. Step 8 – Extensions and new ideas tried

All in `src/extensions.py`, outputs in `outputs/tables/ext_*.csv`.

### 12.1 Whose words? Internal vs external

| 1-year OIS | Effect (bp) | p |
|---|---|---|
| Internal gap | +3.5 | 0.006 |
| External gap | +0.2 | 0.68 |
| Test internal = external | — | 0.025 |

By role: Deputy Governor +1.8 (p = 0.006), Executive Director +1.7 (p = 0.16), externals
+0.2 (p = 0.72).

**Why it might be:** internal members are RBI insiders, so markets may read their
differences from the Governor as signals about the RBI's own future direction. In the
**1-year G-sec**, however, the external gap is the significant one (2.6 bp, p = 0.03), so the
internal result is specific to OIS.

### 12.2 News or tone level?

Entering members' and the Governor's hawkishness separately: members +1.6, Governor −2.2
(1-year OIS). "Equal and opposite" is not rejected (p = 0.54).
**Why test this:** it confirms the market responds to the *difference*, which is what the
"news" argument predicts, rather than the overall tone.

### 12.3 COVID interaction

Instead of just dropping 2020–21, allow a separate effect for those 11 meetings:
4.8 bp in COVID meetings (p < 0.001) vs 1.7 bp outside (p = 0.24); difference p = 0.10.
**Why:** dropping the period throws away information; the interaction shows the effect is
present but weaker outside COVID, not reversed.

### 12.4 Replicating Mahambare and Pathak (2021)

Using their design (dictionary tone *levels*, G-sec yields) in their sample (to Aug 2021),
external tone has the larger effect on the 2-year G-sec (+3.4 bp, p = 0.03). It disappears
after August 2021 and does not appear with our news measure.
**Why:** to reconcile our "internal" result with their "external" result. The two findings
answer different questions (level vs news) in different periods.

### 12.5 A non-LLM measure

A text model (TF-IDF with ridge regression) was trained to predict members' own votes from
their words, each year scored by a model trained on the other years.
Its statement scores correlate 0.32 with the LLM's, but its meeting-level gap does not
(0.01), and it does not reproduce the result.
**Why:** to see whether the result can be found without the LLM. It cannot, so the result
rests on the LLM, which makes the human validation essential.

### 12.6 Do the minutes forecast future policy? (exploratory)

Outcome: change in the repo rate over the next 1–4 meetings. Controls: current decision and
what the OIS curve already priced. Standard errors adjusted for overlapping horizons.

| Measure | 3 meetings ahead | 4 meetings ahead | Outside COVID |
|---|---|---|---|
| External members' words (gap) | +17 bp, p = 0.075 | +24 bp, p = 0.052 | ~+2 to +4 bp, not significant |
| External members' formal dissent votes (no LLM) | +16.5 bp, p = 0.025 | +24 bp, p = 0.03 | ~+6 to +7 bp, not significant |

After 2022 the dissent-vote result is strong (+23 to +35 bp, p < 0.01). With words and votes
together, neither is significant: they carry the same information (correlation 0.75).

**Why try this:** if external members' views predict where policy goes, but markets only
price internal members' words, that would be a new and striking finding. **The recheck
showed it is not robust**, so it is reported as exploratory. The dissent-vote version is
attractive because it needs no LLM.

### 12.7 Do markets under-use the minutes?

If markets ignored useful information, rates should drift in its direction afterwards. OIS
drift from the event day to the next meeting is unrelated to either gap (p ≥ 0.27).
**Not supported.**

### 12.8 Other null results

- **Hidden dissent** is not priced at the short end (1-year OIS p = 0.29).
- **Uncertainty** and dispersion of members' views do not move rates.
- **Predicting the next decision:** text adds nothing beyond votes and market pricing
  (joint p = 0.15).

**Why report nulls:** they are informative (the market prices the gap, not the dissent
count) and referees value honest reporting.

---

## 13. Results summary

| Claim | Status |
|---|---|
| A hawkish members-minus-Governor gap raises short OIS rates on minutes day | **Holds** (concentrated in 2020–21; LLM-dependent) |
| The effect comes from internal RBI members | **Holds for OIS** |
| It is the gap (news), not the tone level | **Holds** |
| Hidden dissent is common (15% of yes-votes) | **Holds** (measurement) |
| Hidden dissent is priced | Not supported |
| Text helps predict the next decision | Not supported |
| External words or dissent votes forecast the repo path | **Exploratory**, not robust outside COVID |
| Markets under-use the minutes | Not supported |

---

## 14. How this relates to existing research

| Paper | What they did | What this project adds |
|---|---|---|
| **Mahambare and Pathak (2021)**, *Economics Letters* | Next-day G-sec yields on internal and external tone levels, 30 meetings to Aug 2021; external tone matters more | News measure (gap to the Governor), OIS rates, twice the sample, decision-day controls, placebos; reconciles the two results (12.4) |
| **Sil et al. (2024); Kumar, Sil, Kurup and Paramanik (2025)** | Disagreement between statements and votes | LLM measure validated on votes; shows hidden dissent is not priced |
| **Lakdawala and Sengupta** | RBI decision-day surprises to early 2023 | Target/path series with information split extended to 2026 |
| **Patnaik (EPW 2022)** | Splits RBI policy and information shocks | Extended to 2026 and used as controls |
| **FOMC and Riksbank minutes studies** | Minutes-day reactions using unattributed or aggregate text | Prices named members' statements |

**What is new:** the price response to the news in attributed statements, the internal vs
external split under that measure, and the reconciliation with Mahambare and Pathak.
**What is not new:** measuring hidden dissent; minutes-day reactions in India as such.

---

## 15. What is done, built-but-not-run, and not done

### Done
- Scraping, parsing and hand-verified decisions for all 62 meetings.
- LLM, dictionary and VADER scores; validation against recorded votes.
- Decision-day surprise series with policy/information split.
- Minutes-day event study with placebos, robustness checks and extensions.
- Mahambare–Pathak replication; exploratory forecasting tests.
- 8 unit tests, all passing; `RESULTS.md` generated straight from output tables.

### Built but not yet run on real data

These two pieces of code exist but have not yet produced results, because they need either
your Gemini key or human coders.

**`python run_pipeline.py llm-checks`** – two checks of the LLM scores using the **same**
model (the project uses only one LLM):
1. **Second prompt.** Differently worded and does *not* tell the model the adopted
   decision. *Why:* a referee may argue that telling the model the decision biases the
   scores. If results hold under the second prompt, the headline does not depend on prompt
   wording.
2. **Date-guessing (look-ahead) probe.** Asks the model to guess the year of each masked
   statement. *Why:* the model was trained after these meetings and might use hindsight. If
   it cannot date statements, hindsight is unlikely; if it can, the code checks whether the
   result holds on statements it could not date.

"Tested only with a stub" means the code was checked with a stand-in that returns fake
answers (the build environment cannot reach Gemini). It runs and saves files correctly, but
no real scores exist yet. It needs about 744 calls (~1 hour on the free tier). Results go to
`outputs/tables/ext_llm_checks.csv` after rerunning `analyze`.

**`python run_pipeline.py validate-draw-meetings`** – creates the hand-coding sheet
`outputs/tables/human_sample.csv`: all six statements from 20 meetings (120 statements),
names and dates masked, rows shuffled, with the adopted decision shown on each row.
*Why whole meetings:* the regressor is a within-meeting gap, so coding all six statements of
a meeting lets us validate the gap itself, not just individual scores. *Why masked and
shuffled:* so coders cannot tell who the Governor is or what happened next. The sheet exists
but has not been coded. Instructions: [`docs/HAND_CODING.md`](docs/HAND_CODING.md).

### Not done
- Two-coder human validation.
- A literature check on whether RBI dissent votes predicting policy is already known.
- Intraday OIS data.
- Final references and author details (`LICENSE`, `CITATION.cff`).

---

## 16. Limitations

| Limitation | Why it matters | What addresses it |
|---|---|---|
| **One LLM** | Non-LLM measures do not reproduce the result | Same-model checks and human coding (section 15) |
| **Small sample** (~50 OIS events) | Limited power; many outcomes tested | Randomisation inference, Holm correction, leave-one-out |
| **COVID concentration** | Effect much stronger in 2020–21 | COVID interaction reported openly |
| **Daily data** | Other news on the reaction day adds noise | Placebos; intraday data would help |
| **Look-ahead risk** | The model was trained after the sample | Masking; date-guessing probe |

---

## 17. Next steps

1. **Two-coder hand validation** of the 120 statements (8–10 hours per coder).
2. **Run `llm-checks`** with the same Gemini model, then `analyze` again.
3. **Literature check** on RBI dissent votes and future policy before developing 12.6.
4. **Finish the draft** around the pricing result, with forecasting as an exploratory section.
5. **Submit**: *Emerging Markets Review* (primary target).

---

## 18. How to run everything

Commands are for Windows PowerShell; on Mac/Linux use `export VAR=...` instead of `$env:VAR = ...`.

```powershell
pip install -r requirements.txt

# 1. Data
python download_data.py                       # RBI minutes, FBIL rates, FRED series
# Put the Investing.com files listed in docs/DATA_GUIDE.md into data_downloads/
python run_pipeline.py market                 # assemble market series
python run_pipeline.py parse                  # minutes -> statements and votes
python run_pipeline.py check                  # fix any FAIL before going on

# 2. Text scores (cached; reruns are free)
$env:GEMINI_API_KEY = "..."                   # never commit or paste keys
$env:RBI_LLM_MODEL  = "gemini-3.5-flash-lite"
python run_pipeline.py score --llm --vader
python run_pipeline.py llm-checks             # same-model checks (recommended)

# 3. Analysis
python run_pipeline.py shocks                 # decision-day surprises
python run_pipeline.py build                  # merge into analysis datasets
python run_pipeline.py analyze                # all regressions and tests
python run_pipeline.py figures
python run_pipeline.py report
python -m pytest -q tests
```

Hand validation:
```powershell
python run_pipeline.py validate-draw-meetings # creates outputs/tables/human_sample.csv
# Code it following docs/HAND_CODING.md, then:
python run_pipeline.py validate               # writes outputs/tables/validation.csv
```

More detail: [`docs/RUNBOOK.md`](docs/RUNBOOK.md).

---

## 19. Repository layout

| Path | Contents |
|---|---|
| `run_pipeline.py` | Runs each stage |
| `download_data.py` | Downloads RBI minutes, FBIL and FRED data |
| `src/parse_minutes.py`, `src/members.py` | Minutes → attributed statements and votes; member registry |
| `src/score_llm.py`, `score_dictionary.py`, `score_vader.py` | Text measures; same-model checks |
| `src/shocks.py`, `src/decision_day.py` | Decision-day target/path and policy/information shocks |
| `src/build_dataset.py` | Member-, meeting- and daily-level datasets |
| `src/event_study.py`, `src/robustness.py` | Minutes-day event study, placebos, robustness |
| `src/extensions.py` | Section 12: internal vs external, news vs level, COVID, replication, non-LLM measure, persistence, jackknife, forecasting, drift |
| `src/linkage.py`, `src/predictability.py` | Links to future decisions; forecasting the next decision |
| `src/validate.py`, `src/validate_votes.py` | Hand-coding sheet and agreement; validation against votes |
| `outputs/tables/`, `outputs/figures/` | All results |
| `RESULTS.md` | Every number in one place |
| `paper/draft.md` | Working draft |
| `docs/DATA_GUIDE.md` | Which files to download and where to put them |
| `docs/RUNBOOK.md` | Step-by-step run instructions |
| `docs/CODEBOOK.md`, `docs/HAND_CODING.md` | Rules and steps for human coding |
| `docs/research_design.md` | Pre-analysis plan |
| `tests/` | Unit tests |

---

## 20. Data and licence

RBI minutes are public documents. Investing.com and FBIL data are licensed and not
redistributed; `download_data.py` rebuilds what can be downloaded automatically.
Code is released under the MIT licence.

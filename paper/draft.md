# Whose Words Move Rates? Attributed Member Statements in RBI Minutes and the Indian Yield Curve

*Working draft, November 2026. All numbers come from `outputs/tables/`; see `RESULTS.md`.*

## Abstract
The Reserve Bank of India publishes a signed statement by every Monetary Policy Committee
member 14 days after each decision. Using all 62 meetings from October 2016 to October 2026
(372 statements), we measure the news in the minutes as the gap between the hawkishness of
the other five members and that of the Governor, whose views are already public on decision
day. A one-point gap raises the 6-month OIS rate by 2.0 bp (p = 0.003) and the 1-year rate
by 2.3 bp (p = 0.015) on the first trading day after release, controlling for decision-day
shocks. The response comes from the internal RBI members (3.5 bp against 0.2 bp for external
members; equality rejected, p = 0.025), does not appear on the day before release, and does
not reverse within a week. It is stronger in 2020–21 and is not reproduced by dictionary
measures. Reservations among members who vote with the majority are common (15.1% of
yes-votes) but are not priced.

## 1. Introduction
Votes are announced with the decision; reasons arrive two weeks later. Since the Governor
explains the decision in the policy statement and press conference, the new information in
the minutes is how far the other members stand from him. The RBI is one of very few central
banks that attribute statements to named members, which makes it possible to ask whose
words markets price.

Contribution relative to the closest work:
- **Mahambare and Pathak (2021)** regress next-day government bond yields on the tone *level*
  of internal and external members for 30 meetings to August 2021 and report a larger
  association for external members. We measure news rather than level, add OIS rates, double
  the sample, control for decision-day shocks and add placebo and randomisation tests. In
  their design and sample we find a similar pattern for the 2-year G-sec (external 3.4 bp,
  p = 0.03); it is absent after August 2021 and in the news measure.
- **Kumar, Sil, Kurup and Paramanik (2025)** and **Sil et al. (2024)** measure disagreement
  between statements and votes. We add a generative-LLM measure validated against the vote
  record and show that it is not priced.
- **Lakdawala and Sengupta** provide decision-day surprises to early 2023. We extend a
  target/path series to 2026 and use it as a control.
- Outside India, minutes-day studies for the FOMC and the Riksbank use unattributed or
  aggregate text.

## 2. Data and measurement
- **Minutes:** 62 releases parsed into six statements each; every vote matched to the table.
- **Text score:** a temperature-zero LLM with names, years and months masked returns
  hawkishness (−2…+2), preferred action, lean relative to the adopted decision and a
  reservation score. Preferred action equals the recorded vote in all 369 classifiable cases;
  the reservation score separates the 40 formal dissenters with AUC 0.977.
- **Surprise:** mean hawkishness of non-Governor members minus the Governor's.
- **Markets:** FBIL OIS (from 2018; 51–53 events), T-bills and G-secs (62 events). Minutes
  are released after the close, so the reaction day is the next trading day.
- **Decision-day shocks:** target and path factors with a policy/information split; 42% of
  decisions have the sign pattern of an information effect.

## 3. Results
**3.1 Headline.** Table 4 of `RESULTS.md`. The effect is 1.3–2.3 bp per point from 3 months to
2 years and absent at 10 years. Only the 6-month estimate survives a Holm correction across
all outcomes (p = 0.043). Minutes days are not much more volatile than ordinary days
(variance ratio 1.75 for 1-year OIS, p = 0.08): the text explains direction, not size.

**3.2 News, not level.** With members' and the Governor's hawkishness entered separately, the
coefficients are of opposite sign and similar size (1-year OIS: +1.6 and −2.2; equality of
magnitudes not rejected, p = 0.54).

**3.3 Whose words.** Internal 3.5 bp (p = 0.006), external 0.2 bp (p = 0.68) for 1-year OIS.
By role, the Deputy Governor's gap carries most of it. In the 1-year G-sec the external gap is
the significant one (2.6 bp, p = 0.03), so the internal result is specific to the swap market.

**3.4 Robustness.** Pre-release placebo null; random-day placebo beaten in 99.6% of draws;
significant at 5% after dropping any single meeting (6-month and 1-year). The cumulative
response rises to about 3.4 bp after five days. Limits: the estimate is 4.8 bp in the 11
COVID-window meetings and 1.7 bp (p = 0.24) outside, with equality not rejected (p = 0.10);
dictionary and supervised bag-of-words gaps do not reproduce it.

**3.5 Hidden dissent.** 15.1% of yes-votes carry a reservation, against 10.8% formal dissents.
The signed measure does not move short rates (1-year OIS p = 0.29; 10-year G-sec 6.0 bp,
p = 0.08) and the text does not improve forecasts of the next decision.

**3.6 Exploratory: who leads policy.** Net signed dissent votes of external members predict
the repo change over the next three and four meetings (16.5 bp, p = 0.025; 24.0 bp, p = 0.03)
beyond the OIS curve, strongly after 2022 but not outside the COVID window; OIS does not
drift after minutes day. We report this as a direction for further work.

## 4. Limitations
One LLM; no human validation yet; daily rather than intraday windows; about 50 OIS events;
concentration in 2020–21; many outcomes tested.

## 5. Next steps
Two-coder human validation of 120 statements; same-model prompt variant and date-guess
look-ahead probe; intraday OIS; a literature check and longer sample for the dissent result.

## References (to complete)
Mahambare and Pathak (2021), *Economics Letters*; Kumar, Sil, Kurup and Paramanik (2025),
*Applied Economics Letters*; Sil et al. (2024); Lakdawala and Sengupta; Gürkaynak, Sack and
Swanson (2005); Jarociński and Karadi (2020); Bauer and Swanson (2023); Tsang and Yang
(arXiv); Trivedi and Ghosh (2025), *Journal of Policy Modeling*.

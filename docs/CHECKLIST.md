# Things to do that are easy to miss

## Before collecting data: novelty checks (highest risk first)
- [ ] Find and read "Doomed in din or synced with signal" (on MPC dissent; seen only as a
      title on ResearchGate).
- [ ] Find and read the EPW 2022 (vol. 57, no. 50) paper on RBI announcements and information
      shocks. If it already runs a Jarociński–Karadi split, cite it and position the shock
      series as an update + extension.
- [ ] Read Wahi, Ranjan & Kumar (Journal of Asian Economics 104, 2026) in full. This is the
      main competitor: an OIS event study to 2024.
- [ ] Check the Lakdawala & Sengupta (JMCB 2025) shock database: end date, and whether it
      separates information shocks.
- [ ] Check whether the IMF WP 2025/109 cross-country LLM paper includes India.
- [ ] Check "Tang & Yang 2026" vs Tsang & Yang (FOMC hidden dissent); cite correctly.
- [ ] Google Scholar + SSRN sweep: "RBI minutes", "MPC minutes India yields",
      "Reserve Bank of India information effect", "India monetary policy surprises OIS".
- [ ] Fix the reading list:
      - Banerjee & Paramanik is not about India.
      - Sil et al. 2023/2024 is one paper.
      - "Garga et al." has two versions with different authors.
      - The "Anand et al. 2021" reference needs a full citation.

## Data integrity
- [ ] Verify every row of `decisions.csv`: decision, repo, stance, unscheduled. Add April
      and June 2026.
- [ ] Replace drafted minutes release dates with actual press-release dates (holidays).
- [ ] Confirm minutes are released at 17:00 IST for the whole sample. If any early minutes
      came out during market hours, set `release_after_market=0` for them.
- [ ] Hand-code dissent direction for every No vote and stance dissent.
- [ ] Inspect yield jumps flagged by `check` (benchmark roll-overs) near event days.
- [ ] Note the October 2026 vote split: sources conflict (unanimous vs two stance dissents).
      The vote table in the minutes settles it.
- [ ] Record every data source, download date and licence in a `data/SOURCES.md` file. You
      will need this for the paper's data appendix.

## Research hygiene
- [ ] Freeze `docs/research_design.md` (git tag) before the first real run.
- [ ] Do the human coding before seeing market results; use two coders if at all possible.
- [ ] Pin the LLM model id. Record the model's training cutoff in the paper (look-ahead
      bias discussion).
- [ ] Keep `data/processed/llm_cache.jsonl`; it makes the scores reproducible.
- [ ] Never publish Bloomberg/Refinitiv data (`.gitignore` covers the downloads). The
      replication package should include code + the derived shock series only, if the licence
      allows.
- [ ] Report null results as nulls. With about 60 events, a precise null on minutes days is
      still informative.

## Writing and positioning
- [ ] Section order:
      1. intro;
      2. institutional setting (RBI Act Sec. 45ZL: minutes on the 14th day, 17:00 release);
      3. data and measurement (shock series, LLM measures, validation);
      4. decision-day surprises;
      5. minutes days (variance → direction → uncertainty);
      6. linkage and predictability;
      7. robustness;
      8. conclusion.
- [ ] Target journals: Emerging Markets Review, Journal of Asian Economics, Economic
      Modelling, Journal of International Money and Finance (stretch: JMCB with intraday data).
- [ ] Before SSRN: send the draft to one or two people working on RBI (IGIDR / NIPFP / ISI
      authors in the literature) for comments.
- [ ] JEL codes: E52, E58, G14, C55.

## Possible extensions (only after the main paper)
- Intraday OIS windows (Bloomberg) for both decision and minutes days.
- Press-conference Q&A text, or audio, as a third communication channel.
- External members' interviews between meetings as additional events.

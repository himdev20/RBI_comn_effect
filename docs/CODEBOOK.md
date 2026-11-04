# Codebook for human validation (same definitions as the LLM prompt)

Code each statement in `outputs/tables/human_sample.csv` **without** looking at the machine
scores. For each statement, look up the adopted decision and stance of that meeting in
`decisions.csv`.

## human_hawk (−2 … +2): the policy stance the text argues for
- **−2:** argues clearly for easing now or soon; growth concerns dominate; inflation risks
  dismissed.
- **−1:** leans towards easing or patience; downside risks to growth emphasised.
- **0:** balanced; risks on both sides; no lean on the policy path.
- **+1:** leans towards tightening or holding firm; upside inflation risks emphasised.
- **+2:** argues clearly for tightening now or soon; inflation and expectations dominate.

Judge the **policy stance**, not whether the economy is described as doing well. Strong
growth described approvingly is not dovish.

## human_lean (−1 / 0 / +1): relative to the ADOPTED decision and stance
- **0:** the reasoning fits the adopted decision.
- **−1:** voted for it but the reasoning points looser, e.g. "I vote for the pause, but
  space for easing may open up soon."
- **+1:** voted for it but the reasoning points tighter, e.g. "I support the cut, but further
  easing must be approached with caution."

## human_reservation (0 / 1 / 2)
- **0:** full support.
- **1:** supports the decision but voices reservations, a different emphasis, or a condition.
- **2:** argues against the decision or the stance (normally a recorded dissent).

## Procedure
- Read the whole statement; the vote sentence is usually at the end.
- Spend 3–5 minutes per statement. Do not look up later decisions.
- With two coders: code independently, compute agreement (`validate`), then discuss
  disagreements and record a consensus column only after the kappa has been computed.

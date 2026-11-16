"""LLM scoring of member statements (and, optionally, the resolution text).

Per member statement the model returns, as JSON:
  hawkishness       -2..+2  desired policy path conveyed by the text (not economic sentiment)
  preferred_action  cut | hold | hike   at THIS meeting, as argued in the text
  preferred_bp      integer size if stated, else null
  lean              -1 | 0 | +1  text leans more dovish / in line / more hawkish than the ADOPTED decision+stance
  reservation       0 full support, 1 voices reservations, 2 argues against the adopted decision or stance
  next_move         cut | hold | hike | unclear   direction the member signals for the NEXT meeting(s)
  uncertainty       0..2   how much the member stresses uncertainty about the outlook
  conditionality    0..2   how explicitly the future path is conditioned on incoming data

`lean` and `reservation` among members who voted Yes are the hidden-dissent measures
(Tsang & Yang's concept, but measured on attributed, real-time text).

Providers: RBI_LLM_PROVIDER=anthropic (ANTHROPIC_API_KEY) or gemini (GEMINI_API_KEY).
Reproducibility: temperature 0, model pinned via RBI_LLM_MODEL (recorded in the output),
member names / years / months masked, every response cached by hash of (model, prompt).
Look-ahead caveat: a model trained after the sample may 'know' later decisions; masking
reduces but does not remove this. Compare results with the dictionary/VADER scores.
"""
import os
import re
import json
import time
import hashlib
import logging
import pandas as pd
from src import config
from src.members import REGISTRY

log = logging.getLogger("llm")
# provider: explicit RBI_LLM_PROVIDER, else Gemini whenever a GEMINI_API_KEY is set
PROVIDER = os.environ.get("RBI_LLM_PROVIDER",
                          "gemini" if os.environ.get("GEMINI_API_KEY") and not os.environ.get("ANTHROPIC_API_KEY")
                          else "anthropic").lower()
MODEL = os.environ.get("RBI_LLM_MODEL", "gemini-2.5-flash" if PROVIDER == "gemini" else "claude-sonnet-5-5")
ACT = {"cut": -1, "hold": 0, "hike": 1}

MEMBER_PROMPT = """You are an expert monetary economist coding the individual statement of a member of
India's Monetary Policy Committee (MPC), published in the MPC minutes two weeks after the meeting.

The decision the Committee ADOPTED at this meeting was: {decision}

Read the member's statement and return ONLY a JSON object with these keys:
"hawkishness": integer -2..2. The stance on the desirable policy path the text conveys:
   -2 strongly dovish (argues for easing / prioritises growth), -1 mildly dovish, 0 balanced,
   +1 mildly hawkish, +2 strongly hawkish (argues for tightening / prioritises inflation).
   Judge the policy stance, not whether the economy is described positively.
"preferred_action": "cut", "hold" or "hike" -- the action the member argues for at this meeting.
"preferred_bp": integer basis points the member argues for (positive number), or null if not stated.
"lean": integer -1, 0 or 1 -- compared with the ADOPTED decision and stance above, does the text lean
   more dovish (-1), is it in line (0), or lean more hawkish (+1)? A member can vote for the
   decision and still lean (e.g. supports a hold but stresses that easing should come soon).
"reservation": integer 0, 1 or 2 -- 0 fully supports the adopted decision and stance; 1 supports it but
   voices reservations or a different emphasis; 2 argues against the decision or the stance.
"next_move": "cut", "hold", "hike" or "unclear" -- the direction the member signals for upcoming meetings.
"uncertainty": integer 0..2 -- how strongly the member stresses uncertainty about the outlook.
"conditionality": integer 0..2 -- 0 no data-dependence language, 2 future path explicitly conditioned on data.

STATEMENT:
{text}"""

RESOLUTION_PROMPT = """You are an expert monetary economist coding the resolution of India's Monetary
Policy Committee. Return ONLY a JSON object with keys:
"hawkishness": integer -2..2 (policy stance conveyed about the desirable path; -2 strongly dovish, +2 strongly hawkish),
"next_move": "cut", "hold", "hike" or "unclear" (direction signalled for upcoming meetings),
"uncertainty": integer 0..2, "conditionality": integer 0..2.

RESOLUTION:
{text}"""


def mask(t: str) -> str:
    for canon in REGISTRY:
        for part in re.split(r"[\s.]+", canon):
            if len(part) > 3:
                t = re.sub(rf"\b{re.escape(part)}\b", "[MEMBER]", t, flags=re.I)
    t = re.sub(r"\b(19|20)\d{2}(-\d{2})?\b", "[YEAR]", t)
    t = re.sub(r"\b(January|February|March|April|May|June|July|August|September|October|"
               r"November|December|Jan|Feb|Mar|Apr|Jun|Jul|Aug|Sep|Sept|Oct|Nov|Dec)\b\.?", "[MONTH]", t)
    return t


def decision_text(bp, stance=None):
    if pd.isna(bp):
        return "(not provided)"
    bp = int(bp)
    s = ("keep the policy repo rate unchanged" if bp == 0 else
         f"{'raise' if bp > 0 else 'reduce'} the policy repo rate by {abs(bp)} basis points")
    if isinstance(stance, str) and stance.strip():
        s += f", with the policy stance '{stance.strip()}'"
    return s + "."


def _load_cache():
    d = {}
    if config.LLM_CACHE.exists():
        for l in config.LLM_CACHE.read_text().splitlines():
            if l.strip():
                r = json.loads(l); d[r["key"]] = r
    return d


def _gemini(prompt):
    """Google Gemini via the public REST API (no SDK needed). Needs GEMINI_API_KEY."""
    import requests
    url = f"https://generativelanguage.googleapis.com/v1beta/models/{MODEL}:generateContent"
    body = {"contents": [{"role": "user", "parts": [{"text": prompt}]}],
            "generationConfig": {"temperature": 0, "maxOutputTokens": 2048, "responseMimeType": "application/json"}}
    # key goes in a header (never in the URL, so it cannot leak into error messages)
    r = requests.post(url, headers={"x-goog-api-key": os.environ["GEMINI_API_KEY"]}, json=body, timeout=120)
    if r.status_code in (429, 500, 503):                       # rate limit / overloaded: wait, then retry
        time.sleep(30); raise RuntimeError(f"Gemini busy ({r.status_code}); waited 30s")
    if r.status_code in (400, 401, 403, 404):                  # not retryable: wrong model or key
        raise SystemExit(f"Gemini returned {r.status_code}: {r.text[:300]}\n"
                         "Run  python run_pipeline.py llm-models  to see model ids your key can use, "
                         "then set $env:RBI_LLM_MODEL to one of them.")
    r.raise_for_status()
    return "".join(p.get("text", "") for p in r.json()["candidates"][0]["content"]["parts"])


def list_gemini_models():
    """Print the Gemini model ids this key can call with generateContent."""
    import requests
    r = requests.get("https://generativelanguage.googleapis.com/v1beta/models",
                     headers={"x-goog-api-key": os.environ["GEMINI_API_KEY"]}, params={"pageSize": 200}, timeout=60)
    if r.status_code != 200:
        raise SystemExit(f"Gemini returned {r.status_code}: {r.text[:300]}")
    ms = [m for m in r.json().get("models", []) if "generateContent" in m.get("supportedGenerationMethods", [])]
    for m in ms:
        print(f"{m['name'].replace('models/', ''):45s} {m.get('displayName', '')}")
    return ms


def _ask(client, prompt, tries=10):
    for k in range(tries):
        try:
            if PROVIDER == "gemini":
                txt = _gemini(prompt)
            else:
                msg = client.messages.create(model=MODEL, max_tokens=300, temperature=0,
                                             messages=[{"role": "user", "content": prompt}])
                txt = "".join(getattr(b, "text", "") for b in msg.content)
            return json.loads(re.search(r"\{.*\}", txt, re.S).group(0))
        except Exception as e:          # API hiccup, rate limit or malformed JSON -> retry
            log.warning("retry %d: %s", k + 1, str(e)[:160]); time.sleep(3 * (k + 1))
    raise RuntimeError("LLM failed repeatedly; inspect the prompt/response")


def _clip(v, lo, hi):
    try:
        return max(lo, min(hi, int(v)))
    except (TypeError, ValueError):
        return None


def _cached_score(client, cache, fh, prompt):
    key = hashlib.sha256((MODEL + prompt).encode()).hexdigest()
    if key not in cache:
        j = _ask(client, prompt)
        cache[key] = dict(key=key, model=MODEL, **j)
        fh.write(json.dumps(cache[key]) + "\n"); fh.flush()
    return cache[key]


def run(path=None, limit=None, resolutions=True):
    if "RBI_LLM_MODEL" not in os.environ:
        log.warning("RBI_LLM_MODEL not set; using %s. Pin an exact model id for the paper.", MODEL)
    if PROVIDER == "gemini":
        if not os.environ.get("GEMINI_API_KEY"):
            raise SystemExit("set GEMINI_API_KEY (Google AI Studio key)")
        client = None
    else:
        import anthropic
        client = anthropic.Anthropic()
    st = pd.read_csv(path or config.PROC / "member_statements.csv")
    dec = pd.read_csv(config.DECISIONS_CSV, dtype={"meeting_date": str})
    if "stance" not in dec:
        dec["stance"] = None
    st = st.merge(dec[["meeting_date", "decision_bp", "stance"]], on="meeting_date", how="left")
    if limit:
        st = st.head(limit)
    cache, rows = _load_cache(), []
    with open(config.LLM_CACHE, "a") as fh:
        for _, r in st.iterrows():
            p = MEMBER_PROMPT.format(decision=decision_text(r.decision_bp, r.stance), text=mask(r.statement)[:20000])
            new = hashlib.sha256((MODEL + p).encode()).hexdigest() not in cache
            j = _cached_score(client, cache, fh, p)
            if PROVIDER == "gemini" and new:
                time.sleep(float(os.environ.get("RBI_LLM_SLEEP", 4)))   # stay under free-tier per-minute limits
            rows.append(dict(statement_id=r.statement_id,
                             hawk_llm=_clip(j.get("hawkishness"), -2, 2),
                             pref_action_llm=ACT.get(str(j.get("preferred_action")).lower()),
                             pref_bp_llm=j.get("preferred_bp"),
                             lean_llm=_clip(j.get("lean"), -1, 1),
                             reservation_llm=_clip(j.get("reservation"), 0, 2),
                             next_move_llm=ACT.get(str(j.get("next_move")).lower()),
                             unc_llm=_clip(j.get("uncertainty"), 0, 2),
                             cond_llm=_clip(j.get("conditionality"), 0, 2), llm_model=MODEL))
        out = pd.DataFrame(rows)
        out.to_csv(config.PROC / "scores_llm.csv", index=False)
        log.info("scored %d statements with %s", len(out), MODEL)
        mt = config.PROC / "meeting_texts.csv"
        if resolutions and mt.exists():
            res = []
            for _, r in pd.read_csv(mt, dtype={"meeting_date": str}).iterrows():
                if not isinstance(r.resolution_text, str) or len(r.resolution_text.split()) < 50:
                    continue
                j = _cached_score(client, cache, fh, RESOLUTION_PROMPT.format(text=mask(r.resolution_text)[:20000]))
                res.append(dict(meeting_date=r.meeting_date, hawk_resolution=_clip(j.get("hawkishness"), -2, 2),
                                next_move_resolution=ACT.get(str(j.get("next_move")).lower()),
                                unc_resolution=_clip(j.get("uncertainty"), 0, 2)))
            if res:
                pd.DataFrame(res).to_csv(config.PROC / "scores_llm_resolution.csv", index=False)
    return out


# ----------------------------------------------------------------------------- same-model checks
# Both checks use the SAME model as the main scores (set the same RBI_LLM_MODEL). They answer two
# referee questions without a second LLM: (1) is the score an artefact of one prompt, or of telling
# the model the adopted decision?  (2) can the model tell WHEN a masked statement was written, i.e.
# could it be using knowledge of later events (look-ahead)?
VARIANT_PROMPT = """Below is a statement written by one member of a central bank's rate-setting committee.
Names and dates have been removed. Rate ONLY the monetary policy leaning of the author.

Return ONLY a JSON object: {{"score": <integer>}} using this scale:
 2 = clearly wants tighter policy than now / inflation is the dominant worry
 1 = leans towards tighter policy
 0 = balanced, no lean either way
-1 = leans towards easier policy
-2 = clearly wants easier policy than now / growth is the dominant worry
Ignore whether the economic outlook is described in good or bad terms.

TEXT:
{text}"""

DATE_PROMPT = """Below is a statement by a member of India's Monetary Policy Committee. Names, years and
months have been removed. Guess the calendar year in which it was written (2016-2026).
Return ONLY a JSON object: {{"year": <integer>, "confidence": <integer 0-2>}}

TEXT:
{text}"""


def _client():
    if PROVIDER == "gemini":
        if not os.environ.get("GEMINI_API_KEY"):
            raise SystemExit("set GEMINI_API_KEY (Google AI Studio key)")
        return None
    import anthropic
    return anthropic.Anthropic()


def _loop(prompt_tpl, parse, outfile, limit=None):
    client = _client()
    st = pd.read_csv(config.PROC / "member_statements.csv")
    if limit:
        st = st.head(limit)
    cache, rows = _load_cache(), []
    with open(config.LLM_CACHE, "a") as fh:
        for _, r in st.iterrows():
            p = prompt_tpl.format(text=mask(r.statement)[:20000])
            new = hashlib.sha256((MODEL + p).encode()).hexdigest() not in cache
            j = _cached_score(client, cache, fh, p)
            if PROVIDER == "gemini" and new:
                time.sleep(float(os.environ.get("RBI_LLM_SLEEP", 4)))
            rows.append(dict(statement_id=r.statement_id, meeting_date=r.meeting_date, llm_model=MODEL, **parse(j)))
    out = pd.DataFrame(rows)
    out.to_csv(config.PROC / outfile, index=False)
    log.info("wrote %s (%d statements, %s)", outfile, len(out), MODEL)
    return out


def run_variant(limit=None):
    """Second prompt, same model: no decision context, different wording, scale listed hawkish-first."""
    return _loop(VARIANT_PROMPT, lambda j: dict(hawk_llm_v2=_clip(j.get("score"), -2, 2)), "scores_llm_v2.csv", limit)


def run_date_test(limit=None):
    """Look-ahead probe: can the model date a masked statement?"""
    return _loop(DATE_PROMPT, lambda j: dict(guess_year=_clip(j.get("year"), 2000, 2100), guess_conf=_clip(j.get("confidence"), 0, 2)),
                 "lookahead_date_guess.csv", limit)


if __name__ == "__main__":
    import sys
    logging.basicConfig(level=logging.INFO, format="%(message)s")
    lim = next((int(a.split("=")[1]) for a in sys.argv if a.startswith("--limit=")), None)
    run(limit=lim)

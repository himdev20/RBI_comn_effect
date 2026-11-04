"""Parse RBI MPC minutes (HTML, PDF or TXT) into member-level statements, votes and
the embedded resolution text.

Layout verified on the Jun-2025 and Dec-2025 minutes (rbi.org.in press releases):
  * the resolution, then one or more tables headed "Voting on the Resolution to ...",
    columns "Member | Vote" (+ "Magnitude of policy repo rate reduction (basis points)"
    when members differ on size), rows like "Shri Saugata Bhattacharya | Yes | 25";
  * then one block per member headed "Statement by Dr. Nagesh Kumar", numbered paras.
Older minutes (2016-2020) may differ: run `python -m src.parse_minutes --debug` and check
that every meeting yields 6 statements and 6 votes before scoring anything.
"""
import re
import sys
import logging
import subprocess
import pandas as pd
from bs4 import BeautifulSoup
from src import config
from src.members import canonical

log = logging.getLogger("parse")
TITLE = r"(?:Dr\.?|Shri|Smt\.?|Prof\.?|Professor|Mr\.?|Ms\.?|Mrs\.?)"
NAME = r"[A-Z][A-Za-z\.\-]*(?:\s+[A-Z][A-Za-z\.\-]*){0,4}"
HEADER_RE = re.compile(
    rf"^\s*(?:\d+\.\s*)?(?:Statement(?:s)?\s+(?:by|of)\s+)(?P<name>{TITLE}\s+{NAME})\s*:?\s*$"
    rf"|^\s*(?P<name2>{TITLE}\s+{NAME})(?:\s*[’']s\s+[Ss]tatement)\s*:?\s*$")
VOTE_HEAD_RE = re.compile(r"^\s*Voting\s+on\s+the\s+(?:Resolution|resolution|proposal)", re.I)
VOTE_ROW_RE = re.compile(
    rf"(?P<name>{TITLE}\s+{NAME}?)\s*(?:\|\s*)?(?P<vote>Yes|No)\b(?:\s*\|?\s*(?P<mag>\d{{1,3}})\b)?")
TAIL_RE = re.compile(r"(Chief General Manager|General Manager\s*$|Press Release\s*:?\s*\d{4}-\d{2,4}/\d+"
                     r"|^\([A-Z][A-Za-z.\s]{2,40}\)$)")
MIN_WORDS = 40
REPO_RE = re.compile(r"policy repo rate[^.]{0,120}?(\d{1,2}\.\d{1,2})\s*per\s*cent", re.I)
STANCE_RE = re.compile(r"(withdrawal of accommodation|calibrated tightening|accommodative|neutral)", re.I)


def parse_decision(resolution: str):
    """Repo rate and stance as stated in the resolution text (cross-check for decisions.csv)."""
    m = REPO_RE.search(resolution or "")
    st = None
    for sent in re.split(r"(?<=[.;])\s+", resolution or ""):
        if re.search(r"\bstance\b|remain focused on", sent, re.I):
            k = STANCE_RE.search(sent)
            if k:
                st = k.group(1).lower(); break
    return (float(m.group(1)) if m else None), st


def html_to_text(html: str) -> str:
    soup = BeautifulSoup(html, "lxml")
    for t in soup(["script", "style"]):
        t.decompose()
    for tr in soup.find_all("tr"):                      # keep table rows on one line
        cells = [c.get_text(" ", strip=True) for c in tr.find_all(["td", "th"])]
        tr.replace_with(soup.new_string("\n" + " | ".join(cells) + "\n"))
    return re.sub(r"\n\s*\n+", "\n", soup.get_text("\n"))


def pdf_to_text(path) -> str:
    try:
        import pdfplumber
        with pdfplumber.open(path) as pdf:
            return "\n".join((p.extract_text() or "") for p in pdf.pages)
    except ImportError:
        return subprocess.run(["pdftotext", "-layout", str(path), "-"], capture_output=True, text=True).stdout


def read_any(path) -> str:
    path = str(path)
    if path.lower().endswith(".pdf"):
        return pdf_to_text(path)
    raw = open(path, errors="ignore").read()
    return html_to_text(raw) if path.lower().endswith((".html", ".htm")) else raw


def _parse_votes(lines, start, stop):
    """Parse vote tables between line indices [start, stop). Returns list of blocks."""
    blocks, cur = [], None
    for i in range(start, stop):
        l = lines[i]
        if VOTE_HEAD_RE.match(l):
            cur = dict(label=l.strip(), rows={}); blocks.append(cur); continue
        if cur is None:
            continue
        for m in VOTE_ROW_RE.finditer(l):
            canon = canonical(m.group("name"))[0]
            cur["rows"][canon] = (1 if m.group("vote") == "Yes" else 0,
                                  int(m.group("mag")) if m.group("mag") else None)
    for b in blocks:
        lab = b["label"].lower()
        b["kind"] = "stance" if ("stance" in lab and "repo" not in lab) else "rate"
    return blocks


def parse_text(text: str, meeting_date: str, release_date: str = ""):
    """Return (statements: list[dict], meeting: dict)."""
    lines = [l.strip() for l in text.split("\n") if l.strip()]
    heads = []
    for i, l in enumerate(lines):
        if 3 < len(l) < 90:
            m = HEADER_RE.match(l)
            if m:
                heads.append((i, m.group("name") or m.group("name2")))
    first_head = heads[0][0] if heads else len(lines)
    vstart = next((i for i, l in enumerate(lines[:first_head]) if VOTE_HEAD_RE.match(l)), None)
    blocks = _parse_votes(lines, vstart, first_head) if vstart is not None else []
    if not blocks:   # fallback: votes anywhere (older layouts) -- logged
        log.warning("%s: no 'Voting on the Resolution' block found; using loose vote search", meeting_date)
        blocks = _parse_votes(["Voting on the Resolution (inferred)"] + lines, 0, len(lines) + 1)
    rate = next((b for b in blocks if b["kind"] == "rate"), {"rows": {}})
    stance = next((b for b in blocks if b["kind"] == "stance"), {"rows": {}})
    # resolution text: from "...resolution that is set out below" (if present) to the first vote table
    rstart = next((i + 1 for i, l in enumerate(lines[:vstart or first_head])
                   if re.search(r"(set out below|adopted the (following )?resolution)", l, re.I)), 0)
    resolution = " ".join(lines[rstart:(vstart if vstart is not None else first_head)])

    out, seen = [], set()
    for k, (i, name) in enumerate(heads):
        end = heads[k + 1][0] if k + 1 < len(heads) else len(lines)
        body_lines = []
        for l in lines[i + 1:end]:
            if TAIL_RE.search(l):
                break
            body_lines.append(l)
        body = " ".join(body_lines)
        canon, mtype, role = canonical(name, meeting_date)
        if len(body.split()) < MIN_WORDS or canon in seen:
            continue
        seen.add(canon)
        if mtype == "unknown":
            log.warning("Unknown member %r in meeting %s - add to members.REGISTRY", name, meeting_date)
        v = rate["rows"].get(canon, (None, None))
        out.append(dict(meeting_date=meeting_date, release_date=release_date, member=canon,
                        member_type=mtype, role=role, governor=int(role == "Governor"),
                        vote_yes=v[0], vote_bp=v[1],
                        stance_vote_yes=stance["rows"].get(canon, (None, None))[0],
                        n_words=len(body.split()), statement=body))
    repo_parsed, stance_parsed = parse_decision(resolution)
    meeting = dict(meeting_date=meeting_date, n_statements=len(out), n_votes=len(rate["rows"]),
                   repo_parsed=repo_parsed, stance_parsed=stance_parsed,
                   vote_label=rate.get("label", ""), stance_vote_label=stance.get("label", ""),
                   resolution_words=len(resolution.split()), resolution_text=resolution)
    return out, meeting


def find_file(meeting_date):
    for ext in (".html", ".htm", ".pdf", ".txt"):
        f = config.HTML_DIR / f"{meeting_date}{ext}"
        if f.exists():
            return f
    return None


def run(debug=False) -> pd.DataFrame:
    urls = pd.read_csv(config.URLS_CSV, dtype=str).fillna("")
    rows, meets = [], []
    for _, r in urls.iterrows():
        f = find_file(r.meeting_date)
        if f is None:
            log.warning("missing minutes file for %s", r.meeting_date); continue
        got, meet = parse_text(read_any(f), r.meeting_date, r.release_date)
        if debug or len(got) != 6 or meet["n_votes"] != 6:
            log.info("%s: %d statements, %d votes (%s)%s", r.meeting_date, len(got), meet["n_votes"],
                     ", ".join(g["member"] for g in got), "" if len(got) == 6 else "  <-- CHECK")
        rows += got; meets.append(meet)
    df = pd.DataFrame(rows)
    if df.empty:
        raise SystemExit("No statements parsed - inspect the files and adjust HEADER_RE.")
    df.insert(0, "statement_id", [f"S{i:04d}" for i in range(len(df))])
    df.to_csv(config.PROC / "member_statements.csv", index=False)
    pd.DataFrame(meets).to_csv(config.PROC / "meeting_texts.csv", index=False)
    log.info("wrote %d statements, %d meetings", len(df), df.meeting_date.nunique())
    return df


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO, format="%(message)s")
    run(debug="--debug" in sys.argv)

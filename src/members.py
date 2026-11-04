"""MPC member registry. VERIFY against the minutes before relying on it:
unknown names are labelled 'unknown' and logged, never silently dropped.

Roles: Governor; DG_MP = Deputy Governor in charge of monetary policy (statutory member);
ED_MP = RBI officer nominated by the Central Board; External = appointed by GoI."""
import re

REGISTRY = {  # canonical name -> (type, role)
    "Urjit Patel": ("internal", "Governor"),
    "Shaktikanta Das": ("internal", "Governor"),
    "Sanjay Malhotra": ("internal", "Governor"),
    "R. Gandhi": ("internal", "DG_MP"),
    "Viral Acharya": ("internal", "DG_MP"),
    "Michael Patra": ("internal", "DG_MP"),      # ED_MP 2016-19, DG_MP 2020-25 (role by date below)
    "Poonam Gupta": ("internal", "DG_MP"),
    "Janak Raj": ("internal", "ED_MP"),
    "Mridul Saggar": ("internal", "ED_MP"),
    "Rajiv Ranjan": ("internal", "ED_MP"),
    "Indranil Bhattacharyya": ("internal", "ED_MP"),
    "Chetan Ghate": ("external", "External"),
    "Pami Dua": ("external", "External"),
    "Ravindra Dholakia": ("external", "External"),
    "Shashanka Bhide": ("external", "External"),
    "Ashima Goyal": ("external", "External"),
    "Jayanth Varma": ("external", "External"),
    "Nagesh Kumar": ("external", "External"),
    "Saugata Bhattacharya": ("external", "External"),
    "Ram Singh": ("external", "External"),
}
# Patra sat on the MPC as Executive Director before becoming Deputy Governor (Jan 2020).
ROLE_BY_DATE = {"Michael Patra": [("2016-01-01", "ED_MP"), ("2020-01-15", "DG_MP")]}

_TITLE = re.compile(r"^(dr|shri|smt|prof|professor|mr|ms|mrs|kum)\.?\s+", re.I)


def strip_title(name: str) -> str:
    name = re.sub(r"\s+", " ", name).strip(" .,:;|")
    return _TITLE.sub("", name).strip()


def _tokens(name: str):
    return [t for t in re.sub(r"[.\-]", " ", name.lower()).split() if t]


def canonical(name: str, date: str = None):
    """Return (canonical_name, type, role). Match on last name; if several registry
    entries share it, require a matching first initial among the given-name tokens."""
    toks = _tokens(strip_title(name))
    if not toks:
        return strip_title(name), "unknown", "unknown"
    cands = [c for c in REGISTRY if _tokens(c)[-1] == toks[-1]]
    if len(cands) > 1:
        cands = [c for c in cands if _tokens(c)[0][0] in {t[0] for t in toks[:-1]}]
    if len(cands) != 1:
        return strip_title(name), "unknown", "unknown"
    canon = cands[0]
    mtype, role = REGISTRY[canon]
    if date and canon in ROLE_BY_DATE:
        for start, r in ROLE_BY_DATE[canon]:
            if str(date) >= start:
                role = r
    return canon, mtype, role

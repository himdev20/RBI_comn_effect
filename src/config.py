"""Central paths and constants. Every module reads paths from here; `use_root`
re-points them (used for the synthetic demo and the tests)."""
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]

# Tenors are detected from the columns present in yields.csv, in this order.
TENOR_CANDIDATES = ["ois_1m", "ois_3m", "ois_6m", "ois_1y", "ois_2y", "ois_5y",
                    "tbill_91d", "tbill_182d", "tbill_364d", "gsec_1y", "gsec_2y", "gsec_5y", "gsec_10y"]
# Price series analysed as 100 x log changes (percent): equity index and USD/INR (+ = rupee depreciates)
RETURN_SERIES = ["nifty", "bank_nifty", "usdinr"]
# Factor tenors for decision-day surprises: OIS if available, else the T-bill/2y fallback
FACTOR_OIS = ["ois_1m", "ois_3m", "ois_6m", "ois_1y", "ois_2y"]
FACTOR_FALLBACK = ["tbill_91d", "tbill_182d", "tbill_364d", "gsec_2y"]
# Ordinal stance scale used to code stance changes (edit if you code stances differently)
STANCE_ORDER = {"accommodative": -1, "neutral": 0, "withdrawal of accommodation": 1, "calibrated tightening": 2}
GLOBAL_CONTROLS = ["us10y", "vix", "brent"]          # optional columns in yields.csv
REF_TENOR = "gsec_10y"                               # defines the Indian trading calendar
REPO_START = 6.50                                    # repo rate before the first MPC decision (Oct 2016)
# MoSPI released CPI at 17:30 IST (after the 17:00 G-sec close) until Oct 2024 and at 16:00
# (market open) from 12 Nov 2024. Before the switch the market reacts the next trading day.
CPI_4PM_FROM = "2024-11-12"
COVID_WINDOW = ("2020-03-01", "2021-12-31")


def use_root(root, tables=None, figs=None):
    """Point every data path at `root` (with raw/, processed/ underneath)."""
    g = globals()
    root = Path(root)
    g["DATA_ROOT"] = root
    g["RAW"] = root / "raw"
    g["HTML_DIR"] = g["RAW"] / "minutes_html"
    g["MARKET_DIR"] = g["RAW"] / "market"
    g["PROC"] = root / "processed"
    g["TABLES"] = Path(tables) if tables else root / "tables"
    g["FIGS"] = Path(figs) if figs else root / "figures"
    g["URLS_CSV"] = g["RAW"] / "minutes_urls.csv"
    g["DECISIONS_CSV"] = g["RAW"] / "decisions.csv"
    g["RESOLUTION_CSV"] = g["RAW"] / "resolution_scores.csv"
    g["DISSENT_CSV"] = g["RAW"] / "dissent_direction.csv"
    g["YIELDS_CSV"] = g["MARKET_DIR"] / "yields.csv"
    g["CPI_DATES_CSV"] = g["MARKET_DIR"] / "cpi_release_dates.csv"
    g["LLM_CACHE"] = g["PROC"] / "llm_cache.jsonl"
    g["CONSENSUS_CSV"] = g["RAW"] / "consensus.csv"        # optional: poll median per meeting
    g["CPI_CSV"] = g["MARKET_DIR"] / "cpi.csv"
    g["OTHER_EVENTS_CSV"] = g["MARKET_DIR"] / "other_events.csv"  # optional: date, after_market, label             # optional: monthly CPI y/y with release dates
    g["SERIES_MAP"] = g["MARKET_DIR"] / "series_map.csv"   # maps downloaded files -> yields.csv columns
    g["DOWNLOADS"] = g["MARKET_DIR"] / "downloads"
    for d in (g["HTML_DIR"], g["MARKET_DIR"], g["PROC"], g["TABLES"], g["FIGS"], g["DOWNLOADS"]):
        d.mkdir(parents=True, exist_ok=True)


# default: real data under data/, outputs under outputs/
use_root(ROOT / "data", tables=ROOT / "outputs" / "tables", figs=ROOT / "outputs" / "figures")

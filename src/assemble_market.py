"""Build raw/market/yields.csv from the files you downloaded (one file per series).

List each download in raw/market/series_map.csv:
  name        target column: gsec_10y, tbill_91d, ois_1y, nifty, usdinr, us10y, vix, brent, ...
  file        file name inside raw/market/downloads/
  date_col    column holding the date (e.g. 'Date', 'observation_date', 'DATE')
  value_col   column holding the value (e.g. 'Price', 'Close', 'DGS10', 'Yield')
  units       percent | bp | level      (yields must end up in percent; bp is divided by 100)
  date_format optional strftime format if dates are ambiguous (e.g. %d-%m-%Y); else auto
Handles Investing.com (thousand separators, 'Change %'), FRED ('.' for missing) and
Excel files. Prints coverage per series so gaps are visible before any analysis.
"""
import re
import logging
import numpy as np
import pandas as pd
from src import config

log = logging.getLogger("market")


def _read(path):
    p = str(path).lower()
    if p.endswith((".xlsx", ".xls")):
        return pd.read_excel(path)
    return pd.read_csv(path, sep=None, engine="python")


def _num(s):
    return pd.to_numeric(s.astype(str).str.replace(",", "").str.replace("%", "").str.strip()
                         .replace({".": np.nan, "": np.nan, "-": np.nan, "nan": np.nan}), errors="coerce")


def run():
    mp = pd.read_csv(config.SERIES_MAP).fillna("")
    out = None
    for _, r in mp.iterrows():
        f = config.DOWNLOADS / r.file
        if not f.exists():
            log.warning("missing download %s (series %s)", f, r["name"]); continue
        d = _read(f)
        d.columns = [str(c).strip().strip('"') for c in d.columns]
        if r.date_col not in d or r.value_col not in d:
            raise SystemExit(f"{r.file}: columns {list(d.columns)}; expected {r.date_col!r} and {r.value_col!r}")
        dt = pd.to_datetime(d[r.date_col], format=r.date_format or None, dayfirst=False, errors="coerce") \
            if r.date_format else pd.to_datetime(d[r.date_col], errors="coerce")
        v = _num(d[r.value_col])
        if r.units == "bp":
            v = v / 100.0
        s = pd.Series(v.values, index=dt).dropna()
        s = s[~s.index.isna()].groupby(level=0).last().sort_index()
        s.name = r["name"]
        log.info("%-12s %s .. %s  n=%d  last=%.4f", s.name, s.index.min().date(), s.index.max().date(), len(s), s.iloc[-1])
        out = s.to_frame() if out is None else out.join(s, how="outer")
    if out is None:
        raise SystemExit("No series assembled - check series_map.csv")
    out.index.name = "date"
    bad = [c for c in out if c in config.TENOR_CANDIDATES + ["us10y"] and (out[c].dropna() > 25).mean() > .01]
    if bad:
        raise SystemExit(f"{bad} look like bp or prices, not percent yields - fix 'units' in series_map.csv")
    out.to_csv(config.YIELDS_CSV)
    log.info("wrote %s with columns %s", config.YIELDS_CSV, list(out.columns))
    return out


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO, format="%(message)s")
    run()

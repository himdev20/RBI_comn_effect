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


def _files(pattern):
    """`file` may be a glob (e.g. 'NIFTY 50_*.csv' for one NSE file per year); searched in
    raw/market/downloads/ and in data_downloads/ at the project root."""
    hits = []
    for d in (config.DOWNLOADS, config.ROOT / "data_downloads"):
        hits += sorted(d.glob(pattern)) if d.exists() else []
    return hits


def _load(files, r):
    parts = []
    for f in files:
        d = _read(f)
        d.columns = [str(c).strip().strip('"').strip() for c in d.columns]
        dc = r.date_col if r.date_col in d else d.columns[0]
        vc = next((c for c in str(r.value_col).split(";") if c in d), None)
        if vc is None:
            raise SystemExit(f"{f.name}: columns {list(d.columns)}; none of {r.value_col!r} found")
        dt = pd.to_datetime(d[dc], format=r.date_format or None, errors="coerce") if r.date_format \
            else pd.to_datetime(d[dc], errors="coerce")
        parts.append(pd.DataFrame({"date": dt, "v": _num(d[vc])}))
    return pd.concat(parts)


def run():
    mp = pd.read_csv(config.SERIES_MAP).fillna("")
    out = None
    for _, r in mp.iterrows():
        files = _files(r.file)
        if not files:
            log.warning("no file matching %r (series %s)", r.file, r["name"]); continue
        raw = _load(files, r)
        dt, v = raw.date, raw.v
        if r.units == "bp":
            v = v / 100.0
        s = pd.Series(v.values, index=dt).dropna()
        s = s[~s.index.isna()].groupby(level=0).last().sort_index()
        s.name = r["name"]
        log.info("%-12s %-34s %s .. %s  n=%d  last=%.4f", s.name, r.file[:34], s.index.min().date(), s.index.max().date(), len(s), s.iloc[-1])
        if out is None:
            out = s.to_frame()
        elif s.name in out:      # second source for the same series: back-fill ONLY before the first
            first = out[s.name].first_valid_index()   # date of the primary source (no day-by-day mixing,
            out = out.join(s.rename("_new"), how="outer")          # which would create spurious jumps)
            fill = out["_new"].where(out.index < first)
            out[s.name] = out[s.name].combine_first(fill)
            out.pop("_new")
            log.info("   %s: back-filled %d days before %s from %s", s.name, int(fill.notna().sum()), first.date(), r.file)
        else:
            out = out.join(s, how="outer")
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

"""Run ONCE on your own computer (Windows/Anaconda is fine), from this folder:

    python download_data.py

Downloads everything that can be fetched automatically:
  * the 62 RBI MPC minutes (press-release HTML pages; PDF fallback)  -> data/raw/minutes_html/
  * FBIL benchmarks: T-bill 3M/6M/12M (from Aug 2017), MIBOR-OIS 1M-5Y (from Apr 2018),
    USD/INR reference rate (from Jul 2018)                            -> data/raw/market/downloads/
  * FRED: US 10y (DGS10), VIX (VIXCLS), Brent (DCOILBRENTEU)          -> data/raw/market/downloads/
Safe to re-run: files already downloaded are skipped. Takes ~5 minutes.
Investing.com and NSE files must be downloaded by hand (see docs/DATA_GUIDE.md).
"""
import json
import time
import datetime as dt
from pathlib import Path
import requests
import pandas as pd

ROOT = Path(__file__).resolve().parent
RAW = ROOT / "data" / "raw"
MIN = RAW / "minutes_html"
DL = RAW / "market" / "downloads"
UA = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) "
                    "Chrome/124.0 Safari/537.36", "Accept-Language": "en-US,en;q=0.9"}
for d in (MIN, DL):
    d.mkdir(parents=True, exist_ok=True)
S = requests.Session(); S.headers.update(UA)


def get(url, **kw):
    for k in range(4):
        try:
            r = S.get(url, timeout=90, **kw)
            r.raise_for_status()
            return r
        except Exception as e:
            print(f"   retry {k + 1}: {url[:90]} ({e})"); time.sleep(4 * (k + 1))
    raise RuntimeError(f"failed: {url}")


def minutes():
    urls = pd.read_csv(RAW / "minutes_urls.csv", dtype=str)
    print(f"== RBI minutes ({len(urls)})")
    for _, r in urls.iterrows():
        html = MIN / f"{r.meeting_date}.html"
        if html.exists() and html.stat().st_size > 30000:
            continue
        try:
            b = get(r.url).content
            if len(b) > 30000 and b"Statement by" in b:
                html.write_bytes(b); print("   ok", r.meeting_date); time.sleep(1.5); continue
        except Exception as e:
            print("   html failed", r.meeting_date, e)
        pdf = MIN / f"{r.meeting_date}.pdf"
        pdf.write_bytes(get(r.pdf_url).content); print("   ok (pdf)", r.meeting_date); time.sleep(1.5)


FBIL = {"tbill": {"3 Months": "fbil_tbill_91d.csv", "6 Months": "fbil_tbill_182d.csv", "12 Months": "fbil_tbill_364d.csv"},
        "miborois": {"1M": "fbil_ois_1m.csv", "3M": "fbil_ois_3m.csv", "6M": "fbil_ois_6m.csv",
                     "1Y": "fbil_ois_1y.csv", "2Y": "fbil_ois_2y.csv", "5Y": "fbil_ois_5y.csv"},
        "refrates": {"INR / 1 USD": "fbil_usdinr.csv"}}


def fbil():
    print("== FBIL benchmarks")
    S.headers.update({"Referer": "https://www.fbil.org.in/"})
    for prod, tenors in FBIL.items():
        rows = []
        for y in range(2017, dt.date.today().year + 1):
            r = get(f"https://www.fbil.org.in/wasdm/{prod}/fetchfiltered",
                    params={"fromDate": f"{y}-01-01", "toDate": f"{y}-12-31", "authenticated": "false"})
            rows += r.json(); time.sleep(1)
        (DL / f"fbil_{prod}_raw.json").write_text(json.dumps(rows))
        df = pd.DataFrame(rows)
        key = "tenorName" if "tenorName" in df else "subProdName"
        df["Date"] = df.processRunDate.str[:10]
        print(f"   {prod}: {len(df)} rows; labels: {sorted(df[key].astype(str).unique())[:12]}")
        for lab, fn in tenors.items():
            s = df[df[key].astype(str).str.strip() == lab][["Date", "rate"]].drop_duplicates("Date", keep="last")
            if s.empty:
                print(f"   WARNING: no rows for {prod} '{lab}' - check the labels printed above"); continue
            s.rename(columns={"rate": "Rate"}).to_csv(DL / fn, index=False)
            print(f"   wrote {fn}: {s.Date.min()} .. {s.Date.max()} ({len(s)})")


def fred():
    print("== FRED")
    for sid in ["DGS10", "VIXCLS", "DCOILBRENTEU"]:
        r = get("https://fred.stlouisfed.org/graph/fredgraph.csv", params={"id": sid, "cosd": "2015-06-01"})
        (DL / f"{sid}.csv").write_bytes(r.content); print("   wrote", sid)


if __name__ == "__main__":
    for step in (minutes, fbil, fred):
        try:
            step()
        except Exception as e:
            print(f"!! {step.__name__} failed: {e}  (the other steps still ran)")
    print("\nDone. Now add the Investing.com and NSE files to data/raw/market/downloads/ and tell Claude.")

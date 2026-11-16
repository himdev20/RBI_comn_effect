"""Download the MPC minutes listed in data/raw/minutes_urls.csv (run on your own machine).

The url column can point to the press-release HTML page or straight to the PDF; the file
is saved as data/raw/minutes_html/<meeting_date>.<html|pdf>. If RBI blocks the request
(403) or the page is rendered by JavaScript, download the PDF in your browser and save it
under that name instead -- the parser reads .pdf, .html and .txt alike.
"""
import time
import logging
import requests
import pandas as pd
from src import config

UA = {"User-Agent": "Mozilla/5.0 (academic research; monetary policy minutes)"}
log = logging.getLogger("scrape")


def run(pause=3):
    urls = pd.read_csv(config.URLS_CSV, dtype=str).fillna("")
    for _, r in urls.iterrows():
        if not r.url or any((config.HTML_DIR / f"{r.meeting_date}{e}").exists() for e in (".html", ".pdf", ".txt")):
            continue
        try:
            resp = requests.get(r.url, headers=UA, timeout=60)
            resp.raise_for_status()
            is_pdf = r.url.lower().endswith(".pdf") or "pdf" in resp.headers.get("Content-Type", "").lower()
            out = config.HTML_DIR / f"{r.meeting_date}{'.pdf' if is_pdf else '.html'}"
            out.write_bytes(resp.content)
            log.info("saved %s", out.name)
        except Exception as e:
            log.error("FAILED %s: %s (save manually)", r.url, e)
        time.sleep(pause)


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO, format="%(message)s")
    run()

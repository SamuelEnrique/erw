"""Chain 701, part D's done line: a sample of equity_fundamentals_quarterly's figures found in the filings themselves.
For each company: its newest 10-Q in the table, the filing's index page on www.sec.gov, the primary 10-Q document, and a
search of the document's text for the table's quarterly revenue and shares outstanding as a filing prints them (in
millions with commas, in thousands, or whole). Two requests a company, a quarter of a second apart at least (the SEC
contact string from .env). Prints one line a figure: found or not, and the words around it."""
import html
import os
import re
import sys
import time

import pandas as pd
import requests

sys.path.insert(0, "warehouse/connectors")
import iso_prices as ip  # noqa: E402

ua = next(ln.split("=", 1)[1].strip() for ln in open(".env", encoding="utf-8") if ln.startswith("SEC_USER_AGENT="))
S = requests.Session()
S.headers["User-Agent"] = ua


def get(url):
    time.sleep(0.5)
    r = S.get(url, timeout=120)
    r.raise_for_status()
    return r.text


def forms(v):
    v = int(float(v))
    out = [f"{v:,}"]
    for d in (1_000_000, 1_000):
        if v % d == 0:
            out.append(f"{v // d:,}")
    return out


p = "warehouse/output/equity_fundamentals_quarterly.csv"
d = pd.read_csv(p, skiprows=ip.header_rows(p), dtype=str, keep_default_na=False)
tickers = sys.argv[1:] or ["CVX", "NEE", "KMI", "SLB", "DUK"]
lines = []
for tk in tickers:
    x = d[(d.x_ticker == tk) & (d.x_form == "10-Q")]
    last = x.vintage.max()
    y = x[x.vintage == last]
    end = y.ts_utc.max()
    y = y[y.ts_utc == end]
    idx = y.source_url.iloc[0]
    page = get(idx)
    m = re.search(r'href="(/Archives/edgar/data/[^"]+\.htm)"[^<]*</a></td>\s*<td[^>]*>\s*10-Q', page)
    if not m:
        m = re.search(r'href="(/(?:ix\?doc=/)?Archives/edgar/data/[^"]+\.htm)"', page)
    doc_url = "https://www.sec.gov" + m.group(1).replace("/ix?doc=", "")
    text = html.unescape(re.sub(r"<[^>]+>", " ", get(doc_url)))
    text = re.sub(r"\s+", " ", text)
    for var in ("revenue_3m_usd", "shares_outstanding"):
        z = y[y.variable == var]
        if z.empty:
            lines.append(f"{tk} {var}: not in the table for {end[:10]}")
            continue
        v, concept = z.value.iloc[0], z.x_concept.iloc[0]
        hit = None
        for f in forms(v):
            k = text.find(f)
            if k >= 0:
                hit = (f, text[max(0, k - 90):k + len(f) + 30])
                break
        lines.append(f"{tk} {end[:10]} {var} = {int(float(v)):,} ({concept}); " +
                     (f"FOUND as '{hit[0]}' in {doc_url}: ...{hit[1]}..." if hit else f"NOT FOUND in {doc_url} (forms {forms(v)})"))
for ln in lines:
    print(ln)
print(f"{sum(1 for ln in lines if 'FOUND as' in ln)} of {len(lines)} figures found in the filings")

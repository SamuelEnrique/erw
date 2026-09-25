#!/usr/bin/env python3
"""Carbon allowance auction results: California cap-and-trade (CARB) and RGGI, quarterly.

Energy Research Warehouse (ERW) connector, session 7 (docs/price-sources.md,
section 6). Writes two `series` tables:

| table                     | source                                   | unit of price |
|---------------------------|------------------------------------------|---------------|
| carb_auction_allowance_prices | CARB summary of joint auction results PDF | USD/tCO2 (metric ton) |
| rggi_auction_allowance_prices | RGGI "Allowance Prices and Volumes" HTML table | USD/short_ton |

    python warehouse/connectors/carbon_auctions.py [--table carb|rggi]

Entities: `carb:current_auction` and `carb:advance_auction` (CARB sells
current-vintage and advance-vintage allowances at each auction);
`rggi:current_auction` and `rggi:future_auction` (RGGI's 2009 to 2011 auctions
of future-vintage allowances). Variables: `settlement_price` (CARB) or
`clearing_price` (RGGI), `allowances_offered`, `allowances_sold`, and for RGGI
`ccr_allowances_sold` (Cost Containment Reserve), in allowances (unit `count`;
one allowance covers one metric ton of CO2 in California, one short ton in
RGGI). freq P3M: the auctions are quarterly. ts_utc is the auction date at
00:00:00Z for RGGI; the CARB summary gives the month only, so a CARB row sits
at the first of the auction month. A cell RGGI shows as "--" is not a value
and is omitted.

License: internal. CARB's terms for the summary are unconfirmed and RGGI's
page says only "(c) RGGI" (docs/price-sources.md); both stay internal until
confirmed. The CARB numbers come from a PDF: every auction line must parse
into exactly six numbers or the run fails.
"""

import argparse
import datetime as dt
import io
import os
import re
import sys
import traceback

import pandas as pd
import requests

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import iso_prices as ip  # noqa: E402

UA = {"User-Agent": "Mozilla/5.0 (ERW research warehouse)"}
CARB_URL = "https://ww2.arb.ca.gov/sites/default/files/2020-08/results_summary.pdf"
CARB_PAGE = "https://ww2.arb.ca.gov/our-work/programs/cap-and-trade-program/auction-information"
RGGI_URL = "https://www.rggi.org/auctions/auction-results/prices-volumes"
RGGI_PAGE = "https://www.rggi.org/auctions/auction-results"
STALE_DAYS = 150  # a quarterly auction plus publication lag
MONTHS = {m: i for i, m in enumerate(["January", "February", "March", "April", "May", "June", "July",
                                      "August", "September", "October", "November", "December"], 1)}
LINE_RE = re.compile(r"^(" + "|".join(MONTHS) + r") (\d{4}) (.*?)#\s*(\d+)\s+(.*)$")
QTY_RE = re.compile(r"\d{1,3}(?:,\d{3})*")


def get(url, what, log):
    def call():
        r = requests.get(url, timeout=120, headers=UA)
        if r.status_code != 200:
            raise RuntimeError(f"{what} HTTP {r.status_code}")
        return r
    r = ip.with_retries(what, call, log)
    log(f"GET {url}: {len(r.content)} bytes")
    return r


def parse_carb_line(rest):
    """'49,016,180 49,016,180 $32.48 6,481,750 6,481,750 $32.75' -> six numbers.
    pdfplumber splits some numbers with stray spaces ('78,82 5,717', '$26 .00'), so
    the spaces are dropped and the numbers are read by their comma grouping."""
    parts = re.sub(r"\s+", "", rest).split("$")
    if len(parts) != 3:
        raise ValueError(f"expected two prices: {rest!r}")
    q1 = QTY_RE.findall(parts[0])
    m = re.match(r"^(\d+\.\d{2})(.*)$", parts[1])
    if not m:
        raise ValueError(f"bad current price: {rest!r}")
    q2 = QTY_RE.findall(m.group(2))
    if len(q1) != 2 or len(q2) != 2 or not re.fullmatch(r"\d+\.\d{2}", parts[2]):
        raise ValueError(f"not six numbers: {rest!r}")
    n = [int(q.replace(",", "")) for q in q1 + q2]
    if "".join(q1) != parts[0] or "".join(q2) != m.group(2):
        raise ValueError(f"unparsed characters: {rest!r}")
    return n[0], n[1], float(m.group(1)), n[2], n[3], float(parts[2])


def carb(run_id, log):
    import pdfplumber
    r = get(CARB_URL, "CARB auction summary PDF", log)
    got = ip.utc_iso(pd.Timestamp.now(tz="UTC"))
    rows, updated = [], ""
    with pdfplumber.open(io.BytesIO(r.content)) as pdf:
        for pg in pdf.pages:
            for line in (pg.extract_text() or "").splitlines():
                line = line.strip()
                if line.startswith("Last updated"):
                    updated = line
                m = LINE_RE.match(line)
                if not m:
                    continue
                month, year, name, num, rest = m.groups()
                try:
                    vals = parse_carb_line(rest)
                except ValueError as e:
                    raise RuntimeError(f"CARB PDF line {line!r}: {e}")
                name = re.sub(r"\s+", "", name).replace("Joint", "Joint ").strip()
                rows.append((f"{year}-{MONTHS[month]:02d}-01T00:00:00Z", f"{name} #{num}", vals))
    if not rows:
        raise RuntimeError("CARB PDF: no auction lines parsed; layout changed")
    ts = [t for t, _, _ in rows]
    if len(set(ts)) != len(ts):
        raise RuntimeError("CARB PDF: two auctions in one month")
    log(f"  CARB: {len(rows)} auctions, {min(ts)[:7]} to {max(ts)[:7]}; {updated}")
    out = []
    for t, name, (co, cs, cp, ao, as_, ap) in rows:
        for ent, var, v, unit in [("current_auction", "settlement_price", cp, "USD/tCO2"),
                                  ("current_auction", "allowances_offered", co, "count"),
                                  ("current_auction", "allowances_sold", cs, "count"),
                                  ("advance_auction", "settlement_price", ap, "USD/tCO2"),
                                  ("advance_auction", "allowances_offered", ao, "count"),
                                  ("advance_auction", "allowances_sold", as_, "count")]:
            out.append(dict(entity=f"carb:{ent}", variable=var, ts_utc=t, value=v, unit=unit,
                            node=name, retrieved_at=got))
    s = pd.DataFrame(out).assign(freq="P3M", geo="US-CA", market="", source="carb:auction-results-summary",
                                 source_url=CARB_URL, vintage="")
    header = [
        "Energy Research Warehouse (ERW): California cap-and-trade (CARB, joint with Quebec) auction results",
        "Shape: series (docs/datastandard.md v0). freq P3M: ts_utc is the first of the auction month "
        "(the summary gives no day). node names the auction as CARB numbers it.",
        f"Retrieved: {run_id} (UTC) by warehouse/connectors/carbon_auctions.py",
        f"Run log: warehouse/output/logs/carbon_auctions_{run_id}.log",
        f"Raw files: warehouse/raw/carbon_auctions/{run_id}/ (not in git)",
        f"Source: California Air Resources Board, Summary of Joint Auction Settlement Prices and Results "
        f"(PDF, {updated or 'no update line'}), {CARB_URL}, linked from {CARB_PAGE}",
        "Prices in USD per metric ton of CO2e; allowances in allowances (1 allowance = 1 metric ton).",
        "License: internal. CARB terms for this summary are unconfirmed.",
    ]
    return s, header, dict(source="carb:auction-results-summary", publisher="California Air Resources Board (CARB)",
                           report="Summary of California and Joint Auction Settlement Prices and Results",
                           report_url=CARB_PAGE, document_list=CARB_URL, license="internal")


def rggi(run_id, log):
    r = get(RGGI_URL, "RGGI prices and volumes page", log)
    got = ip.utc_iso(pd.Timestamp.now(tz="UTC"))
    tables = pd.read_html(io.StringIO(r.text))
    want = ["Auction", "Date", "Quantity Offered", "CCR Sold", "Quantity Sold", "Clearing Price", "Total Proceeds"]
    d = [t for t in tables if list(t.columns) == want]
    if len(d) != 1:
        raise RuntimeError(f"RGGI page: expected one table with columns {want}; layout changed")
    d = d[0].astype(str)
    m = d["Auction"].str.extract(r"^Auction (\d+)( \(Future\))?$")
    if m[0].isna().any():
        raise RuntimeError(f"RGGI page: unparsed auction names {d['Auction'][m[0].isna()].tolist()[:5]}")
    if not d["Date"].str.fullmatch(r"\d{4}-\d{2}-\d{2}").all():
        raise RuntimeError("RGGI page: a date is not YYYY-MM-DD")
    out = []
    cols = [("Clearing Price", "clearing_price", "USD/short_ton"), ("Quantity Offered", "allowances_offered", "count"),
            ("Quantity Sold", "allowances_sold", "count"), ("CCR Sold", "ccr_allowances_sold", "count")]
    for i, row in d.iterrows():
        ent = "rggi:future_auction" if pd.notna(m.at[i, 1]) else "rggi:current_auction"
        for col, var, unit in cols:
            v = row[col].strip().replace("$", "").replace(",", "")
            if v in ("--", "", "nan"):
                continue
            try:
                val = float(v)
            except ValueError:
                raise RuntimeError(f"RGGI {row['Auction']} {col}: not a number: {row[col]!r}")
            out.append(dict(entity=ent, variable=var, ts_utc=row["Date"] + "T00:00:00Z", value=val,
                            unit=unit, node=row["Auction"], retrieved_at=got))
    s = pd.DataFrame(out).assign(freq="P3M", geo="US", market="", source="rggi:prices-volumes",
                                 source_url=RGGI_URL, vintage="")
    log(f"  RGGI: {len(d)} auctions, {d['Date'].min()} to {d['Date'].max()}")
    header = [
        "Energy Research Warehouse (ERW): RGGI CO2 allowance auction results",
        "Shape: series (docs/datastandard.md v0). freq P3M: ts_utc is the auction date at 00:00:00Z. "
        "node names the auction as RGGI does. '--' cells are omitted.",
        f"Retrieved: {run_id} (UTC) by warehouse/connectors/carbon_auctions.py",
        f"Run log: warehouse/output/logs/carbon_auctions_{run_id}.log",
        f"Raw files: warehouse/raw/carbon_auctions/{run_id}/ (not in git)",
        f"Source: Regional Greenhouse Gas Initiative (RGGI, Inc.), Allowance Prices and Volumes, {RGGI_URL}",
        "Prices in USD per short ton of CO2; allowances in allowances (1 allowance = 1 short ton).",
        "License: internal. The page says only '(c) RGGI'; terms unconfirmed.",
    ]
    return s, header, dict(source="rggi:prices-volumes", publisher="Regional Greenhouse Gas Initiative (RGGI, Inc.)",
                           report="Allowance Prices and Volumes", report_url=RGGI_URL,
                           document_list=RGGI_PAGE, license="internal")


TABLES = {"carb": ("carb_auction_allowance_prices", carb), "rggi": ("rggi_auction_allowance_prices", rggi)}


def main(argv=None):
    ap = argparse.ArgumentParser(description="ERW carbon allowance auctions")
    ap.add_argument("--table", action="append", choices=sorted(TABLES))
    args = ap.parse_args(argv)
    os.makedirs(ip.LOG_DIR, exist_ok=True)
    run_id = dt.datetime.now(dt.timezone.utc).strftime("%Y%m%dT%H%M%SZ")
    log = ip.Log(os.path.join(ip.LOG_DIR, f"carbon_auctions_{run_id}.log"))
    ip.RAW.open("carbon_auctions", run_id)
    results = []
    for key in args.table or sorted(TABLES):
        name, fn = TABLES[key]
        try:
            s, header, reg = fn(run_id, log)
            newest = pd.Timestamp(s["ts_utc"].max()[:10])
            age = (pd.Timestamp.now(tz="UTC").tz_localize(None).normalize() - newest).days
            if age > STALE_DAYS:
                raise RuntimeError(f"{name}: newest auction {newest.date()} is {age} days old; not writing")
            ip.write_csv(s[ip.SERIES_COLS].sort_values(["entity", "variable", "ts_utc"]), name, header, log)
            ip.update_sources([dict(reg, tables=[name])])
            results.append(dict(table=name, market=key, status="ok", detail=""))
        except Exception:
            tb = ip.redact(traceback.format_exc())
            last = tb.strip().splitlines()[-1]
            log(f"{name} FAILED, no output file written:\n{tb}")
            print(f"carbon_auctions {name} FAILED, no output file written: {last}", file=sys.stderr)
            results.append(dict(table=name, market=key, status="failed", detail=last[:300]))
    ip.write_status("carbon_auctions", run_id, results)
    failures = sum(r["status"] != "ok" for r in results)
    log(f"done, failures={failures}")
    log.close()
    print(f"carbon_auctions run log: {os.path.relpath(log.path, ip.ROOT)}")
    return 1 if failures else 0


if __name__ == "__main__":
    sys.exit(main())

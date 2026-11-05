#!/usr/bin/env python3
"""Berkeley Lab's power purchase agreement prices, one row a PPA: each wind and utility-scale solar PPA's execution date,
contract capacity, term, region and levelized price, as Lawrence Berkeley National Laboratory's report data files give
them (session 915, chain 051: the price a buyer signs for, which the ERW held nowhere).

Energy Research Warehouse (ERW) connector. One events table, warehouse/output/lbnl_ppa_prices.csv, from two LBNL data
files, each linked from its publication page on LBNL's publications server:

    Land-Based Wind Energy Technology Data Update, 2026 Edition: sheet "Wind PPAs by Plant"
        https://eta-publications.lbl.gov/publications/land-based-wind-energy-technology-0
    Utility-Scale Solar, 2025 Data Update: sheet "PPA Price by Project (PV only)"
        https://eta-publications.lbl.gov/publications/us-utility-scale-solar-2025-data

    event_id     lbnl_ppa:<wind|solar>:<12 hex of the row's date, MW, term, region and price>, with -2, -3 for a second
                 identical row (LBNL names no project)
    event_date   the PPA's execution date; event_type ppa; mw the contract capacity (MW); price the PPA price levelized
                 over its term (USD/MWh in real dollars of x_dollar_year: 2025 for wind, 2024 for solar); currency USD
    x_*          the technology, term (years), region (CAISO, West (non-ISO), MISO, SPP, ERCOT, PJM, NYISO, ISO-NE,
                 Southeast (non-ISO), Hawaii) and LBNL's consolidated region, the price's unit and dollar year

LBNL levelizes each contract's price over its full term after escalation and time-of-delivery factors, in real dollars
(4 percent real discount rate). Solar PPAs here are PV only, without PV+battery. The solar file's sheet note names 2023
dollars, but its averages and the report name 2024 dollars, which the table takes; the header says so. A heading not as
read, a row with no region or two, or a price not a number stops the run. Nothing is filled.

    python warehouse/connectors/lbnl_ppa_prices.py [--offline]

Ceiling: four requests (the two pages and the two workbooks; saved in warehouse/raw/lbnl_ppa_prices/ and reused
offline). eta-publications.lbl.gov's robots file allows these paths (session 253; read again by session 915). License:
CC BY 4.0, as each file's own copyright notice states ("This work is openly licensed via CC BY 4.0"); cite Berkeley Lab.
"""

import argparse
import datetime as dt
import hashlib
import io
import os
import re
import sys
import traceback

import pandas as pd

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import iso_prices as ip  # noqa: E402

NAME = "lbnl_ppa_prices"
CONNECTOR = "lbnl_ppa_prices"
SOURCE = "lbnl:ppa_prices"
HOST = "https://eta-publications.lbl.gov"
UA = {"User-Agent": "Mozilla/5.0 (compatible; ERW-connector/0.1; +https://github.com/SamuelEnrique/erw)"}
FILES = {
    "wind": (HOST + "/publications/land-based-wind-energy-technology-0", "Wind PPAs by Plant", "2025",
             "Land-Based Wind Energy Technology Data Update"),
    "solar": (HOST + "/publications/us-utility-scale-solar-2025-data", "PPA Price by Project (PV only)", "2024",
              "Utility-Scale Solar Data Update"),
}
REGIONS = ["CAISO", "West (non-ISO)", "MISO", "SPP", "ERCOT", "PJM", "NYISO", "ISO-NE", "Southeast (non-ISO)", "Hawaii"]
EVENT_COLS = ["event_id", "event_date", "event_type", "parties", "entity_ids", "mw", "price", "currency", "status",
              "source", "source_url", "retrieved_at"]
X_COLS = ["x_technology", "x_term_years", "x_region", "x_macro_region", "x_price_unit", "x_dollar_year"]


def text(v):
    return "" if v is None or (isinstance(v, float) and pd.isna(v)) else re.sub(r"\s+", " ", str(v)).strip()


def num(v):
    x = pd.to_numeric(v, errors="coerce")
    return None if pd.isna(x) else float(x)


def workbook_url(page_html):
    found = sorted(set(re.findall(r'href="(/sites/default/files/[^"]+\.xlsx)"', page_html)))
    if len(found) != 1:
        raise RuntimeError(f"the page links {len(found)} data files on its own host, not one: {found}")
    return HOST + found[0]


def head_row(frame):
    for i in range(min(60, len(frame))):
        if text(frame.iloc[i, 0]) == "PPA Execution Date":
            return i
    raise RuntimeError("no 'PPA Execution Date' heading in the sheet's first 60 rows")


def wind_rows(frame):
    h = head_row(frame)
    want = ["PPA Execution Date", "Capacity (MW)", "Term (years)", "Region", "Macro Region"]
    head = [text(v) for v in frame.iloc[h]]
    if head[:5] != want or not re.fullmatch(r"Real 2025\$/MWh", head[5]):
        raise RuntimeError(f"the wind sheet's headings are not as read: {head[:6]}")
    out = []
    for _, r in frame.iloc[h + 1:].iterrows():
        d = pd.to_datetime(r.iloc[0], errors="coerce")
        if pd.isna(d):
            continue
        region, macro, price = text(r.iloc[3]), text(r.iloc[4]), num(r.iloc[5])
        if region not in REGIONS or price is None:
            raise RuntimeError(f"a wind row not as read: {[text(v) for v in r.iloc[:6]]}")
        out.append(("wind", d, num(r.iloc[1]), num(r.iloc[2]), region, macro, price))
    return out


def solar_rows(frame):
    h = head_row(frame)
    head = [text(v) for v in frame.iloc[h]]
    if head[:3] != ["PPA Execution Date", "Capacity (MW)", "Term (years)"] or head[3:13] != REGIONS:
        raise RuntimeError(f"the solar sheet's headings are not as read: {head[:13]}")
    macros = {c: head[c] for c in range(14, 19)}
    if list(macros.values()) != ["Hawaii", "West", "Central", "Northeast", "Southeast"]:
        raise RuntimeError(f"the solar sheet's consolidated regions are not as read: {list(macros.values())}")
    out = []
    for _, r in frame.iloc[h + 1:].iterrows():
        d = pd.to_datetime(r.iloc[0], errors="coerce")
        if pd.isna(d):
            continue
        hits = [(REGIONS[c - 3], num(r.iloc[c])) for c in range(3, 13) if num(r.iloc[c]) is not None]
        mac = [macros[c] for c in macros if num(r.iloc[c]) is not None]
        if len(hits) != 1 or len(mac) != 1:
            raise RuntimeError(f"a solar row with {len(hits)} regions and {len(mac)} consolidated regions: {[text(v) for v in r.iloc[:19]]}")
        out.append(("solar", d, num(r.iloc[1]), num(r.iloc[2]), hits[0][0], mac[0], hits[0][1]))
    return out


def events(rows, urls, retrieved, years):
    out, seen = [], {}
    for tech, d, mw, term, region, macro, price in rows:
        key = f"{tech}|{d:%Y-%m-%d}|{mw}|{term}|{region}|{price:.6f}"
        h = hashlib.sha1(key.encode()).hexdigest()[:12]
        seen[h] = seen.get(h, 0) + 1
        eid = f"lbnl_ppa:{tech}:{h}" + (f"-{seen[h]}" if seen[h] > 1 else "")
        out.append(dict(event_id=eid, event_date=f"{d:%Y-%m-%d}", event_type="ppa", parties="", entity_ids="",
                        mw="" if mw is None else mw, price=round(price, 4), currency="USD", status="", source=SOURCE,
                        source_url=urls[tech], retrieved_at=retrieved[tech], x_technology=tech,
                        x_term_years="" if term is None else int(term) if float(term).is_integer() else term,
                        x_region=region, x_macro_region=macro, x_price_unit=f"USD/MWh, levelized, real {years[tech]} dollars",
                        x_dollar_year=years[tech]))
    t = pd.DataFrame(out)
    if t.event_id.duplicated().any():
        raise RuntimeError("an event_id given twice")
    return t.sort_values(["x_technology", "event_date", "event_id"]).reset_index(drop=True)


def main(argv=None):
    ap = argparse.ArgumentParser(description="Berkeley Lab's wind and solar PPA prices, one row a PPA")
    ap.add_argument("--offline", action="store_true", help="the saved pages and workbooks only, no request")
    ap.add_argument("--out-dir", help="a trial: the table under this folder, not warehouse/output")
    args = ap.parse_args(argv)
    if args.out_dir:
        raw_dir = ip.RAW_DIR
        ip.set_out_dir(args.out_dir)
        ip.RAW_DIR = raw_dir
    os.makedirs(ip.LOG_DIR, exist_ok=True)
    run_id = dt.datetime.now(dt.timezone.utc).strftime("%Y%m%dT%H%M%SZ")
    log = ip.Log(os.path.join(ip.LOG_DIR, f"{CONNECTOR}_{run_id}.log"))
    ip.RAW.open(CONNECTOR, run_id)
    results = []
    try:
        rows, urls, retrieved, years, got = [], {}, {}, {}, []
        for tech, (page, sheet, year, report) in FILES.items():
            html, _ = ip.fetch_raw(CONNECTOR, page, log, offline=args.offline, headers=UA)
            url = workbook_url(html.decode("utf-8", errors="replace"))
            content, rec = ip.fetch_raw(CONNECTOR, url, log, offline=args.offline, headers=UA, timeout=600)
            if content[:2] != b"PK":
                raise RuntimeError(f"{url} is not a workbook")
            frame = pd.read_excel(io.BytesIO(content), sheet_name=sheet, header=None)
            got_rows = wind_rows(frame) if tech == "wind" else solar_rows(frame)
            log(f"{tech}: {len(got_rows):,} PPAs from {url}")
            rows += got_rows
            urls[tech], retrieved[tech], years[tech] = url, rec.get("retrieved_at") or "", year
            got.append(f"{report}, sheet '{sheet}': {url} (retrieved {retrieved[tech]})")
        t = events(rows, urls, retrieved, years)
        n = t.x_technology.value_counts().to_dict()
        span = {k: f"{g.event_date.min()[:4]} to {g.event_date.max()[:4]}" for k, g in t.groupby("x_technology")}
        header = [
            "Energy Research Warehouse (ERW): Berkeley Lab, wind and utility-scale solar PPA prices, one row a power purchase agreement (session 915)",
            "Shape: events (docs/datastandard.md v0). event_id lbnl_ppa:<wind|solar>:<12 hex of the row's fields> (LBNL names no project); event_date the PPA's "
            "execution date; event_type ppa; mw the contract capacity; price the PPA's price levelized over its term (after escalation and time-of-delivery "
            "factors, 4 percent real discount rate) in USD/MWh of real dollars of x_dollar_year (wind 2025, solar 2024); x_region the region, "
            "x_macro_region LBNL's consolidated region (wind: West, Central, East; solar: Hawaii, West, Central, Northeast, Southeast).",
            f"Wind {n.get('wind', 0):,} PPAs ({span.get('wind', '')}), solar PV {n.get('solar', 0):,} ({span.get('solar', '')}; PV only, no PV+battery). "
            "The solar sheet's note names 2023 dollars; its averages and the report name 2024 dollars, which are taken. Values as LBNL gives them; nothing is filled.",
            f"Retrieved: {run_id} (UTC) by warehouse/connectors/lbnl_ppa_prices.py",
            f"Run log: warehouse/output/logs/{CONNECTOR}_{run_id}.log",
            f"Raw files: warehouse/raw/{CONNECTOR}/ (not in git)",
            f"Source: {SOURCE} Lawrence Berkeley National Laboratory, Land-Based Wind Energy Technology Data Update (2026 Edition) and Utility-Scale Solar "
            f"(2025 Data Update), {FILES['wind'][0]} and {FILES['solar'][0]}",
            "  access: " + "; ".join(got),
            "License: CC BY 4.0, as each data file's copyright notice states (Copyright The Regents of the University of California, through Lawrence "
            "Berkeley National Laboratory); cite Berkeley Lab and the report.",
        ]
        ip.write_snapshot(t, NAME, header, log, cols=EVENT_COLS + X_COLS)
        if not args.out_dir:
            ip.update_sources([dict(source=SOURCE, publisher="Lawrence Berkeley National Laboratory (Berkeley Lab)",
                                    report="Land-Based Wind Energy Technology Data Update; Utility-Scale Solar Data Update (PPA prices)",
                                    report_url=FILES["wind"][0], document_list=FILES["solar"][0], license="public", tables=[NAME])])
        results.append(dict(table=NAME, market="all", status="ok", detail=f"{len(t):,} PPAs"))
        print(f"{NAME}: {len(t):,} PPAs ({n})")
    except Exception:
        tb = ip.redact(traceback.format_exc())
        log(f"FAILED, no output file written:\n{tb}")
        print(f"{CONNECTOR} FAILED, no output file written: {tb.strip().splitlines()[-1]}", file=sys.stderr)
        results.append(dict(table=NAME, market="all", status="failed", detail=tb.strip().splitlines()[-1][:300]))
    if not args.out_dir:
        ip.write_status(CONNECTOR, run_id, results)
    log.close()
    return 0 if all(r["status"] == "ok" for r in results) else 1


if __name__ == "__main__":
    sys.exit(main())

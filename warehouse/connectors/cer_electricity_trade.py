#!/usr/bin/env python3
"""The Canada Energy Regulator's electricity trade: Canada's exports to and imports from the U.S. each month, and each
province's exports to each U.S. state each year (session 887, chain 048: Canada's own record of the flow that EIA's
international statistics give as one number a year).

Energy Research Warehouse (ERW) connector. One series table, warehouse/output/cer_electricity_trade.csv, from the CER's
Electricity Trade Summary workbook (compiled from its monthly Commodity Statistics reports), linked from

    https://www.cer-rec.gc.ca/en/data-analysis/energy-commodities/electricity/statistics/electricity-trade-summary/

    entity    cer_trade:CA (Canada with the U.S., monthly) or cer_trade:<province>:<U.S. state> (a province's exports to a
              state, a year), the province as ISO 3166-2's code (CA-QC becomes QC) and the state as its postal code; where
              the CER names a market or two states, as the exporter reports them, MN_ND (Minnesota and North Dakota),
              ISONE (ISO New England) or PJM
    variable  exports, imports (MWh; a province's rows hold exports only, as the CER's figure gives them)
    ts_utc    the month's or the year's first day; freq P1M or P1Y; geo CA, or CA-<province>; node in words

Only complete years of the province rows are taken: the workbook's current year (2026 to July) is a part of a year and is
left out of them, named in the header; the monthly rows hold it. The workbook's values and average prices are in Canadian
dollars, a unit the data standard does not have, and are not taken. A province or state name not in the map stops the run;
so does a key given twice. The CER notes that the latest figures, with revisions, are in its Commodity Tracking System;
this table holds the workbook as published.

    python warehouse/connectors/cer_electricity_trade.py [--offline]

Ceiling: two requests (the page and the workbook; both saved in warehouse/raw/cer_electricity_trade/ and reused offline).
The CER's robots file allows these paths (disallowing /fracfocus and /bin). License: the CER's terms allow reproduction
for non-commercial purposes with the title, the author and a statement that it is a copy not produced with the CER's
endorsement; commercial redistribution needs the CER's written permission (license_reads.csv, session 887).
"""

import argparse
import datetime as dt
import io
import os
import re
import sys
import traceback

import pandas as pd

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import iso_prices as ip  # noqa: E402

NAME = "cer_electricity_trade"
CONNECTOR = "cer_electricity_trade"
SOURCE = "cer:electricity_trade_summary"
PAGE = "https://www.cer-rec.gc.ca/en/data-analysis/energy-commodities/electricity/statistics/electricity-trade-summary/"
UA = {"User-Agent": "Mozilla/5.0 (compatible; ERW-connector/0.1; +https://github.com/SamuelEnrique/erw)"}
PROVINCES = {"Alberta": "AB", "British Columbia": "BC", "Manitoba": "MB", "New Brunswick": "NB", "Newfoundland and Labrador": "NL",
             "Nova Scotia": "NS", "Ontario": "ON", "Prince Edward Island": "PE", "Quebec": "QC", "Québec": "QC", "Saskatchewan": "SK",
             "Yukon": "YT", "Northwest Territories": "NT", "Nunavut": "NU"}
STATES = {"Alabama": "AL", "Alaska": "AK", "Arizona": "AZ", "Arkansas": "AR", "California": "CA", "Colorado": "CO",
          "Connecticut": "CT", "Delaware": "DE", "District of Columbia": "DC", "Florida": "FL", "Georgia": "GA", "Hawaii": "HI",
          "Idaho": "ID", "Illinois": "IL", "Indiana": "IN", "Iowa": "IA", "Kansas": "KS", "Kentucky": "KY", "Louisiana": "LA",
          "Maine": "ME", "Maryland": "MD", "Massachusetts": "MA", "Michigan": "MI", "Minnesota": "MN", "Mississippi": "MS",
          "Missouri": "MO", "Montana": "MT", "Nebraska": "NE", "Nevada": "NV", "New Hampshire": "NH", "New Jersey": "NJ",
          "New Mexico": "NM", "New York": "NY", "North Carolina": "NC", "North Dakota": "ND", "Ohio": "OH", "Oklahoma": "OK",
          "Oregon": "OR", "Pennsylvania": "PA", "Rhode Island": "RI", "South Carolina": "SC", "South Dakota": "SD",
          "Tennessee": "TN", "Texas": "TX", "Utah": "UT", "Vermont": "VT", "Virginia": "VA", "Washington": "WA",
          "West Virginia": "WV", "Wisconsin": "WI", "Wyoming": "WY",
          # the CER names some destinations as a market or two states, as the exporter reports them: kept as named
          "Minn / N. Dakota": "MN_ND", "New England-ISO": "ISONE", "Pennsylvania Jersey Maryland Power Pool": "PJM"}
MONTHLY_SHEET, PROVINCE_SHEET = "Fig. 1(m), Fig. 3(m)", "Fig. 2"


def text(v):
    return "" if v is None or (isinstance(v, float) and pd.isna(v)) else re.sub(r"\s+", " ", str(v)).strip()


def workbook_url(page_html):
    found = sorted(set(re.findall(r'href="([^"]*electricity-trade[^"]*\.xlsx)"', page_html)))
    if len(found) != 1:
        raise RuntimeError(f"the page links {len(found)} trade workbooks, not one: {found}")
    href = found[0]
    return href if href.startswith("http") else "https://www.cer-rec.gc.ca" + href


def monthly_rows(frame, base):
    head = [text(v) for v in frame.iloc[0]]
    cols = {}
    for c, h in enumerate(head):
        if h.startswith("Exports") and h.endswith("(MW.h)"):
            cols["exports"] = c
        elif h.startswith("Imports") and h.endswith("(MW.h)"):
            cols["imports"] = c
    if set(cols) != {"exports", "imports"} or head[0] != "Date":
        raise RuntimeError(f"the monthly sheet's headings are not as read: {head}")
    out = []
    for _, r in frame.iloc[1:].iterrows():
        d = pd.to_datetime(r[0], errors="coerce")
        if pd.isna(d):
            continue
        for var, c in cols.items():
            v = pd.to_numeric(r[c], errors="coerce")
            if pd.isna(v):
                continue
            out.append(dict(base, entity="cer_trade:CA", variable=var, ts_utc=d.strftime("%Y-%m-01T00:00:00Z"), value=float(v),
                            unit="MWh", freq="P1M", geo="CA", node=f"Canada, electricity {var} with the U.S."))
    return out


def province_rows(frame, base, last_full):
    head = [text(v) for v in frame.iloc[0]]
    want = {"Date": None, "Volume (MW.h)": None, "Province (Eng. / Ang.)": None, "Destination (Eng. / Ang.)": None}
    for c, h in enumerate(head):
        if h in want:
            want[h] = c
    if any(v is None for v in want.values()):
        raise RuntimeError(f"the province sheet's headings are not as read: {head}")
    out, partial = [], set()
    for _, r in frame.iloc[1:].iterrows():
        year = text(r[want["Date"]])
        if not re.fullmatch(r"\d{4}", year):
            continue
        if int(year) > last_full:
            partial.add(int(year))
            continue
        prov, dest = text(r[want["Province (Eng. / Ang.)"]]), text(r[want["Destination (Eng. / Ang.)"]])
        if prov not in PROVINCES:
            raise RuntimeError(f"a province not in the map: {prov!r}")
        if dest not in STATES:
            raise RuntimeError(f"a destination not in the map: {dest!r}")
        v = pd.to_numeric(r[want["Volume (MW.h)"]], errors="coerce")
        if pd.isna(v):
            continue
        out.append(dict(base, entity=f"cer_trade:{PROVINCES[prov]}:{STATES[dest]}", variable="exports", ts_utc=f"{year}-01-01T00:00:00Z",
                        value=float(v), unit="MWh", freq="P1Y", geo=f"CA-{PROVINCES[prov]}", node=f"{prov} to {dest}"))
    return out, sorted(partial)


def main(argv=None):
    ap = argparse.ArgumentParser(description="The Canada Energy Regulator's electricity trade with the U.S.")
    ap.add_argument("--offline", action="store_true", help="the saved page and workbook only, no request")
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
        if ip.paused_host("www.cer-rec.gc.ca"):
            raise RuntimeError("the Canada Energy Regulator is paused (paused_sources.csv): not asked")
        page, _ = ip.fetch_raw(CONNECTOR, PAGE, log, offline=args.offline, fresh=not args.offline, headers=UA)
        url = workbook_url(page.decode("utf-8", errors="replace"))
        content, rec = ip.fetch_raw(CONNECTOR, url, log, offline=args.offline, fresh=not args.offline, headers=UA, timeout=300)
        if content[:2] != b"PK":
            raise RuntimeError(f"{url} is not a workbook")
        xl = pd.ExcelFile(io.BytesIO(content))
        base = dict(market="", source=SOURCE, source_url=url, retrieved_at=rec.get("retrieved_at") or "", vintage="")
        monthly = monthly_rows(pd.read_excel(xl, MONTHLY_SHEET, header=None), base)
        last_month = max(r["ts_utc"] for r in monthly)
        last_full = int(last_month[:4]) - (0 if last_month[5:7] == "12" else 1)
        prov, partial = province_rows(pd.read_excel(xl, PROVINCE_SHEET, header=None), base, last_full)
        s = pd.DataFrame(monthly + prov)
        if s.duplicated(["entity", "variable", "ts_utc"]).any():
            raise RuntimeError(f"a key given twice: {s.loc[s.duplicated(['entity', 'variable', 'ts_utc']), 'entity'].head(3).tolist()}")
        s = s[ip.SERIES_COLS].sort_values(["entity", "variable", "ts_utc"]).reset_index(drop=True)
        header = [
            "Energy Research Warehouse (ERW): the Canada Energy Regulator, Canada's electricity trade with the U.S., a month, and each province's exports to each state, a year (session 887)",
            "Shape: series (docs/datastandard.md v0). entity cer_trade:CA (Canada with the U.S., freq P1M, variables exports and imports) or cer_trade:<province>:<U.S. state> "
            "(a province's exports to a state, freq P1Y, variable exports); unit MWh; ts_utc the month's or year's first day; geo CA or CA-<province>.",
            f"Months {s[s.freq == 'P1M'].ts_utc.min()[:7]} to {last_month[:7]}; province rows to {last_full}"
            + (f" (the workbook's {', '.join(map(str, partial))}, a part of a year, left out of them)" if partial else "")
            + f"; {len(s):,} rows. The workbook's values and prices in Canadian dollars are not taken (no such unit in the data standard). Nothing is filled.",
            f"Retrieved: {run_id} (UTC) by warehouse/connectors/cer_electricity_trade.py (the workbook retrieved {rec.get('retrieved_at', '')})",
            f"Run log: warehouse/output/logs/{CONNECTOR}_{run_id}.log",
            f"Raw files: warehouse/raw/{CONNECTOR}/ (not in git)",
            f"Source: {SOURCE} Canada Energy Regulator, Electricity Trade Summary (compiled from the CER's monthly Commodity Statistics), {PAGE}",
            f"  access: {url}",
            "License: the CER's terms allow non-commercial reproduction with the title and author, stating that it is a copy not produced in affiliation "
            "with or with the endorsement of the CER; commercial redistribution needs the CER's written permission. This table is a copy of the version "
            "available at the CER website and has not been produced in affiliation with, or with the endorsement of, the CER.",
        ]
        ip.write_snapshot(s, NAME, header, log, ip.SERIES_COLS)
        if not args.out_dir:
            ip.update_sources([dict(source=SOURCE, publisher="Canada Energy Regulator (CER)", report="Electricity Trade Summary",
                                    report_url=PAGE, document_list=PAGE, license="public", tables=[NAME])])
        results.append(dict(table=NAME, market="all", status="ok", detail=f"{len(s):,} rows"))
        print(f"{NAME}: {len(s):,} rows, months to {last_month[:7]}, province rows to {last_full}")
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

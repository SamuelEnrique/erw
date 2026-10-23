#!/usr/bin/env python3
"""EIA's Annual Coal Distribution Report: U.S. domestic coal shipped from each coal-origin state (or region of one) to
each destination state, by consuming sector and transportation mode, a quarter (session 957, chain 054: where the coal
the ERW's plants burn comes from, beside eia_coal_production_annual and eia_coal_receipts_annual).

Energy Research Warehouse (ERW) connector. One series table, warehouse/output/eia_coal_distribution_quarterly.csv, from
the report's "Domestic distribution by origin state" workbook (o_<yy>state.xlsx), the latest year the page links:

    https://www.eia.gov/coal/distribution/annual/

    entity     eia_coal_flow:<origin>:<destination>:<consumer type>:<mode>, each a slug of EIA's words; the origin is EIA's
               coal-origin state or region (Kentucky (East), West Virginia (Southern), Pennsylvania (Anthracite) ...);
               "U.S. (All States)" is EIA's total level: a sum takes one level
    variable   shipments; unit short_ton; ts_utc the quarter's first day; freq P3M; geo US-<destination state>, US for the
               U.S. rows
    x_*        the origin, destination, consumer type and mode as EIA writes them

The destination workbook (d_<yy>state.xlsx) holds the same rows in another order; it is read and must agree row for row,
or the run stops. A heading not as read or a key given twice stops the run; nothing is filled.

    python warehouse/connectors/eia_coal_distribution.py [--offline]

Ceiling: three requests (the page and the two workbooks, saved in warehouse/raw/eia_coal_distribution/ and reused
offline). EIA's robots file allows /coal/distribution/. License: public (EIA, record 1 of license_reads.csv).
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

NAME = "eia_coal_distribution_quarterly"
CONNECTOR = "eia_coal_distribution"
SOURCE = "eia:coal_distribution"
PAGE = "https://www.eia.gov/coal/distribution/annual/"
UA = {"User-Agent": "Mozilla/5.0 (compatible; ERW-connector/0.1; +https://github.com/SamuelEnrique/erw)"}
VOL = "Coal Volume (short tons)"
O_HEAD = ["Year", "Quarter", "Origin State", "Destination State", "Consumer Type", "Transportation Mode", VOL]
D_HEAD = ["Year", "Quarter", "Destination State", "Origin State", "Consumer Type", "Transportation Mode", VOL]
KEY = ["Year", "Quarter", "Origin State", "Destination State", "Consumer Type", "Transportation Mode"]
STATES = {"Alabama": "AL", "Alaska": "AK", "Arizona": "AZ", "Arkansas": "AR", "California": "CA", "Colorado": "CO", "Connecticut": "CT",
          "Delaware": "DE", "Florida": "FL", "Georgia": "GA", "Hawaii": "HI", "Idaho": "ID", "Illinois": "IL", "Indiana": "IN", "Iowa": "IA",
          "Kansas": "KS", "Kentucky": "KY", "Louisiana": "LA", "Maine": "ME", "Maryland": "MD", "Massachusetts": "MA", "Michigan": "MI",
          "Minnesota": "MN", "Mississippi": "MS", "Missouri": "MO", "Montana": "MT", "Nebraska": "NE", "Nevada": "NV", "New Hampshire": "NH",
          "New Jersey": "NJ", "New Mexico": "NM", "New York": "NY", "North Carolina": "NC", "North Dakota": "ND", "Ohio": "OH", "Oklahoma": "OK",
          "Oregon": "OR", "Pennsylvania": "PA", "Rhode Island": "RI", "South Carolina": "SC", "South Dakota": "SD", "Tennessee": "TN",
          "Texas": "TX", "Utah": "UT", "Vermont": "VT", "Virginia": "VA", "Washington": "WA", "West Virginia": "WV", "Wisconsin": "WI",
          "Wyoming": "WY", "U.S. (All States)": "US"}
X_COLS = ["x_origin", "x_destination", "x_consumer_type", "x_mode"]


def slug(s):
    return re.sub(r"[^a-z0-9]+", "_", str(s).lower()).strip("_")


def workbooks(page):
    """The two workbooks' addresses as the page links them (the latest year only)."""
    links = sorted(set(re.findall(r'href="(xls/[od]_(\d\d)state\.xlsx)"', page)))
    years = sorted({y for _, y in links})
    if not years:
        raise RuntimeError("the page links no origin or destination workbook")
    y = years[-1]
    o = [l for l, yy in links if yy == y and "/o_" in l]
    d = [l for l, yy in links if yy == y and "/d_" in l]
    if len(o) != 1 or len(d) != 1:
        raise RuntimeError(f"the page's workbooks for 20{y} are not one of each: {links}")
    return PAGE + o[0], PAGE + d[0]


def build(o, d, base):
    if list(o.columns) != O_HEAD or list(d.columns) != D_HEAD:
        raise RuntimeError(f"headings not as read: {list(o.columns)} / {list(d.columns)}")
    if o.duplicated(KEY).any():
        raise RuntimeError("a flow given twice")
    m = o.merge(d, on=KEY, suffixes=("_o", "_d"), how="outer", indicator=True)
    if (m["_merge"] != "both").any() or (m[VOL + "_o"] != m[VOL + "_d"]).any():
        raise RuntimeError("the origin and destination workbooks do not agree row for row")
    rows = []
    for _, r in o.iterrows():
        dest = str(r["Destination State"]).strip()
        if dest not in STATES:
            raise RuntimeError(f"a destination not in the map: {dest!r}")
        q = int(r["Quarter"])
        if q not in (1, 2, 3, 4):
            raise RuntimeError(f"a quarter not 1 to 4: {q}")
        ts = f"{int(r['Year'])}-{3 * q - 2:02d}-01T00:00:00Z"
        rows.append(dict(base, entity=f"eia_coal_flow:{slug(r['Origin State'])}:{slug(dest)}:{slug(r['Consumer Type'])}:{slug(r['Transportation Mode'])}",
                         variable="shipments", ts_utc=ts, value=float(r[VOL]), unit="short_ton", freq="P3M", geo=f"US-{STATES[dest]}" if STATES[dest] != "US" else "US",
                         market="", node=f"{r['Origin State']} to {dest}, {r['Consumer Type']}, {r['Transportation Mode']}",
                         x_origin=r["Origin State"], x_destination=dest, x_consumer_type=r["Consumer Type"], x_mode=r["Transportation Mode"]))
    return pd.DataFrame(rows)


def main(argv=None):
    ap = argparse.ArgumentParser(description="EIA's Annual Coal Distribution Report, domestic flows a quarter")
    ap.add_argument("--offline", action="store_true", help="the saved page and workbooks only, no request")
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
        page, _ = ip.fetch_raw(CONNECTOR, PAGE, log, offline=args.offline, headers=UA, timeout=120)
        o_url, d_url = workbooks(page.decode("utf-8", "replace"))
        oc, rec = ip.fetch_raw(CONNECTOR, o_url, log, offline=args.offline, headers=UA, timeout=300)
        dc, _ = ip.fetch_raw(CONNECTOR, d_url, log, offline=args.offline, headers=UA, timeout=300)
        base = dict(source=SOURCE, source_url=o_url, retrieved_at=rec.get("retrieved_at") or "", vintage=ip.vintage_of(rec))
        t = build(pd.read_excel(io.BytesIO(oc)), pd.read_excel(io.BytesIO(dc)), base)
        cols = ip.SERIES_COLS + X_COLS
        t = t[cols].sort_values(["entity", "ts_utc"]).reset_index(drop=True)
        us = t[t.x_origin == "U.S. (All States)"].value.sum()
        year = t.ts_utc.str[:4].max()
        header = [
            f"Energy Research Warehouse (ERW): EIA, Annual Coal Distribution Report, U.S. domestic coal shipments by origin, destination state, consuming sector and mode, a quarter, {year} (session 957)",
            "Shape: series (docs/datastandard.md v0). entity eia_coal_flow:<origin>:<destination>:<consumer type>:<mode>; variable shipments; unit short_ton; "
            "ts_utc the quarter's first day; freq P3M; geo US-<destination state> (US for EIA's U.S. rows); x_* EIA's words. The origin is EIA's "
            "coal-origin state or region; 'U.S. (All States)' is EIA's total level: a sum takes one level.",
            f"{len(t):,} rows, {t['entity'].nunique():,} flows; {year}'s domestic distribution {us / 1e6:,.1f} million short tons (the U.S. rows). "
            "The destination workbook agrees row for row. Nothing is filled.",
            f"Retrieved: {run_id} (UTC) by warehouse/connectors/eia_coal_distribution.py; the workbooks retrieved {base['retrieved_at']}, last modified {base['vintage']}",
            f"Run log: warehouse/output/logs/{CONNECTOR}_{run_id}.log",
            f"Raw files: warehouse/raw/{CONNECTOR}/ (not in git)",
            f"Source: {SOURCE} U.S. Energy Information Administration, Annual Coal Distribution Report (domestic distribution by origin and by destination state), {PAGE}",
            f"  access: {o_url}; {d_url}",
            'License: public (a work of the U.S. government; cite "U.S. Energy Information Administration, Annual Coal Distribution Report").',
        ]
        ip.write_snapshot(t, NAME, header, log, cols)
        if not args.out_dir:
            ip.update_sources([dict(source=SOURCE, publisher="U.S. Energy Information Administration (EIA)",
                                    report="Annual Coal Distribution Report (domestic distribution by origin and destination state)",
                                    report_url=PAGE, document_list=PAGE, license="public", tables=[NAME])])
        results.append(dict(table=NAME, market="all", status="ok", detail=f"{len(t):,} rows"))
        print(f"{NAME}: {len(t):,} rows; {year} domestic {us / 1e6:,.1f} million short tons")
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

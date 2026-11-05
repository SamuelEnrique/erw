#!/usr/bin/env python3
"""EIA-923 Schedule 2: each plant's fuel receipts and their cost, delivery by delivery, a month (session 900, chain 049).

Energy Research Warehouse (ERW) connector. One events table, warehouse/output/eia923_fuel_receipts.csv, from the U.S.
Energy Information Administration's Form EIA-923 yearly zip (the workbook EIA923_Schedules_2_3_4_5_M_<month>_<year>_<date>
.xlsx, sheet "Page 5 Fuel Receipts and Costs"), saved by eia923_monthly.py in warehouse/raw/eia923_monthly/:

    event_id    eia923r:<plant id>:<year>-<month>:<the first 12 characters of the SHA-1 of the row's fields as read (runs
                of spaces made one, a whole number without its decimal), YEAR included, joined with "|">; a delivery has no
                id of EIA's
    event_date  the receipt month's first day; event_type fuel_receipt; parties the supplier as EIA names it
    x_*         EIA's columns, headings as names: the plant, its state, operator and balancing authority, the purchase type
                (C contract, S spot, ...), the contract's expiry, the energy source and fuel group, the coal mine (type, state,
                county, MSHA id, name), x_quantity in x_quantity_unit (short_ton for coal and petroleum coke, bbl for
                petroleum, Mcf for gas, as EIA's layout states tons, barrels or Mcf), heat content (MMBtu per unit), sulfur,
                ash and moisture (percent by weight), mercury and chlorine (ppm), x_fuel_cost (cents per MMBtu, EIA's
                FUEL_COST: all costs of purchase and delivery to the plant), regulated or not, the transport modes, the gas
                contract types, the reporting frequency

A row with no fuel group (EIA's footnotes) is read past. A row repeated with every field the same is kept once and counted
(chain 030's rule; EIA gives no delivery id, so two such rows may be two deliveries). A heading or fuel group not in the
form read stops the run.

    python warehouse/connectors/eia923_receipts.py --years 2025 [--offline]

Ceiling: one request a year (the zip; reused from warehouse/raw/eia923_monthly/ when eia923_monthly.py saved it), asked
for at xls/f923_<year>.zip outside /archive/ (EIA's robots file disallows /archive/). License: public (EIA, record 1 of
license_reads.csv; cite "U.S. Energy Information Administration, Form EIA-923").
"""

import argparse
import datetime as dt
import hashlib
import io
import os
import re
import sys
import traceback
import zipfile

import pandas as pd

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import iso_prices as ip  # noqa: E402
from eia923_monthly import CONNECTOR, PAGE, UA, text, zip_url  # noqa: E402  the same zips, saved under its name

NAME = "eia923_fuel_receipts"
SOURCE = "eia:eia923:fuel_receipts"
SHEET = "Page 5 Fuel Receipts and Costs"
UNITS = {"Coal": "short_ton", "Petroleum Coke": "short_ton", "Petroleum": "bbl", "Natural Gas": "Mcf", "Other Gas": "Mcf"}
EVENT_COLS = ["event_id", "event_date", "event_type", "parties", "entity_ids", "mw", "price", "currency", "status", "source",
              "source_url", "retrieved_at"]


def slug(v):
    return re.sub(r"[^a-z0-9]+", "_", v.lower()).strip("_")


def sheet_rows(frame, year, url, retrieved, counts):
    heads = [r for r in range(min(10, len(frame))) if text(frame.iloc[r, 0]) == "YEAR"]
    if not heads:
        raise RuntimeError(f"{year}: no heading row names 'YEAR'")
    hr = heads[0]
    names = ["x_" + slug(text(v)) for v in frame.iloc[hr]]
    need = {"x_year", "x_month", "x_plant_id", "x_fuel_group", "x_supplier", "x_quantity", "x_fuel_cost"}
    if not need <= set(names) or len(set(names)) != len(names):
        raise RuntimeError(f"{year}: the headings are not as read: {names}")
    d = frame.iloc[hr + 1:].copy()
    d.columns = names
    d = d.map(text)
    d = d[d["x_fuel_group"] != ""]
    d = d[pd.to_numeric(d["x_year"], errors="coerce").eq(year)]
    bad = sorted(set(d["x_fuel_group"]) - set(UNITS))
    if bad:
        raise RuntimeError(f"{year}: a fuel group not in the map: {bad}")
    n = len(d)
    d = d.drop_duplicates()
    counts["repeated"] = counts.get("repeated", 0) + n - len(d)
    out = []
    for _, r in d.iterrows():
        h = hashlib.sha1("|".join(r[c] for c in names).encode("utf-8")).hexdigest()[:12]
        month = int(r["x_month"])
        out.append(dict(event_id=f"eia923r:{r['x_plant_id']}:{year}-{month:02d}:{h}", event_date=f"{year}-{month:02d}-01",
                        event_type="fuel_receipt", parties=r["x_supplier"], entity_ids="", mw="", price="", currency="", status="",
                        source=SOURCE, source_url=url, retrieved_at=retrieved, x_quantity_unit=UNITS[r["x_fuel_group"]],
                        **{c: r[c] for c in names if c not in ("x_year",)}))
    t = pd.DataFrame(out)
    if t["event_id"].duplicated().any():
        raise RuntimeError(f"{year}: two different rows with one id")
    return t


def main(argv=None):
    ap = argparse.ArgumentParser(description="EIA-923 Schedule 2: fuel receipts and costs by plant, a month")
    ap.add_argument("--years", type=int, nargs="+", required=True)
    ap.add_argument("--offline", action="store_true", help="the saved zips only, no request")
    ap.add_argument("--out-dir", help="a trial: the table under this folder, not warehouse/output")
    args = ap.parse_args(argv)
    if args.out_dir:
        raw_dir = ip.RAW_DIR
        ip.set_out_dir(args.out_dir)
        ip.RAW_DIR = raw_dir
    os.makedirs(ip.LOG_DIR, exist_ok=True)
    run_id = dt.datetime.now(dt.timezone.utc).strftime("%Y%m%dT%H%M%SZ")
    log = ip.Log(os.path.join(ip.LOG_DIR, f"eia923_receipts_{run_id}.log"))
    ip.RAW.open(CONNECTOR, run_id)
    results = []
    try:
        frames, got, books, counts = [], [], [], {}
        for y in sorted(args.years):
            url = zip_url(y)
            content, rec = ip.fetch_raw(CONNECTOR, url, log, offline=args.offline, headers=UA, timeout=900)
            zf = zipfile.ZipFile(io.BytesIO(content))
            name = next((n for n in zf.namelist() if n.startswith("EIA923_Schedules_2_3_4_5")), None)
            if not name:
                raise RuntimeError(f"f923_{y}.zip holds no schedules workbook")
            books.append(name)
            t = sheet_rows(pd.read_excel(io.BytesIO(zf.read(name)), SHEET, header=None), y, url, rec.get("retrieved_at") or "", counts)
            log(f"{y}: {len(t):,} receipts")
            frames.append(t)
            got.append(f"{url} (retrieved {rec.get('retrieved_at', '')})")
        t = pd.concat(frames, ignore_index=True).fillna("")
        x = [c for c in t.columns if c not in EVENT_COLS]
        cols = EVENT_COLS + x
        t = t[cols].sort_values(["event_date", "event_id"]).reset_index(drop=True)
        header = [
            "Energy Research Warehouse (ERW): EIA-923 Schedule 2, each plant's fuel receipts and their cost, delivery by delivery, a month (session 900)",
            "Shape: events (docs/datastandard.md v0). event_id eia923r:<plant>:<year-month>:<SHA-1 of the row, 12 characters>; event_date the month's first day; "
            "event_type fuel_receipt; parties the supplier; x_* EIA's columns, headings as names: x_quantity in x_quantity_unit (short_ton, bbl or Mcf), "
            "x_average_heat_content MMBtu per unit, sulfur, ash and moisture percent by weight, mercury and chlorine ppm, x_fuel_cost cents per MMBtu.",
            f"Months {t['event_date'].min()[:7]} to {t['event_date'].max()[:7]} ({', '.join(books)}); {len(t):,} receipts, {t['x_plant_id'].nunique():,} plants. "
            f"Rows repeated with every field the same, kept once: {counts.get('repeated', 0)} (EIA gives no delivery id, so they may be separate deliveries). "
            "Nothing is filled.",
            f"Retrieved: {run_id} (UTC) by warehouse/connectors/eia923_receipts.py",
            f"Run log: warehouse/output/logs/eia923_receipts_{run_id}.log",
            f"Raw files: warehouse/raw/{CONNECTOR}/ (not in git)",
            f"Source: {SOURCE} U.S. Energy Information Administration, Form EIA-923, Schedule 2 (page 5, fuel receipts and costs), {PAGE}",
            f"  access: {'; '.join(got)}",
            'License: public (a work of the U.S. government; cite "U.S. Energy Information Administration, Form EIA-923").',
        ]
        ip.write_snapshot(t, NAME, header, log, cols=cols)
        if not args.out_dir:
            ip.update_sources([dict(source=SOURCE, publisher="U.S. Energy Information Administration (EIA)",
                                    report="Form EIA-923, Schedule 2, fuel receipts and costs", report_url=PAGE, document_list=PAGE,
                                    license="public", tables=[NAME])])
        results.append(dict(table=NAME, market="all", status="ok", detail=f"{len(t):,} receipts"))
        print(f"{NAME}: {len(t):,} receipts")
    except Exception:
        tb = ip.redact(traceback.format_exc())
        log(f"FAILED, no output file written:\n{tb}")
        print(f"eia923_receipts FAILED, no output file written: {tb.strip().splitlines()[-1]}", file=sys.stderr)
        results.append(dict(table=NAME, market="all", status="failed", detail=tb.strip().splitlines()[-1][:300]))
    if not args.out_dir:
        ip.write_status("eia923_receipts", run_id, results)
    log.close()
    return 0 if all(r["status"] == "ok" for r in results) else 1


if __name__ == "__main__":
    sys.exit(main())

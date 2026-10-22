#!/usr/bin/env python3
"""EIA-861: every utility's service territory, county by county, a year (session 667, chain 043).

Energy Research Warehouse (ERW) connector. One entities table, warehouse/output/utility_service_territories.csv, from the
U.S. Energy Information Administration's Form EIA-861 annual files (Service_Territory_<year>.xlsx in f861<year>.zip, sheets
Counties_States and Counties_Territories):

    page   https://www.eia.gov/electricity/data/eia861/
    file   https://www.eia.gov/electricity/data/eia861/zip/f861<year>.zip

    entity_id    eia861:<utility number>:<state>:<county>, one county a utility serves in one state (EIA's row)
    entity_type  utility; name the utility's name as EIA writes it; geo US-<state>
    x_*          EIA's own fields: utility number, state, county, short form (Y when the utility filed EIA's short form),
                 data year, and the sheet the row is in

The table is the code machine's "which utility serves this county" for the All grids tab (chain 043). A utility serves a
county when EIA's sheet lists the pair; EIA gives no share of the county and no boundary, and this table adds none. A row
repeated in EIA's sheet stops the run, as does a year in the sheet other than the year asked.

    python warehouse/connectors/eia861_territories.py --year 2025            # the zip saved by eia861_sales.py is reused
    python warehouse/connectors/eia861_territories.py --year 2025 --offline  # never a request: the saved zip or nothing

Ceiling: two requests (the page and the zip), none when both are saved in warehouse/raw/ (session 667 asked none). EIA's
robots file disallows /archive/ (session 666), so a year EIA has moved to archive/zip/ is refused, not asked. License:
public (EIA: "U.S. government publications are in the public domain", read 12 October 2026, record 1 of
license_reads.csv; cite "U.S. Energy Information Administration, Form EIA-861").
"""

import argparse
import datetime as dt
import io
import os
import sys
import traceback
import zipfile

import pandas as pd

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import iso_prices as ip  # noqa: E402
from eia861_sales import PAGE, UA, zip_url  # noqa: E402  the same page and the same zip as the sales table

NAME = "utility_service_territories"
CONNECTOR = "eia861"   # the raw files of the EIA-861 zips are shared with eia861_sales.py
SOURCE = "eia:eia861_territory"
ENTITY_COLS = ["entity_id", "entity_type", "name", "geo", "lat", "lon", "capacity_mw", "status",
               "status_date", "operator", "source", "source_url", "retrieved_at", "vintage"]
X_COLS = ["x_utility_number", "x_state", "x_county", "x_short_form", "x_data_year", "x_sheet"]
SHEETS = ("Counties_States", "Counties_Territories")
HEADINGS = {"data year": "year", "utility number": "utility", "utility name": "name", "short form": "short",
            "state": "state", "county": "county"}


def territories(frame, year, sheet, url, retrieved):
    """One sheet of Service_Territory_<year>.xlsx (its heading row first) as the table's rows."""
    head = [str(c).strip().lower() for c in frame.iloc[0]]
    cols = {HEADINGS[h]: i for i, h in enumerate(head) if h in HEADINGS}
    missing = [k for k in ("year", "utility", "name", "state", "county") if k not in cols]
    if missing:
        raise RuntimeError(f"{sheet}: the headings lack {missing} (they are {head})")
    d = frame.iloc[1:]
    d = d[d[cols["utility"]].notna()]
    years = set(pd.to_numeric(d[cols["year"]], errors="coerce").dropna().astype(int))
    if years != {year}:
        raise RuntimeError(f"{sheet}: data years {sorted(years)}, not {year}")
    text = lambda r, k: "" if k not in cols or pd.isna(r[cols[k]]) else str(r[cols[k]]).strip()  # noqa: E731
    out = []
    for _, r in d.iterrows():
        util, state, county = int(r[cols["utility"]]), text(r, "state"), text(r, "county")
        if not state or not county:
            raise RuntimeError(f"{sheet}: utility {util} has a row without a state or a county")
        out.append(dict(entity_id=f"eia861:{util}:{state}:{county}", entity_type="utility", name=text(r, "name"),
                        geo=f"US-{state}", lat="", lon="", capacity_mw="", status="", status_date="", operator="",
                        source=SOURCE, source_url=url, retrieved_at=retrieved, vintage=f"EIA-861 {year}",
                        x_utility_number=str(util), x_state=state, x_county=county, x_short_form=text(r, "short"),
                        x_data_year=str(year), x_sheet=sheet))
    return pd.DataFrame(out, columns=ENTITY_COLS + X_COLS)


def main(argv=None):
    ap = argparse.ArgumentParser(description="EIA-861 utility service territories by county")
    ap.add_argument("--year", type=int, required=True, help="the data year")
    ap.add_argument("--offline", action="store_true", help="never a request: the saved page and zip, or nothing")
    ap.add_argument("--out-dir", help="a trial: the table under this folder, not warehouse/output")
    args = ap.parse_args(argv)
    if args.out_dir:
        raw_dir = ip.RAW_DIR
        ip.set_out_dir(args.out_dir)
        ip.RAW_DIR = raw_dir
    os.makedirs(ip.LOG_DIR, exist_ok=True)
    run_id = dt.datetime.now(dt.timezone.utc).strftime("%Y%m%dT%H%M%SZ")
    log = ip.Log(os.path.join(ip.LOG_DIR, f"eia861_territories_{run_id}.log"))
    ip.RAW.open(CONNECTOR, run_id)
    results = []
    try:
        page, _ = ip.fetch_raw(CONNECTOR, PAGE, log, offline=args.offline, headers=UA)
        url, year = zip_url(page.decode("utf-8", errors="replace"), args.year)
        if "/archive/" in url:
            raise RuntimeError(f"{url} is under /archive/, which EIA's robots file disallows (session 666); not asked")
        content, rec = ip.fetch_raw(CONNECTOR, url, log, offline=args.offline, headers=UA, timeout=600)
        if content[:2] != b"PK":
            raise RuntimeError(f"{url} is not a zip (it starts {content[:20]!r})")
        xl = pd.ExcelFile(io.BytesIO(zipfile.ZipFile(io.BytesIO(content)).read(f"Service_Territory_{year}.xlsx")))
        if SHEETS[0] not in xl.sheet_names:
            raise RuntimeError(f"Service_Territory_{year}.xlsx has no {SHEETS[0]} sheet: {xl.sheet_names}")
        t = pd.concat([territories(pd.read_excel(xl, s, header=None), year, s, url, rec["retrieved_at"])
                       for s in SHEETS if s in xl.sheet_names], ignore_index=True)
        if t["entity_id"].duplicated().any():
            raise RuntimeError(f"{year}: a utility, state and county given twice: {t.loc[t['entity_id'].duplicated(), 'entity_id'].head(5).tolist()}")
        t = t.sort_values("entity_id").reset_index(drop=True)
        n_util, n_states = t["x_utility_number"].nunique(), t["x_state"].nunique()
        header = [
            f"Energy Research Warehouse (ERW): EIA-861 utility service territories, each utility's counties by state, {year} (session 667)",
            "Shape: entities (docs/datastandard.md v0). entity_id eia861:<utility number>:<state>:<county>; entity_type utility; name the utility's name; geo US-<state>; x_utility_number, x_state, x_county, x_short_form (Y: EIA's short form), x_data_year, x_sheet as EIA gives them.",
            f"Rows: {len(t):,} utility and county pairs, {n_util:,} utilities, {n_states} states and territories. A utility serves a county when EIA's sheet lists the pair; EIA gives no share of a county and no boundary, and none is added.",
            f"Retrieved: {run_id} (UTC) by warehouse/connectors/eia861_territories.py (the zip as saved by an earlier run: {rec['retrieved_at']})",
            f"Run log: warehouse/output/logs/eia861_territories_{run_id}.log",
            f"Raw files: warehouse/raw/{CONNECTOR}/ (not in git)",
            f"Source: {SOURCE} U.S. Energy Information Administration, Form EIA-861 Annual Electric Power Industry Report (Service_Territory_{year}.xlsx), {PAGE}",
            f"  access: {url}",
            'License: public (a work of the U.S. government; cite "U.S. Energy Information Administration, Form EIA-861").',
        ]
        ip.write_snapshot(t, NAME, header, log, cols=ENTITY_COLS + X_COLS)
        if not args.out_dir:
            ip.update_sources([dict(source=SOURCE, publisher="U.S. Energy Information Administration (EIA)",
                                    report="Form EIA-861 Annual Electric Power Industry Report, service territories",
                                    report_url=PAGE, document_list=PAGE, license="public", tables=[NAME])])
        results.append(dict(table=NAME, market="all", status="ok", detail=f"{year}: {len(t):,} rows, {n_util:,} utilities"))
        print(f"{NAME}: {year}, {len(t):,} utility and county pairs, {n_util:,} utilities, {n_states} states and territories")
    except Exception:
        tb = ip.redact(traceback.format_exc())
        log(f"FAILED, no output file written:\n{tb}")
        print(f"eia861_territories FAILED, no output file written: {tb.strip().splitlines()[-1]}", file=sys.stderr)
        results.append(dict(table=NAME, market="all", status="failed", detail=tb.strip().splitlines()[-1][:300]))
    if not args.out_dir:
        ip.write_status("eia861_territories", run_id, results)
    log.close()
    return 0 if all(r["status"] == "ok" for r in results) else 1


if __name__ == "__main__":
    sys.exit(main())

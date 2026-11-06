#!/usr/bin/env python3
"""EIA-861: each utility's NERC region, the RTOs it operates in and its activities, by state and year (session 867,
chain 047: the key that joins a utility to its grid for the All grids tab).

Energy Research Warehouse (ERW) connector. One entities table, warehouse/output/eia861_utility_data.csv, from the U.S.
Energy Information Administration's Form EIA-861 annual files (Utility_Data_<year>.xlsx in f861<year>.zip, sheets States
and Territories), the zips eia861_sales.py saved:

    page   https://www.eia.gov/electricity/data/eia861/
    file   https://www.eia.gov/electricity/data/eia861/zip/f861<year>.zip   (earlier years under archive/zip/)

    entity_id   eia861_utility:<utility number>:<state>:<year>, one row of EIA's sheet (EIA lists a utility once a
                year, under one state, though it may sell in several); entity_type utility; name the
                utility's name; geo US-<state> (US for the few rows EIA gives no state); status_date the data
                year's 1 January
    x_*         EIA's own fields: utility number, state, year, ownership, NERC region; then each flag as EIA gives it (Y, N
                or empty): the other NERC regions the utility also operates in (x_nerc_<region>), the RTOs it operates in
                (x_rto_<rto>, and x_rto_other), and its activities (x_generation, x_transmission, x_buying_transmission,
                x_distribution, x_buying_distribution, x_wholesale_marketing, x_retail_marketing, x_bundled,
                x_alt_fuel_vehicle, x_alt_fuel_vehicle_2); and x_rtos, the RTOs marked Y, joined by ";"

The sheet's columns are found by their headings and their group heading (EIA names a NERC region and an RTO both "SPP";
the group above tells them apart). EIA's aggregates 88888 (Withheld) and 99999 (Adjustment) are not utilities and
are left out, as eia861_sales.py leaves them. A key given twice stops the run.

    python warehouse/connectors/eia861_utility_data.py --years 2015 ... 2025 --offline

Ceiling: two requests a year (the page and the zip), none when both are saved in warehouse/raw/eia861/. EIA's robots
file disallows /archive/ (session 666): a year there is read only from a zip already saved. License: public (EIA, record 1
of license_reads.csv; cite "U.S. Energy Information Administration, Form EIA-861").
"""

import argparse
import datetime as dt
import io
import os
import re
import sys
import traceback
import zipfile

import pandas as pd

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import iso_prices as ip  # noqa: E402
from eia861_sales import NOT_UTILITIES, PAGE, UA, held_text, zip_url  # noqa: E402  the same page, zips and aggregates as the sales table

NAME = "eia861_utility_data"
CONNECTOR = "eia861"
SOURCE = "eia:eia861:utility_data"
SHEETS = ["States", "Territories"]
ENTITY_COLS = ["entity_id", "entity_type", "name", "geo", "lat", "lon", "capacity_mw", "status", "status_date", "operator",
               "source", "source_url", "retrieved_at", "vintage"]
GROUPS = {"also operating in other nerc regions": "nerc", "operating in these rtos": "rto", "other activities": "activity"}
CHARS = {"data year": "x_year", "utility number": "x_utility_number", "utility name": "name", "state": "x_state",
         "ownership type": "x_ownership", "nerc region": "x_nerc_region", "short form": "x_short_form"}
NERC = ["tre", "frcc", "mro", "npcc", "rfc", "serc", "spp", "wecc"]
RTO = ["caiso", "ercot", "pjm", "nyiso", "spp", "miso", "isone", "other"]
ACTIVITY = ["generation", "transmission", "buying_transmission", "distribution", "buying_distribution",
            "wholesale_marketing", "retail_marketing", "bundled", "alt_fuel_vehicle", "alt_fuel_vehicle_2"]
X_COLS = (["x_utility_number", "x_state", "x_year", "x_ownership", "x_nerc_region", "x_short_form"]
          + [f"x_nerc_{r}" for r in NERC] + [f"x_rto_{r}" for r in RTO] + [f"x_{a}" for a in ACTIVITY] + ["x_rtos"])


def slug(v):
    return re.sub(r"[^a-z0-9]+", "_", v.lower()).strip("_")


def text(v):
    if v is None or (isinstance(v, float) and pd.isna(v)):
        return ""
    if isinstance(v, float) and v.is_integer():
        return str(int(v))
    return str(v).strip()


def layout(frame):
    """(heading row, {field: column}); a field missing stops the run."""
    heads = [r for r in range(min(4, len(frame))) if any(text(v) == "Utility Number" for v in frame.iloc[r])]
    if not heads:
        raise RuntimeError("no heading row names 'Utility Number'")
    hr = heads[0]
    cols, group = {}, None
    for c in range(frame.shape[1]):
        top = text(frame.iloc[hr - 1, c]).lower() if hr >= 1 else ""
        if top in GROUPS:
            group = GROUPS[top]
        name = text(frame.iloc[hr, c]).replace("\n", " ").lower()
        if group is None and name in CHARS:
            cols[CHARS[name]] = c
        elif group == "nerc" and slug(name) in NERC:
            cols[f"x_nerc_{slug(name)}"] = c
        elif group == "rto" and slug(name) in RTO:
            cols[f"x_rto_{slug(name)}"] = c
        elif group == "activity" and slug(name) in ACTIVITY:
            cols[f"x_{slug(name)}"] = c
    need = ["x_year", "x_utility_number", "name", "x_state", "x_ownership", "x_nerc_region"] + [x for x in X_COLS[6:-1]]
    missing = [k for k in need if k not in cols]
    if missing:
        raise RuntimeError(f"the sheet's headings lack {missing}")
    return hr, cols


def sheet_rows(frame, year, url, retrieved):
    hr, cols = layout(frame)
    d = frame.iloc[hr + 1:]
    d = d[pd.to_numeric(d[cols["x_year"]], errors="coerce").eq(year)]
    d = d[~pd.to_numeric(d[cols["x_utility_number"]], errors="coerce").isin(NOT_UTILITIES)]   # EIA's 88888 Withheld and 99999 Adjustment
    out = []
    for _, r in d.iterrows():
        x = {k: text(r[c]) for k, c in cols.items()}
        x.setdefault("x_short_form", "")
        util, state = x["x_utility_number"], x["x_state"]
        rtos = ";".join(rto.upper() if rto != "other" else "Other" for rto in RTO if x[f"x_rto_{rto}"] == "Y")
        name = x.pop("name")
        out.append(dict(entity_id=f"eia861_utility:{util}:{state}:{year}", entity_type="utility", name=name, geo=f"US-{state}" if state else "US",
                        lat="", lon="", capacity_mw="", status="", status_date=f"{year}-01-01", operator="", source=SOURCE,
                        source_url=url, retrieved_at=retrieved, vintage="", x_rtos=rtos, **x))
    t = pd.DataFrame(out)
    if len(t) and t["entity_id"].duplicated().any():
        raise RuntimeError(f"{year}: a utility and state given twice: {t.loc[t['entity_id'].duplicated(), 'entity_id'].head(3).tolist()}")
    return t


def main(argv=None):
    ap = argparse.ArgumentParser(description="EIA-861 utilities' NERC regions, RTOs and activities, by state and year")
    ap.add_argument("--years", type=int, nargs="+", required=True, help="the data years")
    ap.add_argument("--offline", action="store_true", help="never a request: the saved page and zips, or nothing")
    ap.add_argument("--out-dir", help="a trial: the table under this folder, not warehouse/output")
    args = ap.parse_args(argv)
    if args.out_dir:
        raw_dir = ip.RAW_DIR
        ip.set_out_dir(args.out_dir)
        ip.RAW_DIR = raw_dir
    os.makedirs(ip.LOG_DIR, exist_ok=True)
    run_id = dt.datetime.now(dt.timezone.utc).strftime("%Y%m%dT%H%M%SZ")
    log = ip.Log(os.path.join(ip.LOG_DIR, f"eia861_utility_data_{run_id}.log"))
    ip.RAW.open(CONNECTOR, run_id)
    results = []
    try:
        page, _ = ip.fetch_raw(CONNECTOR, PAGE, log, offline=args.offline, headers=UA)
        html = page.decode("utf-8", errors="replace")
        frames, urls = [], []
        for y in sorted(args.years):
            url, year = zip_url(html, y)
            if "/archive/" in url and not ip.raw_cached(CONNECTOR, url):
                raise RuntimeError(f"{url} is under /archive/, which EIA's robots file disallows (session 666), and is not saved; not asked")
            content, rec = ip.fetch_raw(CONNECTOR, url, log, offline=args.offline, headers=UA, timeout=600)
            if content[:2] != b"PK":
                raise RuntimeError(f"{url} is not a zip (it starts {content[:20]!r})")
            xl = pd.ExcelFile(io.BytesIO(zipfile.ZipFile(io.BytesIO(content)).read(f"Utility_Data_{year}.xlsx")))
            for s in SHEETS:
                if s in xl.sheet_names:
                    t = sheet_rows(pd.read_excel(xl, s, header=None), year, url, rec["retrieved_at"])
                    log(f"{year} {s}: {len(t):,} rows")
                    frames.append(t)
            urls.append(url)
        s = pd.concat([f for f in frames if len(f)], ignore_index=True)
        if s["entity_id"].duplicated().any():
            raise RuntimeError("a row in both sheets")
        s = s.sort_values("entity_id").reset_index(drop=True)[ENTITY_COLS + X_COLS]
        years = sorted({int(y) for y in s["x_year"]})
        header = [
            "Energy Research Warehouse (ERW): EIA-861 utility data: each utility's NERC region, the RTOs it operates in and its activities, by state and year (session 867)",
            "Shape: entities (docs/datastandard.md v0). entity_id eia861_utility:<utility>:<state>:<year>; entity_type utility; name the utility's name; geo US-<state>; status_date the data year's 1 January; "
            "x_* EIA's fields: each flag as EIA gives it (Y, N or empty): x_nerc_<region> (other NERC regions), x_rto_<rto>, the activities; x_rtos the RTOs marked Y.",
            f"Years held: {held_text(years)}; {len(s):,} rows, {s['x_utility_number'].nunique():,} utilities. EIA lists a utility once a year, under one state, though it may sell in several. EIA names a NERC region and an RTO both SPP; the group heading above tells them apart.",
            f"Retrieved: {run_id} (UTC) by warehouse/connectors/eia861_utility_data.py (the zips as saved by earlier runs)",
            f"Run log: warehouse/output/logs/eia861_utility_data_{run_id}.log",
            f"Raw files: warehouse/raw/{CONNECTOR}/ (not in git)",
            f"Source: {SOURCE} U.S. Energy Information Administration, Form EIA-861 Annual Electric Power Industry Report (Utility_Data_<year>.xlsx), {PAGE}",
            f"  access: {'; '.join(urls)}",
            'License: public (a work of the U.S. government; cite "U.S. Energy Information Administration, Form EIA-861").',
        ]
        ip.write_snapshot(s, NAME, header, log, cols=ENTITY_COLS + X_COLS)
        if not args.out_dir:
            ip.update_sources([dict(source=SOURCE, publisher="U.S. Energy Information Administration (EIA)",
                                    report="Form EIA-861 Annual Electric Power Industry Report, utility data", report_url=PAGE,
                                    document_list=PAGE, license="public", tables=[NAME])])
        results.append(dict(table=NAME, market="all", status="ok", detail=f"{held_text(years)}: {len(s):,} rows"))
        print(f"{NAME}: {held_text(years)}, {len(s):,} rows, {s['x_utility_number'].nunique():,} utilities")
    except Exception:
        tb = ip.redact(traceback.format_exc())
        log(f"FAILED, no output file written:\n{tb}")
        print(f"eia861_utility_data FAILED, no output file written: {tb.strip().splitlines()[-1]}", file=sys.stderr)
        results.append(dict(table=NAME, market="all", status="failed", detail=tb.strip().splitlines()[-1][:300]))
    if not args.out_dir:
        ip.write_status("eia861_utility_data", run_id, results)
    log.close()
    return 0 if all(r["status"] == "ok" for r in results) else 1


if __name__ == "__main__":
    sys.exit(main())

#!/usr/bin/env python3
"""EIA-861's short form: the small utilities' revenue, sales and customers, by state and year (session 876, chain 047:
the utilities eia861_utility_sales leaves out as EIA's imputed rows; here as each utility reported them on Form EIA-861S).

Energy Research Warehouse (ERW) connector. One series table, warehouse/output/eia861_short_form.csv, from the U.S. Energy
Information Administration's Form EIA-861 annual files (Short_Form_<year>.xlsx in f861<year>.zip, sheet 861S; the zips
eia861_sales.py saved). EIA gives no short-form file for 2019, whose short-form utilities are in its main sales file.

    entity    eia861_sf:<utility>:<state>:<balancing authority>
    variable  total_revenue (USD, EIA's thousand dollars times 1,000), total_sales (MWh), total_customers (count)
    ts_utc    the data year's 1 January; freq P1Y; geo US-<state>; node the utility's name
    x_*       EIA's own fields: utility number, state, ownership, balancing authority, and the programs the utility marks
              (x_water_heater, x_net_metering, x_demand_side_management, x_time_based_programs: Y, N or empty)

Every column is found by its heading (EIA spells "BA_Code" and "BA Code", "Water Heater" and "W_Heater"). EIA's
aggregates 88888 and 99999 are left out; a "." cell has no row; nothing is filled. Two rows under one key with different
figures have no key and are both left out whole, named in the header (chain 030's rule).

    python warehouse/connectors/eia861_short_form.py --years 2015 ... 2025 --offline

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
from eia861_sales import NOT_UTILITIES, PAGE, UA, held_text, zip_url  # noqa: E402

NAME = "eia861_short_form"
CONNECTOR = "eia861"
SOURCE = "eia:eia861:short_form"
HEADS = {"data year": "year", "utility number": "utility", "utility name": "name", "ownership": "x_ownership", "state": "state",
         "ba code": "ba", "ba_code": "ba", "total revenue (thousand dollars)": "total_revenue", "total sales (mwh)": "total_sales",
         "total customers": "total_customers", "water heater": "x_water_heater", "w_heater": "x_water_heater",
         "net metering": "x_net_metering", "demand side management": "x_demand_side_management",
         "time based programs": "x_time_based_programs"}
FIGS = {"total_revenue": ("USD", 1000.0), "total_sales": ("MWh", 1.0), "total_customers": ("count", 1.0)}
X_COLS = ["x_utility_number", "x_state", "x_ownership", "x_ba_code", "x_water_heater", "x_net_metering",
          "x_demand_side_management", "x_time_based_programs"]


def text(v):
    if v is None or (isinstance(v, float) and pd.isna(v)):
        return ""
    if isinstance(v, float) and v.is_integer():
        return str(int(v))
    return re.sub(r"\s+", " ", str(v)).strip()


def sheet_rows(frame, year, url, retrieved, notes):
    heads = [r for r in range(min(4, len(frame))) if any(text(v).lower() == "utility number" for v in frame.iloc[r])]
    if not heads:
        raise RuntimeError("no heading row names 'Utility Number'")
    hr = heads[0]
    cols = {}
    for c in range(frame.shape[1]):
        k = HEADS.get(text(frame.iloc[hr, c]).lower())
        if k:
            cols[k] = c
    missing = [k for k in set(HEADS.values()) if k not in cols]
    if missing:
        raise RuntimeError(f"{year}: the sheet's headings lack {sorted(missing)}")
    d = frame.iloc[hr + 1:]
    d = d[pd.to_numeric(d[cols["year"]], errors="coerce").eq(year)]
    d = d[~pd.to_numeric(d[cols["utility"]], errors="coerce").isin(NOT_UTILITIES)]
    out = []
    for _, r in d.iterrows():
        util, state, ba = text(r[cols["utility"]]), text(r[cols["state"]]), text(r[cols["ba"]])
        base = dict(entity=f"eia861_sf:{util}:{state}:{ba}", ts_utc=f"{year}-01-01T00:00:00Z", freq="P1Y",
                    geo=f"US-{state}" if state else "US", market="", node=text(r[cols["name"]]), source=SOURCE, source_url=url,
                    retrieved_at=retrieved, vintage="", x_utility_number=util, x_state=state, x_ba_code=ba,
                    **{k: text(r[cols[k]]) for k in X_COLS if k.startswith("x_") and k in cols})
        for var, (unit, scale) in FIGS.items():
            v = pd.to_numeric(r[cols[var]], errors="coerce")
            if pd.isna(v):
                continue
            out.append(dict(base, variable=var, value=float(v) * scale, unit=unit))
    t = pd.DataFrame(out)
    if len(t):
        t = t.drop_duplicates()
        twice = t.duplicated(["entity", "variable", "ts_utc"], keep=False)
        if twice.any():
            bad = set(t.loc[twice, "entity"])
            notes.update(f"{e} {year}" for e in bad)
            t = t[~t["entity"].isin(bad)]
    return t


def main(argv=None):
    ap = argparse.ArgumentParser(description="EIA-861 short form: small utilities' revenue, sales and customers")
    ap.add_argument("--years", type=int, nargs="+", required=True, help="the data years (EIA has no file for 2019)")
    ap.add_argument("--offline", action="store_true", help="never a request: the saved page and zips, or nothing")
    ap.add_argument("--out-dir", help="a trial: the table under this folder, not warehouse/output")
    args = ap.parse_args(argv)
    if args.out_dir:
        raw_dir = ip.RAW_DIR
        ip.set_out_dir(args.out_dir)
        ip.RAW_DIR = raw_dir
    os.makedirs(ip.LOG_DIR, exist_ok=True)
    run_id = dt.datetime.now(dt.timezone.utc).strftime("%Y%m%dT%H%M%SZ")
    log = ip.Log(os.path.join(ip.LOG_DIR, f"eia861_short_form_{run_id}.log"))
    ip.RAW.open(CONNECTOR, run_id)
    results = []
    try:
        page, _ = ip.fetch_raw(CONNECTOR, PAGE, log, offline=args.offline, headers=UA)
        html = page.decode("utf-8", errors="replace")
        frames, urls, notes, none = [], [], set(), []
        for y in sorted(args.years):
            url, year = zip_url(html, y)
            if "/archive/" in url and not ip.raw_cached(CONNECTOR, url):
                raise RuntimeError(f"{url} is under /archive/, which EIA's robots file disallows (session 666), and is not saved; not asked")
            content, rec = ip.fetch_raw(CONNECTOR, url, log, offline=args.offline, headers=UA, timeout=600)
            zf = zipfile.ZipFile(io.BytesIO(content))
            name = next((n for n in zf.namelist() if n.lower() == f"short_form_{year}.xlsx"), None)
            if not name:
                none.append(year)
                log(f"{year}: no short-form file in the zip")
                continue
            xl = pd.ExcelFile(io.BytesIO(zf.read(name)))
            t = sheet_rows(pd.read_excel(xl, xl.sheet_names[0], header=None), year, url, rec["retrieved_at"], notes)
            log(f"{year}: {len(t):,} rows")
            frames.append(t)
            urls.append(url)
        s = pd.concat([f for f in frames if len(f)], ignore_index=True)
        cols = ip.SERIES_COLS + X_COLS
        s = s[cols]
        years = sorted({int(t[:4]) for t in s["ts_utc"]})
        header = [
            "Energy Research Warehouse (ERW): EIA-861 short form: small utilities' revenue, sales and customers, by state and year, as each reported them (session 876)",
            "Shape: series (docs/datastandard.md v0). entity eia861_sf:<utility>:<state>:<balancing authority>; variables total_revenue (USD, EIA's thousand dollars times 1,000), total_sales (MWh), total_customers (count); "
            "ts_utc the data year's 1 January; freq P1Y; node the utility's name; x_* EIA's fields and the programs the utility marks (Y, N or empty).",
            f"Years held: {held_text(years)}" + (f" (EIA gives no short-form file for {', '.join(map(str, none))})" if none else "")
            + f"; {len(s):,} rows, {s['x_utility_number'].nunique():,} utilities. EIA's aggregates 88888 and 99999 left out; a '.' cell has no row; nothing is filled."
            + (f" Left out, no key (two rows, two values): {', '.join(sorted(notes))}." if notes else ""),
            f"Retrieved: {run_id} (UTC) by warehouse/connectors/eia861_short_form.py (the zips as saved by earlier runs)",
            f"Run log: warehouse/output/logs/eia861_short_form_{run_id}.log",
            f"Raw files: warehouse/raw/{CONNECTOR}/ (not in git)",
            f"Source: {SOURCE} U.S. Energy Information Administration, Form EIA-861 Annual Electric Power Industry Report (Short_Form_<year>.xlsx, Form EIA-861S), {PAGE}",
            f"  access: {'; '.join(urls)}",
            'License: public (a work of the U.S. government; cite "U.S. Energy Information Administration, Form EIA-861").',
        ]
        ip.write_snapshot(s, NAME, header, log, cols)
        if not args.out_dir:
            ip.update_sources([dict(source=SOURCE, publisher="U.S. Energy Information Administration (EIA)",
                                    report="Form EIA-861 Annual Electric Power Industry Report, short form (EIA-861S)", report_url=PAGE,
                                    document_list=PAGE, license="public", tables=[NAME])])
        results.append(dict(table=NAME, market="all", status="ok", detail=f"{held_text(years)}: {len(s):,} rows"))
        print(f"{NAME}: {held_text(years)}, {len(s):,} rows, {s['x_utility_number'].nunique():,} utilities; no file for {none}; {len(notes)} without a key")
    except Exception:
        tb = ip.redact(traceback.format_exc())
        log(f"FAILED, no output file written:\n{tb}")
        print(f"eia861_short_form FAILED, no output file written: {tb.strip().splitlines()[-1]}", file=sys.stderr)
        results.append(dict(table=NAME, market="all", status="failed", detail=tb.strip().splitlines()[-1][:300]))
    if not args.out_dir:
        ip.write_status("eia861_short_form", run_id, results)
    log.close()
    return 0 if all(r["status"] == "ok" for r in results) else 1


if __name__ == "__main__":
    sys.exit(main())

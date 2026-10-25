#!/usr/bin/env python3
"""Great Britain's electricity consumption and meters a year by country and region, 2005 to 2024, domestic and non-domestic, as
the Department for Energy Security and Net Zero (DESNZ) publishes them in its Subnational electricity consumption statistics
(session 2693, chain 135, the session's second own choice; the ERW held the UK's consumption only nationally).

Energy Research Warehouse (ERW) connector. One series table, warehouse/output/desnz_gb_regional_consumption_annual.csv,
from one workbook (no key), a sheet a year:

    https://assets.publishing.service.gov.uk/media/69426e905431f4f94d7f0b5e/Subnational_electricity_consumption_statistics_2005-2024.xlsx

    entity      desnz_sub:<area>:<item>: area the country or region as each sheet names it (great_britain, england, wales,
                scotland and unallocated to 2014; great_britain_inc_unallocated, england_and_wales_inc_unallocated and
                scotland_inc_unallocated from 2015; england's nine regions throughout, inner_london and outer_london from 2015);
                item consumption_domestic, consumption_non_domestic, consumption_total, and from 2012 consumption_domestic_standard
                and consumption_domestic_e7 (variable consumption); the same for meters_ (variable meters)
    unit        MWh (the workbook's GWh times 1,000) or count (its thousands of meters times 1,000); ts_utc the year's first day;
                freq P1Y; geo GB, GB-ENG (England and its regions), GB-WLS, GB-SCT, or GB-ENG,GB-WLS for England and Wales
    node        the area and the column as DESNZ gives them

Only the rows of whole countries and regions ("All local authorities") are read; the local authorities are not taken. Each area
is kept as the sheet names it: from 2015 Great Britain's and Scotland's rows include the consumption not allocated to a local
authority, which earlier sheets give in a row of its own, so the two names are two series and nothing is moved between them.
Columns are read by their headings: "Domestic" (to 2011) and "All Domestic" (from 2012) are one item, as are "Non-Domestic"
and "All Non-Domestic"; the means, medians and consumption per household are not taken. Checks, each within 1 GWh or 0.01
thousand meters: an area's domestic and non-domestic parts add to its total, and from 2012 its standard and Economy 7 meters and
consumption add to its domestic; England's nine regions add to England. A heading or area not in the map, a sheet not a year,
or a check missed stops the run. Nothing is filled.

    python warehouse/connectors/desnz_subnational_consumption.py [--offline] [--fresh] [--out-dir DIR]

Ceiling: one request a run, saved in warehouse/raw/desnz_regional/ and reused unless --fresh; --offline asks nothing.
www.gov.uk's robots file closes only print and search paths; assets.publishing.service.gov.uk has no robots file (session 2678).
License: the Open Government Licence v3.0 (DESNZ's verdict on record, session 2167): public.
"""

import argparse
import datetime as dt
import io
import os
import re
import sys
import traceback

import openpyxl
import pandas as pd

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import iso_prices as ip  # noqa: E402

NAME = "desnz_gb_regional_consumption_annual"
CONNECTOR = "desnz_regional"
SOURCE = "desnz:subnational_electricity_consumption_2005_2024"
HOST = "assets.publishing.service.gov.uk"
URL = ("https://assets.publishing.service.gov.uk/media/69426e905431f4f94d7f0b5e/"
       "Subnational_electricity_consumption_statistics_2005-2024.xlsx")
PAGE = "https://www.gov.uk/government/statistics/regional-and-local-authority-electricity-consumption-statistics"
UA = {"User-Agent": "Mozilla/5.0 (compatible; ERW-connector/0.1; +https://github.com/SamuelEnrique/erw)"}
CITATION = "Department for Energy Security and Net Zero, Subnational electricity consumption statistics, 2005 to 2024"
AREAS = {"Great Britain": ("great_britain", "GB"), "Great Britain (inc unallocated)": ("great_britain_inc_unallocated", "GB"),
         "England and Wales (inc unallocated)": ("england_and_wales_inc_unallocated", "GB-ENG,GB-WLS"),
         "England": ("england", "GB-ENG"), "North East": ("north_east", "GB-ENG"), "North West": ("north_west", "GB-ENG"),
         "Yorkshire and The Humber": ("yorkshire_humber", "GB-ENG"), "East Midlands": ("east_midlands", "GB-ENG"),
         "West Midlands": ("west_midlands", "GB-ENG"), "East": ("east_of_england", "GB-ENG"), "London": ("london", "GB-ENG"),
         "Inner London": ("inner_london", "GB-ENG"), "Outer London": ("outer_london", "GB-ENG"),
         "South East": ("south_east", "GB-ENG"), "South West": ("south_west", "GB-ENG"), "Wales": ("wales", "GB-WLS"),
         "Scotland": ("scotland", "GB-SCT"), "Scotland (inc unallocated)": ("scotland_inc_unallocated", "GB-SCT"),
         "Unallocated": ("unallocated", "GB")}
REGIONS = ["north_east", "north_west", "yorkshire_humber", "east_midlands", "west_midlands", "east_of_england", "london",
           "south_east", "south_west"]
PARTS = {"Domestic": "domestic", "All Domestic": "domestic", "Non-Domestic": "non_domestic", "All Non-Domestic": "non_domestic",
         "All meters": "total", "Domestic Standard": "domestic_standard", "Domestic E7": "domestic_e7"}
MEASURES = {"Number of meters (thousands)": ("meters", "meters", "count", 1000), "Total consumption (GWh)": ("consumption", "consumption", "MWh", 1000)}
SKIP = ("Mean consumption", "Median consumption", "Mean domestic consumption")
X_COLS = []


def label(v):
    return " ".join(str(v).split()) if v is not None else ""


def columns(head):
    cols = {}
    for j, x in enumerate(head[3:], 3):
        s = label(x)
        if not s or s.startswith(SKIP):
            continue
        m = re.fullmatch(r"(.+?): (.+)", s)
        if not m or m.group(1) not in MEASURES or m.group(2) not in PARTS:
            raise RuntimeError(f"a heading not in the map: {s!r}")
        prefix, variable, unit, scale = MEASURES[m.group(1)]
        cols[j] = (f"{prefix}_{PARTS[m.group(2)]}", variable, unit, scale, s)
    return cols


def parse_sheet(rows, year):
    h = next((i for i, r in enumerate(rows) if label(r[0]) == "Code"), None)
    if h is None or [label(x) for x in rows[h][:3]] != ["Code", "Country or region", "Local authority"]:
        raise RuntimeError(f"{year}: no header row")
    cols = columns(rows[h])
    out = {}
    for r in rows[h + 1:]:
        if label(r[2]) != "All local authorities":
            continue
        name = label(r[1])
        if name not in AREAS:
            raise RuntimeError(f"{year}: an area not in the map: {name!r}")
        area = AREAS[name][0]
        for j, (item, variable, unit, scale, head) in cols.items():
            v = r[j] if j < len(r) else None
            if v is None or (isinstance(v, str) and v.strip() in ("", "-", "[x]")):
                continue
            if not isinstance(v, (int, float)) or v < 0:
                raise RuntimeError(f"{year} {name} {head}: not a quantity: {v!r}")
            out[(area, item)] = (float(v), variable, unit, scale, f"{name}: {head}")
    g = lambda a, i: out.get((a, i), (None,))[0]
    for area in {a for a, _ in out}:
        for kind, tol in (("consumption", 1.0), ("meters", 0.01)):
            d, n, t = g(area, f"{kind}_domestic"), g(area, f"{kind}_non_domestic"), g(area, f"{kind}_total")
            if None not in (d, n, t) and abs(d + n - t) > tol:
                raise RuntimeError(f"{year} {area}: {kind} domestic and non-domestic make {d + n:,.2f}, the total {t:,.2f}")
            s, e = g(area, f"{kind}_domestic_standard"), g(area, f"{kind}_domestic_e7")
            if None not in (s, e, d) and abs(s + e - d) > tol:
                raise RuntimeError(f"{year} {area}: {kind} standard and E7 make {s + e:,.2f}, the domestic {d:,.2f}")
    regs = [g(a, "consumption_total") for a in REGIONS]
    if None in regs or g("england", "consumption_total") is None or abs(sum(regs) - g("england", "consumption_total")) > 1.0:
        raise RuntimeError(f"{year}: England's nine regions do not make England's consumption")
    return out


def parse(content, base):
    wb = openpyxl.load_workbook(io.BytesIO(content), data_only=True, read_only=True)
    years = sorted(int(s) for s in wb.sheetnames if re.fullmatch(r"\d{4}", s))
    others = [s for s in wb.sheetnames if not re.fullmatch(r"\d{4}", s) and s != "Cover sheet"]
    if others or not years or years != list(range(years[0], years[-1] + 1)):
        raise RuntimeError(f"the sheets are not a run of years: {wb.sheetnames}")
    geo = {v[0]: v[1] for v in AREAS.values()}
    rows = []
    for y in years:
        vals = parse_sheet([tuple(r) for r in wb[str(y)].iter_rows(values_only=True)], y)
        rows += [dict(entity=f"desnz_sub:{area}:{item}", variable=variable, ts_utc=f"{y}-01-01T00:00:00Z", value=round(v * scale, 3),
                      unit=unit, freq="P1Y", geo=geo[area], market="", node=lab, **base)
                 for (area, item), (v, variable, unit, scale, lab) in sorted(vals.items())]
    return pd.DataFrame(rows)


def main(argv=None):
    ap = argparse.ArgumentParser(description="DESNZ: Great Britain's electricity consumption and meters by country and region")
    ap.add_argument("--offline", action="store_true", help="the saved workbook only, no request")
    ap.add_argument("--fresh", action="store_true", help="ask for the workbook again")
    ap.add_argument("--out-dir", help="a trial: the table under this folder, not warehouse/output")
    args = ap.parse_args(argv)
    if ip.paused(CONNECTOR) or ip.paused_host(HOST):
        print(f"{NAME}: the publisher is paused (warehouse/metadata/paused_sources.csv); nothing asked")
        return 0
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
        content, rec = ip.fetch_raw(CONNECTOR, URL, log, offline=args.offline, fresh=args.fresh, headers=UA, timeout=180, pause=1)
        base = dict(source=SOURCE, source_url=URL, retrieved_at=rec.get("retrieved_at") or "", vintage=ip.vintage_of(rec))
        t = parse(content, base)
        if t.duplicated(["entity", "variable", "ts_utc"]).any():
            raise RuntimeError("a key given twice")
        cols = ip.SERIES_COLS + X_COLS
        t = t[cols].sort_values(["entity", "ts_utc"]).reset_index(drop=True)
        gb = t[t.entity.isin(["desnz_sub:great_britain:consumption_total", "desnz_sub:great_britain_inc_unallocated:consumption_total"])]
        gb = gb.set_index("ts_utc").value
        head = [
            "Energy Research Warehouse (ERW): DESNZ, Subnational electricity consumption statistics: Great Britain's electricity "
            f"consumption and meters by country and region, {t.ts_utc.min()[:4]} to {t.ts_utc.max()[:4]} (session 2693)",
            "Shape: series (docs/datastandard.md v0). entity desnz_sub:<area>:<item>; variable consumption (MWh, the workbook's GWh "
            "times 1,000) or meters (count, its thousands times 1,000); ts_utc the year's first day; freq P1Y; geo GB, GB-ENG, "
            "GB-WLS, GB-SCT or GB-ENG,GB-WLS; node the area and the column.",
            f"{len(t)} rows; Great Britain's consumption, TWh: " + ", ".join(f"{k[:4]} {v / 1e6:.1f}" for k, v in gb.items()
                                                                         if k[:4] in ("2005", "2014", "2015", "2024"))
            + ". Areas as each sheet names them (Great Britain and Scotland include the unallocated consumption from 2015); "
            "parts and regions checked against their totals; nothing is filled.",
            f"Retrieved: {run_id} (UTC) by warehouse/connectors/desnz_subnational_consumption.py; the workbook retrieved "
            f"{base['retrieved_at']}; last modified {base['vintage']}",
            f"Run log: warehouse/output/logs/{CONNECTOR}_{run_id}.log",
            f"Raw files: warehouse/raw/{CONNECTOR}/ (not in git)",
            f"Source: {SOURCE} {CITATION}",
            f"  access: {URL} (listed on {PAGE})",
            "License: Open Government Licence v3.0. Credit: Department for Energy Security and Net Zero.",
        ]
        ip.write_snapshot(t, NAME, head, log, cols)
        results.append(dict(table=NAME, market="all", status="ok", detail=f"{len(t)} rows"))
        print(f"{NAME}: {len(t)} rows, {t.entity.nunique()} entities")
    except Exception:
        tb = ip.redact(traceback.format_exc())
        log(f"{NAME} FAILED, no output file written:\n{tb}")
        print(f"{NAME} FAILED, no output file written: {tb.strip().splitlines()[-1]}", file=sys.stderr)
        results.append(dict(table=NAME, market="all", status="failed", detail=tb.strip().splitlines()[-1][:300]))
    if not args.out_dir:
        if results and results[0]["status"] == "ok":
            ip.update_sources([dict(source=SOURCE, publisher="UK Department for Energy Security and Net Zero (DESNZ)",
                                    report="Subnational electricity consumption statistics, 2005 to 2024 (countries and regions)",
                                    report_url=PAGE, document_list=PAGE, license="public", tables=[NAME])])  # OGL v3.0
        ip.write_status(CONNECTOR, run_id, results)
    log.close()
    return 0 if all(r["status"] == "ok" for r in results) else 1


if __name__ == "__main__":
    sys.exit(main())

#!/usr/bin/env python3
"""EIA's Electric Power Annual, chapter 8: average heat rates by energy source and by prime mover, the major investor-owned
utilities' revenue and expenses, and their power plants' operation and maintenance expenses, 2015 to 2025 (session 903,
chain 049: a public source the ERW did not hold, for the cost of power).

Energy Research Warehouse (ERW) connector. One series table, warehouse/output/eia_power_costs_annual.csv, from four
workbooks of https://www.eia.gov/electricity/annual/ :

    xls/epa_08_01.xlsx   Table 8.1, average operating heat rate by energy source (Btu per kWh)
    xls/epa_08_02.xlsx   Table 8.2, average tested heat rate by prime mover and energy source (Btu per kWh)
    xls/epa_08_03.xlsx   Table 8.3, revenue and expense statistics for major U.S. investor-owned electric utilities (million dollars)
    xls/epa_08_04.xlsx   Table 8.4, average power plant operating expenses for those utilities (mills per kWh)

    entity    eia_epa:heat_rate:<energy source>; eia_epa:tested_heat_rate:<prime mover>:<energy source>;
              eia_epa:iou_finance:<the line's path, its parents joined with ".">; eia_epa:iou_plant_expense:<plant type>
    variable  heat_rate (MMBtu/MWh: EIA's Btu per kWh divided by 1,000), tested_heat_rate (the same), amount (USD: EIA's
              million dollars times 1,000,000), operation_expense, maintenance_expense, fuel_expense and total_expense
              (USD/MWh: EIA's mills per kWh, the same number)
    ts_utc    the year's 1 January; freq P1Y; geo US; node the line as EIA words it

A value EIA withholds ("W") or does not have ("--", "NA") has no row; nothing is filled. A table's lines are found by
their headings and indentation (the dots before a line of table 8.3 give its depth); a heading or a line not in the form
read stops the run. EIA notes that missing or erroneous respondent data may leave table 8.3's subtotals slightly out.

    python warehouse/connectors/eia_epa_costs.py [--offline]

Ceiling: four requests (the workbooks; saved in warehouse/raw/eia_epa_costs/ and reused offline). EIA's robots file allows
/electricity/annual/. License: public (EIA, record 1 of license_reads.csv; cite "U.S. Energy Information Administration,
Electric Power Annual").
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

NAME = "eia_power_costs_annual"
CONNECTOR = "eia_epa_costs"
SOURCE = "eia:electric_power_annual:chapter8"
PAGE = "https://www.eia.gov/electricity/annual/"
UA = {"User-Agent": "Mozilla/5.0 (compatible; ERW-connector/0.1; +https://github.com/SamuelEnrique/erw)"}
SOURCES = ["Coal", "Petroleum", "Natural Gas", "Nuclear"]
MOVERS = ["Steam Generator", "Gas Turbine", "Internal Combustion", "Combined Cycle"]
PLANTS = ["Nuclear", "Fossil Steam", "Hydro-electric", "Gas Turbine and Small Scale"]


def text(v):
    if v is None or (isinstance(v, float) and pd.isna(v)):
        return ""
    if isinstance(v, float) and v.is_integer():
        return str(int(v))
    return re.sub(r"\s+", " ", str(v)).strip()


def slug(v):
    return re.sub(r"[^a-z0-9]+", "_", v.lower()).strip("_")


def row(entity, variable, year, value, unit, node, url, retrieved):
    return dict(entity=entity, variable=variable, ts_utc=f"{year}-01-01T00:00:00Z", value=value, unit=unit, freq="P1Y", geo="US",
                market="", node=node, source=SOURCE, source_url=url, retrieved_at=retrieved, vintage="")


def num(v):
    x = pd.to_numeric(v, errors="coerce")
    return None if pd.isna(x) else float(x)


def table_81(d, url, rec):
    head = [text(v) for v in d.iloc[2]]
    if head != ["Year"] + SOURCES:
        raise RuntimeError(f"8.1: headings {head}")
    out = []
    for _, r in d.iloc[3:].iterrows():
        y = text(r[0])
        if not re.fullmatch(r"\d{4}", y):
            continue
        for c, s in enumerate(SOURCES, 1):
            v = num(r[c])
            if v is not None:
                out.append(row(f"eia_epa:heat_rate:{slug(s)}", "heat_rate", y, v / 1000, "MMBtu/MWh", f"{s}, average operating heat rate", url, rec))
    return out


def table_82(d, url, rec):
    head = [text(v) for v in d.iloc[2]]
    if head != ["Prime Mover"] + SOURCES:
        raise RuntimeError(f"8.2: headings {head}")
    out, year = [], None
    for _, r in d.iloc[3:].iterrows():
        a = text(r[0])
        if re.fullmatch(r"\d{4}", a):
            year = a
            continue
        if a in MOVERS and year:
            for c, s in enumerate(SOURCES, 1):
                v = num(r[c])
                if v is not None:
                    out.append(row(f"eia_epa:tested_heat_rate:{slug(a)}:{slug(s)}", "tested_heat_rate", year, v / 1000, "MMBtu/MWh",
                                   f"{a}, {s}, average tested heat rate", url, rec))
        elif a and not a.startswith("Note") and year:
            raise RuntimeError(f"8.2: a line not in the form read: {a!r}")
    return out


def table_83(d, url, rec):
    out, years, path = [], {}, []
    for _, r in d.iterrows():
        raw = str(r[0]) if not (isinstance(r[0], float) and pd.isna(r[0])) else ""
        label = text(raw).lstrip(".").strip()
        if label == "Description":
            years = {c: text(r[c]) for c in range(1, d.shape[1]) if re.fullmatch(r"\d{4}", text(r[c]))}
            path = []
            continue
        if not years or not label or label.startswith("Notes") or label.startswith("Total may"):
            continue
        depth = (len(raw) - len(raw.lstrip("."))) // 6
        path = path[:depth] + [slug(label)]
        for c, y in years.items():
            v = num(r[c])
            if v is not None:
                out.append(row(f"eia_epa:iou_finance:{'.'.join(path)}", "amount", y, v * 1e6, "USD", label, url, rec))
    return out


def table_84(d, url, rec):
    """Two blocks (operation and maintenance, then fuel and total), each a row of groups over a row of plant types."""
    kinds = {"Operation": "operation_expense", "Maintenance": "maintenance_expense", "Fuel": "fuel_expense", "Total": "total_expense"}
    out, r, blocks = [], 0, 0
    while r < len(d):
        if text(d.iloc[r, 0]) == "Year":
            groups, head = [text(v) for v in d.iloc[r - 1]], [text(v) for v in d.iloc[r]]
            if head[1:5] != PLANTS or head[5:9] != PLANTS or groups[1] not in kinds or groups[5] not in kinds:
                raise RuntimeError(f"8.4: headings {groups} {head}")
            blocks += 1
            k = r + 1
            while k < len(d) and re.fullmatch(r"\d{4}", text(d.iloc[k, 0])):
                y = text(d.iloc[k, 0])
                for c in range(1, 9):
                    v = num(d.iloc[k, c])
                    if v is None:
                        continue
                    kind = kinds[groups[1] if c <= 4 else groups[5]]
                    p = PLANTS[(c - 1) % 4]
                    out.append(row(f"eia_epa:iou_plant_expense:{slug(p)}", kind, y, v, "USD/MWh", f"{p}, {kind.replace('_', ' ')}", url, rec))
                k += 1
            r = k
        else:
            r += 1
    if blocks != 2:
        raise RuntimeError(f"8.4: {blocks} blocks, not 2")
    return out


def main(argv=None):
    ap = argparse.ArgumentParser(description="EIA's Electric Power Annual, chapter 8: heat rates and operating costs")
    ap.add_argument("--offline", action="store_true", help="the saved workbooks only, no request")
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
        rows, got = [], []
        for k, fn in (("01", table_81), ("02", table_82), ("03", table_83), ("04", table_84)):
            url = f"{PAGE}xls/epa_08_{k}.xlsx"
            content, rec = ip.fetch_raw(CONNECTOR, url, log, offline=args.offline, headers=UA, timeout=120)
            got_rows = fn(pd.read_excel(io.BytesIO(content), header=None), url, rec.get("retrieved_at") or "")
            log(f"table 8.{int(k)}: {len(got_rows):,} rows")
            rows += got_rows
            got.append(f"{url} (retrieved {rec.get('retrieved_at', '')})")
        s = pd.DataFrame(rows)
        if s.duplicated(["entity", "variable", "ts_utc"]).any():
            raise RuntimeError(f"a key given twice: {s.loc[s.duplicated(['entity', 'variable', 'ts_utc']), 'entity'].head(3).tolist()}")
        s = s[ip.SERIES_COLS].sort_values(["entity", "variable", "ts_utc"]).reset_index(drop=True)
        header = [
            "Energy Research Warehouse (ERW): EIA, Electric Power Annual chapter 8, heat rates, investor-owned utilities' revenue and expenses, and power plant operating expenses (session 903)",
            "Shape: series (docs/datastandard.md v0). entity eia_epa:heat_rate:<source>, eia_epa:tested_heat_rate:<prime mover>:<source>, eia_epa:iou_finance:<line path>, "
            "eia_epa:iou_plant_expense:<plant type>; variables heat_rate and tested_heat_rate (MMBtu/MWh, EIA's Btu per kWh divided by 1,000), amount (USD, EIA's million "
            "dollars times 1,000,000), operation_expense, maintenance_expense, fuel_expense and total_expense (USD/MWh, EIA's mills per kWh); ts_utc the year's 1 January; freq P1Y; geo US.",
            f"Years {s['ts_utc'].min()[:4]} to {s['ts_utc'].max()[:4]}; {len(s):,} rows. W (withheld) and -- have no row; nothing is filled. Table 8.3's lines are a "
            "hierarchy (a sum takes one level; EIA notes its subtotals may be slightly out).",
            f"Retrieved: {run_id} (UTC) by warehouse/connectors/eia_epa_costs.py",
            f"Run log: warehouse/output/logs/{CONNECTOR}_{run_id}.log",
            f"Raw files: warehouse/raw/{CONNECTOR}/ (not in git)",
            f"Source: {SOURCE} U.S. Energy Information Administration, Electric Power Annual, tables 8.1 to 8.4, {PAGE}",
            f"  access: {'; '.join(got)}",
            'License: public (a work of the U.S. government; cite "U.S. Energy Information Administration, Electric Power Annual").',
        ]
        ip.write_snapshot(s, NAME, header, log, ip.SERIES_COLS)
        if not args.out_dir:
            ip.update_sources([dict(source=SOURCE, publisher="U.S. Energy Information Administration (EIA)",
                                    report="Electric Power Annual, chapter 8 (heat rates, revenue and expenses)", report_url=PAGE,
                                    document_list=PAGE, license="public", tables=[NAME])])
        results.append(dict(table=NAME, market="all", status="ok", detail=f"{len(s):,} rows"))
        print(f"{NAME}: {len(s):,} rows")
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

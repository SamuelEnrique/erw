#!/usr/bin/env python3
"""Berkeley Lab's wind turbine prices and project costs: the reported U.S. turbine orders, the turbine makers' and LBNL's
average turbine prices, the capacity-weighted installed cost and the generation-weighted levelized cost of the projects
of each commercial operation year (session 952, chain 054: the cost side of lbnl_ppa_prices and
lbnl_wind_capacity_factors, from the same data file).

Energy Research Warehouse (ERW) connector. Two tables from LBNL's Land-Based Wind Energy Technology Data Update, 2026
Edition, the data file lbnl_ppa_prices.py saves (warehouse/raw/lbnl_ppa_prices/), read again from there:

    https://eta-publications.lbl.gov/sites/default/files/2026-08/data_file_land-based_wind_energy_technology_update_2026_edition_public_0.xlsx

    lbnl_wind_costs          series, real 2025 USD: entity lbnl_wind_cost:<what>:<whose>
                             turbine_price (USD/kW): vestas, sgre and nordex (the makers' global averages, at LBNL's
                               mid-year dates) and lbnl (LBNL's average turbine price, a year), sheet "Wind Turbine Prices"
                             capex (USD/kW): the capacity-weighted installed cost of the year's projects, sheet "CapEx Over
                               Time"; a year LBNL gives a sample but no cost has no row
                             lcoe (USD/MWh): the generation-weighted levelized cost, sheet "Wind LCOE Over Time"
                             x_sample (projects), x_sample_mw (LCOE only), x_dollar_year 2025
    lbnl_wind_turbine_orders events: one row a reported U.S. turbine order (LBNL names no buyer or maker): event_id
                             lbnl_turbine_order:<12 hex of the date and price>; event_date the order date; event_type
                             turbine_order; price (USD/kW, real 2025); currency USD

Not taken: "Recent CapEx by Region" (the sheet does not say which years' projects it averages) and "O&M Over Time" (a
project's average O&M cost with no project and no date, some points suppressed by LBNL). A heading not as read stops the
run; nothing is filled.

    python warehouse/connectors/lbnl_wind_costs.py [--offline] [--table NAME]

Ceiling: one request, and none while lbnl_ppa_prices' saved file is on the machine. License: CC BY 4.0, as the file's
copyright notice states; cite Berkeley Lab.
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

CONNECTOR = "lbnl_wind_costs"
SAVED_BY = "lbnl_ppa_prices"
SOURCE = "lbnl:wind_costs"
PAGE = "https://eta-publications.lbl.gov/publications/land-based-wind-energy-technology-0"
URL = "https://eta-publications.lbl.gov/sites/default/files/2026-08/data_file_land-based_wind_energy_technology_update_2026_edition_public_0.xlsx"
UA = {"User-Agent": "Mozilla/5.0 (compatible; ERW-connector/0.1; +https://github.com/SamuelEnrique/erw)"}
COSTS, ORDERS = "lbnl_wind_costs", "lbnl_wind_turbine_orders"
COST_X = ["x_sample", "x_sample_mw", "x_dollar_year"]
EVENT_COLS = ["event_id", "event_date", "event_type", "parties", "entity_ids", "mw", "price", "currency", "status", "source",
              "source_url", "retrieved_at", "x_price_unit", "x_dollar_year"]
# the turbine price sheet's blocks: (heading row 23's text, the date column, the price column, the entity's last part)
TURBINE_BLOCKS = [("Vestas global average", 3, 4, "vestas"), ("SGRE global average", 5, 6, "sgre"),
                  ("Nordex global average", 7, 8, "nordex"), ("Average Turbine Price", 11, 12, "lbnl")]


def text(v):
    return "" if v is None or (isinstance(v, float) and pd.isna(v)) else re.sub(r"\s+", " ", str(v)).strip()


def num(v):
    x = pd.to_numeric(v, errors="coerce")
    return None if pd.isna(x) else float(x)


def year_ts(v):
    y = int(float(v))
    return f"{y}-01-01T00:00:00Z"


def turbine(frame, base):
    if text(frame.iloc[23, 0]) != "U.S. turbine orders" or text(frame.iloc[24, 0]) != "Order Date" or text(frame.iloc[24, 1]) != "(2025 $/kW)":
        raise RuntimeError("Wind Turbine Prices: the orders' headings are not as read")
    series, orders = [], []
    for head, dc, pc, who in TURBINE_BLOCKS:
        if text(frame.iloc[23, dc]) != head or text(frame.iloc[24, dc]) != "(2025 $/kW)":
            raise RuntimeError(f"Wind Turbine Prices: the block {head!r} is not as read")
        for i in range(25, len(frame)):
            d, p = frame.iloc[i, dc], num(frame.iloc[i, pc])
            if p is None:
                continue
            if who == "lbnl":
                ts = year_ts(d)
            else:
                ts = pd.Timestamp(d).strftime("%Y-%m-%dT00:00:00Z")
            series.append(dict(base, entity=f"lbnl_wind_cost:turbine_price:{who}", variable="turbine_price", ts_utc=ts, value=p,
                               unit="USD/kW", freq="P1Y", geo="US" if who == "lbnl" else "", market="",
                               node=head.strip(), x_sample="", x_sample_mw="", x_dollar_year=2025))
    seen = {}
    for i in range(25, len(frame)):
        d, p = frame.iloc[i, 0], num(frame.iloc[i, 1])
        if p is None:
            continue
        day = pd.Timestamp(d).strftime("%Y-%m-%d")
        h = hashlib.sha1(f"{day}|{p:.6f}".encode()).hexdigest()[:12]
        seen[h] = seen.get(h, 0) + 1
        orders.append(dict(event_id=f"lbnl_turbine_order:{h}" + (f"-{seen[h]}" if seen[h] > 1 else ""), event_date=day,
                           event_type="turbine_order", parties="", entity_ids="", mw="", price=round(p, 4), currency="USD", status="",
                           source=base["source"], source_url=base["source_url"], retrieved_at=base["retrieved_at"],
                           x_price_unit="USD/kW, real 2025 dollars", x_dollar_year=2025))
    return series, orders


def by_year(frame, base, sheet, heads, variable, unit, with_mw):
    h = None
    for i in range(min(40, len(frame))):
        if text(frame.iloc[i, 0]) == "Commercial Operation Date":
            h = i
            break
    if h is None or [text(frame.iloc[h, j]) for j in range(len(heads))] != heads:
        raise RuntimeError(f"{sheet}: headings not as read")
    out = []
    for i in range(h + 1, len(frame)):
        y, v = frame.iloc[i, 0], num(frame.iloc[i, 1])
        if text(y) == "" or v is None:
            continue
        n = num(frame.iloc[i, 2])
        out.append(dict(base, entity=f"lbnl_wind_cost:{variable}:us", variable=variable, ts_utc=year_ts(y), value=v, unit=unit, freq="P1Y",
                        geo="US", market="", node=f"projects of COD {int(float(y))}",
                        x_sample="" if n is None else int(n), x_sample_mw=num(frame.iloc[i, 3]) if with_mw else "", x_dollar_year=2025))
    return out


def build(content, base):
    x = pd.ExcelFile(io.BytesIO(content))
    series, orders = turbine(pd.read_excel(x, sheet_name="Wind Turbine Prices", header=None), base)
    series += by_year(pd.read_excel(x, sheet_name="CapEx Over Time", header=None), base, "CapEx Over Time",
                      ["Commercial Operation Date", "Capacity-Weighted Average Cost (2025$/kW)", "Annual Cost Sample"], "capex", "USD/kW", False)
    series += by_year(pd.read_excel(x, sheet_name="Wind LCOE Over Time", header=None), base, "Wind LCOE Over Time",
                      ["Commercial Operation Date", "Generation-Weighted Levelized Cost (2025$/MWh)", "Annual LCOE Sample (# projects)",
                       "Annual LCOE Sample (annual MW)"], "lcoe", "USD/MWh", True)
    s = pd.DataFrame(series)
    if s.duplicated(["entity", "variable", "ts_utc"]).any():
        raise RuntimeError("an (entity, variable, ts_utc) given twice")
    o = pd.DataFrame(orders)
    if o.event_id.duplicated().any():
        raise RuntimeError("an order id given twice")
    return s, o


def main(argv=None):
    ap = argparse.ArgumentParser(description="Berkeley Lab's wind turbine prices and project costs")
    ap.add_argument("--offline", action="store_true", help="the saved data file only, no request")
    ap.add_argument("--out-dir", help="a trial: the tables under this folder, not warehouse/output")
    ap.add_argument("--table", choices=[COSTS, ORDERS], action="append", help="the table(s) to write (default both)")
    args = ap.parse_args(argv)
    if args.out_dir:
        raw_dir = ip.RAW_DIR
        ip.set_out_dir(args.out_dir)
        ip.RAW_DIR = raw_dir
    os.makedirs(ip.LOG_DIR, exist_ok=True)
    run_id = dt.datetime.now(dt.timezone.utc).strftime("%Y%m%dT%H%M%SZ")
    log = ip.Log(os.path.join(ip.LOG_DIR, f"{CONNECTOR}_{run_id}.log"))
    ip.RAW.open(CONNECTOR, run_id)
    results, names = [], args.table or [COSTS, ORDERS]
    try:
        hit = ip.raw_cached(SAVED_BY, URL) or ip.raw_cached(CONNECTOR, URL)
        if hit:
            content, rec = hit
            log(f"  saved file reused: {rec['file']}")
        else:
            content, rec = ip.fetch_raw(CONNECTOR, URL, log, offline=args.offline, headers=UA, timeout=600)
        if content[:2] != b"PK":
            raise RuntimeError(f"{URL} is not a workbook")
        base = dict(source=SOURCE, source_url=URL, retrieved_at=rec.get("retrieved_at") or "", vintage=ip.vintage_of(rec))
        s, o = build(content, base)
        common = [
            f"Retrieved: {run_id} (UTC) by warehouse/connectors/lbnl_wind_costs.py; the data file retrieved {base['retrieved_at']}",
            f"Run log: warehouse/output/logs/{CONNECTOR}_{run_id}.log",
            f"Raw files: warehouse/raw/{SAVED_BY}/ (not in git; the file lbnl_ppa_prices.py saves)",
            f"Source: {SOURCE} Lawrence Berkeley National Laboratory, Land-Based Wind Energy Technology Data Update, 2026 Edition (August 2026), {PAGE}",
            f"  access: {URL}",
            "License: CC BY 4.0, as the data file's copyright notice states; cite Berkeley Lab and the report.",
        ]
        if COSTS in names:
            cols = ip.SERIES_COLS + COST_X
            s = s[cols].sort_values(["entity", "ts_utc"]).reset_index(drop=True)
            k = s.groupby("variable").size().to_dict()
            header = [
                "Energy Research Warehouse (ERW): Berkeley Lab, wind turbine prices, installed project costs and levelized costs by commercial operation year, real 2025 dollars (Land-Based Wind Energy Technology Data Update, 2026 Edition) (session 952)",
                "Shape: series (docs/datastandard.md v0). entity lbnl_wind_cost:<turbine_price|capex|lcoe>:<vestas|sgre|nordex|lbnl|us>; turbine_price "
                "(USD/kW: the makers' global averages at LBNL's mid-year dates, geo empty; LBNL's average a year, geo US); capex (USD/kW, capacity-weighted, "
                "the projects of the COD year); lcoe (USD/MWh, generation-weighted); freq P1Y; x_sample the projects, x_sample_mw the LCOE sample's MW.",
                f"Rows: {', '.join(f'{v} {n}' for n, v in k.items())}. A year LBNL gives a sample but no cost has no row; the regional costs (no years "
                "given) and the O&M points (no project, no date) are not taken. EIA's 2024 and 2025 cost estimates are preliminary, as LBNL notes. Nothing is filled.",
            ] + common
            ip.write_snapshot(s, COSTS, header, log, cols)
            results.append(dict(table=COSTS, market="all", status="ok", detail=f"{len(s):,} rows"))
            print(f"{COSTS}: {len(s):,} rows {k}")
        if ORDERS in names:
            o = o[EVENT_COLS].sort_values(["event_date", "event_id"]).reset_index(drop=True)
            header = [
                "Energy Research Warehouse (ERW): Berkeley Lab, reported U.S. wind turbine orders and their prices, real 2025 dollars (Land-Based Wind Energy Technology Data Update, 2026 Edition, sheet 'Wind Turbine Prices') (session 952)",
                "Shape: events (docs/datastandard.md v0). event_id lbnl_turbine_order:<12 hex of the date and price>; event_date the order date; "
                "event_type turbine_order; price USD/kW (real 2025); currency USD; LBNL names no buyer, maker or size.",
                f"{len(o)} orders from {o.event_date.min()} to {o.event_date.max()}; median {o.price.median():,.0f} USD/kW. Nothing is filled.",
            ] + common
            ip.write_snapshot(o, ORDERS, header, log, EVENT_COLS)
            results.append(dict(table=ORDERS, market="all", status="ok", detail=f"{len(o)} orders"))
            print(f"{ORDERS}: {len(o)} orders")
        if not args.out_dir:
            ip.update_sources([dict(source=SOURCE, publisher="Lawrence Berkeley National Laboratory (Berkeley Lab)",
                                    report="Land-Based Wind Energy Technology Data Update (turbine prices, CapEx, LCOE)", report_url=PAGE,
                                    document_list=URL, license="public", tables=[r["table"] for r in results])])
    except Exception:
        tb = ip.redact(traceback.format_exc())
        log(f"FAILED, no output file written:\n{tb}")
        print(f"{CONNECTOR} FAILED, no output file written: {tb.strip().splitlines()[-1]}", file=sys.stderr)
        results.append(dict(table=",".join(names), market="all", status="failed", detail=tb.strip().splitlines()[-1][:300]))
    if not args.out_dir:
        ip.write_status(CONNECTOR, run_id, results)
    log.close()
    return 0 if all(r["status"] == "ok" for r in results) else 1


if __name__ == "__main__":
    sys.exit(main())

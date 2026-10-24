#!/usr/bin/env python3
"""Saint Lucia's electricity, a year, 2010 to 2023: units generated or purchased, sales by class, internal use, losses
and the available capacity, as the Central Statistical Office of Saint Lucia (CSO) gives them in its table "Electricity
Output and Consumption in Kilowatt Hours (KWh) Thousands, 2010 to 2023", from St. Lucia Electricity Services Limited's
(LUCELEC) figures (session 2497, chain 121).

Energy Research Warehouse (ERW) connector. One series table, warehouse/output/slu_cso_electricity_annual.csv, from one
web page (no key):

    https://stats.gov.lc/subjects/sectors/water-and-electricity/electricity-output-and-consumption-in-kilowatt-hours-kwh-thousands-2010-to-2023/

The page's HTML table is read row by row, a row a label and fourteen years.

    row (as the CSO labels it)                         variable            entity slu_cso:lc:<item>       unit
    Total Generated (Units generated/purchases)        generation          total                      MWh
    Sales (kWh x 1000): Commercial Use, Domestic Use,  sales               commercial_excl_hotels or  MWh
      Hotel Use, Industrial Use, Street Lighting,                          commercial_incl_hotels,
      Total Sales                                                          domestic, hotels, industrial,
                                                                           street_lighting, total
    Internal Use                                       own_use             total                      MWh
    Loss of transmission                               losses              total                      MWh
    Available Capacity (kW)                            available_capacity  total                      MW

Thousands of kWh are MWh. The commercial row's figures marked "*" include hotels ("* Includes hotels"; 2013 on), those
without exclude them (2010 to 2012): the two are written as two entities, so a sum over classes never counts hotels
twice by accident; the hotel row is the hotels' own use either way. The available capacity is in kW, as the CSO's
2011 to 2017 table heads it ("Maximum Installed Capacity of Plants (KW)"), divided by 1,000. A cell ".." has no row. A
cell not in the form of the table (2016's commercial "194,66*") has no row and is counted in the header. The consumers'
numbers, the growth and loss percentages, the averages per customer and the diesel burned (imperial gallons) are not
taken. A page without the table, a header other than the years 2010 to 2023, a row of another width, or a key given twice
stops the run. Nothing is filled.

    python warehouse/connectors/slu_cso_electricity.py [--offline] [--out-dir DIR]

Ceiling: one request a run, saved in warehouse/raw/slu_cso_electricity/ and reused unless --fresh; --offline asks
nothing. stats.gov.lc's robots file disallows nothing (session 2497). License: internal. The CSO's Open Licence Agreement
grants a worldwide, royalty-free licence for commercial and non-commercial use of its information, but "is limited
solely to CSO data and shall not extend to any third party data"; these figures are LUCELEC's ("Source: St. Lucia
Electricity Services Limited (LUCELEC)"), and LUCELEC's site reads "Copyright (c) 2025 St. Lucia Electricity Services
Limited. All Rights Reserved." with no grant of reuse.
"""

import argparse
import datetime as dt
import html
import os
import re
import sys
import traceback

import pandas as pd

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import iso_prices as ip  # noqa: E402

NAME = "slu_cso_electricity_annual"
CONNECTOR = "slu_cso_electricity"
SOURCE = "slu_cso:electricity_output_consumption"
SOURCE_LUCELEC = "lucelec:electricity_output_consumption"
HOST = "stats.gov.lc"
URL = ("https://stats.gov.lc/subjects/sectors/water-and-electricity/"
       "electricity-output-and-consumption-in-kilowatt-hours-kwh-thousands-2010-to-2023/")
UA = {"User-Agent": "Mozilla/5.0 (compatible; ERW-connector/0.1; +https://github.com/SamuelEnrique/erw)"}
YEARS = [str(y) for y in range(2010, 2024)]
# the row's label -> (variable, item, unit, factor); item None: the commercial row, whose item follows its "*"
ROWS = {
    "Total Generated (Units generated/purchases (kWhx1000))": ("generation", "total", "MWh", 1.0),
    "Commercial Use (including Hotels)": ("sales", None, "MWh", 1.0),
    "Domestic Use": ("sales", "domestic", "MWh", 1.0),
    "Hotel Use": ("sales", "hotels", "MWh", 1.0),
    "Industrial Use": ("sales", "industrial", "MWh", 1.0),
    "Street Lighting": ("sales", "street_lighting", "MWh", 1.0),
    "Total Sales": ("sales", "total", "MWh", 1.0),
    "Internal Use": ("own_use", "total", "MWh", 1.0),
    "Loss of transmission": ("losses", "total", "MWh", 1.0),
    "Available Capacity": ("available_capacity", "total", "MW", 0.001),
}
FORM = r"\d{1,3}(,\d{3})+|\d+"
X_COLS = ["x_label"]


def table_rows(page):
    i = page.find("<table")
    if i < 0:
        raise RuntimeError("no table on the page")
    tb = page[i:page.find("</table>", i)]
    out = []
    for r in re.findall(r"(?s)<tr.*?</tr>", tb):
        cells = re.findall(r"(?s)<t[dh][^>]*>(.*?)</t[dh]>", r)
        out.append([html.unescape(re.sub(r"\s+", " ", re.sub(r"<[^>]+>", " ", c))).strip() for c in cells])
    return out


def parse_rows(rows, base, counts):
    if not rows or rows[0][1:] != YEARS:
        raise RuntimeError(f"a header other than the years 2010 to 2023: {rows[0][:4] if rows else None}")
    out, seen, section = [], set(), None
    for r in rows[1:]:
        if len(r) != len(YEARS) + 1:
            raise RuntimeError(f"a row of {len(r)} cells: {r[:2]}")
        label = r[0]
        if label.startswith("Sales"):
            section = "sales"
        elif label.startswith("Average Annual Consumption"):
            section = "average"
        if label not in ROWS or (section == "average" and label.startswith("Commercial")):
            continue
        var, item, unit, factor = ROWS[label]
        for year, cell in zip(YEARS, r[1:]):
            if not cell or cell == "..":
                continue
            star = cell.endswith("*")
            num = cell.rstrip("*")
            if not re.fullmatch(FORM, num):
                counts["cells out of form"] = counts.get("cells out of form", 0) + 1
                continue
            it = item or ("commercial_incl_hotels" if star else "commercial_excl_hotels")
            key = (it, var, year)
            if key in seen:
                raise RuntimeError(f"{key} given twice")
            seen.add(key)
            node = label + (" *" if star else "")
            out.append(dict(entity=f"slu_cso:lc:{it}", variable=var, ts_utc=f"{year}-01-01T00:00:00Z",
                            value=round(float(num.replace(",", "")) * factor, 3), unit=unit, freq="P1Y", geo="LC", market="",
                            node=node, **base, x_label=node))
    t = pd.DataFrame(out)
    if t.empty or not (t.variable == "generation").any() or not (t.variable == "sales").any():
        raise RuntimeError("no generation or sales row")
    return t


def main(argv=None):
    ap = argparse.ArgumentParser(description="Saint Lucia's CSO: electricity output and consumption, 2010 to 2023")
    ap.add_argument("--offline", action="store_true", help="the saved page only, no request")
    ap.add_argument("--fresh", action="store_true", help="ask for the page again")
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
        content, rec = ip.fetch_raw(CONNECTOR, URL, log, offline=args.offline, fresh=args.fresh, headers=UA, timeout=120, pause=1)
        base = dict(source=SOURCE, source_url=URL, retrieved_at=rec.get("retrieved_at") or "", vintage=ip.vintage_of(rec))
        counts = {}
        t = parse_rows(table_rows(content.decode("utf-8", errors="replace")), base, counts)
        cols = ip.SERIES_COLS + X_COLS
        t = t[cols].sort_values(["variable", "entity", "ts_utc"]).reset_index(drop=True)
        g = t[t.variable == "generation"].set_index("ts_utc").value / 1e3
        head = [
            "Energy Research Warehouse (ERW): Central Statistical Office of Saint Lucia (CSO), Electricity Output and Consumption in Kilowatt Hours (KWh) "
            f"Thousands, {t.ts_utc.min()[:4]} to {t.ts_utc.max()[:4]}, from St. Lucia Electricity Services Limited (LUCELEC) (session 2497)",
            "Shape: series (docs/datastandard.md v0). entity slu_cso:lc:<item>; variable generation (units generated or purchased), sales (by class), own_use, "
            "losses (MWh, the CSO's thousands of kWh), available_capacity (MW, from kW); ts_utc the year's 1 January; freq P1Y; geo LC; node the CSO's row label, "
            "* where the CSO marks a commercial figure that includes hotels (commercial_incl_hotels; without it, commercial_excl_hotels).",
            f"{len(t)} rows; generation GWh: " + ", ".join(f"{k[:4]} {v:.1f}" for k, v in g.items() if k[:4] in ("2010", "2019", "2020", "2023"))
            + f". Not taken: cells .. (no row), cells out of form {counts.get('cells out of form', 0)}, consumers, percentages, averages per customer, diesel. Nothing is filled.",
            f"Retrieved: {run_id} (UTC) by warehouse/connectors/slu_cso_electricity.py; the page retrieved {base['retrieved_at']}",
            f"Run log: warehouse/output/logs/{CONNECTOR}_{run_id}.log",
            f"Raw files: warehouse/raw/{CONNECTOR}/ (not in git)",
            f"Source: {SOURCE} CSO Saint Lucia, Electricity Output and Consumption in Kilowatt Hours (KWh) Thousands, 2010 to 2023 (Source: LUCELEC)",
            f"  access: {URL}",
            "License: internal (the CSO's Open Licence Agreement covers CSO data only, not third-party data; LUCELEC's site reserves all rights).",
        ]
        ip.write_snapshot(t, NAME, head, log, cols)
        results.append(dict(table=NAME, market="all", status="ok", detail=f"{len(t)} rows"))
        print(f"{NAME}: {len(t)} rows, {t.entity.nunique()} entities; {counts}")
    except Exception:
        tb = ip.redact(traceback.format_exc())
        log(f"{NAME} FAILED, no output file written:\n{tb}")
        print(f"{NAME} FAILED, no output file written: {tb.strip().splitlines()[-1]}", file=sys.stderr)
        results.append(dict(table=NAME, market="all", status="failed", detail=tb.strip().splitlines()[-1][:300]))
    if not args.out_dir:
        if results and results[0]["status"] == "ok":
            ip.update_sources([
                dict(source=SOURCE, publisher="Central Statistical Office of Saint Lucia (CSO)",
                     report="Electricity Output and Consumption in Kilowatt Hours (KWh) Thousands, 2010 to 2023", report_url=URL,
                     document_list="https://stats.gov.lc/subjects/sectors/water-and-electricity/", license="internal", tables=[NAME]),
                dict(source=SOURCE_LUCELEC, publisher="St. Lucia Electricity Services Limited (LUCELEC)",
                     report="LUCELEC's figures as the CSO of Saint Lucia publishes them (2010 to 2023)", report_url=URL,
                     document_list="https://www.lucelec.com/", license="internal", tables=[NAME])])
        ip.write_status(CONNECTOR, run_id, results)
    log.close()
    return 0 if all(r["status"] == "ok" for r in results) else 1


if __name__ == "__main__":
    sys.exit(main())

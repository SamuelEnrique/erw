#!/usr/bin/env python3
"""Grenada's electricity, a year, 2000 to 2023: the volume produced and the volume consumed by category (domestic,
commercial, industrial, street lights), as the Central Statistical Office of Grenada (CSO) gives them in its table
"Production and Consumption of Electricity by Category, 2000 to 2023" (session 2496, chain 121).

Energy Research Warehouse (ERW) connector. One series table, warehouse/output/grenada_cso_electricity_annual.csv, from
one web page (no key):

    https://stats.gov.gd/subjects/energy/production-and-consumption-of-electricity-by-category-2000-to-2023/

The page's HTML table is read row by row: a header of the years, the production row, then the section "Electricity
Consumption, Volume (thousands of KWH)" with a row a category and its total. The section "Value (EC$ thousands)" (East
Caribbean dollars) is not taken.

    entity      grenada_cso:gd:<item> (total; domestic, commercial, industrial, street_lights)
    variable    generation (the volume produced) or consumption
    unit        MWh (thousands of kWh, the same quantity)
    ts_utc      the year's 1 January; freq P1Y; geo GD
    node        the row as the CSO labels it

The page writes some figures without thousands separators (2021 to 2023's consumption) or with two decimals: each is
read as the number it prints. A cell empty has no row. A page without the table, a header other than the years 2000 to
2023, a row of another width, a row not in the map, or a key given twice stops the run. Nothing is filled. The
consumption total is written as printed; its difference from the categories' sum goes in the header.

    python warehouse/connectors/grenada_cso_electricity.py [--offline] [--out-dir DIR]

Ceiling: one request a run, saved in warehouse/raw/grenada_cso_electricity/ and reused unless --fresh; --offline asks
nothing. stats.gov.gd's robots file disallows nothing (session 2496). License: not settled. The site's terms: "The
materials located on this website, including the information ... are protected by copyright"; "Access and use of the
Data is subject to the requirements set forth under the Open Licence Agreement", whose page on 24 October 2026 had no
text. Internal until the licence is read or a ruling.
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

NAME = "grenada_cso_electricity_annual"
CONNECTOR = "grenada_cso_electricity"
SOURCE = "grenada_cso:electricity_by_category"
HOST = "stats.gov.gd"
URL = "https://stats.gov.gd/subjects/energy/production-and-consumption-of-electricity-by-category-2000-to-2023/"
UA = {"User-Agent": "Mozilla/5.0 (compatible; ERW-connector/0.1; +https://github.com/SamuelEnrique/erw)"}
YEARS = [str(y) for y in range(2000, 2024)]
CATEGORIES = {"Domestic": "domestic", "Commercial": "commercial", "Industrial": "industrial", "Street Lights": "street_lights", "Total": "total"}
FORM = r"\d{1,3}(,\d{3})+(\.\d+)?|\d+(\.\d+)?"
X_COLS = ["x_label"]


def table_rows(page):
    """The page's first table as lists of cell texts."""
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
        raise RuntimeError(f"a header other than the years 2000 to 2023: {rows[0][:4] if rows else None}")
    out, seen, section = [], set(), None
    for r in rows[1:]:
        if len(r) != len(YEARS) + 1:
            raise RuntimeError(f"a row of {len(r)} cells: {r[:2]}")
        label = r[0]
        if label.startswith("Electricity Production Volume"):
            item, var = "total", "generation"
        elif label == "Electricity Consumption":
            section = r[1]
            continue
        elif label in CATEGORIES and section and section.startswith("Volume"):
            item, var = CATEGORIES[label], "consumption"
        elif label in CATEGORIES and section and section.startswith("Value"):
            continue
        else:
            raise RuntimeError(f"a row not in the map: {label!r} (section {section!r})")
        for year, cell in zip(YEARS, r[1:]):
            if not cell:
                continue
            if not re.fullmatch(FORM, cell):
                raise RuntimeError(f"{label} {year}: not a figure: {cell!r}")
            key = (item, var, year)
            if key in seen:
                raise RuntimeError(f"{key} given twice")
            seen.add(key)
            node = label if var == "generation" else f"Electricity Consumption Volume, {label}"
            out.append(dict(entity=f"grenada_cso:gd:{item}", variable=var, ts_utc=f"{year}-01-01T00:00:00Z", value=float(cell.replace(",", "")),
                            unit="MWh", freq="P1Y", geo="GD", market="", node=node, **base, x_label=node))
    t = pd.DataFrame(out)
    if t.empty or not (t.variable == "consumption").any():
        raise RuntimeError("no consumption section")
    c = t[t.variable == "consumption"].pivot_table(index="ts_utc", columns="entity", values="value")
    parts = c.drop(columns="grenada_cso:gd:total").sum(axis=1)
    counts["largest gap between the total and its categories, MWh"] = round(float((parts - c["grenada_cso:gd:total"]).abs().max()), 1)
    return t


def main(argv=None):
    ap = argparse.ArgumentParser(description="Grenada's CSO: electricity produced and consumed by category, 2000 to 2023")
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
            "Energy Research Warehouse (ERW): Central Statistical Office of Grenada (CSO), Production and Consumption of Electricity by Category, "
            f"{t.ts_utc.min()[:4]} to {t.ts_utc.max()[:4]} (session 2496)",
            "Shape: series (docs/datastandard.md v0). entity grenada_cso:gd:<item> (total; domestic, commercial, industrial, street_lights); variable generation "
            "(the volume produced) or consumption; unit MWh (the CSO's thousands of kWh); ts_utc the year's 1 January; freq P1Y; geo GD; node the CSO's row label.",
            f"{len(t)} rows; generation GWh: " + ", ".join(f"{k[:4]} {v:.1f}" for k, v in g.items() if k[:4] in ("2000", "2010", "2019", "2020", "2023"))
            + f". Largest gap between the consumption total and its categories: {counts.get('largest gap between the total and its categories, MWh')} MWh. "
            "Not taken: the consumption's value (EC$). Nothing is filled.",
            f"Retrieved: {run_id} (UTC) by warehouse/connectors/grenada_cso_electricity.py; the page retrieved {base['retrieved_at']}",
            f"Run log: warehouse/output/logs/{CONNECTOR}_{run_id}.log",
            f"Raw files: warehouse/raw/{CONNECTOR}/ (not in git)",
            f"Source: {SOURCE} CSO Grenada, Production and Consumption of Electricity by Category, 2000 to 2023",
            f"  access: {URL}",
            "License: internal (the site's terms: the contents are protected by copyright; the data's Open Licence Agreement page had no text when read).",
        ]
        ip.write_snapshot(t, NAME, head, log, cols)
        results.append(dict(table=NAME, market="all", status="ok", detail=f"{len(t)} rows"))
        print(f"{NAME}: {len(t)} rows; {counts}")
    except Exception:
        tb = ip.redact(traceback.format_exc())
        log(f"{NAME} FAILED, no output file written:\n{tb}")
        print(f"{NAME} FAILED, no output file written: {tb.strip().splitlines()[-1]}", file=sys.stderr)
        results.append(dict(table=NAME, market="all", status="failed", detail=tb.strip().splitlines()[-1][:300]))
    if not args.out_dir:
        if results and results[0]["status"] == "ok":
            ip.update_sources([dict(source=SOURCE, publisher="Central Statistical Office of Grenada (CSO)",
                                    report="Production and Consumption of Electricity by Category, 2000 to 2023", report_url=URL,
                                    document_list="https://stats.gov.gd/subjects/energy/", license="internal", tables=[NAME])])
        ip.write_status(CONNECTOR, run_id, results)
    log.close()
    return 0 if all(r["status"] == "ok" for r in results) else 1


if __name__ == "__main__":
    sys.exit(main())

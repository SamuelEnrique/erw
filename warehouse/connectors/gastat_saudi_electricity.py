#!/usr/bin/env python3
"""Saudi Arabia's electricity a year, as the General Authority for Statistics (GASTAT) gives it in its workbook
"Electrical Energy Statistics 2024" (Arabic edition), each table's source the Ministry of Energy: licensed generation
capacity in total and by type of unit, peak load in total and by the Saudi Electricity Company's four business areas,
the electrical energy sent to the network and the energy consumed (2010 to 2024), consumption by category (2021 to 2024),
and the energy sold in 2024 by administrative region and category (session 2552, chain 125: a source of the session's own
choosing; the ERW held Saudi Arabia only in EIA's and OWID's international tables).

Energy Research Warehouse (ERW) connector. One series table, warehouse/output/gastat_saudi_electricity_annual.csv, from one
workbook (no key), listed on GASTAT's "Electrical energy statistics" tab:

    https://www.stats.gov.sa/documents/20117/2435281/Electrical_Energy_Statistics_2024_AR.xlsx_fixed_9794353/b763f431-ab03-cf1d-4a14-eec2fe2f6ef4

Sheets 1 to 8 are read, each found by its name and checked by words of its title; a sheet's columns are found by words
of their headers, its rows by their year (or, in sheet 7, by the region's name):

    1  licensed_capacity, total                        GW, 2019 to 2024
    2  licensed_capacity by type of unit                steam, gas, combined_cycle, diesel, renewable
    3  peak_load, total                                 GW
    4  peak_load by business area                       central, eastern, western, southern (the Saudi Electricity Company's)
    5  energy_sent_out, total                           GWh, 2010 to 2024
    6  energy_consumed, total                           GWh (sales: no internal loads, no energy passed through the grid)
    7  sales_<category> by administrative region, 2024 residential, commercial, government, industrial, other
    8  consumption by category, 2021 to 2024             residential, commercial, government, industrial, other (the
                                                         transmission company's interconnected system only)

    entity      gastat:sa:<item>: total; a type of unit; a business area; a category; a region (riyadh, makkah, madinah,
                qassim, eastern_province, asir, tabuk, hail, northern_borders, jazan, najran, bahah, jawf)
    unit        MW (capacity and peak load: GW times 1,000) or MWh (energy: GWh times 1,000); ts_utc the year's first day;
                freq P1Y; geo SA
    node        GASTAT's Arabic label; x_approx true where GASTAT marks the figure with an approximation sign

The run stops on a sheet or a column not found, a row of another form, a figure that is not a number, a key given twice,
a region not in the map, or a year whose consumption by category differs from the energy consumed by more than 1 GWh
(2024: 340,430 GWh both). Nothing is filled. Prices, the loss rate and the counts of consumers are not taken.

    python warehouse/connectors/gastat_saudi_electricity.py [--offline] [--fresh] [--out-dir DIR]

Ceiling: one request a run, saved in warehouse/raw/gastat_sa/ and reused unless --fresh; --offline asks nothing.
www.stats.gov.sa's robots file closes /api/, /c/portal/ and /o/ (session 2552). License: internal. GASTAT's use policy
(1.2.2) allows reuse "for any purpose, including commercial use", GASTAT acknowledged and changes indicated, "except for
trademarks, logos, and any clearly identified third-party material"; each of these tables names the Ministry of Energy as
its source. Internal until a ruling.
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

NAME = "gastat_saudi_electricity_annual"
CONNECTOR = "gastat_sa"
SOURCE = "gastat:electrical_energy_statistics_2024"
HOST = "www.stats.gov.sa"
URL = ("https://www.stats.gov.sa/documents/20117/2435281/Electrical_Energy_Statistics_2024_AR.xlsx_fixed_9794353/"
       "b763f431-ab03-cf1d-4a14-eec2fe2f6ef4?t=1765087564219")
LIST = "https://www.stats.gov.sa/statistics-tabs?tab=436312&category=124767"
UA = {"User-Agent": "Mozilla/5.0 (compatible; ERW-connector/0.1; +https://github.com/SamuelEnrique/erw)"}
CITATION = ("General Authority for Statistics (GASTAT), Saudi Arabia, Electrical Energy Statistics 2024 (Arabic edition), tables 1 "
            "to 8, source the Ministry of Energy")
APPROX = chr(0x2248)
# sheet: (words its title must hold, variable, unit, scale, columns as (header words, item); one column with no words: total)
SHEETS = {
    "1": (["سعات توليد"], "licensed_capacity", "MW", 1000, [(None, "total")]),
    "2": (["نوع الوحدة"], "licensed_capacity", "MW", 1000,
          [("بخارية", "steam"), ("غازية", "gas"),
           ("دورة مركبة", "combined_cycle"), ("ديزل", "diesel"),
           ("المتجددة", "renewable")]),
    "3": (["الحمل الذروي"], "peak_load", "MW", 1000, [(None, "total")]),
    "4": (["مناطق الأعمال"], "peak_load", "MW", 1000,
          [("الوسطى", "central"), ("الشرقية", "eastern"),
           ("الغربية", "western"), ("الجنوبية", "southern")]),
    "5": (["المرسلة"], "energy_sent_out", "MWh", 1000, [(None, "total")]),
    "6": (["المستهلكة"], "energy_consumed", "MWh", 1000, [(None, "total")]),
    "8": (["حسب فئة الاستهلاك"], "consumption", "MWh", 1000,
          [("سكني", "residential"), ("تجاري", "commercial"),
           ("حكومي", "government"), ("صناعي", "industrial"),
           ("الأخرى", "other")]),
}
# sheet 7: the year in its title, the regions by name, the categories by header words
SHEET7 = ("المناطق الإدارية",
          [("السكني", "residential"), ("التجاري", "commercial"),
           ("الحكومي", "government"), ("الصناعي", "industrial"),
           ("أخرى", "other")])
REGIONS = {"الرياض": "riyadh", "مكة المكرمة": "makkah",
           "المدينة المنورة": "madinah",
           "القصيم": "qassim",
           "المنطقة الشرقية": "eastern_province",
           "عسير": "asir", "تبوك": "tabuk", "حائل": "hail",
           "الحدود الشمالية": "northern_borders",
           "جازان": "jazan", "نجران": "najran",
           "الباحة": "bahah", "الجوف": "jawf"}
X_COLS = ["x_approx"]


def num(c):
    """(value, approximate?) of a cell: a number, or text with commas and an approximation sign."""
    if isinstance(c, bool) or c is None:
        raise RuntimeError(f"not a figure: {c!r}")
    if isinstance(c, (int, float)):
        return float(c), False
    s = str(c).strip()
    approx = APPROX in s
    s = s.replace(APPROX, "").replace(",", "").strip()
    if not re.fullmatch(r"\d+(?:\.\d+)?", s):
        raise RuntimeError(f"not a figure: {c!r}")
    return float(s), approx


def text(c):
    return " ".join(str(c).split()) if c is not None else ""


def header_cols(rows, start, specs):
    """{item: column} from the rows after the title, by words of the headers."""
    if specs == [(None, "total")]:
        return {"total": 2}
    cols = {}
    for words, item in specs:
        hits = {j for r in rows[start:start + 4] for j, c in enumerate(r) if c is not None and words in text(c)}
        if len(hits) != 1:
            raise RuntimeError(f"the column {item} found {len(hits)} times")
        cols[item] = hits.pop()
    return cols


def parse_sheets(sheets, base):
    rows, seen = [], set()

    def add(item, var, year, v, unit, approx, label):
        k = (item, var, year)
        if k in seen:
            raise RuntimeError(f"{k} given twice")
        seen.add(k)
        rows.append(dict(entity=f"gastat:sa:{item}", variable=var, ts_utc=f"{year}-01-01T00:00:00Z", value=round(v, 3), unit=unit,
                         freq="P1Y", geo="SA", market="", node=label, **base, x_approx="true" if approx else ""))

    vals = {}
    for name, (words, var, unit, scale, specs) in SHEETS.items():
        if name not in sheets and name + " " not in sheets:
            raise RuntimeError(f"no sheet {name}")
        sh = sheets.get(name) or sheets[name + " "]
        title_i = next((i for i, r in enumerate(sh) if r and r[0] is not None and all(w in text(r[0]) for w in words)), None)
        if title_i is None:
            raise RuntimeError(f"sheet {name}: its title not found")
        cols = header_cols(sh, title_i + 1, specs)
        labels = {item: text(next((sh[i][j] for i in range(title_i + 1, title_i + 4) if j < len(sh[i]) and sh[i][j] is not None), ""))
                  for item, j in cols.items()}
        years = 0
        for r in sh[title_i + 1:]:
            y = r[0] if r else None
            if isinstance(y, (int, float)) or (isinstance(y, str) and re.fullmatch(r"\d{4}", y.strip())):
                year = str(int(float(y)))
                years += 1
                for item, j in cols.items():
                    v, approx = num(r[j] if j < len(r) else None)
                    vals[(var, item, year)] = v
                    add(item, var, year, v * scale, unit, approx, labels[item] or text(sh[title_i][0]))
        if not years:
            raise RuntimeError(f"sheet {name}: no year")
    for (var, item, year), v in list(vals.items()):
        if var == "energy_consumed" and item == "total":
            parts = [vals.get(("consumption", c, year)) for _, c in SHEETS["8"][4]]
            if all(p is not None for p in parts) and abs(sum(parts) - v) > 1:
                raise RuntimeError(f"{year}: consumption by category sums to {sum(parts)}, not to the energy consumed {v}")
    sh = sheets.get("7") or sheets.get("7 ")
    if sh is None:
        raise RuntimeError("no sheet 7")
    title_i = next((i for i, r in enumerate(sh) if r and r[0] is not None and SHEET7[0] in text(r[0])), None)
    if title_i is None:
        raise RuntimeError("sheet 7: its title not found")
    m = re.search(r"(\d{4})", text(sh[title_i][0]))
    if not m:
        raise RuntimeError("sheet 7: no year in its title")
    year = m.group(1)
    cols = header_cols(sh, title_i + 1, SHEET7[1])
    got = set()
    for r in sh[title_i + 3:]:
        name = text(r[0]) if r else ""
        if not name or not any(isinstance(c, (int, float)) for c in r[1:]):
            continue
        if name not in REGIONS:
            raise RuntimeError(f"sheet 7: a region not in the map: {name!r}")
        got.add(name)
        for cat, j in cols.items():
            v, approx = num(r[j] if j < len(r) else None)
            add(REGIONS[name], f"sales_{cat}", year, v * 1000, "MWh", approx, name)
    if got != set(REGIONS):
        raise RuntimeError(f"sheet 7: regions missing: {sorted(set(REGIONS) - got)}")
    return pd.DataFrame(rows)


def parse(content, base):
    wb = openpyxl.load_workbook(io.BytesIO(content), data_only=True, read_only=True)
    sheets = {ws.title: [tuple(r) for r in ws.iter_rows(values_only=True)] for ws in wb.worksheets}
    wb.close()
    return parse_sheets(sheets, base)


def main(argv=None):
    ap = argparse.ArgumentParser(description="GASTAT: Saudi Arabia's electrical energy statistics, a year")
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
        content, rec = ip.fetch_raw(CONNECTOR, URL, log, offline=args.offline, fresh=args.fresh, headers=UA, timeout=120, pause=1)
        base = dict(source=SOURCE, source_url=URL, retrieved_at=rec.get("retrieved_at") or "", vintage=ip.vintage_of(rec))
        t = parse(content, base)
        cols = ip.SERIES_COLS + X_COLS
        t = t[cols].sort_values(["variable", "entity", "ts_utc"]).reset_index(drop=True)
        v = {(x, e.split(":")[-1], ts[:4]): val for x, e, ts, val in zip(t.variable, t.entity, t.ts_utc, t.value)}
        head = [
            "Energy Research Warehouse (ERW): General Authority for Statistics (GASTAT), Saudi Arabia, Electrical Energy Statistics 2024 "
            "(Arabic edition), tables 1 to 8, from the Ministry of Energy: capacity, peak load, energy sent out and consumed, consumption by "
            "category, and sales by region (session 2552)",
            "Shape: series (docs/datastandard.md v0). entity gastat:sa:<item>; variable licensed_capacity, peak_load (MW, GASTAT's GW times "
            "1,000), energy_sent_out, energy_consumed, consumption, sales_<category> (MWh, GWh times 1,000); ts_utc the year's first day; freq "
            "P1Y; geo SA; node GASTAT's Arabic label; x_approx true where GASTAT marks the figure as approximate.",
            f"{len(t)} rows; in 2024 energy sent out {v[('energy_sent_out', 'total', '2024')] / 1e6:.3f} TWh, consumed "
            f"{v[('energy_consumed', 'total', '2024')] / 1e6:.3f} TWh, peak load {v[('peak_load', 'total', '2024')] / 1e3:.1f} GW. Consumption by "
            "category sums to the energy consumed each year it is given; nothing is filled.",
            f"Retrieved: {run_id} (UTC) by warehouse/connectors/gastat_saudi_electricity.py; the workbook retrieved {base['retrieved_at']}; "
            f"last modified {base['vintage'] or 'not stated'}",
            f"Run log: warehouse/output/logs/{CONNECTOR}_{run_id}.log",
            f"Raw files: warehouse/raw/{CONNECTOR}/ (not in git)",
            f"Source: {SOURCE} {CITATION}",
            f"  access: {URL} (listed on {LIST})",
            "License: internal. GASTAT's use policy allows reuse for any purpose with GASTAT acknowledged and changes indicated, except "
            "clearly identified third-party material; each table names the Ministry of Energy as its source. Internal until a ruling. "
            f"Cite: {CITATION}.",
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
            ip.update_sources([dict(source=SOURCE, publisher="Ministry of Energy, Saudi Arabia, as published by GASTAT",
                                    report="Electrical Energy Statistics 2024 (GASTAT, Arabic edition), tables 1 to 8", report_url=URL,
                                    document_list=LIST, license="internal", tables=[NAME])])
        ip.write_status(CONNECTOR, run_id, results)
    log.close()
    return 0 if all(r["status"] == "ok" for r in results) else 1


if __name__ == "__main__":
    sys.exit(main())

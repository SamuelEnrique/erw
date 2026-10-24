#!/usr/bin/env python3
"""Mauritius's electricity generation by source, capacity, peak demand and sales, a year, from Statistics Mauritius's
Energy and Water Statistics (session 2409, chain 114: in place of Namibia, whose NamPower reserves all rights and whose
Electricity Control Board's certificate does not verify).

Energy Research Warehouse (ERW) connector. One series table, warehouse/output/statsmu_mauritius_electricity_annual.csv,
from two editions of the Economic and Social Indicators "Energy and Water Statistics" (Excel), two requests:

    https://statsmauritius.govmu.org/Documents/Statistics/ESI/2026/EI1929/ESI_Energy_Yr25_050626.xlsx  (2024 and 2025)
    https://statsmauritius.govmu.org/Documents/Statistics/ESI/2024/EI1791/Energy_Water_Yr23_070624.xlsx  (2022 and 2023)

    sheet TAB1, Table 1 (Main Energy and Water Indicators, 2018 to 2025 and 2017 to 2023): generation_total ("Total
        electricity generated", MWh), renewable_share ("Of which renewables", pct), electricity_sold (MWh)
    sheet "TAB7,8,9", Table 7 (capacities, peak power demand, the edition's two years): capacity_installed,
        capacity_effective, peak_demand_mauritius, peak_demand_rodrigues (MW); its footnote 1: capacity "includes plant
        capacity for electricity not exported to CEB"; neither edition defines effective capacity
    sheet "TAB7,8,9", Table 8 (generation by source of energy, the edition's two years): generation_hydro,
        generation_wind, generation_landfill_gas, generation_photovoltaic, generation_gas_turbine_kerosene,
        generation_fuel_oil_diesel, generation_coal, generation_bagasse (the 2025 edition's "Bagasse & Fuelwood", the
        2023 edition's "Bagasse"), generation_renewable (MWh, the tables' GWh times 1,000)

    entity statsmu:MU; geo MU; node Mauritius (the Republic: the islands of Mauritius and Rodrigues); ts_utc the year's
    1 January; freq P1Y

Generation is every producer's (Table 9: the CEB in Mauritius and Rodrigues and the independent power producers), and
it includes what the independent producers generate for their own use, not exported to the CEB (203 to 245 GWh a year in
2022 to 2025); Table 8's thermal rows include theirs, and coal is burned only in their plants. electricity_sold is the
CEB's sales (Table 11's total by tariff), so generation less sales holds that own use as well as losses (session 2410's
note).

A year both editions give is taken from the later one (2025's); the header says how far the two differ. Checks, each
stopping the run: Table 8's primary sources add to its primary energy, its secondary ones to its secondary energy, and the
two to its total; Table 7's sources add to its total; Tables 7 and 8's totals equal Table 1's generation for the year;
all within 0.01 GWh. A label, year or value that does not read stops it too.

    python warehouse/connectors/statsmu_mauritius.py [--offline] [--out-dir DIR]

Ceiling: two requests, reused from warehouse/raw/statsmu_mauritius/ with --offline. statsmauritius.govmu.org has no
robots file (HTTP 404, session 2409). License: public with the source and copyright status acknowledged (session 2419; the record's
verdict, may be public). Its copyright notice: State material "may be
downloaded free of charge to file or printer without requiring specific permission, provided that any such State owned
material being reproduced accurately and not being used in a derogated manner or in a misleading context. Where this
material is being issued to others, the source (including the URL) and copyright status must be acknowledged." Any other
use needs the Government Information Service's approval. The table was internal until session 2419, and Samuel may
rule otherwise.
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

NAME = "statsmu_mauritius_electricity_annual"
CONNECTOR = "statsmu_mauritius"
SOURCE = "statsmu:energy_water_statistics"
PAGE = "https://statsmauritius.govmu.org/Pages/Statistics/ESI/Energy_Water/Energy_Water_Yr25.aspx"
TERMS = "https://statsmauritius.govmu.org/Pages/CopyrightNotice.aspx"
EDITIONS = [  # oldest first: a later edition's year replaces an earlier one's
    "https://statsmauritius.govmu.org/Documents/Statistics/ESI/2024/EI1791/Energy_Water_Yr23_070624.xlsx",
    "https://statsmauritius.govmu.org/Documents/Statistics/ESI/2026/EI1929/ESI_Energy_Yr25_050626.xlsx",
]
T1 = [("Total electricity generated", "generation_total", "MWh", 1000.0),
      ("Of which renewables", "renewable_share", "pct", 1.0),
      ("Total electricity sold", "electricity_sold", "MWh", 1000.0)]
T8 = [(r"Hydro", "generation_hydro"), (r"Wind", "generation_wind"), (r"Landfill gas", "generation_landfill_gas"),
      (r"Photovoltaic", "generation_photovoltaic"), (r"Gas turbine", "generation_gas_turbine_kerosene"),
      (r"Fuel oil", "generation_fuel_oil_diesel"), (r"Coal", "generation_coal"), (r"Bagasse", "generation_bagasse"),
      (r"Primary energy", "primary"), (r"Secondary energy", "secondary"), (r"Total electricity", "total"),
      (r"of which renewab", "generation_renewable")]
PRIMARY = ["generation_hydro", "generation_wind", "generation_landfill_gas", "generation_photovoltaic"]
SECONDARY = ["generation_gas_turbine_kerosene", "generation_fuel_oil_diesel", "generation_coal", "generation_bagasse"]
# Table 7's data row: year, then these columns as the sheet places them (checked against its header words)
T7 = {3: "capacity_installed", 5: "capacity_effective", 9: "peak_demand_mauritius", 10: "peak_demand_rodrigues",
      11: "hydro", 12: "wind", 14: "photovoltaic", 15: "landfill_gas", 17: "thermal_other", 19: "total"}
TOL = 0.01
UA = {"User-Agent": "Mozilla/5.0 (compatible; ERW-connector/0.1; +https://github.com/SamuelEnrique/erw)"}
COLS = ["entity", "variable", "ts_utc", "value", "unit", "freq", "geo", "market", "node", "source", "source_url",
        "retrieved_at", "vintage"]


def num(x, what):
    if isinstance(x, bool) or not isinstance(x, (int, float)):
        raise RuntimeError(f"{what}: not a number: {x!r}")
    return float(x)


def text(x):
    return re.sub(r"\s+", " ", str(x or "")).strip()


def year_of(x, what):
    if isinstance(x, (int, float)) and x == int(x) and 2000 <= x <= 2100:
        return int(x)
    raise RuntimeError(f"{what}: not a year: {x!r}")


def table1(rows):
    hdr = [i for i, r in enumerate(rows) if text(r[0]) == "Indicators" and text(r[1]) == "Unit"]
    if len(hdr) != 1:
        raise RuntimeError(f"Table 1: {len(hdr)} header rows, not one")
    years = {c: year_of(rows[hdr[0]][c], f"Table 1 column {c}") for c in range(2, len(rows[hdr[0]])) if rows[hdr[0]][c] not in (None, "")}
    out = {}
    gen = [i for i, r in enumerate(rows) if text(r[0]) == T1[0][0]]
    if len(gen) != 1:
        raise RuntimeError(f"Table 1: {len(gen)} rows for {T1[0][0]!r}, not one")
    sold = [i for i, r in enumerate(rows) if text(r[0]) == T1[2][0]]
    if len(sold) != 1:
        raise RuntimeError(f"Table 1: {len(sold)} rows for {T1[2][0]!r}, not one")
    if text(rows[gen[0] + 1][0]) != T1[1][0]:
        raise RuntimeError(f"Table 1: the row after the generation is {text(rows[gen[0] + 1][0])!r}, not the renewables' share")
    for i, (label, var, unit, f) in zip((gen[0], gen[0] + 1, sold[0]), T1):
        want = {"MWh": "GWh", "pct": "%"}[unit]
        if text(rows[i][1]) != want:
            raise RuntimeError(f"Table 1 {label}: unit {text(rows[i][1])!r}, not {want}")
        out[var] = {y: num(rows[i][c], f"Table 1 {label} {y}") for c, y in years.items()}
    return out


def table8(rows):
    at = [i for i, r in enumerate(rows) if text(r[0]).startswith("Table 8 ")]
    if len(at) != 1:
        raise RuntimeError(f"Table 8: {len(at)} titles, not one")
    hdr = [i for i in range(at[0], min(at[0] + 6, len(rows))) if text(rows[i][0]) == "Source of energy"]
    if not hdr:
        raise RuntimeError("Table 8: no header row")
    h = hdr[0]
    years = [year_of(x, "Table 8 header") for x in rows[h][1:] if x not in (None, "")]
    gwh = [c for c, x in enumerate(rows[h + 1]) if text(x) == "GWh"]
    if len(years) != 2 or len(gwh) != 2:
        raise RuntimeError(f"Table 8: years {years}, GWh columns {gwh}")
    out = {}
    for r in rows[h + 2:]:
        lab = next((text(x) for x in r[:3] if text(x)), "")   # the rows are indented by column, 0 to 2
        if not lab:
            if out:
                break
            continue
        hit = [v for p, v in T8 if re.match(p, lab, re.I)]
        if len(hit) != 1:
            raise RuntimeError(f"Table 8: row not known: {lab!r}")
        if hit[0] in out:
            raise RuntimeError(f"Table 8: {hit[0]} given twice")
        out[hit[0]] = {y: num(r[c], f"Table 8 {lab} {y}") for c, y in zip(gwh, years)}
    missing = [v for _, v in T8 if v not in out]
    if missing:
        raise RuntimeError(f"Table 8: rows missing: {missing}")
    for y in years:
        for what, a, b in (("primary", sum(out[v][y] for v in PRIMARY), out["primary"][y]),
                           ("secondary", sum(out[v][y] for v in SECONDARY), out["secondary"][y]),
                           ("total", out["primary"][y] + out["secondary"][y], out["total"][y])):
            if abs(a - b) > TOL:
                raise RuntimeError(f"Table 8 {y}: the {what} sources add to {a}, the row is {b}")
    return out, years


def table7(rows, years):
    at = [i for i, r in enumerate(rows) if text(r[0]).startswith("Table 7 ")]
    if len(at) != 1:
        raise RuntimeError(f"Table 7: {len(at)} titles, not one")
    words = " ".join(text(x) for r in rows[at[0] + 1:at[0] + 5] for x in r if x not in (None, ""))
    for w in ("Installed", "Effective", "Peak power demand", "Mauritius", "Rodrigues", "Hydro", "Wind", "Photovoltaic", "Landfill Gas", "Other", "Total"):
        if w not in words:
            raise RuntimeError(f"Table 7: header word {w!r} not found")
    out = {}
    for r in rows[at[0] + 1:at[0] + 12]:
        if isinstance(r[1], (int, float)) and r[1] in years:
            y = int(r[1])
            out[y] = {v: num(r[c], f"Table 7 {y} {v}") for c, v in T7.items()}
            s = sum(out[y][v] for v in ("hydro", "wind", "photovoltaic", "landfill_gas", "thermal_other"))
            if abs(s - out[y]["total"]) > TOL:
                raise RuntimeError(f"Table 7 {y}: the sources add to {s}, the total is {out[y]['total']}")
    if sorted(out) != sorted(years):
        raise RuntimeError(f"Table 7: years {sorted(out)}, not {sorted(years)}")
    return out


def edition_values(content, url):
    wb = openpyxl.load_workbook(io.BytesIO(content), read_only=True, data_only=True)
    rows = lambda name: [list(r) + [None] * 30 for r in wb[name].iter_rows(values_only=True)]  # noqa: E731
    t1 = table1(rows("TAB1"))
    t789 = rows("TAB7,8,9")
    t8, years = table8(t789)
    t7 = table7(t789, years)
    vals = {}   # (variable, year) -> (value in the table's unit, unit)
    for label, var, unit, f in T1:
        for y, v in t1[var].items():
            vals[(var, y)] = (v * f, unit)
    for y in years:
        for what, a in (("Table 8's total", t8["total"][y]), ("Table 7's total", t7[y]["total"])):
            if abs(a - t1["generation_total"][y]) > TOL:
                raise RuntimeError(f"{y}: {what} is {a}, Table 1's generation {t1['generation_total'][y]}")
        for var in PRIMARY + SECONDARY + ["generation_renewable"]:
            vals[(var, y)] = (t8[var][y] * 1000.0, "MWh")
        for var in ("capacity_installed", "capacity_effective", "peak_demand_mauritius", "peak_demand_rodrigues"):
            vals[(var, y)] = (t7[y][var], "MW")
    return vals


def finish(rows):
    t = pd.DataFrame(rows, columns=COLS)
    if t.duplicated(["entity", "variable", "ts_utc"]).any():
        raise RuntimeError("a key given twice")
    return t.sort_values(["entity", "variable", "ts_utc"]).reset_index(drop=True)


def main(argv=None):
    ap = argparse.ArgumentParser(description="Statistics Mauritius: electricity generation by source, capacity, peak demand and sales, a year")
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
        if not args.offline and (ip.paused("statsmu") or ip.paused_host("statsmauritius.govmu.org")):
            raise RuntimeError("Statistics Mauritius is paused (warehouse/metadata/paused_sources.csv): not requested")
        merged, got, diffs = {}, [], []
        for url in EDITIONS:
            content, rec = ip.fetch_raw(CONNECTOR, url, log, offline=args.offline, pause=2, headers=UA, timeout=300)
            for key, (v, unit) in edition_values(content, url).items():
                if key in merged and abs(merged[key][0] - v) > 1e-6:
                    diffs.append((key, merged[key][0], v))
                merged[key] = (v, unit, url, rec.get("retrieved_at") or "", ip.vintage_of(rec))
            got.append(rec.get("retrieved_at") or "")
        rows = [dict(entity="statsmu:MU", variable=var, ts_utc=f"{y}-01-01T00:00:00Z", value=round(v, 6), unit=unit, freq="P1Y",
                     geo="MU", market="", node="Mauritius", source=SOURCE, source_url=url, retrieved_at=ret, vintage=vin)
                 for (var, y), (v, unit, url, ret, vin) in merged.items()]
        t = finish(rows)
        worst = max(diffs, key=lambda d: abs(d[2] - d[1]) / max(abs(d[1]), 1e-9)) if diffs else None
        diff_line = (f"{len(diffs)} values given by both editions differ (the later one is kept); the largest relative change is {worst[0][0]} {worst[0][1]}, "
                     f"{worst[1]:g} to {worst[2]:g}." if diffs else "The values both editions give agree.")
        header = [
            f"Energy Research Warehouse (ERW): Statistics Mauritius, Energy and Water Statistics, electricity generation by source, capacity, peak demand and sales, {t.ts_utc.min()[:4]} to {t.ts_utc.max()[:4]} (session 2409)",
            "Shape: series (docs/datastandard.md v0). entity statsmu:MU (the Republic of Mauritius); ts_utc the year's 1 January; freq P1Y; geo MU. From Table 1: generation_total, renewable_share (pct), electricity_sold (MWh). "
            "From Table 7: capacity_installed, capacity_effective, peak_demand_mauritius, peak_demand_rodrigues (MW). From Table 8: generation_hydro, _wind, _landfill_gas, _photovoltaic, _gas_turbine_kerosene, _fuel_oil_diesel, _coal, "
            "_bagasse (the 2025 edition's \"Bagasse & Fuelwood\"), generation_renewable (MWh, the tables' GWh times 1,000). Tables 7 and 8 give each edition's two years only (2022 to 2025); Table 1 gives 2017 to 2025. "
            "Generation is every producer's, the independent producers' own use included; electricity_sold is the CEB's sales, so generation less sales is not losses. Capacity includes plants not exporting to the CEB (Table 7's footnote); effective capacity is not defined.",
            f"{len(t)} rows, {t.variable.nunique()} variables. Table 8's sources add to its primary, secondary and total rows, Table 7's to its total, and both totals equal Table 1's generation, within 0.01 GWh. {diff_line}",
            f"Retrieved: {run_id} (UTC) by warehouse/connectors/statsmu_mauritius.py; the workbooks retrieved {', '.join(got)}",
            f"Run log: warehouse/output/logs/{CONNECTOR}_{run_id}.log",
            f"Raw files: warehouse/raw/{CONNECTOR}/ (not in git)",
            f"Source: {SOURCE} Statistics Mauritius, Economic and Social Indicators, Energy and Water Statistics 2025 (Issue 1929) and 2023 (Issue 1791), Tables 1, 7 and 8, {PAGE}",
            f"  access: {EDITIONS[1]} and {EDITIONS[0]}",
            f"License: public with acknowledgement (the record's verdict, may be public). The Government of Mauritius's copyright notice ({TERMS}) lets State material be downloaded and reproduced accurately without specific permission, with the source (including the URL) and copyright status acknowledged; "
            "any other use needs the Government Information Service's approval, for Samuel's ruling. Source: Statistics Mauritius, statsmauritius.govmu.org, (c) Government of Mauritius.",
        ]
        ip.write_csv(t, NAME, header, log, cols=COLS)
        if not args.out_dir:
            ip.update_sources([dict(source=SOURCE, publisher="Statistics Mauritius",
                                    report="Economic and Social Indicators, Energy and Water Statistics (2023 and 2025 editions), Tables 1, 7 and 8",
                                    report_url=PAGE, document_list=EDITIONS[1], license="public", tables=[NAME])])
        results.append(dict(table=NAME, market="all", status="ok", detail=f"{len(t)} rows"))
        print(f"{NAME}: {len(t)} rows; {diff_line}")
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

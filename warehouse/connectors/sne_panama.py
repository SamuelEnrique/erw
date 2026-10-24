#!/usr/bin/env python3
"""Panama's gross generation by plant type, net production, maximum demand and load factor, a year, and its gross
generation a month, from the Secretaria Nacional de Energia's historical electricity statistics (session 2407, chain
114: Panama's generation by source, in place of the Centro Nacional de Despacho, whose statistics load only through a
script from its private site).

Energy Research Warehouse (ERW) connector. Two series tables from one workbook (Excel 97), one request:

    http://www.energia.gob.pa/wp-content/uploads/2024/04/2-CEE-1970-2021-GE-Generaci%C3%B3n-El%C3%A9ctrica.xls
    (the Secretaria's "Generacion Historica Electrica (Serie 1970-2021)", listed on its Datos y Estadisticas page)

    warehouse/output/sne_panama_electricity_annual.csv, freq P1Y, ts_utc the year's 1 January:
      sheet C-GE-8 (Cuadro GE-8, gross generation by plant type and plants of the system, 1980 to 2021, GWh):
        generation_gross_total (Total del Sistema), generation_gross_interconnected (the national interconnected
        system, SIN), generation_gross_canal_authority (the Panama Canal Authority's plants, ACP), and the eleven
        numbered types: generation_gross_hydro (1), generation_gross_steam_bunker (2, the sheet's "Vapor (Bunker)": steam
        plants, on bunker to 2010, mostly coal from 2011 (BLM Carbon) and wholly coal from 2015 (BLM Carbon, Minera
        Panama)),
        generation_gross_internal_combustion (3, bunker or diesel), generation_gross_gas_turbine_light_diesel (4),
        generation_gross_gas_turbine_marine_diesel (5), generation_gross_light_diesel_other (6, the sheet's
        "Sub-Total (Diesel Liviano)"), generation_gross_wind (7), generation_gross_solar (8),
        generation_gross_natural_gas (9), generation_gross_biogas (10), generation_gross_isolated_systems (11)
        (MWh, the sheet's GWh times 1,000)
      sheet C-GE-14 (Cuadro GE-14, 1970 to 2021): net_production (MWh, its GWh times 1,000), peak_demand (MW,
        "Demanda Maxima"), load_factor (pct, "Factor de Carga")
    warehouse/output/sne_panama_generation_monthly.csv, freq P1M, ts_utc the month's first day:
      sheet C-GE-10 (Cuadro GE-10, total gross generation a month, 1980 to 2021, GWh): generation_gross_total (MWh)

    entity sne:PA; geo PA; node Panama

What the variables hold (session 2410's note): net production is GE-13's "Produccion Neta Total" (GE-14 has no notes),
which GE-13's footnotes define as net generation (gross less the plants' auxiliaries) plus purchases from other
companies, the purchases being the net interchange in 1986 to 2020 (and -425.6 GWh in 2021). It is therefore above GE-8's
gross generation in the 14 years of positive purchases (1984, 1987 to 1995, 1997 to 2000), and it covers the Canal
Authority's plants: it is national. Neither sheet says whose maximum demand is given. The Canal Authority's row starts
in 2000, so the system total, the annual and the monthly, breaks there (2000 without the Canal: 4,434.34 GWh, below
1999's 4,458.5); its footnote /c/ says the Canal can pass the interconnected system only 40 MW. The interconnected
system's row is labelled "(1a+2a+3a+4a+5+6)" but holds types 7 to 10 (wind, solar, natural gas, biogas) too. Type 11,
the isolated systems, is split by fuel on the sheet and holds natural gas in 2021 (40.6 GWh, not in
generation_gross_natural_gas); Petroterminales is in type 6 in 1999 and 2000 and in type 11 from 2001. Plants marked
/edemet/, /edechi/ and /auto-edechi/ deliver directly to a distributor and are counted in the interconnected system.

The eleven types must add to the system total, and the interconnected system, the Canal Authority and the isolated
systems must add to it too, within 0.5 GWh a year; a month's twelve values must add to the sheet's annual column within
0.5 GWh. A row label, year or value that does not read, or a sum that does not hold, stops the run. A blank cell has no
row; a zero is written as published. The monthly sheet's annual column is not GE-8's total in every year (1980: 1,811.6
against 1,813.277 GWh), so the two tables are not forced to agree; the header says by how much they differ at most.
The increments and the sheets' growth rates are not taken (they are computed from the values).

    python warehouse/connectors/sne_panama.py [--only annual|monthly] [--offline] [--out-dir DIR]

Ceiling: one request, reused from warehouse/raw/sne_panama/ with --offline. www.energia.gob.pa's robots file disallows
only /wp-admin/ and names no AI agent (session 2407). License: internal until a ruling: the Datos y Estadisticas page
says the Secretaria makes the information available and that its use must cite the source (SECRETARIA NACIONAL DE
ENERGIA), while every page's footer says all rights are reserved.
"""

import argparse
import datetime as dt
import io
import os
import re
import sys
import traceback

import pandas as pd
import xlrd

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import iso_prices as ip  # noqa: E402

CONNECTOR = "sne_panama"
ANNUAL = "sne_panama_electricity_annual"
MONTHLY = "sne_panama_generation_monthly"
SOURCE = "sne:estadisticas_electricidad"
PAGE = "https://www.energia.gob.pa/datos-y-estadisticas/"
URL = "http://www.energia.gob.pa/wp-content/uploads/2024/04/2-CEE-1970-2021-GE-Generaci%C3%B3n-El%C3%A9ctrica.xls"
GE8 = "C-GE-8 GenBruXTCen&PSis,80-21"
GE10 = "C-GE-10 GenBruTotMen,80-21"
GE14 = "C-GE-14 ProdNet,DemMax,FactCar"
# GE-8's rows by the start of their label (the sheet's accents are not matched)
TYPES = [(r"1\.\s+Total Hidro", "generation_gross_hydro"),
         (r"2\.\s+Vapor", "generation_gross_steam_bunker"),
         (r"3\.\s+Combustion Interna", "generation_gross_internal_combustion"),
         (r"4\.\s+Turbina de Gas\s+\(Diesel Liviano\)", "generation_gross_gas_turbine_light_diesel"),
         (r"5\.\s+Turbina de Gas\s+\(Diesel Marino\)", "generation_gross_gas_turbine_marine_diesel"),
         (r"6\.\s+Sub-Total\s+\(Diesel Liviano\)", "generation_gross_light_diesel_other"),
         (r"7\.\s+Centrales E", "generation_gross_wind"),
         (r"8\.\s+Central Solar", "generation_gross_solar"),
         (r"9\.\s+Planta de Gas Natural", "generation_gross_natural_gas"),
         (r"10\.\s+Planta de Biogas", "generation_gross_biogas"),
         (r"11\.\s+Sistemas Aislados", "generation_gross_isolated_systems")]
PARTS = [(r"Total del Sistema$", "generation_gross_total"),
         (r"Total - Sistema Interconectado Nacional", "generation_gross_interconnected"),
         (r"Total - Autoridad del Canal", "generation_gross_canal_authority")]
TOL = 0.5
UA = {"User-Agent": "Mozilla/5.0 (compatible; ERW-connector/0.1; +https://github.com/SamuelEnrique/erw)"}
COLS = ["entity", "variable", "ts_utc", "value", "unit", "freq", "geo", "market", "node", "source", "source_url",
        "retrieved_at", "vintage"]


def val(x, what):
    if x == "" or x is None:
        return None
    if not isinstance(x, float):
        raise RuntimeError(f"{what}: not a number: {x!r}")
    return x


def year(x, what):
    if not isinstance(x, float) or x != int(x) or not 1970 <= x <= 2100:
        raise RuntimeError(f"{what}: not a year: {x!r}")
    return int(x)


def ge8(book):
    s = book.sheet_by_name(GE8)
    hdr = [r for r in range(s.nrows) if str(s.cell_value(r, 1)).strip() == "Tipo y Planta"]
    if len(hdr) != 1:
        raise RuntimeError(f"{GE8}: {len(hdr)} header rows, not one")
    years = {c: year(s.cell_value(hdr[0], c), f"{GE8} column {c}") for c in range(2, s.ncols) if s.cell_value(hdr[0], c) != ""}
    found = {}
    for pat, name in TYPES + PARTS:
        rows = [r for r in range(hdr[0] + 1, s.nrows) if re.match(pat, str(s.cell_value(r, 1)).strip())]
        if len(rows) != 1:
            raise RuntimeError(f"{GE8}: {len(rows)} rows for {pat!r}, not one")
        found[name] = {y: val(s.cell_value(rows[0], c), f"{GE8} {name} {y}") for c, y in years.items()}
    for y in years.values():
        total = found["generation_gross_total"][y]
        if total is None:
            raise RuntimeError(f"{GE8} {y}: no system total")
        types = sum(found[n][y] or 0 for _, n in TYPES)
        parts = sum(found[n][y] or 0 for n in ("generation_gross_interconnected", "generation_gross_canal_authority", "generation_gross_isolated_systems"))
        if abs(types - total) > TOL:
            raise RuntimeError(f"{GE8} {y}: the eleven types add to {types}, the total is {total}")
        if abs(parts - total) > TOL:
            raise RuntimeError(f"{GE8} {y}: the system, the Canal Authority and the isolated systems add to {parts}, the total is {total}")
    return found


def ge14(book):
    s = book.sheet_by_name(GE14)
    hdr = [r for r in range(s.nrows) if str(s.cell_value(r, 1)).strip().startswith("A") and "Neta" in str(s.cell_value(r, 2))]
    if len(hdr) != 1:
        raise RuntimeError(f"{GE14}: {len(hdr)} header rows, not one")
    h = [str(s.cell_value(hdr[0], c)) for c in range(s.ncols)]
    if not ("(GWh)" in h[2] and "(MW)" in h[4] and "(%)" in h[6]):
        raise RuntimeError(f"{GE14}: header not as expected: {h}")
    out = {}
    for r in range(hdr[0] + 1, s.nrows):
        y = s.cell_value(r, 1)
        if not isinstance(y, float):
            if out:
                break   # the growth rates below the years
            continue
        y = year(y, f"{GE14} row {r}")
        out[y] = [val(s.cell_value(r, c), f"{GE14} {y} column {c}") for c in (2, 4, 6)]
    if not out:
        raise RuntimeError(f"{GE14}: no year read")
    return out


def ge10(book):
    s = book.sheet_by_name(GE10)
    hdr = [r for r in range(s.nrows) if str(s.cell_value(r, 2)).strip() == "Anual" and str(s.cell_value(r, 3)).strip() == "Enero"]
    if len(hdr) != 1:
        raise RuntimeError(f"{GE10}: {len(hdr)} header rows, not one")
    out = {}
    for r in range(hdr[0] + 1, s.nrows):
        y = s.cell_value(r, 1)
        if not isinstance(y, float):
            if out:
                break   # the growth rates below the years
            continue
        y = year(y, f"{GE10} row {r}")
        annual = val(s.cell_value(r, 2), f"{GE10} {y} annual")
        months = [val(s.cell_value(r, c), f"{GE10} {y} month {c - 2}") for c in range(3, 15)]
        if None in months or annual is None:
            raise RuntimeError(f"{GE10} {y}: a blank month or annual value")
        if abs(sum(months) - annual) > TOL:
            raise RuntimeError(f"{GE10} {y}: the months add to {sum(months)}, the annual column is {annual}")
        out[y] = (annual, months)
    if not out:
        raise RuntimeError(f"{GE10}: no year read")
    return out


def finish(rows):
    t = pd.DataFrame(rows, columns=COLS)
    if t.duplicated(["entity", "variable", "ts_utc"]).any():
        raise RuntimeError("a key given twice")
    return t.sort_values(["entity", "variable", "ts_utc"]).reset_index(drop=True)


def main(argv=None):
    ap = argparse.ArgumentParser(description="Secretaria Nacional de Energia, Panama: generation by type, net production, peak demand, a year; gross generation, a month")
    ap.add_argument("--only", choices=["annual", "monthly"], help="write one of the two tables")
    ap.add_argument("--offline", action="store_true", help="the saved workbook only, no request")
    ap.add_argument("--out-dir", help="a trial: the tables under this folder, not warehouse/output")
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
    written = []
    try:
        if not args.offline and (ip.paused("sne") or ip.paused_host("www.energia.gob.pa")):
            raise RuntimeError("the Secretaria Nacional de Energia is paused (warehouse/metadata/paused_sources.csv): not requested")
        content, rec = ip.fetch_raw(CONNECTOR, URL, log, offline=args.offline, headers=UA, timeout=300)
        book = xlrd.open_workbook(file_contents=content)
        retrieved, vintage = rec.get("retrieved_at") or "", ip.vintage_of(rec)
        a, p, m = ge8(book), ge14(book), ge10(book)
        base = dict(entity="sne:PA", geo="PA", market="", node="Panama", source=SOURCE, source_url=URL,
                    retrieved_at=retrieved, vintage=vintage)
        gap = max(abs(m[y][0] - a["generation_gross_total"][y]) for y in m if y in a["generation_gross_total"])
        common = [
            f"Retrieved: {run_id} (UTC) by warehouse/connectors/sne_panama.py; the workbook retrieved {retrieved}",
            f"Run log: warehouse/output/logs/{CONNECTOR}_{run_id}.log",
            f"Raw files: warehouse/raw/{CONNECTOR}/ (not in git)",
        ]
        license_line = ("License: internal. The Secretaria's Datos y Estadisticas page says it makes the information available and that its use must cite the source; "
                        "every page's footer says all rights are reserved; internal until a ruling. Cite: Secretaria Nacional de Energia, Panama, Generacion Historica Electrica (Serie 1970-2021).")
        if args.only in (None, "annual"):
            rows = []
            for name, by_year in a.items():
                for y, v in by_year.items():
                    if v is not None:
                        rows.append(dict(base, variable=name, ts_utc=f"{y}-01-01T00:00:00Z", value=round(v * 1000.0, 6), unit="MWh", freq="P1Y"))
            for y, (net, peak, lf) in p.items():
                for name, v, unit, f in (("net_production", net, "MWh", 1000.0), ("peak_demand", peak, "MW", 1.0), ("load_factor", lf, "pct", 1.0)):
                    if v is not None:
                        rows.append(dict(base, variable=name, ts_utc=f"{y}-01-01T00:00:00Z", value=round(v * f, 6), unit=unit, freq="P1Y"))
            t = finish(rows)
            header = [
                f"Energy Research Warehouse (ERW): Secretaria Nacional de Energia, Panama, gross generation by plant type, net production, maximum demand and load factor, {t.ts_utc.min()[:4]} to {t.ts_utc.max()[:4]} (session 2407)",
                "Shape: series (docs/datastandard.md v0). entity sne:PA; ts_utc the year's 1 January; freq P1Y; geo PA. From Cuadro GE-8 (1980 to 2021): generation_gross_total, generation_gross_interconnected (the national interconnected system), "
                "generation_gross_canal_authority (the Panama Canal Authority's plants), and by type generation_gross_hydro, _steam_bunker, _internal_combustion (bunker or diesel), _gas_turbine_light_diesel, _gas_turbine_marine_diesel, "
                "_light_diesel_other (the sheet's \"Sub-Total (Diesel Liviano)\"), _wind, _solar, _natural_gas, _biogas, _isolated_systems (MWh, the sheet's GWh times 1,000). From Cuadro GE-14 (1970 to 2021): net_production (MWh), "
                "peak_demand (MW, the maximum demand), load_factor (pct).",
                "Definitions (GE-13's footnotes; session 2410's note): net_production is net generation plus purchases from other companies, the purchases being the net interchange (1986 to 2021), so it is national and above gross generation "
                "in years of positive purchases; neither sheet says whose maximum demand is given. Type 2 (\"Vapor (Bunker)\") is steam plants, mostly coal from 2011 and wholly coal from 2015. The Canal Authority's row starts in 2000, "
                "so the total breaks there; its footnote /c/: the Canal can pass the interconnected system only 40 MW. The interconnected system's row holds types 7 to 10 too. The isolated systems hold 40.6 GWh of natural gas in 2021, "
                "not in generation_gross_natural_gas.",
                f"{len(t)} rows, {t.variable.nunique()} variables. The eleven types add to the total, and the interconnected system, the Canal Authority and the isolated systems add to it, within 0.5 GWh a year. "
                "A blank cell has no row; a zero is written as published. The isolated systems are both a type and a part of the system.",
                *common,
                f"Source: {SOURCE} Secretaria Nacional de Energia, Panama, Generacion Historica Electrica (Serie 1970-2021), sheets {GE8} and {GE14}, listed at {PAGE}",
                f"  access: {URL}",
                license_line,
            ]
            ip.write_csv(t, ANNUAL, header, log, cols=COLS)
            written.append(ANNUAL)
            results.append(dict(table=ANNUAL, market="all", status="ok", detail=f"{len(t)} rows"))
            print(f"{ANNUAL}: {len(t)} rows")
        if args.only in (None, "monthly"):
            rows = []
            for y, (annual, months) in m.items():
                for i, v in enumerate(months, 1):
                    rows.append(dict(base, variable="generation_gross_total", ts_utc=f"{y}-{i:02d}-01T00:00:00Z", value=round(v * 1000.0, 6), unit="MWh", freq="P1M"))
            t = finish(rows)
            header = [
                f"Energy Research Warehouse (ERW): Secretaria Nacional de Energia, Panama, total gross generation a month, {t.ts_utc.min()[:7]} to {t.ts_utc.max()[:7]} (session 2407)",
                "Shape: series (docs/datastandard.md v0). entity sne:PA; variable generation_gross_total (MWh, the sheet's GWh times 1,000); ts_utc the month's first day; freq P1M; geo PA. From Cuadro GE-10.",
                f"{len(t)} rows. From 2000 the total includes the Panama Canal Authority's plants (GE-8's row starts then), so the series breaks there. Each year's twelve months add to the sheet's annual column within 0.5 GWh. That column differs from Cuadro GE-8's system total (sne_panama_electricity_annual) by up to {gap:.3f} GWh in a year; "
                "the two are kept as published.",
                *common,
                f"Source: {SOURCE} Secretaria Nacional de Energia, Panama, Generacion Historica Electrica (Serie 1970-2021), sheet {GE10}, listed at {PAGE}",
                f"  access: {URL}",
                license_line,
            ]
            ip.write_csv(t, MONTHLY, header, log, cols=COLS)
            written.append(MONTHLY)
            results.append(dict(table=MONTHLY, market="all", status="ok", detail=f"{len(t)} rows"))
            print(f"{MONTHLY}: {len(t)} rows; its annual column is within {gap:.3f} GWh of GE-8's total")
        if not args.out_dir:
            ip.update_sources([dict(source=SOURCE, publisher="Secretaria Nacional de Energia, Panama",
                                    report="Generacion Historica Electrica (Serie 1970-2021), cuadros GE-8 (gross generation by plant type), GE-10 (monthly gross generation) and GE-14 (net production, maximum demand, load factor)",
                                    report_url=PAGE, document_list=URL, license="internal", tables=written)])
    except Exception:
        tb = ip.redact(traceback.format_exc())
        log(f"FAILED, no output file written:\n{tb}")
        print(f"{CONNECTOR} FAILED, no output file written: {tb.strip().splitlines()[-1]}", file=sys.stderr)
        results.append(dict(table=ANNUAL if args.only != "monthly" else MONTHLY, market="all", status="failed", detail=tb.strip().splitlines()[-1][:300]))
    if not args.out_dir:
        ip.write_status(CONNECTOR, run_id, results)
    log.close()
    return 0 if results and all(r["status"] == "ok" for r in results) else 1


if __name__ == "__main__":
    sys.exit(main())

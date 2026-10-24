#!/usr/bin/env python3
"""Guatemala's generation by fuel, imports, exports and the national interconnected system's demand, a month from 2017,
from the Administrador del Mercado Mayorista's yearly workbooks of monthly generation by plant (session 2408, chain 114:
Guatemala's generation).

Energy Research Warehouse (ERW) connector. One series table, warehouse/output/amm_guatemala_generation_monthly.csv, from
one workbook a year, 2017 to 2025 (nine requests), at the address AMM's annual reports page opens for "Generacion Mensual
por Planta (XLS)" (its script js/informes.js: .xls before 2021, .xlsx after):

    https://www.amm.org.gt/pdfs2/pub_gen_mensual_x_planta/GM<year>0101.xls[x]

Each workbook's first sheet ("Energia", "Despacho de carga ejecutado del Sistema Nacional Interconectado", GWh) lists
every plant's energy a month and ends with two blocks, which are what is taken:
    the system rows: TRANSACCIONES (regional transactions, exports less imports), IMPORTACIONES, EXPORTACIONES,
        GENERACION TOTAL, DEMANDA S.N.I.
    "GENERACION POR TIPO DE COMBUSTIBLE": one row a fuel and TOTAL

    entity amm:GT; geo GT; node Guatemala; ts_utc the month's first day; freq P1M
    variable generation_<fuel> for geothermal, wind, solar, hydro, biogas, biomass, syngas, natural_gas, coal, petcoke,
             bunker, diesel; generation_total; imports, exports, net_exports (TRANSACCIONES); demand_sni (MWh, the
             workbook's GWh times 1,000)

A fuel a year's workbook does not list has no row that year (syngas from 2021, natural gas from 2019, petroleum coke from
2018), and a blank month has no row (petroleum coke's first months of 2018, natural gas's of 2019); a zero is written as published. Checks, each stopping the run: the workbook's year is the year asked; the fuels
add to the TOTAL row, which equals GENERACION TOTAL; exports less imports equal TRANSACCIONES; generation less
TRANSACCIONES equals the demand; each row's twelve months add to its TOTAL column where the workbook has one; all within
0.01 GWh. A label, a month header or a value that does not read stops it too. The peak demand (MW) is not in these
workbooks and is not taken.

    python warehouse/connectors/amm_guatemala.py [--offline] [--out-dir DIR]

Ceiling: nine requests, reused from warehouse/raw/amm_guatemala/ with --offline. www.amm.org.gt has no robots file (HTTP
404, session 2408). License: internal until a ruling: AMM's pages state no terms of reuse.
"""

import argparse
import datetime as dt
import io
import os
import re
import sys
import traceback
import unicodedata

import openpyxl
import pandas as pd
import xlrd

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import iso_prices as ip  # noqa: E402

NAME = "amm_guatemala_generation_monthly"
CONNECTOR = "amm_guatemala"
SOURCE = "amm:generacion_mensual_por_planta"
PAGE = "https://www.amm.org.gt/portal/?page_id=145"
YEARS = range(2017, 2026)
FUELS = {"GEOT": "geothermal", "EOLI": "wind", "ELIC": "wind", "SOLA": "solar", "HIDR": "hydro", "BIOG": "biogas",
         "BIOM": "biomass", "SYNG": "syngas", "GAS ": "natural_gas", "CARB": "coal", "COQU": "petcoke", "BUNK": "bunker",
         "DIES": "diesel"}
SYSTEM = {"TRANSACCIONES": "net_exports", "IMPORTACIONES": "imports", "EXPORTACIONES": "exports",
          "GENERACION TOTAL": "generation_total", "DEMANDA S.N.I": "demand_sni"}
MONTHS = ["ENE", "FEB", "MAR", "ABR", "MAY", "JUN", "JUL", "AGO", "SEP", "OCT", "NOV", "DIC"]
TOL = 0.01
UA = {"User-Agent": "Mozilla/5.0 (compatible; ERW-connector/0.1; +https://github.com/SamuelEnrique/erw)"}
COLS = ["entity", "variable", "ts_utc", "value", "unit", "freq", "geo", "market", "node", "source", "source_url",
        "retrieved_at", "vintage"]


def url_of(year):
    return f"https://www.amm.org.gt/pdfs2/pub_gen_mensual_x_planta/GM{year}0101.{'xls' if year < 2021 else 'xlsx'}"


def plain(s):
    """A label upper-cased, its accents and any character the workbook's encoding lost dropped."""
    s = unicodedata.normalize("NFKD", str(s)).encode("ascii", "ignore").decode()
    return re.sub(r"\s+", " ", s).strip().upper()


def sheet_rows(content):
    if content[:2] == b"PK":
        ws = openpyxl.load_workbook(io.BytesIO(content), read_only=True, data_only=True).worksheets[0]
        rows = [list(r) for r in ws.iter_rows(values_only=True)]
    else:
        s = xlrd.open_workbook(file_contents=content).sheet_by_index(0)
        rows = [s.row_values(i) for i in range(s.nrows)]
    return [["" if c is None else c for c in r] for r in rows]


def num(x, what):
    if isinstance(x, bool) or not isinstance(x, (int, float)):
        raise RuntimeError(f"{what}: not a number: {x!r}")
    return float(x)


def month_cols(row, what):
    """{month 1-12: column} and the TOTAL column (or None) from a header row of month names."""
    cols, total = {}, None
    for c, x in enumerate(row):
        p = plain(x)
        if p[:3] in MONTHS and p[:3] not in [MONTHS[m - 1] for m in cols]:
            cols[MONTHS.index(p[:3]) + 1] = c
        elif p == "TOTAL":
            total = c
    if sorted(cols) != list(range(1, 13)):
        raise RuntimeError(f"{what}: month header not read: {row}")
    return cols, total


def year_values(rows, year):
    """{variable: [12 monthly GWh]} from one year's sheet."""
    head = [plain(x) for r in rows[:5] for x in r if x != ""]
    if str(year) not in [h[:4] for h in head]:
        raise RuntimeError(f"{year}: the workbook's year is not {year}: {head}")
    label = lambda r: plain(r[1]) if len(r) > 1 and plain(r[1]) else plain(r[0])  # noqa: E731
    fuel_at = [i for i, r in enumerate(rows) if label(r).startswith("GENERACION POR")]
    if len(fuel_at) != 1:
        raise RuntimeError(f"{year}: {len(fuel_at)} fuel blocks, not one")
    f = fuel_at[0]
    fcols, ftotal = month_cols(rows[f - 1], f"{year} fuel block")
    out = {}

    def take(r, var, cols, total, what):
        vals = [None if r[cols[m]] == "" else num(r[cols[m]], f"{what} month {m}") for m in range(1, 13)]
        if total is not None and r[total] != "":
            t = num(r[total], f"{what} total")
            if abs(sum(v or 0 for v in vals) - t) > TOL:
                raise RuntimeError(f"{what}: the months add to {sum(v or 0 for v in vals)}, its total is {t}")
        if var in out:
            raise RuntimeError(f"{what}: {var} given twice")
        out[var] = vals

    for r in rows[f + 1:]:
        lab = label(r)
        if not lab:
            continue
        if lab == "TOTAL":
            take(r, "fuel_total", fcols, ftotal, f"{year} fuel TOTAL")
            break
        key = [k for k in FUELS if lab.startswith(k)]
        if len(key) != 1:
            raise RuntimeError(f"{year}: fuel row not known: {lab!r}")
        take(r, "generation_" + FUELS[key[0]], fcols, ftotal, f"{year} {lab}")
    if "fuel_total" not in out:
        raise RuntimeError(f"{year}: the fuel block has no TOTAL row")
    hdr = [i for i, r in enumerate(rows[:f]) if sum(plain(x)[:3] in MONTHS for x in r) >= 12]
    if not hdr:
        raise RuntimeError(f"{year}: no month header above the plants")
    scols, stotal = month_cols(rows[hdr[0]], f"{year} plant block")
    for lab_want, var in SYSTEM.items():
        hit = [r for r in rows[:f] if label(r).startswith(lab_want)]
        if len(hit) != 1:
            raise RuntimeError(f"{year}: {len(hit)} rows for {lab_want}, not one")
        take(hit[0], var, scols, stotal, f"{year} {lab_want}")
    for var in ("fuel_total",) + tuple(SYSTEM.values()):
        if None in out[var]:
            raise RuntimeError(f"{year}: {var} has a blank month")
    fuels = [v for v in out if v.startswith("generation_") and v != "generation_total"]
    for m in range(12):
        s = sum(out[v][m] or 0 for v in fuels)
        checks = [("the fuels against their TOTAL", s, out["fuel_total"][m]),
                  ("the fuel TOTAL against GENERACION TOTAL", out["fuel_total"][m], out["generation_total"][m]),
                  ("exports less imports against TRANSACCIONES", out["exports"][m] - out["imports"][m], out["net_exports"][m]),
                  ("generation less TRANSACCIONES against the demand", out["generation_total"][m] - out["net_exports"][m], out["demand_sni"][m])]
        for what, a, b in checks:
            if abs(a - b) > TOL:
                raise RuntimeError(f"{year} month {m + 1}: {what}: {a} and {b}")
    del out["fuel_total"]
    return out


def finish(rows):
    t = pd.DataFrame(rows, columns=COLS)
    if t.duplicated(["entity", "variable", "ts_utc"]).any():
        raise RuntimeError("a key given twice")
    return t.sort_values(["entity", "variable", "ts_utc"]).reset_index(drop=True)


def main(argv=None):
    ap = argparse.ArgumentParser(description="AMM Guatemala: generation by fuel, trade and demand, a month")
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
        if not args.offline and (ip.paused("amm") or ip.paused_host("www.amm.org.gt")):
            raise RuntimeError("AMM is paused (warehouse/metadata/paused_sources.csv): not requested")
        rows, got = [], []
        for year in YEARS:
            url = url_of(year)
            content, rec = ip.fetch_raw(CONNECTOR, url, log, offline=args.offline, pause=2, headers=UA, timeout=300)
            vals = year_values(sheet_rows(content), year)
            base = dict(entity="amm:GT", unit="MWh", freq="P1M", geo="GT", market="", node="Guatemala", source=SOURCE,
                        source_url=url, retrieved_at=rec.get("retrieved_at") or "", vintage=ip.vintage_of(rec))
            for var, months in vals.items():
                for m, v in enumerate(months, 1):
                    if v is None:
                        continue
                    rows.append(dict(base, variable=var, ts_utc=f"{year}-{m:02d}-01T00:00:00Z", value=round(v * 1000.0, 6)))
            got.append((year, rec.get("retrieved_at") or ""))
            log(f"  {year}: {len(vals)} variables")
        t = finish(rows)
        firsts = {v: g.ts_utc.min()[:4] for v, g in t.groupby("variable") if g.ts_utc.min()[:4] != str(YEARS[0])}
        header = [
            f"Energy Research Warehouse (ERW): Administrador del Mercado Mayorista (AMM), Guatemala, generation by fuel, imports, exports and the national interconnected system's demand, a month, {t.ts_utc.min()[:7]} to {t.ts_utc.max()[:7]} (session 2408)",
            "Shape: series (docs/datastandard.md v0). entity amm:GT; variable generation_<fuel> (geothermal, wind, solar, hydro, biogas, biomass, syngas, natural_gas, coal, petcoke, bunker, diesel), generation_total, "
            "imports, exports, net_exports (AMM's TRANSACCIONES, regional transactions: exports less imports), demand_sni (DEMANDA S.N.I.) (MWh, the workbooks' GWh times 1,000); ts_utc the month's first day; freq P1M; geo GT.",
            f"{len(t)} rows, {t.variable.nunique()} variables. The fuels add to the total, which equals GENERACION TOTAL; exports less imports equal TRANSACCIONES; generation less TRANSACCIONES equals the demand; all within 0.01 GWh a month. "
            f"A fuel a year's workbook does not list, or a blank month, has no row (first year: {', '.join(f'{k} {v}' for k, v in sorted(firsts.items())) or 'all from the first'}); a zero is as published. The peak demand is not in these workbooks.",
            f"Retrieved: {run_id} (UTC) by warehouse/connectors/amm_guatemala.py; the workbooks retrieved {got[0][1]} to {got[-1][1]}",
            f"Run log: warehouse/output/logs/{CONNECTOR}_{run_id}.log",
            f"Raw files: warehouse/raw/{CONNECTOR}/ (not in git)",
            f"Source: {SOURCE} Administrador del Mercado Mayorista, Guatemala, Generacion Mensual por Planta (XLS), one workbook a year, sheet Energia, its system rows and its block GENERACION POR TIPO DE COMBUSTIBLE, listed at {PAGE} (Anuales)",
            f"  access: {url_of(YEARS[0])} to {url_of(YEARS[-1])}",
            "License: internal. AMM's pages state no terms of reuse; internal until a ruling. Cite: Administrador del Mercado Mayorista, Generacion Mensual por Planta.",
        ]
        ip.write_csv(t, NAME, header, log, cols=COLS)
        if not args.out_dir:
            ip.update_sources([dict(source=SOURCE, publisher="Administrador del Mercado Mayorista (AMM), Guatemala",
                                    report="Generacion Mensual por Planta (XLS), a workbook a year: generation by fuel, imports, exports, regional transactions and the SNI's demand",
                                    report_url=PAGE, document_list=url_of(YEARS[-1]), license="internal", tables=[NAME])])
        results.append(dict(table=NAME, market="all", status="ok", detail=f"{len(t)} rows"))
        print(f"{NAME}: {len(t)} rows; first years {firsts}")
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

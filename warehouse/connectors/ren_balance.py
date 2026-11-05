#!/usr/bin/env python3
"""Portugal's electricity balance a year: production by source, storage, the commercial exchanges and consumption, from
REN's Data Hub (session 2280, chain 104: Portugal's generation and consumption).

Energy Research Warehouse (ERW) connector. One series table, warehouse/output/ren_portugal_balance_annual.csv, from the
Data Hub's CSV export of its monthly electricity balance (model 1550, the "monthly-balance" page), one request a
December:

    https://datahub.ren.pt/service/exports/csv?startDateString=<year>-12-31&endDateString=<year>-12-31&culture=en-GB&country=EN&modelId=1550

The export answers one month whatever the range asked (session 2280: 2020-01-01 to 2026-09-30 gave January 2020 only).
Each holds the month, its year-to-date total ("Acumulado [GWh]") and the same for the year before; December's
year-to-date is the year. So December of 2021, 2023 and 2025 give 2020 to 2025, each year once. The rows (Portuguese,
footnote marks dropped) are mapped to variables, a parent's children named after it:

    production_total; renewable, renewable_hydro, renewable_wind, renewable_solar, renewable_wave, renewable_biomass,
    biomass_cogeneration, biomass_other; non_renewable, coal, natural_gas, natural_gas_combined_cycle,
    natural_gas_cogeneration, other_thermal, other_thermal_cogeneration, other_thermal_other; storage_production,
    pumped_storage_production, battery_injection; storage_consumption, pumping_consumption, battery_charging; net_imports
    (SALDO IMPORTADOR: negative a net export), imports_commercial, exports_commercial; consumption

    entity      ren:PT; node Portugal (mainland): REN's page gives "the consumption of electricity in mainland Portugal"
                (session 2289); geo PT; unit MWh (REN's GWh times 1,000, an exact factor); ts_utc the year's 1
                January at 00:00:00Z; freq P1Y

A row REN does not print in a year (coal after 2021; waves and batteries from 2024) has no row; nothing is filled. A
header not REN's, a label not in the map, a value that is not a number or a year given twice stops the run. The month's
peak (Ponta [MW]) and its own month figures are not taken.

    python warehouse/connectors/ren_balance.py [--decembers 2021,2023,2025] [--offline] [--out-dir DIR]

Ceiling: one request a December, reused from warehouse/raw/ren_balance/ with --offline. datahub.ren.pt has no robots
file (session 2280). License: internal until a ruling: the Data Hub's pages read (its About, API instructions and
Hyperlinks pages) state no terms of reuse, only that REN presents "this service's numbers to the scientific community,
journalists and all interested parties".
"""

import argparse
import csv
import datetime as dt
import io
import os
import re
import sys
import traceback

import pandas as pd

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import iso_prices as ip  # noqa: E402

NAME = "ren_portugal_balance_annual"
CONNECTOR = "ren_balance"
SOURCE = "ren:datahub_monthly_balance"
PAGE = "https://datahub.ren.pt/en/electricity/monthly-balance/"
URL = "https://datahub.ren.pt/service/exports/csv?startDateString={d}-12-31&endDateString={d}-12-31&culture=en-GB&country=EN&modelId=1550"
UA = {"User-Agent": "Mozilla/5.0 (compatible; ERW-connector/0.1; +https://github.com/SamuelEnrique/erw)"}
TOP = {"PRODUÇÃO TOTAL": "production_total", "CONSUMO PARA ARMAZENAMENTO": "storage_consumption",
       "SALDO IMPORTADOR": "net_imports", "CONSUMO": "consumption"}
GROUPS = {"Produção Renovável": "renewable", "Produção não Renovável": "non_renewable",
          "Produção por Armazenamento": "storage_production"}
PARENTS = {"Biomassa": "renewable_biomass", "Gás Natural": "natural_gas", "Outra Térmica": "other_thermal"}
PLAIN = {"Hídrica": "renewable_hydro", "Eólica": "renewable_wind", "Solar": "renewable_solar", "Ondas": "renewable_wave",
         "Carvão": "coal", "Produção por Bombagem": "pumped_storage_production", "Injeção de Baterias": "battery_injection",
         "Bombagem": "pumping_consumption", "Baterias": "battery_charging",
         "Importação (valor comercial)": "imports_commercial", "Exportação (valor comercial)": "exports_commercial"}
CHILD = {("renewable_biomass", "Cogeração"): "biomass_cogeneration", ("renewable_biomass", "Outros"): "biomass_other",
         ("natural_gas", "Ciclo Combinado"): "natural_gas_combined_cycle", ("natural_gas", "Cogeração"): "natural_gas_cogeneration",
         ("other_thermal", "Cogeração"): "other_thermal_cogeneration", ("other_thermal", "Outros"): "other_thermal_other"}
MONTHS = {"Dec": 12}
COLS = ["entity", "variable", "ts_utc", "value", "unit", "freq", "geo", "market", "node", "source", "source_url",
        "retrieved_at", "vintage"]


def label(s):
    return re.sub(r"\s+\d+$", "", s.strip())


def file_rows(text, url, retrieved, vintage):
    rows = list(csv.reader(io.StringIO(text)))
    head = [h.strip() for h in rows[0]]
    m1, m2 = re.fullmatch(r"Dec (\d\d) \[GWh\]", head[2] if len(head) > 2 else ""), re.fullmatch(r"Dec (\d\d) \[GWh\]", head[4] if len(head) > 4 else "")
    if head[1] != "Ponta [MW]" or not m1 or not m2 or head[3] != "Acumulado [GWh]" or head[5] != "Acumulado [GWh]":
        raise RuntimeError(f"{url}: the header is not REN's December balance: {head[:6]}")
    years = (2000 + int(m1.group(1)), 2000 + int(m2.group(1)))
    out, parent = [], None
    for r in rows[1:]:
        if not r or not r[0].strip():
            continue
        name = label(r[0])
        if name in TOP:
            var, parent = TOP[name], None
        elif name in GROUPS:
            var, parent = GROUPS[name], None
        elif name in PARENTS:
            var = parent = PARENTS[name]
        elif (parent, name) in CHILD:
            var = CHILD[(parent, name)]
        elif name in PLAIN:
            var = PLAIN[name]
            parent = None
        else:
            raise RuntimeError(f"{url}: a label not in the map: {name!r} (under {parent})")
        for year, cell in ((years[0], r[3]), (years[1], r[5])):
            v = cell.strip()
            if v == "":
                continue
            try:
                value = float(v) * 1000.0
            except ValueError:
                raise RuntimeError(f"{url}: {name} {year}: not a number: {v!r}")
            out.append({"entity": "ren:PT", "variable": var, "ts_utc": f"{year}-01-01T00:00:00Z", "value": value, "unit": "MWh",
                        "freq": "P1Y", "geo": "PT", "market": "", "node": "Portugal (mainland)", "source": SOURCE, "source_url": url,
                        "retrieved_at": retrieved, "vintage": vintage})
    return out


def finish(rows):
    t = pd.DataFrame(rows, columns=COLS)
    twice = t[t.duplicated(["entity", "variable", "ts_utc"], keep=False)]
    if len(twice):
        raise RuntimeError(f"a year given twice: {twice.variable.iloc[0]} {twice.ts_utc.iloc[0]}")
    return t.sort_values(["entity", "variable", "ts_utc"]).reset_index(drop=True)


def main(argv=None):
    ap = argparse.ArgumentParser(description="REN Data Hub: Portugal's electricity balance a year")
    ap.add_argument("--decembers", default="2021,2023,2025")
    ap.add_argument("--offline", action="store_true", help="the saved files only, no request")
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
        if not args.offline and (ip.paused("ren") or ip.paused_host("datahub.ren.pt")):
            raise RuntimeError("REN is paused (warehouse/metadata/paused_sources.csv): not requested")
        rows, got = [], []
        for d in [int(x) for x in args.decembers.split(",")]:
            url = URL.format(d=d)
            content, rec = ip.fetch_raw(CONNECTOR, url, log, offline=args.offline, fresh=not args.offline, headers=UA, timeout=120)
            rows += file_rows(content.decode("utf-8-sig"), url, rec.get("retrieved_at") or "", ip.vintage_of(rec))
            got.append((d, rec.get("retrieved_at") or ""))
        t = finish(rows)
        header = [
            f"Energy Research Warehouse (ERW): REN, Data Hub, Portugal's electricity balance a year: production by source, storage, the commercial exchanges and consumption, {t.ts_utc.min()[:4]} to {t.ts_utc.max()[:4]} (session 2280)",
            "Shape: series (docs/datastandard.md v0). entity ren:PT; variable REN's rows in snake case, a parent's children named after it (production_total ... consumption; net_imports negative a net export); "
            "unit MWh (REN's GWh times 1,000); ts_utc the year's 1 January; freq P1Y; geo PT, the balance of mainland Portugal. Each year is a December's year-to-date figure.",
            f"{len(t)} rows, {t.variable.nunique()} variables. A row REN does not print in a year has no row; nothing is filled.",
            f"Retrieved: {run_id} (UTC) by warehouse/connectors/ren_balance.py; the Decembers retrieved " + "; ".join(f"{d} {r}" for d, r in got),
            f"Run log: warehouse/output/logs/{CONNECTOR}_{run_id}.log",
            f"Raw files: warehouse/raw/{CONNECTOR}/ (not in git)",
            f"Source: {SOURCE} REN (Redes Energeticas Nacionais), Data Hub, monthly electricity balance (CSV export, model 1550), {PAGE}",
            f"  access: {URL.format(d='<year>')}",
            "License: internal. The Data Hub's pages state no terms of reuse; internal until a ruling. Cite: REN, Data Hub.",
        ]
        ip.write_csv(t, NAME, header, log, cols=COLS)
        if not args.out_dir:
            ip.update_sources([dict(source=SOURCE, publisher="REN (Redes Energeticas Nacionais)",
                                    report="Data Hub, monthly electricity balance (CSV export, model 1550), Decembers' year-to-date",
                                    report_url=PAGE, document_list=URL.format(d="<year>"), license="internal", tables=[NAME])])
        results.append(dict(table=NAME, market="all", status="ok", detail=f"{len(t)} rows"))
        print(f"{NAME}: {len(t)} rows")
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

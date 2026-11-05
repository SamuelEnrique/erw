#!/usr/bin/env python3
"""Denmark's monthly electricity supply, the country and its two price areas, as the Danish Energy Agency
(Energistyrelsen) publishes it ("Månedlig elstatistik", the monthly electricity supply statistics) (session 2348, chain
109: a third source of the session's own choosing; Statistics Denmark's StatBank holds no monthly electricity table).

Energy Research Warehouse (ERW) connector. One series table, warehouse/output/ens_denmark_electricity_monthly.csv, from
one workbook (no key), linked from https://ens.dk/en/analyses-and-statistics/annual-and-monthly-statistics:

    https://ens.dk/media/8572/download   (an .xls workbook: sheets "Hele landet (Denmark)", "Energinet.dk_Vest (West)",
                                         "Energinet.dk_Øst (East)")

    entity      ens:dk, ens:dk_west or ens:dk_east (the sheet)
    variable    one a column (COLUMNS below): gross and net production and their kinds (central, decentral, industrial
                autoproducers, wind, offshore wind, hydro, solar), net exchange, imports, exports and net exports in all
                and by country (Sweden, Norway, Germany, the Netherlands, England), domestic supply with and without
                losses, primary transmission and distribution losses; on the national sheet columns 13 and 14 are West's
                and East's net exchange, on the area sheets the flows from West to East and from East to West
                (flow_west_to_east, flow_east_to_west); node the column's English label as the agency writes it
    unit        MWh (the workbook's GWh times 1,000); ts_utc the month's first day; freq P1M; geo DK

Only the monthly block is taken (the rows from the first "Januar" on, a year row then its month names); the workbook's
annual, January to August and quarterly blocks are its own sums and are not. A blank cell has no row; nothing is filled.
A sheet missing, a sheet whose column labels differ from the national sheet's (but for case, and for columns 13 and 14), a column label other than the one read in
session 2348, a month name not Danish, a value that is not a number, or a month given twice stops the run.

    python warehouse/connectors/ens_denmark_electricity.py [--offline] [--out-dir DIR]

Ceiling: one request a run, saved in warehouse/raw/ens_electricity/ and fetched again unless --offline. ens.dk's robots
file allows Claude-User by name and every other reader but Drupal's own paths (session 2348). License: not read (the
statistics page states none); internal until a read settles it. The workbook names Energinet as the source of most of
its data.
"""

import argparse
import datetime as dt
import os
import sys
import traceback

import pandas as pd
import xlrd

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import iso_prices as ip  # noqa: E402

NAME = "ens_denmark_electricity_monthly"
CONNECTOR = "ens_electricity"
SOURCE = "ens:monthly_electricity"
HOST = "ens.dk"
URL = "https://ens.dk/media/8572/download"
PAGE = "https://ens.dk/en/analyses-and-statistics/annual-and-monthly-statistics"
UA = {"User-Agent": "Mozilla/5.0 (compatible; ERW-connector/0.1; +https://github.com/SamuelEnrique/erw)"}
SHEETS = {"Hele landet (Denmark)": "dk", "Energinet.dk_Vest (West)": "dk_west", "Energinet.dk_Øst (East)": "dk_east"}
MONTHS = {m: i + 1 for i, m in enumerate(["Januar", "Februar", "Marts", "April", "Maj", "Juni", "Juli", "August", "September",
                                         "Oktober", "November", "December"])}
# column: (variable, the words its English label holds, as read in session 2348)
COLUMNS = {
    2: ("gross_production", "Gross Production"), 3: ("own_use_in_generation", "Use of Electricity in Electricity Generation"),
    4: ("net_production", "Net Prod. Total"), 5: ("central_power_stations", "Central Power Stations"),
    6: ("public_power_stations", "Public Power Stations"), 7: ("industrial_autoproducers", "Industrial Autoproducers"),
    8: ("wind", "Total Wind Turbines"), 9: ("wind_offshore", "Thereof Offshore Wind Turbines"), 10: ("hydro", "Hydro- power"),
    11: ("solar", "Solar Photovoltaic"), 12: ("net_exchange", "Exchange, net"), 13: ("net_exchange_west", "West Denmark"),
    14: ("net_exchange_east", "East Denmark"),
    15: ("imports", "Total"), 16: ("imports_sweden", "Sweden"), 17: ("imports_norway", "Norway"), 18: ("imports_germany", "Germany"),
    19: ("imports_netherlands", "Nederlands"), 20: ("imports_england", "England"),
    21: ("exports", "Total"), 22: ("exports_sweden", "Sweden"), 23: ("exports_norway", "Norway"), 24: ("exports_germany", "Germany"),
    25: ("exports_netherlands", "Nederlands"), 26: ("exports_england", "England"),
    27: ("net_exports", "Total"), 28: ("net_exports_sweden", "Sweden"), 29: ("net_exports_norway", "Norway"),
    30: ("net_exports_germany", "Germany"), 31: ("net_exports_netherlands", "Nederlands"), 32: ("net_exports_england", "England"),
    33: ("domestic_supply_incl_losses", "Total Domestic Supply of Electricity, inc."), 34: ("primary_transmission_losses", "Primary Transmission Losses"),
    35: ("domestic_supply_excl_losses", "Total Domestic Supply of Electricity, exc."), 36: ("distribution_losses", "Distribution losses"),
}
AREA_FLOWS = {13: [("From West to East", "flow_west_to_east")], 14: [("From East to West", "flow_east_to_west")]}
X_COLS = ["x_sheet"]


def label(sh, j):
    """The column's English label: rows 6 to 9 joined, with its group's (Imports, Exports, Net Exports) before a country."""
    words = " ".join(str(sh.cell_value(i, j)).replace("\n", " ").strip() for i in range(6, 10) if str(sh.cell_value(i, j)).strip())
    return " ".join(words.split())


def labels(sh):
    """The labels compared across sheets: every column but 13 and 14, which the area sheets use for the flows between the areas."""
    cols = [j for j in range(2, 37) if j not in AREA_FLOWS]
    return [label(sh, j).lower() for j in cols] + [" ".join(str(sh.cell_value(2, j)).split()).lower() for j in cols]


def variable_of(sh, j):
    """A column's variable; columns 13 and 14 of an area sheet are the flows between West and East, named from their label."""
    if j in AREA_FLOWS and sh.name != "Hele landet (Denmark)":
        lab = label(sh, j)
        for words, var in AREA_FLOWS[j]:
            if words in lab:
                return var
        raise RuntimeError(f"{sh.name} column {j}: not a flow between the areas: {lab!r}")
    return COLUMNS[j][0]


def parse(content, base):
    book = xlrd.open_workbook(file_contents=content)
    missing = [s for s in SHEETS if s not in book.sheet_names()]
    if missing:
        raise RuntimeError(f"sheets missing: {missing}")
    nat = book.sheet_by_name("Hele landet (Denmark)")
    for j, (var, words) in COLUMNS.items():
        if words not in label(nat, j):
            raise RuntimeError(f"column {j} is not {words!r}: {label(nat, j)!r}")
    out = []
    for name, ent in SHEETS.items():
        sh = book.sheet_by_name(name)
        if labels(sh) != labels(nat):
            raise RuntimeError(f"{name}: its column labels differ from the national sheet's")
        start = next((i for i in range(sh.nrows) if str(sh.cell_value(i, 0)).strip() == "Januar"), None)
        if start is None or not isinstance(sh.cell_value(start - 1, 0), float):
            raise RuntimeError(f"{name}: no monthly block (a year row then Januar)")
        year = None
        for i in range(start - 1, sh.nrows):
            c0 = sh.cell_value(i, 0)
            if isinstance(c0, float):
                year = int(c0)
                continue
            c0 = str(c0).strip()
            if not c0:
                continue
            if c0 not in MONTHS:
                if c0[0].isdigit() and ")" in c0[:3]:      # the footnotes after the block
                    break
                raise RuntimeError(f"{name} row {i}: not a Danish month: {c0!r}")
            ts = f"{year}-{MONTHS[c0]:02d}-01T00:00:00Z"
            for j, (var, words) in COLUMNS.items():
                v = sh.cell_value(i, j)
                if v == "" or v is None:
                    continue
                if not isinstance(v, float):
                    raise RuntimeError(f"{name} {ts[:7]} column {j}: not a number: {v!r}")
                out.append(dict(entity=f"ens:{ent}", variable=variable_of(sh, j), ts_utc=ts, value=round(v * 1000, 3), unit="MWh", freq="P1M",
                                geo="DK", market="", node=label(sh, j), **base, x_sheet=name))
    t = pd.DataFrame(out)
    if t.empty:
        raise RuntimeError("no value in the workbook")
    if t.duplicated(["entity", "variable", "ts_utc"]).any():
        raise RuntimeError("a month given twice")
    return t


def main(argv=None):
    ap = argparse.ArgumentParser(description="The Danish Energy Agency's monthly electricity supply statistics")
    ap.add_argument("--offline", action="store_true", help="the saved workbook only, no request")
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
        content, rec = ip.fetch_raw(CONNECTOR, URL, log, offline=args.offline, fresh=not args.offline, headers=UA, timeout=120, pause=1)
        base = dict(source=SOURCE, source_url=URL, retrieved_at=rec.get("retrieved_at") or "", vintage=ip.vintage_of(rec))
        t = parse(content, base)
        cols = ip.SERIES_COLS + X_COLS
        t = t[cols].sort_values(["entity", "variable", "ts_utc"]).reset_index(drop=True)
        g = t[(t.entity == "ens:dk") & (t.variable == "domestic_supply_incl_losses")].assign(y=lambda q: q.ts_utc.str[:4]).groupby("y").value.agg(["sum", "size"])
        g = g[g["size"] == 12]["sum"] / 1e6
        head = [
            "Energy Research Warehouse (ERW): Danish Energy Agency (Energistyrelsen), monthly electricity supply statistics, Denmark and its west and east "
            f"areas, {t.ts_utc.min()[:7]} to {t.ts_utc.max()[:7]} (session 2348)",
            "Shape: series (docs/datastandard.md v0). entity ens:dk, ens:dk_west or ens:dk_east; variable one a column (production and its kinds, "
            "exchange, imports, exports and net exports in all and by country, domestic supply and losses); unit MWh (the workbook's GWh times 1,000); "
            "ts_utc the month's first day; freq P1M; geo DK; node the column's English label; x_sheet the workbook's sheet.",
            f"{len(t)} rows, {t.variable.nunique()} variables; Denmark's domestic supply incl. losses TWh a full year: "
            + ", ".join(f"{k} {v:.2f}" for k, v in g.items() if k >= "2015") + ". Only the monthly block is taken. A blank has no row; nothing is filled.",
            f"Retrieved: {run_id} (UTC) by warehouse/connectors/ens_denmark_electricity.py; the workbook retrieved {base['retrieved_at']}; last modified {base['vintage']}",
            f"Run log: warehouse/output/logs/{CONNECTOR}_{run_id}.log",
            f"Raw files: warehouse/raw/{CONNECTOR}/ (not in git)",
            f"Source: {SOURCE} Danish Energy Agency, Maanedlig elstatistik (monthly electricity supply statistics), {PAGE}",
            f"  access: {URL}",
            "License: internal (no licence or terms stated on the statistics page; not yet read). The workbook names Energinet as the source of most of its data.",
        ]
        ip.write_snapshot(t, NAME, head, log, cols)
        results.append(dict(table=NAME, market="all", status="ok", detail=f"{len(t)} rows"))
        print(f"{NAME}: {len(t)} rows, {t.variable.nunique()} variables, {t.ts_utc.min()[:7]} to {t.ts_utc.max()[:7]}")
    except Exception:
        tb = ip.redact(traceback.format_exc())
        log(f"{NAME} FAILED, no output file written:\n{tb}")
        print(f"{NAME} FAILED, no output file written: {tb.strip().splitlines()[-1]}", file=sys.stderr)
        results.append(dict(table=NAME, market="all", status="failed", detail=tb.strip().splitlines()[-1][:300]))
    if not args.out_dir:
        if results and results[0]["status"] == "ok":
            ip.update_sources([dict(source=SOURCE, publisher="Danish Energy Agency (Energistyrelsen)", report="Monthly electricity supply statistics (workbook)",
                                    report_url=PAGE, document_list=URL, license="internal", tables=[NAME])])
        ip.write_status(CONNECTOR, run_id, results)
    log.close()
    return 0 if all(r["status"] == "ok" for r in results) else 1


if __name__ == "__main__":
    sys.exit(main())

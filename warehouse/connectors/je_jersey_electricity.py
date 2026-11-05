#!/usr/bin/env python3
"""Jersey's electricity balance a year, 2023 to 2025: on-island production, net imports (through the cables from France),
primary supply and demand, the statistical difference, the energy industry's own use and losses, and final consumption by
sector, as the Government of Jersey gives them in the electricity column of the energy balances of its Energy Trends 2025
report (Table 5 for 2025, Appendix Tables A3 and A5 for 2023 and 2024, updated) (session 2594, chain 128, a source of the
session's own choosing; the ERW held Jersey in no table).

Energy Research Warehouse (ERW) connector. One series table, warehouse/output/je_jersey_electricity_annual.csv, from one PDF
(no key):

    https://www.gov.je/SiteCollectionDocuments/Government%20and%20administration/Energy%20Trends%202025.pdf

    entity      je:jersey:<item>: production, net_imports, stock_change, primary_supply, statistical_difference,
                primary_demand, generation_transformation, own_use_and_losses, final_consumption, commercial, residential,
                road, air, marine, agriculture
    variable    electricity
    unit        MWh: the balance's tonnes of oil equivalent times 11.63 (1 toe = 11.63 MWh, the factor the report uses: "2.4
                GWh (209 toe)"); ts_utc the year's first day; freq P1Y; geo JE
    node        the report's label

The balances are in whole toe, so each MWh figure carries the rounding of its toe (at most 5.8 MWh). Each balance's page is
found by its title line; its rows are read for their electricity column (the third of four figures: liquid fuels, gas,
electricity, total), a footnote number after a label removed. Checks within 1 toe: production, net imports and stock
change to primary supply; primary supply less the statistical difference to primary demand; the six sectors to final
consumption. The other columns (liquid fuels, gas, total) are not taken; the report's charts of longer trends are not read.
Nothing is filled.

    python warehouse/connectors/je_jersey_electricity.py [--offline] [--fresh] [--out-dir DIR]

Ceiling: one request a run, saved in warehouse/raw/statsje/ and reused unless --fresh; --offline asks nothing.
www.gov.je's robots file names * with no rule (session 2594). License: internal. gov.je's terms: "Copyright protected
material may be reproduced free of charge in any format or medium for research, private study or for internal circulation
within an organisation."; public republication is not among them; internal until a ruling.
"""

import argparse
import datetime as dt
import io
import os
import re
import sys
import traceback

import pandas as pd
import pdfplumber

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import iso_prices as ip  # noqa: E402

NAME = "je_jersey_electricity_annual"
CONNECTOR = "statsje"
SOURCE = "je_gov:energy_trends_2025_balances"
HOST = "www.gov.je"
URL = "https://www.gov.je/SiteCollectionDocuments/Government%20and%20administration/Energy%20Trends%202025.pdf"
UA = {"User-Agent": "Mozilla/5.0 (compatible; ERW-connector/0.1; +https://github.com/SamuelEnrique/erw)"}
CITATION = "Government of Jersey, Energy Trends 2025, Table 5 and Appendix Tables A3 and A5: energy balances for Jersey, the electricity column"
MWH_PER_TOE = 11.63
TITLES = {r"Table 5: Energy Balance for Jersey, (\d{4}); toe": "5",
          r"Table A3: Energy Balance for Jersey, (\d{4}) \(updated\), toe": "A3",
          r"Table A5: Energy Balance for Jersey, (\d{4}) \(updated\); toe": "A5"}
ROWS = [("Production", "production"), ("Net Imports", "net_imports"), ("Stock change", "stock_change"),
        ("Primary supply", "primary_supply"), ("Statistical difference", "statistical_difference"), ("Primary demand", "primary_demand"),
        ("Electricity Generation", "generation_transformation"), ("Energy industry own use and losses", "own_use_and_losses"),
        ("Final consumption", "final_consumption"), ("Commercial", "commercial"), ("Residential", "residential"), ("Road", "road"),
        ("Air", "air"), ("Marine", "marine"), ("Agriculture", "agriculture")]
SECTORS = ["commercial", "residential", "road", "air", "marine", "agriculture"]
FIG = r"-?\d{1,3}(?:,\d{3})*"
X_COLS = ["x_table", "x_toe"]


def num(s):
    return float(s.replace(",", ""))


def parse_balance(lines, year, table, base):
    vals, out = {}, []
    want = dict(ROWS)
    for ln in lines:
        m = re.fullmatch(r"(.+?) (" + FIG + r") (" + FIG + r") (" + FIG + r") (" + FIG + r")", ln.strip())
        if not m:
            continue
        label = re.sub(r"\d+$", "", m.group(1)).strip()
        if label not in want:
            continue
        item = want[label]
        if item in vals:
            raise RuntimeError(f"{table} {year}: {label!r} given twice")
        toe = num(m.group(4))
        vals[item] = toe
        out.append(dict(entity=f"je:jersey:{item}", variable="electricity", ts_utc=f"{year}-01-01T00:00:00Z",
                        value=round(toe * MWH_PER_TOE, 2), unit="MWh", freq="P1Y", geo="JE", market="", node=label, **base,
                        x_table=table, x_toe=toe))
    missing = [r[0] for r in ROWS if r[1] not in vals]
    if missing:
        raise RuntimeError(f"{table} {year}: rows missing: {missing}")
    g = vals.get
    checks = [(g("primary_supply"), g("production") + g("net_imports") + g("stock_change")),
              (g("primary_demand"), g("primary_supply") - g("statistical_difference")),
              (g("final_consumption"), sum(g(s) for s in SECTORS))]
    for n, (a, b) in enumerate(checks):
        if abs(a - b) > 1:
            raise RuntimeError(f"{table} {year}: check {n + 1} misses: {a} against {b}")
    return out


def parse_pages(pages, base):
    out, years = [], []
    for pat, table in TITLES.items():
        hits = [(i, j) for i, p in enumerate(pages) for j, ln in enumerate(p) if re.fullmatch(pat, ln.strip())]
        if len(hits) != 1:
            raise RuntimeError(f"table {table}: its title found {len(hits)} times")
        i, j = hits[0]
        year = int(re.fullmatch(pat, pages[i][j].strip()).group(1))
        if year in years:
            raise RuntimeError(f"table {table}: the year {year} given twice")
        years.append(year)
        out += parse_balance(pages[i][j + 1:], year, table, base)
    return pd.DataFrame(out)


def parse(content, base):
    with pdfplumber.open(io.BytesIO(content)) as pdf:
        pages = [(pg.extract_text() or "").split("\n") for pg in pdf.pages]
    return parse_pages(pages, base)


def main(argv=None):
    ap = argparse.ArgumentParser(description="Government of Jersey: Jersey's electricity balance, 2023 to 2025 (Energy Trends 2025)")
    ap.add_argument("--offline", action="store_true", help="the saved report only, no request")
    ap.add_argument("--fresh", action="store_true", help="ask for the report again")
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
        content, rec = ip.fetch_raw(CONNECTOR, URL, log, offline=args.offline, fresh=args.fresh, headers=UA, timeout=180, pause=1)
        base = dict(source=SOURCE, source_url=URL, retrieved_at=rec.get("retrieved_at") or "", vintage=ip.vintage_of(rec))
        t = parse(content, base)
        cols = ip.SERIES_COLS + X_COLS
        t = t[cols].sort_values(["entity", "ts_utc"]).reset_index(drop=True)
        v = {(e.split(":")[-1], ts[:4]): val for e, ts, val in zip(t.entity, t.ts_utc, t.value)}
        last = max(t.ts_utc.str[:4])
        head = [
            "Energy Research Warehouse (ERW): Government of Jersey, Energy Trends 2025, the electricity column of its energy balances "
            "for 2023, 2024 and 2025 (session 2594)",
            "Shape: series (docs/datastandard.md v0). entity je:jersey:<item>; variable electricity; unit MWh (the balance's toe times "
            "11.63, the report's own factor; x_toe the toe as printed); ts_utc the year's first day; freq P1Y; geo JE; node the label.",
            f"{len(t)} rows; in {last} net imports {v[('net_imports', last)] / 1e3:,.1f} GWh, production {v[('production', last)] / 1e3:,.1f} GWh, "
            f"final consumption {v[('final_consumption', last)] / 1e3:,.1f} GWh. Each figure carries its toe's rounding (at most 5.8 MWh); "
            "the other fuels' columns are not taken; nothing is filled.",
            f"Retrieved: {run_id} (UTC) by warehouse/connectors/je_jersey_electricity.py; the report retrieved {base['retrieved_at']}; last "
            f"modified {base['vintage']}",
            f"Run log: warehouse/output/logs/{CONNECTOR}_{run_id}.log",
            f"Raw files: warehouse/raw/{CONNECTOR}/ (not in git)",
            f"Source: {SOURCE} {CITATION}",
            f"  access: {URL}",
            "License: internal. gov.je's terms allow reproduction for research, private study or internal circulation within an "
            f"organisation; internal until a ruling. Cite: {CITATION}.",
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
            ip.update_sources([dict(source=SOURCE, publisher="Government of Jersey",
                                    report="Energy Trends 2025, Table 5 and Appendix Tables A3 and A5 (energy balances), the electricity column",
                                    report_url=URL, document_list="https://www.gov.je/", license="internal", tables=[NAME])])
        ip.write_status(CONNECTOR, run_id, results)
    log.close()
    return 0 if all(r["status"] == "ok" for r in results) else 1


if __name__ == "__main__":
    sys.exit(main())

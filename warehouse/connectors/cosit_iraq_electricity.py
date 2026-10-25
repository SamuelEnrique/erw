#!/usr/bin/env python3
"""Iraq's electricity a year, 2021 to 2024: the Ministry of Electricity's production by plant type, the energy bought from
imports and private (investment) plants and from the Kurdistan Region, the total, the energy sold, and the internal consumption
and losses, as the Central Statistical Organization (COSIT, now the Statistics and Geographic Information Systems Authority)
gives them in Tables 1 to 3 of its electricity projects statistics for 2024 (session 2661, chain 133; the ERW held Iraq only in
EIA's world tables).

Energy Research Warehouse (ERW) connector. One series table, warehouse/output/cosit_iraq_electricity_annual.csv, from one
workbook (no key), its tables in Arabic and English side by side:

    https://cosit.gov.iq/documents/industrial/water&electric/6.xlsx

    entity      cosit:iq:<item>: steam, gas, diesel, hydro and generated (variable generation, the Ministry's plants);
                imports_investment, kurdistan and purchased (variable purchases); total (supply); sold (sales);
                losses_plants, losses_transmission, losses_distribution and losses_total (variable losses: internal consumption
                and losses)
    unit        MWh, as published; ts_utc the year's first day; freq P1Y; geo IQ
    node        the row's English label as the table gives it

Each table is found by its English title on any sheet and read by its English labels (the column beside the years); a label not
in the map stops the run. The values in Iraqi dinars, the counts of plants and of workers, and the rates of change are not
taken. Checks: the four plant types add to the energy generated, imports and investment plus the Kurdistan Region to the
purchased total, generated plus purchased to the total, and the three losses to their total, each within 1 MWh; Table 1's
figures equal Table 2's. Nothing is filled. COSIT's earlier workbooks (2015 to 2023) are not read.

    python warehouse/connectors/cosit_iraq_electricity.py [--offline] [--fresh] [--out-dir DIR]

Ceiling: one request a run, saved in warehouse/raw/cosit_iq/ and reused unless --fresh; --offline asks nothing. cosit.gov.iq's
robots file closes Joomla's system paths (among them /images/), not /documents/ (session 2661). License: internal. The site's
footer reserves the rights of its design and making only and states no terms of reuse; internal until a ruling.
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

NAME = "cosit_iraq_electricity_annual"
CONNECTOR = "cosit_iq"
SOURCE = "cosit_iq:electricity_projects_2024_tables_1_3"
HOST = "cosit.gov.iq"
URL = "https://cosit.gov.iq/documents/industrial/water&electric/6.xlsx"
PAGE = "https://cosit.gov.iq/ar/industrial/electric-water"
UA = {"User-Agent": "Mozilla/5.0 (compatible; ERW-connector/0.1; +https://github.com/SamuelEnrique/erw)"}
CITATION = ("Central Statistical Organization, Iraq (COSIT), Electricity projects statistics for 2024, Tables 1 to 3 (source: the "
            "Ministry of Electricity)")
YEARS = [2021, 2022, 2023, 2024]
# each table: (a phrase of its English title, {English label: (ERW item, variable)})
TABLES = {
    "t1": ("Main indicators in the electric energy sector", {
        "Total production of the electricity energy system (MWh)": ("total", "supply"),
        "Quantity of electricity produced (MWh)": ("generated", "generation"),
        "Quantity of electricity sold to consumers (MWh)": ("sold", "sales"),
        "Quantity of imported electricity (MWh)": ("imports_investment", "purchases"),
        "The amount of electricity imported from the Kurdistan Region (MWh)": ("kurdistan", "purchases")}),
    "t2": ("Quantity of electrical energy produced by means of", {
        "Steam plants": ("steam", "generation"), "Gas stations": ("gas", "generation"),
        "Diesel stations + Hyundai diesels + STX diesels": ("diesel", "generation"),
        "Hydroelectric stations": ("hydro", "generation"), "Total Energy Generated": ("generated", "generation"),
        "Imported energy + investment": ("imports_investment", "purchases"),
        "Imported from the Kurdistan region": ("kurdistan", "purchases"), "Grand total": ("purchased", "purchases"),
        "Total Electrical Energy": ("total", "supply")}),
    "t3": ("The amount of internal consumption and losses in transmission", {
        "Internal consumption and losses in production plants": ("losses_plants", "losses"),
        "Internal consumption and losses in transportation networks": ("losses_transmission", "losses"),
        "Internal consumption and losses in distribution networks": ("losses_distribution", "losses"),
        "Total": ("losses_total", "losses")}),
}
NOT_TAKEN_T1 = ("Number of stations", "Revenues", "Value of", "Number of employees", "Wages", "Benefits")
X_COLS = []


def is_num(v):
    return isinstance(v, (int, float)) and not isinstance(v, bool)


def norm(v):
    s = " ".join(str(v).split()) if v is not None else ""
    s = re.sub(r"\s*[.…]*\s*\(\s*\d\s*\)\s*$", "", s)  # a footnote mark: "...... (1)"
    return re.sub(r"\s*[.…]+\s*$", "", s).strip()


def find(rows_by_sheet, phrase):
    hits = [(sh, i) for sh, rows in rows_by_sheet.items() for i, r in enumerate(rows)
            if any(phrase.lower() in " ".join(str(x).split()).lower().replace("ofgenerating", "of generating") for x in r if x is not None)]
    sheets = sorted({sh for sh, _ in hits})
    if len(sheets) != 1:
        raise RuntimeError(f"the table titled {phrase!r} found on {len(sheets)} sheets: {sheets}")
    rows = rows_by_sheet[sheets[0]]
    return rows[min(i for sh, i in hits):]  # from the table's title; another table below it on the sheet ends it


def read_table(rows, labels):
    hd = [i for i, r in enumerate(rows) if [x for x in r if is_num(x)][:4] == YEARS]
    if not hd:
        raise RuntimeError("no header row of the years 2021 to 2024")
    h = rows[hd[0]]
    ycol = [j for j, x in enumerate(h) if is_num(x) and x in YEARS]
    if [h[j] for j in ycol] != YEARS:
        raise RuntimeError(f"the header's years are {[h[j] for j in ycol]}")
    # the English labels' column: the last header after the years in Latin letters (Table 1's rate of change comes before it)
    eng = [j for j in range(ycol[-1] + 1, len(h)) if isinstance(h[j], str) and re.search(r"[A-Za-z]", h[j])]
    if not eng:
        raise RuntimeError("no English label column after the years")
    ecol = eng[-1]
    out, seen = {}, set()
    for r in rows[hd[0] + 1:]:
        if [x for x in r if is_num(x)][:4] == YEARS:
            break  # the next table's header
        lab = norm(r[ecol]) if ecol < len(r) else ""
        if not lab or not any(is_num(r[j]) for j in ycol if j < len(r)):
            continue
        if lab not in labels:
            if any(lab.startswith(p) for p in NOT_TAKEN_T1):
                continue
            raise RuntimeError(f"a row not in the map: {lab!r}")
        if lab in seen:
            raise RuntimeError(f"a row given twice: {lab!r}")
        seen.add(lab)
        for j, y in zip(ycol, YEARS):
            v = r[j]
            if not is_num(v) or v < 0:
                raise RuntimeError(f"{lab} {y}: not a quantity: {v!r}")
            out[(labels[lab][0], y)] = (float(v), lab)
    missing = sorted(set(labels) - seen)
    if missing:
        raise RuntimeError(f"rows missing: {missing}")
    return out


def check(v):
    for y in YEARS:
        g = lambda k: v[(k, y)][0]
        for parts, whole in ((("steam", "gas", "diesel", "hydro"), "generated"), (("imports_investment", "kurdistan"), "purchased"),
                             (("generated", "purchased"), "total"),
                             (("losses_plants", "losses_transmission", "losses_distribution"), "losses_total")):
            s = sum(g(k) for k in parts)
            if abs(s - g(whole)) > 1:
                raise RuntimeError(f"{y}: {'+'.join(parts)} make {s:,.0f} MWh, {whole} {g(whole):,.0f}")


def parse(content, base):
    wb = openpyxl.load_workbook(io.BytesIO(content), data_only=True, read_only=True)
    rows_by_sheet = {ws.title: [tuple(r) for r in ws.iter_rows(values_only=True)] for ws in wb.worksheets}
    t1 = read_table(find(rows_by_sheet, TABLES["t1"][0]), TABLES["t1"][1])
    v = {}
    for k in ("t2", "t3"):
        v.update(read_table(find(rows_by_sheet, TABLES[k][0]), TABLES[k][1]))
    for key, (x, lab) in t1.items():
        if key in v and abs(v[key][0] - x) > 1:
            raise RuntimeError(f"{key}: Table 1 gives {x:,.0f}, Table 2 {v[key][0]:,.0f}")
        v.setdefault(key, (x, lab))
    check(v)
    out = [dict(entity=f"cosit:iq:{item}", variable=var, ts_utc=f"{y}-01-01T00:00:00Z", value=x, unit="MWh", freq="P1Y", geo="IQ",
                market="", node=lab, **base)
           for (item, y), (x, lab) in sorted(v.items())
           for var in [next(vv for t in TABLES.values() for (it, vv) in t[1].values() if it == item)]]
    return pd.DataFrame(out)


def main(argv=None):
    ap = argparse.ArgumentParser(description="COSIT: Iraq's electricity production, purchases, sales and losses a year")
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
        content, rec = ip.fetch_raw(CONNECTOR, URL, log, offline=args.offline, fresh=args.fresh, headers=UA, timeout=180, pause=1)
        base = dict(source=SOURCE, source_url=URL, retrieved_at=rec.get("retrieved_at") or "", vintage=ip.vintage_of(rec))
        t = parse(content, base)
        if t.duplicated(["entity", "variable", "ts_utc"]).any():
            raise RuntimeError("a key given twice")
        cols = ip.SERIES_COLS + X_COLS
        t = t[cols].sort_values(["entity", "ts_utc"]).reset_index(drop=True)
        tot = t[t.entity == "cosit:iq:total"].set_index("ts_utc").value
        head = [
            "Energy Research Warehouse (ERW): Central Statistical Organization, Iraq (COSIT), electricity projects statistics for "
            "2024, Tables 1 to 3: Iraq's electricity production by plant type, purchases, sales and losses, 2021 to 2024 (session 2661)",
            "Shape: series (docs/datastandard.md v0). entity cosit:iq:<item>; variable generation (the Ministry's plants), purchases "
            "(imports and investment, the Kurdistan Region), supply (the total), sales or losses; unit MWh as published; ts_utc the "
            "year's first day; freq P1Y; geo IQ; node the row's English label.",
            f"{len(t)} rows; the total, TWh: " + ", ".join(f"{k[:4]} {v / 1e6:.1f}" for k, v in tot.items())
            + ". Each total checked against its parts, and Table 1 against Table 2; values in dinars not taken; nothing is filled.",
            f"Retrieved: {run_id} (UTC) by warehouse/connectors/cosit_iraq_electricity.py; the workbook retrieved {base['retrieved_at']}; "
            f"last modified {base['vintage']}",
            f"Run log: warehouse/output/logs/{CONNECTOR}_{run_id}.log",
            f"Raw files: warehouse/raw/{CONNECTOR}/ (not in git)",
            f"Source: {SOURCE} {CITATION}",
            f"  access: {URL} (listed on {PAGE})",
            f"License: internal. The site states no terms of reuse (its footer reserves its design only); internal until a ruling. "
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
            ip.update_sources([dict(source=SOURCE, publisher="Central Statistical Organization, Iraq (COSIT)",
                                    report="Electricity projects statistics for 2024, Tables 1 to 3", report_url=URL,
                                    document_list=PAGE, license="internal", tables=[NAME])])
        ip.write_status(CONNECTOR, run_id, results)
    log.close()
    return 0 if all(r["status"] == "ok" for r in results) else 1


if __name__ == "__main__":
    sys.exit(main())

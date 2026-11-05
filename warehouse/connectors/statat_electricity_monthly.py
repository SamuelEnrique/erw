#!/usr/bin/env python3
"""Austria's monthly electricity statistics from January 2023, net production by source and the monthly balance (imports and
exports, pumped storage, losses, consumption), as Statistics Austria (Statistik Austria) gives them in its yearly files "Monthly
electricity statistics" (MEle2023.ods to MEle2026.ods) (session 2795, chain 142: another public grid source in place of CPS
Energy, whose robots file disallows Anthropic's agents by name).

Energy Research Warehouse (ERW) connector. One series table, warehouse/output/statat_austria_electricity_monthly.csv, from one
file a year (no key), OpenDocument spreadsheets read with the standard library (session 2764's streaming reader, copied here):

    https://www.statistik.at/fileadmin/pages/99/MEle<year>.ods     (2023 to 2026; the year in progress fills month by month)

Each file has two sheets in GWh: "NetElectricityProduction" and "SummaryProductionAndSupply". Statistics Austria compiles them
from E-Control's and Eurostat's statistics (each sheet's source line), so they are close to `econtrol_austria_electricity_monthly`.

    entity      statat_mele:at (the totals) or statat_mele:at:<item> (the row as a slug, "of which" dropped: conventional_thermal,
                coal, oil, natural_gas, combustible_renewables, other_combustible_fuels_non_renewable, hydro, pure_hydro,
                mixed_hydro, wind, solar)
    variable    net_production (the production sheet's rows), or imports, imports_from_eu, exports, exports_to_eu,
                pumped_storage_use, losses, consumption (the summary sheet's rows)
    unit        MWh (the files' GWh times 1,000); ts_utc the month's first day; freq P1M; geo AT; node the year and the row
                as written

The summary sheet's own "Total net production" row is not written (the production sheet's is), but the two are compared: they
differ in a few months (May 2026 by 45.9 GWh in October 2026's files), counted in the header. A cell "." (not available, not yet
available) has no row; "-" is zero. Checks, within 0.15 GWh (the files' rounding): the total is the conventional thermal, hydro,
wind and solar rows, compared only in a year whose file lists solar (MEle2023 and MEle2024 list none, and their totals include
it); conventional thermal is its five fuels; hydro is pure and mixed. A difference is counted and kept as
published. A sheet missing, a month row not January to December, a row not in the known structure, a key given twice or a
value not a number stops the run. Nothing is filled.

    python warehouse/connectors/statat_electricity_monthly.py [--offline] [--fresh] [--out-dir DIR]

Ceiling: four requests a run, saved in warehouse/raw/statistik_austria/ and reused unless --fresh (the year in progress is
asked again with --fresh); --offline asks nothing. www.statistik.at's robots file closes only its search pages and names no
Claude agent (session 2795, read 1596). License: Statistics Austria's general terms, section 10 (read 1518): public, crediting
STATISTIK AUSTRIA with edits stated.
"""

import argparse
import datetime as dt
import io
import os
import re
import sys
import traceback
import xml.etree.ElementTree as ET
import zipfile

import pandas as pd

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import iso_prices as ip  # noqa: E402

NAME = "statat_austria_electricity_monthly"
CONNECTOR = "statistik_austria"
SOURCE = "statat:monthly_electricity_statistics"
HOST = "www.statistik.at"
YEARS = [2023, 2024, 2025, 2026]
URL = "https://www.statistik.at/fileadmin/pages/99/MEle{year}.ods"
PAGE = "https://www.statistik.at/en/statistics/energy-and-environment/energy/energy-balances"
UA = {"User-Agent": "Mozilla/5.0 (compatible; ERW-connector/0.1; +https://github.com/SamuelEnrique/erw)"}
CITATION = "STATISTIK AUSTRIA, Monthly electricity statistics (MEle2023 to MEle2026)"
MONTHS = ["January", "February", "March", "April", "May", "June", "July", "August", "September", "October", "November", "December"]
PROD = {"total net production": "total", "conventional thermal": "conventional_thermal", "coal": "coal", "oil": "oil",
        "natural gas": "natural_gas", "combustible renewables": "combustible_renewables",
        "other combustible fuels (non-renewable)": "other_combustible_fuels_non_renewable", "hydro": "hydro",
        "pure hydro": "pure_hydro", "mixed hydro": "mixed_hydro", "wind": "wind", "solar": "solar", "not specified": "not_specified"}
SUMM = {"total net production": None, "total imports": "imports", "from eu": "imports_from_eu", "total exports": "exports",
        "to eu": "exports_to_eu", "used for pumped storage": "pumped_storage_use",
        "transmission and distribution losses": "losses", "total consumption (calculated)": "consumption"}
SUMS = (("total", ["conventional_thermal", "hydro", "wind", "solar", "not_specified"]),
        ("conventional_thermal", ["coal", "oil", "natural_gas", "combustible_renewables", "other_combustible_fuels_non_renewable"]),
        ("hydro", ["pure_hydro", "mixed_hydro"]))
TOL = 0.15  # GWh
X_COLS = []
_T = "{urn:oasis:names:tc:opendocument:xmlns:table:1.0}"
_O = "{urn:oasis:names:tc:opendocument:xmlns:office:1.0}"
_X = "{urn:oasis:names:tc:opendocument:xmlns:text:1.0}"


def sheet_rows(content, name, max_cols=40):
    """The rows of one sheet of an .ods file, read by streaming its content.xml (session 2764's reader)."""
    rows, inside, found = [], False, False
    with zipfile.ZipFile(io.BytesIO(content)).open("content.xml") as f:
        for ev, el in ET.iterparse(f, events=("start", "end")):
            if ev == "start" and el.tag == _T + "table":
                inside = el.get(_T + "name") == name
                found = found or inside
            elif ev == "end" and el.tag == _T + "table":
                if inside:
                    return rows
                el.clear()
            elif ev == "end" and el.tag == _T + "table-row":
                if inside:
                    row = []
                    for c in el:
                        if c.tag not in (_T + "table-cell", _T + "covered-table-cell"):
                            continue
                        n = int(c.get(_T + "number-columns-repeated", "1"))
                        v = c.get(_O + "value")
                        if v is None:
                            v = " ".join("".join(p.itertext()) for p in c.findall(_X + "p")) or None
                        else:
                            v = float(v)
                        row += [v] * min(n, max_cols - len(row))
                        if len(row) >= max_cols:
                            break
                    while row and row[-1] is None:
                        row.pop()
                    rr = int(el.get(_T + "number-rows-repeated", "1"))
                    rows += [row] * (rr if row else 1)
                el.clear()
    raise RuntimeError(f"no sheet named {name!r}" if not found else f"the sheet {name!r} did not end")


def label(s):
    s = " ".join(str(s).split()).lower()
    return re.sub(r"^(out of which |of which )", "", s)


def read_sheet(rows, mapping, where):
    head = [i for i, r in enumerate(rows) if len(r) >= 13 and [str(x) for x in r[1:13]] == MONTHS]
    if len(head) != 1:
        raise RuntimeError(f"{where}: no single month row")
    out = {}
    for r in rows[head[0] + 1:]:
        if not r or r[0] is None:
            continue
        lab = label(r[0])
        if lab.startswith("s: "):
            break
        if lab not in mapping:
            raise RuntimeError(f"{where}: a row not in the known structure: {r[0]!r}")
        if lab in out:
            raise RuntimeError(f"{where}: {r[0]!r} given twice")
        vals = []
        for m in range(12):
            v = r[1 + m] if 1 + m < len(r) else None
            if isinstance(v, float):
                vals.append(v)
            elif v in (None, ".") or (isinstance(v, str) and v.strip() == "."):
                vals.append(None)
            elif isinstance(v, str) and v.strip() == "-":
                vals.append(0.0)
            else:
                raise RuntimeError(f"{where} {r[0]!r} {MONTHS[m]}: not a number: {v!r}")
        out[lab] = (vals, " ".join(str(r[0]).split()))
    return out


def parse(files):
    """files: {year: content}. Returns {(year, month, variable, item): (GWh, node)}, the counted differences."""
    vals, counted = {}, []
    for y, content in sorted(files.items()):
        prod = read_sheet(sheet_rows(content, "NetElectricityProduction"), PROD, f"{y} production")
        summ = read_sheet(sheet_rows(content, "SummaryProductionAndSupply"), SUMM, f"{y} summary")
        for lab, (vs, node) in prod.items():
            for m, v in enumerate(vs):
                if v is not None:
                    vals[(y, m + 1, "net_production", PROD[lab])] = (v, f"{y} {node}")
        for lab, (vs, node) in summ.items():
            if SUMM[lab] is None:
                continue
            for m, v in enumerate(vs):
                if v is not None:
                    vals[(y, m + 1, SUMM[lab], "total")] = (v, f"{y} {node}")
        pt, st = prod.get("total net production"), summ.get("total net production")
        for m in range(12):
            g = lambda item: vals.get((y, m + 1, "net_production", item), (None,))[0]
            if pt and st and pt[0][m] is not None and st[0][m] is not None and abs(pt[0][m] - st[0][m]) > TOL:
                counted.append((f"{y}-{m + 1:02d}", "summary total", round(st[0][m] - pt[0][m], 1)))
            for parent, kids in SUMS:
                if g(parent) is None or all(g(k) is None for k in kids):
                    continue
                if parent == "total" and "solar" not in prod:
                    continue  # the year's file lists no solar row, which its total includes
                s = sum(g(k) or 0.0 for k in kids)
                if abs(s - g(parent)) > TOL:
                    counted.append((f"{y}-{m + 1:02d}", parent, round(s - g(parent), 1)))
    return vals, counted


def frame(vals, base_of):
    rows = []
    for (y, m, var, item), (v, node) in sorted(vals.items()):
        rows.append(dict(entity="statat_mele:at" if item == "total" else f"statat_mele:at:{item}", variable=var,
                         ts_utc=f"{y}-{m:02d}-01T00:00:00Z", value=round(v * 1000.0, 3), unit="MWh", freq="P1M", geo="AT",
                         market="", node=node, **base_of[y]))
    return pd.DataFrame(rows)


def main(argv=None):
    ap = argparse.ArgumentParser(description="Statistics Austria: Austria's monthly electricity statistics from 2023")
    ap.add_argument("--offline", action="store_true", help="the saved files only, no request")
    ap.add_argument("--fresh", action="store_true", help="ask for the files again")
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
        files, base_of = {}, {}
        for y in YEARS:
            url = URL.format(year=y)
            content, rec = ip.fetch_raw(CONNECTOR, url, log, offline=args.offline, fresh=args.fresh, headers=UA, timeout=180, pause=1)
            files[y] = content
            base_of[y] = dict(source=SOURCE, source_url=url, retrieved_at=rec.get("retrieved_at") or "", vintage=ip.vintage_of(rec))
        vals, counted = parse(files)
        for k, p, dd in counted:
            log(f"  {p} less its parts or the production sheet: {dd:+.1f} GWh in {k}, kept as published")
        t = frame(vals, base_of)
        if t.duplicated(["entity", "variable", "ts_utc"]).any():
            raise RuntimeError("a key given twice")
        cols = ip.SERIES_COLS + X_COLS
        t = t[cols].sort_values(["variable", "entity", "ts_utc"]).reset_index(drop=True)
        tot = t[(t.entity == "statat_mele:at") & (t.variable == "net_production")]
        head = [
            "Energy Research Warehouse (ERW): Statistics Austria, Monthly electricity statistics (MEle2023 to MEle2026): Austria's "
            f"net production by source and its monthly balance, {t.ts_utc.min()[:7]} to {t.ts_utc.max()[:7]} (session 2795)",
            "Shape: series (docs/datastandard.md v0). entity statat_mele:at or statat_mele:at:<source>; variable net_production, "
            "imports, imports_from_eu, exports, exports_to_eu, pumped_storage_use, losses or consumption; unit MWh (the files' GWh "
            "times 1,000); ts_utc the month's first day; freq P1M; geo AT; node the year and the row. Compiled by Statistics Austria "
            "from E-Control's and Eurostat's statistics.",
            f"{len(t)} rows; net production, MWh: " + ", ".join(f"{r.ts_utc[:7]} {r.value:,.0f}" for r in tot.iloc[[0, -1]].itertuples())
            + f". The totals compared with their parts and the two sheets' totals with each other, within {TOL:g} GWh; "
            f"{len(counted)} differences kept as published (" + ", ".join(f"{p} {k}" for k, p, _ in counted) + "); \".\" has no row; "
            "nothing is filled.",
            f"Retrieved: {run_id} (UTC) by warehouse/connectors/statat_electricity_monthly.py; the files retrieved "
            + ", ".join(f"{y} {base_of[y]['retrieved_at']}" for y in YEARS),
            f"Run log: warehouse/output/logs/{CONNECTOR}_{run_id}.log",
            f"Raw files: warehouse/raw/{CONNECTOR}/ (not in git)",
            f"Source: {SOURCE} {CITATION}",
            f"  access: {URL.format(year='<year>')} (listed on {PAGE})",
            "License: Statistics Austria's general terms, section 10: reproduction and distribution with the source cited and edits "
            "stated. Credit: STATISTIK AUSTRIA; edited by the ERW (GWh written as MWh, reshaped).",
        ]
        ip.write_snapshot(t, NAME, head, log, cols)
        results.append(dict(table=NAME, market="all", status="ok", detail=f"{len(t)} rows"))
        print(f"{NAME}: {len(t)} rows, {t.entity.nunique()} entities; counted {counted}")
    except Exception:
        tb = ip.redact(traceback.format_exc())
        log(f"{NAME} FAILED, no output file written:\n{tb}")
        print(f"{NAME} FAILED, no output file written: {tb.strip().splitlines()[-1]}", file=sys.stderr)
        results.append(dict(table=NAME, market="all", status="failed", detail=tb.strip().splitlines()[-1][:300]))
    if not args.out_dir:
        if results and results[0]["status"] == "ok":
            ip.update_sources([dict(source=SOURCE, publisher="Statistics Austria (Statistik Austria)",
                                    report="Monthly electricity statistics (MEle2023 to MEle2026)", report_url=PAGE,
                                    document_list=PAGE, license="public", tables=[NAME])])
        ip.write_status(CONNECTOR, run_id, results)
    log.close()
    return 0 if all(r["status"] == "ok" for r in results) else 1


if __name__ == "__main__":
    sys.exit(main())

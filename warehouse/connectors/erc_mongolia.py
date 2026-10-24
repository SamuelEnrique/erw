#!/usr/bin/env python3
"""Mongolia's electricity a year, 2015 to 2020, from the Energy Regulatory Commission's "Statistics on Energy Performance"
(English edition, the report of 2020): generation by type of plant and imports, installed capacity by type, and
electricity sales by integrated power grid and class of consumer (session 2422, chain 115: Mongolia's electricity).

Energy Research Warehouse (ERW) connector. One series table, warehouse/output/erc_mongolia_electricity_annual.csv, from
three tables of the report (read with pdfplumber's table extraction), one request:

    http://admin.erc.gov.mn/uploads/files/statisticseng.pdf

    entity     erc_mn:MN (the country) or erc_mn:<grid> (cripg, wripg, eripg, auipg, srpdg: the central, western, eastern
               and Altai-Uliastai integrated power grids and the southern region distribution network); geo MN
    variable   generation_<type> (chp, diesel, solar, hydro, wind, total) and imports, MWh (ERC's GWh times 1,000);
               capacity_<type> (chp, renewable, diesel, total), MW; sales_<class> (entity_industry, apartment,
               ger_district, total), MWh, for each grid and the country ("Total for the Sector")
    ts_utc     the year's 1 January; freq P1Y

Checks: the types add to the total generation within 1 GWh (2020's add to 7,144.9 against a printed 7,145.6; the
report's text says 7,145.7; a gap over 0.15 is named in the header), the capacity types to the installed capacity within 0.15, each grid's classes
to its total and the five grids to the sector's within 0.6 (CRIPG's 2017 and 2018 figures are printed as whole numbers); a header not ERC's, a row not in the map, a value
that is not a number or a failed check stops the run. The capacity table's unit label reads "GWh"; its figures are MW
(1,485.3 in 2020, the country's installed capacity), and are written as MW. One sales figure is printed with a space
("5,033 .2", CRIPG's 2019 total) and is read as 5,033.2. The percentage rows are not taken.

The newer editions (2021 to 2025) are published on erc.gov.mn/mn/statistic only as pictures, which are not read; this
is the newest edition published as a document (session 2422). Statistics Mongolia's www.1212.mn answers with a
certificate that fails verification, and opendata.1212.mn does not resolve.

    python warehouse/connectors/erc_mongolia.py [--offline] [--out-dir DIR]

Ceiling: one request, reused from warehouse/raw/erc_mongolia/ with --offline. erc.gov.mn's and admin.erc.gov.mn's
robots files disallow nothing (every line is a comment) and name no AI agent (session 2422). License: internal until a
ruling: the site shows a copyright sign and states no terms of reuse.
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

NAME = "erc_mongolia_electricity_annual"
CONNECTOR = "erc_mongolia"
SOURCE = "erc_mn:statistics_on_energy_performance"
PAGE = "https://erc.gov.mn/mn/statistic"
URL = "http://admin.erc.gov.mn/uploads/files/statisticseng.pdf"
UA = {"User-Agent": "Mozilla/5.0 (compatible; ERW-connector/0.1; +https://github.com/SamuelEnrique/erw)"}
COLS = ["entity", "variable", "ts_utc", "value", "unit", "freq", "geo", "market", "node", "source", "source_url",
        "retrieved_at", "vintage"]
GEN = {"Combined heat and power plant": "chp", "Diesel station": "diesel", "Solar photovoltaic": "solar",
       "Hydro power plant": "hydro", "Wind power plant": "wind", "Total generation": "total", "Import": "imports"}
CAP = {"Here of CHPPs": "chp", "RE sources": "renewable", "Diesel stations": "diesel", "Installed capacity": "total"}
GRIDS = {"CRIPG": ("cripg", "Central Region Integrated Power Grid"), "WRIPG": ("wripg", "Western Region Integrated Power Grid"),
         "ERIPG": ("eripg", "Eastern Region Integrated Power Grid"), "AUIPG": ("auipg", "Altai-Uliastai Integrated Power Grid"),
         "SRPDG": ("srpdg", "Southern Region Power Distribution Network"), "Total for the Sector": ("MN", "Mongolia")}
CLASSES = {"E&I": "entity_industry", "Ap": "apartment", "GD": "ger_district", "Total": "total"}
TOL = 0.15


def label(c):
    return re.sub(r"\s+", " ", c or "").strip()


def num(cell, what):
    s = re.sub(r"(\d) \.(\d)", r"\1.\2", (cell or "").strip())  # "5,033 .2" as printed
    if not re.fullmatch(r"\d{1,3}(,\d{3})*(\.\d+)?|\d+(\.\d+)?", s):
        raise RuntimeError(f"{what}: not a number: {cell!r}")
    return float(s.replace(",", ""))


def years_of(head, first, what):
    ys = [int(c) for c in head[first:] if c and re.fullmatch(r"\d{4}", c.strip())]
    if len(ys) != len(head) - first or ys != list(range(ys[0], ys[0] + len(ys))):
        raise RuntimeError(f"{what}: the years are not ERC's: {head}")
    return ys


def adds(parts, total, what, tol=TOL):
    if abs(sum(parts) - total) > tol:
        raise RuntimeError(f"{what}: the parts add to {sum(parts):.2f}, the printed total is {total}")


def parse(tables):
    """The rows from the report's tables (every page's, as pdfplumber gives them): (entity, node, variable, year, value, unit)."""
    def find(first, what, second=None):
        got = [t for t in tables if t and label(t[0][0]) == first and (second is None or (len(t[0]) > 1 and label(t[0][1]) == second))]
        if len(got) != 1:
            raise RuntimeError(f"{len(got)} tables headed {first!r}, not one ({what})")
        return got[0]
    out = []

    t = find("Generation set", "generation")
    ys = years_of(t[0], 1, "generation")
    gen = {}
    for r in t[1:]:
        k = label(r[0])
        if k not in GEN:
            raise RuntimeError(f"generation: a row not in the map: {k!r}")
        gen[GEN[k]] = [num(c, f"generation {k}") for c in r[1:]]
    if set(gen) != set(GEN.values()):
        raise RuntimeError(f"generation: rows missing: {set(GEN.values()) - set(gen)}")
    gaps = {}
    for i, y in enumerate(ys):
        parts = [gen[s][i] for s in ("chp", "diesel", "solar", "hydro", "wind")]
        adds(parts, gen["total"][i], f"generation {y}", tol=1.0)
        if abs(sum(parts) - gen["total"][i]) > TOL:
            gaps[y] = (round(sum(parts), 1), gen["total"][i])
        for s, v in gen.items():
            var = "imports" if s == "imports" else f"generation_{s}"
            out.append(("MN", "Mongolia", var, y, v[i] * 1000, "MWh"))

    t = find("Generation sets", "capacity")
    ys = years_of(t[0], 1, "capacity")
    cap = {}
    for r in t[1:]:
        k = label(r[0])
        if k == "Percentage":
            continue
        if k not in CAP:
            raise RuntimeError(f"capacity: a row not in the map: {k!r}")
        cap[CAP[k]] = [num(c, f"capacity {k}") for c in r[1:]]
    if set(cap) != set(CAP.values()):
        raise RuntimeError(f"capacity: rows missing: {set(CAP.values()) - set(cap)}")
    for i, y in enumerate(ys):
        adds([cap[s][i] for s in ("chp", "renewable", "diesel")], cap["total"][i], f"capacity {y}")
        for s, v in cap.items():
            out.append(("MN", "Mongolia", f"capacity_{s}", y, v[i], "MW"))

    t = find("Grid", "sales", second="Classification")
    ys = years_of(t[0], 2, "sales")
    sales, grid = {}, None
    for r in t[1:]:
        if r[0]:
            grid = label(r[0])
            if grid not in GRIDS:
                raise RuntimeError(f"sales: a grid not in the map: {grid!r}")
        k = label(r[1])
        if grid is None or k not in CLASSES:
            raise RuntimeError(f"sales: a row that does not read: {r}")
        sales.setdefault(grid, {})[CLASSES[k]] = [num(c, f"sales {grid} {k}") for c in r[2:]]
    if set(sales) != set(GRIDS) or any(set(v) != set(CLASSES.values()) for v in sales.values()):
        raise RuntimeError("sales: a grid or class missing")
    for i, y in enumerate(ys):
        for g, v in sales.items():
            adds([v[c][i] for c in ("entity_industry", "apartment", "ger_district")], v["total"][i], f"sales {g} {y}", tol=0.6)
        for c in CLASSES.values():
            adds([sales[g][c][i] for g in GRIDS if g != "Total for the Sector"], sales["Total for the Sector"][c][i], f"sales {c} {y}", tol=0.6)
        for g, v in sales.items():
            code, node = GRIDS[g]
            for c, vals in v.items():
                out.append((code, node, f"sales_{c}", y, vals[i] * 1000, "MWh"))
    return out, gaps


def finish(rows, retrieved, vintage):
    t = pd.DataFrame([dict(entity=f"erc_mn:{e}", variable=v, ts_utc=f"{y}-01-01T00:00:00Z", value=round(x, 3), unit=u, freq="P1Y",
                           geo="MN", market="", node=n, source=SOURCE, source_url=URL, retrieved_at=retrieved, vintage=vintage)
                      for e, n, v, y, x, u in rows], columns=COLS)
    if t.duplicated(["entity", "variable", "ts_utc"]).any():
        raise RuntimeError("a key given twice")
    return t.sort_values(["entity", "variable", "ts_utc"]).reset_index(drop=True)


def main(argv=None):
    ap = argparse.ArgumentParser(description="ERC Mongolia's Statistics on Energy Performance: generation, imports, capacity and sales, 2015 to 2020")
    ap.add_argument("--offline", action="store_true", help="the saved report only, no request")
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
        if not args.offline and (ip.paused("erc_mn") or ip.paused_host("admin.erc.gov.mn")):
            raise RuntimeError("ERC Mongolia is paused (warehouse/metadata/paused_sources.csv): not requested")
        content, rec = ip.fetch_raw(CONNECTOR, URL, log, offline=args.offline, headers=UA, timeout=300)
        with pdfplumber.open(io.BytesIO(content)) as pdf:
            tables = [t for p in pdf.pages[:30] for t in p.extract_tables()]
        rows, gaps = parse(tables)
        t = finish(rows, rec.get("retrieved_at") or "", ip.vintage_of(rec))
        header = [
            f"Energy Research Warehouse (ERW): Energy Regulatory Commission of Mongolia (ERC), Statistics on Energy Performance (English, 2020 edition): generation by type and imports, installed capacity, and sales by grid and class, {t.ts_utc.min()[:4]} to {t.ts_utc.max()[:4]} (session 2422)",
            "Shape: series (docs/datastandard.md v0). entity erc_mn:MN (the country) or erc_mn:<grid> (cripg, wripg, eripg, auipg, srpdg); variable generation_<chp|diesel|solar|hydro|wind|total> and imports (MWh, ERC's GWh times 1,000), capacity_<chp|renewable|diesel|total> (MW), "
            "sales_<entity_industry|apartment|ger_district|total> (MWh; ERC's E&I, Ap and GD: entity and industry, apartment, ger district); ts_utc the year's 1 January; freq P1Y; geo MN.",
            f"{len(t)} rows. The types add to the totals, within 0.15 in ERC's units, and each grid's classes to its total and the grids to the sector's within 0.6 (CRIPG's 2017 and 2018 sales are printed as whole numbers)"
            + "".join(f" (but {y}'s types add to {a:,.1f} GWh against the printed total generation {b:,.1f}, kept as printed)" for y, (a, b) in gaps.items())
            + ". The capacity table's unit label reads GWh; its figures are MW and are written as MW. CRIPG's 2019 sales total is printed \"5,033 .2\" and read as 5,033.2. Nothing is filled.",
            "ERC publishes its 2021 to 2025 statistics only as pictures, not read; this 2020 edition is the newest published as a document.",
            f"Retrieved: {run_id} (UTC) by warehouse/connectors/erc_mongolia.py; the report retrieved {rec.get('retrieved_at') or ''}",
            f"Run log: warehouse/output/logs/{CONNECTOR}_{run_id}.log",
            f"Raw files: warehouse/raw/{CONNECTOR}/ (not in git)",
            f"Source: {SOURCE} Energy Regulatory Commission of Mongolia, Statistics on Energy Performance (English), the electricity generation, installed capacity and electricity sales volume tables, {PAGE}",
            f"  access: {URL}",
            "License: internal. ERC's site shows a copyright sign and states no terms of reuse; internal until a ruling. Cite: Energy Regulatory Commission of Mongolia, Statistics on Energy Performance 2020.",
        ]
        ip.write_csv(t, NAME, header, log, cols=COLS)
        if not args.out_dir:
            ip.update_sources([dict(source=SOURCE, publisher="Energy Regulatory Commission of Mongolia (ERC)",
                                    report="Statistics on Energy Performance, English edition of 2020 (generation, imports, installed capacity, sales by grid)",
                                    report_url=PAGE, document_list=URL, license="internal", tables=[NAME])])
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

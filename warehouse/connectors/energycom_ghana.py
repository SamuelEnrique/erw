#!/usr/bin/env python3
"""Ghana's electricity generation by source, imports and exports, and peak load, a year from 2000, from the Energy
Commission's National Energy Statistical Bulletin 2026 (session 2373, chain 112: Ghana's generation).

Energy Research Warehouse (ERW) connector. One series table, warehouse/output/energycom_ghana_electricity_annual.csv,
from three tables of the bulletin (a PDF, read with pdfplumber's table extraction), one request:

    https://www.energycom.gov.gh/index.php/planning/energy-statistics?download=855:2026-energy-statistics

    Table 3.7  Annual Electricity Generation: hydro, thermal, other renewables, total (GWh)
    Table 3.8  Electricity Import and Export (GWh): import, export, net export
    Table 3.9  Ghana and System Peak Load (MW): Ghana peak (ECG, NEDCo, mines, VALCO and direct customers), system peak
               (Ghana peak plus export load)

    entity    energycom:GH; geo GH; node Ghana; ts_utc the year's 1 January; freq P1Y
    variable  generation_hydro, generation_thermal, generation_other_renewables, generation_total, imports, exports,
              net_exports (MWh, the bulletin's GWh times 1,000); peak_ghana, peak_system (MW)

pdfplumber gives the rows with their cells shifted on alternate lines; each row's non-empty cells are read in order
(year, then the values, then the shares, which are not taken). Hydro, thermal and other renewables must add to the total,
and exports less imports to net exports, within 1.5 GWh; a year, header or value that does not read stops the run. A
dash (before other renewables began, 2013) has no row; nothing is filled. The bulletin's footnote 8 says its
generation "includes embedded generation and import". A year whose Ghana peak is above its system peak, which the
bulletin defines as Ghana's plus exports, is kept as published and named in the header.

    python warehouse/connectors/energycom_ghana.py [--offline] [--out-dir DIR]

Ceiling: one request, reused from warehouse/raw/energycom_ghana/ with --offline. www.energycom.gov.gh's robots file
allows every path and asks a crawl delay of 3 seconds; it names no AI agent (session 2373). License: internal until a
ruling: the bulletin states no terms of reuse, and the site's "Terms & Condition" link leads to its home page.
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

NAME = "energycom_ghana_electricity_annual"
CONNECTOR = "energycom_ghana"
SOURCE = "energycom:national_energy_statistics"
PAGE = "https://www.energycom.gov.gh/index.php/planning/energy-statistics"
URL = "https://www.energycom.gov.gh/index.php/planning/energy-statistics?download=855:2026-energy-statistics"
TABLES = {"Annual Electricity Generation": (["generation_hydro", "generation_thermal", "generation_other_renewables", "generation_total"], "MWh", 1000.0),
          "Electricity Import and Export": (["imports", "exports", "net_exports"], "MWh", 1000.0),
          "Ghana and System Peak Load": (["peak_ghana", "peak_system"], "MW", 1.0)}
TOL = 1.5
UA = {"User-Agent": "Mozilla/5.0 (compatible; ERW-connector/0.1; +https://github.com/SamuelEnrique/erw)"}
COLS = ["entity", "variable", "ts_utc", "value", "unit", "freq", "geo", "market", "node", "source", "source_url",
        "retrieved_at", "vintage"]


def num(s, what):
    s = s.strip()
    if s == "-":
        return None
    if not re.fullmatch(r"-?\d{1,3}(,\d{3})*(\.\d+)?|-?\d+(\.\d+)?", s):
        raise RuntimeError(f"{what}: not a number: {s!r}")
    return float(s.replace(",", ""))


def table_values(table, names, what):
    """{year: [value or None for each name]} from a table's rows whose first non-empty cell is a year."""
    out = {}
    for row in table:
        cells = [(c or "").strip() for c in row]
        cells = [c for c in cells if c]
        if not cells or not re.fullmatch(r"(19|20)\d\d", cells[0]):
            continue
        y = int(cells[0])
        if len(cells) < 1 + len(names):
            raise RuntimeError(f"{what} {y}: {len(cells) - 1} values, not {len(names)}: {cells}")
        if y in out:
            raise RuntimeError(f"{what}: {y} given twice")
        out[y] = [num(c, f"{what} {y}") for c in cells[1:1 + len(names)]]
    if not out:
        raise RuntimeError(f"{what}: no year read")
    return out


def bulletin_rows(content, retrieved, vintage):
    found = {}
    with pdfplumber.open(io.BytesIO(content)) as pdf:
        for page in pdf.pages:
            text = page.extract_text() or ""
            for title, (names, unit, f) in TABLES.items():
                if title in found or not re.search(r"Table 3\.\d+: " + re.escape(title), text):
                    continue
                tables = [t for t in page.extract_tables() if sum(1 for r in t if any(re.fullmatch(r"(19|20)\d\d", (c or "").strip()) for c in r)) >= 10]
                if not tables:   # the contents page names the table too
                    continue
                if len(tables) > 1:
                    raise RuntimeError(f"{title}: {len(tables)} tables of years on its page, not one")
                found[title] = table_values(tables[0], names, title)
    missing = [t for t in TABLES if t not in found]
    if missing:
        raise RuntimeError(f"tables not found: {missing}")
    gen, trade = found["Annual Electricity Generation"], found["Electricity Import and Export"]
    for y, (h, t, o, tot) in gen.items():
        if abs(h + t + (o or 0) - tot) > TOL:
            raise RuntimeError(f"generation {y}: hydro, thermal and other add to {h + t + (o or 0)}, the total is {tot}")
    for y, (im, ex, net) in trade.items():
        if abs(ex - im - net) > TOL:
            raise RuntimeError(f"trade {y}: exports less imports are {ex - im}, net exports {net}")
    out = []
    base = dict(entity="energycom:GH", freq="P1Y", geo="GH", market="", node="Ghana", source=SOURCE, source_url=URL,
                retrieved_at=retrieved, vintage=vintage)
    for title, (names, unit, f) in TABLES.items():
        for y, vals in found[title].items():
            for name, v in zip(names, vals):
                if v is not None:
                    out.append(dict(base, variable=name, ts_utc=f"{y}-01-01T00:00:00Z", value=v * f, unit=unit))
    peak = found["Ghana and System Peak Load"]
    above = [y for y, (g, s) in sorted(peak.items()) if g > s]
    return out, above


def finish(rows):
    t = pd.DataFrame(rows, columns=COLS)
    if t.duplicated(["entity", "variable", "ts_utc"]).any():
        raise RuntimeError("a key given twice")
    return t.sort_values(["entity", "variable", "ts_utc"]).reset_index(drop=True)


def main(argv=None):
    ap = argparse.ArgumentParser(description="Energy Commission Ghana: electricity generation, trade and peak load, a year")
    ap.add_argument("--offline", action="store_true", help="the saved bulletin only, no request")
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
        if not args.offline and (ip.paused("energycom") or ip.paused_host("www.energycom.gov.gh")):
            raise RuntimeError("the Energy Commission is paused (warehouse/metadata/paused_sources.csv): not requested")
        content, rec = ip.fetch_raw(CONNECTOR, URL, log, offline=args.offline, fresh=not args.offline, headers=UA, timeout=300)
        rows, above = bulletin_rows(content, rec.get("retrieved_at") or "", ip.vintage_of(rec))
        t = finish(rows)
        header = [
            f"Energy Research Warehouse (ERW): Energy Commission, Ghana, National Energy Statistical Bulletin 2026, electricity generation by source, imports and exports, and peak load, {t.ts_utc.min()[:4]} to {t.ts_utc.max()[:4]} (session 2373)",
            "Shape: series (docs/datastandard.md v0). entity energycom:GH; variable generation_hydro, generation_thermal, generation_other_renewables, generation_total, imports, exports, net_exports (MWh, the bulletin's GWh times 1,000), "
            "peak_ghana, peak_system (MW); ts_utc the year's 1 January; freq P1Y; geo GH. The bulletin's generation includes embedded generation and import (its footnote 8); the system peak is Ghana's peak plus export load.",
            f"{len(t)} rows, {t.variable.nunique()} variables. The sources add to the total, and exports less imports to net exports, within 1.5 GWh. A dash has no row; nothing is filled. "
            f"Years whose Ghana peak is above the system peak, as published: {', '.join(map(str, above)) or 'none'}.",
            f"Retrieved: {run_id} (UTC) by warehouse/connectors/energycom_ghana.py; the bulletin retrieved {rec.get('retrieved_at') or ''}",
            f"Run log: warehouse/output/logs/{CONNECTOR}_{run_id}.log",
            f"Raw files: warehouse/raw/{CONNECTOR}/ (not in git)",
            f"Source: {SOURCE} Energy Commission, Ghana, 2026 National Energy Statistical Bulletin, tables 3.7, 3.8 and 3.9, {PAGE}",
            f"  access: {URL}",
            "License: internal. The bulletin states no terms of reuse; internal until a ruling. Cite: Energy Commission, Ghana, National Energy Statistical Bulletin 2026.",
        ]
        ip.write_csv(t, NAME, header, log, cols=COLS)
        if not args.out_dir:
            ip.update_sources([dict(source=SOURCE, publisher="Energy Commission, Ghana",
                                    report="National Energy Statistical Bulletin 2026, tables 3.7 (generation), 3.8 (imports and exports) and 3.9 (peak load)",
                                    report_url=PAGE, document_list=URL, license="internal", tables=[NAME])])
        results.append(dict(table=NAME, market="all", status="ok", detail=f"{len(t)} rows"))
        print(f"{NAME}: {len(t)} rows; Ghana peak above system peak in {above}")
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

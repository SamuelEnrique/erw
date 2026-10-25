#!/usr/bin/env python3
"""Paraguay's electricity balance, 2023 and 2024: gross generation by plant type (the Acaray hydro plant, Paraguay's
share of the binational plants, thermal plants, autoproducers), imports, exports, the plants' own use, losses, supply and
final consumption by sector, as the Viceministerio de Minas y Energia (VMME) of the Ministerio de Obras Publicas y
Comunicaciones gives them in "Cuadro 3: Comparativo balance de electricidad" of its Balance Energetico Nacional 2024
(August 2025, preliminary) (session 2572, chain 126, a source of the session's own choosing; the ERW held Paraguay only
in EIA's international table, and chain 114's session 2406 could not read ANDE's pages).

Energy Research Warehouse (ERW) connector. One series table, warehouse/output/vmme_paraguay_electricity_annual.csv, from
one PDF (no key):

    https://minasyenergia.mopc.gov.py/pdf/balance2024/BEN 2024_Paraguay.pdf

    entity      vmme:py:<item>
    variable    gross_generation (total, power_plants, acaray_hydro, binational_hydro, thermal, autoproducers);
                imports, exports, own_use (total); losses (total, transmission, distribution); supply (total);
                final_consumption (total, industrial, residential, other_sectors, commercial_public, unspecified)
    unit        MWh (VMME's GWh times 1,000); ts_utc the year's first day; freq P1Y; geo PY
    node        VMME's label

The balance prints exports, own use and losses with a minus sign (they leave the supply); they are written here as
positive quantities. The table's page is found by its title line as printed above the table (the contents page prints
it with a page number after it) and read from the title to "CONSUMO FINAL". The page's text carries the letters of the
rotated unit label ("GWh") at the start of some lines; a single letter before a label is passed over. Figures print a
point between thousands and a comma before the decimal. Checks within 0.2 GWh: the power plants and autoproducers to
gross generation; Acaray, the binational plants and thermal to the power plants; transmission and distribution to the
losses; gross generation, imports, exports, own use and losses to the supply; industrial, residential and other sectors
to final consumption; commercial and public and unspecified to the other sectors; the supply to final consumption. The
year-on-year change is not taken. Nothing is filled.

    python warehouse/connectors/vmme_paraguay_electricity.py [--offline] [--fresh] [--out-dir DIR]

Ceiling: one request a run, saved in warehouse/raw/vmme_py/ and reused unless --fresh; --offline asks nothing.
minasyenergia.mopc.gov.py's robots file closes Joomla's system folders only, not /pdf/ (session 2572). License: internal.
VMME's home page states no terms of reuse; internal until a ruling.
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

NAME = "vmme_paraguay_electricity_annual"
CONNECTOR = "vmme_py"
SOURCE = "vmme_py:ben_2024_cuadro_3"
HOST = "minasyenergia.mopc.gov.py"
URL = "https://minasyenergia.mopc.gov.py/pdf/balance2024/BEN 2024_Paraguay.pdf"
UA = {"User-Agent": "Mozilla/5.0 (compatible; ERW-connector/0.1; +https://github.com/SamuelEnrique/erw)"}
CITATION = ("Viceministerio de Minas y Energia (VMME), Ministerio de Obras Publicas y Comunicaciones, Paraguay, Balance Energetico "
            "Nacional 2024, cuadro 3: Comparativo balance de electricidad (2023 and 2024, preliminary)")
E = chr(0xE9)
O = chr(0xF3)
TITLE = "CUADRO 3: COMPARATIVO BALANCE DE ELECTRICIDAD"
END = "CONSUMO FINAL"
# VMME's label (as printed, accents included) and (variable, item); every one found once, in this order
ROWS = [("Generaci" + O + "n Bruta", "gross_generation", "total"), ("Centrales el" + E + "ctricas", "gross_generation", "power_plants"),
        ("CHE Acaray", "gross_generation", "acaray_hydro"), ("Binacionales", "gross_generation", "binational_hydro"),
        ("T" + E + "rmica", "gross_generation", "thermal"), ("Autoproductores", "gross_generation", "autoproducers"),
        ("Importaci" + O + "n", "imports", "total"), ("Exportaci" + O + "n", "exports", "total"),
        ("Consumo en centrales/ autoconsumo ANDE", "own_use", "total"), ("P" + E + "rdidas", "losses", "total"),
        ("Transmisi" + O + "n", "losses", "transmission"), ("Distribuci" + O + "n", "losses", "distribution"),
        ("OFERTA", "supply", "total"), ("Industrial", "final_consumption", "industrial"),
        ("Residencial", "final_consumption", "residential"), ("Otros sectores", "final_consumption", "other_sectors"),
        ("Comercial y servicios p" + chr(0xFA) + "blicos", "final_consumption", "commercial_public"),
        ("Otros no especificados", "final_consumption", "unspecified"), ("CONSUMO FINAL", "final_consumption", "total")]
SIGNED = {"exports", "own_use", "losses"}
FIG = r"-?\d{1,3}(?:\.\d{3})*,\d"
X_COLS = []


def num(s):
    return float(s.replace(".", "").replace(",", "."))


def parse_lines(pages, base):
    """pages: each page's lines."""
    hits = [(i, j) for i, ln in enumerate(pages) for j, s in enumerate(ln) if s.strip() == TITLE]
    if len(hits) != 1:
        raise RuntimeError(f"the table's title found {len(hits)} times")
    i, j = hits[0]
    block = []
    for s in pages[i][j + 1:]:
        block.append(s.strip())
        if re.sub(r"^[A-Za-z] ", "", s.strip()).startswith(END):
            break
    else:
        raise RuntimeError(f"no {END!r} line after the title")
    yl = [s for s in block if re.fullmatch(r"(\d{4}) (\d{4})", s)]
    if len(yl) != 1:
        raise RuntimeError(f"the years' line found {len(yl)} times")
    years = yl[0].split()
    if int(years[1]) != int(years[0]) + 1:
        raise RuntimeError(f"the years are not two in order: {years}")
    vals, out, k = {}, [], 0
    for s in block:
        s = re.sub(r"^[A-Za-z] (?=[A-Z])", "", s)
        m = re.fullmatch(r"(.+?) (" + FIG + r"|0,0) (" + FIG + r"|0,0) (-?\d+,\d|-)", s)
        if not m:
            continue
        label = m.group(1)
        if k >= len(ROWS) or label != ROWS[k][0]:
            raise RuntimeError(f"{label!r} where {ROWS[k][0] if k < len(ROWS) else 'the end'!r} was expected")
        _, var, item = ROWS[k]
        k += 1
        for y, f in zip(years, (m.group(2), m.group(3))):
            v = num(f)
            if var in SIGNED:
                if v > 0:
                    raise RuntimeError(f"{label!r} {y}: {f} is not printed as leaving the supply")
                v = -v
            elif v < 0:
                raise RuntimeError(f"{label!r} {y}: {f} is negative")
            vals[(var, item, y)] = v
            out.append(dict(entity=f"vmme:py:{item}", variable=var, ts_utc=f"{y}-01-01T00:00:00Z", value=round(v * 1000, 1), unit="MWh",
                            freq="P1Y", geo="PY", market="", node=label, **base))
    if k != len(ROWS):
        raise RuntimeError(f"rows missing: {[r[0] for r in ROWS[k:]]}")
    g = lambda var, item, y: vals[(var, item, y)]  # noqa: E731
    for y in years:
        checks = [(g("gross_generation", "total", y), g("gross_generation", "power_plants", y) + g("gross_generation", "autoproducers", y)),
                  (g("gross_generation", "power_plants", y), sum(g("gross_generation", x, y) for x in ("acaray_hydro", "binational_hydro", "thermal"))),
                  (g("losses", "total", y), g("losses", "transmission", y) + g("losses", "distribution", y)),
                  (g("supply", "total", y), g("gross_generation", "total", y) + g("imports", "total", y) - g("exports", "total", y)
                   - g("own_use", "total", y) - g("losses", "total", y)),
                  (g("final_consumption", "total", y), sum(g("final_consumption", x, y) for x in ("industrial", "residential", "other_sectors"))),
                  (g("final_consumption", "other_sectors", y), g("final_consumption", "commercial_public", y) + g("final_consumption", "unspecified", y)),
                  (g("final_consumption", "total", y), g("supply", "total", y))]
        for n, (a, b) in enumerate(checks):
            if abs(a - b) > 0.2:
                raise RuntimeError(f"{y}: check {n + 1} misses: {a} against {b}")
    return pd.DataFrame(out)


def parse(content, base):
    with pdfplumber.open(io.BytesIO(content)) as pdf:
        pages = [(pg.extract_text() or "").split("\n") for pg in pdf.pages]
    return parse_lines(pages, base)


def main(argv=None):
    ap = argparse.ArgumentParser(description="VMME: Paraguay's electricity balance, two years (BEN 2024, cuadro 3)")
    ap.add_argument("--offline", action="store_true", help="the saved balance only, no request")
    ap.add_argument("--fresh", action="store_true", help="ask for the balance again")
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
        t = t[cols].sort_values(["variable", "entity", "ts_utc"]).reset_index(drop=True)
        v = {(x, e.split(":")[-1], ts[:4]): val for x, e, ts, val in zip(t.variable, t.entity, t.ts_utc, t.value)}
        last = max(t.ts_utc.str[:4])
        head = [
            "Energy Research Warehouse (ERW): Viceministerio de Minas y Energia (VMME), Paraguay, Balance Energetico Nacional 2024, "
            "cuadro 3: Paraguay's electricity balance, 2023 and 2024 (session 2572)",
            "Shape: series (docs/datastandard.md v0). entity vmme:py:<item>; variable gross_generation, imports, exports, own_use, "
            "losses, supply, final_consumption; unit MWh (VMME's GWh times 1,000); ts_utc the year's first day; freq P1Y; geo PY; "
            "node VMME's label.",
            f"{len(t)} rows; in {last} gross generation {v[('gross_generation', 'total', last)] / 1e6:.3f} TWh, exports "
            f"{v[('exports', 'total', last)] / 1e6:.3f} TWh, final consumption {v[('final_consumption', 'total', last)] / 1e6:.3f} TWh. "
            "Exports, own use and losses, printed with a minus sign, are written positive. The balance's 2024 figures are preliminary "
            "(VMME's own word); nothing is filled.",
            f"Retrieved: {run_id} (UTC) by warehouse/connectors/vmme_paraguay_electricity.py; the balance retrieved {base['retrieved_at']}; "
            f"last modified {base['vintage']}",
            f"Run log: warehouse/output/logs/{CONNECTOR}_{run_id}.log",
            f"Raw files: warehouse/raw/{CONNECTOR}/ (not in git)",
            f"Source: {SOURCE} {CITATION}",
            f"  access: {URL}",
            f"License: internal. VMME's home page states no terms of reuse; internal until a ruling. Cite: {CITATION}.",
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
            ip.update_sources([dict(source=SOURCE, publisher="Viceministerio de Minas y Energia (VMME), Paraguay",
                                    report="Balance Energetico Nacional 2024, cuadro 3: comparativo balance de electricidad", report_url=URL,
                                    document_list="https://minasyenergia.mopc.gov.py/", license="internal", tables=[NAME])])
        ip.write_status(CONNECTOR, run_id, results)
    log.close()
    return 0 if all(r["status"] == "ok" for r in results) else 1


if __name__ == "__main__":
    sys.exit(main())

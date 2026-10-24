#!/usr/bin/env python3
"""Mozambique's electricity balance, a year, 2020 to 2024: production by source, imports, exports, primary supply, own use,
losses and final consumption by sector, as the Ministry of Mineral Resources and Energy (MIREME) gives it in table 3.2.2
of its Energy Statistical Report ("Relatorio Estatistico de Energia 2023 - 2024", 5th edition) (session 2477, chain 120).

Energy Research Warehouse (ERW) connector. One series table, warehouse/output/mireme_mozambique_electricity_annual.csv,
from one PDF (no key):

    https://mireme.gov.mz/wp-content/uploads/2026/02/Relatorio-Estatistico-de-Energia_2024-1.pdf

The table "Quadro 3.2.2 Balanco de Electricidade (MWh), 2020-2024" is read by the position of its words on the page: the
row of the five years gives the columns, and each figure's digit groups (written with spaces between thousands) are joined
within their column, so a figure is never split or merged by its spaces.

    entity      mireme:mz:<item> (total, hydro, natural_gas, diesel, bagasse, solar; transport, distribution; industry,
                residential, commerce_public_services, agriculture_forest)
    variable    the section: generation, imports, exports, primary_supply, own_use, losses, final_consumption
    unit        MWh, as MIREME gives it; the table's parentheses (a quantity subtracted in the balance) are not a sign: the
                value is the quantity
    ts_utc      the year's 1 January; freq P1Y; geo MZ
    node        the row as MIREME labels it (Portuguese / English)

A cell MIREME marks "..." (not available) has no row. A cell whose digit groups are not in the form of thousands (2022's
solar, printed "69 7017") has no row and is counted in the header. The variation column (2024/2020) is not taken. A
report without the table, a header without the five years, a row not in the map (ROWS) or a key given twice stops the
run. Nothing is filled.

    python warehouse/connectors/mireme_mozambique_electricity.py [--offline] [--out-dir DIR]

Ceiling: one request a run, saved in warehouse/raw/mireme_mozambique_energy/ and reused unless --fresh; --offline asks
nothing. mireme.gov.mz's robots file disallows nothing (session 2477). License: not settled. The report's technical sheet
is headed "Copyright" and grants no reuse, and the site states no terms; internal until a ruling or a reuse statement
is read.
"""

import argparse
import datetime as dt
import io
import os
import re
import sys
import traceback
import unicodedata

import pandas as pd
import pdfplumber

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import iso_prices as ip  # noqa: E402

NAME = "mireme_mozambique_electricity_annual"
CONNECTOR = "mireme_mozambique_energy"
SOURCE = "mireme:relatorio_estatistico_energia"
HOST = "mireme.gov.mz"
URL = "https://mireme.gov.mz/wp-content/uploads/2026/02/Relatorio-Estatistico-de-Energia_2024-1.pdf"
UA = {"User-Agent": "Mozilla/5.0 (compatible; ERW-connector/0.1; +https://github.com/SamuelEnrique/erw)"}
YEARS = ["2020", "2021", "2022", "2023", "2024"]
# the row's Portuguese head, folded to ascii and lower case -> (section, item); a section's own row is its total
SECTIONS = {"producao": "generation", "uso proprio": "own_use", "perdas totais": "losses", "consumo final": "final_consumption"}
SINGLE = {"importacao": ("imports", "total"), "exportacao": ("exports", "total"), "oferta primario": ("primary_supply", "total")}
ITEMS = {"hidrica": "hydro", "gas natural": "natural_gas", "gasoleo": "diesel", "bagaco": "bagasse", "solar": "solar",
         "transporte": "transport", "distribuicao": "distribution", "industria": "industry", "domoestico": "residential",
         "domestico": "residential", "comercio e servicos publicos": "commerce_public_services", "agricultura e floresta": "agriculture_forest"}
X_COLS = ["x_label"]


def fold(s):
    s = unicodedata.normalize("NFKD", s).encode("ascii", "ignore").decode()
    return re.sub(r"\s+", " ", s.lower()).strip()


def lines_of(page):
    """The page's words grouped into lines by their top, each line a list of words sorted left to right."""
    rows = {}
    for w in page.extract_words():
        key = round(w["top"] / 3)
        rows.setdefault(key, []).append(w)
    return [sorted(rows[k], key=lambda w: w["x0"]) for k in sorted(rows)]


def parse_page(page, base, counts):
    lines = lines_of(page)
    head = next((ln for ln in lines if [w["text"] for w in ln] == YEARS), None)
    if head is None:
        raise RuntimeError("no header of the five years 2020 to 2024")
    centres = [(w["x0"] + w["x1"]) / 2 for w in head]
    gap = (centres[-1] - centres[0]) / 4
    bounds = [c + gap / 2 for c in centres]          # a figure's column: the first whose right bound is past its centre
    left = centres[0] - 0.75 * gap
    out, section, seen, started = [], None, set(), False
    for ln in lines:
        if ln is head:
            started = True
            continue
        if not started:
            continue
        label = " ".join(w["text"] for w in ln if w["x1"] < left)
        cells = [[] for _ in YEARS]
        for w in ln:
            if w["x1"] < left:
                continue
            c = (w["x0"] + w["x1"]) / 2
            j = next((k for k, b in enumerate(bounds) if c < b), None)
            if j is None:
                continue                                  # the variation column
            cells[j].append(w["text"])
        if not any(cells):
            continue
        port = fold(label.split("/")[0])
        if not port:
            continue
        if port in SECTIONS:
            section = SECTIONS[port]
            var, item = section, "total"
        elif port in SINGLE:
            section = None
            var, item = SINGLE[port]
        elif port in ITEMS:
            if section is None:
                raise RuntimeError(f"an item before its section: {label!r}")
            var, item = section, ITEMS[port]
        else:
            raise RuntimeError(f"a row not in the map: {label!r}")
        for year, toks in zip(YEARS, cells):
            text = "".join(toks).strip("()")
            joined = " ".join(t.strip("()") for t in toks)
            if not toks or set(text) <= {".", "…"}:
                continue
            if not re.fullmatch(r"\d{1,3}( \d{3})*", joined):
                counts["cells out of form"] = counts.get("cells out of form", 0) + 1
                continue
            key = (item, var, year)
            if key in seen:
                raise RuntimeError(f"{key} given twice")
            seen.add(key)
            out.append(dict(entity=f"mireme:mz:{item}", variable=var, ts_utc=f"{year}-01-01T00:00:00Z", value=float(joined.replace(" ", "")),
                            unit="MWh", freq="P1Y", geo="MZ", market="", node=label.strip(), **base, x_label=label.strip()))
    return out


def parse(content, base, counts):
    with pdfplumber.open(io.BytesIO(content)) as pdf:
        pages = [pg for pg in pdf.pages if "Quadro 3.2.2" in (pg.extract_text() or "")]
        # the report's list of tables names it too: the table's page is the one with the five years' header
        pages = [pg for pg in pages if any([w["text"] for w in ln] == YEARS for ln in lines_of(pg))]
        if len(pages) != 1:
            raise RuntimeError(f"table 3.2.2 with its header found on {len(pages)} pages")
        rows = parse_page(pages[0], base, counts)
    t = pd.DataFrame(rows)
    if t.empty:
        raise RuntimeError("no value in the table")
    return t


def main(argv=None):
    ap = argparse.ArgumentParser(description="MIREME: Mozambique's electricity balance, 2020 to 2024")
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
        counts = {}
        t = parse(content, base, counts)
        cols = ip.SERIES_COLS + X_COLS
        t = t[cols].sort_values(["variable", "entity", "ts_utc"]).reset_index(drop=True)
        g = t[(t.variable == "generation") & (t.entity == "mireme:mz:total")].set_index("ts_utc").value / 1e6
        head = [
            "Energy Research Warehouse (ERW): Ministry of Mineral Resources and Energy (MIREME), Energy Statistical Report 2023-2024, table 3.2.2, "
            f"Mozambique's electricity balance, {t.ts_utc.min()[:4]} to {t.ts_utc.max()[:4]} (session 2477)",
            "Shape: series (docs/datastandard.md v0). entity mireme:mz:<item>; variable the balance's section (generation, imports, exports, primary_supply, own_use, losses, "
            "final_consumption); unit MWh; ts_utc the year's 1 January; freq P1Y; geo MZ; node MIREME's row label. Values are quantities (the table's parentheses mark a subtraction). "
            "A section's total holds its items: a sum takes one level.",
            f"{len(t)} rows; generation TWh: " + ", ".join(f"{k[:4]} {v:.2f}" for k, v in g.items())
            + f". Not taken: cells marked ... (no row), cells out of form {counts.get('cells out of form', 0)}, the variation column. Nothing is filled.",
            f"Retrieved: {run_id} (UTC) by warehouse/connectors/mireme_mozambique_electricity.py; the report retrieved {base['retrieved_at']}; last modified {base['vintage']}",
            f"Run log: warehouse/output/logs/{CONNECTOR}_{run_id}.log",
            f"Raw files: warehouse/raw/{CONNECTOR}/ (not in git)",
            f"Source: {SOURCE} MIREME, Relatorio Estatistico de Energia 2023-2024 (5th edition), Quadro 3.2.2 Balanco de Electricidade (MWh), 2020-2024",
            f"  access: {URL}",
            "License: internal (the report's technical sheet is headed Copyright and grants no reuse; the site states no terms).",
        ]
        ip.write_snapshot(t, NAME, head, log, cols)
        results.append(dict(table=NAME, market="all", status="ok", detail=f"{len(t)} rows"))
        print(f"{NAME}: {len(t)} rows, {t.entity.nunique()} entities, {t.variable.nunique()} sections; {counts}")
    except Exception:
        tb = ip.redact(traceback.format_exc())
        log(f"{NAME} FAILED, no output file written:\n{tb}")
        print(f"{NAME} FAILED, no output file written: {tb.strip().splitlines()[-1]}", file=sys.stderr)
        results.append(dict(table=NAME, market="all", status="failed", detail=tb.strip().splitlines()[-1][:300]))
    if not args.out_dir:
        if results and results[0]["status"] == "ok":
            ip.update_sources([dict(source=SOURCE, publisher="Ministry of Mineral Resources and Energy, Mozambique (MIREME)",
                                    report="Relatorio Estatistico de Energia 2023-2024, Quadro 3.2.2 (electricity balance)", report_url=URL,
                                    document_list=URL, license="internal", tables=[NAME])])
        ip.write_status(CONNECTOR, run_id, results)
    log.close()
    return 0 if all(r["status"] == "ok" for r in results) else 1


if __name__ == "__main__":
    sys.exit(main())

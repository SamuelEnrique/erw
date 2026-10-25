#!/usr/bin/env python3
"""New Caledonia's electricity from Enercal's activity report 2024-2025: Enercal's net production by plant, the public grid's
purchases by source and the transmission network's sales, for the years July 2022 to June 2025 (session 2608, chain 129, the
session's own choice; the ERW held New Caledonia in no table but EIA's international one).

Energy Research Warehouse (ERW) connector. One series table, warehouse/output/enercal_nc_electricity_annual.csv, from one PDF
(no key):

    https://www.enercal.nc/wp-content/uploads/2026/01/Enercal-Rapport-dactivite-2024-2025.pdf

    entity      enercal:nc:<block>:<item>, the blocks:
                  thermal, renewable    "Chiffres cles 2024-2025 - Enercal Producteur": net production operated by Enercal
                  een                   the same page: net renewable production operated by Enercal Energies Nouvelles
                  public_purchases      "Chiffres cles 2024-2025 - Enercal Transport": purchases from the producers on the
                                        Grande Terre transmission network and the islands' networks, by source (Distribution
                                        Publique)
                  transport_sales       the same page: sales to the transmission network's clients
                each block's TOTAL as the item total
    variable    net_generation (thermal, renewable, een), purchases, sales
    unit        MWh (the report's GWh times 1,000); ts_utc the year's first day, 1 July; freq P1Y; geo NC
    node        the report's label; x_period the report's year ("2024-2025")

Each page is found by its title line, each block by its heading; its rows are the lines after the line of years up to its TOTAL
line, each a label and up to three figures (French decimals). A row with fewer figures than years holds the last years' (its
total checks it); a "-" is not written. Each block's rows add to its TOTAL within 0.2 GWh a year, "-" counted as nothing. Not
taken: the metallurgists' sales outside the public distribution (a line split over several, with shares), the network lengths,
connections, the distributor's tables and the financial pages. Nothing is filled.

    python warehouse/connectors/enercal_nc_electricity.py [--offline] [--fresh] [--out-dir DIR]

Ceiling: one request a run, saved in warehouse/raw/enercal_nc/ and reused unless --fresh; --offline asks nothing.
www.enercal.nc's robots file names * with no rule (session 2608). License: internal. Enercal's Mentions legales: electronic
reproduction "formellement interdite sauf autorisation expresse du directeur de la publication"; internal until a ruling.
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

NAME = "enercal_nc_electricity_annual"
CONNECTOR = "enercal_nc"
SOURCE = "enercal_nc:rapport_activite_2024_2025_chiffres_cles"
HOST = "www.enercal.nc"
URL = "https://www.enercal.nc/wp-content/uploads/2026/01/Enercal-Rapport-dactivite-2024-2025.pdf"
UA = {"User-Agent": "Mozilla/5.0 (compatible; ERW-connector/0.1; +https://github.com/SamuelEnrique/erw)"}
CITATION = "Enercal, Rapport d'activite 2024-2025, Chiffres cles 2024-2025 (Enercal Producteur and Enercal Transport)"
PRODUCER = "Chiffres cl" + chr(0xE9) + "s 2024-2025 - Enercal Producteur"
TRANSPORT = "Chiffres cl" + chr(0xE9) + "s 2024-2025 - Enercal Transport"
# (page title, block, variable, the heading line's start, the line of years: the heading itself or the next line)
BLOCKS = [
    (PRODUCER, "thermal", "net_generation", "PRODUCTION THERMIQUE", "next"),
    (PRODUCER, "renewable", "net_generation", "PRODUCTION RENOUVELABLE", "next"),
    (PRODUCER, "een", "net_generation", "op" + chr(0xE9) + "r" + chr(0xE9) + "e par Enercal Energies Nouvelles", "same"),
    (TRANSPORT, "public_purchases", "purchases", "DISTRIBUTION PUBLIQUE", "same"),
    (TRANSPORT, "transport_sales", "sales", "Ventes d" + chr(0x2019) + chr(0xE9) + "lectricit" + chr(0xE9) + " aux clients du r" + chr(0xE9) + "seau de Transport", None),
]
FIG = r"(?:-|\d+,\d+)"
ROW = re.compile(r"^(?P<label>.*?\S)(?P<figs>(?:\s+" + FIG + r"){1,3})\s*$")
YEARS = re.compile(r"(\d{4})-(\d{4})")
X_COLS = ["x_period"]


def slug(s):
    s = unicodedata.normalize("NFKD", s).encode("ascii", "ignore").decode()
    return re.sub(r"[^a-z0-9]+", "_", s.lower()).strip("_")


def year_line(s):
    ys = [(int(a), int(b)) for a, b in YEARS.findall(s)]
    if len(ys) != 3 or any(b != a + 1 for a, b in ys) or [a for a, _ in ys] != list(range(ys[0][0], ys[0][0] + 3)):
        raise RuntimeError(f"not a line of three years: {s!r}")
    return [f"{a}-{b}" for a, b in ys]


def parse_block(lines, start, block, years_at, years_given=None):
    if years_at == "same":
        years, k = year_line(lines[start]), start + 1
    elif years_at == "next":
        years, k = year_line(lines[start + 1]), start + 2
    else:
        years, k = years_given, start + 1
    rows, total = [], None
    for ln in lines[k:k + 30]:
        if ln.startswith("TOTAL"):
            m = ROW.match(ln)
            if not m or m.group("label") != "TOTAL":
                raise RuntimeError(f"{block}: a TOTAL line not read: {ln!r}")
            total = m.group("figs").split()
            break
        m = ROW.match(ln)
        if m:
            rows.append((m.group("label"), m.group("figs").split()))
        elif rows:
            raise RuntimeError(f"{block}: a line inside the block not a row: {ln!r}")
    if total is None or len(total) != len(years) or not rows:
        raise RuntimeError(f"{block}: no TOTAL of {len(years)} figures after its rows")
    out = []
    for label, figs in rows + [("TOTAL", total)]:
        for y, f in zip(years[len(years) - len(figs):], figs):
            if f != "-":
                out.append((label, y, float(f.replace(",", "."))))
    for y in years:
        s = sum(v for label, yy, v in out if yy == y and label != "TOTAL")
        t = [v for label, yy, v in out if yy == y and label == "TOTAL"][0]
        if abs(s - t) > 0.2:
            raise RuntimeError(f"{block} {y}: the rows make {s:.2f} GWh, the TOTAL {t}")
    return years, out


def parse_pages(pages, base):
    rec, years_of = [], {}
    for title, block, variable, heading, years_at in BLOCKS:
        hits = [p for p in pages if any(ln.strip() == title for ln in p)]
        if len(hits) != 1:
            raise RuntimeError(f"the page {title!r} found {len(hits)} times")
        lines = [ln.strip() for ln in hits[0]]
        at = [i for i, ln in enumerate(lines) if ln.startswith(heading)]
        if not at:
            raise RuntimeError(f"{block}: the heading {heading!r} not found")
        i = at[0]
        if block == "transport_sales":
            if len(at) != 1:
                raise RuntimeError(f"{block}: the heading found {len(at)} times")
            years, out = parse_block(lines, i, block, None, years_of["public_purchases"])
        else:
            if len(at) != 1 and block != "renewable":
                raise RuntimeError(f"{block}: the heading found {len(at)} times")
            years, out = parse_block(lines, i, block, years_at)
        years_of[block] = years
        for label, y, v in out:
            item = "total" if label == "TOTAL" else slug(label)
            rec.append(dict(entity=f"enercal:nc:{block}:{item}", variable=variable, ts_utc=f"{y[:4]}-07-01T00:00:00Z",
                            value=round(v * 1000, 1), unit="MWh", freq="P1Y", geo="NC", market="", node=label, x_period=y, **base))
    t = pd.DataFrame(rec)
    if t.duplicated(["entity", "variable", "ts_utc"]).any():
        raise RuntimeError("a row given twice")
    return t


def parse(content, base):
    with pdfplumber.open(io.BytesIO(content)) as pdf:
        pages = [(pg.extract_text() or "").split("\n") for pg in pdf.pages]
    return parse_pages(pages, base)


def main(argv=None):
    ap = argparse.ArgumentParser(description="Enercal: New Caledonia's production, purchases and sales, July 2022 to June 2025")
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
        content, rec = ip.fetch_raw(CONNECTOR, URL, log, offline=args.offline, fresh=args.fresh, headers=UA, timeout=300, pause=1)
        base = dict(source=SOURCE, source_url=URL, retrieved_at=rec.get("retrieved_at") or "", vintage=ip.vintage_of(rec))
        t = parse(content, base)
        cols = ip.SERIES_COLS + X_COLS
        t = t[cols].sort_values(["entity", "ts_utc"]).reset_index(drop=True)
        pp = t[t.entity == "enercal:nc:public_purchases:total"]
        head = [
            "Energy Research Warehouse (ERW): Enercal, Rapport d'activite 2024-2025, Chiffres cles: New Caledonia's net production by "
            "Enercal's plants, the public grid's purchases by source and the transmission network's sales, July 2022 to June 2025 "
            "(session 2608)",
            "Shape: series (docs/datastandard.md v0). entity enercal:nc:<block>:<item> (blocks thermal, renewable, een, "
            "public_purchases, transport_sales; item total each block's TOTAL); variable net_generation, purchases or sales; unit MWh "
            "(the report's GWh times 1,000); ts_utc the year's first day, 1 July; freq P1Y; geo NC; node the report's label; x_period "
            "the report's year.",
            f"{len(t)} rows; the public distribution's purchases {pp.value.iloc[0] / 1e3:,.1f} GWh in {pp.x_period.iloc[0]}, "
            f"{pp.value.iloc[-1] / 1e3:,.1f} GWh in {pp.x_period.iloc[-1]}. A '-' is not written; nothing is filled.",
            f"Retrieved: {run_id} (UTC) by warehouse/connectors/enercal_nc_electricity.py; the report retrieved {base['retrieved_at']}; "
            f"last modified {base['vintage']}",
            f"Run log: warehouse/output/logs/{CONNECTOR}_{run_id}.log",
            f"Raw files: warehouse/raw/{CONNECTOR}/ (not in git)",
            f"Source: {SOURCE} {CITATION}",
            f"  access: {URL}",
            f"License: internal. Enercal's Mentions legales forbid electronic reproduction without the publication director's express "
            f"permission; internal until a ruling. Cite: {CITATION}.",
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
            ip.update_sources([dict(source=SOURCE, publisher="Enercal", report="Rapport d'activite 2024-2025, Chiffres cles 2024-2025 "
                                    "(Enercal Producteur and Enercal Transport)", report_url=URL,
                                    document_list="https://www.enercal.nc/nos-publications/", license="internal", tables=[NAME])])
        ip.write_status(CONNECTOR, run_id, results)
    log.close()
    return 0 if all(r["status"] == "ok" for r in results) else 1


if __name__ == "__main__":
    sys.exit(main())

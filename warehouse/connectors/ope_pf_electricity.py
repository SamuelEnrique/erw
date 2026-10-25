#!/usr/bin/env python3
"""French Polynesia's electricity a year from the Bilan energetique de la Polynesie francaise, edition 2024, of the Observatoire
Polynesien de l'Energie (the Direction Polynesienne de l'Energie): total production and final consumption 2010 to 2024,
renewable production and network losses 2014 to 2024 (session 2609, chain 129, the session's second own choice; the ERW held
French Polynesia in no table but EIA's international one).

Energy Research Warehouse (ERW) connector. One series table, warehouse/output/ope_pf_electricity_annual.csv, from one PDF (no
key):

    https://www.service-public.pf/sde/wp-content/uploads/sites/15/2025/11/Bilan_energetique_de_la_Polynesie_francaise_-_edition_2024.pdf

    entity      ope:pf:total (variable generation), ope:pf:renewable (generation), ope:pf:final_consumption (consumption),
                ope:pf:losses (losses, transmission and distribution)
    unit        MWh (the balance's GWh times 1,000); ts_utc the year's first day; freq P1Y; geo PF
    node        the balance's label

Read from the text: the "Principaux chiffres" table (its row of years, then "Production totale d'electricite GWh" and
"Consommation finale d'electricite GWh", fifteen figures each); Figure 17's table (its row of years, then "Production d'EnR
electrique (GWh)" and "Production totale d'electricite (GWh)", then the EnR rate); the losses table ("Pertes" and its years,
the line "en GWh"). Checks: Figure 17's total equals the main table's in each of its years; the printed EnR rate is renewable
over total within 0.1 point; Figure 23's consumption equals the main table's. The PDF's "ti" ligature is read as (cid:31) and
restored. Not taken: the 2024 table by archipelago (its labels split over lines), the balance in ktep, prices and emissions.
Nothing is filled.

    python warehouse/connectors/ope_pf_electricity.py [--offline] [--fresh] [--out-dir DIR]

Ceiling: one request a run, saved in warehouse/raw/sde_pf/ and reused unless --fresh; --offline asks nothing.
www.service-public.pf's robots file closes only /wp-admin/ (session 2609). License: internal. The site's Mentions legales: "Toute
reproduction ou representation et extraction, partielle ou totale, des elements du site ne peut etre faite sans autorisation
prealable"; internal until a ruling.
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

NAME = "ope_pf_electricity_annual"
CONNECTOR = "sde_pf"
SOURCE = "sde_pf:bilan_energetique_2024"
HOST = "www.service-public.pf"
URL = ("https://www.service-public.pf/sde/wp-content/uploads/sites/15/2025/11/"
       "Bilan_energetique_de_la_Polynesie_francaise_-_edition_2024.pdf")
UA = {"User-Agent": "Mozilla/5.0 (compatible; ERW-connector/0.1; +https://github.com/SamuelEnrique/erw)"}
CITATION = ("Observatoire Polynesien de l'Energie (Direction Polynesienne de l'Energie), Bilan energetique de la Polynesie "
            "francaise, edition 2024")
E = chr(0xE9)
NUM = r"\d+,\d"
X_COLS = []


def nums(s):
    return [float(x.replace(",", ".")) for x in re.findall(r"(?<![\d,])" + NUM + r"(?![\d,])", s)]


def year_run(s, first):
    ys = [int(y) for y in re.findall(r"\b(20\d\d)\b", s)]
    if not ys or ys[0] != first:
        raise RuntimeError(f"a row of years not from {first}: {s!r}")
    run = [ys[0]]
    for y in ys[1:]:
        if y != run[-1] + 1:
            break
        run.append(y)
    return run


def one(lines, pred, what):
    hit = [i for i, ln in enumerate(lines) if pred(ln)]
    if len(hit) != 1:
        raise RuntimeError(f"{what}: found {len(hit)} times")
    return hit[0]


def series(line, label, years, what):
    i = line.index(label) + len(label)
    v = nums(line[i:])[:len(years)]
    if len(v) != len(years):
        raise RuntimeError(f"{what}: {len(v)} figures for {len(years)} years: {line!r}")
    return dict(zip(years, v))


def parse_lines(lines, base):
    lines = [ln.replace("(cid:31)", "ti").strip() for ln in lines]
    prod_label = "Production totale d'" + E + "lectricit" + E + " GWh"
    cons_label = "Consommation finale d'" + E + "lectricit" + E + " GWh"
    k = one(lines, lambda s: s.startswith("Sous th" + chr(0xE8) + "mes Indicateurs Unit" + E + "s 2010"), "the main table's years")
    years = year_run(lines[k], 2010)
    p = one(lines, lambda s: s.startswith(prod_label), "the main table's production")
    total = series(lines[p], prod_label, years, "production")
    c = one(lines, lambda s: cons_label in s, "the main table's final consumption")
    cons = series(lines[c], cons_label, years, "final consumption")
    enr_label = "Production d'EnR " + E + "lectrique (GWh)"
    r = one(lines, lambda s: s.startswith(enr_label), "Figure 17's renewable production")
    y17 = year_run(lines[r - 1], 2014)
    enr = series(lines[r], enr_label, y17, "renewable production")
    t17 = series(lines[r + 1], "Production totale d'" + E + "lectricit" + E + " (GWh)", y17, "Figure 17's total")
    rate = [float(x.replace(",", ".")) for x in re.findall(r"(\d+,\d)%", lines[r + 3])]
    if len(rate) != len(y17):
        raise RuntimeError(f"Figure 17's EnR rate: {len(rate)} figures: {lines[r + 3]!r}")
    for y, q in zip(y17, rate):
        if t17[y] != total[y]:
            raise RuntimeError(f"{y}: Figure 17's total {t17[y]}, the main table's {total[y]}")
        if abs(100 * enr[y] / total[y] - q) > 0.1:
            raise RuntimeError(f"{y}: renewable over total {100 * enr[y] / total[y]:.2f}%, the rate printed {q}%")
    q = one(lines, lambda s: s.startswith("Pertes 2014"), "the losses table")
    yl = year_run(lines[q], 2014)
    g = [i for i in range(q + 1, q + 4) if lines[i].startswith("en GWh")]
    if len(g) != 1:
        raise RuntimeError("the losses' line in GWh not found")
    losses = series(lines[g[0]], "en GWh", yl, "losses")
    c23 = [i for i, ln in enumerate(lines) if ln.startswith("GWh ") and i > 0 and lines[i - 1].startswith("d'" + E + "lectricit" + E)]
    if len(c23) != 1:
        raise RuntimeError(f"Figure 23's consumption found {len(c23)} times")
    y23 = year_run(lines[c23[0] - 2], 2014)
    for y, v in series(lines[c23[0]], "GWh", y23, "Figure 23's consumption").items():
        if v != cons[y]:
            raise RuntimeError(f"{y}: Figure 23's consumption {v}, the main table's {cons[y]}")
    rows = []
    for item, variable, node, d in (("total", "generation", "Production totale d'" + E + "lectricit" + E, total),
                                    ("renewable", "generation", "Production d'EnR " + E + "lectrique", enr),
                                    ("final_consumption", "consumption", "Consommation finale d'" + E + "lectricit" + E, cons),
                                    ("losses", "losses", "Pertes, transport et distribution", losses)):
        for y, v in d.items():
            rows.append(dict(entity=f"ope:pf:{item}", variable=variable, ts_utc=f"{y}-01-01T00:00:00Z", value=round(v * 1000, 1),
                             unit="MWh", freq="P1Y", geo="PF", market="", node=node, **base))
    return pd.DataFrame(rows)


def parse(content, base):
    with pdfplumber.open(io.BytesIO(content)) as pdf:
        lines = [ln for pg in pdf.pages for ln in (pg.extract_text() or "").split("\n")]
    return parse_lines(lines, base)


def main(argv=None):
    ap = argparse.ArgumentParser(description="OPE: French Polynesia's electricity production, consumption and losses a year")
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
        content, rec = ip.fetch_raw(CONNECTOR, URL, log, offline=args.offline, fresh=args.fresh, headers=UA, timeout=300, pause=1)
        base = dict(source=SOURCE, source_url=URL, retrieved_at=rec.get("retrieved_at") or "", vintage=ip.vintage_of(rec))
        t = parse(content, base)
        cols = ip.SERIES_COLS + X_COLS
        t = t[cols].sort_values(["entity", "ts_utc"]).reset_index(drop=True)
        tot = t[t.entity == "ope:pf:total"]
        head = [
            "Energy Research Warehouse (ERW): Observatoire Polynesien de l'Energie, Bilan energetique de la Polynesie francaise, edition "
            "2024: French Polynesia's electricity production and final consumption 2010 to 2024, renewable production and losses 2014 "
            "to 2024 (session 2609)",
            "Shape: series (docs/datastandard.md v0). entity ope:pf:<item> (total, renewable, final_consumption, losses); variable "
            "generation, consumption or losses; unit MWh (the balance's GWh times 1,000); ts_utc the year's first day; freq P1Y; geo "
            "PF; node the balance's label.",
            f"{len(t)} rows; total production {tot.value.iloc[0] / 1e3:,.1f} GWh in {tot.ts_utc.iloc[0][:4]}, {tot.value.iloc[-1] / 1e3:,.1f} "
            f"GWh in {tot.ts_utc.iloc[-1][:4]}. Checked against Figures 17 and 23 and the printed EnR rate; nothing is filled.",
            f"Retrieved: {run_id} (UTC) by warehouse/connectors/ope_pf_electricity.py; the balance retrieved {base['retrieved_at']}; last "
            f"modified {base['vintage']}",
            f"Run log: warehouse/output/logs/{CONNECTOR}_{run_id}.log",
            f"Raw files: warehouse/raw/{CONNECTOR}/ (not in git)",
            f"Source: {SOURCE} {CITATION}",
            f"  access: {URL}",
            f"License: internal. www.service-public.pf's Mentions legales: no reproduction or extraction without prior permission; "
            f"internal until a ruling. Cite: {CITATION}.",
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
            ip.update_sources([dict(source=SOURCE, publisher="Government of French Polynesia (Direction Polynesienne de l'Energie)",
                                    report="Bilan energetique de la Polynesie francaise, edition 2024 (Observatoire Polynesien de "
                                           "l'Energie): Principaux chiffres, Figures 17 and 23, losses", report_url=URL,
                                    document_list="https://www.service-public.pf/sde/wp-json/wp/v2/media?search=bilan",
                                    license="internal", tables=[NAME])])
        ip.write_status(CONNECTOR, run_id, results)
    log.close()
    return 0 if all(r["status"] == "ok" for r in results) else 1


if __name__ == "__main__":
    sys.exit(main())

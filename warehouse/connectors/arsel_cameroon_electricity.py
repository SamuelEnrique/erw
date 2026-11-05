#!/usr/bin/env python3
"""Cameroon's electricity a year, as its regulator, the Agence de Regulation du Secteur de l'Electricite (ARSEL), gives it
in its activity report for 2025 (published September 2026): the energy produced in 2025 by source, the energy bought from
each independent producer in 2025 (table 19, the realised column), and the energy injected into and withdrawn from the
transmission network in 2024 and 2025, for the Southern and the Northern interconnected grids (RIS, RIN) (table 21)
(session 2533, chain 124; the ERW held Cameroon only in EIA's and OWID's international tables).

Energy Research Warehouse (ERW) connector. One series table, warehouse/output/arsel_cameroon_electricity_annual.csv, from one
PDF (no key):

    https://arsel-cm.org/wp-content/uploads/2026/09/Rapport-ARSEL-2025.pdf

Three blocks are read from the PDF's text, each found by its own words, not by its page:

    production              "Total energies produites en MWh": hydro, thermal HFO, thermal LFO, gas, solar, total (2025)
    ipp_purchases           "Tableau 19": the realised column, in GWh, a plant a row and the total (2025); a plant with
                            "-" realised (none bought) is not written
    transmission_injection, "Tableau 21": the RIS's injections by ENEO and by the independent producers, its withdrawals
    transmission_withdrawal by ENEO, by high-voltage customers and by the independent producers' own sites, the RIN's
                            injections and withdrawals by ENEO, each grid's total and the national total (2024, 2025)

    entity      arsel:cm:<item> (a source, a plant, or a grid's part: ris_eneo, ris_ipp, ris_hv_clients, ris_ipps,
                ris_total, rin_eneo, rin_total, total)
    variable    production, ipp_purchases, transmission_injection, transmission_withdrawal
    unit        MWh (table 19's GWh times 1,000); ts_utc the year's first day; freq P1Y; geo CM
    node        ARSEL's label

The run stops on a block not found, a row of another form, a label not in the map, a row missing, a key given twice, or
a total that differs from the sum of its parts by more than 1 MWh (table 21 by more than 1.5 MWh: its RIS injections
for 2025 sum to 1 MWh less than its total; table 19 by more than 20 MWh, its figures given to 10 MWh). Nothing is filled. Prices, tariffs and fuel costs (in FCFA) are not taken.

    python warehouse/connectors/arsel_cameroon_electricity.py [--offline] [--fresh] [--out-dir DIR]

Ceiling: one request a run, saved in warehouse/raw/arsel_reports/ and reused unless --fresh; --offline asks nothing.
arsel-cm.org's robots file allows every path with a crawl delay of 10 seconds, which is kept (session 2533). License:
internal. ARSEL's site states "Copyright 2025 ARSEL, All rights reserved" and links no terms of reuse; internal until a
ruling.
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

NAME = "arsel_cameroon_electricity_annual"
CONNECTOR = "arsel_reports"
SOURCE = "arsel:rapport_activites_2025"
HOST = "arsel-cm.org"
URL = "https://arsel-cm.org/wp-content/uploads/2026/09/Rapport-ARSEL-2025.pdf"
LIST = "https://arsel-cm.org/index.php/rapports-annuels/"
UA = {"User-Agent": "Mozilla/5.0 (compatible; ERW-connector/0.1; +https://github.com/SamuelEnrique/erw)"}
TITLE = "Rapport d’activités 2025"
YEAR = "2025"
CITATION = ("Agence de Regulation du Secteur de l'Electricite (ARSEL), Cameroun, Rapport d'activites 2025: energies produites "
            "par source, tableau 19 (volumes d'achats d'energie 2025) and tableau 21 (energies injectees et soutirees sur le "
            "reseau de transport)")
PRODUCTION = {"Hydraulique": "hydro", "Thermique HFO": "thermal_hfo", "Thermique LFO": "thermal_lfo", "GAZ": "gas",
              "Solaire Photovoltaïque": "solar", "Total": "total"}
PURCHASES = {"NHPC": "nhpc", "KPDC": "kpdc", "DPDC": "dpdc", "Memv'ele": "memve_ele", "Lom Pangar": "lom_pangar", "Mekin": "mekin",
             "Aggreko": "aggreko", "SCATEC Solaire": "scatec_solar", "Release 2 Solaire": "release2_solar", "Mbakaou": "mbakaou",
             "Total": "total"}
# table 21's figure rows in order: the count of figures and, a pair of figures (2024, 2025) at a time, (variable, item)
T21 = [(4, [("transmission_injection", "ris_eneo"), ("transmission_withdrawal", "ris_eneo")]),
       (4, [("transmission_injection", "ris_ipp"), ("transmission_withdrawal", "ris_hv_clients")]),
       (2, [("transmission_withdrawal", "ris_ipps")]),
       (4, [("transmission_injection", "ris_total"), ("transmission_withdrawal", "ris_total")]),
       (4, [("transmission_injection", "rin_eneo"), ("transmission_withdrawal", "rin_eneo")]),
       (4, [("transmission_injection", "rin_total"), ("transmission_withdrawal", "rin_total")]),
       (4, [("transmission_injection", "total"), ("transmission_withdrawal", "total")])]
LABELS21 = {"ris_eneo": "RIS, ENEO", "ris_ipp": "RIS, producteurs independants (IPP)", "ris_hv_clients": "RIS, clients HT",
            "ris_ipps": "RIS, IPPs", "ris_total": "Total RIS", "rin_eneo": "RIN, ENEO", "rin_total": "Total RIN",
            "total": "TOTAL (RIS+RIN)"}
# (variable, total item, parts, tolerance in MWh)
SUMS = [("production", "total", ["hydro", "thermal_hfo", "thermal_lfo", "gas", "solar"], 1),
        ("ipp_purchases", "total", ["nhpc", "kpdc", "dpdc", "memve_ele", "lom_pangar", "mekin", "aggreko", "scatec_solar",
                                    "release2_solar", "mbakaou"], 20),
        ("transmission_injection", "ris_total", ["ris_eneo", "ris_ipp"], 1.5),
        ("transmission_withdrawal", "ris_total", ["ris_eneo", "ris_hv_clients", "ris_ipps"], 1.5),
        ("transmission_injection", "rin_total", ["rin_eneo"], 1.5), ("transmission_withdrawal", "rin_total", ["rin_eneo"], 1.5),
        ("transmission_injection", "total", ["ris_total", "rin_total"], 1.5),
        ("transmission_withdrawal", "total", ["ris_total", "rin_total"], 1.5)]
NUM_SP = r"\d{1,3}(?: \d{3})*"
X_COLS = ["x_label"]


def fr_num(s):
    """A figure as ARSEL prints it: spaces between thousands, a decimal comma or point."""
    s = s.strip()
    if not re.fullmatch(NUM_SP + r"(?:[,.]\d+)?", s):
        raise RuntimeError(f"not a figure: {s!r}")
    return float(s.replace(" ", "").replace(",", "."))


def block(text, start, end):
    """The text from start's last place (the report's list of tables names each table first) to end."""
    if text.count(start) < 1:
        raise RuntimeError(f"block not found: {start!r}")
    i = text.rindex(start)
    j = text.find(end, i)
    if j < 0:
        raise RuntimeError(f"the end of the block {start!r} not found: {end!r}")
    return text[i + len(start):j]


def parse_text(text, base):
    if TITLE not in text:
        raise RuntimeError("not ARSEL's activity report for 2025")
    rows, seen = [], set()

    def add(var, item, year, mwh, label):
        k = (var, item, year)
        if k in seen:
            raise RuntimeError(f"{k} given twice")
        seen.add(k)
        rows.append(dict(entity=f"arsel:cm:{item}", variable=var, ts_utc=f"{year}-01-01T00:00:00Z", value=round(mwh, 3), unit="MWh",
                         freq="P1Y", geo="CM", market="", node=label, **base, x_label=label))

    # production by source, 2025
    got = set()
    for ln in block(text, "Total énergies produites en MWh", "LA TRANSPARENCE").splitlines():
        ln = ln.strip()
        if not ln:
            continue
        m = re.fullmatch(r"(.+?) (" + NUM_SP + r"(?:,\d+)?)", ln)
        if not m or m.group(1) not in PRODUCTION:
            raise RuntimeError(f"a production row not in the map: {ln!r}")
        add("production", PRODUCTION[m.group(1)], YEAR, fr_num(m.group(2)), m.group(1))
        got.add(m.group(1))
    if got != set(PRODUCTION):
        raise RuntimeError(f"production rows missing: {sorted(set(PRODUCTION) - got)}")
    # table 19: purchases from the independent producers, 2025, the realised column (GWh)
    t19 = block(text, "Tableau 19", "Tableau 20")
    got = set()
    for ln in t19.splitlines():
        ln = ln.strip()
        if not ln or ln.startswith(":") or ln.startswith("Projet"):
            continue
        if ln.startswith("- "):
            break
        fig = NUM_SP + r",\d+"
        m = re.fullmatch(r"(.+?) (" + fig + r"|-) (" + fig + r"|-) (-?\d+%)", ln)
        if not m or m.group(1) not in PURCHASES:
            raise RuntimeError(f"a row of table 19 not in the map: {ln!r}")
        got.add(m.group(1))
        if m.group(3) != "-":
            add("ipp_purchases", PURCHASES[m.group(1)], YEAR, fr_num(m.group(3)) * 1000, m.group(1))
    if got != set(PURCHASES):
        raise RuntimeError(f"rows of table 19 missing: {sorted(set(PURCHASES) - got)}")
    # table 21: transmission injections and withdrawals, 2024 and 2025
    t21 = block(text, "Tableau 21", "- Le secteur")
    figrows = []
    for ln in t21.splitlines():
        figs = re.findall(NUM_SP + r"\.\d{2}", ln)
        if figs:
            figrows.append(figs)
    if [len(f) for f in figrows] != [n for n, _ in T21]:
        raise RuntimeError(f"table 21's figure rows are not as expected: {[len(f) for f in figrows]}")
    for figs, (n, keys) in zip(figrows, T21):
        for k, (var, item) in enumerate(keys):
            add(var, item, "2024", fr_num(figs[2 * k]), LABELS21[item])
            add(var, item, "2025", fr_num(figs[2 * k + 1]), LABELS21[item])
    t = pd.DataFrame(rows)
    v = {(x, e.split(":")[-1], y[:4]): val for x, e, y, val in zip(t.variable, t.entity, t.ts_utc, t.value)}
    for var, tot, parts, tol in SUMS:
        for year in sorted({y for (x, _, y) in v if x == var}):
            s = sum(v.get((var, p, year), 0.0) for p in parts)
            if abs(s - v[(var, tot, year)]) > tol:
                raise RuntimeError(f"{var} {year}: {tot} {v[(var, tot, year)]} is not the sum of its parts {s}")
    return t


def parse(content, base):
    with pdfplumber.open(io.BytesIO(content)) as pdf:
        text = "\n".join(pg.extract_text() or "" for pg in pdf.pages)
    return parse_text(text, base)


def main(argv=None):
    ap = argparse.ArgumentParser(description="ARSEL: Cameroon's electricity, from the activity report for 2025")
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
        content, rec = ip.fetch_raw(CONNECTOR, URL, log, offline=args.offline, fresh=args.fresh, headers=UA, timeout=300, pause=10)
        base = dict(source=SOURCE, source_url=URL, retrieved_at=rec.get("retrieved_at") or "", vintage=ip.vintage_of(rec))
        t = parse(content, base)
        cols = ip.SERIES_COLS + X_COLS
        t = t[cols].sort_values(["variable", "entity", "ts_utc"]).reset_index(drop=True)
        v = {(x, e.split(":")[-1], y[:4]): val for x, e, y, val in zip(t.variable, t.entity, t.ts_utc, t.value)}
        head = [
            "Energy Research Warehouse (ERW): Agence de Regulation du Secteur de l'Electricite (ARSEL), Cameroun, Rapport d'activites 2025: "
            "Cameroon's electricity produced by source, bought from independent producers, and injected into and withdrawn from the "
            "transmission network (session 2533)",
            "Shape: series (docs/datastandard.md v0). entity arsel:cm:<item>; variable production (by source, 2025), ipp_purchases (by "
            "plant, 2025, table 19's realised column), transmission_injection and transmission_withdrawal (by grid and party, 2024 and "
            "2025, table 21); unit MWh (table 19's GWh times 1,000); ts_utc the year's first day; freq P1Y; geo CM; node ARSEL's label.",
            f"{len(t)} rows; production in 2025 {v[('production', 'total', '2025')] / 1e6:.3f} TWh (hydro "
            f"{v[('production', 'hydro', '2025')] / 1e6:.3f}); injections into the transmission network {v[('transmission_injection', 'total', '2024')] / 1e6:.3f} "
            f"TWh in 2024 and {v[('transmission_injection', 'total', '2025')] / 1e6:.3f} TWh in 2025. Each total equals its parts; a plant "
            "with none bought is not written; nothing is filled. Prices, tariffs and fuel costs (FCFA) are not taken.",
            f"Retrieved: {run_id} (UTC) by warehouse/connectors/arsel_cameroon_electricity.py; the report retrieved {base['retrieved_at']}; "
            f"last modified {base['vintage']}",
            f"Run log: warehouse/output/logs/{CONNECTOR}_{run_id}.log",
            f"Raw files: warehouse/raw/{CONNECTOR}/ (not in git)",
            f"Source: {SOURCE} {CITATION}",
            f"  access: {URL} (listed on {LIST})",
            "License: internal. ARSEL's site states \"Copyright 2025 ARSEL, All rights reserved\" and links no terms of reuse; internal "
            f"until a ruling. Cite: {CITATION}.",
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
            ip.update_sources([dict(source=SOURCE, publisher="Agence de Regulation du Secteur de l'Electricite (ARSEL), Cameroun",
                                    report="Rapport d'activites 2025: energies produites, tableau 19 and tableau 21", report_url=URL,
                                    document_list=LIST, license="internal", tables=[NAME])])
        ip.write_status(CONNECTOR, run_id, results)
    log.close()
    return 0 if all(r["status"] == "ok" for r in results) else 1


if __name__ == "__main__":
    sys.exit(main())

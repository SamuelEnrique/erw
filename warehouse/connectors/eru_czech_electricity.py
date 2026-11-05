#!/usr/bin/env python3
"""Czechia's electricity, from the Energy Regulatory Office's (Energeticky regulacni urad, ERU) annual report on the
operation of the Czech electricity system for 2025 (Rocni zprava o provozu elektrizacni soustavy Ceske republiky 2025,
last modified 1 July 2026): each month of 2025, gross and net production by technology with the plants' own use, and
the balance (cross-border trade by voltage level, losses, consumption by category); and gross production by technology
a year, 2016 to 2025 (session 2538, chain 124: a source of the session's own choosing; the ERW held Czechia only in
Eurostat's, EIA's and Energy-Charts' international tables, and ceps.cz's robots file disallows every path).

Energy Research Warehouse (ERW) connector. One series table, warehouse/output/eru_czech_electricity.csv, from one PDF (no
key):

    https://eru.gov.cz/sites/default/files/obsah/prilohy/eruelektro2025.pdf

Three tables are read from the PDF's text, each found by its title:

    3.1 Bilance elektriny - zdroje [GWh]    a month: gross_generation, own_use_power (the plants' own use for producing
                                            electricity), own_use_heat (for producing heat) and net_generation, each
                                            by technology and in total
    3.2 Bilance elektriny - spotreba [GWh]  a month: net_imports (ERU's cross-border balance), imports and exports at
                                            the transmission and distribution levels, losses (transmission,
                                            distribution, total), consumption by category, the grid operators' and
                                            the local consumption, pumping, gross and net domestic consumption, and
                                            the balance difference
    3.3 Vyvoj bilance a vyroby [GWh]        a year, 2016 to 2025: annual_gross_generation by technology and in total

    entity      eru:cz:<item>: total; a technology (nuclear, steam, ccgt, gas_combustion, hydro, pumped_storage, wind,
                solar); transmission, distribution; a consumption category (large_ehv, large_hv, small_business,
                households, grid_operators, local, pumping); gross_domestic, net_domestic
    variable    gross_generation, own_use_power, own_use_heat, net_generation, net_imports, imports, exports, losses,
                consumption, balance_difference (a month); annual_gross_generation (a year)
    unit        MWh (ERU's GWh times 1,000); ts_utc the month's or year's first day; freq P1M or P1Y; geo CZ
    node        ERU's label

ERU prints exports as negative figures; they are written positive (exports), and net_imports keeps ERU's sign (import
less export). Each row's twelve months must sum to its "Celkem" within 1 GWh, each month's technologies to its total
within 0.5 GWh, and every row given once; a row not in the map, a row of another width, or a figure of another form
stops the run. Nothing is filled. The rows of table 3.2 that repeat table 3.1's own use are not taken twice.

    python warehouse/connectors/eru_czech_electricity.py [--offline] [--fresh] [--out-dir DIR]

Ceiling: one request a run, saved in warehouse/raw/eru_reports/ and reused unless --fresh; --offline asks nothing.
eru.gov.cz's robots file closes Drupal's own paths only (session 2538). License: internal. ERU's site states "2026 (c)
Energeticky regulacni urad" and that its information is given under the Free Access to Information Act (106/1999); no
terms of reuse are given. Internal until a ruling.
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

NAME = "eru_czech_electricity"
CONNECTOR = "eru_reports"
SOURCE = "eru:rocni_zprava_elektro_2025"
HOST = "eru.gov.cz"
URL = "https://eru.gov.cz/sites/default/files/obsah/prilohy/eruelektro2025.pdf"
UA = {"User-Agent": "Mozilla/5.0 (compatible; ERW-connector/0.1; +https://github.com/SamuelEnrique/erw)"}
YEAR = 2025
CITATION = ("Energeticky regulacni urad (ERU), Rocni zprava o provozu elektrizacni soustavy Ceske republiky 2025, tables 3.1, 3.2 "
            "and 3.3")
TECH = {"Jaderné (JE)": "nuclear", "Parní (PE)": "steam", "Paroplynové (PPE)": "ccgt", "Plynové a spalovací (PSE)": "gas_combustion",
        "Vodní (VE)": "hydro", "Přečerpávací (PVE)": "pumped_storage", "Větrné (VTE)": "wind", "Fotovoltaické (FVE)": "solar"}
# table 3.1: a section's label (as its figure line begins) and its variable
SECT31 = [("Výroba elektřiny brutto", "gross_generation"), ("(TVS )", "own_use_power"),
          ("elektřiny na výrobu tepla (TVS)", "own_use_heat"), ("Výroba elektřiny netto", "net_generation")]
# table 3.2: label, (variable, item, sign), None for a row not taken
ROWS32 = {"Přeshraniční saldo *)": ("net_imports", "total", 1),
          "Import elektřiny na úrovni PS": ("imports", "transmission", 1),
          "Import elektřiny na úrovni DS": ("imports", "distribution", 1),
          "Export elektřiny na úrovni PS": ("exports", "transmission", -1),
          "Export elektřiny na úrovni DS": ("exports", "distribution", -1),
          "Celkové ztráty": ("losses", "total", 1),
          "v přenosové soustavě": ("losses", "transmission", 1),
          "v distribučních soustavách": ("losses", "distribution", 1),
          "Spotřeba elektřiny ČR": ("consumption", "total", 1),
          "Velkoodběr (VO) z hladiny vvn": ("consumption", "large_ehv", 1),
          "Velkoodběr (VO) z hladiny vn": ("consumption", "large_hv", 1),
          "Maloodběr podnikatelé (MOP)": ("consumption", "small_business", 1),
          "Maloodběr obyvatelstvo (MOO)": ("consumption", "households", 1),
          "Spotřeba PPS a PDS": ("consumption", "grid_operators", 1),
          "Lokální spotřeba": ("consumption", "local", 1),
          "Tech. vl. spotřeba na výrobu elektřiny": None,
          "Tech. vl. spotřeba na výrobu tepla": None,
          "Spotřeba na přečerpávání PVE": ("consumption", "pumping", 1),
          "Tuzemská brutto spotřeba (TBS)": ("consumption", "gross_domestic", 1),
          "Tuzemská netto spotřeba (TNS)": ("consumption", "net_domestic", 1),
          "Bilanční rozdíl": ("balance_difference", "total", 1)}
EN = chr(0x2013)  # the en dash of ERU's table titles
FIG = r"-?\d{1,3}(?: \d{3})*,\d"
X_COLS = ["x_label"]


def gwh(s):
    if not re.fullmatch(FIG, s):
        raise RuntimeError(f"not a figure: {s!r}")
    return float(s.replace(" ", "").replace(",", "."))


def split_line(ln, n):
    """(label, [n figures]) of a line ending in n figures, else None."""
    figs = list(re.finditer(r"(?:(?<=\s)|^)" + FIG + r"(?=\s|$)", ln))
    if len(figs) < n:
        return None
    tail = figs[-n:]
    rest = ln[tail[0].start():].split()
    if " ".join(rest) != " ".join(f.group(0) for f in tail):
        return None
    return ln[:tail[0].start()].strip(), [gwh(f.group(0)) for f in tail]


def page_with(pages, title):
    hits = [p for p in pages if title in p]
    if len(hits) != 1:
        raise RuntimeError(f"the page of {title!r} found {len(hits)} times")
    return hits[0]


def check_months(label, figs):
    if abs(sum(figs[:12]) - figs[12]) > 1.0:
        raise RuntimeError(f"{label!r}: the months sum to {sum(figs[:12]):.1f}, not to its total {figs[12]}")


def parse_pages(pages, base):
    rows, seen = [], set()

    def add(var, item, ts, freq, mwh, label):
        k = (var, item, ts)
        if k in seen:
            raise RuntimeError(f"{k} given twice")
        seen.add(k)
        rows.append(dict(entity=f"eru:cz:{item}", variable=var, ts_utc=ts, value=round(mwh, 3), unit="MWh", freq=freq, geo="CZ",
                         market="", node=label, **base, x_label=label))

    months = [f"{YEAR}-{m:02d}-01T00:00:00Z" for m in range(1, 13)]
    # table 3.1
    text = page_with(pages, "3.1 Bilance elektřiny " + EN + " zdroje [GWh]")
    section, got = None, {}
    for ln in text.splitlines():
        sp = split_line(ln, 13)
        if sp is None:
            continue
        label, figs = sp
        sec = next((v for s, v in SECT31 if label == s or label.endswith(s)), None)
        if sec:
            section, item = sec, "total"
        elif label in TECH and section:
            item = TECH[label]
        else:
            raise RuntimeError(f"table 3.1: a row not in the map: {label!r}")
        check_months(label, figs)
        got.setdefault(section, {})[item] = figs
        for ts, v in zip(months, figs[:12]):
            add(section, item, ts, "P1M", v * 1000, label)
    if set(got) != {v for _, v in SECT31}:
        raise RuntimeError(f"table 3.1: sections missing: {sorted({v for _, v in SECT31} - set(got))}")
    for sec, items in got.items():
        parts = [k for k in items if k != "total"]
        if sec != "own_use_heat" and len(parts) != len(TECH):
            raise RuntimeError(f"table 3.1 {sec}: {len(parts)} technologies")
        for m in range(13):
            if abs(sum(items[k][m] for k in parts) - items["total"][m]) > 0.5:
                raise RuntimeError(f"table 3.1 {sec}: column {m + 1} is not the sum of its technologies")
    # table 3.2: its first block, to the footnote (the chart's figures follow it on the page)
    text = page_with(pages, "3.2 Bilance elektřiny " + EN + " spotřeba [GWh]")
    body = text[:text.index("*) zahrnuty")]
    got32 = set()
    for ln in body.splitlines():
        sp = split_line(ln, 13)
        if sp is None:
            continue
        label, figs = sp
        if label not in ROWS32:
            raise RuntimeError(f"table 3.2: a row not in the map: {label!r}")
        if label in got32:
            raise RuntimeError(f"table 3.2: {label!r} given twice")
        got32.add(label)
        check_months(label, figs)
        if ROWS32[label] is None:
            continue
        var, item, sign = ROWS32[label]
        for ts, v in zip(months, figs[:12]):
            add(var, item, ts, "P1M", sign * v * 1000, label)
    if got32 != set(ROWS32):
        raise RuntimeError(f"table 3.2: rows missing: {sorted(set(ROWS32) - got32)}")
    # table 3.3: its second block, gross production by technology a year (to one decimal)
    text = page_with(pages, "3.3 Vývoj bilance a výroby elektřiny [GWh]")
    head = "2016 2017 2018 2019 2020 2021 2022 2023 2024 2025"
    if text.count(head) < 2:
        raise RuntimeError("table 3.3: its second block not found")
    i = text.index(head, text.index(head) + 1) + len(head)
    years, got33 = [f"{y}-01-01T00:00:00Z" for y in range(2016, 2026)], {}
    for ln in text[i:].splitlines():
        sp = split_line(ln, 10)
        if sp is None:
            if got33 and len(got33) == len(TECH) + 1:
                break
            continue
        label, figs = sp
        if label == "Výroba elektřiny brutto":
            item = "total"
        elif label in TECH:
            item = TECH[label]
        else:
            raise RuntimeError(f"table 3.3: a row not in the map: {label!r}")
        if item in got33:
            raise RuntimeError(f"table 3.3: {label!r} given twice")
        got33[item] = figs
        for ts, v in zip(years, figs):
            add("annual_gross_generation", item, ts, "P1Y", v * 1000, label)
        if len(got33) == len(TECH) + 1:
            break
    if len(got33) != len(TECH) + 1:
        raise RuntimeError(f"table 3.3: {len(got33)} rows, not {len(TECH) + 1}")
    for k in range(10):
        if abs(sum(got33[t][k] for t in TECH.values()) - got33["total"][k]) > 0.5:
            raise RuntimeError(f"table 3.3: {years[k][:4]} is not the sum of its technologies")
    if abs(got33["total"][9] - got["gross_generation"]["total"][12]) > 0.1:
        raise RuntimeError("table 3.3's 2025 differs from table 3.1's year")
    return pd.DataFrame(rows)


def parse(content, base):
    with pdfplumber.open(io.BytesIO(content)) as pdf:
        pages = [pg.extract_text() or "" for pg in pdf.pages[:20]]
    return parse_pages(pages, base)


def main(argv=None):
    ap = argparse.ArgumentParser(description="ERU: Czechia's electricity, from the annual report on the electricity system 2025")
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
        t = t[cols].sort_values(["variable", "entity", "ts_utc"]).reset_index(drop=True)
        y = t[(t.freq == "P1M") & (t.entity == "eru:cz:total")].groupby("variable").value.sum()
        head = [
            "Energy Research Warehouse (ERW): Energeticky regulacni urad (ERU), annual report on the operation of the Czech electricity system "
            "2025, tables 3.1 to 3.3: Czechia's production by technology and balance a month in 2025, and gross production a year, 2016 to "
            "2025 (session 2538)",
            "Shape: series (docs/datastandard.md v0). entity eru:cz:<item>; variable gross_generation, own_use_power, own_use_heat, "
            "net_generation, net_imports, imports, exports, losses, consumption, balance_difference (a month), annual_gross_generation (a year); unit MWh (ERU's GWh times 1,000); ts_utc "
            "the month's or year's first day; freq P1M (2025) or P1Y (annual_gross_generation, 2016 to 2025); geo CZ; node ERU's label.",
            f"{len(t)} rows; in 2025 gross production {y['gross_generation'] / 1e6:.3f} TWh, net production {y['net_generation'] / 1e6:.3f} TWh, "
            f"net imports {y['net_imports'] / 1e6:.3f} TWh (ERU's sign: import less export). Exports, printed negative by ERU, are written "
            "positive. Each row's months sum to its year and each month's technologies to its total; nothing is filled.",
            f"Retrieved: {run_id} (UTC) by warehouse/connectors/eru_czech_electricity.py; the report retrieved {base['retrieved_at']}; "
            f"last modified {base['vintage']}",
            f"Run log: warehouse/output/logs/{CONNECTOR}_{run_id}.log",
            f"Raw files: warehouse/raw/{CONNECTOR}/ (not in git)",
            f"Source: {SOURCE} {CITATION}",
            f"  access: {URL}",
            "License: internal. ERU's site states \"2026 (c) Energeticky regulacni urad\" and that its information is given under the Free "
            f"Access to Information Act (106/1999); no terms of reuse are given. Internal until a ruling. Cite: {CITATION}.",
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
            ip.update_sources([dict(source=SOURCE, publisher="Energeticky regulacni urad (ERU), Czechia",
                                    report="Rocni zprava o provozu elektrizacni soustavy Ceske republiky 2025, tables 3.1 to 3.3", report_url=URL,
                                    document_list="https://eru.gov.cz/", license="internal", tables=[NAME])])
        ip.write_status(CONNECTOR, run_id, results)
    log.close()
    return 0 if all(r["status"] == "ok" for r in results) else 1


if __name__ == "__main__":
    sys.exit(main())

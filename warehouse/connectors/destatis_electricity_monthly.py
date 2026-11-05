#!/usr/bin/env python3
"""Destatis's (the Federal Statistical Office's) monthly report on electricity and heat generation by energy source: the
plants for general supply in Germany, their gross and net electricity generation, net generation in combined heat and power,
and net heat generation, by energy source, for the latest month published (session 2807, chain 143).

Energy Research Warehouse (ERW) connector. One series table, warehouse/output/destatis_de_electricity_monthly.csv, from one
page of www.destatis.de (one request), whose table is the month's report:

    https://www.destatis.de/DE/Themen/Branchen-Unternehmen/Energie/Erzeugung/Tabellen/elekrizitaet-waermeerzeugung-energietraeger-monatsbericht.html

    entity      destatis:de or destatis:de:<the energy source's slug> (the German label transliterated: "Erdgas, Erdoelgas"
                gives erdgas_erdoelgas; the page prints "okereigas" for Kokereigas, coke oven gas, kept as printed)
    variable    gross_generation, net_generation, net_generation_chp (of which in combined heat and power),
                net_heat_generation, net_heat_generation_chp
    unit        MWh, as the page gives them
    ts_utc      the month's first day at 00:00:00Z, from the table's caption; freq P1M; geo DE
    node        "Destatis general supply, <the German label>, <the measure>"
    x_*         the page's label and its cell as printed

The page holds one month, provisional ("Vorlaeufige Angaben"), as of its "Stand" date; each run adds the month then published
and keeps the earlier months the table holds. The long series is in GENESIS-Online (table 43311-0002), whose API needs a
registered account, which the ERW does not make. Plants for general supply only: wind and solar are not in this survey,
and industrial plants are not either. A "." (unknown or confidential) has no row; a "-" (nothing) is zero. A cell's digits are
read whatever their grouping, and a cell grouped other than in threes (the page prints "10 420 92" for household waste's heat)
is counted. Compared: each column's parts against its total ("Insgesamt"; the parts fall short by what the "." cells hide,
never above), gross against net and net against its CHP part in each row; a case that does not hold is counted, kept as
printed. Checks that stop the run: no table, a caption without a German month and year, a header not the report's five
measures, a cell neither a number, "." nor "-", or no total row.

    python warehouse/connectors/destatis_electricity_monthly.py [--offline] [--out-dir DIR]

Ceiling: one request, reused from warehouse/raw/destatis_electricity/ with --offline. www.destatis.de's robots file
(session 2807, read 1604) disallows /SiteGlobals/ and a search servlet, not the tables, names no Claude agent, and sets a crawl
delay of 30 seconds, kept. License: Destatis's imprint (read 1606): "Vervielfaeltigung und Verbreitung, auch auszugsweise, mit
Quellennachweis gestattet" (reproduction and distribution, in part too, permitted with the source cited); source: Statistisches
Bundesamt (Destatis).
"""

import argparse
import datetime as dt
import html
import os
import re
import sys
import traceback

import pandas as pd

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import iso_prices as ip  # noqa: E402

NAME = "destatis_de_electricity_monthly"
CONNECTOR = "destatis_electricity"
SOURCE = "destatis:monatsbericht_elektrizitaet_waerme"
URL = ("https://www.destatis.de/DE/Themen/Branchen-Unternehmen/Energie/Erzeugung/Tabellen/"
       "elekrizitaet-waermeerzeugung-energietraeger-monatsbericht.html")
UA = {"User-Agent": "Mozilla/5.0 (compatible; ERW-connector/0.1; +https://github.com/SamuelEnrique/erw)"}
MEASURES = ["gross_generation", "net_generation", "net_generation_chp", "net_heat_generation", "net_heat_generation_chp"]
LABELS = {"gross_generation": "gross electricity generation", "net_generation": "net electricity generation",
          "net_generation_chp": "net electricity generation in CHP", "net_heat_generation": "net heat generation",
          "net_heat_generation_chp": "net heat generation in CHP"}
MONTHS = {"Januar": 1, "Februar": 2, "März": 3, "April": 4, "Mai": 5, "Juni": 6, "Juli": 7, "August": 8,
          "September": 9, "Oktober": 10, "November": 11, "Dezember": 12}
TOTAL = "Insgesamt"
COLS = ["entity", "variable", "ts_utc", "value", "unit", "freq", "geo", "market", "node", "source", "source_url",
        "retrieved_at", "vintage", "x_label", "x_cell"]


def text(s):
    return re.sub(r"\s+", " ", html.unescape(re.sub(r"<[^>]+>", "", s)).replace("­", "")).strip()


def slug(label):
    s = label.lower()
    for a, b in (("ä", "ae"), ("ö", "oe"), ("ü", "ue"), ("ß", "ss")):
        s = s.replace(a, b)
    return re.sub(r"[^a-z0-9]+", "_", s).strip("_")


def cell_value(raw):
    """(value or None, irregular grouping): '.' gives None, '-' (or '- -') zero, digits whatever their spaces."""
    c = raw.replace(" ", " ").strip()
    if c == ".":
        return None, False
    if re.fullmatch(r"-( -)*", c):
        return 0.0, False
    if re.fullmatch(r"\d+( \d+)*", c):
        groups = c.split(" ")
        irregular = len(groups) > 1 and (len(groups[0]) > 3 or any(len(g) != 3 for g in groups[1:]))
        return float("".join(groups)), irregular
    raise RuntimeError(f"a cell neither a number, '.' nor '-': {raw!r}")


def parse(content):
    s = content.decode("utf-8")
    m = re.search(r"<table[^>]*>(.*?)</table>", s, re.S)
    if not m:
        raise RuntimeError("no table on the page")
    tab = m.group(1)
    cap = text((re.search(r"<caption>(.*?)</caption>", tab, re.S) or [None, ""])[1])
    mm = re.search(r"(" + "|".join(MONTHS) + r") (\d{4})", cap)
    if not mm:
        raise RuntimeError(f"the caption names no German month and year: {cap!r}")
    month = (int(mm.group(2)), MONTHS[mm.group(1)])
    head = text((re.search(r"<thead>(.*?)</thead>", tab, re.S) or [None, ""])[1])
    for w in ("brutto", "netto", "insgesamt", "darunter", "KWK", "MWh"):
        if w not in head:
            raise RuntimeError(f"the header is not the report's five measures (no {w!r}): {head[:200]!r}")
    body = (re.search(r"<tbody>(.*?)</tbody>", tab, re.S) or [None, ""])[1]
    rows, irregular = [], []
    for tr in re.findall(r"<tr>(.*?)</tr>", body, re.S):
        cells = [text(c) if i == 0 else html.unescape(re.sub(r"<[^>]+>", "", c))
                 for i, c in enumerate(re.findall(r"<td[^>]*>(.*?)</td>", tr, re.S))]
        if len(cells) != 6:
            raise RuntimeError(f"a row without six cells: {cells}")
        label = cells[0]
        for k, raw in zip(MEASURES, cells[1:]):
            v, irr = cell_value(raw)
            if irr:
                irregular.append((label, k, raw.replace(" ", " ").strip()))
            rows.append((label, k, v, raw.replace(" ", " ").strip()))
    if not any(r[0] == TOTAL for r in rows):
        raise RuntimeError("no total row (Insgesamt)")
    stand = re.search(r"Stand(?:&nbsp;|\s)+(\d{1,2}\. \w+ \d{4})", s.replace(" ", " "))
    return month, rows, irregular, (stand.group(1) if stand else "")


def checks(rows):
    v = {(lab, k): x for lab, k, x, _ in rows}
    labels = [lab for lab in dict.fromkeys(r[0] for r in rows) if lab != TOTAL]
    parts = {}
    for k in MEASURES:
        got = sum(v[(lab, k)] or 0 for lab in labels)
        parts[k] = (got, v[(TOTAL, k)], any(v[(lab, k)] is None for lab in labels))
    off = []
    for lab in labels + [TOTAL]:
        for a, b in (("gross_generation", "net_generation"), ("net_generation", "net_generation_chp"),
                     ("net_heat_generation", "net_heat_generation_chp")):
            if v[(lab, a)] is not None and v[(lab, b)] is not None and v[(lab, a)] < v[(lab, b)]:
                off.append((lab, a, b))
    return parts, off


def frame(month, rows, retrieved, vintage):
    ts = f"{month[0]:04d}-{month[1]:02d}-01T00:00:00Z"
    out = []
    for lab, k, x, raw in rows:
        if x is None:
            continue
        ent = "destatis:de" if lab == TOTAL else f"destatis:de:{slug(lab)}"
        out.append({"entity": ent, "variable": k, "ts_utc": ts, "value": x, "unit": "MWh", "freq": "P1M", "geo": "DE",
                    "market": "", "node": f"Destatis general supply, {lab}, {LABELS[k]}", "source": SOURCE, "source_url": URL,
                    "retrieved_at": retrieved, "vintage": vintage, "x_label": lab, "x_cell": raw})
    t = pd.DataFrame(out, columns=COLS)
    twice = t[t.duplicated(["entity", "variable", "ts_utc"], keep=False)]
    if len(twice):
        raise RuntimeError(f"a key given twice: {twice.entity.iloc[0]} {twice.variable.iloc[0]}")
    return t


def main(argv=None):
    ap = argparse.ArgumentParser(description="Destatis: Germany's general supply plants' electricity and heat, the latest month")
    ap.add_argument("--offline", action="store_true", help="the saved page only, no request")
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
        if not args.offline and (ip.paused("destatis") or ip.paused_host("www.destatis.de")):
            raise RuntimeError("Destatis is paused (warehouse/metadata/paused_sources.csv): not requested")
        content, rec = ip.fetch_raw(CONNECTOR, URL, log, offline=args.offline, fresh=not args.offline, headers=UA, timeout=120)
        month, rows, irregular, stand = parse(content)
        parts, off = checks(rows)
        t = frame(month, rows, rec.get("retrieved_at") or "", ip.vintage_of(rec))
        for k, (got, tot, hidden) in parts.items():
            log(f"  {k}: the parts {got:,.0f} MWh of the total {tot:,.0f}" + (" (some '.' cells)" if hidden else ""))
            if got > tot + 1:
                off.append((TOTAL, k, "the parts above the total"))
        for x in irregular:
            log(f"  a cell grouped other than in threes, read as its digits: {x}")
        for x in off:
            log(f"  not as expected, kept as printed: {x}")
        unknown = sum(1 for r in rows if r[2] is None)
        g = parts["net_generation"]
        header = [
            f"Energy Research Warehouse (ERW): Destatis, Monatsbericht ueber die Elektrizitaets- und Waermeerzeugung der Stromerzeugungsanlagen fuer die allgemeine Versorgung: Germany's general supply plants by energy source, {month[0]}-{month[1]:02d} (provisional; Stand {stand or 'not given'}) (session 2807)",
            "Shape: series (docs/datastandard.md v0). entity destatis:de (Insgesamt) or destatis:de:<the energy source's slug>; variable gross_generation, net_generation, net_generation_chp, net_heat_generation or net_heat_generation_chp; unit MWh; ts_utc the month's first day; freq P1M; geo DE; x_label and x_cell the page's label and cell. "
            "Plants for general supply only: wind and solar are not in this survey, nor industrial plants.",
            f"{len(t)} rows, {t.entity.nunique()} entities. {unknown} cells '.' (unknown or confidential) have no row; '-' is zero; nothing is filled. Net generation: the parts {g[0]:,.0f} MWh of the total {g[1]:,.0f}. "
            f"{len(irregular)} cell(s) grouped other than in threes, read as their digits; {len(off)} row or column comparison(s) not as expected, kept as printed; both listed in the run log.",
            f"Retrieved: {run_id} (UTC) by warehouse/connectors/destatis_electricity_monthly.py; the page retrieved {rec.get('retrieved_at') or ''}",
            f"Run log: warehouse/output/logs/{CONNECTOR}_{run_id}.log",
            f"Raw files: warehouse/raw/{CONNECTOR}/ (not in git)",
            f"Source: {SOURCE} Statistisches Bundesamt (Destatis), Elektrizitaets- und Waermeerzeugung nach Energietraegern (Monatsbericht), {URL}",
            "  long series: GENESIS-Online table 43311-0002 (not read: its API needs a registered account)",
            "License: Destatis's imprint: reproduction and distribution, in part too, permitted with the source cited. Source: Statistisches Bundesamt (Destatis), 2026; reshaped by the ERW.",
        ]
        ip.write_csv(t, NAME, header, log, cols=COLS)
        if not args.out_dir:
            ip.update_sources([dict(source=SOURCE, publisher="Statistisches Bundesamt (Destatis)",
                                    report="Elektrizitaets- und Waermeerzeugung nach Energietraegern (Monatsbericht)",
                                    report_url=URL, document_list=URL, license="public", tables=[NAME])])
        results.append(dict(table=NAME, market="all", status="ok", detail=f"{len(t)} rows"))
        print(f"{NAME}: {len(t)} rows for {month[0]}-{month[1]:02d}; unknown {unknown}; irregular {len(irregular)}; off {len(off)}; net parts {g[0]:,.0f} of {g[1]:,.0f}")
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

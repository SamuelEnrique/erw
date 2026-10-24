#!/usr/bin/env python3
"""Botswana's electricity a month, from Statistics Botswana's Electricity Generation and Distribution Stats Brief: local
generation, imports and distribution, January 2016 to the brief's last month, and the brief's quarter by source
(generation by coal, diesel and solar; imports from Eskom, the SAPP markets and cross-border supply) (session 2421, chain
115: Botswana's electricity).

Energy Research Warehouse (ERW) connector. One series table, warehouse/output/statsbots_botswana_electricity_monthly.csv,
from the brief's tables 2, 3, 7, 10 and 11 (read with pdfplumber's text), two requests: the home page, which links the
newest brief, and the brief itself (the second quarter of 2026 when written):

    https://www.statsbots.org.bw/
    https://www.statsbots.org.bw/sites/default/files/Electricity%20Generation%20and%20Distribution%20Stats%20Brief%2C%20Second%20Quarter%202026.pdf

    entity     statsbots_bw:BW; geo BW; node Botswana
    variable   generation (electricity generated locally), imports, distribution (MWh), freq P1M, ts_utc the month's 1st;
               generation_<source> (coal, diesel, solar) and imports_<source> (eskom, sapp_markets, cross_border), MWh,
               freq P3M, ts_utc the quarter's first day: the brief's one quarter by source

Checks: each year's months add to its quarters and its quarters to its total (within 2 MWh; the imports to 0.1 decimals
as printed, within 2 MWh), and each month's distribution equals its generation plus imports within 1.5 MWh, as it does
in 125 of the brief's 126 months. The one exception: the brief's February 2026 distribution (292,427 MWh) is that
month's generation printed again (generation plus imports is 344,839 MWh, which the first quarter's printed total,
1,122,208 MWh, also implies), so a distribution month equal to its generation that fails the identity is not taken and
the header names it; any other failure stops the run. The quarter by source must add to its total, and its totals to
the quarter's monthly tables within 1 MWh. A header not the brief's, a value that is not a number or a month not read
stops the run. Nothing is filled. The indices and percentage changes (tables 1, 4 to 6, 8, 9, 12 to 14) are not taken.

    python warehouse/connectors/statsbots_botswana.py [--offline] [--out-dir DIR]

Ceiling: two requests, reused from warehouse/raw/statsbots_botswana/ with --offline. www.statsbots.org.bw's robots file
asks a crawl delay of 10 seconds, kept between the two requests, disallows Drupal's system paths and /search/, and names
no AI agent (session 2421). License: its terms of use (read in session 2421): "users may utilise the information as they
wish, provided that they acknowledge Statistics Botswana as the source of the basic data", and specify that the analysis
is their own; internal until the licenses' round writes the verdict.
"""

import argparse
import datetime as dt
import io
import os
import re
import sys
import time
import traceback

import pandas as pd
import pdfplumber

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import iso_prices as ip  # noqa: E402

NAME = "statsbots_botswana_electricity_monthly"
CONNECTOR = "statsbots_botswana"
SOURCE = "statsbots:electricity_stats_brief"
HOME = "https://www.statsbots.org.bw/"
UA = {"User-Agent": "Mozilla/5.0 (compatible; ERW-connector/0.1; +https://github.com/SamuelEnrique/erw)"}
COLS = ["entity", "variable", "ts_utc", "value", "unit", "freq", "geo", "market", "node", "source", "source_url",
        "retrieved_at", "vintage"]
MONTHS = ["jan", "feb", "mar", "apr", "may", "jun", "jul", "aug", "sep", "oct", "nov", "dec"]
QUARTER = {"first": 1, "second": 4, "third": 7, "fourth": 10}
TABLES = {"3": "generation", "7": "imports", "11": "distribution"}
GEN_SOURCES = {"Coal": "coal", "Diesel": "diesel", "Solar": "solar"}
IMP_SOURCES = {"Eskom (SA)": "eskom", "SAPP Markets (SADC)": "sapp_markets", "Cross Border": "cross_border"}
NUM = r"\d{1,3}(?:,\d{3})*(?:\.\d+)?|\d+(?:\.\d+)?"
TOL = 2.0


def num(tok, what):
    t = (tok or "").strip()
    if not re.fullmatch(NUM, t):
        raise RuntimeError(f"{what}: not a number: {t!r}")
    return float(t.replace(",", ""))


def brief_url(home):
    m = re.search(r'href="([^"]+Electricity[^"]+Stats%20Brief[^"]*\.pdf)"', home)
    if not m:
        raise RuntimeError("the home page links no Electricity Generation and Distribution Stats Brief")
    return requests_url(m.group(1))


def requests_url(u):
    return u if u.startswith("http") else HOME.rstrip("/") + "/" + u.lstrip("/")


def segment(text, n):
    i = text.rfind(f"\nTable {n}:")  # the last: the table of contents comes first
    if i < 0:
        raise RuntimeError(f"no Table {n} in the brief")
    j = text.find("Note:", i)
    return text[i + 1:j if j > 0 else len(text)]


def monthly(text, n):
    """{(year, month): value} of table n, and its sums: [(months, printed quarter or year total)]."""
    lines = segment(text, n).splitlines()
    head = next((l for l in lines if l.startswith("Period ")), "")
    years = [int(y.rstrip("*")) for y in head.split()[1:]]
    if not years or years != list(range(years[0], years[0] + len(years))):
        raise RuntimeError(f"Table {n}'s header is not the brief's: {head!r}")
    rows, quarters, totals = {}, {}, None
    for line in lines[1:]:
        toks = line.split()
        if not toks:
            continue
        key = toks[0].lower()
        if not (key[:3] in MONTHS or re.fullmatch(r"q[1-4]", key) or key in ("total", "year")):
            continue  # the title, the header and the notes
        vals = [num(t, f"Table {n} {toks[0]}") for t in toks[1:]]
        if key[:3] in MONTHS:
            m = MONTHS.index(key[:3]) + 1
            if m in rows:
                raise RuntimeError(f"Table {n}: {toks[0]} twice")
            rows[m] = vals
        elif re.fullmatch(r"q[1-4]", key):
            quarters[int(key[1])] = vals
        elif key in ("total", "year"):
            totals = vals
    if sorted(rows) != list(range(1, 13)) or sorted(quarters) != [1, 2, 3, 4] or totals is None:
        raise RuntimeError(f"Table {n}: months {sorted(rows)}, quarters {sorted(quarters)}")
    out, sums = {}, []
    for k, y in enumerate(years):
        have = [m for m in range(1, 13) if len(rows[m]) > k]
        if have != list(range(1, len(have) + 1)):
            raise RuntimeError(f"Table {n} {y}: months not in order: {have}")
        for m in have:
            out[(y, m)] = rows[m][k]
        for q in range(1, 5):
            ms = [m for m in range(3 * q - 2, 3 * q + 1) if m in have]
            if len(ms) == 3:
                if len(quarters[q]) <= k:
                    raise RuntimeError(f"Table {n} {y} Q{q}: no quarter total")
                sums.append(([(y, m) for m in ms], quarters[q][k]))
        if len(totals) <= k:
            raise RuntimeError(f"Table {n} {y}: no year total")
        sums.append(([(y, m) for m in have], totals[k]))
    return out, sums


def check_sums(n, values, sums):
    for keys, printed in sums:
        if abs(sum(values[k] for k in keys) - printed) > TOL:
            raise RuntimeError(f"Table {n} {keys[0][0]}: months {keys[0][1]} to {keys[-1][1]} do not add to the printed {printed}")


def by_source(text, n, names):
    seg = segment(text, n)
    m = re.search(r"in MWH: (First|Second|Third|Fourth) Quarter (\d{4})", seg)
    if not m:
        raise RuntimeError(f"Table {n}'s title is not the brief's")
    got = {}
    for line in seg.splitlines():
        for label in list(names) + ["Total"]:
            mm = re.fullmatch(rf"{re.escape(label)} ({NUM}) [\d.]+", line)
            if mm:
                got[label] = num(mm.group(1), f"Table {n} {label}")
    if set(got) != set(names) | {"Total"}:
        raise RuntimeError(f"Table {n}: rows missing: {set(names) | {'Total'} - set(got)}")
    if abs(sum(got[l] for l in names) - got["Total"]) > 1.0:
        raise RuntimeError(f"Table {n}: the sources do not add to the total")
    return int(m.group(2)), QUARTER[m.group(1).lower()], got


def parse(text):
    """The rows from the brief's text: (variable, year, month, value, freq), and the distribution months not taken."""
    (gen, gs), (imp, is_), (dist, ds) = (monthly(text, n) for n in TABLES)
    if set(gen) != set(imp) or set(gen) != set(dist):
        raise RuntimeError("the three tables cover different months")
    check_sums("3", gen, gs)
    check_sums("7", imp, is_)
    out, left, sound = [], [], dict(dist)
    for (y, m) in sorted(gen):
        out.append(("generation", y, m, gen[(y, m)], "P1M"))
        out.append(("imports", y, m, imp[(y, m)], "P1M"))
        if abs(gen[(y, m)] + imp[(y, m)] - dist[(y, m)]) > 1.5:
            if dist[(y, m)] == gen[(y, m)] and imp[(y, m)] > 0:
                left.append((y, m, dist[(y, m)], gen[(y, m)] + imp[(y, m)]))
                sound[(y, m)] = gen[(y, m)] + imp[(y, m)]  # only to check the printed totals, never written
                continue
            raise RuntimeError(f"{y}-{m:02d}: distribution {dist[(y, m)]} is not generation plus imports ({gen[(y, m)] + imp[(y, m)]})")
        out.append(("distribution", y, m, dist[(y, m)], "P1M"))
    check_sums("11", sound, ds)  # the printed quarters and years agree with generation plus imports for a month left out
    for n, names, var, monthly_ in (("2", GEN_SOURCES, "generation", gen), ("10", IMP_SOURCES, "imports", imp)):
        y, m0, got = by_source(text, n, names)
        months = [(y, m) for m in range(m0, m0 + 3)]
        if not all(k in monthly_ for k in months) or abs(sum(monthly_[k] for k in months) - got["Total"]) > 1.0:
            raise RuntimeError(f"Table {n}: its total is not the quarter's {var} in the monthly table")
        for label, s in names.items():
            out.append((f"{var}_{s}", y, m0, got[label], "P3M"))
    return out, left


def finish(rows, retrieved, vintage, url):
    t = pd.DataFrame([dict(entity="statsbots_bw:BW", variable=v, ts_utc=f"{y}-{m:02d}-01T00:00:00Z", value=x, unit="MWh", freq=f,
                           geo="BW", market="", node="Botswana", source=SOURCE, source_url=url, retrieved_at=retrieved,
                           vintage=vintage) for v, y, m, x, f in rows], columns=COLS)
    if t.duplicated(["entity", "variable", "ts_utc"]).any():
        raise RuntimeError("a key given twice")
    return t.sort_values(["variable", "ts_utc"]).reset_index(drop=True)


def main(argv=None):
    ap = argparse.ArgumentParser(description="Statistics Botswana's electricity stats brief: generation, imports and distribution a month")
    ap.add_argument("--offline", action="store_true", help="the saved pages only, no request")
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
        if not args.offline and (ip.paused("statsbots") or ip.paused_host("www.statsbots.org.bw")):
            raise RuntimeError("Statistics Botswana is paused (warehouse/metadata/paused_sources.csv): not requested")
        home, _ = ip.fetch_raw(CONNECTOR, HOME, log, offline=args.offline, fresh=not args.offline, headers=UA, timeout=120)
        url = brief_url(home.decode("utf-8", errors="replace"))
        if not args.offline:
            time.sleep(10)  # the robots file's crawl delay
        content, rec = ip.fetch_raw(CONNECTOR, url, log, offline=args.offline, headers=UA, timeout=300)
        with pdfplumber.open(io.BytesIO(content)) as pdf:
            text = "\n" + "\n".join(p.extract_text() or "" for p in pdf.pages)
        rows, left = parse(text)
        t = finish(rows, rec.get("retrieved_at") or "", ip.vintage_of(rec), url)
        mon = t[t.freq == "P1M"]
        header = [
            f"Energy Research Warehouse (ERW): Statistics Botswana, Electricity Generation and Distribution Stats Brief, Botswana's local generation, imports and distribution a month, {mon.ts_utc.min()[:7]} to {mon.ts_utc.max()[:7]}, and the brief's quarter by source (session 2421)",
            "Shape: series (docs/datastandard.md v0). entity statsbots_bw:BW; variable generation (generated locally), imports, distribution (MWh, freq P1M, ts_utc the month's 1st); generation_coal, generation_diesel, generation_solar, imports_eskom, imports_sapp_markets, imports_cross_border "
            "(MWh, freq P3M, ts_utc the quarter's first day: the brief's one quarter by source); geo BW.",
            f"{len(t)} rows. Each year's months add to its quarters and total, and each month's distribution equals its generation plus imports within 1.5 MWh. "
            + "".join(f"The brief's distribution for {y}-{m:02d} ({d:,.0f} MWh) is that month's generation printed again (generation plus imports is {s:,.0f} MWh), so it has no row. " for y, m, d, s in left)
            + "The indices and percentage changes are not taken. Nothing is filled.",
            f"Retrieved: {run_id} (UTC) by warehouse/connectors/statsbots_botswana.py; the brief retrieved {rec.get('retrieved_at') or ''}",
            f"Run log: warehouse/output/logs/{CONNECTOR}_{run_id}.log",
            f"Raw files: warehouse/raw/{CONNECTOR}/ (not in git)",
            f"Source: {SOURCE} Statistics Botswana, Electricity Generation and Distribution Stats Brief (tables 2, 3, 7, 10 and 11), linked from {HOME}",
            f"  access: {url}",
            "License: internal until the licenses' round writes the verdict. Statistics Botswana's terms of use: users \"may utilise the information as they wish, provided that they acknowledge Statistics Botswana as the source of the basic data\"; this table is the ERW's own processing of it. Cite: Statistics Botswana, Electricity Generation and Distribution Stats Brief.",
        ]
        ip.write_csv(t, NAME, header, log, cols=COLS)
        if not args.out_dir:
            ip.update_sources([dict(source=SOURCE, publisher="Statistics Botswana",
                                    report="Electricity Generation and Distribution Stats Brief (tables 2, 3, 7, 10 and 11)",
                                    report_url=HOME, document_list=url, license="internal", tables=[NAME])])
        results.append(dict(table=NAME, market="all", status="ok", detail=f"{len(t)} rows"))
        print(f"{NAME}: {len(t)} rows; distribution months not taken: {[(y, m) for y, m, *_ in left]}")
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

#!/usr/bin/env python3
"""Bahrain's electricity, a year, 2020 to 2024: units sent out by station, the two interconnectors' net flows, the
stations' maximum generation capacity, the annual maximum and minimum load, and consumption by sector, as the Electricity
and Water Authority (EWA) gives them in its Statistical Book 2024 (session 2490, chain 121).

Energy Research Warehouse (ERW) connector. One series table, warehouse/output/ewa_bahrain_electricity_annual.csv, from
one PDF (no key):

    https://ewa-new-website-ireland.s3.eu-west-1.amazonaws.com/uploads/book_2024_final_p_1.pdf

linked from https://www.ewa.bh/en/publications. Five of the book's tables are read, each found by its English title, its
rows the five lines that end in the years 2020 to 2024 in order. The book prints some figures in Arabic-Indic digits
(read as their ASCII digits) and keeps an older edition's years under the visible ones in white: characters drawn in
white are dropped before the page is read.

    table (page)                                         variable                    entity ewa:bh:<item>      unit
    Electricity Production from Power Stations (9)       sent_out (a station)        sitra ... al_dur_2        MWh
                                                         net_imports (a link)        gcc_link, alba_link       MWh
                                                         supply (their sum)          total                     MWh
    Total Generated Electricity Units (10)               sent_out                    ewa_stations, ipp_stations MWh
    Power Stations and Other Sources Installed           max_generation_capacity     a station                 MW
      Capacity (12)                                      net_transfer_capacity       a link                    MW
                                                         capacity_with_links         total                     MW
    Development of Maximum & Minimum Load (15)           peak_load, minimum_load,    system                    MW
                                                         installed_capacity
    Electricity Consumption by Sectors (44)              consumption                 domestic, commercial,     MWh
                                                                                     industrial, agricultural,
                                                                                     total

EWA gives energy in GWh (million kWh for consumption): the value is multiplied by 1,000 to MWh. A link's negative flow is
power sent from Bahrain's grid to the link, as EWA notes. The maximum generation capacity is at 40 degrees C. Page 10's
total and imports repeat page 9's sums: they are checked against them (a difference stops the run) and not written. A cell
"-" has no row. A cell not in the form of its table (a decimal point where the table prints whole numbers, as 2023's
commercial consumption "5.348") has no row and is counted in the header. A table not found, a row count other than five,
years not 2020 to 2024 in order, or a row of another width stops the run. Nothing is filled. The load table's ratio and
increase columns, the network table, the fuel tables and the water tables are not taken.

    python warehouse/connectors/ewa_bahrain_electricity.py [--offline] [--out-dir DIR]

Ceiling: one request a run, saved in warehouse/raw/ewa_bahrain_statistics/ and reused unless --fresh; --offline asks
nothing. www.ewa.bh's robots file allows every path (session 2490); the bucket's answers HTTP 403 (no such object).
License: not settled. EWA's terms of use: "Reproduction is prohibited other than in accordance with the copyright
notice"; no grant of reuse is stated. Internal until a ruling.
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

NAME = "ewa_bahrain_electricity_annual"
CONNECTOR = "ewa_bahrain_statistics"
SOURCE = "ewa:statistical_book"
HOST = "ewa-new-website-ireland.s3.eu-west-1.amazonaws.com"
URL = "https://ewa-new-website-ireland.s3.eu-west-1.amazonaws.com/uploads/book_2024_final_p_1.pdf"
LISTING = "https://www.ewa.bh/en/publications"
UA = {"User-Agent": "Mozilla/5.0 (compatible; ERW-connector/0.1; +https://github.com/SamuelEnrique/erw)"}
YEARS = ["2020", "2021", "2022", "2023", "2024"]
DIGITS = {**{chr(0x0660 + i): str(i) for i in range(10)}, **{chr(0x06F0 + i): str(i) for i in range(10)}}
STATIONS = ["sitra", "riffa", "al_hidd", "al_ezzel", "al_dur", "al_dur_2"]
LINKS = ["gcc_link", "alba_link"]
WIDE = ["total", "gcc_link", "alba_link", "al_dur_2", "al_dur", "al_ezzel", "al_hidd", "riffa", "sitra"]
LABEL = {"sitra": "Sitra", "riffa": "Riffa", "al_hidd": "Al-Hidd", "al_ezzel": "Al-Ezzel", "al_dur": "Al-Dur", "al_dur_2": "Al-Dur 2",
         "gcc_link": "GCC Link", "alba_link": "ALBA Link"}
# title -> (the row's columns left to right, each (item, variable, label) or None; decimals allowed; unit; to MWh or MW factor)
TABLES = {
    "Electricity Production from Power Stations and Other Sources": (
        [("total", "supply", "Total units sent out and imported (GWh)")]
        + [(c, "net_imports" if c in LINKS else "sent_out", f"{LABEL[c]} (GWh)") for c in WIDE[1:]], True, "MWh", 1000.0),
    "Total Generated Elecricity Units from Power Stations & Other Sources": (
        [("total", "check_supply", ""), ("imported", "check_imports", ""),
         ("ipp_stations", "sent_out", "IPP Power Production (GWh)"), ("ewa_stations", "sent_out", "EWA Power Production (GWh)")],
        True, "MWh", 1000.0),
    "Power Stations and Other Sources Installed Capacity": (
        [("total", "capacity_with_links", "Total (MW)")]
        + [(c, "net_transfer_capacity" if c in LINKS else "max_generation_capacity", f"{LABEL[c]} (MW)") for c in WIDE[1:]],
        False, "MW", 1.0),
    "Development of Maximum & Minimum Load": (
        [None, None, ("system", "minimum_load", "Annual Minimum Load (MW)"), None,
         ("system", "peak_load", "Annual Maximum Load (MW)"), ("system", "installed_capacity", "Installed Capacity (MW)")],
        False, "MW", 1.0),
    "Electricity Consumption by Sectors": (
        [("total", "consumption", "Total (million kWh)"), ("agricultural", "consumption", "Agricultural (million kWh)"),
         ("industrial", "consumption", "Industrial (million kWh)"), ("commercial", "consumption", "Commercial (million kWh)"),
         ("domestic", "consumption", "Domestic (million kWh)")], False, "MWh", 1000.0),
}
X_COLS = ["x_label", "x_page"]


def ascii_digits(s):
    return "".join(DIGITS.get(ch, ch) for ch in s)


def visible_text(page):
    """The page's text without the characters drawn in white (an older edition's years kept under the visible ones)."""
    def keep(o):
        return o.get("object_type") != "char" or tuple(o.get("non_stroking_color") or ()) not in ((1, 1, 1), (1.0, 1.0, 1.0))
    return ascii_digits(page.filter(keep).extract_text() or "")


def number(tok, decimals):
    """A cell's value, or None for '-', or the string 'bad' for a cell out of its table's form."""
    tok = tok.strip()
    if tok == "-":
        return None
    form = r"-?\d{1,3}(,\d{3})*(\.\d+)?" if decimals else r"-?(\d{1,3}(,\d{3})*|\d+)"
    if not re.fullmatch(form, tok):
        return "bad"
    return float(tok.replace(",", ""))


def table_rows(text, title, width):
    """The five rows after the title: lines that end in a year and hold `width` cells before it."""
    if title not in text:
        raise RuntimeError(f"table not found: {title!r}")
    rows = []
    for ln in text[text.index(title) + len(title):].splitlines():
        toks = ln.split()
        if len(toks) < 2 or not re.fullmatch(r"20\d\d", toks[-1]):
            continue
        if not all(re.fullmatch(r"-|-?[\d,.]+%?", t) for t in toks[:-1]):
            continue
        rows.append(toks)
        if len(rows) == len(YEARS):
            break
    years = [r[-1] for r in rows]
    if years != YEARS:
        raise RuntimeError(f"{title!r}: rows for {years}, not {YEARS}")
    for r in rows:
        if len(r) - 1 != width:
            raise RuntimeError(f"{title!r}: a row of {len(r) - 1} cells, not {width}: {' '.join(r)}")
    return rows


def parse_text(pages, base, counts):
    """pages: (page number, visible text). Returns the table's rows; page 10's sums checked against page 9's."""
    out, seen, checks = [], set(), {}
    for title, (cols, decimals, unit, factor) in TABLES.items():
        found = [(n, t) for n, t in pages if title in t]
        if len(found) != 1:
            raise RuntimeError(f"{title!r} found on {len(found)} pages")
        pno, text = found[0]
        for toks in table_rows(text, title, len(cols)):
            year = toks[-1]
            for spec, tok in zip(cols, toks[:-1]):
                if spec is None:
                    continue
                item, var, label = spec
                v = number(tok, decimals)
                if v is None:
                    continue
                if v == "bad":
                    counts["cells out of form"] = counts.get("cells out of form", 0) + 1
                    continue
                if var.startswith("check_"):
                    checks[(var, year)] = v
                    continue
                key = (item, var, year)
                if key in seen:
                    raise RuntimeError(f"{key} given twice")
                seen.add(key)
                out.append(dict(entity=f"ewa:bh:{item}", variable=var, ts_utc=f"{year}-01-01T00:00:00Z", value=round(v * factor, 3),
                                unit=unit, freq="P1Y", geo="BH", market="", node=label, **base, x_label=label, x_page=pno))
    t = pd.DataFrame(out)
    if t.empty:
        raise RuntimeError("no value in the tables")
    for year in YEARS:
        ts = f"{year}-01-01T00:00:00Z"
        y = t[t.ts_utc == ts]
        supply = y[(y.variable == "supply")].value.sum()
        links = y[y.variable == "net_imports"].value.sum()
        if ("check_supply", year) in checks and abs(checks[("check_supply", year)] * 1000 - supply) > 1000:
            raise RuntimeError(f"{year}: page 10's total {checks[('check_supply', year)]} GWh is not page 9's {supply / 1000} GWh")
        if ("check_imports", year) in checks and abs(checks[("check_imports", year)] * 1000 - links) > 1000:
            raise RuntimeError(f"{year}: page 10's imports {checks[('check_imports', year)]} GWh are not page 9's links {links / 1000} GWh")
    return t


def parse(content, base, counts):
    with pdfplumber.open(io.BytesIO(content)) as pdf:
        pages = []
        for i, pg in enumerate(pdf.pages):
            raw = pg.extract_text() or ""
            if any(title in raw for title in TABLES):
                pages.append((i + 1, visible_text(pg)))
    return parse_text(pages, base, counts)


def main(argv=None):
    ap = argparse.ArgumentParser(description="EWA: Bahrain's electricity, 2020 to 2024, from the Statistical Book 2024")
    ap.add_argument("--offline", action="store_true", help="the saved book only, no request")
    ap.add_argument("--fresh", action="store_true", help="ask for the book again")
    ap.add_argument("--out-dir", help="a trial: the table under this folder, not warehouse/output")
    args = ap.parse_args(argv)
    if ip.paused(CONNECTOR) or ip.paused_host(HOST) or ip.paused_host("www.ewa.bh"):
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
        s = t[t.variable == "supply"].set_index("ts_utc").value / 1e6
        pk = t[t.variable == "peak_load"].set_index("ts_utc").value
        head = [
            "Energy Research Warehouse (ERW): Electricity and Water Authority (EWA), Kingdom of Bahrain, Statistical Book 2024, "
            f"Bahrain's electricity, {t.ts_utc.min()[:4]} to {t.ts_utc.max()[:4]} (session 2490)",
            "Shape: series (docs/datastandard.md v0). entity ewa:bh:<item> (a station, a link, ewa_stations, ipp_stations, system, a sector, total); "
            "variable sent_out, net_imports, supply (MWh, from EWA's GWh), max_generation_capacity (at 40 C), net_transfer_capacity, capacity_with_links, "
            "peak_load, minimum_load, installed_capacity (MW), consumption (MWh, from EWA's million kWh); ts_utc the year's 1 January; freq P1Y; geo BH. "
            "A link's negative flow is power sent from Bahrain's grid to the link. supply is the stations' sent out plus the links' net flows.",
            f"{len(t)} rows; supply TWh: " + ", ".join(f"{k[:4]} {v:.2f}" for k, v in s.items())
            + "; peak load MW: " + ", ".join(f"{k[:4]} {v:,.0f}" for k, v in pk.items())
            + f". Not taken: cells '-' (no row), cells out of form {counts.get('cells out of form', 0)}, page 10's total and imports (checked against page 9's). Nothing is filled.",
            f"Retrieved: {run_id} (UTC) by warehouse/connectors/ewa_bahrain_electricity.py; the book retrieved {base['retrieved_at']}; last modified {base['vintage']}",
            f"Run log: warehouse/output/logs/{CONNECTOR}_{run_id}.log",
            f"Raw files: warehouse/raw/{CONNECTOR}/ (not in git)",
            f"Source: {SOURCE} EWA, Statistical Book 2024, tables on pages 9, 10, 12, 15 and 44 (listed at {LISTING})",
            f"  access: {URL}",
            "License: internal (EWA's terms of use: reproduction is prohibited other than in accordance with the copyright notice; no grant of reuse).",
        ]
        ip.write_snapshot(t, NAME, head, log, cols)
        results.append(dict(table=NAME, market="all", status="ok", detail=f"{len(t)} rows"))
        print(f"{NAME}: {len(t)} rows, {t.entity.nunique()} entities, {t.variable.nunique()} variables; {counts}")
    except Exception:
        tb = ip.redact(traceback.format_exc())
        log(f"{NAME} FAILED, no output file written:\n{tb}")
        print(f"{NAME} FAILED, no output file written: {tb.strip().splitlines()[-1]}", file=sys.stderr)
        results.append(dict(table=NAME, market="all", status="failed", detail=tb.strip().splitlines()[-1][:300]))
    if not args.out_dir:
        if results and results[0]["status"] == "ok":
            ip.update_sources([dict(source=SOURCE, publisher="Electricity and Water Authority, Kingdom of Bahrain (EWA)",
                                    report="Statistical Book 2024 (electricity production, capacity, load and consumption)", report_url=URL,
                                    document_list=LISTING, license="internal", tables=[NAME])])
        ip.write_status(CONNECTOR, run_id, results)
    log.close()
    return 0 if all(r["status"] == "ok" for r in results) else 1


if __name__ == "__main__":
    sys.exit(main())

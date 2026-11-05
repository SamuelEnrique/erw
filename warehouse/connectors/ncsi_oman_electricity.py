#!/usr/bin/env python3
"""Oman's electricity, a year, 2023 to 2025: production, distribution and connections by governorate, and production by
source, as the National Centre for Statistics and Information (NCSI) gives them in tables 11 and 12 of its "Energy
Statistics 2026, Fifth Edition - data 2025" (from the Public Services Regulatory Authority's figures) (session 2504,
chain 122; in place of Kuwait, whose hosts did not serve its figures).

Energy Research Warehouse (ERW) connector. One series table, warehouse/output/ncsi_oman_electricity_annual.csv, from one
PDF (no key):

    https://api.ncsi.gov.om/uploads/pdfs/energy_statistics_bulletin_2026_1783504139.pdf

    table (page)                                               variable              entity ncsi:om:<item>      unit
    11 Production and distribution of electrical energy by     production,           a governorate (muscat ...   MWh
       governorate (46)                                        distribution          al_wusta, others), total
                                                               connections                                       count
    12 Total electrical energy production and its sources (48) production_by_source  diesel, gas, solar, wind,   MWh
                                                                                     other, total

Table 11's figures are GWh (times 1,000 to MWh) and thousands of connections (times 1,000). Each of its rows holds nine
figures, the three years' connections, distribution and production, 2025 first. The order is checked: the production
total of each year must equal table 12's total within 0.1 TWh, or the run stops. Table 12's figures are TWh with one
decimal (times 1,000,000). The bulletin prints table 11 twice (pages 46 and 47); the first is read and the second must
equal it. A cell "-" has no row. A table not found, a governorate row of another width, a governorate given twice, or
years other than 2025, 2024 and 2023 stop the run. Nothing is filled. Table 13 (renewable stations, TWh to one
decimal) and the water, waste water and oil and gas tables are not taken.

    python warehouse/connectors/ncsi_oman_electricity.py [--offline] [--out-dir DIR]

Ceiling: one request a run, saved in warehouse/raw/ncsi_oman_energy/ and reused unless --fresh; --offline asks nothing.
api.ncsi.gov.om and www.ncsi.gov.om answer HTTP 404 for a robots file (session 2504). License: public. NCSI's site: "The
contents of this website are licensed under the Open Government Licence" of the Sultanate of Oman, whose text grants use,
reuse and redistribution for commercial and non-commercial purposes with the source named, and states its compatibility
with CC BY 4.0.
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

NAME = "ncsi_oman_electricity_annual"
CONNECTOR = "ncsi_oman_energy"
SOURCE = "ncsi:energy_statistics"
HOST = "api.ncsi.gov.om"
URL = "https://api.ncsi.gov.om/uploads/pdfs/energy_statistics_bulletin_2026_1783504139.pdf"
UA = {"User-Agent": "Mozilla/5.0 (compatible; ERW-connector/0.1; +https://github.com/SamuelEnrique/erw)"}
CITATION = ("National Centre for Statistics and Information (NCSI), Sultanate of Oman, Energy Statistics 2026 (Fifth Edition, "
            "data 2025), tables 11 and 12 (source: Public Services Regulatory Authority)")
YEARS = ["2025", "2024", "2023"]
GOVERNORATES = {"Muscat": "muscat", "Dhofar": "dhofar", "Musandam": "musandam", "Al Buraimai": "al_buraimi",
                "Ad Dakhliyah": "ad_dakhiliyah", "Al Batinah North": "al_batinah_north", "Al Batinah South": "al_batinah_south",
                "Ash Sharqiyah South": "ash_sharqiyah_south", "Ash Sharqiyah North": "ash_sharqiyah_north",
                "Al Dhahirah": "al_dhahirah", "Al Wusta": "al_wusta", "Others": "others", "Total": "total"}
SOURCES = {"Diesel": "diesel", "Gas": "gas", "Solar energy": "solar", "Wind energy": "wind", "Other": "other", "Total": "total"}
T11 = "Production and distribution of electrical energy by governorate from the year 2023 to 2025"
T12 = "Total electrical energy production and its sources from the year 2023 to 2025 (TWH)"
NUM = r"-|\d{1,3}(,\d{3})*\.\d"
X_COLS = ["x_label", "x_table"]


def table11(text):
    """{governorate: [9 cells]} from the lines after table 11's title (the governorate's English name, nine figures)."""
    if T11 not in text:
        raise RuntimeError("table 11 not found")
    out = {}
    names = sorted(GOVERNORATES, key=len, reverse=True)
    for ln in text[text.index(T11):].splitlines():
        if ln.startswith("Source:") and out:
            break
        name = next((n for n in names if re.search(r"(?<![A-Za-z])" + re.escape(n) + r"(?![A-Za-z])", ln)), None)
        if name is None:
            continue
        cells = [t for t in ln.split() if re.fullmatch(NUM, t)]
        if not cells:
            continue
        if len(cells) != 9:
            raise RuntimeError(f"table 11, {name}: {len(cells)} figures, not 9: {ln!r}")
        if name in out:
            raise RuntimeError(f"table 11: {name} given twice")
        out[name] = cells
    if "Total" not in out:
        raise RuntimeError("table 11: no total row")
    return out


def table12(text):
    if T12 not in text:
        raise RuntimeError("table 12 not found")
    part = text[text.index(T12):]
    lines = part.splitlines()
    head = next((ln.split() for ln in lines if ln.startswith("Item ")), None)
    if head is None or head[1:4] != YEARS:
        raise RuntimeError(f"table 12: a header other than Item {' '.join(YEARS)}: {head}")
    out = {}
    for ln in lines:
        if ln.startswith("Source:"):
            break
        m = re.match(r"^(" + "|".join(re.escape(s) for s in sorted(SOURCES, key=len, reverse=True)) + r") (\d[\d,]*\.\d|-) (\d[\d,]*\.\d|-) (\d[\d,]*\.\d|-)(?: |$)", ln)
        if m:
            if m.group(1) in out:
                raise RuntimeError(f"table 12: {m.group(1)} given twice")
            out[m.group(1)] = [m.group(2), m.group(3), m.group(4)]
    if "Total" not in out:
        raise RuntimeError("table 12: no total row")
    return out


def num(cell):
    return None if cell == "-" else float(cell.replace(",", ""))


def parse_text(pages, base, counts):
    """pages: the bulletin's pages' text in order."""
    found = [i for i, t in enumerate(pages) if T11 in t and any(f" {n} " in t for n in ("Muscat",))]
    with_rows = [i for i in found if "Total " in pages[i]]
    if not with_rows:
        raise RuntimeError("table 11 with its rows not found")
    t11 = table11(pages[with_rows[0]])
    for i in with_rows[1:]:
        if table11(pages[i]) != t11:
            raise RuntimeError(f"table 11 on page {i + 1} differs from page {with_rows[0] + 1}")
    counts["table 11 printed"] = len(with_rows)
    t12 = table12(next(t for t in pages if T12 in t))
    rows, seen = [], set()

    def add(item, var, year, value, unit, label, table):
        key = (item, var, year)
        if key in seen:
            raise RuntimeError(f"{key} given twice")
        seen.add(key)
        rows.append(dict(entity=f"ncsi:om:{item}", variable=var, ts_utc=f"{year}-01-01T00:00:00Z", value=round(value, 3), unit=unit,
                         freq="P1Y", geo="OM", market="", node=label, **base, x_label=label, x_table=table))

    for name, cells in t11.items():
        for k, year in enumerate(YEARS):
            conn, dist, prod = (num(c) for c in cells[3 * k:3 * k + 3])
            if conn is not None:
                add(GOVERNORATES[name], "connections", year, conn * 1000, "count", f"{name}, Connections (000)", "11")
            if dist is not None:
                add(GOVERNORATES[name], "distribution", year, dist * 1000, "MWh", f"{name}, Distribution (GWh)", "11")
            if prod is not None:
                add(GOVERNORATES[name], "production", year, prod * 1000, "MWh", f"{name}, Production (GWh)", "11")
    for name, cells in t12.items():
        for year, c in zip(YEARS, cells):
            v = num(c)
            if v is not None:
                add(SOURCES[name], "production_by_source", year, v * 1e6, "MWh", f"{name} (TWh)", "12")
    t = pd.DataFrame(rows)
    for year in YEARS:
        a = t[(t.entity == "ncsi:om:total") & (t.variable == "production") & (t.ts_utc.str[:4] == year)].value.sum()
        b = t[(t.entity == "ncsi:om:total") & (t.variable == "production_by_source") & (t.ts_utc.str[:4] == year)].value.sum()
        if abs(a - b) > 0.1e6:
            raise RuntimeError(f"{year}: table 11's production total {a / 1e6:.2f} TWh is not table 12's {b / 1e6:.1f} TWh")
        g = t[(t.entity != "ncsi:om:total") & (t.variable == "production") & (t.ts_utc.str[:4] == year)].value.sum()
        counts[f"{year} governorates' production less the total, GWh"] = round((g - a) / 1000, 1)
    return t


def parse(content, base, counts):
    with pdfplumber.open(io.BytesIO(content)) as pdf:
        pages = [pg.extract_text() or "" for pg in pdf.pages]
    return parse_text(pages, base, counts)


def main(argv=None):
    ap = argparse.ArgumentParser(description="NCSI: Oman's electricity by governorate and by source, 2023 to 2025")
    ap.add_argument("--offline", action="store_true", help="the saved bulletin only, no request")
    ap.add_argument("--fresh", action="store_true", help="ask for the bulletin again")
    ap.add_argument("--out-dir", help="a trial: the table under this folder, not warehouse/output")
    args = ap.parse_args(argv)
    if ip.paused(CONNECTOR) or ip.paused_host(HOST) or ip.paused_host("www.ncsi.gov.om"):
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
        counts = {}
        t = parse(content, base, counts)
        cols = ip.SERIES_COLS + X_COLS
        t = t[cols].sort_values(["variable", "entity", "ts_utc"]).reset_index(drop=True)
        p = t[(t.entity == "ncsi:om:total") & (t.variable == "production")].set_index("ts_utc").value / 1e6
        gaps = "; ".join(f"{k[:4]} {v}" for k, v in counts.items() if "less the total" in k)
        head = [
            "Energy Research Warehouse (ERW): National Centre for Statistics and Information (NCSI), Oman, Energy Statistics 2026, tables 11 and 12, "
            f"Oman's electricity by governorate and by source, {t.ts_utc.min()[:4]} to {t.ts_utc.max()[:4]} (session 2504)",
            "Shape: series (docs/datastandard.md v0). entity ncsi:om:<item> (a governorate, others, total; or a source: diesel, gas, solar, wind, other, total); "
            "variable production, distribution (MWh, from GWh), connections (count, from thousands), production_by_source (MWh, from TWh to one decimal); "
            "ts_utc the year's 1 January; freq P1Y; geo OM; node NCSI's row and column; x_table the bulletin's table.",
            f"{len(t)} rows; production TWh: " + ", ".join(f"{k[:4]} {v:.2f}" for k, v in p.items())
            + f". Each year's production total equals table 12's within 0.1 TWh (checked). The governorates' production less the total, GWh: {gaps}. "
            "Not taken: cells - (no row), table 13, the water and oil and gas tables. Nothing is filled.",
            f"Retrieved: {run_id} (UTC) by warehouse/connectors/ncsi_oman_electricity.py; the bulletin retrieved {base['retrieved_at']}; last modified {base['vintage']}",
            f"Run log: warehouse/output/logs/{CONNECTOR}_{run_id}.log",
            f"Raw files: warehouse/raw/{CONNECTOR}/ (not in git)",
            f"Source: {SOURCE} {CITATION}",
            f"  access: {URL}",
            "License: public. NCSI's site: the contents of this website are licensed under the Open Government Licence of the Sultanate of Oman "
            f"(use and redistribution, commercial included, with the source named; compatible with CC BY 4.0). Cite: {CITATION}.",
        ]
        ip.write_snapshot(t, NAME, head, log, cols)
        results.append(dict(table=NAME, market="all", status="ok", detail=f"{len(t)} rows"))
        print(f"{NAME}: {len(t)} rows, {t.entity.nunique()} entities; {counts}")
    except Exception:
        tb = ip.redact(traceback.format_exc())
        log(f"{NAME} FAILED, no output file written:\n{tb}")
        print(f"{NAME} FAILED, no output file written: {tb.strip().splitlines()[-1]}", file=sys.stderr)
        results.append(dict(table=NAME, market="all", status="failed", detail=tb.strip().splitlines()[-1][:300]))
    if not args.out_dir:
        if results and results[0]["status"] == "ok":
            ip.update_sources([dict(source=SOURCE, publisher="National Centre for Statistics and Information, Oman (NCSI)",
                                    report="Energy Statistics 2026 (Fifth Edition, data 2025), tables 11 and 12 (electricity)", report_url=URL,
                                    document_list="https://www.ncsi.gov.om/", license="public", tables=[NAME])])
        ip.write_status(CONNECTOR, run_id, results)
    log.close()
    return 0 if all(r["status"] == "ok" for r in results) else 1


if __name__ == "__main__":
    sys.exit(main())

#!/usr/bin/env python3
"""Egypt's installed capacity, peak load and generation by type, a fiscal year (July to June), as the Egyptian Electricity
Holding Company (EEHC) states them in the "Electricity in <year>" table of its annual reports (session 2435, chain 117).

Energy Research Warehouse (ERW) connector. One series table, warehouse/output/eehc_egypt_electricity_annual.csv, from four
annual reports (PDF, no key), each giving its fiscal year and the one before:

    http://www.moee.gov.eg/english_new/EEHC_Rep/2015-2016en.pdf          2014/2015 and 2015/2016
    http://www.moee.gov.eg/english_new/EEHC_Rep/2017-2018en.pdf          2016/2017 and 2017/2018
    http://www.moee.gov.eg/english_new/EEHC_Rep/REP2021-2022en.pdf       2019/2020 and 2020/2021 (the file holds the
                                                                         2020/2021 report, whatever its name)
    https://www.eehc.gov.eg/CMSEehc/Files/AnnualReport2024En.pdf         2022/2023 and 2023/2024

    entity      eehc:eg:<kind>: total, hydro, thermal (EEHC's affiliated companies and its own plants), fast_track (the
                2015/2016 fast track plan), renewable (wind and solar), private_boot (the BOOT plants), ipp_purchased,
                isolated (isolated, unconnected and reserve plants), industrial_surplus; eehc:eg for the peak load
    variable    capacity (MW, installed); generation (MWh, the report's GWh times 1,000); peak_load (MW)
    ts_utc      the fiscal year's first day (1 July); freq P1Y; geo EG
    node        the line as the report labels it; x_report the report's file; x_fiscal_year as EEHC writes it

The table of each report is read from the line "Description <year> <year>" to the line of total fuel consumption; a line
is taken by its label (LINES), then its unit, then its two figures (a dash has no row). The 2015/2016 report prints the
peak load's unit as GWh; its figures (28,015 and 29,200) are megawatts, as every other report gives them, and are written
as MW. A report without its table, a table without one of the labels it is expected to hold (REPORTS), a figure that is
not a number, or a fiscal year and line given twice with different figures stops the run. Fiscal years 2018/2019 and
2021/2022 are in no report read: the 2018/2019 and 2021/2022 reports were not found, and the 2022/2023 and 2024/2025
reports on eehc.gov.eg are scanned images without text (session 2435).

    python warehouse/connectors/eehc_egypt_electricity.py [--offline] [--out-dir DIR]

Ceiling: four requests a run, one a report, saved in warehouse/raw/eehc_electricity/ and reused offline. www.eehc.gov.eg
has no robots file (HTTP 404); www.moee.gov.eg's closes two pages only (session 2435). License: not settled. EEHC's site
carries "All Rights Reserved ©2022" and grants no reuse; internal until a ruling or a reuse statement is read.
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

NAME = "eehc_egypt_electricity_annual"
CONNECTOR = "eehc_electricity"
SOURCE = "eehc:annual_report"
HOSTS = ("www.eehc.gov.eg", "www.moee.gov.eg")
PAGE = "https://www.eehc.gov.eg/CMSEehc/en/company-info/annual-report-2023-2024/"
UA = {"User-Agent": "Mozilla/5.0 (compatible; ERW-connector/0.1; +https://github.com/SamuelEnrique/erw)"}
# report: (its url, the labels its table must hold)
REPORTS = {
    "2015-2016en.pdf": ("http://www.moee.gov.eg/english_new/EEHC_Rep/2015-2016en.pdf",
                        {"capacity:total", "capacity:hydro", "capacity:thermal", "capacity:fast_track", "capacity:renewable", "capacity:private_boot",
                         "peak_load:", "generation:total", "generation:hydro", "generation:thermal", "generation:renewable", "generation:ipp_purchased",
                         "generation:private_boot", "generation:isolated"}),
    "2017-2018en.pdf": ("http://www.moee.gov.eg/english_new/EEHC_Rep/2017-2018en.pdf",
                        {"capacity:total", "capacity:hydro", "capacity:thermal", "capacity:renewable", "capacity:private_boot", "peak_load:",
                         "generation:total", "generation:hydro", "generation:thermal", "generation:renewable", "generation:ipp_purchased",
                         "generation:private_boot", "generation:isolated"}),
    "REP2021-2022en.pdf": ("http://www.moee.gov.eg/english_new/EEHC_Rep/REP2021-2022en.pdf",
                           {"capacity:total", "capacity:hydro", "capacity:thermal", "capacity:renewable", "capacity:private_boot", "peak_load:",
                            "generation:total", "generation:hydro", "generation:thermal", "generation:renewable", "generation:private_boot",
                            "generation:isolated"}),
    "AnnualReport2024En.pdf": ("https://www.eehc.gov.eg/CMSEehc/Files/AnnualReport2024En.pdf",
                               {"capacity:total", "capacity:hydro", "capacity:thermal", "capacity:renewable", "capacity:private_boot", "peak_load:",
                                "generation:total", "generation:hydro", "generation:thermal", "generation:renewable", "generation:private_boot",
                                "generation:isolated", "generation:industrial_surplus"}),
}
NUM = r"(-|--|[\d][\d’',]*(?:\.\d+)?)"
# (label pattern, kind); the unit after the label says capacity (MW) or generation (GWh)
LINES = [
    (r"Total Installed Capacity", "total"),
    (r"Total (?:power|Power|Energy) [Gg]enerated", "total"),
    (r"Peak [Ll]oad", "peak"),
    (r"(?<![A-Za-z])Hydro", "hydro"),
    (r"Fast Track Plan", "fast_track"),
    (r"(?<![A-Za-z])Thermal(?= \(| Affiliated)", "thermal"),
    (r"New (?:and|&) Renewable Energy", "renewable"),
    (r"(?i:private sector)", "private_boot"),
    (r"Energy Purchased from \(IPPs\)", "ipp_purchased"),
    (r"(?:Isolated|Unconnected) Plants", "isolated"),
    (r"Industrial Companies. Surplus", "industrial_surplus"),
]
X_COLS = ["x_report", "x_fiscal_year"]


def number(v):
    v = v.strip()
    if v in ("-", "--"):
        return None
    return float(re.sub(r"[’',]", "", v))


def table_lines(text):
    lines = text.splitlines()
    start = next((i for i, l in enumerate(lines) if re.search(r"Description\s+20\d\d\s*/\s*20\d\d\s+20\d\d\s*/\s*20\d\d", l)), None)
    if start is None:
        return None, []
    years = re.findall(r"(20\d\d)\s*/\s*(20\d\d)", lines[start])[:2]
    out = []
    for l in lines[start + 1:]:
        if re.search(r"Total Fuel Consumption", l):
            break
        out.append(l)
    # a label alone on its line, its unit and figures on the next (the 2017/2018 report's total capacity)
    joined = []
    for l in out:
        if joined and re.match(rf"^\s*(MW|GWh)\s+{NUM}", l):
            joined[-1] = joined[-1] + " " + l.strip()
        else:
            joined.append(l)
    return years, joined


def parse(pages, report, base):
    years, lines = None, []
    for text in pages:
        years, lines = table_lines(text)
        if years:
            break
    if not years or len(years) != 2:
        raise RuntimeError(f"{report}: no table 'Description <year> <year>'")
    fys = [f"{a}/{b}" for a, b in years]
    rows, seen = [], set()
    for l in lines:
        for pat, kind in LINES:
            m = re.search(pat + r"(?:[^0-9]|\(\d+\))*?\b(MW|GWh)\b\s+" + NUM + r"\s+" + NUM + r"(?=\s|$)", l)   # a footnote mark (2) may stand before the unit
            if not m:
                continue
            unit = m.group(1)
            if kind == "peak":
                variable, entity = "peak_load", "eehc:eg"
                unit = "MW"          # the 2015/2016 report prints GWh beside megawatts
            else:
                variable, entity = ("capacity" if unit == "MW" else "generation"), f"eehc:eg:{kind}"
            key = f"{variable}:{'' if kind == 'peak' else kind}"
            if key in seen:
                break
            seen.add(key)
            label = re.sub(r"^[^A-Za-z]*", "", l[m.start():m.start(1)]).strip(" :")
            for fy, v in zip(fys, (m.group(2), m.group(3))):
                try:
                    x = number(v)
                except ValueError:
                    raise RuntimeError(f"{report} {fy} {label}: not a number: {v!r}")
                if x is None:
                    continue
                f = 1000.0 if unit == "GWh" else 1.0
                rows.append(dict(entity=entity, variable=variable, ts_utc=f"{fy[:4]}-07-01T00:00:00Z", value=round(x * f, 3),
                                 unit="MWh" if unit == "GWh" else "MW", freq="P1Y", geo="EG", market="", node=label[:120], **base,
                                 x_report=report, x_fiscal_year=fy))
            break
    want = REPORTS[report][1]
    missing = sorted(want - seen)
    if missing:
        raise RuntimeError(f"{report}: lines not found in its table: {missing}")
    return rows


def main(argv=None):
    ap = argparse.ArgumentParser(description="EEHC's annual reports: Egypt's capacity, peak load and generation by fiscal year")
    ap.add_argument("--offline", action="store_true", help="the saved reports only, no request")
    ap.add_argument("--out-dir", help="a trial: the table under this folder, not warehouse/output")
    args = ap.parse_args(argv)
    if ip.paused(CONNECTOR) or any(ip.paused_host(h) for h in HOSTS):
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
        rows, got = [], []
        for report, (url, _) in REPORTS.items():
            content, rec = ip.fetch_raw(CONNECTOR, url, log, offline=args.offline, headers=UA, timeout=180, pause=2)
            with pdfplumber.open(io.BytesIO(content)) as pdf:
                pages = [(pg.extract_text() or "") for pg in pdf.pages[:25]]
            base = dict(source=SOURCE, source_url=url, retrieved_at=rec.get("retrieved_at") or "", vintage=ip.vintage_of(rec))
            rows += parse(pages, report, base)
            got.append(f"{report} {base['retrieved_at']}")
        t = pd.DataFrame(rows)
        if t.empty:
            raise RuntimeError("no value in the reports")
        d = t[t.duplicated(["entity", "variable", "ts_utc"], keep=False)]
        if len(d):
            if d.groupby(["entity", "variable", "ts_utc"]).value.nunique().max() > 1:
                raise RuntimeError(f"a fiscal year and line given twice with different figures: {d.head(4)[['entity', 'variable', 'ts_utc']].values.tolist()}")
            t = t.drop_duplicates(["entity", "variable", "ts_utc"], keep="last")
        cols = ip.SERIES_COLS + X_COLS
        t = t[cols].sort_values(["variable", "entity", "ts_utc"]).reset_index(drop=True)
        g = t[(t.variable == "generation") & (t.entity == "eehc:eg:total")].set_index("x_fiscal_year").value / 1e6
        head = [
            "Energy Research Warehouse (ERW): Egyptian Electricity Holding Company (EEHC), annual reports' table 'Electricity in <year>', "
            f"fiscal years {t.x_fiscal_year.min()} to {t.x_fiscal_year.max()} (session 2435)",
            "Shape: series (docs/datastandard.md v0). entity eehc:eg:<kind> (total, hydro, thermal, fast_track, renewable, private_boot, ipp_purchased, isolated, "
            "industrial_surplus) or eehc:eg (peak load); variable capacity (MW), generation (MWh, GWh times 1,000) or peak_load (MW); ts_utc the fiscal year's "
            "first day (1 July); freq P1Y; geo EG; node the report's label; x_report the report; x_fiscal_year as EEHC writes it. Totals and parts are EEHC's.",
            f"{len(t)} rows; total generation TWh by fiscal year: " + ", ".join(f"{k} {v:.1f}" for k, v in g.items())
            + ". Fiscal years 2018/2019 and 2021/2022 are in no report read. The 2015/2016 report's peak load, printed in GWh, is in MW. A dash has no row; nothing is filled.",
            f"Retrieved: {run_id} (UTC) by warehouse/connectors/eehc_egypt_electricity.py; the reports retrieved: " + "; ".join(got),
            f"Run log: warehouse/output/logs/{CONNECTOR}_{run_id}.log",
            f"Raw files: warehouse/raw/{CONNECTOR}/ (not in git)",
            f"Source: {SOURCE} Egyptian Electricity Holding Company, annual reports, {PAGE}",
            "  access: " + ", ".join(u for u, _ in REPORTS.values()),
            "License: internal (EEHC's site: \"All Rights Reserved ©2022\"; no reuse statement read).",
        ]
        ip.write_snapshot(t, NAME, head, log, cols)
        results.append(dict(table=NAME, market="all", status="ok", detail=f"{len(t)} rows"))
        print(f"{NAME}: {len(t)} rows, fiscal years {sorted(t.x_fiscal_year.unique())}")
    except Exception:
        tb = ip.redact(traceback.format_exc())
        log(f"{NAME} FAILED, no output file written:\n{tb}")
        print(f"{NAME} FAILED, no output file written: {tb.strip().splitlines()[-1]}", file=sys.stderr)
        results.append(dict(table=NAME, market="all", status="failed", detail=tb.strip().splitlines()[-1][:300]))
    if not args.out_dir:
        if results and results[0]["status"] == "ok":
            ip.update_sources([dict(source=SOURCE, publisher="Egyptian Electricity Holding Company (EEHC)",
                                    report="Annual reports, the table 'Electricity in <year>'", report_url=PAGE,
                                    document_list="; ".join(u for u, _ in REPORTS.values()), license="internal", tables=[NAME])])
        ip.write_status(CONNECTOR, run_id, results)
    log.close()
    return 0 if all(r["status"] == "ok" for r in results) else 1


if __name__ == "__main__":
    sys.exit(main())

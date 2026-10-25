#!/usr/bin/env python3
"""Kenya's generation capacity by technology and electricity consumption by customer category, a fiscal year (July to
June), from the Energy and Petroleum Regulatory Authority's Energy and Petroleum Statistics Reports (session 2325,
chain 108: Kenya's generation and demand).

Energy Research Warehouse (ERW) connector. One series table, warehouse/output/epra_kenya_electricity_annual.csv, from
two tables of each of EPRA's three fiscal-year reports (PDF, read with pdfplumber's table extraction), one request a
report:

    Table 2.1  Installed, Effective and Captive Power Capacity as at 30th June <year>
    Table 2.2  A summary of energy consumption by each customer category during the (financial) year <year-1>/<year>

    entity    epra:KE; geo KE; node Kenya
    variable  capacity_<part>_<technology> in MW, part interconnected_installed, interconnected_effective, captive,
              offgrid or total_installed; technology geothermal, hydro, thermal, solar, wind, bioenergy, imports,
              waste_heat_recovery or total (EPRA's rows; WHR and WHRC are waste heat recovery);
              consumption_<category> in MWh (EPRA's GWh times 1,000), category industrial, domestic, small_commercial,
              street_lighting, e_mobility or total
    ts_utc    the fiscal year's first day, 1 July (capacity: as at the year's end, 30 June); freq P1Y

A cell EPRA leaves blank or marks "-" has no row; nothing is filled. The percentage columns are not taken. Each part's
technologies must add to its total row, and each technology's interconnected installed, captive and offgrid capacity to
its total installed capacity, within 0.15 MW (EPRA rounds to one or two decimals); consumption's categories must add to
its total within 0.15 GWh. A report without both tables, a table title without its year, a row or category not in the
map, a value that is not a number or a check that fails stops the run.

    python warehouse/connectors/epra_kenya_electricity.py [--offline] [--out-dir DIR]

Ceiling: three requests, reused from warehouse/raw/epra_kenya_electricity/ with --offline. www.epra.go.ke's robots file
disallows Drupal's admin, search and user paths and names no AI agent (session 2325). License: each report's notice,
"Unless otherwise stated, material in this publication may be freely used, shared, copied, reproduced, printed and/or
stored, provided that appropriate acknowledgment is given of EPRA as the source and copyright holder." Cite: Energy and
Petroleum Regulatory Authority (EPRA), Energy and Petroleum Statistics Report.
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

NAME = "epra_kenya_electricity_annual"
CONNECTOR = "epra_kenya_electricity"
SOURCE = "epra:energy_petroleum_statistics_report"
PAGE = "https://www.epra.go.ke/index.php/statistics-0"
REPORTS = [
    "https://www.epra.go.ke/sites/default/files/2024-10/EPRA%20Energy%20and%20Petroleum%20Statistics%20Report%20FY%202023-2024_2.pdf",
    "https://www.epra.go.ke/sites/default/files/2025-09/Statistics-Report-June-2025-Web.pdf",
    "https://www.epra.go.ke/sites/default/files/2026-09/Energy%20%26%20Petroleum%20Statistics%20Report%202026.pdf",
]
TECH = {"geothermal": "geothermal", "hydro": "hydro", "thermal": "thermal", "solar": "solar", "wind": "wind",
        "bioenergy": "bioenergy", "imports": "imports", "whr": "waste_heat_recovery", "whrc": "waste_heat_recovery",
        "total": "total"}
PARTS = ["interconnected_installed", "interconnected_effective", "captive", "offgrid", "total_installed"]
CATEGORY = {"industrial": "industrial", "domestic": "domestic", "small commercial (smes)": "small_commercial",
            "street lighting": "street_lighting", "e-mobility": "e_mobility", "electric mobility": "e_mobility",
            "total": "total"}
TOL = 0.15
UA = {"User-Agent": "Mozilla/5.0 (compatible; ERW-connector/0.1; +https://github.com/SamuelEnrique/erw)"}
COLS = ["entity", "variable", "ts_utc", "value", "unit", "freq", "geo", "market", "node", "source", "source_url",
        "retrieved_at", "vintage"]


def num(cell, what):
    s = (cell or "").strip()
    if s in ("", "-"):
        return None
    if not re.fullmatch(r"\d{1,3}(,\d{3})*(\.\d+)?|\d+(\.\d+)?", s):
        raise RuntimeError(f"{what}: not a number: {s!r}")
    return float(s.replace(",", ""))


def capacity(table, year):
    """Table 2.1's rows: {part: {technology: MW}}, each checked."""
    head = [(c or "").replace("\n", " ") for c in table[0]]
    if not head[0].startswith("Technology") or "Interconnected" not in head[1] or "Captive" not in head[3] \
            or "Off" not in head[4] or "Total" not in head[5] or [(c or "") for c in table[1][1:3]] != ["Installed", "Effective"]:
        raise RuntimeError(f"{year}: table 2.1's header is not EPRA's: {head} / {table[1]}")
    got = {p: {} for p in PARTS}
    for row in table[2:]:
        name = (row[0] or "").strip().lower()
        if name not in TECH:
            raise RuntimeError(f"{year}: a technology not in the map: {row[0]!r}")
        for p, cell in zip(PARTS, row[1:6]):
            v = num(cell, f"{year} {row[0]} {p}")
            if v is not None:
                got[p][TECH[name]] = v
    for p, d in got.items():
        parts = sum(v for k, v in d.items() if k != "total")
        if "total" not in d or abs(parts - d["total"]) > TOL:
            raise RuntimeError(f"{year}: {p}: the technologies add to {parts:.2f}, the total row says {d.get('total')}")
    for t, total in got["total_installed"].items():
        parts = sum(got[p].get(t, 0.0) for p in ("interconnected_installed", "captive", "offgrid"))
        if abs(parts - total) > TOL:
            raise RuntimeError(f"{year}: {t}: interconnected, captive and offgrid add to {parts:.2f}, the total installed is {total}")
    return got


def consumption(table, year):
    head = [(c or "").replace("\n", " ") for c in table[0]]
    if head[:2] != ["Customer category", "Energy consumption (GWh)"]:
        raise RuntimeError(f"{year}: table 2.2's header is not EPRA's: {head}")
    got = {}
    for row in table[1:]:
        name = (row[0] or "").strip().lower()
        if name not in CATEGORY:
            raise RuntimeError(f"{year}: a customer category not in the map: {row[0]!r}")
        v = num(row[1], f"{year} {row[0]}")
        if v is not None:
            got[CATEGORY[name]] = v
    parts = sum(v for k, v in got.items() if k != "total")
    if "total" not in got or abs(parts - got["total"]) > TOL:
        raise RuntimeError(f"{year}: the categories add to {parts:.2f} GWh, the total row says {got.get('total')}")
    return got


def report_rows(content, url, retrieved, vintage):
    cap = use = None
    with pdfplumber.open(io.BytesIO(content)) as pdf:
        for page in pdf.pages:
            text = page.extract_text() or ""
            m1 = re.search(r"Table 2\.1: Installed, [Ee]ffective and [Cc]aptive [Pp]ower [Cc]apacity as at 30th June (\d{4})", text)
            # the year may fall on a later line, among the other column's text (the 2026 report)
            m2 = re.search(r"Table 2\.2: A summary of energy consumption by each customer category during the (?:financial )?year[\s\S]{0,400}?(\d{4})/(\d{4})", text)
            for t in page.extract_tables():
                first = (t[0][0] or "") if t and t[0] else ""
                if m1 and cap is None and first.startswith("Technology"):
                    cap = (int(m1.group(1)), capacity(t, m1.group(1)))
                if m2 and use is None and first.startswith("Customer category"):
                    if int(m2.group(2)) != int(m2.group(1)) + 1:
                        raise RuntimeError(f"{url}: a fiscal year not of two years running: {m2.group(0)}")
                    use = (int(m2.group(2)), consumption(t, m2.group(0)))
    if cap is None or use is None:
        raise RuntimeError(f"{url}: tables 2.1 and 2.2 not both found (2.1 {cap is not None}, 2.2 {use is not None})")
    if cap[0] != use[0]:
        raise RuntimeError(f"{url}: table 2.1 is of June {cap[0]}, table 2.2 of the year ending in {use[0]}")
    ts = f"{cap[0] - 1}-07-01T00:00:00Z"
    base = dict(entity="epra:KE", ts_utc=ts, freq="P1Y", geo="KE", market="", node="Kenya", source=SOURCE, source_url=url,
                retrieved_at=retrieved, vintage=vintage)
    out = [dict(base, variable=f"capacity_{p}_{t}", value=v, unit="MW") for p, d in cap[1].items() for t, v in d.items()]
    out += [dict(base, variable=f"consumption_{c}", value=v * 1000.0, unit="MWh") for c, v in use[1].items()]
    return out


def finish(rows):
    t = pd.DataFrame(rows, columns=COLS)
    if t.duplicated(["entity", "variable", "ts_utc"]).any():
        raise RuntimeError("a fiscal year given by two reports")
    return t.sort_values(["entity", "variable", "ts_utc"]).reset_index(drop=True)


def main(argv=None):
    ap = argparse.ArgumentParser(description="EPRA: Kenya's generation capacity and electricity consumption, a fiscal year")
    ap.add_argument("--offline", action="store_true", help="the saved reports only, no request")
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
        if not args.offline and (ip.paused("epra") or ip.paused_host("www.epra.go.ke")):
            raise RuntimeError("EPRA is paused (warehouse/metadata/paused_sources.csv): not requested")
        rows, got = [], []
        for url in REPORTS:
            content, rec = ip.fetch_raw(CONNECTOR, url, log, offline=args.offline, fresh=not args.offline, headers=UA, timeout=300)
            rows += report_rows(content, url, rec.get("retrieved_at") or "", ip.vintage_of(rec))
            got.append(rec.get("retrieved_at") or "")
        t = finish(rows)
        years = sorted(t.ts_utc.str[:4].astype(int) + 1)
        # session 2326: EPRA's effective capacity printed above installed, and an effective column repeating the year before's
        cap = t[t.variable.str.startswith("capacity_interconnected_")].copy()
        cap["fy"] = cap.ts_utc.str[:4].astype(int) + 1
        cap["part"] = cap.variable.str.extract(r"capacity_interconnected_(installed|effective)_")[0]
        cap["tech"] = cap.variable.str.replace(r"capacity_interconnected_(installed|effective)_", "", regex=True)
        cw = cap.pivot_table(index=["fy", "tech"], columns="part", values="value")
        above = [f"{tech} {fy} ({r.effective:,.2f} against {r.installed:,.2f})" for (fy, tech), r in cw.iterrows() if r.effective > r.installed]
        eff = cap[cap.part == "effective"].pivot_table(index="tech", columns="fy", values="value")
        ins = cap[cap.part == "installed"].pivot_table(index="tech", columns="fy", values="value")
        repeat = [f"{tech} {b} ({eff.at[tech, b]:,.2f}, installed {ins.at[tech, a]:,.2f} to {ins.at[tech, b]:,.2f})"
                  for a, b in zip(eff.columns[:-1], eff.columns[1:]) for tech in eff.index
                  if abs(eff.at[tech, b] - eff.at[tech, a]) < 0.05 and abs(ins.at[tech, b] - ins.at[tech, a]) >= 0.05]
        header = [
            f"Energy Research Warehouse (ERW): EPRA (Energy and Petroleum Regulatory Authority), Kenya's generation capacity by technology and electricity consumption by customer category, fiscal years ending June {years[0]} to {years[-1]} (session 2325)",
            "Shape: series (docs/datastandard.md v0). entity epra:KE; variable capacity_<interconnected_installed, interconnected_effective, captive, offgrid, total_installed>_<technology> (MW, as at 30 June) "
            "and consumption_<industrial, domestic, small_commercial, street_lighting, e_mobility, total> (MWh, EPRA's GWh times 1,000); ts_utc the fiscal year's 1 July; freq P1Y; geo KE.",
            f"{len(t)} rows, {t.variable.nunique()} variables, from tables 2.1 and 2.2 of three reports. A cell EPRA leaves blank or marks '-' has no row; nothing is filled. Every part adds to its total within 0.15 MW, and the categories to theirs within 0.15 GWh. "
            f"As EPRA prints them: effective capacity above installed for {'; '.join(above) or 'none'}; effective capacity unchanged from the year before while installed changed for {'; '.join(repeat) or 'none'} (session 2326's note).",
            f"Retrieved: {run_id} (UTC) by warehouse/connectors/epra_kenya_electricity.py; the reports retrieved " + "; ".join(got),
            f"Run log: warehouse/output/logs/{CONNECTOR}_{run_id}.log",
            f"Raw files: warehouse/raw/{CONNECTOR}/ (not in git)",
            f"Source: {SOURCE} Energy and Petroleum Regulatory Authority (EPRA), Energy and Petroleum Statistics Reports for the fiscal years 2023/24, 2024/25 and 2025/26, tables 2.1 and 2.2, {PAGE}",
            "  access: " + " ".join(REPORTS),
            "License: public. Each report: material \"may be freely used, shared, copied, reproduced, printed and/or stored, provided that appropriate acknowledgment is given of EPRA as the source and copyright holder\". Cite: EPRA.",
        ]
        ip.write_csv(t, NAME, header, log, cols=COLS)
        if not args.out_dir:
            ip.update_sources([dict(source=SOURCE, publisher="Energy and Petroleum Regulatory Authority, Kenya (EPRA)",
                                    report="Energy and Petroleum Statistics Report (fiscal years 2023/24 to 2025/26), table 2.1 (installed, effective and captive capacity) and table 2.2 (consumption by customer category)",
                                    report_url=PAGE, document_list=" ".join(REPORTS), license="public", tables=[NAME])])
        results.append(dict(table=NAME, market="all", status="ok", detail=f"{len(t)} rows"))
        print(f"{NAME}: {len(t)} rows")
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

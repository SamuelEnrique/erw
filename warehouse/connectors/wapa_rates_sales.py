#!/usr/bin/env python3
"""The Western Area Power Administration's (WAPA) energy sold and power rate by project, each federal fiscal year from 2008 to
2025, as WAPA gives them in its workbook "Rates and Sales Data FY 2008-2025" (session 2751, chain 139: the Western Area Power
Administration, after the BPA, which the ERW holds).

Energy Research Warehouse (ERW) connector. One series table, warehouse/output/wapa_energy_sales_annual.csv, from one workbook (no
key), its sheet "Energy Sales and Rates Data", three tables one above another:

    https://www.wapa.gov/wp-content/uploads/2026/03/3-Rates-and-Sales-Data-FY-2008-2025.xlsx

    entity      wapa_proj:<project>: the row's label as a slug, its footnote mark dropped (boulder_canyon_project,
                central_arizona_project, central_valley_project, falcon_amistad_project, loveland_area_projects, olmsted,
                parker_davis_project, pick_sloan_missouri_basin_program_eastern_division, provo_river_project,
                salt_lake_city_area_integrated_projects, washoe_project), and wapa_proj:wapa_total, WAPA's total row
    variable    energy_sold (MWh, "Energy Sold (MWh)"), or power_rate (USD/MWh: WAPA's "Power Rate (cents/kWh)" times 10, an
                exact change of unit, 1 cent/kWh = 10 USD/MWh)
    ts_utc      the fiscal year's first day, 1 October of the year before (WAPA's fiscal year 2025 runs from 1 October 2024 to
                30 September 2025); freq P1Y; geo US; node the row's label as written

The third table, the transmission rate in dollars a kW a month, is not taken: the data standard has no unit for it. WAPA's
footnotes are kept in node only where they change a figure's meaning, and in the header: the Central Arizona Project's Navajo
plant ceased generating on 19 November 2019 (its later years are N/A); the Central Valley Project's energy includes custom product
power purchases; the Boulder Canyon and Parker-Davis rates exclude the Lower Colorado River Basin Development Fund surcharge; the
Boulder Canyon rates for 2018 to 2024 were restated; the Central Valley rate excludes the Restoration Fund charge; the Loveland and
Pick-Sloan rates include a drought adder from FY 2008 to FY 2024.

Each table is found by its title in column A; its year row must be each year from 2025 down to 2008. A project given twice, a
cell neither a number nor "N/A", or a negative stops the run. "N/A" has no row; nothing is filled. Check, within 0.5 MWh in every
year: the projects' energy sold adds to WAPA's total. A check missed stops the run.

    python warehouse/connectors/wapa_rates_sales.py [--offline] [--fresh] [--out-dir DIR]

Ceiling: one request a run, saved in warehouse/raw/wapa/ and reused unless --fresh; --offline asks nothing.
www.wapa.gov's robots file closes only /wp-admin/ and names no Claude agent (session 2751, read 1485); wapa.gov answers no TLS
handshake. License: WAPA is part of the Department of Energy, whose notice says "Government information at DOE websites is in the
public domain" (read 54); WAPA's web policies state no other term (session 2751): public, crediting WAPA.
"""

import argparse
import datetime as dt
import io
import os
import re
import sys
import traceback

import openpyxl
import pandas as pd

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import iso_prices as ip  # noqa: E402

NAME = "wapa_energy_sales_annual"
CONNECTOR = "wapa"
SOURCE = "wapa:rates_and_sales_data"
HOST = "www.wapa.gov"
URL = "https://www.wapa.gov/wp-content/uploads/2026/03/3-Rates-and-Sales-Data-FY-2008-2025.xlsx"
UA = {"User-Agent": "Mozilla/5.0 (compatible; ERW-connector/0.1; +https://github.com/SamuelEnrique/erw)"}
CITATION = "Western Area Power Administration, Rates and Sales Data FY 2008-2025 (workbook, March 2026)"
SHEET = "Energy Sales and Rates Data"
TABLES = [("Energy Sold (MWh)", "energy_sold", "MWh", 1.0),
          ("Power Rate (cents/kWh)", "power_rate", "USD/MWh", 10.0)]
STOP = "Transmission Rate (dollars/kW/month)"
YEARS = list(range(2025, 2007, -1))
TOTAL = "(WAPA Total)"
TOL = 0.5
X_COLS = []


def label(v):
    return " ".join(str(v).replace(chr(0xA0), " ").split()) if v is not None else ""


def project(s):
    return re.sub(r"\s+\d+/$", "", s).strip()


def slug(s):
    return re.sub(r"_+", "_", re.sub(r"[^a-z0-9]+", "_", s.lower())).strip("_")


def parse_sheet(rows):
    titles = {label(r[0]): i for i, r in enumerate(rows) if r and r[0] is not None}
    out, nodes = {}, {}
    for title, var, unit, k in TABLES:
        if title not in titles:
            raise RuntimeError(f"no table titled {title!r}")
        i = titles[title]
        years = [c for c in rows[i][1:] if c is not None]
        if years != YEARS:
            raise RuntimeError(f"{title}: the years are {years}, not 2025 down to 2008")
        seen = set()
        for r in rows[i + 1:]:
            name = label(r[0]) if r else ""
            if not name:
                continue
            if name in [t[0] for t in TABLES] + [STOP] or re.match(r"^\d+/ ", name):
                break
            p = project(name)
            ent = "wapa_total" if p == TOTAL else slug(p)
            if ent in seen:
                raise RuntimeError(f"{title}: {p} given twice")
            seen.add(ent)
            nodes[ent] = "WAPA Total" if p == TOTAL else p
            for j, y in enumerate(YEARS):
                v = r[1 + j] if 1 + j < len(r) else None
                if v is None or (isinstance(v, str) and v.strip() == "N/A"):
                    continue
                if not isinstance(v, (int, float)) or isinstance(v, bool) or v < 0:
                    raise RuntimeError(f"{title} {p} {y}: not a quantity: {v!r}")
                out[(y, ent, var)] = (float(v) * k, unit)
    if not any(k[1] == "wapa_total" for k in out):
        raise RuntimeError("no WAPA total row")
    for y in YEARS:
        tot = out.get((y, "wapa_total", "energy_sold"))
        parts = [v[0] for (yy, e, var), v in out.items() if yy == y and var == "energy_sold" and e != "wapa_total"]
        if tot is None or abs(sum(parts) - tot[0]) > TOL:
            raise RuntimeError(f"FY {y}: the projects sold {sum(parts):,.3f} MWh, WAPA's total {tot}")
    return out, nodes


def parse(content, base):
    wb = openpyxl.load_workbook(io.BytesIO(content), data_only=True, read_only=True)
    if SHEET not in wb.sheetnames:
        raise RuntimeError(f"the workbook has no sheet {SHEET!r}: {wb.sheetnames}")
    vals, nodes = parse_sheet([tuple(r) for r in wb[SHEET].iter_rows(values_only=True)])
    rows = [dict(entity=f"wapa_proj:{e}", variable=var, ts_utc=f"{y - 1}-10-01T00:00:00Z", value=round(x, 4), unit=u, freq="P1Y",
                 geo="US", market="", node=nodes[e], **base) for (y, e, var), (x, u) in sorted(vals.items())]
    return pd.DataFrame(rows)


def main(argv=None):
    ap = argparse.ArgumentParser(description="WAPA: energy sold and power rate by project, each fiscal year from 2008")
    ap.add_argument("--offline", action="store_true", help="the saved workbook only, no request")
    ap.add_argument("--fresh", action="store_true", help="ask for the workbook again")
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
        if t.duplicated(["entity", "variable", "ts_utc"]).any():
            raise RuntimeError("a key given twice")
        cols = ip.SERIES_COLS + X_COLS
        t = t[cols].sort_values(["entity", "variable", "ts_utc"]).reset_index(drop=True)
        tot = t[(t.entity == "wapa_proj:wapa_total") & (t.variable == "energy_sold")].set_index("ts_utc").value
        head = [
            "Energy Research Warehouse (ERW): Western Area Power Administration (WAPA), Rates and Sales Data FY 2008-2025: energy "
            "sold and power rate by project, each federal fiscal year (October to September) from FY 2008 to FY 2025 (session 2751)",
            "Shape: series (docs/datastandard.md v0). entity wapa_proj:<project> or wapa_proj:wapa_total; variable energy_sold (MWh) "
            "or power_rate (USD/MWh, WAPA's cents/kWh times 10); ts_utc the fiscal year's first day (1 October of the year before); "
            "freq P1Y; geo US; node the row's label. The transmission rate (dollars/kW/month) is not taken.",
            f"{len(t)} rows; WAPA's total energy sold, MWh: " + ", ".join(
                f"FY {int(k[:4]) + 1} {tot[k]:,.0f}" for k in tot.index if k[:4] in ("2007", "2015", "2024"))
            + ". The projects checked against WAPA's total every year; N/A has no row; nothing is filled.",
            "WAPA's notes: the Central Arizona Project's Navajo plant ceased generating on 19 November 2019; the Central Valley "
            "Project's energy includes custom product power purchases; the Boulder Canyon and Parker-Davis rates exclude the LCRBDF "
            "surcharge, and Boulder Canyon's 2018 to 2024 rates were restated; the Central Valley rate excludes the Restoration Fund "
            "charge; the Loveland and Pick-Sloan rates include a drought adder from FY 2008 to FY 2024.",
            f"Retrieved: {run_id} (UTC) by warehouse/connectors/wapa_rates_sales.py; the workbook retrieved "
            f"{base['retrieved_at']}; last modified {base['vintage']}",
            f"Run log: warehouse/output/logs/{CONNECTOR}_{run_id}.log",
            f"Raw files: warehouse/raw/{CONNECTOR}/ (not in git)",
            f"Source: {SOURCE} {CITATION}",
            f"  access: {URL} (listed in WAPA's media library, www.wapa.gov)",
            "License: public domain (DOE: \"Government information at DOE websites is in the public domain\"). Credit: Western Area "
            "Power Administration.",
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
            ip.update_sources([dict(source=SOURCE, publisher="Western Area Power Administration (WAPA)",
                                    report="Rates and Sales Data FY 2008-2025: energy sold and power rate by project",
                                    report_url=URL, document_list="https://www.wapa.gov/wp-json/wp/v2/media", license="public",
                                    tables=[NAME])])  # DOE's public-domain notice
        ip.write_status(CONNECTOR, run_id, results)
    log.close()
    return 0 if all(r["status"] == "ok" for r in results) else 1


if __name__ == "__main__":
    sys.exit(main())

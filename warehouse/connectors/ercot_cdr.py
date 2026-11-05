#!/usr/bin/env python3
"""ERCOT's Capacity, Demand and Reserves report (CDR): the seasonal load forecast, the capacity counted and the planning
reserve margin, each season and year of the report (session 851, chain 046: reserve margins for ERCOT, whatever NERC's
terms hold).

Energy Research Warehouse (ERW) connector. One series table, warehouse/output/ercot_cdr_reserve_margins.csv, from the
newest CDR workbook ERCOT links on its resource adequacy page:

    page   https://www.ercot.com/gridinfo/resource
    file   https://www.ercot.com/files/docs/<yyyy>/<mm>/<dd>/CapacityDemandandReservesReport_<Month><yyyy>.xlsx

The sheet read is "Seasonal Summary": for each season (summer, fall, winter, spring) and year the report covers, two
columns, the peak load hour and the peak net load hour (ERCOT names the hour), each with the load forecast and its
adjustments, the capacity counted by kind, and the reserve margin.

    entity    ercot_cdr:<season>:<peak_load | peak_net_load>
    variable  a row of the sheet (the map ROWS below; a row the map does not know stops the run): MW, and
              reserve_margin in pct (ERCOT's fraction times 100)
    ts_utc    the season's first day at 00:00:00Z (summer 1 June, fall 1 September, winter 1 December of its first year,
              spring 1 March); freq P3M; geo US-TX; market ercot; node ERCOT's season and hour, as printed
    vintage   the report's posting date (from its address); x_hour the hour ending ERCOT names; x_report the file

ERCOT's robots file (read by session 850) disallows /misapp and /misdownload; this report is posted under /files/docs/
and the page under /gridinfo/, which it allows. A value is written as ERCOT prints it; a cell ERCOT leaves empty has no
row. Every run replaces the table with the newest report (a snapshot).

    python warehouse/connectors/ercot_cdr.py [--offline]

Ceiling: two requests (the page and the workbook; a workbook saved in warehouse/raw/ercot_cdr/ is reused). License:
public (ERCOT, licenses.md #2; cite "ERCOT, Capacity, Demand and Reserves Report").
"""

import argparse
import datetime as dt
import io
import os
import re
import sys
import traceback

import pandas as pd

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import iso_prices as ip  # noqa: E402

NAME = "ercot_cdr_reserve_margins"
CONNECTOR = "ercot_cdr"
SOURCE = "ercot:cdr"
PAGE = "https://www.ercot.com/gridinfo/resource"
UA = {"User-Agent": "Mozilla/5.0 (compatible; ERW-connector/0.1; +https://github.com/SamuelEnrique/erw)"}
SHEET = "Seasonal Summary"
SEASON_START = {"summer": "06-01", "fall": "09-01", "winter": "12-01", "spring": "03-01"}
# the sheet's row labels, matched in order inside their section: (section, pattern, variable)
ROWS = [
    ("load", r"^Total Seasonal Load", "total_seasonal_load"),
    ("load", r"Incremental Rooftop PV", "less_rooftop_pv"),
    ("load", r"Load Resources providing Responsive Reserves", "less_load_resources_rrs"),
    ("load", r"Load Resources providing Non-Spinning", "less_load_resources_nonspin"),
    ("load", r"Load Resources providing ERCOT Contingency", "less_load_resources_ecrs"),
    ("load", r"Controllable Load Resources not included", "less_controllable_load"),
    ("load", r"Emergency Response Service", "less_emergency_response_service"),
    ("load", r"TDSP Standard Offer", "less_tdsp_load_management"),
    ("load", r"Distribution Voltage Reduction", "less_voltage_reduction"),
    ("load", r"^Firm Peak Load", "firm_peak_load"),
    ("load", r"^Energy Efficiency Program Savings", "energy_efficiency_savings"),
    ("operational", r"^Installed Seasonal-rated Thermal", "operational_thermal"),
    ("operational", r"^Hydroelectric", "operational_hydro"),
    ("operational", r"^Switchable Capacity$", "operational_switchable"),
    ("operational", r"Switchable Capacity Unavailable", "operational_less_switchable_unavailable"),
    ("operational", r"^Available Mothballed", "operational_mothballed"),
    ("operational", r"Private Use Networks", "operational_private_use_networks"),
    ("operational", r"^Coastal Wind", "operational_coastal_wind"),
    ("operational", r"^Panhandle Wind", "operational_panhandle_wind"),
    ("operational", r"^Other Wind", "operational_other_wind"),
    ("operational", r"^Far West Solar", "operational_far_west_solar"),
    ("operational", r"^West Solar", "operational_west_solar"),
    ("operational", r"^Other Solar", "operational_other_solar"),
    ("operational", r"^Energy Storage", "operational_storage"),
    ("operational", r"^RMR Capacity", "operational_rmr"),
    ("operational", r"^Capacity Pending Retirement", "operational_pending_retirement"),
    ("operational", r"^Operational Generation Capacity, Total", "operational_total"),
    ("operational", r"^Non-Synchronous Ties", "dc_ties"),
    ("planned", r"^Thermal Resources", "planned_thermal"),
    ("planned", r"^Coastal Wind", "planned_coastal_wind"),
    ("planned", r"^Panhandle Wind", "planned_panhandle_wind"),
    ("planned", r"^Other Wind", "planned_other_wind"),
    ("planned", r"^Far West Solar", "planned_far_west_solar"),
    ("planned", r"^West Solar", "planned_west_solar"),
    ("planned", r"^Other Solar", "planned_other_solar"),
    ("planned", r"^Energy Storage", "planned_storage"),
    ("planned", r"^Unconfirmed Planned Retirements", "planned_unconfirmed_retirements"),
    ("planned", r"^Planned Generation Capacity Total", "planned_total"),
    ("planned", r"^Total Capacity$", "total_capacity"),
    ("planned", r"^Reserve Margin$", "reserve_margin"),
]
HEADINGS = {r"^Load Forecast and Adjustments": "load", r"^Operational Generation Capacity$": "operational",
            r"^Planned Resource Additions": "planned"}
SKIP = [r"^Seasonal Summary$", r"^Expected Resource Capacity Available", r"^Inverter-Based Resources",
        r"^\[\(Total Resources", r"^\*"]
X_COLS = ["x_hour", "x_report"]


def label(frame, r):
    for c in (2, 1):
        v = frame.iloc[r, c]
        if isinstance(v, str) and v.strip():
            return re.sub(r"\s+", " ", v.replace("less:", "")).strip()
    return ""


def columns(frame):
    """[(column, season, first year, the hour's kind, hour)], from the sheet's heading rows 1 to 4."""
    out = []
    for c in range(3, frame.shape[1]):
        season, year, kind, hour = (str(frame.iloc[r, c]).strip() for r in (1, 2, 3, 4))
        if season.lower() not in SEASON_START:
            continue
        k = {"peak load hour:": "peak_load", "peak net load hour:": "peak_net_load"}.get(kind.lower())
        if not k:
            continue    # ERCOT's "Difference" columns
        out.append((c, season.lower(), int(str(year)[:4]), k, str(int(float(hour))) if hour not in ("", "nan") else ""))
    if not out:
        raise RuntimeError("the sheet names no season and hour in its heading rows")
    return out


def rows_of(frame):
    """{row index: variable}, each label matched in its section; a label not in the map stops the run."""
    found, section = {}, None
    for r in range(5, frame.shape[0]):
        lab = label(frame, r)
        if not lab or any(re.search(p, lab) for p in SKIP):
            continue
        head = next((s for p, s in HEADINGS.items() if re.search(p, lab)), None)
        if head:
            section = head
            continue
        var = next((v for s, p, v in ROWS if s == section and re.search(p, lab) and v not in found.values()), None)
        if not var:
            raise RuntimeError(f"row {r}: '{lab}' (section {section}) is not in the map")
        found[r] = var
    missing = [v for _, _, v in ROWS if v not in found.values()]
    if missing:
        raise RuntimeError(f"the sheet lacks {missing}")
    return found


def sheet_rows(frame, url, retrieved, vintage, report):
    out = []
    for c, season, year, kind, hour in columns(frame):
        ts = f"{year}-{SEASON_START[season]}T00:00:00Z"
        node = f"{season.title()} {year}{'/' + str(year + 1) if season == 'winter' else ''}, {kind.replace('_', ' ')} hour {hour}"
        for r, var in rows_of(frame).items():
            v = pd.to_numeric(frame.iloc[r, c], errors="coerce")
            if pd.isna(v):
                continue
            pct = var == "reserve_margin"
            out.append(dict(entity=f"ercot_cdr:{season}:{kind}", variable=var, ts_utc=ts, value=float(v) * (100.0 if pct else 1.0),
                            unit="pct" if pct else "MW", freq="P3M", geo="US-TX", market="ercot", node=node, source=SOURCE,
                            source_url=url, retrieved_at=retrieved, vintage=vintage, x_hour=hour, x_report=report))
    t = pd.DataFrame(out)
    if len(t) and t.duplicated(["entity", "variable", "ts_utc"]).any():
        raise RuntimeError("an (entity, variable, ts_utc) is given twice")
    return t


def newest(page_html):
    """The newest CDR workbook the page links, by the date in its address: (url, yyyy-mm-dd)."""
    links = set(re.findall(r'href="(https://www\.ercot\.com/files/docs/(\d{4})/(\d{2})/(\d{2})/CapacityDemandandReservesReport_[^"]+\.xlsx)"', page_html))
    if not links:
        raise RuntimeError("the page links no CDR workbook")
    url, y, m, d = max(links, key=lambda x: (x[1], x[2], x[3], "Revised" in x[0]))
    return url, f"{y}-{m}-{d}T00:00:00Z"


def main(argv=None):
    ap = argparse.ArgumentParser(description="ERCOT's Capacity, Demand and Reserves report: load, capacity and reserve margin by season")
    ap.add_argument("--offline", action="store_true", help="the saved page and workbook only, no request")
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
        if ip.paused("ercot"):
            raise RuntimeError("ERCOT is paused (warehouse/metadata/paused_sources.csv): nothing is requested")
        page, _ = ip.fetch_raw(CONNECTOR, PAGE, log, offline=args.offline, fresh=not args.offline, headers=UA)
        url, posted = newest(page.decode("utf-8", errors="replace"))
        content, rec = ip.fetch_raw(CONNECTOR, url, log, offline=args.offline, headers=UA, timeout=300)
        if content[:2] != b"PK":
            raise RuntimeError(f"{url} is not a workbook")
        report = url.rsplit("/", 1)[1]
        frame = pd.read_excel(io.BytesIO(content), SHEET, header=None)
        s = sheet_rows(frame, url, rec.get("retrieved_at") or ip.utc_iso(pd.Timestamp.now(tz="UTC")), posted, report)
        cols = ip.SERIES_COLS + X_COLS
        s = s[cols]
        seasons = sorted({(t[:4], n.split(",")[0]) for t, n in zip(s["ts_utc"], s["node"])})
        header = [
            "Energy Research Warehouse (ERW): ERCOT, Capacity, Demand and Reserves report (CDR): load forecast, capacity counted and planning reserve margin by season (session 851)",
            "Shape: series (docs/datastandard.md v0). entity ercot_cdr:<season>:<peak_load | peak_net_load>; variable a row of the report's Seasonal Summary (MW; reserve_margin in pct); "
            "ts_utc the season's first day; freq P3M; geo US-TX; market ercot; node ERCOT's season and hour; vintage the report's posting date; x_hour the hour ending ERCOT names; x_report the file.",
            f"Report: {report}, posted {posted[:10]}; {len(seasons)} seasons, {s['ts_utc'].min()[:7]} to {s['ts_utc'].max()[:7]}. Values as ERCOT prints them; reserve_margin is ERCOT's (total capacity less firm peak load) over firm peak load, times 100.",
            f"Retrieved: {run_id} (UTC) by warehouse/connectors/ercot_cdr.py",
            f"Run log: warehouse/output/logs/{CONNECTOR}_{run_id}.log",
            f"Raw files: warehouse/raw/{CONNECTOR}/ (not in git)",
            f"Source: {SOURCE} Electric Reliability Council of Texas (ERCOT), Capacity, Demand and Reserves Report, {PAGE}",
            f"  access: {url}",
            'License: public (ERCOT, licenses.md #2; cite "ERCOT, Capacity, Demand and Reserves Report").',
        ]
        ip.write_snapshot(s, NAME, header, log, cols)
        if not args.out_dir:
            ip.update_sources([dict(source=SOURCE, publisher="Electric Reliability Council of Texas (ERCOT)",
                                    report="Capacity, Demand and Reserves Report", report_url=PAGE, document_list=PAGE,
                                    license="public", tables=[NAME])])
        results.append(dict(table=NAME, market="ercot", status="ok", detail=f"{len(s):,} rows"))
        print(f"{NAME}: {len(s):,} rows, {s['variable'].nunique()} variables, {len(seasons)} seasons; {report}")
    except Exception:
        tb = ip.redact(traceback.format_exc())
        log(f"FAILED, no output file written:\n{tb}")
        print(f"{CONNECTOR} FAILED, no output file written: {tb.strip().splitlines()[-1]}", file=sys.stderr)
        results.append(dict(table=NAME, market="ercot", status="failed", detail=tb.strip().splitlines()[-1][:300]))
    if not args.out_dir:
        ip.write_status(CONNECTOR, run_id, results)
    log.close()
    return 0 if all(r["status"] == "ok" for r in results) else 1


if __name__ == "__main__":
    sys.exit(main())

#!/usr/bin/env python3
"""New Zealand's grid generation and demand a month, for the country and each island, from the Electricity Authority's
Electricity Market Information (EMI) reports (session 2254, chain 102: New Zealand's grid, a hydro-led system, beside
the ERW's U.S. grids).

Energy Research Warehouse (ERW) connector. One series table from two EMI reports' CSV downloads, each for New Zealand
and for its two islands, monthly from January 2015 to the last month ended:

    https://www.emi.ea.govt.nz/Wholesale/Download/DataReport/CSV/W_GG_C?DateFrom=20150101&DateTo=<end>&RegionType=<NZ|ISLAND>&TimeScale=MONTH&Show=Gwh&_si=v|3
    https://www.emi.ea.govt.nz/Wholesale/Download/DataReport/CSV/W_GD_C?DateFrom=20150101&DateTo=<end>&RegionType=<NZ|ISLAND>&TimeScale=MONTH&_si=v|3

    emi_nz_generation_demand_monthly   entity emi:nz, emi:ni (North Island) or emi:si (South Island); variable
               generation (W_GG_C, "Generation trends") or demand (W_GD_C, "Demand trends"); value in MWh (EMI's GWh times
               1,000); ts_utc the month's first day; freq P1M; geo NZ; node EMI's region name; x_region_id EMI's id;
               x_report the report's code

The reports' dollar columns (NZD) are not taken. Generation by fuel is not in these reports (their only dimension is the
region), and EMI's half-hourly files by unit (Generation_MD, one a month from August 1997) are more files than the
ceiling allows; the fuel split is for a later session. Each CSV must state its report, its region type, monthly time
scale and GWh, and hold the columns read; a month given twice for a region, a region not in the map, a month that is not
a calendar month, or a figure that does not read stops the run, as does a month where the islands differ from New
Zealand's figure by more than 1 percent; the months where they differ by more than rounding (from June 2026, New Zealand's
generation exceeds the islands' by up to 10 GWh) are named in the header. Nothing is filled.

    python warehouse/connectors/emi_nz.py [--offline] [--out-dir DIR] [--to YYYYMMDD]

Ceiling: four requests, each asked again unless --offline (EMI's figures are revised). www.emi.ea.govt.nz has no robots
file (HTTP 404); www.ea.govt.nz's allows every path. License: public; the Authority's copyright statement licenses its
material under CC BY 4.0 with attribution to the Electricity Authority (read in session 2254).
"""

import argparse
import csv
import datetime as dt
import io
import os
import sys
import traceback

import pandas as pd

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import iso_prices as ip  # noqa: E402

CONNECTOR = "emi_nz"
SOURCE = "emi:generation_demand_trends"
HOST = "www.emi.ea.govt.nz"
PAGE = "https://www.emi.ea.govt.nz/Wholesale/Reports"
TABLE = "emi_nz_generation_demand_monthly"
UA = {"User-Agent": "Mozilla/5.0 (compatible; ERW-connector/0.1; +https://github.com/SamuelEnrique/erw)"}
REPORTS = {"W_GG_C": ("generation", "Generation trends", "Generation (GWh)", "&Show=Gwh"),
           "W_GD_C": ("demand", "Demand trends", "Demand (GWh)", "")}
REGIONS = {"NZ": ("emi:nz", "New Zealand"), "NI": ("emi:ni", "North Island"), "SI": ("emi:si", "South Island")}
TYPES = {"NZ": "New Zealand", "ISLAND": "Island"}
X_COLS = ["x_region_id", "x_report"]


def url_of(code, rtype, to):
    return (f"https://www.emi.ea.govt.nz/Wholesale/Download/DataReport/CSV/{code}?DateFrom=20150101&DateTo={to}&RegionType={rtype}"
            f"&TimeScale=MONTH{REPORTS[code][3]}&_si=v|3")


def parse(content, code, rtype, base):
    var, title, col, _ = REPORTS[code]
    lines = content.decode("utf-8-sig").splitlines()
    if lines[0].strip() != title:
        raise RuntimeError(f"{code}: not the report read: {lines[0]!r}")
    params = dict(l.split(",", 1) for l in lines if l.count(",") == 1 and not l.startswith("Period"))
    if params.get("Region type") != TYPES[rtype] or params.get("Time scale") != "Month" or params.get("Show") != "GWh":
        raise RuntimeError(f"{code} {rtype}: parameters not as asked: {params}")
    k = next(i for i, l in enumerate(lines) if l.startswith("Period start,"))
    rows = list(csv.DictReader(io.StringIO("\n".join(lines[k:]))))
    if not rows or col not in rows[0] or "Region ID" not in rows[0]:
        raise RuntimeError(f"{code} {rtype}: columns not as read: {lines[k]!r}")
    out, seen = [], set()
    for r in rows:
        a = dt.datetime.strptime(r["Period start"], "%d/%m/%Y")
        b = dt.datetime.strptime(r["Period end"], "%d/%m/%Y")
        if a.day != 1 or b != (a.replace(day=28) + dt.timedelta(days=4)).replace(day=1):
            raise RuntimeError(f"{code} {rtype}: not a calendar month: {r['Period start']} to {r['Period end']}")
        rid = r["Region ID"]
        if rid not in REGIONS:
            raise RuntimeError(f"{code} {rtype}: a region not in the map: {rid!r}")
        key = (rid, a)
        if key in seen:
            raise RuntimeError(f"{code} {rtype}: {key} given twice")
        seen.add(key)
        try:
            v = float(r[col]) * 1000
        except ValueError:
            raise RuntimeError(f"{code} {rtype}: a figure that does not read: {r[col]!r}")
        ent, name = REGIONS[rid]
        out.append(dict(base, entity=ent, variable=var, ts_utc=a.strftime("%Y-%m-%dT00:00:00Z"), value=round(v, 3), unit="MWh", freq="P1M",
                        geo="NZ", market="", node=name, x_region_id=rid, x_report=code))
    return out


def main(argv=None):
    ap = argparse.ArgumentParser(description="EMI: New Zealand's generation and demand a month, nationally and by island")
    ap.add_argument("--offline", action="store_true", help="the saved files only, no request")
    ap.add_argument("--out-dir", help="a trial: the table under this folder, not warehouse/output")
    ap.add_argument("--to", help="the last day asked (YYYYMMDD); by default the last day of the last month ended in New Zealand")
    args = ap.parse_args(argv)
    if args.out_dir:
        raw_dir = ip.RAW_DIR
        ip.set_out_dir(args.out_dir)
        ip.RAW_DIR = raw_dir
    os.makedirs(ip.LOG_DIR, exist_ok=True)
    now = dt.datetime.now(dt.timezone.utc)
    run_id = now.strftime("%Y%m%dT%H%M%SZ")
    to = args.to or (pd.Timestamp(now).tz_convert("Pacific/Auckland").normalize().replace(day=1) - pd.Timedelta(days=1)).strftime("%Y%m%d")
    log = ip.Log(os.path.join(ip.LOG_DIR, f"{CONNECTOR}_{run_id}.log"))
    ip.RAW.open(CONNECTOR, run_id)
    results = []
    try:
        if ip.paused(CONNECTOR) or ip.paused_host(HOST):
            raise RuntimeError(f"{HOST} is paused (warehouse/metadata/paused_sources.csv): no request made")
        rows, got = [], []
        for code in REPORTS:
            for rtype in TYPES:
                url = url_of(code, rtype, to)
                content, rec = ip.fetch_raw(CONNECTOR, url, log, offline=args.offline, fresh=not args.offline, headers=UA, timeout=120, pause=2)
                base = dict(source=SOURCE, source_url=url, retrieved_at=rec.get("retrieved_at") or "", vintage=ip.vintage_of(rec))
                rows += parse(content, code, rtype, base)
                got.append(base["retrieved_at"])
        s = pd.DataFrame(rows)
        apart = {}
        for var, g in s.groupby("variable"):
            p = g.pivot_table(index="ts_utc", columns="x_region_id", values="value")
            off = p["NZ"] - p["NI"] - p["SI"]
            if (off.abs() > 0.01 * p["NZ"]).any():
                raise RuntimeError(f"{var}: the islands differ from New Zealand by more than 1 percent in {list(off[off.abs() > 0.01 * p['NZ']].index[:3])}")
            big = off[off.abs() > 1000.0]  # more than rounding (1 GWh)
            apart[var] = ", ".join(f"{t[:7]} {v / 1000:+.1f} GWh" for t, v in big.items()) or "none"
        cols = ip.SERIES_COLS + X_COLS
        s = s[cols].sort_values(["entity", "variable", "ts_utc"]).reset_index(drop=True)
        head = [
            f"Energy Research Warehouse (ERW): the Electricity Authority's EMI, New Zealand's grid generation and demand a month, nationally and by "
            f"island, {s.ts_utc.min()[:7]} to {s.ts_utc.max()[:7]} (session 2254)",
            "Shape: series (docs/datastandard.md v0). entity emi:nz, emi:ni or emi:si; variable generation (report W_GG_C) or demand (W_GD_C); "
            "unit MWh (EMI's GWh times 1,000); freq P1M; ts_utc the month's first day; geo NZ; node EMI's region; x_region_id; x_report.",
            f"New Zealand less the two islands, months beyond rounding: generation {apart.get('generation')}; demand {apart.get('demand')} "
            "(EMI's own figures, kept as given; more than 1 percent would stop the run). The reports' dollar columns (NZD) are not taken. "
            "Nothing is filled.",
            f"Retrieved: {run_id} (UTC) by warehouse/connectors/emi_nz.py; the four files retrieved from {min(got)} to {max(got)}",
            f"Run log: warehouse/output/logs/{CONNECTOR}_{run_id}.log",
            f"Raw files: warehouse/raw/{CONNECTOR}/ (not in git)",
            f"Source: {SOURCE} Electricity Authority (New Zealand), Electricity Market Information, reports Generation trends (W_GG_C) and "
            f"Demand trends (W_GD_C), {PAGE}",
            "  access: https://www.emi.ea.govt.nz/Wholesale/Download/DataReport/CSV/<report>?...&TimeScale=MONTH",
            "License: public (CC BY 4.0, the Authority's copyright statement; see license_verdicts.csv). Source: Electricity Authority, EMI.",
        ]
        ip.write_snapshot(s, TABLE, head, log, cols)
        results.append(dict(table=TABLE, market="all", status="ok", detail=f"{len(s)} rows"))
        print(f"{TABLE}: {len(s):,} rows, {s.ts_utc.min()[:7]} to {s.ts_utc.max()[:7]}")
    except Exception:
        tb = ip.redact(traceback.format_exc())
        log(f"{TABLE} FAILED, no output file written:\n{tb}")
        print(f"{TABLE} FAILED, no output file written: {tb.strip().splitlines()[-1]}", file=sys.stderr)
        results.append(dict(table=TABLE, market="all", status="failed", detail=tb.strip().splitlines()[-1][:300]))
    if not args.out_dir:
        if results and results[0]["status"] == "ok":
            ip.update_sources([dict(source=SOURCE, publisher="Electricity Authority (New Zealand)",
                                    report="EMI reports: Generation trends (W_GG_C) and Demand trends (W_GD_C), monthly", report_url=PAGE,
                                    document_list=PAGE, license="public", tables=[TABLE])])
        ip.write_status(CONNECTOR, run_id, results)
    log.close()
    return 0 if all(r["status"] == "ok" for r in results) else 1


if __name__ == "__main__":
    sys.exit(main())

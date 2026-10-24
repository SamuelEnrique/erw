#!/usr/bin/env python3
"""Hungary's, Romania's, Greece's and Bulgaria's electricity a day: public net production by type, load, residual load
and cross-border trading, from Energy-Charts (Fraunhofer ISE), its power summed over each complete UTC day (session 2259,
chain 102: four southeastern European grids, none of them in the ERW before).

Energy Research Warehouse (ERW) connector. One series table from the Energy-Charts API, one request a country for
2020 to the last day asked:

    https://api.energy-charts.info/public_power?country=<hu|ro|gr|bg>&start=2020-01-01&end=<last day>

    energy_charts_southeast_europe_daily   entity energy_charts:<country>:<production type as a slug> (as Energy-Charts
               names them: nuclear, fossil_brown_coal_lignite, fossil_hard_coal, fossil_gas, fossil_oil, hydro_run_of_river,
               hydro_water_reservoir, hydro_pumped_storage and its consumption, battery and battery_consumption, wind_onshore,
               solar, biomass, geothermal, waste, others, other_renewables, cross_border_electricity_trading, load,
               residual_load); variable public_net_energy for a production type, load, residual_load or cross_border_trading
               for the others; value in MWh, the day's sum of Energy-Charts' mean power over each of its periods (a quarter
               hour or an hour) times the period's length; ts_utc the UTC day's start; freq P1D; geo HU, RO, GR or BG;
               x_type Energy-Charts' name; x_periods the number of periods summed

Energy-Charts gives Hungary in quarter hours, Romania in hours to 2021 and quarter hours from 1 January 2022, Greece
and Bulgaria in hours (a positive cross-border trading figure is an import); a quarter
hour series of four countries would run to millions of rows, so each UTC day is summed. A day is summed for a type only
when its periods cover the whole day (86,400 seconds) and none is blank; any other day has no row for that type and is
counted (the first and last UTC days, cut by the countries' local days, among them). The renewable shares (Energy-Charts'
own percentages) are not taken. A type not in the map, a series shorter than its periods, or a period that is not 15 or
60 minutes stops the run. Nothing is filled.

    python warehouse/connectors/energy_charts_southeast.py [--offline] [--out-dir DIR] [--last-day YYYY-MM-DD]

Ceiling: four requests (one a country), 35 seconds apart: the API allows 2 requests a minute for each client. Each is
asked again unless --offline. api.energy-charts.info has no robots file (HTTP 404). License: public (CC BY 4.0,
attribution to Energy-Charts.info, the API's description; the verdict recorded in session 2257).
"""

import argparse
import datetime as dt
import json
import os
import re
import sys
import traceback

import pandas as pd

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import iso_prices as ip  # noqa: E402

CONNECTOR = "energy_charts_southeast"
SOURCE = "energy_charts:public_power_southeast"
HOST = "api.energy-charts.info"
PAGE = "https://energy-charts.info/charts/power/chart.htm?l=en"
TABLE = "energy_charts_southeast_europe_daily"
COUNTRIES = {"hu": "HU", "ro": "RO", "gr": "GR", "bg": "BG"}
UA = {"User-Agent": "Mozilla/5.0 (compatible; ERW-connector/0.1; +https://github.com/SamuelEnrique/erw)"}
TYPES = {"Nuclear", "Fossil brown coal / lignite", "Fossil hard coal", "Fossil gas", "Fossil oil", "Hydro Run-of-River", "Hydro water reservoir",
         "Hydro pumped storage", "Hydro pumped storage consumption", "Battery", "Battery Consumption", "Wind onshore", "Wind offshore", "Solar",
         "Biomass", "Geothermal", "Waste", "Others", "Other renewables"}
OTHER = {"Load": "load", "Residual load": "residual_load", "Cross border electricity trading": "cross_border_trading"}
SHARES = {"Renewable share of load", "Renewable share of generation"}
X_COLS = ["x_type", "x_periods"]


def slug(s):
    return re.sub(r"[^a-z0-9]+", "_", s.lower()).strip("_")


def url_of(country, last):
    return f"https://api.energy-charts.info/public_power?country={country}&start=2020-01-01&end={last}"


def parse(content, country, base, counts):
    d = json.loads(content)
    u = d["unix_seconds"]
    steps = [b - a for a, b in zip(u, u[1:])]
    if any(s not in (900, 3600) for s in steps):
        raise RuntimeError(f"{country}: a period not 15 or 60 minutes: {sorted(set(steps))[:5]}")
    dur = steps + [steps[-1]]
    day = [dt.datetime.fromtimestamp(x, dt.timezone.utc).strftime("%Y-%m-%d") for x in u]
    frame = pd.DataFrame({"day": day, "dur": dur})
    # a period that runs past midnight would split across two days; the API's periods start on the quarter or the hour
    whole = frame.groupby("day").dur.sum()
    out = []
    for p in d["production_types"]:
        name = p["name"]
        if name in SHARES:
            continue
        if name not in TYPES and name not in OTHER:
            raise RuntimeError(f"{country}: a type not in the map: {name!r}")
        if len(p["data"]) != len(u):
            raise RuntimeError(f"{country}: {name} has {len(p['data'])} figures for {len(u)} periods")
        f = frame.assign(v=p["data"])
        f["blank"] = f.v.isna()
        f["mwh"] = f.v.astype(float) * f.dur / 3600.0
        g = f.groupby("day").agg(mwh=("mwh", "sum"), blank=("blank", "sum"), n=("dur", "size"))
        for dd, r in g.iterrows():
            if whole[dd] != 86400 or r.blank:
                counts[f"{country} {'part day' if whole[dd] != 86400 else 'day with a blank'}"] = counts.get(
                    f"{country} {'part day' if whole[dd] != 86400 else 'day with a blank'}", 0) + 1
                continue
            out.append(dict(base, entity=f"energy_charts:{country}:{slug(name)}", variable=OTHER.get(name, "public_net_energy"),
                            ts_utc=f"{dd}T00:00:00Z", value=round(float(r.mwh), 3), unit="MWh", freq="P1D", geo=COUNTRIES[country], market="",
                            node=f"{COUNTRIES[country]}: {name}", x_type=name, x_periods=int(r.n)))
    return out


def main(argv=None):
    ap = argparse.ArgumentParser(description="Energy-Charts: Hungary, Romania, Greece and Bulgaria, production by type and load, a day")
    ap.add_argument("--offline", action="store_true", help="the saved files only, no request")
    ap.add_argument("--out-dir", help="a trial: the table under this folder, not warehouse/output")
    ap.add_argument("--last-day", help="the last day asked (YYYY-MM-DD); by default yesterday (UTC)")
    args = ap.parse_args(argv)
    if args.out_dir:
        raw_dir = ip.RAW_DIR
        ip.set_out_dir(args.out_dir)
        ip.RAW_DIR = raw_dir
    os.makedirs(ip.LOG_DIR, exist_ok=True)
    now = dt.datetime.now(dt.timezone.utc)
    run_id = now.strftime("%Y%m%dT%H%M%SZ")
    last = args.last_day or (now - dt.timedelta(days=1)).strftime("%Y-%m-%d")
    log = ip.Log(os.path.join(ip.LOG_DIR, f"{CONNECTOR}_{run_id}.log"))
    ip.RAW.open(CONNECTOR, run_id)
    results = []
    try:
        if ip.paused(CONNECTOR) or ip.paused_host(HOST):
            raise RuntimeError(f"{HOST} is paused (warehouse/metadata/paused_sources.csv): no request made")
        rows, counts, got = [], {}, []
        for country in COUNTRIES:
            url = url_of(country, last)
            content, rec = ip.fetch_raw(CONNECTOR, url, log, offline=args.offline, fresh=not args.offline, headers=UA, timeout=300, pause=35)
            base = dict(source=SOURCE, source_url=url, retrieved_at=rec.get("retrieved_at") or "", vintage=ip.vintage_of(rec))
            rows += parse(content, country, base, counts)
            got.append((country, base["retrieved_at"]))
        s = pd.DataFrame(rows)
        if s.duplicated(["entity", "variable", "ts_utc"]).any():
            raise RuntimeError("a day given twice")
        cols = ip.SERIES_COLS + X_COLS
        s = s[cols].sort_values(["entity", "variable", "ts_utc"]).reset_index(drop=True)
        head = [
            f"Energy Research Warehouse (ERW): Energy-Charts (Fraunhofer ISE), public net electricity production by type, load, residual load and "
            f"cross-border trading for Hungary, Romania, Greece and Bulgaria, a UTC day, {s.ts_utc.min()[:10]} to {s.ts_utc.max()[:10]} (session 2259)",
            "Shape: series (docs/datastandard.md v0). entity energy_charts:<country>:<type>; variable public_net_energy, load, residual_load or "
            "cross_border_trading; unit MWh (the day's sum of Energy-Charts' mean power times each period's length, quarter hours or hours); "
            "freq P1D; ts_utc the UTC day; geo HU, RO, GR or BG; x_type Energy-Charts' name; x_periods the periods summed.",
            f"Days not summed, counted (a part day or a blank): {', '.join(f'{k} {v:,}' for k, v in sorted(counts.items())) or 'none'}. The "
            "renewable shares are not taken. Nothing is filled.",
            f"Retrieved: {run_id} (UTC) by warehouse/connectors/energy_charts_southeast.py; the countries retrieved {', '.join(f'{c} {a}' for c, a in got)}",
            f"Run log: warehouse/output/logs/{CONNECTOR}_{run_id}.log",
            f"Raw files: warehouse/raw/{CONNECTOR}/ (not in git)",
            f"Source: {SOURCE} Energy-Charts.info (Fraunhofer Institute for Solar Energy Systems ISE), public net electricity production, {PAGE}",
            "  access: https://api.energy-charts.info/public_power?country=<hu|ro|gr|bg>&start=2020-01-01&end=<last day>",
            "License: public (CC BY 4.0, attribution to Energy-Charts.info, the API's description; see license_verdicts.csv). Source: Energy-Charts.info.",
        ]
        ip.write_snapshot(s, TABLE, head, log, cols)
        results.append(dict(table=TABLE, market="all", status="ok", detail=f"{len(s)} rows"))
        print(f"{TABLE}: {len(s):,} rows, {s.entity.nunique()} series, {s.ts_utc.min()[:10]} to {s.ts_utc.max()[:10]}; not summed {counts}")
    except Exception:
        tb = ip.redact(traceback.format_exc())
        log(f"{TABLE} FAILED, no output file written:\n{tb}")
        print(f"{TABLE} FAILED, no output file written: {tb.strip().splitlines()[-1]}", file=sys.stderr)
        results.append(dict(table=TABLE, market="all", status="failed", detail=tb.strip().splitlines()[-1][:300]))
    if not args.out_dir:
        if results and results[0]["status"] == "ok":
            ip.update_sources([dict(source=SOURCE, publisher="Energy-Charts.info (Fraunhofer ISE)",
                                    report="Public net electricity production, Hungary, Romania, Greece and Bulgaria (API public_power)", report_url=PAGE,
                                    document_list="https://api.energy-charts.info/openapi.json", license="public", tables=[TABLE])])
        ip.write_status(CONNECTOR, run_id, results)
    log.close()
    return 0 if all(r["status"] == "ok" for r in results) else 1


if __name__ == "__main__":
    sys.exit(main())

#!/usr/bin/env python3
"""Ontario's hourly generation by fuel, as the Independent Electricity System Operator publishes it (session 2224, chain
099: the fuels behind the demand in ieso_ontario_demand_hourly).

Energy Research Warehouse (ERW) connector. One series table, warehouse/output/ieso_generation_fuel_hourly.csv, from the
IESO's yearly Generator Output by Fuel Type Hourly Reports on its public reports site:

    https://reports-public.ieso.ca/public/GenOutputbyFuelHourly/PUB_GenOutputbyFuelHourly_<YEAR>.xml

Each file is XML: a DocHeader (CreatedAt), a DeliveryYear, then DailyData (Day), HourlyData (Hour 1 to 24) and one
FuelTotal a fuel (NUCLEAR, GAS, HYDRO, WIND, SOLAR, BIOFUEL, OTHER from 2025, and CONTROL ACTIONS on one day of July
2026) with its EnergyValue (OutputQuality, Output). The
IESO's hour is an hour ending in Eastern Standard Time, all year (as in its demand reports), so an hour's start in UTC is
the day's midnight plus the hour less one, plus five hours.

    entity      ieso:ontario
    variable    generation_<fuel> (nuclear, gas, hydro, wind, solar, biofuel, other), MWh (the hour's energy, the
                report's Output); control_actions for the IESO's CONTROL ACTIONS line, which is not a fuel
    ts_utc      the hour's start in UTC, freq PT1H; geo CA-ON; node the fuel as the IESO names it
    x_quality   the report's OutputQuality for the value, as published
    vintage     the file's CreatedAt, read as Eastern Standard Time and written in UTC

A fuel without an Output has no row. A document not of this form, a year not the file's, an hour outside 1 to 24, a fuel
given twice in an hour, a fuel not one of the eight or a value that is not a number stops the run. Nothing is filled.

    python warehouse/connectors/ieso_genfuel.py [--offline] [--years 2020 2026] [--out-dir DIR]

Ceiling: one request a year's file (the current year's fetched fresh each run, earlier years reused from
warehouse/raw/ieso_genfuel/). reports-public.ieso.ca has no robots file (HTTP 404, sessions 2070 and 2224). License: the
IESO's Terms of Use (read 225) grant "a limited, non-exclusive, non-sublicensable, non-transferrable licence to use and
reproduce the Content", provided each reproduction carries the IESO's copyright notice, which this table's header does.
"""

import argparse
import datetime as dt
import os
import sys
import traceback
import xml.etree.ElementTree as ET

import pandas as pd

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import iso_prices as ip  # noqa: E402

CONNECTOR = "ieso_genfuel"
SOURCE = "ieso:gen_output_by_fuel_hourly"
URL = "https://reports-public.ieso.ca/public/GenOutputbyFuelHourly/PUB_GenOutputbyFuelHourly_{year}.xml"
PAGE = "https://reports-public.ieso.ca/public/GenOutputbyFuelHourly/"
TABLE = "ieso_generation_fuel_hourly"
UA = {"User-Agent": "Mozilla/5.0 (compatible; ERW-connector/0.1; +https://github.com/SamuelEnrique/erw)"}
NS = {"i": "http://www.ieso.ca/schema"}
FUELS = ["NUCLEAR", "GAS", "HYDRO", "WIND", "SOLAR", "BIOFUEL", "OTHER", "CONTROL ACTIONS"]
VAR = {f: f"generation_{f.lower()}" for f in FUELS[:-1]} | {"CONTROL ACTIONS": "control_actions"}
X_COLS = ["x_quality"]
EST = dt.timezone(dt.timedelta(hours=-5))
NOTICE = ("Copyright " + chr(0xA9) + " 2004-2022 Independent Electricity System Operator, all rights reserved. This information is subject to "
          "the Terms of Use set out in the IESO's website (www.ieso.ca).")  # as ieso_demand.py carries it


def text(el, path):
    e = el.find(path, NS)
    return None if e is None or e.text is None else e.text.strip()


def parse(content, year, base):
    root = ET.fromstring(content)
    if root.tag != "{http://www.ieso.ca/schema}Document" or root.get("docID") != "GenOutputbyFuelHourly":
        raise RuntimeError(f"{year}: not a GenOutputbyFuelHourly document: {root.tag} {root.get('docID')}")
    created = text(root, "i:DocHeader/i:CreatedAt")
    body = root.find("i:DocBody", NS)
    if body is None or text(body, "i:DeliveryYear") != str(year):
        raise RuntimeError(f"{year}: the file's year is {text(body, 'i:DeliveryYear') if body is not None else None}")
    vintage = ""
    if created:
        vintage = dt.datetime.fromisoformat(created).replace(tzinfo=EST).astimezone(dt.timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
    rows = []
    for day in body.findall("i:DailyData", NS):
        d = dt.date.fromisoformat(text(day, "i:Day"))
        if d.year != year:
            raise RuntimeError(f"{year}: a day of another year: {d}")
        for hd in day.findall("i:HourlyData", NS):
            h = int(text(hd, "i:Hour"))
            if not 1 <= h <= 24:
                raise RuntimeError(f"{d}: an hour outside 1 to 24: {h}")
            ts = (dt.datetime(d.year, d.month, d.day, tzinfo=EST) + dt.timedelta(hours=h - 1)).astimezone(dt.timezone.utc)
            seen = set()
            for ft in hd.findall("i:FuelTotal", NS):
                fuel = text(ft, "i:Fuel")
                if fuel not in FUELS:
                    raise RuntimeError(f"{d} hour {h}: a fuel not one of the eight: {fuel!r}")
                if fuel in seen:
                    raise RuntimeError(f"{d} hour {h}: {fuel} given twice")
                seen.add(fuel)
                out = text(ft, "i:EnergyValue/i:Output")
                if out is None or out == "":
                    continue
                try:
                    v = float(out)
                except ValueError:
                    raise RuntimeError(f"{d} hour {h} {fuel}: a value not a number: {out!r}")
                rows.append(dict(entity="ieso:ontario", variable=VAR[fuel], ts_utc=ts.strftime("%Y-%m-%dT%H:%M:%SZ"),
                                 value=v, unit="MWh", freq="PT1H", geo="CA-ON", market="", node=fuel, **base, vintage=vintage,
                                 x_quality=text(ft, "i:EnergyValue/i:OutputQuality") or ""))
    if not rows:
        raise RuntimeError(f"{year}: no hour in the file")
    return rows


def main(argv=None):
    ap = argparse.ArgumentParser(description="The IESO's hourly generation by fuel")
    ap.add_argument("--offline", action="store_true", help="the saved files only, no request")
    ap.add_argument("--years", nargs=2, type=int, default=[2020, dt.date.today().year], metavar=("FIRST", "LAST"))
    ap.add_argument("--out-dir", help="a trial: the table under this folder, not warehouse/output")
    args = ap.parse_args(argv)
    if ip.paused(CONNECTOR) or ip.paused_host("reports-public.ieso.ca"):
        print(f"{TABLE}: the publisher is paused (warehouse/metadata/paused_sources.csv); nothing asked")
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
        rows, years = [], list(range(args.years[0], args.years[1] + 1))
        this_year = dt.date.today().year
        for y in years:
            url = URL.format(year=y)
            content, rec = ip.fetch_raw(CONNECTOR, url, log, offline=args.offline, fresh=(not args.offline and y == this_year),
                                        headers=UA, timeout=180, pause=2)
            base = dict(source=SOURCE, source_url=url, retrieved_at=rec.get("retrieved_at") or "")
            rows += parse(content, y, base)
        s = pd.DataFrame(rows)
        if s.duplicated(["entity", "variable", "ts_utc"]).any():
            raise RuntimeError("an hour and fuel given twice across the files")
        cols = ip.SERIES_COLS + X_COLS
        s = s[cols].sort_values(["variable", "ts_utc"]).reset_index(drop=True)
        hours = s.ts_utc.nunique()
        q = s.x_quality.value_counts().to_dict()
        tot = s.groupby(s.ts_utc.str[:4]).value.sum() / 1e6
        head = [
            "Energy Research Warehouse (ERW): Independent Electricity System Operator (IESO), Ontario, Generator Output by Fuel Type Hourly "
            f"Report: Ontario's generation by fuel, an hour, {years[0]} to {years[-1]} (session 2224)",
            "Shape: series (docs/datastandard.md v0). entity ieso:ontario; variable generation_<fuel> (nuclear, gas, hydro, wind, solar, biofuel, "
            "other) and control_actions (the IESO's CONTROL ACTIONS line), unit MWh (the hour's energy, the report's Output); ts_utc the hour's start in UTC (the IESO's hour ending in Eastern Standard "
            "Time, all year); freq PT1H; geo CA-ON; node the fuel as the IESO names it; x_quality the report's OutputQuality as published; vintage "
            "the file's CreatedAt in UTC.",
            f"{len(s)} rows, {hours} hours, {s.ts_utc.min()} to {s.ts_utc.max()}; OutputQuality as published: "
            + ", ".join(f"{k} {v}" for k, v in sorted(q.items())) + "; TWh a calendar year (UTC hours): "
            + ", ".join(f"{k} {v:.2f}" for k, v in tot.items()) + ". A fuel without an Output has no row. Nothing is filled.",
            f"Retrieved: {run_id} (UTC) by warehouse/connectors/ieso_genfuel.py; one file a year",
            f"Run log: warehouse/output/logs/{CONNECTOR}_{run_id}.log",
            f"Raw files: warehouse/raw/{CONNECTOR}/ (not in git)",
            f"Source: {SOURCE} IESO, Generator Output by Fuel Type Hourly Report, {PAGE}",
            f"  access: {URL}",
            f"License: the IESO's Terms of Use, a licence to use and reproduce with its notice: {NOTICE}",
        ]
        ip.write_snapshot(s, TABLE, head, log, cols)
        results.append(dict(table=TABLE, market="all", status="ok", detail=f"{len(s)} rows"))
        print(f"{TABLE}: {len(s)} rows, {hours} hours, quality {q}")
    except Exception:
        tb = ip.redact(traceback.format_exc())
        log(f"{TABLE} FAILED, no output file written:\n{tb}")
        print(f"{TABLE} FAILED, no output file written: {tb.strip().splitlines()[-1]}", file=sys.stderr)
        results.append(dict(table=TABLE, market="all", status="failed", detail=tb.strip().splitlines()[-1][:300]))
    if not args.out_dir:
        if results and results[0]["status"] == "ok":
            ip.update_sources([dict(source=SOURCE, publisher="Independent Electricity System Operator (IESO), Ontario",
                                    report="Generator Output by Fuel Type Hourly Report", report_url=PAGE, document_list=URL.format(year="<YEAR>"),
                                    license="public", tables=[TABLE])])
        ip.write_status(CONNECTOR, run_id, results)
    log.close()
    return 0 if all(r["status"] == "ok" for r in results) else 1


if __name__ == "__main__":
    sys.exit(main())

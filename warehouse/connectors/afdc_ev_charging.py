#!/usr/bin/env python3
"""The Alternative Fuels Data Center's historical station counts: public and private (non-residential) electric vehicle
charging stations and their ports, Level 1, Level 2 and DC fast, by state, near the end of December each year (session
2155, chain 092: a source of the session's choosing, the charging that is a new and growing load on the grid).

Energy Research Warehouse (ERW) connector. One series table from AFDC's workbook "Historical Alternative Fueling Station
Counts", linked from its station counts by state page:

    https://afdc.energy.gov/stations/states   (the page; the workbook's address is read from it)
    https://afdc.energy.gov/files/docs/historical-station-counts.xlsx

    afdc_ev_charging_state_annual   entity afdc_ev:<state postal code>; variables ev_stations (station locations),
               ev_ports (charging outlets: EV charging ports from 2021, connectors before, as AFDC's notes say),
               ev_level1_ports, ev_level2_ports, ev_dcfast_ports (count); ts_utc 1 January of the year (the counts are
               AFDC's near the end of December of that year); freq P1Y; geo US-<state>; node the state as AFDC names it;
               x_counted_at AFDC's words for when (near the end of December)

AFDC's notes: the counts are public and private (non-residential) stations in its Station Locator, legacy chargers
included and residential charging not; changes in the counts are openings net of closures; in 2021 NREL moved to the
OCPI hierarchy, so from then an outlet is a port (vehicles that can charge at once), where before it was a connector.
Each year's sheet (2014 on, the years with the EV columns) must hold the header read below and two lines a state, the
second the Level 1, Level 2 and DC fast ports; the states (with DC) must sum to the sheet's Total row in every column,
or the run stops. Where a state's three levels do not sum to its ports (one to four states a year, among them Georgia in
2016, whose levels exceed its ports), both are kept as AFDC prints them and the header lists each. The Total row is checked and not kept. A cell that does not read
as "a | b" or "a | b | c" of whole numbers, or a state not in the map, stops the run. Other fuels are not taken. Nothing
is filled.

    python warehouse/connectors/afdc_ev_charging.py [--offline] [--out-dir DIR]

Ceiling: two requests (the page and the workbook, saved in warehouse/raw/afdc_ev_charging/, asked again unless
--offline, since AFDC adds a year to the same address). afdc.energy.gov's robots file holds no rule. License: public
(DOE, read 54: AFDC's pages link DOE's web policies and name no terms of their own, as for afdc_vehicle_registrations).
"""

import argparse
import datetime as dt
import io
import os
import re
import sys
import traceback
import urllib.parse

import pandas as pd

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import iso_prices as ip  # noqa: E402

CONNECTOR = "afdc_ev_charging"
SOURCE = "afdc:historical_station_counts"
HOST = "afdc.energy.gov"
PAGE = "https://afdc.energy.gov/stations/states"
TABLE = "afdc_ev_charging_state_annual"
FIRST = 2014
UA = {"User-Agent": "Mozilla/5.0 (compatible; ERW-connector/0.1; +https://github.com/SamuelEnrique/erw)"}
X_COLS = ["x_counted_at"]
STATES = {"Alabama": "AL", "Alaska": "AK", "Arizona": "AZ", "Arkansas": "AR", "California": "CA", "Colorado": "CO", "Connecticut": "CT",
          "Delaware": "DE", "District of Columbia": "DC", "Florida": "FL", "Georgia": "GA", "Hawaii": "HI", "Idaho": "ID", "Illinois": "IL",
          "Indiana": "IN", "Iowa": "IA", "Kansas": "KS", "Kentucky": "KY", "Louisiana": "LA", "Maine": "ME", "Maryland": "MD",
          "Massachusetts": "MA", "Michigan": "MI", "Minnesota": "MN", "Mississippi": "MS", "Missouri": "MO", "Montana": "MT", "Nebraska": "NE",
          "Nevada": "NV", "New Hampshire": "NH", "New Jersey": "NJ", "New Mexico": "NM", "New York": "NY", "North Carolina": "NC",
          "North Dakota": "ND", "Ohio": "OH", "Oklahoma": "OK", "Oregon": "OR", "Pennsylvania": "PA", "Rhode Island": "RI",
          "South Carolina": "SC", "South Dakota": "SD", "Tennessee": "TN", "Texas": "TX", "Utah": "UT", "Vermont": "VT", "Virginia": "VA",
          "Washington": "WA", "West Virginia": "WV", "Wisconsin": "WI", "Wyoming": "WY"}
VARS = ["ev_stations", "ev_ports", "ev_level1_ports", "ev_level2_ports", "ev_dcfast_ports"]


def workbook_url(page):
    hits = sorted(set(h for h in re.findall(r'href="([^"]+\.xlsx)"', page) if "historical-station-counts" in h))
    if len(hits) != 1:
        raise RuntimeError(f"the page links not one historical station counts workbook: {hits}")
    return urllib.parse.urljoin(PAGE, hits[0])


def parts(cell, n, where):
    s = str(cell).strip()
    f = [x.strip().replace(",", "") for x in s.split("|")]
    if len(f) != n or not all(x.isdigit() for x in f):
        raise RuntimeError(f"{where}: {s!r} is not {n} whole numbers joined by '|'")
    return [int(x) for x in f]


def parse_year(v, year, base, unequal):
    if not str(v.iat[2, 4]).strip().startswith("(stations / charging outlets") or str(v.iat[1, 0]).strip() != "State":
        raise RuntimeError(f"{year}: the header is not as read: {list(v.iloc[1, :5])} {v.iat[2, 4]!r}")
    out, seen, total = [], set(), None
    sums = [0] * 5
    i = 4
    while i < len(v):
        name = str(v.iat[i, 0]).strip()
        if not name:
            i += 1
            continue
        if name == "Total":
            st, ports = parts(v.iat[i, 4], 2, f"{year} Total")
            lv = parts(v.iat[i + 1, 4], 3, f"{year} Total levels") if i + 1 < len(v) and str(v.iat[i + 1, 4]).strip() else None
            total = [st, ports] + (lv or [None] * 3)
            break
        if name not in STATES:
            raise RuntimeError(f"{year} row {i}: not a state in the map: {name!r}")
        if name in seen:
            raise RuntimeError(f"{year}: {name} given twice")
        seen.add(name)
        st, ports = parts(v.iat[i, 4], 2, f"{year} {name}")
        lv = parts(v.iat[i + 1, 4], 3, f"{year} {name} levels")
        if sum(lv) != ports:
            unequal.append(f"{year} {name} {sum(lv)} of {ports}")  # as AFDC prints them: counted, not changed
        vals = [st, ports] + lv
        sums = [a + b for a, b in zip(sums, vals)]
        code = STATES[name]
        for var, val in zip(VARS, vals):
            out.append(dict(base, entity=f"afdc_ev:{code.lower()}", variable=var, ts_utc=f"{year}-01-01T00:00:00Z", value=float(val),
                            unit="count", freq="P1Y", geo=f"US-{code}", market="", node=name, x_counted_at=f"near the end of December {year}"))
        i += 2
    if total is None:
        raise RuntimeError(f"{year}: no Total row")
    if len(seen) != len(STATES):
        raise RuntimeError(f"{year}: {len(seen)} states, missing {sorted(set(STATES) - seen)}")
    for k, (a, b) in enumerate(zip(sums, total)):
        if b is not None and a != b:
            raise RuntimeError(f"{year}: the states' {VARS[k]} sum to {a}, the Total row is {b}")
    return out


def main(argv=None):
    ap = argparse.ArgumentParser(description="AFDC's historical EV charging station and port counts by state")
    ap.add_argument("--offline", action="store_true", help="the saved files only, no request")
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
        if ip.paused(CONNECTOR) or ip.paused_host(HOST):
            raise RuntimeError(f"{HOST} is paused (warehouse/metadata/paused_sources.csv): no request made")
        page, _ = ip.fetch_raw(CONNECTOR, PAGE, log, offline=args.offline, fresh=not args.offline, headers=UA, timeout=120, pause=1)
        url = workbook_url(page.decode("utf-8", errors="replace"))
        content, rec = ip.fetch_raw(CONNECTOR, url, log, offline=args.offline, fresh=not args.offline, headers=UA, timeout=120, pause=1)
        base = dict(source=SOURCE, source_url=url, retrieved_at=rec.get("retrieved_at") or "", vintage=ip.vintage_of(rec))
        x = pd.ExcelFile(io.BytesIO(content))
        years = sorted(int(s) for s in x.sheet_names if re.fullmatch(r"\d{4}", s) and int(s) >= FIRST)
        if not years or years != list(range(FIRST, max(years) + 1)):
            raise RuntimeError(f"the workbook's years from {FIRST} are not a run: {years}")
        rows, unequal = [], []
        for year in years:
            v = pd.read_excel(x, str(year), header=None, dtype=object, keep_default_na=False)
            got = parse_year(v, year, base, unequal)
            log(f"  {year}: {len(got)} rows")
            rows += got
        s = pd.DataFrame(rows)
        if s.duplicated(["entity", "variable", "ts_utc"]).any():
            raise RuntimeError("an (entity, variable, ts_utc) given twice")
        cols = ip.SERIES_COLS + X_COLS
        s = s[cols].sort_values(["entity", "variable", "ts_utc"]).reset_index(drop=True)
        head = [
            "Energy Research Warehouse (ERW): U.S. Department of Energy, Alternative Fuels Data Center, historical station counts: public and "
            f"private (non-residential) EV charging stations and ports by state, near the end of December, {years[0]} to {years[-1]} (session 2155)",
            "Shape: series (docs/datastandard.md v0). entity afdc_ev:<state>; variables ev_stations, ev_ports, ev_level1_ports, ev_level2_ports, "
            "ev_dcfast_ports (count); freq P1Y; ts_utc 1 January of the year (counted near the end of its December); geo US-<state>; node the "
            "state; x_counted_at.",
            "AFDC's notes: legacy chargers included, residential charging not; counts are openings net of closures; from 2021 an outlet is a "
            "port (OCPI hierarchy), before a connector, so 2021's jump is partly the new counting. Checked as read: the states with DC sum to "
            "each sheet's Total row in every column; the Total row is not kept. Where a state's three levels do not sum to its ports, both are "
            f"kept as AFDC prints them ({len(unequal)}: {'; '.join(unequal)}). Nothing is filled.",
            f"Retrieved: {run_id} (UTC) by warehouse/connectors/afdc_ev_charging.py; the workbook retrieved {base['retrieved_at']}",
            f"Run log: warehouse/output/logs/{CONNECTOR}_{run_id}.log",
            f"Raw files: warehouse/raw/{CONNECTOR}/ (not in git)",
            f"Source: {SOURCE} U.S. Department of Energy, Alternative Fuels Data Center, Historical Alternative Fueling Station Counts, {PAGE}",
            f"  access: {url}",
            'License: public (DOE; cite "U.S. Department of Energy, Alternative Fuels Data Center, Station Locator").',
        ]
        ip.write_snapshot(s, TABLE, head, log, cols)
        results.append(dict(table=TABLE, market="all", status="ok", detail=f"{len(s)} rows"))
        print(f"{TABLE}: {len(s)} rows, {s.entity.nunique()} areas, {years[0]} to {years[-1]}")
    except Exception:
        tb = ip.redact(traceback.format_exc())
        log(f"{TABLE} FAILED, no output file written:\n{tb}")
        print(f"{TABLE} FAILED, no output file written: {tb.strip().splitlines()[-1]}", file=sys.stderr)
        results.append(dict(table=TABLE, market="all", status="failed", detail=tb.strip().splitlines()[-1][:300]))
    if not args.out_dir:
        if results and results[0]["status"] == "ok":
            ip.update_sources([dict(source=SOURCE, publisher="U.S. Department of Energy (DOE)",
                                    report="Historical Alternative Fueling Station Counts (EV charging stations and ports by state)",
                                    report_url=PAGE, document_list=PAGE, license="public", tables=[TABLE])])
        ip.write_status(CONNECTOR, run_id, results)
    log.close()
    return 0 if all(r["status"] == "ok" for r in results) else 1


if __name__ == "__main__":
    sys.exit(main())

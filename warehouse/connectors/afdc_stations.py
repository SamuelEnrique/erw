#!/usr/bin/env python3
"""The Alternative Fuels Data Center's alternative fueling station counts by state and fuel type, near the end of each
December from 2007: electric charging locations and ports (by level from 2014), hydrogen, natural gas, propane, E85,
biodiesel and renewable diesel (session 2141, chain 090: the chargers whose load grows with the vehicles in
afdc_vehicle_registrations_annual).

Energy Research Warehouse (ERW) connector. One series table from AFDC's historical counts workbook, linked from its
Alternative Fueling Station Counts by State page (https://afdc.energy.gov/stations/states):

    https://afdc.energy.gov/files/docs/historical-station-counts.xlsx   a sheet a year (2007 to 2025) and an About the
        Data sheet; public and private (non-residential) stations in the Station Locator near the end of December

    afdc_station_counts_annual   entity afdc_st:<state code>, and afdc_st:US for the sheet's own Total row; variable as
                                 below, unit count; ts_utc the year's first day (the count is as of late December); freq
                                 P1Y; geo US-<state> or US; node the column's name as the sheet prints it

    2014 on (stations / ports and Level 1 / Level 2 / DC Fast under Electric; retail / non-retail / total under Hydrogen;
    primary / secondary / total under Propane): stations_biodiesel, stations_cng, stations_e85, ev_locations, ev_ports,
    ev_ports_level1, ev_ports_level2, ev_ports_dc_fast, stations_hydrogen_retail, stations_hydrogen_non_retail,
    stations_hydrogen, stations_lng, stations_propane_primary, stations_propane_secondary, stations_propane,
    stations_renewable_diesel, stations_total.
    2007 to 2013 (one number a fuel): stations_biodiesel, stations_cng, stations_e85, stations_hydrogen, stations_lng,
    stations_propane, stations_total, and the Electric column as ev_locations for 2007 to 2010 and as ev_ports for 2011 to
    2013, as the About the Data sheet says it counts.

The sheet's Total column is kept as published: AFDC's note says it counts a station once for each fuel it offers, and
electric by ports. In the sheets for 2007 to 2013 a state's Total does not always equal the sum of its fuels; the
header counts those rows. A sheet whose header is not one of the two forms, a place not known, a count not a whole number
(commas allowed), a pair or triple that is not one, or a year sheet given twice stops the run. Nothing is filled.

    python warehouse/connectors/afdc_stations.py [--offline] [--out-dir DIR]

Ceiling: one request, saved in warehouse/raw/afdc_stations/ and reused offline (asked fresh when not offline: AFDC
replaces the workbook at its address each year). afdc.energy.gov's robots file holds no rule (read 215). License: public
(DOE, read 54).
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
import afdc_registrations as ar  # noqa: E402  the same publisher's place names (PLACES)

CONNECTOR = "afdc_stations"
SOURCE = "doe:afdc_station_counts"
URL = "https://afdc.energy.gov/files/docs/historical-station-counts.xlsx"
PAGE = "https://afdc.energy.gov/stations/states"
TABLE = "afdc_station_counts_annual"
UA = {"User-Agent": "Mozilla/5.0 (compatible; ERW-connector/0.1; +https://github.com/SamuelEnrique/erw)"}
X_COLS = ["x_layout"]
NEW_HEAD = ["State", "Biodiesel", "CNG", "E85", "Electrica", "Hydrogenb", "LNG", "Propanec", "Renewable Diesel", "Totald"]
OLD_HEAD = ["State", "Biodiesel", "CNG", "E85", "Electric", "Hydrogen", "LNG", "Propane", "Total"]
PLAIN = {"Biodiesel": "stations_biodiesel", "CNG": "stations_cng", "E85": "stations_e85", "LNG": "stations_lng",
         "Renewable Diesel": "stations_renewable_diesel", "Totald": "stations_total", "Total": "stations_total",
         "Hydrogen": "stations_hydrogen", "Propane": "stations_propane"}


def whole(v, what):
    if isinstance(v, (int, float)) and float(v).is_integer():
        return int(v)
    s = str(v).strip().replace(",", "")
    if not re.fullmatch(r"\d+", s):
        raise RuntimeError(f"{what}: a count not a whole number: {v!r}")
    return int(s)


def parts(v, n, what):
    p = [x.strip() for x in str(v).split("|")]
    if len(p) != n:
        raise RuntimeError(f"{what}: {n} numbers expected, found {v!r}")
    return [whole(x, what) for x in p]


def place(name, what):
    if name == "Total":
        return "US"
    if name not in ar.PLACES:
        raise RuntimeError(f"{what}: a place not known: {name!r}")
    return ar.PLACES[name]


def parse_sheet(rows, year):
    """One year's sheet as (place, variable, node, count) tuples, and the form it is in."""
    head_at = [i for i, r in enumerate(rows) if r and r[0] == "State"]
    if len(head_at) != 1:
        raise RuntimeError(f"{year}: {len(head_at)} header rows")
    h = head_at[0]
    head = [c for c in rows[h] if c is not None]
    out = []
    if head == NEW_HEAD:
        layout = "2014_on"
        cols = {c: i for i, c in enumerate(rows[h]) if c}
        i = h + 3
        while i < len(rows):
            r = rows[i]
            if not r or r[0] is None or str(r[0]).startswith("("):
                i += 1
                continue
            where = f"{year} {r[0]}"
            st = place(r[0], where)
            for c in ("Biodiesel", "CNG", "E85", "LNG", "Renewable Diesel", "Totald"):
                out.append((st, PLAIN[c], c, whole(r[cols[c]], where)))
            loc, ports = parts(r[cols["Electrica"]], 2, where)
            l1, l2, dc = parts(rows[i + 1][cols["Electrica"]], 3, where + " (levels)")
            out += [(st, "ev_locations", "Electric: stations", loc), (st, "ev_ports", "Electric: charging outlets", ports),
                    (st, "ev_ports_level1", "Electric: Level 1", l1), (st, "ev_ports_level2", "Electric: Level 2", l2),
                    (st, "ev_ports_dc_fast", "Electric: DC Fast", dc)]
            hr, hn, ht = parts(r[cols["Hydrogenb"]], 3, where)
            out += [(st, "stations_hydrogen_retail", "Hydrogen: retail", hr), (st, "stations_hydrogen_non_retail", "Hydrogen: non-retail", hn),
                    (st, "stations_hydrogen", "Hydrogen: total", ht)]
            pp, ps, pt = parts(r[cols["Propanec"]], 3, where)
            out += [(st, "stations_propane_primary", "Propane: primary", pp), (st, "stations_propane_secondary", "Propane: secondary", ps),
                    (st, "stations_propane", "Propane: total", pt)]
            i += 2
    else:
        names = [rows[h][k] if rows[h][k] is not None else rows[h + 2][k] for k in range(len(rows[h]))]
        if [c for c in names if c is not None] != OLD_HEAD:
            raise RuntimeError(f"{year}: a header not of either form: {names}")
        layout = "2007_2013"
        ev = "ev_locations" if year <= 2010 else "ev_ports"
        for r in rows[h + 3:]:
            if not r or r[0] is None:
                continue
            if str(r[0]).startswith("("):
                break
            where = f"{year} {r[0]}"
            st = place(r[0], where)
            for k, c in enumerate(names):
                if c is None or c == "State":
                    continue
                out.append((st, ev if c == "Electric" else PLAIN[c], c, whole(r[k], where)))
    return out, layout


def parse(content):
    wb = openpyxl.load_workbook(io.BytesIO(content), read_only=True, data_only=True)
    years = [ws.title for ws in wb.worksheets if re.fullmatch(r"\d{4}", ws.title)]
    if len(years) != len(set(years)) or not years:
        raise RuntimeError(f"the year sheets: {years}")
    per_year = {}
    for y in years:
        per_year[int(y)] = parse_sheet(list(wb[y].iter_rows(values_only=True)), int(y))
    return per_year


def main(argv=None):
    ap = argparse.ArgumentParser(description="AFDC's alternative fueling station counts by state, a year from 2007")
    ap.add_argument("--offline", action="store_true", help="the saved workbook only, no request")
    ap.add_argument("--out-dir", help="a trial: the table under this folder, not warehouse/output")
    args = ap.parse_args(argv)
    if ip.paused(CONNECTOR) or ip.paused_host("afdc.energy.gov"):
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
        content, rec = ip.fetch_raw(CONNECTOR, URL, log, offline=args.offline, fresh=not args.offline, headers=UA, timeout=60, pause=1)
        base = dict(source=SOURCE, source_url=URL, retrieved_at=rec.get("retrieved_at") or "", vintage=ip.vintage_of(rec))
        per_year = parse(content)
        rows, uneven = [], 0
        for y, (tuples, layout) in sorted(per_year.items()):
            for st, var, node, n in tuples:
                rows.append(dict(entity=f"afdc_st:{st}", variable=var, ts_utc=f"{y}-01-01T00:00:00Z", value=n, unit="count", freq="P1Y",
                                 geo="US" if st == "US" else f"US-{st}", market="", node=node, **base, x_layout=layout))
            if layout == "2007_2013":
                by = {}
                for st, var, node, n in tuples:
                    by.setdefault(st, {})[var] = n
                uneven += sum(1 for st, v in by.items() if v["stations_total"] != sum(n for k, n in v.items() if k != "stations_total"))
        s = pd.DataFrame(rows)
        if s.duplicated(["entity", "variable", "ts_utc"]).any():
            d = s[s.duplicated(["entity", "variable", "ts_utc"], keep=False)]
            raise RuntimeError(f"a count given twice: {d[['entity', 'variable', 'ts_utc']].head(3).values.tolist()}")
        cols = ip.SERIES_COLS + X_COLS
        s = s[cols].sort_values(["entity", "variable", "ts_utc"]).reset_index(drop=True)
        us = s[s.entity == "afdc_st:US"].set_index(["variable", "ts_utc"]).value
        last = max(per_year)
        head = [
            "Energy Research Warehouse (ERW): U.S. Department of Energy, Alternative Fuels Data Center, historical alternative fueling station counts by "
            f"state and fuel type, near the end of each December, {min(per_year)} to {last} (session 2141)",
            "Shape: series (docs/datastandard.md v0). entity afdc_st:<state> or afdc_st:US (the sheet's Total row); variable stations_<fuel>, ev_locations, "
            "ev_ports and, from 2014, ev_ports_level1, _level2, _dc_fast and the hydrogen and propane designations; unit count; ts_utc the year's first "
            "day (the count is as of late December); freq P1Y; node the column as printed; x_layout the sheet's form.",
            f"{len(s)} rows, {s.entity.nunique()} places, {len(per_year)} years. The United States at the end of {last}: "
            f"{us.get(('ev_ports', f'{last}-01-01T00:00:00Z'), float('nan')):,.0f} charging ports at "
            f"{us.get(('ev_locations', f'{last}-01-01T00:00:00Z'), float('nan')):,.0f} locations "
            f"({us.get(('ev_ports_dc_fast', f'{last}-01-01T00:00:00Z'), float('nan')):,.0f} DC fast). "
            "AFDC's note: public and private (non-residential) stations; the Electric column counts locations for 2007 to 2010 and ports for 2011 to "
            "2013; EV counts jump in 2021 as charging networks' OCPI feeds were integrated. "
            f"stations_total as published: it counts a station once a fuel, electric by ports; {uneven} place-years of 2007 to 2013 have a Total "
            "that is not the sum of their fuels. Nothing is filled.",
            f"Retrieved: {run_id} (UTC) by warehouse/connectors/afdc_stations.py; the workbook retrieved {base['retrieved_at']}",
            f"Run log: warehouse/output/logs/{CONNECTOR}_{run_id}.log",
            f"Raw files: warehouse/raw/{CONNECTOR}/ (not in git)",
            f"Source: {SOURCE} DOE, Alternative Fuels Data Center, Historical Station Counts, {URL} (linked from {PAGE})",
            "License: public (U.S. Department of Energy; AFDC's pages link DOE's web policies, read 54).",
        ]
        ip.write_snapshot(s, TABLE, head, log, cols)
        results.append(dict(table=TABLE, market="all", status="ok", detail=f"{len(s)} rows"))
        print(f"{TABLE}: {len(s)} rows, {len(per_year)} years, {uneven} uneven totals")
    except Exception:
        tb = ip.redact(traceback.format_exc())
        log(f"{TABLE} FAILED, no output file written:\n{tb}")
        print(f"{TABLE} FAILED, no output file written: {tb.strip().splitlines()[-1]}", file=sys.stderr)
        results.append(dict(table=TABLE, market="all", status="failed", detail=tb.strip().splitlines()[-1][:300]))
    if not args.out_dir:
        if results and results[0]["status"] == "ok":
            ip.update_sources([dict(source=SOURCE, publisher="U.S. Department of Energy (DOE)",
                                    report="Alternative Fuels Data Center: Historical Alternative Fueling Station Counts", report_url=PAGE,
                                    document_list=URL, license="public", tables=[TABLE])])
        ip.write_status(CONNECTOR, run_id, results)
    log.close()
    return 0 if all(r["status"] == "ok" for r in results) else 1


if __name__ == "__main__":
    sys.exit(main())

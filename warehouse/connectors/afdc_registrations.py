#!/usr/bin/env python3
"""The Alternative Fuels Data Center's light-duty vehicle registration counts by state and fuel type, a year: electric,
plug-in hybrid, hybrid, flex fuel, gasoline, diesel and the rest, as the Department of Energy publishes them (session 2036,
chain 058: the electric vehicles whose charging is a growing load, state by state).

Energy Research Warehouse (ERW) connector. One series table from the table AFDC's Vehicle Registration Counts by State page
prints for each year (https://afdc.energy.gov/vehicle-registration?year=<year>, 2016 to 2025), not from AFDC's API, which
needs a key the ERW does not hold. The counts are derived by the National Laboratory of the Rockies (formerly NREL) from
Experian Information Solutions' data, rounded to the closest 100 vehicles, and count the light-duty vehicles registered
through the selected year.

    afdc_vehicle_registrations_annual   entity afdc_reg:<state code>, and afdc_reg:US for the page's own United States row;
                                        variable registrations_<fuel> (ev, phev, hev, biodiesel, e85, cng, propane,
                                        hydrogen, methanol, gasoline, diesel, unknown_fuel), unit count; ts_utc the year's
                                        first day (the count is as of the year's end); freq P1Y; geo US-<state> or US; node
                                        the column's name as the page prints it

A page whose table does not have these twelve columns after State, a place not known, a count not a whole number (commas
allowed) or a year whose table is not the year asked stops the run. Nothing is filled.

    python warehouse/connectors/afdc_registrations.py [--offline] [--out-dir DIR] [--years 2016-2025]

Ceiling: one request a year (ten), saved in warehouse/raw/afdc_registrations/ and reused offline. afdc.energy.gov's
robots file holds no rule. License: public (DOE, read 54: AFDC's pages link DOE's web policies and name no terms of their own).
"""

import argparse
import datetime as dt
import html as htmlmod
import os
import re
import sys
import traceback

import pandas as pd

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import iso_prices as ip  # noqa: E402

CONNECTOR = "afdc_registrations"
SOURCE = "doe:afdc_vehicle_registrations"
PAGE = "https://afdc.energy.gov/vehicle-registration"
TABLE = "afdc_vehicle_registrations_annual"
UA = {"User-Agent": "Mozilla/5.0 (compatible; ERW-connector/0.1; +https://github.com/SamuelEnrique/erw)"}
YEARS = (2016, 2025)
COLUMNS = {"Electric (EV)": "ev", "Plug-In Hybrid Electric (PHEV)": "phev", "Hybrid Electric (HEV)": "hev", "Biodiesel": "biodiesel",
           "Ethanol/Flex (E85)": "e85", "Compressed Natural Gas (CNG)": "cng", "Propane": "propane", "Hydrogen": "hydrogen",
           "Methanol": "methanol", "Gasoline": "gasoline", "Diesel": "diesel", "Unknown Fuel": "unknown_fuel"}
PLACES = {"Alabama": "AL", "Alaska": "AK", "Arizona": "AZ", "Arkansas": "AR", "California": "CA", "Colorado": "CO", "Connecticut": "CT",
          "Delaware": "DE", "District of Columbia": "DC", "Florida": "FL", "Georgia": "GA", "Hawaii": "HI", "Idaho": "ID", "Illinois": "IL",
          "Indiana": "IN", "Iowa": "IA", "Kansas": "KS", "Kentucky": "KY", "Louisiana": "LA", "Maine": "ME", "Maryland": "MD",
          "Massachusetts": "MA", "Michigan": "MI", "Minnesota": "MN", "Mississippi": "MS", "Missouri": "MO", "Montana": "MT", "Nebraska": "NE",
          "Nevada": "NV", "New Hampshire": "NH", "New Jersey": "NJ", "New Mexico": "NM", "New York": "NY", "North Carolina": "NC",
          "North Dakota": "ND", "Ohio": "OH", "Oklahoma": "OK", "Oregon": "OR", "Pennsylvania": "PA", "Rhode Island": "RI",
          "South Carolina": "SC", "South Dakota": "SD", "Tennessee": "TN", "Texas": "TX", "Utah": "UT", "Vermont": "VT", "Virginia": "VA",
          "Washington": "WA", "West Virginia": "WV", "Wisconsin": "WI", "Wyoming": "WY", "United States": "US"}


def url_of(year):
    return f"{PAGE}?year={year}"


def cells(row):
    return [htmlmod.unescape(re.sub(r"<[^>]+>", "", c)).strip() for c in re.findall(r"<t[hd][^>]*>.*?</t[hd]>", row, re.S)]


def parse(page, year):
    """{(place code, column name): count} of the year's table."""
    title = re.search(r"(\d{4}) Light-Duty Vehicle Registration Counts by State and Fuel Type", page)
    if not title or int(title.group(1)) != year:
        raise RuntimeError(f"{year}: the page's table is for {title.group(1) if title else 'no year'}")
    tables = re.findall(r"<table.*?</table>", page, re.S)
    if len(tables) != 1:
        raise RuntimeError(f"{year}: {len(tables)} tables on the page, not one")
    rows = [cells(r) for r in re.findall(r"<tr.*?</tr>", tables[0], re.S)]
    head = rows[0]
    if head != ["State"] + list(COLUMNS):
        raise RuntimeError(f"{year}: the table's columns are {head}")
    out = {}
    for r in rows[1:]:
        if r[0] not in PLACES:
            raise RuntimeError(f"{year}: a place not known: {r[0]!r}")
        if len(r) != len(head):
            raise RuntimeError(f"{year}: {r[0]} has {len(r)} cells")
        for name, v in zip(head[1:], r[1:]):
            if not re.fullmatch(r"\d{1,3}(,\d{3})*", v):
                raise RuntimeError(f"{year}: {r[0]}, {name}: not a whole number: {v!r}")
            out[(PLACES[r[0]], name)] = int(v.replace(",", ""))
    if len({k[0] for k in out}) != 52:
        raise RuntimeError(f"{year}: {len({k[0] for k in out})} places, not the 50 states, DC and the United States")
    return out


def build(per_year, base_of):
    rows = []
    for year, counts in per_year:
        for (place, name), v in counts.items():
            rows.append(dict(entity=f"afdc_reg:{place}", variable=f"registrations_{COLUMNS[name]}", ts_utc=f"{year}-01-01T00:00:00Z", value=v,
                             unit="count", freq="P1Y", geo="US" if place == "US" else f"US-{place}", market="", node=name, **base_of(year)))
    return pd.DataFrame(rows)


def main(argv=None):
    ap = argparse.ArgumentParser(description="AFDC's light-duty vehicle registration counts by state and fuel type, a year")
    ap.add_argument("--offline", action="store_true", help="the saved pages only, no request")
    ap.add_argument("--out-dir", help="a trial: the table under this folder, not warehouse/output")
    ap.add_argument("--years", default=f"{YEARS[0]}-{YEARS[1]}")
    args = ap.parse_args(argv)
    y0, y1 = (int(x) for x in args.years.split("-"))
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
        per_year, recs = [], {}
        for year in range(y0, y1 + 1):
            content, rec = ip.fetch_raw(CONNECTOR, url_of(year), log, offline=args.offline, fresh=not args.offline, headers=UA,
                                        timeout=60, pause=1)  # a year's page can be revised at the same address
            recs[year] = rec
            per_year.append((year, parse(content.decode("utf-8", errors="replace"), year)))

        def base_of(year):
            return dict(source=SOURCE, source_url=url_of(year), retrieved_at=recs[year].get("retrieved_at") or "", vintage=ip.vintage_of(recs[year]))
        s = build(per_year, base_of)
        if s.duplicated(["entity", "variable", "ts_utc"]).any():
            raise RuntimeError("a place, fuel and year given twice")
        cols = ip.SERIES_COLS
        s = s[cols].sort_values(["entity", "variable", "ts_utc"]).reset_index(drop=True)
        us_ev = {y: c[("US", "Electric (EV)")] for y, c in per_year}
        head = [
            "Energy Research Warehouse (ERW): U.S. Department of Energy, Alternative Fuels Data Center (AFDC), Vehicle Registration Counts by "
            f"State: light-duty vehicles registered by state and fuel type, {y0} to {y1} (session 2036)",
            "Shape: series (docs/datastandard.md v0). entity afdc_reg:<state> and afdc_reg:US (the page's own United States row); variable "
            "registrations_<fuel> (ev, phev, hev, biodiesel, e85, cng, propane, hydrogen, methanol, gasoline, diesel, unknown_fuel); unit count; "
            "ts_utc the year's first day, the count being the vehicles registered through the year's end; freq P1Y; node the page's column name.",
            f"{len(s)} rows. Counts are derived by the National Laboratory of the Rockies from Experian Information Solutions' data and rounded to "
            "the closest 100 vehicles (AFDC's words); fuel types come from VINs, not aftermarket conversions. Electric vehicles in the United "
            "States: " + ", ".join(f"{y} {v:,}" for y, v in us_ev.items()) + ". Nothing is filled.",
            f"Retrieved: {run_id} (UTC) by warehouse/connectors/afdc_registrations.py",
            f"Run log: warehouse/output/logs/{CONNECTOR}_{run_id}.log",
            f"Raw files: warehouse/raw/{CONNECTOR}/ (not in git)",
            f"Source: {SOURCE} U.S. Department of Energy, Alternative Fuels Data Center, Vehicle Registration Counts by State, {PAGE}",
            f"  access: {url_of(y0)} to {url_of(y1)} (the table each page prints; AFDC's API is not asked)",
            'License: public (DOE; cite "U.S. Department of Energy, Alternative Fuels Data Center, with data from Experian Information Solutions").',
        ]
        ip.write_snapshot(s, TABLE, head, log, cols)
        results.append(dict(table=TABLE, market="all", status="ok", detail=f"{len(s)} rows"))
        print(f"{TABLE}: {len(s)} rows, {y0} to {y1}; EVs " + ", ".join(f"{y} {v:,}" for y, v in us_ev.items()))
    except Exception:
        tb = ip.redact(traceback.format_exc())
        log(f"{TABLE} FAILED, no output file written:\n{tb}")
        print(f"{TABLE} FAILED, no output file written: {tb.strip().splitlines()[-1]}", file=sys.stderr)
        results.append(dict(table=TABLE, market="all", status="failed", detail=tb.strip().splitlines()[-1][:300]))
    if not args.out_dir:
        if results and results[0]["status"] == "ok":
            ip.update_sources([dict(source=SOURCE, publisher="U.S. Department of Energy (DOE)",
                                    report="Alternative Fuels Data Center (AFDC): Vehicle Registration Counts by State", report_url=PAGE,
                                    document_list=PAGE, license="public", tables=[TABLE])])
        ip.write_status(CONNECTOR, run_id, results)
    log.close()
    return 0 if all(r["status"] == "ok" for r in results) else 1


if __name__ == "__main__":
    sys.exit(main())

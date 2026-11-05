#!/usr/bin/env python3
"""The Federal Highway Administration's monthly motor fuel volumes reported by the states: the gallons of gasoline and of
special fuels (diesel, mostly, and alternative fuels) each state taxed a month, as FHWA publishes them on DOT's DataHub
(session 2035, chain 058: the road fuel demand that EIA's national product supplied tables hold only as a whole).

Energy Research Warehouse (ERW) connector. One series table from two DataHub (Socrata) datasets of FHWA's Office of
Highway Policy Information, the source data of its Monthly Motor Fuel Report, which FHWA's own site stopped publishing
after December 2023 (https://www.fhwa.dot.gov/policyinformation/motorfuelhwy_trustfund.cfm):

    https://data.transportation.gov/api/views/5qxh-t94v/rows.csv?accessType=DOWNLOAD   Monthly Motor Fuel - Gasoline
                                                                                     Volumes Distributed
    https://data.transportation.gov/api/views/5n49-mh85/rows.csv?accessType=DOWNLOAD   Monthly Special Fuel Volumes
                                                                                     Distributed
    (columns STATE, YEAR, MONTH, VOL GASOLINE or VOL SPEC FUEL, DATA TYPE, DATE MODIFIED)

    fhwa_motor_fuel_monthly   entity fhwa_mf:<state code>; variables gasoline_volume and special_fuel_volume, unit gal
                              (Decision 59: the gallons the state reports, taxed); ts_utc the month's first day; freq
                              P1M; geo US-<state> (the 50 states, DC and Puerto Rico); x_data_type the dataset's DATA TYPE
                              (Actual, Estimate, Gas Holiday: Georgia's months its gasoline tax was suspended, whose
                              volumes are those still taxed); x_date_modified as published

Two kinds of row are not written, and are counted in the header: a "Not Published" row (its volume is a 0 that measures
nothing), and every row of a month in which all 52 places read 0 (the datasets carry the rest of the current year so,
before the states report). Nothing is filled. A dataset without its columns, a place or month not known, a volume not a
number or a state and month given twice stops the run.

    python warehouse/connectors/fhwa_motor_fuel.py [--offline] [--out-dir DIR]

Ceiling: two requests, saved in warehouse/raw/fhwa_motor_fuel/ and reused offline, 1.5 seconds apart (data.transportation.gov's
robots file asks one second between requests and disallows only its search and browse paths). License: public (each
dataset's own metadata: "Public Domain"; FHWA, Office of Highway Policy Information, attribution).
"""

import argparse
import datetime as dt
import io
import os
import sys
import traceback

import pandas as pd

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import iso_prices as ip  # noqa: E402

CONNECTOR = "fhwa_motor_fuel"
SOURCE = "fhwa:monthly_motor_fuel"
HOST = "https://data.transportation.gov"
STORY = HOST + "/stories/s/nrec-wf7k"
SETS = {"gasoline_volume": ("5qxh-t94v", "VOL GASOLINE"), "special_fuel_volume": ("5n49-mh85", "VOL SPEC FUEL")}
TABLE = "fhwa_motor_fuel_monthly"
UA = {"User-Agent": "Mozilla/5.0 (compatible; ERW-connector/0.1; +https://github.com/SamuelEnrique/erw)"}
MONTHS = {m: i for i, m in enumerate(["January", "February", "March", "April", "May", "June", "July", "August", "September", "October",
                                      "November", "December"], start=1)}
TYPES = {"Actual", "Estimate", "Gas Holiday", "Not Published"}
X_COLS = ["x_data_type", "x_date_modified"]
PLACES = {"Alabama": "AL", "Alaska": "AK", "Arizona": "AZ", "Arkansas": "AR", "California": "CA", "Colorado": "CO", "Connecticut": "CT",
          "Delaware": "DE", "District of Columbia": "DC", "Florida": "FL", "Georgia": "GA", "Hawaii": "HI", "Idaho": "ID", "Illinois": "IL",
          "Indiana": "IN", "Iowa": "IA", "Kansas": "KS", "Kentucky": "KY", "Louisiana": "LA", "Maine": "ME", "Maryland": "MD",
          "Massachusetts": "MA", "Michigan": "MI", "Minnesota": "MN", "Mississippi": "MS", "Missouri": "MO", "Montana": "MT", "Nebraska": "NE",
          "Nevada": "NV", "New Hampshire": "NH", "New Jersey": "NJ", "New Mexico": "NM", "New York": "NY", "North Carolina": "NC",
          "North Dakota": "ND", "Ohio": "OH", "Oklahoma": "OK", "Oregon": "OR", "Pennsylvania": "PA", "Puerto Rico": "PR",
          "Rhode Island": "RI", "South Carolina": "SC", "South Dakota": "SD", "Tennessee": "TN", "Texas": "TX", "Utah": "UT", "Vermont": "VT",
          "Virginia": "VA", "Washington": "WA", "West Virginia": "WV", "Wisconsin": "WI", "Wyoming": "WY"}


def url_of(var):
    return f"{HOST}/api/views/{SETS[var][0]}/rows.csv?accessType=DOWNLOAD"


def read(content, var):
    d = pd.read_csv(io.BytesIO(content), dtype=str, keep_default_na=False)
    d.columns = [c.strip() for c in d.columns]
    need = ["STATE", "YEAR", "MONTH", SETS[var][1], "DATA TYPE", "DATE MODIFIED"]
    miss = [c for c in need if c not in d.columns]
    if miss:
        raise RuntimeError(f"{var}: no column {miss}; its columns are {list(d.columns)}")
    d = d[need].apply(lambda s: s.str.strip())
    bad = sorted(set(d.STATE) - set(PLACES))
    if bad:
        raise RuntimeError(f"{var}: a place not known: {bad[:5]}")
    bad = sorted(set(d.MONTH) - set(MONTHS))
    if bad or (~d.YEAR.str.fullmatch(r"\d{4}")).any():
        raise RuntimeError(f"{var}: a month or year not known: {bad[:5]}")
    bad = sorted(set(d["DATA TYPE"]) - TYPES)
    if bad:
        raise RuntimeError(f"{var}: a data type not known: {bad}")
    v = pd.to_numeric(d[SETS[var][1]].str.replace(",", "", regex=False), errors="coerce")
    if v.isna().any():
        raise RuntimeError(f"{var}: a volume not a number: {d.loc[v.isna(), SETS[var][1]].head(3).tolist()}")
    d["v"] = v
    d["ts"] = d.YEAR + "-" + d.MONTH.map(MONTHS).map("{:02d}".format) + "-01T00:00:00Z"
    if d.duplicated(["STATE", "ts"]).any():
        raise RuntimeError(f"{var}: a state and month given twice")
    return d


def rows(d, var, base):
    """(the series rows, rows left out as Not Published, rows left out in all-zero months, those months)."""
    unpublished = d["DATA TYPE"] == "Not Published"
    zero_month = d.groupby("ts").v.transform(lambda s: (s == 0).all())
    keep = ~unpublished & ~zero_month
    k = d[keep]
    s = pd.DataFrame({"entity": "fhwa_mf:" + k.STATE.map(PLACES), "variable": var, "ts_utc": k.ts,
                      "value": k.v.map(lambda x: f"{x:.0f}" if float(x).is_integer() else f"{x}"), "unit": "gal", "freq": "P1M",
                      "geo": "US-" + k.STATE.map(PLACES), "market": "", "node": k.STATE, **base,
                      "x_data_type": k["DATA TYPE"], "x_date_modified": k["DATE MODIFIED"]})
    return s, int(unpublished.sum()), int((zero_month & ~unpublished).sum()), sorted(d.ts[zero_month].str[:7].unique())


def main(argv=None):
    ap = argparse.ArgumentParser(description="FHWA's monthly gasoline and special fuel volumes reported by the states")
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
        parts, notes = [], []
        for var in SETS:
            content, rec = ip.fetch_raw(CONNECTOR, url_of(var), log, offline=args.offline, fresh=not args.offline, headers=UA, timeout=120,
                                        pause=1.5)
            base = dict(source=SOURCE, source_url=url_of(var), retrieved_at=rec.get("retrieved_at") or "", vintage=ip.vintage_of(rec))
            s, unpub, zero, months = rows(read(content, var), var, base)
            parts.append(s)
            notes.append(f"{var}: {len(s)} rows; {unpub} Not Published rows and {zero} rows of all-zero months ({months[0] if months else 'none'}"
                         f"{' to ' + months[-1] if len(months) > 1 else ''}) not written")
        s = pd.concat(parts, ignore_index=True)
        cols = ip.SERIES_COLS + X_COLS
        s = s[cols].sort_values(["entity", "variable", "ts_utc"]).reset_index(drop=True)
        head = [
            "Energy Research Warehouse (ERW): Federal Highway Administration (FHWA), Office of Highway Policy Information, Monthly Motor Fuel: the "
            "gallons of gasoline and of special fuels each state reports taxed a month, from DOT's DataHub (session 2035)",
            "Shape: series (docs/datastandard.md v0). entity fhwa_mf:<state>; variables gasoline_volume and special_fuel_volume (unit gal, Decision "
            "59: the gallons the state reports, taxed, as FHWA compiles them); ts_utc the month's first day; freq P1M; geo US-<state> (50 states, "
            "DC, Puerto Rico); node the place as FHWA names it; x_data_type Actual, Estimate or Gas Holiday (Georgia's months its gasoline tax was "
            "suspended: the volumes still taxed); x_date_modified as published.",
            f"{len(s)} rows, {s.ts_utc.min()[:7]} to {s.ts_utc.max()[:7]}. " + "; ".join(notes) + ". Nothing is filled.",
            f"Retrieved: {run_id} (UTC) by warehouse/connectors/fhwa_motor_fuel.py",
            f"Run log: warehouse/output/logs/{CONNECTOR}_{run_id}.log",
            f"Raw files: warehouse/raw/{CONNECTOR}/ (not in git)",
            f"Source: {SOURCE} FHWA, Monthly Motor Fuel Report source data, DOT DataHub, {STORY}",
            "  access: " + "; ".join(f"{url_of(v)} ({SETS[v][1]})" for v in SETS),
            'License: public (each dataset\'s metadata: "Public Domain"; cite "FHWA, Office of Highway Policy Information").',
        ]
        ip.write_snapshot(s, TABLE, head, log, cols)
        results.append(dict(table=TABLE, market="all", status="ok", detail=f"{len(s)} rows"))
        print(f"{TABLE}: {len(s)} rows, {s.ts_utc.min()[:7]} to {s.ts_utc.max()[:7]}; " + "; ".join(notes))
    except Exception:
        tb = ip.redact(traceback.format_exc())
        log(f"{TABLE} FAILED, no output file written:\n{tb}")
        print(f"{TABLE} FAILED, no output file written: {tb.strip().splitlines()[-1]}", file=sys.stderr)
        results.append(dict(table=TABLE, market="all", status="failed", detail=tb.strip().splitlines()[-1][:300]))
    if not args.out_dir:
        if results and results[0]["status"] == "ok":
            ip.update_sources([dict(source=SOURCE, publisher="U.S. Department of Transportation, Federal Highway Administration (FHWA)",
                                    report="Monthly Motor Fuel: Gasoline Volumes Distributed; Special Fuel Volumes Distributed (DOT DataHub)",
                                    report_url=STORY, document_list=HOST + "/api/views/", license="public", tables=[TABLE])])
        ip.write_status(CONNECTOR, run_id, results)
    log.close()
    return 0 if all(r["status"] == "ok" for r in results) else 1


if __name__ == "__main__":
    sys.exit(main())

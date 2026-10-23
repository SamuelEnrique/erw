#!/usr/bin/env python3
"""NOAA's nClimDiv statewide monthly climate: each of the 48 contiguous states' (and the contiguous nation's) monthly
average temperature and precipitation, with the 1901 to 2000 mean NCEI publishes for that state and calendar month
(session 2045, chain 059: the climate that moves demand; the data behind NCEI's Climate at a Glance).

Energy Research Warehouse (ERW) connector. One series table, warehouse/output/noaa_climdiv_state_monthly.csv, from four
files of NCEI's nClimDiv directory (https://www.ncei.noaa.gov/pub/data/cirs/climdiv/), named by their processing date:

    climdiv-tmpcst-v1.0.0-<YYYYMMDD>         statewide monthly average temperature, deg F, 1895 to the latest month
    climdiv-pcpnst-v1.0.0-<YYYYMMDD>         statewide monthly precipitation, inches
    climdiv-norm-tmpcst-v1.0.0-<YYYYMMDD>    the means of special periods; period code 0031 is 1901 to 2000
    climdiv-norm-pcpnst-v1.0.0-<YYYYMMDD>

The record format is state-readme.txt's and normals-readme.txt's: a 3-digit state code (NCEI's own numbering, 001
Alabama to 048 Wyoming, 110 the contiguous United States), a division digit (0, the state's area average), a 2-digit
element code (01 precipitation, 02 average temperature), a 4-digit year (in the normals files, the period's code), then
twelve 7-character monthly values. A month marked missing (-99.90 for temperature, -9.99 for precipitation; NCEI
marks the months the latest year has not reached) is an omitted row in whatever year it falls; any other value below
those marks stops the run.

    entity      noaa_climdiv:<state code>, e.g. noaa_climdiv:041 (Texas); node the state's name; geo its ISO 3166-2 code
    variable    temp_avg (degF) or precip (in), a calendar month: ts_utc the month's first day, freq P1M
    x_mean_1901_2000   the 1901 to 2000 mean of that state, element and calendar month, from the normals file

Values as NCEI publishes them; nothing is filled. A line not 94 characters, an element or division not the file's, or a missing 1901 to 2000
mean stops the run; a state code outside the map (Hawaii, Alaska, the regions) is not taken.

    python warehouse/connectors/noaa_climdiv_states.py [--offline] [--first-year 2000] [--out-dir DIR]

Ceiling: five requests (the directory listing, fresh each run, and the four files, reused from
warehouse/raw/noaa_climdiv_states/ when a file of that name was saved). NCEI's robots file disallows /data* and /orders*;
/pub/data/cirs/ is not among them. License: NOAA's data, a U.S. Government work in the public domain (NOAA NCEI, read 9:
its one restriction is on ISD's non-U.S. stations).
"""

import argparse
import datetime as dt
import os
import re
import sys
import traceback

import pandas as pd

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import iso_prices as ip  # noqa: E402

NAME = "noaa_climdiv_state_monthly"
CONNECTOR = "noaa_climdiv_states"
SOURCE = "noaa:climdiv"
DIR = "https://www.ncei.noaa.gov/pub/data/cirs/climdiv/"
UA = {"User-Agent": "Mozilla/5.0 (compatible; ERW-connector/0.1; +https://github.com/SamuelEnrique/erw)"}
COLS = ["entity", "variable", "ts_utc", "value", "unit", "freq", "geo", "market", "node", "source", "source_url",
        "retrieved_at", "vintage", "x_mean_1901_2000"]
ELEMENTS = {"tmpc": ("02", "temp_avg", "degF", "-99.90"), "pcpn": ("01", "precip", "in", "-9.99")}
MEAN_PERIOD = "0031"  # normals-readme.txt: 0031 means 1901-2000
STATES = {1: ("Alabama", "AL"), 2: ("Arizona", "AZ"), 3: ("Arkansas", "AR"), 4: ("California", "CA"), 5: ("Colorado", "CO"),
          6: ("Connecticut", "CT"), 7: ("Delaware", "DE"), 8: ("Florida", "FL"), 9: ("Georgia", "GA"), 10: ("Idaho", "ID"),
          11: ("Illinois", "IL"), 12: ("Indiana", "IN"), 13: ("Iowa", "IA"), 14: ("Kansas", "KS"), 15: ("Kentucky", "KY"),
          16: ("Louisiana", "LA"), 17: ("Maine", "ME"), 18: ("Maryland", "MD"), 19: ("Massachusetts", "MA"),
          20: ("Michigan", "MI"), 21: ("Minnesota", "MN"), 22: ("Mississippi", "MS"), 23: ("Missouri", "MO"),
          24: ("Montana", "MT"), 25: ("Nebraska", "NE"), 26: ("Nevada", "NV"), 27: ("New Hampshire", "NH"),
          28: ("New Jersey", "NJ"), 29: ("New Mexico", "NM"), 30: ("New York", "NY"), 31: ("North Carolina", "NC"),
          32: ("North Dakota", "ND"), 33: ("Ohio", "OH"), 34: ("Oklahoma", "OK"), 35: ("Oregon", "OR"),
          36: ("Pennsylvania", "PA"), 37: ("Rhode Island", "RI"), 38: ("South Carolina", "SC"), 39: ("South Dakota", "SD"),
          40: ("Tennessee", "TN"), 41: ("Texas", "TX"), 42: ("Utah", "UT"), 43: ("Vermont", "VT"), 44: ("Virginia", "VA"),
          45: ("Washington", "WA"), 46: ("West Virginia", "WV"), 47: ("Wisconsin", "WI"), 48: ("Wyoming", "WY"),
          110: ("Contiguous United States", "")}


def files(html):
    """The newest file of each of the four names the listing gives: {key: name}."""
    out = {}
    for kind in ("tmpc", "pcpn"):
        for norm in ("", "norm-"):
            names = sorted(set(re.findall(rf'href="(climdiv-{norm}{kind}st-v[\d.]+-(\d{{8}}))"', html)), key=lambda x: x[1])
            if not names:
                raise RuntimeError(f"the listing names no climdiv-{norm}{kind}st file")
            out[(kind, bool(norm))] = names[-1][0]
    return out


def records(content, element, label):
    """{(state, year or period): [12 values as text]} of one file's lines of the element, states and nation only."""
    out = {}
    for line in content.decode("ascii", errors="strict").splitlines():
        if not line.strip():
            continue
        line = line.rstrip()
        if len(line) != 94:
            raise RuntimeError(f"{label}: a line not 94 characters: {line[:40]!r}")
        state, div, el, year = int(line[0:3]), line[3], line[4:6], line[6:10]
        if el != element:
            raise RuntimeError(f"{label}: element {el}, not {element}")
        if div != "0":
            raise RuntimeError(f"{label}: division {div}, not the state's area average")
        if state not in STATES:
            if 1 <= state <= 110:
                continue  # Hawaii, Alaska and the regions: not taken
            continue
        out[(state, year)] = [line[10 + 7 * m: 17 + 7 * m].strip() for m in range(12)]
    return out


def build(data, norms, first_year, urls, retrieved, vintages):
    rows = []
    for kind, (element, variable, unit, missing) in ELEMENTS.items():
        means = {s: v for (s, p), v in norms[kind].items() if p == MEAN_PERIOD}
        for (state, year), values in data[kind].items():
            if int(year) < first_year:
                continue
            if state not in means:
                raise RuntimeError(f"no 1901-2000 mean for state {state:03d}, {variable}")
            name, code = STATES[state]
            for m, v in enumerate(values):
                if v == missing:
                    continue
                if float(v) <= -9.99 and kind == "pcpn" or float(v) <= -99.9 and kind == "tmpc":
                    raise RuntimeError(f"a missing value not in the latest months: {state:03d} {year}-{m + 1:02d} {v}")
                rows.append({"entity": f"noaa_climdiv:{state:03d}", "variable": variable,
                             "ts_utc": f"{year}-{m + 1:02d}-01T00:00:00Z", "value": float(v), "unit": unit, "freq": "P1M",
                             "geo": f"US-{code}" if code else "US", "market": "", "node": name, "source": SOURCE,
                             "source_url": urls[kind], "retrieved_at": retrieved[kind], "vintage": vintages[kind],
                             "x_mean_1901_2000": float(means[state][m])})
    t = pd.DataFrame(rows, columns=COLS)
    # the latest year's missing months are omitted, never filled; a month present in one element and not the other is kept
    return t.sort_values(["entity", "variable", "ts_utc"]).reset_index(drop=True)


def main(argv=None):
    ap = argparse.ArgumentParser(description="NOAA nClimDiv statewide monthly temperature and precipitation")
    ap.add_argument("--offline", action="store_true", help="the saved files only, no request")
    ap.add_argument("--first-year", type=int, default=2000)
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
        listing, _ = ip.fetch_raw(CONNECTOR, DIR, log, offline=args.offline, fresh=not args.offline, headers=UA, timeout=120)
        names = files(listing.decode("utf-8", errors="replace"))
        data, norms, urls, retrieved, vintages = {}, {}, {}, {}, {}
        for kind, (element, *_rest) in ELEMENTS.items():
            for is_norm in (False, True):
                url = DIR + names[(kind, is_norm)]
                content, rec = ip.fetch_raw(CONNECTOR, url, log, offline=args.offline, headers=UA, timeout=300)
                got = records(content, element, names[(kind, is_norm)])
                if is_norm:
                    norms[kind] = got
                else:
                    data[kind], urls[kind] = got, url
                    retrieved[kind] = rec.get("retrieved_at") or ""
                    vintages[kind] = names[(kind, False)][-8:-4] + "-" + names[(kind, False)][-4:-2] + "-" + names[(kind, False)][-2:] + "T00:00:00Z"
                log(f"  {names[(kind, is_norm)]}: {len(got)} state lines")
        t = build(data, norms, args.first_year, urls, retrieved, vintages)
        last = t.ts_utc.max()[:7]
        header = [
            f"Energy Research Warehouse (ERW): NOAA NCEI nClimDiv, statewide monthly average temperature and precipitation, the 48 contiguous states and the nation, {args.first_year} to {last}, with the 1901-2000 mean (session 2045)",
            "Shape: series (docs/datastandard.md v0). entity noaa_climdiv:<NCEI state code> (001 Alabama to 048 Wyoming, 110 the contiguous U.S.); variable temp_avg "
            "(degF) or precip (in, Decision 60); ts_utc the month's first day, freq P1M; x_mean_1901_2000 NCEI's own 1901-2000 mean of the state's calendar month "
            "(the normals file's period 0031).",
            f"{len(t)} rows: " + "; ".join(f"{v} {n}" for v, n in t.groupby("variable").size().items()) + ". The latest year's months not yet processed are omitted. "
            "Values as NCEI publishes them; nothing is filled.",
            f"Retrieved: {run_id} (UTC) by warehouse/connectors/noaa_climdiv_states.py; the files: " + ", ".join(sorted(names.values())),
            f"Run log: warehouse/output/logs/{CONNECTOR}_{run_id}.log",
            f"Raw files: warehouse/raw/{CONNECTOR}/ (not in git)",
            f"Source: {SOURCE} NOAA National Centers for Environmental Information, nClimDiv (Vose et al. 2014), statewide files, {DIR}",
            f"  access: {DIR}climdiv-tmpcst-v1.0.0-<YYYYMMDD> and climdiv-pcpnst, climdiv-norm-tmpcst and climdiv-norm-pcpnst of the same date",
            "License: NOAA's data, a U.S. Government work in the public domain.",
        ]
        ip.write_csv(t, NAME, header, log, cols=COLS)
        if not args.out_dir:
            ip.update_sources([dict(source=SOURCE, publisher="NOAA National Centers for Environmental Information (NCEI)",
                                    report="nClimDiv statewide monthly temperature and precipitation, with the 1901-2000 means",
                                    report_url=DIR, document_list=DIR, license="public", tables=[NAME])])
        results.append(dict(table=NAME, market="all", status="ok", detail=f"{len(t)} rows to {last}"))
        print(f"{NAME}: {len(t)} rows, {t.entity.nunique()} areas, to {last}")
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

#!/usr/bin/env python3
"""The U.S. Geological Survey's daily mean streamflow at gauges below large hydropower plants: the rivers that are the
hydro fleet's fuel (session 2113, chain 069).

Energy Research Warehouse (ERW) connector. One series table from the USGS's daily values service (NWIS), one request a
gauge, tab-delimited (rdb), parameter 00060 (discharge) and statistic 00003 (mean), from 2015:

    https://waterservices.usgs.gov/nwis/dv/?format=rdb&sites=<site>&parameterCd=00060&statCd=00003&startDT=2015-01-01

    usgs_streamflow_daily   entity usgs_gauge:<site number>; variable discharge (ft3/s: the day's mean discharge in cubic
               feet a second, as the USGS gives it); ts_utc the local day's start written as 00:00 UTC (the USGS's daily
               values are local calendar days); freq P1D; geo US-<state>; node the gauge's name as the USGS gives it;
               x_site; x_plant the hydropower plant above the gauge; x_qual the USGS's qualification codes (A approved,
               P provisional, e estimated, R revised, joined by ":" when several)

Each answer must name the one gauge asked in its header ("USGS <site> <name>"), hold the columns agency_cd, site_no,
datetime and one value column of 00060_00003 with its _cd column, and give each day once, or the run stops. A day the
USGS writes as a code instead of a number (Ice, Eqp, Ssn, Dis, ***, and the like) has no row and is counted in the
header. Provisional values are kept with their P code, as the USGS releases them, and they can be revised. Nothing is
filled.

    python warehouse/connectors/usgs_streamflow.py [--offline] [--out-dir DIR]

Ceiling: one request a gauge, eight a run, two seconds apart (saved in warehouse/raw/usgs_streamflow/ and reused
offline; asked again unless --offline, since each gauge's address stays as its days are added). waterservices.usgs.gov has no robots file (HTTP 404). License: may be public (USGS, read 87: USGS-authored or
produced data and information are in the public domain); cite the U.S. Geological Survey.
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

CONNECTOR = "usgs_streamflow"
SOURCE = "usgs:nwis_daily_values"
HOST = "waterservices.usgs.gov"
BASE = "https://waterservices.usgs.gov/nwis/dv/"
START = "2015-01-01"
TABLE = "usgs_streamflow_daily"
UA = {"User-Agent": "Mozilla/5.0 (compatible; ERW-connector/0.1; +https://github.com/SamuelEnrique/erw)"}
X_COLS = ["x_site", "x_plant", "x_qual"]
# site: (state, the hydropower plant above the gauge)
GAUGES = {"14105700": ("OR", "The Dalles"), "12436500": ("WA", "Grand Coulee"), "09421500": ("AZ", "Hoover"),
          "09380000": ("AZ", "Glen Canyon"), "06342500": ("ND", "Garrison"), "13290450": ("OR", "Hells Canyon"),
          "11370500": ("CA", "Shasta"), "11407000": ("CA", "Oroville")}


def url_of(site):
    return f"{BASE}?format=rdb&sites={site}&parameterCd=00060&statCd=00003&startDT={START}"


def parse(text, site, base, codes):
    st, plant = GAUGES[site]
    names = re.findall(r"^#\s+USGS (\d+) (.+?)\s*$", text, re.M)
    if [n for n, _ in names] != [site]:
        raise RuntimeError(f"{site}: the answer names {[n for n, _ in names]}, not the one gauge asked")
    name = names[0][1]
    lines = [l for l in text.splitlines() if l and not l.startswith("#")]
    if len(lines) < 3:
        raise RuntimeError(f"{site}: no day in the answer")
    head = lines[0].split("\t")
    vals = [c for c in head if c.endswith("_00060_00003")]
    if head[:3] != ["agency_cd", "site_no", "datetime"] or len(vals) != 1 or vals[0] + "_cd" not in head:
        raise RuntimeError(f"{site}: the columns are not as read: {head}")
    iv, ic = head.index(vals[0]), head.index(vals[0] + "_cd")
    out, seen = [], set()
    for l in lines[2:]:  # the second line holds the columns' widths
        f = l.split("\t")
        if len(f) != len(head):
            raise RuntimeError(f"{site}: a line of {len(f)} fields, not {len(head)}: {l[:80]!r}")
        if f[1] != site:
            raise RuntimeError(f"{site}: a line of another gauge: {f[1]}")
        d = f[2]
        if not re.fullmatch(r"\d{4}-\d{2}-\d{2}", d) or d in seen:
            raise RuntimeError(f"{site}: a day that does not read or is given twice: {d!r}")
        seen.add(d)
        x = f[iv].strip()
        try:
            v = float(x)
        except ValueError:
            codes[x or "(empty)"] = codes.get(x or "(empty)", 0) + 1
            continue
        out.append(dict(base, entity=f"usgs_gauge:{site}", variable="discharge", ts_utc=f"{d}T00:00:00Z", value=v, unit="ft3/s",
                        freq="P1D", geo=f"US-{st}", market="", node=name, x_site=site, x_plant=plant, x_qual=f[ic].strip()))
    if not out:
        raise RuntimeError(f"{site}: no day with a value")
    return out, name


def main(argv=None):
    ap = argparse.ArgumentParser(description="The USGS's daily mean streamflow at gauges below large hydropower plants")
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
        rows, codes, latest, gauges = [], {}, "", []
        for site in GAUGES:
            content, rec = ip.fetch_raw(CONNECTOR, url_of(site), log, offline=args.offline, fresh=not args.offline, headers=UA, timeout=120, pause=2)
            base = dict(source=SOURCE, source_url=url_of(site), retrieved_at=rec.get("retrieved_at") or "", vintage=ip.vintage_of(rec))
            got, name = parse(content.decode("utf-8"), site, base, codes)
            log(f"  {site} {name}: {len(got)} days")
            rows += got
            gauges.append(f"{site} {name} (below {GAUGES[site][1]})")
            latest = max(latest, base["retrieved_at"])
        s = pd.DataFrame(rows)
        if s.duplicated(["entity", "variable", "ts_utc"]).any():
            raise RuntimeError("an (entity, variable, ts_utc) given twice")
        cols = ip.SERIES_COLS + X_COLS
        s = s[cols].sort_values(["entity", "variable", "ts_utc"]).reset_index(drop=True)
        coded = ", ".join(f"{k} {n}" for k, n in sorted(codes.items()))
        prov = int(s.x_qual.str.contains("P").sum())
        head = [
            f"Energy Research Warehouse (ERW): U.S. Geological Survey, NWIS daily values, the daily mean discharge at {len(GAUGES)} gauges below "
            f"large hydropower plants, {s.ts_utc.min()[:10]} to {s.ts_utc.max()[:10]} (session 2113)",
            "Shape: series (docs/datastandard.md v0). entity usgs_gauge:<site>; variable discharge (ft3/s, cubic feet a second, the day's mean); "
            "freq P1D; ts_utc the local day written as 00:00 UTC; geo US-<state>; node the gauge's name; x_site; x_plant the plant above the "
            "gauge; x_qual the USGS's codes (A approved, P provisional, e estimated, R revised).",
            f"Gauges: {'; '.join(gauges)}. Days the USGS writes as a code have no row: {coded or 'none'}. {prov:,} rows are provisional (P), "
            "released by the USGS on the condition that it is not liable for their use, and subject to revision. Nothing is filled.",
            f"Retrieved: {run_id} (UTC) by warehouse/connectors/usgs_streamflow.py; the latest answer retrieved {latest}",
            f"Run log: warehouse/output/logs/{CONNECTOR}_{run_id}.log",
            f"Raw files: warehouse/raw/{CONNECTOR}/ (not in git)",
            f"Source: {SOURCE} U.S. Geological Survey, National Water Information System, daily values service, {BASE}",
            f"  access: {BASE}?format=rdb&sites=<site>&parameterCd=00060&statCd=00003&startDT={START}",
            "License: may be public (USGS: USGS-authored or produced data and information are in the public domain; see license_verdicts.csv). "
            "Cite the U.S. Geological Survey.",
        ]
        ip.write_snapshot(s, TABLE, head, log, cols)
        results.append(dict(table=TABLE, market="all", status="ok", detail=f"{len(s)} rows"))
        print(f"{TABLE}: {len(s)} rows, {s.entity.nunique()} gauges; coded days {coded or 'none'}; provisional {prov}")
    except Exception:
        tb = ip.redact(traceback.format_exc())
        log(f"{TABLE} FAILED, no output file written:\n{tb}")
        print(f"{TABLE} FAILED, no output file written: {tb.strip().splitlines()[-1]}", file=sys.stderr)
        results.append(dict(table=TABLE, market="all", status="failed", detail=tb.strip().splitlines()[-1][:300]))
    if not args.out_dir:
        if results and results[0]["status"] == "ok":
            ip.update_sources([dict(source=SOURCE, publisher="U.S. Geological Survey (USGS)",
                                    report="National Water Information System, daily values (discharge, daily mean)", report_url=BASE,
                                    document_list=BASE, license="public", tables=[TABLE])])
        ip.write_status(CONNECTOR, run_id, results)
    log.close()
    return 0 if all(r["status"] == "ok" for r in results) else 1


if __name__ == "__main__":
    sys.exit(main())

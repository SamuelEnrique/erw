#!/usr/bin/env python3
"""The U.S. Drought Monitor: the percent of each state's area in each drought category, a week, from 2015 (session 2058,
chain 066: the drought that takes hydropower and cooling water, which the ERW did not hold).

Energy Research Warehouse (ERW) connector. One series table from the Drought Monitor's data services, the 48 contiguous
states in each request, a few years a request:

    https://usdmdataservices.unl.edu/api/StateStatistics/GetDroughtSeverityStatisticsByAreaPercent?aoi=<FIPS,...>&startdate=M/D/YYYY&enddate=M/D/YYYY&statisticsType=1

    usdm_drought_state_weekly   entity usdm:<ST>; variables none, d0, d1, d2, d3, d4 (pct of the state's area, the
                                Monitor's traditional statistics: each category is cumulative, so d1 is the area in
                                moderate drought or worse and d0 the area abnormally dry or worse; none is the area in
                                none of them); ts_utc the week's map date (a Tuesday, 00:00 UTC); freq P1W; geo US-<ST>;
                                x_valid_start, x_valid_end the week the map is valid for

The answer must be CSV with the columns read below, every state asked must answer, and each figure must lie between 0
and 100, with none plus d0 equal to 100 within 0.02 and d0 >= d1 >= ... >= d4 (the traditional form), or the run
stops; a week two spans both give (the 2023 span's start returned the map of 27 December 2022) is kept once if the two
agree, and stops the run if they differ. Nothing is filled.

    python warehouse/connectors/usdm_drought.py [--offline] [--out-dir DIR] [--start 2015]

Ceiling: one request a span of up to four years (three for 2015 to 2026). droughtmonitor.unl.edu's robots file disallows
/data/, /nadmdata/, /webfiles/ and /DmData/DataArchive.aspx, none of which is asked; usdmdataservices.unl.edu has no
robots file (HTTP 404). License: not settled until the Monitor's Permission page is read (session 2061); it asks credit: "The U.S. Drought Monitor is jointly produced
by the National Drought Mitigation Center at the University of Nebraska-Lincoln, the United States Department of
Agriculture, and the National Oceanic and Atmospheric Administration. Map courtesy of NDMC." (the credit is the Monitor's;
its terms are read in session 2061's round).
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

CONNECTOR = "usdm_drought"
SOURCE = "usdm:state_statistics"
PAGE = "https://droughtmonitor.unl.edu/DmData/DataDownload/WebServiceInfo.aspx"
API = "https://usdmdataservices.unl.edu/api/StateStatistics/GetDroughtSeverityStatisticsByAreaPercent"
TABLE = "usdm_drought_state_weekly"
UA = {"User-Agent": "Mozilla/5.0 (compatible; ERW-connector/0.1; +https://github.com/SamuelEnrique/erw)", "Accept": "text/csv"}
# the 48 contiguous states, two-digit FIPS -> abbreviation
STATES = {"01": "AL", "04": "AZ", "05": "AR", "06": "CA", "08": "CO", "09": "CT", "10": "DE", "12": "FL", "13": "GA", "16": "ID", "17": "IL",
          "18": "IN", "19": "IA", "20": "KS", "21": "KY", "22": "LA", "23": "ME", "24": "MD", "25": "MA", "26": "MI", "27": "MN", "28": "MS",
          "29": "MO", "30": "MT", "31": "NE", "32": "NV", "33": "NH", "34": "NJ", "35": "NM", "36": "NY", "37": "NC", "38": "ND", "39": "OH",
          "40": "OK", "41": "OR", "42": "PA", "44": "RI", "45": "SC", "46": "SD", "47": "TN", "48": "TX", "49": "UT", "50": "VT", "51": "VA",
          "53": "WA", "54": "WV", "55": "WI", "56": "WY"}
CATS = ["None", "D0", "D1", "D2", "D3", "D4"]
NEED = ["MapDate", "StateAbbreviation"] + CATS + ["ValidStart", "ValidEnd"]
X_COLS = ["x_valid_start", "x_valid_end"]
CREDIT = ("The U.S. Drought Monitor is jointly produced by the National Drought Mitigation Center at the University of Nebraska-Lincoln, "
          "the United States Department of Agriculture, and the National Oceanic and Atmospheric Administration. Map courtesy of NDMC.")


def spans(start, end_year):
    out, y = [], start
    while y <= end_year:
        out.append((y, min(y + 3, end_year)))
        y += 4
    return out


def url_for(y0, y1, today):
    end = f"12/31/{y1}" if y1 < today.year else f"{today.month}/{today.day}/{today.year}"
    return f"{API}?aoi={'%2C'.join(STATES)}&startdate=1/1/{y0}&enddate={end}&statisticsType=1"


def parse(content, base):
    d = pd.read_csv(io.BytesIO(content), dtype=str, keep_default_na=False)
    missing = [c for c in NEED if c not in d.columns]
    if missing:
        raise RuntimeError(f"no column {missing}; the answer's columns are {list(d.columns)[:15]}")
    asked = set(STATES.values())
    got = set(d.StateAbbreviation)
    if got != asked:
        raise RuntimeError(f"states asked and answered differ: missing {sorted(asked - got)}, extra {sorted(got - asked)}")
    out = []
    for r in d.to_dict("records"):  # a column named None: tuples would rename it
        st = r["StateAbbreviation"]
        md = pd.to_datetime(r["MapDate"], format="%Y%m%d", errors="coerce")
        if pd.isna(md):
            raise RuntimeError(f"{st}: a map date that does not read: {r['MapDate']!r}")
        try:
            v = [float(r[c]) for c in CATS]
        except ValueError:
            raise RuntimeError(f"{st} {r['MapDate']}: a figure not a number: {[r[c] for c in CATS]}")
        if any(x < 0 or x > 100 for x in v) or abs(v[0] + v[1] - 100) > 0.02 or any(v[i] < v[i + 1] - 1e-9 for i in range(1, 5)):
            raise RuntimeError(f"{st} {r['MapDate']}: figures not in the traditional form: {v}")
        for c, x in zip(CATS, v):
            out.append(dict(base, entity=f"usdm:{st}", variable=c.lower(), ts_utc=md.strftime("%Y-%m-%dT00:00:00Z"), value=x, unit="pct",
                            freq="P1W", geo=f"US-{st}", market="", node=st, x_valid_start=r["ValidStart"], x_valid_end=r["ValidEnd"]))
    return out


def main(argv=None):
    ap = argparse.ArgumentParser(description="The U.S. Drought Monitor's weekly percent of area in drought, by state")
    ap.add_argument("--offline", action="store_true", help="the saved answers only, no request")
    ap.add_argument("--out-dir", help="a trial: the table under this folder, not warehouse/output")
    ap.add_argument("--start", type=int, default=2015)
    args = ap.parse_args(argv)
    if args.out_dir:
        raw_dir = ip.RAW_DIR
        ip.set_out_dir(args.out_dir)
        ip.RAW_DIR = raw_dir
    os.makedirs(ip.LOG_DIR, exist_ok=True)
    now = dt.datetime.now(dt.timezone.utc)
    run_id = now.strftime("%Y%m%dT%H%M%SZ")
    log = ip.Log(os.path.join(ip.LOG_DIR, f"{CONNECTOR}_{run_id}.log"))
    ip.RAW.open(CONNECTOR, run_id)
    results = []
    try:
        # session 2066: the pause list first (CLAUDE.md), as boem_ogor.py asks it
        if ip.paused(CONNECTOR) or ip.paused_host("usdmdataservices.unl.edu"):
            raise RuntimeError("usdmdataservices.unl.edu is paused (warehouse/metadata/paused_sources.csv): no request made")
        rows, urls, latest = [], [], ""
        for y0, y1 in spans(args.start, now.year):
            url = url_for(y0, y1, now.date())
            # the current year's span grows each week: fetched again unless offline; an earlier span is kept
            content, rec = ip.fetch_raw(CONNECTOR, url, log, offline=args.offline, fresh=(y1 == now.year and not args.offline), headers=UA,
                                        timeout=300, pause=2)
            base = dict(source=SOURCE, source_url=url, retrieved_at=rec.get("retrieved_at") or "", vintage=ip.vintage_of(rec))
            got = parse(content, base)
            log(f"  {y0} to {y1}: {len(got)} rows")
            rows += got
            urls.append(url)
            latest = max(latest, base["retrieved_at"])
        s = pd.DataFrame(rows)
        # a span's start date can return the week before it (1/1/2023 gave the map of 27 December 2022; 1/1/2019 gave
        # 1 January 2019's): a week two spans give is kept once if the two agree, and stops the run if they differ
        key = ["entity", "variable", "ts_utc"]
        dup = s.duplicated(key, keep=False)
        if dup.any():
            spread = s[dup].groupby(key).value.agg(["min", "max"])
            if ((spread["max"] - spread["min"]) > 1e-9).any():
                raise RuntimeError(f"a state and map date given twice with different figures: {spread[spread['max'] > spread['min']].head(3)}")
            log(f"  {int(dup.sum()) // 2} rows given by two spans alike, kept once")
            s = s.drop_duplicates(key, keep="first")
        cols = ip.SERIES_COLS + X_COLS
        s = s[cols].sort_values(["entity", "variable", "ts_utc"]).reset_index(drop=True)
        weeks = s.ts_utc.nunique()
        head = [
            "Energy Research Warehouse (ERW): the U.S. Drought Monitor, the percent of each of the 48 contiguous states' area in each drought "
            f"category, a week, from {args.start} (session 2058)",
            "Shape: series (docs/datastandard.md v0). entity usdm:<ST>; variables none, d0, d1, d2, d3, d4 (pct of the state's area, the Monitor's "
            "traditional statistics: cumulative, d1 the area in moderate drought or worse); freq P1W; ts_utc the map date; geo US-<ST>; "
            "x_valid_start and x_valid_end the week the map is valid for.",
            f"48 states, {weeks} weeks, {s.ts_utc.min()[:10]} to {s.ts_utc.max()[:10]}. none plus d0 is 100 in every row. Nothing is filled.",
            f"Retrieved: {run_id} (UTC) by warehouse/connectors/usdm_drought.py; the latest answer retrieved {latest}",
            f"Run log: warehouse/output/logs/{CONNECTOR}_{run_id}.log",
            f"Raw files: warehouse/raw/{CONNECTOR}/ (not in git)",
            f"Source: {SOURCE} the U.S. Drought Monitor's data services (National Drought Mitigation Center, USDA, NOAA), {PAGE}",
            f"  access: {API}?aoi=<the 48 states' FIPS>&startdate=...&enddate=...&statisticsType=1 ({len(urls)} spans)",
            f"License: not settled (the Monitor's Permission page not yet read, session 2061); the Monitor asks credit: {CREDIT}",
        ]
        ip.write_snapshot(s, TABLE, head, log, cols)
        results.append(dict(table=TABLE, market="all", status="ok", detail=f"{len(s)} rows"))
        print(f"{TABLE}: {len(s)} rows, 48 states, {weeks} weeks, {s.ts_utc.min()[:10]} to {s.ts_utc.max()[:10]}")
    except Exception:
        tb = ip.redact(traceback.format_exc())
        log(f"{TABLE} FAILED, no output file written:\n{tb}")
        print(f"{TABLE} FAILED, no output file written: {tb.strip().splitlines()[-1]}", file=sys.stderr)
        results.append(dict(table=TABLE, market="all", status="failed", detail=tb.strip().splitlines()[-1][:300]))
    if not args.out_dir:
        if results and results[0]["status"] == "ok":
            ip.update_sources([dict(source=SOURCE, publisher="U.S. Drought Monitor (National Drought Mitigation Center, USDA, NOAA)",
                                    report="U.S. Drought Monitor, state statistics: percent of area by drought category, weekly", report_url=PAGE,
                                    document_list=PAGE, license="public", tables=[TABLE])])
        ip.write_status(CONNECTOR, run_id, results)
    log.close()
    return 0 if all(r["status"] == "ok" for r in results) else 1


if __name__ == "__main__":
    sys.exit(main())

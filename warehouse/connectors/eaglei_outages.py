#!/usr/bin/env python3
"""Oak Ridge National Laboratory's EAGLE-I customer outage records, a county's peak a day: the most customers its
utilities' public outage maps showed out at once, from the 15-minute records the EAGLE-I program collects (session
2029, chain 058: outages where customers live, beside DOE-417's reported events).

Energy Research Warehouse (ERW) connector. One series table from the dataset ORNL publishes for reuse on figshare,
"The Environment for Analysis of Geo-Located Energy Information's Recorded Electricity Outages 2014-2025" (version 4,
25 February 2026, CC BY 4.0, doi 10.6084/m9.figshare.24237376):

    https://api.figshare.com/v2/articles/24237376        the dataset's record and its files
    https://ndownloader.figshare.com/files/<id>          each year's eaglei_outages_<year>.csv (about 1.2 to 1.4 GB),
                                                         answered by a signed address on figshare's S3 bucket

    eaglei_county_outages_daily   entity eaglei:<county FIPS>; variable customers_out_peak (the largest customers_out
                                  of the county's 15-minute records that day); unit count; freq P1D; ts_utc the day of
                                  run_start_time as the files print it (UTC: the files' times run through the clock
                                  changes without a gap or a repeat, checked below); geo US-<state> from the FIPS
                                  code's state; x_county and x_state as the file names them; x_records the 15-minute
                                  records that day

The 15-minute files are too large to hold whole (2023 to 2025 alone are about 4 GB and some 60 million rows), so the
table holds a county's daily peak. A county and day with no record has no row: EAGLE-I's coverage of a state's
customers is partial and changes over the years (the dataset's coverage_history.csv), and no record is never read as no
outage. Nothing is filled. A file without the columns fips_code, county, state, run_start_time and customers_out (or
sum, the name the early years use), a FIPS code not of five digits, or a time not a time stops the run.

    python warehouse/connectors/eaglei_outages.py [--offline] [--out-dir DIR] [--years 2023 2024 2025]

Ceiling: one request a year (each followed through figshare's redirect), saved in warehouse/raw/eaglei_outages/ and
reused offline. figshare.com's robots file answered with an empty challenge page; api.figshare.com,
ndownloader.figshare.com and the S3 bucket have none. License: public (CC BY 4.0; cite "Brelsford, C., et al., The
Environment for Analysis of Geo-Located Energy Information's Recorded Electricity Outages 2014-2025, Oak Ridge National
Laboratory, figshare, doi 10.6084/m9.figshare.24237376").
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

CONNECTOR = "eaglei_outages"
SOURCE = "ornl:eaglei_outages"
ARTICLE = "https://api.figshare.com/v2/articles/24237376"
DOI = "https://doi.org/10.6084/m9.figshare.24237376.v4"
FILES = {2014: 42547717, 2015: 42547822, 2016: 42547825, 2017: 42547828, 2018: 42547879, 2019: 42547885, 2020: 42547894,
         2021: 42547891, 2022: 42547897, 2023: 44574907, 2024: 53581661, 2025: 62164877}  # the record's file ids, read 23 October 2026
TABLE = "eaglei_county_outages_daily"
UA = {"User-Agent": "Mozilla/5.0 (compatible; ERW-connector/0.1; +https://github.com/SamuelEnrique/erw)"}
YEARS = [2023, 2024, 2025]
X_COLS = ["x_county", "x_state", "x_records"]
# the state of a county's FIPS code (its first two digits), as the Census Bureau numbers the states
STATE_FIPS = {"01": "AL", "02": "AK", "04": "AZ", "05": "AR", "06": "CA", "08": "CO", "09": "CT", "10": "DE", "11": "DC", "12": "FL",
              "13": "GA", "15": "HI", "16": "ID", "17": "IL", "18": "IN", "19": "IA", "20": "KS", "21": "KY", "22": "LA", "23": "ME",
              "24": "MD", "25": "MA", "26": "MI", "27": "MN", "28": "MS", "29": "MO", "30": "MT", "31": "NE", "32": "NV", "33": "NH",
              "34": "NJ", "35": "NM", "36": "NY", "37": "NC", "38": "ND", "39": "OH", "40": "OK", "41": "OR", "42": "PA", "44": "RI",
              "45": "SC", "46": "SD", "47": "TN", "48": "TX", "49": "UT", "50": "VT", "51": "VA", "53": "WA", "54": "WV", "55": "WI",
              "56": "WY", "60": "AS", "66": "GU", "69": "MP", "72": "PR", "78": "VI"}
CHUNK = 1_000_000


def url_of(year):
    return f"https://ndownloader.figshare.com/files/{FILES[year]}"


def daily_peaks(content, year):
    """(rows, the day's distinct record times around each clock change): one row a county and day, in chunks."""
    head = content[:4096].decode("utf-8", errors="replace").splitlines()[0]
    names = [c.strip().strip('"') for c in head.split(",")]
    count = "customers_out" if "customers_out" in names else "sum" if "sum" in names else None
    need = ["fips_code", "county", "state", "run_start_time"]
    miss = [c for c in need if c not in names] + ([] if count else ["customers_out (or sum)"])
    if miss:
        raise RuntimeError(f"{year}: the file has no column {miss}; its columns are {names}")
    parts, times = [], {}
    reader = pd.read_csv(io.BytesIO(content), usecols=need + [count], dtype={"fips_code": str, "county": str, "state": str, "run_start_time": str},
                         chunksize=CHUNK)
    for ch in reader:
        t = pd.to_datetime(ch["run_start_time"], format="ISO8601", errors="coerce")
        if t.isna().any():
            raise RuntimeError(f"{year}: a time not a time: {ch.loc[t.isna(), 'run_start_time'].head(3).tolist()}")
        fips = ch["fips_code"].str.strip().str.zfill(5)
        if (~fips.str.fullmatch(r"\d{5}")).any():
            raise RuntimeError(f"{year}: a FIPS code not of five digits: {fips[~fips.str.fullmatch(r'\d{5}')].head(3).tolist()}")
        n = pd.to_numeric(ch[count], errors="coerce")
        if n.isna().any():
            raise RuntimeError(f"{year}: a {count} not a number: {ch.loc[n.isna(), count].head(3).tolist()}")
        d = pd.DataFrame({"fips": fips, "day": t.dt.strftime("%Y-%m-%d"), "n": n, "county": ch["county"], "state": ch["state"]})
        g = d.groupby(["fips", "day"], sort=False).agg(n=("n", "max"), records=("n", "size"), county=("county", "last"), state=("state", "last"))
        parts.append(g)
        for day in clock_days(year):
            sel = t.dt.strftime("%Y-%m-%d") == day
            if sel.any():
                times.setdefault(day, set()).update(t[sel].dt.strftime("%H:%M").unique())
    g = pd.concat(parts).groupby(level=[0, 1]).agg(n=("n", "max"), records=("records", "sum"), county=("county", "last"), state=("state", "last"))
    return g.reset_index(), {k: len(v) for k, v in times.items()}


def clock_days(year):
    """The two days a year the US clocks change (the second Sunday of March, the first Sunday of November)."""
    def nth_sunday(month, n):
        d = dt.date(year, month, 1)
        d += dt.timedelta(days=(6 - d.weekday()) % 7)
        return (d + dt.timedelta(weeks=n - 1)).isoformat()
    return [nth_sunday(3, 2), nth_sunday(11, 1)]


def to_series(g, base):
    geo = g["fips"].str[:2].map(STATE_FIPS)
    if geo.isna().any():
        raise RuntimeError(f"a FIPS state code not known: {sorted(g.loc[geo.isna(), 'fips'].str[:2].unique())[:5]}")
    return pd.DataFrame({
        "entity": "eaglei:" + g["fips"], "variable": "customers_out_peak", "ts_utc": g["day"] + "T00:00:00Z",
        "value": g["n"].round(0).astype("int64"), "unit": "count", "freq": "P1D", "geo": "US-" + geo, "market": "", "node": "",
        "source": base["source"], "source_url": base["source_url"], "retrieved_at": base["retrieved_at"], "vintage": base["vintage"],
        "x_county": g["county"].fillna(""), "x_state": g["state"].fillna(""), "x_records": g["records"].astype("int64")})


def main(argv=None):
    ap = argparse.ArgumentParser(description="ORNL's EAGLE-I customer outages, a county's peak a day")
    ap.add_argument("--offline", action="store_true", help="the saved files only, no request")
    ap.add_argument("--out-dir", help="a trial: the table under this folder, not warehouse/output")
    ap.add_argument("--years", type=int, nargs="+", default=YEARS)
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
        frames, clock, latest = [], {}, ""
        for y in sorted(args.years):
            content, rec = ip.fetch_raw(CONNECTOR, url_of(y), log, offline=args.offline, headers=UA, timeout=600, pause=1)
            base = dict(source=SOURCE, source_url=url_of(y), retrieved_at=rec.get("retrieved_at") or "", vintage=ip.vintage_of(rec))
            g, times = daily_peaks(content, y)
            del content
            frames.append(to_series(g, base))
            clock.update(times)
            latest = max(latest, str(base["retrieved_at"]))
            log(f"  {y}: {len(g)} county days; record times on the clock days: {times}")
        bad = {d: n for d, n in clock.items() if n != 96}
        if bad:
            raise RuntimeError(f"a clock day without 96 record times (the files' times would be local, not UTC): {bad}")
        s = pd.concat(frames, ignore_index=True)
        if s.duplicated(["entity", "variable", "ts_utc"]).any():
            raise RuntimeError("a county and day given twice")
        cols = ip.SERIES_COLS + X_COLS
        s = s[cols].sort_values(["entity", "ts_utc"]).reset_index(drop=True)
        years = ", ".join(str(y) for y in sorted(args.years))
        head = [
            "Energy Research Warehouse (ERW): Oak Ridge National Laboratory, EAGLE-I (Environment for Analysis of Geo-Located Energy Information), "
            f"Recorded Electricity Outages 2014-2025, a county's peak customers out a day, {years} (session 2029)",
            "Shape: series (docs/datastandard.md v0). entity eaglei:<county FIPS>; variable customers_out_peak, the largest customers_out of the county's "
            "15-minute records that day, as EAGLE-I read its utilities' public outage maps; unit count; freq P1D; ts_utc the day (UTC: the files' times "
            "run through each clock change with 96 a day); geo US-<state> from the FIPS code; x_county, x_state as the file names them; x_records the "
            "15-minute records that day.",
            f"{len(s)} county days, {s.entity.nunique()} counties, {s.ts_utc.min()[:10]} to {s.ts_utc.max()[:10]}. The 15-minute files (about 1.2 to "
            "1.4 GB a year) are too large to hold whole, so a day's peak is held. A county and day with no record has no row: EAGLE-I's coverage of "
            "each state's customers is partial and changes over the years, and no record is not no outage. Nothing is filled.",
            f"Retrieved: {run_id} (UTC) by warehouse/connectors/eaglei_outages.py; the latest file retrieved {latest}",
            f"Run log: warehouse/output/logs/{CONNECTOR}_{run_id}.log",
            f"Raw files: warehouse/raw/{CONNECTOR}/ (not in git)",
            f"Source: {SOURCE} Oak Ridge National Laboratory, EAGLE-I Recorded Electricity Outages 2014-2025 (figshare, version 4, 25 February 2026), {DOI}",
            f"  access: {ARTICLE}; " + "; ".join(f"{y} {url_of(y)} (eaglei_outages_{y}.csv)" for y in sorted(args.years)),
            "License: public (CC BY 4.0; cite \"Brelsford, C., et al., The Environment for Analysis of Geo-Located Energy Information's Recorded "
            "Electricity Outages 2014-2025, Oak Ridge National Laboratory, figshare, doi 10.6084/m9.figshare.24237376\").",
        ]
        ip.write_snapshot(s, TABLE, head, log, cols)
        results.append(dict(table=TABLE, market="all", status="ok", detail=f"{len(s)} rows"))
        print(f"{TABLE}: {len(s)} county days, {s.entity.nunique()} counties, {s.ts_utc.min()[:10]} to {s.ts_utc.max()[:10]}")
    except Exception:
        tb = ip.redact(traceback.format_exc())
        log(f"{TABLE} FAILED, no output file written:\n{tb}")
        print(f"{TABLE} FAILED, no output file written: {tb.strip().splitlines()[-1]}", file=sys.stderr)
        results.append(dict(table=TABLE, market="all", status="failed", detail=tb.strip().splitlines()[-1][:300]))
    if not args.out_dir:
        if results and results[0]["status"] == "ok":
            ip.update_sources([dict(source=SOURCE, publisher="Oak Ridge National Laboratory (ORNL), EAGLE-I",
                                    report="The Environment for Analysis of Geo-Located Energy Information's Recorded Electricity Outages 2014-2025 (figshare)",
                                    report_url=DOI, document_list=ARTICLE, license="public", tables=[TABLE])])
        ip.write_status(CONNECTOR, run_id, results)
    log.close()
    return 0 if all(r["status"] == "ok" for r in results) else 1


if __name__ == "__main__":
    sys.exit(main())

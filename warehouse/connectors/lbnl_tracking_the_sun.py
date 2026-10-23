#!/usr/bin/env python3
"""Berkeley Lab's Tracking the Sun: installed distributed solar systems, summarised by state, customer segment and year of
installation (session 2015, chain 057: rooftop and other distributed solar, which the ERW held only as EIA-861's
small-scale capacity by state).

Energy Research Warehouse (ERW) connector. One series table from the public data file Berkeley Lab publishes on the Open
Energy Data Initiative's data lake (OEDI submission 3, "Tracking the Sun"), one Parquet file a state:

    https://oedi-data-lake.s3.amazonaws.com/?list-type=2&prefix=tracking-the-sun/<EDITION>/     the listing
    https://oedi-data-lake.s3.amazonaws.com/tracking-the-sun/<EDITION>/state=<ST>/part-....snappy.parquet

The file holds one row a system (1.9 million in California's file alone; 118 MB as Parquet for the 2024 edition): too
large to hold whole, so the table is its summary, as its header says:

    lbnl_tracking_the_sun   entity tts:<st>_<segment> (the state's two letters, lowered, and the customer segment as the
                            file writes it, slugged; "-1", the file's missing value, is "unknown"); variables systems,
                            systems_priced, systems_battery (count), capacity_dc (MW, the sum of the systems' DC size,
                            the file's kW over 1,000) and price_median (USD/kW: the median of each priced system's total
                            installed price over its DC size, unscreened); ts_utc 1 January of the year of installation;
                            freq P1Y; geo US-<ST>; node the segment as written; x_segment the same

A system with no installation date, or one after its file's own Last-Modified day (one in the 2024 edition's Arizona
file reads 2038-03-29), has no year and no row (each state's count is in the run log, the total in the header); a size or price of zero or less (the file writes -1 for missing) is missing: such a system counts in systems,
not in capacity_dc or the price. A system is priced when both its price and its size are above zero. A battery is a
battery_rated_capacity_kwh above zero. The price is not Berkeley Lab's: its report screens outliers and third-party-owned
systems' appraised values, and this table does not. A file whose columns lack those read, a listing that is truncated or
names a state twice, or an (entity, variable, ts_utc) given twice stops the run; nothing is filled.

    python warehouse/connectors/lbnl_tracking_the_sun.py [--offline] [--out-dir DIR] [--edition 2024]
                                                         [--fetch-only --states AR AZ ...]

Ceiling: one request for the listing and one a state (28 for the 2024 edition). Sessions 2015 and 2020 fetched them
under their own ceilings (8 and 19 files: --fetch-only --states), and the write reads the saved files only. The data
lake's host has no robots file (HTTP 404, NoSuchKey); data.openei.org has none either (HTTP 404). License: CC BY 4.0,
as the OEDI submission states ("license": https://creativecommons.org/licenses/by/4.0/); cite Berkeley Lab.
"""

import argparse
import datetime as dt
import io
import os
import re
import sys
import traceback

import pandas as pd
import pyarrow.parquet as pq

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import iso_prices as ip  # noqa: E402

CONNECTOR = "lbnl_tracking_the_sun"
SOURCE = "lbnl:tracking_the_sun"
PAGE = "https://data.openei.org/submissions/3"
LAKE = "https://oedi-data-lake.s3.amazonaws.com/"
TABLE = "lbnl_tracking_the_sun"
UA = {"User-Agent": "Mozilla/5.0 (compatible; ERW-connector/0.1; +https://github.com/SamuelEnrique/erw)"}
EDITION = "2024"
COLS = ["installation_date", "pv_system_size_dc", "total_installed_price", "customer_segment", "battery_rated_capacity_kwh"]
UNITS = {"systems": "count", "systems_priced": "count", "systems_battery": "count", "capacity_dc": "MW", "price_median": "USD/kW"}
X_COLS = ["x_segment"]


def slug(s):
    return re.sub(r"[^a-z0-9]+", "_", str(s).lower()).strip("_")


def listing(edition, log, offline):
    """The edition's Parquet files, one a state: [(state, url)]."""
    url = f"{LAKE}?list-type=2&prefix=tracking-the-sun/{edition}/"
    content, rec = ip.fetch_raw(CONNECTOR, url, log, offline=offline, headers=UA, timeout=60, pause=1)
    t = content.decode("utf-8", errors="replace")
    if re.search(r"<IsTruncated>true</IsTruncated>", t):
        raise RuntimeError(f"the listing of {edition} is truncated: more than one page of files")
    out = []
    for k in re.findall(r"<Key>(.*?)</Key>", t):
        m = re.fullmatch(rf"tracking-the-sun/{edition}/state=([A-Z]{{2}})/[^/]+\.parquet", k)
        if m:
            out.append((m.group(1), LAKE + k))
    states = [s for s, _ in out]
    if not out or len(set(states)) != len(states):
        raise RuntimeError(f"the listing of {edition}: {len(out)} files, states {states}: none, or a state twice")
    return out, rec


def summarise(d, state, base, cutoff=None):
    """One state's systems (a frame of COLS): its rows by segment and year, and the count of systems without a year. A
    date after cutoff (the file's own Last-Modified day) cannot be an installation's and counts as no date."""
    missing = [c for c in COLS if c not in d.columns]
    if missing:
        raise RuntimeError(f"{state}: no column {missing}; the file's columns are {list(d.columns)[:20]} ...")
    when = pd.to_datetime(d.installation_date, errors="coerce")
    if cutoff is not None:
        when = when.where(when <= cutoff)
    year = when.dt.year
    no_year = int(year.isna().sum())
    d = d.assign(year=year).dropna(subset=["year"]).copy()
    d["year"] = d.year.astype(int)
    seg = d.customer_segment.fillna("-1").astype(str).str.strip()
    d["segment"] = seg.where(seg != "-1", "unknown")
    size = d.pv_system_size_dc.where(d.pv_system_size_dc > 0)
    price = d.total_installed_price.where(d.total_installed_price > 0)
    d["kw"] = size
    d["per_kw"] = price / size
    d["battery"] = (d.battery_rated_capacity_kwh.fillna(-1) > 0).astype(int)
    g = d.groupby(["segment", "year"])
    agg = pd.DataFrame({"systems": g.size(), "capacity_dc": g.kw.sum(min_count=1) / 1000.0, "systems_priced": g.per_kw.count(),
                        "price_median": g.per_kw.median(), "systems_battery": g.battery.sum()})
    out = []
    for (segment, y), r in agg.iterrows():
        for var, unit in UNITS.items():
            v = r[var]
            if pd.isna(v):
                continue
            out.append(dict(base, entity=f"tts:{state.lower()}_{slug(segment)}", variable=var, ts_utc=f"{y:04d}-01-01T00:00:00Z",
                            value=round(float(v), 6), unit=unit, freq="P1Y", geo=f"US-{state}", market="", node=segment, x_segment=segment))
    return out, no_year


def read_file(content, state):
    t = pq.read_table(io.BytesIO(content))
    missing = [c for c in COLS if c not in t.column_names]
    if missing:
        raise RuntimeError(f"{state}: no column {missing}; the file's columns are {t.column_names[:20]} ...")
    return t.select(COLS).to_pandas(), t.num_rows


def main(argv=None):
    ap = argparse.ArgumentParser(description="Berkeley Lab's Tracking the Sun, by state, segment and year")
    ap.add_argument("--offline", action="store_true", help="the saved files only, no request")
    ap.add_argument("--out-dir", help="a trial: the table under this folder, not warehouse/output")
    ap.add_argument("--edition", default=EDITION)
    ap.add_argument("--fetch-only", action="store_true", help="save the files of --states and write nothing")
    ap.add_argument("--states", nargs="+", help="with --fetch-only: the states whose files to fetch")
    args = ap.parse_args(argv)
    if args.out_dir:
        raw_dir = ip.RAW_DIR
        ip.set_out_dir(args.out_dir)
        ip.RAW_DIR = raw_dir
    os.makedirs(ip.LOG_DIR, exist_ok=True)
    run_id = dt.datetime.now(dt.timezone.utc).strftime("%Y%m%dT%H%M%SZ")
    log = ip.Log(os.path.join(ip.LOG_DIR, f"{CONNECTOR}_{run_id}.log"))
    ip.RAW.open(CONNECTOR, run_id)
    rc = 0
    try:
        files, _ = listing(args.edition, log, args.offline)
        if args.fetch_only:
            want = set(args.states or [])
            unknown = want - {s for s, _ in files}
            if not want or unknown:
                raise RuntimeError(f"--fetch-only needs --states from the listing; not in it: {sorted(unknown)}")
            for st, url in files:
                if st in want:
                    content, rec = ip.fetch_raw(CONNECTOR, url, log, offline=args.offline, headers=UA, timeout=300, pause=1)
                    print(f"{st}: {len(content)} bytes")
        else:
            rows, latest, n_sys, n_noyear = [], "", 0, 0
            for st, url in files:
                content, rec = ip.fetch_raw(CONNECTOR, url, log, offline=args.offline, headers=UA, timeout=300, pause=1)
                base = dict(source=SOURCE, source_url=url, retrieved_at=rec.get("retrieved_at") or "", vintage=ip.vintage_of(rec))
                d, n = read_file(content, st)
                stamp = pd.to_datetime(rec.get("last_modified") or rec.get("retrieved_at") or None, errors="coerce", utc=True)
                if pd.isna(stamp):
                    raise RuntimeError(f"{st}: the file's date is not known (no Last-Modified and no retrieval time)")
                got, no_year = summarise(d, st, base, cutoff=stamp.tz_localize(None).normalize())
                rows += got
                n_sys += n
                n_noyear += no_year
                latest = max(latest, base["retrieved_at"])
                log(f"  {st}: {n} systems, {no_year} without an installation date, {len(got)} rows")
            s = pd.DataFrame(rows)
            if s.duplicated(["entity", "variable", "ts_utc"]).any():
                raise RuntimeError("an (entity, variable, ts_utc) given twice")
            cols = ip.SERIES_COLS + X_COLS
            s = s[cols].sort_values(["entity", "variable", "ts_utc"]).reset_index(drop=True)
            states = sorted({st for st, _ in files})
            head = [
                "Energy Research Warehouse (ERW): Berkeley Lab, Tracking the Sun, installed distributed solar systems summarised by state, customer "
                f"segment and year of installation, the {args.edition} public data file (session 2015)",
                "Shape: series (docs/datastandard.md v0). entity tts:<st>_<segment>; variables systems, systems_priced, systems_battery (count), "
                "capacity_dc (MW DC) and price_median (USD/kW: the median of total installed price over DC size, unscreened, not Berkeley Lab's "
                "reported figure); freq P1Y; ts_utc 1 January of the year of installation; geo US-<ST>; node and x_segment the customer segment as "
                "the file writes it (unknown for its -1).",
                f"A summary: the file holds one row a system ({n_sys:,} systems in {len(states)} states: {' '.join(states)}), too large to hold whole. "
                f"{n_noyear:,} systems have no installation date, or one after their file's own date, and no row. A size or price of zero or less is missing. Nothing is filled.",
                f"Retrieved: {run_id} (UTC) by warehouse/connectors/lbnl_tracking_the_sun.py; the latest file retrieved {latest}",
                f"Run log: warehouse/output/logs/{CONNECTOR}_{run_id}.log",
                f"Raw files: warehouse/raw/{CONNECTOR}/ (not in git)",
                f"Source: {SOURCE} Lawrence Berkeley National Laboratory, Tracking the Sun, public data file, on the Open Energy Data Initiative, {PAGE}",
                f"  access: {LAKE}tracking-the-sun/{args.edition}/state=<ST>/part-*.parquet ({len(files)} files)",
                "License: CC BY 4.0, as the OEDI submission states; cite Berkeley Lab, Tracking the Sun.",
            ]
            ip.write_snapshot(s, TABLE, head, log, cols)
            print(f"{TABLE}: {len(s)} rows, {s.entity.nunique()} state segments, {len(states)} states, {s.ts_utc.min()[:4]} to {s.ts_utc.max()[:4]}")
            if not args.out_dir:
                ip.update_sources([dict(source=SOURCE, publisher="Lawrence Berkeley National Laboratory (Berkeley Lab)",
                                        report="Tracking the Sun: installed distributed solar systems, public data file", report_url=PAGE,
                                        document_list=f"{LAKE}?list-type=2&prefix=tracking-the-sun/{args.edition}/", license="public", tables=[TABLE])])
                ip.write_status(CONNECTOR, run_id, [dict(table=TABLE, market="all", status="ok", detail=f"{len(s)} rows")])
    except Exception:
        tb = ip.redact(traceback.format_exc())
        log(f"{TABLE} FAILED, no output file written:\n{tb}")
        print(f"{TABLE} FAILED, no output file written: {tb.strip().splitlines()[-1]}", file=sys.stderr)
        rc = 1
        if not args.out_dir and not args.fetch_only:
            ip.write_status(CONNECTOR, run_id, [dict(table=TABLE, market="all", status="failed", detail=tb.strip().splitlines()[-1][:300])])
    log.close()
    return rc


if __name__ == "__main__":
    sys.exit(main())

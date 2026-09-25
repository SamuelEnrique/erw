#!/usr/bin/env python3
"""ERCOT trading hub settlement point prices, last 30 operating days.

Energy Research Warehouse (ERW) connector. Pulls day-ahead (DAM) and real-time
(RTM) settlement point prices for five ERCOT trading hubs with the gridstatus
Ercot class, reshapes them into the ERW `series` shape (docs/datastandard.md),
and writes:

    warehouse/output/ercot_dam_hub_prices.csv
    warehouse/output/ercot_rtm_hub_prices.csv
    warehouse/output/logs/ercot_prices_<run>.log

Sources (all public ERCOT MIS reports, www.ercot.com):
  DAM  NP4-190-CD  DAM Settlement Point Prices (one file per operating day)
  RTM  NP6-785-ER  Historical RTM Load Zone and Hub Prices (one file per year,
                   updated by ERCOT periodically)
  RTM  NP6-905-CD  Settlement Point Prices at Resource Nodes, Hubs and Load
                   Zones (one file per 15-minute interval, kept about 8 days)

The live NP6-905-CD files only reach back about a week, so RTM rows come from
the yearly NP6-785-ER archive wherever it covers the window, and from
NP6-905-CD for the intervals after the archive ends. Every row records the
exact ERCOT document it was read from (source, source_url, vintage).

Window: the 30 complete ERCOT operating days (America/Chicago) before the day
the script runs. Interval timestamps are converted to UTC interval start.

Fails loudly: if any document cannot be read, or any hub is missing any
interval in the window, no output file is written for that market and the
script exits non-zero. Nothing is filled, interpolated or invented.

Run:  python warehouse/connectors/ercot_prices.py
"""

import datetime as dt
import os
import sys
import time
import traceback

import pandas as pd
from gridstatus import Ercot, Markets

HUBS = ["HB_NORTH", "HB_SOUTH", "HB_WEST", "HB_HOUSTON", "HB_BUSAVG"]
DAYS = 30
TZ = "America/Chicago"
OVERLAP_TOLERANCE = 0.005  # USD/MWh; archive and live values are both 2 dp

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
OUT_DIR = os.path.join(ROOT, "warehouse", "output")
LOG_DIR = os.path.join(OUT_DIR, "logs")

REPORTS = {
    "NP4-190-CD": ("DAM Settlement Point Prices", 12331),
    "NP6-785-ER": ("Historical RTM Load Zone and Hub Prices", 13061),
    "NP6-905-CD": ("Settlement Point Prices at Resource Nodes, Hubs and Load Zones", 12301),
}
PRODUCT_PAGE = "https://www.ercot.com/mp/data-products/data-product-details?id={}"
DOC_LIST = "https://www.ercot.com/misapp/servlets/IceDocListJsonWS?reportTypeId={}"

SERIES_COLS = ["entity", "variable", "ts_utc", "value", "unit", "freq", "geo",
               "market", "node", "source", "source_url", "retrieved_at", "vintage"]


def utc_iso(ts):
    return pd.Timestamp(ts).tz_convert("UTC").strftime("%Y-%m-%dT%H:%M:%SZ")


class TracedErcot(Ercot):
    """Ercot that remembers every document it reads, and retries downloads.

    gridstatus concatenates documents and drops which row came from which one.
    These overrides keep that link so each output row can name its document.
    """

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.frames = []   # (doc, retrieved_at, parsed frame) per document read
        self.singles = []  # (doc, retrieved_at) per _get_document call

    def read_doc(self, doc, *args, **kwargs):
        last = None
        for attempt in range(4):
            try:
                df = super().read_doc(doc, *args, **kwargs)
                self.frames.append((doc, pd.Timestamp.now(tz="UTC"), df.copy()))
                return df
            except Exception as exc:  # retried, then re-raised with context
                last = exc
                time.sleep(2 * (attempt + 1))
        raise RuntimeError(f"could not read ERCOT document {doc.url} "
                           f"({doc.constructed_name}) after 4 attempts: {last!r}")

    def parse_doc(self, doc, *args, **kwargs):
        # gridstatus 0.36.0 bug: the current year's NP6-785-ER workbook has
        # empty sheets for the months still to come. get_rtm_spp concatenates
        # all sheets, the empty ones turn the hour column into dtype object,
        # and parse_doc's .astype("timedelta64[h]") then raises. Cast
        # whole-number hours to int64 first; values are unchanged, and anything
        # that is not a whole number is left alone so the parent still fails.
        for col in ("Delivery Hour", "DeliveryHour", "HourEnding"):
            if col in doc.columns and not pd.api.types.is_integer_dtype(doc[col]):
                h = pd.to_numeric(doc[col], errors="coerce")
                if h.notna().all() and (h == h.round()).all():
                    doc[col] = h.astype("int64")
        return super().parse_doc(doc, *args, **kwargs)

    def _get_document(self, *args, **kwargs):
        doc = super()._get_document(*args, **kwargs)
        self.singles.append((doc, pd.Timestamp.now(tz="UTC")))
        return doc


def window():
    today = pd.Timestamp.now(tz=TZ).normalize()
    start = today - pd.Timedelta(days=DAYS)
    # normalize() on a tz-aware timestamp keeps local midnight across DST
    start = pd.Timestamp(start.date()).tz_localize(TZ)
    end = pd.Timestamp(today.date()).tz_localize(TZ)
    return start, end


def rows_from_frames(frames, report_id):
    """Hub rows from each traced document frame, with the document attached."""
    out = []
    for doc, retrieved_at, df in frames:
        loc_col = next(c for c in ("SettlementPointName", "SettlementPoint",
                                   "Settlement Point Name", "Settlement Point")
                       if c in df.columns)
        price_col = next(c for c in ("SettlementPointPrice", "Settlement Point Price")
                         if c in df.columns)
        d = df[df[loc_col].isin(HUBS)]
        out.append(pd.DataFrame({
            "node": d[loc_col].astype(str).values,
            "interval_start": d["Interval Start"].values,
            "value": pd.to_numeric(d[price_col]).values,
            "source": f"ercot:{report_id}",
            "source_url": doc.url,
            "doc_name": doc.constructed_name,
            "retrieved_at": utc_iso(retrieved_at),
            "vintage": utc_iso(doc.publish_date),
        }))
    if not out:
        return pd.DataFrame(columns=["node", "interval_start", "value", "source",
                                     "source_url", "doc_name", "retrieved_at", "vintage"])
    r = pd.concat(out, ignore_index=True)
    r["interval_start"] = pd.to_datetime(r["interval_start"], utc=True)
    return r


def latest_per_key(rows, log):
    """One row per (node, interval): the most recently published document wins.

    ERCOT posts _retry files that repeat an interval. Identical repeats are
    dropped silently; differing ones are logged.
    """
    rows = rows.sort_values("vintage")
    dup = rows.duplicated(["node", "interval_start"], keep=False)
    if dup.any():
        spread = rows[dup].groupby(["node", "interval_start"])["value"].agg(["min", "max"])
        differing = spread[spread["max"] - spread["min"] > OVERLAP_TOLERANCE]
        log(f"  duplicate (node, interval) keys across documents: {int(dup.sum())} rows; "
            f"{len(differing)} keys with differing values, latest-published kept")
        for key, r in differing.iterrows():
            log(f"    differing: {key[0]} {utc_iso(key[1])} min={r['min']} max={r['max']}")
    return rows.drop_duplicates(["node", "interval_start"], keep="last")


def check_complete(rows, start, end, step, log):
    """Every hub has every interval in [start, end) exactly once, or raise."""
    expected = pd.date_range(start.tz_convert("UTC"), end.tz_convert("UTC"),
                             freq=step, inclusive="left")
    problems = []
    for hub in HUBS:
        have = pd.DatetimeIndex(rows.loc[rows["node"] == hub, "interval_start"])
        missing = expected.difference(have)
        extra = have.difference(expected)
        if len(missing) or len(extra) or have.has_duplicates:
            problems.append(f"{hub}: {len(have)} rows, expected {len(expected)}, "
                            f"missing {len(missing)} (first {[utc_iso(t) for t in missing[:5]]}), "
                            f"extra {len(extra)}")
    if problems:
        for p in problems:
            log("  INCOMPLETE " + p)
        raise RuntimeError("incomplete data, no file written: " + "; ".join(problems))
    log(f"  complete: {len(HUBS)} hubs x {len(expected)} intervals")


def to_series(rows, variable, freq, market):
    s = pd.DataFrame({
        "entity": "ercot:" + rows["node"],
        "variable": variable,
        "ts_utc": rows["interval_start"].dt.strftime("%Y-%m-%dT%H:%M:%SZ"),
        "value": rows["value"],
        "unit": "USD/MWh",
        "freq": freq,
        "geo": "US-TX",
        "market": market,
        "node": rows["node"],
        "source": rows["source"],
        "source_url": rows["source_url"],
        "retrieved_at": rows["retrieved_at"],
        "vintage": rows["vintage"],
    })
    return s.sort_values(["entity", "ts_utc"]).reset_index(drop=True)[SERIES_COLS]


def write_csv(series, name, header_lines, log):
    path = os.path.join(OUT_DIR, name + ".csv")
    tmp = path + ".tmp"
    with open(tmp, "w", encoding="utf-8", newline="") as f:
        for line in header_lines:
            f.write("# " + line + "\n")
        series.to_csv(f, index=False, lineterminator="\n")
    os.replace(tmp, path)
    v = series["value"]
    summary = (f"{name}.csv: rows={len(series)} "
               f"range={series['ts_utc'].min()}..{series['ts_utc'].max()} "
               f"hubs={','.join(sorted(series['node'].unique()))} "
               f"min={v.min():.2f} max={v.max():.2f} USD/MWh")
    print(summary)
    log("  " + summary)
    return path


def header(title, run_id, start, end, used_docs, notes):
    lines = [
        f"Energy Research Warehouse (ERW): {title}",
        "Shape: series (docs/datastandard.md v0). Units: USD/MWh. ts_utc is interval start, UTC.",
        f"Window: ERCOT operating days {start.date()} to {(end - pd.Timedelta(days=1)).date()} "
        f"(America/Chicago), [{utc_iso(start)}, {utc_iso(end)})",
        f"Retrieved: {run_id} (UTC) by warehouse/connectors/ercot_prices.py via gridstatus Ercot",
        f"Run log: warehouse/output/logs/ercot_prices_{run_id}.log (every source document, by name)",
    ]
    for rid, g in used_docs.groupby("source"):
        rid = rid.split(":", 1)[1]
        name, rtid = REPORTS[rid]
        lines.append(f"Source: ERCOT {rid} {name}, {PRODUCT_PAGE.format(rid)}")
        lines.append(f"  document list: {DOC_LIST.format(rtid)}")
        lines.append(f"  {len(g)} document(s) used, published {g['vintage'].min()} to "
                     f"{g['vintage'].max()}; rows from each: see source_url and vintage columns")
    lines += notes
    return lines


def pull_dam(e, start, end, run_id, log):
    log("DAM: ERCOT NP4-190-CD via Ercot.get_spp(market=DAY_AHEAD_HOURLY)")
    # a delivery day's DAM file is published the day before, so ask from start - 1 day
    ret = e.get_spp(date=start - pd.Timedelta(days=1), end=end,
                    market=Markets.DAY_AHEAD_HOURLY, location_type="Trading Hub")
    rows = rows_from_frames(e.frames, "NP4-190-CD")
    rows = rows[(rows["interval_start"] >= start) & (rows["interval_start"] < end)]
    log(f"  documents read: {len(e.frames)}; hub rows in window: {len(rows)}")
    rows = latest_per_key(rows, log)
    check_complete(rows, start, end, "1h", log)
    cross_check(rows, ret, log)
    log_docs(rows, log)
    s = to_series(rows, "spp_dam", "PT1H", "ercot_dam")
    return write_csv(s, "ercot_dam_hub_prices",
                     header("ERCOT day-ahead market settlement point prices, trading hubs",
                            run_id, start, end, rows[["source", "vintage", "source_url"]]
                            .drop_duplicates(), []), log)


def pull_rtm(e, start, end, run_id, log):
    log("RTM: ERCOT NP6-785-ER via Ercot.get_rtm_spp(year), then NP6-905-CD via "
        "Ercot.get_spp(market=REAL_TIME_15_MIN)")
    hist = []
    for year in range(start.year, (end - pd.Timedelta(seconds=1)).year + 1):
        n = len(e.singles)
        df = e.get_rtm_spp(year=year)
        doc, retrieved_at = e.singles[n]
        d = df[df["Location"].isin(HUBS)]
        hist.append(pd.DataFrame({
            "node": d["Location"].astype(str).values,
            "interval_start": pd.to_datetime(d["Interval Start"], utc=True).values,
            "value": pd.to_numeric(d["SPP"]).values,
            "source": "ercot:NP6-785-ER",
            "source_url": doc.url,
            "doc_name": doc.constructed_name,
            "retrieved_at": utc_iso(retrieved_at),
            "vintage": utc_iso(doc.publish_date),
        }))
        log(f"  NP6-785-ER {year}: {doc.constructed_name}, published {utc_iso(doc.publish_date)}, "
            f"hub rows {len(d)}, last interval {utc_iso(d['Interval Start'].max())}")
    hist = pd.concat(hist, ignore_index=True)
    hist["interval_start"] = pd.to_datetime(hist["interval_start"], utc=True)
    hist = hist[(hist["interval_start"] >= start) & (hist["interval_start"] < end)]
    hist_last = hist["interval_start"].max() if len(hist) else start - pd.Timedelta(minutes=15)

    live = rows_from_frames([], "NP6-905-CD")
    if hist_last + pd.Timedelta(minutes=15) < end:
        # one day of overlap with the archive, to compare the two sources
        live_from = max(start, hist_last - pd.Timedelta(days=1))
        e.frames = []
        ret = e.get_spp(date=live_from.tz_convert(TZ), end=end + pd.Timedelta(minutes=15),
                        market=Markets.REAL_TIME_15_MIN, location_type="Trading Hub")
        live = rows_from_frames(e.frames, "NP6-905-CD")
        live = live[(live["interval_start"] >= live_from) & (live["interval_start"] < end)]
        log(f"  NP6-905-CD: documents read {len(e.frames)}, hub rows in window {len(live)}")
        live = latest_per_key(live, log)
        cross_check(live, ret, log)
        compare_overlap(hist, live, log)
        live = live[live["interval_start"] > hist_last]

    rows = pd.concat([hist, live], ignore_index=True)
    check_complete(rows, start, end, "15min", log)
    log_docs(rows, log)
    s = to_series(rows, "spp_rtm", "PT15M", "ercot_rtm")
    notes = [f"Split: NP6-785-ER for intervals up to {utc_iso(hist_last)}, "
             f"NP6-905-CD after. See run log for the overlap comparison."]
    return write_csv(s, "ercot_rtm_hub_prices",
                     header("ERCOT real-time market settlement point prices, trading hubs, 15-minute",
                            run_id, start, end, rows[["source", "vintage", "source_url"]]
                            .drop_duplicates(), notes), log)


def cross_check(rows, ret, log):
    """The traced rows must equal what gridstatus returned for the same keys."""
    r = ret[ret["Location"].isin(HUBS)].copy()
    r["interval_start"] = pd.to_datetime(r["Interval Start"], utc=True)
    r = r.rename(columns={"Location": "node"}).groupby(["node", "interval_start"])["SPP"]
    # ERCOT retry files can repeat a key; accept a match against any returned value
    r_min, r_max = r.min(), r.max()
    m = rows.set_index(["node", "interval_start"])["value"]
    joined = m.to_frame().join(r_min.rename("lo")).join(r_max.rename("hi"))
    if len(joined) != len(rows):
        raise RuntimeError(f"cross-check join fanned out: {len(joined)} keys for {len(rows)} rows")
    missing = int(joined["lo"].isna().sum())
    off = joined[(joined["value"] < joined["lo"] - OVERLAP_TOLERANCE)
                 | (joined["value"] > joined["hi"] + OVERLAP_TOLERANCE)]
    log(f"  cross-check vs gridstatus return: {len(joined)} keys, {missing} absent from return, "
        f"{len(off)} with a different value")
    if missing or len(off):
        raise RuntimeError(f"cross-check failed: {missing} traced rows absent from gridstatus "
                           f"output, {len(off)} with a different value")


def compare_overlap(hist, live, log):
    j = hist.set_index(["node", "interval_start"])["value"].to_frame("archive").join(
        live.set_index(["node", "interval_start"])["value"].rename("live"), how="inner")
    if j.empty:
        log("  overlap NP6-785-ER vs NP6-905-CD: none")
        return
    d = (j["archive"] - j["live"]).abs()
    n_diff = int((d > OVERLAP_TOLERANCE).sum())
    log(f"  overlap NP6-785-ER vs NP6-905-CD: {len(j)} keys, {n_diff} differ by more than "
        f"{OVERLAP_TOLERANCE}, max abs diff {d.max():.4f}. Archive values kept in the overlap.")
    for key, row in j[d > OVERLAP_TOLERANCE].head(20).iterrows():
        log(f"    differs: {key[0]} {utc_iso(key[1])} archive={row['archive']} live={row['live']}")


def log_docs(rows, log):
    g = rows.groupby(["source", "doc_name", "source_url", "vintage"]).size().reset_index(name="rows")
    log(f"  source documents used: {len(g)}")
    for _, r in g.sort_values("vintage").iterrows():
        log(f"    {r['source']} {r['doc_name']} published {r['vintage']} rows {r['rows']} {r['source_url']}")


def main():
    os.makedirs(LOG_DIR, exist_ok=True)
    run_id = dt.datetime.now(dt.timezone.utc).strftime("%Y%m%dT%H%M%SZ")
    log_path = os.path.join(LOG_DIR, f"ercot_prices_{run_id}.log")
    log_f = open(log_path, "w", encoding="utf-8", newline="\n")

    def log(msg):
        log_f.write(msg + "\n")
        log_f.flush()

    start, end = window()
    import gridstatus
    log(f"ERW ercot_prices run {run_id}")
    log(f"gridstatus {gridstatus.__version__}, pandas {pd.__version__}, python {sys.version.split()[0]}")
    log(f"hubs: {', '.join(HUBS)}")
    log(f"window: {start} to {end} (exclusive), UTC [{utc_iso(start)}, {utc_iso(end)})")

    failures = 0
    for name, fn in (("DAM", pull_dam), ("RTM", pull_rtm)):
        e = TracedErcot()
        try:
            fn(e, start, end, run_id, log)
        except Exception:
            failures += 1
            tb = traceback.format_exc()
            log(f"{name} FAILED, no output file written:\n{tb}")
            print(f"{name} FAILED, no output file written. Full error in {log_path}", file=sys.stderr)
            print(tb, file=sys.stderr)
    log(f"done, failures={failures}")
    log_f.close()
    print(f"run log: {os.path.relpath(log_path, ROOT)}")
    return 1 if failures else 0


if __name__ == "__main__":
    sys.exit(main())

#!/usr/bin/env python3
"""The Western Energy Imbalance Market's transfers between balancing areas, every five minutes, the last 35 days, as
CAISO publishes them on OASIS.

Energy Research Warehouse (ERW) connector, chain 601 part F (session 9000; docs/methods/caiso_tie_flows.md). Writes one
rolling series table, caiso_tie_flows_5min:

    entity    caiso:<A>-<B>       a pair of balancing areas, the two codes in alphabetical order, as OASIS names them
    variable  transfer_mw_net     the sum of the pair's tie transfers from A to B less those from B to A, MW (positive:
                                  A sends to B), in the real-time dispatch (RTD)
    freq PT5M, ts_utc the start of the five minutes, market caiso_rtd

    python warehouse/connectors/caiso_tie_flows.py               # the last 35 days (days already held are not asked)
    python warehouse/connectors/caiso_tie_flows.py --days 3      # the last three days
    python warehouse/connectors/caiso_tie_flows.py --out-dir DIR # a trial

Source: CAISO OASIS, ENE_EIM_TRANSFER_TIE version 4 ("EIM Transfer by Tie"), baa_grp_id=ALL, market_run_id=RTD, one
request a day, five seconds apart (https://oasis.caiso.com/oasisapi/SingleZip). OASIS lists each tie of each pair in
both directions (452 tie directions on 18 November 2026, 25 balancing areas). These are the market's scheduled
transfers on each tie, not metered flows.

Kept: a pair's five minutes only on a day the pair had any transfer that was not zero; a pair with none all day has no
row that day (said in the header). A day is written for a pair only when all its five-minute intervals are there.

License: public, with credit. CAISO: "freely available for public use consistent with the general policies of the
Public Records Act" (docs/licenses.md, read #3).
"""

import argparse
import datetime as dt
import os
import sys
import time
import traceback

import pandas as pd

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import iso_prices as ip  # noqa: E402
import grid_congestion as gc  # noqa: E402

CONNECTOR = "caiso_tie_flows"
TABLE = "caiso_tie_flows_5min"
SOURCE = "caiso:ENE_EIM_TRANSFER_TIE"
REPORT = "OASIS EIM Transfer by Tie, real-time dispatch (RTD), five minutes"
URL = ("https://oasis.caiso.com/oasisapi/SingleZip?resultformat=6&queryname=ENE_EIM_TRANSFER_TIE&version=4"
       "&baa_grp_id=ALL&market_run_id=RTD&startdatetime={s}&enddatetime={e}")
WINDOW = 35


def day_url(day):
    tz = gc.CAISO_TZ
    s = pd.Timestamp(day).tz_localize(tz).tz_convert("UTC").strftime("%Y%m%dT%H:%M-0000")
    e = (pd.Timestamp(day) + pd.Timedelta(days=1)).tz_localize(tz).tz_convert("UTC").strftime("%Y%m%dT%H:%M-0000")
    return URL.format(s=s, e=e)


def rows_of(day, x, rec, gaps):
    need = ["INTERVAL_START_GMT", "FROM_BAA", "TO_BAA", "DIRECTION", "VALUE"]
    if any(c not in x.columns for c in need):
        raise RuntimeError(f"ENE_EIM_TRANSFER_TIE columns {list(x.columns)}: layout changed")
    x = x.copy()
    x["MW"] = pd.to_numeric(x["VALUE"], errors="raise")
    a = x["FROM_BAA"].str.strip()
    b = x["TO_BAA"].str.strip()
    lo = a.where(a < b, b)
    hi = b.where(a < b, a)
    # each area reports its own ties: E an export from FROM_BAA to TO_BAA, I an import; both sides' reports agree
    # (every interval of 18 November 2026), so the pair's figure is the first area's report, the second's negated
    # only where the first is missing
    out_of_from = x["MW"].where(x["DIRECTION"].str.strip() == "E", -x["MW"])
    x["pair"] = lo + "-" + hi
    x["side"] = (a == lo).map({True: "lo", False: "hi"})
    x["signed"] = out_of_from.where(a == lo, -out_of_from)
    x["ts"] = pd.to_datetime(x["INTERVAL_START_GMT"], utc=True)
    active = x.groupby("pair")["MW"].apply(lambda s: (s != 0).any())
    x = x[x["pair"].isin(active[active].index)]
    by = x.groupby(["pair", "ts", "side"])["signed"].sum().unstack("side")
    first = by["lo"] if "lo" in by.columns else pd.Series(float("nan"), index=by.index)
    second = by["hi"] if "hi" in by.columns else pd.Series(float("nan"), index=by.index)
    net = first.fillna(second).rename("signed").reset_index()
    a0 = pd.Timestamp(day).tz_localize(gc.CAISO_TZ).tz_convert("UTC")
    a1 = (pd.Timestamp(day) + pd.Timedelta(days=1)).tz_localize(gc.CAISO_TZ).tz_convert("UTC")
    want = set(pd.date_range(a0, a1, freq="5min", inclusive="left"))
    keep = []
    for p, g in net.groupby("pair"):
        if set(g["ts"]) == want and len(g) == len(want):
            keep.append(g)
        else:
            gaps.append(f"{p} {pd.Timestamp(day).date()}: {len(g)} of {len(want)} intervals, left out")
    if not keep:
        return None
    net = pd.concat(keep, ignore_index=True)
    return pd.DataFrame({
        "entity": "caiso:" + net["pair"], "variable": "transfer_mw_net", "ts_utc": net["ts"].map(gc.utc_text),
        "value": net["signed"].round(3), "unit": "MW", "freq": "PT5M", "geo": "US-CA,US-NV,US-AZ,US-OR,US-WA,US-ID,US-UT,US-WY,US-MT,US-NM",
        "market": "caiso_rtd", "node": "", "source": SOURCE, "source_url": rec["url"], "retrieved_at": rec["retrieved_at"],
        "vintage": ""})[ip.SERIES_COLS]


def held_days(log):
    path = os.path.join(ip.OUT_DIR, TABLE + ".csv")
    if not os.path.exists(path):
        return set()
    d = ip.read_series(path, ip.SERIES_COLS)
    ts = pd.to_datetime(d["ts_utc"], utc=True).dt.tz_convert(gc.CAISO_TZ).dt.tz_localize(None).dt.normalize()
    return set(ts.unique())


def main(argv=None):
    ap = argparse.ArgumentParser(description="ERW: CAISO's EIM transfers by balancing-area pair, five minutes, 35 days")
    ap.add_argument("--days", type=int, default=WINDOW)
    ap.add_argument("--out-dir")
    ap.add_argument("--offline", action="store_true")
    a = ap.parse_args(argv)
    raw_dir = ip.RAW_DIR
    if a.out_dir:
        ip.set_out_dir(a.out_dir)
        ip.RAW_DIR = raw_dir
    os.makedirs(ip.LOG_DIR, exist_ok=True)
    run_id = dt.datetime.now(dt.timezone.utc).strftime("%Y%m%dT%H%M%SZ")
    log = ip.Log(os.path.join(ip.LOG_DIR, f"{CONNECTOR}_{run_id}.log"))
    ip.RAW.open(CONNECTOR, run_id)
    results, gaps, frames = [], [], []
    try:
        if ip.paused("caiso"):
            raise RuntimeError(ip.pause_line("caiso"))
        today = pd.Timestamp.now(tz=gc.CAISO_TZ).tz_localize(None).normalize()
        days = [today - pd.Timedelta(days=i) for i in range(1, min(a.days, WINDOW) + 1)]
        held = held_days(log)
        todo = [d for d in days if d not in held or d >= today - pd.Timedelta(days=2)]
        for i, day in enumerate(todo):
            url = day_url(day)
            raw, rec = ip.fetch_raw(CONNECTOR, url, log, offline=a.offline, fresh=gc.stale(day))
            x = gc.oasis_frame(raw, url, gaps, f"ENE_EIM_TRANSFER_TIE {day.date()}")
            if x is not None:
                r = rows_of(day, x, rec, gaps)
                if r is not None:
                    frames.append(r)
            if not rec.get("cached"):
                time.sleep(5)
            print(f"{CONNECTOR}: {i + 1} of {len(todo)} days", flush=True)
        if not frames and not held:
            raise RuntimeError("no row was read; nothing written")
        new = pd.concat(frames, ignore_index=True) if frames else pd.DataFrame(columns=ip.SERIES_COLS)
        since = (today - pd.Timedelta(days=WINDOW)).tz_localize(gc.CAISO_TZ).tz_convert("UTC").strftime("%Y-%m-%dT%H:%M:%SZ")
        hdr = [
            "Energy Research Warehouse (ERW): the Western Energy Imbalance Market's transfers between balancing areas, "
            "five minutes, the last 35 days (CAISO OASIS)",
            "Shape: series (docs/datastandard.md v0). entity caiso:<A>-<B>, the codes in alphabetical order; value the "
            "pair's tie transfers from A to B less those from B to A, MW, real-time dispatch; ts_utc the interval's start.",
            "These are the market's transfers on each tie as OASIS prints them, not metered flows. A pair with no transfer "
            "that was not zero all day has no row that day.",
            f"Gaps in this run: {len(gaps)}" + (": " + "; ".join(gaps[:20]) if gaps else "") + ".",
            f"Retrieved: {run_id} (UTC) by warehouse/connectors/{CONNECTOR}.py",
            f"Run log: warehouse/output/logs/{CONNECTOR}_{run_id}.log",
            f"Raw files: warehouse/raw/{CONNECTOR}/ (not in git; each run's manifest.csv lists each file and URL)",
            f"Source: {SOURCE} {ip.ISO_PUBLISHERS['caiso']}, {REPORT}, {gc.OASIS_PAGE}",
            "License: public, with credit. CAISO: \"freely available for public use consistent with the general policies "
            "of the Public Records Act\" (credit the California ISO).",
            "Method: docs/methods/caiso_tie_flows.md",
        ]
        gc.write(TABLE, new, ip.SERIES_COLS, hdr, log, keep_since=since)
        ip.update_sources([dict(source=SOURCE, publisher=ip.ISO_PUBLISHERS["caiso"], report=REPORT,
                                report_url=gc.OASIS_PAGE, document_list=gc.OASIS_PAGE, license="public", tables=[TABLE])])
        results.append(dict(table=TABLE, market="RTD", status="ok", detail=f"{len(new)} rows"))
        results += [dict(table=TABLE, market="RTD", status="gap", detail=g[:300]) for g in gaps]
    except Exception:
        tb = ip.redact(traceback.format_exc())
        last = tb.strip().splitlines()[-1]
        log(f"{TABLE} FAILED, no output file written:\n{tb}")
        print(f"{CONNECTOR} {TABLE} FAILED, no output file written: {last}", file=sys.stderr)
        results.append(dict(table=TABLE, market="RTD", status="failed", detail=last[:300]))
    ip.write_status(CONNECTOR, run_id, results)
    failures = sum(r["status"] == "failed" for r in results)
    log(f"done, failures={failures}")
    log.close()
    print(f"{CONNECTOR} run log: {os.path.relpath(log.path, ip.ROOT)}")
    return 1 if failures else 0


if __name__ == "__main__":
    sys.exit(main())

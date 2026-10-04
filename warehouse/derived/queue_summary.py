#!/usr/bin/env python3
"""The interconnection queue, summarized by grid and technology (session 95, the interconnection queue explorer).

Energy Research Warehouse (ERW). One derived table, interconnection_queue_summary, from lbnl_interconnection_queue
(Berkeley Lab and GridTracker's Queued Up data file: one row per interconnection request, through the end of the
edition's year). Method: docs/methods/interconnection_queue_summary.md. Page: /queues (in review).

    python warehouse/derived/queue_summary.py                 # the table, under the data lock
    python warehouse/derived/queue_summary.py --out-dir DIR   # a trial run: the table under DIR, nothing in warehouse/output
    python warehouse/derived/queue_summary.py --snapshot      # also the site's own copy (site/data/queues.json)

No request is made. Nothing is estimated: every figure is a count, a sum, a share of counted requests or a median of
dated ones.

Entity queue:<grid>:<technology>. Grids: the seven ISOs (Berkeley Lab's region), its two regions outside them (west,
southeast) and us (every request of the file). Technologies, from Berkeley Lab's type_clean:
    solar           Solar alone
    solar_battery   Solar+Battery: solar with storage at one point of interconnection, kept apart from both
    battery         Battery alone (standalone storage)
    wind            Wind (onshore)
    offshore_wind   Offshore Wind
    gas             Gas alone
    other           everything else: hydro, coal, nuclear, geothermal, oil, other storage, every other hybrid, and a
                    request with no type
    all             every request

Rows of a year entered (freq P1Y, ts_utc the first day of the year the request entered the queue, q_year):
    requests_entered, mw_entered                    every request of that year, whatever became of it
    requests_active, mw_active                      still active in the file (Berkeley Lab's q_status active)
    requests_suspended, mw_suspended
    requests_operating, mw_operating                reached operation (q_status operational)
    requests_withdrawn, mw_withdrawn
A request of unknown status is in requests_entered only. MW is capacity_mw (the request's mw_1 + mw_2 + mw_3; for a
hybrid, all of its parts); a request with no positive capacity is counted and adds no MW.

Rows of an operation year (ts_utc the first day of the year the request began operating, from on_date), written when
at least five requests are dated:
    on_median_years_to_operation, on_requests_dated

Rows of the whole file (ts_utc the first day of the edition's last year):
    total_requests, total_mw, requests_without_year
    total_active_requests, total_active_mw, total_suspended_requests, total_suspended_mw
    past_requests, past_mw                          requests that entered from 2000 to five years before the edition's
                                                    last year (2000 to 2020), with a known status
    past_operating_share_pct, past_withdrawn_share_pct, past_open_share_pct          of past_requests (open: active or suspended)
    past_mw_operating_share_pct, past_mw_withdrawn_share_pct, past_mw_open_share_pct  of past_mw
    operating_requests, years_to_operation_n        requests that reached operation; those with both a request date and
                                                    an operation date, the operation date not before the request
    median_years_to_operation                       the median, over those, of the days between the two dates over 365.25;
                                                    written when years_to_operation_n is at least 5
A share is written when past_requests is at least 20: under that, one project moves it by five points or more.
"""

import argparse
import json
import os
import sys

import numpy as np
import pandas as pd

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.abspath(os.path.join(HERE, "..", ".."))
sys.path.insert(0, os.path.join(ROOT, "warehouse", "connectors"))
import iso_prices as ip  # noqa: E402

NAME = "interconnection_queue_summary"
INPUT = "lbnl_interconnection_queue"
SOURCE = "erw:interconnection_queue_summary"
METHOD_URL = "https://github.com/SamuelEnrique/erw/blob/main/docs/methods/interconnection_queue_summary.md"
SITE_FILE = os.path.join(ROOT, "site", "data", "queues.json")
LICENSE = ("CC BY 4.0 (Berkeley Lab: \"The Queued Up data file is licensed CC BY 4.0... You may use, share, or adapt the dataset as long as you "
           "attribute it to Lawrence Berkeley National Laboratory and GridTracker.\")")

GRIDS = {"caiso": ("CAISO", "US-CA"), "ercot": ("ERCOT", "US-TX"), "isone": ("ISO-NE", "US"), "miso": ("MISO", "US"), "nyiso": ("NYISO", "US-NY"),
         "pjm": ("PJM", "US"), "spp": ("SPP", "US"), "west": ("West", "US"), "southeast": ("Southeast", "US"), "us": (None, "US")}
TECHS = {"solar": "Solar", "solar_battery": "Solar+Battery", "battery": "Battery", "wind": "Wind", "offshore_wind": "Offshore Wind", "gas": "Gas"}
TECH_ORDER = ["all", "solar", "solar_battery", "battery", "wind", "offshore_wind", "gas", "other"]
STATUSES = ["active", "suspended", "operating", "withdrawn"]
PAST_FROM = 2000
PAST_LAG = 5        # a past request entered at least this many years before the edition's last year
MIN_SHARE = 20      # a share is written when at least this many past requests are counted
MIN_MEDIAN = 5      # a median is written when at least this many requests are dated


def read_input(in_dir):
    """The queue file as the connector wrote it. The header's lines are counted and skipped: a queue id can hold a '#',
    and pandas' comment option would cut such a row short."""
    path = os.path.join(in_dir, f"{INPUT}.csv")
    n = 0
    with open(path, encoding="utf-8") as f:
        for line in f:
            if not line.startswith("#"):
                break
            n += 1
    return pd.read_csv(path, skiprows=n, low_memory=False), path


def tech_of(type_clean):
    for k, v in TECHS.items():
        if type_clean == v:
            return k
    return "other"


def prepared(d):
    """The columns the summary needs: the technology group, a status of the four or unknown, MW (zero when not
    positive), the year entered, and the years from request to operation where both dates are held and in order."""
    x = pd.DataFrame({"region": d["region"], "status": d["status"].where(d["status"].isin(STATUSES), "unknown"),
                      "tech": d["type_clean"].map(tech_of), "year": pd.to_numeric(d["q_year"], errors="coerce")})
    mw = pd.to_numeric(d["capacity_mw"], errors="coerce")
    x["mw"] = mw.where(mw > 0, 0.0)
    q, on = pd.to_datetime(d["q_date"], errors="coerce"), pd.to_datetime(d["on_date"], errors="coerce")
    years = (on - q).dt.days / 365.25
    x["years_to_operation"] = years.where((x["status"] == "operating") & (years >= 0))
    x["on_year"] = on.dt.year.where(x["years_to_operation"].notna())
    return x


def summarize(x, last_year):
    """Every (grid, technology) of the file as a dict: years (by year entered), on (by operation year) and whole."""
    out = {}
    past_to = last_year - PAST_LAG
    for grid, (region, _) in GRIDS.items():
        g = x if region is None else x[x["region"] == region]
        for tech in TECH_ORDER:
            t = g if tech == "all" else g[g["tech"] == tech]
            if t.empty:
                continue
            years = {}
            for y, c in t[t["year"].notna()].groupby("year"):
                row = {"requests_entered": int(len(c)), "mw_entered": round(float(c["mw"].sum()), 1)}
                for s in STATUSES:
                    k = c[c["status"] == s]
                    row[f"requests_{s}"] = int(len(k))
                    row[f"mw_{s}"] = round(float(k["mw"].sum()), 1)
                years[int(y)] = row
            on = {}
            for y, c in t[t["on_year"].notna()].groupby("on_year"):
                if len(c) >= MIN_MEDIAN:
                    on[int(y)] = {"on_median_years_to_operation": round(float(c["years_to_operation"].median()), 2), "on_requests_dated": int(len(c))}
            act, sus = t[t["status"] == "active"], t[t["status"] == "suspended"]
            whole = {"total_requests": int(len(t)), "total_mw": round(float(t["mw"].sum()), 1), "requests_without_year": int(t["year"].isna().sum()),
                     "total_active_requests": int(len(act)), "total_active_mw": round(float(act["mw"].sum()), 1),
                     "total_suspended_requests": int(len(sus)), "total_suspended_mw": round(float(sus["mw"].sum()), 1)}
            p = t[(t["year"] >= PAST_FROM) & (t["year"] <= past_to) & (t["status"] != "unknown")]
            whole["past_requests"] = int(len(p))
            whole["past_mw"] = round(float(p["mw"].sum()), 1)
            if len(p) >= MIN_SHARE:
                for name, mask in (("operating", p["status"] == "operating"), ("withdrawn", p["status"] == "withdrawn"),
                                   ("open", p["status"].isin(["active", "suspended"]))):
                    whole[f"past_{name}_share_pct"] = round(100 * float(mask.sum()) / len(p), 2)
                    if p["mw"].sum() > 0:
                        whole[f"past_mw_{name}_share_pct"] = round(100 * float(p.loc[mask, "mw"].sum()) / float(p["mw"].sum()), 2)
            dated = t["years_to_operation"].dropna()
            whole["operating_requests"] = int((t["status"] == "operating").sum())
            whole["years_to_operation_n"] = int(len(dated))
            if len(dated) >= MIN_MEDIAN:
                whole["median_years_to_operation"] = round(float(dated.median()), 2)
            out[(grid, tech)] = {"years": years, "on": on, "whole": whole}
    return out


def unit_of(variable):
    if variable.endswith("share_pct"):
        return "pct"
    if variable.endswith("median_years_to_operation"):
        return "year"
    if variable.startswith("mw_") or variable.endswith("_mw"):
        return "MW"
    return "count"


def rows_of(summary, last_year, retrieved, vintage):
    rows = []
    for (grid, tech), s in summary.items():
        geo = GRIDS[grid][1]

        def add(variable, year, value):
            rows.append(dict(entity=f"queue:{grid}:{tech}", variable=variable, ts_utc=f"{year}-01-01T00:00:00Z", value=value, unit=unit_of(variable), freq="P1Y",
                             geo=geo, market="", node="", source=SOURCE, source_url=METHOD_URL, retrieved_at=retrieved, vintage=""))  # the edition is in the header
        for y, r in s["years"].items():
            for k, v in r.items():
                add(k, y, v)
        for y, r in s["on"].items():
            for k, v in r.items():
                add(k, y, v)
        for k, v in s["whole"].items():
            add(k, last_year, v)
    return rows


def snapshot(summary, last_year, retrieved, vintage, input_retrieved, counts):
    os.makedirs(os.path.dirname(SITE_FILE), exist_ok=True)
    views = {f"{g}|{t}": {"years": {str(y): r for y, r in sorted(s["years"].items())}, "on": {str(y): r for y, r in sorted(s["on"].items())}, "whole": s["whole"]}
             for (g, t), s in summary.items()}
    with open(SITE_FILE, "w", encoding="utf-8", newline="\n") as f:
        json.dump(dict(table=NAME, built=retrieved, vintage=vintage, input_retrieved=input_retrieved, last_year=last_year, past=[PAST_FROM, last_year - PAST_LAG],
                       min_share=MIN_SHARE, min_median=MIN_MEDIAN, grids=list(GRIDS), techs=TECH_ORDER, counts=counts, views=views), f, separators=(",", ":"))


def main(argv=None):
    ap = argparse.ArgumentParser(description="The interconnection queue, summarized by grid and technology")
    ap.add_argument("--out-dir", help="a trial run: the table, its log and the registry under this directory; nothing in warehouse/output")
    ap.add_argument("--snapshot", action="store_true", help="also write the site's own copy (site/data/queues.json)")
    a = ap.parse_args(argv)
    inputs = ip.OUT_DIR
    if a.out_dir:
        os.makedirs(a.out_dir, exist_ok=True)
    run_id = pd.Timestamp.now(tz="UTC").strftime("%Y%m%dT%H%M%SZ")
    retrieved = ip.utc_iso(pd.Timestamp.now(tz="UTC"))
    log_dir = os.path.join(a.out_dir, "logs") if a.out_dir else ip.LOG_DIR
    os.makedirs(log_dir, exist_ok=True)
    log = ip.Log(os.path.join(log_dir, f"queue_summary_{run_id}.log"))
    d, path = read_input(inputs)
    vintage = str(d["vintage"].dropna().iloc[0])
    input_retrieved = str(d["retrieved_at"].dropna().iloc[0])
    last_year = int(pd.to_numeric(d["q_year"], errors="coerce").max())
    x = prepared(d)
    op = x["status"] == "operating"
    early = int(((pd.to_datetime(d["on_date"], errors="coerce") - pd.to_datetime(d["q_date"], errors="coerce")).dt.days < 0)[op].sum())
    counts = {"requests": int(len(x)), "unknown_status": int((x["status"] == "unknown").sum()), "without_year": int(x["year"].isna().sum()),
              "no_positive_capacity": int((x["mw"] <= 0).sum()), "operating": int(op.sum()), "operating_dated": int(x["years_to_operation"].notna().sum()),
              "operating_before_request": early, "no_type": int(d["type_clean"].isna().sum())}
    log(f"  {INPUT}: {len(d):,} requests, {vintage}; last year entered {last_year}; {counts}")
    summary = summarize(x, last_year)
    out = pd.DataFrame(rows_of(summary, last_year, retrieved, vintage))[ip.SERIES_COLS]
    if a.out_dir:
        ip.set_out_dir(a.out_dir)
    target = os.path.join(ip.OUT_DIR, NAME + ".csv")
    if os.path.exists(target):
        ip._require_lock(target, f"rebuilding {NAME}")
        os.remove(target)  # rebuilt whole from its input each run: a new edition of the file replaces every figure
    ip.write_csv(out, NAME, [
        "Energy Research Warehouse (ERW): the interconnection queue summarized by grid and technology (session 95)",
        "Shape: series (docs/datastandard.md v0). freq P1Y. Entity queue:<grid>:<technology>. By year entered (ts_utc the first day of that year): "
        "requests_entered, mw_entered and requests_ and mw_ for active, suspended, operating, withdrawn. By operation year: on_median_years_to_operation, "
        f"on_requests_dated. For the whole file (ts_utc {last_year}-01-01): total_, past_ and median_years_to_operation. Definitions: "
        "docs/methods/interconnection_queue_summary.md.",
        f"Window: {vintage}. Past requests entered from {PAST_FROM} to {last_year - PAST_LAG}. A share is written when at least {MIN_SHARE} past requests are "
        f"counted, a median when at least {MIN_MEDIAN} requests are dated.",
        f"Retrieved: {run_id} (UTC) by warehouse/derived/queue_summary.py", f"Run log: warehouse/output/logs/queue_summary_{run_id}.log",
        f"Derived from: {INPUT} (retrieved {input_retrieved}); read by this run from {os.path.relpath(path, ROOT).replace(os.sep, '/')}",
        f"Source: {SOURCE} from lbnl:queued_up, Lawrence Berkeley National Laboratory and GridTracker, Queued Up: 2026 Edition data file, "
        "https://eta-publications.lbl.gov/publications/queued-2026-edition-characteristics",
        f"License: {LICENSE} A derived table inherits the license of its input: attribute Lawrence Berkeley National Laboratory and GridTracker.",
    ], log, key=["entity", "variable", "ts_utc"])
    ip.update_sources([dict(source=SOURCE, publisher="Energy Research Warehouse (ERW), derived",
                            report="The interconnection queue summarized by grid and technology, from Berkeley Lab and GridTracker's Queued Up data file (CC BY 4.0)",
                            report_url=METHOD_URL, document_list="docs/methods/interconnection_queue_summary.md", license="public", tables=[NAME])])
    if a.snapshot:
        snapshot(summary, last_year, retrieved, vintage, input_retrieved, counts)
    log.close()
    print(f"{NAME}: {len(out):,} rows, {out['entity'].nunique()} grid and technology pairs; {counts}"
          + ("; the site's copy written" if a.snapshot else "") + (f" (trial, under {a.out_dir}; input read from {inputs})" if a.out_dir else ""))
    return 0


if __name__ == "__main__":
    sys.exit(main())

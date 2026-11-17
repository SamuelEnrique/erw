#!/usr/bin/env python3
"""ERW, the interconnection queue (/queues): an independent replication of every figure of the page's file (session
7014, chain 301; the done line's tool 24).

Written from docs/methods/interconnection_queue_summary.md and the table lbnl_interconnection_queue alone (Lawrence
Berkeley National Laboratory and GridTracker, Queued Up, CC BY 4.0), not from warehouse/derived/queue_summary.py. Per
view (grid: Berkeley Lab's region lower-cased without its hyphen, or "us" for every request; technology: from type_clean, or "all"):

  by year entered (q_year)    requests and MW entered, and of them active, suspended, operating (operational) and
                              withdrawn; a request of unknown status counted as entered and in no status; MW only when
                              positive
  by operation year (on_date) the median years from q_date to on_date (days over 365.25) and the count, when at least
                              five requests are dated and the operation date is not before the request
  the whole file              totals, active and suspended totals, the past window (entered 2000 to 2020 with a known
                              status) and its shares (when at least 20 requests), the requests that reached operation,
                              those dated in order and their median (when at least 5)

and the file's counts (requests, unknown status, without a year, no positive capacity, operating, dated, dated the
wrong way round, no type). Prints N of N.

    python replication/queues/replicate.py [--tables DIR] [--site DIR]

Figures are compared to half a unit of their printed last decimal. Exit 0 when every figure is equal, 1 when one is not,
2 when the inputs cannot be read. Standard library only.
"""
import argparse
import csv
import datetime as dt
import json
import os
import statistics
import sys
from collections import defaultdict

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(os.path.dirname(HERE))
TECH = {"Solar": "solar", "Solar+Battery": "solar_battery", "Battery": "battery", "Wind": "wind",
        "Offshore Wind": "offshore_wind", "Gas": "gas"}
STATUS = {"active": "active", "suspended": "suspended", "operational": "operating", "withdrawn": "withdrawn"}


def rows_of(path):
    with open(path, encoding="utf-8", newline="") as f:
        yield from csv.DictReader(ln for ln in f if not ln.startswith("#"))


def num(v):
    try:
        return float(v)
    except (TypeError, ValueError):
        return None


def date(v):
    try:
        return dt.date.fromisoformat(v[:10]) if v else None
    except ValueError:
        return None


def decimals(x):
    s = repr(float(x))
    return 0 if "e" in s else len(s.split(".")[1])


PARTS = {"Battery": "battery", "Solar": "solar", "Wind": "wind", "Offshore Wind": "wind", "Gas": "gas", "Other Storage": "other_storage"}


def summarize(reqs, past, min_share, min_median, last_year, all_rows=False):
    years = defaultdict(lambda: defaultdict(float))
    on = defaultdict(list)
    w = defaultdict(float)
    durations = []
    for r in reqs:
        mw = r["mw"] if r["mw"] and r["mw"] > 0 else 0.0
        st = r["status"]
        w["total_requests"] += 1
        w["total_mw"] += mw
        if r["year"] is None:
            w["requests_without_year"] += 1
        else:
            y = years[r["year"]]
            y["requests_entered"] += 1
            y["mw_entered"] += mw
            if st:
                y[f"requests_{st}"] += 1
                y[f"mw_{st}"] += mw
        if st in ("active", "suspended"):
            w[f"total_{st}_requests"] += 1
            w[f"total_{st}_mw"] += mw
        if r["year"] is not None and past[0] <= r["year"] <= past[1] and st:
            w["past_requests"] += 1
            w["past_mw"] += mw
            w[f"past_{st}"] += 1
            w[f"past_mw_{st}"] += mw
        if st == "operating":
            w["operating_requests"] += 1
            if r["q_date"] and r["on_date"] and r["on_date"] >= r["q_date"]:
                yrs = (r["on_date"] - r["q_date"]).days / 365.25
                durations.append(yrs)
                on[r["on_date"].year].append(yrs)
    out_years = {}
    for y, f in years.items():
        g = dict(f)
        for st in ("active", "suspended", "operating", "withdrawn"):
            g.setdefault(f"requests_{st}", 0.0)
            g.setdefault(f"mw_{st}", 0.0)
        out_years[str(y)] = g
    out_on = {str(y): {"on_median_years_to_operation": statistics.median(xs), "on_requests_dated": len(xs)}
              for y, xs in on.items() if len(xs) >= min_median}
    whole = {k: w.get(k, 0.0) for k in ("total_requests", "total_mw", "requests_without_year", "total_active_requests",
                                         "total_active_mw", "total_suspended_requests", "total_suspended_mw",
                                         "past_requests", "past_mw", "operating_requests")}
    if all_rows:   # session 7051 (done-line request 190): the active MW of each part type, a hybrid's parts included
        for kind in dict.fromkeys(PARTS.values()):
            whole[f"active_mw_parts_{kind}"] = sum(mw for r in reqs if r["status"] == "active" for k, mw in r["parts"] if k == kind and mw and mw > 0)
    whole["years_to_operation_n"] = len(durations)
    if durations and len(durations) >= min_median:
        whole["median_years_to_operation"] = statistics.median(durations)
    if w["past_requests"] >= min_share:
        for name, sts in (("operating", ("operating",)), ("withdrawn", ("withdrawn",)), ("open", ("active", "suspended"))):
            whole[f"past_{name}_share_pct"] = 100 * sum(w[f"past_{s}"] for s in sts) / w["past_requests"]
            if w["past_mw"]:
                whole[f"past_mw_{name}_share_pct"] = 100 * sum(w[f"past_mw_{s}"] for s in sts) / w["past_mw"]
    return {"years": out_years, "on": out_on, "whole": whole}


def main(argv=None):
    ap = argparse.ArgumentParser(description="The queue page's replication")
    ap.add_argument("--tables", default=os.path.join(ROOT, "warehouse", "output"))
    ap.add_argument("--site", default=os.path.join(ROOT, "site"))
    ap.add_argument("--show", type=int, default=40)
    a = ap.parse_args(argv)
    try:
        with open(os.path.join(a.site, "data", "queues.json"), encoding="utf-8") as f:
            page = json.load(f)
        raw = list(rows_of(os.path.join(a.tables, "lbnl_interconnection_queue.csv")))
    except (OSError, ValueError) as exc:
        print(f"the inputs could not be read: {exc}")
        return 2
    n, misses = 0, []

    def check(what, mine, theirs):
        nonlocal n
        n += 1
        if isinstance(theirs, (int, float)) and isinstance(mine, (int, float)) and not isinstance(theirs, bool):
            ok = abs(mine - theirs) <= 0.5 * 10 ** -decimals(theirs) + 1e-6
        else:
            ok = mine == theirs
        if not ok:
            misses.append(f"{what}: replication {mine!r}, file {theirs!r}")

    reqs = []
    for r in raw:
        y = num(r["q_year"])
        reqs.append(dict(grid="".join(ch for ch in (r["region"] or "").lower() if ch.isalnum()), tech=TECH.get(r["type_clean"], "other"),
                         status=STATUS.get((r["q_status"] or "").strip().lower()), mw=num(r["capacity_mw"]),
                         year=int(y) if y is not None else None, q_date=date(r["q_date"]), on_date=date(r["on_date"]),
                         has_type=bool(r["type_clean"]),
                         # session 7051: each part's type and MW (the note's active MW by part type)
                         parts=[(PARTS.get((r.get(f"type_{k}") or "").strip()), num(r.get(f"mw_{k}"))) for k in (1, 2, 3)]))
    c = page["counts"]
    ops = [r for r in reqs if r["status"] == "operating"]
    mine_c = {"requests": len(reqs), "unknown_status": sum(1 for r in reqs if not r["status"]),
              "without_year": sum(1 for r in reqs if r["year"] is None),
              "no_positive_capacity": sum(1 for r in reqs if not (r["mw"] and r["mw"] > 0)),
              "operating": len(ops),
              "operating_dated": sum(1 for r in ops if r["q_date"] and r["on_date"] and r["on_date"] >= r["q_date"]),
              "operating_before_request": sum(1 for r in ops if r["q_date"] and r["on_date"] and r["on_date"] < r["q_date"]),
              "no_type": sum(1 for r in reqs if not r["has_type"])}
    for k, v in c.items():
        check(f"counts {k}", mine_c.get(k), v)
    for key, theirs in page["views"].items():
        grid, tech = key.split("|")
        sel = [r for r in reqs if (grid == "us" or r["grid"] == grid) and (tech == "all" or r["tech"] == tech)]
        mine = summarize(sel, page["past"], page["min_share"], page["min_median"], page["last_year"], all_rows=(tech == "all"))
        for part in ("years", "on"):
            ks = set(theirs.get(part, {})) | set(mine[part])
            for y in sorted(ks):
                t, m = theirs.get(part, {}).get(y, {}), mine[part].get(y, {})
                for k in sorted(set(t) | set(m)):
                    check(f"{key} {part} {y} {k}", m.get(k), t.get(k))
        t, m = theirs.get("whole", {}), mine["whole"]
        for k in sorted(set(t) | set(m)):
            check(f"{key} whole {k}", m.get(k), t.get(k))
    print(f"The interconnection queue, {len(reqs):,} requests of lbnl_interconnection_queue against queues.json "
          f"(built {page['built']}, {page['vintage']}): {len(page['views'])} views")
    for x in misses[:a.show]:
        print("  " + x)
    print(f"{n - len(misses):,} of {n:,} figures equal")
    return 0 if not misses else 1


if __name__ == "__main__":
    sys.exit(main())

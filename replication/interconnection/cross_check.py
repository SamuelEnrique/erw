#!/usr/bin/env python3
"""ERW, the interconnection queue explorer: the cross-check's own arithmetic (session 7509, chain 304).

    python replication/interconnection/cross_check.py --rows <folder with iso_queue_statistics.csv> --lbnl <folder with interconnection_queue_summary.csv>

Sets the explorer's table (iso_queue_statistics: each operator's current queue report, as pulled for the build) beside
Lawrence Berkeley National Laboratory and GridTracker, Queued Up: 2026 Edition (the data file through the end of 2025,
May 2026, CC BY 4.0), as the warehouse holds it summarized in interconnection_queue_summary (a public table; its note is
docs/methods/interconnection_queue_summary.md). For CAISO, ERCOT and SPP, the queues the explorer shows:

  - the requests that entered from 2000 to 2020, and how many of them reached operation, were withdrawn, are open;
  - the withdrawn share of those years;
  - the requests and MW that entered in each of the last five complete years;
  - the active (waiting) requests and MW over every entry year (a sum the page itself never makes).

No request is made of any host: both tables are read from the folders named. No figure is adjusted. Prints one table
(markdown) that docs/methods/interconnection_explorer.md and the faults file quote. Standard library only.
"""
import argparse
import csv
import os
import re
import sys

QUEUES = [("caiso", "CAISO"), ("ercot", "ERCOT"), ("spp", "SPP")]   # the queues the explorer shows; the held ones are not read


def series(path, keep):
    """{(entity, variable, year): value} of a series table, for the entities `keep` accepts."""
    out = {}
    with open(path, encoding="utf-8", newline="") as f:
        lines = f.read().split("\n")
    n = 0
    while lines[n].startswith("#"):
        n += 1
    for r in csv.DictReader(lines[n:]):
        if keep(r["entity"]):
            out[(r["entity"], r["variable"], int(r["ts_utc"][:4]))] = float(r["value"])
    return out


def main(argv=None):
    ap = argparse.ArgumentParser()
    ap.add_argument("--rows", default=os.path.join(os.path.dirname(os.path.abspath(__file__)), "rows"))
    ap.add_argument("--lbnl", required=True, help="the folder holding interconnection_queue_summary.csv")
    a = ap.parse_args(argv)
    ours = series(os.path.join(a.rows, "iso_queue_statistics.csv"), lambda e: e.split(":")[0] in dict(QUEUES))
    lbnl = series(os.path.join(a.lbnl, "interconnection_queue_summary.csv"), lambda e: re.fullmatch(r"queue:(caiso|ercot|spp):all", e) is not None)
    print("| Queue | Figure | The explorer's table (the operator's report, pulled 19 October 2026) | Queued Up 2026 (through 2025) | Difference |")
    print("|---|---|---|---|---|")
    def line(name, what, x, y, fmt="{:,.0f}"):
        d = "" if x is None or y is None else fmt.format(x - y)
        print(f"| {name} | {what} | {fmt.format(x) if x is not None else 'not held'} | {fmt.format(y) if y is not None else 'not held'} | {d} |")
    for q, name in QUEUES:
        o = lambda v, y: ours.get((f"{q}:queue_{y}", v, y))
        l = lambda v, y: lbnl.get((f"queue:{q}:all", v, y))
        span = range(2000, 2021)
        tot = lambda f, v: sum(f(v, y) or 0.0 for y in span)
        ent_o, ent_l = tot(o, "positions_entered"), tot(l, "requests_entered")
        line(name, "entered 2000 to 2020, requests", ent_o, ent_l)
        line(name, "the same: reached operation", tot(o, "positions_operating"), tot(l, "requests_operating"))
        if q != "ercot":
            wd_o, wd_l = tot(o, "positions_withdrawn"), tot(l, "requests_withdrawn")
            line(name, "the same: withdrawn", wd_o, wd_l)
            line(name, "the same: withdrawn share", wd_o / ent_o, wd_l / ent_l, "{:.3f}")
        else:
            print(f"| {name} | the same: withdrawn | not held (ERCOT's report lists none) | {tot(l, 'requests_withdrawn'):,.0f} | |")
        line(name, "the same: still waiting (LBNL: active and suspended)", tot(o, "positions_waiting"), tot(l, "requests_active") + tot(l, "requests_suspended"))
        for y in range(2021, 2026):
            line(name, f"entered {y}, requests", o("positions_entered", y), l("requests_entered", y))
            line(name, f"entered {y}, MW", o("mw_entered", y), l("mw_entered", y))
        years = sorted({k[2] for k in ours if k[0].startswith(f"{q}:")})
        line(name, "still waiting, every entry year, requests (LBNL: active, end of 2025)", sum(o("positions_waiting", y) or 0.0 for y in years), lbnl.get((f"queue:{q}:all", "total_active_requests", 2025)))
        line(name, "still waiting, every entry year, MW (LBNL: active, end of 2025)", sum(o("mw_waiting", y) or 0.0 for y in years), lbnl.get((f"queue:{q}:all", "total_active_mw", 2025)))
        print(f"| {name} | median years from request to operation | by entry year only (no one figure over all years) | {lbnl.get((f'queue:{q}:all', 'median_years_to_operation', 2025), float('nan')):.2f} over {lbnl.get((f'queue:{q}:all', 'years_to_operation_n', 2025), 0):,.0f} requests | |")
    return 0


if __name__ == "__main__":
    sys.exit(main())

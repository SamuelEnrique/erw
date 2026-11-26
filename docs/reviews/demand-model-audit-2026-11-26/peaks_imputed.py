"""Session 10214 (demand audit): for every peak the page's file holds (each whole year's highest hour and each year's
highest hour so far), whether that hour is the balancing authority's own report or EIA's: EIA's "Demand" blank (EIA
filled the hour in its "Adjusted demand") or different. From the extract of the workbooks of 3 October 2026; the 2026
peaks of the file are dated after that and are looked up where the extract holds them. Standard library.

Usage: python peaks_imputed.py <hours dir> <site demand_growth.json> <out>
"""
import csv
import json
import sys


def main(hours, site_p, out):
    S = json.load(open(site_p, encoding="utf-8"))
    lines, n_peaks, n_eia = [], 0, 0
    for ba, a in S["areas"].items():
        if ba == "US48":
            continue
        want = {}
        for y, at in a["at"].items():
            for k, ts in at.items():
                want.setdefault(ts, []).append((y, k))
        found = {}
        with open(f"{hours}/{ba}.csv", newline="", encoding="utf-8") as f:
            for r in csv.DictReader(f):
                if r["ts_start_utc"] in want:
                    found[r["ts_start_utc"]] = (r["demand"], r["adjusted_demand"])
        for ts, keys in sorted(want.items()):
            for y, k in keys:
                n_peaks += 1
                d, adj = found.get(ts, (None, None))
                if d is None:
                    state = "not in the extract (after 3 October 2026)"
                elif d == "":
                    state = f"EIA's estimate: the authority reported nothing; EIA's adjusted value {adj}"
                    n_eia += 1
                elif abs(float(d) - float(adj)) > 0.5:
                    state = f"EIA's estimate: the authority reported {d}, EIA's adjusted value {adj}"
                    n_eia += 1
                else:
                    state = "the authority's own report"
                lines.append(f"{ba} {y} {k} {a['years'][y][k]:,.0f} MW at {ts}: {state}")
    head = f"{n_peaks} peaks in the page's file (seven authorities); {n_eia} of them are hours EIA estimated"
    open(out, "w", encoding="utf-8").write("\n".join([head, ""] + lines) + "\n")
    print(head)
    print("\n".join(x for x in lines if "EIA's estimate" in x))


if __name__ == "__main__":
    main(*sys.argv[1:4])

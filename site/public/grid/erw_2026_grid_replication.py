#!/usr/bin/env python3
"""ERW, the Grid tool (/grid?view=network): the figures of the Network view and of its gravity shape, rebuilt from
erw_2026_grid_replication.csv. The Python mirror of erw_2026_grid_replication.do, step for step, for a reader without
Stata. Standard library only. It prints the do-file's lines, without Stata's padding of a number.

    python erw_2026_grid_replication.py [erw_2026_grid_replication.csv]

What it rebuilds, for the hour shown (the newest hour every reporting pair holds): the count of balancing authorities
drawn and of pairs reporting; how many hours the hour began before the snapshot's refresh (the two-day lag); for each of
the seven ISO grids its ties reporting, its net imports (positive) or net exports over them, MW, and their share of its
demand, percent (the panel's figure); and the gravity shape's place for each: net imports as a share of net generation,
the circle's radius and its distance from the center (site/lib/networkGravity.ts). Method: docs/methods/grid_network.md.
"""

import csv
import math
import os
import sys
from datetime import datetime

CSV_NAME = "erw_2026_grid_replication.csv"
HEADER_LINES = 8             # the do-file: varnames(9) rowrange(10)
ISO = ["CISO", "ERCO", "ISNE", "MISO", "NYIS", "PJM", "SWPP"]
CENTER = "US48"
# site/lib/networkGravity.ts GRAVITY: the frame, the Lower 48's radius, the middle ring, a full pull, the share of a full pull, the smallest radius, the gap
SIZE, R_CENTER, D_MID, D_SPAN, S_FULL, R_MIN, GAP = 640, 80, 205, 90, 0.25, 6, 4


def half_up(x, places=0):
    """JavaScript's Math.round at a number of places (half away from zero for the positive values here)."""
    k = 10 ** places
    return math.floor(x * k + 0.5) / k


def clamp(v, lo, hi):
    return max(lo, min(hi, v))


def when(ts):
    return datetime.strptime(ts[:19], "%Y-%m-%dT%H:%M:%S")


def read(path):
    """import delimited ..., varnames(9) rowrange(10); the two header lines that hold the refresh and the hour."""
    with open(path, encoding="utf-8", newline="") as f:
        lines = f.read().splitlines()
    meta = {}
    for line in lines[:HEADER_LINES]:
        if line.startswith("# snapshot_built,") or line.startswith("# hour_shown,"):
            k, v = line[2:].split(",", 1)
            meta[k] = v
    rows = list(csv.DictReader(lines[HEADER_LINES:]))
    for r in rows:
        r["value"] = float(r["value"])
    return meta, rows


def main(path):
    meta, rows = read(path)
    print(f"hour_shown = {meta['hour_shown']}")
    print(f"snapshot_built = {meta['snapshot_built']}")
    lag = half_up((when(meta["snapshot_built"]) - when(meta["hour_shown"])).total_seconds() / 3600)
    print(f"lag_hours = {int(lag)}")
    print(f"nodes = {sum(1 for r in rows if r['kind'] == 'node')}")
    ties = [r for r in rows if r["kind"] == "tie"]
    print(f"pairs_reporting = {len(ties)}")
    demand = {r["id"]: r["value"] for r in rows if r["kind"] == "demand"}
    gen = {r["id"]: r["value"] for r in rows if r["kind"] == "generation"}
    g0 = gen.get(CENTER)
    held = [gen[b] for b in ISO if gen.get(b, 0) > 0]
    scale = g0 if g0 and g0 > 0 else (max(held) if held else 1)
    print(f"generation_{CENTER} = {g0:g}" if g0 is not None else f"generation_{CENTER} = not held")
    for b in ISO:
        mine = [r for r in ties if r["id"] == b or r["other"] == b]
        net = sum(-r["value"] if r["id"] == b else r["value"] for r in mine)
        print(f"ties_{b} = {len(mine)}")
        if not mine:
            print(f"net_import_{b} = no tie reported")
        else:
            print(f"net_import_{b} = {net:g}")
            if b in demand and demand[b]:
                print(f"net_share_of_demand_pct_{b} = {half_up(abs(net) / demand[b] * 100, 2):.2f}")
        g = gen.get(b)
        r, pull, share = R_MIN, 0.0, None
        if g is not None and g > 0:
            r = max(R_MIN, R_CENTER * math.sqrt(g / scale))
        if mine and g is not None and g > 0:
            share = net / g
            pull = clamp(share / S_FULL, -1, 1)
        elif mine and g is not None and net != 0:
            pull = math.copysign(1, net)
        d = clamp(D_MID - D_SPAN * pull, R_CENTER + r + GAP, SIZE / 2 - r - GAP)
        print(f"generation_{b} = {g:g}" if g is not None else f"generation_{b} = not held")
        print(f"gravity_share_{b} = {share:.6f}" if share is not None else f"gravity_share_{b} = none")
        print(f"gravity_r_{b} = {half_up(r, 1):.1f}")
        print(f"gravity_d_{b} = {half_up(d, 1):.1f}")


if __name__ == "__main__":
    here = os.path.dirname(os.path.abspath(__file__))
    main(sys.argv[1] if len(sys.argv) > 1 else os.path.join(here, CSV_NAME))

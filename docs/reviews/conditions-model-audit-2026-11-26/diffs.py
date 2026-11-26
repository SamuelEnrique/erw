"""Session 10219: the daily-against-hourly differences of restate.json, by grid and column, and their largest size."""
import json
import sys
from collections import Counter, defaultdict

import importlib.util

spec = importlib.util.spec_from_file_location("restate", sys.argv[1] + "/runs/c10219/restate.py")
ROOT = sys.argv[1]
sys.argv = [sys.argv[0], ROOT, ROOT + "/runs/c10219/_unused.json"]
m = importlib.util.module_from_spec(spec)
spec.loader.exec_module(m)

for op in m.OPS:
    f = m.load(op)
    checked, bad, nh = m.restate_daily(f, m.TZ[op])
    by = defaultdict(list)
    for b in bad:
        by[b["col"]].append(b)
    for c, v in by.items():
        if c == "adder_hours":
            gap = [x["file"] - x["restated"] for x in v]
            print(op, c, len(v), "days; file minus restated: sum", sum(gap), "max", max(gap), "min", min(gap))
        else:
            gap = [abs(x["file"] - x["restated"]) for x in v if x["file"] is not None and x["restated"] is not None]
            print(op, c, len(v), "days; largest gap", round(max(gap), 3) if gap else None, Counter(round(g, 2) for g in gap).most_common(3))

"""Session 11402: is anything known early through revisions? The demand the backtest reads for day A is EIA-930's demand
as it stands at the build (revised), while a live forecast reads day A as first published. Three builds of the place
files read three vintages of the demand table:
  V1 0cdfd65ad   tables through 24 November (the run of 11:00 UTC 26 November)
  V2 e5f755eda   tables through 25 November (main's place files)
  V3 15511cb2e   tables through 26 November (the data machine's run of 19:00 UTC 27 November)
Each history row holds `actual` (the demand) and `operator`. Read only; prints and writes revisions.json."""
import json
import os
import subprocess
import sys
from collections import defaultdict

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", ".."))
OUT = sys.argv[1] if len(sys.argv) > 1 else os.path.join(os.path.dirname(__file__), "out")
VS = {"V1": "0cdfd65ad", "V2": "e5f755eda", "V3": "15511cb2e"}


def load(name, commit):
    raw = subprocess.run(["git", "-C", ROOT, "show", f"{commit}:site/data/predict/{name}"], capture_output=True, check=True).stdout
    return json.loads(raw.decode("utf-8"))


idx = load("index.json", VS["V1"])
places = [p["place"] for p in idx["places"]]
hist = {}
for v, c in VS.items():
    hist[v] = {}
    for p in places:
        s = load(f"{p}.json", c)["series"]["demand"]
        cols = s["history_columns"]
        hist[v][p] = {r[0]: dict(zip(cols, r)) for r in s["history"]}
        hist[v][p]["_last"] = max(r[1] for r in s["history"] if r[cols.index("actual")] is not None)


def compare(va, vb, field="actual"):
    """By local day: hours both hold, hours changed by more than 0.05 MW, mean and max absolute percent change."""
    by = defaultdict(lambda: [0, 0, 0.0, 0.0, []])
    for p in places:
        A, B = hist[va][p], hist[vb][p]
        for ts, ra in A.items():
            if ts == "_last" or ts not in B:
                continue
            x, y = ra[field], B[ts][field]
            if x is None or y is None or x <= 0:
                continue
            day = ra["local_day"]
            g = by[(p, day)]
            g[0] += 1
            d = abs(y - x) / x * 100
            if abs(y - x) > 0.05:
                g[1] += 1
            g[2] += d
            g[3] = max(g[3], d)
    return by


out = {}
for va, vb in (("V1", "V2"), ("V2", "V3"), ("V1", "V3")):
    for field in ("actual", "operator"):
        by = compare(va, vb, field)
        # the newest day of the older vintage, place by place (its first publication), against the rest
        newest, older = [0, 0, 0.0], [0, 0, 0.0]
        worst = []
        for (p, day), g in by.items():
            tgt = newest if day == hist[va][p]["_last"] else older
            tgt[0] += g[0]
            tgt[1] += g[1]
            tgt[2] += g[2]
            if day == hist[va][p]["_last"] and g[0]:
                worst.append((round(g[2] / g[0], 3), round(g[3], 2), p, day, g[1], g[0]))
        worst.sort(reverse=True)
        out[f"{va}_{vb}_{field}"] = {
            "newest_day_hours": newest[0], "newest_day_changed": newest[1], "newest_day_mean_abs_pct": round(newest[2] / newest[0], 4) if newest[0] else None,
            "older_days_hours": older[0], "older_days_changed": older[1], "older_days_mean_abs_pct": round(older[2] / older[0], 4) if older[0] else None,
            "newest_day_places_changed": sum(1 for w in worst if w[4]), "newest_day_places": len(worst), "worst_newest": worst[:10]}

# what a revision does to a forecast that reads day A: the "yesterday" method of target day A+2 is day A's demand
# itself, so its error moves one for one; measured on the target days whose day A is V1's newest day
eff = []
for p in places:
    a1 = hist["V1"][p]["_last"]
    for ts, r3 in hist["V3"][p].items():
        if ts == "_last" or r3["actual"] is None:
            continue
        # the row of V3 for target day = a1 + 2 days
        pass
out["note"] = "newest day: the last local day the older vintage holds, read about a day after it ended; compared with the same hours of the newer vintage"
os.makedirs(OUT, exist_ok=True)
with open(os.path.join(OUT, "revisions.json"), "w", encoding="utf-8") as f:
    json.dump(out, f, indent=1)
for k, v in out.items():
    if isinstance(v, dict):
        print(k, {kk: vv for kk, vv in v.items() if kk != "worst_newest"})
        print("   worst newest:", v["worst_newest"][:6])

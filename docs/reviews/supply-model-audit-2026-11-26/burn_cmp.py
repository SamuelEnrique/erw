"""Session 10222: the burn rows of site/data/supply.json against the restatement of burn.py (weeks EIA's workbook of
3 October 2026 holds), and the three comparisons recomputed on the restated weeks with the file's newest weeks over them.

    python burn_cmp.py <supply.json> <burn csv dir> <out.json> [--caiso-own <caiso_own.csv>]
"""
import csv
import datetime as dt
import glob
import json
import os
import sys
from collections import defaultdict

F = json.load(open(sys.argv[1], encoding="utf-8"))
d = sys.argv[2]
own_path = sys.argv[sys.argv.index("--caiso-own") + 1] if "--caiso-own" in sys.argv else None
NEAR = 3
JOIN_WEEK = dt.date(2025, 12, 19)   # the first Friday week end holding an hour from the join (16 December 2025)
WB_END = dt.date(2026, 10, 2)       # the last Friday whose week the workbook holds whole


def at(s, target):
    c = [x for x in s if abs((x - target).days) <= NEAR]
    if not c:
        return None
    x = min(c, key=lambda y: (abs((y - target).days), y))
    return x, s[x]


def figures(s):
    d0 = max(s)
    v0 = s[d0]
    back = lambda x, k: x - dt.timedelta(days=364 * k)   # noqa: E731
    p = at(s, d0 - dt.timedelta(days=7))
    y = at(s, back(d0, 1))
    five = [at(s, back(d0, k)) for k in range(1, 6)]
    out = {"t": d0.isoformat(), "v": v0, "prev_ch": None if p is None else v0 - p[1],
           "year_v": None if y is None else y[1], "year_ch": None if y is None else v0 - y[1],
           "year_pct": None if y is None or y[1] <= 0 else 100 * (v0 - y[1]) / y[1]}
    out["avg5"] = None
    if all(five):
        vals = [x[1] for x in five]
        out["avg5"] = {"v": sum(vals) / 5, "lo": min(vals), "hi": max(vals), "five": [(x[0].isoformat(), x[1]) for x in five]}
    out["surprise"] = None
    if p is not None and all(five):
        chs = []
        for x in five:
            b = at(s, x[0] - dt.timedelta(days=7))
            chs.append(None if b is None else x[1] - b[1])
        if all(c is not None for c in chs):
            m = sum(chs) / 5
            out["surprise"] = {"v": (v0 - p[1]) - m, "lo": min(chs), "hi": max(chs), "outside": not (min(chs) <= v0 - p[1] <= max(chs))}
    return out


mine = defaultdict(dict)
for path in glob.glob(os.path.join(d, "burn_*.csv")):
    if path.endswith("_own.csv"):
        continue
    for r in csv.DictReader(open(path, encoding="utf-8")):
        mine[(r["grid"], r["fuel"])][dt.date.fromisoformat(r["week_end"])] = float(r["value"])
own = {}
if own_path:
    for r in csv.DictReader(open(own_path, encoding="utf-8")):
        own[dt.date.fromisoformat(r["week_end"])] = float(r["value"])

rep = {}
for r in F["rows"]:
    if r["group"] != "burn" or r["status"] != "ok":
        continue
    _, grid, fuel = r["id"].split("-", 2)
    fuel = fuel.replace("-", "_")
    spark = {dt.date.fromisoformat(t): v for t, v in zip(r["spark"]["t"], r["spark"]["v"])}
    if grid == "all":
        grids = sorted({g for g, f in mine if f == fuel})
        common = set.intersection(*(set(mine[(g, fuel)]) for g in grids)) if grids else set()
        s = {w: sum(mine[(g, fuel)][w] for g in grids) for w in common}
        grids_n = len(grids)
    else:
        s = dict(mine.get((grid, fuel), {}))
        grids_n = 1
    # weeks of the spark the restatement can settle: inside the workbook, and for California before the join
    settle = [w for w in spark if w <= WB_END and not ((grid in ("caiso", "all")) and w >= JOIN_WEEK)]
    eq = sum(1 for w in settle if w in s and abs(round(s[w], 4) - spark[w]) <= 1.5e-4)
    miss = [(w.isoformat(), spark[w], None if w not in s else round(s[w], 4)) for w in settle if not (w in s and abs(round(s[w], 4) - spark[w]) <= 1.5e-4)]
    extra = [w.isoformat() for w in s if spark and min(spark) <= w <= WB_END and w not in spark and not ((grid in ("caiso", "all")) and w >= JOIN_WEEK)]
    full = dict(s)
    for w, v in spark.items():
        full[w] = v
    x = figures(full)
    f = {"t": r["last"]["t"], "v": r["last"]["v"], "prev_ch": (r.get("prev") or {}).get("ch"), "year_v": (r.get("year") or {}).get("v"),
         "year_ch": (r.get("year") or {}).get("ch"), "year_pct": (r.get("year") or {}).get("pct"),
         "avg5": None if not r.get("avg5") else {k: r["avg5"][k] for k in ("v", "lo", "hi")}, "surprise": None if not (r.get("change") or {}).get("surprise") and (r.get("change") or {}).get("surprise") != 0 else
         {"v": r["change"]["surprise"], "lo": r["change"]["lo"], "hi": r["change"]["hi"], "outside": r["change"]["outside"]}}

    def same(a, b):
        if a is None or b is None:
            return a is None and b is None
        return abs(a - b) <= 2e-4 * max(1.0, abs(b))
    checks = {"year": same(x["year_ch"], f["year_ch"]) and same(x["year_v"], f["year_v"]),
              "avg5": (x["avg5"] is None and f["avg5"] is None) or (x["avg5"] is not None and f["avg5"] is not None and all(same(x["avg5"][k], f["avg5"][k]) for k in ("v", "lo", "hi"))),
              "surprise": (x["surprise"] is None and f["surprise"] is None) or (x["surprise"] is not None and f["surprise"] is not None and same(x["surprise"]["v"], f["surprise"]["v"]) and x["surprise"]["outside"] == f["surprise"]["outside"])}
    item = {"spark_weeks_settled": len(settle), "spark_weeks_equal": eq, "spark_unequal": miss[:6], "weeks_restated_not_in_file": extra[:6], "grids": grids_n,
            "checks": checks, "restated": x, "file": f}
    if grid == "caiso" and fuel == "natural_gas" and own:
        # California on CAISO's own supply throughout: the like-for-like comparison
        o = dict(own)
        for w, v in spark.items():
            if w >= JOIN_WEEK:
                o[w] = v
        item["caiso_own"] = figures(o)
        post = [w for w in spark if JOIN_WEEK <= w <= max(own)]
        item["caiso_own_vs_spark_after_join"] = {"weeks": len(post), "equal": sum(1 for w in post if w in own and abs(round(own[w], 4) - spark[w]) <= 1.5e-4),
                                                 "unequal": [(w.isoformat(), spark[w], round(own.get(w, float('nan')), 4)) for w in post if not (w in own and abs(round(own[w], 4) - spark[w]) <= 1.5e-4)][:6]}
    rep[r["id"]] = item
json.dump(rep, open(sys.argv[3], "w", encoding="utf-8"), indent=1, default=str)
for k, v in rep.items():
    print(f'{k:28} spark {v["spark_weeks_equal"]}/{v["spark_weeks_settled"]} checks {v["checks"]} unequal {v["spark_unequal"][:2]} extra {v["weeks_restated_not_in_file"][:3]}')
    if "caiso_own" in v:
        print("   caiso own:", json.dumps({k2: v["caiso_own"][k2] for k2 in ("year_v", "year_ch", "year_pct")}), "avg5", json.dumps(v["caiso_own"]["avg5"]), "after join", json.dumps(v["caiso_own_vs_spark_after_join"]))

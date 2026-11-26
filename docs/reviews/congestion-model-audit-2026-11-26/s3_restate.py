"""Session 10220: an independent restatement of every figure /congestion prints as it opens (SPP, 2026, the constraint
whose shadow price summed highest, SPP North hub, no second place), written from docs/methods/grid_congestion.md, the
page file's own rules (sign_rule, cost_rule, share_rule) and the page's words, not from page.tsx or congestion.ts.

The page file holds each constraint's months (hours, mean size, highest size) and each place's months (hours and
means), so the year figures are rebuilt from the months and checked against the year figures the page prints:
  - a constraint's hours in a year      = the sum of its months' hours in that year (exact)
  - its summed shadow price ("cost")    = the sum over months of hours x mean size (to the months' rounding)
  - its highest                         = the largest month's highest (exact)
  - its mean                            = cost / hours (to rounding)
  - the two ranked lists                = the 25 largest by hours and by cost among every constraint the file details
    (a constraint in any year's list is detailed, so the 25 largest of the detailed set are the 25 largest of all)
  - a place's year mean LMP and congestion part = the hour-weighted mean of its months (to the months' rounding);
    its share = congestion mean / LMP mean x 100
  - the chosen constraint's hour-by-month table sums to its hours over every year held; its line sums the same
  - the place's hour-by-month table, weighted by the days of each month held, gives the year mean (DST hours aside)
Compares with the drawn page (out/main_default_fig.json and main_default.txt from draw.mjs). Writes restate.json.
usage: s3_restate.py [drawn tag]"""
import calendar
import json
import os
import re
import sys
from collections import defaultdict

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.abspath(os.path.join(HERE, "..", ".."))
F = json.load(open(os.path.join(ROOT, "site", "data", "conditions", "congestion.json"), encoding="utf-8"))
TAG = sys.argv[1] if len(sys.argv) > 1 else "main"
DRAWN = json.load(open(os.path.join(HERE, "out", f"{TAG}_default_fig.json"), encoding="utf-8"))
TEXT = open(os.path.join(HERE, "out", f"{TAG}_default.txt"), encoding="utf-8").read()

OP, YEAR = "spp", None
O = F["constraints"][OP]
YEAR = O["years"][-1]


def whole(v):  # the page's whole numbers: rounded half away from zero (JavaScript's Math.round for positives), commas
    return f"{int(v + 0.5) if v >= 0 else -int(-v + 0.5):,}"


def usd(v):
    return f"{v:.2f} USD/MWh"


def pct(v):
    return f"{v:.1f}%"


# 1. Each detailed constraint's year figures from its months
rebuilt = {}
gaps = defaultdict(list)
for k, c in O["constraints"].items():
    yrs = defaultdict(lambda: [0, 0.0, 0.0])
    for m, h, am, ax, sm in c["monthly"]:
        y = yrs[m[:4]]
        y[0] += h
        y[1] += h * (am or 0.0)
        y[2] = max(y[2], ax or 0.0)
    rebuilt[k] = {y: {"hours": v[0], "cost": v[1], "abs_max": v[2], "abs_mean": v[1] / v[0] if v[0] else None} for y, v in yrs.items()}
    for y, v in rebuilt[k].items():
        p = c["by_year"].get(y)
        if p is None:
            gaps["year missing"].append((k, y))
            continue
        if p["hours"] != v["hours"]:
            gaps["hours"].append((k, y, p["hours"], v["hours"]))
        if abs(p["abs_max"] - v["abs_max"]) > 0.0051:
            gaps["abs_max"].append((k, y, p["abs_max"], v["abs_max"]))
        # each month's mean is rounded to 0.005, so the sum may stray by up to hours x 0.005
        if abs(p["cost"] - v["cost"]) > 0.005 * v["hours"] + 0.051:
            gaps["cost"].append((k, y, p["cost"], round(v["cost"], 1)))
        if abs(p["abs_mean"] - v["abs_mean"]) > 0.0051 + 0.01:
            gaps["abs_mean"].append((k, y, p["abs_mean"], round(v["abs_mean"], 3)))
    if sum(c["by_year"][y]["hours"] for y in c["by_year"]) != c["hours"]:
        gaps["total hours"].append(k)
    if sum(sum(r) for r in c["hod_month"]) != c["hours"]:
        gaps["hod sum"].append(k)
print("constraints detailed:", len(O["constraints"]), "| gaps:", {g: len(v) for g, v in gaps.items()})
for g, v in gaps.items():
    print("  ", g, v[:5])

# 2. The two lists of the newest year, re-ranked from the detailed set
def rank(year, field):
    rows = [(k, c["by_year"][year]) for k, c in O["constraints"].items() if year in c["by_year"]]
    return [k for k, _ in sorted(rows, key=lambda kv: -kv[1][field])][:25]


lists_ok = {}
for field, name in [("hours", "by_hours"), ("cost", "by_cost")]:
    mine = rank(YEAR, field)
    lists_ok[name] = mine == O["top"][YEAR][name]
    if not lists_ok[name]:
        print("list differs", name, [(a, b) for a, b in zip(mine, O["top"][YEAR][name]) if a != b][:5])
print("lists of", YEAR, "re-ranked from the detailed set equal the page's:", lists_ok)

# 3. What the page prints, restated in order: the hours list, then the cost list (rank, hours, mean, highest, summed)
expect = []
for name in ["by_hours", "by_cost"]:
    for i, k in enumerate(O["top"][YEAR][name]):
        v = rebuilt[k][YEAR]
        p = O["constraints"][k]["by_year"][YEAR]
        # the page prints the file's year figure; the restatement prints what the months give, and the rounding
        # reached by the file's own year figure is kept beside it for the compare
        expect.append((f"h-{i}", whole(v["hours"]), whole(p["hours"])))
        expect.append((f"m-{i}", usd(v["abs_mean"]), usd(p["abs_mean"])))
        expect.append((f"x-{i}", usd(v["abs_max"]), usd(p["abs_max"])))
        expect.append((f"c-{i}", whole(v["cost"]), whole(p["cost"])))

# the places table: every place with the year of SPP North (the first SPP place), ranked by mean congestion part
places = [p for op in F["places"] for p in F["places"][op]]
A = next(p for p in places if p["id"].startswith("spp:"))
PY = sorted(A["years"])[-1]
prow = []
for p in places:
    if PY not in p["by_year"]:
        continue
    ms = [m for m in p["monthly"] if m[0][:4] == PY]
    h = sum(m[1] for m in ms)
    lmp = sum(m[1] * m[2] for m in ms) / h
    cong = sum(m[1] * m[4] for m in ms) / h
    prow.append((p, h, lmp, cong))
prow.sort(key=lambda t: -t[0]["by_year"][PY]["congestion_mean"])
mine_order = [t[0]["id"] for t in sorted(prow, key=lambda t: -t[3])]
print("places ranked by the months' hour-weighted congestion mean, same order as the page's:", mine_order == [t[0]["id"] for t in prow])
for p, h, lmp, cong in prow:
    y = p["by_year"][PY]
    share = 100 * cong / lmp if lmp > 0 else None
    expect.append((f"pl-{p['id']}", usd(lmp), usd(y["lmp_mean"])))
    expect.append((f"pc-{p['id']}", usd(cong), usd(y["congestion_mean"])))
    expect.append((f"ps-{p['id']}", pct(share) if share is not None else "not held", pct(y["congestion_share_pct"]) if y["congestion_share_pct"] is not None else "not held"))
    expect.append((f"pu-{p['id']}", whole(y["hours_congestion_up"]), whole(y["hours_congestion_up"])))
    expect.append((f"pd-{p['id']}", whole(y["hours_congestion_down"]), whole(y["hours_congestion_down"])))
    if h != y["hours"]:
        print("place hours differ", p["id"], h, y["hours"])

# 4. Compare with the drawn page
drawn = [(k, w) for kind, k, w in DRAWN]
n_ok_file = n_ok_months = 0
diffs = []
for (k, w), (ek, from_months, from_file) in zip(drawn, expect):
    if k != ek:
        diffs.append(("key order", k, ek))
        continue
    n_ok_file += w == from_file
    n_ok_months += w == from_months
    if w != from_months:
        diffs.append((k, "page", w, "months give", from_months))
print(f"figures drawn: {len(drawn)}; restated: {len(expect)}; equal to the file's year figure: {n_ok_file}; equal to the months rebuilt: {n_ok_months}")
for d in diffs[:40]:
    print("  ", d)

# 5. The held line, the chosen constraint, its table and line, the place's table
ck = O["top"][YEAR]["by_cost"][0]
C = O["constraints"][ck]
held = f"{whole(O['constraints_by_year'][YEAR])} constraints bound in {whole(O['hours_by_year'][YEAR])} constraint-hours over {O['days_held'][YEAR]} days held in {YEAR}."
print("held line drawn as restated:", held in TEXT, "|", held)
line = f"Bound {whole(C['hours'])} hours from {C['first'][:10]} to {C['last'][:10]}."
print("constraint line drawn as restated:", line in TEXT, "|", line)
hod_sum = sum(sum(r) for r in C["hod_month"])
hod_max = max(max(r) for r in C["hod_month"])
mon_sum = sum(m[1] for m in C["monthly"])
print("chosen", ck, "| table sum", hod_sum, "line sum", mon_sum, "hours", C["hours"], "| darkest", hod_max,
      "drawn:", f"largest figure, {hod_max};" in TEXT or f"largest figure, {hod_max}" in TEXT)
g = A["hod_month_congestion_mean"][PY]
mx = max(abs(v) for r in g for v in r if v is not None)
print("place table darkest", usd(mx), "drawn:", f"largest figure, {usd(mx)}" in TEXT)
# year mean from the hour-by-month table, each month weighted by its days held
num = den = 0.0
for i, r in enumerate(g):
    mm = [m for m in A["monthly"] if m[0] == f"{PY}-{i + 1:02d}"]
    if not mm:
        continue
    days = mm[0][1] / 24
    for v in r:
        if v is not None:
            num += v * days
            den += days
print("place year mean from its hour-by-month table", round(num / den, 3), "page", A["by_year"][PY]["congestion_mean"])

# 6. Dates: the constraint's first and last are UTC dates; the operator's own (Central) date
import datetime as dt
from zoneinfo import ZoneInfo
TZ = {"spp": ZoneInfo("America/Chicago"), "caiso": ZoneInfo("America/Los_Angeles")}
for op in F["constraints"]:
    n = moved = 0
    for k, c in F["constraints"][op]["constraints"].items():
        for f in ("first", "last"):
            t = dt.datetime.fromisoformat(c[f].replace("Z", "+00:00"))
            n += 1
            if t.astimezone(TZ[op]).date().isoformat() != c[f][:10]:
                moved += 1
    print(f"{op}: first and last dates printed as UTC dates; {moved} of {n} differ from the operator's own date")
t = dt.datetime.fromisoformat(C["last"].replace("Z", "+00:00")).astimezone(TZ[OP])
t0 = dt.datetime.fromisoformat(C["first"].replace("Z", "+00:00")).astimezone(TZ[OP])
print("chosen constraint: printed", C["first"][:10], "to", C["last"][:10], "| Central", t0.date(), "to", t.date())

json.dump({"expect": expect, "drawn": drawn, "diffs": diffs, "lists_ok": lists_ok, "gaps": {g: v for g, v in gaps.items()}},
          open(os.path.join(HERE, "restate.json"), "w", encoding="utf-8"), indent=1)

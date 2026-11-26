"""Session 10213 (chain 710, part D): /queues restated independently, from the method note alone.

Reads Berkeley Lab's rows (lbnl_interconnection_queue.csv, as the warehouse writes it) with the standard library only
(csv, statistics; no pandas, no import of the builder or of the replication), applies the rules of
docs/methods/interconnection_queue_summary.md, and sets the result against:
  (a) every value of every view of the page's file, site/data/queues.json;
  (b) every number the default view (/queues, grid us, technology all) prints, as the page's own code drew it
      (the data-n keys of the drawn HTML, the bar hovers, the fold's counts, the peak year).

    python restate_queues.py <lbnl csv> <queues.json> <drawn html> <drawn txt> <out json>
"""
import csv
import datetime as dt
import html as htmlmod
import json
import re
import statistics
import sys
from collections import defaultdict

LBNL, QJSON, HTML, TXT, OUT = sys.argv[1:6]

REGION = {"caiso": "CAISO", "ercot": "ERCOT", "isone": "ISO-NE", "miso": "MISO", "nyiso": "NYISO", "pjm": "PJM",
          "spp": "SPP", "west": "West", "southeast": "Southeast", "us": None}
TECH = {"Solar": "solar", "Solar+Battery": "solar_battery", "Battery": "battery", "Wind": "wind",
        "Offshore Wind": "offshore_wind", "Gas": "gas"}
TECHS = ["all", "solar", "solar_battery", "battery", "wind", "offshore_wind", "gas", "other"]
STATUS = {"active": "active", "suspended": "suspended", "operational": "operating", "withdrawn": "withdrawn"}


def rows_of(path):
    with open(path, encoding="utf-8", newline="") as f:
        lines = [ln for ln in f if not ln.startswith("#")]
    return list(csv.DictReader(lines))


def day(s):
    try:
        return dt.date.fromisoformat(s[:10]) if s else None
    except ValueError:
        return None


def num(s):
    try:
        return float(s)
    except (TypeError, ValueError):
        return None


raw = rows_of(LBNL)
reqs = []
for r in raw:
    st = STATUS.get(r["q_status"], "unknown")
    mw = num(r["capacity_mw"])
    y = num(r["q_year"])
    q, on = day(r["q_date"]), day(r["on_date"])
    yto = None
    if st == "operating" and q and on and on >= q:
        yto = (on - q).days / 365.25
    reqs.append(dict(region=r["region"], tech=TECH.get(r["type_clean"], "other"), status=st,
                     mw=mw if mw is not None and mw > 0 else 0.0, year=int(y) if y is not None else None,
                     yto=yto, on_year=on.year if yto is not None else None, erw_status=r["status"]))

LAST = max(r["year"] for r in reqs if r["year"] is not None)
P0, P1 = 2000, LAST - 5


def view(grid, tech):
    reg = REGION[grid]
    t = [r for r in reqs if (reg is None or r["region"] == reg) and (tech == "all" or r["tech"] == tech)]
    if not t:
        return None
    years = defaultdict(lambda: {k: 0 for k in ["requests_entered", "mw_entered", "requests_active", "mw_active", "requests_suspended",
                                                 "mw_suspended", "requests_operating", "mw_operating", "requests_withdrawn", "mw_withdrawn"]})
    for r in t:
        if r["year"] is None:
            continue
        y = years[r["year"]]
        y["requests_entered"] += 1
        y["mw_entered"] += r["mw"]
        if r["status"] != "unknown":
            y[f"requests_{r['status']}"] += 1
            y[f"mw_{r['status']}"] += r["mw"]
    on = {}
    by_on = defaultdict(list)
    for r in t:
        if r["on_year"] is not None:
            by_on[r["on_year"]].append(r["yto"])
    for y, v in by_on.items():
        if len(v) >= 5:
            on[y] = {"on_median_years_to_operation": statistics.median(v), "on_requests_dated": len(v)}
    act = [r for r in t if r["status"] == "active"]
    sus = [r for r in t if r["status"] == "suspended"]
    past = [r for r in t if r["year"] is not None and P0 <= r["year"] <= P1 and r["status"] != "unknown"]
    w = {"total_requests": len(t), "total_mw": sum(r["mw"] for r in t), "requests_without_year": sum(r["year"] is None for r in t),
         "total_active_requests": len(act), "total_active_mw": sum(r["mw"] for r in act),
         "total_suspended_requests": len(sus), "total_suspended_mw": sum(r["mw"] for r in sus),
         "past_requests": len(past), "past_mw": sum(r["mw"] for r in past)}
    if len(past) >= 20:
        pm = sum(r["mw"] for r in past)
        for name, ok in (("operating", lambda r: r["status"] == "operating"), ("withdrawn", lambda r: r["status"] == "withdrawn"),
                         ("open", lambda r: r["status"] in ("active", "suspended"))):
            sel = [r for r in past if ok(r)]
            w[f"past_{name}_share_pct"] = 100 * len(sel) / len(past)
            if pm > 0:
                w[f"past_mw_{name}_share_pct"] = 100 * sum(r["mw"] for r in sel) / pm
    dated = [r["yto"] for r in t if r["yto"] is not None]
    w["operating_requests"] = sum(r["status"] == "operating" for r in t)
    w["years_to_operation_n"] = len(dated)
    if len(dated) >= 5:
        w["median_years_to_operation"] = statistics.median(dated)
    return {"years": dict(years), "on": on, "whole": w}


def js_round(v):
    # Math.round: half up
    import math
    return math.floor(v + 0.5)


def whole(v):
    return f"{js_round(v):,}"


def two(v):
    return f"{v:,.2f}"


views = {(g, t): view(g, t) for g in REGION for t in TECHS}
views = {k: v for k, v in views.items() if v is not None}

# (a) every value of every view of the page's file
fj = json.load(open(QJSON, encoding="utf-8"))
gaps, n_a, maxgap = [], 0, 0.0
for key, v in fj["views"].items():
    g, t = key.split("|")
    mine = views.get((g, t))
    if mine is None:
        gaps.append(f"{key}: in the file, not restated")
        continue
    for part in ("years", "on"):
        for y, row in v[part].items():
            for k, val in row.items():
                n_a += 1
                m = mine[part].get(int(y), {}).get(k)
                tol = 0.0051 if "median" in k else 0.051
                d = abs((m if m is not None else 1e18) - val)
                maxgap = max(maxgap, d if m is not None else maxgap)
                if d > tol:
                    gaps.append(f"{key} {part} {y} {k}: file {val}, restated {m}")
    for k, val in v["whole"].items():
        if k.startswith("active_mw_parts_"):
            continue
        n_a += 1
        m = mine["whole"].get(k)
        tol = 0.0051 if ("pct" in k or "median" in k) else 0.051
        if m is None or abs(m - val) > tol:
            gaps.append(f"{key} whole {k}: file {val}, restated {m}")
    for k in mine["whole"]:
        if k not in v["whole"]:
            gaps.append(f"{key} whole {k}: restated, not in the file")
missing_views = sorted(f"{g}|{t}" for (g, t) in views if f"{g}|{t}" not in fj["views"])
print(f"(a) the page's file: {len(fj['views'])} views in the file, {len(views)} restated; {n_a:,} values compared; "
      f"{len(gaps)} beyond rounding; views restated but not in the file: {missing_views}")
for x in gaps[:20]:
    print("   ", x)

# counts of the whole file
counts = {"requests": len(reqs), "unknown_status": sum(r["status"] == "unknown" for r in reqs),
          "without_year": sum(r["year"] is None for r in reqs), "no_positive_capacity": sum(r["mw"] <= 0 for r in reqs),
          "operating": sum(r["status"] == "operating" for r in reqs), "operating_dated": sum(r["yto"] is not None for r in reqs)}
cgap = {k: (fj["counts"].get(k), v) for k, v in counts.items() if fj["counts"].get(k) != v}
print(f"    the file's counts against the rows: {'equal' if not cgap else cgap} ({counts})")
st_agree = sum((r["status"] == (r["erw_status"] or "unknown")) for r in reqs)
print(f"    status read from q_status equals the table's status column on {st_agree:,} of {len(reqs):,} rows")

# (b) every number the default view prints
expect = {}
v = views[("us", "all")]
w = v["whole"]
expect["total_active_requests"] = whole(w["total_active_requests"])
expect["total_active_mw"] = whole(w["total_active_mw"])
expect["past_requests"] = whole(w["past_requests"])
expect["past_operating_share_pct"] = two(w["past_operating_share_pct"])
expect["past_withdrawn_share_pct"] = two(w["past_withdrawn_share_pct"])
expect["median_years_to_operation"] = two(w["median_years_to_operation"])
for k, src, f in [("head|active_mw", "total_active_mw", whole), ("head|active_requests", "total_active_requests", whole),
                  ("head|suspended_requests", "total_suspended_requests", whole), ("head|suspended_mw", "total_suspended_mw", whole),
                  ("head|operating", "past_operating_share_pct", two), ("head|past_requests", "past_requests", whole),
                  ("head|operating_mw", "past_mw_operating_share_pct", two), ("head|past_mw", "past_mw", whole),
                  ("head|withdrawn", "past_withdrawn_share_pct", two), ("head|withdrawn_mw", "past_mw_withdrawn_share_pct", two),
                  ("head|open", "past_open_share_pct", two), ("head|median", "median_years_to_operation", two),
                  ("head|dated", "years_to_operation_n", whole), ("head|operating_requests", "operating_requests", whole),
                  ("without_year", "requests_without_year", whole), ("total_requests", "total_requests", whole)]:
    expect[k] = f(w[src])
for y, row in v["years"].items():
    for c in ["requests_entered", "mw_entered", "requests_operating", "requests_withdrawn", "requests_active", "requests_suspended", "mw_active"]:
        expect[f"year|{y}|{c}"] = whole(row[c])
for t in TECHS[1:]:
    kv = views.get(("us", t))
    if not kv:
        continue
    kw = kv["whole"]
    expect[f"kind|{t}|total_active_mw"] = whole(kw["total_active_mw"])
    expect[f"kind|{t}|total_active_requests"] = whole(kw["total_active_requests"])
    for k in ("past_operating_share_pct", "past_withdrawn_share_pct", "median_years_to_operation"):
        if k in kw:
            expect[f"kind|{t}|{k}"] = two(kw[k])
for g in REGION:
    gv = views.get((g, "all"))
    gw = gv["whole"]
    expect[f"grid|{g}|total_active_mw"] = whole(gw["total_active_mw"])
    expect[f"grid|{g}|total_active_requests"] = whole(gw["total_active_requests"])
    for k in ("past_operating_share_pct", "past_withdrawn_share_pct", "median_years_to_operation"):
        if k in gw:
            expect[f"grid|{g}|{k}"] = two(gw[k])

page = {m.group(1): htmlmod.unescape(m.group(2)) for m in re.finditer(r'<span data-n="([^"]+)">([^<]*)</span>', open(HTML, encoding="utf-8").read())}
bad = [(k, page.get(k), expect.get(k)) for k in sorted(set(page) | set(expect)) if page.get(k) != expect.get(k)]
print(f"(b) the default view's keyed numbers: {len(page)} drawn, {len(expect)} restated, {len(page) - len([b for b in bad if b[1] is not None])} equal to the digit")
for b in bad[:30]:
    print("    differs:", b)

txt = open(TXT, encoding="utf-8").read()
hov_bad, hov_n = [], 0
for m in re.finditer(r"Entered (\d{4}): ([\d,]+) MW still active, in ([\d,]+) requests", txt):
    hov_n += 1
    row = v["years"][int(m.group(1))]
    if (m.group(2), m.group(3)) != (whole(row["mw_active"]), whole(row["requests_active"])):
        hov_bad.append(m.group(0))
for m in re.finditer(r"Entered (\d{4}), ([\d,]+) requests: ([\d,]+) operating, ([\d,]+) withdrawn, ([\d,]+) still active or suspended", txt):
    hov_n += 1
    row = v["years"][int(m.group(1))]
    n = row["requests_operating"] + row["requests_withdrawn"] + row["requests_active"] + row["requests_suspended"]
    want = (whole(n), whole(row["requests_operating"]), whole(row["requests_withdrawn"]), whole(row["requests_active"] + row["requests_suspended"]))
    if m.groups()[1:] != want:
        hov_bad.append(m.group(0))
for m in re.finditer(r"Began operating in (\d{4}): median ([\d.]+) years from request, over ([\d,]+) dated requests", txt):
    hov_n += 1
    o = v["on"][int(m.group(1))]
    if (m.group(2), m.group(3)) != (two(o["on_median_years_to_operation"]), whole(o["on_requests_dated"])):
        hov_bad.append(m.group(0))
print(f"    hovers (active bars, outcome bars, median points): {hov_n} read, {hov_n - len(hov_bad)} equal; differs: {hov_bad[:5]}")
expected_hovers = sum(1 for y, r in v["years"].items() if y >= 2000 and r["mw_active"] > 0) \
    + sum(1 for y, r in v["years"].items() if y >= 2000 and (r["requests_operating"] + r["requests_withdrawn"] + r["requests_active"] + r["requests_suspended"]) > 0) \
    + sum(1 for y in v["on"] if y >= 2000)
print(f"    hovers the restatement expects (years from 2000): {expected_hovers}")

fold = re.search(r"of ([\d,]+) that reached operation, ([\d,]+) have both", txt)
fold2 = re.search(r"The year entered of ([\d,]+) requests, and the status of ([\d,]+)\.", txt)
fold_ok = fold and fold2 and (fold.group(1), fold.group(2), fold2.group(1), fold2.group(2)) == (
    whole(counts["operating"]), whole(counts["operating_dated"]), whole(counts["without_year"]), whole(counts["unknown_status"]))
print(f"    the fold's four counts (operating, dated, without a year, unknown status): {'equal' if fold_ok else 'DIFFER'} "
      f"({counts['operating']:,}, {counts['operating_dated']:,}, {counts['without_year']:,}, {counts['unknown_status']:,})")
peak = max(((y, r["mw_active"]) for y, r in v["years"].items() if r["mw_active"] > 0), key=lambda x: x[1])
pk = re.search(r"The most entered in (\d{4})\.", txt)
print(f"    'The most entered in': drawn {pk.group(1) if pk else None}; restated year of most active MW {peak[0]} ({peak[1]:,.1f} MW)")
past_lbl = re.search(r"entered from (\d{4}) to (\d{4})", txt)
print(f"    past window drawn {past_lbl.groups() if past_lbl else None}; restated {P0} to {P1}; last year entered {LAST}")

# whole-number sums across regions: the US equals the nine regions
reg_sum = sum(views[(g, "all")]["whole"]["total_requests"] for g in REGION if g != "us")
print(f"    the nine regions' requests add to {reg_sum:,}; the US view holds {views[('us', 'all')]['whole']['total_requests']:,}; "
      f"rows with a region outside the nine: {sum(1 for r in reqs if r['region'] not in REGION.values())}")
tech_sum = sum(views[("us", t)]["whole"]["total_active_mw"] for t in TECHS[1:] if ("us", t) in views)
print(f"    the seven technologies' active MW add to {tech_sum:,.1f}; the US every-technology view {w['total_active_mw']:,.1f}")

out = {"expect": expect, "page": page, "counts": counts, "gaps_file": gaps, "differs_page": bad, "hovers_bad": hov_bad,
       "us_all_whole": w, "last_year": LAST, "past": [P0, P1]}
json.dump(out, open(OUT, "w", encoding="utf-8"), indent=1, default=str)

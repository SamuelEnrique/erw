"""Session 10213 (chain 710, part D): /queues, one rule changed at a time, and each claim measured.

Reads Berkeley Lab's rows (lbnl_interconnection_queue.csv) and the page files (queues.json, queue_places.json) with
the standard library only. Every rule not named is the method note's.

    python measures_queues.py <lbnl csv> <queues.json> <queue_places.json> <out json>
"""
import csv
import datetime as dt
import json
import statistics
import sys
from collections import Counter, defaultdict

LBNL, QJSON, PJSON, OUT = sys.argv[1:5]
END = dt.date(2025, 12, 31)
TECH = {"Solar": "solar", "Solar+Battery": "solar_battery", "Battery": "battery", "Wind": "wind",
        "Offshore Wind": "offshore_wind", "Gas": "gas"}
REGIONS = ["CAISO", "ERCOT", "ISO-NE", "MISO", "NYISO", "PJM", "SPP", "West", "Southeast"]
STATUS = {"active": "active", "suspended": "suspended", "operational": "operating", "withdrawn": "withdrawn"}
res = {}


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


raw = [r for r in csv.DictReader(ln for ln in open(LBNL, encoding="utf-8", newline="") if not ln.startswith("#"))]
R = []
for r in raw:
    mw = num(r["capacity_mw"])
    parts = [(r[f"type_{k}"], num(r[f"mw_{k}"]) or 0.0) for k in (1, 2, 3) if r[f"type_{k}"]]
    q, on, wd, ia = day(r["q_date"]), day(r["on_date"]), day(r["wd_date"]), day(r["ia_date"])
    st = STATUS.get(r["q_status"], "unknown")
    y = num(r["q_year"])
    R.append(dict(region=r["region"], entity=r["lbnl_entity"], tech=TECH.get(r["type_clean"], "other"), type_clean=r["type_clean"],
                  status=st, mw=mw if mw and mw > 0 else 0.0, mw_raw=mw or 0.0, year=int(y) if y is not None else None,
                  q=q, on=on, wd=wd, ia=ia, parts=parts, poi=r["poi_name"].strip().lower(), name=r["name"].strip().lower(),
                  qid=r["q_id"], state=r["state"], county=r["county"].strip().lower()))


def yto(r):
    return (r["on"] - r["q"]).days / 365.25 if r["status"] == "operating" and r["q"] and r["on"] and r["on"] >= r["q"] else None


def past(rows, p0=2000, p1=2020):
    return [r for r in rows if r["year"] is not None and p0 <= r["year"] <= p1 and r["status"] != "unknown"]


def shares(rows, p0=2000, p1=2020):
    p = past(rows, p0, p1)
    n = len(p)
    if not n:
        return None
    c = Counter(r["status"] for r in p)
    mw = sum(r["mw"] for r in p)
    return dict(n=n, operating=100 * c["operating"] / n, withdrawn=100 * c["withdrawn"] / n,
                open=100 * (c["active"] + c["suspended"]) / n,
                resolved_operating=100 * c["operating"] / (c["operating"] + c["withdrawn"]) if (c["operating"] + c["withdrawn"]) else None,
                mw_operating=100 * sum(r["mw"] for r in p if r["status"] == "operating") / mw if mw else None)


def p(label, val):
    res[label] = val
    print(f"{label}: {val}")


US = R
# ---- 1. each region's record: where it starts, how it thins, how late it runs
print("== 1. each region's record")
reg = {}
for g in REGIONS:
    t = [r for r in R if r["region"] == g]
    ys = [r["year"] for r in t if r["year"] is not None]
    early = [r for r in t if r["year"] is not None and 2000 <= r["year"] <= 2009]
    late = [r for r in t if r["year"] is not None and 2010 <= r["year"] <= 2020]
    wd26 = [r for r in t if r["status"] == "withdrawn" and r["wd"] and r["wd"] > END]
    q4 = [r for r in t if r["q"] and r["q"] >= dt.date(2025, 10, 1)]
    reg[g] = dict(requests=len(t), first_year=min(ys), years_2000_2009=len(early), years_2010_2020=len(late),
                  first_year_with_20=min((y for y, n in Counter(ys).items() if n >= 20), default=None),
                  withdrawn_share_2000_2009=round(100 * sum(r["status"] == "withdrawn" for r in early) / len(early), 2) if early else None,
                  withdrawn_share_2010_2020=round(100 * sum(r["status"] == "withdrawn" for r in late) / len(late), 2) if late else None,
                  operating_share_2000_2009=round(100 * sum(r["status"] == "operating" for r in early) / len(early), 2) if early else None,
                  max_q_date=str(max(r["q"] for r in t if r["q"])), max_on_date=str(max((r["on"] for r in t if r["on"]), default=None)),
                  max_wd_date=str(max((r["wd"] for r in t if r["wd"]), default=None)), entered_oct_dec_2025=len(q4),
                  entered_2025=sum(r["year"] == 2025 for r in t), entered_2024=sum(r["year"] == 2024 for r in t),
                  withdrawn_after_2025=len(wd26), withdrawn_no_date=sum(r["status"] == "withdrawn" and not r["wd"] for r in t),
                  operating_no_on_date=sum(r["status"] == "operating" and not r["on"] for r in t),
                  operating=sum(r["status"] == "operating" for r in t))
    print(g, reg[g])
res["regions"] = reg
p("withdrawn with a withdrawal date after 2025-12-31, every region", sum(v["withdrawn_after_2025"] for v in reg.values()))
p("their MW", round(sum(r["mw"] for r in R if r["status"] == "withdrawn" and r["wd"] and r["wd"] > END), 1))
p("their dates", sorted({str(r["wd"]) for r in R if r["status"] == "withdrawn" and r["wd"] and r["wd"] > END}))
p("the past window's requests by region, 2000 to 2009 against 2010 to 2020", {g: (reg[g]["years_2000_2009"], reg[g]["years_2010_2020"]) for g in REGIONS})
pe = past(R)
p("share of the US past requests (2000 to 2020) that entered 2000 to 2009, by region", {g: round(100 * sum(1 for r in pe if r["region"] == g and r["year"] <= 2009) / sum(1 for r in pe if r["region"] == g), 1) for g in REGIONS})

# ---- 2. hybrids: every part summed against the largest part
print("== 2. hybrids")
act = [r for r in R if r["status"] == "active"]
multi = [r for r in act if len([x for x in r["parts"] if x[1] > 0]) > 1]
summed = sum(r["mw"] for r in act)
largest = sum((max(x[1] for x in r["parts"]) if r["parts"] else r["mw"]) if len([x for x in r["parts"] if x[1] > 0]) > 1 else r["mw"] for r in act)
p("active requests with two or more parts of positive MW", len(multi))
p("active MW, every part summed (the page)", round(summed, 1))
p("active MW, a hybrid at its largest part", round(largest, 1))
p("difference, MW and percent", (round(summed - largest, 1), round(100 * (summed - largest) / summed, 2)))
sb = [r for r in act if r["tech"] == "solar_battery"]
sb_sum = sum(r["mw"] for r in sb)
sb_large = sum(max([x[1] for x in r["parts"]] or [r["mw"]]) for r in sb)
p("solar with storage active: summed, largest part, percent less", (round(sb_sum, 1), round(sb_large, 1), round(100 * (sb_sum - sb_large) / sb_sum, 2)))
p("by region, active MW summed and at the largest part", {g: (round(sum(r["mw"] for r in act if r["region"] == g)), round(sum((max(x[1] for x in r["parts"]) if len([x for x in r["parts"] if x[1] > 0]) > 1 else r["mw"]) for r in act if r["region"] == g))) for g in REGIONS})

# ---- 3. the same project twice
print("== 3. the same project twice")
key = defaultdict(list)
for r in act:
    if r["poi"] and r["name"] and r["name"] != r["qid"].strip().lower():
        key[(r["region"], r["entity"], r["name"], r["poi"])].append(r)
dups = {k: v for k, v in key.items() if len(v) > 1}
extra = sum(len(v) - 1 for v in dups.values())
extra_mw = sum(sum(r["mw"] for r in v) - max(r["mw"] for r in v) for v in dups.values())
p("active requests sharing a region, owner, project name and point of interconnection with another (groups, requests beyond the first, their MW)", (len(dups), extra, round(extra_mw, 1)))
named = sum(1 for r in act if r["name"] and r["name"] != r["qid"].strip().lower())
p("active requests with a project name (other than the queue id)", named)
same_mw = defaultdict(list)
for r in act:
    if r["poi"]:
        same_mw[(r["region"], r["entity"], r["poi"], r["type_clean"], round(r["mw"], 1))].append(r)
d2 = {k: v for k, v in same_mw.items() if len(v) > 1}
p("active requests sharing a region, owner, point of interconnection, type and MW with another (groups, requests beyond the first, their MW)", (len(d2), sum(len(v) - 1 for v in d2.values()), round(sum(sum(r["mw"] for r in v[1:]) for v in d2.values()), 1)))

# ---- 4. time in queue
print("== 4. time in queue")
dated = [yto(r) for r in R if yto(r) is not None]
qs = statistics.quantiles(dated, n=4)
p("built, every year: n, median, mean, quartiles", (len(dated), round(statistics.median(dated), 2), round(statistics.mean(dated), 2), [round(x, 2) for x in qs]))
wdt = [(r["wd"] - r["q"]).days / 365.25 for r in R if r["status"] == "withdrawn" and r["q"] and r["wd"] and r["wd"] >= r["q"]]
p("withdrawn: n dated, median and mean years from request to withdrawal", (len(wdt), round(statistics.median(wdt), 2), round(statistics.mean(wdt), 2)))
age = [(END - r["q"]).days / 365.25 for r in act if r["q"]]
p("active at the end of 2025: n dated, median and mean years already waited", (len(age), round(statistics.median(age), 2), round(statistics.mean(age), 2)))
p("active requests that have waited longer than the built ones' median (3.58 years)", (sum(a > 3.58 for a in age), round(100 * sum(a > 3.58 for a in age) / len(age), 1)))
iat = [(r["ia"] - r["q"]).days / 365.25 for r in R if r["q"] and r["ia"] and r["ia"] >= r["q"]]
p("with an interconnection agreement dated: n, median years from request to agreement", (len(iat), round(statistics.median(iat), 2)))
# the past cohort, 2000 to 2020: share built within N years of the request, every request of the cohort in the denominator
coh = past(R)
for n in (3, 5, 10):
    built = sum(1 for r in coh if yto(r) is not None and yto(r) <= n)
    p(f"past cohort 2000 to 2020: share of all {len(coh):,} built within {n} years (dated ones only)", round(100 * built / len(coh), 2))

# ---- 5. the median line by operation year: the file's start
print("== 5. the operation-year line and the file's start")
byon = defaultdict(list)
for r in R:
    v = yto(r)
    if v is not None:
        byon[r["on"].year].append((v, r["year"]))
line = {}
for y in range(2000, 2026):
    v = byon.get(y, [])
    if len(v) < 5:
        continue
    w = [a for a, _ in v]
    cap = [a for a in w if a <= 4]
    line[y] = dict(n=len(w), median=round(statistics.median(w), 2), longest_possible=round((dt.date(y, 12, 31) - dt.date(1995, 11, 8)).days / 365.25, 1),
                   share_over_5=round(100 * sum(a > 5 for a in w) / len(w), 1), median_of_waits_to_4=round(statistics.median(cap), 2) if cap else None)
for y, v in line.items():
    print(y, v)
res["line"] = line
oldest = min(r["q"] for r in R if r["q"])
p("the file's oldest request date", str(oldest))
p("requests entered before 2000, by year", dict(sorted(Counter(r["year"] for r in R if r["year"] is not None and r["year"] < 2000).items())))

# ---- 6. ERCOT's hybrids in the United States' solar with storage
print("== 6. the US solar with storage, with and without ERCOT's")
sbu = [r for r in R if r["tech"] == "solar_battery"]
p("US solar with storage, as the page", shares(sbu))
p("US solar with storage, ERCOT's left out", shares([r for r in sbu if r["region"] != "ERCOT"]))
qj = json.load(open(QJSON, encoding="utf-8"))
p("the page's file carries not_comparable for", sorted(qj.get("not_comparable", {})))

# ---- 7. "The most entered in": which year, by which measure, every view
print("== 7. the headline's 'The most entered in'")
diff = []
for k, v in qj["views"].items():
    ys = v["years"]
    act_y = max(((y, r["mw_active"]) for y, r in ys.items() if r["mw_active"] > 0), key=lambda x: x[1], default=(None, 0))[0]
    mwe = max(ys.items(), key=lambda x: x[1]["mw_entered"])[0]
    rqe = max(ys.items(), key=lambda x: x[1]["requests_entered"])[0]
    if act_y and (act_y != mwe or act_y != rqe):
        diff.append((k, act_y, mwe, rqe))
p("views where the year of most active MW is not the year of most MW entered or of most requests entered (view, active, MW entered, requests entered)", (len(diff), len(qj["views"])))
p("of which the default view", [d for d in diff if d[0] == "us|all"])
p("first ten", diff[:10])
p("views where a bar hover reads '1 requests' (a year with one active request)", sum(1 for v in qj["views"].values() for r in v["years"].values() if r["requests_active"] == 1))

# ---- 8. one rule changed at a time (the default view, us|all)
print("== 8. one rule at a time, the default view")
base = shares(R)
p("base: past 2000 to 2020, shares", {k: (round(v, 2) if isinstance(v, float) else v) for k, v in base.items()})
for p0, p1 in ((2000, 2018), (2000, 2015), (2010, 2020), (2005, 2020)):
    s = shares(R, p0, p1)
    p(f"past {p0} to {p1}", {k: (round(v, 2) if isinstance(v, float) else v) for k, v in s.items()})
p("base, of resolved requests only (operating over operating plus withdrawn)", round(base["resolved_operating"], 2))
susp = [r for r in R if r["status"] == "suspended"]
p("suspended counted as active: requests, MW", (len(act) + len(susp), round(summed + sum(r["mw"] for r in susp), 1)))
p("negative capacities kept as filed (the page counts them as zero): total MW change", round(sum(r["mw_raw"] for r in R if r["mw_raw"] < 0), 1))
late = [r for r in R if r["status"] == "withdrawn" and r["wd"] and r["wd"] > END]
p("status at 2025-12-31: the withdrawn of 2026 counted as active (requests, MW)", (len(act) + len(late), round(summed + sum(r["mw"] for r in late), 1)))
p("median years, every year (page) against the mean", (round(statistics.median(dated), 2), round(statistics.mean(dated), 2)))
p("median years, operation years 2016 to 2025 only", round(statistics.median([v for y, l in byon.items() if 2016 <= y <= 2025 for v, _ in l]), 2))
# the floors: how many cells of the two tables of every view go "not held" at higher floors
for ms, mm in ((20, 5), (50, 5), (20, 10), (50, 20)):
    ns = sum(1 for v in qj["views"].values() if v["whole"]["past_requests"] >= ms)
    nm = sum(1 for v in qj["views"].values() if v["whole"]["years_to_operation_n"] >= mm)
    p(f"views with a share at a floor of {ms}, a median at {mm}", (ns, nm, len(qj["views"])))

# ---- 9. ISO-NE's dates
print("== 9. ISO-NE")
ne = [r for r in R if r["region"] == "ISO-NE" and r["status"] == "operating"]
p("ISO-NE operating: requests, with an operation date, with a request date", (len(ne), sum(1 for r in ne if r["on"]), sum(1 for r in ne if r["q"])))

# ---- 10. the places page
print("== 10. /queues/places")
pj = json.load(open(PJSON, encoding="utf-8"))
ws = [r for r in R if r["region"] in ("West", "Southeast")]
p("West and Southeast rows with a negative capacity (the places file sums them as filed)", (sum(r["mw_raw"] < 0 for r in ws), round(sum(r["mw_raw"] for r in ws if r["mw_raw"] < 0), 1)))
bad = []
n = 0
for o in pj["owners"]:
    g = [r for r in ws if r["region"] == o["region"] and r["entity"] == o["owner"]]
    n += 1
    if len(g) != o["entries"]:
        bad.append((o["owner"], "entries", o["entries"], len(g)))
    for s, sv in o["by_status"].items():
        stv = {"operational": "operating"}.get(s, s)
        k = [r for r in g if r["status"] == stv]
        n += 2
        if len(k) != sv["entries"]:
            bad.append((o["owner"], s, sv["entries"], len(k)))
        if sv["mw"] is not None and abs(round(sum(r["mw_raw"] for r in k), 1) - sv["mw"]) > 0.051:
            bad.append((o["owner"], s + " mw", sv["mw"], round(sum(r["mw_raw"] for r in k), 1)))
    for t, mv in o["active_mw_by_type"].items():
        n += 1
        x = round(sum(r["mw_raw"] for r in g if r["status"] == "active" and r["type_clean"] == t), 1)
        if mv is not None and abs(x - mv) > 0.051:
            bad.append((o["owner"], "type " + t, mv, x))
    for y, mv in o["active_mw_by_year"].items():
        n += 1
        x = round(sum(r["mw_raw"] for r in g if r["status"] == "active" and r["year"] == int(y)), 1)
        if mv is not None and abs(x - mv) > 0.051:
            bad.append((o["owner"], "year " + y, mv, x))
p("places owners: values restated, differing", (n, bad[:10]))
order = [o["owner"] for o in pj["owners"]]
act_by = sorted({(o["region"], o["owner"]): sum(r["mw_raw"] for r in ws if r["region"] == o["region"] and r["entity"] == o["owner"] and r["status"] == "active") for o in pj["owners"]}.items(), key=lambda x: -x[1])
p("places: the two owners the page opens on, and the two largest by active MW restated", (order[:2], [(k[1], round(v, 1)) for k, v in act_by[:2]]))
sbad = []
for s in pj["states"]:
    g = [r for r in ws if r["state"] == s["state"]]
    a = [r for r in g if r["status"] == "active"]
    if len(g) != s["entries"] or len(a) != s["active_entries"] or (s["active_mw"] is not None and abs(round(sum(r["mw_raw"] for r in a), 1) - s["active_mw"]) > 0.051):
        sbad.append(s["state"])
p("places states: restated, differing", (len(pj["states"]), sbad))
# the states with an entry, and how many of those entries are in a region outside the two (the page counts only West and Southeast)
p("places: owners, states, states with no entry", (len(pj["owners"]), len(pj["states"]), sum(s["no_public_queue"] for s in pj["states"])))

# ---- 11. queue dates bunched on one day (cluster windows)
print("== 11. queue dates")
for g in REGIONS:
    t = [r for r in R if r["region"] == g and r["q"] and r["year"] and r["year"] >= 2020]
    c = Counter(r["q"] for r in t).most_common(3)
    print(g, len(t), [(str(d), n) for d, n in c])
res["bunched"] = {g: [(str(d), n) for d, n in Counter(r["q"] for r in R if r["region"] == g and r["q"] and r["year"] and r["year"] >= 2020).most_common(3)] for g in REGIONS}
qy = sum(1 for r in R if r["q"] and r["year"] is not None and r["q"].year != r["year"])
p("rows whose q_year is not the year of q_date", qy)

json.dump(res, open(OUT, "w", encoding="utf-8"), indent=1, default=str)

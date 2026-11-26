"""Session 10213: the second set of measures for /queues: hybrids' parts by region, each grid's newest dates, the
recent years' open shares, and the places file's whole MW where a tenth differed.

    python measures2_queues.py <lbnl csv> <queues.json> <out json>
"""
import csv
import datetime as dt
import json
import sys
from collections import Counter, defaultdict
from decimal import Decimal

LBNL, QJSON, OUT = sys.argv[1:4]
rows = [r for r in csv.DictReader(ln for ln in open(LBNL, encoding="utf-8", newline="") if not ln.startswith("#"))]
res = {}


def p(k, v):
    res[k] = v
    print(f"{k}: {v}")


def f(s):
    try:
        return float(s)
    except (TypeError, ValueError):
        return None


REG = ["CAISO", "ERCOT", "ISO-NE", "MISO", "NYISO", "PJM", "SPP", "West", "Southeast"]
# ---- hybrids: which regions give a second part its own MW
print("== hybrids' parts")
hy = {}
for g in REG:
    t = [r for r in rows if r["region"] == g and r["type_2"]]
    with_mw2 = [r for r in t if (f(r["mw_2"]) or 0) > 0]
    act_sb = [r for r in rows if r["region"] == g and r["type_clean"] == "Solar+Battery" and r["q_status"] == "active"]
    hy[g] = dict(with_second_part=len(t), second_part_with_mw=len(with_mw2), active_solar_storage=len(act_sb),
                 active_solar_storage_with_mw2=sum((f(r["mw_2"]) or 0) > 0 for r in act_sb),
                 active_solar_storage_mw=round(sum(max(f(r["capacity_mw"]) or 0, 0) for r in act_sb), 1),
                 active_solar_storage_mw2=round(sum(f(r["mw_2"]) or 0 for r in act_sb), 1))
    print(g, hy[g])
res["hybrids"] = hy
ex = [r for r in rows if r["region"] == "ERCOT" and r["type_clean"] == "Solar+Battery" and r["q_status"] == "active"][:3]
p("ERCOT active solar with storage, three rows (type_1, mw_1, type_2, mw_2, capacity)", [(r["type_1"], r["mw_1"], r["type_2"], r["mw_2"], r["capacity_mw"]) for r in ex])
ex = [r for r in rows if r["region"] == "CAISO" and r["type_clean"] == "Solar+Battery" and r["q_status"] == "active"][:3]
p("CAISO active solar with storage, three rows", [(r["type_1"], r["mw_1"], r["type_2"], r["mw_2"], r["capacity_mw"]) for r in ex])
# battery parts that carry no MW, active, every region
nomw = [r for r in rows if r["q_status"] == "active" and any(r[f"type_{k}"] in ("Battery",) and not (f(r[f"mw_{k}"]) or 0) > 0 for k in (1, 2, 3))]
p("active requests with a battery part that carries no MW (requests, their capacity MW)", (len(nomw), round(sum(max(f(r["capacity_mw"]) or 0, 0) for r in nomw), 1)))
p("of which by region", dict(Counter(r["region"] for r in nomw)))

# ---- each grid's newest dates
print("== newest dates")
for g in ("NYISO", "MISO", "ISO-NE", "West", "CAISO", "PJM"):
    t = [r for r in rows if r["region"] == g]
    on_y = Counter(r["on_date"][:4] for r in t if r["q_status"] == "operational" and r["on_date"])
    wd_y = Counter(r["wd_date"][:4] for r in t if r["q_status"] == "withdrawn" and r["wd_date"])
    wd_recent_nodate = sum(1 for r in t if r["q_status"] == "withdrawn" and not r["wd_date"] and f(r["q_year"]) and f(r["q_year"]) >= 2022)
    wd_recent = sum(1 for r in t if r["q_status"] == "withdrawn" and f(r["q_year"]) and f(r["q_year"]) >= 2022)
    op_recent = sum(1 for r in t if r["q_status"] == "operational" and f(r["q_year"]) and f(r["q_year"]) >= 2020)
    op_recent_nodate = sum(1 for r in t if r["q_status"] == "operational" and not r["on_date"] and f(r["q_year"]) and f(r["q_year"]) >= 2020)
    p(f"{g}: operation dates by year (2021 on)", {y: n for y, n in sorted(on_y.items()) if y >= "2021"})
    p(f"{g}: withdrawal dates by year (2021 on)", {y: n for y, n in sorted(wd_y.items()) if y >= "2021"})
    p(f"{g}: withdrawn of entry years 2022 on, and of them with no withdrawal date", (wd_recent, wd_recent_nodate))
    p(f"{g}: operating of entry years 2020 on, and of them with no operation date", (op_recent, op_recent_nodate))
ny = [r for r in rows if r["region"] == "NYISO" and r["wd_date"] == "2023-12-31"]
p("NYISO withdrawn dated exactly 2023-12-31", len(ny))
ny2 = [r for r in rows if r["region"] == "NYISO" and r["on_date"] == "2023-12-31"]
p("NYISO operating dated exactly 2023-12-31", len(ny2))

# ---- the recent years' open shares, us|all and every view
print("== recent years")
qj = json.load(open(QJSON, encoding="utf-8"))
us = qj["views"]["us|all"]["years"]
op = {}
for y in range(2016, 2026):
    r = us[str(y)]
    n = r["requests_operating"] + r["requests_withdrawn"] + r["requests_active"] + r["requests_suspended"]
    op[y] = dict(open=round(100 * (r["requests_active"] + r["requests_suspended"]) / n, 1), withdrawn=round(100 * r["requests_withdrawn"] / n, 1), operating=round(100 * r["requests_operating"] / n, 1))
    print(y, op[y])
res["us_open_by_year"] = op
cnt = defaultdict(int)
tot = 0
for k, v in qj["views"].items():
    for y in range(2021, 2026):
        r = v["years"].get(str(y))
        if not r:
            continue
        n = r["requests_operating"] + r["requests_withdrawn"] + r["requests_active"] + r["requests_suspended"]
        if not n:
            continue
        tot += 1
        if (r["requests_active"] + r["requests_suspended"]) / n > 0.5:
            cnt["mostly_open"] += 1
p("view-years 2021 to 2025 with a request: mostly open (more than half active or suspended), of all", (cnt["mostly_open"], tot))
mo = sum(1 for k, v in qj["views"].items() for y in range(2021, 2025) if (r := v["years"].get(str(y))) and (n := r["requests_operating"] + r["requests_withdrawn"] + r["requests_active"] + r["requests_suspended"]) and (r["requests_active"] + r["requests_suspended"]) / n > 0.5)
mt = sum(1 for k, v in qj["views"].items() for y in range(2021, 2025) if (r := v["years"].get(str(y))) and (r["requests_operating"] + r["requests_withdrawn"] + r["requests_active"] + r["requests_suspended"]))
p("view-years 2021 to 2024 only: mostly open, of all", (mo, mt))
# open share of the past window per view, the largest
big = sorted(((v["whole"].get("past_open_share_pct"), k) for k, v in qj["views"].items() if v["whole"].get("past_open_share_pct") is not None), reverse=True)[:5]
p("past window: the five views with the largest share still open", big)

# ---- places: TEP's withdrawn and the three other tenths, exact
print("== places, exact")
for owner, region, what in (("TEP", "West", ("q_status", "withdrawn")), ("BHCT", None, ("q_status", "withdrawn")), ("PacifiCorp", "West", ("type_clean", "Solar"))):
    sel = [r for r in rows if r["lbnl_entity"] == owner and r["region"] in ("West", "Southeast") and r[what[0]] == what[1] and (what[0] != "type_clean" or r["q_status"] == "active")]
    s = sum((Decimal(r["capacity_mw"]) for r in sel if r["capacity_mw"]), Decimal(0))
    p(f"places {owner} {what}: exact MW", str(s))
neg = [r for r in rows if r["region"] in ("West", "Southeast") and (f(r["capacity_mw"]) or 0) < 0]
p("places: the negative row (owner, status, MW)", [(r["lbnl_entity"], r["q_status"], r["capacity_mw"]) for r in neg])
json.dump(res, open(OUT, "w", encoding="utf-8"), indent=1, default=str)

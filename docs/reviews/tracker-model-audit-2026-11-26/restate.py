# Session 10211: an independent restatement of every keyed figure of the datacenter power tracker (/datacenters and
# /datacenters?view=grids), written from docs/methods/datacenter_tracker.md (sections 3 to 8) and the components' own
# words, not from site/lib/dctop.ts, dcrollups.ts, largeload.ts or bygrid.ts. Standard library only. It reads the CSVs
# as the warehouse writes them (never the live set): datacenter_facilities, datacenter_queue_positions,
# ercot_interconnection_queue, ercot_large_load_status, and the site's own files (data/siting/headroom.json,
# data/datacenter/). Prints one JSON object {figures: {key: value}, notes: {...}}.
#   python runs/c10211/restate.py <warehouse output dir> <site dir> <today YYYY-MM-DD>
import csv
import datetime as dt
import json
import math
import os
import re
import sys

OUT, SITE, TODAY = sys.argv[1], sys.argv[2], sys.argv[3]

US = set("AL AK AZ AR CA CO CT DE DC FL GA HI ID IL IN IA KS KY LA ME MD MA MI MN MS MO MT NE NV NH NJ NM NY NC "
         "ND OH OK OR PA RI SC SD TN TX UT VT VA WA WV WI WY PR".split())
STATE_GRID = {"TX": "ERCOT", "CA": "CAISO", "NY": "NYISO", "PA": "PJM", "NJ": "PJM", "MD": "PJM", "DE": "PJM", "VA": "PJM",
              "WV": "PJM", "OH": "PJM", "DC": "PJM", "MN": "MISO", "IA": "MISO", "WI": "MISO", "MI": "MISO", "LA": "MISO",
              "OK": "SPP", "KS": "SPP", "NE": "SPP"}
for s in "CT ME MA NH RI VT".split():
    STATE_GRID[s] = "ISO-NE"


def table(name):
    path = os.path.join(OUT, name + ".csv")
    with open(path, encoding="utf-8", newline="") as f:
        lines = [ln for ln in f if not ln.startswith("#")]
    return list(csv.DictReader(lines))


def jsround(x):
    return math.floor(x + 0.5)


def mw(r):
    v = r.get("capacity_mw", "")
    return float(v) if v not in ("", None) else None


rows = table("datacenter_facilities")
F = {}
N = {}

# --- the top block (note 3, 4, 5, 7.1)
def us(r):
    return r["state"] in US or r.get("country", "") == "US"


def gone(r):
    return r["status"].lower() in ("withdrawn", "cancelled")


cnt = [r for r in rows if us(r) and not gone(r)]
F["datacenters|count"] = len(rows)
F["datacenters|counted"] = len(cnt)
F["datacenters|no_us_state"] = sum(1 for r in rows if not us(r))
F["datacenters|cancelled"] = sum(1 for r in rows if us(r) and gone(r))
wm = [r for r in cnt if mw(r) is not None]
F["datacenters|mw_total"] = sum(mw(r) for r in wm)
F["datacenters|n_with_mw"] = len(wm)


def sums(key, keep_blank=False):
    d = {}
    for r in wm:
        k = key(r)
        if k or keep_blank:
            d[k] = d.get(k, 0.0) + mw(r)
    return sorted(d.items(), key=lambda kv: (-kv[1], kv[0]))


for k, v in sums(lambda r: r["status"], True):
    F[f"datacenters|status_mw|{k}"] = v
for k, v in sums(lambda r: r["state"]):
    F[f"datacenters|state_mw|{k}"] = v
top5 = sums(lambda r: r["operator"])[:5]
for k, v in top5:
    F[f"datacenters|operator_mw|{k}"] = v
start = (dt.date.fromisoformat(TODAY) - dt.timedelta(days=6)).isoformat()
F[f"datacenters|first_week|{start}"] = sum(1 for r in rows if r["first_story_at"] and start <= r["first_story_at"][:10] <= TODAY)
F["datacenters|n_first_story"] = sum(1 for r in rows if r["first_story_at"])
ops = {}
for r in rows:
    g = ops.setdefault(r["operator"], [0, 0.0, 0])
    g[0] += 1
    if us(r) and not gone(r) and mw(r) is not None:
        g[1] += mw(r)
        g[2] += 1
for op, (n, m, nm) in ops.items():
    F[f"datacenters|operator_count|{op}"] = n
    if nm:
        F[f"datacenters|operator_mw|{op}"] = m

# --- beside ERCOT (note 7.3)
F["datacenters|sites_us"] = sum(1 for r in rows if us(r))
tx = [r for r in rows if r["state"] == "TX"]
F["datacenters|sites_texas"] = len(tx)
allm = [r for r in rows if mw(r) is not None]
F["datacenters|sites_n_with_mw"] = len(allm)
F["datacenters|sites_mw"] = sum(mw(r) for r in allm)
txm = [r for r in tx if mw(r) is not None]
F["datacenters|texas_n_with_mw"] = len(txm)
if txm:
    F["datacenters|texas_mw"] = sum(mw(r) for r in txm)
for r in rows:
    k = r["kind"] or "not stated"
    F[f"datacenters|kind_count|{k}"] = F.get(f"datacenters|kind_count|{k}", 0) + 1

# --- rollups (note 6, 7.5)
def grid(r):
    return r.get("grid", "") or STATE_GRID.get(r["state"].upper(), "")


for dim, of in (("grid", grid), ("operator", lambda r: r["operator"])):
    groups = {}
    for r in rows:
        groups.setdefault(of(r), []).append(r)
    for v, rs in groups.items():
        c = [r for r in rs if r["state"].upper() in US and not gone(r)]
        if not c:
            continue
        m = [mw(r) for r in c if mw(r) is not None]
        kv = v or "-"
        F[f"datacenters|rollup_facilities|{dim}|{kv}"] = len(c)
        if m:
            F[f"datacenters|rollup_mw|{dim}|{kv}"] = sum(m)
        F[f"datacenters|rollup_with_mw|{dim}|{kv}"] = len(m)
        F[f"datacenters|rollup_without|{dim}|{kv}"] = len(c) - len(m)

# --- timeline (note 7.6)
tl = []
for r in rows:
    rep = r["first_story_at"]
    yv = r.get("energized_year", "") or r.get("planned_year", "")
    if not re.match(r"^\d{4}-\d{2}", rep):
        continue
    try:
        y = int(float(yv))
    except ValueError:
        continue
    if float(yv) != y or y < 2000:
        continue
    tl.append((grid(r), rep[:4], y - int(rep[:4])))
F["dctime|rows"] = len(tl)


def med(xs):
    if len(xs) < 3:
        return None
    s = sorted(xs)
    h = len(s) // 2
    return s[h] if len(s) % 2 else (s[h - 1] + s[h]) / 2


for i, dim in ((0, "grid"), (1, "year")):
    cells = {}
    for t in tl:
        cells.setdefault(t[i], []).append(t[2])
    for v, ws in cells.items():
        F[f"dctime|count|{dim}|{v or '-'}"] = len(ws)
        if med(ws) is not None:
            F[f"dctime|median|{dim}|{v or '-'}"] = med(ws)

# --- the charts (note 7.7)
ahead = [r for r in cnt if r["status"].lower() in ("planned", "under_construction")]
gmw = {}
for r in ahead:
    if mw(r) is not None and grid(r):
        gmw[grid(r)] = gmw.get(grid(r), 0.0) + mw(r)
top4 = [g for g, _ in sorted(gmw.items(), key=lambda kv: (-kv[1], kv[0]))[:4]]
dated = [r for r in ahead if re.match(r"^\d{4}-\d{2}", r["first_story_at"])]


def quarter(d):
    return f"{d[:4]}-Q{(int(d[5:7]) - 1) // 3 + 1}"


for q in sorted({quarter(r["first_story_at"]) for r in dated}):
    inq = [r for r in dated if quarter(r["first_story_at"]) == q]
    for g in top4 + ["other"]:
        F[f"dcchart|planned|{q}|{g}"] = sum(mw(r) or 0.0 for r in inq if (grid(r) if grid(r) in top4 else "other") == g)
    F[f"dcchart|planned|{q}|without"] = sum(1 for r in inq if mw(r) is None)
opmw = sorted(((k, v) for k, v in ops.items() if k and v[2]), key=lambda kv: (-kv[1][1], -kv[1][0], kv[0]))[:10]
for k, v in opmw:
    F[f"dcchart|operator|{k}|mw"] = v[1]
pk = {}
for r in cnt:
    k = r.get("power_kind", "") or "none"
    pk[k] = pk.get(k, 0) + 1
for k, n in pk.items():
    F[f"dcchart|power|{k}|facilities"] = n
    F[f"dcchart|power|{k}|pct"] = jsround(1000 * n / len(cnt)) / 10

# --- the facilities against each grid (note 7.8)
head = json.load(open(os.path.join(SITE, "data", "siting", "headroom.json"), encoding="utf-8"))
GID = {"ERCOT": "ercot", "CAISO": "caiso", "PJM": "pjm", "MISO": "miso", "SPP": "spp", "NYISO": "nyiso", "ISO-NE": "isone"}
for g, gid in GID.items():
    rs = [r for r in cnt if r["state"].upper() in US and grid(r) == g]
    pc = head.get("peak_capacity", {}).get(gid)
    if rs:
        F[f"dcgrid|facilities|{g}"] = len(rs)
        F[f"dcgrid|with_mw|{g}"] = sum(1 for r in rs if mw(r) is not None)
        st = {}
        for r in rs:
            if mw(r) is not None and r["status"].lower() in ("planned", "under_construction", "operating"):
                st.setdefault(r["status"].lower(), []).append(mw(r))
        for s in ("planned", "under_construction", "operating"):
            if s in st:
                F[f"dcgrid|{s}|{g}"] = sum(st[s])
        if pc and pc.get("peak_mw") and ("planned" in st or "under_construction" in st):
            F[f"dcgrid|share_of_peak|{g}"] = jsround(1000 * (sum(st.get("planned", [])) + sum(st.get("under_construction", []))) / pc["peak_mw"]) / 10
    if pc:
        F[f"dcgrid|peak_mw|{g}"] = pc["peak_mw"]
        F[f"dcgrid|capacity_mw|{g}"] = pc["capacity_mw"]
    rm = head.get("reserve", {}).get("grids", {}).get(gid)
    if rm:
        F[f"dcgrid|reserve_margin|{g}"] = rm["peak"]["pct"]

# --- ERCOT's large loads, from the warehouse's CSV (not the site's copy)
ll = table("ercot_large_load_status")
VAR = {"approved_to_energize_mw": "approved", "observed_nonsimultaneous_peak_mw": "non", "observed_simultaneous_peak_mw": "sim",
       "new_submissions_count": "nc", "new_submissions_mw": "nm"}
reps = {}
for r in ll:
    if r["variable"] in VAR:
        F[f"series|ercot_large_load_status|ercot:large_load|{r['variable']}|{r['ts_utc'][:10]}T00:00:00Z"] = float(r["value"])
        reps.setdefault(r["ts_utc"][:10], {})[VAR[r["variable"]]] = float(r["value"])
full = sorted(d for d, v in reps.items() if all(k in v for k in ("approved", "non", "sim")))
last = reps[full[-1]]
F["ercot|observed_share_pct"] = jsround(100 * last["non"] / last["approved"])
F["ercot|reports"] = len(reps)
F["ercot|impossible_reports"] = sum(1 for v in reps.values() if "sim" in v and "non" in v and v["sim"] > v["non"])
MONTHS = ["January", "February", "March", "April", "May", "June", "July", "August", "September", "October", "November", "December"]
written = {r["ts_utc"][:10]: r["x_month_as_written"] for r in ll if r.get("x_month_as_written", "")}
mism = 0
for d, w in written.items():
    parts = w.split(" ")
    if len(parts) == 2 and parts[0] in MONTHS and not (parts[1] == d[:4] and MONTHS.index(parts[0]) == int(d[5:7]) - 1):
        mism += 1
F["ercot|month_mismatch_reports"] = mism
N["ercot_newest_full"] = full[-1]
N["ercot_share_simultaneous_pct"] = 100 * last["sim"] / last["approved"]

# --- the queue sites and the view by grid (note 7.8), the queues not held
qp = [r for r in table("datacenter_queue_positions") if r["entity_id"].split("_", 1)[0] in ("ercot", "caiso", "spp")]
act = [r for r in table("ercot_interconnection_queue") if r["status"] == "active"]
for r in qp:
    if r["capacity_mw"] != "":
        F[f"entity|{r['entity_id'].split('_', 1)[0]}_interconnection_queue|{r['entity_id']}|capacity_mw"] = float(r["capacity_mw"])
grp = {}
for r in qp:
    g, z = r["entity_id"].split("_", 1)[0], (r.get("zone", "") or "").strip() or "-"
    e = grp.setdefault((g, z), dict(sites=0, sites_with_mw=0, mw_asked=0.0))
    e["sites"] += 1
    if r["capacity_mw"] != "":
        e["sites_with_mw"] += 1
        e["mw_asked"] += float(r["capacity_mw"])
for (g, z), e in grp.items():
    a = [x for x in act if g == "ercot" and (z == "-" or (x.get("zone", "") or "").strip() == z)]
    e["active_positions"] = len(a)
    e["active_mw"] = sum(float(x["capacity_mw"]) for x in a if x["capacity_mw"] != "")
    for k, v in e.items():
        F[f"dcq|{g}|{z}|{k}"] = v

# --- what a flat load paid at each ERCOT load zone (the calculator's rule, note 7.8; datacenter_pays_algorithm.md)
D = os.path.join(SITE, "data", "datacenter")
IDX = json.load(open(os.path.join(D, "index.json"), encoding="utf-8"))
DAYS = [31, 28, 31, 30, 31, 30, 31, 31, 30, 31, 30, 31]


def leap(y):
    return (y % 4 == 0 and y % 100 != 0) or y % 400 == 0


def monthly(grid_id, region, buy):
    gi = IDX["grids"][grid_id]
    out = []
    for y in range(min(gi["years"]), max(gi["years"]) + 1):
        p = os.path.join(D, f"{grid_id}_{y}.json")
        if not os.path.exists(p):
            continue
        f = json.load(open(p, encoding="utf-8"))
        s = f["regions"].get(region, {}).get(buy)
        if not s:
            continue
        pr = [None] * f["hours"]
        for i, v in enumerate(s["v"]):
            pr[s["s"] + i] = v
        st = 0
        for m in range(12):
            n = 24 * (DAYS[m] + (1 if m == 1 and leap(y) else 0))
            vals = [v for v in pr[st:st + n] if v is not None]
            st += n
            if vals:
                out.append(dict(m=f"{y}-{m + 1:02d}", held=len(vals), total=sum(vals), complete=len(vals) >= 0.95 * n))
    return out


def l12(ms):
    by = {r["m"]: r for r in ms}
    for r in reversed(ms):
        if not r["complete"]:
            continue
        y, mo = int(r["m"][:4]), int(r["m"][5:7])
        win = []
        for k in range(12):
            mm = mo - 1 - k
            yy = y + mm // 12
            win.append(by.get(f"{yy}-{mm % 12 + 1:02d}"))
        if all(w and w["complete"] for w in win):
            return list(reversed(win))
    return None


gi = IDX["grids"]["ercot"]
for reg in gi["regions"]:
    if reg.get("kind", "") not in ("", "zone"):
        continue
    buy, ms = "rt", monthly("ercot", reg["id"], "rt") if reg.get("rt") else []
    w = l12(ms)
    if not w and reg.get("da"):
        buy, ms = "da", monthly("ercot", reg["id"], "da")
        w = l12(ms)
    if not w:
        continue
    F[f"dcpow|ercot|{reg['id']}|per"] = sum(x["total"] for x in w) / sum(x["held"] for x in w)
    N[f"dcpow|ercot|{reg['id']}|span"] = f"{buy} {w[0]['m']} to {w[-1]['m']}"
    # the chart shows the complete calendar years (twelve complete months), at most the last eight
    full_years = [y for y in sorted({x["m"][:4] for x in ms}) if sum(1 for x in ms if x["m"].startswith(y) and x["complete"]) == 12]
    for y in full_years[-8:]:
        done = [x for x in ms if x["m"].startswith(y) and x["complete"]]
        F[f"dcpow|ercot|{reg['id']}|year|{y}"] = sum(x["total"] for x in done) / sum(x["held"] for x in done)

print(json.dumps({"today": TODAY, "figures": F, "notes": N}, sort_keys=True))

"""Session 10227 (play audit): the prices the audit needs, read only from the main copy's warehouse/output (never written).
Streams each table line by line. Writes runs/c10227/extract.json.

    python extract.py <main output dir> <worktree root>
"""
import json
import os
import sys
from datetime import datetime, timedelta, timezone
from zoneinfo import ZoneInfo

OUT_DIR, ROOT = sys.argv[1], sys.argv[2]
HERE = os.path.dirname(os.path.abspath(__file__))
CT, PT = ZoneInfo("America/Chicago"), ZoneInfo("America/Los_Angeles")
levels = json.load(open(os.path.join(ROOT, "site", "data", "battery_levels.json"), encoding="utf-8"))["levels"]
ercot_dates = {l["date"] for l in levels if l.get("grid", "ERCOT") == "ERCOT"}
caiso_dates = {l["date"] for l in levels if l.get("grid") == "CAISO"}

_cache = {}


def local_day(ts, tz):
    k = (ts[:13], tz.key)
    if k not in _cache:
        t = datetime.strptime(ts[:13], "%Y-%m-%dT%H").replace(tzinfo=timezone.utc)
        _cache[k] = t.astimezone(tz).strftime("%Y-%m-%d")
    return _cache[k]


def need(day, tz):
    a = datetime.strptime(day, "%Y-%m-%d").replace(tzinfo=tz)
    b = (a + timedelta(days=1)).replace(tzinfo=tz)
    return int((b.astimezone(timezone.utc) - a.astimezone(timezone.utc)).total_seconds() // 900)


def rows(name):
    with open(os.path.join(OUT_DIR, name), encoding="utf-8") as f:
        head = None
        for ln in f:
            if ln.startswith("#"):
                continue
            if head is None:
                head = ln.rstrip("\n").split(",")
                continue
            yield ln


out = {"ercot_hist_days": {}, "famous_ercot": {}, "recent_rt": {}, "dam": {}, "kinds": {}}
ZONES = ("ercot:HB_HUBAVG,", "ercot:LZ_HOUSTON,", "ercot:LZ_NORTH,", "ercot:LZ_SOUTH,", "ercot:LZ_WEST,")

# 1. the history: every complete day's mean of HB_HUBAVG real time; the famous days' prices at the hub and four zones
days = {}
kinds = set()
for ln in rows("ercot_all_hub_prices_history.csv"):
    if not ln.startswith(ZONES):
        continue
    e, v, ts, val, rest = ln.split(",", 4)
    m = rest.split(",")[3] if rest.count(",") >= 3 else ""
    kinds.add(f"{e}|{v}|{m}")
    d = local_day(ts, CT)
    if e == "ercot:HB_HUBAVG" and v == "spp_rtm":
        x = days.setdefault(d, [0.0, 0, 1e18, -1e18])
        f = float(val)
        x[0] += f; x[1] += 1; x[2] = min(x[2], f); x[3] = max(x[3], f)
    if d in ercot_dates:
        out["famous_ercot"].setdefault(d, {}).setdefault(f"{e}|{v}", []).append([ts, float(val)])
out["kinds"]["history"] = sorted(kinds)
for d, (s, n, lo, hi) in days.items():
    if n == need(d, CT):
        out["ercot_hist_days"][d] = [s / n, lo, hi, n]

# 2. the live table: the complete ERCOT days at the hub (the newest is the proxy for today's level) and the zones
kinds = set()
rt = {}
for ln in rows("iso_rtm_hub_prices.csv"):
    e, v, ts, val, rest = ln.split(",", 4)
    if not e.startswith("ercot:"):
        continue
    kinds.add(f"{e}|{v}")
    if v != "spp_rtm":
        continue
    rt.setdefault(e, {}).setdefault(local_day(ts, CT), []).append([ts, float(val)])
out["kinds"]["rtm"] = sorted(kinds)
hub = rt.get("ercot:HB_HUBAVG", {})
full = sorted(d for d, r in hub.items() if len(r) == need(d, CT))
out["recent_full_days"] = full
for d in full[-3:]:
    out["recent_rt"][d] = {e: sorted(rt[e][d]) for e in rt if d in rt[e]}

# 3. day-ahead: ERCOT at the hub for the famous ERCOT days and the newest days; CAISO SP15 for its two days
kinds = set()
want_ct = ercot_dates | set(full[-3:])
for ln in rows("iso_dam_hub_prices.csv"):
    e, v, ts, val, rest = ln.split(",", 4)
    kinds.add(f"{e}|{v}")
    if e == "ercot:HB_HUBAVG":
        d = local_day(ts, CT)
        if d in want_ct:
            out["dam"].setdefault(d, {}).setdefault(f"{e}|{v}", []).append([ts, float(val)])
    elif e == "caiso:TH_SP15_GEN-APND":
        d = local_day(ts, PT)
        if d in caiso_dates:
            out["dam"].setdefault(d, {}).setdefault(f"{e}|{v}", []).append([ts, float(val)])
out["kinds"]["dam"] = sorted(kinds)

json.dump(out, open(os.path.join(HERE, "extract.json"), "w"), indent=0)
print("history complete days:", len(out["ercot_hist_days"]), min(out["ercot_hist_days"]), max(out["ercot_hist_days"]))
print("recent full days:", full[-5:])
print("famous days held:", {d: {k: len(v) for k, v in x.items()} for d, x in out["famous_ercot"].items()})
print("dam held:", {d: {k: len(v) for k, v in x.items()} for d, x in out["dam"].items()})
print("kinds:", {k: v[:40] for k, v in out["kinds"].items()})

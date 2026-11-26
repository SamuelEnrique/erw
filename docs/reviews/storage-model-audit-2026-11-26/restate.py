"""Session 10212 (storage audit): every figure of /storage's default view (the fleet tab), restated independently.

    python restate.py <trial dir> <drawn n.json> <drawn html> <out json>

Standard library only, none of the site's code and none of the builders': written from docs/methods/storage.md and the
page's words. The fleet from the EIA-860M tables themselves (not storage_capacity); the daily cycle from the hourly
EIA-930 series and CAISO's 5-minute values (not storage_daily_cycle). "Now" is 2026-11-05 12:00 UTC, as drawn.
Prints each figure, the page's, the restated and whether they agree (raw value, and the shown text).
"""
import csv
import datetime as dt
import json
import os
import re
import sys
from collections import defaultdict
from decimal import Decimal, ROUND_HALF_UP
from zoneinfo import ZoneInfo

trial, npath, hpath, out = sys.argv[1:5]
UTC = dt.timezone.utc
NOW = dt.datetime(2026, 11, 5, 12, 0, tzinfo=UTC)


def read(name):
    with open(os.path.join(trial, name + ".csv"), encoding="utf-8", newline="") as f:
        return list(csv.DictReader(line for line in f if not line.startswith("#")))


def d(s):
    return Decimal(s) if s not in ("", None) else None


def shown(v):
    """The page's number format: a whole number with separators, else two decimals with separators."""
    v = Decimal(str(v))
    if v == v.to_integral_value():
        return f"{int(v):,}"
    return f"{v.quantize(Decimal('0.01'), rounding=ROUND_HALF_UP):,}"


R = {}  # key -> (raw text, shown text)


def put(key, value, text=None):
    v = Decimal(str(value))
    raw = format(v.normalize(), "f") if v != v.to_integral_value() else str(int(v))
    R[key] = (raw, text if text is not None else shown(v))


# ---- the fleet, from EIA-860M ----------------------------------------------------------------------------------
units = []
for t, kind in (("eia860m_operating_generators", "op"), ("eia860m_planned_generators", "pl"), ("eia860m_retired_generators", "rt")):
    for x in read(t):
        if x["prime_mover"] != "BA":
            continue
        if kind == "op":
            st = "operating"
        elif kind == "rt":
            st = "retired"
        else:  # EIA's codes: U, V, TS under construction; P, L, T not yet
            st = "under_construction" if x["eia_status"] in ("U", "V", "TS") else "planned"
        units.append(dict(st=st, mw=d(x["nameplate_mw"]), mwh=d(x.get("energy_capacity_mwh", "")), ba=x["balancing_authority"],
                          state=x["state"], year=(x.get("planned_operation_date") or "")[:4], vint=x["vintage"],
                          net=d(x.get("net_summer_mw", "")), eia=x["eia_status"]))
ISO = {"CISO": "CAISO", "ERCO": "ERCOT", "ISNE": "ISO-NE", "MISO": "MISO", "NYIS": "NYISO", "PJM": "PJM", "SWPP": "SPP"}


def mw(us):
    return sum((u["mw"] for u in us), Decimal(0))


def r1(v):
    return v.quantize(Decimal("0.1"), rounding=ROUND_HALF_UP)


for s in ("operating", "under_construction", "planned", "retired"):
    us = [u for u in units if u["st"] == s]
    put(f"storage|mw|{s}", r1(mw(us)))
    put(f"storage|n|{s}", len(us))
    w = [u for u in us if u["mwh"] is not None]
    if w:
        put(f"storage|mwh|{s}", r1(sum((u["mwh"] for u in w), Decimal(0))))
        put(f"storage|n_mwh|{s}", len(w))
for iso in ["CAISO", "ERCOT", "ISO-NE", "MISO", "NYISO", "PJM", "SPP", "none"]:
    for s in ("operating", "under_construction", "planned"):
        us = [u for u in units if u["st"] == s and (ISO.get(u["ba"], "none") == iso)]
        put(f"storage|iso_mw|{iso}|{s}", r1(mw(us)))
op_state = defaultdict(Decimal)
for u in units:
    if u["st"] == "operating" and u["state"]:
        op_state[u["state"]] += u["mw"]
states = sorted({u["state"] for u in units if u["state"]}, key=lambda s: (-op_state.get(s, Decimal(0)), s))[:15]
for s in states:
    put(f"storage|state_mw|{s}|operating", r1(mw([u for u in units if u["state"] == s and u["st"] == "operating"])))
    put(f"storage|state_mw|{s}|build", r1(mw([u for u in units if u["state"] == s and u["st"] in ("under_construction", "planned")])))
for y in sorted({u["year"] for u in units if u["st"] in ("under_construction", "planned") and u["year"]}):
    put(f"storage|year_mw|{y}", r1(mw([u for u in units if u["st"] in ("under_construction", "planned") and u["year"] == y])))
MONTHS = ["January", "February", "March", "April", "May", "June", "July", "August", "September", "October", "November", "December"]
v = max(u["vint"] for u in units if u["st"] == "operating")
EXTRA = {"inventory": f"{MONTHS[int(v[5:7]) - 1]} {v[:4]}"}

# ---- the daily cycle -------------------------------------------------------------------------------------------
TZ = {"eia930:US48": "America/New_York", "eia930:ERCO": "America/Chicago", "eia930:ISNE": "America/New_York",
      "eia930:MISO": "Etc/GMT+5", "eia930:SWPP": "America/Chicago"}


def ts(s):
    return dt.datetime.strptime(s, "%Y-%m-%dT%H:%M:%SZ").replace(tzinfo=UTC)


def hours_in(day, tz):
    z = ZoneInfo(tz)
    a = dt.datetime(day.year, day.month, day.day, tzinfo=z)
    nxt = day + dt.timedelta(days=1)
    b = dt.datetime(nxt.year, nxt.month, nxt.day, tzinfo=z)
    return int((b.astimezone(UTC) - a.astimezone(UTC)).total_seconds() // 3600)


def h3(x):
    return Decimal(repr(float(x))).quantize(Decimal("0.001"), rounding=ROUND_HALF_UP)


def day_figs(hours):
    """hours: list of (utc datetime, local hour, value). Returns the five figures of a day."""
    pos = sum(max(v, 0.0) for _, _, v in hours)
    neg = sum(-min(v, 0.0) for _, _, v in hours)
    f = {"mwh_discharged": h3(pos), "mwh_charged": h3(neg)}
    if max(v for _, _, v in hours) > 0:
        f["peak_discharge_hour"] = sorted(hours, key=lambda h: (-h[2], h[0]))[0][1]
    if min(v for _, _, v in hours) < 0:
        f["peak_charge_hour"] = sorted(hours, key=lambda h: (h[2], h[0]))[0][1]
    if pos > 0 and neg > 0:
        f["round_trip_ratio"] = h3(pos / neg)
    return f


hourly = defaultdict(list)
for x in read("eia930_all_storage"):
    hourly[x["entity"]].append((ts(x["ts_utc"]), float(x["value"])))
cycle = {}  # entity -> {day: figs}
for e, rows in hourly.items():
    tz = ZoneInfo(TZ[e])
    newest = max(t for t, _ in rows)
    by = defaultdict(list)
    for t, val in rows:
        lt = t.astimezone(tz)
        by[lt.date()].append((t, lt.hour, val))
    days = {}
    for day, hs in by.items():
        if len(hs) != hours_in(day, TZ[e]):
            continue
        z = ZoneInfo(TZ[e])
        nxt = day + dt.timedelta(days=1)
        end = dt.datetime(nxt.year, nxt.month, nxt.day, tzinfo=z).astimezone(UTC)
        if newest - end < dt.timedelta(hours=47):  # the 48-hour settling rule of the method note (session 7050)
            continue
        days[day] = day_figs(hs)
    cycle[e] = days
# CAISO: hourly means of twelve 5-minute values, complete Pacific days
five = []
for x in read("caiso_battery_storage"):
    if x["variable"] == "batteries_mw":
        five.append((ts(x["ts_utc"]), float(x["value"])))
pac = ZoneInfo("America/Los_Angeles")
byday = defaultdict(list)
for t, val in five:
    byday[t.astimezone(pac).date()].append((t, val))
cdays = {}
for day, xs in byday.items():
    if len(xs) != 12 * hours_in(day, "America/Los_Angeles"):
        continue
    hrs = defaultdict(list)
    for t, val in xs:
        hrs[t.replace(minute=0)].append(val)
    hs = [(h, h.astimezone(pac).hour, sum(vs) / len(vs)) for h, vs in sorted(hrs.items())]
    cdays[day] = day_figs(hs)
cycle["caiso:ISO"] = cdays
since45 = (NOW - dt.timedelta(days=45)).date()
SPARK = {}
for e, days in cycle.items():
    shown_days = sorted(k for k in days if k >= since45)
    if not shown_days:
        continue
    last = shown_days[-1]
    f = days[last]
    key = f"{last.isoformat()}T00:00:00Z"
    for var, val in f.items():
        if var.startswith("peak"):
            put(f"series|storage_daily_cycle|{e}|{var}|{key}", val, str(val))
        else:
            put(f"series|storage_daily_cycle|{e}|{var}|{key}", val)
    sp = shown_days[-30:]
    held = set(sp)
    gaps = []
    a = sp[0]
    while a < sp[-1]:
        if a not in held:
            gaps.append(a.isoformat())
        a += dt.timedelta(days=1)
    SPARK[e] = dict(first=sp[0].isoformat(), last=sp[-1].isoformat(), n=len(sp), not_held=gaps,
                    values=[float(days[k]["mwh_discharged"]) for k in sp])
EXTRA["spark"] = SPARK
EXTRA["no_charge"] = [n for e, n in (("eia930:ERCO", "ERCOT"), ("eia930:ISNE", "ISO-NE"), ("eia930:MISO", "MISO"), ("eia930:SWPP", "SPP"))
                      if e in cycle and cycle[e] and cycle[e][max(k for k in cycle[e] if k >= since45)]["mwh_charged"] == 0]
EXTRA["newest_hour"] = max(t for rows in hourly.values() for t, _ in rows if t >= NOW - dt.timedelta(days=31)).strftime("%Y-%m-%d %H:%M")

# ---- compare ---------------------------------------------------------------------------------------------------
page = json.load(open(npath, encoding="utf-8"))
html = open(hpath, encoding="utf-8").read()
agree = differ = 0
lines = []
for k, p in page.items():
    if k not in R:
        lines.append(f"NOT RESTATED {k}: page {p}")
        differ += 1
        continue
    raw, txt = R[k]
    ok_raw = Decimal(p["raw"]) == Decimal(raw)
    ok_txt = p["shown"] == txt
    if ok_raw and ok_txt:
        agree += 1
    else:
        differ += 1
        lines.append(f"DIFFER {k}: page {p['raw']} '{p['shown']}', restated {raw} '{txt}'")
for k in R:
    if k not in page:
        lines.append(f"restated, not on the page: {k} {R[k]}")
# the words-level figures
checks = []
checks.append(("inventory month", f"of {EXTRA['inventory']}, nameplate" in html.replace("&#x27;", "'")))
checks.append(("24-hour window end", f"the 24 hours to {EXTRA['newest_hour']} UTC" in html))
nc = EXTRA["no_charge"]
named = "none" if not nc else nc[0] if len(nc) == 1 else ", ".join(nc[:-1]) + " and " + nc[-1]
checks.append((f"no-charge grids named '{named}'", f"({named} on this day)" in html))
for e, sp in SPARK.items():
    label = {"eia930:US48": "US Lower 48", "eia930:ERCO": "ERCOT", "eia930:ISNE": "ISO-NE", "eia930:MISO": "MISO", "eia930:SWPP": "SPP", "caiso:ISO": "CAISO"}[e]
    runs = []
    for g in sp["not_held"]:
        if runs and (dt.date.fromisoformat(runs[-1][1]) + dt.timedelta(days=1)).isoformat() == g:
            runs[-1][1] = g
        else:
            runs.append([g, g])
    gaps = "; not held: " + ", ".join(a if a == b else f"{a} to {b}" for a, b in runs) if runs else ""
    f2 = lambda v: f"{Decimal(str(v)).quantize(Decimal('0.01'), rounding=ROUND_HALF_UP)}"  # noqa: E731
    head = f"{label} battery MWh discharged per day, the last 30 days held{gaps}: "
    want = f"{head}{sp['first']} {f2(sp['values'][0])} to {sp['last']} {f2(sp['values'][-1])}"
    days_sp = sorted(k for k in cycle[e] if k >= since45)[-30:]
    vals_ok = all(f"{head}{k.isoformat()} {f2(val)}<" in html for k, val in zip(days_sp, sp["values"]))
    checks.append((f"spark {label}: span {sp['first']} to {sp['last']}, {sp['n']} values, gaps {runs}", want in html and vals_ok))
for name, ok in checks:
    lines.append(f"{'agree' if ok else 'DIFFER'} words: {name}")
    if ok:
        agree += 1
    else:
        differ += 1
summary = f"{agree} agree, {differ} differ, of {len(page)} marked figures and {len(checks)} words-level figures"
print(summary)
print("\n".join(lines))
json.dump(dict(summary=summary, restated={k: v for k, v in R.items()}, extra=EXTRA), open(out, "w", encoding="utf-8"), indent=1, default=str)

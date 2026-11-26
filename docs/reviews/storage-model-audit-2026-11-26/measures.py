"""Session 10212 (storage audit): one rule of the storage page changed at a time, and what each is worth.

    python measures.py <trial dir> <main copy warehouse/output> <out json>

Standard library only. Reads the trial folder's copies (EIA-860M of September 2026; EIA-930 from 2025-11-01; CAISO's
5-minute values from 2025-11-01) and, read only, the main copy's eia860m_retired_generators_all (every retired generator
EIA lists, August 2026). "Now" is 2026-11-05 12:00 UTC, as drawn.
"""
import csv
import datetime as dt
import json
import os
import sys
from collections import defaultdict
from decimal import Decimal, ROUND_HALF_UP
from zoneinfo import ZoneInfo

trial, main, out = sys.argv[1:4]
UTC = dt.timezone.utc
NOW = dt.datetime(2026, 11, 5, 12, 0, tzinfo=UTC)
M = {}


def read(path):
    with open(path, encoding="utf-8", newline="") as f:
        return list(csv.DictReader(line for line in f if not line.startswith("#")))


def D(s):
    return Decimal(s) if s not in ("", None) else None


def r1(v):
    return float(Decimal(v).quantize(Decimal("0.1"), rounding=ROUND_HALF_UP))


op = [x for x in read(os.path.join(trial, "eia860m_operating_generators.csv")) if x["prime_mover"] == "BA"]
pl = [x for x in read(os.path.join(trial, "eia860m_planned_generators.csv")) if x["prime_mover"] == "BA"]
rt = [x for x in read(os.path.join(trial, "eia860m_retired_generators.csv")) if x["prime_mover"] == "BA"]
sol = [x for x in read(os.path.join(trial, "eia860m_operating_generators.csv")) if x["technology_group"] == "solar" and x["prime_mover"] != "BA"]

# 1. nameplate against operable: EIA's status codes inside "operating", and net summer capacity
by = defaultdict(lambda: [0, Decimal(0)])
for x in op:
    by[x["eia_status"]][0] += 1
    by[x["eia_status"]][1] += D(x["nameplate_mw"])
M["operating_by_eia_status"] = {k: dict(units=v[0], mw=r1(v[1])) for k, v in sorted(by.items())}
M["operating_by_eia_status_labels"] = sorted({(x["eia_status"], x["eia_status_label"]) for x in op})
nameplate = sum(D(x["nameplate_mw"]) for x in op)
with_net = [x for x in op if D(x["net_summer_mw"]) is not None]
M["net_summer"] = dict(units_with=len(with_net), nameplate_of_those=r1(sum(D(x["nameplate_mw"]) for x in with_net)),
                       net_summer=r1(sum(D(x["net_summer_mw"]) for x in with_net)), nameplate_all=r1(nameplate))
M["operating_states_outside_lower48"] = {s: r1(sum(D(x["nameplate_mw"]) for x in op if x["state"] == s)) for s in ("AK", "HI", "PR")}

# 2. which part of the operating fleet EIA-930's battery series can see
NO_BAT = {"CISO", "NYIS", "PJM"}
IN_TABLE = {"ERCO", "ISNE", "MISO", "SWPP"}
mw_ba = defaultdict(Decimal)
for x in op:
    mw_ba[x["balancing_authority"]] += D(x["nameplate_mw"])
M["fleet_share"] = dict(no_bat_series_mw=r1(sum(mw_ba[b] for b in NO_BAT)), four_in_table_mw=r1(sum(mw_ba[b] for b in IN_TABLE)),
                        other_mw=r1(sum(v for b, v in mw_ba.items() if b not in NO_BAT | IN_TABLE)),
                        no_bat_share_pct=r1(100 * sum(mw_ba[b] for b in NO_BAT) / nameplate),
                        lower48_outside_no_bat_mw=r1(sum(D(x["nameplate_mw"]) for x in op if x["balancing_authority"] not in NO_BAT and x["state"] not in ("AK", "HI", "PR"))))

# 3. the hourly series: EIA-930 and CAISO
hourly = defaultdict(dict)
for x in read(os.path.join(trial, "eia930_all_storage.csv")):
    hourly[x["entity"]][dt.datetime.strptime(x["ts_utc"], "%Y-%m-%dT%H:%M:%SZ").replace(tzinfo=UTC)] = float(x["value"])
five = defaultdict(list)
for x in read(os.path.join(trial, "caiso_battery_storage.csv")):
    if x["variable"] == "batteries_mw":
        t = dt.datetime.strptime(x["ts_utc"], "%Y-%m-%dT%H:%M:%SZ").replace(tzinfo=UTC)
        five[t.replace(minute=0)].append(float(x["value"]))
caiso = {t: sum(v) / len(v) for t, v in five.items() if len(v) == 12}
hourly["caiso:ISO"] = caiso
TZ = {"eia930:US48": "America/New_York", "eia930:ERCO": "America/Chicago", "eia930:ISNE": "America/New_York",
      "eia930:MISO": "Etc/GMT+5", "eia930:SWPP": "America/Chicago", "caiso:ISO": "America/Los_Angeles"}

# 3a. US Lower 48 against CAISO's own and the four ISOs, over the chart's 30 days (UTC hours both hold)
lo = NOW - dt.timedelta(days=31)
common = sorted(t for t in hourly["eia930:US48"] if t >= lo and t in caiso and all(t in hourly[e] for e in ("eia930:ERCO", "eia930:MISO")))
pos = lambda v: max(v, 0.0)  # noqa: E731
M["us48_vs_caiso_30d"] = dict(hours=len(common), us48_discharged_mwh=round(sum(pos(hourly["eia930:US48"][t]) for t in common)),
                              caiso_discharged_mwh=round(sum(pos(caiso[t]) for t in common)),
                              us48_peak_mw=max(hourly["eia930:US48"][t] for t in common), caiso_peak_hourly_mw=round(max(caiso[t] for t in common)),
                              hours_caiso_above_us48=sum(1 for t in common if caiso[t] > hourly["eia930:US48"][t] and caiso[t] > 0))

# 3b. never negative: share of zero hours and negative hours, by series, over the year held
M["sign_by_series"] = {}
for e, h in hourly.items():
    vals = list(h.values())
    M["sign_by_series"][e] = dict(hours=len(vals), negative=sum(v < 0 for v in vals), zero=sum(v == 0 for v in vals), positive=sum(v > 0 for v in vals),
                                  first_negative=min((t for t, v in h.items() if v < 0), default=None))


# 3c. days: the newest complete local day, the newest the page shows (the 48-hour rule), the fall-back day's extra hour
def hours_in(day, tz):
    z = ZoneInfo(tz)
    nxt = day + dt.timedelta(days=1)
    # aware datetimes of one tzinfo subtract on the wall clock in Python, so both go to UTC first
    a = dt.datetime(day.year, day.month, day.day, tzinfo=z).astimezone(UTC)
    b = dt.datetime(nxt.year, nxt.month, nxt.day, tzinfo=z).astimezone(UTC)
    return int((b - a).total_seconds() // 3600)


days = {}
M["newest_days"] = {}
for e, h in hourly.items():
    z = ZoneInfo(TZ[e])
    byday = defaultdict(list)
    for t, v in h.items():
        byday[t.astimezone(z).date()].append((t, v))
    complete = sorted(d for d, xs in byday.items() if len(xs) == hours_in(d, TZ[e]))
    newest = max(h)
    def end_of(d):
        n = d + dt.timedelta(days=1)
        return dt.datetime(n.year, n.month, n.day, tzinfo=z).astimezone(UTC)
    settled = [d for d in complete if newest - end_of(d) >= dt.timedelta(hours=47)]
    days[e] = (byday, complete)
    M["newest_days"][e] = dict(newest_hour=newest.isoformat(), newest_complete=str(complete[-1]), newest_settled=str(settled[-1]) if e != "caiso:ISO" else "no rule (CAISO)")

# the newest days of each EIA-930 series, settled or not: the day's discharged MWh and its hours above zero
M["newest_days_values"] = {}
for e in ("eia930:ERCO", "eia930:ISNE", "eia930:MISO", "eia930:SWPP", "eia930:US48"):
    byday, complete = days[e]
    M["newest_days_values"][e] = {str(d): dict(discharged=round(sum(max(v, 0) for _, v in byday[d])), hours_above_zero=sum(1 for _, v in byday[d] if v > 0))
                                  for d in complete[-8:]}

# the fall-back day of 2026 (1 November), its second 01:00 hour
fb = {}
for e in ("eia930:US48", "eia930:ERCO", "eia930:ISNE", "eia930:SWPP"):
    byday, _ = days[e]
    xs = sorted(byday[dt.date(2026, 11, 1)])
    z = ZoneInfo(TZ[e])
    ones = [(t, v) for t, v in xs if t.astimezone(z).hour == 1]
    dis = sum(pos(v) for _, v in xs)
    chg = sum(-min(v, 0) for _, v in xs)
    fb[e] = dict(hours=len(xs), discharged=dis, charged=chg, hour_01_values=[v for _, v in ones],
                 discharged_24h=dis - pos(ones[-1][1]) if len(ones) == 2 else None)
M["fall_back_2026_11_01"] = fb

# 3d. out over in: each day's against the 30 days' energy ratio (the page's 30 days held, complete settled days)
M["out_over_in"] = {}
for e in ("eia930:ERCO", "eia930:MISO", "caiso:ISO"):
    byday, complete = days[e]
    keep = [d for d in complete if d >= (NOW - dt.timedelta(days=45)).date()]
    if e != "caiso:ISO":
        keep = [d for d in keep if str(d) <= M["newest_days"][e]["newest_settled"]]
    keep = keep[-30:]
    ratios, td, tc = [], 0.0, 0.0
    for d in keep:
        dis = sum(pos(v) for _, v in byday[d])
        chg = sum(-min(v, 0) for _, v in byday[d])
        td += dis
        tc += chg
        if dis > 0 and chg > 0:
            ratios.append(dis / chg)
    ratios.sort()
    M["out_over_in"][e] = dict(days=len(keep), first=str(keep[0]), last=str(keep[-1]), thirty_day=round(td / tc, 3), daily_min=round(ratios[0], 3),
                               daily_median=round(ratios[len(ratios) // 2], 3), daily_max=round(ratios[-1], 3))
# ERCOT over every month held in the year: discharged and charged
ec = defaultdict(lambda: [0.0, 0.0])
for t, v in hourly["eia930:ERCO"].items():
    k = t.astimezone(ZoneInfo("America/Chicago")).strftime("%Y-%m")
    ec[k][0] += pos(v)
    ec[k][1] += -min(v, 0)
M["ercot_months"] = {k: dict(discharged=round(a), charged=round(b)) for k, (a, b) in sorted(ec.items())}

# 4. planned units dated before the inventory month
vint = op[0]["vintage"]
past = [x for x in pl if x["planned_operation_date"][:7] < vint]
M["planned_dated_before_inventory"] = dict(units=len(past), mw=r1(sum(D(x["nameplate_mw"]) for x in past)),
                                           of_which_2026=r1(sum(D(x["nameplate_mw"]) for x in past if x["planned_operation_date"][:4] == "2026")),
                                           earliest=min((x["planned_operation_date"] for x in past), default=None),
                                           under_construction_mw=r1(sum(D(x["nameplate_mw"]) for x in past if x["eia_status"] in ("U", "V", "TS"))))
y26 = [x for x in pl if x["planned_operation_date"][:4] == "2026"]
M["planned_2026"] = dict(mw=r1(sum(D(x["nameplate_mw"]) for x in y26)), dated_before_inventory_mw=M["planned_dated_before_inventory"]["of_which_2026"])

# 5. retired: the table's window against every retired battery EIA lists
ra = [x for x in read(os.path.join(main, "eia860m_retired_generators_all.csv")) if x["prime_mover"] == "BA"]
M["retired"] = dict(window_units=len(rt), window_mw=r1(sum(D(x["nameplate_mw"]) for x in rt)),
                    window_dates=sorted(x["retirement_date"][:7] for x in rt),
                    all_units=len(ra), all_mw=r1(sum(D(x["nameplate_mw"]) for x in ra)), all_vintage=ra[0]["vintage"] if ra else None,
                    before_2025_units=sum(1 for x in ra if x["retirement_date"][:4] < "2025"),
                    before_2025_mw=r1(sum(D(x["nameplate_mw"]) for x in ra if x["retirement_date"][:4] < "2025")))
# the build-out's year ends with every retired battery put back (rule: units retired before 2025 counted until they retired)
early = {}
for y in range(2015, 2025):
    m = y * 12 + 11
    add = [x for x in ra if x["retirement_date"][:4] < "2025" and int(x["operating_year"]) * 12 + int(x["operating_month"]) - 1 <= m
           and (int(x["retirement_date"][:4]) * 12 + int(x["retirement_date"][5:7]) - 1) > m]
    base = [x for x in op + rt if int(x["operating_year"]) * 12 + int(x["operating_month"]) - 1 <= m
            and (not x.get("retirement_date") or (int(x["retirement_date"][:4]) * 12 + int(x["retirement_date"][5:7]) - 1) > m)]
    b = sum(D(x["nameplate_mw"]) for x in base)
    a = sum(D(x["nameplate_mw"]) for x in add)
    early[y] = dict(page_mw=r1(b), put_back_mw=r1(a), with_them=r1(b + a), pct=r1(100 * a / b) if b else None)
M["buildout_year_ends_with_retired"] = early

# 6. storage against solar: battery MW against solar MW, by grid, at the inventory month
REG = {"CISO": "caiso", "ERCO": "ercot", "ISNE": "isone", "MISO": "miso", "NYIS": "nyiso", "PJM": "pjm", "SWPP": "spp"}
g = defaultdict(lambda: [Decimal(0), Decimal(0), Decimal(0)])
for x in op:
    k = REG.get(x["balancing_authority"], "outside")
    for kk in (k, "us"):
        g[kk][0] += D(x["nameplate_mw"])
        g[kk][1] += D(x["energy_capacity_mwh"]) if D(x["energy_capacity_mwh"]) is not None else Decimal(0)
for x in sol:
    k = REG.get(x["balancing_authority"], "outside")
    for kk in (k, "us"):
        g[kk][2] += D(x["nameplate_mw"])
M["battery_vs_solar"] = {k: dict(battery_mw=r1(a), battery_mwh=r1(b), solar_mw=r1(c), mwh_per_solar_mw=round(float(b / c), 4) if c else None,
                                 battery_mw_over_solar_mw=round(float(a / c), 3) if c else None) for k, (a, b, c) in sorted(g.items())}

json.dump(M, open(out, "w", encoding="utf-8"), indent=1, default=str)
for k, v in M.items():
    print(k, json.dumps(v, default=str)[:900])

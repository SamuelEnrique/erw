#!/usr/bin/env python3
"""ERW, ruling impact for /prices (session 7587, 17 November 2026).

The four lines marked "Changes a figure" under /prices in docs/reviews/rulings-for-samuel-2026-11-17.md (branch
wip/7560-six-reads). Tables (warehouse/output, retrieved 13 November 2026): iso_dam_hub_prices (hourly day-ahead) and
iso_rtm_hub_prices (real time, 15-minute rows averaged to the hour), for the public grids only (ERCOT, CAISO, SPP); the
held grids (PJM, NYISO, ISO-NE) and MISO (paused) are not read. Hours are each grid's local clock.

    .venv/Scripts/python.exe runs/ruling_impact/prices_impact.py
"""
import csv
import datetime as dt
import os
import statistics
import zoneinfo
from collections import defaultdict

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
OUT = os.path.join(ROOT, "warehouse", "output")
TZ = {"ercot": "America/Chicago", "caiso": "America/Los_Angeles", "spp": "America/Chicago"}
HUBS = ["ercot:HB_HUBAVG", "ercot:HB_WEST", "ercot:HB_HOUSTON", "ercot:HB_NORTH", "caiso:TH_SP15_GEN-APND", "caiso:TH_NP15_GEN-APND", "spp:SPPNORTH_HUB", "spp:SPPSOUTH_HUB"]


def load(name, var_ok):
    acc = defaultdict(lambda: defaultdict(list))
    with open(os.path.join(OUT, name + ".csv"), encoding="utf-8", newline="") as f:
        for r in csv.DictReader(l for l in f if not l.startswith("#")):
            if r["entity"] not in HUBS or not var_ok(r["variable"]) or not r["value"]:
                continue
            acc[r["entity"]][r["ts_utc"][:13]].append(float(r["value"]))
    return {e: {h: sum(v) / len(v) for h, v in hs.items()} for e, hs in acc.items()}


DA = load("iso_dam_hub_prices", lambda v: v in ("spp_dam", "lmp_dam"))
RT = load("iso_rtm_hub_prices", lambda v: v in ("spp_rtm", "lmp_rtm_15m_mean"))


def local(e, h):
    t = dt.datetime(int(h[:4]), int(h[5:7]), int(h[8:10]), int(h[11:13]), tzinfo=dt.timezone.utc)
    return t.astimezone(zoneinfo.ZoneInfo(TZ[e.split(":")[0]]))


last = max(h for e in RT for h in RT[e])
end = dt.datetime(int(last[:4]), int(last[5:7]), int(last[8:10]), int(last[11:13]), tzinfo=dt.timezone.utc)
start = end - dt.timedelta(days=30)
win = lambda h: start.strftime("%Y-%m-%dT%H") < h <= end.strftime("%Y-%m-%dT%H")
print(f"day-ahead hubs: {sorted(DA)}; real-time hubs: {sorted(RT)}; the newest real-time hour {last}; the rolling 30 days from {start:%Y-%m-%d %H}:00 UTC")

print("\n== line 1: a calendar month's line (October 2026) under the rolling 30 days")
for src, D in (("real time", RT), ("day-ahead", DA)):
    for e in HUBS:
        if e not in D:
            continue
        oct_ = [v for h, v in D[e].items() if local(e, h).strftime("%Y-%m") == "2026-10"]
        r30 = [v for h, v in D[e].items() if win(h)]
        if oct_ and r30:
            print(f"{src} {e}: rolling 30 days {statistics.fmean(r30):.2f} USD/MWh ({len(r30)} hours); October 2026 {statistics.fmean(oct_):.2f} ({len(oct_)} hours; "
                  f"{(statistics.fmean(oct_) / statistics.fmean(r30) - 1) * 100:+.1f} percent); October's low {min(oct_):.2f}, high {max(oct_):.2f}")

print("\n== line 2: a second hub, A less B over the hours both hold (ERCOT West less Houston, the rolling 30 days)")
for src, D in (("real time", RT), ("day-ahead", DA)):
    a, b = D.get("ercot:HB_WEST", {}), D.get("ercot:HB_HOUSTON", {})
    both = sorted(h for h in a if h in b and win(h))
    d = [a[h] - b[h] for h in both]
    if d:
        lo, hi = min(range(len(d)), key=lambda i: d[i]), max(range(len(d)), key=lambda i: d[i])
        print(f"{src}: {len(d)} hours; mean West less Houston {statistics.fmean(d):+.2f} USD/MWh; median {statistics.median(d):+.2f}; lowest {d[lo]:+.2f} ({both[lo]}Z), highest {d[hi]:+.2f} ({both[hi]}Z); "
              f"hours West below Houston {sum(1 for x in d if x < 0)}")

print("\n== line 3: SPP's hub pages and /network on SPP's real-time table instead of day-ahead")
for e in ("spp:SPPNORTH_HUB", "spp:SPPSOUTH_HUB"):
    da, rt = DA.get(e, {}), RT.get(e, {})
    both = [h for h in rt if h in da and win(h)]
    if both:
        m_da, m_rt = statistics.fmean(da[h] for h in both), statistics.fmean(rt[h] for h in both)
        diff = [rt[h] - da[h] for h in both]
        print(f"{e}: rolling 30 days over {len(both)} hours both hold: day-ahead {m_da:.2f}, real time {m_rt:.2f} USD/MWh ({(m_rt / m_da - 1) * 100:+.1f} percent); "
              f"an hour's real time less day-ahead from {min(diff):+.2f} to {max(diff):+.2f}; latest hour {max(both)}Z: {da[max(both)]:.2f} -> {rt[max(both)]:.2f}")
    elif rt:
        print(f"{e}: real-time rows {len(rt)} hours, day-ahead rows {len(da)}: no hour both hold in the window")
    rth = sorted(rt)
    if rth:
        print(f"   SPP real-time history held: {rth[0]} to {rth[-1]} ({len(rth)} hours), which the hub pages would gain")

print("\n== line 4: the hub's table split into on-peak (06:00 to 22:00 local, Monday to Friday) and off-peak hours")
for src, D in (("real time", RT), ("day-ahead", DA)):
    for e in HUBS:
        if e not in D:
            continue
        hs = [(local(e, h), v) for h, v in D[e].items() if win(h)]
        pk = [v for t, v in hs if t.weekday() < 5 and 6 <= t.hour < 22]
        op = [v for t, v in hs if not (t.weekday() < 5 and 6 <= t.hour < 22)]
        if pk and op:
            allm = statistics.fmean(v for _, v in hs)
            print(f"{src} {e}: all hours {allm:.2f}; on-peak {statistics.fmean(pk):.2f} ({len(pk)} h, {(statistics.fmean(pk) / allm - 1) * 100:+.1f} percent); "
                  f"off-peak {statistics.fmean(op):.2f} ({len(op)} h, {(statistics.fmean(op) / allm - 1) * 100:+.1f} percent)")

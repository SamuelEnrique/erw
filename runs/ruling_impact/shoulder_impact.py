#!/usr/bin/env python3
"""ERW, ruling impact for /shoulder (session 7572, 17 November 2026).

The six lines marked "Changes a figure" under /shoulder in docs/reviews/rulings-for-samuel-2026-11-17.md (branch
wip/7560-six-reads). Rules from replication/shoulder/replicate.py and from_hourly.py (imported); tables
shoulder_hours_monthly, storage_buildout_monthly (warehouse/output); for the ten worst days, EIA's ERCO workbook held
under warehouse/raw/eia930_emissions/20261004T021545Z/.

    .venv/Scripts/python.exe runs/ruling_impact/shoulder_impact.py [--no-hourly]
"""
import importlib.util
import os
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
HERE_REP = os.path.join(ROOT, "replication", "shoulder")
sys.path.insert(0, HERE_REP)
spec = importlib.util.spec_from_file_location("replicate", os.path.join(HERE_REP, "replicate.py"))
rep = importlib.util.module_from_spec(spec)
sys.modules["replicate"] = rep
spec.loader.exec_module(rep)

T = rep.Tables(os.path.join(ROOT, "warehouse", "output"))


def pct(a, b):
    return "n/a" if not a else f"{(b - a) / a * 100:+.1f}%"


def month_measures(entity, fleet_entity, month):
    net, solar = T.day(entity, "net_load", month), T.day(entity, "solar", month)
    if net is None or solar is None:
        return None
    m = rep.measures(net, solar)
    mw = T.fleet.get((fleet_entity, "mw", month)) or T.t.get((entity, "fleet_mw", month + "-01"))       # the table's own row when the local
    mwh = T.fleet.get((fleet_entity, "mwh", month)) or T.t.get((entity, "fleet_mwh", month + "-01"))   # copy of storage_buildout is older
    m.update(rep.against_fleet(m, mw, mwh))
    return m


# ---- line 1: the fleet, EIA-860M against the market monitors' counts at the end of 2025
print("== line 1: the fleet at the end of 2025, EIA-860M against the market monitors")
MONITOR = {"iso:ercot": (17000.0, 31500.0, "Potomac Economics, 2025 State of the Market Report for the ERCOT Electricity Markets, June 2026, page ii: more than 17,000 MW and 31,500 MWh"),
           "iso:caiso": (17000.0, None, "CAISO Department of Market Monitoring, 2025 Annual Report on Market Issues and Performance, June 2026, page 23: over 17 GW")}
for entity, fleet_entity in (("iso:ercot", "iso:ercot"), ("iso:caiso_own", "iso:caiso")):
    m = month_measures(entity, fleet_entity, "2025-12")
    mw_m, mwh_m, doc = MONITOR[fleet_entity]
    mw, mwh = T.fleet.get((fleet_entity, "mw", "2025-12")), T.fleet.get((fleet_entity, "mwh", "2025-12"))
    e = m["shoulder_mwh_above_mean"]
    print(f"{entity} 2025-12: shoulder {e:,.2f} MWh above the mean; EIA-860M {mw:,.0f} MW, {mwh:,.0f} MWh: hours needed {e / mw:.2f}, fleet hours {mwh / mw:.2f}; "
          f"monitor {mw_m:,.0f} MW: hours needed {e / mw_m:.2f} ({e / mw_m - e / mw:+.2f}, {pct(e / mw, e / mw_m)})"
          + (f", fleet hours {mwh_m / mw_m:.2f} ({mwh_m / mw_m - mwh / mw:+.2f}, {pct(mwh / mw, mwh_m / mw_m)})" if mwh_m else ", fleet hours: the monitor gives no MWh")
          + f"; second measure hours needed {m['shoulder2_mwh_above_midpoint'] / mw:.2f} -> {m['shoulder2_mwh_above_midpoint'] / mw_m:.2f}; {doc}")
print("other months: the monitors publish a year-end count only; a monthly series is data not held")

# ---- line 2: which measure is the headline
print("\n== line 2: the headline, the shoulder against the daily mean (default) or the second measure to the evening peak's midpoint")
for entity, fleet_entity in (("iso:ercot", "iso:ercot"), ("iso:caiso", "iso:caiso"), ("iso:caiso_own", "iso:caiso")):
    months = T.months(entity)
    last = [mo for mo in months if (month_measures(entity, fleet_entity, mo) or {}).get("fleet_mw")][-1]   # the latest month with a fleet in the local tables
    m = month_measures(entity, fleet_entity, last)
    print(f"{entity} opening month {last}: hours {m['shoulder_hours']} -> {m['shoulder2_hours']}; MWh {m['shoulder_mwh_above_mean']:,.0f} -> {m['shoulder2_mwh_above_midpoint']:,.0f} "
          f"({pct(m['shoulder_mwh_above_mean'], m['shoulder2_mwh_above_midpoint'])}); hours needed {m.get('shoulder_hours_needed', 0):.2f} -> {m.get('shoulder2_hours_needed', 0):.2f} "
          f"({pct(m.get('shoulder_hours_needed'), m.get('shoulder2_hours_needed'))}); midnight-cut {m['shoulder_runs_to_midnight']} -> {m['shoulder2_runs_to_midnight']}")
    for year in ("2024", "2025"):
        ms = [month_measures(entity, fleet_entity, mo) for mo in months if mo.startswith(year)]
        ms = [x for x in ms if x and "shoulder_hours_needed" in x and "shoulder2_hours_needed" in x]
        if ms:
            a = sum(x["shoulder_hours_needed"] for x in ms) / len(ms)
            b = sum(x["shoulder2_hours_needed"] for x in ms) / len(ms)
            cut = sum(x["shoulder_runs_to_midnight"] for x in ms)
            print(f"   {year} mean of {len(ms)} months: hours needed {a:.2f} -> {b:.2f} ({pct(a, b)}); months cut at midnight {cut} -> {sum(x['shoulder2_runs_to_midnight'] for x in ms)}")

# ---- line 3: the midday low looked for only while the sun is up
print("\n== line 3: the midday surplus around the whole day's low (default) or the low while the sun is up (solar at least 5 percent of its daily peak)")


def surplus_sun(net, solar):
    mean = sum(net) / 24
    top = max(solar)
    up = [h for h in range(24) if solar[h] >= 0.05 * top]
    low = min(up, key=lambda h: (net[h], h))
    a = b = low
    while a - 1 >= 0 and net[a - 1] < mean:
        a -= 1
    while b + 1 <= 23 and net[b + 1] < mean:
        b += 1
    run = range(a, b + 1) if net[low] < mean else range(0)
    return low, len(run), sum(mean - net[h] for h in run)


for entity in ("iso:ercot", "iso:caiso"):
    moved = []
    months = T.months(entity)
    for mo in months:
        net, solar = T.day(entity, "net_load", mo), T.day(entity, "solar", mo)
        if net is None or solar is None:
            continue
        m = rep.measures(net, solar)
        low, hrs, mwh = surplus_sun(net, solar)
        if low != m["midday_low_hour"]:
            moved.append((mo, m["midday_low_hour"], low, m["midday_surplus_hours"], hrs, m["midday_surplus_mwh"], mwh))
    print(f"{entity}: {len(moved)} of {len(months)} months move")
    for x in [y for y in moved if abs(y[5] - y[6]) >= 0.01 or y[3] != y[4]]:
        print(f"   {x[0]}: low {x[1]:02d}:00 -> {x[2]:02d}:00; hours {x[3]} -> {x[4]}; MWh {x[5]:,.0f} -> {x[6]:,.0f} ({pct(x[5], x[6])})")
    if moved:
        same_run = sum(1 for x in moved if x[3] == x[4] and abs(x[5] - x[6]) < 0.01)
        print(f"   of the {len(moved)}: the run and the MWh stay the same in {same_run} (the night's low and the day's low lie in one run below the mean); "
              f"largest change {min(moved, key=lambda x: (x[6] - x[5]) / x[5] if x[5] else 0)[0]} {pct(min(moved, key=lambda x: (x[6] - x[5]) / x[5] if x[5] else 0)[5], min(moved, key=lambda x: (x[6] - x[5]) / x[5] if x[5] else 0)[6])}")

# ---- line 5: a battery of 2, 4 or 8 hours
print("\n== line 5: the fleet's hours needed (default) against the MW of batteries of 2, 4 or 8 hours the shoulder's energy needs")
for entity, fleet_entity in (("iso:ercot", "iso:ercot"), ("iso:caiso", "iso:caiso")):
    last = [mo for mo in T.months(entity) if (month_measures(entity, fleet_entity, mo) or {}).get("fleet_mw")][-1]
    m = month_measures(entity, fleet_entity, last)
    e, mw = m["shoulder_mwh_above_mean"], m["fleet_mw"]
    print(f"{entity} {last}: shoulder {e:,.0f} MWh, {m['shoulder_hours']} hours; fleet {mw:,.0f} MW, hours needed {e / mw:.2f}; "
          + "; ".join(f"{d}-hour batteries: {e / d:,.0f} MW ({e / d / mw * 100:.0f} percent of the fleet's MW), covering {min(d, m['shoulder_hours'])} of {m['shoulder_hours']} hours" for d in (2, 4, 8)))

# ---- line 6: California's demand, EIA-930 against CAISO's own
print("\n== line 6: California's shoulder on EIA-930's demand (iso:caiso) against CAISO's own supply (iso:caiso_own)")
both = sorted(set(T.months("iso:caiso")) & set(T.months("iso:caiso_own")))
for mo in both:
    a, b = month_measures("iso:caiso", "iso:caiso", mo), month_measures("iso:caiso_own", "iso:caiso", mo)
    print(f"{mo}: MWh above the mean {a['shoulder_mwh_above_mean']:,.0f} -> {b['shoulder_mwh_above_mean']:,.0f} ({pct(a['shoulder_mwh_above_mean'], b['shoulder_mwh_above_mean'])}); "
          f"hours needed {a['shoulder_hours_needed']:.2f} -> {b['shoulder_hours_needed']:.2f}; hours {a['shoulder_hours']} -> {b['shoulder_hours']}; "
          f"mean {a['net_load_mean_mw']:,.0f} -> {b['net_load_mean_mw']:,.0f} MW")

# ---- line 4: the ten worst days ranked by the evening's net load peak
if "--no-hourly" in sys.argv:
    sys.exit(0)
import from_hourly as fh
book = os.path.join(ROOT, "warehouse", "raw", "eia930_emissions", "20261004T021545Z", "20261004T021615.318504Z_00004_ERCO.xlsx")
print(f"\n== line 4: ERCOT's ten worst days of 2025, by energy above the day's mean (default) or by the evening's highest net load; workbook {os.path.basename(book)} (EIA, retrieved 2026-10-04)")
days = fh.hours(book, "America/Chicago")
n, ten = fh.ranked_days(days, "2025", "America/Chicago")
measured = {}
for d, rows in days.items():
    if d.startswith("2025") and len(rows) == 24 and fh.complete(rows, d, "America/Chicago"):
        rows = sorted(rows)
        m = rep.measures([x[1] - x[2] - x[3] for x in rows], [x[2] for x in rows])
        if m.get("shoulder_hours"):
            measured[d] = m
peak_ten = sorted(measured, key=lambda d: (-measured[d]["evening_peak_mw"], d))[:10]
mw_of = lambda d: T.fleet.get(("iso:ercot", "mw", d[:7]))
print(f"days ranked: {n} (table's count rule)")
print("default ten: " + ", ".join(f"{d} peak {m['evening_peak_mw']:,.0f} MW, {m['shoulder_mwh_above_mean']:,.0f} MWh" for _, d, m in ten))
print("other ten:   " + ", ".join(f"{d} peak {measured[d]['evening_peak_mw']:,.0f} MW, {measured[d]['shoulder_mwh_above_mean']:,.0f} MWh" for d in peak_ten))
for label, ds in (("default", [d for _, d, _ in ten]), ("other", peak_ten)):
    e = [measured[d]["shoulder_mwh_above_mean"] for d in ds]
    need = [measured[d]["shoulder_mwh_above_mean"] / mw_of(d) for d in ds if mw_of(d)]
    pk = [measured[d]["evening_peak_mw"] for d in ds]
    print(f"{label}: mean energy above the mean {sum(e) / len(e):,.0f} MWh; mean hours needed {sum(need) / len(need):.2f} ({len(need)} days with a fleet); mean evening peak {sum(pk) / len(pk):,.0f} MW; "
          f"months {sorted({d[5:7] for d in ds})}; days in both tens {len(set(ds) & set(d for _, d, _ in ten))}")

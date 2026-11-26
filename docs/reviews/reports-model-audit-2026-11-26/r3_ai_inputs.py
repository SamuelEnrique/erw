"""Session 10232 (reports audit), r3: the measures of ai_power_regions re-done from the tables its header names, by an
independent restatement of the method note and the builder (no import of the builder; the Flex Alert count alone is
taken from the scorecard's own function, said below), set against the table the draft reads.

    python runs/c10232/r3_ai_inputs.py <csv dir> <raw extract dir>

Large tables are streamed line by line and only the rows needed are kept (this machine is short of memory).
"""
import csv
import io
import os
import statistics as st
import sys
from collections import defaultdict

CSV_DIR, EXTRACT_DIR = sys.argv[1], sys.argv[2]
W0, W1 = "2025-09-01", "2026-09-01"
REG = {"caiso": ("CISO", "caiso:TH_SP15_GEN-APND", "caiso_rtm", "CAISO"), "ercot": ("ERCO", "ercot:HB_HUBAVG", "ercot", "ERCOT"),
       "isone": ("ISNE", "isone:.H.INTERNAL_HUB", "isone_rtm", "ISO-NE"), "miso": ("MISO", "miso:INDIANA.HUB", "miso_rtm", "MISO"),
       "nyiso": ("NYIS", "nyiso:N.Y.C.", "nyiso_rtm", "NYISO"), "pjm": ("PJM", None, None, "PJM"), "spp": ("SWPP", "spp:SPPNORTH_HUB", "spp_rtm", "SPP")}


def rows(name, keep=None, prefixes=None):
    path = os.path.join(CSV_DIR, name + ".csv")
    if not prefixes:
        # a field may hold a line break (the queues' notes): the csv reader over the whole file, not line by line
        with open(path, encoding="utf-8", newline="") as f:
            for r in csv.DictReader(ln for ln in f if not ln.startswith("#")):
                if keep is None or keep(r):
                    yield r
        return
    with open(path, encoding="utf-8") as f:
        head = None
        for ln in f:
            if ln.startswith("#"):
                continue
            if head is None:
                head = next(csv.reader([ln]))
                continue
            if prefixes and not ln.startswith(prefixes):
                continue
            r = dict(zip(head, next(csv.reader([ln]))))
            if keep is None or keep(r):
                yield r


T = defaultdict(dict)
for r in rows("ai_power_regions"):
    T[r["entity"].split(":")[1]][r["variable"]] = float(r["value"])
got = defaultdict(dict)
inw = lambda ts: W0 <= ts[:10] < W1

# cost
cm = defaultdict(dict)
for r in rows("cost_of_power_monthly", lambda r: inw(r["ts_utc"])):
    cm[(r["entity"], r["ts_utc"][:10])][r["variable"]] = float(r["value"])
for reg, (ba, hub, mk, _) in REG.items():
    if not hub:
        continue
    ms = [m for (e, ts), m in cm.items() if e == hub]
    rt = sum(m["rt_simple_mean"] * m["rt_hours"] for m in ms) / sum(m["rt_hours"] for m in ms)
    da = sum(m["da_simple_mean"] * m["da_hours"] for m in ms) / sum(m["da_hours"] for m in ms)
    complete = sum(1 for m in ms if m["rt_hours"] == m["hours_in_month"])
    got[reg].update(flat_rt_price_usd_mwh=rt, flat_da_price_usd_mwh=da, flat_1gw_cost_usd=rt * 8760 * 1000, rt_hours_priced=sum(m["rt_hours"] for m in ms))
    print(f"cost {reg}: {len(ms)} months, {complete} complete in real time, hours priced {sum(m['rt_hours'] for m in ms):.0f}")

# carbon
cd = defaultdict(list)
for r in rows("carbon_intensity_daily", lambda r: r["variable"] == "intensity_demand" and inw(r["ts_utc"])):
    cd[r["entity"]].append(float(r["value"]))
for reg, (ba, *_) in REG.items():
    g = cd.get(f"eia930:{ba}", [])
    if g:
        got[reg].update(carbon_intensity_kg_mwh=st.mean(g), flat_1gw_co2_t=st.mean(g) * 8760 * 1000, carbon_days=float(len(g)))

# stress: hourly means of the hub's real-time prices
for reg, (ba, hub, mk, _) in REG.items():
    if not hub:
        continue
    hours = defaultdict(list)
    if reg == "ercot":
        src = rows("ercot_all_hub_prices_history", lambda r: r["variable"] == "spp_rtm" and inw(r["ts_utc"]), prefixes=(hub + ",spp_rtm,",))
    else:
        src = rows("iso_hub_prices_history", lambda r: r["market"] == mk and inw(r["ts_utc"]), prefixes=(hub + ",",))
    for r in src:
        hours[r["ts_utc"][:13]].append(float(r["value"]))
    h = [st.mean(v) for v in hours.values()]
    got[reg].update(scarcity_hours_200=float(sum(x >= 200 for x in h)), scarcity_hours_1000=float(sum(x >= 1000 for x in h)),
                    max_rt_hour_usd_mwh=max(h), rt_hours_seen=float(len(h)))

# events (COVID left out; temperature-controlled where held)
ev = defaultdict(dict)
for r in rows("event_study_estimates", lambda r: r["event"] != "covid_2020"):
    ev[(r["entity"], r["event"])][r["variable"]] = float(r["value"])
for reg, (ba, *_) in REG.items():
    best = None
    for (e, name), v in ev.items():
        if e != f"eia930:{ba}":
            continue
        eff, cf = ("demand_mwh_effect_pooled_temp", "demand_mwh_counterfactual_mean_temp") if "demand_mwh_effect_pooled_temp" in v else ("demand_mwh_effect_pooled", "demand_mwh_counterfactual_mean")
        if eff in v and cf in v:
            pct = v[eff] / v[cf] * 100
            if best is None or abs(pct) > abs(best[0]):
                best = (pct, name, eff.endswith("_temp"))
    if best:
        got[reg]["event_largest_effect_pct"] = best[0]
        print(f"event {reg}: {best[1]}, {best[0]:.4f} percent, temperature-controlled {best[2]}")

# Berkeley Lab
import datetime as dt
lb = defaultdict(list)
for r in rows("lbnl_interconnection_queue"):
    lb[r["region"]].append(r)
for reg, (ba, hub, mk, name) in REG.items():
    g = lb.get(name, [])
    act = [r for r in g if r["status"] == "active"]
    mw = sum(float(r["capacity_mw"]) for r in act if r["capacity_mw"] not in ("", "nan"))
    yrs = []
    for r in g:
        if r["status"] == "operating" and r["on_date"] and r["q_date"]:
            on, q = dt.date.fromisoformat(r["on_date"][:10]), dt.date.fromisoformat(r["q_date"][:10])
            if 2018 <= on.year <= 2025:
                y = (on - q).days / 365.25
                if y >= 0:
                    yrs.append(y)
    cohort = [r for r in g if r["q_year"] not in ("", "nan") and 2000 <= float(r["q_year"]) <= 2019]
    got[reg].update(lbnl_active_mw=mw, lbnl_active_requests=float(len(act)), lbnl_cod_sample=float(len(yrs)), lbnl_cohort_requests=float(len(cohort)))
    if yrs:
        got[reg]["lbnl_median_years_to_cod"] = st.median(yrs)
    if cohort:
        got[reg]["lbnl_completion_pct"] = sum(r["status"] == "operating" for r in cohort) / len(cohort) * 100

# the ISOs' own queues
for reg in ("caiso", "ercot", "isone", "miso", "nyiso", "spp"):
    a = [float(r["capacity_mw"]) for r in rows(f"{reg}_interconnection_queue", lambda r: r["status"] == "active") if r["capacity_mw"] not in ("", "nan")]
    got[reg]["queue_active_mw"] = sum(a)

# imports: EIA's balance from the extracts (complete hours), and the pair sums for the BAs with no pair-day screened in the year
ext = {}
for reg, (ba, *_) in REG.items():
    path = os.path.join(EXTRACT_DIR, f"{ba.lower()}_hours.csv")
    d = ng = 0.0
    day = defaultdict(float)
    with open(path, encoding="utf-8") as f:
        for r in csv.DictReader(ln for ln in f if not ln.startswith("#")):
            if not inw(r["ts_utc"]):
                continue
            try:
                dd = float(r["demand_mwh"])
            except ValueError:
                continue
            day[r["ts_utc"][:10]] += dd
            try:
                gg = float(r["net_generation_mwh"])
            except ValueError:
                continue
            d += dd
            ng += gg
    got[reg]["net_import_share_pct"] = (d - ng) / d * 100
    got[reg]["demand_mwh"] = d
    ext[reg] = day
pairs = defaultdict(lambda: defaultdict(dict))
want = {"ciso": "caiso", "erco": "ercot", "pjm": "pjm"}
for r in rows("eia930_daily_interchange", lambda r: r["ba"] in want and inw(r["ts_utc"])):
    pairs[r["ba"]][r["ts_utc"][:10]][r["entity"]] = float(r["value"])
for ba, reg in want.items():
    days = pairs[ba]
    cnt = defaultdict(int)
    for dd in days.values():
        for e in dd:
            cnt[e] += 1
    regular = {e for e, c in cnt.items() if c >= 0.5 * len(days)}
    ok = sorted(d for d, dd in days.items() if regular <= set(dd))
    exp = {d: sum(days[d].values()) for d in ok}
    dem = {d: ext[reg].get(d) for d in ok}
    tot_dem = sum(v for v in dem.values() if v is not None)
    share = {d: -exp[d] / dem[d] for d in ok if dem.get(d)}
    top = sorted([d for d in ok if dem.get(d)], key=lambda d: -dem[d])[:10]
    got[reg].update(pair_import_share_pct=-sum(exp.values()) / tot_dem * 100, net_import_days_pct=sum(v < 0 for v in exp.values()) / len(exp) * 100,
                    peak_import_share_pct=st.mean(share[d] for d in top) * 100, interchange_days=float(len(exp)))

# set against the table
print("\nregion, measure, table, re-done, difference")
n_ok = n_bad = 0
for reg in REG:
    for k, v in sorted(got[reg].items()):
        t = T[reg].get(k)
        if t is None:
            print(f"  {reg} {k}: not in the table; re-done {v:.4f}")
            continue
        same = abs(t - v) <= 0.00011 if abs(t) < 1e6 else abs(t - v) <= 1
        if same:
            n_ok += 1
        else:
            n_bad += 1
            print(f"  DIFFERS {reg} {k}: table {t:.4f}, re-done {v:.4f}, difference {v - t:+.4f}")
print(f"\n{n_ok} measures agree to the table's four decimals (or to a unit for amounts over a million), {n_bad} differ")

# the Flex Alert count: the scorecard's own rule, imported (not restated: the rule reads the report's notice types)
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "..", "warehouse", "derived"))
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "..", "warehouse", "connectors"))
try:
    import pandas as pd
    import flex_alert_scorecard as fa
    path = os.path.join(CSV_DIR, "caiso_grid_emergencies.csv")
    n = sum(1 for ln in open(path, encoding="utf-8") if ln.startswith("#"))
    df = pd.read_csv(path, skiprows=n, dtype=str, keep_default_na=False)
    print(f"Flex Alert days by the scorecard's own function: {len(fa.alert_days(df))} (table {T['caiso'].get('emergency_days')})")
except Exception as e:  # noqa: BLE001
    print(f"Flex Alert days: not re-done ({type(e).__name__}: {e})")

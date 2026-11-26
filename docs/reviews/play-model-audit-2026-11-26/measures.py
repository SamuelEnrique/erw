"""Session 10227 (play audit): one rule of the battery game changed at a time, each measured with restate.py's own
functions (none of the site's code) on the default game (the newest complete ERCOT day held here, 2026-11-12, Normal and
Easy score alike) and on the seven famous days. Also the levels' stated rules checked against the history.

    python measures.py      (reads extract.json, retail.json, restate.json; writes measures.json)
"""
import json
import os

import restate as R0

HERE = os.path.dirname(os.path.abspath(__file__))
levels, ex = R0.load_levels()
retail = json.load(open(os.path.join(HERE, "retail.json")))["power"]
base = json.load(open(os.path.join(HERE, "restate.json")))


def expand_hourly(ts_utc, hourly):
    """Each interval takes the price of its UTC hour from an hourly series [[ts, value], ...]; None where one is missing."""
    by = {t[:13]: v for t, v in hourly}
    out = [by.get(t[:13]) for t in ts_utc]
    return None if any(v is None for v in out) else out


out = {}
for L in levels:
    p, d = L["price"], L["date"]
    R = R0.rules("normal")
    dp0 = base[f"{d}|normal"]["dp"]
    m = {"dp": dp0}
    m["any_power"] = base[f"{d}|normal"]["mip_any_power"]
    m["end_at_least_start"] = R0.dp(p, R, min_end=R["start"])[0]
    m["end_at_least_start_any_power"] = R0.mip(p, R, True, end_at_least=R["start"])
    Re = dict(R, start=0.0)
    m["start_empty"] = R0.dp(p, Re)[0]
    m["no_bonus"] = R0.dp(p, dict(R, no_bonus=True))[0]
    m["wear_charged"] = R0.dp(p, dict(R, deg=0.11))[0]
    hm = [sum(p[i - i % 4:i - i % 4 + 4]) / len(p[i - i % 4:i - i % 4 + 4]) for i in range(len(p))]
    m["hourly_mean_prices"] = R0.dp(hm, R)[0]
    # day-ahead: the perfect battery on the day-ahead prices; and the plan made on them, scored at real time
    da = ex["dam"].get(d) or {k: v for k, v in ex["famous_ercot"].get(d, {}).items() if k.endswith("spp_dam")}
    key = next((k for k in da if k.endswith("spp_dam") or k.endswith("lmp_dam")), None)
    if key:
        dap = expand_hourly(L["ts_utc"], sorted(da[key]))
        if dap:
            v, acts, _ = R0.dp(dap, R)
            m["dayahead_perfect"] = v
            m["dayahead_plan_scored_at_realtime"] = R0.sim(p, acts, R)["score"]
            m["dayahead_mean"] = sum(dap) / len(dap)
    # retail: every kWh bought at the state's average residential price of that month, sold at the real-time price
    st = "CA" if L.get("grid") == "CAISO" else "TX"
    ser = retail.get(f"eia:retail_price:{st}:RES", {})
    month = d[:7] + "-01"
    if month not in ser:  # the newest day is newer than EIA's newest month: its newest month is used, and said
        month = max(ser)
    rp = ser.get(month)
    if rp is not None:
        m["retail_month"] = [st, month, rp]
        m["retail_buy_any_power"] = R0.mip(p, R, True, buy_add=[rp] * len(p))
        m["retail_buy_end_at_least_start_any_power"] = R0.mip(p, R, True, end_at_least=R["start"], buy_add=[rp] * len(p))
    m["any_power_end_free_check"] = R0.mip(p, R, True)
    # Hard: the share of the perfect score that is the game's emergency (spike, its bonus, the outage)
    Rh = R0.rules("hard")
    m["hard"] = base[f"{d}|hard"]["dp"]
    m["hard_without_emergency"] = R0.dp(p, dict(Rh, emergency=False))[0]
    out[d] = m

# the hub against a place: the newest day, Houston's hub against the hub average
d = levels[0]["date"]
hou = ex["recent_rt"][d].get("ercot:HB_HOUSTON")
if hou:
    hp = [v for _, v in sorted(hou)]
    R = R0.rules("normal")
    v_h, a_h, _ = R0.dp(hp, R)
    v_a, a_a, _ = R0.dp(levels[0]["price"], R)
    out[d]["houston_perfect"] = v_h
    out[d]["hubavg_plan_scored_at_houston"] = R0.sim(hp, a_a, R)["score"]

# the levels' own rules against the history held here (ercot_all_hub_prices_history, to 2026-08-25)
H = ex["ercot_hist_days"]
low = min(H, key=lambda k: H[k][0])
spring = {k: v for k, v in H.items() if "2026-03-01" <= k <= "2026-05-31"}
calm = min(spring, key=lambda k: spring[k][2] - spring[k][1])
# and the live table's complete days after the history ends (iso_rtm_hub_prices, main copy, read only)
import sys  # noqa: E402
from extract_days import rtm_day_means  # noqa: E402
RT = rtm_day_means(sys.argv[1]) if len(sys.argv) > 1 else {}
later = {k: v for k, v in RT.items() if k > max(H)}
low_later = min(later, key=lambda k: later[k]) if later else None
out["_rules"] = {"lowest_mean_day": [low, H[low][0], len(H), min(H), max(H)], "lowest_5": sorted(H, key=lambda k: H[k][0])[:5],
                 "after_history": [len(later), min(later) if later else None, max(later) if later else None, low_later, later.get(low_later)],
                 "calm_day": [calm, spring[calm][2] - spring[calm][1], len(spring)], "uri_mean": H.get("2021-02-15")}
json.dump(out, open(os.path.join(HERE, "measures.json"), "w"), indent=1)

f = lambda v: "n/a" if v is None else f"{v:.4f}"  # noqa: E731
for d, m in out.items():
    if d == "_rules":
        continue
    print(f"{d}: dp {f(m['dp'])} | any power {f(m['any_power'])} | end>=start {f(m['end_at_least_start'])} (any power {f(m['end_at_least_start_any_power'])}) | "
          f"start empty {f(m['start_empty'])} | no bonus {f(m['no_bonus'])} | wear {f(m['wear_charged'])} | hourly {f(m['hourly_mean_prices'])} | "
          f"DA perfect {f(m.get('dayahead_perfect'))} DA plan at RT {f(m.get('dayahead_plan_scored_at_realtime'))} | "
          f"retail {m.get('retail_month')} buy {f(m.get('retail_buy_any_power'))} | hard {f(m['hard'])} without emergency {f(m['hard_without_emergency'])}"
          + (f" | Houston {f(m['houston_perfect'])} hubavg plan at Houston {f(m['hubavg_plan_scored_at_houston'])}" if "houston_perfect" in m else ""))
print("rules:", out["_rules"])

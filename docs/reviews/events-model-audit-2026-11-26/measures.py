"""Session 10225: one rule changed at a time, on the events pages' own rows (event_window_daily, read only from the main
copy) and the events' region files. Reuses restate.py's estimator (numpy least squares, my own HC1).

    python measures.py <event_window_daily.csv> <out.json>
"""
import datetime as dt
import json
import os
import sys

import numpy as np

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import restate as R  # noqa: E402

ROOT = R.ROOT
OUT = {}


def series(rows, ev, ent, var):
    xs = sorted((r for r in R.sel(rows, ev, ent, var) if r["freq"] in ("", "P1D")), key=lambda r: r["d"])
    return [r["d"] for r in xs], [r["v"] for r in xs]


def weather_rule(rows, ev, ent, var):
    """The page's pooled temperature estimate against the same model's weather terms fitted on the baseline days alone
    (the rule each day's estimate uses), the window's mean of those day effects; and the share each rule gives."""
    s0, s1 = R.WIN[ev]
    dates, y = series(rows, ev, ent, var)
    w = R.weather(rows, ev, R.ba_of(ent))
    keep = [i for i, d in enumerate(dates) if d in w]
    dd, yy = [dates[i] for i in keep], [y[i] for i in keep]
    evm = [s0 <= d <= s1 for d in dd]
    Zx = np.array([[w[d][0], w[d][0] ** 2, w[d][1], w[d][1] ** 2] for d in dd])
    s = R.study(dates, y, [s0 <= d <= s1 for d in dates])
    t = R.study(dd, yy, evm, Zx)
    mean_s = sum(x["est"] for x in s["days"]) / len(s["days"])
    mean_t = sum(x["est"] for x in t["days"]) / len(t["days"])

    def share(a, b):
        return round((1 - a / b) * 100, 2) if np.sign(a) == np.sign(b) and abs(a) <= abs(b) else None
    hdd_b = [w[d][0] for d, e in zip(dd, evm) if not e]
    cdd_b = [w[d][1] for d, e in zip(dd, evm) if not e]
    beyond_h = [d for d, e in zip(dd, evm) if e and w[d][0] > max(hdd_b)]
    beyond_c = [d for d, e in zip(dd, evm) if e and w[d][1] > max(cdd_b)]
    return dict(pooled=round(s["est"], 2), pooled_temp=round(t["est"], 2), share_page=share(t["est"], s["est"]),
                mean_day=round(mean_s, 2), mean_day_temp_baseline_fit=round(mean_t, 2), share_baseline_fit=share(mean_t, mean_s),
                event_days=sum(evm), hdd_baseline_max=round(max(hdd_b), 2), cdd_baseline_max=round(max(cdd_b), 2),
                event_days_colder_than_any_baseline=beyond_h, event_days_hotter_than_any_baseline=beyond_c,
                hdd_event_max=round(max(w[d][0] for d, e in zip(dd, evm) if e), 2),
                cdd_event_max=round(max(w[d][1] for d, e in zip(dd, evm) if e), 2))


def narrowed(rows, ev, ent, var, a, b):
    """The pooled estimate (no weather) with the window cut to [a, b]; the window's other days left out of the fit."""
    s0, s1 = R.WIN[ev]
    dates, y = series(rows, ev, ent, var)
    keep = [i for i, d in enumerate(dates) if not (s0 <= d <= s1) or a <= d <= b]
    dd, yy = [dates[i] for i in keep], [y[i] for i in keep]
    full = R.study(dates, y, [s0 <= d <= s1 for d in dates])
    cut = R.study(dd, yy, [a <= d <= b for d in dd])
    return dict(window=[s0, s1], cut=[a, b], pooled=round(full["est"], 2), pct=round(full["est"] / full["cf"] * 100, 2),
                pooled_cut=round(cut["est"], 2), pct_cut=round(cut["est"] / cut["cf"] * 100, 2),
                lo_cut=round(cut["lo"], 2), hi_cut=round(cut["hi"], 2))


def ciso_intensity(rows):
    s0, s1 = R.WIN["caiso_heat_2020"]
    xs = R.sel(rows, "caiso_heat_2020", "eia930:CISO", "intensity_generation")
    ev = [r["v"] for r in xs if s0 <= r["d"] <= s1]
    base = {}
    for r in xs:
        if not (s0 <= r["d"] <= s1):
            base.setdefault(r["d"][:4], []).append(r["v"])
    out = dict(event_days=len(ev), event_mean=round(sum(ev) / len(ev), 2), event_max=max(ev),
               baseline={y: dict(days=len(v), mean=round(sum(v) / len(v), 2)) for y, v in sorted(base.items())})
    # the hydro the region file holds for California (CAL: CAISO and BANC, LDWP, IID, TIDC), window against baseline
    f = json.load(open(os.path.join(ROOT, "site", "data", "regions", "events", "caiso_heat_2020.json"), encoding="utf-8"))
    cal = f["regions"]["CAL"]
    ok = lambda v: isinstance(v, (int, float))  # noqa: E731
    h_e, h_b = cal["gen"]["hydro"], cal["baseline"]["gen"]["hydro"]
    ng_e, ng_b = cal["net_generation_mw"], cal["baseline"]["net_generation_mw"]
    both = [i for i in range(len(h_e)) if ok(h_e[i]) and ok(h_b[i]) and ok(ng_e[i]) and ok(ng_b[i])]
    m = lambda a: sum(a[i] for i in both) / len(both)  # noqa: E731
    out["CAL_region_file"] = dict(hours=len(both), hydro_event_mean_mw=round(m(h_e)), hydro_baseline_mean_mw=round(m(h_b)),
                                  net_gen_event_mean_mw=round(m(ng_e)), net_gen_baseline_mean_mw=round(m(ng_b)),
                                  hydro_share_event_pct=round(m(h_e) / m(ng_e) * 100, 2),
                                  hydro_share_baseline_pct=round(m(h_b) / m(ng_b) * 100, 2))
    return out


def caiso_net_peak(rows):
    """CISO's gross peak hour on 14, 15 and 18 August 2020 (the table), and California's net demand (demand less solar
    and wind, the region file, Pacific days) at its highest hour of those days."""
    out = {}
    for d in ("2020-08-14", "2020-08-15", "2020-08-17", "2020-08-18", "2020-08-19"):
        r = R.sel(rows, "caiso_heat_2020", "eia930:CISO", "demand_max_mw", lambda x, d=d: x == d)
        out[d] = dict(ciso_peak_mw=r[0]["v"] if r else None)
    f = json.load(open(os.path.join(ROOT, "site", "data", "regions", "events", "caiso_heat_2020.json"), encoding="utf-8"))
    cal = f["regions"]["CAL"]
    t0 = dt.datetime.fromisoformat(f["hours"]["start"].replace("Z", "+00:00"))
    ok = lambda v: isinstance(v, (int, float))  # noqa: E731
    by = {}
    for i, dem in enumerate(cal["demand_mw"]):
        so, wi = cal["gen"]["solar"][i], cal["gen"]["wind"][i]
        if not (ok(dem) and ok(so) and ok(wi)):
            continue
        local = t0 + dt.timedelta(hours=i) - dt.timedelta(hours=7)  # Pacific daylight time in August
        day = local.strftime("%Y-%m-%d")
        g = by.setdefault(day, dict(gross=(0, None), net=(0, None)))
        if dem > g["gross"][0]:
            g["gross"] = (dem, local.strftime("%H:00"))
        if dem - so - wi > g["net"][0]:
            g["net"] = (dem - so - wi, local.strftime("%H:00"))
    for d in out:
        if d in by:
            out[d].update(cal_gross_peak=by[d]["gross"], cal_net_peak=by[d]["net"])
    p = {d: v["ciso_peak_mw"] for d, v in out.items()}
    out["shed_needed_to_reorder_mw"] = {d: round(p["2020-08-18"] - p[d]) for d in ("2020-08-14", "2020-08-15")}
    return out


def uri_prices(rows):
    xs = {r["d"]: r for r in R.sel(rows, "uri_2021", "ercot:HB_HUBAVG", "rt_max") if r["d"][:4] == "2021"}
    ms = {r["d"]: r["v"] for r in R.sel(rows, "uri_2021", "ercot:HB_HUBAVG", "rt_mean") if r["d"][:4] == "2021"}
    days = sorted(xs)
    return dict(days_rt_max_at_or_above_8900=[(d, xs[d]["v"], ms.get(d)) for d in days if xs[d]["v"] >= 8900],
                rt_max_window=max(x["v"] for x in xs.values()))


def main():
    rows = R.read(sys.argv[1])
    OUT["weather_rule"] = {
        "uri ERCOT demand": weather_rule(rows, "uri_2021", "eia930:ERCO", "demand_mwh"),
        "uri ERCOT hub price": weather_rule(rows, "uri_2021", "ercot:HB_HUBAVG", "rt_mean"),
        "caiso_heat_2020 CAISO demand": weather_rule(rows, "caiso_heat_2020", "eia930:CISO", "demand_mwh"),
    }
    for g in ("eia930:PJM", "eia930:ERCO", "eia930:SWPP", "eia930:MISO", "eia930:NYIS", "eia930:ISNE"):
        OUT["weather_rule"][f"elliott {g} demand"] = weather_rule(rows, "elliott_2022", g, "demand_mwh")
    OUT["narrowed"] = {
        "uri ERCOT, the storm part of the window (14 to 17 February)": narrowed(rows, "uri_2021", "eia930:ERCO", "demand_mwh", "2021-02-14", "2021-02-17"),
        "caiso_heat_2020 CAISO, the report's days (14 to 19 August)": narrowed(rows, "caiso_heat_2020", "eia930:CISO", "demand_mwh", "2020-08-14", "2020-08-19"),
        "elliott PJM, FERC's days (21 to 26 December)": narrowed(rows, "elliott_2022", "eia930:PJM", "demand_mwh", "2022-12-21", "2022-12-26"),
    }
    OUT["ciso_intensity_hydro_gap"] = ciso_intensity(rows)
    OUT["caiso_net_peak"] = caiso_net_peak(rows)
    OUT["uri_prices"] = uri_prices(rows)
    json.dump(OUT, open(sys.argv[2], "w", encoding="utf-8"), indent=1)
    print(json.dumps(OUT, indent=1))


if __name__ == "__main__":
    main()

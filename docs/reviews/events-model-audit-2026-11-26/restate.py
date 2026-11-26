"""Session 10225 (chain 710, part D): the events pages' figures restated, independently of the site's code.

Three views: /events/uri-2021 (the first card of the index, its default), /events/caiso-heat-2020 and
/events/elliott-2022, and the index's three cards for them. Every figure is computed from the rules as the pages and
docs/methods/events.md and event_study.md state them, from the warehouse's event_window_daily.csv (the main copy's
warehouse/output, read only) and the events' region files (site/data/regions/events/<event>.json). The regression is
numpy's least squares with my own HC1, not the site's Gauss-Jordan.

The whole country's net imports and the pair table are not restated: out of bounds, the paper's.

    python restate.py <event_window_daily.csv> <out.json>
"""
import csv
import datetime as dt
import json
import os
import sys

import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.abspath(os.path.join(HERE, "..", ".."))
T = "event_window_daily"
Z = 1.959963984540054
WIN = {"uri_2021": ("2021-02-07", "2021-02-24"), "caiso_heat_2020": ("2020-08-10", "2020-08-24"),
       "elliott_2022": ("2022-12-19", "2022-12-29")}
STATION_BA = {"noaa:DFW": "erco", "noaa:IAH": "erco", "noaa:SAC": "ciso", "noaa:LAX": "ciso", "noaa:PHL": "pjm",
              "noaa:ORD": "pjm", "noaa:MSP": "miso", "noaa:JFK": "nyis", "noaa:BOS": "isne", "noaa:OKC": "swpp"}
REGIONS = ["CAL", "CAR", "CENT", "FLA", "MIDA", "MIDW", "NE", "NW", "NY", "SE", "SW", "TEN", "TEX"]
SOURCES = ["natural_gas", "coal", "nuclear", "wind", "solar", "hydro", "storage", "other"]


def read(path):
    rows = []
    with open(path, encoding="utf-8") as f:
        lines = (l for l in f if not l.startswith("#"))
        for r in csv.DictReader(lines):
            if r["event"] in WIN:
                rows.append(dict(entity=r["entity"], variable=r["variable"], ts=r["ts_utc"], d=r["ts_utc"][:10],
                                 v=float(r["value"]), freq=r["freq"], event=r["event"]))
    return rows


def key(r):
    return f"series|{T}|{r['entity']}|{r['variable']}|{r['ts']}|{r['event']}"


def best(rows, how):
    """The highest or lowest; of equal values the earliest day (rows in day order)."""
    rows = sorted(rows, key=lambda r: r["d"])
    if not rows:
        return None
    out = rows[0]
    for r in rows[1:]:
        if (how == "max" and r["v"] > out["v"]) or (how == "min" and r["v"] < out["v"]):
            out = r
    return out


def sel(rows, ev, ent=None, var=None, keep=lambda d: True):
    return [r for r in rows if r["event"] == ev and (ent is None or r["entity"] == ent) and (var is None or r["variable"] == var)
            and keep(r["d"])]


# --- the event study, my own least squares and HC1 ---------------------------------------------------------------
def weekday(d):
    return dt.date.fromisoformat(d).weekday()  # Monday 0


def columns(dates, event, base_years, pooled, Zx):
    names = ["const"] + (["pooled"] if pooled else []) + [f"dow{k}" for k in range(1, 7)]
    names += [f"yr{y}" for y in base_years[:-1]] if len(base_years) >= 2 else []
    if Zx is not None:
        names += [f"z{j}" for j in range(Zx.shape[1])]
    X = np.zeros((len(dates), len(names)))
    for i, d in enumerate(dates):
        c = [1.0] + ([1.0 if event[i] else 0.0] if pooled else []) + [1.0 if weekday(d) == k else 0.0 for k in range(1, 7)]
        if len(base_years) >= 2:
            y0 = int(d[:4])
            c += [0.0 if event[i] else float(y0 == y) - float(y0 == base_years[-1]) for y in base_years[:-1]]
        if Zx is not None:
            c += list(Zx[i])
        X[i] = c
    return X, names


def independent(X):
    """Columns kept in order: each that raises the rank of those kept before it."""
    keep = []
    for j in range(X.shape[1]):
        if not np.any(X[:, j]):
            continue
        if np.linalg.matrix_rank(X[:, keep + [j]], tol=1e-9 * max(1.0, np.linalg.norm(X[:, j]))) > len(keep):
            keep.append(j)
    return keep


def hc1(X, y):
    n, k = X.shape
    b, *_ = np.linalg.lstsq(X, y, rcond=None)
    e = y - X @ b
    A = np.linalg.pinv(X.T @ X)
    V = A @ (X.T * e ** 2) @ X @ A * n / (n - k)
    return b, V, float(e @ e) / (n - k)


def study(dates, y, event, Zx=None):
    y = np.array(y, float)
    event = np.array(event, bool)
    base_years = sorted({int(d[:4]) for d, e in zip(dates, event) if not e})
    X, names = columns(dates, event, base_years, False, Zx)
    keep = independent(X[~event])
    b, V, s2 = hc1(X[~event][:, keep], y[~event])
    days = []
    for i in np.where(event)[0]:
        x = X[i, keep]
        cf = float(x @ b)
        se = float(np.sqrt(s2 + x @ V @ x))
        days.append(dict(day=dates[i], cf=cf, est=float(y[i] - cf), lo=float(y[i] - cf - Z * se), hi=float(y[i] - cf + Z * se)))
    Xp, pn = columns(dates, event, base_years, True, Zx)
    kp = independent(Xp)
    bp, Vp, _ = hc1(Xp[:, kp], y)
    j = kp.index(pn.index("pooled"))
    est, se = float(bp[j]), float(np.sqrt(Vp[j, j]))
    cfm = sum(d["cf"] for d in days) / len(days)
    return dict(days=days, est=est, lo=est - Z * se, hi=est + Z * se, cf=cfm, n=len(y), nbase=int((~event).sum()))


def weather(rows, ev, ba):
    acc = {}
    for r in rows:
        if r["event"] != ev or STATION_BA.get(r["entity"]) != ba or r["variable"] not in ("hdd_65f", "cdd_65f"):
            continue
        a = acc.setdefault(r["d"], {"h": [], "c": []})
        a["h" if r["variable"] == "hdd_65f" else "c"].append(r["v"])
    return {d: (sum(a["h"]) / len(a["h"]), sum(a["c"]) / len(a["c"])) for d, a in acc.items() if a["h"] and a["c"]}


def ba_of(entity):
    return "erco" if entity == "ercot:HB_HUBAVG" else entity.split(":")[1].lower()


def studies(rows, ev, entity, variable, figs, lead):
    s0, s1 = WIN[ev]
    xs = sorted((r for r in sel(rows, ev, entity, variable) if r["freq"] in ("", "P1D")), key=lambda r: r["d"])
    dates, y = [r["d"] for r in xs], [r["v"] for r in xs]
    ev_ = [s0 <= d <= s1 for d in dates]
    s = study(dates, y, ev_)
    k = f"es|{ev}|{entity}|{variable}"
    figs.update({f"{k}|pooled|est": s["est"], f"{k}|pooled|lo": s["lo"], f"{k}|pooled|hi": s["hi"],
                 f"{k}|pooled|pct": s["est"] / s["cf"] * 100})
    if lead:
        figs[f"{k}|pooled|cf"] = s["cf"]
        for d in s["days"]:
            figs.update({f"{k}|day|{d['day']}|est": d["est"], f"{k}|day|{d['day']}|lo": d["lo"], f"{k}|day|{d['day']}|hi": d["hi"]})
    w = weather(rows, ev, ba_of(entity))
    t = None
    if w:
        keep = [i for i, d in enumerate(dates) if d in w]
        dd = [dates[i] for i in keep]
        Zx = np.array([[w[d][0], w[d][0] ** 2, w[d][1], w[d][1] ** 2] for d in dd])
        t = study(dd, [y[i] for i in keep], [ev_[i] for i in keep], Zx)
        figs.update({f"{k}|pooled_temp|est": t["est"], f"{k}|pooled_temp|lo": t["lo"], f"{k}|pooled_temp|hi": t["hi"]})
        if lead and np.sign(t["est"]) == np.sign(s["est"]) and abs(t["est"]) <= abs(s["est"]):
            figs[f"{k}|weather_share|pct"] = (1 - t["est"] / s["est"]) * 100
        t = dict(t, mean_day_effect=sum(d["est"] for d in t["days"]) / len(t["days"]))
    return dict(n=s["n"], nbase=s["nbase"], days=len(s["days"]), temp_n=(t or {}).get("n"),
                mean_day_effect=sum(d["est"] for d in s["days"]) / len(s["days"]), pooled=s["est"],
                pooled_temp=(t or {}).get("est"), temp_mean_day_effect=(t or {}).get("mean_day_effect"))


# --- the pages -----------------------------------------------------------------------------------------------------
def uri(rows, figs, info):
    ev = "uri_2021"
    y = lambda ys: (lambda d: d[:4] in ys)  # noqa: E731
    picks = {
        "rtPeak": best(sel(rows, ev, var="rt_max", keep=y(["2021"])), "max"),
        "rtBase": best(sel(rows, ev, var="rt_max", keep=y(["2019", "2020"])), "max"),
        "lowDemand": best(sel(rows, ev, var="demand_min_mw", keep=y(["2021"])), "min"),
        "low15": next(iter(sel(rows, ev, var="demand_min_mw", keep=lambda d: d == "2021-02-15")), None),
        "fall": best(sel(rows, ev, var="net_generation_mwh_day_change", keep=y(["2021"])), "min"),
        "short": best(sel(rows, ev, var="net_generation_mwh_vs_baseline", keep=y(["2021"])), "min"),
        "ciPeak": best(sel(rows, ev, var="intensity_generation", keep=y(["2021"])), "max"),
    }
    for n, r in picks.items():
        figs[key(r)] = r["v"]
        info[f"uri.{n}"] = [r["d"], r["v"]]
    info["uri.study.ERCO"] = studies(rows, ev, "eia930:ERCO", "demand_mwh", figs, True)
    info["uri.study.hub"] = studies(rows, ev, "ercot:HB_HUBAVG", "rt_mean", figs, False)


def template(rows, ev, grids, figs, info, hub=None):
    s0, s1 = WIN[ev]
    w = lambda d: s0 <= d <= s1  # noqa: E731
    for g in grids:
        hi = best(sel(rows, ev, g, "demand_max_pct_vs_baseline", w), "max")
        peak = next(iter(sel(rows, ev, g, "demand_max_mw", lambda d: d == hi["d"])), None) if hi else None
        top = best(sel(rows, ev, g, "demand_max_mw", w), "max")
        ci = best(sel(rows, ev, g, "intensity_generation", w), "max")
        for n, r in (("hi", hi), ("peak", peak), ("top", top), ("ci", ci)):
            if r:
                figs[key(r)] = r["v"]
                info[f"{ev}.{g}.{n}"] = [r["d"], r["v"]]
            else:
                info[f"{ev}.{g}.{n}"] = None
    if hub:
        for var in ("rt_max", "rt_mean", "da_max"):
            r = best(sel(rows, ev, hub, var, w), "max")
            figs[key(r)] = r["v"]
            info[f"{ev}.hub.{var}"] = [r["d"], r["v"]]


def regions(ev, figs, info):
    f = json.load(open(os.path.join(ROOT, "site", "data", "regions", "events", ev + ".json"), encoding="utf-8"))
    step = f["hours"].get("step_hours") or 1
    ok = lambda v: isinstance(v, (int, float))  # noqa: E731
    t0 = dt.datetime.fromisoformat(f["hours"]["start"].replace("Z", "+00:00"))
    reach, withd = [], []
    for c in REGIONS:
        r = f["regions"].get(c)
        if not r:
            continue
        b = r.get("baseline", {})

        def vs(a, bb):
            if not a or not bb:
                return None
            pairs_ = [(x, z) for x, z in zip(a, bb) if ok(x) and ok(z)]
            if not pairs_:
                return None
            sa, sb = sum(x for x, _ in pairs_), sum(z for _, z in pairs_)
            return dict(mwh=sa * step, diff=(sa - sb) * step, pct=((sa - sb) / abs(sb) * 100) if sb else None, n=len(pairs_))
        d = vs(r.get("demand_mw"), b.get("demand_mw"))
        if d:
            figs[f"{ev}#wc|{c}|demand_gwh"] = d["mwh"] / 1000
            if d["pct"] is not None:
                figs[f"{ev}#wc|{c}|demand_pct"] = d["pct"]
                withd.append(c)
                if abs(d["pct"]) >= 5:
                    reach.append(c)
        dm = r.get("demand_mw") or []
        held = [i for i, v in enumerate(dm) if ok(v)]
        if held:
            i = max(held, key=lambda i: (dm[i], -i))
            figs[f"{ev}#wc|{c}|peak_mw"] = dm[i]
            info[f"{ev}.wc.{c}.peak_at"] = (t0 + dt.timedelta(hours=i * step)).strftime("%Y-%m-%d %H:%M UTC")
            bd = (b.get("demand_mw") or [None] * len(dm))[i]
            if ok(bd):
                figs[f"{ev}#wc|{c}|peak_base_mw"] = bd
        figs[f"{ev}#wc|{c}|hours"] = len(held)
        for s in SOURCES:
            x = vs((r.get("gen") or {}).get(s), (b.get("gen") or {}).get(s))
            if x:
                figs[f"{ev}#wc|{c}|gen|{s}"] = x["diff"] / 1000
        x = vs(r.get("net_generation_mw"), b.get("net_generation_mw"))
        if x:
            figs[f"{ev}#wc|{c}|gen|net"] = x["diff"] / 1000
    figs[f"reached|{ev}|n"] = len(reach)
    figs[f"reached|{ev}|of"] = len(withd)
    info[f"{ev}.wc.reached"] = reach


def main():
    src, out = sys.argv[1], sys.argv[2]
    rows = read(src)
    figs, info = {}, {}
    uri(rows, figs, info)
    template(rows, "caiso_heat_2020", ["eia930:CISO"], figs, info)
    for n in ("2020-08-14", "2020-08-15"):
        r = sel(rows, "caiso_heat_2020", "eia930:CISO", "demand_max_pct_vs_baseline", lambda d, n=n: d == n)[0]
        figs[key(r)] = r["v"]
        info[f"caiso_heat_2020.{n}"] = r["v"]
    info["caiso_heat_2020.study.CISO"] = studies(rows, "caiso_heat_2020", "eia930:CISO", "demand_mwh", figs, True)
    eg = ["eia930:PJM", "eia930:MISO", "eia930:SWPP", "eia930:NYIS", "eia930:ISNE", "eia930:ERCO"]
    template(rows, "elliott_2022", eg, figs, info, hub="ercot:HB_HUBAVG")
    r = sel(rows, "elliott_2022", "eia930:SWPP", "demand_max_mw", lambda d: d == "2022-12-23")[0]
    figs[key(r)] = r["v"]
    for g in ["eia930:PJM", "eia930:ERCO", "eia930:ISNE", "eia930:MISO", "eia930:NYIS", "eia930:SWPP"]:
        info[f"elliott_2022.study.{g}"] = studies(rows, "elliott_2022", g, "demand_mwh", figs, g == "eia930:PJM")
    info["elliott_2022.study.hub"] = studies(rows, "elliott_2022", "ercot:HB_HUBAVG", "rt_mean", figs, False)
    for ev in WIN:
        regions(ev, figs, info)
    json.dump(dict(figures=figs, info=info), open(out, "w", encoding="utf-8"), indent=1)
    print(f"{len(figs)} figures restated; info {len(info)} entries -> {out}")
    for k in sorted(info):
        if ".study." in k:
            print(k, json.dumps(info[k]))


if __name__ == "__main__":
    main()

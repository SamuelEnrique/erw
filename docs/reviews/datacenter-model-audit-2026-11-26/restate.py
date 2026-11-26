# Session 10203: an independent restatement of /cost-of-power's default case (and the flexible example) from the
# page's own files (site/data/datacenter/), written from docs/methods/datacenter_pays_algorithm.md, not from
# lib/datacenter.ts. Standard library only. Prints JSON of every figure, full precision.
#   python runs/c10203/restate.py <site dir> [grid] [region] [buy]
import json
import math
import os
import sys

SITE = sys.argv[1] if len(sys.argv) > 1 else "site"
GRID = sys.argv[2] if len(sys.argv) > 2 else "ercot"
REGION = sys.argv[3] if len(sys.argv) > 3 else None
BUY = sys.argv[4] if len(sys.argv) > 4 else "rt"
D = os.path.join(SITE, "data", "datacenter")
INDEX = json.load(open(os.path.join(D, "index.json"), encoding="utf-8"))
G = INDEX["grids"][GRID]
REGION = REGION or G["main"]
NEAR = 0.95
MW = 100.0
GPU, PUE = 1.3, 1.56
LIFE, HURDLE = 20, 9.6
DAYS = [31, 28, 31, 30, 31, 30, 31, 31, 30, 31, 30, 31]


def jsround(x):
    """Math.round of JavaScript: halves go up."""
    return math.floor(x + 0.5)


def leap(y):
    return (y % 4 == 0 and y % 100 != 0) or y % 400 == 0


def hours_in(y):
    return 8784 if leap(y) else 8760


def load_years(grid):
    ys = sorted(G["years"]) if grid == GRID else sorted(INDEX["grids"][grid]["years"])
    files = {y: json.load(open(os.path.join(D, f"{grid}_{y}.json"), encoding="utf-8")) for y in ys}
    out = []
    for y in range(ys[0], ys[-1] + 1):
        out.append(files.get(y, {"year": y, "hours": hours_in(y), "regions": {}}))
    return out


def series(f, region, buy):
    p = [None] * f["hours"]
    s = f["regions"].get(region, {}).get(buy)
    if s:
        for i, v in enumerate(s["v"]):
            p[s["s"] + i] = v
    return p


def month_bounds(y):
    st = [0]
    for m in range(12):
        st.append(st[-1] + 24 * (DAYS[m] + (1 if m == 1 and leap(y) else 0)))
    return st


def months(years, pays, ws, tights=None):
    out = []
    for k, f in enumerate(years):
        y = f["year"]
        st = month_bounds(y)
        p, w = pays[k], ws[k]
        tight = set((tights or {}).get(y, []))
        for m in range(12):
            r = dict(m=f"{y}-{m + 1:02d}", due=st[m + 1] - st[m], held=0, flat=0.0, cost=0.0, energy=0.0, down=0, tight=0, tightDown=0)
            for i in range(st[m], st[m + 1]):
                v = p[i]
                if i in tight:
                    r["tight"] += 1
                    if v is not None and w[i] == 0:
                        r["tightDown"] += 1
                if v is None:
                    continue
                r["held"] += 1
                r["flat"] += v
                r["cost"] += v * w[i]
                r["energy"] += w[i]
                if w[i] == 0:
                    r["down"] += 1
            r["complete"] = r["held"] >= NEAR * r["due"]
            if r["held"]:
                out.append(r)
    return out


def prev(m, k):
    y, mo = int(m[:4]), int(m[5:7]) - 1 - k
    y += mo // 12
    mo %= 12
    return f"{y}-{mo + 1:02d}"


def last_twelve(ms):
    by = {r["m"]: r for r in ms}
    for r in reversed(ms):
        if not r["complete"]:
            continue
        tw = [by.get(prev(r["m"], k)) for k in range(12)]
        if all(t and t["complete"] for t in tw):
            return list(reversed(tw))
    return None


def span(ms):
    t = dict(held=0, cost=0.0, flatCost=0.0, energy=0.0, down=0)
    for r in ms:
        t["held"] += r["held"]
        t["cost"] += r["cost"]
        t["flatCost"] += r["flat"]
        t["energy"] += r["energy"]
        t["down"] += r["down"]
    t["flat"] = t["flatCost"] / t["held"] if t["held"] else None
    t["per"] = t["cost"] / t["energy"] if t["energy"] else None
    return t


def bad_month(ms):
    l12 = last_twelve(ms)
    done = [r for r in ms if r["complete"]]
    to = (l12[-1] if l12 else done[-1])["m"]
    fr = prev(to, 35)
    win = [r for r in done if fr <= r["m"] <= to and r["energy"] > 0]
    s = sorted(win, key=lambda r: (-(r["cost"] / r["energy"]), r["m"]))
    k = max(0, math.ceil(0.1 * len(s)) - 1)
    return s[k], len(win)


def flat_weights(p):
    return [0 if v is None else 1 for v in p]


def shed_share(run, n, pct):
    return min(1, n / 8760) if run == "hours" else min(1, pct / 100) if run == "share" else 0


def rule(years, pays, das, run, n=100, pct=5, shift=20):
    """The forecast rule, written from the note's section 5.1."""
    ws = [flat_weights(p) for p in pays]
    if run == "flat":
        return ws
    if run == "shift":
        h = 24 * min(50, max(0, shift)) / 100
        wh, part = math.floor(h), h - math.floor(h)
        for k in range(len(years)):
            da, pay = das[k], pays[k]
            for d in range(0, len(da) - 23, 24):
                idx = [i for i in range(d, d + 24) if da[i] is not None]
                if len(idx) < 24 or sum(1 for i in range(d, d + 24) if pay[i] is not None) < 24:
                    continue
                idx.sort(key=lambda i: (-da[i], i))
                for j in range(wh):
                    ws[k][idx[j]] -= 1
                    ws[k][idx[23 - j]] += 1
                if part > 0:
                    ws[k][idx[wh]] -= part
                    ws[k][idx[23 - wh]] += part
        return ws
    q = shed_share(run, n, pct)
    flat_da = [v for da in das for v in da]
    starts = []
    t = 0
    for da in das:
        starts.append(t)
        t += len(da)
    for k in range(len(years)):
        da, pay = das[k], pays[k]
        left = jsround(q * len(pay))
        for d in range(0, len(da) - 23, 24):
            g = starts[k] + d
            if g < 720:
                continue
            prior = [v for v in flat_da[g - 720:g] if v is not None]
            if len(prior) < NEAR * 720:
                continue
            kk = min(len(prior), max(1, jsround(q * len(prior))))
            if q <= 0:
                continue
            prior.sort(reverse=True)
            thr = prior[kk - 1]
            if left <= 0:
                continue
            over = [i for i in range(d, d + 24) if da[i] is not None and da[i] >= thr and pay[i] is not None]
            over.sort(key=lambda i: (-da[i], i))
            for i in over[:left]:
                ws[k][i] = 0
            left -= min(left, len(over))
    return ws


def foreseen(years, pays, run, n=100, pct=5, shift=20):
    ws = [flat_weights(p) for p in pays]
    q = shed_share(run, n, pct)
    for k in range(len(years)):
        p = pays[k]
        if run in ("hours", "share"):
            held = sorted([i for i in range(len(p)) if p[i] is not None], key=lambda i: (-p[i], i))
            kk = min(len(held), jsround(q * len(p)))
            for i in held[:kk]:
                ws[k][i] = 0
        elif run == "shift":
            h = 24 * min(50, max(0, shift)) / 100
            wh, part = math.floor(h), h - math.floor(h)
            for d in range(0, len(p) - 23, 24):
                idx = [i for i in range(d, d + 24) if p[i] is not None]
                if len(idx) < 24:
                    continue
                idx.sort(key=lambda i: (-p[i], i))
                for j in range(wh):
                    ws[k][idx[j]] -= 1
                    ws[k][idx[23 - j]] += 1
                if part > 0:
                    ws[k][idx[wh]] -= part
                    ws[k][idx[23 - wh]] += part
    return ws


def by_year(ms):
    out = {}
    for y in sorted({r["m"][:4] for r in ms}):
        done = [r for r in ms if r["m"].startswith(y) and r["complete"]]
        if done:
            s = span(done)
            out[y] = dict(flat=s["flat"], per=s["per"], months=len(done))
    return out


def way(ms):
    l = last_twelve(ms)
    s = span(l)
    b, of = bad_month(ms)
    return dict(per=s["per"], cost=s["cost"], energy=s["energy"], held=s["held"], flatCost=s["flatCost"], down=s["down"], flat=s["flat"],
                bad=dict(m=b["m"], per=b["cost"] / b["energy"], cost=b["cost"]), of=of, first=l[0]["m"], last=l[-1]["m"])


def finance(w, adder=0.0, growth=0.0, upfront=0.0, life=LIFE, hurdle=HURDLE, gpu=GPU, pue=PUE):
    r, g = hurdle / 100, growth / 100
    bill = w["cost"] + adder * w["energy"]
    pv = upfront * 1000 + sum(bill * (1 + g) ** (t - 1) / (1 + r) ** t for t in range(1, life + 1))
    ann = sum(1 / (1 + r) ** t for t in range(1, life + 1))
    lev = (w["cost"] / w["energy"]) * sum((1 + g) ** (t - 1) / (1 + r) ** t for t in range(1, life + 1)) / ann
    price = w["cost"] / w["energy"] + adder
    gpus = 1000 / (gpu * pue)
    gh = w["energy"] * gpus
    out = dict(price=price, bill=bill, gpuHour=price * gpu * pue / 1000, gpusPerMw=gpus, gpuHours=gh, pv=pv, level=lev, allIn=pv / (gh * ann))
    mwh = w["held"] - w["energy"]
    if w["down"] > 0 and mwh > 1e-9:
        pm = (w["flatCost"] - w["cost"]) / mwh + adder
        out["off"] = dict(hours=w["down"], mwh=mwh, perMwh=pm, perGpuHour=pm * gpu * pue / 1000)
    return out


def main():
    years = load_years(GRID)
    pay = [series(f, REGION, BUY) for f in years]
    da = [series(f, REGION, "da") for f in years]
    tights = {f["year"]: f.get("tight", []) for f in years}
    res = dict(grid=GRID, region=REGION, buy=BUY)
    ms = months(years, pay, [flat_weights(p) for p in pay], tights)
    flat = way(ms)
    res["flat"] = flat
    res["flat_finance"] = finance(flat)
    res["gpus_100mw"] = MW * 1000 / (GPU * PUE)
    res["by_year"] = by_year(ms)
    region = next(r for r in G["regions"] if r["id"] == REGION)
    if region.get("ref"):
        hp = [series(f, region["ref"], BUY) for f in years]
        hm = [r for r in months(years, hp, [flat_weights(p) for p in hp]) if flat["first"] <= r["m"] <= flat["last"] and r["complete"]]
        if len(hm) == 12:
            res["hub"] = dict(id=region["ref"], flat=span(hm)["flat"], diff=flat["flat"] - span(hm)["flat"])
    if BUY == "rt" and region.get("da"):
        dm = months(years, da, [flat_weights(p) for p in da])
        res["da_l12"] = span(last_twelve(dm))["per"]
    # the scarce hours of the last twelve months, flat
    l12 = set(r["m"] for r in last_twelve(ms))
    sc_h, sc_usd = 0, 0.0
    for k, f in enumerate(years):
        st = month_bounds(f["year"])
        for m in range(12):
            if f"{f['year']}-{m + 1:02d}" not in l12:
                continue
            for i in range(st[m], st[m + 1]):
                v = pay[k][i]
                if v is not None and v >= 1000:
                    sc_h += 1
                    sc_usd += v * MW
    res["scarce"] = dict(hours=sc_h, flat_usd=sc_usd)
    # the flexible way the scenarios compare (off in 100 hours, the rule), and the flexible example
    for run, kw in (("hours", dict(n=100)), ("share", dict(pct=5)), ("shift", dict(shift=20))):
        w_rule = rule(years, pay, da, run, **kw)
        w_fore = foreseen(years, pay, run, **kw)
        mr = months(years, pay, w_rule, tights)
        mf = months(years, pay, w_fore, tights)
        wr, wf = way(mr), way(mf)
        saved = flat["flat"] - wr["per"]
        saved_f = flat["flat"] - wf["per"]
        res[f"rule_{run}"] = dict(way=wr, finance=finance(wr), saved=saved, foreseen_per=wf["per"], foreseen_saved=saved_f,
                                  kept_pct=100 * saved / saved_f if saved_f else None, foreseen_down=wf["down"])
    print(json.dumps(res, indent=1))


if __name__ == "__main__":
    main()

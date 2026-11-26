"""Session 10218: every figure /prices/compare draws (draw_compare.json, the page's own function on its own file) against
the restatement (restate_compare_fill.json), with the page's choices (cheapest, dearest, most hours below zero, widest
spread, the order, B less A) made again here from the restated rows.

    python check_drawn.py <draw json> <restate json>
"""
import json
import sys

D = json.load(open(sys.argv[1], encoding="utf-8"))
R = json.load(open(sys.argv[2], encoding="utf-8"))["rows"]
MEAS = [("avg", "avg_price"), ("neg", "negative_hours_share_pct"), ("high", "above_200_hours_share_pct"), ("spread", "day_spread_top4_bottom4")]


def two(v):
    return f"{round(v + 0.0, 2):,.2f}"


def val(r, market, slug):
    if slug == "carbon":
        return r.get("grid_carbon_intensity")
    f = dict(MEAS)[slug]
    return r.get(f"{market}_{f}")


tot = ok = 0
bad = []


def check(view, key, want):
    global tot, ok
    got = D[view]["marked"].get(key)
    tot += 1
    if got == want:
        ok += 1
    else:
        bad.append(f"{view} {key}: drawn {got!r}, restated {want!r}")


for view, period, market in (("default", "year", "dam"), ("ab", "year", "dam"), ("month", "month", "dam"), ("rtm", "year", "rtm")):
    rows = [r for r in R[period].values() if val(r, market, "avg") is not None]
    rows2 = {e: {k: (round(v, 2) if isinstance(v, float) else v) for k, v in r.items()} for e, r in R[period].items()}
    rr = [rows2[r["entity"]] for r in rows]
    by = lambda slug, rev: sorted(rr, key=lambda r: ((val(r, market, slug) is None), (-1 if rev else 1) * (val(r, market, slug) or 0), r["entity"]))[0]
    cheap, dear, neg, wide = by("avg", False), by("avg", True), by("neg", True), by("spread", True)
    check(view, "count", str(len(rr)))
    check(view, "sum|cheapest", two(val(cheap, market, "avg")))
    check(view, "sum|dearest", two(val(dear, market, "avg")))
    if val(neg, market, "neg") > 0:
        check(view, "sum|negative", two(val(neg, market, "neg")))
    check(view, "head|cheapest", two(val(cheap, market, "avg")))
    check(view, "head|dearest", two(val(dear, market, "avg")))
    check(view, "head|negative", two(val(neg, market, "neg")))
    check(view, "head|spread", two(val(wide, market, "spread")))
    for r in rr:
        for slug in ("avg", "neg", "high", "spread", "carbon"):
            v = val(r, market, slug)
            if v is not None:
                check(view, f"{r['entity']}|{slug}", two(v))
        check(view, f"{r['entity']}|hours", f"{r[market + '_hours_held']:,}")
    order = [r["entity"] for r in sorted(rr, key=lambda r: (val(r, market, "avg"), r["entity"]))]
    tot += 1
    if D[view]["bars"][: len(order)] == order:
        ok += 1
    else:
        bad.append(f"{view} bars order: drawn {D[view]['bars']}, restated {order}")
    print(f"{view}: cheapest {cheap['entity']} {val(cheap, market, 'avg')}, dearest {dear['entity']} {val(dear, market, 'avg')}, "
          f"most below zero {neg['entity']} {val(neg, market, 'neg')}, widest {wide['entity']} {val(wide, market, 'spread')}, count {len(rr)}")

# A and B: ERCOT West hub against ERCOT West load zone, both markets, B less A on the figures drawn
a, b = {k: (round(v, 2) if isinstance(v, float) else v) for k, v in R["year"]["ercot:HB_WEST"].items()}, {k: (round(v, 2) if isinstance(v, float) else v) for k, v in R["year"]["ercot:LZ_WEST"].items()}
for m in ("dam", "rtm"):
    for slug, _ in MEAS:
        x, y = val(a, m, slug), val(b, m, slug)
        check("ab", f"ab|a|{m}|{slug}", two(x))
        check("ab", f"ab|b|{m}|{slug}", two(y))
        d = round((y - x) * 100) / 100 or 0
        check("ab", f"ab|diff|{m}|{slug}", two(d))
    check("ab", f"ab|a|{m}|hours", f"{a[m + '_hours_held']:,}")
    check("ab", f"ab|b|{m}|hours", f"{b[m + '_hours_held']:,}")
check("ab", "ab|a|carbon", two(a["grid_carbon_intensity"]))
check("ab", "ab|b|carbon", two(b["grid_carbon_intensity"]))

print(f"drawn figures checked {tot}, equal {ok}")
for x in bad:
    print("  ", x)
unchecked = {v: sorted(set(D[v]["marked"]) - set()) for v in D}
print("marked keys per view:", {v: len(D[v]["marked"]) for v in D})
print("== the default view's sentence and headline, as drawn")
t = D["default"]["text"]
i = t.find("Over the twelve")
print(t[i:i + 700])

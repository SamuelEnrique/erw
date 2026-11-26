"""Session 10231: the demand growth explorer's default view (ERCOT, the whole year's average hour), restated.

From the table's levels alone (avg_demand_mw, peak_demand_mw, ytd_avg_demand_mw, hours_used), by the method note's
rules: growth = level / 2019's level - 1, in percent, from the levels as the table writes them; on the year before
the same with the year before; the hours in a local year 8,760 or 8,784; each grid at its own last whole year (the
newest with an annual average), the year so far at the newest year; the bars largest first. The levels themselves
were restated from EIA-930's hours by the consumption page's audit of tonight (24,204 values equal); here they are read.
Written by the page's rule (MW whole, a percent to two decimals with its sign) and set beside the slots drawn by
site/scripts/demand-growth-figures.mjs.

    python restate_dg.py <eia930_demand_growth.csv> <dg_opening.json>
"""
import csv
import json
import sys
from decimal import Decimal, ROUND_HALF_UP

GRIDS = [("ercot", "ERCO", "ERCOT"), ("caiso", "CISO", "CAISO"), ("pjm", "PJM", "PJM"), ("miso", "MISO", "MISO"),
         ("spp", "SWPP", "SPP"), ("nyiso", "NYIS", "NYISO"), ("isone", "ISNE", "ISO-NE"), ("us48", "US48", "Lower 48")]


def two(x):
    q = Decimal(repr(round(x, 6))).quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)
    return f"{q:,.2f}"


def signed(x):
    return ("+" if x > 0 else "") + two(x)


def whole(x):
    return f"{int(Decimal(repr(x)).quantize(Decimal('1'), rounding=ROUND_HALF_UP)):,}"


def main():
    T = {}
    with open(sys.argv[1], newline="", encoding="utf-8") as f:
        for r in csv.DictReader(l for l in f if not l.startswith("#")):
            T[(r["entity"].split(":")[1], r["variable"], int(r["ts_utc"][:4]))] = float(r["value"])
    view = json.load(open(sys.argv[2], encoding="utf-8"))["views"][0]
    S = view["slots"]

    def g(ba, v, y):
        return T.get((ba, v, y))

    def growth(ba, v, y, base=2019):
        a, b = g(ba, v, y), g(ba, v, base)
        return None if a is None or b is None else (a / b - 1) * 100

    def last_whole(ba):
        return max(y for (b, v, y) in T if b == ba and v == "avg_demand_mw")

    def newest(ba):
        return max(y for (b, v, y) in T if b == ba and v == "ytd_avg_demand_mw")

    mine = {}
    lw, nw = last_whole("ERCO"), newest("ERCO")
    mine["h1.value"] = signed(growth("ERCO", "avg_demand_mw", lw))
    mine["h1.note"] = f"2019: {whole(g('ERCO', 'avg_demand_mw', 2019))} MW; {lw}: {whole(g('ERCO', 'avg_demand_mw', lw))} MW"
    mine["h2.value"] = whole(g("ERCO", "avg_demand_mw", lw))
    mine["h2.note"] = f"2019: {whole(g('ERCO', 'avg_demand_mw', 2019))} MW"
    mine["h3.value"] = signed(growth("ERCO", "ytd_avg_demand_mw", nw))
    bars = []
    for slug, ba, name in GRIDS:
        y = last_whole(ba)
        v = growth(ba, "avg_demand_mw", y)
        bars.append((v, name, y))
        mine[f"bar1.{name}"] = f"{name}: {signed(v)} percent from 2019 to {y}"
        mine[f"grid.{slug}.base"] = whole(g(ba, "avg_demand_mw", 2019))
        mine[f"grid.{slug}.latest"] = whole(g(ba, "avg_demand_mw", y))
        mine[f"grid.{slug}.growth"] = signed(v)
    mine["bar1.order"] = " | ".join(n for _, n, _ in sorted(bars, key=lambda b: -b[0]))
    for y in range(2019, nw + 1):
        if g("ERCO", "avg_demand_mw", y) is not None:
            mine[f"year.{y}.0"] = str(y)
            mine[f"year.{y}.1"] = whole(g("ERCO", "avg_demand_mw", y))
            mine[f"bar3.{y}"] = f"ERCOT, {y}: {whole(g('ERCO', 'avg_demand_mw', y))} MW"
            if y > 2019:
                mine[f"year.{y}.2"] = signed(growth("ERCO", "avg_demand_mw", y))
                mine[f"year.{y}.3"] = signed(growth("ERCO", "avg_demand_mw", y, y - 1))
            else:
                mine[f"year.{y}.2"] = mine[f"year.{y}.3"] = "base year"
            mine[f"year.{y}.4"] = whole(g("ERCO", "hours_used", y))
            mine[f"year.{y}.5"] = f"{8784 if y % 4 == 0 else 8760:,}"
        if y > 2019:
            parts = []
            for v, label in (("avg_demand_mw", "average hour, whole year"), ("peak_demand_mw", "highest hour, whole year"), ("ytd_avg_demand_mw", "the year so far (January to October)")):
                x = growth("ERCO", v, y)
                parts.append(f"{label} {'not held' if x is None else signed(x) + ' percent'}")
            mine[f"bar2.{y}"] = f"ERCOT, {y}: " + "; ".join(parts)
    eq = 0
    diff = []
    for k, v in mine.items():
        if S.get(k) == v:
            eq += 1
        else:
            diff.append((k, S.get(k), v))
    print(f"slots restated: {eq} of {len(mine)} equal the page's text")
    for d in diff:
        print("  differs:", d)
    # the table's own growth rows against growth from its levels
    worst = 0.0
    n = 0
    for (ba, v, y), x in T.items():
        if v == "avg_demand_growth_since_2019_pct":
            m = growth(ba, "avg_demand_mw", y)
            n += 1
            worst = max(worst, abs(round(m, 2) - round(x, 2)))
    print(f"the table's {n} average growth rows against growth from its levels: largest gap at two decimals {worst:.2f}")
    # the claims of the decisions block
    hu = [(g(ba, "hours_used", y) / g(ba, "hours_in_year", y), ba, y, g(ba, "hours_used", y), g(ba, "hours_in_year", y))
          for (ba, v, y) in T if v == "hours_used" and g(ba, "hours_in_year", y)]
    hu.sort()
    print("the fewest hours used of a whole year:", hu[:3])
    print("MISO 2025 peak:", g("MISO", "peak_demand_mw", 2025), "growth", g("MISO", "peak_demand_growth_since_2019_pct", 2025))
    print("unmatched slots of the view not restated here:", sorted(k for k in S if k not in mine and not k.endswith(".drawn"))[:60])


if __name__ == "__main__":
    main()

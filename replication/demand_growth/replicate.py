"""Energy Research Warehouse (ERW), session 7508 (chain 304): the demand growth explorer (/explore/demand-growth), every
figure of every view, written again from the method note and the table alone.

    python replication/demand_growth/replicate.py                      # the figures, from the rows beside this file
    python replication/demand_growth/replicate.py --headline           # the five headline figures (the do-file's lines)
    python replication/demand_growth/replicate.py --table=<eia930_demand_growth.csv> --page=<drawn.json> [--write]

Written from docs/methods/demand_growth.md, "The tool as a reader meets it" (the views, the row each figure reads, how a
figure is written), not from the page's code. The table is public: eia930_demand_growth, as the page's own download
gives it or as warehouse/output holds it; table_rows.csv beside this file is the rows the page reads (every variable
but the month-and-hour cells, which the explorer does not draw), with the table's header, as this machine held it on
16 November 2026.

Two things are done for every view (8 grids by 39 windows, 312, and the page as it opens):

1. Which row a figure is, and how it is written: the grid's last whole year or its newest year, the window's variable,
   MW whole, percent to two decimals, a growth with its sign, "not held" with no unit where the table has no row.
2. The arithmetic the table itself carries, done again from its MW rows: growth since 2019 and on the year before
   (percent, two decimals), and a month's or an hour's change from 2019 (MW to one decimal, percent to two). A growth
   figure of the replication is this recomputed value, not the table's growth row.

--page names the page drawn with the site's own code (site/scripts/demand-growth-figures.mjs on the same rows); each
slot of text the page draws is then set beside the replication's. A figure is inside when the two texts are the same,
or when both are numbers and differ by less than half the page's last shown digit. The rows of the table themselves
are recomputed from EIA's hourly demand by from_hourly.py.
"""
import csv
import json
import math
import os
import re
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
TABLE = "eia930_demand_growth"
BASE = 2019
MONTHS = ["January", "February", "March", "April", "May", "June", "July", "August", "September", "October", "November", "December"]
# the note's table of grids, in the order the page lists them
GRIDS = [("ercot", "ERCO", "ERCOT"), ("caiso", "CISO", "CAISO"), ("pjm", "PJM", "PJM"), ("miso", "MISO", "MISO"), ("spp", "SWPP", "SPP"),
         ("nyiso", "NYIS", "NYISO"), ("isone", "ISNE", "ISO-NE"), ("us48", "US48", "Lower 48")]


def windows():
    """The note's table of windows: slug, the words in a title, the MW variable, the growth variable, the change in MW
    (a month and an hour only), and whether growth is read at the newest year (the year so far) or the last whole year."""
    w = [
        dict(slug="avg", label="Whole year, average hour", short="average demand", mw="avg_demand_mw", growth="avg_demand_growth_since_2019_pct", change=None, newest=False),
        dict(slug="peak", label="Whole year, highest hour", short="peak demand", mw="peak_demand_mw", growth="peak_demand_growth_since_2019_pct", change=None, newest=False),
        dict(slug="ytd", label="The year so far, average hour", short="average demand, the year so far", mw="ytd_avg_demand_mw", growth="ytd_avg_demand_growth_since_2019_pct", change=None, newest=True),
    ]
    for i, m in enumerate(MONTHS):
        k = f"m{i + 1:02d}"
        w.append(dict(slug=k, label=f"{m}, average hour", short=f"average demand in {m}", mw=f"avg_demand_mw_{k}", growth=f"growth_pct_{k}", change=f"growth_mw_{k}", newest=False))
    for h in range(24):
        k = f"h{h:02d}"
        w.append(dict(slug=k, label=f"{h:02d}:00 local, average over the year", short=f"average demand at {h:02d}:00 local", mw=f"avg_demand_mw_{k}", growth=f"growth_pct_{k}", change=f"growth_mw_{k}", newest=False))
    return w


def read_table(path):
    header, rows = [], {}
    with open(path, encoding="utf-8", newline="") as fh:
        lines = fh.read().replace("\r\n", "\n").split("\n")
    body = [l for l in lines if l and not l.startswith("#")]
    header = [l[1:].strip() for l in lines if l.startswith("#")]
    for r in csv.DictReader(body):
        rows[(r["entity"], r["variable"], int(r["ts_utc"][:4]))] = float(r["value"])
    return header, rows


# ---- how a figure is written
def js_round(x):
    return math.floor(x + 0.5)


def whole(x):
    return f"{js_round(x):,}"


def two(x):
    return f"{x:,.2f}"


def signed_two(x):
    return ("+" if x > 0 else "") + two(x)


class Table:
    def __init__(self, header, rows):
        self.rows = rows
        m = re.search(r"year to date: 1 January to the end of (\d{2})/(\d{4})", "\n".join(header))
        self.through = (int(m.group(1)), int(m.group(2))) if m else None

    def v(self, e, var, y):
        return None if y is None else self.rows.get((e, var, y))

    def years(self, e, var):
        return sorted(y for (ee, vv, y) in self.rows if ee == e and vv == var)

    def last_whole(self, e):
        y = self.years(e, "avg_demand_mw")
        return y[-1] if y else None

    def newest(self, e):
        y = self.years(e, "ytd_avg_demand_mw")
        return y[-1] if y else None

    def latest(self, e, w):
        return self.newest(e) if w["newest"] else self.last_whole(e)

    # ---- the arithmetic the table carries, done again from its MW rows (rule 6 of the note)
    def growth(self, e, var, y):
        """The growth the page shows under `var`, recomputed from the MW rows; None where the table writes none."""
        if self.v(e, var, y) is None:
            return None, None
        held = self.v(e, var, y)
        pairs = {"avg_demand_growth_since_2019_pct": ("avg_demand_mw", BASE), "peak_demand_growth_since_2019_pct": ("peak_demand_mw", BASE),
                 "ytd_avg_demand_growth_since_2019_pct": ("ytd_avg_demand_mw", BASE), "avg_demand_growth_yoy_pct": ("avg_demand_mw", y - 1)}
        if var in pairs:
            mw, y0 = pairs[var]
            a, b = self.v(e, mw, y), self.v(e, mw, y0)
            return (None if a is None or b is None else round((a / b - 1) * 100 + 0.0, 2)), held
        m = re.match(r"growth_(pct|mw)_(.+)$", var)
        a, b = self.v(e, f"avg_demand_mw_{m.group(2)}", y), self.v(e, f"avg_demand_mw_{m.group(2)}", BASE)
        if a is None or b is None:
            return None, held
        return (round((a / b - 1) * 100 + 0.0, 2) if m.group(1) == "pct" else round(a - b + 0.0, 1)), held


def view(t, grid, w, arithmetic):
    """Every slot of text of one view, by the note's rules. `arithmetic` collects each growth recomputed beside the table's row."""
    slug, ba, name = grid
    e = f"eia930:{ba}"
    s = {}
    through = t.through
    month = MONTHS[through[0] - 1] if through else None
    so = lambda y: f" so far (January to {month})" if through and y == through[1] else ""
    latest, last_whole, newest = t.latest(e, w), t.last_whole(e), t.newest(e)
    when = lambda y: "" if y is None else f"{y}{so(y) if w['newest'] else ''}"
    ytd_words = lambda y: "" if y is None else f"{y}{so(y) or (f' (January to {month})' if through else '')}"

    def mw(ent, var, y):
        x = t.v(ent, var, y)
        return "not held" if x is None else whole(x)

    def g(ent, var, y):
        """A growth: percent to two decimals, MW whole, its sign before it; recomputed from the MW rows."""
        x, held = t.growth(ent, var, y) if y is not None else (None, None)
        if held is None:
            return "not held"
        arithmetic.append((ent, var, y, held, x))
        x = held if x is None else x
        return ("+" if x > 0 else "") + (whole(x) if var.startswith("growth_mw") else two(x))

    def unit(ent, var, y, u):
        return u if t.v(ent, var, y) is not None else ""

    def with_mw(ent, var, y):
        return mw(ent, var, y) + (" MW" if t.v(ent, var, y) is not None else "")

    cap = lambda x: x[0].upper() + x[1:]
    s["h1.label"] = f"Growth since {BASE}, {w['short']}, {name}, {when(latest)}"
    s["h1.value"] = g(e, w["growth"], latest)
    s["h1.unit"] = unit(e, w["growth"], latest, "percent")
    s["h1.note"] = f"{BASE}{f', January to {month}' if w['newest'] and through else ''}: {with_mw(e, w['mw'], BASE)}; {latest if latest is not None else ''}: {with_mw(e, w['mw'], latest)}"
    s["h2.label"] = f"{cap(w['short'])}, {name}, {when(latest)}"
    s["h2.value"] = mw(e, w["mw"], latest)
    s["h2.unit"] = unit(e, w["mw"], latest, "MW")
    s["h2.note"] = f"{BASE}: {with_mw(e, w['mw'], BASE)}"
    if w["change"]:
        s["h3.label"] = f"Change since {BASE}, {w['short']}, {name}, {when(latest)}"
        s["h3.value"], s["h3.unit"] = g(e, w["change"], latest), unit(e, w["change"], latest, "MW")
    elif w["slug"] == "ytd":
        s["h3.label"] = f"Average demand growth since {BASE}, whole year, {name}, {last_whole if last_whole is not None else ''}"
        s["h3.value"], s["h3.unit"] = g(e, "avg_demand_growth_since_2019_pct", last_whole), unit(e, "avg_demand_growth_since_2019_pct", last_whole, "percent")
    else:
        s["h3.label"] = f"The year so far: growth since {BASE}, {name}, {ytd_words(newest)}"
        s["h3.value"], s["h3.unit"] = g(e, "ytd_avg_demand_growth_since_2019_pct", newest), unit(e, "ytd_avg_demand_growth_since_2019_pct", newest, "percent")

    # the headline chart: one bar a grid at its own latest year, largest first, a grid without a row last
    by_grid = []
    for (gs, gb, gn) in GRIDS:
        ge = f"eia930:{gb}"
        y = t.latest(ge, w)
        x, held = t.growth(ge, w["growth"], y) if y is not None else (None, None)
        by_grid.append((gs, gn, ge, y, held if x is None else x))
    ordered = sorted(by_grid, key=lambda r: (r[4] is None, -(r[4] or 0)))
    s["bar1.order"] = " | ".join(r[1] for r in ordered)
    for (gs, gn, ge, y, x) in ordered:
        s[f"bar1.{gn}"] = f"{gn}: not held" if x is None else f"{gn}: {signed_two(x)} percent from {BASE} to {y}"
        s[f"bar1.{gn}.drawn"] = f"{gn} | not held" if x is None else f"{signed_two(x)} | {gn}" + (" | shown below" if gs == slug else "")

    # the table "Every grid"
    s["grid.head"] = " | ".join(["Grid", f"{BASE}, MW", f"{latest if latest is not None else ('Newest year' if w['newest'] else 'Last whole year')}, MW",
                                 f"Growth since {BASE}, percent"] + (["Change, MW"] if w["change"] else []))
    for (gs, gn, ge, y, x) in by_grid:
        s[f"grid.{gs}.name"] = gn
        s[f"grid.{gs}.base"] = mw(ge, w["mw"], BASE)
        s[f"grid.{gs}.latest"] = mw(ge, w["mw"], y) + (f" {y}" if y is not None and y != latest else "")
        s[f"grid.{gs}.growth"] = g(ge, w["growth"], y)
        if w["change"]:
            s[f"grid.{gs}.change"] = g(ge, w["change"], y)

    # the grid's growth by window along the years
    series = [("avg_demand_growth_since_2019_pct", "Average hour, whole year"), ("peak_demand_growth_since_2019_pct", "Highest hour, whole year"),
              ("ytd_avg_demand_growth_since_2019_pct", f"The year so far{f' (January to {month})' if through else ''}")]
    series = [x for x in series if t.years(e, x[0])]
    lower_first = lambda x: x[0].lower() + x[1:]
    for y in sorted({y for var, _ in series for y in t.years(e, var)}):
        vs = [(t.growth(e, var, y)[0] if t.v(e, var, y) is not None else None) for var, _ in series]
        s[f"bar2.{y}"] = f"{name}, {y}: " + "; ".join(f"{lower_first(nm)} {'not held' if v is None else signed_two(v) + ' percent'}" for (_, nm), v in zip(series, vs))
        s[f"bar2.{y}.drawn"] = " | ".join([""] * sum(v is not None for v in vs) + [str(y)])

    # the grid's demand in the window by year, and its table year by year
    years = t.years(e, w["mw"])
    for y in years:
        s[f"bar3.{y}"] = f"{name}, {y}: {whole(t.v(e, w['mw'], y))} MW"
        s[f"bar3.{y}.drawn"] = f"{whole(t.v(e, w['mw'], y))} | {y}"
    if years:
        per_year = w["slug"] in ("avg", "peak", "ytd")
        head = ["Year", "MW"] + ([f"Growth since {BASE}, percent"] if per_year else [])
        head += ["On the year before, percent", "Hours used", "Hours in the year"] if w["slug"] == "avg" else []
        head += ["Hours used", "Hours in the window"] if w["slug"] == "ytd" else []
        s["year.head"] = " | ".join(head)
        for y in years:
            cells = [f"{y}{so(y) if w['newest'] else ''}", mw(e, w["mw"], y)]
            if per_year:
                cells.append("base year" if y == BASE else g(e, w["growth"], y))
            if w["slug"] == "avg":
                cells += ["base year" if y == BASE else g(e, "avg_demand_growth_yoy_pct", y), mw(e, "hours_used", y), mw(e, "hours_in_year", y)]
            if w["slug"] == "ytd":
                cells += [mw(e, "ytd_hours_used", y), mw(e, "ytd_hours_in_window", y)]
            for i, c in enumerate(cells):
                s[f"year.{y}.{i}"] = c
    return s


NUMBER = re.compile(r"^[+-]?[\d,]+(\.\d+)?$")


def inside(page, mine):
    """The same text, or two numbers closer than half the page's last shown digit."""
    page = re.sub(r" ([;,.])", r"\1", page)
    if page == mine:
        return True
    if NUMBER.match(page) and NUMBER.match(mine):
        digits = len(page.split(".")[1]) if "." in page else 0
        return abs(float(page.replace(",", "")) - float(mine.replace(",", ""))) < 0.5 * 10 ** -digits and page[0] == mine[0]
    return False


def headline(t):
    e, us = "eia930:ERCO", "eia930:US48"
    y, n = t.last_whole(e), t.newest(e)
    month = MONTHS[t.through[0] - 1]
    a = []
    return [
        f"1. ERCOT, average demand, growth {BASE} to {y}, percent: {two(t.growth(e, 'avg_demand_growth_since_2019_pct', y)[0])} ({BASE}: {t.v(e, 'avg_demand_mw', BASE):,.1f} MW; {y}: {t.v(e, 'avg_demand_mw', y):,.1f} MW)",
        f"2. ERCOT, peak demand (the highest hour), growth {BASE} to {y}, percent: {two(t.growth(e, 'peak_demand_growth_since_2019_pct', y)[0])} ({BASE}: {t.v(e, 'peak_demand_mw', BASE):,.0f} MW; {y}: {t.v(e, 'peak_demand_mw', y):,.0f} MW)",
        f"3. ERCOT, the year so far (January to {month} {n}) against the same months of {BASE}, percent: {two(t.growth(e, 'ytd_avg_demand_growth_since_2019_pct', n)[0])} ({BASE}: {t.v(e, 'ytd_avg_demand_mw', BASE):,.1f} MW; {n}: {t.v(e, 'ytd_avg_demand_mw', n):,.1f} MW)",
        f"4. Lower 48, average demand, growth {BASE} to {y}, percent: {two(t.growth(us, 'avg_demand_growth_since_2019_pct', y)[0])} ({BASE}: {t.v(us, 'avg_demand_mw', BASE):,.1f} MW; {y}: {t.v(us, 'avg_demand_mw', y):,.1f} MW)",
        f"5. ERCOT, average demand, growth {y - 1} to {y}, percent: {two(t.growth(e, 'avg_demand_growth_yoy_pct', y)[0])} ({y - 1}: {t.v(e, 'avg_demand_mw', y - 1):,.1f} MW)",
    ]


def main():
    opt = dict((a[2:].split("=", 1) + [""])[:2] for a in sys.argv[1:] if a.startswith("--"))
    header, rows = read_table(opt.get("table") or os.path.join(HERE, "table_rows.csv"))
    t = Table(header, rows)
    if "headline" in opt:
        print("\n".join(headline(t)))
        return 0
    arithmetic = []
    mine = {}
    for grid in GRIDS:
        for w in windows():
            mine[(grid[0], w["slug"])] = view(t, grid, w, arithmetic)
    seen = {(a[0], a[1], a[2]): a for a in arithmetic}
    off = [a for a in seen.values() if a[4] is None or abs(a[4] - a[3]) > 1e-9]
    print(f"The table's own arithmetic: {len(seen) - len(off)} of {len(seen)} growth figures the page shows equal their recomputation from the table's MW rows")
    n_slots = sum(len(v) for v in mine.values())
    if not opt.get("page"):
        print(f"{len(mine)} views, {n_slots} slots of text written from the note and the table ({len(rows)} rows); no page given to set them beside (--page)")
        return 1 if off else 0
    with open(opt["page"], encoding="utf-8") as fh:
        page = json.load(fh)
    total = same = 0
    diffs = []
    figures = []
    default = ("ercot", "avg")
    for v in page["views"]:
        q = v["q"]
        key = (q.get("grid", default[0]), q.get("window", default[1]))
        if key not in mine:
            key = default               # an address the table does not hold falls back to the default, and the page says so
        m, p = mine[key], dict(v["slots"])
        if "bar1.order" not in p:
            p["bar1.order"] = " | ".join(k[5:] for k in p if k.startswith("bar1.") and not k.endswith(".drawn"))
        for slot in sorted(set(m) | set(p)):
            total += 1
            a, b = p.get(slot), m.get(slot)
            ok = a is not None and b is not None and inside(a, b)
            same += ok
            if not ok:
                diffs.append({"view": q, "slot": slot, "page": a, "replication": b})
            if q == {} or (slot in ("h1.value", "h2.value", "h3.value") and v["why"] == "a grid and a window"):
                figures.append({"view": "the page as it opens" if q == {} else f"grid={q['grid']}&window={q['window']}", "slot": slot, "page": a, "replication": b, "inside": bool(ok)})
    line = (f"/explore/demand-growth: {same} of {total} slots of text on {len(page['views'])} views equal the replication's "
            f"({len(page['keyed'])} distinct checked figures; {len(seen) - len(off)} of {len(seen)} growth figures recomputed from the MW rows)")
    print(line)
    for d in diffs[:40]:
        print("  differs:", json.dumps(d))
    if "write" in opt:
        about = ("The demand growth explorer (/explore/demand-growth): the page's own code drawn on the rows of eia930_demand_growth "
                 "(site/scripts/demand-growth-figures.mjs) beside the replication (replication/demand_growth/replicate.py). Held here: every slot of the "
                 "page as it opens, and the three headline numbers of each of the 312 views; the run itself compares every slot of every view.")
        with open(os.path.join(HERE, "page_figures.json"), "w", encoding="utf-8", newline="\n") as fh:
            json.dump({"_about": about, "line": line, "table_rows_read": len(rows), "year_to_date_through": f"{t.through[0]:02d}/{t.through[1]}",
                       "views": len(page["views"]), "slots_all_views": total, "equal_all_views": same, "differences": diffs,
                       "headline": headline(t), "figures": figures}, fh, indent=1)
        with open(os.path.join(HERE, "page_figures.csv"), "w", encoding="utf-8", newline="") as fh:
            fh.write(f"# ERW, the demand growth explorer: the page beside the replication (replication/demand_growth/replicate.py --write); {same} of {total} slots over every view; held here, the page as it opens and each view's three headline numbers\n")
            wr = csv.writer(fh, lineterminator="\n")
            wr.writerow(["view", "slot", "page", "replication", "inside"])
            for f in figures:
                wr.writerow([f["view"], f["slot"], f["page"], f["replication"], "yes" if f["inside"] else "no"])
    return 1 if (diffs or off) else 0


if __name__ == "__main__":
    sys.exit(main())

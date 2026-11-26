"""Session 10223 (states audit): an independent restatement of /states.

Written from docs/methods/states_page.md ("Arithmetic") and the contract (docs/state/page_files_states.md), not from
warehouse/derived/states_page.py or site/lib/states.ts. Standard library only (csv, json, decimal).

Part 1. From the main copy's source tables (read only, paths given), rebuild for every place the parts this machine
holds the tables of: generation (state_generation_mix_monthly), retail (eia_retail_sales_monthly and
eia_retail_electricity_prices) and, for the places named, plants (EIA-860M's three sheets); set them beside the page
files (site/data/states/<st>.json).
Part 2. From the page files and the Part 1 rows, the printed string of every figure the page marks in the views
drawn (draw_states.mjs: data-fig keys), and the comparison with the drawn figures.

    python restate.py <warehouse output dir> <site/data/states dir> <drawn prefix> <out json> view1 view2 ...
    view: "default" or "a_CA_b_WV" (the drawn file's name)
"""
import csv
import json
import os
import sys
from collections import defaultdict
from decimal import Decimal, ROUND_HALF_UP

OUT, SD, PREFIX, RESULT = sys.argv[1:5]
VIEWS = sys.argv[5:] or ["default"]
SRCS = ["coal", "natural_gas", "nuclear", "hydro", "wind", "solar", "other_renewables", "oil_and_other", "not_itemized"]
SECT = {"RES": "residential", "COM": "commercial", "IND": "industrial", "TRA": "transportation", "ALL": "all"}


def rows(name, need=None):
    """The table's rows as dicts, comment lines skipped; only rows where need(row) is true."""
    with open(os.path.join(OUT, name + ".csv"), encoding="utf-8", newline="") as fh:
        lines = (ln for ln in fh if not ln.startswith("#"))
        for r in csv.DictReader(lines):
            if need is None or need(r):
                yield r


def months_between(a, b):
    out, y, m = [], int(a[:4]), int(a[5:7])
    while f"{y:04d}-{m:02d}" <= b:
        out.append(f"{y:04d}-{m:02d}")
        y, m = (y + 1, 1) if m == 12 else (y, m + 1)
    return out


# ---------- Part 1: generation
gen = defaultdict(dict)   # st -> {(src, month): value}
for r in rows("state_generation_mix_monthly"):
    st = r["entity"].split(":")[1]
    src = r["variable"][len("net_generation_"):-len("_mwh")]
    if r["value"] == "":
        continue
    gen[st][(src, r["ts_utc"][:7])] = float(r["value"])


def restate_gen(st):
    d = gen.get(st)
    if not d:
        return None
    ms = sorted({m for _, m in d})
    months = months_between(ms[0], ms[-1])
    last = months[-12:]
    sums = {}
    for s in SRCS:
        vals = [d[(s, m)] for m in last if (s, m) in d]
        sums[s] = sum(vals) if vals else None
    tot = sum(v for v in sums.values() if v is not None)
    years = {}
    for y in sorted({m[:4] for m in months}):
        ym = [m for m in months if m[:4] == y]
        tot_y, per = 0.0, {}
        whole_total = len(ym) == 12 and all(any((s, m) in d for s in SRCS) for m in ym)
        for s in SRCS:
            have = [d[(s, m)] for m in ym if (s, m) in d]
            per[s] = sum(have) if len(ym) == 12 and len(have) == 12 else None
            tot_y += sum(have)
        years[y] = {"total": tot_y if whole_total else None, **per}
    return {"from": last[0], "to": last[-1], "total": tot, "sums": sums,
            "share": {s: (100 * v / tot if v is not None and tot else None) for s, v in sums.items()},
            "partial": {s: sum((s, m) not in d for m in last) for s in SRCS if sums[s] is not None and any((s, m) not in d for m in last)},
            "years": years}


# ---------- Part 1: retail
sales = defaultdict(dict)
cust = defaultdict(dict)
for r in rows("eia_retail_sales_monthly", lambda r: r["variable"] in ("retail_sales", "customers")):
    _, _, st, sec = r["entity"].split(":")
    if sec not in SECT or r["value"] == "":
        continue
    (sales if r["variable"] == "retail_sales" else cust)[st][(SECT[sec], r["ts_utc"][:7])] = float(r["value"])
price = defaultdict(dict)
for r in rows("eia_retail_electricity_prices"):
    _, _, st, sec = r["entity"].split(":")
    if sec not in SECT or r["value"] == "":
        continue
    price[st][(SECT[sec], r["ts_utc"][:7])] = float(r["value"])


def restate_retail(st):
    s, p = sales.get(st, {}), price.get(st, {})
    if not s:
        return None
    ms = sorted({m for _, m in s} | {m for _, m in p})
    months = months_between(ms[0], ms[-1])
    last = months[-12:]
    out = {"from": last[0], "to": last[-1], "by": {}}
    for sec in SECT.values():
        if all((sec, m) in s and (sec, m) in p for m in last):
            sv = sum(s[(sec, m)] for m in last)
            rv = sum(s[(sec, m)] * p[(sec, m)] for m in last)
            out["by"][sec] = {"sales": sv, "revenue": rv, "price": rv / sv if sv else None}
        else:
            out["by"][sec] = {"sales": None, "revenue": None, "price": None}
    c = cust.get(st, {})
    cm = max((m for _, m in c), default=None)
    out["cust_month"] = cm
    out["cust"] = {sec: c.get((sec, cm)) for sec in SECT.values()}
    return out


# ---------- Part 1: plants, for the places drawn
def restate_plants(st):
    def f(v):
        try:
            return float(v)
        except ValueError:
            return 0.0
    op = [r for r in rows("eia860m_operating_generators", lambda r: st == "US" or r["state"] == st)]
    by = defaultdict(lambda: [0.0, 0.0, 0, 0.0])
    plants = defaultdict(float)
    pinfo = {}
    going = defaultdict(float)
    for r in op:
        t = r["technology_group"]
        by[t][0] += f(r["nameplate_mw"]); by[t][1] += f(r["net_summer_mw"]); by[t][2] += 1; by[t][3] += f(r["energy_capacity_mwh"])
        plants[r["plant_id"]] += f(r["nameplate_mw"])
        pinfo.setdefault(r["plant_id"], r["name"])
        if len(r["planned_retirement_date"]) >= 4:
            going[(r["planned_retirement_date"][:4], t)] += f(r["nameplate_mw"])
    coming = defaultdict(float)
    uc = defaultdict(float)
    for r in rows("eia860m_planned_generators", lambda r: st == "US" or r["state"] == st):
        k = (r["planned_operation_date"][:4] or "no date", r["technology_group"])
        coming[k] += f(r["nameplate_mw"])
        if r["status"] == "under_construction":
            uc[k] += f(r["nameplate_mw"])
    gone = defaultdict(float)
    for r in rows("eia860m_retired_generators", lambda r: st == "US" or r["state"] == st):
        gone[(r["retirement_date"][:4], r["technology_group"])] += f(r["nameplate_mw"])
    largest = sorted(plants.items(), key=lambda kv: -kv[1])[:10]
    states_in = sorted({r["state"] for r in op})
    return {"by": {k: v for k, v in by.items()}, "total": sum(v[0] for v in by.values()), "plants": len(plants),
            "largest": [(pid, pinfo[pid], mw) for pid, mw in largest], "coming": dict(coming), "uc": dict(uc),
            "going": dict(going), "gone": dict(gone), "states": states_in}


# ---------- formats, as the page prints (half up on the exact decimal of the double)
def q(v, nd):
    return Decimal(v).quantize(Decimal(1).scaleb(-nd), rounding=ROUND_HALF_UP)


def comma(dv, nd):
    s = f"{dv:,.{nd}f}"
    return s


def twh(v): return comma(q(v / 1e6, 1), 1)
def gw(v): return comma(q(v / 1e3, 1), 1)
def mt(v): return comma(q(v / 1e6, 1), 1)
def bcf(v): return comma(q(v / 1e3, 1), 1)
def one1(v): return comma(q(v, 1), 1)
def whole(v): return comma(q(v, 0), 0)
def pct(v): return f"{q(v, 1)}%"
def cents(v): return f"{q(v / 10, 2)}"
def bn(v): return f"${comma(q(v / 1e9, 2), 2)} bn"


def load(st):
    with open(os.path.join(SD, f"{st.lower()}.json"), encoding="utf-8") as fh:
        return json.load(fh)


def expected(st, R, mine_gen, mine_ret, mine_pl):
    """{data-fig key: printed string} for one place, from the restated rows (generation, retail, plants) and, for the
    parts whose tables are not on this machine, from the file's own rows (CO2, gas, SEDS, disposition, serving)."""
    e = {}
    f = load(st)
    if mine_gen:
        for s in SRCS:
            if mine_gen["sums"][s] is not None:
                e[f"g12-{st}-{s}"] = twh(mine_gen["sums"][s]); e[f"g12s-{st}-{s}"] = pct(mine_gen["share"][s])
        e[f"g12t-{st}"] = twh(mine_gen["total"])
        ys = [y for y, v in mine_gen["years"].items() if v["total"] is not None]
        for y in ys:
            e[f"gyt-{st}-{y}"] = twh(mine_gen["years"][y]["total"])
            for s in SRCS:
                v = mine_gen["years"][y][s]
                if v is not None:
                    e[f"gy-{st}-{s}-{y}"] = pct(100 * v / mine_gen["years"][y]["total"])
    if mine_ret:
        for sec, b in mine_ret["by"].items():
            if b["sales"] is not None:
                e[f"r-{st}-{sec}-s"] = twh(b["sales"]); e[f"r-{st}-{sec}-r"] = bn(b["revenue"])
                if b["price"] is not None:
                    e[f"r-{st}-{sec}-p"] = cents(b["price"])
            if mine_ret["cust"].get(sec) is not None:
                e[f"r-{st}-{sec}-c"] = whole(mine_ret["cust"][sec])
    if mine_pl:
        for t, (n, s_, g, en) in mine_pl["by"].items():
            e[f"c-{st}-{t}"] = whole(n); e[f"cs-{st}-{t}"] = whole(s_)
        e[f"c-{st}-all"] = whole(mine_pl["total"])
        for i, (_, _, mw) in enumerate(mine_pl["largest"]):
            e[f"pl-{st}-{i}"] = whole(mw)
        for (y, g), mw in mine_pl["coming"].items():
            e[f"cm-{st}-{g}-{y}"] = whole(mw)
        for (y, g), mw in mine_pl["going"].items():
            e[f"go-{st}-{g}-{y}"] = whole(mw)
    # parts whose tables are not here: from the file's own rows, by the note's arithmetic
    c = f["co2"]
    if c.get("years"):
        pass
    s = f["serving"]
    if s.get("by_authority") and not s.get("shares_reason"):
        tot = sum(a["population"] for a in s["by_authority"])
        for a in s["by_authority"]:
            e[f"sv-{st}-{a['code'] or 'none'}"] = pct(100 * a["population"] / tot)
    d = f["disposition"]
    if d.get("years"):
        for k in ("total_net_generation", "full_service_providers", "energy_only_providers", "net_interstate_trade", "estimated_losses"):
            for y in d["years"][-3:]:
                v = (d["values"].get(k) or [None] * len(d["years"]))[d["years"].index(y)]
                if v is not None:
                    e[f"dp-{st}-{k}-{y}"] = whole(v)
    g = f["gas"]
    if g.get("months"):
        last = g["months"][-1]
        gy = last[:4] if last.endswith("-12") else str(int(last[:4]) - 1)
        idx = [i for i, m in enumerate(g["months"]) if m[:4] == gy]
        for k in ("residential", "commercial", "industrial", "electric_power"):
            a = g["consumption"].get(k)
            if a and len(idx) == 12 and all(a[i] is not None for i in idx):
                e[f"gas-{st}-{k}"] = bcf(sum(a[i] for i in idx))
        a = g.get("marketed_production")
        if a and all(a[i] is not None for i in idx):
            e[f"gas-{st}-prod"] = bcf(sum(a[i] for i in idx))
    en = f["energy"]
    if en.get("years"):
        y = en["years"][-1]
        i = en["years"].index(y)
        for k, a in en["by_source"].items():
            if a and a[i] is not None:
                e[f"seds-{st}-{k}"] = one1(a[i])
        for k, a in en["by_sector"].items():
            if a and a[i] is not None:
                e[f"seds-{st}-sec-{k}"] = one1(a[i])
    return e, f


def headline(st, f, mine_gen, mine_ret):
    e = {}
    if mine_gen:
        e["h-gen"] = twh(mine_gen["total"])
        top = max(SRCS, key=lambda s: mine_gen["share"][s] if mine_gen["share"][s] is not None else -1)
        e["h-top"] = pct(mine_gen["share"][top])
        e["_top"] = top
    if mine_ret and mine_ret["by"]["all"]["price"] is not None:
        e["h-price"] = cents(mine_ret["by"]["all"]["price"])
    c = f["co2"]
    if c.get("years"):
        for i in range(len(c["years"]) - 1, -1, -1):
            v = c["tons_by_fuel"]["all"][i]
            if v is not None:
                e["h-co2"] = mt(v); e["_co2year"] = c["years"][i]; e["_rate"] = c["rate_kg_per_mwh"][i]
                break
    return e


def side(a, b, ea, eb, ga, gb, ra, rb, fa, fb):
    e = {}
    for tag, gx, rx, fx, hx in (("a", ga, ra, fa, ea), ("b", gb, rb, fb, eb)):
        if gx:
            e[f"sd-{tag}-gen"] = twh(gx["total"])
            for s in SRCS[:6]:
                if gx["share"][s] is not None:
                    e[f"sd-{tag}-sh-{s}"] = pct(gx["share"][s])
        if rx:
            for sec in ("residential", "commercial", "industrial", "all"):
                if rx["by"][sec]["price"] is not None:
                    e[f"sd-{tag}-p-{sec}"] = cents(rx["by"][sec]["price"])
        if fx["plants"].get("capacity_total_mw") is not None:
            e[f"sd-{tag}-cap"] = gw(fx["plants"]["capacity_total_mw"])
        if "h-co2" in hx:
            e[f"sd-{tag}-co2"] = hx["h-co2"]
            if hx["_rate"] is not None:
                e[f"sd-{tag}-rate"] = one1(hx["_rate"])
    return e


# ---------- Part 1 comparisons over every place
idx = json.load(open(os.path.join(SD, "index.json"), encoding="utf-8"))
report = {"part1": {}, "views": {}}
gap_gen, gap_ret, part = [], [], []
cache = {}
for row in idx["states"]:
    st = row["state"]
    f = load(st)
    mg, mr = restate_gen(st), restate_retail(st)
    cache[st] = (mg, mr)
    fg, fr = f["generation"], f["retail"]
    if mg and fg.get("last12"):
        d = abs(mg["total"] - fg["last12"]["total_mwh"])
        win = (mg["from"], mg["to"]) == (fg["last12"]["from"], fg["last12"]["to"])
        gap_gen.append((st, round(d, 1), win))
        if mg["partial"]:
            part.append((st, mg["partial"], {s: round(mg["share"][s], 3) for s in mg["partial"]}))
    if mr and fr.get("last12"):
        a = mr["by"]["all"]; b = fr["last12"]["by_sector"]["all"]
        if a["price"] is not None and b["price_usd_per_mwh"] is not None:
            gap_ret.append((st, round(a["price"] - b["price_usd_per_mwh"], 4), (mr["from"], mr["to"]) == (fr["last12"]["from"], fr["last12"]["to"]),
                            (fg.get("last12") or {}).get("to") == fr["last12"]["to"]))
report["part1"]["generation_gap_mwh"] = gap_gen
report["part1"]["retail_all_price_gap"] = gap_ret
report["part1"]["partial_sources_last12"] = part
print("Part 1: generation, places", len(gap_gen), "largest twelve-month gap (MWh)", max(gap_gen, key=lambda x: x[1]), "windows equal", all(w for _, _, w in gap_gen))
print("Part 1: retail all-sector price, places", len(gap_ret), "largest gap (USD/MWh)", max(gap_ret, key=lambda x: abs(x[1])), "windows equal", all(w for _, _, w, _ in gap_ret), "retail window = generation window", all(x for *_, x in gap_ret))
print("Part 1: sources printed over the last twelve months with a month missing:", len(part))
for p in part:
    print("   ", p)

# ---------- Part 2: each view
for view in VIEWS:
    parts = view.split("_")
    qd = dict(zip(parts[0::2], parts[1::2])) if view != "default" else {}
    a = qd.get("a", "TX")
    b = qd.get("b")
    places = [a] + ([b] if b else [])
    exp = {}
    pl_cache = {}
    for st in places:
        mg, mr = cache[st]
        pl = restate_plants(st)
        pl_cache[st] = pl
        e, f = expected(st, None, mg, mr, pl)
        exp.update(e)
    fa = load(a)
    ha = headline(a, fa, *cache[a])
    exp.update({k: v for k, v in ha.items() if not k.startswith("_")})
    if b:
        fb = load(b)
        hb = headline(b, fb, *cache[b])
        exp.update(side(a, b, ha, hb, cache[a][0], cache[b][0], cache[a][1], cache[b][1], fa, fb))
    drawn = json.load(open(f"{PREFIX}_{view}_figures.json", encoding="utf-8"))
    figs = {k: v for k, v, _ in drawn["figs"]}
    equal = [k for k in figs if k in exp and exp[k] == figs[k]]
    differ = [(k, figs[k], exp[k]) for k in figs if k in exp and exp[k] != figs[k]]
    unrestated = [k for k in figs if k not in exp]
    only_mine = [k for k in exp if k not in figs]
    report["views"][view] = {"figures": len(figs), "equal": len(equal), "differ": differ, "not_restated": unrestated, "restated_not_drawn": only_mine,
                             "plants_states": {st: pl_cache[st]["states"][:60] for st in places}}
    print(f"\n/states view {view}: {len(figs)} marked figures; {len(equal)} equal to the restatement; {len(differ)} differ; {len(unrestated)} not restated; {len(only_mine)} restated but not drawn")
    for d_ in differ[:40]:
        print("   differs:", d_)
    if unrestated:
        print("   not restated:", unrestated[:40])
    if only_mine:
        print("   restated, not drawn:", only_mine[:40])
    if "_top" in ha:
        print(f"   headline: largest source {ha['_top']}; CO2 year {ha.get('_co2year')}, rate {ha.get('_rate')}")
json.dump(report, open(RESULT, "w", encoding="utf-8"), indent=1, default=str)

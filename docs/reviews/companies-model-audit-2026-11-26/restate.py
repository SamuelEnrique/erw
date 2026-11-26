"""An independent restatement of every figure the company database's default view (/companies) and three company pages
(/companies/eia-6452, eia-64846, eia-65506) print, from the page files' links alone (site/data/companies/c/*.json, each
company's public links), by the rules docs/methods/companies.md states, with the standard library only. It reads no
figure the builder computed (no "figures", "fuel", "years", "kind", "segment", "states" of a shard, no figure column of
the index): only the links, the index's lists of tables, rules and confidences, the held counts, and, for a company's
name, parent, EIA id and HQ state, the shard's own fields (they are not figures). Writes restate.json beside it.
Session 10228, the companies audit."""
import csv
import json
import math
import os
import re
from collections import Counter, defaultdict

WT = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
D = os.path.join(WT, "site", "data", "companies")
OUT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "restate.json")

ix = json.load(open(os.path.join(D, "index.json"), encoding="utf-8"))
TABLES, RULES, CONF = ix["tables"], ix["rules"], ix["confidence"]
comp = {}
for f in sorted(os.listdir(os.path.join(D, "c"))):
    comp.update(json.load(open(os.path.join(D, "c", f), encoding="utf-8")))


def jsround(v):
    """JavaScript's Math.round: half up."""
    return math.floor(v + 0.5)


def whole(v):
    return f"{jsround(v):,}"


def fnum(s):
    try:
        return float(s)
    except (TypeError, ValueError):
        return 0.0


def links(c):
    out = []
    for l in c["links"]:
        out.append(dict(link=l[0], table=TABLES[l[1]], row=l[2], role=l[3], name=l[4] or c["name"], rule=RULES[l[5]],
                        mw=l[6], usd=l[7], date=l[8], fuel=l[9], state=l[10], grid=l[11], detail=l[12]))
    return out


# the note's kinds, in its order ("The columns of company_directory", kind); "power marketer" since session 7001
ORDER = ["regulator", "lab or hyperscaler", "OEM", "utility", "IPP", "lender or investor", "developer", "operator",
         "power marketer", "other"]
OWNERSHIP_UTILITY = {"Investor Owned", "Cooperative", "Municipal", "Political Subdivision", "State", "Federal",
                     "Municipal Mktg Authority"}


def simple(s):
    return re.sub(r"[^a-z0-9]+", " ", s.lower()).strip()


reviewed_kind = {}
with open(os.path.join(WT, "warehouse", "companies", "reviewed_aliases.csv"), encoding="utf-8") as fh:
    for r in csv.DictReader(ln for ln in fh if not ln.startswith("#")):
        if (r.get("kind") or "").strip():
            reviewed_kind[simple(r.get("canonical") or r["alias"])] = r["kind"].strip()


def kind_of(c, ls):
    shows = set()
    names = {simple(c["name"])} | {simple(n[0]) for n in c["names"]}
    for n in names:
        if n in reviewed_kind:
            shows.add(reviewed_kind[n])
    for l in ls:
        t, role, det = l["table"], l["role"], l["detail"]
        if t == "eia861_utility_data" and det in OWNERSHIP_UTILITY:
            shows.add("utility")
        elif t == "eia861_utility_data" and det in ("Retail Power Marketer", "Wholesale Power Marketer"):
            shows.add("power marketer")
        elif t == "eia860_plants_annual" and det == "Electric Utility":
            shows.add("utility")
        elif t == "eia860_plants_annual" and det.startswith("IPP"):
            shows.add("IPP")
        elif t == "nrc_power_reactors" and role in ("licensee", "operator"):
            shows.add("operator")
        elif t in ("ercot_interconnection_queue", "eia860m_planned_generators"):
            shows.add("developer")
        elif t == "utility_service_territories":
            shows.add("utility")
    for k in ORDER:
        if k in shows:
            return k
    return "other"


def live_queue(l):
    return l["table"] == "ercot_interconnection_queue" and l["detail"] not in ("withdrawn", "Completed")


def figures(ls):
    f = defaultdict(float)
    plants, planned, owned, queue, reactors, policy = set(), set(), set(), set(), set(), set()
    fuel = defaultdict(float)
    years = defaultdict(lambda: [0.0, 0.0, 0.0])
    seg = defaultdict(float)
    for l in ls:
        t, mw, y = l["table"], fnum(l["mw"]), l["date"][:4]
        if t == "eia860m_operating_generators":
            plants.add(l["detail"]); f["n_generators"] += 1; f["plants_mw"] += mw
            fuel[l["fuel"] or "other"] += mw; seg[l["fuel"] or "other"] += mw
            if y:
                years[y][0] += mw
        elif t == "eia860m_planned_generators":
            planned.add(l["detail"]); f["planned_mw"] += mw; seg[l["fuel"] or "other"] += mw
            if y:
                years[y][1] += mw
        elif t == "eia860_generator_owners":
            owned.add(l["row"]); f["owned_mw"] += mw
        elif live_queue(l):
            queue.add(l["row"]); f["queue_mw"] += mw; seg[l["fuel"] or "other"] += mw
            if y:
                years[y][2] += mw
        elif t == "nrc_power_reactors" and l["role"] in ("licensee", "operator") and l["row"] not in reactors:
            reactors.add(l["row"]); f["reactors_mw"] += mw
        elif t == "policy_actions":
            policy.add(l["row"])
    out = dict(n_plants=len(plants), n_generators=int(f["n_generators"]), plants_mw=f["plants_mw"],
               n_owned_generators=len(owned), owned_mw=f["owned_mw"], n_planned_plants=len(planned),
               planned_mw=f["planned_mw"], n_queue=len(queue), queue_mw=f["queue_mw"], n_reactors=len(reactors),
               reactors_mw=f["reactors_mw"], n_policy_actions=len(policy))
    out["footprint_mw"] = out["plants_mw"] + out["owned_mw"] + out["planned_mw"] + out["queue_mw"]
    return out, dict(fuel), dict(years), dict(seg)


def segment(seg, kind):
    s = {k: v for k, v in seg.items() if k not in ("other", "")}
    if kind != "regulator" and s:
        k, v = max(s.items(), key=lambda kv: (kv[1], kv[0]))
        if v > 0:
            return k
    return {"utility": "utility", "regulator": "government"}.get(kind, "")


def states_of(ls):
    st = Counter(l["state"] for l in ls if len(l["state"]) == 2 and l["table"] != "policy_actions")
    return st


rows = []
for cid, c in comp.items():
    ls = links(c)
    fig, fuel, years, seg = figures(ls)
    k = kind_of(c, ls)
    st = states_of(ls)
    dates = sorted(l["date"] for l in ls if l["date"])
    rows.append(dict(id=cid, name=c["name"], kind=k, segment=segment(seg, k), states=st,
                     grids=sorted({g for l in ls for g in l["grid"].split(";") if g}), n_links=len(ls),
                     first=dates[0] if dates else "", last=dates[-1] if dates else "",
                     minconf=min(CONF[l["rule"]] for l in ls), fig=fig, fuel=fuel, years=years, held=c["held"]))
# the default order: the footprint, largest first (the builder rounds each figure to 0.1 MW before the sum; a sort on
# the unrounded sum is tried in measures.py)
r1 = lambda x: round(x + 0.0, 1)
for r in rows:
    f = r["fig"]
    r["fp_sorted"] = r1(r1(f["plants_mw"]) + r1(f["owned_mw"]) + r1(f["planned_mw"]) + r1(f["queue_mw"]))
rows.sort(key=lambda r: (-r["fp_sorted"], -r["n_links"], r["id"]))


def states_text(st, most=3):
    ordered = [s for s, _ in st.most_common()]
    return ", ".join(ordered[:most]) + (" ..." if len(ordered) > most else "")


page1 = []
for r in rows[:50]:
    f = r["fig"]
    page1.append(dict(id=r["id"], name=r["name"], kind=r["kind"], segment=r["segment"],
                      states_counts=dict(r["states"]), states_text=states_text(r["states"]),
                      op=whole(f["plants_mw"]) if f["plants_mw"] else "0", planned=whole(f["planned_mw"]) if f["planned_mw"] else "0",
                      queue=whole(f["queue_mw"]) if f["queue_mw"] else "0", policy=str(f["n_policy_actions"]),
                      footprint=whole(f["footprint_mw"]) if f["footprint_mw"] else "0"))
kinds = Counter(r["kind"] for r in rows)
segs = Counter(r["segment"] for r in rows if r["segment"])
states = Counter(s for r in rows for s in r["states"])
grids = Counter(g for r in rows for g in r["grids"])
held_listed = Counter()
for r in rows:
    held_listed.update(r["held"])

FUELS = ["solar", "wind", "gas", "coal", "nuclear", "hydro", "storage", "oil", "geothermal", "other"]


def plural(n, one, many):
    return f"{whole(n)} {one if jsround(n) == 1 else many}"


def page(cid):
    c = comp[cid]
    r = next(x for x in rows if x["id"] == cid)
    ls = links(c)
    f = r["fig"]
    by_table = Counter(l["table"] for l in ls)
    held_n = sum(c["held"].values())
    st = [s for s, _ in r["states"].most_common()]
    lead = f"{r['kind']}{', ' + r['segment'] if r['segment'] else ''}"
    lead_states = f", in {', '.join(st[:6])}" + (f" and {plural(len(st) - 6, 'more state', 'more states')}" if len(st) > 6 else "") if st else ""
    lead_rows = (f"{plural(len(ls), 'public row', 'public rows')} of {plural(len(by_table), 'table', 'tables')} "
                 f"name{'s' if len(ls) == 1 else ''} it" + (f"; {plural(held_n, 'held row does', 'held rows do')} too" if held_n else "") + ".")
    heads = {}
    for col, v in (("plants_mw", f["plants_mw"]), ("planned_mw", f["planned_mw"]), ("owned_mw", f["owned_mw"]),
                   ("queue_mw", f["queue_mw"]), ("n_reactors", f["n_reactors"]), ("n_policy_actions", f["n_policy_actions"])):
        if v > 0:
            heads[col] = whole(v)
    tips = {
        "plants_mw": f"Nameplate MW of the {plural(f['n_generators'], 'operating generator', 'operating generators')} at {plural(f['n_plants'], 'plant', 'plants')} it operates (EIA-860M).",
        "planned_mw": f"Nameplate MW of planned generators at {plural(f['n_planned_plants'], 'plant', 'plants')} it would operate (EIA-860M).",
        "owned_mw": f"Nameplate MW times the percent owned, of {plural(f['n_owned_generators'], 'jointly owned generator', 'jointly owned generators')} (EIA-860 schedule 4 lists only those).",
        "n_reactors": f"NRC power reactors it is the licensee or operator of: {whole(f['reactors_mw'])} MW as the NRC states them.",
    }
    fuel_rows = {}
    for k in FUELS:
        v = r["fuel"].get(k, 0.0)
        if round(v, 1) > 0:
            fuel_rows[k] = [whole(v), f"{v / f['plants_mw'] * 100:.1f}%" if f["plants_mw"] else ""]
    # MW by year: one group a year, or five-year spans past 15 years
    ys = sorted(r["years"])
    groups = []
    if ys:
        first, last = int(ys[0]), int(ys[-1])
        width = 5 if last - first + 1 > 15 else 1
        start = (first // width) * width if width > 1 else first
        a = start
        while a <= last:
            o = p = q = 0.0
            for y in range(a, min(a + width, last + 1)):
                v = r["years"].get(str(y))
                if v:
                    o += v[0]; p += v[1]; q += v[2]
            b = min(a + width - 1, last)
            groups.append([str(a), f"to {str(b)[2:]}" if width > 1 else "", o, p, q])
            a += width
    live = [i for i, k in enumerate(("operating", "planned", "queue")) if any(g[2 + i] > 0 for g in groups)]
    words = ("operating", "planned", "in the ERCOT queue")
    titles = [f"{g[0]}{' ' + g[1] if g[1] else ''}: " + ", ".join(f"{whole(g[2 + i])} MW {words[i]}" for i in live) for g in groups]
    names = Counter((l["name"], l["table"], l["role"]) for l in ls)
    return dict(name=c["name"], lead=f"{lead}{lead_states}. {lead_rows}", heads=heads, tips=tips, fuel=fuel_rows,
                year_titles=titles, rows_by_table=dict(by_table), held=c["held"], kind=r["kind"], segment=r["segment"],
                grids=", ".join(r["grids"]), seen=f"{r['first']} to {r['last']}" + (" (planned)" if r["last"][:10] > ix["built"][:10] else ""),
                match=f"{r['minconf']:.2f}", names_counts={f"{n}|{t}|{ro}": k for (n, t, ro), k in names.items()},
                deals_held=(f"{plural(c['held'].get('energy_deals', 0), 'row', 'rows')} of energy_deals name"
                            f"{'s' if c['held'].get('energy_deals') == 1 else ''} this company" if c["held"].get("energy_deals") else ""))


out = dict(n_listed=len(rows), pages=max(1, math.ceil(len(rows) / 50)), kinds=dict(kinds), segments=dict(segs),
           states=dict(states), grids=dict(grids), held_listed=dict(held_listed), page1=page1,
           company={cid: page(cid) for cid in ("eia-6452", "eia-64846", "eia-65506")},
           all_rows={r["id"]: dict(kind=r["kind"], segment=r["segment"], fig={k: round(v, 1) for k, v in r["fig"].items()},
                                   states=";".join(s for s, _ in r["states"].most_common()), grids=";".join(r["grids"]),
                                   n_links=r["n_links"], first=r["first"], last=r["last"]) for r in rows},
           order=[r["id"] for r in rows])
json.dump(out, open(OUT, "w", encoding="utf-8"), indent=0)
print("restated", len(rows), "companies; page 1 of", out["pages"], "pages")

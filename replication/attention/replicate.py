#!/usr/bin/env python3
"""ERW, the Attention and Friction indices (/attention): an independent replication of every figure of the page's file
(session 7007, chain 301, goal 4).

Written from docs/methods/attention.md and the tables alone, not from warehouse/derived/attention_index.py. It reads the
public tables attention_story_links (one row a classified story: its week, sector, place, opposition, kind and tone)
and attention_index_weekly's corpus rows (each week's judged stories: the denominators), and the internal news_stories
for one column only, the scorer's cluster id, which the page shows as a count of events. By the method's words:

  a cell is a sector (one of seven, or "energy": any energy sector, other_energy included) and a place ("all", "US":
  the stories about the United States, or a state) in a week;
  attention index = the cell's stories as a percent of the week's judged stories;
  friction index = the cell's opposition stories as a percent of its stories; tone = the mean of its stories' tones;
  opposition events = the distinct news clusters among its opposition stories (a story clustered with none its own);
  each kind of opposition's count;
  what rose = a week's index (sector, all places; and each state, energy) beside the mean of the classified weeks
  among the four before (a classified week with no story in the cell counts as zero), with their count; no row where
  none is classified;
  together = each sector's figures over the classified weeks;
  the places = the stories naming a county, city or metro in the United States, by sector, place, state and week;
  a story whose week is not a week of the corpus (a listing dated after it was read) is in no week.

It compares each with site/data/attention.json and prints N of N.

    python replication/attention/replicate.py [--tables DIR] [--site DIR]

Exit 0 when every figure is equal (to 0.0001), 1 when one is not, 2 when the inputs cannot be read. Standard library only.
"""
import argparse
import csv
import json
import os
import sys
from collections import Counter, defaultdict

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(os.path.dirname(HERE))
csv.field_size_limit(10 ** 9)
SECTORS7 = ["datacenters", "transmission", "gas", "nuclear", "solar_wind", "storage", "oil_lng"]
SECTORS = SECTORS7 + ["energy"]
ENERGY = set(SECTORS7) | {"other_energy"}


def rows(path):
    with open(path, encoding="utf-8", newline="") as f:
        yield from csv.DictReader(ln for ln in f if not ln.startswith("#"))


def r4(x):
    return round(x, 4)


def main(argv=None):
    ap = argparse.ArgumentParser(description="The attention indices' replication")
    ap.add_argument("--tables", default=os.path.join(ROOT, "warehouse", "output"))
    ap.add_argument("--site", default=os.path.join(ROOT, "site"))
    a = ap.parse_args(argv)
    try:
        with open(os.path.join(a.site, "data", "attention.json"), encoding="utf-8") as f:
            page = json.load(f)
        den = defaultdict(dict)
        for r in rows(os.path.join(a.tables, "attention_index_weekly.csv")):
            if r["entity"] == "attention:corpus:all":
                den[r["ts_utc"]][r["variable"]] = int(float(r["value"]))
        cluster = {r["event_id"]: r["cluster_id"] for r in rows(os.path.join(a.tables, "news_stories.csv"))}
        links = [r for r in rows(os.path.join(a.tables, "attention_story_links.csv")) if r["week"] in den]
    except (OSError, ValueError, KeyError) as exc:
        print(f"the inputs could not be read: {exc}")
        return 2
    weeks = sorted(den)
    classified = {w for w in weeks if den[w].get("stories_classified", 0) > 0}
    for l in links:
        l["opp"] = l["opposition"] == "true"
        l["us_"] = l["us"] == "true"
        l["ev"] = cluster.get(l["story_event_id"]) or l["story_event_id"]
    states = sorted({l["state"] for l in links if l["state"]})
    geos = ["all", "US"] + ["US-" + s for s in states]
    n, misses = 0, []

    def check(what, mine, theirs, tol=0.0):
        nonlocal n
        n += 1
        ok = (abs(float(mine) - float(theirs)) <= tol + 1e-9) if isinstance(mine, (int, float)) and isinstance(theirs, (int, float)) else mine == theirs
        if not ok:
            misses.append(f"{what}: replication {mine!r}, file {theirs!r}")

    check("weeks", weeks, page["weeks"])
    check("sectors", SECTORS, page["sectors"])
    check("geos", geos, page["geos"])
    wi, gi, si = {w: i for i, w in enumerate(weeks)}, {g: i for i, g in enumerate(geos)}, {s: i for i, s in enumerate(SECTORS)}
    # denominators
    mine_den = sorted([wi[w], d.get("stories_week", 0), d.get("stories_judged", 0), d.get("stories_classified", 0),
                       d.get("stories_unsent_zero", 0)] for w, d in den.items())
    check("denominators", mine_den, sorted(page["denominators"]))

    def members(sector, geo):
        s = [l for l in links if (l["sector"] in ENERGY if sector == "energy" else l["sector"] == sector)]
        if geo == "all":
            return s
        if geo == "US":
            return [l for l in s if l["us_"]]
        return [l for l in s if l["state"] == geo[3:]]

    cells, kinds, ai = {}, {}, {}
    for sector in SECTORS:
        for geo in geos:
            by = defaultdict(list)
            for l in members(sector, geo):
                by[l["week"]].append(l)
            for w, g in by.items():
                nn, opp = len(g), [x for x in g if x["opp"]]
                judged = den[w].get("stories_judged", 0)
                idx = r4(100.0 * nn / judged) if judged else 0.0
                ai[(sector, geo, w)] = idx
                cells[(si[sector], gi[geo], wi[w])] = [si[sector], gi[geo], wi[w], nn, idx, len(opp), r4(100.0 * len(opp) / nn),
                                                       r4(sum(int(x["tone"]) for x in g) / nn), len({x["ev"] for x in opp})]
                k = Counter(x["kind"] for x in opp)
                if k:
                    kinds[f"{si[sector]}|{gi[geo]}|{wi[w]}"] = dict(k)
    theirs = {tuple(c[:3]): c for c in page["cells"]}
    check("cells listed", sorted(cells), sorted(theirs))
    for key, c in cells.items():
        t = theirs.get(key)
        if t:
            for j, name in enumerate(["sector", "geo", "week", "stories", "attention_index", "opposition_stories",
                                      "friction_index", "tone_mean", "opposition_events"]):
                if j >= 3:
                    check(f"cell {key} {name}", c[j], t[j] if j < len(t) else None, 0.0001)
    check("kinds", kinds, page["kinds"])
    # what rose
    rising = []
    for i, w in enumerate(weeks):
        before = [b for b in weeks[max(0, i - 4):i] if b in classified]
        if not before:
            continue
        for sector in SECTORS:
            this = ai.get((sector, "all", w))
            if this is not None:
                m = r4(sum(ai.get((sector, "all", b), 0.0) for b in before) / len(before))
                rising.append([i, "sector", si[sector], this, m, r4(this - m), len(before)])
        for st in states:
            this = ai.get(("energy", "US-" + st, w))
            if this is not None:
                m = r4(sum(ai.get(("energy", "US-" + st, b), 0.0) for b in before) / len(before))
                rising.append([i, "state", st, this, m, r4(this - m), len(before)])
    key = lambda r: (r[0], r[1], str(r[2]))
    th = {key(r): r for r in page["rising"]}
    check("rising rows", sorted(key(r) for r in rising), sorted(th))
    for r in rising:
        t = th.get(key(r))
        if t:
            for j in (3, 4, 5, 6):
                check(f"rising {key(r)} [{j}]", r[j], t[j], 0.0001)
    # together
    cw = [l for l in links if l["week"] in classified]
    th = {(t[0], t[1]): t for t in page.get("together", [])}
    for sector in SECTORS:
        s_ = [l for l in cw if (l["sector"] in ENERGY if sector == "energy" else l["sector"] == sector)]
        for geo, g in (("all", s_), ("US", [l for l in s_ if l["us_"]])):
            if not g:
                continue
            o, rest = [x for x in g if x["opp"]], [x for x in g if not x["opp"]]
            mine = [si[sector], gi[geo], len({x["week"] for x in g}), len(g), len(o), len({x["ev"] for x in o}),
                    r4(100.0 * len(o) / len(g)), r4(sum(int(x["tone"]) for x in g) / len(g)),
                    r4(sum(int(x["tone"]) for x in o) / len(o)) if o else None,
                    r4(sum(int(x["tone"]) for x in rest) / len(rest)) if rest else None]
            t = th.get((si[sector], gi[geo]))
            check(f"together {sector} {geo}", mine, t)
    # the places
    pl = Counter()
    po = Counter()
    for l in links:
        if l["place"] and l["us_"] and l["sector"] in ENERGY:
            k = (si.get(l["sector"], si["energy"]), l["place"], l["state"], wi[l["week"]])
            pl[k] += 1
            po[k] += l["opp"]
    mine_pl = sorted([k[0], k[1], k[2], k[3], v, po[k]] for k, v in pl.items())
    check("places", mine_pl, sorted(page["places"]))
    check("counts", {"stories": len(links), "opposition": sum(l["opp"] for l in links),
                     "weeks_with_stories": len({l["week"] for l in links})}, page["counts"])
    print(f"The attention indices, from {a.tables} and attention.json (built {page['built']}): {len(links):,} classified "
          f"stories in {len(classified)} classified weeks, {len(cells):,} cells")
    for m in misses[:40]:
        print("  " + m[:300])
    print(f"{n - len(misses):,} of {n:,} figures equal")
    return 0 if not misses else 1


if __name__ == "__main__":
    sys.exit(main())

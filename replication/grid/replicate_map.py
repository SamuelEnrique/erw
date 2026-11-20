#!/usr/bin/env python3
"""ERW, the Grid tool's map (the Map shape of /grid?view=network): the replication a reader can run (session 8606, chain 504).

The map draws the network's snapshot on the balancing authorities' published boundaries. This script reads the
snapshot the page drew (map_snapshot.json, kept by map_figures.mjs), the boundary file
(site/data/regions/ba_boundaries.json), this folder's assumptions.json, and map_page_figures.json (what the map
draws, read from the page), computes every such figure again without the page's code, and compares:

- the hour the week opens on: the newest hour every reporting pair holds (a pair reports when it held a flow in the
  last 48 hours), the count of reporting pairs, and how many the newest hour holds;
- the regions drawn: the balancing authorities of the snapshot that have a boundary in the file; the authorities
  listed under the map: those that have none;
- every tie of the hour: a pair whose flow is held and is not zero, drawn from the exporter to the importer with
  its megawatts; the ties drawn on the map are those whose two ends both have a boundary;
- each region's hover: its net exchange (the sum of its ties' flows, signed from its side, zero flows counted as
  ties) and its count of ties; its carbon intensity as the snapshot holds it;
- the width key: the largest flow of the week on any tie, and its quarter and sixteenth.

Not compared here: a region's demand in the hover, which the page reads from the live set (the seven grids only) and
not from the snapshot; "State under the pointer" and "Also covers this point", which are geometry at the pointer.
A region whose reachable point lies under a tie's line gave the tie's card to the harvest; it is counted and named.

    python replication/grid/replicate_map.py [--snapshot JSON] [--boundaries JSON] [--page JSON] [--csv OUT]

Exit 0 when every figure is met, 1 when one is not, 2 when an input cannot be read. Standard library only.
"""
import argparse
import csv
import json
import math
import os
import re
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(os.path.dirname(HERE))


def load(path):
    with open(path, encoding="utf-8") as f:
        return json.load(f)


def half_up(x):
    """JavaScript's Math.round."""
    return math.floor(x + 0.5)


def complete_hour(hours, links, quiet):
    """The index of the newest hour every reporting pair holds, the pairs, and the reporting pairs."""
    n = len(hours)
    reporting = [l for l in links if max((h for h in range(n) if l["mw"][h] is not None), default=-1) >= n - quiet]
    for h in range(n - 1, -1, -1):
        if reporting and all(l["mw"][h] is not None for l in reporting):
            return h, len(links), len(reporting)
    return None, len(links), len(reporting)


def flows_at(links, h):
    """The hour's ties as the map draws them: exporter, importer, megawatts; a zero flow is not a tie drawn."""
    out = {}
    for l in links:
        v = l["mw"][h]
        if v is None or v == 0:
            continue
        out[f"{l['a']}>{l['b']}" if v > 0 else f"{l['b']}>{l['a']}"] = abs(float(v))
    return out


def net_of(links, ba, h):
    """A region's net imports over its ties in the hour (positive: it imports) and its count of ties; None with no tie."""
    net, ties = 0.0, 0
    for l in links:
        if ba not in (l["a"], l["b"]):
            continue
        v = l["mw"][h]
        if v is None:
            continue
        net += -v if l["a"] == ba else v
        ties += 1
    return (net if ties else None), ties


class Tally:
    def __init__(self):
        self.rows = []

    def same(self, name, page, computed):
        met = page == computed
        self.rows.append({"figure": name, "page": str(page), "computed": str(computed), "met": "yes" if met else "no"})
        return met

    def near(self, name, page, computed, tol):
        met = (page is None and computed is None) or (page is not None and computed is not None and abs(page - computed) <= tol + 1e-9)
        self.rows.append({"figure": name, "page": "not held" if page is None else repr(page), "computed": "not held" if computed is None else repr(round(computed, 4)), "met": "yes" if met else "no"})
        return met


def number(text):
    return float(text.replace(",", ""))


def main(argv):
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    ap.add_argument("--snapshot", default=os.path.join(HERE, "map_snapshot.json"))
    ap.add_argument("--boundaries", default=os.path.join(ROOT, "site", "data", "regions", "ba_boundaries.json"))
    ap.add_argument("--page", default=os.path.join(HERE, "map_page_figures.json"))
    ap.add_argument("--csv", default="")
    a = ap.parse_args(argv)
    try:
        snap, bounds, got, assume = load(a.snapshot), load(a.boundaries), load(a.page), load(os.path.join(HERE, "assumptions.json"))
    except (OSError, ValueError) as e:
        print("cannot read an input:", e)
        return 2
    if got.get("snapshot_built") != snap.get("built"):
        print(f"the page's figures are of the snapshot built {got.get('snapshot_built')}; the snapshot here was built {snap.get('built')}. Read the page again (map_figures.mjs).")
        return 2
    page, hovers, t = got["page"], got["hovers"], Tally()
    links, hours = snap["links"], snap["hours"]
    name = {n["id"]: n["name"] for n in snap["nodes"]}

    # the hour the week opens on
    h, pairs, reporting = complete_hour(hours, links, int(assume["network_quiet_hours"]["value"]))
    t.same("the hour the week opens on", page["complete_hour"], None if h is None else hours[h])
    m = re.search(r"every one of the (\d+) reporting pairs holds\. Later hours, to (\d{4}-\d{2}-\d{2} \d{2}:\d{2}) UTC, are on the slider; the newest holds (\d+) of the (\d+)", page.get("opens_line") or "")
    newest_holds = sum(1 for l in links if max((x for x in range(len(hours)) if l["mw"][x] is not None), default=-1) >= len(hours) - int(assume["network_quiet_hours"]["value"]) and l["mw"][-1] is not None)
    t.same("the line under the controls: reporting pairs, the newest hour, how many it holds", None if not m else [int(m.group(1)), m.group(2), int(m.group(3)), int(m.group(4))],
           [reporting, hours[-1][:16].replace("T", " "), newest_holds, reporting])
    if h is None:
        print("the snapshot holds no hour every reporting pair holds")
        return 1

    # the regions drawn and the authorities listed
    with_shape = {f["properties"]["code"] for f in bounds["features"]}
    drawn = [n["id"] for n in snap["nodes"] if n["id"] in with_shape]
    t.same("regions on the map", page["regions"], len(drawn))
    t.same("the regions drawn, by code", sorted(page["region_codes"]), sorted(drawn))
    t.same("boundaries in the file", page["matched"], len(bounds["features"]))
    listed = sorted((n["id"] for n in snap["nodes"] if n["id"] not in with_shape), key=lambda c: name[c])
    t.same("authorities listed under the map: no boundary in the file", sorted(page["listed"]), sorted(listed))
    t.same("their count", page["listed_count"], len(listed))

    # the hour's ties
    flows = flows_at(links, h)
    on_map = {k: v for k, v in flows.items() if all(end in with_shape for end in k.split(">"))}
    t.same("ties of the hour", page["flows_all"], len(flows))
    t.same("ties drawn on the map (both ends have a boundary)", page["flows"], len(on_map))
    seen = {x["flow"]: x["mw"] for x in page["ties"]}
    t.same("the ties drawn, each from its exporter to its importer", sorted(seen), sorted(on_map))
    for k in sorted(on_map):
        if k in seen:
            t.near(f"tie {k}, MW", float(seen[k]), on_map[k], 0.5)

    # each region's hover
    under_a_tie = []
    for ba in sorted(drawn):
        card = hovers.get(ba)
        if not card:
            t.same(f"{ba}: a hover was read", False, True)
            continue
        if card[0] != name[ba]:
            under_a_tie.append(ba)
            continue
        text = " | ".join(card)
        net, ties = net_of(links, ba, h)
        mm = re.search(r"Net (imports|exports): ([\d,]+) MW over (\d+) ties?", text)
        if net is None:
            t.same(f"{ba}: no tie reported this hour", "No tie reported this hour" in text, True)
        else:
            t.same(f"{ba}: a net exchange is drawn", bool(mm), True)
            if mm:
                t.same(f"{ba}: net importer or exporter", mm.group(1), "imports" if net >= 0 else "exports")
                t.near(f"{ba}: net exchange, MW", number(mm.group(2)), abs(net), 0.5)
                t.same(f"{ba}: ties", int(mm.group(3)), ties)
        node = next(n for n in snap["nodes"] if n["id"] == ba)
        ci = re.search(r"Carbon intensity of generation: (not held|[\d,.]+ kg CO2/MWh)", text)
        shown = None if not ci or ci.group(1) == "not held" else number(ci.group(1).split(" ")[0])
        t.near(f"{ba}: carbon intensity of generation, kg CO2 per MWh", shown, node.get("intensity"), 0.005 if shown is not None and "." in ci.group(1) else 0.5)

    # the width key
    largest = max(abs(v) for l in links for v in l["mw"] if v is not None)
    t.near("the width key: the largest flow of the week, MW", float(page["width_key"]), largest, 0.5)
    steps = [number(x) for x in re.findall(r"(?<![\d,])(\d[\d,]*)(?![\d,])", (page.get("width_key_text") or "").split("megawatts:")[-1].split("The dash")[0])]
    t.same("the width key's three steps: the largest, its quarter, its sixteenth", steps, [float(half_up(largest)), float(half_up(largest / 4)), float(half_up(largest / 16))])

    met = sum(1 for r in t.rows if r["met"] == "yes")
    for r in t.rows:
        if r["met"] == "no":
            print(f"  NOT MET {r['figure']} | page {r['page'][:160]} | computed {r['computed'][:160]}")
    print(f"the week opens on {hours[h]}: {len(drawn)} regions, {len(on_map)} of {len(flows)} ties on the map, {len(listed)} authorities listed, the largest flow of the week {largest:,.0f} MW")
    if under_a_tie:
        print(f"not compared, the pointer read a tie's card over the region: {', '.join(under_a_tie)}")
    print(f"{met} of {len(t.rows)} figures met (the page read {got.get('taken')}, the snapshot built {snap.get('built')})")
    if a.csv:
        with open(a.csv, "w", encoding="utf-8", newline="") as f:
            f.write("# ERW, the Grid tool's map: every figure the map draws computed again from the snapshot and the boundary file (replication/grid/replicate_map.py)\n")
            f.write("# Source: the network's snapshot (Form EIA-930 interchange, public domain; replication/grid/map_snapshot.json, built " + str(snap.get("built")) + ") and site/data/regions/ba_boundaries.json (" + str(bounds.get("source")) + ")\n")
            f.write("# Source URL: https://www.eia.gov/electricity/gridmonitor/ ; the boundaries: " + str(bounds.get("source_url")) + "\n")
            f.write("# Retrieved: the page read " + str(got.get("taken")) + "; the boundaries " + str(bounds.get("retrieved_at")) + "\n")
            w = csv.DictWriter(f, fieldnames=["figure", "page", "computed", "met"])
            w.writeheader()
            w.writerows(t.rows)
    return 0 if met == len(t.rows) else 1


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))

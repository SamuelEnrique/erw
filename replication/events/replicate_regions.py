"""Energy Research Warehouse (ERW), session 8440 (chain 503, part E): the replication of "The whole country" on the
nine event pages and of the line of regions on /events.

Written from the method note (docs/methods/events.md, the section "The whole country") and the contract of the files
(docs/state/page_files_regions.md, section 6) alone, not from the pages' code. Standard library only.

For each event whose file is on the site (site/data/regions/events/<event>.json, written by the data machine from
EIA's Form EIA-930), every figure the section prints is recomputed here from the file and set beside the figure the
site's own code draws (a figures file written by site/scripts/events-regions-figures.mjs):

- a region's demand over the window in GWh, its percent on the baseline, its highest hour, the baseline at that hour,
  the mean of its net imports and of the baseline's, and the hours held;
- each source's generation less the baseline's, and net generation's, in GWh;
- each pair's mean flow and energy in the direction of the window's sum, and the baseline's mean;
- how many regions the event reached (demand over the window 5 percent or more from the baseline, either way), of how
  many with a baseline.

A sum or a mean is taken over the hours the event and the baseline both hold (a pair's own figure: over the hours it
holds). A figure passes when ours is within half the last digit the page shows. Exit 0 when every figure of every
event with a file passes (also when no file is on the site yet: nothing to compare, said so), 1 when one does not,
2 on bad input.

    python replication/events/replicate_regions.py --figures <figures.json> [--files <dir of the event files>]

No row of a warehouse table is read and nothing is written. The files are public (EIA's Form EIA-930, public domain);
a file whose license line is not "public" is not recomputed, as the page draws no figure from it.
"""
from __future__ import annotations

import argparse
import json
import os
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
REGIONS = ["CAL", "CAR", "CENT", "FLA", "MIDA", "MIDW", "NE", "NW", "NY", "SE", "SW", "TEN", "TEX"]
SOURCES = ["natural_gas", "coal", "nuclear", "wind", "solar", "hydro", "storage", "other"]


def num(v):
    return isinstance(v, (int, float)) and not isinstance(v, bool) and v == v and abs(v) != float("inf")


def both(event, base):
    """The hours both hold: (count, sum of the event, sum of the baseline), or None."""
    if not event or not base:
        return None
    n = a = b = 0
    for x, y in zip(event, base):
        if num(x) and num(y):
            n += 1
            a += x
            b += y
    return (n, a, b) if n else None


def parse(shown):
    """A figure as the page shows it ("+1,234.5", "-10.0", "14,400") as a number and the size of its last digit."""
    s = shown.replace(",", "").replace("+", "").strip()
    value = float(s)
    step = 10 ** -len(s.split(".")[1]) if "." in s else 1.0
    return value, step


def expected(file):
    """Our own figures of one event's file, keyed as the page keys them, each a float."""
    step = file["hours"].get("step_hours") or 1
    out = {}
    with_base = 0
    hit = 0
    for code in REGIONS:
        r = (file.get("regions") or {}).get(code)
        if not r:
            out[f"wc|{code}|hours"] = 0.0
            continue
        base = r.get("baseline") or {}
        demand = r.get("demand_mw") or []
        out[f"wc|{code}|hours"] = float(sum(1 for v in demand if num(v)))
        d = both(demand, base.get("demand_mw"))
        if d:
            n, a, b = d
            out[f"wc|{code}|demand_gwh"] = a * step / 1000
            if b != 0:
                pct = (a - b) / abs(b) * 100
                out[f"wc|{code}|demand_pct"] = pct
                with_base += 1
                if abs(pct) >= 5:
                    hit += 1
        held = [(v, i) for i, v in enumerate(demand) if num(v)]
        if held:
            top = max(v for v, _ in held)
            at = next(i for v, i in held if v == top)  # the first hour at the highest value
            out[f"wc|{code}|peak_mw"] = top
            bd = base.get("demand_mw") or []
            if at < len(bd) and num(bd[at]):
                out[f"wc|{code}|peak_base_mw"] = bd[at]
        im = both(r.get("net_imports_mw"), base.get("net_imports_mw"))
        if im:
            n, a, b = im
            out[f"wc|{code}|imports_mw"] = a / n
            out[f"wc|{code}|imports_base_mw"] = b / n
        for s in SOURCES:
            g = both((r.get("gen") or {}).get(s), (base.get("gen") or {}).get(s))
            if g:
                out[f"wc|{code}|gen|{s}"] = (g[1] - g[2]) * step / 1000
        g = both(r.get("net_generation_mw"), base.get("net_generation_mw"))
        if g:
            out[f"wc|{code}|gen|net"] = (g[1] - g[2]) * step / 1000
    for key, p in (file.get("pairs") or {}).items():
        flow = [v for v in (p.get("flow_mw") or []) if num(v)]
        if not flow:
            continue
        out[f"wc|pair|{key}|mean_mw"] = abs(sum(flow) / len(flow))
        out[f"wc|pair|{key}|gwh"] = abs(sum(flow) * step / 1000)
        basef = [v for v in (p.get("baseline_mw") or []) if num(v)]
        if basef:
            out[f"wc|pair|{key}|base_mean_mw"] = abs(sum(basef) / len(basef))
    ev = file["event"]
    out[f"reached|{ev}|n"] = float(hit)
    out[f"reached|{ev}|of"] = float(with_base)
    return out


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--figures", required=True)
    ap.add_argument("--files", default=os.path.join(ROOT, "site", "data", "regions", "events"))
    a = ap.parse_args()
    try:
        with open(a.figures, encoding="utf-8") as f:
            page = json.load(f)["events"]
    except (OSError, ValueError, KeyError) as e:
        print(f"the figures file cannot be read: {e}")
        return 2
    total = passed = events = 0
    for event, drawn in page.items():
        at = os.path.join(a.files, f"{event}.json")
        if not drawn.get("file") or not os.path.exists(at):
            print(f"{event}: no file on the site yet")
            continue
        with open(at, encoding="utf-8") as f:
            file = json.load(f)
        if file.get("license", "public") != "public" or drawn.get("held"):
            print(f"{event}: the file is not public, not recomputed (the page draws no figure)")
            continue
        events += 1
        ours = expected(file)
        figures = drawn["figures"]
        n = ok = 0
        for key, shown in sorted(figures.items()):
            n += 1
            if key not in ours:
                print(f"  FAIL {event} {key}: the page shows {shown}, the file gives no figure by the note's rule")
                continue
            value, step = parse(shown)
            want = ours[key]
            # the page shows a pair's figures and a difference's without a sign only where the rule says so
            if abs(value - want) <= step / 2 + 1e-9:
                ok += 1
            else:
                print(f"  FAIL {event} {key}: the page shows {shown}, ours {want:.6f}")
        # every figure the rule gives must be on the page too (a missing figure is a fault of the page)
        absent = [k for k in ours if k not in figures and not (k.endswith("|hours") and ours[k] == 0.0)]
        for k in absent:
            n += 1
            print(f"  FAIL {event} {k}: ours {ours[k]:.6f}, not on the page")
        print(f"{event}: {ok} of {n} figures")
        total += n
        passed += ok
    if not events:
        print("no event's file is on the site yet: nothing to recompute")
        return 0
    print(f"{passed} of {total} figures over {events} events")
    return 0 if passed == total else 1


if __name__ == "__main__":
    sys.exit(main())

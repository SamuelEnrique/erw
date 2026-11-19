"""Energy Research Warehouse (ERW), session 8460 (chain 503, part E): the replication of "The whole country" on
/supply (net imports by month and by neighbour, who trades with whom, the generation mix by region).

Written from the method note (docs/methods/supply_and_trade.md, the section "The whole country") and the contract of
the files (docs/state/page_files_regions.md, sections 4, 5 and 7) alone, not from the page's code. Standard library
only.

For each file of the whole country that is on the site (site/data/regions/trade/<region>.json, trade_matrix.json and
mix/<region>.json, written by the data machine from EIA's Form EIA-930), every figure the section prints is recomputed
here from the file and set beside the figure the site's own code draws (a figures file written by
site/scripts/supply-regions-figures.mjs):

- a region's year with each neighbour: its own report, the neighbour's report and the gap in GWh, the gap in percent,
  the months held and the months of the year in the file; the year from all neighbours;
- the year month by month: all neighbours and each neighbour by the own report, and from the month's hover the
  neighbour's report, the gap and its percent;
- each pair of regions and of balancing authorities in a year: the sender's and the receiver's report, the mean, the
  gap, its percent, and which the row says sent and which received; the counts of pairs and of authorities;
- a region's mix: each source's share of net generation by month as the file writes it, the net generation, the days
  held; the year's row (each source's energy over the year's held months as a percent of the net generation of those
  same months), the year's net generation and its count of months;
- which figures carry the mark of a large gap (10 percent or more of the mean size of the two reports);
- the regions and the year drawn when the address names none.

A figure passes when ours is within half the last digit the page shows. A figure the rule gives that the page does not
show fails, and so does a figure the page shows that the rule does not give. Exit 0 when every figure of every file
passes (also when no file is on the site yet: nothing to compare, said so), 1 when one does not, 2 on bad input.

    python replication/supply/replicate_regions.py --figures <figures.json> [--files <the folder of the files>]
                                                   [--same-flow]

--same-flow also sets the two files that hold one flow side by side: a pair's year in trade_matrix.json and the sum
of the same year's months in each region's trade file (both are sums of EIA's Eastern months). A difference there is
a matter of the files, not of the page; it is printed and makes the exit 1.

No row of a warehouse table is read and nothing is written. The files are public (EIA's Form EIA-930, public domain);
a file whose license line is not "public", or that the page holds, is not recomputed, as the page draws no figure
from it.
"""
from __future__ import annotations

import argparse
import json
import os
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
# EIA's thirteen regions of the lower 48 in the contract's order, then the two neighbours outside it
NAME = {"CAL": "California", "CAR": "Carolinas", "CENT": "Central", "FLA": "Florida", "MIDA": "Mid-Atlantic", "MIDW": "Midwest",
        "NE": "New England", "NW": "Northwest", "NY": "New York", "SE": "Southeast", "SW": "Southwest", "TEN": "Tennessee",
        "TEX": "Texas", "CAN": "Canada", "MEX": "Mexico"}
REGIONS = list(NAME)[:13]
SOURCES = ["natural_gas", "coal", "nuclear", "wind", "solar", "hydro", "storage", "other"]
LARGE_PCT = 10.0          # the note: a gap of 10 percent or more of the mean size of the two reports is called large
SAME_FLOW_MWH = 50.0      # half of 0.1 GWh, the last digit the page shows


def num(v):
    return isinstance(v, (int, float)) and not isinstance(v, bool) and v == v and abs(v) != float("inf")


def at(arr, i):
    """The value of an array at a position, or None when it is not held there."""
    return arr[i] if arr and i < len(arr) and num(arr[i]) else None


def gap_pct(gap, one, other):
    """The gap as a percent of the mean size of the two reports (the mean of their absolute values); None when one of
    the three is not held or both reports are zero."""
    if gap is None or one is None or other is None:
        return None
    size = (abs(one) + abs(other)) / 2
    return abs(gap) / size * 100 if size > 0 else None


def parse(shown):
    """A figure as the page shows it ("+1,234.5", "-10.0", "12") as a number and the size of its last digit."""
    s = shown.replace(",", "").replace("+", "").strip()
    value = float(s)
    step = 10 ** -len(s.split(".")[1]) if "." in s else 1.0
    return value, step


def years_of(months):
    return sorted({m[:4] for m in months})


def expected_trade(code, file, figs, large):
    """One region's trade file (the contract's section 5): every year its months touch, and every month."""
    months = file["months"]
    neighbours = file.get("neighbors") or {}
    total = file.get("net_imports_mwh")
    for year in years_of(months):
        pos = [i for i, m in enumerate(months) if m[:4] == year]
        for nb, n in neighbours.items():
            own, their, gap = n.get("net_imports_mwh"), n.get("their_report_mwh"), n.get("gap_mwh")
            key = f"trade|{code}|{year}|{nb}"
            # a year's figure is the sum of the months the file holds; the months held are counted beside it
            for name, arr in (("own", own), ("their", their), ("gap", gap)):
                held = [at(arr, i) for i in pos if at(arr, i) is not None]
                if held:
                    figs[f"{key}|{name}"] = sum(held) / 1000
                    if name == "own":
                        figs[f"{key}|months"] = float(len(held))
                        figs[f"{key}|months|of"] = float(len(pos))
            # the percent runs over the months that hold both reports and the gap
            three = [i for i in pos if at(own, i) is not None and at(their, i) is not None and at(gap, i) is not None]
            if three:
                pct = gap_pct(sum(gap[i] for i in three), sum(own[i] for i in three), sum(their[i] for i in three))
                if pct is not None:
                    figs[f"{key}|gap_pct"] = pct
                    if pct >= LARGE_PCT:
                        large.add(f"{key}|gap_pct")
        held = [at(total, i) for i in pos if at(total, i) is not None]
        if held:
            figs[f"trade|{code}|{year}|all"] = sum(held) / 1000
            figs[f"trade|{code}|{year}|all|months"] = float(len(held))
            figs[f"trade|{code}|{year}|all|months|of"] = float(len(pos))
        for i in pos:
            m = months[i]
            if at(total, i) is not None:
                figs[f"trade|{code}|{m}|all"] = total[i] / 1000
            for nb, n in neighbours.items():
                o, t, g = at(n.get("net_imports_mwh"), i), at(n.get("their_report_mwh"), i), at(n.get("gap_mwh"), i)
                if o is None:
                    continue
                key = f"trade|{code}|{m}|{nb}"
                figs[key] = o / 1000
                if t is not None:
                    figs[f"{key}|their"] = t / 1000
                if g is not None:
                    figs[f"{key}|gap"] = g / 1000
                pct = gap_pct(g, o, t)
                if pct is not None:
                    figs[f"{key}|gap_pct"] = pct
                    if pct >= LARGE_PCT:
                        large.add(key)   # in the month table the mark stands on the month's own figure


def expected_mix(code, file, figs):
    """One region's mix file (the contract's section 4): every month it holds and every year they touch."""
    months = file.get("months") or {}
    for m, r in months.items():
        for s in SOURCES:
            if num(r.get(f"{s}_share_pct")):
                figs[f"mix|{code}|{m}|{s}"] = r[f"{s}_share_pct"]       # the share as the file writes it
        if num(r.get("net_generation_mwh")):
            figs[f"mix|{code}|{m}|net"] = r["net_generation_mwh"] / 1000
        if num(r.get("days_held")):
            figs[f"mix|{code}|{m}|days_held"] = float(r["days_held"])
            if num(r.get("days_in_month")):
                figs[f"mix|{code}|{m}|days_in_month"] = float(r["days_in_month"])
    for year in years_of(months):
        rows = [months[m] for m in sorted(months) if m[:4] == year]
        figs[f"mix|{code}|{year}|months"] = float(len(rows))
        for s in SOURCES:
            # the source's energy over the year's months that hold it and the net generation, over the net generation
            # of those same months
            both = [(r[f"{s}_mwh"], r["net_generation_mwh"]) for r in rows if num(r.get(f"{s}_mwh")) and num(r.get("net_generation_mwh"))]
            net = sum(g for _, g in both)
            if both and net != 0:
                figs[f"mix|{code}|{year}|{s}"] = sum(e for e, _ in both) / net * 100
        held = [r["net_generation_mwh"] for r in rows if num(r.get("net_generation_mwh"))]
        if held:
            figs[f"mix|{code}|{year}|net"] = sum(held) / 1000


def expected_matrix(file, years, figs, large, words):
    """The matrix file (the contract's section 7): each pair of regions and of balancing authorities in its year, and
    for every year a file holds the counts of the authorities' pairs and of the authorities with partners."""
    for kind, rows, name in (("pair", file.get("region_pairs") or [], lambda c: NAME.get(c, c)), ("bapair", file.get("ba_pairs") or [], lambda c: c)):
        for r in rows:
            a, b = r.get("a"), r.get("b")
            if not a or not b:
                continue
            year = str(r.get("year"))
            key = f"{kind}|{a}-{b}|{year}"
            ra, rb, mean, gap = (r.get(k) if num(r.get(k)) else None for k in ("a_report_mwh", "b_report_mwh", "mean_mwh", "gap_mwh"))
            # the file's direction; the sign of its mean where it names none; no direction at zero or with no mean
            d = r.get("direction")
            if d not in ("a_to_b", "b_to_a"):
                d = ("a_to_b" if mean > 0 else "b_to_a") if mean is not None and mean != 0 else None
            turn = -1 if d == "b_to_a" else 1
            sender, receiver = (rb, ra) if d == "b_to_a" else (ra, rb)
            if sender is not None:
                figs[f"{key}|from_report"] = sender * turn / 1000
            if receiver is not None:
                figs[f"{key}|to_report"] = receiver * turn / 1000
            if mean is not None:
                figs[f"{key}|mean"] = mean * turn / 1000
            if gap is not None:
                figs[f"{key}|gap"] = gap / 1000      # as the file gives it: the sender's report less the receiver's
            pct = gap_pct(gap, ra, rb)
            if pct is not None:
                figs[f"{key}|gap_pct"] = pct
                if pct >= LARGE_PCT:
                    large.add(f"{key}|gap_pct")
            if d:
                words[key] = {"sent": name(b if d == "b_to_a" else a), "received": name(a if d == "b_to_a" else b)}
            else:
                words[key] = {"sent": f"{name(a)} and {name(b)}", "received": "no net flow" if mean == 0 else "not held yet"}
    partners = file.get("partners") or {}
    for year in years:
        figs[f"bapairs|{year}|n"] = float(sum(1 for r in file.get("ba_pairs") or [] if str(r.get("year")) == year and r.get("a") and r.get("b")))
        figs[f"partners|{year}|n"] = float(sum(1 for p in partners.values() if isinstance(p, dict) and isinstance(p.get(year), dict)))


def first_year(read):
    """The year drawn when the address names none: of the files of the two regions drawn first and the matrix, the
    last calendar year that had ended when the newest of them was built, when they hold it; else the newest year
    they hold before it; else the newest they hold."""
    built, years = "", set()
    for rel, file in read.items():
        if rel not in ("trade/cal.json", "trade/car.json", "mix/cal.json", "mix/car.json", "trade_matrix.json"):
            continue
        built = max(built, str(file.get("built") or ""))
        if rel.startswith("trade/"):
            years |= set(years_of(file["months"]))
        elif rel.startswith("mix/"):
            years |= set(years_of(file.get("months") or {}))
        else:
            years |= {str(y) for y in file.get("years") or []}
    if not years:
        return None
    ended = str(int(built[:4]) - 1) if built[:4].isdigit() else None
    before = [y for y in years if ended and y <= ended]
    return max(before) if before else max(years)


def same_flow(read):
    """A pair's year in the matrix beside the same year's months in each region's trade file. Returns (agree, total)."""
    matrix = read.get("trade_matrix.json")
    n = ok = 0
    if not matrix:
        return 0, 0
    for r in matrix.get("region_pairs") or []:
        a, b, year = r.get("a"), r.get("b"), str(r.get("year"))
        for side, other, report, sign in ((a, b, r.get("a_report_mwh"), -1), (b, a, r.get("b_report_mwh"), 1)):
            trade = read.get(f"trade/{str(side).lower()}.json")
            nb = ((trade or {}).get("neighbors") or {}).get(other)
            if not nb or not num(report):
                continue
            pos = [i for i, m in enumerate(trade["months"]) if m[:4] == year]
            own = [at(nb.get("net_imports_mwh"), i) for i in pos]
            if not pos or any(v is None for v in own):
                continue   # a year the trade file holds in part is not set against the matrix
            # the matrix counts power from a to b; a region's net imports from its neighbour run the other way for a
            n += 1
            ours = sign * sum(own)
            if abs(ours - report) <= SAME_FLOW_MWH:
                ok += 1
            else:
                print(f"  DIFFERS {a}-{b} {year}, {side}'s report: the matrix {report / 1000:,.1f} GWh from {a} to {b}, "
                      f"the months of trade/{str(side).lower()}.json {ours / 1000:,.1f} GWh")
    return ok, n


def load(folder, rel):
    path = os.path.join(folder, *rel.split("/"))
    if not os.path.exists(path):
        return None
    try:
        with open(path, encoding="utf-8") as f:
            v = json.load(f)
    except ValueError:
        return None
    return v if isinstance(v, dict) else None


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--figures", required=True)
    ap.add_argument("--files", default=os.path.join(ROOT, "site", "data", "regions"))
    ap.add_argument("--same-flow", action="store_true")
    a = ap.parse_args()
    try:
        with open(a.figures, encoding="utf-8") as f:
            page = json.load(f)
        drawn, page_large, page_words, state = page["figures"], set(page["large"]), page["words"], page["files"]
    except (OSError, ValueError, KeyError, TypeError) as e:
        print(f"the figures file cannot be read: {e}")
        return 2

    rels = [f"trade/{c.lower()}.json" for c in REGIONS] + [f"mix/{c.lower()}.json" for c in REGIONS] + ["trade_matrix.json"]
    read = {}
    fails = []
    for rel in rels:
        file = load(a.files, rel)
        said = state.get(rel) or {}
        if file is None:
            if said.get("file"):
                fails.append(f"{rel}: the page read a file that is not in {a.files}")
            continue
        if rel.startswith("trade/") and not isinstance(file.get("months"), list):
            print(f"{rel}: no list of months, not in the contract's form (the page says not built yet)")
            continue
        if not said.get("file"):
            if "fixture" in file:
                print(f"{rel}: a fixture, which the site's reader refuses in its own folder: not recomputed")
            else:
                fails.append(f"{rel}: the file is in the folder and the page did not read it")
            continue
        if file.get("license", "public") != "public" or said.get("held"):
            print(f"{rel}: the file is not public, not recomputed (the page draws no figure)")
            continue
        read[rel] = file
    if not read and not fails:
        print("no file of the whole country is on the site yet: nothing to recompute")
        return 0

    figs, large, words = {}, set(), {}
    years = set()
    for rel, file in read.items():
        code = os.path.basename(rel)[:-5].upper()
        if rel.startswith("trade/"):
            expected_trade(code, file, figs, large)
            years |= set(years_of(file["months"]))
        elif rel.startswith("mix/"):
            expected_mix(code, file, figs)
            years |= set(years_of(file.get("months") or {}))
        else:
            years |= {str(y) for y in file.get("years") or []}
    if "trade_matrix.json" in read:
        expected_matrix(read["trade_matrix.json"], sorted(years), figs, large, words)

    n = ok = 0
    for key, shown in sorted(drawn.items()):
        n += 1
        if key not in figs:
            fails.append(f"{key}: the page shows {shown}, the file gives no figure by the note's rule")
            continue
        try:
            value, step = parse(shown)
        except ValueError:
            fails.append(f"{key}: the page shows {shown!r}, which is not a figure")
            continue
        if abs(value - figs[key]) <= step / 2 + 1e-9:
            ok += 1
        else:
            fails.append(f"{key}: the page shows {shown}, ours {figs[key]:.6f}")
    # every figure the rule gives must be on the page too (a missing figure is a fault of the page)
    for key in sorted(k for k in figs if k not in drawn):
        n += 1
        fails.append(f"{key}: ours {figs[key]:.6f}, not on the page")
    # the mark of a large gap: on the same figures, no more and no fewer
    for key in sorted(large | page_large):
        n += 1
        if key in large and key in page_large:
            ok += 1
        elif key in large:
            fails.append(f"{key}: large by the note's rule ({figs.get(key if key.endswith('gap_pct') else key + '|gap_pct', 0):.3f} percent), not marked on the page")
        else:
            fails.append(f"{key}: marked large on the page, not large by the note's rule")
    # which side the row says sent and which received
    for key in sorted(set(words) | set(page_words)):
        n += 1
        if words.get(key) == page_words.get(key):
            ok += 1
        else:
            fails.append(f"{key}: the page's row reads {page_words.get(key)}, ours {words.get(key)}")
    # the regions and the year drawn first
    first = page.get("first") or {}
    for name, ours in (("a", "CAL"), ("b", "CAR"), ("year", first_year(read))):
        if first.get(name) is None and (ours is None or name != "year"):
            continue
        n += 1
        if first.get(name) == ours:
            ok += 1
        else:
            fails.append(f"first|{name}: the page draws {first.get(name)} first, ours {ours}")

    for line in fails:
        print(f"  FAIL {line}")
    kinds = [("trade", "trade/"), ("mix", "mix/"), ("matrix", "trade_matrix")]
    held = ", ".join(f"{sum(1 for r in read if r.startswith(p))} {name} file{'s' if sum(1 for r in read if r.startswith(p)) != 1 else ''}" for name, p in kinds)
    print(f"{ok} of {n} figures over {len(read)} files ({held})")
    code = 0 if ok == n and not fails else 1
    if a.same_flow:
        agree, total = same_flow(read)
        if total:
            print(f"the same flow in two files: {agree} of {total} agree within {SAME_FLOW_MWH / 1000:.2f} GWh")
            if agree != total:
                code = 1
        else:
            print("the same flow in two files: no pair's year stands whole in both the matrix and a trade file")
    return code


if __name__ == "__main__":
    sys.exit(main())

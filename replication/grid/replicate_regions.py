#!/usr/bin/env python3
"""ERW, the Grid tool's thirteen regions: the replication a reader can run (session 8606, chain 504).

The region tabs of /grid draw site/data/regions/index.json, mix/<region>.json and trade/<region>.json. This script
reads those files and regions_page_figures.json (the figures the page draws, read from the page by
regions_figures.mjs), computes every such figure again without the page's code, and compares. For each region:

- the latest hour held: the newest hour of the file's hourly part that holds a net generation; its demand, net
  generation and net imports; each of the eight sources with its megawatts and its share of that hour's net generation;
- the period drawn: the file's newest month; each source's energy, and its share computed here as its energy over
  the period's net generation; the period's net generation; the days held of the days in the month;
- the months the file does not hold between its first and newest month, and the whole months since the newest;
- one calendar month across the years: net load by hour (demand less wind and solar), its lowest hour from 09:00
  to 16:00, its highest from 16:00, the ramp between them, the days held;
- the trade of the newest month in which any neighbour's own report is held: each neighbour's net imports by the
  region's own report, by the neighbour's, the gap, the hours each side held; the total; and, when the reports hold
  only a part of the month, the most hours of the region's own report and the hours of the month.

A figure the page prints as "not held" must be absent from the file, and the other way round. Nothing is filled.

    python replication/grid/replicate_regions.py [--regions DIR] [--page JSON] [--csv OUT]

Exit 0 when every figure is met inside its tolerance (half of the last digit shown; for a share, 0.056 of a percent,
the file's shares being held to two decimals), 1 when one is not, 2 when an input cannot be read. Standard library only.
This replicates the page from its files. The files against EIA's own series are crosscheck_regions.py; the files from
the warehouse's tables are the data machine's (docs/methods/regions_pages.md).
"""
import argparse
import csv
import datetime as dt
import json
import os
import re
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(os.path.dirname(HERE))
SOURCES = [("natural_gas", "Natural gas"), ("coal", "Coal"), ("nuclear", "Nuclear"), ("wind", "Wind"), ("solar", "Solar"), ("hydro", "Hydro"), ("storage", "Storage"), ("other", "Other")]
MONTH = re.compile(r"^\d{4}-(0[1-9]|1[0-2])$")
NAMES = ["January", "February", "March", "April", "May", "June", "July", "August", "September", "October", "November", "December"]


def load(path):
    with open(path, encoding="utf-8") as f:
        return json.load(f)


def num(text):
    """A figure as the page prints it, as a number; None for "not held" or an empty cell."""
    if text is None:
        return None
    t = text.replace(",", "").replace("MW", "").replace("%", "").strip()
    if t in ("", "not held", "not held for this region"):
        return None
    return float(t)


def month_name(k):
    return f"{NAMES[int(k[5:]) - 1]} {k[:4]}"


class Tally:
    def __init__(self):
        self.rows = []

    def check(self, region, name, page, computed, tol):
        """page and computed are numbers or None (not held)."""
        if page is None or computed is None:
            met = page is None and computed is None
        else:
            met = abs(page - computed) <= tol + 1e-9
        self.rows.append({"region": region, "figure": name, "page": "not held" if page is None else repr(page), "computed": "not held" if computed is None else repr(round(computed, 4)), "tolerance": tol, "met": "yes" if met else "no"})
        return met

    def same(self, region, name, page, computed):
        met = page == computed
        self.rows.append({"region": region, "figure": name, "page": str(page), "computed": str(computed), "tolerance": "", "met": "yes" if met else "no"})
        return met


def latest(hourly):
    gen = hourly.get("net_generation") or []
    i = min(int(hourly["hours"]["n"]), len(gen)) - 1
    while i >= 0 and gen[i] is None:
        i -= 1
    return i if i >= 0 else None


def at(hourly, key, i):
    v = hourly.get(key)
    return None if not v or i >= len(v) else v[i]


def months_not_held(mix):
    held = sorted(k for k in mix["months"] if MONTH.match(k))
    if not held:
        return 0, [], []
    built = mix.get("built", "")[:7] if MONTH.match(mix.get("built", "")[:7]) else held[-1]
    y, m = int(held[0][:4]), int(held[0][5:])
    span, missing, after = 0, [], []
    while True:
        k = f"{y}-{m:02d}"
        if k > held[-1] and k >= built:
            break
        if k > held[-1]:
            after.append(k)
        else:
            span += 1
            if k not in mix["months"]:
                missing.append(k)
        m += 1
        if m > 12:
            y, m = y + 1, 1
    return span, missing, after


def mix_tab(code, mix, page, t):
    hourly = mix.get("hourly")
    i = latest(hourly) if hourly else None
    if i is None:
        t.same(code, "the latest hour held", page.get("now"), None)
    else:
        ts = (dt.datetime.strptime(hourly["hours"]["start"], "%Y-%m-%dT%H:%M:%SZ") + dt.timedelta(hours=i * int(hourly["hours"].get("step_hours", 1)))).strftime("%Y-%m-%dT%H:%M:%SZ")
        t.same(code, "the latest hour held", page.get("now"), ts)
        total = at(hourly, "net_generation", i)
        for name, key in (("Demand", "demand"), ("Net generation", "net_generation"), ("Net imports", "net_imports")):
            t.check(code, f"latest hour: {name}, MW", num(page["figures"].get(name)), at(hourly, key, i), 0.5)
        t.same(code, "latest hour: the sources listed", [r[0] for r in page["now_rows"]], [label for _, label in SOURCES])
        for (key, label), row in zip(SOURCES, page["now_rows"]):
            mw = at(hourly, key, i)
            t.check(code, f"latest hour: {label}, MW", num(row[1]), mw, 0.5)
            t.check(code, f"latest hour: {label}, share of net generation, percent", num(row[2]), None if mw is None or not total else mw / total * 100, 0.056)
        t.check(code, "hours drawn in the hour by hour chart", float(page["hours_drawn"]), float(min(int(hourly["hours"]["n"]), 35 * 24)), 0)
    # the period drawn: the file's newest month
    upto = mix["upto"] if mix["upto"] in mix["months"] else sorted((k for k in mix["months"] if MONTH.match(k)), reverse=True)[0]
    t.same(code, "the period drawn", page.get("period"), upto)
    p = mix["months"][upto]
    drawn = {r[0]: r for r in page["shares_rows"]}
    total = p.get("net_generation_mwh")
    for key, label in SOURCES:
        if f"{key}_mwh" not in p:
            t.same(code, f"{upto}: {label} is not in the period and not in the table", label in drawn, False)
            continue
        row = drawn.get(label)
        if not row:
            t.same(code, f"{upto}: {label} in the table", False, True)
            continue
        mwh = p[f"{key}_mwh"]          # None for a source no authority of the region has ever printed: blank on the page, never zero
        t.check(code, f"{upto}: {label}, MWh", num(row[2]), mwh, 0.5)
        t.check(code, f"{upto}: {label}, share, percent (its MWh over the period's net generation)", num(row[1]), None if mwh is None or not total else mwh / total * 100, 0.056)
    t.check(code, f"{upto}: net generation, MWh", num(drawn.get("Net generation", ["", "", None])[2]), total, 0.5)
    held_labels = {label for key, label in SOURCES if p.get(f"{key}_mwh") is not None}
    blank = [r[0] for r in page["shares_rows"][:-1] if r[0] not in held_labels]
    t.same(code, f"{upto}: the sources the period holds as blank stand after the others", [r[0] for r in page["shares_rows"][:-1]][len(page["shares_rows"]) - 1 - len(blank):], blank)
    shown = [r[0] for r in page["shares_rows"][:-1] if r[0] in held_labels]
    by_share = sorted(shown, key=lambda label: -float(p.get(next(k for k, lab in SOURCES if lab == label) + "_share_pct", 0)))
    t.same(code, f"{upto}: the table's order is by share, largest first", [float(p.get(next(k for k, lab in SOURCES if lab == label) + "_share_pct", 0)) for label in shown],
           [float(p.get(next(k for k, lab in SOURCES if lab == label) + "_share_pct", 0)) for label in by_share])
    days = f"{int(p['days_held']):,} days held" + (f" of {int(p['days_in_month'])}" if isinstance(p.get("days_in_month"), (int, float)) else "") + "."
    t.same(code, f"{upto}: the days held", page.get("days_line"), days)
    # the months not held
    span, missing, after = months_not_held(mix)
    line = page.get("months_not_held")
    got = None if not line else [int(x) for x in re.match(r"(\d+) of the (\d+) months", line).groups()]
    t.same(code, "months not held of the months from the first to the newest", got, [len(missing), span] if missing else None)
    line = page.get("months_after")
    want = None if not after else (f"{month_name(after[0])} is not held" if len(after) == 1 else f"No month from {month_name(after[0])} to {month_name(after[-1])} is held") + f": the newest month held is {month_name(upto)}."
    t.same(code, "the whole months since the newest held", line, want)
    # one calendar month across the years
    cal = upto[5:]
    years = []
    # a source the file names as never printed (no authority of the region has reported it since July 2018) is not there
    # to take from demand: net load is then demand less the one that is reported, and the page says so under the table
    never = [k for k in (mix.get("sources_not_printed") or []) if k in ("wind", "solar")]
    t.same(code, "net load: the sources left out because no authority has ever reported them", page.get("net_load_without"), ",".join(never) if never else None)
    for k in sorted(m for m in mix["months"] if MONTH.match(m) and m[5:] == cal):
        avg = mix["months"][k]["avg"]
        d = avg.get("demand") or []
        w = [0.0] * 24 if "wind" in never and avg.get("wind") is None else (avg.get("wind") or [])
        s = [0.0] * 24 if "solar" in never and avg.get("solar") is None else (avg.get("solar") or [])
        net = [None if h >= len(d) or h >= len(w) or h >= len(s) or d[h] is None or w[h] is None or s[h] is None else round(d[h] - w[h] - s[h], 1) for h in range(24)]

        def best(a, b, lower):
            out = None
            for h in range(a, b + 1):
                if net[h] is None:
                    continue
                if out is None or (net[h] < out[1] if lower else net[h] > out[1]):
                    out = (h, net[h])
            return out
        low, high = best(9, 16, True), best(16, 23, False)
        years.append((k[:4], low, high, None if not low or not high else round(high[1] - low[1], 1), mix["months"][k]["days_held"]))
    t.same(code, f"{NAMES[int(cal) - 1]} across the years: the years", [r[0] for r in page["years_rows"]], [y[0] for y in years])
    for row, (year, low, high, ramp, days) in zip(page["years_rows"], years):
        t.check(code, f"{NAMES[int(cal) - 1]} {year}: midday low of net load, MW", num(row[1]), None if not low else low[1], 0.5)
        t.same(code, f"{NAMES[int(cal) - 1]} {year}: its hour", row[2], "" if not low else f"{low[0]:02d}:00")
        t.check(code, f"{NAMES[int(cal) - 1]} {year}: evening high, MW", num(row[3]), None if not high else high[1], 0.5)
        t.same(code, f"{NAMES[int(cal) - 1]} {year}: its hour", row[4], "" if not high else f"{high[0]:02d}:00")
        t.check(code, f"{NAMES[int(cal) - 1]} {year}: ramp, MW", num(row[5]), ramp, 0.5)
        t.check(code, f"{NAMES[int(cal) - 1]} {year}: days held", num(row[6]), float(days), 0)


def trade_tab(code, trade, page, t):
    months, nb = trade["months"], trade["neighbors"]
    newest = None
    for i in range(len(months) - 1, -1, -1):
        if any(i < len(n.get("net_imports_mwh", [])) and n["net_imports_mwh"][i] is not None for n in nb.values()):
            newest = i
            break
    t.same(code, "trade: the month drawn", page.get("month"), None if newest is None else months[newest])
    if newest is None:
        return
    i = newest

    def cell(v):
        return None if v is None or i >= len(v) else v[i]
    rows = sorted(((c, cell(n.get("net_imports_mwh")), cell(n.get("their_report_mwh")), cell(n.get("gap_mwh")), cell(n.get("hours_own")), cell(n.get("hours_their")), cell(n.get("hours_both"))) for c, n in nb.items()),
                  key=lambda r: (-abs(r[1] or 0), r[0]))
    t.same(code, f"trade {months[i]}: the neighbours, by the size of the region's own report", [r[0].split(" ")[-1] for r in page["rows"][:-1]], [r[0] for r in rows])
    for prow, (c, own, theirs, gap, ho, ht, hb) in zip(page["rows"], rows):
        t.check(code, f"trade {months[i]}: net imports from {c}, own report, MWh", num(prow[1]), own, 0.5)
        t.check(code, f"trade {months[i]}: net imports from {c}, the neighbour's report, MWh", num(prow[2]), theirs, 0.5)
        t.check(code, f"trade {months[i]}: gap with {c}, MWh", num(prow[3]), gap, 0.5)
        t.same(code, f"trade {months[i]}: hours with {c}: own, theirs, both", prow[4], ", ".join("" if h is None else f"{int(h):,}" for h in (ho, ht, hb)))
    t.check(code, f"trade {months[i]}: all neighbours, MWh", num(page["rows"][-1][1]), cell(trade.get("net_imports_mwh")), 0.5)
    of = (trade.get("hours_in_month") or [None] * len(months))[i]
    most = max([0] + [h for h in (cell(n.get("hours_own")) for n in nb.values()) if h is not None])
    want = None if not isinstance(of, (int, float)) or most >= of else f"{month_name(months[i])} is a part of a month here: the region's own reports hold at most {int(most):,} of its {int(of):,} hours."
    t.same(code, f"trade {months[i]}: the line on a part of a month", page.get("part_month"), want)


def main(argv):
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    ap.add_argument("--regions", default=os.path.join(ROOT, "site", "data", "regions"))
    ap.add_argument("--page", default=os.path.join(HERE, "regions_page_figures.json"))
    ap.add_argument("--csv", default="")
    a = ap.parse_args(argv)
    try:
        index, page = load(os.path.join(a.regions, "index.json")), load(a.page)
    except (OSError, ValueError) as e:
        print("cannot read an input:", e)
        return 2
    if page.get("index_built") != index.get("built"):
        print(f"the page's figures were read from files built {page.get('index_built')}; the files here were built {index.get('built')}. Read the page again (regions_figures.mjs) before comparing.")
        return 2
    t = Tally()
    for region in index["regions"]:
        code = region["code"]
        got = page["regions"].get(code)
        if not got or not got.get("mix") or not got.get("trade"):
            t.same(code, "the region is in the page's figures", bool(got), True)
            continue
        try:
            mix_tab(code, load(os.path.join(a.regions, "mix", code.lower() + ".json")), got["mix"], t)
            trade_tab(code, load(os.path.join(a.regions, "trade", code.lower() + ".json")), got["trade"], t)
        except (OSError, ValueError, KeyError) as e:
            print(f"{code}: cannot read its files: {e!r}")
            return 2
    met = sum(1 for r in t.rows if r["met"] == "yes")
    for code in [r["code"] for r in index["regions"]]:
        mine = [r for r in t.rows if r["region"] == code]
        print(f"{code}: {sum(1 for r in mine if r['met'] == 'yes')} of {len(mine)} figures met")
    for r in t.rows:
        if r["met"] == "no":
            print(f"  NOT MET {r['region']} | {r['figure']} | page {r['page']} | computed {r['computed']}")
    print(f"{met} of {len(t.rows)} figures met (the page read {page.get('taken')}, the files built {index.get('built')})")
    if a.csv:
        with open(a.csv, "w", encoding="utf-8", newline="") as f:
            f.write("# ERW, the Grid tool's thirteen regions: every figure of the page computed again from its files (replication/grid/replicate_regions.py)\n")
            f.write("# Source: site/data/regions/index.json, mix/<region>.json, trade/<region>.json (Form EIA-930, public domain), built " + str(index.get("built")) + "\n")
            f.write("# Source URL: https://www.eia.gov/electricity/gridmonitor/ (the files' own source); the page's figures: replication/grid/regions_page_figures.json\n")
            f.write("# Retrieved: the page read " + str(page.get("taken")) + "\n")
            w = csv.DictWriter(f, fieldnames=["region", "figure", "page", "computed", "tolerance", "met"])
            w.writeheader()
            w.writerows(t.rows)
    return 0 if met == len(t.rows) else 1


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))

#!/usr/bin/env python3
"""ERW, the ERCOT peak premium explorer (/explore/ercot-peak-premium): the replication a reader can run
(session 7507, chain 304).

Written from the method note (docs/methods/ercot_peak_premium.md, "The tool as a reader meets it") and the two public
tables alone, not from the page's code. For every view the page can be asked for (each of the six hubs, the whole year
and each of the twelve months, every year offered, two years at a time) it works out from the tables what the page must
draw, by the note's rules:

  - which hubs, years and periods are offered, which first and second year a view opens on, which years are marked
    partial or not held, and whether the page must say the address asked for something the tables do not hold;
  - every figure: the three headline numbers, the five numbers of each of the four blocks, the nine figures of the
    thesis, for both years. A figure is the row of the table its key names. Where the note defines a figure by other
    rows of the same table (the peak-block IQR is Q3 less Q1, the spread is the peak median less the midday median, the
    worst-interval multiple is the 99.9th percentile over the median, the all-intervals minimum and maximum are the
    blocks', a complete year's count of intervals is 35,040 or 35,136), it is computed that way here and the row is
    held to it;
  - the text: a price or a ratio with two decimals, a count whole, thousands with commas.

and sets each beside what the page itself draws on the same rows (site/scripts/peak-premium-figures.mjs, run with node,
or a file of its output). The tables' own rows are recomputed from ERCOT's 15-minute prices by from_hourly.py.

    python replication/ercot_peak_premium/replicate.py              # N of N, or each difference named
    python replication/ercot_peak_premium/replicate.py --write      # also writes page_figures.json and page_figures.csv
    python replication/ercot_peak_premium/replicate.py --headline   # only the do-file's lines (replicate.do)

    --in-dir DIR      the folder of the two tables (default: $ERW_OUTPUT_DIR, else warehouse/output of this repository)
    --page FILE       the page's figures as a file (the JSON the node script writes) instead of running node
    --coverage FILE   warehouse/metadata/coverage.csv, the catalogue the freshness line is read from (default: this repository's)

A figure is inside the tolerance when it differs from the page's by at most half the last digit the page shows (0.005
for a price or a ratio, 0.5 for a count) and the text is the same. Exit 0 when every figure and every view agrees, 1
when one does not, 2 when the inputs cannot be read. Standard library only.
"""
import argparse
import calendar
import csv
import decimal
import json
import os
import subprocess
import sys
import tempfile

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(os.path.dirname(HERE))
SITE = os.path.join(ROOT, "site")
ANNUAL, MONTHLY = "ercot_peak_premium_annual", "ercot_peak_premium_monthly"
THESIS_HUB = "ercot:HB_HUBAVG"
# The note, "The tool as a reader meets it": what a view draws, in the order drawn.
HEADLINES = ["peak_iqr", "peak_minus_midday_median", "all_median"]
BLOCKS = ["overnight", "midday", "peak", "all"]
STATS = ["min", "q1", "median", "q3", "max"]
FIGURES = ["all_median", "all_p999", "worst_interval_multiple", "peak_iqr", "peak_minus_midday_median", "midday_min", "n_scarcity", "n_negative", "n_intervals"]
COUNTS = {"n_scarcity", "n_negative", "n_intervals"}
MONTH_NAMES = ["January", "February", "March", "April", "May", "June", "July", "August", "September", "October", "November", "December"]


def default_dir():
    for d in (os.environ.get("ERW_OUTPUT_DIR"), os.path.join(ROOT, "warehouse", "output")):
        if d and os.path.isdir(d):
            return d
    return os.path.join(ROOT, "warehouse", "output")


def read_table(path):
    """({(entity, variable, 'YYYY-MM'): value}, the header's lines) of a standard series table."""
    rows, header = {}, []
    with open(path, encoding="utf-8", newline="") as f:
        lines = []
        for line in f:
            if line.startswith("#"):
                header.append(line[1:].strip())
            else:
                lines.append(line)
    for r in csv.DictReader(lines):
        rows[(r["entity"], r["variable"], r["ts_utc"][:7])] = float(r["value"])
    return rows, header


class Tables:
    def __init__(self, in_dir):
        self.annual, self.annual_header = read_table(os.path.join(in_dir, ANNUAL + ".csv"))
        self.monthly, self.monthly_header = read_table(os.path.join(in_dir, MONTHLY + ".csv"))
        self.hubs = sorted({e for (e, v, _) in self.annual if v == "n_intervals"})

    def years(self, hub):
        return sorted({int(p[:4]) for (e, v, p) in self.annual if e == hub and v == "n_intervals"})

    def row(self, hub, variable, year, month):
        """The row a figure is: the annual table's for the whole year, the monthly table's for a month."""
        if month:
            return self.monthly.get((hub, variable, f"{year}-{month:02d}"))
        return self.annual.get((hub, variable, f"{year}-01"))

    def figure(self, hub, variable, year, month):
        """A figure by the note's definition where it has one on the table's other rows, else the row itself."""
        g = lambda v: self.row(hub, v, year, month)
        row = g(variable)
        if row is None:
            return None, "not held"
        if variable == "peak_iqr" and g("peak_q3") is not None:
            return g("peak_q3") - g("peak_q1"), "Q3 less Q1 of the peak block"
        if variable == "peak_minus_midday_median" and g("peak_median") is not None and g("midday_median") is not None:
            return g("peak_median") - g("midday_median"), "the peak median less the midday median"
        if variable == "worst_interval_multiple" and g("all_median"):
            return g("all_p999") / g("all_median"), "the 99.9th percentile over the median"
        if variable in ("all_min", "all_max"):
            parts = [g(f"{b}_{variable[4:]}") for b in BLOCKS[:3]]
            parts = [x for x in parts if x is not None]
            return (min(parts) if variable == "all_min" else max(parts)), "the blocks' " + ("lowest minimum" if variable == "all_min" else "highest maximum")
        if variable == "n_intervals" and not self.partial(hub, year, month):
            return float(full_period(year, month)), "the quarter hours of a complete period"
        return row, "the table's row"

    def held(self, hub, year, month):
        return self.row(hub, "n_intervals", year, month) is not None

    def partial(self, hub, year, month):
        """The note: a year is partial when its count is not 35,040 (35,136 in a leap year); a month when its count is
        below the quarter hours of the full month."""
        n = self.row(hub, "n_intervals", year, month)
        if n is None:
            return False
        if month:
            return n < full_period(year, month)
        return n != full_period(year, None)


def full_period(year, month):
    """The quarter hours of a complete local year or month in America/Chicago: 96 a day, four fewer in the month the
    clocks go forward (March) and four more in the month they go back (November), since 2007."""
    if not month:
        return 35136 if calendar.isleap(year) else 35040
    return calendar.monthrange(year, month)[1] * 96 + (-4 if month == 3 else 4 if month == 11 else 0)


def text_of(variable, v):
    """The note: a count whole, a price or a ratio with two decimals, thousands with commas. A value is taken at the
    table's six decimals and a tie at the third decimal (37.035, the median of two prices a cent apart) is rounded
    away from zero: 37.04, and -0.165 gives -0.17."""
    if variable in COUNTS:
        return f"{round(v):,}"
    d = decimal.Decimal(repr(round(v, 6))).quantize(decimal.Decimal("0.01"), rounding=decimal.ROUND_HALF_UP)
    s = f"{d:,.2f}"
    return "-0.00" if d == 0 and round(v, 6) < 0 else s


def tolerance(variable):
    return 0.5 if variable in COUNTS else 0.005


def view(t, q):
    """What the page must draw for the address q, by the note: the choices, the marks and the figures' keys in order."""
    unknown = []
    hub = q.get("hub") or (THESIS_HUB if THESIS_HUB in t.hubs else t.hubs[0])
    if hub not in t.hubs:
        unknown.append("hub")
        hub = THESIS_HUB if THESIS_HUB in t.hubs else t.hubs[0]
    month = None
    if q.get("month"):
        if q["month"] in [str(i) for i in range(1, 13)]:
            month = int(q["month"])
        else:
            unknown.append("month")
    years = t.years(hub)
    held = [y for y in years if t.held(hub, y, month)]
    complete = [y for y in held if not t.partial(hub, y, month)]
    first = held[0] if held else years[0]
    second = complete[-1] if complete else held[-1] if held else years[-1]
    if q.get("from"):
        if q["from"] in map(str, years):
            first = int(q["from"])
        else:
            unknown.append("first year")
    if q.get("to"):
        if q["to"] in map(str, years):
            second = int(q["to"])
        else:
            unknown.append("second year")
    pair = [second] if first == second else [first, second]
    table = MONTHLY if month else ANNUAL
    key = lambda v, y: f"series|{table}|{hub}|{v}|{y}-{month or 1:02d}-01T00:00:00Z"
    keys = []
    for v in HEADLINES:
        for y in ([second] if first == second else [second, first]):
            keys.append((v, y))
    for b in BLOCKS:
        for y in pair:
            keys.extend((f"{b}_{s}", y) for s in STATS)
    for v in FIGURES:
        keys.extend((v, y) for y in pair)
    drawn = [(v, y) for (v, y) in keys if t.row(hub, v, y, month) is not None]
    marks = [f"{y} ({'not held' if not t.held(hub, y, month) else 'partial'})" for y in years if not t.held(hub, y, month) or t.partial(hub, y, month)]
    lo, hi = min(first, second), max(first, second)
    return {
        "hub": hub, "month": month, "first": first, "second": second, "unknown": unknown, "marks": marks,
        "keys": [key(v, y) for (v, y) in drawn], "figures": [(key(v, y), hub, v, y, month) for (v, y) in drawn],
        "not_held": len(keys) - len(drawn),
        "download": f"/api/download?table={table}&entity={hub.replace(':', '%3A')}&start={lo}-01-01&end={hi + 1}-01-01",
    }


def page_from_node(in_dir, coverage):
    fd, out = tempfile.mkstemp(suffix=".json")
    os.close(fd)
    cmd = ["node", "--import", "./scripts/tsx-register.mjs", "scripts/peak-premium-figures.mjs",
           os.path.join(in_dir, ANNUAL + ".csv"), os.path.join(in_dir, MONTHLY + ".csv"), out]
    if coverage and os.path.exists(coverage):
        cmd.append(f"--coverage={coverage}")
    r = subprocess.run(cmd, cwd=SITE, capture_output=True, text=True, encoding="utf-8")
    if r.returncode != 0:
        raise OSError(f"the page could not be drawn (node exit {r.returncode}): {(r.stdout + r.stderr)[-800:]}")
    with open(out, encoding="utf-8") as f:
        page = json.load(f)
    os.remove(out)
    return page


def catalogue(path):
    out = {}
    if path and os.path.exists(path):
        with open(path, encoding="utf-8", newline="") as f:
            for r in csv.DictReader(line for line in f if not line.startswith("#")):
                if r["table"] in (ANNUAL, MONTHLY):
                    out[r["table"]] = r
    return out


def last_input(header):
    for line in header:
        if line.startswith("Last input interval:"):
            return line[len("Last input interval:"):].split(";")[0].strip()
    return None


def long_time(ts):
    return f"{int(ts[8:10])} {MONTH_NAMES[int(ts[5:7]) - 1]} {ts[:4]} {ts[11:16]} UTC"


def headline(t):
    """The do-file's lines: the page as it opens, and the five figures it leads with."""
    v = view(t, {})
    hub, a, b = v["hub"], v["first"], v["second"]
    f = lambda var, y: text_of(var, t.figure(hub, var, y, None)[0])
    return [
        f"the page opens on {hub.split(':')[1]}, the whole year, {a} against {b}",
        f"1. peak-block IQR, USD/MWh: {f('peak_iqr', b)} in {b} ({f('peak_iqr', a)} in {a})",
        f"2. peak median minus midday median, USD/MWh: {f('peak_minus_midday_median', b)} in {b} ({f('peak_minus_midday_median', a)} in {a})",
        f"3. median of all intervals, USD/MWh: {f('all_median', b)} in {b} ({f('all_median', a)} in {a})",
        f"4. 99.9th percentile, USD/MWh, and the worst-interval multiple: {f('all_p999', b)} and {f('worst_interval_multiple', b)} in {b} ({f('all_p999', a)} and {f('worst_interval_multiple', a)} in {a})",
        f"5. intervals at or above 1,000 USD/MWh, and at or below 0: {f('n_scarcity', b)} and {f('n_negative', b)} in {b} ({f('n_scarcity', a)} and {f('n_negative', a)} in {a})",
    ]


def main(argv):
    ap = argparse.ArgumentParser()
    ap.add_argument("--in-dir", default=default_dir())
    ap.add_argument("--page")
    ap.add_argument("--coverage", default=os.path.join(ROOT, "warehouse", "metadata", "coverage.csv"))
    ap.add_argument("--write", action="store_true")
    ap.add_argument("--headline", action="store_true")
    a = ap.parse_args(argv[1:])
    try:
        t = Tables(a.in_dir)
        if a.headline:
            print("\n".join(headline(t)))
            return 0
        if a.page:
            with open(a.page, encoding="utf-8") as f:
                page = json.load(f)
        else:
            page = page_from_node(a.in_dir, a.coverage)
    except (OSError, KeyError, ValueError) as exc:
        print(f"the inputs could not be read: {exc}")
        return 2

    cat = catalogue(a.coverage)
    newest = last_input(t.annual_header)
    bad_views, bad_figures, figures, rules = [], [], {}, {}
    expected_keys = set()
    for pv in page["views"]:
        v = view(t, pv["q"])
        why = []
        f = pv["filters"]
        if f.get("hub", {}).get("chosen") != v["hub"]:
            why.append(f"hub drawn {f.get('hub', {}).get('chosen')}, by the note {v['hub']}")
        if (f.get("month", {}).get("chosen") or "") != (str(v["month"]) if v["month"] else ""):
            why.append(f"period drawn {f.get('month', {}).get('chosen')!r}, by the note {v['month']}")
        if f.get("from", {}).get("chosen") != str(v["first"]) or f.get("to", {}).get("chosen") != str(v["second"]):
            why.append(f"years drawn {f.get('from', {}).get('chosen')} and {f.get('to', {}).get('chosen')}, by the note {v['first']} and {v['second']}")
        if f.get("from", {}).get("marked") != v["marks"] or f.get("to", {}).get("marked") != v["marks"]:
            why.append(f"years marked {f.get('from', {}).get('marked')}, by the note {v['marks']}")
        if f.get("hub", {}).get("options") != len(t.hubs) or f.get("from", {}).get("options") != len(t.years(v["hub"])):
            why.append("the hubs or the years offered are not the annual table's")
        if pv["asked_unknown"] != bool(v["unknown"]):
            why.append(f"the page {'says' if pv['asked_unknown'] else 'does not say'} the address asked for something not held; by the note {v['unknown']}")
        if pv["keys"] != v["keys"]:
            why.append(f"{len(pv['keys'])} figures drawn, {len(v['keys'])} by the note, or in another order")
        if pv["not_held"] != v["not_held"]:
            why.append(f"'not held' drawn {pv['not_held']} times, by the note {v['not_held']}")
        if pv["download"] != v["download"]:
            why.append(f"the rows' download is {pv['download']}, by the note {v['download']}")
        if newest and pv.get("newest_interval") != long_time(newest):
            why.append(f"the newest interval drawn is {pv.get('newest_interval')}, the header's is {long_time(newest)}")
        for fr in pv.get("fresh", []):
            c = cat.get(fr["table"])
            if c and (fr["last_run"] != c["last_run"] or fr["ts_max"] != c["ts_max"]):
                why.append(f"the freshness of {fr['table']} is not the catalogue's")
        if cat and len(pv.get("fresh", [])) != 2:
            why.append("the freshness line does not name both tables")
        if why:
            bad_views.append((pv["q"], why))
        for (key, hub, var, y, month) in v["figures"]:
            expected_keys.add(key)
            if key in figures:
                continue
            mine, rule = t.figure(hub, var, y, month)
            row = t.row(hub, var, y, month)
            drawn = page["keyed"].get(key)
            figures[key] = (hub, var, y, month, mine, drawn)
            rules[rule] = rules.get(rule, 0) + 1
            if drawn is None:
                bad_figures.append((key, "not drawn by the page", mine, None))
            elif abs(drawn["raw"] - mine) > tolerance(var) or drawn["text"] != text_of(var, mine) or abs(row - mine) > 0.000002 * max(1.0, abs(mine) if var == "worst_interval_multiple" else 1.0):
                bad_figures.append((key, f"the page draws {drawn['text']} (read {drawn['raw']}), the table's row is {row}", mine, drawn))
    only_page = sorted(set(page["keyed"]) - expected_keys)

    n = len(figures)
    print(f"ERCOT peak premium explorer, the tables in {a.in_dir}: {ANNUAL} {len(t.annual):,} rows, {MONTHLY} {len(t.monthly):,} rows; last input interval {newest}")
    print("how each figure was computed: " + "; ".join(f"{k}: {v:,}" for k, v in sorted(rules.items(), key=lambda kv: -kv[1])))
    for key, what, mine, _ in bad_figures[:40]:
        print(f"  DIFFERS {key}: {what}; the replication {mine}")
    for key in only_page[:10]:
        print(f"  ONLY ON THE PAGE {key}")
    for q, why in bad_views[:20]:
        print(f"  VIEW {q}: " + "; ".join(why))
    print(f"{len(page['views']) - len(bad_views)} of {len(page['views'])} views open as the note says (the hub, the period, the two years, the years marked, the rows' download, the freshness line)")
    print(f"{n - len(bad_figures)} of {n} figures inside the tolerance, with the same text; {len(only_page)} drawn by the page and not expected; {len(page.get('conflicts', []))} drawn two ways")

    if a.write:
        rows = sorted(figures.items())
        with open(os.path.join(HERE, "page_figures.csv"), "w", encoding="utf-8", newline="\n") as f:
            f.write("table,hub,variable,period,page,replication,tolerance\n")
            for key, (hub, var, y, month, mine, drawn) in rows:
                f.write(f"{'monthly' if month else 'annual'},{hub.split(':')[1]},{var},{y}{f'-{month:02d}' if month else ''},\"{drawn['text'] if drawn else ''}\",{round(mine, 6):.6f},{tolerance(var)}\n")
        opening = view(t, {})
        doc = {
            "_about": "The ERCOT peak premium explorer (/explore/ercot-peak-premium): every figure the page draws for every hub, every period (the whole year and each month) and every year it offers, as the page's own code draws it on the two tables (site/scripts/peak-premium-figures.mjs), beside the replication's value (replication/ercot_peak_premium/replicate.py, written from docs/methods/ercot_peak_premium.md). A figure's check key is series|<table>|<hub>|<variable>|<period>. The tolerance is half the last digit shown: 0.005 for a price or a ratio, 0.5 for a count. The figures themselves are in page_figures.csv, one line each.",
            "tables": {"annual_rows": len(t.annual), "monthly_rows": len(t.monthly), "last_input_interval": newest,
                       "built": next((x for x in t.annual_header if x.startswith("Retrieved:")), None)},
            "views": len(page["views"]), "views_as_the_note_says": len(page["views"]) - len(bad_views),
            "figures": n, "figures_inside_the_tolerance": n - len(bad_figures),
            "opening": {"hub": opening["hub"], "period": "the whole year", "first_year": opening["first"], "second_year": opening["second"],
                        "figures": [{"key": k, "page": page["keyed"][k]["text"], "replication": round(figures[k][4], 6), "tolerance": tolerance(figures[k][1])} for k in opening["keys"] if k in page["keyed"]]},
            "headline": headline(t),
            "named_differences": [],
            "not_replicated": "the points of the three charts as a browser draws them (the same rows as the figures: a browser read), and the days since the tables were last computed (it moves with the day the page is read)",
        }
        with open(os.path.join(HERE, "page_figures.json"), "w", encoding="utf-8", newline="\n") as f:
            json.dump(doc, f, indent=1)
            f.write("\n")
        print("written: page_figures.json and page_figures.csv")
    return 0 if not bad_figures and not bad_views and not only_page and not page.get("conflicts") else 1


if __name__ == "__main__":
    sys.exit(main(sys.argv))

#!/usr/bin/env python3
"""ERW, the datacenter tracker (/datacenters and /datacenters?view=grids): the replication a reader can run
(session 7400, chain 303).

Written from the method note (docs/methods/datacenter_tracker.md) and the rows alone, not from the page's code: every
figure the page shows is computed again here, in this file's own words, and set beside the figure the page's own
functions give on the same rows (site/scripts/datacenter-tracker-figures.mjs, run with node, or a file of its output).
A difference is inside the tolerance when it is at most half the last digit the page shows.

    python replication/datacenter_tracker/fetch_rows.py          # the rows, from the live set, into rows/ (not in git)
    python replication/datacenter_tracker/replicate.py           # N of N
    python replication/datacenter_tracker/replicate.py --write   # also writes page_figures.json and page_figures.csv

    --rows DIR      another folder of rows (default: this folder's rows/)
    --page FILE     the page's figures as a file (the JSON the node script prints) instead of running node
    --today DAY     the day the page is drawn on, YYYY-MM-DD (default: the day the rows were retrieved)

The facilities are held ("license needed" since 21 October 2026), so the built page draws none of their figures to a
visitor; the page's figure here is what its functions compute on the rows, which is what it draws when the hold allows.
Exit 0 when every figure is inside its tolerance, 1 when one is not or a key is on one side only, 2 when the inputs
cannot be read. Standard library only.
"""
import argparse
import csv
import datetime
import json
import os
import shutil
import statistics
import subprocess
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(os.path.dirname(HERE))
SITE = os.path.join(ROOT, "site")

# The note, section 3: a named US state is one of the 50 states, the District of Columbia or Puerto Rico.
US = set("AL AK AZ AR CA CO CT DE DC FL GA HI ID IL IN IA KS KY LA ME MD MA MI MN MS MO MT NE NV NH NJ NM NY NC ND OH OK OR PA RI SC SD TN "
         "TX UT VT VA WA WV WI WY PR".split())
# The note, section 5: the grid that serves most of a state; a state split between grids has none.
GRID_OF_STATE = {"TX": "ERCOT", "CA": "CAISO", "NY": "NYISO", **{s: "ISO-NE" for s in "CT ME MA NH RI VT".split()},
                 **{s: "PJM" for s in "PA NJ MD DE VA WV OH DC".split()}, **{s: "MISO" for s in "MN IA WI MI LA".split()},
                 **{s: "SPP" for s in "OK KS NE".split()}}
GRIDS = {"ERCOT": "ercot", "CAISO": "caiso", "PJM": "pjm", "MISO": "miso", "SPP": "spp", "NYISO": "nyiso", "ISO-NE": "isone"}
SERIES = {"approved_to_energize_mw", "observed_nonsimultaneous_peak_mw", "observed_simultaneous_peak_mw", "new_submissions_count", "new_submissions_mw"}
NEAR = 0.95   # the calculator's rule: a month is complete when 95 percent of its hours hold a price


def load(path):
    with open(path, encoding="utf-8") as f:
        return json.load(f)


class Fac:
    """One facility, read as the note's sections 2 and 3 say."""

    def __init__(self, r):
        x = r.get("extra") or {}
        self.id = r["entity_id"]
        self.operator = r.get("operator") or ""
        self.state = x.get("state") or ""
        self.us = (x.get("country") or ("US" if self.state in US else "")) == "US"
        self.status = (r.get("status") or "")
        self.cancelled = self.status.lower() in ("withdrawn", "cancelled")
        self.mw = None if r.get("capacity_mw") in (None, "") else float(r["capacity_mw"])
        self.counted = self.us and not self.cancelled
        self.first = x.get("first_story_at") or ""
        self.kind = x.get("kind") or "not stated"
        self.grid = x.get("grid") or GRID_OF_STATE.get(self.state.upper(), "")
        self.year = x.get("energized_year") or x.get("planned_year") or ""
        self.power = x.get("power_kind") or "none"


def add(d, k, v):
    d[k] = d.get(k, 0) + v


def quarter(day):
    return f"{day[:4]}-Q{(int(day[5:7]) - 1) // 3 + 1}"


def median3(xs):
    return statistics.median(xs) if len(xs) >= 3 else None


def facilities(rows, today):
    """The top block, the list's group lines, the sites beside ERCOT, the rollups, the timeline and the charts."""
    fs, out = [Fac(r) for r in rows], {}
    counted = [f for f in fs if f.counted]
    stating = [f for f in counted if f.mw is not None]
    out["datacenters|count"] = len(fs)
    out["datacenters|counted"] = len(counted)
    out["datacenters|no_us_state"] = sum(1 for f in fs if not f.us)
    out["datacenters|cancelled"] = sum(1 for f in fs if f.us and f.cancelled)
    out["datacenters|mw_total"] = sum(f.mw for f in stating)
    out["datacenters|n_with_mw"] = len(stating)
    for f in stating:
        add(out, f"datacenters|status_mw|{f.status}", f.mw)
        if f.state:
            add(out, f"datacenters|state_mw|{f.state}", f.mw)
    # the week: the seven UTC days that end on the day the page is drawn
    start = (datetime.date.fromisoformat(today) - datetime.timedelta(days=6)).isoformat()
    out[f"datacenters|first_week|{start}"] = sum(1 for f in fs if f.first and f.first[:10] >= start)
    out["datacenters|n_first_story"] = sum(1 for f in fs if f.first)
    # by operator: every row of the operator counted as a facility of the list; its MW only from the rows the sums count
    op_n, op_mw = {}, {}
    for f in fs:
        add(op_n, f.operator, 1)
        if f.counted and f.mw is not None:
            add(op_mw, f.operator, f.mw)
    for op, n in op_n.items():
        out[f"datacenters|operator_count|{op}"] = n
        if op in op_mw:
            out[f"datacenters|operator_mw|{op}"] = op_mw[op]
    # beside ERCOT's section: every site held, the cancelled and those with no US state among them
    out["datacenters|sites_us"] = sum(1 for f in fs if f.us)
    out["datacenters|sites_texas"] = sum(1 for f in fs if f.state == "TX")
    out["datacenters|sites_n_with_mw"] = sum(1 for f in fs if f.mw is not None)
    out["datacenters|sites_mw"] = sum(f.mw for f in fs if f.mw is not None)
    tx = [f for f in fs if f.state == "TX" and f.mw is not None]
    out["datacenters|texas_n_with_mw"] = len(tx)
    if tx:
        out["datacenters|texas_mw"] = sum(f.mw for f in tx)
    for f in fs:
        add(out, f"datacenters|kind_count|{f.kind}", 1)
    # the rollups by grid and by operator: a group is shown where it has a counted facility; no sum where none states MW
    for dim, of in (("grid", lambda f: f.grid), ("operator", lambda f: f.operator)):
        groups = {}
        for f in counted:
            groups.setdefault(of(f), []).append(f)
        for value, g in groups.items():
            v = value or "-"
            mws = [f.mw for f in g if f.mw is not None]
            out[f"datacenters|rollup_facilities|{dim}|{v}"] = len(g)
            if mws:
                out[f"datacenters|rollup_mw|{dim}|{v}"] = sum(mws)
            out[f"datacenters|rollup_with_mw|{dim}|{v}"] = len(mws)
            out[f"datacenters|rollup_without|{dim}|{v}"] = len(g) - len(mws)
    # the timeline: every facility held (counted or not) that states a first story and the year it is to be energized
    waits = []
    for f in fs:
        if len(f.first) >= 7 and f.first[:4].isdigit() and f.first[4] == "-" and f.first[5:7].isdigit() and str(f.year).isdigit() and int(f.year) >= 2000:
            waits.append((f.grid, f.first[:4], int(f.year) - int(f.first[:4])))
    out["dctime|rows"] = len(waits)
    for dim, pos in (("grid", 0), ("year", 1)):
        cells = {}
        for w in waits:
            cells.setdefault(w[pos], []).append(w[2])
        for value, ws in cells.items():
            out[f"dctime|count|{dim}|{value or '-'}"] = len(ws)
            m = median3(ws)
            if m is not None:
                out[f"dctime|median|{dim}|{value or '-'}"] = m
    # chart 1: planned and under construction, by the quarter first reported and the grid (the four largest, the rest other)
    ahead = [f for f in counted if f.status.lower() in ("planned", "under_construction")]
    by_grid = {}
    for f in ahead:
        if f.mw is not None and f.grid:
            add(by_grid, f.grid, f.mw)
    top = [g for g, _ in sorted(by_grid.items(), key=lambda kv: (-kv[1], kv[0]))[:4]]
    dated = [f for f in ahead if len(f.first) >= 7 and f.first[:4].isdigit() and f.first[5:7].isdigit()]
    for q in sorted({quarter(f.first) for f in dated}):
        in_q = [f for f in dated if quarter(f.first) == q]
        for g in top + ["other"]:
            out[f"dcchart|planned|{q}|{g}"] = sum(f.mw or 0 for f in in_q if (f.grid if f.grid in top else "other") == g)
        out[f"dcchart|planned|{q}|without"] = sum(1 for f in in_q if f.mw is None)
    # chart 2: the ten operators with the most MW stated (a named operator, of the rows the sums count)
    named = sorted(((op, mw) for op, mw in op_mw.items() if op), key=lambda kv: (-kv[1], -sum(1 for f in counted if f.operator == kv[0]), kv[0]))
    for op, mw in named[:10]:
        out[f"dcchart|operator|{op}|mw"] = mw
    # chart 3: the counted facilities by the kind of power stated, and each kind's share to a tenth of a percent
    kinds = {}
    for f in counted:
        add(kinds, f.power, 1)
    for k, n in kinds.items():
        out[f"dcchart|power|{k}|facilities"] = n
        out[f"dcchart|power|{k}|pct"] = round(1000 * n / len(counted)) / 10 if counted else 0
    # the facilities against each grid: counted facilities with a grid, MW by stage, the share of the grid's peak hour
    for g in GRIDS:
        mine = [f for f in counted if f.grid == g]
        if not mine:
            continue
        out[f"dcgrid|facilities|{g}"] = len(mine)
        out[f"dcgrid|with_mw|{g}"] = sum(1 for f in mine if f.mw is not None)
        for stage in ("planned", "under_construction", "operating"):
            mws = [f.mw for f in mine if f.mw is not None and f.status.lower() == stage]
            if mws:
                out[f"dcgrid|{stage}|{g}"] = sum(mws)
    return out


def js_round(x):
    """Round half up, as the page rounds a positive figure."""
    return int(x + 0.5)


def grid_side(out, headroom):
    """The grids' own figures (the site's copy of grid_peak_vs_capacity and ERCOT's reserve margin), and the share of peak."""
    for g, gid in GRIDS.items():
        pc = (headroom.get("peak_capacity") or {}).get(gid)
        rm = ((headroom.get("reserve") or {}).get("grids") or {}).get(gid)
        if pc:
            out[f"dcgrid|peak_mw|{g}"] = pc["peak_mw"]
            out[f"dcgrid|capacity_mw|{g}"] = pc["capacity_mw"]
            p, u = out.get(f"dcgrid|planned|{g}"), out.get(f"dcgrid|under_construction|{g}")
            if pc["peak_mw"] and (p is not None or u is not None):
                out[f"dcgrid|share_of_peak|{g}"] = js_round(1000 * ((p or 0) + (u or 0)) / pc["peak_mw"]) / 10
        if rm:
            out[f"dcgrid|reserve_margin|{g}"] = rm["peak"]["pct"]


def ercot(series, site_copy):
    """ERCOT's large loads: each figure a report states, from the live set's series rows; the summary's share."""
    out = {}
    for r in series:
        if r["variable"] in SERIES:
            out[f"series|{r['table_name']}|{r['entity']}|{r['variable']}|{r['ts_utc'][:10]}T00:00:00Z"] = float(r["value"])
    days = sorted({r["ts_utc"][:10] for r in series})
    val = lambda day, var: next((float(r["value"]) for r in series if r["ts_utc"][:10] == day and r["variable"] == var), None)
    whole = [d for d in days if all(val(d, v) is not None for v in ("approved_to_energize_mw", "observed_nonsimultaneous_peak_mw", "observed_simultaneous_peak_mw"))]
    out["ercot|reports"] = len(days)
    if whole:
        last = whole[-1]
        out["ercot|observed_share_pct"] = js_round(100 * val(last, "observed_nonsimultaneous_peak_mw") / val(last, "approved_to_energize_mw"))
    out["ercot|impossible_reports"] = sum(1 for d in whole if val(d, "observed_simultaneous_peak_mw") > val(d, "observed_nonsimultaneous_peak_mw"))
    # the month as ERCOT wrote it is on the site's copy only (x_month_as_written is not in the live set's series rows)
    months = "January February March April May June July August September October November December".split()
    odd = 0
    for rep in site_copy.get("reports", []):
        w = (rep.get("month_as_written") or "").split(" ")
        if len(w) == 2 and w[0] in months and not (w[1] == rep["day"][:4] and months.index(w[0]) + 1 == int(rep["day"][5:7])):
            odd += 1
    out["ercot|month_mismatch_reports"] = odd
    return out


def queues(sites, active):
    """The queue positions that name a datacenter or a large load, by grid and the zone the queue states."""
    out, groups = {}, {}
    grid_of = lambda r: r["table_name"].replace("_interconnection_queue", "")
    zone_of = lambda r: ((r.get("zone") if "zone" in r else (r.get("extra") or {}).get("zone")) or "").strip() or "-"
    num = lambda r: None if r.get("capacity_mw") in (None, "") else float(r["capacity_mw"])
    for r in sites:
        if num(r) is not None:
            out[f"entity|{r['table_name']}|{r['entity_id']}|capacity_mw"] = num(r)
        groups.setdefault((grid_of(r), zone_of(r)), []).append(r)
    for (grid, zone), rs in groups.items():
        k = f"dcq|{grid}|{zone}|"
        mws = [num(r) for r in rs if num(r) is not None]
        out[k + "sites"], out[k + "sites_with_mw"], out[k + "mw_asked"] = len(rs), len(mws), sum(mws)
        mine = [a for a in active if grid_of(a) == grid and (zone == "-" or zone_of(a) == zone)]
        out[k + "active_positions"] = len(mine)
        out[k + "active_mw"] = sum(num(a) for a in mine if num(a) is not None)
    return out, sorted({g for g, _ in groups})


def month_bounds(year):
    leap = (year % 4 == 0 and year % 100 != 0) or year % 400 == 0
    days = [31, 29 if leap else 28, 31, 30, 31, 30, 31, 31, 30, 31, 30, 31]
    out = [0]
    for d in days:
        out.append(out[-1] + 24 * d)
    return out


def flat_prices(grid):
    """What a flat load paid at each load zone of a grid: the mean of the hourly prices held, over the last twelve
    consecutive complete months (real time where twelve such months are held, else day-ahead), and by complete year."""
    out = {}
    folder = os.path.join(SITE, "data", "datacenter")
    index = load(os.path.join(folder, "index.json"))["grids"].get(grid)
    if not index:
        return out
    files = {y: load(os.path.join(folder, f"{grid}_{y}.json")) for y in index["years"]}
    per_region = {}
    for region in index["regions"]:
        if region.get("kind") and region["kind"] != "zone":
            continue
        for market in ("rt", "da"):
            if not region.get(market):
                continue
            months = {}   # "YYYY-MM": (sum of prices, hours held, hours due)
            for y in sorted(files):
                s = (files[y]["regions"].get(region["id"]) or {}).get(market)
                prices = [None] * files[y]["hours"]
                if s:
                    prices[s["s"]: s["s"] + len(s["v"])] = s["v"]
                b = month_bounds(y)
                for m in range(12):
                    held = [v for v in prices[b[m]: b[m + 1]] if v is not None]
                    if held:
                        months[f"{y}-{m + 1:02d}"] = (sum(held), len(held), b[m + 1] - b[m])
            complete = {m for m, (_, held, due) in months.items() if held >= NEAR * due}
            twelve = None
            for m in sorted(complete, reverse=True):
                y, mo = int(m[:4]), int(m[5:7])
                run = [f"{y + (mo - 1 - k) // 12}-{(mo - 1 - k) % 12 + 1:02d}" for k in range(12)]
                if all(x in complete for x in run):
                    twelve = run
                    break
            if not twelve:
                continue
            per_region[region["id"]] = {"per": sum(months[m][0] for m in twelve) / sum(months[m][1] for m in twelve), "years": {}}
            for y in sorted(files):
                ms = [f"{y}-{k:02d}" for k in range(1, 13)]
                if all(m in complete for m in ms):
                    per_region[region["id"]]["years"][str(y)] = sum(months[m][0] for m in ms) / sum(months[m][1] for m in ms)
            break
    years = sorted({y for r in per_region.values() for y in r["years"]})[-8:]   # the view by grid shows at most the last eight
    for rid, r in per_region.items():
        out[f"dcpow|{grid}|{rid}|per"] = r["per"]
        for y, v in r["years"].items():
            if y in years:
                out[f"dcpow|{grid}|{rid}|year|{y}"] = v
    return out


def tolerance(key):
    """Half the last digit the page shows for the figure."""
    if key.startswith("dcpow|"):
        return 0.005                                   # two decimals, USD per MWh
    if key.startswith("dcgrid|share_of_peak|") or key.startswith("dcgrid|reserve_margin|") or (key.startswith("dcchart|power|") and key.endswith("|pct")):
        return 0.05                                    # one decimal
    if key.startswith("dcq|") and key.endswith("|mw_asked") or key.startswith("entity|"):
        return 0.005                                   # as the queue states it, to two decimals
    if key.startswith("dctime|median|"):
        return 0.05                                    # a median of whole years: whole or a half
    return 0.5                                         # a count or a figure shown whole


def page_figures(rows_dir, today, page_file):
    if page_file:
        return load(page_file)
    node = shutil.which("node")
    if not node:
        raise OSError("node is not installed: pass --page with the JSON site/scripts/datacenter-tracker-figures.mjs prints")
    got = subprocess.run([node, os.path.join("scripts", "datacenter-tracker-figures.mjs"), rows_dir, today], cwd=SITE, capture_output=True, text=True, timeout=300)
    if got.returncode != 0:
        raise OSError("the page's functions did not run: " + got.stderr.strip()[-400:])
    return json.loads(got.stdout)


def headline(rows_dir):
    """The do-file's five lines (replicate.do), step for step on the same two CSVs: the mirror a reader without Stata runs."""
    def table(name):
        with open(os.path.join(rows_dir, name), encoding="utf-8", newline="") as f:
            return list(csv.DictReader(line for line in f if not line.startswith("#")))
    fac, n_counted, mws = table("facilities_slim.csv"), 0, []
    for r in fac:
        us = r["country"] == "US" or (r["country"] == "" and r["state"] in US)
        if us and r["status"].lower() not in ("withdrawn", "cancelled"):
            n_counted += 1
            if r["capacity_mw"] != "":
                mws.append(float(r["capacity_mw"]))
    approved = sorted((r["day"], float(r["value"])) for r in table("ercot_large_load.csv") if r["variable"] == "approved_to_energize_mw")
    return [("1. facilities held", len(fac), ""), ("2. counted in the sums (a named US state, not cancelled)", n_counted, ""),
            ("3. megawatts stated by the counted facilities", sum(mws), ""), ("4. counted facilities that state megawatts", len(mws), ""),
            ("5. ERCOT, megawatts approved to energize, newest report", approved[-1][1], f" ({approved[-1][0]})")]


def name_of(key):
    p = key.split("|")
    if p[0] == "series":
        return f"ERCOT {p[3]}, report of {p[4][:10]}"
    return key


def main(argv):
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    ap.add_argument("--rows", default=os.path.join(HERE, "rows"))
    ap.add_argument("--page")
    ap.add_argument("--today")
    ap.add_argument("--write", action="store_true")
    ap.add_argument("--headline", action="store_true", help="only the do-file's five lines, from the two CSVs it reads")
    a = ap.parse_args(argv[1:])
    if a.headline:
        try:
            for words, value, more in headline(os.path.abspath(a.rows)):
                print(f"{words}{more}: {round(value):,}")
        except (OSError, ValueError, KeyError, IndexError) as exc:
            print(f"the inputs could not be read: {exc}")
            return 2
        return 0
    try:
        rows_dir = os.path.abspath(a.rows)
        stamp = load(os.path.join(rows_dir, "retrieved.json"))
        today = a.today or stamp["retrieved_at"][:10]
        rows = load(os.path.join(rows_dir, "datacenter_facilities.json"))
        mine = facilities(rows, today)
        grid_side(mine, load(os.path.join(SITE, "data", "siting", "headroom.json")))
        mine.update(ercot(load(os.path.join(rows_dir, "ercot_large_load_status.json")), load(os.path.join(SITE, "data", "large_load_status.json"))))
        q, grids = queues(load(os.path.join(rows_dir, "queue_sites.json")), load(os.path.join(rows_dir, "queue_active.json")))
        mine.update(q)
        for g in grids:
            mine.update(flat_prices(g))
        page = page_figures(rows_dir, today, a.page)
    except (OSError, ValueError, KeyError) as exc:
        print(f"the inputs could not be read: {exc}")
        return 2
    shown = page["figures"]
    lines, bad = [], 0
    for key in sorted(set(mine) | set(shown)):
        got, want = mine.get(key), shown.get(key)
        if got is None or want is None:
            lines.append((key, got, want, None, False, "page only" if got is None else "replication only"))
            bad += 1
            continue
        diff = float(got) - float(want)
        ok = abs(diff) <= tolerance(key) + 1e-9
        bad += 0 if ok else 1
        lines.append((key, got, want, diff, ok, ""))
    print(f"The datacenter tracker, {len(rows)} rows of datacenter_facilities as the live set served them at {stamp['retrieved_at']} "
          f"(vintage {stamp.get('vintage', '')}); the page drawn on {today}")
    print("figure | replication | the page's functions | difference | inside the tolerance")
    for key, got, want, diff, ok, why in lines:
        f = lambda v: "none" if v is None else (f"{v:,.4f}" if isinstance(v, float) and not float(v).is_integer() else f"{int(v):,}")
        print(f"{name_of(key)} | {f(got)} | {f(want)} | {'' if diff is None else f'{diff:+.4f}'} | {'yes' if ok else 'NO ' + why}")
    print(f"{len(lines) - bad} of {len(lines)} inside the tolerance")
    print("not replicated here: the words of the list (each facility's own row), which are the table's rows themselves")
    if a.write:
        figures = [{"key": k, "page": w, "replication": g, "tolerance": tolerance(k)} for k, g, w, _, _, _ in lines]
        with open(os.path.join(HERE, "page_figures.json"), "w", encoding="utf-8", newline="\n") as f:
            json.dump({"tool": "/datacenters", "retrieved_at": stamp["retrieved_at"], "vintage": stamp.get("vintage", ""), "today": today,
                       "rows": len(rows), "source": stamp["source"],
                       "note": "the page's figure is what its own functions compute on the live set's rows (site/scripts/datacenter-tracker-figures.mjs); "
                               "the facilities are held (license needed), so the built page draws none of them to a visitor",
                       "figures": figures}, f, indent=1)
            f.write("\n")
        with open(os.path.join(HERE, "page_figures.csv"), "w", encoding="utf-8", newline="") as f:
            f.write(f"# ERW, the datacenter tracker: every figure of the page on the live set's rows of {stamp['retrieved_at']} (replication/datacenter_tracker/replicate.py --write)\n")
            w = csv.writer(f, lineterminator="\n")
            w.writerow(["key", "page", "replication", "tolerance"])
            for x in figures:
                w.writerow([x["key"], x["page"], x["replication"], x["tolerance"]])
    return 0 if not bad else 1


if __name__ == "__main__":
    sys.exit(main(sys.argv))

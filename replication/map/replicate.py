#!/usr/bin/env python3
"""ERW, the project map (/map, the Projects tab): the replication a reader can run (session 7601, chain 305).

Written from the method note (docs/methods/map.md) and the public rows alone, not from the page's code: every figure
the tab draws is computed again here, in this file's own words, and set beside the figure the page's own functions give
on the page's own file (site/scripts/map-figures.mjs, run with node, or a file of its output). The generating units are
read from EIA's own workbook, not from an ERW table: the comparison is between the page and its publisher.

    python replication/map/fetch_rows.py         # the rows, into rows/ (not in git): EIA's workbook, the live set's queue and datacenters
    python replication/map/replicate.py          # the tally
    python replication/map/replicate.py --write  # also writes page_figures.json and page_figures.csv
    python replication/map/replicate.py --headline   # the five headline figures, as replicate.do prints them

    --rows DIR      another folder of rows (default: this folder's rows/)
    --page FILE     the page's figures as a file (the JSON the node script writes) instead of running node

A figure is inside the tolerance when it is at most half the last digit the page shows (a whole megawatt or a whole
row: 0.5). The page's file and the rows can be of different days: the units are EIA's month, which the workbook's own
title names and this file checks; the queue positions and the datacenters are the ERW's tables as the live set holds
them on the day of the fetch, and the page's copy as it was built. A figure that differs for that reason alone is
named as such (its key, both sides, and the rows that differ), never passed over.

Exit 0 when every figure of the generating units is inside its tolerance and every other difference is named; 1 when
a figure of the units is outside, or a key is on one side only; 2 when the inputs cannot be read. Standard library only.
"""
import argparse
import csv
import json
import math
import os
import shutil
import subprocess
import sys
import urllib.parse

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(os.path.dirname(HERE))
SITE = os.path.join(ROOT, "site")
PAGE_FILE = os.path.join(SITE, "data", "map.json")

# The note, section 3: the four kinds, in the page's order.
KINDS = ["operating", "planned", "queue", "datacenter"]
# The note, section 4: a unit's grid is EIA's balancing authority code; the seven ISOs are named, every other code and a blank one are "outside".
GRID_OF_BA = {"ERCO": "ercot", "CISO": "caiso", "PJM": "pjm", "MISO": "miso", "SWPP": "spp", "NYIS": "nyiso", "ISNE": "isone"}
GRIDS = ["ercot", "caiso", "pjm", "miso", "spp", "nyiso", "isone", "outside", "none"]
# The note, section 5: EIA's technology, grouped (the table of the note, word for word).
TECH_GROUP = {
    "Solar Photovoltaic": "solar", "Solar Thermal with Energy Storage": "solar", "Solar Thermal without Energy Storage": "solar",
    "Onshore Wind Turbine": "wind", "Offshore Wind Turbine": "wind",
    "Batteries": "storage", "Flywheels": "storage", "Hydroelectric Pumped Storage": "storage", "Natural Gas with Compressed Air Storage": "storage",
    "Natural Gas Fired Combined Cycle": "natural_gas", "Natural Gas Fired Combustion Turbine": "natural_gas", "Natural Gas Internal Combustion Engine": "natural_gas",
    "Natural Gas Steam Turbine": "natural_gas", "Other Natural Gas": "natural_gas",
    "Conventional Steam Coal": "coal", "Coal Integrated Gasification Combined Cycle": "coal", "Nuclear": "nuclear", "Conventional Hydroelectric": "hydro",
    "Geothermal": "geothermal", "Petroleum Liquids": "petroleum", "Petroleum Coke": "petroleum",
    "Wood/Wood Waste Biomass": "biomass", "Landfill Gas": "biomass", "Municipal Solid Waste": "biomass", "Other Waste Biomass": "biomass",
    "Other Gases": "other", "All Other": "other",
}
TECHS = ["solar", "wind", "battery", "storage", "natural_gas", "nuclear", "coal", "hydro", "petroleum", "biomass", "geothermal", "other", "queue_storage", "hybrid",
         "transmission", "datacenter", "unknown"]
# The note, section 6: the queues whose positions may be drawn (the others are held back: MISO's and NYISO's).
QUEUES_SHOWN = {"ercot", "spp", "caiso", "isone"}
FILTERS = ["kind", "grid", "tech", "status", "state"]


class Row:
    __slots__ = ("id", "kind", "grid", "tech", "status", "state", "tenths", "lat", "lon")

    def __init__(self, id_, kind, grid, tech, status, state, mw, lat, lon):
        self.id, self.kind, self.grid, self.tech, self.status, self.state = id_, kind, grid, tech, status, state
        # the page's copy keeps a megawatt figure to one decimal (the note, section 7): tenths, as a whole number
        self.tenths = None if mw is None else tenths(mw)
        self.lat, self.lon = lat, lon


def tenths(v):
    """A figure rounded to one decimal as the file's builder rounds it (Python's round on the figure as a float)."""
    return int(round(round(float(v), 1) * 10))


def number(text):
    t = (text or "").strip()
    try:
        return float(t)
    except ValueError:
        return None


def read_units(rows):
    """The generating units of EIA's workbook (rows/units.csv), each as the note's sections 3 to 7 read it."""
    out = []
    with open(os.path.join(rows, "units.csv"), encoding="utf-8", newline="") as f:
        lines = [ln for ln in f if not ln.startswith("#")]
    for r in csv.DictReader(lines):
        kind = r["kind"]
        group = TECH_GROUP.get(r["technology"], "") if r["technology"] else ""
        if r["technology"] and not group:
            raise ValueError(f"EIA technology the note's table does not hold: {r['technology']!r}")
        tech = "battery" if group == "storage" and r["prime_mover"] == "BA" else (group or "unknown")
        code = r["status"].split(")")[0].lstrip("(") if r["status"].startswith("(") else ""
        status = "operating" if kind == "operating" else code.lower()
        mw = number(r["nameplate_mw"])
        if mw is None:
            raise ValueError(f"a unit of the workbook states no nameplate MW: {r['plant_id']}:{r['generator_id']}")
        lat, lon = number(r["latitude"]), number(r["longitude"])
        out.append(Row(f"{r['plant_id']}:{r['generator_id']}", kind, GRID_OF_BA.get(r["balancing_authority"], "outside"), tech, status, r["plant_state"], mw,
                       None if lat is None or lon is None else round(lat, 4), None if lat is None or lon is None else round(lon, 4)))
    return out


def read_queue(rows):
    """The queue positions the map draws (the note, section 6): not withdrawn, of a queue that may be shown."""
    with open(os.path.join(rows, "queue.json"), encoding="utf-8") as f:
        data = json.load(f)
    out, withdrawn = [], 0
    for r in data:
        x = r.get("extra") or {}
        grid = (x.get("source_table") or "").replace("_interconnection_queue", "")
        if (r.get("status") or "") == "withdrawn":
            withdrawn += 1
            continue
        if grid not in QUEUES_SHOWN:
            continue
        group = x.get("technology_group") or ""
        tech = "queue_storage" if group == "storage" else (group or "unknown")
        mw = r.get("capacity_mw")
        lat, lon = r.get("lat"), r.get("lon")
        out.append(Row(r["entity_id"], "queue", grid, tech, "q-" + (r.get("status") or "none"), x.get("state") or "", mw,
                       None if lat is None or lon is None else round(float(lat), 4), None if lat is None or lon is None else round(float(lon), 4)))
    return out, withdrawn, max((r.get("vintage") or "" for r in data), default="")


def read_datacenters(rows):
    """The datacenters the map draws (the note, section 6): the facilities the tracker places in a US state."""
    with open(os.path.join(rows, "datacenter_facilities.json"), encoding="utf-8") as f:
        data = json.load(f)
    out, stateless = [], 0
    for r in data:
        x = r.get("extra") or {}
        state = x.get("state") or ""
        if not state:
            stateless += 1
            continue
        lat, lon = r.get("lat"), r.get("lon")
        out.append(Row(r["entity_id"], "datacenter", "none", "datacenter", "dc-" + (r.get("status") or "none"), state, r.get("capacity_mw"),
                       None if lat is None or lon is None else round(float(lat), 4), None if lat is None or lon is None else round(float(lon), 4)))
    return out, stateless, max((r.get("vintage") or "" for r in data), default="")


# ---------------------------------------------------------------------------------------------------------------------
# The drawing's plane (the note, section 9): the Albers projection of the United States that the state outlines are
# drawn with (us-atlas: scale 1300, translated to 487.5, 305): the lower 48 in one conic equal-area projection, Alaska
# and Hawaii each in its own, in a box at the lower left. A place outside the three boxes has no place on the drawing.
# ---------------------------------------------------------------------------------------------------------------------
def conic(lat0, lat1):
    s0 = math.sin(math.radians(lat0))
    n = (s0 + math.sin(math.radians(lat1))) / 2
    c = 1 + s0 * (2 * n - s0)
    r0 = math.sqrt(c) / n

    def raw(lam, phi):
        r = math.sqrt(c - 2 * n * math.sin(phi)) / n
        return r * math.sin(lam * n), r0 - r * math.cos(lam * n)
    return raw


def part(parallels, rotate, center, k, tx, ty):
    raw = conic(*parallels)
    cx, cy = raw(math.radians(center[0]), math.radians(center[1]))

    def project(lon, lat):
        lam = math.radians(lon + rotate)
        lam = (lam + math.pi) % (2 * math.pi) - math.pi
        x, y = raw(lam, math.radians(lat))
        return tx + k * (x - cx), ty - k * (y - cy)
    return project


K, TX, TY, EPS = 1300.0, 487.5, 305.0, 1e-6
LOWER48 = (part((29.5, 45.5), 96, (-0.6, 38.7), K, TX, TY), (TX - 0.455 * K, TY - 0.238 * K, TX + 0.455 * K, TY + 0.238 * K))
ALASKA = (part((55, 65), 154, (-2, 58.5), K * 0.35, TX - 0.307 * K, TY + 0.201 * K), (TX - 0.425 * K + EPS, TY + 0.120 * K + EPS, TX - 0.214 * K - EPS, TY + 0.234 * K - EPS))
HAWAII = (part((8, 18), 157, (-3, 19.9), K, TX - 0.205 * K, TY + 0.212 * K), (TX - 0.214 * K + EPS, TY + 0.166 * K + EPS, TX - 0.115 * K - EPS, TY + 0.234 * K - EPS))


def on_drawing(lat, lon):
    if lat is None or lon is None:
        return False
    for project, (x0, y0, x1, y1) in (LOWER48, ALASKA, HAWAII):
        x, y = project(lon, lat)
        if x0 <= x <= x1 and y0 <= y <= y1:
            return True
    return False


# ---------------------------------------------------------------------------------------------------------------------
# A view, its rows and its figures (the note, sections 8 and 10)
# ---------------------------------------------------------------------------------------------------------------------
def choice_of(view, options):
    """The address as the note reads it: a list of slugs with commas; absent or empty is every one; "none" is none; a
    slug the page does not know is passed over (and a list of none known is every one); a size is a number at or above 0."""
    q = urllib.parse.parse_qs(view.lstrip("?"), keep_blank_values=True)
    c = {}
    for which in FILTERS:
        v = (q.get(which, [""])[0]).strip()
        if not v:
            c[which] = None
        elif v == "none":
            c[which] = set()
        else:
            found = {s.strip() for s in v.split(",") if s.strip() in options[which]}
            c[which] = found if found and found != set(options[which]) else None
    for edge in ("min", "max"):
        t = (q.get(edge, [""])[0]).strip().replace(",", "")
        ok = t.replace(".", "", 1).isdigit() and not t.startswith(".") and not t.endswith(".")
        c[edge] = float(t) if ok else None
    return c


def picked(rows, c):
    sized = c["min"] is not None or c["max"] is not None
    out = []
    for r in rows:
        if c["kind"] is not None and r.kind not in c["kind"]:
            continue
        if c["grid"] is not None and r.grid not in c["grid"]:
            continue
        if c["tech"] is not None and r.tech not in c["tech"]:
            continue
        if c["status"] is not None and r.status not in c["status"]:
            continue
        if c["state"] is not None and (r.state or "na") not in c["state"]:
            continue
        if sized:                                           # a row with no MW cannot be said to fit a size
            if r.tenths is None or (c["min"] is not None and r.tenths < c["min"] * 10 - 1e-9) or (c["max"] is not None and r.tenths > c["max"] * 10 + 1e-9):
                continue
        out.append(r)
    return out


def figures_of(view, rows, options, status_order):
    c = choice_of(view, options)
    chosen = picked(rows, c)
    name = view or "(no choice)"
    out = {}
    by_kind = {k: [r for r in chosen if r.kind == k] for k in KINDS}
    mw = lambda rs: sum(r.tenths for r in rs if r.tenths is not None) / 10   # noqa: E731
    with_mw = lambda rs: sum(1 for r in rs if r.tenths is not None)          # noqa: E731
    out[f"{name}|rows"] = len(chosen)
    out[f"{name}|units"] = len(by_kind["operating"]) + len(by_kind["planned"])
    out[f"{name}|units_mw"] = mw(by_kind["operating"] + by_kind["planned"])
    out[f"{name}|queue"] = len(by_kind["queue"])
    out[f"{name}|queue_mw"] = mw(by_kind["queue"])
    out[f"{name}|datacenters"] = len(by_kind["datacenter"])
    out[f"{name}|datacenters_mw"] = mw(by_kind["datacenter"])
    out[f"{name}|datacenters_with_mw"] = with_mw(by_kind["datacenter"])
    for s in status_order:
        rs = [r for r in chosen if r.status == s]
        if not rs:
            continue
        out[f"{name}|status|{s}|rows"] = len(rs)
        out[f"{name}|status|{s}|with_mw"] = with_mw(rs)
        if with_mw(rs):
            out[f"{name}|status|{s}|mw"] = mw(rs)
    for t in TECHS:
        if t == "datacenter":
            continue
        for k in ("operating", "planned", "queue"):
            if c["kind"] is not None and k not in c["kind"]:
                continue
            rs = [r for r in by_kind[k] if r.tech == t]
            if rs:
                out[f"{name}|tech|{t}|{k}|rows"] = len(rs)
                out[f"{name}|tech|{t}|{k}|mw"] = mw(rs)
    drawn = sum(1 for r in chosen if on_drawing(r.lat, r.lon))
    out[f"{name}|drawn"] = drawn
    out[f"{name}|not_drawn"] = len(chosen) - drawn
    return out, chosen


def page_figures(path):
    if path:
        with open(path, encoding="utf-8") as f:
            return json.load(f)
    node = shutil.which("node")
    if not node:
        raise RuntimeError("node is not installed: give the page's figures with --page FILE")
    r = subprocess.run([node, "--no-warnings", "scripts/map-figures.mjs"], cwd=SITE, capture_output=True, text=True, encoding="utf-8", timeout=600)
    if r.returncode != 0:
        raise RuntimeError("site/scripts/map-figures.mjs: " + r.stderr[-800:])
    return json.loads(r.stdout)


def page_rows():
    """The page's own file, row by row, for the comparison of a row's own fields (what a hover and a card show)."""
    with open(PAGE_FILE, encoding="utf-8") as f:
        m = json.load(f)
    out = {}
    for i in range(len(m["k"])):
        out[m["id"][i]] = (KINDS[m["k"][i]], m["grids"][m["g"][i]]["slug"], m["techs"][m["t"][i]]["slug"], m["statuses"][m["st"][i]]["slug"], m["states"][m["s"][i]],
                           None if m["mw"][i] is None else int(round(m["mw"][i] * 10)), m["la"][i], m["lo"][i])
    return m, out


def uses(key, kinds_changed):
    """Whether a figure can move with a kind's rows: its own name says which kinds it sums."""
    what = key.split("|", 1)[1]
    if what.startswith("units") or what.startswith("status|operating") or (what.startswith("status|") and not what.startswith(("status|q-", "status|dc-"))):
        return False
    if what.startswith("tech|") and not what.endswith(("|queue|rows", "|queue|mw")):
        return False
    return True


def main(argv):
    ap = argparse.ArgumentParser()
    ap.add_argument("--rows", default=os.path.join(HERE, "rows"))
    ap.add_argument("--page")
    ap.add_argument("--write", action="store_true")
    ap.add_argument("--headline", action="store_true")
    a = ap.parse_args(argv)
    try:
        units = read_units(a.rows)
        queue, withdrawn, queue_vintage = read_queue(a.rows)
        dcs, stateless, dc_vintage = read_datacenters(a.rows)
        with open(os.path.join(a.rows, "retrieved.json"), encoding="utf-8") as f:
            got = json.load(f)
    except (OSError, ValueError, KeyError) as e:
        print(f"the rows cannot be read ({type(e).__name__}: {e}); run fetch_rows.py first", file=sys.stderr)
        return 2
    if a.headline:
        op = [r for r in units if r.kind == "operating"]
        pl = [r for r in units if r.kind == "planned"]
        print(f"1. operating units: {len(op):,}")
        print(f"2. operating units, nameplate megawatts (each to one decimal, summed): {sum(r.tenths for r in op) / 10:,.1f}")
        print(f"3. planned units: {len(pl):,}")
        print(f"4. planned units, nameplate megawatts: {sum(r.tenths for r in pl) / 10:,.1f}")
        print(f"5. batteries (storage units whose prime mover is BA), operating and planned: {sum(1 for r in units if r.tech == 'battery'):,}")
        return 0
    try:
        page = page_figures(a.page)
        m, own = page_rows()
    except (OSError, RuntimeError, ValueError) as e:
        print(f"the page's figures cannot be read ({e})", file=sys.stderr)
        return 2

    # the month: the workbook's own title names it, and the page's file must name the same
    title = got.get("units", {}).get("titles", {}).get("Operating", "")
    month_ok = m["vintage"] in title.replace("September", "09") or _month_of(title) == m["vintage"]

    rows = units + queue + dcs
    options = {"kind": KINDS, "grid": GRIDS, "tech": TECHS, "status": [s["slug"] for s in m["statuses"]], "state": [(s or "na") for s in m["states"]]}
    views = sorted({f["key"].split("|", 1)[0] for f in page["figures"] if not f["key"].startswith("file|")})
    mine = {}
    for v in views:
        figs, _ = figures_of("" if v == "(no choice)" else v, rows, options, options["status"])
        mine.update(figs)
    # the file's own counts (the note, section 11)
    op = [r for r in units if r.kind == "operating"]
    pl = [r for r in units if r.kind == "planned"]
    mwsum = lambda rs: sum(r.tenths for r in rs if r.tenths is not None) / 10   # noqa: E731
    # the note, section 4: a unit with no balancing authority is one whose cell EIA leaves blank or fills with "NA"
    with open(os.path.join(a.rows, "units.csv"), encoding="utf-8", newline="") as f:
        codes = [r["balancing_authority"] for r in csv.DictReader(ln for ln in f if not ln.startswith("#"))]
    no_ba = sum(1 for c in codes if c in ("", "NA"))
    ba_note = {"blank": sum(1 for c in codes if c == ""), "NA": sum(1 for c in codes if c == "NA")}
    mine.update({
        "file|counts|rows": len(rows), "file|counts|operating": len(op), "file|counts|planned": len(pl), "file|counts|queue": len(queue), "file|counts|datacenter": len(dcs),
        "file|counts|operating_mw": mwsum(op), "file|counts|planned_mw": mwsum(pl), "file|counts|queue_mw": mwsum(queue), "file|counts|datacenter_mw": mwsum(dcs),
        "file|counts|units": len(units), "file|counts|units_mw": mwsum(units), "file|counts|batteries": sum(1 for r in rows if r.tech == "battery"),
        "file|counts|under_1_mw": sum(1 for r in units if r.tenths < 10), "file|counts|without_balancing_authority": no_ba,
        "file|counts|without_mw": sum(1 for r in rows if r.tenths is None), "file|counts|not_placed": sum(1 for r in rows if r.lat is None),
        "file|counts|datacenters_without_state": stateless, "file|counts|queue_rows_held": 0,
    })

    # which kinds' rows differ between the page's copy and the rows read today (a different day's table)
    mine_by_id = {("eia860:" if r.kind in ("operating", "planned") else "") + r.id: r for r in rows}
    page_ids = {("eia860:" if v[0] in ("operating", "planned") else "") + k: v for k, v in own.items()}
    kinds_changed, row_notes, fields_same, fields_all = set(), [], 0, 0
    for kind in KINDS:
        a_ids = {i for i, r in mine_by_id.items() if r.kind == kind}
        b_ids = {i for i, v in page_ids.items() if v[0] == kind}
        both = a_ids & b_ids
        differ = 0
        for i in both:
            r, v = mine_by_id[i], page_ids[i]
            fields_all += 1
            same = (r.grid, r.tech, r.status, r.state, r.tenths, r.lat, r.lon) == (v[1], v[2], v[3], v[4], v[5], v[6], v[7])
            fields_same += same
            differ += not same
        if a_ids != b_ids or differ:
            kinds_changed.add(kind)
        row_notes.append({"kind": kind, "rows_read": len(a_ids), "rows_on_the_page": len(b_ids), "in_both": len(both), "only_in_the_rows_read": len(a_ids - b_ids),
                          "only_on_the_page": len(b_ids - a_ids), "in_both_with_a_field_that_differs": differ})

    figs, outside, named, one_side = [], [], [], []
    keys = {f["key"] for f in page["figures"]}
    for f in page["figures"]:
        k = f["key"]
        if k not in mine:
            mine_v = 0 if "|status|" in k or "|tech|" in k else None      # a status or a technology with no row read today
            if mine_v is None:
                one_side.append(k)
                continue
        else:
            mine_v = mine[k]
        inside = abs(f["page"] - mine_v) <= f["tolerance"] + 1e-9
        rec = {"key": k, "page": f["page"], "replication": round(mine_v, 1) if isinstance(mine_v, float) else mine_v, "tolerance": f["tolerance"], "inside": inside}
        if not inside:
            touches = k.startswith("file|counts|") and any(w in k for w in ("queue", "datacenter", "rows", "without_mw", "not_placed")) or (not k.startswith("file|") and uses(k, kinds_changed))
            if touches and (kinds_changed & {"queue", "datacenter"}):
                rec["named"] = "the queue's or the tracker's rows are of another day in the page's copy"
                named.append(rec)
            else:
                outside.append(rec)
        figs.append(rec)
    for k in mine:
        if k not in keys and not k.startswith("file|"):
            v = mine[k]
            if v:
                rec = {"key": k, "page": 0, "replication": v, "tolerance": 0.5, "inside": False, "named": "a status or a technology the rows read today hold and the page's copy does not"}
                (named if uses(k, kinds_changed) and (kinds_changed & {"queue", "datacenter"}) else one_side).append(rec if isinstance(rec, dict) and uses(k, kinds_changed) else k)
    n = len(figs)
    ok = sum(1 for f in figs if f["inside"])
    units_figs = [f for f in figs if not (f["key"].startswith("file|") and any(w in f["key"] for w in ("queue", "datacenter", "rows", "without_mw", "not_placed"))) and (f["key"].startswith("file|") or not uses(f["key"], {"queue", "datacenter"}))]
    units_ok = sum(1 for f in units_figs if f["inside"])
    print(f"the month: the workbook says \"{title}\"; the page's file says {m['vintage']}: {'the same' if month_ok else 'NOT the same'}")
    print(f"the rows read: {len(units):,} units of EIA's workbook; {len(queue):,} queue positions not withdrawn of four queues (vintage {queue_vintage}); {len(dcs):,} datacenters in a US state (vintage {dc_vintage}; {stateless} in none)")
    print(f"the page's copy: built {m['built'][:10]}; queue vintage {m['vintages'].get('queue')}; datacenter vintage {m['vintages'].get('datacenter')}")
    for r in row_notes:
        print(f"  {r['kind']}: {r['rows_read']:,} rows read, {r['rows_on_the_page']:,} on the page, {r['in_both']:,} in both ({r['in_both_with_a_field_that_differs']} with a field that differs), {r['only_in_the_rows_read']} only in the rows read, {r['only_on_the_page']} only on the page")
    print(f"a row's own fields (grid, technology, status, state, MW, latitude, longitude), of the rows in both: {fields_same:,} of {fields_all:,} the same")
    print(f"units with no balancing authority: {ba_note['blank']} whose cell the workbook leaves blank and {ba_note['NA']} it fills with \"NA\"")
    lost = sorted(i for i, r in mine_by_id.items() if r.kind in ("operating", "planned") and i not in page_ids)
    if lost:
        print(f"units whose id the page's copy does not hold as the workbook writes it: {', '.join(lost)} (the workbook's generator id is the text \"NA\")")
    print(f"figures that read the generating units alone: {units_ok:,} of {len(units_figs):,} inside the tolerance")
    print(f"every figure: {ok:,} of {n:,} inside the tolerance; {len(named):,} named (another day's queue or tracker rows); {len(outside)} outside and not named; {len(one_side)} on one side only")
    for f in outside[:20]:
        print(f"  OUTSIDE {f['key']}: page {f['page']}, replication {f['replication']}")
    for k in one_side[:10]:
        print(f"  ONE SIDE {k}")
    if a.write:
        out = {"tool": "/map", "tab": "projects", "written": got.get("written", ""), "page_file_built": m["built"], "eia_month": m["vintage"], "workbook": got.get("workbook", {}),
               "queue_vintage_read": queue_vintage, "queue_vintage_on_the_page": m["vintages"].get("queue"), "datacenter_vintage_read": dc_vintage,
               "datacenter_vintage_on_the_page": m["vintages"].get("datacenter"), "views": len(views), "rows": row_notes,
               "row_fields_the_same": fields_same, "row_fields_compared": fields_all,
               "tally": {"figures": n, "inside": ok, "named": len(named), "outside": len(outside), "one_side": len(one_side), "units_alone": len(units_figs), "units_alone_inside": units_ok},
               "note": "the page's figure is what its own functions compute on its own file (site/scripts/map-figures.mjs); the replication's is computed from EIA's workbook and the live set's rows by the rules of docs/methods/map.md. Datacenter rows are held (license needed): only counts and sums are written here",
               "figures": [{k: v for k, v in f.items()} for f in figs]}
        with open(os.path.join(HERE, "page_figures.json"), "w", encoding="utf-8", newline="\n") as f:
            json.dump(out, f, indent=1)
            f.write("\n")
        with open(os.path.join(HERE, "page_figures.csv"), "w", encoding="utf-8", newline="") as f:
            f.write(f"# ERW replication of /map (Projects tab): the page's figure and the replication's, {n} figures over {len(views)} views. Page file built {m['built']}; rows read {got.get('written', '')}. Method: docs/methods/map.md.\n")
            w = csv.writer(f, lineterminator="\n")
            w.writerow(["key", "page", "replication", "tolerance", "inside", "named"])
            for x in figs:
                w.writerow([x["key"], x["page"], x["replication"], x["tolerance"], "yes" if x["inside"] else "no", x.get("named", "")])
    return 0 if not outside and not one_side and units_ok == len(units_figs) and month_ok else 1


def _month_of(title):
    months = ["January", "February", "March", "April", "May", "June", "July", "August", "September", "October", "November", "December"]
    words = title.split()
    for i, w in enumerate(words):
        if w in months and i + 1 < len(words) and words[i + 1][:4].isdigit():
            return f"{words[i + 1][:4]}-{months.index(w) + 1:02d}"
    return ""


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))

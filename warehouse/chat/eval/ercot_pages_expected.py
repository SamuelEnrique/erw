#!/usr/bin/env python3
"""Energy Research Warehouse (ERW), session 153: the 20 test questions of Ask ERCOT about four pages, with every
expected number made here, by code, from the file or table the question is answered from. No model, no request.

    python warehouse/chat/eval/ercot_pages_expected.py --write          # writes warehouse/chat/eval_ercot_pages.json
    python warehouse/chat/eval/ercot_pages_expected.py --check          # recomputes and compares; exit 1 on a difference
    python warehouse/chat/eval/ercot_pages_expected.py --in-dir C:/.../warehouse/output --write

The four pages: /cost-of-power (what a datacenter pays), /curtailment (with "Where free energy is"),
/cost-of-power/seller (the capture price) and /resources. Each question is answerable from ONE source, named in its
expectation (`cite`, a pattern the answer's sources must match), and carries the read that answers it (`read`: the
tool call a test replays against the site's own tool, with the place in its result where the figure stands).

The arithmetic here is written again from each page's Method note, not copied from the site's code, so that the
site's tool (site/lib/chat/pagefiles.ts, which calls the pages' own functions) and this script are two readings of
the same files: site/scripts/test-ask-tables.mjs sets one against the other.

  a flat load (docs/methods/datacenter_cost.md): the mean of the hourly prices held; a month counts when at least
      95 percent of its hours are held; the last twelve months are the newest twelve consecutive counted months.
  the capture price (docs/methods/cost_of_power.md): sum(price x generation) / sum(generation) over the counted
      months; the flat average is sum(price) / hours over the same hours.
  a year's share of curtailment (docs/methods/curtailment.md): the year's curtailed MWh over its curtailed plus
      output MWh, over its months that have a share.

Two questions are answered from tables of the live set (iso_curtailment_monthly, ercot_large_load_status): their
numbers are read from the table on the data machine (--in-dir, or warehouse/output beside this repository). Where the
tables are not on the machine those two keep the numbers the committed file holds, and --check says so.

Two of the twenty must be refused: ISO-NE's monthly curtailment (held, not shown) and a MISO figure (paused while
terms are reviewed). Their expectation is the refusal's words.
"""
import argparse
import base64
import csv
import json
import os
import struct
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.normpath(os.path.join(HERE, "..", "..", ".."))
DATA = os.path.join(ROOT, "site", "data")
OUT = os.path.join(ROOT, "warehouse", "chat", "eval_ercot_pages.json")
NEAR = 0.95


def load(*parts):
    with open(os.path.join(DATA, *parts), encoding="utf-8") as f:
        return json.load(f)


def js_round(v, d):
    """Math.round(v * 10^d) / 10^d, as the site's tool rounds (half up, on the product)."""
    import math
    return math.floor(v * 10 ** d + 0.5) / 10 ** d


# ---- what a flat load paid (site/data/datacenter) ----------------------------------------------------------------

def leap(y):
    return (y % 4 == 0 and y % 100 != 0) or y % 400 == 0


def month_starts(y):
    days = [31, 29 if leap(y) else 28, 31, 30, 31, 30, 31, 31, 30, 31, 30, 31]
    out = [0]
    for d in days:
        out.append(out[-1] + 24 * d)
    return out


def flat_months(grid, region, market):
    """Every month held of a region and market: {"YYYY-MM": (sum of prices, hours held, hours due)}."""
    index = load("datacenter", "index.json")
    months = {}
    for y in index["grids"][grid]["years"]:
        f = load("datacenter", f"{grid}_{y}.json")
        side = f["regions"].get(region, {}).get(market)
        if not side:
            continue
        prices = [None] * f["hours"]
        for i, v in enumerate(side["v"]):
            prices[side["s"] + i] = v
        st = month_starts(y)
        for m in range(12):
            held = [v for v in prices[st[m]:st[m + 1]] if v is not None]
            if held:
                months[f"{y}-{m + 1:02d}"] = (sum(held), len(held), st[m + 1] - st[m])
    return months


def prev_month(m, k):
    y, mo = int(m[:4]), int(m[5:7]) - k
    while mo < 1:
        mo += 12
        y -= 1
    return f"{y}-{mo:02d}"


def last_twelve(months, counted):
    for m in sorted(months, reverse=True):
        twelve = [prev_month(m, k) for k in range(11, -1, -1)]
        if all(t in months and counted(months[t]) for t in twelve):
            return twelve
    return None


def flat_load(grid, region, market):
    months = flat_months(grid, region, market)
    counted = lambda r: r[1] >= NEAR * r[2]
    t = last_twelve(months, counted)
    twelve = sum(months[m][0] for m in t) / sum(months[m][1] for m in t)
    years = {}
    for y in sorted({m[:4] for m in months}):
        done = [months[m] for m in months if m.startswith(y) and counted(months[m])]
        if done:
            years[y] = js_round(sum(r[0] for r in done) / sum(r[1] for r in done), 2)
    return {"from": t[0], "to": t[-1], "usd_per_mwh": js_round(twelve, 2), "gpu_hour": js_round(twelve * 1.3 * 1.56 / 1000, 4), "years": years}


# ---- the capture price (site/data/seller/capture.json) -----------------------------------------------------------

def capture_months(grid, hub, market, fuel):
    f = load("seller", "capture.json")
    h = next(x for x in f["grids"][grid]["hubs"] if x["id"] == hub)
    return h[market][fuel], f["near"]


def capture_figure(recs):
    n = sum(r[0] for r in recs)
    sp = sum(r[2] for r in recs)
    g = sum(r[3] for r in recs)
    pg = sum(r[4] for r in recs)
    price, flat = pg / g, sp / n
    return {"price": js_round(price, 2), "flat": js_round(flat, 2), "premium": js_round(price - flat, 2), "pct": js_round(100 * (price - flat) / flat, 1)}


def capture(grid, hub, market, fuel):
    months, near = capture_months(grid, hub, market, fuel)
    counted = lambda r: r[0] >= near * r[1] - 1e-9
    t = last_twelve(months, counted)
    out = capture_figure([months[m] for m in t])
    out.update({"from": t[0], "to": t[-1], "years": {}})
    for y in sorted({m[:4] for m in months}):
        done = [months[m] for m in months if m.startswith(y) and counted(months[m])]
        if done:
            out["years"][y] = capture_figure(done)["price"]
    return out


def capture_hubs(grid, market, fuel):
    f = load("seller", "capture.json")
    rows = {}
    for h in f["grids"][grid]["hubs"]:
        months = (h.get(market) or {}).get(fuel)
        if not months:
            continue
        counted = lambda r: r[0] >= f["near"] * r[1] - 1e-9
        t = last_twelve(months, counted)
        if t:
            rows[h["id"]] = capture_figure([months[m] for m in t])["price"]
    return rows


# ---- curtailment (site/data/curtailment) -------------------------------------------------------------------------

def year_share(grid, year):
    months = load("curtailment", "shares.json")["grids"][grid]["months"]
    ms = [r for m, r in months.items() if m.startswith(f"{year}-")]
    c, o = sum(r["curtailed_mwh"] for r in ms), sum(r["output_mwh"] for r in ms)
    return js_round(100 * c / (c + o), 2), len(ms)


def month_shares(grid, year):
    months = load("curtailment", "shares.json")["grids"][grid]["months"]
    return {m: js_round(r["share_pct"], 2) for m, r in sorted(months.items()) if m.startswith(f"{year}-")}


def free_hours(grid, window):
    g = load("curtailment", "free_energy.json")["grids"][grid]
    return {loc["id"]: loc[window]["under5"] for loc in g["locations"] if loc["kind"] != "average" and "basis" in loc[window]}


# ---- the resource layers (site/data/resources) -------------------------------------------------------------------

def layer_entry(layer):
    return next(x for x in load("resources", "manifest.json")["layers"] if x["id"] == layer)


def grid_value(layer, lon, lat):
    """The stored value of the cell of the layer's finest level that holds a place: lon0 the west edge, lat0 the north."""
    entry = layer_entry(layer)
    finest = min(entry["levels"], key=lambda v: v["cell_deg"])
    f = load("resources", "layers", finest["file"])
    col, row = int((lon - f["lon0"]) // abs(f["dlon"])), int((f["lat0"] - lat) // abs(f["dlat"]))
    assert 0 <= col < f["ncols"] and 0 <= row < f["nrows"], "the place is outside the grid"
    raw = base64.b64decode(f["values"])
    stored = struct.unpack_from("<H", raw, 2 * (row * f["ncols"] + col))[0]
    assert stored != f.get("nodata", 65535), "the cell is empty"
    decimals = 0
    scale = f["scale"]
    while scale < 1 and decimals < 4 and round(scale * 10 ** decimals, 9) < 1:
        decimals += 1
    return js_round(stored * scale + f.get("offset", 0.0), decimals), finest["cell_deg"]


def shape_features(layer):
    f = load("resources", "layers", layer_entry(layer)["file"])
    return [(x["properties"]["name"], x["properties"].get("value")) for x in f["features"]]


def plain(v):
    return js_round(v, 1) if abs(v) >= 1000 else js_round(v, 4)


# ---- the two tables of the live set ------------------------------------------------------------------------------

def table_rows(in_dir, name):
    path = os.path.join(in_dir, f"{name}.csv")
    if not os.path.exists(path):
        return None
    with open(path, encoding="utf-8", newline="") as f:
        return list(csv.DictReader(line for line in f if not line.startswith("#")))


def table_value(in_dir, name, entity, variable, ts=None):
    """One value of a series table: the row of that time, or the newest row when no time is given. None: no table here."""
    rows = table_rows(in_dir, name)
    if rows is None:
        return None
    hits = [r for r in rows if r["entity"] == entity and r["variable"] == variable and (ts is None or r["ts_utc"].startswith(ts))]
    hit = max(hits, key=lambda r: r["ts_utc"])
    return float(hit["value"]), hit["ts_utc"][:10]


# ---- the questions -----------------------------------------------------------------------------------------------

COST, CAPTURE, SHARES, TEXAS, FREE, RESOURCES = ("site/data/datacenter/index.json", "site/data/seller/capture.json", "site/data/curtailment/shares.json",
                                                 "site/data/curtailment/ercot.json", "site/data/curtailment/free_energy.json", "site/data/resources/manifest.json")
esc = lambda s: s.replace("/", "\\/").replace(".", "\\.")


def build(in_dir, kept=None):
    kept = kept or {}
    north = flat_load("ercot", "LZ_NORTH", "rt")
    west = flat_load("ercot", "HB_WEST", "rt")
    solar_west = capture("ercot", "HB_WEST", "rt", "solar")
    wind_avg = capture("ercot", "HB_HUBAVG", "rt", "wind")
    solar_sp15 = capture("caiso", "TH_SP15_GEN-APND", "rt", "solar")
    solar_hubs = capture_hubs("ercot", "rt", "solar")
    ca_2025, ca_months = year_share("caiso", "2025")
    spp_2025 = month_shares("spp", "2025")
    free = free_hours("ercot", "year")
    texas = load("curtailment", "ercot.json")
    wind_speed, cell = grid_value("wind_speed_100m", -101.83, 35.22)
    basins = shape_features("oil_gas_basins")
    permian = next(v for n, v in basins if n == "Permian")
    ghi = layer_entry("solar_ghi")
    assert "1998-2016" in ghi["vintage"], ghi["vintage"]
    load_mw = table_value(in_dir, "ercot_large_load_status", "ercot:large_load", "approved_to_energize_mw")
    ca_solar = table_value(in_dir, "iso_curtailment_monthly", "caiso:ISO", "curtailed_solar_mwh", "2025-05")
    from_table = lambda qid, got: ({"expect": [got[0]], "table_read": True} if got is not None else {"expect": kept.get(qid, {}).get("expect", []), "table_read": False})

    q = [
        # /cost-of-power: what a datacenter pays
        {"id": "p01", "kind": "sentence", "page": "/cost-of-power", "q": "What did a flat load pay for power at ERCOT's North load zone over the last twelve months, in real time?",
         "expect": [north["usd_per_mwh"]], "cite": esc(COST), "source": COST,
         "read": {"tool": "page_file", "input": {"view": "cost", "grid": "ercot", "place": "LZ_NORTH", "market": "rt"}, "at": "last_twelve_months.usd_per_mwh"}},
        {"id": "p02", "kind": "chart", "page": "/cost-of-power", "q": "Show what a flat load paid for power at ERCOT's West hub year by year, in real time.",
         "cite": esc(COST), "source": COST, "series_has": {"key": "2021", "value": west["years"]["2021"]}, "series_rows": len(west["years"]),
         "read": {"tool": "page_file", "input": {"view": "cost", "grid": "ercot", "place": "HB_WEST", "market": "rt", "by": "year"}, "row": {"year": "2021"}}},
        {"id": "p03", "kind": "sentence", "page": "/cost-of-power", "q": "What does power cost per GPU-hour for a flat load at ERCOT's North load zone, at the page's own assumptions?",
         "expect": [north["gpu_hour"]], "cite": esc(COST), "source": COST,
         "read": {"tool": "page_file", "input": {"view": "cost", "grid": "ercot", "place": "LZ_NORTH"}, "at": "last_twelve_months.power_per_gpu_hour_usd"}},
        {"id": "p04", "kind": "sentence", "page": "/cost-of-power", "q": "How many megawatts of large load has ERCOT approved to energize, by its newest status report?",
         **from_table("p04", load_mw), "cite": "ercot_large_load_status", "source": "ercot_large_load_status",
         "read": {"tool": "query", "input": {"table": "ercot_large_load_status", "aggregation": "latest", "entity": "ercot:large_load", "variable": "approved_to_energize_mw"}}},
        # /cost-of-power/seller: the capture price
        {"id": "p05", "kind": "sentence", "page": "/cost-of-power/seller", "q": "What is the capture price of solar at ERCOT's West hub over the last twelve months, in real time?",
         "expect": [solar_west["price"]], "cite": esc(CAPTURE), "source": CAPTURE,
         "read": {"tool": "page_file", "input": {"view": "capture", "grid": "ercot", "place": "HB_WEST", "market": "rt", "fuel": "solar"}, "at": "last_twelve_months.capture_price_usd_per_mwh"}},
        {"id": "p06", "kind": "chart", "page": "/cost-of-power/seller", "q": "Show the capture price of wind at ERCOT's hub average year by year.",
         "cite": esc(CAPTURE), "source": CAPTURE, "series_has": {"key": "2022", "value": wind_avg["years"]["2022"]}, "series_rows": len(wind_avg["years"]),
         "read": {"tool": "page_file", "input": {"view": "capture", "grid": "ercot", "place": "HB_HUBAVG", "fuel": "wind", "by": "year"}, "row": {"year": "2022"}}},
        {"id": "p07", "kind": "sentence", "page": "/cost-of-power/seller", "q": "How far below the flat average price is solar's capture price at California's SP15 hub over the last twelve months?",
         "expect": [abs(solar_sp15["premium"]), abs(solar_sp15["pct"])], "cite": esc(CAPTURE), "source": CAPTURE,
         "read": {"tool": "page_file", "input": {"view": "capture", "grid": "caiso", "place": "TH_SP15_GEN-APND", "fuel": "solar"}, "at": "last_twelve_months.premium_usd_per_mwh", "abs": True}},
        {"id": "p08", "kind": "chart", "page": "/cost-of-power/seller", "q": "Compare the capture price of solar across ERCOT's hubs and load zones over the last twelve months.",
         "cite": esc(CAPTURE), "source": CAPTURE, "series_has": {"key": "HB_WEST", "value": solar_hubs["HB_WEST"]}, "series_rows": len(solar_hubs),
         "read": {"tool": "page_file", "input": {"view": "hubs", "grid": "ercot", "fuel": "solar"}, "row": {"place": "HB_WEST"}}},
        # /curtailment, with where free energy is
        {"id": "p09", "kind": "sentence", "page": "/curtailment", "q": "What share of its available wind and solar output did California curtail in 2025?",
         "expect": [ca_2025], "cite": f"{esc(SHARES)}|iso_curtailment_monthly", "source": SHARES,
         "read": {"tool": "page_file", "input": {"view": "share", "grid": "caiso", "period": "2025"}, "at": "period.share_pct"}},
        {"id": "p10", "kind": "chart", "page": "/curtailment", "q": "Show the share of its available wind and solar output that SPP curtailed, month by month in 2025.",
         "cite": f"{esc(SHARES)}|iso_curtailment_monthly", "source": SHARES, "series_has": {"key": "2025-04", "value": spp_2025["2025-04"]}, "series_rows": len(spp_2025),
         "read": {"tool": "page_file", "input": {"view": "share", "grid": "spp", "period": "2025", "by": "month"}, "row": {"month": "2025-04"}}},
        {"id": "p11", "kind": "sentence", "page": "/curtailment", "q": "How much solar energy did California curtail in May 2025?",
         **from_table("p11", ca_solar), "cite": "iso_curtailment_monthly|caiso_curtailment_profile", "source": "iso_curtailment_monthly",
         "read": {"tool": "query", "input": {"table": "iso_curtailment_monthly", "aggregation": "sum", "entity": "caiso:ISO", "variable": "curtailed_solar_mwh", "start": "2025-05-01", "end": "2025-06-01"}}},
        {"id": "p12", "kind": "sentence", "page": "/curtailment", "q": "In how many hours of the last twelve months was power at ERCOT's West hub priced under 5 dollars per MWh?",
         "expect": [free["HB_WEST"]], "cite": esc(FREE), "source": FREE,
         "read": {"tool": "page_file", "input": {"view": "free_energy", "grid": "ercot", "window": "year", "place": "HB_WEST"}, "at": "in_the_window.hours_under_usd_5"}},
        {"id": "p13", "kind": "chart", "page": "/curtailment", "q": "Show the hours priced under 5 dollars per MWh at each ERCOT hub and load zone over the last twelve months.",
         "cite": esc(FREE), "source": FREE, "series_has": {"key": "LZ_WEST", "value": free["LZ_WEST"]}, "series_rows": len(free),
         "read": {"tool": "page_file", "input": {"view": "free_energy", "grid": "ercot", "window": "year"}, "row": {"place": "LZ_WEST"}}},
        {"id": "p14", "kind": "sentence", "page": "/curtailment", "q": "Over the days held, what percent of the limit its plants reported was Texas wind and solar output below?",
         "expect": [texas["window"]["both"]["share_pct"]], "cite": f"{esc(TEXAS)}|ercot_wind_solar_hsl_daily", "source": TEXAS,
         "read": {"tool": "page_file", "input": {"view": "share", "grid": "ercot"}, "at": "over_the_days_held.share_of_limit_pct"}},
        # /resources
        {"id": "p15", "kind": "sentence", "page": "/resources", "q": "What is the mean wind speed at 100 m at longitude -101.83, latitude 35.22, near Amarillo?",
         "expect": [wind_speed], "cite": esc(RESOURCES), "source": RESOURCES,
         "read": {"tool": "page_file", "input": {"view": "value_at", "layer": "wind_speed_100m", "lon": -101.83, "lat": 35.22}, "at": "value"}, "cell_deg": cell},
        {"id": "p16", "kind": "sentence", "page": "/resources", "q": "How large is the Permian sedimentary basin on the resource map, in square miles?",
         "expect": [plain(permian)], "cite": esc(RESOURCES), "source": RESOURCES,
         "read": {"tool": "page_file", "input": {"view": "features", "layer": "oil_gas_basins", "name": "Permian"}, "row": {"name": "Permian"}}},
        {"id": "p17", "kind": "chart", "page": "/resources", "q": "List the sedimentary basins the resource map holds, with the area of each.",
         "cite": esc(RESOURCES), "source": RESOURCES, "series_has": {"key": "Permian", "value": plain(permian)}, "series_rows": len(basins),
         "read": {"tool": "page_file", "input": {"view": "features", "layer": "oil_gas_basins"}, "row": {"name": "Permian"}}},
        {"id": "p18", "kind": "sentence", "page": "/resources", "q": "Who publishes the resource map's global horizontal irradiance layer, and which years does it average?",
         "expect_all": [1998, 2016], "cite": esc(RESOURCES), "source": RESOURCES, "must": "NLR|NREL|National (Renewable Energy )?Laboratory",
         "read": {"tool": "page_file", "input": {"view": "layer", "layer": "solar_ghi"}, "contains": "1998-2016"}},
        # the two it must refuse
        {"id": "p19", "kind": "refuse", "page": "/curtailment", "q": "How much wind and solar energy did ISO New England curtail in August 2026?",
         "say": "held, not shown", "why": "internal: ISO-NE's monthly undelivered energy is held under its terms and not shown", "source": "isone_ddg_undelivered_monthly",
         "read": {"tool": "page_file", "input": {"view": "share", "grid": "isone", "period": "2026-08"}, "refused": "isone_ddg_undelivered_monthly is held, not shown"}},
        {"id": "p20", "kind": "refuse", "page": "/cost-of-power/seller", "q": "What is the capture price of wind at MISO's Indiana hub?",
         "say": "paused while terms are reviewed", "why": "MISO is paused: no figure of it is shown", "source": "none",
         "read": {"tool": "page_file", "input": {"view": "capture", "grid": "miso", "place": "INDIANA.HUB", "fuel": "wind"}, "words": "paused while terms are reviewed"}},
    ]
    for x in q:
        x["new"] = "pages153"
    return {
        "_about": "Session 153: 20 test questions for Ask ERCOT about four pages built in the week of 5 October 2026: what a datacenter pays (/cost-of-power), curtailment and where free energy is (/curtailment), the capture price (/cost-of-power/seller) and where the resources are (/resources). Written by warehouse/chat/eval/ercot_pages_expected.py: every expected number is computed there from the file or table named in the question's `source`; do not edit by hand. The rule of a question's kind is the one of the 100 (warehouse/chat/eval_ercot_panel.json), and these fields add to it: `expect` (one of these numbers is in the answer, at its own precision or one decimal coarser), `expect_all` (each of them is), `cite` (a source the answer cites, or the table of a series it shows, matches), `must` (the answer matches), `series_has` (a series shown holds this row) and `series_rows` (and has this many rows). `read` is the tool call that answers the question, replayed with no model by site/scripts/test-ask-tables.mjs.",
        "rules_added": {
            "expect": "one of the numbers is in the answer: equal at the answer's own precision, which may be one decimal coarser than the expected number's and no coarser (a number of 100 or more may be written whole); signs are not compared",
            "expect_all": "each of the numbers is in the answer, by the same rule",
            "cite": "a citation's table, or the table of a series shown, matches the pattern",
            "must": "the answer matches the pattern",
            "series_has": "a series shown holds a row with this key whose value, at the expected value's decimals, is this value",
            "series_rows": "a series shown has this many rows",
        },
        "built_from": {"datacenter": load("datacenter", "index.json")["built"], "capture": load("seller", "capture.json")["built"], "shares": load("curtailment", "shares.json")["built"],
                       "free_energy": load("curtailment", "free_energy.json")["built"], "texas": texas["built"], "resources": load("resources", "manifest.json")["built_at_utc"],
                       "tables_read": {"ercot_large_load_status": load_mw is not None, "iso_curtailment_monthly": ca_solar is not None}},
        "facts": {"flat_load_last_twelve_months": [north["from"], north["to"]], "capture_last_twelve_months": [solar_west["from"], solar_west["to"]], "california_months_with_a_share_2025": ca_months,
                  "large_load_report_day": load_mw[1] if load_mw else kept.get("_facts", {}).get("large_load_report_day")},
        "questions": q,
    }


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--in-dir", default=os.path.join(ROOT, "warehouse", "output"), help="where the tables are (read only)")
    ap.add_argument("--write", action="store_true")
    ap.add_argument("--check", action="store_true")
    a = ap.parse_args()
    old = None
    if os.path.exists(OUT):
        with open(OUT, encoding="utf-8") as f:
            old = json.load(f)
    kept = {x["id"]: x for x in (old or {}).get("questions", [])}
    kept["_facts"] = (old or {}).get("facts", {})
    new = build(a.in_dir, kept)
    if a.check:
        if old is None:
            print(f"{OUT} is not written yet")
            return 1
        diff = [x["id"] for x, y in zip(new["questions"], old["questions"]) if {k: v for k, v in x.items() if k != "table_read"} != {k: v for k, v in y.items() if k != "table_read"}]
        if len(new["questions"]) != len(old["questions"]) or diff:
            print(f"the committed questions differ from what the files give: {diff or 'another number of questions'}")
            return 1
        unread = [k for k, v in new["built_from"]["tables_read"].items() if not v]
        print(f"{len(new['questions'])} questions agree with the files" + (f"; not on this machine, so kept as committed: {', '.join(unread)}" if unread else ""))
        return 0
    if a.write:
        with open(OUT, "w", encoding="utf-8", newline="\n") as f:
            json.dump(new, f, indent=1, ensure_ascii=True)
            f.write("\n")
        print(f"wrote {OUT}: {len(new['questions'])} questions")
        for x in new["questions"]:
            print(f"  {x['id']} {x['kind']:8s} {x['page']:22s} {x.get('expect', x.get('expect_all', x.get('series_has', x.get('say'))))}")
        return 0
    print(json.dumps(new, indent=1))
    return 0


if __name__ == "__main__":
    sys.exit(main())

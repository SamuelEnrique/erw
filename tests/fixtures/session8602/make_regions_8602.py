"""Session 8602 (chain 504): writes the test fixture of the Grid tool's region views, tests/fixtures/session8602/regions/.

THE FIGURES ARE THE TESTS' OWN. The files have the form of docs/state/page_files_regions.md (sections 2 to 5): an index,
two regions' mix files, one trade file and one demand file with its `alike` object. They exist so that the readers
(site/lib/gridregions.ts) and the drawing (site/components/grid/RegionViews.tsx) can be tested before the data
machine's files are on main and whatever those files hold. They are never shipped with the site and nothing on a page a
person opens is drawn from them.

- The index: the thirteen regions by EIA's code and name; the lists of balancing authorities are short lists of real
  EIA-930 codes placed by this script, not EIA's reference table.
- mix/tex.json and mix/se.json: the newest 26 months and two years of site/data/mix/ercot.json as that file stands
  (so the drawing is tried on a real file's shape), renamed, with an hourly part made by repeating the newest month's
  average day for 35 days: not hours anyone measured. One hour is blanked, to try a gap.
- trade/se.json: six months of typed numbers, with a month one neighbour did not report.
- demand/tex.json: the `alike` object alone, with a typed sentence.

Run once; the result is committed.

    python tests/fixtures/session8602/make_regions_8602.py
"""
import copy
import json
import os

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.abspath(os.path.join(HERE, "..", "..", ".."))
OUT = os.path.join(HERE, "regions")
MARK = "TEST FIXTURE: the tests' own figures, not a region's"

REGIONS = [("CAL", "California", "America/Los_Angeles", ["BANC", "CISO", "IID", "LDWP", "TIDC"], ["CISO"]),
           ("CAR", "Carolinas", "America/New_York", ["CPLE", "CPLW", "DUK", "SC", "SCEG", "YAD"], []),
           ("CENT", "Central", "America/Chicago", ["SPA", "SWPP"], ["SWPP"]),
           ("FLA", "Florida", "America/New_York", ["FMPP", "FPC", "FPL", "GVL", "HST", "JEA", "SEC", "TAL", "TEC"], []),
           ("MIDA", "Mid-Atlantic", "America/New_York", ["PJM"], ["PJM"]),
           ("MIDW", "Midwest", "America/Chicago", ["AECI", "LGEE", "MISO"], ["MISO"]),
           ("NE", "New England", "America/New_York", ["ISNE"], ["ISNE"]),
           ("NW", "Northwest", "America/Los_Angeles", ["AVA", "BPAT", "IPCO", "NWMT", "PACE", "PACW", "PGE", "PSEI", "SCL", "TPWR"], []),
           ("NY", "New York", "America/New_York", ["NYIS"], ["NYIS"]),
           ("SE", "Southeast", "America/Chicago", ["AEC", "SEPA", "SOCO"], []),
           ("SW", "Southwest", "America/Phoenix", ["AZPS", "EPE", "PNM", "SRP", "TEPC", "WALC"], []),
           ("TEN", "Tennessee", "America/Chicago", ["TVA"], []),
           ("TEX", "Texas", "America/Chicago", ["ERCO"], ["ERCO"])]
GRID_OF = {"CISO": "CISO", "SWPP": "SWPP", "PJM": "PJM", "MISO": "MISO", "ISNE": "ISNE", "NYIS": "NYIS", "ERCO": "ERCO"}
COMMON = {"built": "2026-11-19T00:00:00Z", "method": "docs/methods/regions_pages.md", "license": "public"}


def write(rel, obj):
    path = os.path.join(OUT, rel)
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "w", encoding="utf-8", newline="\n") as f:
        json.dump(obj, f, separators=(",", ":"))
        f.write("\n")
    print(rel, os.path.getsize(path))


def index():
    return {**COMMON, "fixture": MARK, "tables": ["eia930_ba_demand_hourly", "eia930_region_hourly"],
            "regions": [{"code": c, "name": n, "tz": tz, "bas": bas, "grids": grids, "first_hour": "2018-07-01T05:00:00Z", "last_hour": "2026-11-17T05:00:00Z"} for c, n, tz, bas, grids in REGIONS],
            "bas": [{"code": b, "name": "Fixture name of " + b, "region": c, "tz": tz, "grid": GRID_OF.get(b), "region_grids": grids, "generation_only": b in ("SEPA", "YAD"), "active": True, "retired": None,
                     "first_hour": "2018-07-01T05:00:00Z", "last_hour": "2026-11-17T05:00:00Z", "files": ["demand"]} for c, n, tz, bas, grids in REGIONS for b in bas]}


def mix(code, name, tz):
    with open(os.path.join(ROOT, "site", "data", "mix", "ercot.json"), encoding="utf-8") as f:
        src = json.load(f)
    keep = sorted(src["months"])[-26:]            # the newest 26 months and the newest two years: enough for every view, and a small file
    years = sorted(src["years"])[-2:]
    out = {"grid": code.lower(), "name": name + " (" + MARK + ")", "tz": tz, **COMMON, "tables": ["eia930_region_fuel_hourly"], "join": None, "first": keep[0], "upto": src["upto"], "sources": src["sources"],
           "months": {m: copy.deepcopy(src["months"][m]) for m in keep}, "years": {y: copy.deepcopy(src["years"][y]) for y in years}}
    for p in out["months"].values():
        p["side"] = "eia930"
    day = out["months"][src["upto"]]["avg"]
    n = 35 * 24
    # local hour h of the Central zone at UTC hour (h + 6) of the fixture's start, 2026-10-14T06:00:00Z: the average day, repeated
    hourly = {"hours": {"start": "2026-10-14T06:00:00Z", "step_hours": 1, "n": n}}
    for key in list(src["sources"]) + ["demand", "net_generation"]:
        v = day.get(key)
        hourly[key] = [None] * n if not v else [v[i % 24] for i in range(n)]
    hourly["net_imports"] = [None if d is None or g is None else round(d - g, 1) for d, g in zip(hourly["demand"], hourly["net_generation"])]
    for key in hourly:
        if key != "hours":
            hourly[key][n - 30] = None       # one hour not held, in every series
    hourly["net_generation"][n - 1] = None   # and the newest hour holds no net generation: the latest hour held is the one before
    out["hourly"] = hourly
    return out


def trade():
    months = ["2026-05", "2026-06", "2026-07", "2026-08", "2026-09", "2026-10"]
    car = {"net_imports_mwh": [-501753.0, -410220.0, -388001.0, -501753.0, -299870.0, -120045.0], "their_report_mwh": [-506389.0, -409950.0, -390012.0, -506389.0, -300100.0, -119800.0],
           "gap_mwh": [2226.0, -270.0, 2011.0, 2226.0, 230.0, -245.0], "hours_own": [744, 720, 744, 744, 720, 744], "hours_their": [720, 720, 744, 720, 720, 744], "hours_both": [720, 720, 744, 720, 720, 744]}
    fla = {"net_imports_mwh": [-880120.0, -910400.0, -1002300.0, -1100950.0, -905600.0, None], "their_report_mwh": [-878900.0, -911020.0, -1001800.0, -1099700.0, -906010.0, -700300.0],
           "gap_mwh": [-1220.0, 620.0, -500.0, -1250.0, 410.0, None], "hours_own": [744, 720, 744, 744, 720, 0], "hours_their": [744, 720, 744, 744, 720, 744], "hours_both": [744, 720, 744, 744, 720, 0]}
    ten = {"net_imports_mwh": [210500.0, 180300.0, 95020.0, 60010.0, 150700.0, 220900.0], "their_report_mwh": [209800.0, 181000.0, 95500.0, 61000.0, 150100.0, 221500.0],
           "gap_mwh": [700.0, -700.0, -480.0, -990.0, 600.0, -600.0], "hours_own": [744, 720, 744, 744, 720, 744], "hours_their": [744, 720, 744, 744, 720, 744], "hours_both": [744, 720, 744, 744, 720, 744]}
    total = [round(a + b + c, 1) if b is not None else None for a, b, c in zip(car["net_imports_mwh"], fla["net_imports_mwh"], ten["net_imports_mwh"])]
    return {**COMMON, "fixture": MARK, "tables": ["eia930_region_pair_hourly"], "code": "SE", "name": "Southeast", "months": months, "net_imports_mwh": total, "neighbors": {"CAR": car, "FLA": fla, "TEN": ten}}


def demand():
    return {**COMMON, "fixture": MARK, "tables": ["eia930_ba_demand_hourly"], "code": "TEX", "name": "Texas", "tz": "America/Chicago", "level": "region", "basis": "region_sum", "bas_summed": ["ERCO"],
            "alike": {"grid": "ERCO", "years": {"2025": {"region_avg_demand_mw": 54000.0, "grid_avg_demand_mw": 54000.0, "difference_pct": 0.0}},
                      "why": "Fixture sentence: the region sums the authorities EIA places in it and the grid's file reads one authority's own workbook. A second sentence that a hover does not carry."}}


if __name__ == "__main__":
    write("index.json", index())
    write(os.path.join("mix", "tex.json"), mix("TEX", "Texas", "America/Chicago"))
    write(os.path.join("mix", "se.json"), mix("SE", "Southeast", "America/Chicago"))
    write(os.path.join("trade", "se.json"), trade())
    write(os.path.join("demand", "tex.json"), demand())

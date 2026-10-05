"""Session 123: how hard the system works (/mix/stress, in review).

Energy Research Warehouse (ERW). No request leaves the machine. The arithmetic of warehouse/derived/mix_stress.py on
small frames made for the tests (round numbers, shown nowhere: they test the sums, not the data), the table and the
site's copy where they are on this machine, and the page's words.

    python -m unittest tests.test_session123 -v
"""
import json
import os
import re
import shutil
import subprocess
import sys
import tempfile
import unittest

import numpy as np
import pandas as pd

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
os.environ.setdefault("ERW_LOCK_EXEMPT", "1")
for p in ("warehouse/connectors", "warehouse/derived"):
    sys.path.insert(0, os.path.join(ROOT, *p.split("/")))
import iso_prices as ip  # noqa: E402
import mix_profile as mp  # noqa: E402
import mix_stress as ms  # noqa: E402

OUT = os.path.join(ROOT, "warehouse", "output")
SITE = os.path.join(ROOT, "site", "data", "stress")
TZ = "America/Chicago"


def src(*parts):
    with open(os.path.join(ROOT, *parts), encoding="utf-8") as f:
        return f.read()


def hours(n, start="2024-06-01T05:00:00Z", demand=1000.0, wind=100.0, solar=0.0):
    """n hours of one grid in the shape mix_profile.hours_of gives; demand, wind and solar a constant or a list (a
    shorter list is repeated)."""
    idx = pd.date_range(start, periods=n, freq="h", tz="UTC")
    full = lambda v: (list(v) * (n // len(v) + 1))[:n] if isinstance(v, (list, tuple)) else v  # noqa: E731
    x = pd.DataFrame({"demand": full(demand), "wind": full(wind), "solar": full(solar)}, index=idx)
    x["natural_gas"], x["coal"], x["nuclear"], x["hydro"], x["storage"] = x["demand"] - x["wind"] - x["solar"] - 200.0, 0.0, 200.0, 0.0, 0.0
    x["other"] = (np.arange(n) % 2) * 0.5      # half a MW on and off: an hour that repeats the one before to the MW is a stale report, and is not used
    x["net_generation"] = x[mp.SOURCES].sum(axis=1)
    x["interchange"] = 0.0
    x["side"], x["held"] = "eia930", True
    local = idx.tz_convert(TZ)
    x["day"], x["month"], x["hour"] = local.strftime("%Y-%m-%d"), local.strftime("%Y-%m"), local.hour
    return x


def caps(wind=1000.0, solar=1000.0, months=("2024-01", "2024-02")):
    s = lambda v: pd.Series(v, index=list(months))  # noqa: E731
    return {("ERCO", "wind"): s(wind), ("ERCO", "solar"): s(solar), ("ERCO", "natural_gas"): s(2000.0), ("ERCO", "nuclear"): s(250.0), ("ERCO", "storage"): s(100.0), ("ERCO", "hydro"): s(50.0)}


def table(x, c=None, fleet=(100.0, 200.0)):
    mw, mwh = pd.Series({"2024-01": fleet[0]}), pd.Series({"2024-01": fleet[1]})
    rows = ms.grid_rows("ercot", x, c or caps(), mw, mwh, "2026-10-05T00:00:00Z", lambda m: None)
    return {r["variable"]: r for r in rows}


class Stretches(unittest.TestCase):
    def test_a_run_is_hours_next_to_each_other(self):
        idx = pd.date_range("2024-01-01", periods=10, freq="h", tz="UTC")
        self.assertEqual(ms.stretches([0, 1, 1, 1, 0, 0, 1, 1, 0, 1], idx), [(1, 3), (6, 2), (9, 1)])
        self.assertEqual(ms.stretches([1] * 10, idx), [(0, 10)])
        self.assertEqual(ms.stretches([0] * 10, idx), [])

    def test_a_gap_in_the_hours_ends_a_run(self):
        idx = pd.date_range("2024-01-01", periods=6, freq="h", tz="UTC").delete(3)      # the fourth hour is not held
        self.assertEqual(ms.stretches([1, 1, 1, 1, 1], idx), [(0, 3), (3, 2)])


class TheEveningRamp(unittest.TestCase):
    def day(self, net_by_local_hour, start="2024-06-01T05:00:00Z"):
        x = hours(24, start=start, demand=net_by_local_hour, wind=0.0)
        return x.assign(net=x["demand"])

    def test_it_is_the_largest_rise_between_14_and_22_local(self):
        net = [500.0] * 24
        net[9], net[10] = 500.0, 5000.0                    # a morning rise is not an evening ramp
        net[17:24] = [600.0, 900.0, 1500.0, 1600.0, 1600.0, 1600.0, 1600.0]
        r = ms.evening_ramps(self.day(net), TZ)
        self.assertEqual(float(r["ramp1"].iloc[0]), 600.0)                               # 900 to 1,500, from 18:00 to 19:00
        self.assertEqual(pd.Timestamp(r["ramp1_at"].iloc[0]).tz_convert(TZ).hour, 18)
        self.assertEqual(float(r["ramp3"].iloc[0]), 1000.0)                              # 16:00 to 19:00, 500 to 1,500 (and 17:00 to 20:00, 600 to 1,600)
        self.assertIn(pd.Timestamp(r["ramp3_at"].iloc[0]).tz_convert(TZ).hour, (16, 17))

    def test_a_rise_the_next_hour_takes_back_is_a_spike_not_a_ramp(self):
        net = [1000.0] * 24
        net[15] = 3000.0                                    # up 2,000 at 15:00, back down at 16:00
        net[19], net[20], net[21] = 1300.0, 1300.0, 1300.0  # a rise of 300 that stays
        r = ms.evening_ramps(self.day(net), TZ)
        self.assertEqual(float(r["ramp1"].iloc[0]), 300.0)

    def test_a_step_across_an_hour_that_is_not_there_is_not_a_step(self):
        net = [1000.0] * 24
        net[19:24] = [5000.0] * 5
        d = self.day(net)
        d = d[d["hour"] != 18]                              # the hour before the rise is not held
        r = ms.evening_ramps(d, TZ)
        self.assertEqual(float(r["ramp1"].max()), 0.0)


class TheYear(unittest.TestCase):
    def year(self, **kw):
        # thirty days from the year's first local hour: the hours the year is due "to date" are these
        return hours(24 * 30, start="2024-01-01T06:00:00Z", **kw)

    def test_net_load_is_demand_less_wind_less_solar(self):
        x = self.year(demand=1000.0, wind=100.0, solar=[0.0] * 12 + [300.0] * 12)
        t = table(x)
        self.assertEqual(t["net_load_min_mw"]["value"], 600.0)
        self.assertEqual(t["net_load_peak_mw"]["value"], 900.0)
        self.assertEqual(t["peak_demand_mw"]["value"], 1000.0)
        self.assertEqual(t["net_load_min_share_of_peak_pct"]["value"], 60.0)
        self.assertEqual(t["net_load_min_wind_solar_share_pct"]["value"], 40.0)
        self.assertTrue(t["net_load_min_mw"]["x_at"].endswith("Z"))
        self.assertEqual(t["hours_held"]["unit"], "count")

    def test_a_fuel_in_the_tightest_hours_is_its_output_over_its_capacity(self):
        x = self.year(demand=[1000.0] * 600 + [1500.0] * 120, wind=100.0)
        t = table(x)
        self.assertEqual(t["tight_net_load_mw"]["value"], 1400.0)
        self.assertEqual(t["tight_wind_share_of_capacity_pct"]["value"], 10.0)            # 100 MW of 1,000
        self.assertEqual(t["tight_wind_mw"]["value"], 100.0)
        self.assertNotIn("tight_solar_mw", t)                                            # solar is not in the file this year: no figure, never a zero
        self.assertNotIn("tight_natural_gas_share_of_capacity_pct", t)                   # 2024: units retired before 2025 are not in the inventory read
        self.assertIn("tight_natural_gas_mw", t)
        self.assertEqual(t["solar_reported"]["value"], 0.0)

    def test_from_2025_the_thermal_fuels_have_a_share_too(self):
        x = hours(24 * 30, start="2025-01-01T06:00:00Z", demand=1000.0, wind=100.0)
        x["storage"] = 60.0
        x["natural_gas"] -= 60.0
        c = {k: pd.Series(v.values, index=["2025-01", "2025-02"]) for k, v in caps().items()}
        rows = ms.grid_rows("ercot", x, c, pd.Series({"2025-01": 100.0}), pd.Series({"2025-01": 200.0}), "t", lambda m: None)
        t = {r["variable"]: r["value"] for r in rows}
        self.assertEqual(t["tight_nuclear_share_of_capacity_pct"], 80.0)                  # 200 MW of 250
        self.assertEqual(t["tight_natural_gas_share_of_capacity_pct"], 32.0)             # 640 MW of 2,000
        # hydro and storage are set against capacity together: 60 MW of storage and no hydro, over 100 and 50
        self.assertEqual((t["tight_storage_mw"], t["tight_hydro_storage_mw"], t["capacity_hydro_storage_mw"], t["tight_hydro_storage_share_of_capacity_pct"]), (60.0, 60.0, 150.0, 40.0))
        self.assertNotIn("tight_storage_share_of_capacity_pct", t)
        self.assertNotIn("capacity_hydro_mw", t)

    def test_dark_and_calm_is_under_a_tenth_of_installed_wind_and_solar(self):
        wind = [300.0] * 720
        wind[100:148] = [50.0] * 48                         # two days at 50 MW of 1,000 installed (solar is not reported: its capacity does not count)
        wind[300:310] = [99.0] * 10
        t = table(self.year(wind=wind))
        self.assertEqual(t["calm_hours"]["value"], 58.0)
        self.assertEqual(t["calm_longest_hours"]["value"], 48.0)
        self.assertEqual(t["calm_stretches_ge24h"]["value"], 1.0)
        mean = (300.0 * 662 + 50.0 * 48 + 99.0 * 10) / 720
        self.assertAlmostEqual(t["calm_longest_missing_mwh"]["value"], round((mean - 50.0) * 48, 3), places=2)
        self.assertAlmostEqual(t["calm_longest_fleet_full_power_hours"]["value"], (mean - 50.0) * 48 / 100.0, places=2)
        self.assertAlmostEqual(t["calm_longest_fleet_energy_multiples"]["value"], (mean - 50.0) * 48 / 200.0, places=2)
        self.assertEqual(t["wind_solar_capacity_mw"]["value"], 1000.0)

    def test_hours_that_do_not_describe_the_grid_are_not_used(self):
        x = self.year()
        x.iloc[50, x.columns.get_loc("demand")] = 300.0     # demand far from net generation less interchange: the balance does not close
        t = table(x)
        self.assertGreater(t["net_load_min_mw"]["value"], 300.0)                         # the unbalanced hour would have been the year's lowest net load
        self.assertEqual(t["hours_held"]["value"], 719.0)
        stale = self.year()
        for c in ("net_generation", "wind", "solar"):                                    # four hours that repeat the hour before to the MW
            stale.iloc[200:204, stale.columns.get_loc(c)] = stale.iloc[199][c]
        self.assertEqual(table(stale)["hours_held"]["value"], 716.0)

    def test_a_year_with_too_few_hours_is_not_written(self):
        x = self.year()
        x.loc[x.index[:200], "held"] = False
        self.assertEqual(table(x), {})


class TheInventory(unittest.TestCase):
    def test_a_unit_counts_from_its_first_month_and_a_retired_one_until_it_retires(self):
        d = tempfile.mkdtemp()
        try:
            head = "balancing_authority,technology_group,nameplate_mw,operating_year,operating_month"
            with open(os.path.join(d, ms.OPERATING + ".csv"), "w", encoding="utf-8") as f:
                f.write("# test\n" + head + "\nERCO,wind,100,2015,1\nERCO,wind,50,2024,6\nERCO,solar,30,,\nXXXX,wind,999,2015,1\nERCO,biomass,5,2015,1\n")
            with open(os.path.join(d, ms.RETIRED + ".csv"), "w", encoding="utf-8") as f:
                f.write("# test\n" + head + ",status_date\nERCO,coal,400,1980,1,2025-03-01\n")
            c = ms.capacity(d)
        finally:
            shutil.rmtree(d, ignore_errors=True)
        self.assertEqual((c[("ERCO", "wind")]["2024-05"], c[("ERCO", "wind")]["2024-06"]), (100.0, 150.0))
        self.assertEqual(c[("ERCO", "solar")]["2019-01"], 30.0)                          # no operating month: counted from the start
        self.assertEqual((c[("ERCO", "coal")]["2025-02"], c[("ERCO", "coal")]["2025-03"]), (400.0, 0.0))
        self.assertNotIn(("XXXX", "wind"), c)
        self.assertNotIn(("ERCO", "biomass"), c)


class TheTable(unittest.TestCase):
    def t(self):
        path = os.path.join(OUT, ms.NAME + ".csv")
        if not os.path.exists(path):
            raise unittest.SkipTest(f"{ms.NAME} is not on this machine")
        t = pd.read_csv(path, skiprows=ip.header_rows(path), keep_default_na=False)
        t["value"] = pd.to_numeric(t["value"])
        return t

    def test_its_shape_and_its_identities(self):
        t = self.t()
        self.assertFalse(t.duplicated(["entity", "variable", "ts_utc"]).any())
        self.assertEqual(set(t["freq"]), {"P1Y"})
        w = t.pivot(index=["entity", "ts_utc"], columns="variable", values="value")
        self.assertTrue((w["hours_held"] >= ms.NEAR * w["hours_in_year"]).all())
        self.assertTrue((w["net_load_peak_mw"] <= w["peak_demand_mw"] + 1e-6).all())
        self.assertTrue((w["net_load_min_mw"] <= w["tight_net_load_mw"]).all())
        self.assertTrue((w["evening_ramp_median_mw_per_h"] <= w["evening_ramp_max_mw_per_h"]).all())
        self.assertTrue((w["evening_ramp_3h_max_mw"].dropna() >= w["evening_ramp_max_mw_per_h"][w["evening_ramp_3h_max_mw"].notna()] - 1e-6).all())
        self.assertLess((100 * w["evening_ramp_max_mw_per_h"] / w["peak_demand_mw"] - w["evening_ramp_max_share_of_peak_pct"]).abs().max(), 0.01)
        self.assertTrue((w["calm_longest_hours"].dropna() <= w["calm_hours"][w["calm_longest_hours"].notna()]).all())
        for fuel in ms.FUELS + ["hydro_storage"]:
            share = w.get(f"tight_{fuel}_share_of_capacity_pct")
            if share is not None:
                self.assertTrue((share.dropna() <= 105).all(), fuel)      # output at or under nameplate
        for fuel in ms.TOGETHER:                                           # hydro and storage alone are never set against capacity (PJM's pumped storage is in its hydro)
            self.assertNotIn(f"tight_{fuel}_share_of_capacity_pct", w.columns)

    def test_the_thermal_fuels_have_no_share_before_2025(self):
        t = self.t()
        early = t[t["ts_utc"].str[:4].astype(int) < ms.FROM_YEAR]
        for fuel in ("natural_gas", "coal", "nuclear", "hydro_storage"):
            self.assertFalse((early["variable"] == f"tight_{fuel}_share_of_capacity_pct").any(), fuel)
        self.assertTrue((early["variable"] == "tight_wind_share_of_capacity_pct").any())

    def test_new_yorks_solar_is_not_reported_and_is_no_zero(self):
        t = self.t()
        ny = t[t["entity"] == "iso:nyiso"]
        self.assertEqual(set(ny[ny["variable"] == "solar_reported"]["value"]), {0.0})
        self.assertFalse(ny["variable"].str.startswith("tight_solar").any())

    def test_every_record_says_when(self):
        t = self.t()
        for v in ("peak_demand_mw", "net_load_min_mw", "evening_ramp_max_mw_per_h", "calm_longest_hours"):
            at = t[t["variable"] == v]["x_at"]
            self.assertTrue(at.str.match(r"^\d{4}-\d{2}-\d{2}T\d{2}:00:00Z$").all(), v)
        self.assertEqual(set(t[t["variable"] == "hours_held"]["x_at"]), {""})

    def test_the_sites_copy_is_the_table(self):
        t = self.t()
        for grid in mp.GRIDS:
            p = os.path.join(SITE, f"{grid}.json")
            if not os.path.exists(p):
                raise unittest.SkipTest("the site's copy is not on this machine")
            f = json.load(open(p, encoding="utf-8"))
            g = t[t["entity"] == f"iso:{grid}"]
            for r in g.itertuples():
                self.assertEqual(f["years"][r.ts_utc[:4]][r.variable], r.value, f"{grid} {r.variable} {r.ts_utc}")
                if r.x_at:
                    self.assertEqual(f["years"][r.ts_utc[:4]][r.variable + "_at"], r.x_at)
            self.assertEqual(sum(1 for y in f["years"].values() for k in y if not k.endswith("_at")), len(g), grid)


def node(js):
    exe = shutil.which("node")
    if not exe:
        raise unittest.SkipTest("node is not on this machine")
    r = subprocess.run([exe, "--input-type=module"], input=js, cwd=os.path.join(ROOT, "site"), capture_output=True, text=True, timeout=120, encoding="utf-8")
    if r.returncode != 0:
        if "ERR_UNKNOWN_FILE_EXTENSION" in r.stderr or "Unknown file extension" in r.stderr:
            raise unittest.SkipTest("this node does not read TypeScript files")
        raise AssertionError(r.stderr[-2000:])
    return json.loads(r.stdout.strip().splitlines()[-1])


class ThePage(unittest.TestCase):
    def test_it_is_in_review_with_its_method_and_no_live_page_knows_of_it(self):
        self.assertIn('"/mix/stress": "review"', src("site", "lib", "release.ts"))
        routes = src("site", "scripts", "check-routes.mjs")
        self.assertIn('"/mix/stress"', routes)
        self.assertIn('"/data/methods/grid_stress"', routes)
        for f in ("site/app/page.tsx", "site/app/storage/page.tsx", "site/app/network/page.tsx", "site/app/cost-of-power/battery/page.tsx", "site/app/cost-of-power/seller/page.tsx"):
            if os.path.exists(os.path.join(ROOT, *f.split("/"))):
                self.assertNotIn("mix/stress", src(*f.split("/")), f)

    def test_the_definitions_are_on_the_page_as_computed(self):
        page = src("site", "app", "mix", "stress", "page.tsx")
        for words in ("Demand less wind less solar", "The largest rise of net load from one hour to the next between {w0}:00 and {w1}:00 local time", "The {f.tight} hours of the year with the highest net load",
                      "less than {f.calm_pct} percent of their installed capacity", "a one-hour rise the next hour takes back", "California is two series, not one.", "data-stress-unreported",
                      "This is what the fleet did, not what it could do", "No fleet can do either"):
            self.assertIn(words, page)
        self.assertEqual((ms.TIGHT, ms.CALM, ms.WINDOW), (100, 0.10, (14, 22)))

    def test_no_figure_is_written_into_the_page(self):
        page = re.sub(r"^\s*//.*$", "", src("site", "app", "mix", "stress", "page.tsx"), flags=re.M)
        self.assertIsNone(re.search(r">\s*-?\d+\.\d+\s*<", page))
        self.assertIsNone(re.search(r"\b\d{3,} MW\b", page))
        self.assertNotIn("2025-12-16", page)
        self.assertNotIn("2025-12-16", src("warehouse", "derived", "mix_stress.py"))

    def test_the_library_picks_and_never_computes(self):
        p = os.path.join(SITE, "ercot.json")
        if not os.path.exists(p):
            raise unittest.SkipTest("the site's copy is not on this machine")
        f = json.load(open(p, encoding="utf-8"))
        r = node("""
import fs from "node:fs";
import { get, at, defaultYear, yearsOf, wholeYear, fuelRows, when, span, pct, whole, isGrid } from "./lib/stress.ts";
const f = JSON.parse(fs.readFileSync("data/stress/ercot.json", "utf8"));
const ny = JSON.parse(fs.readFileSync("data/stress/nyiso.json", "utf8"));
const y = defaultYear(f), last = yearsOf(f).at(-1), first = yearsOf(f)[0];
console.log(JSON.stringify({ y, last, lastWhole: wholeYear(f, last), ramp: get(f, y, "evening_ramp_max_mw_per_h"), at: at(f, y, "evening_ramp_max_mw_per_h"), none: get(f, y, "no_such"), noneAt: at(f, y, "hours_held"),
  when: when("2025-01-19T22:00:00Z", "America/Chicago"), whenNone: when(null, "America/Chicago"), spans: [span(18), span(38), span(48), span(0), span(null)], fuels: fuelRows(f, y), early: fuelRows(f, first),
  nySolar: fuelRows(ny, yearsOf(ny).at(-2)).find((r) => r.fuel === "solar"), fmt: [pct(null), pct(19.068), whole(15940.4), whole(null)], grids: [isGrid("spp"), isGrid("x")] }));
""")
        y = r["y"]
        self.assertEqual(f["years"][y]["hours_in_year"] >= 8760, True)
        self.assertFalse(r["lastWhole"])                                    # the newest year is to date
        self.assertEqual((r["ramp"], r["at"]), (f["years"][y]["evening_ramp_max_mw_per_h"], f["years"][y]["evening_ramp_max_mw_per_h_at"]))
        self.assertEqual((r["none"], r["noneAt"]), (None, None))
        self.assertEqual((r["when"], r["whenNone"]), ("19 January 2025, 16:00", "not held"))
        self.assertEqual(r["spans"], ["18 hours", "1 day 14 hours", "2 days", "0 hours", "not held"])
        wind = next(x for x in r["fuels"] if x["fuel"] == "wind")
        self.assertEqual(wind["share"], f["years"][y]["tight_wind_share_of_capacity_pct"])
        gas = next(x for x in r["early"] if x["fuel"] == "natural_gas")
        self.assertEqual((gas["share"], gas["why"]), (None, "installed capacity is held from 2025 only"))
        self.assertEqual((r["nySolar"]["mw"], r["nySolar"]["why"]), (None, "the source file does not report it for this year"))
        self.assertEqual(r["fmt"], ["not held", "19.1%", "15,940", "not held"])
        self.assertEqual(r["grids"], [True, False])

    def test_no_em_dash_and_no_request(self):
        for parts in (("warehouse", "derived", "mix_stress.py"), ("docs", "methods", "grid_stress.md"), ("site", "app", "mix", "stress", "page.tsx"), ("site", "lib", "stress.ts"),
                      ("site", "app", "mix", "stress", "data.ts"), ("tests", "test_session123.py")):
            self.assertNotIn(chr(0x2014), src(*parts), parts[-1])
        self.assertNotIn("requests", src("warehouse", "derived", "mix_stress.py").split('"""', 2)[2])
        self.assertIn("miso", src("warehouse", "metadata", "paused_sources.csv").lower())


if __name__ == "__main__":
    unittest.main()

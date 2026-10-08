"""Session 129: demand growth without weather, finished.

Energy Research Warehouse (ERW). What session 129 added to session 126's work: the Census Bureau's populations in place
of the stated weights (warehouse/connectors/census_metro_population.py), the stations' hours as a table and the grid
tables rebuilt from it, a grid's hour on four stations of five (New England's trial), and dew point tried in the fit
(warehouse/derived/demand_weather.py). On a real sample saved under tests/fixtures/session129/ (the Census Bureau's
rows for New York State's metropolitan areas, as served) and on session 126's samples. Where a test makes up a value
it says so: it tests the arithmetic and writes nothing.
"""
import gzip
import io
import json
import os
import sys
import unittest

import numpy as np
import pandas as pd

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
sys.path.insert(0, os.path.join(ROOT, "warehouse", "connectors"))
sys.path.insert(0, os.path.join(ROOT, "warehouse", "derived"))
import census_metro_population as cmp_  # noqa: E402
import demand_weather as dw  # noqa: E402
import noaa_grid_weather as ngw  # noqa: E402

FIX = os.path.join(ROOT, "tests", "fixtures", "session129")
OUT = os.path.join(ROOT, "warehouse", "output")
COPY = os.path.join(ROOT, "site", "data", "demand_weather.json")


def src(*p):
    with open(os.path.join(ROOT, *p), encoding="utf-8") as f:
        return f.read()


def census_sample():
    with open(os.path.join(FIX, "cbsa-est2025-alldata_new_york_state_areas.csv"), encoding="latin-1") as f:
        return cmp_.shape(f.read(), cmp_.URL, "2026-10-06T00:37:00Z")


class Census(unittest.TestCase):
    def test_the_bureaus_rows_and_the_parts_by_state(self):
        t, n, areas = census_sample()
        self.assertEqual(areas, 6)
        b = t[t["variable"] == "population_base_2020"].set_index("entity")["value"]
        self.assertEqual(int(b["census:cbsa:45060"]), 662063)                      # Syracuse, as the Bureau's file gives it
        self.assertEqual(int(b["census:cbsa:28880"]), 698330)                      # Kiryas Joel-Poughkeepsie-Newburgh
        self.assertEqual(int(b["census:cbsa:35620"]), 20083400)                    # New York-Newark-Jersey City, whole
        self.assertEqual(int(b["census:cbsa:35620:36"]) + int(b["census:cbsa:35620:34"]), 20083400)   # its two states add to it
        self.assertEqual(int(b["census:cbsa:35620:36"]), 13167758)
        self.assertEqual(set(t["unit"]), {"count"})
        self.assertEqual(sorted(t["variable"].unique()), ["population_2025", "population_base_2020"])

    def test_counties_that_do_not_add_to_their_area_stop_it(self):
        with open(os.path.join(FIX, "cbsa-est2025-alldata_new_york_state_areas.csv"), encoding="latin-1") as f:
            lines = f.read().splitlines()
        i = next(k for k, ln in enumerate(lines) if ln.startswith("45060,") and "County or equivalent" in ln)
        with self.assertRaises(RuntimeError):
            cmp_.shape("\n".join(lines[:i] + lines[i + 1:]) + "\n", cmp_.URL, "2026-10-06T00:37:00Z")   # one county's row removed
        self.assertEqual(cmp_.CEILING, 5_000)


class Weights(unittest.TestCase):
    def pop(self):
        """A table of the stations' areas: the Bureau's counts for New York State's, and made-up counts for the others
        (the arithmetic of a share does not depend on whose count it is)."""
        t, _, _ = census_sample()
        b = t[t["variable"] == "population_base_2020"]
        pop = {e: (int(v), n) for e, v, n in zip(b["entity"], b["value"], b["node"])}
        for code, (cbsa, part) in ngw.CBSA.items():
            pop.setdefault(f"census:cbsa:{cbsa}" + (f":{part}" if part else ""), (1_000_000, "made up"))
        return pop

    def test_new_yorks_weights_are_the_bureaus_shares_and_the_citys_is_its_part_in_the_state(self):
        w = ngw.census_weights(self.pop())
        ny = {c: v for c, v in w.items() if v["ba"] == "nyis"}
        tot = 13167758 + 1166897 + 1065373 + 899223 + 662063
        self.assertEqual(ny["LGA"]["population"], 13167758)
        self.assertEqual(ny["LGA"]["cbsa"], "35620:36")
        self.assertAlmostEqual(ny["LGA"]["weight"], 13167758 / tot, places=12)
        self.assertAlmostEqual(ny["SYR"]["weight"], 662063 / tot, places=12)
        for ba in ngw.GRIDS:
            self.assertAlmostEqual(sum(v["weight"] for v in w.values() if v["ba"] == ba), 1.0, places=12)

    def test_the_rule_says_where_the_counts_and_the_stations_part(self):
        said = ngw.rule_check(self.pop())
        self.assertEqual(len([x for x in said if x.startswith("NYISO")]), 1)
        self.assertIn("Kiryas Joel-Poughkeepsie-Newburgh, NY (698,330) is more populous than Syracuse, NY (662,063)", said[0])

    def test_an_area_the_table_lacks_stops_it(self):
        pop = self.pop()
        del pop["census:cbsa:45060"]
        with self.assertRaises(RuntimeError):
            ngw.census_weights(pop)

    def test_every_station_has_an_area_and_the_stated_shares_are_kept_as_a_record(self):
        self.assertEqual(sorted(ngw.CBSA), sorted(s[1] for s in ngw.STATIONS))
        self.assertEqual({c: p for c, (a, p) in ngw.CBSA.items() if p}, {"LGA": "36"})


class FourOfFive(unittest.TestCase):
    def stations(self, temps):
        idx = pd.date_range("2025-07-01T00:00:00Z", periods=len(next(iter(temps.values()))), freq="h")
        return {c: pd.DataFrame({"temp_f": v, "dew_f": v, "interp": 0}, index=idx) for c, v in temps.items()}

    def test_an_hour_on_four_stations_is_the_weighted_mean_of_the_four(self):
        st = self.stations({"A": [60.0, 60.0, 60.0], "B": [70.0, np.nan, np.nan], "C": [80.0, 80.0, np.nan], "D": [50.0, 50.0, 50.0], "E": [90.0, 90.0, 90.0]})
        w = {"A": 0.4, "B": 0.2, "C": 0.2, "D": 0.1, "E": 0.1}
        h = ngw.grid_hours(st, w, min_stations=4)
        self.assertAlmostEqual(h["temperature_f"].iloc[0], 68.0, places=9)                                   # all five
        self.assertAlmostEqual(h["temperature_f"].iloc[1], (0.4 * 60 + 0.2 * 80 + 0.1 * 50 + 0.1 * 90) / 0.8, places=9)   # four: the weights restated
        self.assertTrue(np.isnan(h["temperature_f"].iloc[2]))                                                  # three: not held
        self.assertEqual(list(h["stations"]), [5, 4, 3])
        self.assertAlmostEqual(h["cooling_degrees_f"].iloc[1], (0.2 * 15 + 0.1 * 25) / 0.8, places=9)
        self.assertAlmostEqual(h["heating_degrees_f"].iloc[1], (0.4 * 5 + 0.1 * 15) / 0.8, places=9)

    def test_the_tables_rule_is_all_five(self):
        st = self.stations({"A": [60.0, 60.0], "B": [70.0, np.nan]})
        h = ngw.grid_hours(st, {"A": 0.5, "B": 0.5})
        self.assertEqual(h["temperature_f"].notna().tolist(), [True, False])
        self.assertNotIn("stations", h)


class StationHours(unittest.TestCase):
    def test_a_value_turns_back_to_noaas_tenth_exactly(self):
        c = np.round(np.arange(-400, 500) / 10.0, 1)                       # every tenth of a degree C from -40.0 to 49.9
        f = np.round(c * 9 / 5 + 32, 2)
        self.assertTrue((np.round((f - 32) * 5 / 9, 1) == c).all())

    def test_only_measured_hours_are_rows_and_the_hours_come_back_from_the_table(self):
        idx = pd.date_range("2025-07-31T22:00:00Z", periods=6, freq="h")   # across the seam of 1 August 2025
        raw = {"DFW": pd.DataFrame({"temp_c": [30.0, np.nan, 28.3, 27.8, 27.2, 26.7], "dew_c": [20.0, 20.6, np.nan, 21.1, 21.1, 21.7]}, index=idx)}   # made up, for the arithmetic
        facts = {"DFW": dict(ba="erco", wban="03927", state="TX", lite_retrieved="2026-10-05T17:20:00Z", lcd_retrieved="2026-10-05T17:20:00Z")}
        t = ngw.station_table(raw, facts, idx)
        self.assertEqual(len(t), 10)                                         # two missing values: no row for either
        self.assertEqual(set(t["entity"]), {"noaa:USW00003927"})
        self.assertEqual(set(t["node"]), {"DFW"})
        self.assertEqual(list(t[t["variable"] == "temperature_f"]["source"]), ["noaa:isd_lite"] + ["noaa:lcd_v2"] * 4)
        path = os.path.join(FIX, "_station_hours_test.csv")
        try:
            with open(path, "w", encoding="utf-8", newline="") as f:
                f.write("# made by a test\n")
                t.to_csv(f, index=False, lineterminator="\n")
            back = ngw.raw_from_table(path)["DFW"].reindex(idx)
        finally:
            if os.path.exists(path):
                os.remove(path)
        pd.testing.assert_series_equal(back["temp_c"], raw["DFW"]["temp_c"], check_names=False, check_freq=False)
        pd.testing.assert_series_equal(back["dew_c"], raw["DFW"]["dew_c"], check_names=False, check_freq=False)
        self.assertEqual(ngw.STATION_CEILING, 5_000_000)


class DewPoint(unittest.TestCase):
    def test_the_rule_of_adoption(self):
        base = {g: 4.0 for g in "abcdefg"}
        self.assertEqual(dw.adopt_dew(base, {g: 3.9 for g in "abcdefg"}), (True, []))
        self.assertEqual(dw.adopt_dew(base, {**{g: 3.5 for g in "abcdef"}, "g": 4.2}), (False, ["g"]))      # better on average, but it costs one grid too much
        self.assertEqual(dw.adopt_dew(base, {g: 4.01 for g in "abcdefg"}), (False, []))                       # no better on average
        self.assertEqual(dw.adopt_dew(base, {**{g: 3.5 for g in "abcdef"}, "g": 4.04})[0], True)

    def test_the_humid_term_is_zero_without_cooling_and_absent_without_a_dew_point(self):
        idx = pd.date_range("2022-07-01T00:00:00Z", periods=4, freq="h")
        demand = pd.Series([100.0, 101.0, 102.0, 103.0], index=idx)          # made up, for the arithmetic
        w = pd.DataFrame({"temperature_f": [80.0, 60.0, 85.0, 85.0], "dew_point_f": [70.0, 70.0, 55.0, np.nan],
                          "heating_degrees_f": [0.0, 5.0, 0.0, 0.0], "cooling_degrees_f": [15.0, 0.0, 20.0, 20.0]}, index=idx)
        x = dw.frame(demand, w, "America/New_York")
        self.assertEqual(x["hum"].iloc[0], 10.0)                             # dew point 70, ten above 60, in an hour that cools
        self.assertEqual(x["hum"].iloc[1], 0.0)                              # no cooling: no humid term
        self.assertEqual(x["hum"].iloc[2], 0.0)                              # dry air
        self.assertTrue(np.isnan(x["hum"].iloc[3]))                          # no dew point held: the term is not made up
        self.assertEqual(dw.FEATURES_DEW, dw.FEATURES + ("hum", "hum24"))

    def test_on_new_englands_real_hours_the_fit_runs_with_the_term_absent(self):
        with gzip.open(os.path.join(ROOT, "tests", "fixtures", "session126", "isne_demand_weather_2019_2022.csv.gz"), "rt", encoding="utf-8") as f:
            x = pd.read_csv(io.StringIO(f.read()), comment="#", index_col=0)
        x.index = pd.to_datetime(x.index, utc=True)
        r = dw.analyse(x["demand"].dropna(), x[["heating_degrees_f", "cooling_degrees_f"]].dropna(), "America/New_York", "ISNE", dw.FEATURES_DEW)
        self.assertEqual((r["fit"]["kinds"], r["fit"]["hours"]), (0, 0))      # the sample holds no dew point: no line is fitted
        self.assertEqual(r["years"], {})                                     # and no figure is written, for any year


class Moved(unittest.TestCase):
    def test_what_moved_and_what_changed_its_reading(self):
        old = {"ERCO": {"2025": {"energy": dict(unexplained_pct=23.8, finding=True, uncertainty_pct=4.1), "summer_peak": dict(unexplained_pct=3.0, finding=False, uncertainty_pct=6.6), "winter_peak": None}}}
        new = {"ERCO": {2025: {"energy": dict(unexplained_pct=24.0, finding=True, uncertainty_pct=4.0), "summer_peak": dict(unexplained_pct=7.0, finding=True, uncertainty_pct=6.0), "winter_peak": dict(unexplained_pct=1.0, finding=False, uncertainty_pct=30.0)}}}
        rows = {r["figure"]: r for r in dw.moved(old, new)}
        self.assertAlmostEqual(rows["energy"]["change"], 0.2, places=9)
        self.assertEqual((rows["summer_peak"]["was_finding"], rows["summer_peak"]["finding"]), (False, True))
        self.assertIsNone(rows["winter_peak"]["change"])                     # held now and not before: named, with no change to give


class Repository(unittest.TestCase):
    def test_no_em_dash_in_what_the_session_wrote(self):
        for p in (("warehouse", "connectors", "census_metro_population.py"), ("warehouse", "connectors", "noaa_grid_weather.py"), ("warehouse", "derived", "demand_weather.py"),
                  ("docs", "methods", "demand_weather.md"), ("site", "app", "demand", "weather", "page.tsx"), ("tests", "test_session129.py")):
            self.assertNotIn(chr(0x2014), src(*p), p)
            self.assertNotIn(chr(0x2013), src(*p), p)

    def test_the_page_names_the_bureau_and_shows_new_england_both_ways(self):
        page = src("site", "app", "demand", "weather", "page.tsx")
        for words in ("Census Bureau", "New England under two rules", "Which rule stands is a ruling still to be made", "People, 2020"):
            self.assertIn(words, page)
        self.assertNotIn("The populations were not retrieved", page)
        self.assertIn('"/demand/weather": "review"', src("site", "lib", "release.ts"))

    def test_the_new_tables_are_held_out_of_the_catalogue(self):
        sys.path.insert(0, os.path.join(ROOT, "warehouse", "supabase"))
        import load
        for t in ("noaa_station_weather_hourly", "census_metro_population"):
            self.assertIn(t, load.LIVE["catalogue_hold"])
        self.assertIn("census:popest_cbsa", load.LIVE["sources_hold"])


@unittest.skipUnless(os.path.exists(COPY), "the site's copy is written by demand_weather.py --snapshot")
class SiteCopy(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        with open(COPY, encoding="utf-8") as f:
            cls.f = json.load(f)

    def test_dew_point_was_decided_by_its_rule(self):
        d = self.f["dew"]
        base = {g: v["without"]["hour"] for g, v in d["by_grid"].items()}
        with_ = {g: v["with_dew"]["hour"] for g, v in d["by_grid"].items()}
        self.assertEqual(len(base), 7)
        self.assertEqual(d["adopted"], dw.adopt_dew(base, with_)[0])
        self.assertEqual(("hum" in self.f["features"]), d["adopted"])

    def test_the_weights_are_the_bureaus_shares(self):
        st = self.f["weather"]["stations"]
        for ba in {s["ba"] for s in st.values()}:
            tot = sum(s["population"] for s in st.values() if s["ba"] == ba)
            for s in st.values():
                if s["ba"] == ba:
                    self.assertAlmostEqual(s["weight"], s["population"] / tot, places=4)   # the copy rounds to four decimals
        self.assertEqual(st["LGA"]["cbsa"], "35620:36")
        self.assertLessEqual(max(abs(s["weight"] - s["weight_stated"]) for s in st.values()), 0.05)   # session 126's twentieths were close

    def test_new_england_is_there_under_both_rules_and_the_comparison_with_session_126(self):
        ne = self.f["isne_four_of_five"]
        self.assertEqual(ne["least"], 4)
        self.assertGreater(ne["hours_held"], self.f["weather"]["grids"]["isne"]["hours_held"])
        self.assertGreater(len(self.f["moved_from_126"]), 100)


@unittest.skipUnless(os.path.exists(os.path.join(OUT, "noaa_station_weather_hourly.csv")), "the tables are on the data machine")
class TablesAsBuilt(unittest.TestCase):
    def test_the_grid_table_comes_back_from_the_station_table(self):
        """One grid, rebuilt from the stations' table alone, equals the grid table as built, hour for hour."""
        raw = ngw.raw_from_table(os.path.join(OUT, "noaa_station_weather_hourly.csv"))
        facts = ngw.facts_from_tables(OUT)
        self.assertEqual(len(raw), 35)
        _, hours, _, _, _ = ngw.build(raw, facts)
        g = pd.read_csv(os.path.join(OUT, "noaa_grid_weather_hourly.csv"), comment="#", usecols=["variable", "ts_utc", "value", "ba"])
        for ba in ("erco", "isne"):
            t = g[(g["ba"] == ba) & (g["variable"] == "temperature_f")].set_index("ts_utc")["value"]
            t.index = pd.to_datetime(t.index, utc=True)
            mine = hours[ba]["temperature_f"].dropna().round(2)
            self.assertEqual(len(mine), len(t), ba)
            self.assertLess(float((mine - t.reindex(mine.index)).abs().max()), 0.011, ba)

    def test_the_station_table_is_under_its_ceiling_and_holds_measured_values_only(self):
        n = sum(1 for _ in open(os.path.join(OUT, "noaa_station_weather_hourly.csv"), encoding="utf-8")) - 1
        self.assertLess(n, ngw.STATION_CEILING + 40)
        s = pd.read_csv(os.path.join(OUT, "noaa_grid_weather_stations.csv"), comment="#")
        measured = int(s[s["variable"] == "hours_measured"]["value"].sum())
        self.assertGreater(n, measured)                                      # the temperatures measured, and the dew points beside them
        self.assertLess(n, 2 * measured + 40)


if __name__ == "__main__":
    unittest.main()

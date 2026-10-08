"""Session 126: demand growth with the weather taken out (/demand/weather, in review).

Energy Research Warehouse (ERW). The NOAA connector (warehouse/connectors/noaa_grid_weather.py) and the fit
(warehouse/derived/demand_weather.py), on real samples saved under tests/fixtures/session126/ as NOAA and EIA served
them: Austin's ISD-Lite hours and its Local Climatological Data reports of 1 to 3 July 2025; Minneapolis's of 14 and
15 July 2020, where ISD-Lite keeps one hour in six; and New England's hourly demand and weather of 2019 to 2022. A test
that blanks or scales a real value says so: it tests the arithmetic, and writes nothing to the warehouse. The tables
and the site's copy as built are checked where they are on the machine.
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
import demand_weather as dw  # noqa: E402
import noaa_grid_weather as ngw  # noqa: E402

FIX = os.path.join(ROOT, "tests", "fixtures", "session126")
SITE = os.path.join(ROOT, "site")
COPY = os.path.join(SITE, "data", "demand_weather.json")
OUT = os.path.join(ROOT, "warehouse", "output")
NEW = ["warehouse/connectors/noaa_grid_weather.py", "warehouse/derived/demand_weather.py", "docs/methods/demand_weather.md",
       "site/app/_retired/demand-weather/page.tsx", "site/lib/demandweather.ts", "tests/test_session126.py"]


def read(name, mode="rb"):
    with open(os.path.join(FIX, name), mode) as f:
        return f.read()


def lite(name):
    return ngw.parse_lite(read(name))


class IsdLite(unittest.TestCase):
    def test_a_real_file_reads_as_hours_in_tenths_of_a_degree(self):
        x, n = lite("isd_lite_722540-13904_2025-07-01_03.txt")
        self.assertEqual(n, 72)
        self.assertEqual(str(x.index[0]), "2025-07-01 00:00:00+00:00")
        self.assertEqual((x["temp_c"].iloc[0], x["dew_c"].iloc[0]), (25.0, 22.2))    # the file's "250" and "222"
        self.assertTrue(x.index.is_monotonic_increasing and not x.index.has_duplicates)

    def test_minus_9999_is_a_missing_value_not_a_temperature(self):
        x, n = lite("isd_lite_726580-14922_2020-07-14_16.txt")
        self.assertEqual(n, 72)
        self.assertGreater(int(x["temp_c"].isna().sum()), 40)       # Minneapolis, July 2020: most hours are -9999
        self.assertGreater(float(x["temp_c"].min()), -60)


class LocalClimatologicalData(unittest.TestCase):
    def test_local_standard_time_moves_to_utc_and_an_hour_takes_the_report_just_before_it(self):
        x, n, marked = ngw.parse_lcd(read("lcd_v2_USW00013904_2025-06-30_07-03.csv", "r"), 6)
        self.assertEqual(marked, 0)
        # the report of 00:53 local standard time (23.3 C) is the hour 07:00 UTC
        self.assertEqual(float(x.loc[pd.Timestamp("2025-07-01T07:00:00Z"), "temp_c"]), 23.3)
        self.assertEqual(float(x.loc[pd.Timestamp("2025-07-01T07:00:00Z"), "dew_c"]), 22.2)

    def test_the_two_products_agree_outside_the_synoptic_hours_and_only_with_the_right_clock(self):
        a, _ = lite("isd_lite_722540-13904_2025-07-01_03.txt")
        for hours, least, most in ((6, 0.999, 1.0), (5, 0.0, 0.5), (7, 0.0, 0.5)):
            b, _, _ = ngw.parse_lcd(read("lcd_v2_USW00013904_2025-06-30_07-03.csv", "r"), hours)
            both = a.join(b, how="inner", lsuffix="_lite", rsuffix="_lcd").dropna(subset=["temp_c_lite", "temp_c_lcd"])
            off = both[both.index.hour % 3 != 0]
            share = float((off["temp_c_lite"] - off["temp_c_lcd"]).abs().le(0.051).mean())
            self.assertGreater(len(off), 30)
            self.assertTrue(least <= share <= most, (hours, share))

    def test_austin_differs_at_the_synoptic_hours(self):
        a, _ = lite("isd_lite_722540-13904_2025-07-01_03.txt")
        b, _, _ = ngw.parse_lcd(read("lcd_v2_USW00013904_2025-06-30_07-03.csv", "r"), 6)
        both = a.join(b, how="inner", lsuffix="_lite", rsuffix="_lcd").dropna(subset=["temp_c_lite", "temp_c_lcd"])
        syn = both[both.index.hour % 3 == 0]
        self.assertLess(float((syn["temp_c_lite"] - syn["temp_c_lcd"]).abs().le(0.051).mean()), 0.9)

    def test_minneapolis_holds_every_hour_where_isd_lite_holds_one_in_six(self):
        a, _ = lite("isd_lite_726580-14922_2020-07-14_16.txt")
        b, n, _ = ngw.parse_lcd(read("lcd_v2_USW00014922_2020-07-14_15.csv", "r"), 6)
        self.assertEqual(n, 298)                                    # rows returned, the reports without a temperature among them
        day = pd.date_range("2020-07-14T07:00:00Z", "2020-07-15T06:00:00Z", freq="h")
        self.assertEqual(int(b["temp_c"].reindex(day).notna().sum()), 24)
        self.assertLessEqual(int(a["temp_c"].reindex(day).notna().sum()), 6)
        both = a.join(b, how="inner", lsuffix="_lite", rsuffix="_lcd").dropna(subset=["temp_c_lite", "temp_c_lcd"])
        self.assertTrue(((both["temp_c_lite"] - both["temp_c_lcd"]).abs() <= 0.051).all())

    def test_a_marked_or_blank_value_is_not_a_number(self):
        v = ngw.number(["23.3", "23.3s", "", "-1.1", "*", "T", " 4 "])
        self.assertEqual([None if pd.isna(x) else float(x) for x in v], [23.3, None, None, -1.1, None, None, 4.0])

    def test_an_empty_or_cut_off_answer_is_not_whole(self):
        url = ngw.lcd_url("13904", "2025-07-01", "2026-10-05")
        body = read("lcd_v2_USW00013904_2025-06-30_07-03.csv")
        self.assertFalse(ngw.whole_answer(b"", url))
        self.assertFalse(ngw.whole_answer(body, url))               # it stops in July 2025: fifteen months short of the day asked
        self.assertTrue(ngw.whole_answer(body, ngw.lcd_url("13904", "2025-07-01", "2025-07-10")))


class MissingHours(unittest.TestCase):
    def setUp(self):
        x, _ = lite("isd_lite_722540-13904_2025-07-01_03.txt")
        self.s = x["temp_c"].copy()
        self.assertEqual(int(self.s.isna().sum()), 0)

    def test_three_hours_are_interpolated_on_a_line_and_counted(self):
        s = self.s.copy()
        s.iloc[10:13] = np.nan                                       # three real hours blanked, for the arithmetic
        t, it = ngw.fill_short(s)
        self.assertEqual(int(it.sum()), 3)
        self.assertAlmostEqual(float(t.iloc[11]), (self.s.iloc[9] + self.s.iloc[13]) / 2, places=9)
        self.assertEqual(ngw.gaps(s), (3, 1, 3))

    def test_four_hours_stay_missing(self):
        s = self.s.copy()
        s.iloc[10:14] = np.nan
        t, it = ngw.fill_short(s)
        self.assertEqual(int(it.sum()), 0)
        self.assertEqual(int(t.isna().sum()), 4)

    def test_a_run_at_either_end_is_never_filled(self):
        s = self.s.copy()
        s.iloc[:2] = np.nan
        s.iloc[-2:] = np.nan
        t, it = ngw.fill_short(s)
        self.assertEqual(int(it.sum()), 0)
        self.assertEqual(int(t.isna().sum()), 4)

    def test_a_short_run_beside_a_long_one_is_filled_and_the_long_one_is_not(self):
        s = self.s.copy()
        s.iloc[5:7] = np.nan
        s.iloc[20:30] = np.nan
        t, it = ngw.fill_short(s)
        self.assertEqual(int(it.sum()), 2)
        self.assertEqual(int(t.isna().sum()), 10)


class GridWeather(unittest.TestCase):
    def stations(self, temps):
        idx = pd.date_range("2025-07-01T00:00:00Z", periods=len(next(iter(temps.values()))), freq="h")
        return {c: pd.DataFrame({"temp_f": v, "dew_f": v, "interp": 0}, index=idx) for c, v in temps.items()}

    def test_the_stated_weights_of_every_grid_add_to_one(self):
        tot = {}
        for ba, code, usaf, wban, weight, lst, metro in ngw.STATIONS:
            tot[ba] = tot.get(ba, 0) + weight
            self.assertAlmostEqual(weight * 20, round(weight * 20), places=9)     # a twentieth
        self.assertEqual(sorted(tot), sorted(ngw.GRIDS))
        for ba, t in tot.items():
            self.assertAlmostEqual(t, 1.0, places=9, msg=ba)
        self.assertEqual(len(ngw.STATIONS), 35)
        self.assertEqual({ba: sum(1 for s in ngw.STATIONS if s[0] == ba) for ba in ngw.GRIDS}, {ba: 5 for ba in ngw.GRIDS})

    def test_degrees_are_taken_at_each_station_and_then_weighted(self):
        st = self.stations({"A": [55.0, 60.0], "B": [75.0, 60.0]})
        h = ngw.grid_hours(st, {"A": 0.5, "B": 0.5})
        self.assertEqual(list(h["temperature_f"]), [65.0, 60.0])
        self.assertEqual(list(h["heating_degrees_f"]), [5.0, 5.0])     # the first hour: one city 10 below, one 10 above
        self.assertEqual(list(h["cooling_degrees_f"]), [5.0, 0.0])

    def test_an_hour_one_station_lacks_is_not_held(self):
        st = self.stations({"A": [55.0, np.nan], "B": [75.0, 60.0]})
        h = ngw.grid_hours(st, {"A": 0.5, "B": 0.5})
        self.assertEqual(h["temperature_f"].notna().tolist(), [True, False])
        self.assertTrue(np.isnan(h["heating_degrees_f"].iloc[1]) and np.isnan(h["cooling_degrees_f"].iloc[1]))

    def test_weights_that_do_not_add_to_one_stop_it(self):
        st = self.stations({"A": [55.0], "B": [75.0]})
        with self.assertRaises(ValueError):
            ngw.grid_hours(st, {"A": 0.5, "B": 0.4})

    def test_only_whole_local_days_are_written(self):
        idx = pd.date_range("2025-03-08T06:00:00Z", "2025-03-11T04:00:00Z", freq="h")     # Central: 9 March has 23 hours
        h = pd.DataFrame({"temperature_f": 50.0, "dew_point_f": 40.0, "heating_degrees_f": 15.0, "cooling_degrees_f": 0.0}, index=idx)
        h.loc[pd.Timestamp("2025-03-08T12:00:00Z"), ["temperature_f", "heating_degrees_f", "cooling_degrees_f"]] = np.nan
        d = ngw.grid_days(h, "America/Chicago")
        self.assertEqual(list(d.index), ["2025-03-09", "2025-03-10"])   # the 8th lacks an hour; the 9th has 23 and is whole
        self.assertEqual([int(v) for v in d["hours"]], [23, 24])
        self.assertAlmostEqual(float(d["heating_degree_days"].iloc[0]), 15.0 * 23 / 24, places=9)
        cut = ngw.grid_days(h.iloc[:-1], "America/Chicago")           # the 10th cut short by an hour is not whole
        self.assertEqual(list(cut.index), ["2025-03-09"])

    def test_the_ceiling_stops_the_pull_before_it_is_passed(self):
        led = ngw.Ledger(ngw.EXPLORED + 1000, lambda *a: None)
        led.allow(1000, "x")
        with self.assertRaises(RuntimeError):
            led.allow(1001, "x")
        led.add(900, {"cached": True}, 0)
        with self.assertRaises(RuntimeError):
            led.add(200, {}, 0)
        self.assertEqual(ngw.CEILING, 3_000_000)


class Fit(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        with gzip.open(os.path.join(FIX, "isne_demand_weather_2019_2022.csv.gz"), "rt", encoding="utf-8") as f:
            x = pd.read_csv(io.StringIO(f.read()), comment="#", index_col=0)
        x.index = pd.to_datetime(x.index, utc=True)
        cls.demand = x["demand"].dropna()
        cls.weather = x[["heating_degrees_f", "cooling_degrees_f"]].dropna()
        cls.res = dw.analyse(cls.demand, cls.weather, "America/New_York", "ISNE")

    def test_growth_is_the_weather_plus_the_rest(self):
        for m, g in self.res["years"][2022].items():
            self.assertIsNotNone(g, m)
            self.assertAlmostEqual(g["growth_pct"], g["weather_pct"] + g["unexplained_pct"], places=9)
            self.assertAlmostEqual(g["growth_pct"], 100 * (g["actual"] / g["base"] - 1), places=9)

    def test_a_year_the_fit_did_not_see_comes_back_near_zero_for_a_flat_grid(self):
        # New England's demand was flat across 2019 to 2021: each year left out of the fit comes back within 2 points
        for y, row in self.res["holdout"].items():
            self.assertLess(abs(row["energy"]["unexplained_pct"]), 2.0, y)
        self.assertLess(self.res["fit"]["oos_mape_pct"], 8.0)
        self.assertGreater(self.res["fit"]["oos_mape_pct"], self.res["fit"]["in_sample_mape_pct"])

    def test_a_year_made_of_the_fits_own_demand_has_nothing_left_unexplained(self):
        # the answer is known: 2022's demand replaced by what the fit expects (made up, for the arithmetic only)
        x, pred = self.res["x"], self.res["pred"]
        d = self.demand.copy()
        y22 = (x["year"] == 2022) & pred.notna() & x["demand"].notna()
        d.loc[y22[y22].index] = pred[y22]
        r = dw.analyse(d, self.weather, "America/New_York", "ISNE")
        self.assertLess(abs(r["years"][2022]["energy"]["unexplained_pct"]), 0.02)
        # only the mean is tested this way: a peak or a minimum of the fit's smooth hours is not a peak or a minimum of
        # metered ones, which is why each figure is compared with its own base (A with A0, P with P0)
        g = r["years"][2022]["overnight_min"]
        self.assertAlmostEqual(g["unexplained_pct"], 100 * (g["expected"] / g["base"] - g["expected"] / g["base_expected"]), places=6)

    def test_five_percent_more_demand_is_five_percent_more_unexplained(self):
        x = self.res["x"]
        d = self.demand.copy()
        y22 = x.index[x["year"] == 2022]
        d.loc[d.index.isin(y22)] *= 1.05                              # made up, for the arithmetic only
        r = dw.analyse(d, self.weather, "America/New_York", "ISNE")
        a, b = self.res["years"][2022]["energy"], r["years"][2022]["energy"]
        self.assertAlmostEqual(b["weather_pct"], a["weather_pct"], places=6)
        self.assertAlmostEqual(b["unexplained_pct"] - a["unexplained_pct"], 5.0 * a["actual"] / a["base"], places=6)

    def test_an_hour_that_fails_the_rule_is_used_for_nothing(self):
        x = self.res["x"]
        d = self.demand.copy()
        ts = pd.Timestamp("2022-07-20T18:00:00Z")
        d.loc[ts] = d.loc[ts] * 3                                     # an impossible hour, made up
        r = dw.analyse(d, self.weather, "America/New_York", "ISNE")
        self.assertTrue(np.isnan(r["x"].loc[ts, "demand"]))
        self.assertEqual(r["years"][2022]["energy"]["used"], self.res["years"][2022]["energy"]["used"] - 1)
        self.assertLess(r["years"][2022]["summer_peak"]["actual"], float(d.loc[ts]))
        self.assertEqual(int(x["demand"].notna().sum()) - 1, int(r["x"]["demand"].notna().sum()))

    def test_a_peak_is_never_more_certain_than_one_hour_of_the_fit(self):
        for m in dw.PEAKS:
            g = self.res["years"][2022][m]
            self.assertGreaterEqual(g["uncertainty_pct"], self.res["fit"]["oos_mape_pct"] - 1e-9)

    def test_a_finding_is_larger_than_its_uncertainty_and_inside_the_fits_weather(self):
        for m, g in self.res["years"][2022].items():
            self.assertEqual(g["finding"], abs(g["unexplained_pct"]) > g["uncertainty_pct"] and not g.get("outside", False), m)

    def test_a_figure_short_of_its_hours_is_not_written(self):
        w = self.weather[(self.weather.index < "2022-07-01T00:00:00Z") | (self.weather.index >= "2022-08-01T00:00:00Z")]   # a month of weather not held
        r = dw.analyse(self.demand, w, "America/New_York", "ISNE")
        self.assertIsNone(r["years"][2022]["energy"])
        self.assertIsNone(r["years"][2022]["summer_peak"])
        self.assertIsNotNone(r["years"][2022]["winter_peak"])

    def test_the_winter_before_the_weather_begins_is_not_a_base(self):
        self.assertIsNone(self.res["holdout"][2019]["winter_peak"])
        self.assertEqual(self.res["years"][2022]["winter_peak"]["base_years"], 2)

    def test_texas_hours_of_the_load_shed_are_out_of_the_fit_only(self):
        x = dw.frame(self.demand, self.weather, "America/Chicago", "ERCO")      # New England's hours under Texas's rule, to read the flag
        shed = x[x["shed"]]
        self.assertEqual((shed["day"].min(), shed["day"].max()), dw.SHED["ERCO"])
        self.assertEqual(len(shed), 120)
        self.assertFalse(dw.frame(self.demand, self.weather, "America/New_York", "ISNE")["shed"].any())


class Repository(unittest.TestCase):
    def test_no_em_dash_in_what_the_session_wrote(self):
        for p in NEW:
            path = os.path.join(ROOT, p)
            if not os.path.exists(path):
                continue
            with open(path, encoding="utf-8") as f:
                text = f.read()
            self.assertNotIn(chr(0x2014), text, p)
            self.assertNotIn(chr(0x2013), text, p)

    def test_the_page_is_in_review_and_says_what_the_remainder_is_not(self):
        with open(os.path.join(SITE, "lib", "release.ts"), encoding="utf-8") as f:
            self.assertIn('"/demand/weather": "review"', f.read())
        with open(os.path.join(SITE, "app", "_retired", "demand-weather", "page.tsx"), encoding="utf-8") as f:  # session 152: the page file as built is kept there; the view is components/demand/Weather.tsx (tests/test_session152.py)
            page = f.read()
        for words in ("What the remainder is not", "The warehouse cannot split them", "data-summary", "Census Bureau",   # session 129: the weights are the Bureau's
                      "@/data/demand_weather.json", "never interpolated across more than three hours", "robots: { index: false"):
            self.assertIn(words, page)
        with open(os.path.join(SITE, "scripts", "check-routes.mjs"), encoding="utf-8") as f:
            self.assertIn('"/demand/weather"', f.read())

    def test_the_method_quotes_noaas_terms(self):
        path = os.path.join(ROOT, "docs", "methods", "demand_weather.md")
        if not os.path.exists(path):
            self.skipTest("the method is written from the build's summary")
        with open(path, encoding="utf-8") as f:
            text = f.read()
        for words in ("Cite as: NOAA National Centers for Environmental Information (2001): Global Surface Hourly", "WMO Resolution 40",
                      "https://doi.org/10.25921/96dw-mb77", "The populations are the Census Bureau's", "What the remainder is not"):
            self.assertIn(words, text)


@unittest.skipUnless(os.path.exists(COPY), "the site's copy is written by demand_weather.py --snapshot")
class SiteCopy(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        with open(COPY, encoding="utf-8") as f:
            cls.raw = f.read()
        cls.f = json.loads(cls.raw)

    def test_it_is_plain_json_of_seven_grids(self):
        self.assertNotIn("NaN", self.raw)
        self.assertEqual(sorted(self.f["grids"]), sorted(dw.BAS))
        self.assertEqual(self.f["train"], list(dw.TRAIN))

    def test_every_figure_adds_up_and_is_read_by_the_rule(self):
        n = found = 0
        for ba, g in self.f["grids"].items():
            for y, row in g["years"].items():
                for m, v in row.items():
                    if v is None:
                        continue
                    n += 1
                    self.assertAlmostEqual(v["growth_pct"], v["weather_pct"] + v["unexplained_pct"], places=3)
                    self.assertGreaterEqual(v["used"] / v["wanted"], dw.NEAR)
                    self.assertEqual(v["finding"], abs(v["unexplained_pct"]) > v["uncertainty_pct"] and not v.get("outside", False), (ba, y, m))
                    if m in dw.PEAKS:
                        self.assertGreaterEqual(v["uncertainty_pct"], g["fit"]["oos_mape_pct"] - 1e-3)
                    found += v["finding"]
        self.assertGreater(n, 100)
        self.assertGreater(found, 0)

    def test_the_pull_stayed_under_its_ceiling_and_the_weights_add_up(self):
        w = self.f.get("weather")
        if not w:
            self.skipTest("built without the pull's summary")
        self.assertLessEqual(w["rows_read"], 3_000_000)
        tot = {}
        for s in w["stations"].values():
            tot[s["ba"]] = tot.get(s["ba"], 0) + s["weight"]
            self.assertGreaterEqual(s["agree"], ngw.AGREE)
            self.assertEqual(s["hours"], s["measured"] + s["interpolated"] + s["missing"])
        for ba, t in tot.items():
            self.assertAlmostEqual(t, 1.0, places=3)     # session 129: shares, not twentieths; the copy rounds each to four decimals


@unittest.skipUnless(os.path.exists(os.path.join(OUT, "noaa_grid_weather_hourly.csv")), "the tables are on the data machine")
class TablesAsBuilt(unittest.TestCase):
    def test_the_hourly_table(self):
        t = pd.read_csv(os.path.join(OUT, "noaa_grid_weather_hourly.csv"), comment="#", usecols=["entity", "variable", "ts_utc", "value", "x_interpolated"])
        self.assertFalse(t.duplicated(["entity", "variable", "ts_utc"]).any())
        self.assertEqual(sorted(t["variable"].unique()), ["cooling_degrees_f", "dew_point_f", "heating_degrees_f", "temperature_f"])
        self.assertEqual(t["entity"].nunique(), 7)
        self.assertTrue(t["x_interpolated"].between(0, 5).all())
        deg = t[t["variable"].isin(["cooling_degrees_f", "heating_degrees_f"])]["value"]
        self.assertGreaterEqual(float(deg.min()), 0.0)
        temp = t[t["variable"] == "temperature_f"]["value"]
        self.assertTrue(temp.between(-40, 125).all())

    def test_the_stations_table_and_the_registry(self):
        s = pd.read_csv(os.path.join(OUT, "noaa_grid_weather_stations.csv"), comment="#")
        w = s[s["variable"] == "weight"]
        self.assertEqual(len(w), 35)
        for ba, g in w.groupby("ba"):
            self.assertAlmostEqual(float(g["value"].sum()), 1.0, places=5)     # session 129: shares written to six decimals
        src = pd.read_csv(os.path.join(ROOT, "warehouse", "metadata", "sources.csv"), dtype=str, keep_default_na=False)
        for name in ("noaa:isd_lite", "noaa:lcd_v2", "erw:demand_weather"):
            row = src[src["source"] == name]
            self.assertEqual(len(row), 1, name)
            self.assertEqual(row.iloc[0]["license"], "public")
        cov = pd.read_csv(os.path.join(ROOT, "warehouse", "metadata", "coverage.csv"), dtype=str, keep_default_na=False)
        for name in ("noaa_grid_weather_stations", "noaa_grid_weather_hourly", "noaa_grid_weather_daily", "eia930_demand_weather"):
            row = cov[cov["table"] == name]
            self.assertEqual(len(row), 1, name)
            self.assertEqual((row.iloc[0]["validator_status"], row.iloc[0]["license"]), ("pass", "public"))

    def test_nothing_of_it_reaches_a_live_page(self):
        # the home page counts the catalogue's public tables and rows, and /terms lists the registry: both are live
        sys.path.insert(0, os.path.join(ROOT, "warehouse", "supabase"))
        import load
        for name in ("noaa_grid_weather_stations", "noaa_grid_weather_hourly", "noaa_grid_weather_daily", "eia930_demand_weather"):
            self.assertIn(name, load.LIVE["catalogue_hold"])
            self.assertNotIn(name, load.LIVE["review_hold"])
        for name in ("noaa:isd_lite", "noaa:lcd_v2", "erw:demand_weather"):
            self.assertIn(name, load.LIVE["sources_hold"])


if __name__ == "__main__":
    unittest.main()

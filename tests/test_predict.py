"""The ERW forecast (chain 730, session 10600): the rules a forecast and its files must keep.

1. Nothing is known early: a forecast for day T, and its band, do not move when any hour after the information cut
   (the last whole day held, T - h) is changed.
2. Every place's file has its score: each place of index.json has its demand rows in scores.json for every method,
   and a summary in its own file.
3. A held series holds no number: a series whose status is not "shown" has no figure in its file, the index or the
   scores.
4. The ledger is never overwritten: a second run for the same place and day adds nothing and changes nothing.
5. Every file says what it is: tier derived, "ERW forecast".
"""
import datetime as dt
import io
import json
import os
import sys
import tempfile
import unittest

import numpy as np
import pandas as pd

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
sys.path.append(os.path.join(ROOT, "warehouse", "predict"))
import predict_demand as demand  # noqa: E402

SITE = os.path.join(ROOT, "site", "data", "predict")


def synthetic(days=900, tz="America/Chicago", seed=7):
    """A demand-like hourly series (a daily and weekly shape, a yearly wave, noise), fixed seed: no warehouse needed."""
    rng = np.random.default_rng(seed)
    start = pd.Timestamp("2023-01-01", tz=tz).tz_convert("UTC")
    idx = pd.date_range(start, periods=days * 24, freq="h")
    loc = idx.tz_convert(tz)
    h = loc.hour.to_numpy()
    dow = loc.dayofweek.to_numpy()
    doy = loc.dayofyear.to_numpy()
    v = 30000 + 6000 * np.sin(2 * np.pi * (h - 6) / 24) + 3000 * np.cos(2 * np.pi * doy / 365.25) - 2500 * (dow >= 5) + rng.normal(0, 600, len(idx))
    return pd.Series(v, index=idx)


class NothingKnownEarly(unittest.TestCase):
    def check(self, h):
        tz = "America/Chicago"
        s = synthetic()
        base = demand.place_forecasts(s, tz, h=h)
        M = base["M"]
        i = len(M) - h - 40                     # a target day well inside the backtest
        T = M.index[i]
        cut_end = (T - pd.Timedelta(days=h - 1)).tz_localize(tz).tz_convert("UTC")   # the first hour after day A
        s2 = s.copy()
        s2[s2.index >= cut_end] = s2[s2.index >= cut_end] * 1.5 + 999.0
        moved = demand.place_forecasts(s2, tz, h=h)
        for m in demand.METHODS:
            for arr in ("P", "lo", "hi"):
                a, b = base[arr][m][i], moved[arr][m][i]
                np.testing.assert_allclose(a, b, rtol=1e-9, equal_nan=True, err_msg=f"{m} {arr} moved with hours after the cut (h={h})")
        # and the hours before the cut do move it (the test is not empty)
        s3 = s.copy()
        early = (s3.index < cut_end) & (s3.index >= cut_end - pd.Timedelta(days=3))
        s3[early] = s3[early] * 1.5
        moved3 = demand.place_forecasts(s3, tz, h=h)
        self.assertFalse(np.allclose(base["P"]["regression"][i], moved3["P"]["regression"][i], equal_nan=True))

    def test_day_ahead(self):
        self.check(2)

    def test_three_days(self):
        self.check(3)

    def test_seven_days(self):
        self.check(7)

    def test_horizon_beyond_a_week_refused(self):
        with self.assertRaises(ValueError):
            demand.features(demand.matrix(demand.local_frame(synthetic(60), "UTC")), 8)

    def test_repeatable_to_the_last_digit(self):
        s = synthetic(500)
        a = demand.place_forecasts(s, "America/New_York", h=2)["P"]["regression"]
        b = demand.place_forecasts(s, "America/New_York", h=2)["P"]["regression"]
        self.assertTrue(np.array_equal(a, b, equal_nan=True))

    def test_clock_change_days(self):
        f = demand.day_hours("America/Chicago", pd.Timestamp("2026-03-08"))
        self.assertEqual(len(f), 23)
        f = demand.day_hours("America/Chicago", pd.Timestamp("2026-11-01"))
        self.assertEqual(len(f), 25)


class PriceNothingKnownEarly(unittest.TestCase):
    def test_price_after_its_cut_and_demand_after_its_cut_change_nothing(self):
        import predict_price as price
        tz = "America/Chicago"
        d = synthetic(1000, tz, seed=3)
        rng = np.random.default_rng(11)
        p = pd.Series(30 + 0.002 * (d.to_numpy() - 30000) + rng.normal(0, 4, len(d)), index=d.index)
        gas = pd.Series(3.0 + 0.001 * np.arange(1100), index=pd.date_range("2022-12-01", periods=1100, freq="D"))
        hp, hd = 1, 3
        base = price.place_forecasts(p, tz, d, tz, gas, hp=hp, hd=hd)
        M = base["M"]
        i = len(M) - hp - 30
        T = M.index[i]
        p_cut = (T - pd.Timedelta(days=hp - 1)).tz_localize(tz).tz_convert("UTC")
        d_cut = (T - pd.Timedelta(days=hd - 1)).tz_localize(tz).tz_convert("UTC")
        p2, d2 = p.copy(), d.copy()
        p2[p2.index >= p_cut] += 500.0
        d2[d2.index >= d_cut] *= 1.4
        g2 = gas.copy()
        g2[g2.index > T - pd.Timedelta(days=1 + price.GAS_LAG_DAYS)] += 10.0
        moved = price.place_forecasts(p2, tz, d2, tz, g2, hp=hp, hd=hd)
        for m in price.METHODS:
            for arr in ("P", "lo", "hi"):
                np.testing.assert_allclose(base[arr][m][i], moved[arr][m][i], rtol=1e-9, equal_nan=True, err_msg=f"price {m} {arr} moved")
        self.assertTrue(np.isfinite(base["P"]["regression"][i]).all())


class WeatherForecastNothingKnownEarly(unittest.TestCase):
    """Method note section 19: a forecast hour enters target day D only from an issue no later than 20:00 UTC on D-1;
    of those, the latest; and the observed weather of day D and after never moves the forecast for D."""

    def rows(self, tz, day, vintages_values):
        hours = demand.day_hours(tz, day)["ts"]
        out = []
        for vt, val in vintages_values:
            for t in hours:
                out.append({"airport": "KXXX", "ts": t, "vintage": pd.Timestamp(vt, tz="UTC"), "value": val})
        return pd.DataFrame(out)

    def test_late_issue_never_used(self):
        import predict_weather as pw
        tz = "America/Chicago"
        day = pd.Timestamp("2026-11-10")
        days = pd.date_range("2026-11-08", "2026-11-12", freq="D")
        r = self.rows(tz, day, [("2026-11-09T12:00:00", 40.0), ("2026-11-09T19:59:00", 50.0), ("2026-11-09T20:01:00", 99.0)])
        F, V = pw.forecast_matrix(r, "KXXX", tz, days)
        i = list(days).index(day)
        self.assertTrue(np.all(F[i] == 50.0))
        self.assertEqual(pd.Timestamp(V[i]), pd.Timestamp("2026-11-09T19:59:00"))
        r2 = self.rows(tz, day, [("2026-11-09T20:30:00", 99.0)])
        F2, _ = pw.forecast_matrix(r2, "KXXX", tz, days)
        self.assertTrue(np.isnan(F2[i]).all())

    def test_observed_weather_of_the_day_moves_nothing(self):
        tz = "America/Chicago"
        s = synthetic(800, tz, seed=5)
        M = demand.place_forecasts(s, tz, h=2)["M"]
        idx = pd.date_range(s.index.min(), s.index.max() + pd.Timedelta(days=3), freq="h")
        rng = np.random.default_rng(2)
        temp = pd.Series(60 + 20 * np.sin(np.arange(len(idx)) * 2 * np.pi / 24) + rng.normal(0, 3, len(idx)), index=idx)
        F = np.full((len(M), 24), np.nan)
        i = len(M) - 30
        F[i] = 55.0 + np.arange(24) * 0.5
        a, _ = demand.regression_weather_forecast(M, temp, F, tz, 2)
        T = M.index[i]
        cut = (T - pd.Timedelta(days=1)).tz_localize(tz).tz_convert("UTC")      # the first hour after day A = T - 2
        t2 = temp.copy()
        t2[t2.index >= cut] += 25.0
        b, _ = demand.regression_weather_forecast(M, t2, F, tz, 2)
        np.testing.assert_allclose(a[i], b[i], rtol=1e-9)
        self.assertTrue(np.isfinite(a[i]).all())


class WindSolarNothingKnownEarly(unittest.TestCase):
    """predict_wind_solar.md: the forecast for day T and its band read only output through day T - 2."""

    def test_output_after_the_cut_moves_nothing(self):
        import predict_ws as ws
        tz = "America/Chicago"
        s = synthetic(700, tz, seed=9).clip(lower=0) / 3.0
        base = ws.place_forecasts(s, tz)
        M = base["M"]
        i = len(M) - ws.H - 30
        T = M.index[i]
        cut = (T - pd.Timedelta(days=ws.H - 1)).tz_localize(tz).tz_convert("UTC")
        s2 = s.copy()
        s2[s2.index >= cut] = s2[s2.index >= cut] * 2.0 + 500.0
        moved = ws.place_forecasts(s2, tz)
        for m in ws.METHODS:
            for arr in ("P", "lo", "hi"):
                np.testing.assert_allclose(base[arr][m][i], moved[arr][m][i], rtol=1e-9, equal_nan=True, err_msg=f"{m} {arr}")
        self.assertTrue(np.isfinite(base["P"]["regression"][i]).all())
        self.assertTrue((base["P"]["regression"][i] >= 0).all())

    def test_ledger_never_overwritten(self):
        import wind_solar
        with tempfile.TemporaryDirectory() as d:
            row = {"fuel": "wind", "place": "region-tex", "target_day": "2026-11-28", "ts_utc": "2026-11-28T06:00:00Z", "local_hour": 0,
                   "made_utc": "2026-11-27T20:00:00Z", "inputs_through_utc": "2026-11-26T05:00:00Z", "horizon_days": 2, "method": "regression",
                   "erw": 100.0, "lo": 50.0, "hi": 150.0}
            self.assertEqual(wind_solar.append_ledger(d, [row]), 1)
            before = open(os.path.join(d, "ledger_wind_solar.csv"), encoding="utf-8").read()
            self.assertEqual(wind_solar.append_ledger(d, [dict(row, erw=999.0)]), 0)
            self.assertEqual(open(os.path.join(d, "ledger_wind_solar.csv"), encoding="utf-8").read(), before)


class RealTimePriceNothingKnownEarly(unittest.TestCase):
    """predict_price.md section 7: the forecast for day T reads real-time prices through T - 2 and day-ahead prices
    through day T; a later real-time price or a day-ahead price of a later day moves nothing."""

    def test_after_the_cuts_nothing_moves(self):
        import predict_rt as rtm
        tz = "America/Chicago"
        d = synthetic(900, tz, seed=4)
        rng = np.random.default_rng(8)
        da = pd.Series(30 + 0.001 * (d.to_numpy() - 30000) + rng.normal(0, 3, len(d)), index=d.index)
        rt = da + rng.normal(0, 6, len(d))
        base = rtm.place_forecasts(rt, da, tz)
        M = base["M"]
        i = len(M) - rtm.H - 30
        T = M.index[i]
        rt_cut = (T - pd.Timedelta(days=rtm.H - 1)).tz_localize(tz).tz_convert("UTC")
        da_cut = (T + pd.Timedelta(days=1)).tz_localize(tz).tz_convert("UTC")
        rt2, da2 = rt.copy(), da.copy()
        rt2[rt2.index >= rt_cut] += 400.0
        da2[da2.index >= da_cut] += 400.0
        moved = rtm.place_forecasts(rt2, da2, tz)
        for m in rtm.METHODS + ["day_ahead"]:
            for arr in ("P", "lo", "hi"):
                np.testing.assert_allclose(base[arr][m][i], moved[arr][m][i], rtol=1e-9, equal_nan=True, err_msg=f"{m} {arr}")
        self.assertTrue(np.isfinite(base["P"]["regression"][i]).all())


@unittest.skipUnless(os.path.exists(os.path.join(SITE, "rt_price.json")), "rt_price.json is not built here")
class TheRealTimeFile(unittest.TestCase):
    def test_every_hub_has_its_scores_beside_the_day_ahead_price(self):
        doc = load("rt_price.json")
        self.assertEqual(doc["label"], "ERW forecast")
        cols = doc["rows_columns"]
        rows = {(r[0], r[1], r[2], r[3], r[4]): dict(zip(cols, r)) for r in doc["rows"]}
        for h in doc["hubs"]:
            for m in ("erw", "day_ahead", "yesterday", "regression"):
                r = rows[(f"hub-{h['grid']}", "rt_price", m, "all", "")]
                self.assertEqual(r["hours"], h["summary"]["backtest"]["hours"])
                self.assertAlmostEqual(r["mae"], h["summary"]["backtest"]["mae"][m], places=2)
            self.assertNotEqual(h["method"], "day_ahead")

    def test_the_hubs_added_come_after_the_three(self):
        """Session 10603: the file's hubs are the three of section 7 first, then the four added, each with its entity."""
        import predict_rt as rtm
        doc = load("rt_price.json")
        self.assertEqual([h["grid"] for h in doc["hubs"]], list(rtm.RT_HUBS))
        self.assertEqual([h["grid"] for h in doc["hubs"]][:3], ["ercot", "spp", "caiso"])
        self.assertEqual({h["grid"]: h["hub"] for h in doc["hubs"]}, rtm.RT_HUBS)
        cuts = {r[3] for r in doc["rows"]}
        self.assertFalse(cuts - set(doc["cuts"]), cuts - set(doc["cuts"]))

    def test_the_longer_backtest_adds_up_and_changes_nothing_above(self):
        """Session 10603: the years partition the longer backtest's hours, its MAE is their hour-weighted mean, it ends
        where the backtest ends, and it starts no later; the method is the one chosen now."""
        doc = load("rt_price.json")
        for h in doc["hubs"]:
            lb = h["long_backtest"]
            self.assertEqual(lb["method"], h["method"])
            self.assertEqual(sum(y["hours"] for y in lb["by_year"]), lb["all"]["hours"])
            self.assertEqual(lb["all"]["last_day"], h["summary"]["backtest"]["last_day"])
            self.assertLessEqual(lb["all"]["first_day"], h["summary"]["backtest"]["first_day"])
            self.assertGreaterEqual(lb["all"]["hours"], h["summary"]["backtest"]["hours"])
            for m in ("erw", "day_ahead", "yesterday", "regression"):
                w = sum(y["mae"][m] * y["hours"] for y in lb["by_year"]) / lb["all"]["hours"]
                self.assertAlmostEqual(w, lb["all"]["mae"][m], delta=0.01 * len(lb["by_year"]), msg=(h["grid"], m))
            self.assertEqual([y["year"] for y in lb["by_year"]], sorted(y["year"] for y in lb["by_year"]))


@unittest.skipUnless(os.path.exists(os.path.join(SITE, "long_backtest.json")), "long_backtest.json is not built here")
class TheLongerBacktest(unittest.TestCase):
    def test_years_add_up_and_the_method_is_the_place_files(self):
        """Session 10603: every place of the run; the years partition the span's hours; its MAE is their hour-weighted
        mean; the method is the place file's (unless the file draws tomorrow from the ledger); it starts no later than
        the place file's backtest and ends where it ends."""
        import importlib.util
        spec = importlib.util.spec_from_file_location("predict_run_long", os.path.join(ROOT, "warehouse", "predict", "run.py"))
        run = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(run)
        doc = load("long_backtest.json")
        self.assertEqual(doc["label"], "ERW forecast")
        self.assertEqual([p["place"] for p in doc["places"]], run.PLACES)
        for p in doc["places"]:
            pf = load(p["place"] + ".json")["series"]["demand"]
            same_days = p["all"]["last_day"] == pf["summary"]["backtest"]["last_day"]
            if same_days and not pf.get("tomorrow_from"):
                self.assertEqual(p["method"], pf["method"], p["place"])
            ys = p["by_year"]
            self.assertEqual(sum(y["hours"] for y in ys), p["all"]["hours"], p["place"])
            for m in ("erw", "yesterday", "week_ago", "regression", "regression_recent"):
                w = sum(y["mae"][m] * y["hours"] for y in ys) / p["all"]["hours"]
                self.assertAlmostEqual(w, p["all"]["mae"][m], delta=0.01 * len(ys), msg=(p["place"], m))
            self.assertLessEqual(p["all"]["first_day"], pf["summary"]["backtest"]["first_day"])
            # session 10000 (chain 701): long_backtest.json is rebuilt on Sundays (predict data request 15) and the place
            # files every day, so the long backtest ends no later than the place files, within the week between runs
            import datetime as _dt
            self.assertLessEqual(p["all"]["last_day"], pf["summary"]["backtest"]["last_day"], p["place"])
            gap = (_dt.date.fromisoformat(pf["summary"]["backtest"]["last_day"]) - _dt.date.fromisoformat(p["all"]["last_day"])).days
            self.assertLessEqual(gap, 8, p["place"])


@unittest.skipUnless(os.path.exists(os.path.join(SITE, "long_price.json")), "long_price.json is not built here")
class TheLongerPriceBacktest(unittest.TestCase):
    def test_years_add_up_and_it_ends_where_the_backtest_ends(self):
        """Session 10603: the ten price places; the years partition the span's hours and their MAE is its hour-weighted
        mean; it starts no later than the published backtest of the same place and ends where it ends."""
        doc = load("long_price.json")
        hubs = {h["place"]: h for h in load("price_hubs.json")["hubs"]} if os.path.exists(os.path.join(SITE, "price_hubs.json")) else {}
        self.assertEqual(len(doc["places"]), 10)
        for p in doc["places"]:
            ys = p["by_year"]
            self.assertEqual(sum(y["hours"] for y in ys), p["all"]["hours"], p["place"])
            for m in ("erw", "yesterday", "week_ago", "regression"):
                w = sum(y["mae"][m] * y["hours"] for y in ys) / p["all"]["hours"]
                self.assertAlmostEqual(w, p["all"]["mae"][m], delta=0.01 * len(ys), msg=(p["place"], m))
            pub = hubs.get(p["place"]) or load(p["place"] + ".json")["series"]["price"]
            self.assertLessEqual(p["all"]["first_day"], pub["summary"]["backtest"]["first_day"], p["place"])
            # session 10000 (chain 701): long_price.json is rebuilt on Sundays (predict data request 16), the backtest it
            # is set beside every day: it ends no later, within the week between its runs
            self.assertLessEqual(p["all"]["last_day"], pub["summary"]["backtest"]["last_day"], p["place"])
            gap = (dt.date.fromisoformat(pub["summary"]["backtest"]["last_day"]) - dt.date.fromisoformat(p["all"]["last_day"])).days
            self.assertLessEqual(gap, 8, p["place"])


@unittest.skipUnless(os.path.exists(os.path.join(SITE, "price_hubs.json")), "price_hubs.json is not built here")
class ThePriceHubsFile(unittest.TestCase):
    def test_every_hub_has_its_scores_and_the_rule_chose(self):
        """Session 10603: each hub's series agrees with its score rows, the method is the lowest error of the last two
        years, the band holds its forecast, and the hubs are those of predict_rt.MORE_HUBS with their grid's demand."""
        import predict_rt as rtm
        doc = load("price_hubs.json")
        self.assertEqual(doc["tier"], "derived")
        self.assertEqual(doc["label"], "ERW forecast")
        self.assertEqual([h["grid"] for h in doc["hubs"]], list(rtm.MORE_HUBS))
        self.assertFalse({r[3] for r in doc["rows"]} - set(doc["cuts"]))
        cols = doc["rows_columns"]
        rows = {(r[0], r[2], r[3], r[4]): dict(zip(cols, r)) for r in doc["rows"]}
        for h in doc["hubs"]:
            self.assertEqual(h["hub"], rtm.MORE_HUBS[h["grid"]])
            self.assertEqual(h["demand_place"], "ba-ciso" if h["grid"].startswith("caiso") else "ba-erco")
            maes = h["method_mae_last_2_years"]
            self.assertEqual(maes[h["method"]], min(maes.values()), h["grid"])
            for m in ("erw", "yesterday", "week_ago"):
                r = rows[(h["place"], m, "all", "")]
                self.assertEqual(r["hours"], h["summary"]["backtest"]["hours"], (h["grid"], m))
                self.assertAlmostEqual(r["mae"], h["summary"]["backtest"]["mae"][m], places=2)
            self.assertAlmostEqual(rows[(h["place"], "erw", "last_2_years", "")]["mae"], maes[h["method"]], places=2)
            for t in h["tomorrow"] or []:
                self.assertLessEqual(t[3], t[4])
            self.assertTrue(0 <= h["band_coverage_pct"] <= 100)


@unittest.skipUnless(os.path.exists(os.path.join(SITE, "wind_solar.json")), "wind_solar.json is not built here")
class TheWindSolarFile(unittest.TestCase):
    def test_every_place_and_fuel_has_its_scores_and_the_operator_where_held(self):
        doc = load("wind_solar.json")
        self.assertEqual(doc["tier"], "derived")
        self.assertEqual(doc["label"], "ERW forecast")
        cols = doc["rows_columns"]
        rows = [dict(zip(cols, r)) for r in doc["rows"]]
        for p in doc["places"]:
            for fuel, b in p["fuels"].items():
                if b["status"] != "shown":
                    continue
                got = {r["method"] for r in rows if r["place"] == p["place"] and r["fuel"] == fuel and r["cut"] == "all" and r["mae_mw"] is not None}
                self.assertEqual(got, {"erw", "yesterday", "profile7", "regression"}, (p["place"], fuel))
                maes = {k: v for k, v in b["method_mae_last_2_years"].items() if v is not None}
                self.assertEqual(maes[b["method"]], min(maes.values()), (p["place"], fuel))   # a tie (no output) may go either way
                if b["operator"]:
                    w = b["summary"]["with_operator"]
                    want = [r for r in rows if r["place"] == p["place"] and r["fuel"] == fuel and r["cut"] == "with_operator" and r["method"] == "operator"]
                    self.assertEqual(want[0]["hours"], w["hours"])
                    self.assertAlmostEqual(want[0]["mae_mw"], w["mae_mw"]["operator"], places=1)
                else:
                    op = [r for r in rows if r["place"] == p["place"] and r["fuel"] == fuel and r["method"] == "operator"]
                    self.assertTrue(op and all(r["mae_mw"] is None and r["held"] for r in op))
                if b["tomorrow"]:
                    self.assertEqual(b["horizon_days"], 2)

    def test_a_day_not_forecast_says_why_and_every_entry_has_its_page(self):
        """Session 10603 (chain 720's requests 11 and 12): no tomorrow of nulls only, a reason where there is no tomorrow,
        every entry shown for a place file that exists, and every cut of the rows has its words."""
        doc = load("wind_solar.json")
        index = {p["place"] for p in load("index.json")["places"]} if os.path.exists(os.path.join(SITE, "index.json")) else None
        cuts = {r[3] for r in doc["rows"]}
        self.assertFalse(cuts - set(doc["cuts"]), cuts - set(doc["cuts"]))
        for p in doc["places"]:
            self.assertTrue(p["shown_for"])
            if index is not None:
                self.assertFalse(set(p["shown_for"]) - index, p["place"])
            for fuel, b in p["fuels"].items():
                if b["status"] != "shown":
                    continue
                if b["tomorrow"] is None:
                    self.assertTrue(b["tomorrow_held"], (p["place"], fuel))
                else:
                    self.assertTrue(any(r[2] is not None for r in b["tomorrow"]), (p["place"], fuel))


class Ledger(unittest.TestCase):
    def test_never_overwritten(self):
        import importlib.util
        spec = importlib.util.spec_from_file_location("predict_run", os.path.join(ROOT, "warehouse", "predict", "run.py"))
        run = importlib.util.module_from_spec(spec)   # its own name: other tests import modules named "run"
        spec.loader.exec_module(run)
        with tempfile.TemporaryDirectory() as d:
            row = {"series": "demand", "place": "region-tex", "target_day": "2026-11-27", "ts_utc": "2026-11-27T06:00:00Z", "local_hour": 0,
                   "made_utc": "2026-11-26T20:00:00Z", "inputs_through_utc": "2026-11-26T05:00:00Z", "horizon_days": 2, "method": "regression",
                   "erw": 1.0, "lo": 0.5, "hi": 1.5}
            self.assertEqual(run.append_ledger(d, [row]), 1)
            with open(run.ledger_path(d), encoding="utf-8") as f:
                first = f.read()
            changed = dict(row, erw=2.0, made_utc="2026-11-26T21:00:00Z")
            self.assertEqual(run.append_ledger(d, [changed]), 0)
            with open(run.ledger_path(d), encoding="utf-8") as f:
                self.assertEqual(f.read(), first)


def load(name):
    with open(os.path.join(SITE, name), encoding="utf-8") as f:
        return json.load(f)


def numbers(o):
    """Every number in a nested structure (booleans aside)."""
    if isinstance(o, bool) or o is None:
        return []
    if isinstance(o, (int, float)):
        return [o]
    if isinstance(o, dict):
        return [x for v in o.values() for x in numbers(v)]
    if isinstance(o, list):
        return [x for v in o for x in numbers(v)]
    return []


@unittest.skipUnless(os.path.exists(os.path.join(SITE, "index.json")), "the forecast's page files are not built here")
class TheFiles(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.index = load("index.json")
        cls.scores = load("scores.json")
        cls.places = {p["place"]: load(p["file"]) for p in cls.index["places"]}

    def test_what_they_are(self):
        for doc in [self.index, self.scores] + list(self.places.values()):
            self.assertEqual(doc["tier"], "derived")
            self.assertEqual(doc["label"], "ERW forecast")
            self.assertNotIn("example", doc)

    def test_every_place_has_its_score(self):
        cols = self.scores["rows_columns"]
        rows = [dict(zip(cols, r)) for r in self.scores["rows"]]
        methods = {m["id"] for m in self.scores["methods"]}
        for p in self.index["places"]:
            if p["series"]["demand"]["status"] != "shown":
                continue
            got = {r["method"] for r in rows if r["place"] == p["place"] and r["series"] == "demand" and r["cut"] == "all" and r["mae"] is not None}
            self.assertEqual(got, methods, p["place"])
            s = self.places[p["place"]]["series"]["demand"]
            self.assertIsNotNone(s["summary"]["backtest"]["mae"]["erw"], p["place"])

    def test_the_places_added_follow_their_rule(self):
        """Session 10603: every place of the run has its file; each authority added runs to the last day the 29 places
        reach (within a week) and its backtest scores at least two years; none is one of the 29."""
        import importlib.util
        spec = importlib.util.spec_from_file_location("predict_run_places", os.path.join(ROOT, "warehouse", "predict", "run.py"))
        run = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(run)
        self.assertEqual(set(self.places), set(run.PLACES))
        added = [f"ba-{b.lower()}" for b in run.MORE_BAS]
        self.assertFalse(set(added) & set(run.CORE_PLACES))
        last = max(self.places[p]["series"]["demand"]["summary"]["backtest"]["last_day"] for p in run.CORE_PLACES)
        for p in added:
            b = self.places[p]["series"]["demand"]["summary"]["backtest"]
            gap = (dt.date.fromisoformat(last) - dt.date.fromisoformat(b["last_day"])).days
            self.assertLessEqual(gap, 7, p)   # a filing a few days late is ordinary (SCEG, two days on 28 November); a week is not
            span = (dt.date.fromisoformat(b["last_day"]) - dt.date.fromisoformat(b["first_day"])).days
            self.assertGreaterEqual(span, 730, p)

    def test_each_file_agrees_with_the_report_card(self):
        """The check of each file's figures: a place file's summary of the backtest is the score file's row 'all' for
        the same method, the band's coverage lies in 0 to 100, and every history row's band holds its own forecast."""
        cols = self.scores["rows_columns"]
        rows = {(r[0], r[1], r[2], r[3], r[4]): dict(zip(cols, r)) for r in self.scores["rows"]}
        for p in self.index["places"]:
            for name in ("demand", "price"):
                s = self.places[p["place"]]["series"][name]
                if s["status"] != "shown":
                    continue
                for m in ("erw", "yesterday", "week_ago"):
                    want = rows[(p["place"], name, m, "all", "")]
                    got = s["summary"]["backtest"]
                    self.assertEqual(got["hours"], want["hours"], (p["place"], name, m))
                    self.assertAlmostEqual(got["mae"][m], want["mae"], places=2, msg=(p["place"], name, m))
                self.assertTrue(0 <= s["band_coverage_pct"] <= 100, p["place"])
                for row in s["history"]:
                    erw, lo, hi = row[5], row[6], row[7]
                    if None not in (erw, lo, hi) and row[4] == "backtest":
                        self.assertTrue(lo <= erw <= hi, (p["place"], name, row[0]))

    def test_every_place_has_its_peak(self):
        cols = self.scores["rows_columns"]
        rows = [dict(zip(cols, r)) for r in self.scores["rows"] if r[1] == "demand_peak"]
        for p in self.index["places"]:
            got = {r["method"] for r in rows if r["place"] == p["place"] and r["cut"] == "all" and r["mae"] is not None}
            self.assertEqual(got, {m["id"] for m in self.scores["methods"]}, p["place"])
            pk = self.places[p["place"]]["series"]["demand"]["peak"]
            self.assertIsNotNone(pk["backtest"]["methods"]["erw"]["mae"], p["place"])

    @unittest.skipUnless(os.path.exists(os.path.join(SITE, "ahead.json")), "ahead.json is not built here")
    def test_further_ahead_shown_only_where_it_beats_the_week_ago_hour(self):
        docs = [load("ahead.json")]
        if os.path.exists(os.path.join(SITE, "ahead_more.json")):
            # session 10603: the 35 authorities in a file of their own, under the same rule
            docs.append(load("ahead_more.json"))
        for doc in docs:
            self.check_ahead(doc)

    def check_ahead(self, doc):
        self.assertEqual(doc["tier"], "derived")
        for p in doc["places"]:
            for h in p["horizons"]:
                m = h["last_2_years"]["mae"]
                meth = h.get("method", "regression")
                beats = m[meth] is not None and m["week_ago"] is not None and m[meth] < m["week_ago"]
                self.assertEqual(h["shown"], beats, (p["place"], h["horizon_days"]))
                if h["shown"]:
                    # a horizon shown by the rule has its forecast, or says why the day could not be forecast (session 10603)
                    self.assertTrue(h["forecast"] or h.get("forecast_held"), (p["place"], h["horizon_days"]))
                    self.assertTrue(all(x[2] is not None for x in (h["forecast"] or [])), (p["place"], h["horizon_days"]))
                else:
                    self.assertIsNone(h["forecast"])
                    self.assertTrue(h["held"])

    def test_the_weather_known_line_is_never_the_forecast(self):
        cols = self.scores["rows_columns"]
        for r in self.scores["rows"]:
            r = dict(zip(cols, r))
            if r["method"] == "with_weather_known":
                self.assertEqual(r["series"], "demand_weather_known", r)
        self.assertNotIn("with_weather_known", {m["id"] for m in self.scores["methods"]})
        for p in self.index["places"]:
            for s in p["series"].values():
                self.assertNotEqual(s["method"], "with_weather_known")
            d = self.places[p["place"]]["series"]["demand"]
            self.assertNotEqual(d["method"], "with_weather_known")
            self.assertNotIn("with_weather_known", d["history_columns"] + d["tomorrow_columns"])

    def test_the_operator_filing_check_follows_its_rule(self):
        """Method note section 18: a month is flagged exactly when its filed forecast is more than 5 percent from the
        demand; the sound months' summary is the score file's cut operator_sound_last_2_years; the check never moves
        the choice of method (the file's method is still the lowest error of method_mae_last_2_years)."""
        cols = self.scores["rows_columns"]
        rows = {(r[0], r[1], r[2], r[3], r[4]): dict(zip(cols, r)) for r in self.scores["rows"]}
        for p in self.index["places"]:
            d = self.places[p["place"]]["series"]["demand"]
            fc = d.get("operator_filing")
            self.assertIsNotNone(fc, p["place"])
            for month, hours, pct, flagged in fc["months"]:
                # the flag is set on the exact ratio and the file prints it to one decimal: a month within 0.05 of the
                # line may read 95.0 and be flagged
                if abs(abs(pct - 100) - fc["tolerance_pct"]) > 0.05:
                    self.assertEqual(flagged, abs(pct - 100) > fc["tolerance_pct"], (p["place"], month))
                self.assertGreater(hours, 0)
            self.assertEqual(fc["months_flagged"], sum(1 for m in fc["months"] if m[3]))
            sm = fc["sound_last_2_years"]
            for m in ("erw", "operator"):
                want = rows.get((p["place"], "demand", m, "operator_sound_last_2_years", ""))
                self.assertIsNotNone(want, (p["place"], m))
                self.assertEqual(sm["hours"], want["hours"], (p["place"], m))
                if want["hours"]:
                    self.assertAlmostEqual(sm["mae"][m], want["mae"], places=2, msg=(p["place"], m))
            maes = {k: v for k, v in d["method_mae_last_2_years"].items() if v is not None}
            # when tomorrow is the ledger's first making (contract, 21:45 UTC on 26 November), `method` is that
            # making's and `tomorrow_from` names the method chosen now
            chosen = d["tomorrow_from"].rsplit("the method chosen now is ", 1)[1].strip(" .") if d.get("tomorrow_from") else d["method"]
            self.assertEqual(maes[chosen], min(maes.values()), p["place"])

    def test_the_share_inside_each_band(self):
        """The share of past hours inside each band (Samuel's order of 27 November 2026): the detail agrees with the
        headline share, and inside, below and above make the whole."""
        docs = [(p["place"], name, self.places[p["place"]]["series"][name]) for p in self.index["places"] for name in ("demand", "price")]
        if os.path.exists(os.path.join(SITE, "rt_price.json")):
            docs += [(h["grid"], "rt_price", h) for h in load("rt_price.json")["hubs"]]
        if os.path.exists(os.path.join(SITE, "wind_solar.json")):
            docs += [(p["place"], f, b) for p in load("wind_solar.json")["places"] for f, b in p["fuels"].items()]
        for place, name, s in docs:
            if s.get("status") != "shown":
                continue
            bc = s["band_coverage"]
            self.assertIsNotNone(bc, (place, name))
            self.assertAlmostEqual(bc["inside_pct"], s["band_coverage_pct"], delta=0.11, msg=(place, name))
            self.assertAlmostEqual(bc["inside_pct"] + bc["below_pct"] + bc["above_pct"], 100.0, delta=0.21, msg=(place, name))
            self.assertEqual(len(bc["by_local_hour_inside_pct"]), 24)
            self.assertEqual(sum(m[1] for m in bc["by_month"]), bc["hours"])

    def test_net_demand_agrees_with_the_report_card(self):
        """Method note section 20: every region and ERCO carries net demand, and since session 10603 (section 26) every
        place run.net_place gives a wind and solar entry; its summary is the score file's rows."""
        import importlib.util
        spec = importlib.util.spec_from_file_location("predict_run_net", os.path.join(ROOT, "warehouse", "predict", "run.py"))
        run = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(run)
        cols = self.scores["rows_columns"]
        rows = {(r[0], r[1], r[2], r[3], r[4]): dict(zip(cols, r)) for r in self.scores["rows"]}
        for p in self.index["places"]:
            nd = self.places[p["place"]]["series"]["demand"].get("net_demand")
            if run.net_place(p["place"]) is None:
                self.assertIsNone(nd, p["place"])
                continue
            self.assertIsNotNone(nd, p["place"])
            if nd["status"] != "shown":
                continue
            sm = nd["last_2_years"]
            for m in ("erw", "yesterday"):
                want = rows[(p["place"], "net_demand", m, "last_2_years", "")]
                self.assertEqual(want["hours"], sm["hours"])
                self.assertAlmostEqual(want["mae"], sm["mae_mw"][m], places=1)
            if nd["with_operator"] is None:
                self.assertTrue(rows[(p["place"], "net_demand", "operator", "all", "")]["held"])

    def test_the_weather_forecast_line_is_never_the_forecast(self):
        for p in self.index["places"]:
            d = self.places[p["place"]]["series"]["demand"]
            w = d.get("with_weather_forecast")
            self.assertNotEqual(d["method"], "with_weather_forecast")
            if w is None:
                continue
            self.assertEqual(w["status"], "scored" if w["days"] >= w["min_days"] else "too_few_days")
            if w["tomorrow"]:
                self.assertLessEqual(w["tomorrow_issue_utc"], d["made_utc"][:10] + "T20:00:00Z")

    def test_every_shown_price_has_its_score(self):
        cols = self.scores["rows_columns"]
        rows = [dict(zip(cols, r)) for r in self.scores["rows"]]
        for p in self.index["places"]:
            if p["series"]["price"]["status"] != "shown":
                continue
            got = {r["method"] for r in rows if r["place"] == p["place"] and r["series"] == "price" and r["cut"] == "all" and r["mae"] is not None}
            self.assertEqual(got, {"erw", "yesterday", "week_ago", "regression"}, p["place"])
            op = [r for r in rows if r["place"] == p["place"] and r["series"] == "price" and r["method"] == "operator"]
            self.assertTrue(op and all(r["mae"] is None and r["held"] for r in op), p["place"])
            self.assertTrue(any(r["cut"] == "spike" for r in rows if r["place"] == p["place"] and r["series"] == "price"), p["place"])

    def test_every_cut_has_its_words_and_net_demand_says_why(self):
        """Session 10603 (chain 720's requests 11 and 12): the price rows' cuts are named in cuts_price, the others in cuts;
        a net demand with no hour for tomorrow says why."""
        cols = self.scores["rows_columns"]
        rows = [dict(zip(cols, r)) for r in self.scores["rows"]]
        price = {r["cut"] for r in rows if r["series"] == "price"}
        rest = {r["cut"] for r in rows if r["series"] != "price"}
        self.assertFalse(price - set(self.scores["cuts_price"]), price - set(self.scores["cuts_price"]))
        known = set(self.scores["cuts"]) | set(self.scores.get("cuts_added", {}))
        self.assertFalse(rest - known, rest - known)
        for place, doc in self.places.items():
            n = doc["series"]["demand"].get("net_demand")
            if n and n.get("status") == "shown" and not n.get("tomorrow"):
                self.assertTrue(n.get("tomorrow_held"), place)

    def test_no_forecast_hour_without_a_figure(self):
        """Session 10603 (SPA, 28 November): a day the method cannot forecast has no rows and says why; every hour a
        file or a ledger gives as a forecast has its figure."""
        for place, doc in self.places.items():
            for name in ("demand", "price"):
                s = doc["series"][name]
                if s.get("status") != "shown":
                    continue
                if s.get("tomorrow"):
                    self.assertTrue(all(r[2] is not None for r in s["tomorrow"]), (place, name))
                else:
                    self.assertTrue(s.get("tomorrow_held"), (place, name))
        for led in ("ledger_demand.csv", "ledger_price.csv"):
            p = os.path.join(SITE, led)
            if not os.path.exists(p):
                continue
            with open(p, encoding="utf-8") as f:
                lines = [ln for ln in f if not ln.startswith("#")]
            d = pd.read_csv(io.StringIO("".join(lines)), dtype=str)
            # the one known making without figures, written before the fix (SPA, made 27 November 19:00 UTC): its rows
            # are window A's to remove or pass over (predict data request 20); any other empty row is a fault
            known = (d["place"] == "ba-spa") & (d["made_utc"] == "2026-11-27T19:00:00Z")
            bad = d[d["erw"].isna() & ~known]
            self.assertTrue(bad.empty, (led, bad.head(3).to_dict("records")))

    def test_a_held_series_holds_no_number(self):
        cols = self.scores["rows_columns"]
        for p in self.index["places"]:
            for name, ix in p["series"].items():
                if ix["status"] == "shown":
                    continue
                self.assertTrue(ix["held"], (p["place"], name))
                s = self.places[p["place"]]["series"][name]
                for key in ("tomorrow", "history", "summary", "band_coverage_pct"):
                    self.assertEqual(numbers(s.get(key)), [], (p["place"], name, key))
                for r in self.scores["rows"]:
                    r = dict(zip(cols, r))
                    if r["place"] == p["place"] and r["series"] == name:
                        self.assertEqual([r["hours"], r["mae"], r["mape"]], [None, None, None], (p["place"], name))
                        self.assertTrue(r["held"])

    def test_shown_series_carry_their_hours(self):
        for place, doc in self.places.items():
            s = doc["series"]["demand"]
            if s["status"] != "shown":
                continue
            self.assertTrue(s["made_utc"] and s["inputs_through_utc"], place)
            self.assertLess(s["inputs_through_utc"], s["made_utc"], place)
            if s["tomorrow"]:
                self.assertGreater(s["tomorrow"][0][0], s["made_utc"], place)
            for row in s["history"]:
                if row[4] == "backtest":
                    self.assertLess(row[3], row[0], place)


if __name__ == "__main__":
    unittest.main()

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
        doc = load("ahead.json")
        self.assertEqual(doc["tier"], "derived")
        for p in doc["places"]:
            for h in p["horizons"]:
                m = h["last_2_years"]["mae"]
                beats = m["regression"] is not None and m["week_ago"] is not None and m["regression"] < m["week_ago"]
                self.assertEqual(h["shown"], beats, (p["place"], h["horizon_days"]))
                if h["shown"]:
                    self.assertTrue(h["forecast"], (p["place"], h["horizon_days"]))
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

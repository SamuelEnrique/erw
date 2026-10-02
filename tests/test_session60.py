"""Session 60: the Flex Alert scorecard (warehouse/derived/flex_alert_scorecard.py). The estimator recovers a known effect
on a synthetic panel (and finds none where none was put), the alert days and hours are read from every form of CAISO's
time frames, and, where the tables are on this machine, the published numbers agree with each other."""

import os
import sys
import unittest

import numpy as np
import pandas as pd

ROOT = os.path.abspath(os.path.join(os.path.dirname(os.path.abspath(__file__)), ".."))
sys.path.insert(0, os.path.join(ROOT, "warehouse", "derived"))
import flex_alert_scorecard as fa  # noqa: E402

OUT = os.path.join(ROOT, "warehouse", "output")


def synthetic(effect_mw, seed=7):
    """Four alert seasons of hourly demand that is exactly linear in the model's terms plus noise (sd 300 MW), and eight
    of its hottest days as alert days whose hours 16 to 20 have effect_mw taken off."""
    rng = np.random.default_rng(seed)
    days = [d for d in pd.date_range("2019-05-01", "2022-10-31", freq="D") if d.month in fa.MONTHS]
    rows = []
    heat = {d: 10 + 12 * rng.random() + 8 * np.sin((d.dayofyear - 120) / 60) for d in days}
    for d in days:
        for h in range(24):
            t = heat[d] + 12 * np.sin((h - 9) / 24 * 2 * np.pi) + rng.normal(0, 1.5)
            rows.append(dict(day=d.strftime("%Y-%m-%d"), hour=h, ts=pd.Timestamp(d) + pd.Timedelta(hours=h), temp_f=65 + t,
                             dew_point=50 + 5 * rng.random(), month=d.month, year=d.year, saturday=float(d.dayofweek == 5),
                             sunday=float(d.dayofweek == 6), holiday=0.0))
    p = pd.DataFrame(rows)
    p["cdh"] = (p["temp_f"] - 65).clip(lower=0)
    p["cdh_prev24"] = p["cdh"].shift(1).rolling(24, min_periods=1).mean().fillna(0)
    p["cdh2"], p["cdh_prev24_2"], p["cdh_x_dew"] = p["cdh"] ** 2, p["cdh_prev24"] ** 2, p["cdh"] * p["dew_point"]
    p["y"] = (22000 + 1500 * np.sin((p["hour"] - 3) / 24 * 2 * np.pi) + 380 * p["cdh"] + 6 * p["cdh2"] + 150 * p["cdh_prev24"]
              + 20 * p["dew_point"] - 900 * p["sunday"] - 400 * p["saturday"] + 500 * (p["year"] - 2019) + rng.normal(0, 300, len(p)))
    tmax = p.groupby("day")["temp_f"].max().sort_values(ascending=False)
    alert = sorted(tmax.index[:30][::4][:8])
    hit = p["day"].isin(alert) & p["hour"].isin(fa.DEFAULT_HOURS)
    p.loc[hit, "y"] -= effect_mw
    alerts = pd.DataFrame([dict(day=d, types=["flex_alert"], hours=list(fa.DEFAULT_HOURS), basis="flex_alert", assumed=False,
                                source_notices=[]) for d in alert])
    train = sorted(set(p["day"]) - set(alert))
    return p, alerts, train


class Recovers(unittest.TestCase):
    def run_case(self, effect):
        p, alerts, train = synthetic(effect)
        hold, _ = fa.hot_days(p, train)
        m, _, vec = fa.out_of_sample(p, train, hold)
        D, H, Y, pooled, _ = fa.estimate(p, alerts, train, vec, None, b=60)
        return m, D, pooled

    def test_known_effect(self):
        m, D, pooled = self.run_case(1000.0)
        self.assertEqual(pooled["days"], 8)
        self.assertEqual(pooled["hours"], 40)
        self.assertAlmostEqual(pooled["reduction_mw"], 1000.0, delta=150)
        self.assertLess(pooled["reduction_mw_lo"], 1000.0)
        self.assertGreater(pooled["reduction_mw_hi"], 1000.0)
        self.assertLess(abs(m["bias_mw"]), 150)  # the model is right on the synthetic hot days
        self.assertAlmostEqual(pooled["reduction_mwh"], pooled["reduction_mw"] * 40, delta=1e-6)

    def test_no_effect(self):
        _, D, pooled = self.run_case(0.0)
        self.assertLess(pooled["reduction_mw_lo"], 0.0)
        self.assertGreater(pooled["reduction_mw_hi"], 0.0)
        self.assertLess(abs(pooled["reduction_mw"]), 150)


def notice(date, typ, start="", end="", frame="", region="ISO", eid=None):
    return dict(event_id=eid or f"x:{date}:{typ}:{start}{frame}", event_date=date, event_type=typ, x_region=region,
                x_start=start, x_end=end, x_time_frame=frame)


class AlertHours(unittest.TestCase):
    def test_hours_of(self):
        self.assertEqual(fa.hours_of(16 * 60, 21 * 60), [16, 17, 18, 19, 20])
        self.assertEqual(fa.hours_of(17 * 60 + 45, 23 * 60 + 59), [18, 19, 20, 21, 22, 23])  # 23:59 is midnight; 17:45 is 15 minutes
        self.assertEqual(fa.hours_of(18 * 60 + 30, 20 * 60), [18, 19])

    def test_forms_and_precedence(self):
        rows = pd.DataFrame([
            notice("2018-07-24", "flex_alert", "2018-07-24 17:00", "2018-07-24 21:00"),
            notice("2020-08-16", "flex_alert", "2020-08-16 15:00", "2020-08-19 22:00"),            # a four-day notice
            notice("2020-08-17", "warning", "2020-08-17 12:00", "2020-08-17 21:00"),
            notice("2020-09-30", "flex_alert", frame="10/1/2020 15:00:00 through 22:00:00"),     # the day is in the text
            notice("2021-07-12", "flex_alert", frame="2021-07-12 16:00:00 through 2021-07-12 21:00:00"),
            notice("2022-09-06", "flex_alert", frame="September 6 at 4:00 PM to September 6 at 9:00 PM"),
            notice("2022-09-06", "eea3", frame="09/06/2022 at 17:17 through 09/06/2022 at 20:00"),
            notice("2023-07-20", "eea1", "2023-07-20 19:30", "2023-07-20 22:00"),
            notice("2023-07-21", "rmo", "2023-07-21 06:00", "2023-07-21 22:00"),                 # not an alert type
            notice("2023-07-22", "flex_alert", "2023-07-22 16:00", "2023-07-22 21:00", region="Southern CA"),  # not ISO-wide
            notice("2024-08-01", "eea_watch", frame="no hours given"),
        ])
        a = fa.alert_days(rows).set_index("day")
        self.assertEqual(list(a.index), ["2018-07-24", "2020-08-16", "2020-08-17", "2020-08-18", "2020-08-19", "2020-10-01",
                                         "2021-07-12", "2022-09-06", "2023-07-20", "2024-08-01"])
        self.assertEqual(a.loc["2020-08-17", "hours"], [15, 16, 17, 18, 19, 20, 21])  # the Flex Alert's hours, not the Warning's
        self.assertEqual(a.loc["2020-08-17", "types"], ["flex_alert", "warning"])
        self.assertEqual(a.loc["2020-10-01", "hours"], [15, 16, 17, 18, 19, 20, 21])
        self.assertEqual(a.loc["2022-09-06", "hours"], [16, 17, 18, 19, 20])
        self.assertEqual(a.loc["2023-07-20", "hours"], [19, 20, 21])
        self.assertEqual(a.loc["2023-07-20", "basis"], "emergency")
        self.assertTrue(a.loc["2024-08-01", "assumed"])
        self.assertEqual(a.loc["2024-08-01", "hours"], list(fa.DEFAULT_HOURS))
        self.assertEqual(sorted(fa.notice_days(rows))[:2], ["2018-07-24", "2020-08-16"])
        self.assertIn("2023-07-21", fa.notice_days(rows))  # the price pull takes every notice day


def read(name):
    path = os.path.join(OUT, name + ".csv")
    with open(path, encoding="utf-8") as f:
        n = sum(1 for ln in f if ln.startswith("#"))
    return pd.read_csv(path, skiprows=n)


@unittest.skipUnless(os.path.exists(os.path.join(OUT, "flex_alert_effects.csv")), "flex_alert_effects is not on this machine")
class Published(unittest.TestCase):
    def test_pooled_is_the_hour_weighted_mean_of_the_days(self):
        e, m = read("flex_alert_effects"), read("flex_alert_model")
        day = e[e["variable"].isin(["reduction_mwh", "alert_hours"])].pivot(index="ts_utc", columns="variable", values="value")
        g = m.set_index("variable")["value"]
        self.assertEqual(int(g["pooled_days"]), len(day))
        self.assertEqual(int(g["pooled_hours"]), int(day["alert_hours"].sum()))
        self.assertAlmostEqual(g["pooled_reduction_mwh"], day["reduction_mwh"].sum(), delta=0.01 * len(day))
        self.assertAlmostEqual(g["pooled_reduction_mw"], day["reduction_mwh"].sum() / day["alert_hours"].sum(), delta=0.01)
        self.assertLessEqual(g["pooled_reduction_mw_lo"], g["pooled_reduction_mw"])
        self.assertGreaterEqual(g["pooled_reduction_mw_hi"], g["pooled_reduction_mw"])

    def test_each_day_actual_less_predicted(self):
        e = read("flex_alert_effects")
        d = e[e["freq"] == "P1D"].pivot(index="ts_utc", columns="variable", values="value")
        self.assertTrue(np.allclose(d["predicted_mwh"] - d["actual_mwh"], d["reduction_mwh"], atol=0.01))
        h = e[e["freq"] == "PT1H"].pivot(index="ts_utc", columns="variable", values="value")
        self.assertTrue((h["predicted_mw_lo"] <= h["predicted_mw_hi"]).all())


class LoaderRefusesOlder(unittest.TestCase):
    """warehouse/supabase/load.py's session 60 gate: a table older than Supabase's copy is refused, not loaded over it."""

    def client(self, newest=None, count=0):
        from unittest import mock
        c = mock.MagicMock()
        q = c.table.return_value.select.return_value.eq.return_value
        q.order.return_value.limit.return_value.execute.return_value.data = [{"retrieved_at": newest}] if newest else []
        q.execute.return_value.count = count
        return c

    def test_older_newer_and_counts(self):
        sys.path.insert(0, os.path.join(ROOT, "warehouse", "supabase"))
        import load
        df = pd.DataFrame({"retrieved_at": ["2026-09-29T01:00:00Z", "2026-09-29T00:58:45Z"], "value": [1, 2]})
        why = load.older_than_live(self.client("2026-10-01T23:12:46+00:00"), "weather_obs_hourly", df, "series")
        self.assertIn("2026-09-29T01:00:00Z", why)
        self.assertIsNone(load.older_than_live(self.client("2026-09-28T00:00:00+00:00"), "weather_obs_hourly", df, "series"))
        self.assertIsNone(load.older_than_live(self.client(None), "new_table", df, "series"))  # nothing live yet
        ledger = pd.DataFrame({"x": range(351)})
        self.assertIn("351 rows here and 477", load.older_than_live(self.client(count=477), "api_cost_ledger", ledger, "series"))
        self.assertIsNone(load.older_than_live(self.client(count=300), "api_cost_ledger", ledger, "series"))


class RestoredDates(unittest.TestCase):
    """warehouse/redivis/upload.py as_erw_text: a date column read back from Redivis (a datetime at midnight) is written
    YYYY-MM-DD, as the connectors write it; timestamps keep their time and Z."""

    def test_dates_and_timestamps(self):
        sys.path.insert(0, os.path.join(ROOT, "warehouse", "redivis"))
        import upload as up
        df = pd.DataFrame({"status_date": pd.to_datetime(["2015-09-09", None]), "queue_date": pd.to_datetime(["2010-07-31 06:00", None]),
                           "retrieved_at": pd.to_datetime(["2026-10-01T23:10:06", "2026-10-01T00:00:00"]), "value": [1.5, None]})
        out = up.as_erw_text(df)
        self.assertEqual(list(out["status_date"]), ["2015-09-09", ""])
        self.assertEqual(out["queue_date"].iloc[0], "2010-07-31T06:00:00Z")  # not midnight: kept whole
        self.assertEqual(list(out["retrieved_at"]), ["2026-10-01T23:10:06Z", "2026-10-01T00:00:00Z"])
        self.assertEqual(list(out["value"]), ["1.5", ""])


@unittest.skipUnless(os.path.exists(os.path.join(OUT, "flex_alert_effects.csv")) and os.path.isdir(os.path.join(ROOT, "warehouse", "raw", "eia930_emissions")),
                     "the scorecard's tables or the CISO extract are not on this machine")
class Notebook(unittest.TestCase):
    def test_the_replication_notebook_reproduces_the_point_estimates(self):
        """notebooks/flex_alert_scorecard.ipynb, its code cells run in order with ERW_NOTEBOOK_QUICK=1 (the bootstrap's
        intervals are left to a full run): it asserts every point estimate, variant and value equal to the tables."""
        import json
        from unittest import mock
        with open(os.path.join(ROOT, "notebooks", "flex_alert_scorecard.ipynb"), encoding="utf-8") as f:
            nb = json.load(f)
        g = {}
        cwd = os.getcwd()
        try:
            os.chdir(ROOT)
            with mock.patch.dict(os.environ, {"ERW_NOTEBOOK_QUICK": "1"}):
                for c in nb["cells"]:
                    if c["cell_type"] == "code":
                        exec("".join(c["source"]), g)  # noqa: S102  the repository's own notebook
        finally:
            os.chdir(cwd)
        self.assertEqual(len(g["alerts"]), 38)


if __name__ == "__main__":
    unittest.main()

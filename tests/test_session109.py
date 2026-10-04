"""Session 109: the network, version 3, finished: the replay's share of demand.

The approved pull's connector (EIA's daily demand by balancing authority); the rule that says which days' demand is
used; the replay's files against the table; the component's day view; the holds. No network.
"""
import json
import os
import sys
import unittest

import pandas as pd

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(ROOT, "warehouse", "derived"))
sys.path.insert(0, os.path.join(ROOT, "warehouse", "connectors"))
sys.path.insert(0, os.path.join(ROOT, "warehouse", "supabase"))
import eia930_daily_demand as conn  # noqa: E402
import iso_prices as ip  # noqa: E402
import network_daily as nd  # noqa: E402

OUT = os.path.join(ROOT, "warehouse", "output")
TABLE = os.path.join(OUT, "eia930_daily_demand.csv")


def src(*parts):
    with open(os.path.join(ROOT, *parts), encoding="utf-8") as f:
        return f.read()


class TheConnector(unittest.TestCase):
    def test_it_asks_for_demand_by_day_under_the_ceiling(self):
        self.assertEqual((conn.NAME, conn.ROUTE, conn.START, conn.TZ, conn.CEILING), ("eia930_daily_demand", "electricity/rto/daily-region-data", "2019-01-01", "Eastern", 300_000))
        params = dict(conn.base("2026-01-01", "2026-01-31"))
        self.assertEqual((params["facets[type][]"], params["frequency"], params["facets[timezone][]"]), ("D", "daily", "Eastern"))
        code = src("warehouse", "connectors", "eia930_daily_demand.py")
        self.assertIn('raise RuntimeError(f"{total:,} rows would pass the {CEILING:,} ceiling: nothing pulled")', code)   # counted before a page is asked for
        self.assertIn('"variable": "demand_mwh"', code)
        self.assertNotIn("total_interchange_mwh", code)
        self.assertIn("License: public domain", code)

    def test_held_out_of_what_a_visitor_counts(self):
        import load
        self.assertIn(conn.NAME, load.LIVE["catalogue_hold"])            # a history: no page reads it from Supabase
        self.assertIsNone(load.live_rule(conn.NAME))
        self.assertIn(conn.SOURCE, load.LIVE["sources_hold"])


class TheRule(unittest.TestCase):
    def days(self, values):
        return pd.Series(values, index=[str(d.date()) for d in pd.date_range("2021-02-01", periods=len(values))], dtype=float)

    def test_a_days_demand_is_used_inside_the_band_and_nothing_is_filled(self):
        d = self.days([1000, 1050, 980, 1020, 300, 990, 1010, 0, 1030, 2500, 1000, 1005, 995])
        s = nd.screened_demand(d)
        self.assertTrue(pd.isna(s.iloc[4]))               # under half the days around it: hours missing at the source
        self.assertTrue(pd.isna(s.iloc[7]))               # zero
        self.assertTrue(pd.isna(s.iloc[9]))               # over twice
        self.assertEqual(int(s.notna().sum()), 10)
        self.assertEqual(float(s.iloc[3]), 1020.0)        # a day that is used is as EIA gave it
        # a real fall is kept: Texas in the storm of February 2021 fell by about a quarter
        storm = nd.screened_demand(self.days([1430, 1410, 1490, 1200, 1080, 1085, 1240, 1300]))
        self.assertEqual(int(storm.notna().sum()), 8)

    def test_demand_by_day_keeps_the_networks_nodes_and_counts_what_it_screens(self):
        t = pd.DataFrame({"ba": ["ERCO"] * 5 + ["ZZZZ"] * 2, "day": ["2021-02-13", "2021-02-14", "2021-02-15", "2021-02-16", "2021-02-17", "2021-02-13", "2021-02-14"],
                          "v": [1400.0, 1500.0, 10.0, 1100.0, 1200.0, 5.0, 6.0]})
        out, screened = nd.demand_by_day(t, {"ERCO", "SWPP"})
        self.assertEqual(sorted(out), ["ERCO"])
        self.assertEqual(screened, 1)
        self.assertNotIn("2021-02-15", out["ERCO"])

    def test_a_day_is_its_average_mw_over_its_own_hours(self):
        flows = pd.DataFrame({"day": ["2021-03-13", "2021-03-14"], "fr": ["ERCO", "ERCO"], "to": ["SWPP", "SWPP"], "v": [2400.0, 2300.0], "bad": [False, False]})
        ci = pd.DataFrame({"day": pd.Series([], dtype=str), "ba": pd.Series([], dtype=str), "value": pd.Series([], dtype=float)})
        y = nd.build_year(2021, flows, {"ERCO", "SWPP"}, ci, {}, "2021-03-14", {"ERCO": {"2021-03-13": 1_200_000.0, "2021-03-14": 1_150_000.0}})
        i, j = y["days"].index("2021-03-13"), y["days"].index("2021-03-14")
        self.assertEqual(y["demand"]["ERCO"][i], 50000.0)                 # 24 hours
        self.assertEqual(y["demand"]["ERCO"][j], 50000.0)                 # the day the clocks go forward has 23
        self.assertIsNone(y["demand"]["ERCO"][0])                          # a day not held is null, never filled
        link = y["links"][0]
        self.assertEqual((link["mw"][i], link["mw"][j]), (100.0, 100.0))   # the flows are on the same scale
        self.assertNotIn("SWPP", y["demand"])
        self.assertEqual(y["missing"]["demand_days_held"], 2)


class TheFiles(unittest.TestCase):
    def setUp(self):
        self.index = json.loads(src("site", "public", "network", "daily_index.json"))

    def test_the_index_says_where_demand_comes_from_and_what_was_screened(self):
        self.assertEqual(self.index["demand_source"], "eia930_daily_demand")
        self.assertEqual(self.index["demand_band"], [0.5, 2.0])
        self.assertGreaterEqual(len(self.index["demand_bas"]), 50)
        for iso in ("ERCO", "CISO", "PJM", "MISO", "SWPP", "NYIS", "ISNE"):
            self.assertIn(iso, self.index["demand_bas"])
        self.assertTrue(all(v["with_demand"] >= 50 for v in self.index["years"].values()))

    @unittest.skipUnless(os.path.exists(TABLE), "eia930_daily_demand is not on this machine")
    def test_a_year_file_is_the_table_over_the_days_hours(self):
        t = pd.read_csv(TABLE, skiprows=ip.header_rows(TABLE), usecols=["entity", "ts_utc", "value"])
        y = json.loads(src("site", "public", "network", "daily_2021.json"))
        n = 0
        for ba in ("ERCO", "PJM", "CISO", "SWPP"):
            m = dict(zip(t[t["entity"] == f"eia930:{ba}"]["ts_utc"].str[:10], t[t["entity"] == f"eia930:{ba}"]["value"]))
            for k, day in enumerate(y["days"]):
                v = y["demand"][ba][k]
                if v is None:
                    continue
                self.assertAlmostEqual(v, m[day] / nd.day_hours(day), delta=0.06, msg=(ba, day))
                n += 1
        self.assertGreater(n, 1400)
        i = y["days"].index("2021-02-15")
        self.assertAlmostEqual(y["demand"]["ERCO"][i], 50151.8, delta=0.1)     # Texas, 15 February 2021, the day's average MW


class ThePage(unittest.TestCase):
    def test_the_day_view_reads_demand_and_shows_each_suppliers_share(self):
        comp = src("site", "app", "network", "Network.tsx")
        self.assertIn("demand: (id, h) => f.demand?.[id]?.[h] ?? null", comp)
        self.assertNotIn("intensity: (id, h) => f.intensity[id]?.[h] ?? null, demand: () => null", comp)
        self.assertIn("isDayView && demandNow && Math.round(t.imp) !== 0", comp)       # a share only in the replay's day view: the live page is as it was
        self.assertIn("data-tie-share={t.other}", comp)
        page = src("site", "app", "network", "v3", "page.tsx")
        self.assertIn("A share of demand, by day:", page)
        self.assertNotIn("demand, so a share of demand is not given for a replayed day", page)
        self.assertIn('"eia930_daily_demand"', page)
        live = src("site", "app", "network", "page.tsx")
        self.assertNotIn("v3=", live)                                                   # the live page passes no version 3: no replay, no day view
        self.assertRegex(src("site", "lib", "release.ts"), r'"/network/v3":\s*"review"')

    def test_no_em_dash(self):
        for rel in ("warehouse/connectors/eia930_daily_demand.py", "warehouse/derived/network_daily.py", "site/scripts/check-network-v3.mjs", "tests/test_session109.py"):
            self.assertNotIn(chr(0x2014), src(*rel.split("/")), rel)


if __name__ == "__main__":
    unittest.main()

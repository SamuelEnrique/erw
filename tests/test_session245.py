"""Session 245: a year of hourly carbon in the live set (the owner's ruling of 12 October 2026).

Energy Research Warehouse (ERW). warehouse/supabase/live_set.yaml; docs/methods/emissions.md. The live set held
carbon_intensity_hourly for the recent window of 35 days. It now holds at least 13 months, hour by hour, for the seven
ISOs and the US48: the table has its own window of 430 days.

What is held here: the rule (the table is out of the 35-day rule and has its own), that the loader's filter keeps
every hour, every balancing authority and both variables of the window and nothing older, and that 430 days are 13
whole calendar months on any day of the year. No request: the table is a stand-in built here.
"""

import datetime as dt
import os
import re
import sys
import unittest
from unittest import mock

import pandas as pd
import yaml

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
sys.path.insert(0, os.path.join(ROOT, "warehouse", "supabase"))
import load  # noqa: E402

EM = chr(0x2014)
T = "carbon_intensity_hourly"
BAS = ["CISO", "ERCO", "ISNE", "MISO", "NYIS", "PJM", "SWPP", "US48"]


def src(*parts):
    with open(os.path.join(ROOT, *parts), encoding="utf-8") as f:
        return f.read()


class TheRule(unittest.TestCase):
    def setUp(self):
        self.live = yaml.safe_load(src("warehouse", "supabase", "live_set.yaml"))

    def test_the_hourly_intensity_has_its_own_window_of_430_days(self):
        self.assertIn("^carbon_intensity_hourly$", self.live["full"])
        self.assertEqual(self.live["select"][T], {"days": 430})
        self.assertFalse(any(re.match(p, T) for p in self.live["recent"]["tables"]), "it is no longer in the 35-day rule")
        self.assertEqual(load.live_rule(T), ("full", None))
        # the tables beside it are as they were: EIA's CO2 estimates in the recent window, the daily intensity its 100 days
        self.assertEqual(load.live_rule("eia930_all_emissions"), ("recent", 35))
        self.assertEqual(self.live["select"]["carbon_intensity_daily"], {"days": 100})
        self.assertEqual(load.live_rule("carbon_intensity_monthly"), ("full", None))

    def test_no_row_of_the_window_is_left_out_by_a_column_or_a_value(self):
        self.assertEqual(set(self.live["select"][T]), {"days"}, "no include, no exclude, no columns: hour by hour, both variables, every balancing authority")
        self.assertNotIn(T, self.live["catalogue_hold"])
        self.assertNotIn(T, self.live["review_hold"])

    def test_430_days_hold_13_whole_calendar_months_on_any_day_with_eias_lag(self):
        # the table ends a few days behind the calendar; whatever the day, the window must reach back past the first
        # day of the thirteenth whole month before the month under way
        for start in (dt.date(2026, 1, 1), dt.date(2027, 1, 1), dt.date(2028, 1, 1)):   # 2028 is a leap year
            for offset in range(366):
                today = start + dt.timedelta(days=offset)
                first = (today.replace(day=1) - dt.timedelta(days=1)).replace(day=1)   # the month before, its first day
                y, m = first.year, first.month - 12
                while m < 1:
                    y, m = y - 1, m + 12
                thirteenth = dt.date(y, m, 1)
                self.assertLessEqual(today - dt.timedelta(days=430), thirteenth, today)


class TheFilter(unittest.TestCase):
    def table(self, now, days):
        hours = pd.date_range(now - pd.Timedelta(days=days), now - pd.Timedelta(hours=1), freq="h", tz="UTC")
        rows = [{"entity": f"eia930:{ba}", "variable": v, "ts_utc": t.strftime(load.TS_FMT), "value": 300.0, "unit": "kgCO2/MWh", "freq": "PT1H", "geo": "US",
                 "market": "", "node": "", "source": "erw:carbon_intensity", "source_url": "https://example.invalid/m", "retrieved_at": "2026-10-12T14:32:55Z",
                 "vintage": "", "ba": ba.lower()} for ba in BAS for v in ("intensity_generation", "intensity_demand") for t in hours]
        return pd.DataFrame(rows)

    def test_the_last_430_days_hour_by_hour_and_nothing_older(self):
        now = pd.Timestamp("2026-10-13T07:00:00Z")
        df = self.table(now, 500)
        with mock.patch.object(load, "read_table", return_value=df):
            rule, days = load.live_rule(T)
            got, shape = load.filtered(T, days, now)
        self.assertEqual(shape, "series")
        self.assertEqual(len(got), 430 * 24 * len(BAS) * 2)
        self.assertEqual(got["ts_utc"].min(), "2025-08-09T07:00:00Z")
        self.assertEqual(got["ts_utc"].max(), "2026-10-13T06:00:00Z")
        per = got.groupby(["entity", "variable"]).size()
        self.assertEqual((len(per), per.min(), per.max()), (16, 430 * 24, 430 * 24))
        months = sorted({t[:7] for t in got["ts_utc"]})
        whole = [m for m in months if m not in (months[0], months[-1])]
        self.assertGreaterEqual(len(whole), 13)
        self.assertEqual(whole[0], "2025-09")


class TheWords(unittest.TestCase):
    def test_the_method_and_the_chat_say_what_is_held(self):
        doc = src("docs", "methods", "emissions.md")
        for words in ("In the site's database (the live set)", "the last 430 days, hour by hour", "at least 13 months; it was 35 days"):
            self.assertIn(words, doc, words)
        self.assertIn("carbon_intensity_hourly) is held for 430 days", src("warehouse", "chat", "tools.py"))

    def test_no_em_dash_in_what_the_session_wrote(self):
        for f in ("warehouse/supabase/live_set.yaml", "docs/methods/emissions.md", "tests/test_session245.py", "warehouse/chat/tools.py"):
            self.assertNotIn(EM, src(*f.split("/")), f)


if __name__ == "__main__":
    unittest.main()

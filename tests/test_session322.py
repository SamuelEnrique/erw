"""Session 322: ERCOT's notices, the Flex Alert scorecard to 2026, CAISO's 25-hour day.

Energy Research Warehouse (ERW). No network: the parser is held against short pieces of text written here (test fixtures,
not data values) and the wiring against the files.

  1. ercot_grid_notices: the days a notice covers, its kind from its own words, and what counts toward stress days.
  2. grid_stress_days reads ERCOT's notices as it reads CAISO's.
  3. CAISO's request ends at the next local midnight, so a 25-hour day is asked whole.
  4. The scorecard's window runs to 2026-10-31.

    python -m unittest tests.test_session322 -v
"""

import datetime as dt
import os
import re
import sys
import unittest

import pandas as pd

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
sys.path.insert(0, os.path.join(ROOT, "warehouse", "connectors"))
import ercot_grid_notices as g  # noqa: E402


def src(*parts):
    with open(os.path.join(ROOT, *parts), encoding="utf-8") as f:
        return f.read()


D = dt.date


class Days(unittest.TestCase):
    def test_a_title_naming_its_day(self):
        self.assertEqual(g.named_days("Requests Conservation Monday, January 15, from 6 a.m. to 10 a.m. CT", D(2024, 1, 14)),
                         [D(2024, 1, 15)])

    def test_through_a_day(self):
        self.assertEqual(g.named_days("ERCOT Issues Winter Weather Watch Through Sun., Feb. 6", D(2022, 2, 2)),
                         [D(2022, 2, d) for d in range(2, 7)])

    def test_a_range_of_days_in_one_month(self):
        self.assertEqual(g.named_days("ERCOT has issued a Weather Watch from January 20-23 due to cold", D(2025, 1, 17)),
                         [D(2025, 1, d) for d in range(20, 24)])

    def test_two_named_days_through(self):
        txt = "between Thursday, December 22 through Monday, December 26."
        self.assertEqual(g.named_days(txt, D(2022, 12, 16)), [D(2022, 12, d) for d in range(22, 27)])

    def test_the_dateline_is_not_a_covered_day(self):
        txt = "AUSTIN, TX, Sept. 4, 2019 - reduce their electricity use on Thursday, Sept. 5 and Friday, Sept. 6"
        self.assertEqual(g.named_days(txt, D(2019, 9, 4)), [D(2019, 9, 5), D(2019, 9, 6)])
        self.assertEqual(g.named_days("(Austin, TX/June 23) a Weather Watch from June 25 - 27", D(2023, 6, 23)),
                         [D(2023, 6, 25), D(2023, 6, 26), D(2023, 6, 27)])

    def test_through_a_weekday(self):
        self.assertEqual(g.through_weekday("Vital Need for Conservation Today Through Tuesday", D(2011, 8, 28)),
                         [D(2011, 8, 28), D(2011, 8, 29), D(2011, 8, 30)])

    def test_the_day_from_the_address(self):
        self.assertEqual(g.release_day("/news/release/2023-09-06-ercot-has-initiated"), D(2023, 9, 6))
        self.assertEqual(g.release_day("/news/release/01212026-ercot-issues-weather"), D(2026, 1, 21))


class Kinds(unittest.TestCase):
    def test_kinds_from_the_words(self):
        k = lambda t, p="": g.release_kind(t, p)[0]  # noqa: E731
        self.assertEqual(k("ERCOT Has Initiated Energy Emergency Alert Level 2 (EEA 2), Conservation is Critical"), "eea2")
        self.assertEqual(k("Power Watch - Conservation Needed", "ERCOT may need an Energy Emergency Alert"), "power_watch")
        self.assertEqual(k("ERCOT Issues Voluntary Conservation Notice"), "voluntary_conservation")
        self.assertEqual(k("ERCOT Issues Weather Watch"), "weather_watch")
        self.assertEqual(k("ERCOT calls for rotating outages as extreme winter weather forces generating units offline"),
                         "rotating_outages")
        self.assertEqual(k("Tight grid conditions today, no conservation appeal"), "statement")
        self.assertEqual(k("Level 2 emergency cancelled; interruptible loads restored"), "update")
        self.assertEqual(k("ERCOT Closely Monitoring Changing Weather Conditions",
                           "ERCOT issued an Operating Condition Notice (OCN) that temperatures will be 25 degrees or lower"), "ocn_weather")
        self.assertEqual(k("ERCOT sets new winter peak demand record", "ERCOT is not asking Texans to conserve"), "statement")
        self.assertEqual(g.release_kind("Rotating outages in Rio Grande Valley", "")[1], "Rio Grande Valley")

    def test_control_room_kinds(self):
        self.assertIsNone(g.ops_kind("No sudden loss of generation greater than 450 MW occurred", "Operational Information"))
        self.assertEqual(g.ops_kind("ERCOT is issuing an OCN for an extreme hot weather event", "OCN"), "ocn_weather")
        self.assertEqual(g.ops_kind("this is a test of the ERCOT Emergency Notification System", "Emergency Notice"), "emergency_test")
        self.assertEqual(g.ops_kind("ERCOT has cancelled the following notice: Advisory issued", "Advisory"), "update")
        self.assertEqual(g.ops_kind("Advisory issued for a geomagnetic disturbance of K7", "Advisory"), "advisory")

    def test_what_counts(self):
        self.assertEqual(g.COUNTS, {"eea1", "eea2", "eea3", "rotating_outages", "conservation_appeal", "voluntary_conservation",
                                    "weather_watch", "power_watch", "ocn_weather"})


class Wiring(unittest.TestCase):
    def test_stress_days_reads_ercot_notices(self):
        s = src("warehouse", "derived", "stress_days.py")
        self.assertIn('ERCOT_NOTICES = "ercot_grid_notices"', s)
        self.assertIn('en = en[en["x_counts"] == "yes"]', s)
        self.assertIn("Derived from: {ERCOT_DAILY}; {HISTORY}; {NOTICES}; {ERCOT_NOTICES}", s)

    def test_caiso_asks_a_calendar_day(self):
        self.assertIn("end=day + pd.DateOffset(days=1), market=market", src("warehouse", "connectors", "iso_prices.py"))
        day = pd.Timestamp("2025-11-02", tz="America/Los_Angeles")
        self.assertEqual(day + pd.DateOffset(days=1) - day, pd.Timedelta(hours=25))

    def test_the_scorecard_runs_to_2026(self):
        self.assertTrue(re.search(r'^END = "2026-10-31"', src("warehouse", "derived", "flex_alert_scorecard.py"), re.M))

    def test_registered(self):
        self.assertIn("'^ercot_grid_notices$'", src("warehouse", "supabase", "live_set.yaml"))
        self.assertIn('(r"^ercot_grid_notices$", "power")', src("warehouse", "metadata", "build_coverage.py"))
        self.assertTrue(os.path.exists(os.path.join(ROOT, "docs", "methods", "ercot_grid_notices.md")))


if __name__ == "__main__":
    unittest.main()

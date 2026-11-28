"""Session 11407 (chain 770 part C), readied from session 10225's test of the events audit's finding 6
(wip/audit-events-6, docs/reviews/events-model-audit-2026-11-26.md): the ERW's rule for California's hydro gap
(warehouse/derived/impossible_hours.py without_hydro_gap) is approved for event_window_daily on its own
(impossible_hours.HYDRO_GAP_APPROVED), while the rest of the rule stays held with the table in HELD. Every one of the
14 days of the August 2020 window that held an intensity has hours inside the gap, so the table's next build leaves
them all out: the page's "highest carbon intensity" (305.93 kg/MWh, 2020-08-18) and its carbon chart's line go, and
the page says why. The builder run on this machine's extract (retrieved 2026-10-04): 14 rows gone for CAISO 2020, 92
for the COVID-19 window's CISO days, no other row moved. For the owner's ruling, not for landing alone.
"""
import csv
import datetime as dt
import os
import sys
import unittest
from unittest import mock
from zoneinfo import ZoneInfo

import numpy as np
import pandas as pd

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
ROWS = os.path.join(ROOT, "replication", "events", "window_rows.csv")
GAP = (dt.datetime(2019, 10, 1, 21, tzinfo=dt.timezone.utc), dt.datetime(2020, 8, 24, 17, tzinfo=dt.timezone.utc))
sys.path.insert(0, os.path.join(ROOT, "warehouse", "derived"))
import impossible_hours  # noqa: E402


def src(*p):
    with open(os.path.join(ROOT, *p), encoding="utf-8") as fh:
        return fh.read()


class TheHydroGapRuleIsApprovedForTheEventTable(unittest.TestCase):
    def test_the_rule_is_written_in_and_approved_alone(self):
        self.assertIn('impossible_hours.without_hydro_gap(x, ba, NAME)', src("warehouse", "derived", "event_window.py"))
        self.assertIn('CISO_NO_HYDRO = ("2019-10-01T21:00:00Z", "2020-08-24T17:00:00Z")', src("warehouse", "derived", "impossible_hours.py"))
        self.assertIn("event_window_daily", impossible_hours.HYDRO_GAP_APPROVED)
        self.assertIn("event_window_daily", impossible_hours.HELD, "the rest of the rule (screen_extract) stays held")
        self.assertEqual(set(impossible_hours.HYDRO_GAP_APPROVED), {"event_window_daily"})

    def test_the_builder_blanks_the_gap_hours_outside_a_trial(self):
        ts = ["2020-08-24T16:00:00Z", "2020-08-24T17:00:00Z", "2020-08-24T18:00:00Z"]
        x = pd.DataFrame({"ts_utc": ts, "demand_mwh": [40000.0, 41000.0, 42000.0], "net_generation_mwh": [30000.0, 31000.0, 32000.0]})
        with mock.patch.dict(os.environ, {}, clear=False):
            os.environ.pop("ERW_SCREEN_TRIAL", None)
            self.assertFalse(impossible_hours.applies("event_window_daily"))
            got = impossible_hours.without_hydro_gap(x, "ciso", "event_window_daily")
            self.assertTrue(np.isnan(got["net_generation_mwh"].iloc[0]) and np.isnan(got["net_generation_mwh"].iloc[1]))
            self.assertEqual(got["net_generation_mwh"].iloc[2], 32000.0)
            self.assertEqual(list(got["demand_mwh"]), [40000.0, 41000.0, 42000.0], "demand is not touched")
            # another held table keeps the rule held
            self.assertEqual(list(impossible_hours.without_hydro_gap(x, "ciso", "ba_supply_monthly")["net_generation_mwh"]), [30000.0, 31000.0, 32000.0])
            # another grid comes back as it came
            self.assertEqual(list(impossible_hours.without_hydro_gap(x, "erco", "event_window_daily")["net_generation_mwh"]), [30000.0, 31000.0, 32000.0])

    def test_the_page_says_why(self):
        s = src("site", "app", "events", "caiso-heat-2020", "page.tsx")
        self.assertIn('<span data-hydro-gap="1">{HYDRO_GAP_WORDS}</span>', s)
        self.assertIn("No carbon intensity of CAISO is drawn for the event's window", s)
        self.assertNotIn("it is held until a person approves it", s)
        self.assertNotIn(chr(0x2014), s)

    def test_the_notes_say_it(self):
        self.assertIn("HYDRO_GAP_APPROVED", src("docs", "methods", "impossible_hours.md"))
        self.assertIn("the table holds no CAISO intensity on the window's 14 days", src("docs", "methods", "events.md"))

    @unittest.skipUnless(os.path.exists(ROWS), "the replication's public rows are not in this checkout")
    def test_every_window_day_with_an_intensity_touches_the_gap(self):
        """The before: the published rows (run 20261019T094329Z) hold 14 days, each touching the gap, so all go."""
        with open(ROWS, encoding="utf-8") as fh:
            xs = {r["ts_utc"][:10]: float(r["value"]) for r in csv.DictReader(l for l in fh if not l.startswith("#"))
                  if r["event"] == "caiso_heat_2020" and r["entity"] == "eia930:CISO" and r["variable"] == "intensity_generation"
                  and "2020-08-10" <= r["ts_utc"][:10] <= "2020-08-24"}
        pt = ZoneInfo("America/Los_Angeles")
        inside = []
        for d in xs:
            a = dt.datetime.fromisoformat(d).replace(tzinfo=pt).astimezone(dt.timezone.utc)
            if a <= GAP[1] and a + dt.timedelta(hours=24) > GAP[0]:
                inside.append(d)
        self.assertEqual(len(xs), 14)
        self.assertEqual(sorted(inside), sorted(xs), "every day the page drew is left out")
        top = max(xs, key=lambda d: xs[d])
        self.assertEqual((top, round(xs[top], 2)), ("2020-08-18", 305.93))


if __name__ == "__main__":
    unittest.main()

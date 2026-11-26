"""Session 10225 (chain 710, the events audit, finding 6): the ERW's rule for California's hydro gap
(warehouse/derived/impossible_hours.py without_hydro_gap) is written into warehouse/derived/event_window.py and held
(impossible_hours.HELD), so event_window_daily still writes CAISO's carbon intensity on days whose net generation has
no hydro. Every one of the 14 days of the August 2020 window that holds an intensity has hours inside the gap, so the
rule, approved, would leave them all out: the page's "highest carbon intensity" (305.93 kg/MWh, 2020-08-18) and its
carbon chart would go. Not fixed: approving a held rule moves figures, so the ruling is the owner's
(docs/reviews/events-model-audit-2026-11-26.md; docs/methods/impossible_hours.md). These tests pass on main.
"""
import csv
import datetime as dt
import os
import unittest
from zoneinfo import ZoneInfo

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
ROWS = os.path.join(ROOT, "replication", "events", "window_rows.csv")
GAP = (dt.datetime(2019, 10, 1, 21, tzinfo=dt.timezone.utc), dt.datetime(2020, 8, 24, 17, tzinfo=dt.timezone.utc))


def src(*p):
    with open(os.path.join(ROOT, *p), encoding="utf-8") as fh:
        return fh.read()


class TheHeldRuleWouldTakeTheWindow(unittest.TestCase):
    def test_the_rule_is_written_in_and_held(self):
        self.assertIn('impossible_hours.without_hydro_gap(x, ba, NAME)', src("warehouse", "derived", "event_window.py"))
        self.assertIn('CISO_NO_HYDRO = ("2019-10-01T21:00:00Z", "2020-08-24T17:00:00Z")', src("warehouse", "derived", "impossible_hours.py"))

    @unittest.skipUnless(os.path.exists(ROWS), "the replication's public rows are not in this checkout")
    def test_every_window_day_with_an_intensity_touches_the_gap(self):
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
        self.assertEqual(sorted(inside), sorted(xs), "every day the page draws would be left out")
        top = max(xs, key=lambda d: xs[d])
        self.assertEqual((top, round(xs[top], 2)), ("2020-08-18", 305.93))


if __name__ == "__main__":
    unittest.main()

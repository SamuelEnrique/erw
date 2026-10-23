"""Session 2071: the AESO's hourly Alberta internal load.

Energy Research Warehouse (ERW). Tests warehouse/connectors/aeso_load.py on reports built here in the AESO's form (made
up for the test, not the AESO's): an ordinary day, the spring day of 23 hours and the autumn day of 25 ("02*") placed by
their order from the local midnight in UTC, hours not yet reached ("-") no rows; a day's hours out of order, a time not in
the AESO's form and a header not the AESO's stopping the run; the sector rule and the holds. No network.

    python -m unittest tests.test_session2071 -v
"""

import os
import sys
import unittest

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
sys.path.insert(0, os.path.join(ROOT, "warehouse", "connectors"))
sys.path.insert(0, os.path.join(ROOT, "warehouse", "metadata"))
sys.path.insert(0, os.path.join(ROOT, "warehouse", "redivis"))
import aeso_load as A  # noqa: E402
import build_coverage as B  # noqa: E402
import release_v1 as R  # noqa: E402


def report(rows):
    return "Pool Price\n\n\"\"\n\nDate (HE),Price ($),30Ravg ($),AIL Demand (MW)\n" + "".join(f'"{t}","1.00","2.00","{v}"\n' for t, v in rows)


def day(date, hours, value=10000.0):
    return [(f"{date} {h}", value + i) for i, h in enumerate(hours)]


SPRING = ["01"] + [f"{h:02d}" for h in range(3, 25)]
AUTUMN = ["01", "02", "02*"] + [f"{h:02d}" for h in range(3, 25)]


class Build(unittest.TestCase):
    def test_days(self):
        rows = day("07/01/2025", [f"{h:02d}" for h in range(1, 25)]) + day("03/09/2025", SPRING) + day("11/02/2025", AUTUMN)
        t = A.build([(report(rows), "u", "r")]).set_index("ts_utc")
        self.assertEqual(t.loc["2025-07-01T06:00:00Z", "value"], 10000.0)          # MDT: midnight is 06:00 UTC
        self.assertEqual(t.loc["2025-03-09T07:00:00Z", "value"], 10000.0)          # MST midnight
        self.assertEqual(t.loc["2025-03-09T08:00:00Z", "value"], 10001.0)          # "03", the day's second hour
        self.assertEqual(t.loc["2025-11-02T07:00:00Z", "value"], 10001.0)          # "02" (midnight was still MDT, 06:00 UTC)
        self.assertEqual(t.loc["2025-11-02T08:00:00Z", "value"], 10002.0)          # "02*"
        self.assertEqual(len(t), 24 + 23 + 25)

    def test_not_yet_and_stops(self):
        partial = day("10/23/2026", ["01", "02"]) + [("10/23/2026 03", "-")]
        self.assertEqual(len(A.build([(report(partial), "u", "r")])), 2)
        with self.assertRaises(RuntimeError):
            A.build([(report(day("07/01/2025", ["01", "03"]) + day("07/02/2025", ["01"])), "u", "r")])
        with self.assertRaises(RuntimeError):
            A.build([(report([("2025-07-01 01", 1.0)]), "u", "r")])
        with self.assertRaises(RuntimeError):
            A.build([(report(day("07/01/2025", ["01"])).replace("AIL Demand (MW)", "Load"), "u", "r")])


class Registered(unittest.TestCase):
    def test_sector_and_holds(self):
        self.assertEqual(B.sector_of(A.NAME), "power")
        self.assertIn(A.NAME, R.STORAGE_HELD)
        with open(os.path.join(ROOT, "warehouse", "supabase", "live_set.yaml"), encoding="utf-8") as f:
            self.assertIn(f"  - {A.NAME}\n", f.read().replace("\r\n", "\n"))


if __name__ == "__main__":
    unittest.main()

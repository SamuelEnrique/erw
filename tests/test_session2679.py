"""Session 2679: BC Hydro's Hourly Control Area Load Reports, British Columbia's balancing authority load an hour.

Energy Research Warehouse (ERW). Tests warehouse/connectors/bchydro_ba_load.py on sheets built here (made up for the test, not
BC Hydro's): the Pacific local hours ending counted from each day's local midnight in UTC, the spring day's 23 hours and the
autumn day's 25 with its repeated hour "2*" placed after HE 2 whatever its row order, a day not ended at retrieval left out; a
day whose hours are not its date's, a load not positive, a wrong area group and a gap of a day stopping the run; the sector
rule and the holds. No network.

    python -m unittest tests.test_session2679 -v
"""

import datetime as dt
import os
import sys
import unittest

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
sys.path.insert(0, os.path.join(ROOT, "warehouse", "connectors"))
sys.path.insert(0, os.path.join(ROOT, "warehouse", "metadata"))
sys.path.insert(0, os.path.join(ROOT, "warehouse", "redivis"))
import bchydro_ba_load as A  # noqa: E402
import build_coverage as B  # noqa: E402
import release_v1 as R  # noqa: E402

LATE = dt.datetime(2030, 1, 1, tzinfo=dt.timezone.utc)


def sheet(days, area="BCHA", year=2025):
    rows = [["Hourly Control Area Load Report", "", ""], ["Date Range:", -float(year), ""], ["Area Group Name:", area, ""],
            ["Date \xa0", "HE", "Control Area Load"]]
    for d, hes in days:
        for he in hes:
            rows.append([d, he, 1000.0 + (he if isinstance(he, float) else 2.5)])
    return rows


NORMAL = [float(h) for h in range(1, 25)]
SPRING = [1.0] + [float(h) for h in range(3, 25)]
AUTUMN = [1.0, "2*", 2.0] + [float(h) for h in range(3, 25)]  # as the 2025 sheet lists it


class Parse(unittest.TestCase):
    def test_hours(self):
        out = dict(A.parse_rows(sheet([("03/08/2025", NORMAL), ("03/09/2025", SPRING)]), 2025, LATE))
        self.assertEqual(len(out), 24 + 23)
        self.assertEqual(out["2025-03-08T08:00:00Z"], 1001.0)  # HE 1 starts at local midnight, PST
        self.assertEqual(out["2025-03-09T09:00:00Z"], 1003.0)  # the spring day's second hour is HE 3
        self.assertEqual(max(out), "2025-03-10T06:00:00Z")  # the spring day ends at local midnight, PDT

    def test_autumn(self):
        out = A.parse_rows(sheet([("11/01/2025", NORMAL), ("11/02/2025", AUTUMN)]), 2025, LATE)
        d = dict(out)
        self.assertEqual(len(out), 24 + 25)
        self.assertEqual(d["2025-11-02T08:00:00Z"], 1002.0)  # HE 2, the first 01:00 to 02:00, PDT
        self.assertEqual(d["2025-11-02T09:00:00Z"], 1002.5)  # "2*", the repeated hour, PST
        self.assertEqual(d["2025-11-02T10:00:00Z"], 1003.0)

    def test_not_ended(self):
        cut = dt.datetime(2025, 3, 9, 7, 30, tzinfo=dt.timezone.utc)  # the second day has not begun
        out = A.parse_rows(sheet([("03/07/2025", NORMAL), ("03/08/2025", NORMAL)]), 2025, cut)
        self.assertEqual(len(out), 24)

    def test_stops(self):
        bad_load = sheet([("01/01/2025", NORMAL)])
        bad_load[5][2] = 0.0
        for rows in (sheet([("03/09/2025", NORMAL)]), sheet([("01/01/2025", SPRING)]), bad_load, sheet([("01/01/2025", NORMAL)], area="AESO"),
                     sheet([("01/01/2025", NORMAL), ("01/03/2025", NORMAL)]), sheet([("01/01/2024", NORMAL)])):
            with self.assertRaises(RuntimeError):
                A.parse_rows(rows, 2025, LATE)


class Registered(unittest.TestCase):
    def test_sector_and_holds(self):
        self.assertEqual(B.sector_of(A.NAME), "power")
        self.assertIn(A.NAME, R.STORAGE_HELD)
        with open(os.path.join(ROOT, "warehouse", "supabase", "live_set.yaml"), encoding="utf-8") as f:
            self.assertIn(f"  - {A.NAME}\n", f.read().replace("\r\n", "\n"))


if __name__ == "__main__":
    unittest.main()

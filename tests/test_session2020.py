"""Session 2020: Berkeley Lab's Tracking the Sun written: its registration and its license.

Energy Research Warehouse (ERW). The table built by warehouse/connectors/lbnl_tracking_the_sun.py (sessions 2015 and
2020; its summary is tested in tests/test_session2015.py): the sector rule, the holds (public, so in the release package
while Redivis's storage is settled, and out of the live set), its own verdict (read 176) by hand, and the 1980 floor.
No network.

    python -m unittest tests.test_session2020 -v
"""

import csv
import os
import sys
import unittest

import pandas as pd

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
sys.path.insert(0, os.path.join(ROOT, "warehouse", "connectors"))
sys.path.insert(0, os.path.join(ROOT, "warehouse", "metadata"))
sys.path.insert(0, os.path.join(ROOT, "warehouse", "redivis"))
sys.path.insert(0, os.path.join(ROOT, "scripts"))
import lbnl_tracking_the_sun as T  # noqa: E402
import build_coverage as B  # noqa: E402
import release_v1 as R  # noqa: E402
import licenses as L  # noqa: E402


class Registered(unittest.TestCase):
    def test_sector_holds_and_license(self):
        self.assertEqual(B.sector_of(T.TABLE), "power")
        self.assertIn(T.TABLE, R.STORAGE_HELD)
        with open(os.path.join(ROOT, "warehouse", "supabase", "live_set.yaml"), encoding="utf-8") as f:
            self.assertIn(f"  - {T.TABLE}\n", f.read().replace("\r\n", "\n"))
        key = L.BY_HAND[T.TABLE][0]
        self.assertEqual(key, ["Berkeley Lab, Tracking the Sun on OEDI"])
        with open(os.path.join(ROOT, "warehouse", "metadata", "license_verdicts.csv"), encoding="utf-8") as f:
            v = {r["key"]: r for r in csv.DictReader(f)}
        self.assertEqual((v[key[0]]["read"], v[key[0]]["verdict"]), ("176", "may be public"))

    def test_floor(self):
        self.assertEqual(T.FLOOR, pd.Timestamp("1980-01-01"))


if __name__ == "__main__":
    unittest.main()

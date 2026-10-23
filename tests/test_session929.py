"""Session 929: every country's monthly petroleum production, consumption and stocks from EIA's bulk file.

Energy Research Warehouse (ERW). Tests warehouse/connectors/eia_intl_bulk.py's third table on a bulk file built here in
EIA's form (figures made up for the test, not EIA's): only monthly series taken, the month's first day, kbbl/d and kbbl,
the OECD's imports by source left out, the annual series left to the annual table; the sector rule and the holds. No
network.

    python -m unittest tests.test_session929 -v
"""

import os
import sys
import unittest

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
sys.path.insert(0, os.path.join(ROOT, "warehouse", "connectors"))
sys.path.insert(0, os.path.join(ROOT, "warehouse", "metadata"))
sys.path.insert(0, os.path.join(ROOT, "warehouse", "redivis"))
sys.path.insert(0, os.path.join(ROOT, "tests"))
import eia_intl_bulk as E  # noqa: E402
import build_coverage as B  # noqa: E402
import release_v1 as R  # noqa: E402
from test_session909 import ser, bulk  # noqa: E402

SERIES = [
    ser("INTL.57-1-SAU-TBPD.M", "Crude oil including lease condensate production, Saudi Arabia, Monthly", [["202606", 9500.5], ["202605", "NA"]]),
    ser("INTL.5-5-SAU-MBBL.M", "Petroleum and other liquids stocks, Saudi Arabia, Monthly", [["202606", 2.5]]),
    ser("INTL.785-3-SAU-TBPD.M", "Japan petroleum and other liquids gross imports, Saudi Arabia, Monthly", [["202606", 1200]]),
    ser("INTL.57-1-SAU-TBPD.A", "Crude oil including lease condensate production, Saudi Arabia, Annual", [["2025", 9300]]),
]


class Monthly(unittest.TestCase):
    def test_months_units_and_skips(self):
        t, n = E.rows(E.read_series(bulk(SERIES)), "u", "r", "v", E.OIL_MONTHLY)
        self.assertEqual(n, 2)
        g = t.set_index(["entity", "variable"])
        self.assertEqual(g.loc[("eia_intl:SAU:57", "production"), "ts_utc"], "2026-06-01T00:00:00Z")
        self.assertEqual((g.loc[("eia_intl:SAU:57", "production"), "freq"], g.loc[("eia_intl:SAU:57", "production"), "unit"]), ("P1M", "kbbl/d"))
        self.assertEqual((g.loc[("eia_intl:SAU:5", "stocks"), "value"], g.loc[("eia_intl:SAU:5", "stocks"), "unit"]), (2500.0, "kbbl"))
        a, na = E.rows(E.read_series(bulk(SERIES)), "u", "r", "v", E.OIL_GAS)
        self.assertEqual((na, a.ts_utc.tolist()), (1, ["2025-01-01T00:00:00Z"]))


class Registered(unittest.TestCase):
    def test_sector_and_holds(self):
        name = "eia_world_oil_monthly"
        self.assertEqual(B.sector_of(name), "oil")
        self.assertIn(name, R.STORAGE_HELD)
        with open(os.path.join(ROOT, "warehouse", "supabase", "live_set.yaml"), encoding="utf-8") as f:
            self.assertIn(f"  - {name}\n", f.read().replace("\r\n", "\n"))


if __name__ == "__main__":
    unittest.main()

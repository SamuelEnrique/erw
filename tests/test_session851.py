"""Session 851: ERCOT's Capacity, Demand and Reserves report (CDR) by season, as ercot_cdr_reserve_margins.

Energy Research Warehouse (ERW). Tests warehouse/connectors/ercot_cdr.py on a Seasonal Summary sheet built here in the
report's layout (labels from the connector's own map, figures made up for the test, not ERCOT's): the seasons and hours
of the heading rows, the sections, the reserve margin in pct, a row the map does not know, the newest workbook on the
page, the sector rule and the holds. No network.

    python -m unittest tests.test_session851 -v
"""

import os
import re
import sys
import unittest

import pandas as pd

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
sys.path.insert(0, os.path.join(ROOT, "warehouse", "connectors"))
sys.path.insert(0, os.path.join(ROOT, "warehouse", "metadata"))
sys.path.insert(0, os.path.join(ROOT, "warehouse", "redivis"))
import ercot_cdr as C  # noqa: E402
import build_coverage as B  # noqa: E402
import release_v1 as R  # noqa: E402

N = float("nan")
HEADS = {"load": "Load Forecast and Adjustments, MW:", "operational": "Operational Generation Capacity",
         "planned": "Planned Resource Additions (with Signed IA and Proof of Financial Commitment) and Retirements"}


def sheet(extra=None):
    rows = [[N, "Seasonal Summary", N, N, N, N, N],
            [N, N, N, "Summer", "Summer", N, "Winter"],
            [N, N, N, 2026, 2026, N, "2026/2027"],
            [N, N, N, "Peak Load Hour:", "Peak Net Load Hour:", "Difference", "Peak Load Hour:"],
            [N, N, N, 17, 21, N, 8]]
    section = None
    for s, p, v in C.ROWS:
        if s != section:
            rows.append([N, HEADS[s], N, N, N, N, N])
            section = s
        lab = re.sub(r"[\^\$]", "", p)
        val = 0.15 if v == "reserve_margin" else 100.0
        rows.append([N, N, lab, val, val + 1, 1, val + 2])
        if extra and v == extra[0]:
            rows.append([N, N, extra[1], 1, 1, 0, 1])
    return pd.DataFrame(rows)


class TheSheet(unittest.TestCase):
    def test_seasons_hours_and_units(self):
        t = C.sheet_rows(sheet(), "u", "r", "2025-12-19T00:00:00Z", "x.xlsx")
        self.assertEqual(sorted(t.entity.unique()), ["ercot_cdr:summer:peak_load", "ercot_cdr:summer:peak_net_load", "ercot_cdr:winter:peak_load"])
        self.assertEqual(len(t), 3 * len(C.ROWS))
        w = t[(t.entity == "ercot_cdr:winter:peak_load")].set_index("variable")
        self.assertEqual(w.loc["firm_peak_load", "ts_utc"], "2026-12-01T00:00:00Z")
        self.assertAlmostEqual(w.loc["reserve_margin", "value"], 215.0)     # the sheet's 2.15, times 100
        self.assertEqual(w.loc["reserve_margin", "unit"], "pct")
        s = t[(t.entity == "ercot_cdr:summer:peak_load")].set_index("variable")
        self.assertAlmostEqual(s.loc["reserve_margin", "value"], 15.0)
        self.assertEqual((s.loc["firm_peak_load", "unit"], s.loc["firm_peak_load", "x_hour"], s.loc["firm_peak_load", "geo"]), ("MW", "17", "US-TX"))

    def test_an_unknown_row_stops(self):
        with self.assertRaises(RuntimeError):
            C.sheet_rows(sheet(extra=("operational_hydro", "A Kind Not Seen Before")), "u", "r", "v", "x")

    def test_the_newest_workbook(self):
        html = ('<a href="https://www.ercot.com/files/docs/2025/05/15/CapacityDemandandReservesReport_May2025.xlsx">'
                '<a href="https://www.ercot.com/files/docs/2025/12/19/CapacityDemandandReservesReport_December2025.xlsx">')
        url, posted = C.newest(html)
        self.assertTrue(url.endswith("December2025.xlsx"))
        self.assertEqual(posted, "2025-12-19T00:00:00Z")


class Registered(unittest.TestCase):
    def test_sector_and_holds(self):
        self.assertEqual(B.sector_of("ercot_cdr_reserve_margins"), "power")
        self.assertIn("ercot_cdr_reserve_margins", R.STORAGE_HELD)
        with open(os.path.join(ROOT, "warehouse", "supabase", "live_set.yaml"), encoding="utf-8") as f:
            self.assertIn("  - ercot_cdr_reserve_margins", f.read())


if __name__ == "__main__":
    unittest.main()

"""Session 10212 (storage audit, finding 1): "US Lower 48" on /storage leaves out CAISO, NYISO and PJM.

The fleet tab draws a "US Lower 48" row in the daily cycle and a "US Lower 48" line under the hourly chart, beside a
headline of every battery operating in the US. The series is EIA-930's Lower 48 battery total, which adds the
authorities that report a battery series; CAISO, NYISO and PJM report none (warehouse/connectors/eia930_storage.py,
NO_BAT), so it leaves them out. Measured (docs/reviews/storage-model-audit-2026-11-26/measures.json): their units are
18,200.1 of the 56,120.7 operating MW of EIA-860M's September 2026 inventory, 32.4 percent; over the 683 UTC hours of the
30 days to 4 November 2026 that both hold, CAISO's own output (1,286,677 MWh discharged) was 88 percent of the Lower 48's
(1,467,480), and stood above it in 267 hours. The page said neither.

Words only (site/app/storage/page.tsx, LOWER48_WORDS and LOWER48_LINE): no figure moves.
"""
import json
import os
import unittest

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))


def read(*p):
    with open(os.path.join(ROOT, *p), encoding="utf-8") as f:
        return f.read()


class LowerFortyEight(unittest.TestCase):
    def test_the_three_grids_report_no_battery_series(self):
        self.assertIn('NO_BAT = ["ciso", "nyis", "pjm"]', read("warehouse", "connectors", "eia930_storage.py"))

    def test_a_third_of_the_operating_fleet_is_in_them(self):
        f = json.loads(read("site", "data", "storage", "places.json"))
        left = sum(f["authorities"][c]["operating_mw"] or 0 for c in ("CISO", "NYIS", "PJM"))
        share = left / f["us"]["operating_mw"]
        self.assertGreater(share, 0.30)
        self.assertLess(share, 0.35)

    def test_the_page_says_so(self):
        p = read("site", "app", "storage", "page.tsx")
        self.assertIn('const LOWER48_WORDS = "The Lower 48 row is EIA-930\'s national total, which leaves out CAISO, NYISO and PJM', p)
        self.assertIn('data-lower48-note="1">{LOWER48_WORDS}</p>', p)
        self.assertIn('const LOWER48_LINE = "US Lower 48 (EIA-930, without CAISO, NYISO and PJM)";', p)
        self.assertIn("label: LOWER48_LINE,", p)
        self.assertIn("The Lower 48 line is EIA-930's national total, which leaves out CAISO, NYISO and PJM.", p)
        self.assertNotIn('label: "US Lower 48", color: "ink"', p)
        self.assertNotIn(chr(0x2014), p)


if __name__ == "__main__":
    unittest.main()

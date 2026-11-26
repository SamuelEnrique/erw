"""Audit of the trader view, finding 5 (session 10209, docs/reviews/trader-model-audit-2026-11-26.md): the on-peak
block is hours ending 7 to 22 local in every grid (warehouse/derived/trader_view.py, `6 <= h <= 21` on the local hour
start), the Central and Western block. The Eastern block that NYISO, ISO-NE and PJM name is hours ending 8 to 23
Eastern prevailing time, one hour later. NYISO's, ISO-NE's and MISO's rows of iso_trader_daily take the earlier block;
those grids are held or paused, so no page shows them. The note called the block "the standard 5x16 block" for every
grid.

1. The code's rule, one block for every grid (read from the source). Passes on main.
2. The fix on this branch, words only: the note says the block is the Central and Western one and names the Eastern
   block. Fails on main. Not sized: no held grid's price is read."""
import os
import re
import unittest

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))


class OnPeakBlockIsOneForEveryGrid(unittest.TestCase):
    def test_the_code_takes_one_block(self):
        with open(os.path.join(ROOT, "warehouse", "derived", "trader_view.py"), encoding="utf-8") as f:
            src = f.read()
        self.assertEqual(len(re.findall(r"6 <= h <= 21", src)), 2)        # on and off, the same hours for every iso
        self.assertNotRegex(src, r"iso\s*==\s*\"(nyiso|isone|miso)\"")
        self.assertIn('"nyiso": ("nyiso_dam_zone_prices"', src)

    def test_the_note_names_the_eastern_block(self):
        with open(os.path.join(ROOT, "docs", "methods", "trader_view.md"), encoding="utf-8") as f:
            text = f.read()
        self.assertIn("**The block is the Central and Western one in every grid (session 10209", text)
        self.assertIn("hours ending 8 to 23 Eastern prevailing time (07:00 to 23:00), one hour later", text)


if __name__ == "__main__":
    unittest.main()

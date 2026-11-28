"""Session 11200 (chain 760, part E): the price board's step does not stop when EIA's fuel prices were not written.

On 27 November eia_fuels failed (EIA's API answered 504) and price_board stopped on the missing file, so the latest,
peak and carbon tables were not written either. Without the file the spreads are now carried from the last run (tried
on hard links to the data machine's tables with the file left out: all four tables written, exit 0).
"""
import os
import unittest

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


class TheBoardWithoutFuels(unittest.TestCase):
    def setUp(self):
        with open(os.path.join(ROOT, "warehouse", "derived", "price_board.py"), encoding="utf-8") as fh:
            self.src = fh.read()

    def test_the_fuel_file_is_read_only_when_held(self):
        self.assertIn('fuels = read_table("eia_fuel_spot_prices") if fuels_held else None', self.src)
        self.assertNotIn('        fuels = read_table("eia_fuel_spot_prices")\n', self.src)

    def test_the_spreads_are_carried_and_said_so(self):
        self.assertIn('spreads = previous("price_board_spreads", SPREAD_COLS)', self.src)
        self.assertIn("every row is carried from the last run", self.src)


if __name__ == "__main__":
    unittest.main()

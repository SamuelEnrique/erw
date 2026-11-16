"""Session 7012 (chain 301): the hub price comparison's hourly real-time price (warehouse/derived/price_compare.py),
found by replication/compare/replicate.py: four 15-minute prices that sum to zero are an hour of zero, not a negative
hour, whatever the float sum's noise. MADE UP prices; no file of the warehouse is read.

    python -m unittest tests.test_session7012_price_compare -v
"""
import os
import sys
import unittest

import pandas as pd

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
sys.path.insert(0, os.path.join(ROOT, "warehouse", "derived"))
import price_compare as PC  # noqa: E402


class HourOfZero(unittest.TestCase):
    def test_four_quarters_summing_to_zero_are_not_negative(self):
        idx = pd.date_range("2026-03-20T16:00:00Z", periods=4, freq="15min")
        s = pd.Series([0.1, 0.2, -0.3, 0.0], index=idx)   # their float mean is not exactly 0
        h = PC.hourly(s, "PT15M")
        self.assertEqual(len(h), 1)
        self.assertFalse((h < 0).any())
        self.assertEqual(float(h.iloc[0]), 0.0)

    def test_an_hour_short_of_a_quarter_is_not_an_hour(self):
        idx = pd.date_range("2026-03-20T16:00:00Z", periods=3, freq="15min")
        self.assertEqual(len(PC.hourly(pd.Series([1.0, 2.0, 3.0], index=idx), "PT15M")), 0)


if __name__ == "__main__":
    unittest.main()

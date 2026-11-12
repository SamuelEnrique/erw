"""Session 2285 (chain 179): a figure the evidence states in US dollars beside another currency.

The third read (session 2284) found T024, "Return has secured an EUR 835 million (US$938 million) portfolio financing
underwritten by Deutsche Bank and Rabobank", with USD empty: the model is told not to convert currencies and left it.
warehouse/deals/fields.py (usd_stated) takes a figure the evidence itself states in US dollars (US$ or USD, never a
bare $), when it states exactly one and the model gave none. On the replayed answers of the four deal fixtures, only
T024 changes.
"""

import os
import sys
import unittest

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
sys.path.insert(0, os.path.join(ROOT, "warehouse", "deals"))
sys.path.insert(0, os.path.join(ROOT, "warehouse", "deals", "eval"))
import deal_fields as fields  # noqa: E402  session 3233: by its own name (deal_fields.py)
import fixture  # noqa: E402


class TheRule(unittest.TestCase):
    def test_an_explicit_us_dollar_figure(self):
        self.assertEqual(fields.usd_stated("an EUR 835 million (US$938 million) portfolio financing"), (938e6, "US$938 million"))
        self.assertEqual(fields.usd_stated("a GBP 3.6 billion (USD 4.8 billion) framework")[0], 4.8e9)

    def test_none(self):
        self.assertEqual(fields.usd_stated("a $500 million loan"), (None, ""))   # a bare $ is the model's to read
        self.assertEqual(fields.usd_stated("US$1 billion now and US$2 billion later"), (None, ""))   # two figures
        self.assertEqual(fields.usd_stated("an EUR 835 million financing"), (None, ""))


class TheSample(unittest.TestCase):
    def test_t024(self):
        rows, log = fixture.replay("2284")
        got = [r for r in rows.to_dict("records") if "Return" in (r["seller"] or "")]
        self.assertEqual([r["dollars"] for r in got], ["938000000"])
        self.assertEqual(log.count("from the words 'US$"), 1)


if __name__ == "__main__":
    unittest.main()

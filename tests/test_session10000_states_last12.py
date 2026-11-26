"""Session 10000 (chain 701): a state's twelve-month retail figures end at the newest month with sales. On 26 November 2026
EIA's prices reached September 2026 while the sales stopped at August, so the window ended on September and every
sector's twelve-month figure went blank (tests/test_audit_states_8 caught Texas). Made-up frames; no table is read."""
import importlib.util
import os
import sys
import unittest

import pandas as pd

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))


def load():
    sys.path.insert(0, os.path.join(ROOT, "warehouse", "derived"))
    sys.path.insert(0, os.path.join(ROOT, "warehouse", "connectors"))
    spec = importlib.util.spec_from_file_location("states_page_t", os.path.join(ROOT, "warehouse", "derived", "states_page.py"))
    m = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(m)
    return m


def frame(months, sectors, value):
    return pd.DataFrame([{"st": "TX", "month": mo, "sector": k, "value": value} for mo in months for k in sectors])


class TheWindowEndsAtTheSales(unittest.TestCase):
    def setUp(self):
        self.m = load()
        self.sales_months = self.m.month_range("2025-01", "2026-08")
        self.price_months = self.m.month_range("2025-01", "2026-09")
        self.cust = pd.DataFrame(columns=["st", "month", "sector", "value"])

    def test_prices_a_month_ahead_leave_the_figures(self):
        sales = frame(self.sales_months, list(self.m.SECTORS), 10.0)
        price = frame(self.price_months, list(self.m.SECTORS), 100.0)
        r = self.m.build_retail(sales, price, self.cust, "TX")
        self.assertEqual((r["last12"]["from"], r["last12"]["to"]), ("2025-09", "2026-08"))
        self.assertEqual(r["last12"]["by_sector"]["all"]["sales_mwh"], 120.0)
        self.assertEqual(r["last12"]["by_sector"]["transportation"]["price_usd_per_mwh"], 100.0)
        self.assertEqual(r["months"][-1], "2026-09")   # the price's month is still drawn on the chart

    def test_a_sector_the_page_omits_does_not_move_the_end(self):
        sales = pd.concat([frame(self.sales_months, list(self.m.SECTORS), 10.0), frame(["2026-09"], ["OTH"], 1.0)])
        price = frame(self.price_months, list(self.m.SECTORS), 100.0)
        r = self.m.build_retail(sales, price, self.cust, "TX")
        self.assertEqual(r["last12"]["to"], "2026-08")

    def test_both_tables_together_are_unchanged(self):
        sales = frame(self.sales_months, list(self.m.SECTORS), 10.0)
        price = frame(self.sales_months, list(self.m.SECTORS), 100.0)
        r = self.m.build_retail(sales, price, self.cust, "TX")
        self.assertEqual((r["last12"]["from"], r["last12"]["to"]), ("2025-09", "2026-08"))


if __name__ == "__main__":
    unittest.main()

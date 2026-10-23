"""Session 904: EIA's Uranium Marketing Annual Report, its summary tables; Decision 55, the units lb, SWU and USD/SWU.

Energy Research Warehouse (ERW). Tests warehouse/connectors/eia_uranium_marketing.py on a sheet built here in the
tables' form (figures made up for the test, not EIA's): each column mapped by its heading, million pounds as lb and
million SWU as SWU, W and - having no row, a heading not in the map stopping the run, the units in the validator, the
sector rule and the holds. No network.

    python -m unittest tests.test_session904 -v
"""

import os
import sys
import unittest

import pandas as pd

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
sys.path.insert(0, os.path.join(ROOT, "warehouse", "connectors"))
sys.path.insert(0, os.path.join(ROOT, "warehouse", "metadata"))
sys.path.insert(0, os.path.join(ROOT, "warehouse", "redivis"))
sys.path.append(os.path.join(ROOT, "warehouse", "validate"))
import eia_uranium_marketing as U  # noqa: E402
import build_coverage as B  # noqa: E402
import release_v1 as R  # noqa: E402
import erw_validate as V  # noqa: E402

N = float("nan")


def sheet(head, rows):
    top = [["2025 Uranium Marketing Annual Report"] + [N] * (len(head) - 1)] + [[N] * len(head)] * 6
    return pd.DataFrame(top + [head] + rows)


class Uranium(unittest.TestCase):
    def test_enrichment_units(self):
        head = ["Year", "Feed deliveries by owners and operators", "Uranium in fuel assemblies loaded into U.S. reactors",
                "U.S.-origin enrichment services purchased", "Foreign-origin enrichment services purchased",
                "Total purchased enrichment services", "Average price (US$ per SWU)"]
        out = pd.DataFrame(U.sheet_rows(sheet(head, [[2025, 40.5, 45.0, 2.0, 12.0, 14.0, 108.7], [2005, 52.9, "W", 1.0, 10.0, 11.0, "-"]]),
                                        "umartableS2figuresS3n4.xlsx", "u", "r")).set_index(["variable", "ts_utc"])
        self.assertEqual((out.loc[("feed_deliveries", "2025-01-01T00:00:00Z"), "value"], out.loc[("feed_deliveries", "2025-01-01T00:00:00Z"), "unit"]), (40.5e6, "lb"))
        self.assertEqual(out.loc[("enrichment_total", "2025-01-01T00:00:00Z"), "unit"], "SWU")
        self.assertEqual(out.loc[("enrichment_price", "2025-01-01T00:00:00Z"), "unit"], "USD/SWU")
        self.assertNotIn(("uranium_loaded", "2005-01-01T00:00:00Z"), out.index)
        self.assertNotIn(("enrichment_price", "2005-01-01T00:00:00Z"), out.index)

    def test_prices_and_an_unknown_heading(self):
        head = ["Delivery year", "Total purchased (weighted-average price)", "Purchased from U.S. producers", "Purchased from U.S. brokers and traders",
                "Purchased from other owners and operators of U.S. civilian nuclear power reactors", "Purchased from foreign suppliers",
                "U.S.-origin uranium (weighted-average price)", "Foreign-origin uranium (weighted-average price)",
                "Spot contracts b (weighted-average price)", "Long-term contracts c (weighted-average price)"]
        out = pd.DataFrame(U.sheet_rows(sheet(head, [[2025, 58.46, "- -", 60, 55, 57, 59, 58, 75.8, 55.1]]), "umartableS1bfigureS2.xlsx", "u", "r"))
        g = out.set_index("variable")
        self.assertEqual((g.loc["price_purchased_spot", "value"], g.loc["price_purchased_spot", "unit"]), (75.8, "USD/lb"))
        self.assertNotIn("price_purchased_from_us_producers", g.index)
        bad = list(head)
        bad[3] = "Something New"
        with self.assertRaises(RuntimeError):
            U.sheet_rows(sheet(bad, [[2025] + [1] * 9]), "umartableS1bfigureS2.xlsx", "u", "r")


class Registered(unittest.TestCase):
    def test_units_sector_and_holds(self):
        self.assertTrue({"lb", "SWU", "USD/SWU"} <= V.UNITS)
        name = "eia_uranium_marketing_annual"
        self.assertEqual(B.sector_of(name), "power;uranium")
        self.assertIn(name, R.STORAGE_HELD)
        with open(os.path.join(ROOT, "warehouse", "supabase", "live_set.yaml"), encoding="utf-8") as f:
            self.assertIn(f"  - {name}\n", f.read().replace("\r\n", "\n"))


if __name__ == "__main__":
    unittest.main()

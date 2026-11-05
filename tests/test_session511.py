"""Session 511: Form EIA-861M, each sampled utility's monthly sales, revenue and customers by state and sector.

Energy Research Warehouse (ERW). Held on real rows of EIA's sheet (sales_ult_cust_2025.xlsx, December, Alaska): the
columns are found by their headings, EIA's State Adjustment, State Total and US Total rows are not taken, revenue's
thousand dollars become USD, a heading missing or a key given twice stops the run, and the page's links are read.
"""

import os
import sys
import unittest

import pandas as pd

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
sys.path.insert(0, os.path.join(ROOT, "warehouse", "connectors"))
import eia861m_sales as M  # noqa: E402

NAN = float("nan")
HEAD = [["UTILITY CHARATERISTICS", NAN, NAN, NAN, NAN, NAN, NAN, "RESIDENTIAL", NAN, NAN, "COMMERCIAL", NAN, NAN, "INDUSTRIAL", NAN, NAN, "TRANSPORTATION", NAN, NAN, "TOTAL", NAN, NAN],
        [NAN, NAN, NAN, NAN, NAN, NAN, NAN] + ["Revenue", "Sales", "Customers"] * 5,
        ["Year", "Month", "Utility Number", "Utility Name", "State", "Ownership", "Data Status"] + ["Thousands Dollars", "Megawatthours", "Count"] * 5]
ROWS = [[2025, 12, 0, "State Adjustment 2025", "AK", NAN, "Preliminary", 5695.758, 19365.727, 27400, 9996.74, 34963.385, 11402, 2658.589, 10812.858, 327, 0, 0, 0, 18351.087, 65141.97, 39129],
        [2025, 12, 213, "Alaska Electric Light & Power Co.", "AK", "Investor Owned", "Preliminary", 2690.512, 18700.478, 15560, 1324.133, 10664.256, 2529, 1038.205, 8668.632, 147, 0, 0, 0, 5052.85, 38033.366, 18236],
        [2025, 12, 219, "Alaska Power and Telephone Co", "AK", "Investor Owned", "Preliminary", 1277.152, 2893.602, 5837, 1709.07, 4262.753, 2854, 0, 0, 0, 0, 0, 0, 2986.222, 7156.355, 8691],
        [2025, 12, 88888, "State Total", "AK", NAN, "Preliminary", 59199.872, 231779.652, 305423, 53050.166, 245439.646, 58188, 24515.368, 123859.354, 1240, 0, 0, 0, 136765.406, 601078.652, 364851],
        [2025, 12, 88888, "US Total", "US", NAN, "Preliminary", 22350573.757, 129666744.119, 145338734, 16700979.634, 122521592.035, 19719132, 7240757.874, 84906782.696, 1152674, 87142.422, 620608.012, 81, 46379453.687, 337715726.862, 166210621]]


def frame(rows=ROWS, head=HEAD):
    return pd.DataFrame(head + rows)


class TheSheet(unittest.TestCase):
    def setUp(self):
        self.t = M.sheet_rows(frame(), 2025, "https://www.eia.gov/electricity/data/eia861m/archive/xls/sales_ult_cust_2025.xlsx", "2026-10-21T19:28:00Z")

    def test_only_the_sampled_utilities(self):
        self.assertEqual(sorted(self.t["entity"].unique()), ["eia861m:213:AK", "eia861m:219:AK"])
        self.assertEqual(len(self.t), 2 * 15)

    def test_units_and_values(self):
        g = self.t[(self.t["entity"] == "eia861m:213:AK")].set_index("variable")
        self.assertAlmostEqual(g.loc["residential_revenue", "value"], 2690512.0)
        self.assertEqual(g.loc["residential_revenue", "unit"], "USD")
        self.assertEqual((g.loc["total_sales", "value"], g.loc["total_sales", "unit"]), (38033.366, "MWh"))
        self.assertEqual((g.loc["total_customers", "value"], g.loc["total_customers", "unit"]), (18236.0, "count"))
        r = g.loc["total_sales"]
        self.assertEqual((r["ts_utc"], r["freq"], r["geo"], r["node"], r["x_data_status"], r["x_ownership"]),
                         ("2025-12-01T00:00:00Z", "P1M", "US-AK", "Alaska Electric Light & Power Co.", "Preliminary", "Investor Owned"))

    def test_a_missing_heading_stops(self):
        head = [list(HEAD[0]), list(HEAD[1]), list(HEAD[2])]
        head[2][6] = "Status"
        with self.assertRaises(RuntimeError):
            M.sheet_rows(frame(head=head), 2025, "u", "r")

    def test_a_key_given_twice_stops(self):
        with self.assertRaises(RuntimeError):
            M.sheet_rows(frame(rows=[ROWS[1], ROWS[1]]), 2025, "u", "r")

    def test_the_page_links(self):
        html = '<a href="./archive/xls/sales_ult_cust_2025.xlsx">2025</a> <a href="./xls/sales_ult_cust_2026.xlsx">2026</a>'
        self.assertEqual(M.file_urls(html, [2025, 2026]),
                         {2025: "https://www.eia.gov/electricity/data/eia861m/archive/xls/sales_ult_cust_2025.xlsx",
                          2026: "https://www.eia.gov/electricity/data/eia861m/xls/sales_ult_cust_2026.xlsx"})
        with self.assertRaises(RuntimeError):
            M.file_urls(html, [2024])

    def test_both_new_tables_are_held_until_uploaded(self):
        sys.path.insert(0, os.path.join(ROOT, "warehouse", "redivis"))
        import release_v1 as R
        with open(os.path.join(ROOT, "warehouse", "supabase", "live_set.yaml"), encoding="utf-8") as h:
            y = h.read()
        for t in ("eia923_plant_fuel_annual", "eia861m_utility_sales_monthly"):
            self.assertIn(f"  - {t}\n", y[y.index("catalogue_hold:"):], t)
            self.assertIn(f"upload.py {t}", R.STORAGE_HELD[t])

    def test_no_em_dash(self):
        for f in ("warehouse/connectors/eia861m_sales.py", "tests/test_session511.py"):
            with open(os.path.join(ROOT, *f.split("/")), encoding="utf-8") as h:
                self.assertNotIn(chr(0x2014), h.read(), f)


if __name__ == "__main__":
    unittest.main()

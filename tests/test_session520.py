"""Session 520: EIA-861M's back years. The 2017 to 2020 files are named retail_sales_<year>.xlsx and are found beside
sales_ult_cust_<year>.xlsx; a year the page does not link still stops the run; the ceiling holds the page and ten years.
"""

import os
import sys
import unittest

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
sys.path.insert(0, os.path.join(ROOT, "warehouse", "connectors"))
import eia861m_sales as M  # noqa: E402

PAGE = ('<a href="./archive/xls/retail_sales_2017.xlsx">2017</a> <a href="./archive/xls/retail_sales_2020.xlsx">2020</a> '
        '<a href="./archive/xls/sales_ult_cust_2021.xlsx">2021</a> <a href="./xls/sales_ult_cust_2026.xlsx">2026</a> '
        '<a href="./archive/xls/small_scale_solar_2018.xlsx">solar</a>')


class TheBackYears(unittest.TestCase):
    def test_both_names_are_found(self):
        u = M.file_urls(PAGE, [2017, 2020, 2021, 2026])
        self.assertEqual(u[2017], "https://www.eia.gov/electricity/data/eia861m/archive/xls/retail_sales_2017.xlsx")
        self.assertEqual(u[2021], "https://www.eia.gov/electricity/data/eia861m/archive/xls/sales_ult_cust_2021.xlsx")
        self.assertEqual(u[2026], "https://www.eia.gov/electricity/data/eia861m/xls/sales_ult_cust_2026.xlsx")

    def test_an_unlinked_year_stops(self):
        with self.assertRaises(RuntimeError):
            M.file_urls(PAGE, [2018])

    def test_the_ceiling_holds_ten_years(self):
        self.assertGreaterEqual(M.CEILING, 11)


if __name__ == "__main__":
    unittest.main()

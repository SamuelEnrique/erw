"""Session 485: EIA-861 retail sales, revenue and customers by utility, state, part and sector. Observed rows only (EIA's
imputed rows, its Withheld and Adjustment aggregates and its "." cells are not taken); revenue in USD (EIA's thousand
dollars times 1,000); the newest zip the page links is the one read."""

import os
import sys
import unittest

import pandas as pd

ROOT = os.path.abspath(os.path.join(os.path.dirname(os.path.abspath(__file__)), ".."))
sys.path.insert(0, os.path.join(ROOT, "warehouse", "connectors"))
import eia861_sales as es  # noqa: E402


HEAD = [["Utility Characteristics"] + [None] * 8 + ["RESIDENTIAL", None, None, "COMMERCIAL", None, None, "INDUSTRIAL", None, None,
                                                    "TRANSPORTATION", None, None, "TOTAL", None, None],
        [None] * 9 + ["Revenues", "Sales", "Customers"] * 5,
        ["Data Year", "Utility Number", "Utility Name", "Part", "Service Type", "Data Type" + chr(10) + "O = Observed" + chr(10) + "I = Imputed", "State",
         "Ownership", "BA Code"] + ["Thousand Dollars", "Megawatthours", "Count"] * 5]


def sheet(*rows, head=HEAD):
    """EIA's sheet: its three heading rows, then rows of 9 characteristics and 5 sectors of 3 figures."""
    return pd.DataFrame([list(r) for r in head] + [list(r) for r in rows])


ROW_A = [2025, 55, "City of Aberdeen - (MS)", "A", "Bundled", "O", "MS", "Municipal", "TVA",
         4216, 31966, 2577, 3541, 28066, 691, 6876, 108807, 2, 0, 0, 0, 14633, 168839, 3270]


class Sheet(unittest.TestCase):
    def test_an_observed_row_becomes_fifteen_figures(self):
        t = es.sheet_rows(sheet(ROW_A), 2025, "u", "r")
        self.assertEqual(len(t), 15)
        by = dict(zip(t["variable"], t["value"]))
        self.assertEqual(by["total_sales"], 168839.0)
        self.assertEqual(by["residential_revenue"], 4216000.0)   # thousand dollars to dollars
        self.assertEqual(by["total_customers"], 3270.0)
        self.assertEqual(set(t["entity"]), {"eia861:55:MS:A:TVA"})
        self.assertEqual(set(t["geo"]), {"US-MS"})
        self.assertEqual(dict(zip(t["variable"], t["unit"]))["total_sales"], "MWh")

    def test_imputed_rows_and_the_aggregates_are_not_taken(self):
        imputed = ROW_A[:5] + ["I"] + ROW_A[6:]
        withheld = [2025, 88888, "Withheld", "D", "Bundled", "O", "TX", "Retail Power Marketer", "ERCO"] + ["."] * 15
        adjust = [2025, 99999, "Adjustment 2025", "A", "Bundled", "O", "HI", None, None] + [1.0] * 15
        self.assertEqual(len(es.sheet_rows(sheet(imputed, withheld, adjust), 2025, "u", "r")), 0)

    def test_a_dot_cell_has_no_row(self):
        row = ROW_A[:18] + [".", ".", "."] + ROW_A[21:]   # transportation withheld
        t = es.sheet_rows(sheet(row), 2025, "u", "r")
        self.assertEqual(len(t), 12)
        self.assertFalse(t["variable"].str.startswith("transportation").any())

    def test_a_repeated_key_stops_the_run(self):
        with self.assertRaisesRegex(RuntimeError, "given twice"):
            es.sheet_rows(sheet(ROW_A, ROW_A), 2025, "u", "r")

    def test_2019s_extra_column_is_read_by_its_heading(self):
        # session 495: 2019's sheet holds a "Short Form" column after the BA code, which a positional read shifted
        head = [h[:9] + [x] + h[9:] for h, x in zip(HEAD, [None, None, "Short Form"])]
        row = ROW_A[:9] + ["N"] + ROW_A[9:]
        by = dict(zip(*[es.sheet_rows(sheet(row, head=head), 2025, "u", "r")[c] for c in ("variable", "value")]))
        self.assertEqual((by["residential_revenue"], by["total_sales"], by["total_customers"]), (4216000.0, 168839.0, 3270.0))

    def test_a_missing_heading_stops_the_run(self):
        head = [h[:23] for h in HEAD]   # the total's customers gone
        with self.assertRaisesRegex(RuntimeError, "headings lack"):
            es.sheet_rows(sheet(ROW_A[:23], head=head), 2025, "u", "r")

    def test_the_newest_zip_or_the_year_asked(self):
        html = '<a href="archive/zip/f86199.zip"></a><a href="zip/f8612023er.zip"></a><a href="zip/f8612025.zip"></a><a href="archive/zip/f8612024.zip"></a>'
        self.assertEqual(es.zip_url(html), (es.PAGE + "zip/f8612025.zip", 2025))
        self.assertEqual(es.zip_url(html, 2024), (es.PAGE + "archive/zip/f8612024.zip", 2024))
        with self.assertRaises(RuntimeError):
            es.zip_url(html, 2010)


if __name__ == "__main__":
    unittest.main()

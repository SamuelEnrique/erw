"""Session 689: EIA-861M's aggregates of 2017 to 2021 ("Adjustment <year>", utility 0; "Total EPM", 88888) leave the table.

Energy Research Warehouse (ERW). The 2017 to 2021 files name EIA's estimate of the utilities outside the sample
"Adjustment <year>" and its state totals "Total EPM"; neither name matched the connector's rule, and the table held
9,360 rows of each a year. warehouse/connectors/eia861m_sales.py now leaves out EIA's aggregate numbers (0, 88888, 99999)
whatever their name. Rows in the form of session 511's (that test's real Alaska row of 2025, renamed and redated here as
the 2017 file names its aggregates); no network.

    python -m unittest tests.test_session689 -v
"""

import os
import sys
import unittest

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
sys.path.insert(0, os.path.join(ROOT, "tests"))
sys.path.insert(0, os.path.join(ROOT, "warehouse", "connectors"))
import eia861m_sales as M  # noqa: E402
import test_session511 as T  # noqa: E402


def as_2017(row, number, name):
    r = list(row)
    r[0], r[2], r[3] = 2017, number, name
    return r


class TheAggregatesOf2017To2021(unittest.TestCase):
    def test_left_out_by_number(self):
        rows = [as_2017(T.ROWS[0], 0, "Adjustment 2017"), as_2017(T.ROWS[1], 213, "Alaska Electric Light & Power Co."),
                as_2017(T.ROWS[3], 88888, "Total EPM"), as_2017(T.ROWS[4], 88888, "US Total EPM")]
        t = M.sheet_rows(T.frame(rows=rows), 2017, "u", "r")
        self.assertEqual(sorted(t["entity"].unique()), ["eia861m:213:AK"])
        self.assertEqual(len(t), 15)

    def test_99999_too(self):
        rows = [as_2017(T.ROWS[1], 213, "Alaska Electric Light & Power Co."), as_2017(T.ROWS[2], 99999, "Some aggregate")]
        t = M.sheet_rows(T.frame(rows=rows), 2017, "u", "r")
        self.assertEqual(sorted(t["entity"].unique()), ["eia861m:213:AK"])

    def test_the_numbers(self):
        self.assertEqual(M.NOT_UTILITY_NUMBERS, {0, 88888, 99999})


if __name__ == "__main__":
    unittest.main()

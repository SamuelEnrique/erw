"""Session 7019 (chain 301, done-line request 20): the stored summary of ferc_eqr_contracts counts the rows and the
priced rows by quarter of execution, product group (energy, capacity, tolling, other) and delivery balancing authority
(trimmed, in capitals, "not stated" for none). Every name here is made up. No request, no model call."""
import os
import sys
import unittest
from unittest import mock

import pandas as pd

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
sys.path.insert(0, os.path.join(ROOT, "warehouse", "supabase"))
import load  # noqa: E402


class ByQuarterGroupAuthority(unittest.TestCase):
    def test_the_counts(self):
        df = pd.DataFrame({"event_date": ["2026-04-03T00:00:00Z", "2026-05-01T00:00:00Z", "2026-06-30T00:00:00Z", "2026-08-01T00:00:00Z"],
                           "x_rate": ["5", "", "6", "7"],
                           "x_product_name": ["Energy", "CAPACITY", "ENERGY", "Booked Out Power"],
                           "x_point_of_delivery_balancing_authority": [" duk", "", "DUK ", "SOCO"],
                           "x_quarter": ["2026_Q2"] * 4})
        with mock.patch.object(load, "eqr_largest", lambda *a, **k: None), mock.patch.object(load, "eqr_terms", lambda *a, **k: None):
            got = load.eqr_summary(df)["by_quarter_group_ba"]
        self.assertEqual(got, [
            {"quarter": "2026_Q2", "group": "capacity", "ba": "not stated", "rows": 1, "priced": 0},
            {"quarter": "2026_Q2", "group": "energy", "ba": "DUK", "rows": 2, "priced": 2},
            {"quarter": "2026_Q3", "group": "other", "ba": "SOCO", "rows": 1, "priced": 1},
        ])
        self.assertEqual(sum(r["rows"] for r in got), len(df))


if __name__ == "__main__":
    unittest.main()

"""Session 8002 (chain 501, part C): the pair rule of warehouse/derived/interchange_pairs.py on small frames written here,
and the page file's keys where the data machine has written it.

Energy Research Warehouse (ERW). docs/methods/interchange_pairs.md, docs/state/page_files_regions.md section 7.

    python -m unittest tests.test_session8002_interchange_pairs -v
"""

import json
import os
import sys
import unittest

import numpy as np
import pandas as pd

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
sys.path.insert(0, os.path.join(ROOT, "warehouse", "connectors"))
sys.path.insert(0, os.path.join(ROOT, "warehouse", "derived"))
import interchange_pairs as ipairs  # noqa: E402

PAGE = os.path.join(ROOT, "site", "data", "regions", "trade_matrix.json")


def hours(a, b):
    ts = pd.date_range("2025-08-01T04:00Z", periods=len(a), freq="h")
    return pd.DataFrame({"level": "ba", "A": "CPLE", "B": "DUK", "ts": ts, "a": a, "b": b})


class PairRule(unittest.TestCase):
    def rows(self, w):
        acc = ipairs.accumulate(w, pd.Series("2025-08-01", index=w.index))
        return ipairs.pair_rows(acc, "P1D", lambda k: f"{k}T00:00:00Z").iloc[0]

    def test_mean_and_gap_over_the_hours_both_reported(self):
        r = self.rows(hours([100.0, 110.0, 120.0], [90.0, 100.0, np.nan]))
        self.assertEqual(r["x_a_report_mwh"], 330.0)
        self.assertEqual(r["x_b_report_mwh"], 190.0)
        self.assertEqual(r["x_hours_both"], 2)
        self.assertEqual(r["x_gap_mwh"], 20.0)
        self.assertEqual(r["value"], 200.0)            # (100 + 90) / 2 + (110 + 100) / 2
        self.assertEqual(r["x_basis"], "mean")
        self.assertEqual(r["x_direction"], "a_to_b")

    def test_one_side_only(self):
        r = self.rows(hours([np.nan, np.nan], [-50.0, -60.0]))
        self.assertEqual(r["x_basis"], "b")
        self.assertEqual(r["value"], -110.0)
        self.assertTrue(np.isnan(r["x_a_report_mwh"]))
        self.assertEqual(r["x_direction"], "b_to_a")

    def test_partial_sums_add_across_files(self):
        w1, w2 = hours([10.0], [10.0]), hours([30.0], [20.0])
        k = pd.Series("2025-08-01", index=[0])
        acc = pd.concat([ipairs.accumulate(w1, k), ipairs.accumulate(w2, k)], ignore_index=True)
        r = ipairs.pair_rows(acc, "P1D", lambda x: x).iloc[0]
        self.assertEqual((r["x_hours_a"], r["x_hours_both"], r["value"], r["x_gap_mwh"]), (2, 2, 35.0, 10.0))


@unittest.skipUnless(os.path.exists(PAGE), "the page file is written on the data machine")
class PageFile(unittest.TestCase):
    def test_contract_keys(self):
        d = json.load(open(PAGE, encoding="utf-8"))
        for k in ("built", "tables", "method", "license", "years", "regions", "region_pairs", "ba_pairs", "partners"):
            self.assertIn(k, d)
        p = d["region_pairs"][0]
        self.assertEqual(set(p), {"a", "b", "year", "a_report_mwh", "b_report_mwh", "mean_mwh", "gap_mwh", "hours_a", "hours_b",
                                  "hours_both", "direction"})
        self.assertLess(p["a"], p["b"])


if __name__ == "__main__":
    unittest.main()

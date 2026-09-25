"""Idempotent writes: a rerun replaces overlapping rows and never duplicates them.

Energy Research Warehouse (ERW) test for iso_prices.write_csv / merge_series.
The fixture is 8 real rows copied from warehouse/output/ercot_dam_hub_prices.csv
(tests/fixtures/ercot_dam_sample.csv); no values are invented.

    python -m unittest discover -s tests -v
"""

import os
import shutil
import sys
import tempfile
import unittest

import pandas as pd

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
sys.path.insert(0, os.path.join(ROOT, "warehouse", "connectors"))
sys.path.insert(0, os.path.join(ROOT, "warehouse", "validate"))

import erw_validate  # noqa: E402
import iso_prices as ip  # noqa: E402

FIXTURE = os.path.join(ROOT, "tests", "fixtures", "ercot_dam_sample.csv")
NAME = "ercot_dam_hub_prices"
LATER_RUN = "2099-01-01T00:00:00Z"  # marks rows written by the "second run"; not a data value


def silent(_msg):
    pass


class MergeTest(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.mkdtemp()
        self._out = ip.OUT_DIR
        ip.OUT_DIR = self.tmp
        self.rows = ip.read_series(FIXTURE)
        self.path = os.path.join(self.tmp, NAME + ".csv")

    def tearDown(self):
        ip.OUT_DIR = self._out
        shutil.rmtree(self.tmp)

    def data(self):
        return ip.read_series(self.path)

    def second_pull(self):
        # rows 3..7: overlaps rows 3..5 of the first pull, adds rows 6..7
        second = self.rows.iloc[3:8].copy()
        second["retrieved_at"] = LATER_RUN
        return second

    def test_rerun_replaces_and_appends_without_duplicates(self):
        ip.write_csv(self.rows.iloc[0:6], NAME, ["first run"], silent)
        self.assertEqual(len(self.data()), 6)

        ip.write_csv(self.second_pull(), NAME, ["second run"], silent)
        d = self.data()
        self.assertEqual(len(d), 8)
        self.assertFalse(d.duplicated(ip.SERIES_KEY).any())
        later = d[d["retrieved_at"] == LATER_RUN]["ts_utc"].tolist()
        self.assertEqual(later, self.rows["ts_utc"].iloc[3:8].tolist())
        pd.testing.assert_series_equal(d["value"], self.rows["value"], check_names=False)

    def test_same_pull_twice_is_idempotent(self):
        ip.write_csv(self.rows.iloc[0:6], NAME, ["first run"], silent)
        ip.write_csv(self.second_pull(), NAME, ["second run"], silent)
        once = self.data()
        ip.write_csv(self.second_pull(), NAME, ["second run again"], silent)
        twice = self.data()
        pd.testing.assert_frame_equal(once, twice)
        self.assertEqual(len(twice), 8)

    def test_pull_with_repeated_key_is_refused(self):
        dup = pd.concat([self.rows.iloc[0:2], self.rows.iloc[0:1]], ignore_index=True)
        with self.assertRaises(RuntimeError):
            ip.write_csv(dup, NAME, ["bad run"], silent)
        self.assertFalse(os.path.exists(self.path))

    def test_merged_file_passes_validator(self):
        ip.write_csv(self.rows.iloc[0:6], NAME, ["first run"], silent)
        ip.write_csv(self.second_pull(), NAME, ["second run"], silent)
        report = erw_validate.validate(self.path)
        self.assertEqual(report["errors"], [])


if __name__ == "__main__":
    unittest.main()

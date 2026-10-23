"""Session 688: the package's remote test of the Stanford draft holds when a daily run has rewritten a table since its upload.

Energy Research Warehouse (ERW). package/tests/test_backends_stanford.py compared the draft's copy of a table with the
local one row for row. On 23 October 2026 the draft held 27,754 rows of eia_fuel_spot_prices and this machine 27,766: the
daily run rewrites the whole table (every row's retrieved_at new) and adds the trading days since. The comparison
(`same_as_local`) now asks, for a table rewritten since the upload, that every draft row is held here with the same
values apart from the run's own columns. Frames built here, no network.

    python -m unittest tests.test_session688 -v
"""

import importlib.util
import os
import unittest

import pandas as pd

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
spec = importlib.util.spec_from_file_location("stanford_t", os.path.join(ROOT, "package", "tests", "test_backends_stanford.py"))
S = importlib.util.module_from_spec(spec)
spec.loader.exec_module(S)

KEYS = ["entity", "variable", "ts_utc"]


def frame(days, retrieved, header):
    d = pd.DataFrame({"entity": "eia:henry_hub", "variable": "price", "ts_utc": [f"2026-10-{x:02d}T00:00:00Z" for x in days],
                      "value": [float(x) for x in days], "retrieved_at": retrieved, "vintage": ""})
    d.attrs = {"erw": {"header": header}}
    return d


H1 = ["Energy Research Warehouse (ERW): Daily fuel spot prices", "Retrieved: 20261022T103000Z (UTC)"]
H2 = ["Energy Research Warehouse (ERW): Daily fuel spot prices", "Retrieved: 20261022T143423Z (UTC)"]


class SameAsLocal(unittest.TestCase):
    def test_as_uploaded_needs_every_row(self):
        self.assertEqual(S.same_as_local(frame([1, 2], "a", H1), frame([1, 2], "a", H1), KEYS), "as uploaded")
        with self.assertRaises(AssertionError):
            S.same_as_local(frame([1, 2], "a", H1), frame([1, 2, 3], "a", H1), KEYS)

    def test_rewritten_since_the_upload_is_a_part(self):
        msg = S.same_as_local(frame([1, 2], "a", H1), frame([1, 2, 3], "b", H2), KEYS)
        self.assertIn("1 rows newer here", msg)

    def test_a_changed_value_or_a_lost_row_fails(self):
        rem = frame([1, 2], "a", H1)
        loc = frame([1, 2, 3], "b", H2)
        loc.loc[0, "value"] = 9.0
        with self.assertRaises(AssertionError):
            S.same_as_local(rem, loc, KEYS)
        with self.assertRaises(AssertionError):
            S.same_as_local(frame([1, 2, 4], "a", H1), frame([1, 2, 3], "b", H2), KEYS)

    def test_another_table_fails(self):
        other = ["Energy Research Warehouse (ERW): Weekly petroleum stocks", "Retrieved: 20261022T143423Z (UTC)"]
        with self.assertRaises(AssertionError):
            S.same_as_local(frame([1], "a", H1), frame([1, 2], "b", other), KEYS)


if __name__ == "__main__":
    unittest.main()

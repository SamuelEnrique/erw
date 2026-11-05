"""Session 864: the package's remote test of the Stanford draft, when a daily run has rewritten a table since its upload.

Energy Research Warehouse (ERW). Session 864 ran the eight remote tests session 688's ceiling left: four passed, and
four failed only because the draft is an earlier run's copy: EIA revised one recent spot price (98.73 in the draft,
94.99 here), and the citation's "Retrieved" date and coverage's window moved with the rewrite. The comparisons now allow
a publisher's revision of under 0.1 percent of the rows in common, compare a citation without its date, and compare
coverage on the columns a run does not move. Frames built here; no network.

    python -m unittest tests.test_session864 -v
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
H1 = ["Energy Research Warehouse (ERW): Daily fuel spot prices", "Retrieved: a"]
H2 = ["Energy Research Warehouse (ERW): Daily fuel spot prices", "Retrieved: b"]


def frame(values, retrieved, header):
    d = pd.DataFrame({"entity": "eia:wti", "variable": "price", "ts_utc": [f"t{i:05d}" for i in range(len(values))],
                      "value": values, "retrieved_at": retrieved, "vintage": ""})
    d.attrs = {"erw": {"header": header}}
    return d


class Revisions(unittest.TestCase):
    def test_one_revised_value_in_many_is_allowed_and_counted(self):
        rem = frame([1.0] * 2000, "a", H1)
        loc = frame([1.0] * 1999 + [2.0] + [3.0], "b", H2)
        self.assertIn("1 revised", S.same_as_local(rem, loc, KEYS))

    def test_many_revised_values_fail(self):
        rem = frame([1.0] * 100, "a", H1)
        loc = frame([2.0] * 100, "b", H2)
        with self.assertRaises(AssertionError):
            S.same_as_local(rem, loc, KEYS)


class CitationsAndCoverage(unittest.TestCase):
    def test_a_citation_without_its_date(self):
        a = "U.S. Energy Information Administration (EIA). 860m. https://www.eia.gov/x/. Retrieved 2026-10-21"
        b = a.replace("2026-10-21", "2026-10-22")
        self.assertEqual(S.undated(a), S.undated(b))
        self.assertNotEqual(S.undated(a), S.undated(a.replace("860m", "861m")))

    def test_coverage_columns_a_run_moves(self):
        self.assertEqual(set(S.RUN_COVERAGE) & {"table", "license", "sector", "tier", "source_report"}, set())
        self.assertLessEqual(S.REVISED_SHARE, 0.001)


if __name__ == "__main__":
    unittest.main()

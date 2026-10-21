"""Session 514: FERC Form 714's respondents, from PUDL's core_ferc714__respondent_id.

Energy Research Warehouse (ERW). Held on real rows of PUDL's table (session 484's saved file): the entity is the one
ferc714_area_demand_<year> uses, FERC's two ids and the EIA code are kept as published, a blank stays blank, and a
missing column or an id given twice stops the run.
"""

import os
import sys
import unittest

import pandas as pd

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
sys.path.insert(0, os.path.join(ROOT, "warehouse", "connectors"))
import ferc714_respondents as F  # noqa: E402

REAL = pd.DataFrame({
    "respondent_id_ferc714": pd.array([219, 90, 64], dtype="Int64"),
    "respondent_id_ferc714_csv": pd.array([None, 200, 172], dtype="Int64"),
    "respondent_id_ferc714_xbrl": pd.array(["C011267", "C011472", "C011518"], dtype="string"),
    "respondent_name_ferc714": pd.array(["Ameren Services Company", "Memphis Light, Gas and Water", "Gainesville Regional Utilities"], dtype="string"),
    "eia_code": pd.array([117, 12293, 6909], dtype="Int64"),
})


class TheRespondents(unittest.TestCase):
    def test_the_rows(self):
        t = F.respondents(REAL, F.URL, "2026-10-21T16:54:04Z", "2026-10-14T00:00:00Z")
        self.assertEqual(list(t["entity_id"]), ["ferc714:64", "ferc714:90", "ferc714:219"])
        r = t.set_index("entity_id").loc["ferc714:219"]
        self.assertEqual((r["entity_type"], r["name"], r["respondent_id_ferc714_csv"], r["respondent_id_ferc714_xbrl"], r["eia_code"]),
                         ("utility", "Ameren Services Company", "", "C011267", "117"))
        self.assertEqual(t.set_index("entity_id").loc["ferc714:90", "respondent_id_ferc714_csv"], "200")

    def test_a_missing_column_or_an_id_twice_stops(self):
        with self.assertRaises(RuntimeError):
            F.respondents(REAL.drop(columns=["eia_code"]), "u", "r", "")
        with self.assertRaises(RuntimeError):
            F.respondents(pd.concat([REAL, REAL.iloc[:1]]), "u", "r", "")

    def test_no_em_dash(self):
        for f in ("warehouse/connectors/ferc714_respondents.py", "tests/test_session514.py"):
            with open(os.path.join(ROOT, *f.split("/")), encoding="utf-8") as h:
                self.assertNotIn(chr(0x2014), h.read(), f)


if __name__ == "__main__":
    unittest.main()

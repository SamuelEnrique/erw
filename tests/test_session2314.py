"""Session 2314: the Central Statistical Bureau of Latvia's table ENB010m, Latvia's electricity production, imports and
exports.

Energy Research Warehouse (ERW). Tests warehouse/connectors/csp_latvia_electricity.py on a metadata and an answer built
here in PxWeb's and JSON-stat 2.0's forms (made up for the test, not CSP's): the query of every indicator and month; each
cell a row on the month's first day in MWh, the leading dots dropped from the name, the code kept as x_code; an empty cell
not written; a metadata without the three variables, a unit other than million kWh, a month of another form and a value
array of the wrong size stopping the run; the sector rule and the holds. No network.

    python -m unittest tests.test_session2314 -v
"""

import copy
import os
import sys
import unittest

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
sys.path.insert(0, os.path.join(ROOT, "warehouse", "connectors"))
sys.path.insert(0, os.path.join(ROOT, "warehouse", "metadata"))
sys.path.insert(0, os.path.join(ROOT, "warehouse", "redivis"))
import csp_latvia_electricity as S  # noqa: E402
import build_coverage as B  # noqa: E402
import release_v1 as R  # noqa: E402

BASE = {"source": "s", "source_url": "u", "retrieved_at": "r", "vintage": "v"}
META = {"variables": [{"code": "INDICATOR", "values": ["GEP", "WT"], "valueTexts": ["Total gross electricity production", "..wind turbines"]},
                      {"code": "ContentsCode", "values": ["ENB010m"], "valueTexts": ["million. kWh"]},
                      {"code": "TIME", "values": ["2026M07", "2026M08"], "valueTexts": ["2026M07", "2026M08"]}]}
JS = {"id": ["INDICATOR", "ContentsCode", "TIME"], "size": [2, 1, 2],
      "dimension": {"INDICATOR": {"category": {"index": {"GEP": 0, "WT": 1},
                                               "label": {"GEP": "Total gross electricity production", "WT": "..wind turbines"}}},
                    "ContentsCode": {"category": {"index": {"ENB010m": 0}}},
                    "TIME": {"category": {"index": {"2026M07": 0, "2026M08": 1}}}},
      "value": [450.5, 470, None, 60.25]}


class Parse(unittest.TestCase):
    def test_query(self):
        q = S.query(META)
        self.assertEqual([x["code"] for x in q["query"]], ["INDICATOR", "ContentsCode", "TIME"])
        self.assertEqual(q["query"][0]["selection"]["values"], ["GEP", "WT"])
        self.assertEqual(q["response"]["format"], "json-stat2")
        with self.assertRaises(RuntimeError):
            S.query({"variables": META["variables"][:2]})
        m = copy.deepcopy(META); m["variables"][1]["valueTexts"] = ["GWh"]
        with self.assertRaises(RuntimeError):
            S.query(m)

    def test_rows(self):
        t = S.parse(JS, BASE).set_index(["variable", "ts_utc"])
        self.assertEqual(len(t), 3)
        r = t.loc[("total_gross_electricity_production", "2026-07-01T00:00:00Z")]
        self.assertEqual((r.value, r.unit, r.x_code, r.geo), (450500.0, "MWh", "GEP", "LV"))
        self.assertEqual(t.loc[("wind_turbines", "2026-08-01T00:00:00Z")].value, 60250.0)
        self.assertNotIn(("wind_turbines", "2026-07-01T00:00:00Z"), t.index)

    def test_stops(self):
        bad = []
        x = copy.deepcopy(JS); x["id"] = ["INDICATOR", "TIME"]; bad.append(x)
        x = copy.deepcopy(JS); x["dimension"]["TIME"]["category"]["index"] = {"2026-07": 0, "2026M08": 1}; bad.append(x)
        x = copy.deepcopy(JS); x["value"] = [1, 2]; bad.append(x)
        for js in bad:
            with self.assertRaises((RuntimeError, KeyError)):
                S.parse(js, BASE)


class Registered(unittest.TestCase):
    def test_sector_and_holds(self):
        self.assertEqual(B.sector_of(S.NAME), "power")
        self.assertIn(S.NAME, R.STORAGE_HELD)
        with open(os.path.join(ROOT, "warehouse", "supabase", "live_set.yaml"), encoding="utf-8") as f:
            self.assertIn(f"  - {S.NAME}\n", f.read().replace("\r\n", "\n"))


if __name__ == "__main__":
    unittest.main()

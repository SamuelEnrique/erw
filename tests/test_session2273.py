"""Session 2273: Statistics Finland's table 12su, Finland's electricity supply and consumption.

Energy Research Warehouse (ERW). Tests warehouse/connectors/statfi_electricity.py on a metadata and an answer built here
in PxWeb's and JSON-stat 2.0's forms (made up for the test, not Statistics Finland's): the query of every month and line,
the quantity in GWh only; each cell a row on the month's first day in MWh, the line's code dropped from its name and kept
as x_code; an empty cell not written; a metadata without the three variables, a content other than GWh, a month of
another form and a value array of the wrong size stopping the run; the sector rule and the holds. No network.

    python -m unittest tests.test_session2273 -v
"""

import copy
import os
import sys
import unittest

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
sys.path.insert(0, os.path.join(ROOT, "warehouse", "connectors"))
sys.path.insert(0, os.path.join(ROOT, "warehouse", "metadata"))
sys.path.insert(0, os.path.join(ROOT, "warehouse", "redivis"))
import statfi_electricity as S  # noqa: E402
import build_coverage as B  # noqa: E402
import release_v1 as R  # noqa: E402

BASE = {"source": "s", "source_url": "u", "retrieved_at": "r", "vintage": "v"}
META = {"variables": [{"code": "timeperiod_m", "values": ["2026M05", "2026M06"]},
                      {"code": "energia_30_20200915", "values": ["SSS", "1.4"]},
                      {"code": "contentscode", "values": ["maara_gwh", "osuus_sahko_kul"]}]}
JS = {"id": ["timeperiod_m", "energia_30_20200915", "contentscode"], "size": [2, 2, 1],
      "dimension": {"timeperiod_m": {"category": {"index": {"2026M05": 0, "2026M06": 1}}},
                    "energia_30_20200915": {"category": {"index": {"SSS": 0, "1.4": 1},
                                                         "label": {"SSS": "SSS TOTAL ELECTRICITY CONSUMPTION", "1.4": "1.4 Nuclear power"}}},
                    "contentscode": {"category": {"index": {"maara_gwh": 0}}}},
      "value": [6500.5, 2900, None, 2800]}


class Parse(unittest.TestCase):
    def test_query(self):
        q = S.query(META)
        self.assertEqual(q["query"][2]["selection"]["values"], ["maara_gwh"])
        self.assertEqual(q["response"]["format"], "json-stat2")
        with self.assertRaises(RuntimeError):
            S.query({"variables": META["variables"][:2]})

    def test_rows(self):
        t = S.parse(JS, BASE).set_index(["variable", "ts_utc"])
        self.assertEqual(len(t), 3)
        r = t.loc[("total_electricity_consumption", "2026-05-01T00:00:00Z")]
        self.assertEqual((r.value, r.unit, r.x_code, r.geo), (6500500.0, "MWh", "SSS", "FI"))
        self.assertEqual(t.loc[("nuclear_power", "2026-06-01T00:00:00Z")].node, "1.4 Nuclear power")
        self.assertNotIn(("total_electricity_consumption", "2026-06-01T00:00:00Z"), t.index)

    def test_stops(self):
        bad = []
        x = copy.deepcopy(JS); x["id"] = ["Tid", "energia_30_20200915", "contentscode"]; bad.append(x)
        x = copy.deepcopy(JS); x["dimension"]["contentscode"]["category"]["index"] = {"osuus_sahko_kul": 0}; bad.append(x)
        x = copy.deepcopy(JS); x["dimension"]["timeperiod_m"]["category"]["index"] = {"2026-05": 0, "2026M06": 1}; bad.append(x)
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

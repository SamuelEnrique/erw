"""Session 2320: the Central Statistics Office's PxStat table MSM01, Ireland's gross and net electricity output.

Energy Research Warehouse (ERW). Tests warehouse/connectors/cso_ireland_electricity.py on an answer built here in
JSON-stat 2.0's form with PxStat's dimension names (made up for the test, not CSO's): each cell a row on the month's first
day in MWh, the statistic's name in snake case and its code kept as x_code, an empty cell not written, the answer's
"updated" returned; a unit other than Gigawatt Hours, a month of another form, a value array of the wrong size and an
answer of other dimensions stopping the run; the sector rule and the holds. No network.

    python -m unittest tests.test_session2320 -v
"""

import copy
import json
import os
import sys
import unittest

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
sys.path.insert(0, os.path.join(ROOT, "warehouse", "connectors"))
sys.path.insert(0, os.path.join(ROOT, "warehouse", "metadata"))
sys.path.insert(0, os.path.join(ROOT, "warehouse", "redivis"))
import cso_ireland_electricity as S  # noqa: E402
import build_coverage as B  # noqa: E402
import release_v1 as R  # noqa: E402

BASE = {"source": "s", "source_url": "u", "retrieved_at": "r", "vintage": ""}
GWH = {"decimals": 0, "label": "Gigawatt Hours", "position": "end"}
JS = {"id": ["STATISTIC", "TLIST(M1)", "C02196V02652"], "size": [2, 2, 1], "updated": "2026-10-09T11:00:00.000Z",
      "dimension": {"STATISTIC": {"category": {"index": ["MSM01C1", "MSM01C2"],
                                               "label": {"MSM01C1": "Gross Electricity Output", "MSM01C2": "Net Electricity Output"},
                                               "unit": {"MSM01C1": GWH, "MSM01C2": GWH}}},
                    "TLIST(M1)": {"category": {"index": ["202607", "202608"]}},
                    "C02196V02652": {"category": {"index": ["-"]}}},
      "value": [None, None, 2500, 2610.5]}


def enc(d):
    return json.dumps(d).encode("utf-8")


class Parse(unittest.TestCase):
    def test_rows(self):
        t, updated = S.parse(enc(JS), BASE)
        self.assertEqual(updated, "2026-10-09T11:00:00.000Z")
        t = t.set_index(["variable", "ts_utc"])
        self.assertEqual(len(t), 2)
        r = t.loc[("net_electricity_output", "2026-08-01T00:00:00Z")]
        self.assertEqual((r.value, r.unit, r.x_code, r.geo, r.node), (2610500.0, "MWh", "MSM01C2", "IE", "Net Electricity Output"))
        self.assertNotIn(("gross_electricity_output", "2026-07-01T00:00:00Z"), t.index)

    def test_stops(self):
        bad = []
        x = copy.deepcopy(JS); x["dimension"]["STATISTIC"]["category"]["unit"]["MSM01C2"] = {"label": "Thousand Tonnes"}; bad.append(x)
        x = copy.deepcopy(JS); x["dimension"]["TLIST(M1)"]["category"]["index"] = ["2026M07", "202608"]; bad.append(x)
        x = copy.deepcopy(JS); x["value"] = [1, 2]; bad.append(x)
        x = copy.deepcopy(JS); x["id"] = ["STATISTIC", "TLIST(M1)"]; bad.append(x)
        for js in bad:
            with self.assertRaises((RuntimeError, KeyError)):
                S.parse(enc(js), BASE)


class Registered(unittest.TestCase):
    def test_sector_and_holds(self):
        self.assertEqual(B.sector_of(S.NAME), "power")
        self.assertIn(S.NAME, R.STORAGE_HELD)
        with open(os.path.join(ROOT, "warehouse", "supabase", "live_set.yaml"), encoding="utf-8") as f:
            self.assertIn(f"  - {S.NAME}\n", f.read().replace("\r\n", "\n"))


if __name__ == "__main__":
    unittest.main()

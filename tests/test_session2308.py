"""Session 2308: SingStat Table Builder's M890831 and M890841, Singapore's electricity generation and consumption.

Energy Research Warehouse (ERW). Tests warehouse/connectors/singstat_electricity.py on answers built here in Table
Builder's form (made up for the test, not SingStat's): a monthly and an annual table's rows, each cell a row in MWh on the
period's first day, the table's code before the row's name, a blank or "na" cell not written; a unit other than GWh, a
column key of another form and a value that is not a number stopping the run; the vintage from dataLastUpdated; the
sector rule and the holds. No network.

    python -m unittest tests.test_session2308 -v
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
import singstat_electricity as S  # noqa: E402
import build_coverage as B  # noqa: E402
import release_v1 as R  # noqa: E402

BASE = {"source": "s", "source_url": "u", "retrieved_at": "r", "vintage": "v"}
MONTHLY = {"Data": {"id": "M890831", "dataLastUpdated": "14/10/2026",
                    "row": [{"seriesNo": "1", "rowText": "Electricity Generation", "uoM": "Gigawatt Hours",
                             "columns": [{"key": "2026 May", "value": "5100.5"}, {"key": "2026 Jun", "value": "na"}]}]}}
ANNUAL = {"Data": {"id": "M890841", "dataLastUpdated": "23/06/2026",
                   "row": [{"seriesNo": "2.4", "rowText": "Households", "uoM": "Gigawatt Hours",
                            "columns": [{"key": "2024", "value": "8,200.1"}, {"key": "2023", "value": ""}]}]}}


def enc(d):
    return json.dumps(d).encode("utf-8")


class Parse(unittest.TestCase):
    def test_monthly(self):
        rows = S.parse(enc(MONTHLY), "M890831", BASE)
        self.assertEqual(len(rows), 1)
        r = rows[0]
        self.assertEqual((r["variable"], r["ts_utc"], r["value"], r["unit"], r["freq"], r["x_series"]),
                         ("m890831_electricity_generation", "2026-05-01T00:00:00Z", 5100500.0, "MWh", "P1M", "1"))

    def test_annual(self):
        rows = S.parse(enc(ANNUAL), "M890841", BASE)
        self.assertEqual([(r["variable"], r["ts_utc"], r["value"], r["freq"]) for r in rows],
                         [("m890841_households", "2024-01-01T00:00:00Z", 8200100.0, "P1Y")])

    def test_vintage(self):
        self.assertEqual(S.updated(enc(MONTHLY)), "2026-10-14T00:00:00Z")
        self.assertEqual(S.updated(enc({"Data": {"dataLastUpdated": "October 2026"}})), "")

    def test_stops(self):
        bad = []
        x = copy.deepcopy(MONTHLY); x["Data"]["row"][0]["uoM"] = "Thousand Tonnes"; bad.append(("M890831", x))
        x = copy.deepcopy(MONTHLY); x["Data"]["row"][0]["columns"][0]["key"] = "2026-05"; bad.append(("M890831", x))
        x = copy.deepcopy(ANNUAL); x["Data"]["row"][0]["columns"][0]["key"] = "2024 Jan"; bad.append(("M890841", x))
        x = copy.deepcopy(ANNUAL); x["Data"]["row"][0]["columns"][0]["value"] = "about 8"; bad.append(("M890841", x))
        x = copy.deepcopy(ANNUAL); x["Data"]["row"] = []; bad.append(("M890841", x))
        for table, d in bad:
            with self.assertRaises(RuntimeError):
                S.parse(enc(d), table, BASE)


class Registered(unittest.TestCase):
    def test_sector_and_holds(self):
        self.assertEqual(B.sector_of(S.NAME), "power")
        self.assertIn(S.NAME, R.STORAGE_HELD)
        with open(os.path.join(ROOT, "warehouse", "supabase", "live_set.yaml"), encoding="utf-8") as f:
            self.assertIn(f"  - {S.NAME}\n", f.read().replace("\r\n", "\n"))


if __name__ == "__main__":
    unittest.main()

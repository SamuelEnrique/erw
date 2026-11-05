"""Session 2397: Statistics Iceland's table IDN02101, the public power plants' installed capacity and generation.

Energy Research Warehouse (ERW). Tests warehouse/connectors/hagstofa_iceland_electricity.py on an answer built here in the
PxWeb JSON-stat 2.0 form (made up for the test, not Statistics Iceland's): the capacity in MW and the generation in MWh on
the year's first day, the share unit not taken, a cell without a number not written; dimensions not the expected, an
energy label not the two, a year not of four digits and a value array of the wrong size stopping the run; the sector rule
and the holds. No network.

    python -m unittest tests.test_session2397 -v
"""

import os
import sys
import unittest

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
sys.path.insert(0, os.path.join(ROOT, "warehouse", "connectors"))
sys.path.insert(0, os.path.join(ROOT, "warehouse", "metadata"))
sys.path.insert(0, os.path.join(ROOT, "warehouse", "redivis"))
import hagstofa_iceland_electricity as S  # noqa: E402
import build_coverage as B  # noqa: E402
import release_v1 as R  # noqa: E402

BASE = {"source": "s", "source_url": "u", "retrieved_at": "r", "vintage": "v"}
CAP, GEN = "Installed capacity at end of period, MW", "Annual generation of energy, GWh"


def answer(values=(502.7, 2421.4, 607, None, 100, 100, 100, 100), years=("1976", "1977"), energy=(CAP, GEN), unit_label="Unit"):
    return {"id": ["Eining", "Ár", "Orka"], "size": [2, len(years), 2], "value": list(values),
            "dimension": {"Eining": {"label": unit_label, "category": {"index": {"Q": 0, "F": 1}, "label": {"Q": "Magn", "F": "Hlutfall"}}},
                          "Ár": {"label": "Year", "category": {"index": {y: i for i, y in enumerate(years)}, "label": {y: y for y in years}}},
                          "Orka": {"label": "Energy", "category": {"index": {"1": 0, "2": 1}, "label": {"1": energy[0], "2": energy[1]}}}}}


class Parse(unittest.TestCase):
    def test_rows(self):
        rows = {(r["variable"], r["ts_utc"]): r for r in S.parse(answer(), "IDN02101", BASE)}
        self.assertEqual(len(rows), 3)
        c = rows[("capacity", "1976-01-01T00:00:00Z")]
        self.assertEqual((c["value"], c["unit"], c["freq"], c["geo"], c["entity"], c["x_table"]), (502.7, "MW", "P1Y", "IS", "hagstofa:is", "IDN02101"))
        self.assertEqual((rows[("generation", "1976-01-01T00:00:00Z")]["value"], rows[("generation", "1976-01-01T00:00:00Z")]["unit"]), (2421400.0, "MWh"))
        self.assertNotIn(("generation", "1977-01-01T00:00:00Z"), rows)

    def test_stops(self):
        for js in (answer(unit_label="Region"), answer(energy=(CAP, "Annual generation, TWh")), answer(years=("1976", "77")),
                   answer(values=(1, 2, 3))):
            with self.assertRaises(RuntimeError):
                S.parse(js, "IDN02101", BASE)


class Registered(unittest.TestCase):
    def test_sector_and_holds(self):
        self.assertEqual(S.TABLES, ["IDN02101"])
        self.assertEqual(B.sector_of(S.NAME), "power")
        self.assertIn(S.NAME, R.STORAGE_HELD)
        with open(os.path.join(ROOT, "warehouse", "supabase", "live_set.yaml"), encoding="utf-8") as f:
            self.assertIn(f"  - {S.NAME}\n", f.read().replace("\r\n", "\n"))


if __name__ == "__main__":
    unittest.main()

"""Session 2656: EDF SEI's annual electricity production by source on the French island grids.

Energy Research Warehouse (ERW). Tests warehouse/connectors/edf_sei_islands_electricity.py on a data-fair answer built here
(made up for the test, not EDF's): each source given its variable and its territory's code, a cell without a number not
written, the per cent columns not taken; a territory or column not in the map, a count of lines not the total, a negative
production and sources that miss the total stopping the run; the sector rule and the holds. No network.

    python -m unittest tests.test_session2656 -v
"""

import os
import sys
import unittest

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
sys.path.insert(0, os.path.join(ROOT, "warehouse", "connectors"))
sys.path.insert(0, os.path.join(ROOT, "warehouse", "metadata"))
sys.path.insert(0, os.path.join(ROOT, "warehouse", "redivis"))
import edf_sei_islands_electricity as A  # noqa: E402
import build_coverage as B  # noqa: E402
import release_v1 as R  # noqa: E402

BASE = {"source": "s", "source_url": "u", "retrieved_at": "r", "vintage": ""}


def line(**kw):
    ln = {"territoire_open_data": "Corse", "annee_prod": 2024, "moteurs_diesel": 600, "liaisons": 300, "solaire_photovoltaique": 100,
          "total": 1000, "part_enr": 10.0, "_id": "x", "_i": 1, "_rand": 5, "_score": None}
    ln.update(kw)
    return ln


def answer(lines, total=None):
    return {"total": len(lines) if total is None else total, "results": lines}


class Parse(unittest.TestCase):
    def test_rows(self):
        rows = A.parse(answer([line(), line(territoire_open_data="St Martin", liaisons=None, moteurs_diesel=850, solaire_photovoltaique=150)]),
                       BASE)
        r = {(x["entity"], x["ts_utc"][:4]): (x["variable"], x["value"], x["geo"]) for x in rows}
        self.assertEqual(r[("edf_sei:corsica:links", "2024")], ("net_imports", 300.0, "FR-20R"))
        self.assertEqual(r[("edf_sei:corsica:diesel", "2024")], ("generation", 600.0, "FR-20R"))
        self.assertEqual(r[("edf_sei:saint_martin:total", "2024")], ("supply", 1000.0, "MF"))
        self.assertNotIn(("edf_sei:saint_martin:links", "2024"), r)
        self.assertEqual(len(rows), 7)
        self.assertFalse([x for x in rows if "part" in x["entity"]])

    def test_stops(self):
        for js in (answer([line(territoire_open_data="Mayotte")]), answer([line(nucleaire=5)]), answer([line()], total=2),
                   answer([line(moteurs_diesel=-1, total=399)]), answer([line(total=1100)])):
            with self.assertRaises((RuntimeError, KeyError)):
                A.parse(js, BASE)


class Registered(unittest.TestCase):
    def test_sector_and_holds(self):
        self.assertEqual(B.sector_of(A.NAME), "power")
        self.assertIn(A.NAME, R.STORAGE_HELD)
        with open(os.path.join(ROOT, "warehouse", "supabase", "live_set.yaml"), encoding="utf-8") as f:
            self.assertIn(f"  - {A.NAME}\n", f.read().replace("\r\n", "\n"))


if __name__ == "__main__":
    unittest.main()

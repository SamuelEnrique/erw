"""Session 2651: ASUB's PxWeb table MI009, Aland's electricity supply by origin a year.

Energy Research Warehouse (ERW). Tests warehouse/connectors/asub_aland_electricity.py on a JSON-stat 2.0 answer built here (made
up for the test, not ASUB's): each origin given its variable and stated in MWh, a cell without a number not written; dimensions
not year, statistic and origin, an origin not in the map, a value array of the wrong size and origins that miss the total
stopping the run; the sector rule and the holds. No network.

    python -m unittest tests.test_session2651 -v
"""

import os
import sys
import unittest

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
sys.path.insert(0, os.path.join(ROOT, "warehouse", "connectors"))
sys.path.insert(0, os.path.join(ROOT, "warehouse", "metadata"))
sys.path.insert(0, os.path.join(ROOT, "warehouse", "redivis"))
import asub_aland_electricity as A  # noqa: E402
import build_coverage as B  # noqa: E402
import release_v1 as R  # noqa: E402

BASE = {"source": "s", "source_url": "u", "retrieved_at": "r", "vintage": ""}
ORIG = ["Import Sverige", "Import Finland", "Olja", "Vindkraft", "Bioenergi", "Solkraft", "Totalt"]


def answer(values=None, origins=None, dims=None):
    origins = origins or ORIG
    years = ["2024", "2025"]
    vals = values if values is not None else [100.0, 10.0, 0.0, 200.0, None, 5.0, 315.0,
                                              110.0, 5.0, 0.0, 210.0, 1.0, 9.0, 335.0]
    return {"id": dims or [A.YEAR, "statistik", "ursprung"], "size": [2, 1, len(origins)],
            "dimension": {A.YEAR: {"category": {"index": {y: i for i, y in enumerate(years)}, "label": {y: y for y in years}}},
                          "statistik": {"category": {"index": {"GWh": 0}, "label": {"GWh": "GWh (gigawattimmar)"}}},
                          "ursprung": {"category": {"index": {o: i for i, o in enumerate(origins)}, "label": {o: o for o in origins}}}},
            "value": vals}


class Parse(unittest.TestCase):
    def test_rows(self):
        rows = A.parse(answer(), BASE)
        r = {(x["entity"].split(":")[-1], x["ts_utc"][:4]): (x["variable"], x["value"]) for x in rows}
        self.assertEqual(r[("import_sweden", "2024")], ("imports", 100000.0))
        self.assertEqual(r[("wind", "2025")], ("generation", 210000.0))
        self.assertEqual(r[("total", "2025")], ("supply", 335000.0))
        self.assertNotIn(("bioenergy", "2024"), r)
        self.assertEqual(len(rows), 13)

    def test_stops(self):
        bad_total = [100.0, 10.0, 0.0, 200.0, None, 5.0, 320.0, 110.0, 5.0, 0.0, 210.0, 1.0, 9.0, 335.0]
        for js in (answer(dims=[A.YEAR, "statistik", "region"]), answer(origins=ORIG[:-1] + ["Annat"]), answer(values=[1.0] * 3),
                   answer(values=bad_total)):
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

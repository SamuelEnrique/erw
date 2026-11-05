"""Session 2502: Statistics Faroe Islands' tables UO03020 and UO03030 (SEV's electricity production by source and sales).

Energy Research Warehouse (ERW). Tests warehouse/connectors/hagstova_faroe_electricity.py on JSON-stat 2.0 answers built
here (made up for the test, not Statistics Faroe Islands'): the cells in the dimensions' order, a cell without a number
with no row, the categories mapped to their items; a category not in the map, the category dimension missing (an
answer to an empty query), a value array of the wrong size and a year not of four digits stopping the run; the query
selecting every category and year; the sector rule and the holds. No network.

    python -m unittest tests.test_session2502 -v
"""

import os
import sys
import unittest

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
sys.path.insert(0, os.path.join(ROOT, "warehouse", "connectors"))
sys.path.insert(0, os.path.join(ROOT, "warehouse", "metadata"))
sys.path.insert(0, os.path.join(ROOT, "warehouse", "redivis"))
import hagstova_faroe_electricity as S  # noqa: E402
import build_coverage as B  # noqa: E402
import release_v1 as R  # noqa: E402

BASE = {"source": "s", "source_url": "u", "retrieved_at": "r", "vintage": ""}


def answer(cats=("Total", "Hydro", "Wind"), years=("1990", "1991"), values=None, dims=("production", "year")):
    dim = {"production": {"label": "production", "category": {"index": {f"c{i}": i for i in range(len(cats))},
                                                              "label": {f"c{i}": c for i, c in enumerate(cats)}}},
           "year": {"label": "year", "category": {"index": {y: i for i, y in enumerate(years)}, "label": {y: y for y in years}}}}
    size = [len(cats) if d == "production" else len(years) for d in dims]
    n = size[0] * (size[1] if len(size) > 1 else 1)
    return {"id": list(dims), "size": size, "dimension": {d: dim[d] for d in dims},
            "value": values if values is not None else [float(k) for k in range(n)]}


class Parse(unittest.TestCase):
    def test_rows(self):
        js = answer(values=[100.0, 110.0, 70.0, None, 30.0, 40.0])
        rows = S.parse(js, "ork_elgerd", BASE)
        r = {(x["entity"], x["ts_utc"][:4]): x["value"] for x in rows}
        self.assertEqual(r[("hagstova:fo:total", "1990")], 100.0)
        self.assertEqual(r[("hagstova:fo:total", "1991")], 110.0)
        self.assertEqual(r[("hagstova:fo:hydro", "1990")], 70.0)
        self.assertNotIn(("hagstova:fo:hydro", "1991"), r)
        self.assertEqual(r[("hagstova:fo:wind", "1991")], 40.0)
        self.assertEqual(len(rows), 5)
        self.assertEqual({x["variable"] for x in rows}, {"generation"})
        self.assertEqual({x["unit"] for x in rows}, {"MWh"})
        self.assertEqual({x["x_table"] for x in rows}, {"UO03020"})

    def test_stops(self):
        bad = [answer(cats=("Total", "Nuclear")), answer(dims=("year",)), answer(values=[1.0, 2.0]), answer(years=("1990", "199x"))]
        for js in bad:
            with self.assertRaises(RuntimeError):
                S.parse(js, "ork_elgerd", BASE)

    def test_every_sales_group_mapped(self):
        self.assertEqual(len(S.TABLES["ork_elsola"][3]), 9)
        self.assertEqual(S.TABLES["ork_elsola"][1], "consumer groups")


class Registered(unittest.TestCase):
    def test_sector_and_holds(self):
        self.assertEqual(B.sector_of(S.NAME), "power")
        self.assertIn(S.NAME, R.STORAGE_HELD)
        with open(os.path.join(ROOT, "warehouse", "supabase", "live_set.yaml"), encoding="utf-8") as f:
            self.assertIn(f"  - {S.NAME}\n", f.read().replace("\r\n", "\n"))


if __name__ == "__main__":
    unittest.main()

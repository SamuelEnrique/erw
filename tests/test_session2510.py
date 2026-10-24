"""Session 2510: Statistics Greenland's Statbank tables ENX3VVE and ENX4NUK (renewable electricity, Nukissiorfiit's sales).

Energy Research Warehouse (ERW). Tests warehouse/connectors/statgl_greenland_electricity.py on JSON-stat 2.0 answers built
here (made up for the test, not Statistics Greenland's): the MWh unit taken and TJ not, the electricity products taken and
water not, kWh to MWh, the locations' slugs, a cell without a number with no row; dimensions not the expected ones, a value
array of the wrong size and a year not of four digits stopping the run; the sector rule and the holds. No network.

    python -m unittest tests.test_session2510 -v
"""

import os
import sys
import unittest

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
sys.path.insert(0, os.path.join(ROOT, "warehouse", "connectors"))
sys.path.insert(0, os.path.join(ROOT, "warehouse", "metadata"))
sys.path.insert(0, os.path.join(ROOT, "warehouse", "redivis"))
import statgl_greenland_electricity as S  # noqa: E402
import build_coverage as B  # noqa: E402
import release_v1 as R  # noqa: E402

BASE = {"source": "s", "source_url": "u", "retrieved_at": "r", "vintage": ""}


def answer(dims, values):
    """dims: [(code, [labels])]; values in the dimensions' order."""
    d = {c: {"label": c, "category": {"index": {str(i): i for i in range(len(ls))}, "label": {str(i): l for i, l in enumerate(ls)}}}
         for c, ls in dims}
    return {"id": [c for c, _ in dims], "size": [len(ls) for _, ls in dims], "dimension": d, "value": values}


VVE = [("unit", ["TJ", "MWh"]), ("type", ["Production"]), ("source", ["Total", "Hydropower"]), ("time", ["2023", "2024"])]
NUK = [("product", ["Electricity, normal rates [kWh]", "Water, normal rates [m3]"]),
       ("location", ["Total sales", "- here of in towns", "- Nuuk town"]), ("time", ["2024"])]


class Parse(unittest.TestCase):
    def test_vve(self):
        rows = S.parse(answer(VVE, [1, 2, 3, 4, 100.0, 110.0, 90.0, None]), "ENX3VVE", BASE)
        r = {(x["entity"], x["ts_utc"][:4]): x["value"] for x in rows}
        self.assertEqual(r, {("statgl:gl:total", "2023"): 100.0, ("statgl:gl:total", "2024"): 110.0, ("statgl:gl:hydropower", "2023"): 90.0})
        self.assertEqual({x["variable"] for x in rows}, {"renewable_production"})

    def test_nuk(self):
        rows = S.parse(answer(NUK, [5000.0, 4000.0, 3000.0, 7, 8, 9]), "ENX4NUK", BASE)
        r = {x["entity"]: x["value"] for x in rows}
        self.assertEqual(r, {"statgl:gl:total_sales": 5.0, "statgl:gl:towns": 4.0, "statgl:gl:nuuk_town": 3.0})
        self.assertEqual({x["variable"] for x in rows}, {"sales_normal_rates"})
        self.assertEqual({x["unit"] for x in rows}, {"MWh"})

    def test_slugs(self):
        self.assertEqual(S.slug("- Settlements in Kommune Kujalleq"), "settlements_in_kommune_kujalleq")
        self.assertEqual(S.slug("- here of in settlements"), "settlements")

    def test_stops(self):
        bad = [(answer(VVE[1:], [1.0] * 4), "ENX3VVE"), (answer(VVE, [1.0] * 3), "ENX3VVE"),
               (answer(NUK[:2] + [("time", ["20x4"])], [1.0] * 6), "ENX4NUK")]
        for js, table in bad:
            with self.assertRaises(RuntimeError):
                S.parse(js, table, BASE)


class Registered(unittest.TestCase):
    def test_sector_and_holds(self):
        self.assertEqual(B.sector_of(S.NAME), "power")
        self.assertIn(S.NAME, R.STORAGE_HELD)
        with open(os.path.join(ROOT, "warehouse", "supabase", "live_set.yaml"), encoding="utf-8") as f:
            self.assertIn(f"  - {S.NAME}\n", f.read().replace("\r\n", "\n"))


if __name__ == "__main__":
    unittest.main()

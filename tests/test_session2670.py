"""Session 2670: ASUB's PxWeb table MI010, Aland's electricity sales by distributor and sector, with its exports.

Energy Research Warehouse (ERW). Tests warehouse/connectors/asub_aland_sales.py on a JSON-stat 2.0 answer built here (made up
for the test, not ASUB's): each region and sector given its entity and variable and stated in MWh, exports as exports, a cell
without a number not written; dimensions not as MI010's, a region not in the map, a value array of the wrong size, sectors that
miss their total by more than the rounding and distributors that miss Aland's total stopping the run; the sector rule and the
holds. No network.

    python -m unittest tests.test_session2670 -v
"""

import os
import sys
import unittest

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
sys.path.insert(0, os.path.join(ROOT, "warehouse", "connectors"))
sys.path.insert(0, os.path.join(ROOT, "warehouse", "metadata"))
sys.path.insert(0, os.path.join(ROOT, "warehouse", "redivis"))
import asub_aland_sales as A  # noqa: E402
import build_coverage as B  # noqa: E402
import release_v1 as R  # noqa: E402

BASE = {"source": "s", "source_url": "u", "retrieved_at": "r", "vintage": ""}
REG = list(A.REGIONS)
SEC = list(A.SECTORS)


def answer(values, regions=None, dims=None):
    regions = regions or REG
    years = ["2025"]
    cat = lambda xs: {"category": {"index": {x: i for i, x in enumerate(xs)}, "label": {x: x for x in xs}}}
    return {"id": dims or [A.YEAR, "region", A.STAT, "bransch"], "size": [1, len(regions), 1, len(SEC)],
            "dimension": {A.YEAR: cat(years), "region": cat(regions), (dims or [0, 0, A.STAT])[2]: {"category": {
                "index": {"GWh (gigawattimmar)": 0}, "label": {"GWh (gigawattimmar)": "GWh (gigawattimmar)"}}}, "bransch": cat(SEC)},
            "value": values}


# regions in REG's order (Aland, Mariehamn, the rural co-op, export); sectors in SEC's (total, households, agriculture,
# industry, services, public sector)
GOOD = [276, 100, 10, 50, 70, 46,
        98, 40, None, 20, 25, 13,
        178, 60, 10, 30, 45, 33,
        47, None, None, None, None, None]


class Parse(unittest.TestCase):
    def test_rows(self):
        rows = A.parse(answer(GOOD), BASE)
        r = {x["entity"]: (x["variable"], x["value"]) for x in rows}
        self.assertEqual(r["asub:ax:aland:total"], ("sales", 276000.0))
        self.assertEqual(r["asub:ax:mariehamns_energi:households"], ("sales", 40000.0))
        self.assertEqual(r["asub:ax:export:total"], ("exports", 47000.0))
        self.assertNotIn("asub:ax:mariehamns_energi:agriculture", r)
        self.assertEqual(len(rows), 6 + 5 + 6 + 1)

    def test_stops(self):
        far = list(GOOD)
        far[0] = 290  # the sectors make 276
        apart = list(GOOD)
        apart[6], apart[7] = 110, 52  # Mariehamn 110 and the co-op 178 make 288, not 276
        for js in (answer(GOOD, dims=[A.YEAR, "omrade", A.STAT, "bransch"]), answer(GOOD, regions=REG[:3] + ["Import"]),
                   answer(GOOD[:5]), answer(far), answer(apart)):
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

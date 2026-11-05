"""Session 2665: the Alaska Energy Data Gateway's monthly electrical generation by community, kept a row a service area.

Energy Research Warehouse (ERW). Tests warehouse/connectors/aedg_alaska_generation.py on an answer built here (made up for the
test, not the Gateway's): the communities' repeats of a service area's figure kept once, the node naming the first community
and the others, a blank fuel kept as fuel_not_given, a record with no year and the fuel price not written, a negative figure
kept; a total not the records' count, a fuel not in the map, communities that disagree and a month of 13 stopping the run; the
sector rule and the holds. No network.

    python -m unittest tests.test_session2665 -v
"""

import os
import sys
import unittest

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
sys.path.insert(0, os.path.join(ROOT, "warehouse", "connectors"))
sys.path.insert(0, os.path.join(ROOT, "warehouse", "metadata"))
sys.path.insert(0, os.path.join(ROOT, "warehouse", "redivis"))
import aedg_alaska_generation as A  # noqa: E402
import build_coverage as B  # noqa: E402
import release_v1 as R  # noqa: E402

BASE = {"source": "s", "source_url": "u", "retrieved_at": "r", "vintage": ""}


def rec(name, sa="8_1", year="2021", month="1", fuel="Natural Gas", mwh="100.5", price=None):
    return {"fips_code": "02", "name": name, "aea_plant_ids": "101", "service_area_geom_id": sa, "year": year, "month": month,
            "fuel_type": fuel, "service_area_pce_fuel_price": price, "service_area_generation_mwh": mwh}


def answer(recs, total=None):
    return {"recordsTotal": len(recs) if total is None else total, "data": recs, "columns": []}


GOOD = [rec("Anchorage"), rec("Eagle River"), rec("Anchorage", fuel="Wind", mwh="-2.5"), rec("Eagle River", fuel="Wind", mwh="-2.5"),
        rec("Adak", sa="684_1", fuel="Distillate Fuel Oil", mwh="380.127", price="4.80"), rec("Adak", sa="684_1", fuel=None, mwh="5"),
        rec("Aleneva", sa=None, year=None, month=None, fuel=None, mwh=None)]


class Parse(unittest.TestCase):
    def test_rows(self):
        t = A.parse(answer(GOOD), BASE)
        r = {e: (v, n) for e, v, n in zip(t.entity, t.value, t.node)}
        self.assertEqual(len(t), 4)
        self.assertEqual(r["aedg:ak:8_1:natural_gas"], (100.5, "Anchorage and 1 other communities"))
        self.assertEqual(r["aedg:ak:8_1:wind"][0], -2.5)
        self.assertEqual(r["aedg:ak:684_1:distillate_oil"], (380.127, "Adak"))
        self.assertIn("aedg:ak:684_1:fuel_not_given", r)
        self.assertEqual(set(t.ts_utc), {"2021-01-01T00:00:00Z"})
        self.assertEqual(set(t.geo), {"US-AK"})

    def test_stops(self):
        for js in (answer(GOOD, total=9), answer(GOOD + [rec("X", fuel="Nuclear")]), answer(GOOD + [rec("Girdwood", mwh="101")]),
                   answer(GOOD + [rec("Y", sa="9_1", month="13")])):
            with self.assertRaises(RuntimeError):
                A.parse(js, BASE)


class Registered(unittest.TestCase):
    def test_sector_and_holds(self):
        self.assertEqual(B.sector_of(A.NAME), "power")
        self.assertIn(A.NAME, R.STORAGE_HELD)
        with open(os.path.join(ROOT, "warehouse", "supabase", "live_set.yaml"), encoding="utf-8") as f:
            self.assertIn(f"  - {A.NAME}\n", f.read().replace("\r\n", "\n"))


if __name__ == "__main__":
    unittest.main()

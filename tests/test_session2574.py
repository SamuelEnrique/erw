"""Session 2574: SBS's Electricity Statistics 2025, tables E1 and E3 (Samoa's production by source, EPC's sales by category).

Energy Research Warehouse (ERW). Tests warehouse/connectors/sbs_samoa_electricity.py on sheet rows built here (made up for
the test, not SBS's): E1's sources by their header (the shares passed over) adding to the total, E3's categories taken and
its total written only for a year where it equals them; a source missing its total, a share row where MWh was expected, a
category not in the map, a year missing and a negative figure stopping the run; the sector rule and the holds. No network.

    python -m unittest tests.test_session2574 -v
"""

import os
import sys
import unittest

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
sys.path.insert(0, os.path.join(ROOT, "warehouse", "connectors"))
sys.path.insert(0, os.path.join(ROOT, "warehouse", "metadata"))
sys.path.insert(0, os.path.join(ROOT, "warehouse", "redivis"))
import sbs_samoa_electricity as S  # noqa: E402
import build_coverage as B  # noqa: E402
import release_v1 as R  # noqa: E402

BASE = {"source": "s", "source_url": "u", "retrieved_at": "r", "vintage": "v"}


def e1(years=(2024, 2025), diesel=100.0, units="MWh"):
    head = [None, "Year", "Total", None, "Diesel", None, "Hydro", None, "Coconut", None, "Solar ", None, "Wind", None, "Biomass", None]
    unit = [None, None] + [units, "%"] * 7
    rows = [[None, "Table E1 : Total Electricity Production by all Sources 2008-2025 (MWh) "], [None, None], head, unit]
    for y in years:
        rows.append([None, y, 160.0, 100, diesel, 62.5, 40.0, 25, 0, 0, 20.0, 12.5, 0, 0, 0, 0])
    return rows + [[None, "Source: Electric Power Corporation (EPC)"]]


def e3(extra=None, neg=False):
    rows = [[None, "Table E3 : EPC Electricity Sales, 2008-2024(MWh)"], [None, None], [None, None, 2015, 2016, 2017, 2018, 2019]]
    for name, _ in S.CATEGORIES:
        rows.append([None, name, 10.0, 10.0, -1.0 if neg and name == "Hotels" else 10.0, 10.0, 10.0])
    if extra:
        rows.append([None, extra, 1.0, 1.0, 1.0, 1.0, 1.0])
    rows.append([None, "TOTAL", 999.0, 90.0, 90.0, 90.0, 90.0])
    return rows + [[None, "Source: Electric Power Corporation (EPC) "]]


class Parse(unittest.TestCase):
    def test_rows(self):
        p = S.parse_e1(e1(), BASE)
        s, skipped = S.parse_e3(e3(), BASE)
        r = {(x["entity"], x["variable"], x["ts_utc"][:4]): x["value"] for x in p + s}
        self.assertEqual(r[("sbs:ws:diesel", "production", "2025")], 100.0)
        self.assertEqual(r[("sbs:ws:solar", "production", "2024")], 20.0)
        self.assertEqual(r[("sbs:ws:street_lights", "sales", "2016")], 10.0)
        self.assertEqual(r[("sbs:ws:total", "sales", "2019")], 90.0)
        self.assertNotIn(("sbs:ws:total", "sales", "2015"), r)
        self.assertEqual(skipped, [2015])
        self.assertEqual(len(p), 7 * 2)
        self.assertEqual(len(s), 9 * 5 + 4)

    def test_stops(self):
        for f in (lambda: S.parse_e1(e1(diesel=90.0), BASE), lambda: S.parse_e1(e1(units="%"), BASE),
                  lambda: S.parse_e1(e1(years=(2023, 2025)), BASE), lambda: S.parse_e3(e3(extra="Fisheries"), BASE),
                  lambda: S.parse_e3(e3(neg=True), BASE)):
            with self.assertRaises(RuntimeError):
                f()


class Registered(unittest.TestCase):
    def test_sector_and_holds(self):
        self.assertEqual(B.sector_of(S.NAME), "power")
        self.assertIn(S.NAME, R.STORAGE_HELD)
        with open(os.path.join(ROOT, "warehouse", "supabase", "live_set.yaml"), encoding="utf-8") as f:
            self.assertIn(f"  - {S.NAME}\n", f.read().replace("\r\n", "\n"))


if __name__ == "__main__":
    unittest.main()

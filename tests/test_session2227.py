"""Session 2227: Statistics Norway's table 14091, Norway's electricity balance.

Energy Research Warehouse (ERW). Tests warehouse/connectors/ssb_electricity.py on a metadata and an answer built here in
PxWeb's form (made up for the test, not SSB's): the query of every line and month; each cell a row on the month's first
day in MWh, its line's name in snake case and SSB's code kept; an empty cell counted, not written; a metadata without the
three variables, a month of another form, a line not in the metadata and a value not a number stopping the run; the
sector rule and the holds. No network.

    python -m unittest tests.test_session2227 -v
"""

import os
import sys
import unittest

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
sys.path.insert(0, os.path.join(ROOT, "warehouse", "connectors"))
sys.path.insert(0, os.path.join(ROOT, "warehouse", "metadata"))
sys.path.insert(0, os.path.join(ROOT, "warehouse", "redivis"))
import ssb_electricity as S  # noqa: E402
import build_coverage as B  # noqa: E402
import release_v1 as R  # noqa: E402

META = {"variables": [
    {"code": "Produk2", "values": ["1", "1.1", "7.41"], "valueTexts": ["Total electricity generation", "Hydro power generation", "Consumption in dwellings"]},
    {"code": "ContentsCode", "values": ["Kraft"], "valueTexts": ["Electricity power"]},
    {"code": "Tid", "values": ["2025M12", "2026M01"], "valueTexts": ["2025M12", "2026M01"]}]}
BASE = {"source": "s", "source_url": "u", "retrieved_at": "r", "vintage": "v"}


def answer(data):
    return {"columns": [{"code": "Produk2"}, {"code": "Tid"}, {"code": "Kraft"}], "data": data}


class Parse(unittest.TestCase):
    def test_query(self):
        q = S.query(META)
        self.assertEqual([x["code"] for x in q["query"]], ["Produk2", "ContentsCode", "Tid"])
        self.assertEqual(q["query"][2]["selection"]["values"], ["2025M12", "2026M01"])
        with self.assertRaises(RuntimeError):
            S.query({"variables": META["variables"][:2]})

    def test_rows(self):
        s, empty = S.parse(answer([{"key": ["1", "2026M01"], "values": ["14500123"]}, {"key": ["1.1", "2026M01"], "values": ["13800000"]},
                                   {"key": ["7.41", "2025M12"], "values": [".."]}]), META, BASE)
        self.assertEqual(empty, 1)
        r = s.set_index("variable").loc["total_electricity_generation"]
        self.assertEqual((r.ts_utc, r.value, r.unit, r.geo, r.x_code), ("2026-01-01T00:00:00Z", 14500123.0, "MWh", "NO", "1"))
        self.assertEqual(s.set_index("variable").loc["hydro_power_generation"].node, "Hydro power generation")

    def test_stops(self):
        for data in ([{"key": ["1", "2026-01"], "values": ["1"]}], [{"key": ["9", "2026M01"], "values": ["1"]}],
                     [{"key": ["1", "2026M01"], "values": ["many"]}]):
            with self.assertRaises(RuntimeError):
                S.parse(answer(data), META, BASE)
        with self.assertRaises(RuntimeError):
            S.parse({"columns": [{"code": "Tid"}], "data": []}, META, BASE)


class Registered(unittest.TestCase):
    def test_sector_and_holds(self):
        self.assertEqual(B.sector_of(S.NAME), "power")
        self.assertIn(S.NAME, R.STORAGE_HELD)
        with open(os.path.join(ROOT, "warehouse", "supabase", "live_set.yaml"), encoding="utf-8") as f:
            self.assertIn(f"  - {S.NAME}\n", f.read().replace("\r\n", "\n"))


if __name__ == "__main__":
    unittest.main()

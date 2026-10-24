"""Session 2524: the Kosovo Agency of Statistics' ASKdata table tab01 (Kosovo's electricity a month, from 2022).

Energy Research Warehouse (ERW). Tests warehouse/connectors/ask_kosovo_electricity.py on a JSON-stat 2.0 answer built
here (made up for the test, not ASK's): the items mapped to entity and variable, thousands of MWh times 1,000, both month
forms (2026M07 and 202308), a cell without a number with no row; an item not in the map, a bad month, the wrong
dimensions and a value array of the wrong size stopping the run; the sector rule and the holds. No network.

    python -m unittest tests.test_session2524 -v
"""

import os
import sys
import unittest

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
sys.path.insert(0, os.path.join(ROOT, "warehouse", "connectors"))
sys.path.insert(0, os.path.join(ROOT, "warehouse", "metadata"))
sys.path.insert(0, os.path.join(ROOT, "warehouse", "redivis"))
import ask_kosovo_electricity as S  # noqa: E402
import build_coverage as B  # noqa: E402
import release_v1 as R  # noqa: E402

BASE = {"source": "s", "source_url": "u", "retrieved_at": "r", "vintage": ""}


def answer(items=("Gross Production from Power Plants", "Import", "Households"), periods=("2026M07", "202308"), values=None,
           dims=("MWH", "Viti/muaji")):
    d = {"MWH": {"label": "MWH", "category": {"index": {str(i): i for i in range(len(items))}, "label": {str(i): x for i, x in enumerate(items)}}},
         "Viti/muaji": {"label": "Year/month", "category": {"index": {p: i for i, p in enumerate(periods)}, "label": {p: p for p in periods}}}}
    n = len(items) * len(periods)
    return {"id": list(dims), "size": [len(items), len(periods)], "dimension": d,
            "value": values if values is not None else [100.5 + i for i in range(n)]}


class Parse(unittest.TestCase):
    def test_rows(self):
        t = S.parse(answer(values=[386.257, 371.835, 300.0, None, 260.5, 250.25]), BASE)
        r = {(e, v, ts[:7]): x for e, v, ts, x in zip(t.entity, t.variable, t.ts_utc, t.value)}
        self.assertEqual(r[("ask:xk:thermal", "gross_production", "2026-07")], 386257.0)
        self.assertEqual(r[("ask:xk:thermal", "gross_production", "2023-08")], 371835.0)
        self.assertEqual(r[("ask:xk:total", "imports", "2026-07")], 300000.0)
        self.assertNotIn(("ask:xk:total", "imports", "2023-08"), r)
        self.assertEqual(r[("ask:xk:households", "consumption", "2023-08")], 250250.0)
        self.assertEqual(set(t.unit), {"MWh"})
        self.assertEqual(set(t.freq), {"P1M"})

    def test_stops(self):
        for js in (answer(items=("Nuclear",), values=[1.0, 2.0]), answer(periods=("2026M13",), values=[1.0, 2.0, 3.0]),
                   answer(dims=("Viti/muaji", "MWH")), answer(values=[1.0])):
            with self.assertRaises(RuntimeError):
                S.parse(js, BASE)


class Registered(unittest.TestCase):
    def test_sector_and_holds(self):
        self.assertEqual(B.sector_of(S.NAME), "power")
        self.assertIn(S.NAME, R.STORAGE_HELD)
        with open(os.path.join(ROOT, "warehouse", "supabase", "live_set.yaml"), encoding="utf-8") as f:
            self.assertIn(f"  - {S.NAME}\n", f.read().replace("\r\n", "\n"))


if __name__ == "__main__":
    unittest.main()

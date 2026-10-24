"""Session 2474: Eurostat's monthly gas oil and diesel imports by partner (nrg_ti_oilm, gas/diesel oil).

Energy Research Warehouse (ERW). Tests warehouse/connectors/eurostat_diesel_imports.py on a JSON-stat answer built here in
Eurostat's form (figures made up for the test, not Eurostat's): the sparse values placed on their dimensions, tonnes,
Namibia's code NA kept as text, the United Kingdom left out, the EU's blank geo, a flag carried; a product or unit not
expected and a value not a number stopping the run; the sector rule and the holds. No network.

    python -m unittest tests.test_session2474 -v
"""

import os
import sys
import unittest

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
sys.path.insert(0, os.path.join(ROOT, "warehouse", "connectors"))
sys.path.insert(0, os.path.join(ROOT, "warehouse", "metadata"))
import eurostat_diesel_imports as E  # noqa: E402
import build_coverage as B  # noqa: E402


def answer(values, status=None, siec="O4671XR5220B", unit="THS_T"):
    def cat(codes, labels=None):
        c = {"index": {k: i for i, k in enumerate(codes)}}
        if labels:
            c["label"] = labels
        return {"category": c}
    return {"version": "2.0", "id": ["freq", "siec", "partner", "unit", "geo", "time"], "size": [1, 1, 3, 1, 3, 2],
            "dimension": {"freq": cat(["M"]), "siec": cat([siec]), "partner": cat(["TOTAL", "US", "NA"], {"TOTAL": "Total", "US": "United States", "NA": "Namibia"}),
                          "unit": cat([unit]), "geo": cat(["EU27_2020", "DE", "UK"]), "time": cat(["2024-01", "2024-02"])},
            "value": values, "status": status or {}}


class Build(unittest.TestCase):
    def test_rows(self):
        # index = ((partner * 3) + geo) * 2 + time
        t, left = E.build(answer({"0": 40000.5, "8": 1500.25, "13": 0.0, "4": 9.0}, {"8": "p"}), "2026-10-24T09:40:02Z")
        got = {(r.entity, r.ts_utc): r for r in t.itertuples()}
        r = got[("eurostat_diesel_imp:DE:US", "2024-01-01T00:00:00Z")]
        self.assertEqual((r.value, r.unit, r.freq, r.geo, r.node, r.x_flag), (1500250.0, "t", "P1M", "DE", "Gas oil and diesel imports from United States", "p"))
        self.assertEqual(got[("eurostat_diesel_imp:EU27_2020:TOTAL", "2024-01-01T00:00:00Z")].geo, "")
        self.assertEqual(got[("eurostat_diesel_imp:EU27_2020:NA", "2024-02-01T00:00:00Z")].x_partner, "NA")
        self.assertNotIn("eurostat_diesel_imp:UK:TOTAL", {k[0] for k in got})
        self.assertEqual((len(t), left), (3, ["UK"]))

    def test_stops(self):
        for kw in ({"siec": "O4600"}, {"unit": "TJ_GCV"}):
            with self.assertRaises(RuntimeError):
                E.build(answer({"0": 1.0}, **kw), "")
        with self.assertRaises(RuntimeError):
            E.build(answer({"0": "x"}), "")


class Registered(unittest.TestCase):
    def test_sector_and_holds(self):
        self.assertEqual(B.sector_of(E.NAME), "oil")
        with open(os.path.join(ROOT, "warehouse", "supabase", "live_set.yaml"), encoding="utf-8") as f:
            self.assertIn(f"  - {E.NAME}\n", f.read().replace("\r\n", "\n"))
        with open(os.path.join(ROOT, "warehouse", "redivis", "release_v1.py"), encoding="utf-8") as f:
            self.assertIn(f'"{E.NAME}",', f.read())


if __name__ == "__main__":
    unittest.main()

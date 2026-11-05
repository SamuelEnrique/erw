"""Session 2426: Eurostat's annual hard coal imports by partner (nrg_ti_sff, hard coal).

Energy Research Warehouse (ERW). Tests warehouse/connectors/eurostat_coal_imports.py on a JSON-stat answer built here in
Eurostat's form (figures made up for the test, not Eurostat's): the sparse values placed on their dimensions, tonnes,
the year's 1 January, Namibia's code NA kept as text, the United Kingdom left out, the EU's blank geo, a flag carried; a
product, unit or frequency not expected and a value not a number stopping the run; the sector rule and the holds. No
network.

    python -m unittest tests.test_session2426 -v
"""

import os
import sys
import unittest

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
sys.path.insert(0, os.path.join(ROOT, "warehouse", "connectors"))
sys.path.insert(0, os.path.join(ROOT, "warehouse", "metadata"))
import eurostat_coal_imports as E  # noqa: E402
import build_coverage as B  # noqa: E402


def answer(values, status=None, siec="C0100", unit="THS_T", freq="A"):
    def cat(codes, labels=None):
        c = {"index": {k: i for i, k in enumerate(codes)}}
        if labels:
            c["label"] = labels
        return {"category": c}
    return {"version": "2.0", "id": ["freq", "siec", "partner", "unit", "geo", "time"], "size": [1, 1, 3, 1, 3, 2],
            "dimension": {"freq": cat([freq]), "siec": cat([siec]), "partner": cat(["TOTAL", "US", "NA"], {"TOTAL": "Total", "US": "United States", "NA": "Namibia"}),
                          "unit": cat([unit]), "geo": cat(["EU27_2020", "PL", "UK"]), "time": cat(["2023", "2024"])},
            "value": values, "status": status or {}}


class Build(unittest.TestCase):
    def test_rows(self):
        # index = ((partner * 3) + geo) * 2 + time
        t, left = E.build(answer({"0": 92400.5, "8": 3500.25, "13": 0.0, "4": 9.0}, {"8": "p"}), "2026-10-24T11:22:52Z")
        got = {(r.entity, r.ts_utc): r for r in t.itertuples()}
        r = got[("eurostat_coal_imp:PL:US", "2023-01-01T00:00:00Z")]
        self.assertEqual((r.value, r.unit, r.freq, r.geo, r.node, r.x_flag), (3500250.0, "t", "P1Y", "PL", "Hard coal imports from United States", "p"))
        self.assertEqual(got[("eurostat_coal_imp:EU27_2020:TOTAL", "2023-01-01T00:00:00Z")].geo, "")
        self.assertEqual(got[("eurostat_coal_imp:EU27_2020:NA", "2024-01-01T00:00:00Z")].x_partner, "NA")
        self.assertNotIn("eurostat_coal_imp:UK:TOTAL", {k[0] for k in got})
        self.assertEqual((len(t), left), (3, ["UK"]))

    def test_stops(self):
        for kw in ({"siec": "C0200"}, {"unit": "TJ_GCV"}, {"freq": "M"}):
            with self.assertRaises(RuntimeError):
                E.build(answer({"0": 1.0}, **kw), "")
        with self.assertRaises(RuntimeError):
            E.build(answer({"0": "x"}), "")


class Registered(unittest.TestCase):
    def test_sector_and_holds(self):
        self.assertEqual(B.sector_of(E.NAME), "coal")
        with open(os.path.join(ROOT, "warehouse", "supabase", "live_set.yaml"), encoding="utf-8") as f:
            self.assertIn(f"  - {E.NAME}\n", f.read().replace("\r\n", "\n"))
        with open(os.path.join(ROOT, "warehouse", "redivis", "release_v1.py"), encoding="utf-8") as f:
            self.assertIn(f'"{E.NAME}",', f.read())


if __name__ == "__main__":
    unittest.main()

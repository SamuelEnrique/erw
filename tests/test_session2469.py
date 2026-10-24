"""Session 2469: Eurostat's monthly natural gas and LNG exports by partner (nrg_te_gasm).

Energy Research Warehouse (ERW). Tests warehouse/connectors/eurostat_gas_exports.py on a JSON-stat answer built here in
Eurostat's form (figures made up for the test, not Eurostat's): the sparse values placed on their dimensions, terajoules
written as MWh, the product in the entity, Namibia's code NA kept as text, the United Kingdom left out, the EU's blank geo,
a flag carried; a product, unit or frequency not expected and a value not a number stopping the run; the sector rule and
the holds. No network.

    python -m unittest tests.test_session2469 -v
"""

import os
import sys
import unittest

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
sys.path.insert(0, os.path.join(ROOT, "warehouse", "connectors"))
sys.path.insert(0, os.path.join(ROOT, "warehouse", "metadata"))
import eurostat_gas_exports as E  # noqa: E402
import build_coverage as B  # noqa: E402


def answer(values, status=None, siec=("G3000", "G3200"), unit="TJ_GCV", freq="M"):
    def cat(codes, labels=None):
        c = {"index": {k: i for i, k in enumerate(codes)}}
        if labels:
            c["label"] = labels
        return {"category": c}
    return {"version": "2.0", "id": ["freq", "siec", "partner", "unit", "geo", "time"], "size": [1, len(siec), 3, 1, 3, 2],
            "dimension": {"freq": cat([freq]), "siec": cat(list(siec)), "partner": cat(["TOTAL", "DE", "NA"], {"TOTAL": "Total", "DE": "Germany", "NA": "Namibia"}),
                          "unit": cat([unit]), "geo": cat(["EU27_2020", "NO", "UK"]), "time": cat(["2024-01", "2024-02"])},
            "value": values, "status": status or {}}


def at(siec, partner, geo, time):
    # index = ((siec * 3 + partner) * 3 + geo) * 2 + time
    return str(((siec * 3 + partner) * 3 + geo) * 2 + time)


class Build(unittest.TestCase):
    def test_rows(self):
        t, left = E.build(answer({at(0, 1, 1, 0): 3600.0, at(1, 1, 1, 0): 36.0, at(0, 0, 0, 1): 0.0, at(0, 2, 0, 0): 7.2,
                                  at(0, 0, 2, 0): 5.0}, {at(0, 1, 1, 0): "p"}), "2026-10-24T13:32:42Z")
        got = {(r.entity, r.ts_utc): r for r in t.itertuples()}
        r = got[("eurostat_gas_exports:NO:G3000:DE", "2024-01-01T00:00:00Z")]
        self.assertEqual((round(r.value, 3), r.unit, r.geo, r.node, r.x_flag), (1000000.0, "MWh", "NO", "Natural gas exports to Germany", "p"))
        self.assertEqual(got[("eurostat_gas_exports:NO:G3200:DE", "2024-01-01T00:00:00Z")].node, "LNG exports to Germany")
        self.assertEqual(got[("eurostat_gas_exports:EU27_2020:G3000:TOTAL", "2024-02-01T00:00:00Z")].geo, "")
        self.assertEqual(got[("eurostat_gas_exports:EU27_2020:G3000:NA", "2024-01-01T00:00:00Z")].x_partner, "NA")
        self.assertNotIn("eurostat_gas_exports:UK:G3000:TOTAL", {k[0] for k in got})
        self.assertEqual((len(t), left), (4, ["UK"]))

    def test_stops(self):
        for kw in ({"siec": ("G3000", "O4100_TOT")}, {"unit": "MIO_M3"}, {"freq": "A"}):
            with self.assertRaises(RuntimeError):
                E.build(answer({"0": 1.0}, **kw), "")
        with self.assertRaises(RuntimeError):
            E.build(answer({"0": "x"}), "")


class Registered(unittest.TestCase):
    def test_sector_and_holds(self):
        self.assertEqual(B.sector_of(E.NAME), "gas;lng")
        with open(os.path.join(ROOT, "warehouse", "supabase", "live_set.yaml"), encoding="utf-8") as f:
            self.assertIn(f"  - {E.NAME}\n", f.read().replace("\r\n", "\n"))
        with open(os.path.join(ROOT, "warehouse", "redivis", "release_v1.py"), encoding="utf-8") as f:
            self.assertIn(f'"{E.NAME}",', f.read())


if __name__ == "__main__":
    unittest.main()

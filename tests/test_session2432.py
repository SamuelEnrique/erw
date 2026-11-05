"""Session 2432: Eurostat's annual electricity imports and exports by partner (nrg_ti_eh, nrg_te_eh, electricity).

Energy Research Warehouse (ERW). Tests warehouse/connectors/eurostat_electricity_trade.py on JSON-stat answers built here
in Eurostat's form (figures made up for the test, not Eurostat's): the sparse values placed on their dimensions, GWh
written as MWh and the TJ figures passed over, imports and exports joined, Namibia's code NA kept as text, the United
Kingdom left out, the EU's blank geo; a product, unit or frequency not expected and a value not a number stopping the
run; the sector rule and the holds. No network.

    python -m unittest tests.test_session2432 -v
"""

import os
import sys
import unittest

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
sys.path.insert(0, os.path.join(ROOT, "warehouse", "connectors"))
sys.path.insert(0, os.path.join(ROOT, "warehouse", "metadata"))
import eurostat_electricity_trade as E  # noqa: E402
import build_coverage as B  # noqa: E402


def answer(values, siec="E7000", units=("GWH", "TJ"), freq="A"):
    def cat(codes, labels=None):
        c = {"index": {k: i for i, k in enumerate(codes)}}
        if labels:
            c["label"] = labels
        return {"category": c}
    return {"version": "2.0", "id": ["freq", "siec", "partner", "unit", "geo", "time"], "size": [1, 1, 3, len(units), 3, 2],
            "dimension": {"freq": cat([freq]), "siec": cat([siec]), "partner": cat(["TOTAL", "FR", "NA"], {"TOTAL": "Total", "FR": "France", "NA": "Namibia"}),
                          "unit": cat(list(units)), "geo": cat(["EU27_2020", "DE", "UK"]), "time": cat(["2023", "2024"])},
            "value": values, "status": {}}


def at(partner, unit, geo, time):
    # index = ((partner * 2 + unit) * 3 + geo) * 2 + time
    return str(((partner * 2 + unit) * 3 + geo) * 2 + time)


class Build(unittest.TestCase):
    def test_rows(self):
        imp, left = E.build(answer({at(1, 0, 1, 1): 20490.5, at(1, 1, 1, 1): 73765.8, at(0, 0, 0, 0): 406800.0,
                                     at(2, 0, 0, 1): 0.0, at(0, 0, 2, 0): 5.0}), "imports", "u1", "2026-10-24T11:43:38Z")
        exp, _ = E.build(answer({at(1, 0, 1, 1): 15000.0}), "exports", "u2", "2026-10-24T11:43:45Z")
        t = E.finish([imp, exp])
        got = {(r.entity, r.variable, r.ts_utc): r for r in t.itertuples()}
        r = got[("eurostat_elec_trade:DE:FR", "imports", "2024-01-01T00:00:00Z")]
        self.assertEqual((r.value, r.unit, r.freq, r.geo, r.source_url), (20490500.0, "MWh", "P1Y", "DE", "u1"))
        self.assertEqual(got[("eurostat_elec_trade:DE:FR", "exports", "2024-01-01T00:00:00Z")].value, 15000000.0)
        self.assertEqual(got[("eurostat_elec_trade:EU27_2020:TOTAL", "imports", "2023-01-01T00:00:00Z")].geo, "")
        self.assertEqual(got[("eurostat_elec_trade:EU27_2020:NA", "imports", "2024-01-01T00:00:00Z")].value, 0.0)
        self.assertNotIn("eurostat_elec_trade:UK:TOTAL", {k[0] for k in got})
        self.assertEqual((len(t), left), (4, ["UK"]))

    def test_stops(self):
        for kw in ({"siec": "H8000"}, {"units": ("KTOE",)}, {"freq": "M"}):
            with self.assertRaises(RuntimeError):
                E.build(answer({"0": 1.0}, **kw), "imports", "u", "")
        with self.assertRaises(RuntimeError):
            E.build(answer({"0": "x"}), "imports", "u", "")


class Registered(unittest.TestCase):
    def test_sector_and_holds(self):
        self.assertEqual(B.sector_of(E.NAME), "power")
        with open(os.path.join(ROOT, "warehouse", "supabase", "live_set.yaml"), encoding="utf-8") as f:
            self.assertIn(f"  - {E.NAME}\n", f.read().replace("\r\n", "\n"))
        with open(os.path.join(ROOT, "warehouse", "redivis", "release_v1.py"), encoding="utf-8") as f:
            self.assertIn(f'"{E.NAME}",', f.read())


if __name__ == "__main__":
    unittest.main()

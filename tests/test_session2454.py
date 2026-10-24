"""Session 2454: Eurostat's annual supply, transformation and consumption of electricity (nrg_cb_e).

Energy Research Warehouse (ERW). Tests warehouse/connectors/eurostat_electricity_balance.py on a small SDMX-CSV and
codelist built here in Eurostat's form (made up for the test, not its figures): GWh written as MWh, the item's code in
lower case, EL as GR, the EU's blank geo, a country Eurostat's terms leave out, a flag kept; a unit, product or item not
expected stopping the run; net production above gross stopping it; the sector rule and the holds (public). No network.

    python -m unittest tests.test_session2454 -v
"""

import os
import sys
import unittest

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
sys.path.insert(0, os.path.join(ROOT, "warehouse", "connectors"))
sys.path.insert(0, os.path.join(ROOT, "warehouse", "metadata"))
import eurostat_electricity_balance as E  # noqa: E402
import build_coverage as B  # noqa: E402

CODES = "GEP\tGross electricity production\nNEP\tNet electricity production\nFC\tFinal consumption\nEXP\tExports\n".encode()


def csv(lines, unit="GWH", siec="E7000"):
    head = ",".join(E.HEADER)
    out = [head] + [f"ESTAT:NRG_CB_E(1.0),25/09/26 23:00:00,A,{b},{siec},{unit},{g},{y},{v},{f}," for g, b, y, v, f in lines]
    return ("\n".join(out) + "\n").encode()


ROWS = [("EL", "GEP", "2023", "50", ""), ("EL", "NEP", "2023", "48", "p"), ("EL", "EXP", "2023", "3", ""),
        ("EU27_2020", "GEP", "2023", "2700", ""), ("EU27_2020", "NEP", "2023", "2600", ""), ("UK", "GEP", "2023", "300", "")]


class Build(unittest.TestCase):
    def test_build(self):
        t, counts = E.build(csv(ROWS), E.item_names(CODES), "u", "r", "")
        self.assertEqual(len(t), 5)
        self.assertEqual(counts["left_out_geo"], ["UK"])
        gr = t[(t.x_geo_code == "EL") & (t.variable == "nep")].iloc[0]
        self.assertEqual((gr.geo, gr.value, gr.x_flag, gr.unit), ("GR", 48000.0, "p", "MWh"))
        self.assertEqual(t[t.x_geo_code == "EU27_2020"].geo.unique().tolist(), [""])
        self.assertEqual(E.nep_check(t), 2)

    def test_stops(self):
        names = E.item_names(CODES)
        for content in (csv(ROWS[:1], unit="TJ"), csv(ROWS[:1], siec="G3000"), csv([("EL", "XYZ", "2023", "1", "")])):
            with self.assertRaises(RuntimeError):
                E.build(content, names, "u", "r", "")
        t, _ = E.build(csv([("EL", "GEP", "2023", "40", ""), ("EL", "NEP", "2023", "48", "")]), names, "u", "r", "")
        with self.assertRaises(RuntimeError):
            E.nep_check(t)

    def test_inland_demand(self):
        """Session 2457: inland demand is net production plus imports less exports less transformation input."""
        names = E.item_names(CODES + "IMP\tImports\nID\tInland demand\nTI_EHG_EPS_PURE\tPumping\n".encode())
        rows = [("EL", "GEP", "2023", "50", ""), ("EL", "NEP", "2023", "48", ""), ("EL", "IMP", "2023", "5", ""),
                ("EL", "EXP", "2023", "3", ""), ("EL", "TI_EHG_EPS_PURE", "2023", "2", "")]
        t, _ = E.build(csv(rows + [("EL", "ID", "2023", "48", "")]), names, "u", "r", "")
        self.assertEqual(E.nep_check(t), 1)
        t, _ = E.build(csv(rows + [("EL", "ID", "2023", "50", "")]), names, "u", "r", "")
        with self.assertRaises(RuntimeError):
            E.nep_check(t)


class Registered(unittest.TestCase):
    def test_sector_and_holds(self):
        self.assertEqual(B.sector_of(E.NAME), "power")
        with open(os.path.join(ROOT, "warehouse", "supabase", "live_set.yaml"), encoding="utf-8") as f:
            self.assertIn(f"  - {E.NAME}\n", f.read().replace("\r\n", "\n"))
        with open(os.path.join(ROOT, "warehouse", "redivis", "release_v1.py"), encoding="utf-8") as f:
            self.assertIn(f'"{E.NAME}"', f.read())


if __name__ == "__main__":
    unittest.main()

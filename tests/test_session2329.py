"""Session 2329: Eurostat's monthly supply, transformation and consumption of natural gas (nrg_cb_gasm).

Energy Research Warehouse (ERW). Tests warehouse/connectors/eurostat_gas_balance.py on an SDMX-CSV built here in
Eurostat's form (made up for the test, not Eurostat's): the energy rows of the kept areas, TJ written as MWh, a zero
kept and counted, a blank without a row, million cubic metres and an area left out by Eurostat's terms not taken, EL
written GR and an aggregate without a geo; a header not Eurostat's, a balance item not in the map, a value that is not
a number and a key given twice stopping the run; the sector rule and the holds. No network.

    python -m unittest tests.test_session2329 -v
"""

import os
import sys
import unittest

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
sys.path.insert(0, os.path.join(ROOT, "warehouse", "connectors"))
sys.path.insert(0, os.path.join(ROOT, "warehouse", "metadata"))
sys.path.insert(0, os.path.join(ROOT, "warehouse", "redivis"))
import eurostat_gas_balance as E  # noqa: E402
import build_coverage as B  # noqa: E402
import release_v1 as R1  # noqa: E402

HEAD = ",".join(E.HEADER) + "\n"


def line(bal="IMP", unit="TJ_GCV", geo="DE", period="2026-01", value="3600", flag=""):
    return f"ESTAT:NRG_CB_GASM(1.0),23/10/26 23:00:00,M,{bal},G3000,{unit},{geo},{period},{value},{flag},\n"


class Rows(unittest.TestCase):
    def test_rows(self):
        text = HEAD + line() + line(bal="EXP", value="0") + line(bal="IPRD", value="") + line(unit="MIO_M3") + line(geo="UK") \
            + line(geo="EL", value="36") + line(geo="EU27_2020", flag="p")
        t, counts = E.build(text.encode(), "u", "r", "v")
        self.assertEqual((counts["zero"], counts["blank"], counts["left_out_geo"]), (1, 1, ["UK"]))
        self.assertEqual(len(t), 4)
        de = t[(t.x_geo_code == "DE") & (t.variable == "imports")].iloc[0]
        self.assertEqual((de.value, de.unit, de.geo, de.freq, de.entity), (1_000_000.0, "MWh", "DE", "P1M", "eurostat_gas_balance:DE"))
        self.assertEqual(t[t.x_geo_code == "EL"].geo.iloc[0], "GR")
        eu = t[t.x_geo_code == "EU27_2020"].iloc[0]
        self.assertEqual((eu.geo, eu.x_flag), ("", "p"))

    def test_stops(self):
        for text in (HEAD.replace("nrg_bal", "balance") + line(), HEAD + line(bal="XYZ"), HEAD + line(value="lots"), HEAD + line() + line()):
            with self.assertRaises(RuntimeError):
                E.build(text.encode(), "u", "r", "v")


class Registered(unittest.TestCase):
    def test_sector_and_holds(self):
        self.assertEqual(B.sector_of(E.NAME), "gas")
        self.assertIn(E.NAME, R1.STORAGE_HELD)
        with open(os.path.join(ROOT, "warehouse", "supabase", "live_set.yaml"), encoding="utf-8") as f:
            self.assertIn(f"  - {E.NAME}\n", f.read().replace("\r\n", "\n"))


if __name__ == "__main__":
    unittest.main()

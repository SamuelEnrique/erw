"""Session 2030: EPA's Renewable Fuel Standard, RINs generated and renewable fuel produced.

Energy Research Warehouse (ERW). Tests warehouse/connectors/epa_rfs_rins.py on files built here in EPA's form (made up
for the test, not EPA's): the newest file a listing page links, the monthly and yearly rows with the D code's name from
the fuel type file; a D code the fuel type file does not name, a missing column, a quantity not a whole number and a
month given twice stopping the run; the unit gal in the validator and the data standard (Decision 59); the sector rule
and the holds. No network.

    python -m unittest tests.test_session2030 -v
"""

import os
import sys
import unittest

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
sys.path.insert(0, os.path.join(ROOT, "warehouse", "connectors"))
sys.path.insert(0, os.path.join(ROOT, "warehouse", "metadata"))
sys.path.insert(0, os.path.join(ROOT, "warehouse", "redivis"))
sys.path.append(os.path.join(ROOT, "warehouse", "validate"))
import epa_rfs_rins as E  # noqa: E402
import build_coverage as B  # noqa: E402
import release_v1 as R  # noqa: E402
import erw_validate as V  # noqa: E402

BASE = {"source": "s", "source_url": "u", "retrieved_at": "r", "vintage": "v"}
FUEL = (b"RIN Year,Fuel,Fuel Code,Fuel Category,Fuel Category Code,RIN Quantity,Batch Volume\n"
        b'2024,Renewable Fuel,6,Ethanol,1,"1,500",1500\n'
        b"2024,Biomass-Based Diesel,4,Biodiesel (EV 1.5),20,300,200\n")
MONTH = (b"FUEL_CODE,RIN_YEAR,Production Month,RIN_QUANTITY,BATCH_VOLUME\n"
         b"6,2024,1,700,700\n6,2024,2,800,800\n4,2024,1,300,200\n")


class Files(unittest.TestCase):
    def test_newest(self):
        page = ('<a href="https://www.epa.gov/system/files/other-files/2026-09/rindata_aug2026.csv">a</a>'
                '<a href="/system/files/other-files/2026-10/rindata_sep2026.csv">b</a>'
                '<a href="/system/files/other-files/2025-12/rindata_nov2025.csv">c</a>')
        self.assertEqual(E.newest(page, "rindata"), (2026, 9, "https://www.epa.gov/system/files/other-files/2026-10/rindata_sep2026.csv"))
        with self.assertRaises(RuntimeError):
            E.newest(page, "fuelproduction")

    def test_rows(self):
        f, m = E.read(FUEL, "fuel"), E.read(MONTH, "month")
        names = E.d_names(f)
        self.assertEqual(names, {4: "Biomass-Based Diesel", 6: "Renewable Fuel"})
        sm = E.monthly(m, names, BASE).set_index(["entity", "variable", "ts_utc"])
        self.assertEqual(sm.loc[("epa_rfs:d6", "rins_generated", "2024-02-01T00:00:00Z")].value, 800)
        self.assertEqual(sm.loc[("epa_rfs:d4", "batch_volume", "2024-01-01T00:00:00Z")].unit, "gal")
        self.assertEqual(sm.loc[("epa_rfs:d4", "batch_volume", "2024-01-01T00:00:00Z")].node, "Biomass-Based Diesel")
        sa = E.annual(f, names, BASE).set_index(["entity", "variable", "ts_utc"])
        a = sa.loc[("epa_rfs:d6:1", "rins_generated", "2024-01-01T00:00:00Z")]
        self.assertEqual((a.value, a.freq, a.x_fuel_category, a.x_d_code_name), (1500, "P1Y", "Ethanol", "Renewable Fuel"))

    def test_stops(self):
        f = E.read(FUEL, "fuel")
        with self.assertRaises(RuntimeError):
            E.monthly(E.read(MONTH + b"3,2024,1,5,5\n", "month"), E.d_names(f), BASE)
        with self.assertRaises(RuntimeError):
            E.read(b"FUEL_CODE,RIN_YEAR,RIN_QUANTITY,BATCH_VOLUME\n6,2024,1,1\n", "month")
        with self.assertRaises(RuntimeError):
            E.read(MONTH + b"6,2024,3,many,1\n", "month")
        with self.assertRaises(RuntimeError):
            E.once(E.monthly(E.read(MONTH + b"6,2024,1,9,9\n", "month"), E.d_names(f), BASE), "t")


class Registered(unittest.TestCase):
    def test_unit_sector_and_holds(self):
        self.assertIn("gal", V.UNITS)
        with open(os.path.join(ROOT, "docs", "datastandard.md"), encoding="utf-8") as f:
            self.assertIn("59. **Session 2030: gal.**", f.read())
        for t in (E.MONTHLY, E.ANNUAL):
            self.assertEqual(B.sector_of(t), "products;carbon")
            self.assertIn(t, R.STORAGE_HELD)
            with open(os.path.join(ROOT, "warehouse", "supabase", "live_set.yaml"), encoding="utf-8") as f:
                self.assertIn(f"  - {t}\n", f.read().replace("\r\n", "\n"))


if __name__ == "__main__":
    unittest.main()

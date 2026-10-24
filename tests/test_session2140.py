"""Session 2140: DOE's LEAD Tool, the households' energy burden.

Energy Research Warehouse (ERW). Tests warehouse/connectors/doe_lead.py on a zip built here in LEAD's form (made up for
the test, not DOE's): the AMI Counties cells summed to the county and bracket, and to the state; each average a sum of
value-times-units over its own units; the burden the cost averages over the income average; a zip without its AMI
Counties file, a row of another state and a bracket not one of the six stopping the write; the sector rule and the
holds. No network.

    python -m unittest tests.test_session2140 -v
"""

import io
import os
import sys
import tempfile
import unittest
import zipfile

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
sys.path.insert(0, os.path.join(ROOT, "warehouse", "connectors"))
sys.path.insert(0, os.path.join(ROOT, "warehouse", "metadata"))
sys.path.insert(0, os.path.join(ROOT, "warehouse", "redivis"))
import doe_lead as D  # noqa: E402
import build_coverage as B  # noqa: E402
import release_v1 as R  # noqa: E402

HEAD = "ABV,STATE,FIP,NAME,AMI150,TEN,UNITS,HINCP*UNITS,ELEP*UNITS,GASP*UNITS,FULP*UNITS,HINCP UNITS,ELEP UNITS,GASP UNITS,FULP UNITS\n"
# two cells of one county and bracket (owner and renter), one of another bracket
ROWS = ("VT,50,50001,Addison County,0-30%,OWN,2,20000,2000,400,600,2,2,2,2\n"
        "VT,50,50001,Addison County,0-30%,REN,3,30000,3000,0,0,3,3,3,3\n"
        "VT,50,50001,Addison County,150%+,OWN,5,1000000,10000,5000,0,5,5,5,5\n")


def zipped(body, name="VT AMI Counties 2022.csv"):
    d = tempfile.mkdtemp()
    p = os.path.join(d, "VT-2022-LEAD-data.zip")
    with zipfile.ZipFile(p, "w") as z:
        z.writestr(name, HEAD + body)
        z.writestr("VT FPL Counties 2022.csv", HEAD)
    return p


class Cells(unittest.TestCase):
    def test_sums_and_measures(self):
        g, year, inner, fips = D.county_cells(zipped(ROWS), "VT")
        self.assertEqual((year, inner, fips), (2022, "VT AMI Counties 2022.csv", "50"))
        g = g.set_index("AMI150")
        self.assertEqual(g.at["0-30%", "UNITS"], 5)
        m = D.measures(g)
        self.assertAlmostEqual(m.at["0-30%", "income_avg"], 10000)
        self.assertAlmostEqual(m.at["0-30%", "electricity_cost_avg"], 1000)
        self.assertAlmostEqual(m.at["0-30%", "gas_cost_avg"], 80)
        self.assertAlmostEqual(m.at["0-30%", "other_fuel_cost_avg"], 120)
        self.assertAlmostEqual(m.at["0-30%", "energy_cost_avg"], 1200)
        self.assertAlmostEqual(m.at["0-30%", "energy_burden"], 12.0)
        self.assertAlmostEqual(m.at["150%+", "energy_burden"], 1.5)

    def test_stops(self):
        for p in (zipped(ROWS, name="VT AMI Tracts 2022.csv"), zipped(ROWS.replace("VT,50,50001,Addison County,150%+", "NH,33,33001,Belknap County,150%+")),
                  zipped(ROWS.replace("150%+", "200%+"))):
            with self.assertRaises(RuntimeError):
                D.county_cells(p, "VT")


class Registered(unittest.TestCase):
    def test_sector_and_holds(self):
        self.assertEqual(B.sector_of(D.TABLE), "power;gas")
        self.assertIn(D.TABLE, R.STORAGE_HELD)
        with open(os.path.join(ROOT, "warehouse", "supabase", "live_set.yaml"), encoding="utf-8") as f:
            self.assertIn(f"  - {D.TABLE}\n", f.read().replace("\r\n", "\n"))


if __name__ == "__main__":
    unittest.main()

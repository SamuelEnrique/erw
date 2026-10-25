"""Session 2136: EPA's Inventory of U.S. Greenhouse Gas Emissions and Sinks.

Energy Research Warehouse (ERW). Tests warehouse/connectors/epa_ghg_inventory.py on a zip built here in the form of the
Inventory's Chapter 2 tables (made up for the test, not EPA's): Table 2-10's sectors and sources, Table 2-11's gases and
fuels, Table 2-12's sectors by basis and gas; MMT CO2 Eq. times 1,000,000 in tCO2e; the footnote letters dropped; a value
printed as + counted, not written; Table 2-11's Total and Table 2-12's repeated lines checked against Table 2-10's (1965.0
alike with 1965); a line under no sector, years out of order and a repeated line that differs stopping the run; the
sector rule and the holds. No network.

    python -m unittest tests.test_session2136 -v
"""

import io
import os
import sys
import unittest
import zipfile

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
sys.path.insert(0, os.path.join(ROOT, "warehouse", "connectors"))
sys.path.insert(0, os.path.join(ROOT, "warehouse", "metadata"))
sys.path.insert(0, os.path.join(ROOT, "warehouse", "redivis"))
import epa_ghg_inventory as G  # noqa: E402
import build_coverage as B  # noqa: E402
import release_v1 as R  # noqa: E402

BASE = {"source": "s", "source_url": "u", "retrieved_at": "r", "vintage": "v"}
SECTOR_LINES = "".join(f"{s},10.0,11.0,\nCO2 from Fossil Fuel Combustion,9,10,\n" for s in G.SECTORS if s != "Electric Power Industry")
T210 = ("Table 2-10:  Emissions Allocated to Economic Sectors,,,\nSector/Source,1990,1991,Percent of Total Emissionsa\n"
        "Electric Power Industry,1965.0,2.5,30%\nStationary Combustionb,1,+,1%\n" + SECTOR_LINES +
        "Total Gross Emissions (Sources),100,101,\nLULUCF Sector Net Totalc,-5,-6,\nNet Emissions (Sources and Sinks),95,95,\n"
        "+ Does not exceed 0.05 MMT CO2 Eq.,,,\n")
T211 = ("Table 2-11:  Electric Power-Related Emissions,,\nGas/Fuel Type or Source,1990,1991\nCO2,1960,2.4\nCoal,1500,2\n"
        "SF6,5,0.1\nElectrical Equipment,5,0.1\nTotal,1965,2.5\n")
T212 = ("Table 2-12:  by Economic Sector and Gas,,,\nEmissions by Gas,1990,1991,Percenta\nIndustry,20,21,1%\nDirect Emissions,10,11,1%\n"
        "CO2,9,10,1%\nElectricity-Related,10,10,1%\nSF6,1,+,+%\nU.S. Territories,10.0,11.0,\nTotal Gross Emissions (Sources),100,101,\n"
        "LULUCF Sector Net Totalc,-5,-6,\nNet Emissions (Sources and Sinks),95,95,\n")


def zipped(t210=T210, t211=T211, t212=T212):
    b = io.BytesIO()
    with zipfile.ZipFile(b, "w") as z:
        z.writestr("Table 2-10.csv", t210)
        z.writestr("Table 2-11.csv", t211)
        z.writestr("Table 2-12.csv", t212)
    return b.getvalue()


class Parse(unittest.TestCase):
    def test_rows(self):
        s, plus = G.parse(zipped(), BASE)
        self.assertEqual(plus, 2)
        s = s.set_index(["entity", "variable", "ts_utc"])
        self.assertEqual(s.loc[("epa_ghgi:electric_power_industry", "direct:total", "1990-01-01T00:00:00Z")].value, 1_965_000_000)
        self.assertEqual(s.loc[("epa_ghgi:electric_power_industry", "direct:stationary_combustion", "1990-01-01T00:00:00Z")].x_line,
                         "Stationary Combustion")
        self.assertNotIn(("epa_ghgi:electric_power_industry", "direct:stationary_combustion", "1991-01-01T00:00:00Z"), s.index)
        self.assertEqual(s.loc[("epa_ghgi:us", "lulucf_sector_net_total", "1991-01-01T00:00:00Z")].value, -6_000_000)
        self.assertEqual(s.loc[("epa_ghgi:electric_power_industry", "power:co2:coal", "1991-01-01T00:00:00Z")].value, 2_000_000)
        self.assertEqual(s.loc[("epa_ghgi:electric_power_industry", "power:total", "1991-01-01T00:00:00Z")].value, 2_500_000)
        self.assertEqual(s.loc[("epa_ghgi:industry", "distributed:electricity_related:sf6", "1990-01-01T00:00:00Z")].x_group,
                         "Electricity-Related")
        self.assertEqual(s.loc[("epa_ghgi:industry", "distributed:total", "1990-01-01T00:00:00Z")].unit, "tCO2e")
        self.assertFalse(any(v.startswith("distributed") for e, v, t in s.index if e == "epa_ghgi:us"))

    def test_stops(self):
        for z in (zipped(t210=T210.replace("Electric Power Industry,", "Electric Power,")),
                  zipped(t211=T211.replace("Total,1965,2.5", "Total,1966,2.5")),
                  zipped(t212=T212.replace("U.S. Territories,10.0,", "U.S. Territories,10.1,")),
                  zipped(t211=T211.replace("Gas/Fuel Type or Source,1990,1991", "Gas/Fuel Type or Source,1991,1990")),
                  zipped(t212=T212.replace("Industry,20,21,1%\n", "")),
                  zipped(t211=T211.replace("Coal,1500,2", "Coal,n/a,2"))):
            with self.assertRaises(RuntimeError):
                G.parse(z, BASE)


class Registered(unittest.TestCase):
    def test_sector_and_holds(self):
        self.assertEqual(B.sector_of(G.TABLE), "carbon;power;oil;gas")
        self.assertIn(G.TABLE, R.STORAGE_HELD)
        with open(os.path.join(ROOT, "warehouse", "supabase", "live_set.yaml"), encoding="utf-8") as f:
            self.assertIn(f"  - {G.TABLE}\n", f.read().replace("\r\n", "\n"))


if __name__ == "__main__":
    unittest.main()

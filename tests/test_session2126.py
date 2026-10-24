"""Session 2126: Our World in Data's energy dataset, Ember's columns.

Energy Research Warehouse (ERW). Tests warehouse/connectors/owid_energy.py on a codebook and a data file built here in Our
World in Data's form (made up for the test, not its): the two Ember-only columns taken, TWh and million tonnes written as
MWh and tCO2e, a country by its ISO code and a region by its name, blanks left out, the other columns not taken; a
codebook whose sources for a taken column are no longer Ember's alone, or whose unit changed, stopping the run, as do a
missing column, a year that is not a year, a value that is not a number and a key given twice; the sector rule, the
verdict and the holds. No network.

    python -m unittest tests.test_session2126 -v
"""

import csv
import io
import os
import sys
import unittest

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
sys.path.insert(0, os.path.join(ROOT, "warehouse", "connectors"))
sys.path.insert(0, os.path.join(ROOT, "warehouse", "metadata"))
sys.path.insert(0, os.path.join(ROOT, "warehouse", "redivis"))
import owid_energy as O  # noqa: E402
import build_coverage as B  # noqa: E402
import release_v1 as R  # noqa: E402

DASH = "\N{EN DASH}"
EMBER = f"Ember {DASH} Yearly Electricity Data Europe (2026); Ember {DASH} Yearly Electricity Data (2026)"


def codebook(demand_source=EMBER, demand_unit="terawatt-hours (TWh)"):
    out = io.StringIO()
    w = csv.writer(out)
    w.writerow(["column", "title", "description", "unit", "date_range", "source"])
    w.writerow(["electricity_demand_twh", "", "", demand_unit, "", demand_source])
    w.writerow(["electricity_emissions_mtco2eq", "", "", "million tonnes CO2 equivalents (Mt)", "", EMBER])
    w.writerow(["coal_energy_twh", "", "", "terawatt-hours (TWh)", "", f"Energy Institute {DASH} Statistical Review of World Energy (2026)"])
    return out.getvalue()


HEAD = "country,year,iso_code,coal_energy_twh,electricity_demand_twh,electricity_emissions_mtco2eq\n"


class Build(unittest.TestCase):
    def test_codebook(self):
        O.check_codebook(codebook())
        for bad in (codebook(demand_source=EMBER + f"; Energy Institute {DASH} Statistical Review of World Energy (2026)"),
                    codebook(demand_unit="gigawatt-hours (GWh)"), codebook().replace("electricity_demand_twh", "demand")):
            with self.assertRaises(RuntimeError):
                O.check_codebook(bad)

    def test_rows(self):
        t = O.build(HEAD + "United States,2024,USA,9000,4404.83,1685.2\nEurope (Ember),2024,,1,3500.5,\n"
                    "Chad,1990,TCD,,,\n", "u", "r", "")
        us = t[t.entity == "owid_energy:USA"].set_index("variable")
        self.assertEqual((us.loc["electricity_demand", "value"], us.loc["electricity_demand", "unit"]), (4404830000.0, "MWh"))
        self.assertEqual((us.loc["electricity_emissions", "value"], us.loc["electricity_emissions", "unit"]), (1685200000.0, "tCO2e"))
        self.assertEqual(us.loc["electricity_demand", "node"], "United States")
        eu = t[t.entity == "owid_energy:europe_ember"]
        self.assertEqual(list(eu.variable), ["electricity_demand"])
        self.assertEqual(eu.iloc[0].geo, "")
        self.assertEqual(len(t), 3)
        self.assertNotIn("coal_energy_twh", set(t.x_owid_column))

    def test_stops(self):
        for bad in (HEAD.replace(",electricity_emissions_mtco2eq", "") + "X,2024,XXX,1,2\n",
                    HEAD + "United States,24,USA,1,2,3\n", HEAD + "United States,2024,USA,1,lots,3\n",
                    HEAD + "United States,2024,USA,1,2,3\nUnited States,2024,USA,1,2,3\n"):
            with self.assertRaises(RuntimeError):
                O.build(bad, "u", "r", "")


class Registered(unittest.TestCase):
    def test_verdicts_sector_and_holds(self):
        with open(os.path.join(ROOT, "warehouse", "metadata", "license_verdicts.csv"), encoding="utf-8", newline="") as f:
            v = {r["key"]: r for r in csv.DictReader(f)}
        self.assertEqual(v["Our World in Data"]["verdict"], "may be public")
        self.assertEqual(v["Ember"]["verdict"], "may be public")
        self.assertEqual(B.sector_of(O.NAME), "power;carbon")
        self.assertIn(O.NAME, R.STORAGE_HELD)
        with open(os.path.join(ROOT, "warehouse", "supabase", "live_set.yaml"), encoding="utf-8") as f:
            self.assertIn(f"  - {O.NAME}\n", f.read().replace("\r\n", "\n"))


if __name__ == "__main__":
    unittest.main()

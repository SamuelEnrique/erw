"""Session 2563: ABS's Milieustatistieken / Environment Statistics 2024, tables 7.1, 7.4, 7.8 and 7.9 (Suriname's EBS demand,
generation and capacity, Staatsolie's generation).

Energy Research Warehouse (ERW). Tests warehouse/connectors/abs_suriname_electricity.py on page lines built here (made up for
the test, not ABS's): each table found by its title line (a contents page's run-together title passed over) and read to
its source line, kWh, billion kWh with a comma or a point, GWh and MWh to MWh, revised years marked "#"; a title found
twice, categories that miss their total, a billion out of its range, consumption above generation, a plant's line
missing, available above installed capacity and a year's figure missing stopping the run; the sector rule and the
registration. No network.

    python -m unittest tests.test_session2563 -v
"""

import os
import sys
import unittest

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
sys.path.insert(0, os.path.join(ROOT, "warehouse", "connectors"))
sys.path.insert(0, os.path.join(ROOT, "warehouse", "metadata"))
sys.path.insert(0, os.path.join(ROOT, "warehouse", "redivis"))
import abs_suriname_electricity as A  # noqa: E402
import build_coverage as B  # noqa: E402
import release_v1 as R  # noqa: E402

BASE = {"source": "s", "source_url": "u", "retrieved_at": "r", "vintage": "v"}
I_ = chr(0xEF)
CONTENTS = ["Tabel 7.4: Elektriciteitsvraag (kWh), 2022-2023 Table 7.4: Electricity Demand (kWh), 2022-2023 155"]
P71 = ["Tabel 7.1: Beschikbaar en ge" + I_ + "nstalleerd vermogen (MW), 2020-2021", "Table 7.1: Electricity Production and Installed Capacity (MW), 2020-2021",
       "Jaar/Year Installed Capacity Available Capacity", "MW", "2020 200.0 150.5", "2021# 210.0 160.0", "Bron: N.V. EnergieBedrijven Suriname"]
P74 = ["Tabel 7.4: Elektriciteitsvraag (kWh), 2022-2023", "Table 7.4: Electricity Demand (kWh), 2022-2023", "Categorie/ Category 2022 2023",
       "Huishoudens/Residential 600,000,000 700,000,500", "Bedrijven/Commercial 200,000,000 200,000,000", "Industrieel/Industrial 400,000,000 450,000,000",
       "Anders/Other 20,000,000 25,000,000", "Totaal/Total 1,220,000,000 1,375,000,500", "Bron: N.V. EnergieBedrijven Suriname"]
P78 = ["Tabel 7.8: Geselecteerde energiedata van EnergieBedrijven Suriname (EBS), 2022-2023", "Geselecteerde energie data/ Eenheid/", "2022 2023",
       "Selected Energy Data Unit", "Totaal Elektriciteit Net Generatie/", "Billion 1,300 1.400", "Total Electricity Net Generation", "Kilowatthours",
       "Net Consumptie/ Net Consumption 1,200 1.350", "Ge" + I_ + "nstalleerde capaciteit/ Installed Capacity GWe Gigawatts 0.210 .", "Bron/Source: N.V. EnergieBedrijven Suriname"]
P79 = ["Tabel 7.9: Elektriciteitsopwekking door Staatsolie Maatschappij Suriname, 2022-2023", "Elektriciteitsopwekking/ Eenheid/", "2022# 2023#",
       "Electricity Generation Unit", "Energie productie/ Energy production", "MWh 200 150", "(back-up production in Saramacca)",
       "Tout Lui Faut Thermal Power Plant t.b.v. EBS/", "GWh 300 250", "for the purpose of EBS", "Afobaka Hydro Operations t.b.v. EPAR (EBS)/",
       "GWh 900 950", "for the purpose of EPAR (EBS)", "Bron/Source: Staatsolie Power Company Suriname (SPCS)"]


def pages(p71=P71, p74=P74, p78=P78, p79=P79):
    return [CONTENTS, ["prose"] + p71, p74 + ["Tabel 7.5: Elektriciteitsverkopen per district (kWh), 2022-2023", "EPAR 1 2"], p78, p79]


class Parse(unittest.TestCase):
    def test_rows(self):
        t = A.parse_texts(pages(), BASE)
        r = {(e, v, ts[:4]): x for e, v, ts, x in zip(t.entity, t.variable, t.ts_utc, t.value)}
        self.assertEqual(r[("abs_sr:ebs", "installed_capacity", "2021")], 210.0)
        self.assertEqual(r[("abs_sr:ebs", "available_capacity", "2020")], 150.5)
        self.assertEqual(r[("abs_sr:ebs:residential", "demand", "2023")], 700000.5)
        self.assertEqual(r[("abs_sr:ebs:total", "demand", "2022")], 1220000.0)
        self.assertEqual(r[("abs_sr:ebs", "net_generation", "2022")], 1300000.0)
        self.assertEqual(r[("abs_sr:ebs", "net_consumption", "2023")], 1350000.0)
        self.assertEqual(r[("abs_sr:staatsolie:afobaka_hydro", "generation", "2023")], 950000.0)
        self.assertEqual(r[("abs_sr:staatsolie:saramacca_backup", "generation", "2022")], 200.0)
        self.assertEqual(len(t), 4 + 10 + 4 + 6)
        self.assertEqual(set(t.unit), {"MW", "MWh"})

    def test_stops(self):
        bad = [pages() + [[P74[0]]],
               pages(p74=P74[:7] + ["Totaal/Total 1,220,000,000 1,385,000,500"] + P74[8:]),
               pages(p78=P78[:5] + ["Billion 1,300 7.400"] + P78[6:]),
               pages(p78=P78[:8] + ["Net Consumptie/ Net Consumption 1,200 1.450"] + P78[9:]),
               pages(p79=P79[:8] + P79[9:]),
               pages(p71=P71[:4] + ["2020 200.0 250.5"] + P71[5:]),
               pages(p71=P71[:5] + P71[6:])]
        for p in bad:
            with self.assertRaises(RuntimeError):
                A.parse_texts(p, BASE)


class Registered(unittest.TestCase):
    def test_sector_and_registration(self):
        self.assertEqual(B.sector_of(A.NAME), "power")
        self.assertIn(A.NAME, R.STORAGE_HELD)
        with open(os.path.join(ROOT, "warehouse", "supabase", "live_set.yaml"), encoding="utf-8") as f:
            self.assertIn(f"  - {A.NAME}\n", f.read().replace("\r\n", "\n"))


if __name__ == "__main__":
    unittest.main()

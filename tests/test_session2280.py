"""Session 2280: REN's Data Hub, Portugal's electricity balance a year (the monthly balance's December year-to-date).

Energy Research Warehouse (ERW). Tests warehouse/connectors/ren_balance.py on an export built here in REN's form (made
up for the test, not REN's): both years of a December file, GWh written as MWh, the children of biomass, natural gas and
other thermal named after their parent, a blank without a row; a header not REN's, a label not in the map, a value that
is not a number and a year given twice stopping the run; the sector rule and the live-set hold (internal, so not in
the release package). No network.

    python -m unittest tests.test_session2280 -v
"""

import os
import sys
import unittest

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
sys.path.insert(0, os.path.join(ROOT, "warehouse", "connectors"))
sys.path.insert(0, os.path.join(ROOT, "warehouse", "metadata"))
import ren_balance as R  # noqa: E402
import build_coverage as B  # noqa: E402

HEAD = ",Ponta [MW],Dec 25 [GWh],Acumulado [GWh],Dec 24 [GWh],Acumulado [GWh],Mês [Variação %],Acumulado [Variação %]\n"


def line(name, ytd="100", prev="90"):
    return f"{name},1,10,{ytd},9,{prev},1,1\n"


class Rows(unittest.TestCase):
    def test_rows(self):
        text = (HEAD + line("PRODUÇÃO TOTAL", "48872", "45686") + line("Produção Renovável") + line("Biomassa 2")
                + line("Cogeração", "40") + line("Outros", "60") + line("Produção não Renovável") + line("Gás Natural")
                + line("Cogeração", "7", "") + line("CONSUMO", "53036", "51407"))
        t = R.finish(R.file_rows(text, "u", "r", "v"))
        c = t[(t.variable == "consumption") & (t.ts_utc == "2025-01-01T00:00:00Z")].iloc[0]
        self.assertEqual((c.value, c.unit, c.freq, c.geo, c.node), (53036000.0, "MWh", "P1Y", "PT", "Portugal (mainland)"))
        self.assertEqual(t[t.ts_utc.str.startswith("2024") & (t.variable == "consumption")].value.iloc[0], 51407000.0)
        self.assertIn("biomass_cogeneration", set(t.variable))
        self.assertIn("natural_gas_cogeneration", set(t.variable))
        self.assertEqual(len(t[t.variable == "natural_gas_cogeneration"]), 1)

    def test_stops(self):
        for text in (HEAD.replace("Ponta [MW]", "Peak") + line("CONSUMO"), HEAD + line("Nuclear"), HEAD + line("CONSUMO", "lots")):
            with self.assertRaises(RuntimeError):
                R.file_rows(text, "u", "r", "v")
        with self.assertRaises(RuntimeError):
            R.finish(R.file_rows(HEAD + line("CONSUMO") + line("CONSUMO"), "u", "r", "v"))


class Registered(unittest.TestCase):
    def test_sector_and_hold(self):
        self.assertEqual(B.sector_of(R.NAME), "power")
        with open(os.path.join(ROOT, "warehouse", "supabase", "live_set.yaml"), encoding="utf-8") as f:
            self.assertIn(f"  - {R.NAME}\n", f.read().replace("\r\n", "\n"))


if __name__ == "__main__":
    unittest.main()

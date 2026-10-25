"""Session 2608: Enercal's activity report 2024-2025, New Caledonia's net production by plant, the public grid's purchases by
source and the transmission network's sales (July 2022 to June 2025).

Energy Research Warehouse (ERW). Tests warehouse/connectors/enercal_nc_electricity.py on page lines built here (made up for the
test, not the report's): each block found by its heading, the years read from their line, French decimals stated in MWh, a "-"
not written, a row of fewer figures given the last years; a page found twice, rows that miss their TOTAL and a line of years out
of order stopping the run; the sector rule and the holds. No network.

    python -m unittest tests.test_session2608 -v
"""

import os
import sys
import unittest

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
sys.path.insert(0, os.path.join(ROOT, "warehouse", "connectors"))
sys.path.insert(0, os.path.join(ROOT, "warehouse", "metadata"))
sys.path.insert(0, os.path.join(ROOT, "warehouse", "redivis"))
import enercal_nc_electricity as E  # noqa: E402
import build_coverage as B  # noqa: E402
import release_v1 as R  # noqa: E402

BASE = {"source": "s", "source_url": "u", "retrieved_at": "r", "vintage": "v"}
Y = "2022-2023 2023-2024 2024-2025"
E_ACUTE = chr(0xE9)


def producer(thermal_total="11,00"):
    return [E.PRODUCER, "PRODUCTION THERMIQUE", Y, "op" + E_ACUTE + "r" + E_ACUTE + "e par Enercal (nette en GWh)",
            "Alpha 10,00 - -", "Beta 1,00 2,00 3,00", f"TOTAL {thermal_total} 2,00 3,00",
            "PRODUCTION RENOUVELABLE", Y, "op" + E_ACUTE + "r" + E_ACUTE + "e par Enercal (nette en GWh)", "Gamma 5,00 6,00 7,00", "TOTAL 5,00 6,00 7,00",
            "PRODUCTION RENOUVELABLE", "op" + E_ACUTE + "r" + E_ACUTE + "e par Enercal Energies Nouvelles " + Y, "(nette en GWh)",
            "Delta 1,00 1,00 1,00", "Epsilon 0,50", "TOTAL 1,00 1,00 1,50"]


def transport(years=Y):
    return ["Chiffres", E.TRANSPORT, "DISTRIBUTION PUBLIQUE " + years, "Achats aux producteurs - en GWh", "Charbon 3,0 2,0 1,0",
            "Biogaz 2,1", "TOTAL 3,0 2,0 3,1", "Total thermique 60 % 43 % 39 %",
            "Ventes d" + chr(0x2019) + E_ACUTE + "lectricit" + E_ACUTE + " aux clients du r" + E_ACUTE + "seau de Transport de la Grande Terre - en GWh",
            "A Client 4,0 4,0 4,0", "TOTAL 4,0 4,0 4,0"]


class Parse(unittest.TestCase):
    def test_rows(self):
        t = E.parse_pages([["cover"], producer(), transport()], BASE)
        r = {(e.split(":", 2)[2], ts[:4]): v for e, ts, v in zip(t.entity, t.ts_utc, t.value)}
        self.assertEqual(r[("thermal:alpha", "2022")], 10000.0)
        self.assertNotIn(("thermal:alpha", "2023"), r)
        self.assertEqual(r[("een:epsilon", "2024")], 500.0)
        self.assertNotIn(("een:epsilon", "2022"), r)
        self.assertEqual(r[("public_purchases:biogaz", "2024")], 2100.0)
        self.assertEqual(r[("transport_sales:total", "2023")], 4000.0)
        self.assertEqual(set(t.ts_utc.str[5:10]), {"07-01"})
        self.assertEqual(set(t.unit), {"MWh"})

    def test_stops(self):
        for pages in ([producer(), producer(), transport()], [producer("12,00"), transport()],
                      [producer(), transport("2023-2024 2022-2023 2024-2025")]):
            with self.assertRaises(RuntimeError):
                E.parse_pages(pages, BASE)


class Registered(unittest.TestCase):
    def test_sector_and_holds(self):
        self.assertEqual(B.sector_of(E.NAME), "power")
        self.assertIn(E.NAME, R.STORAGE_HELD)
        with open(os.path.join(ROOT, "warehouse", "supabase", "live_set.yaml"), encoding="utf-8") as f:
            self.assertIn(f"  - {E.NAME}\n", f.read().replace("\r\n", "\n"))


if __name__ == "__main__":
    unittest.main()

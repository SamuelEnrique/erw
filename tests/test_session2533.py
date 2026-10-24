"""Session 2533: ARSEL's activity report for 2025 (Cameroon's production by source, purchases from independent producers,
transmission injections and withdrawals).

Energy Research Warehouse (ERW). Tests warehouse/connectors/arsel_cameroon_electricity.py on a report text built here (made
up for the test, not ARSEL's): the three blocks found by their words, each table's last place taken (the list of tables
names it first), figures with spaces between thousands and a decimal comma or point, table 19's GWh to MWh and its
plants with none bought not written, table 21's pairs of years; a block missing, a label not in the map, a row missing,
table 21's rows of another count and a total not the sum of its parts stopping the run; the sector rule and the holds.
No network.

    python -m unittest tests.test_session2533 -v
"""

import os
import sys
import unittest

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
sys.path.insert(0, os.path.join(ROOT, "warehouse", "connectors"))
sys.path.insert(0, os.path.join(ROOT, "warehouse", "metadata"))
sys.path.insert(0, os.path.join(ROOT, "warehouse", "redivis"))
import arsel_cameroon_electricity as A  # noqa: E402
import build_coverage as B  # noqa: E402
import release_v1 as R  # noqa: E402

BASE = {"source": "s", "source_url": "u", "retrieved_at": "r", "vintage": "v"}
NL = chr(10)
PROD = ["Hydraulique 1 000 000", "Thermique HFO 10,5", "Thermique LFO 20,5", "GAZ 300 000", "Solaire Photovolta" + chr(0xEF) + "que 4 000",
        "Total 1 304 031"]
T19 = ["NHPC 2 000,00 1 500,25 -25%", "KPDC 10,00 5,00 -50%", "DPDC 1,00 - -100%", "Memv'ele 1,00 2,00 100%", "Lom Pangar 1,00 1,00 0%",
       "Mekin 1,00 - -100%", "Aggreko 1,00 1,00 0%", "SCATEC Solaire 1,00 1,00 0%", "Release 2 Solaire 1,00 - -100%",
       "Mbakaou 1,00 1,00 0%", "Total 2 017,00 1 511,25 -25%"]
T21 = ["Injection ENEO Soutirage", "1 000.00 1 100.00 1 200.00 1 300.00", "ENEO",
       "2 000.00 2 100.00 300.00 400.00", "IPPs 5.00 6.00", "Total RIS 3 000.00 3 200.00 1 505.00 1 706.00",
       "100.00 110.00 90.00 95.00", "Total RIN 100.00 110.00 90.00 95.00", "LA TRANSPARENCE 50",
       "TOTAL (RIS+RIN) 3 100.00 3 310.00 1 595.00 1 801.00"]


def report(prod=PROD, t19=T19, t21=T21):
    title = "Rapport d" + chr(0x2019) + "activit" + chr(0xE9) + "s 2025 de l" + chr(0x2019) + "Agence"
    return NL.join([title, "Liste des tableaux", "Tableau 19:: Volumes 2025 ____ 48", "Tableau 20: Volume ____ 48",
                    "Tableau 21: energies ____ 50", "Production Total " + chr(0xE9) + "nergies produites en MWh"] + prod +
                   ["LA TRANSPARENCE POUR UN SECTEUR ELECTRIQUE PERFORMANT 14", "Tableau 19:: Volumes d'achats 2025",
                    "Projet" + chr(0xE9) + " R" + chr(0xE9) + "alis" + chr(0xE9) + " " + chr(0xE9) + "cart"] + t19 +
                   ["- une baisse globale", "Tableau 20: Volume de combustible 2025", "Tableau 21: energies injectees",
                    "Energies inject" + chr(0xE9) + "es (MWh) Energies soutir" + chr(0xE9) + "es (MWh)", "2024 2025 2024 2025"] + t21 +
                   ["- Le secteur affiche une dynamique positive"])


class Parse(unittest.TestCase):
    def test_rows(self):
        t = A.parse_text(report(), BASE)
        r = {(e, v, y[:4]): x for e, v, y, x in zip(t.entity, t.variable, t.ts_utc, t.value)}
        self.assertEqual(r[("arsel:cm:hydro", "production", "2025")], 1000000.0)
        self.assertEqual(r[("arsel:cm:thermal_hfo", "production", "2025")], 10.5)
        self.assertEqual(r[("arsel:cm:nhpc", "ipp_purchases", "2025")], 1500250.0)
        self.assertNotIn(("arsel:cm:dpdc", "ipp_purchases", "2025"), r)
        self.assertEqual(r[("arsel:cm:ris_ipp", "transmission_injection", "2024")], 2000.0)
        self.assertEqual(r[("arsel:cm:ris_hv_clients", "transmission_withdrawal", "2025")], 400.0)
        self.assertEqual(r[("arsel:cm:ris_ipps", "transmission_withdrawal", "2025")], 6.0)
        self.assertEqual(r[("arsel:cm:total", "transmission_injection", "2025")], 3310.0)
        self.assertEqual(len(t), 6 + 8 + 12 + 14)
        self.assertEqual(set(t.unit), {"MWh"})

    def test_stops(self):
        bad = [report(prod=PROD[:-1] + ["Total 9 999 999"]),
               report(prod=PROD[1:]),
               report(prod=PROD + ["Nucleaire 5"]),
               report(t19=T19[:3] + T19[4:]),
               report(t19=T19 + ["Autre 1,00 1,00 0%"]),
               report(t21=T21[:4] + T21[5:]),
               report(t21=T21[:1] + ["1 000.00 1 100.00 1 200.00 9 300.00"] + T21[2:]),
               report().replace("Tableau 21", "Tableau XXI"),
               "no report here"]
        for text in bad:
            with self.assertRaises(RuntimeError):
                A.parse_text(text, BASE)


class Registered(unittest.TestCase):
    def test_sector_and_holds(self):
        self.assertEqual(B.sector_of(A.NAME), "power")
        self.assertIn(A.NAME, R.STORAGE_HELD)
        with open(os.path.join(ROOT, "warehouse", "supabase", "live_set.yaml"), encoding="utf-8") as f:
            self.assertIn(f"  - {A.NAME}\n", f.read().replace("\r\n", "\n"))


if __name__ == "__main__":
    unittest.main()

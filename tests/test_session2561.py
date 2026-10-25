"""Session 2561: ARSE's activity report 2024, table 15 (Burkina Faso's production by producer and imports, 2023 and 2024).

Energy Research Warehouse (ERW). Tests warehouse/connectors/arse_burkina_electricity.py on page words built here (made up
for the test, not ARSE's): the label left of x 300, the 2023 and 2024 cells by their place (figures with spaces between
thousands that the text cannot split), a "-" cell and a "Non disponible" row not written, a label's second line passed
over, the page's text after the table's source line passed over, kWh to MWh; a row missing, a row not in the map, a
figure of another form and a total that misses its parts stopping the run; the sector rule and the holds. No network.

    python -m unittest tests.test_session2561 -v
"""

import os
import sys
import unittest

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
sys.path.insert(0, os.path.join(ROOT, "warehouse", "connectors"))
sys.path.insert(0, os.path.join(ROOT, "warehouse", "metadata"))
sys.path.insert(0, os.path.join(ROOT, "warehouse", "redivis"))
import arse_burkina_electricity as A  # noqa: E402
import build_coverage as B  # noqa: E402
import release_v1 as R  # noqa: E402

BASE = {"source": "s", "source_url": "u", "retrieved_at": "r", "vintage": "v"}
A_ = chr(0xE2)
E_ = chr(0xE9)


def w(text, x0, x1, top):
    return {"text": text, "x0": x0, "x1": x1, "top": top}


def line(label, c23, c24, top):
    ws, x = [], 40
    for part in label.split(" "):
        ws.append(w(part, x, x + 4 * len(part), top))
        x += 4 * len(part) + 2
    for cell, start in ((c23, 319), (c24, 413)):
        x = start
        for part in cell.split(" ") if cell else []:
            ws.append(w(part, x, x + 16, top))
            x += 18
    return ws


# label, 2023 kWh, 2024 kWh: the totals are their parts' sums
ROWS1 = [("SONABEL Thermique", "1 000 000", "2 000 000"), ("Hydro" + E_ + "lectrique", "100 000", "200 000"),
         ("Solaire Photovolta" + chr(0xEF) + "que", "10 000", "20 000"), ("FIESS (Ex. Aggreko) Thermique", "300 000", "400 000"),
         ("Nagr" + E_ + "ongo Solaire PV", "50 000", "60 000"), ("Kod" + E_ + "ni Solaire PV", "40 000", "50 000"),
         ("P" + A_ + " Solaire PV", "1 000", "30 000"), ("Zano Solaire raccord" + E_, "2 000", "3 000"), ("au RNI", "", ""),
         ("Faso Biogaz Thermique", "5 000", "6 000"), ("Essakane solar Solaire PV", "7 000", "8 000"), ("Zina (Mana) Solaire PV", "-", "9 000"),
         ("COOPEL non Mixte", "Non disponible", "Non disponible"), ("Thermique priv" + E_ + " total", "305 000", "406 000"),
         ("Solaire priv" + E_ + " Total", "90 000", "150 000")]
ROWS2 = [("HTB C" + chr(0xF4) + "te d'Ivoire- Imports", "100 000", "90 000"), ("HTB Ghana- Imports", "1 000 000", "900 000"),
         ("HTA Ghana- Imports", "20 000", "30 000"), ("HTA Togo-Burkina Imports", "5 000", "6 000"),
         ("Total SONABEL (kWh)", "1 110 000", "2 220 000"), ("Total production nationale (SONABEL + IPP)", "1 505 000", "2 776 000"),
         ("Total imports (HTB+HTA)", "1 125 000", "1 026 000"), ("Total " + E_ + "nergie produite et import" + E_ + "e en 2024", "2 630 000", "3 802 000"),
         ("Rendement de production/transport en %", "95,83", "95,83"), ("Source : ARSE, 2024", "", ""),
         ("En 2024, la production nationale", "1 411", "376 568")]


def pages(rows1=ROWS1, rows2=ROWS2):
    p1 = [w for i, r in enumerate(rows1) for w in line(*r, top=100 + 15 * i)]
    p2 = [w for i, r in enumerate(rows2) for w in line(*r, top=100 + 15 * i)]
    return [p1, p2]


class Parse(unittest.TestCase):
    def test_rows(self):
        t = A.parse_words(pages(), BASE)
        r = {(e.split(":")[-1], v, ts[:4]): x for e, v, ts, x in zip(t.entity, t.variable, t.ts_utc, t.value)}
        self.assertEqual(r[("sonabel_thermal", "production", "2024")], 2000.0)
        self.assertEqual(r[("htb_ghana", "imports", "2023")], 1000.0)
        self.assertEqual(r[("total", "supply", "2024")], 3802.0)
        self.assertNotIn(("zina_solar", "production", "2023"), r)
        self.assertEqual(r[("zina_solar", "production", "2024")], 9.0)
        self.assertEqual(len(t), 21 * 2 - 1)
        self.assertEqual(set(t.unit), {"MWh"})

    def test_stops(self):
        bad = [pages(rows1=ROWS1[:2] + ROWS1[3:]),
               pages(rows1=ROWS1 + [("Nucl" + E_ + "aire Fission", "1 000", "2 000")]),
               pages(rows1=[("SONABEL Thermique", "1 000 0000", "2 000 000")] + ROWS1[1:]),
               pages(rows2=ROWS2[:4] + [("Total SONABEL (kWh)", "1 110 000", "2 230 000")] + ROWS2[5:])]
        for p in bad:
            with self.assertRaises(RuntimeError):
                A.parse_words(p, BASE)


class Registered(unittest.TestCase):
    def test_sector_and_holds(self):
        self.assertEqual(B.sector_of(A.NAME), "power")
        self.assertIn(A.NAME, R.STORAGE_HELD)
        with open(os.path.join(ROOT, "warehouse", "supabase", "live_set.yaml"), encoding="utf-8") as f:
            self.assertIn(f"  - {A.NAME}\n", f.read().replace("\r\n", "\n"))


if __name__ == "__main__":
    unittest.main()

"""Session 2572: VMME's Balance Energetico Nacional 2024, cuadro 3 (Paraguay's electricity balance, 2023 and 2024).

Energy Research Warehouse (ERW). Tests warehouse/connectors/vmme_paraguay_electricity.py on page lines built here (made up
for the test, not VMME's): the table found by its title line (the contents page's line with a page number passed over),
the rotated unit's stray letters before a label passed over, a point between thousands and a comma before the decimal,
exports, own use and losses written positive, GWh to MWh; a row missing, a row out of order, a quantity leaving the
supply printed positive and a check missed stopping the run; the sector rule and the holds. No network.

    python -m unittest tests.test_session2572 -v
"""

import os
import sys
import unittest

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
sys.path.insert(0, os.path.join(ROOT, "warehouse", "connectors"))
sys.path.insert(0, os.path.join(ROOT, "warehouse", "metadata"))
sys.path.insert(0, os.path.join(ROOT, "warehouse", "redivis"))
import vmme_paraguay_electricity as V  # noqa: E402
import build_coverage as B  # noqa: E402
import release_v1 as R  # noqa: E402

BASE = {"source": "s", "source_url": "u", "retrieved_at": "r", "vintage": "v"}
L = [r[0] for r in V.ROWS]
# label: 2023, 2024 (GWh as printed); the totals hold their parts
FIGS = {L[0]: ("10.100,0", "12.200,0"), L[1]: ("10.000,0", "12.000,0"), L[2]: ("1.000,0", "1.000,0"), L[3]: ("8.999,0", "10.999,5"),
        L[4]: ("1,0", "0,5"), L[5]: ("100,0", "200,0"), L[6]: ("0,0", "0,0"), L[7]: ("-5.000,0", "-6.000,0"), L[8]: ("-100,0", "-200,0"),
        L[9]: ("-1.000,0", "-1.000,0"), L[10]: ("-200,0", "-300,0"), L[11]: ("-800,0", "-700,0"), L[12]: ("4.000,0", "5.000,0"),
        L[13]: ("1.000,0", "1.500,0"), L[14]: ("2.000,0", "2.500,0"), L[15]: ("1.000,0", "1.000,0"), L[16]: ("600,0", "700,0"),
        L[17]: ("400,0", "300,0"), L[18]: ("4.000,0", "5.000,0")}
STRAY = {L[7]: "h ", L[9]: "G ", L[10]: "n "}


def pages(figs=FIGS, order=None):
    order = order or L
    body = [f"{STRAY.get(k, '')}{k} {figs[k][0]} {figs[k][1]} 1,0" for k in order if k in figs]
    return [["CUADRO 3: COMPARATIVO BALANCE DE ELECTRICIDAD 48", "Generaci" + chr(0xF3) + "n Bruta 1,0 2,0 3,0"],
            ["BALANCE", V.TITLE, "METODOLOG" + chr(0xCD) + "A siePARAGUAY", "2024 - 2023", "Variaci" + chr(0xF3) + "n", "2023 2024", "W"] + body + ["48"]]


class Parse(unittest.TestCase):
    def test_rows(self):
        t = V.parse_lines(pages(), BASE)
        r = {(e.split(":")[-1], v, ts[:4]): x for e, v, ts, x in zip(t.entity, t.variable, t.ts_utc, t.value)}
        self.assertEqual(r[("total", "gross_generation", "2024")], 12200000.0)
        self.assertEqual(r[("binational_hydro", "gross_generation", "2024")], 10999500.0)
        self.assertEqual(r[("total", "exports", "2023")], 5000000.0)
        self.assertEqual(r[("transmission", "losses", "2024")], 300000.0)
        self.assertEqual(r[("total", "imports", "2023")], 0.0)
        self.assertEqual(len(t), 19 * 2)
        self.assertEqual(set(t.unit), {"MWh"})

    def test_stops(self):
        f = dict(FIGS)
        f.pop(L[4])
        g = dict(FIGS)
        g[L[7]] = ("5.000,0", "-6.000,0")
        h = dict(FIGS)
        h[L[16]] = ("700,0", "700,0")
        bad = [pages(figs=f), pages(order=[L[1], L[0]] + L[2:]), pages(figs=g), pages(figs=h)]
        for p in bad:
            with self.assertRaises(RuntimeError):
                V.parse_lines(p, BASE)


class Registered(unittest.TestCase):
    def test_sector_and_holds(self):
        self.assertEqual(B.sector_of(V.NAME), "power")
        self.assertIn(V.NAME, R.STORAGE_HELD)
        with open(os.path.join(ROOT, "warehouse", "supabase", "live_set.yaml"), encoding="utf-8") as f:
            self.assertIn(f"  - {V.NAME}\n", f.read().replace("\r\n", "\n"))


if __name__ == "__main__":
    unittest.main()

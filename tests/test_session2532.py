"""Session 2532: INSTAT Madagascar's Tableau de Bord de l'Economie no. 63, table 21 (JIRAMA's electricity a month).

Energy Research Warehouse (ERW). Tests warehouse/connectors/instat_madagascar_electricity.py on sheet rows built here (made
up for the test, not INSTAT's): the columns found by their headers whatever their place, accents in the headers, a month's
date on the 15th read as the month, the half-year totals after the months not taken, the price column not taken; a header
missing, a month given twice, a gap between months, a figure that is not a number and a total that is not the sum of its
parts stopping the run; the sector rule and the holds. No network.

    python -m unittest tests.test_session2532 -v
"""

import datetime as dt
import os
import sys
import unittest

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
sys.path.insert(0, os.path.join(ROOT, "warehouse", "connectors"))
sys.path.insert(0, os.path.join(ROOT, "warehouse", "metadata"))
sys.path.insert(0, os.path.join(ROOT, "warehouse", "redivis"))
import instat_madagascar_electricity as M  # noqa: E402
import build_coverage as B  # noqa: E402
import release_v1 as R  # noqa: E402

BASE = {"source": "s", "source_url": "u", "retrieved_at": "r", "vintage": "v"}
E = chr(0xE9)
HEAD = [(None, "Tableau 21 : Evolution mensuelle des production et consommation d'" + E + "lectricit" + E),
        (None, "P" + E + "riode", None, "Production (MWh)", None, None, None, None, None, "Prix moyen (Ar/KWh)", None,
         "Consommation d'" + E + "lectricit" + E + "  (MWh)"),
        (None, None, None, "Total", None, "Hydraulique", None, "Thermique", None, None, None, "Total", None, "M" + E + "nages", None,
         "Industries et services", None, "Eclairage public"),
        (None, "      ")]


def month(i, y, m, hyd=100.0, the=50.0, men=40.0, ind=60.0, ecl=1.5):
    return (i, dt.datetime(y, m, 15), None, hyd + the, 0, hyd, 0, the, 0, 650.5, 0, men + ind + ecl, 0, men, 0, ind, 0, ecl, 0)


def rows(months):
    return HEAD + months + [(2023, "Cumul jan-juin 26", None, 1.0, None, 1.0), (None, "Variation", "6 premiers mois", 0.1),
                            (None, "Source : JIRAMA")]


class Parse(unittest.TestCase):
    def test_rows(self):
        t = M.parse_rows(rows([month(2, 2025, 12), month(1, 2026, 1, hyd=200.25), month(0, 2026, 2)]), BASE)
        r = {(e, v, p): x for e, v, p, x in zip(t.entity, t.variable, t.x_period, t.value)}
        self.assertEqual(len(t), 3 * 7)
        self.assertEqual(r[("jirama:mg:hydro", "production", "2026-01")], 200.25)
        self.assertEqual(r[("jirama:mg:total", "production", "2026-01")], 250.25)
        self.assertEqual(r[("jirama:mg:total", "consumption", "2025-12")], 101.5)
        self.assertEqual(r[("jirama:mg:public_lighting", "consumption", "2026-02")], 1.5)
        self.assertEqual(sorted(set(t.ts_utc))[0], "2025-12-01T00:00:00Z")
        self.assertEqual(set(t.unit), {"MWh"})
        self.assertNotIn(650.5, set(t.value))

    def test_stops(self):
        bad_head = [HEAD[0], HEAD[1], tuple(c if c != "Thermique" else "Autre" for c in HEAD[2]), HEAD[3]]
        bad = [rows([month(1, 2026, 1), month(0, 2026, 1)]),
               rows([month(1, 2026, 1), month(0, 2026, 3)]),
               rows([month(0, 2026, 1)[:5] + ("n.d.",) + month(0, 2026, 1)[6:]]),
               rows([month(0, 2026, 1)[:3] + (999.0,) + month(0, 2026, 1)[4:]]),
               bad_head + [month(0, 2026, 1)],
               [("no table here",)]]
        for rs in bad:
            with self.assertRaises(RuntimeError):
                M.parse_rows(rs, BASE)


class Registered(unittest.TestCase):
    def test_sector_and_holds(self):
        self.assertEqual(B.sector_of(M.NAME), "power")
        self.assertIn(M.NAME, R.STORAGE_HELD)
        with open(os.path.join(ROOT, "warehouse", "supabase", "live_set.yaml"), encoding="utf-8") as f:
            self.assertIn(f"  - {M.NAME}\n", f.read().replace("\r\n", "\n"))


if __name__ == "__main__":
    unittest.main()

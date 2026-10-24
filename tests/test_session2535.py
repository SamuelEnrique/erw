"""Session 2535: INSEED Togo's Annuaire Statistique National 2024, tables 25.2 and 25.7 (CEET's purchases, production and
sales).

Energy Research Warehouse (ERW). Tests warehouse/connectors/inseed_togo_electricity.py on page words built here (made up
for the test, not INSEED's): the year headings giving the columns, a figure placed by its right edge, a cell of two words
("1 351") kept whole beside its neighbour, "-" not written, GWh to MWh, the table of contents' page passed over; a row
not in the map, a row missing, a year heading missing, a figure of another form and a total not the sum of its parts
stopping the run; the sector rule and the holds. No network.

    python -m unittest tests.test_session2535 -v
"""

import os
import sys
import unittest

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
sys.path.insert(0, os.path.join(ROOT, "warehouse", "connectors"))
sys.path.insert(0, os.path.join(ROOT, "warehouse", "metadata"))
sys.path.insert(0, os.path.join(ROOT, "warehouse", "redivis"))
import inseed_togo_electricity as T  # noqa: E402
import build_coverage as B  # noqa: E402
import release_v1 as R  # noqa: E402

BASE = {"source": "s", "source_url": "u", "retrieved_at": "r", "vintage": "v"}
RIGHT = {"2020": 320, "2021": 369, "2022": 417, "2023": 465, "2024": 513}
E = chr(0xE9)
VENTES = "Ventes d" + chr(0x2019) + E + "lectricit" + E


def word(text, x0, x1, top):
    return {"text": text, "x0": x0, "x1": x1, "top": top}


def row(label, cells, top):
    """Label words from x 77, then each year's cell, right-aligned under its heading; a cell of two words is split."""
    ws, x = [], 77
    for part in label.split(" "):
        ws.append(word(part, x, x + 6 * len(part), top))
        x += 6 * len(part) + 3
    for y, c in zip(T.YEARS, cells):
        parts = c.split(" ")
        right = RIGHT[y]
        for part in reversed(parts):
            ws.append(word(part, right - 5 * len(part), right, top + 0.5))
            right -= 5 * len(part) + 3
    return ws


def table(no, title, rows, top=100, years=T.YEARS):
    ws = [word("Tableau", 71, 108, top), word(no, 112, 132, top), word(":", 135, 137, top), word(title, 141, 200, top),
          word("RUBRIQUES", 77, 132, top + 20)]
    ws += [word(y, RIGHT[y] - 31, RIGHT[y] - 8, top + 20.5) for y in years]
    for k, (label, cells) in enumerate(rows):
        ws += row(label, cells, top + 40 + 17 * k)
    ws.append(word("Source", 77, 110, top + 60 + 17 * len(rows)))
    return ws


T252 = [("ACHATS VRA-TCN- SBEE-NANGBETO", ["868,59", "838,18", "907,98", "1 351", "983,53"]),
        ("SBEE B" + E + "nin (Transfrontalier)", ["1,92", "1,74", "1,97", "2,57", "1,78"]),
        ("ECG Ghana (Transfrontalier)", ["5,3", "5,32", "5,74", "5,97", "5,39"]),
        ("SNPT Togo", ["0,47", "0,52", "0,56", "0,62", "0,68"]),
        ("TOTAL Achats (GWh)", ["876,28", "845,76", "916,26", "1 360,05", "991,38"]),
        ("Production Brute CEET (GWh)", ["6,58", "8,37", "7,57", "7,72", "4,90"]),
        ("Production Brute CGT(GWh)", ["533,86", "619,85", "552,08", "398,02", "530,51"]),
        ("Production Nette KEP(GWh)", ["-", "14,08", "181,20", "148,04", "439,44"]),
        ("Production AMEA(GWh)", ["-", "55,07", "82,86", "79,35", "120,65"])]
T257 = [(VENTES + " BT", ["718", "776", "805", "907", "-"]), (VENTES + " MT", ["460", "506", "664", "593", "-"]),
        ("TOTAL", ["1 178", "1 282", "1 469", "1 500", "-"])]


def pages(t252=T252, t257=T257, years=T.YEARS):
    toc = ("Tableau 25.2 : Achat et production .......... 501 Tableau 25.7 : Ventes .......... 502 RUBRIQUES Source", [])
    p1 = ("Tableau 25.2 : Achat et production RUBRIQUES Source", table("25.2", "Achat", t252, years=years) +
          [word("Tableau", 71, 108, 400), word("25.3", 112, 132, 400)])
    p2 = ("Tableau 25.7 : Ventes RUBRIQUES Source", table("25.7", "Ventes", t257, years=years))
    return [toc, p1, p2]


class Parse(unittest.TestCase):
    def test_rows(self):
        t = T.parse_pages(pages(), BASE)
        r = {(e, v, y[:4]): x for e, v, y, x in zip(t.entity, t.variable, t.ts_utc, t.value)}
        self.assertEqual(r[("inseed:tg:vra_tcn_sbee_nangbeto", "purchases", "2023")], 1351000.0)
        self.assertEqual(r[("inseed:tg:vra_tcn_sbee_nangbeto", "purchases", "2024")], 983530.0)
        self.assertEqual(r[("inseed:tg:total", "purchases", "2023")], 1360050.0)
        self.assertEqual(r[("inseed:tg:kep", "net_production", "2024")], 439440.0)
        self.assertNotIn(("inseed:tg:kep", "net_production", "2020"), r)
        self.assertEqual(r[("inseed:tg:total", "sales", "2020")], 1178000.0)
        self.assertNotIn(("inseed:tg:total", "sales", "2024"), r)
        self.assertEqual(len(t), 9 * 5 - 2 + 3 * 4)
        self.assertEqual(set(t.unit), {"MWh"})

    def test_stops(self):
        bad = [pages(t252=T252 + [("Production Solaire (GWh)", ["1", "1", "1", "1", "1"])]),
               pages(t252=T252[:3] + T252[4:]),
               pages(years=T.YEARS[:4]),
               pages(t257=T257[:2] + [("TOTAL", ["1 178", "1 282", "1 469", "1 600", "-"])]),
               pages(t252=T252[:5] + [("Production Brute CEET (GWh)", ["6.58", "8,37", "7,57", "7,72", "4,90"])] + T252[6:]),
               pages()[:2]]
        for p in bad:
            with self.assertRaises(RuntimeError):
                T.parse_pages(p, BASE)


class Registered(unittest.TestCase):
    def test_sector_and_holds(self):
        self.assertEqual(B.sector_of(T.NAME), "power")
        self.assertIn(T.NAME, R.STORAGE_HELD)
        with open(os.path.join(ROOT, "warehouse", "supabase", "live_set.yaml"), encoding="utf-8") as f:
            self.assertIn(f"  - {T.NAME}\n", f.read().replace("\r\n", "\n"))


if __name__ == "__main__":
    unittest.main()

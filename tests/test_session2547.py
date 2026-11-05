"""Session 2547: DERK's report on activities 2025, Annex C (Bosnia and Herzegovina's balance by utility, a year).

Energy Research Warehouse (ERW). Tests warehouse/connectors/derk_bih_electricity.py on page words built here (made up for
the test, not DERK's): a block a year, its headings giving the columns' right edges (two headings on a second line, "BIH"
twice), right-aligned figures placed under their column with cells left empty, the footer passed over, BIH's consumption
holding the transmission losses, GWh to MWh; a row not in the map, a row missing, two figures under one column, a figure
of another form and a BIH figure not the sum of the utilities stopping the run; the sector rule and the holds. No network.

    python -m unittest tests.test_session2547 -v
"""

import os
import sys
import unittest

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
sys.path.insert(0, os.path.join(ROOT, "warehouse", "connectors"))
sys.path.insert(0, os.path.join(ROOT, "warehouse", "metadata"))
sys.path.insert(0, os.path.join(ROOT, "warehouse", "redivis"))
import derk_bih_electricity as D  # noqa: E402
import build_coverage as B  # noqa: E402
import release_v1 as R  # noqa: E402

BASE = {"source": "s", "source_url": "u", "retrieved_at": "r", "vintage": "v"}
EDGE = {"ep_bih": 264, "ers": 321, "ep_hzhb": 370, "komunalno_brcko": 434, "other_entities": 484, "total": 534}
BRCKO = "Br" + chr(0x10D) + "ko"


def w(text, x0, x1, top):
    return {"text": text, "x0": x0, "x1": x1, "top": top}


def label_words(label, top):
    out, x = [], 71
    for part in label.split(" "):
        out.append(w(part, x, x + 4 * len(part), top))
        x += 4 * len(part) + 2
    return out


# a row: label and {utility: figure text}
ROWS = [("Generation in hydropower plants", {"ep_bih": "100.00", "ers": "200.00", "ep_hzhb": "50.00", "other_entities": "10.00", "total": "360.00"}),
        ("Generation in thermal power plants", {"ep_bih": "1,000.00", "ers": "500.00", "other_entities": "5.00", "total": "1,505.00"}),
        ("Generation in larger solar and wind PPs", {"ep_bih": "1.00", "ep_hzhb": "2.00", "other_entities": "3.00", "total": "6.00"}),
        ("Generation in small and industrial PPs", {"ep_bih": "4.00", "ers": "5.00", "other_entities": "6.00", "total": "15.00"}),
        ("Generation", {"ep_bih": "1,105.00", "ers": "705.00", "ep_hzhb": "52.00", "other_entities": "24.00", "total": "1,886.00"}),
        ("Customers connected to distr. network", {"ep_bih": "900.00", "ers": "600.00", "ep_hzhb": "100.00", "komunalno_brcko": "30.00", "total": "1,630.00"}),
        ("Transmission losses", {"total": "40.00"}),
        ("Large customers", {"ep_bih": "50.00", "ers": "20.00", "ep_hzhb": "1.00", "total": "71.00"}),
        ("PPs self-consumption and pumping", {"ep_bih": "1.00", "ers": "2.00", "ep_hzhb": "3.00", "other_entities": "0.50", "total": "6.50"}),
        ("Consumption", {"ep_bih": "951.00", "ers": "622.00", "ep_hzhb": "104.00", "komunalno_brcko": "30.00", "other_entities": "0.50", "total": "1,747.50"})]


def block(year, top, rows=ROWS):
    ws = [w("Komunalno", 393, 434, top - 5), w("Other", 464, 484, top - 5), w("Year", 64, 82, top), w(year, 84, 102, top),
          w("EP", 237, 247, top), w("BIH", 249, 264, top), w("ERS", 304, 321, top), w("EP", 334, 344, top), w("HZHB", 346, 370, top),
          w("BIH", 519, 534, top), w(BRCKO, 413, 434, top + 5), w("entities", 459, 484, top + 5)]
    for k, (label, cells) in enumerate(rows):
        t = top + 16 + 11 * k
        ws += label_words(label, t)
        for util, fig in cells.items():
            ws.append(w(fig, EDGE[util] - 4 * len(fig), EDGE[util], t))
    return ws


def page(rows=ROWS):
    return block("2025", 100, rows) + block("2024", 236) + [w("serc", 57, 77, 790), w("2025", 80, 104, 790), w("report", 107, 137, 790), w("81", 527, 539, 790)]


class Parse(unittest.TestCase):
    def test_rows(self):
        t, years = D.parse_words(page(), BASE)
        r = {(e.split(":")[-1], v, ts[:4]): x for e, v, ts, x in zip(t.entity, t.variable, t.ts_utc, t.value)}
        self.assertEqual(years, ["2025", "2024"])
        self.assertEqual(r[("ep_hzhb", "generation_hydro", "2025")], 50000.0)
        self.assertEqual(r[("other_entities", "generation_thermal", "2024")], 5000.0)
        self.assertNotIn(("ep_hzhb", "generation_thermal", "2025"), r)
        self.assertEqual(r[("komunalno_brcko", "consumption_distribution", "2025")], 30000.0)
        self.assertEqual(r[("total", "transmission_losses", "2025")], 40000.0)
        self.assertEqual(r[("total", "consumption", "2025")], 1747500.0)
        self.assertEqual(len(t), 2 * sum(len(c) for _, c in ROWS))
        self.assertEqual(set(t.unit), {"MWh"})

    def test_stops(self):
        bad = [ROWS + [("Generation in fusion plants", {"total": "1.00"})],
               ROWS[:2] + ROWS[3:],
               [(ROWS[0][0], dict(ROWS[0][1], total="361.00"))] + ROWS[1:],
               [(ROWS[0][0], dict(ROWS[0][1], ep_bih="100,00"))] + ROWS[1:],
               ROWS[:9] + [("Consumption", dict(ROWS[9][1], total="1,707.50"))]]
        for rows in bad:
            with self.assertRaises(RuntimeError):
                D.parse_words(page(rows), BASE)
        twice = page()
        twice.append(w("9.00", 300, 321, 100 + 16))  # a second figure under ERS on the hydro line
        with self.assertRaises(RuntimeError):
            D.parse_words(twice, BASE)


class Registered(unittest.TestCase):
    def test_sector_and_holds(self):
        self.assertEqual(B.sector_of(D.NAME), "power")
        self.assertIn(D.NAME, R.STORAGE_HELD)
        with open(os.path.join(ROOT, "warehouse", "supabase", "live_set.yaml"), encoding="utf-8") as f:
            self.assertIn(f"  - {D.NAME}\n", f.read().replace("\r\n", "\n"))


if __name__ == "__main__":
    unittest.main()

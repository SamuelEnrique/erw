"""Session 2633: ESO's Compendium of Statistics 2024, Table 20.01, Grand Cayman's electricity capacity, production and
consumption by class a year.

Energy Research Warehouse (ERW). Tests warehouse/connectors/eso_cayman_electricity.py on sheet rows built here (made up for the
test, not the Office's): the table found by its title and header row, blank spacing rows skipped, each year's six figures taken
with their units; a gap in the years, classes that miss the total, a header out of order and a text cell stopping the run; the
sector rule and the holds. No network.

    python -m unittest tests.test_session2633 -v
"""

import os
import sys
import unittest

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
sys.path.insert(0, os.path.join(ROOT, "warehouse", "connectors"))
sys.path.insert(0, os.path.join(ROOT, "warehouse", "metadata"))
sys.path.insert(0, os.path.join(ROOT, "warehouse", "redivis"))
import eso_cayman_electricity as E  # noqa: E402
import build_coverage as B  # noqa: E402
import release_v1 as R  # noqa: E402

BLANK = ["", "", "", "", "", "", "", "", "", ""]


def rows(body=None, header=None):
    h = ["", ""] + (header or E.HEADER)
    body = body if body is not None else [
        ["", "", 2000.0, 100.0, 500.0, 200.0, 250.0, 5.0, 455.0, 1.0], BLANK,
        ["", "", 2001.0, 100.0, 520.0, 210.0, 260.0, 5.0, 475.0, 4.4], ["", "", 2002.0, 110.0, 540.0, 220.0, 270.0, 5.0, 495.0, 4.2]]
    return [["", "", "", "", "", "", "", "COMPENDIUM", "", ""], ["", 20.01, E.TITLE + ", 2000 -  2002", "", "", "", "", "", "", ""],
            h, BLANK] + body + [["", "", "Note:", "", "", "", "", "", "", ""]]


class Parse(unittest.TestCase):
    def test_rows(self):
        years = E.parse_rows(rows())
        self.assertEqual([y for y, _ in years], [2000, 2001, 2002])
        self.assertEqual(years[1][1], [100.0, 520.0, 210.0, 260.0, 5.0, 475.0])

    def test_frame(self):
        t = E.frame(E.parse_rows(rows()), {"source": "s", "source_url": "u", "retrieved_at": "r", "vintage": "v"})
        r = {(e.split(":")[-1], ts[:4]): (v, u) for e, ts, v, u in zip(t.entity, t.ts_utc, t.value, t.unit)}
        self.assertEqual(r[("capacity", "2002")], (110.0, "MW"))
        self.assertEqual(r[("production", "2000")], (500.0, "MWh"))
        self.assertEqual(len(t), 18)

    def test_stops(self):
        gap = [["", "", 2000.0, 1.0, 5.0, 1.0, 1.0, 1.0, 3.0, 0], ["", "", 2002.0, 1.0, 5.0, 1.0, 1.0, 1.0, 3.0, 0]]
        off = [["", "", 2000.0, 1.0, 5.0, 1.0, 1.0, 1.0, 9.0, 0]]
        text = [["", "", 2000.0, 1.0, "x", 1.0, 1.0, 1.0, 3.0, 0]]
        for b, h in ((gap, None), (off, None), (text, None), (None, list(reversed(E.HEADER)))):
            with self.assertRaises(RuntimeError):
                E.parse_rows(rows(b, h))


class Registered(unittest.TestCase):
    def test_sector_and_holds(self):
        self.assertEqual(B.sector_of(E.NAME), "power")
        self.assertIn(E.NAME, R.STORAGE_HELD)
        with open(os.path.join(ROOT, "warehouse", "supabase", "live_set.yaml"), encoding="utf-8") as f:
            self.assertIn(f"  - {E.NAME}\n", f.read().replace("\r\n", "\n"))


if __name__ == "__main__":
    unittest.main()

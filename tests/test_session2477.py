"""Session 2477: MIREME's Energy Statistical Report, table 3.2.2 (Mozambique's electricity balance, 2020 to 2024).

Energy Research Warehouse (ERW). Tests warehouse/connectors/mireme_mozambique_electricity.py on a page built here as words
with their positions (made up for the test, not MIREME's): each figure's digit groups joined within its year's column, the
parentheses of a subtracted quantity dropped, a section's own row as its total and its items under it, a cell marked "..."
with no row, a cell out of the form of thousands not written and counted, the variation column not taken; a page without
the five years, a row not in the map and an item before its section stopping the run; the sector rule and the holds. No
network.

    python -m unittest tests.test_session2477 -v
"""

import os
import sys
import unittest

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
sys.path.insert(0, os.path.join(ROOT, "warehouse", "connectors"))
sys.path.insert(0, os.path.join(ROOT, "warehouse", "metadata"))
sys.path.insert(0, os.path.join(ROOT, "warehouse", "redivis"))
import mireme_mozambique_electricity as S  # noqa: E402
import build_coverage as B  # noqa: E402
import release_v1 as R  # noqa: E402

BASE = {"source": "s", "source_url": "u", "retrieved_at": "r", "vintage": "v"}
COLS = [276, 364, 455, 544, 635]          # the years' x0, as on the report's page


class Page:
    def __init__(self, words):
        self.words = words

    def extract_words(self):
        return self.words


def word(text, x0, top):
    return {"text": text, "x0": float(x0), "x1": float(x0 + 6 * len(text)), "top": float(top)}


def line(label, cells, top, vp="1,0"):
    """A row: its label at the left, then each year's figure as digit groups ending just right of the year's column."""
    ws = [word(t, 57 + 40 * i, top) for i, t in enumerate(label.split())]
    for x, cell in zip(COLS, cells):
        groups = cell.split()
        for k, g in enumerate(groups):
            ws.append(word(g, x - 25 + 14 * k, top))
    ws.append(word(vp, 711, top))
    return ws


def page(rows, years=True):
    ws = [word("Quadro", 72, 120), word("3.2.2", 106, 120)]
    if years:
        ws += [word(y, x, 138) for y, x in zip(S.YEARS, COLS)]
    top = 159
    for label, cells in rows:
        ws += line(label, cells, top)
        top += 12
    return Page(ws)


ROWS = [("PRODUÇÃO / Production", ["18 939 680", "18 786 866", "19 402 606", "19 628 104", "19 455 039"]),
        ("Hídrica / Hydro", ["15 703 398", "15 466 323", "16 173 409", "16 350 864", "16 317 104"]),
        ("Solar / Solar", ["45 638", "69 175", "69 7017", "66 942", "61 058"]),
        ("Bagaço / Bagasse", ["104 507", "77 698", "65 428", "…", "…"]),
        ("EXPORTAÇÃO / EXPORT", ["(11 488 796)", "(11 174 165)", "(11 456 772)", "(11 391 511)", "(10 679 212)"]),
        ("PERDAS TOTAIS / Losses", ["(3 040 985)", "(2 947 446)", "(2 976 268)", "(3 360 679)", "(2 809 604)"]),
        ("Transporte / Transport", ["(1 630 797)", "(1 557 462)", "(1 664 659)", "(1 201 853)", "(1 486 253)"])]


class Parse(unittest.TestCase):
    def test_rows(self):
        counts = {}
        rows = {(r["entity"], r["variable"], r["ts_utc"]): r for r in S.parse_page(page(ROWS), BASE, counts)}
        g = rows[("mireme:mz:total", "generation", "2020-01-01T00:00:00Z")]
        self.assertEqual((g["value"], g["unit"], g["freq"], g["geo"]), (18939680.0, "MWh", "P1Y", "MZ"))
        self.assertEqual(rows[("mireme:mz:hydro", "generation", "2024-01-01T00:00:00Z")]["value"], 16317104.0)
        self.assertEqual(rows[("mireme:mz:total", "exports", "2024-01-01T00:00:00Z")]["value"], 10679212.0)
        self.assertEqual(rows[("mireme:mz:transport", "losses", "2023-01-01T00:00:00Z")]["value"], 1201853.0)
        self.assertNotIn(("mireme:mz:solar", "generation", "2022-01-01T00:00:00Z"), rows)
        self.assertNotIn(("mireme:mz:bagasse", "generation", "2023-01-01T00:00:00Z"), rows)
        self.assertEqual(counts, {"cells out of form": 1})
        self.assertEqual(len(rows), 7 * 5 - 1 - 2)

    def test_stops(self):
        for pg in (page(ROWS, years=False), page([("Nuclear / Nuclear", ["1", "2", "3", "4", "5"])]),
                   page([("Hídrica / Hydro", ["1", "2", "3", "4", "5"])])):
            with self.assertRaises(RuntimeError):
                S.parse_page(pg, BASE, {})


class Registered(unittest.TestCase):
    def test_sector_and_holds(self):
        self.assertEqual(B.sector_of(S.NAME), "power")
        self.assertIn(S.NAME, R.STORAGE_HELD)
        with open(os.path.join(ROOT, "warehouse", "supabase", "live_set.yaml"), encoding="utf-8") as f:
            self.assertIn(f"  - {S.NAME}\n", f.read().replace("\r\n", "\n"))


if __name__ == "__main__":
    unittest.main()

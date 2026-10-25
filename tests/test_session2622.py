"""Session 2622: the Amt fuer Statistik Liechtenstein's Energie 2025, Tabelle 5, Liechtenstein's electricity a year since 1985.

Energy Research Warehouse (ERW). Tests warehouse/connectors/asli_liechtenstein_electricity.py on sheet rows built here (made up
for the test, not the Office's): the table found by its title and header rows, each year's four figures taken, 2022's two rows
read as the old and the new method (the new written, the old kept beside it), "-" written as 0; a gap in the years, a year other
than 2022 given twice, a balance that misses consumption and a cell outside the key stopping the run; the sector rule and the
holds. No network.

    python -m unittest tests.test_session2622 -v
"""

import os
import sys
import unittest

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
sys.path.insert(0, os.path.join(ROOT, "warehouse", "connectors"))
sys.path.insert(0, os.path.join(ROOT, "warehouse", "metadata"))
sys.path.insert(0, os.path.join(ROOT, "warehouse", "redivis"))
import asli_liechtenstein_electricity as A  # noqa: E402
import build_coverage as B  # noqa: E402
import release_v1 as R  # noqa: E402

BASE = {"source": "s", "source_url": "u", "retrieved_at": "r", "vintage": "v"}


def rows(years=None):
    head = [(A.TITLE, None, None, None, None), ("<<< Inhalt",), ("Tabelle 5",),
            (None, "Produktion im Inland", "Import", "Export", "Verbrauch im Inland"), ("Jahr", "MWh", "MWh", "MWh", "MWh")]
    body = years if years is not None else (
        [(y, 100.0, 300.0, "-", 400.0) for y in range(1985, 2022)] + [(2022, 90.0, 300.0, 0, 390.0), (2022, 95.0, 300.0, 0, 395.0),
                                                                      (2023, 120.0, 280.0, 0, 400.0)])
    return head + body + [("<<< Metadaten ",)]


class Parse(unittest.TestCase):
    def test_rows(self):
        years = A.parse_rows(rows())
        self.assertEqual(len(years), 40)
        self.assertEqual(years[0], (1985, [100.0, 300.0, 0.0, 400.0]))

    def test_frame(self):
        import io
        import openpyxl
        wb = openpyxl.Workbook()
        ws = wb.active
        ws.title = "Tabelle 5"
        for r in rows():
            ws.append(list(r))
        buf = io.BytesIO()
        wb.save(buf)
        t = A.parse(buf.getvalue(), BASE)
        r = {(e.split(":")[-1], ts[:4]): (v, m, o) for e, ts, v, m, o in zip(t.entity, t.ts_utc, t.value, t.x_pv_method, t.x_old_method_value)}
        self.assertEqual(r[("production", "2022")], (95.0, "new", 90.0))
        self.assertEqual(r[("production", "2021")], (100.0, "old", ""))
        self.assertEqual(r[("exports", "1990")][0], 0.0)
        self.assertEqual(len(t), 39 * 4)

    def test_stops(self):
        gap = [(y, 1.0, 1.0, 0, 2.0) for y in range(1985, 2020) if y != 2000]
        twice = [(y, 1.0, 1.0, 0, 2.0) for y in range(1985, 2020)] + [(2019, 1.0, 1.0, 0, 2.0)]
        off = [(y, 1.0, 1.0, 0, 2.0) for y in range(1985, 2020)] + [(2020, 1.0, 1.0, 0, 5.0)]
        bad = [(y, 1.0, 1.0, 0, 2.0) for y in range(1985, 2020)] + [(2020, "x", 1.0, 0, 2.0)]
        for b in (gap, twice, off, bad):
            with self.assertRaises(RuntimeError):
                A.parse_rows(rows(b))


class Registered(unittest.TestCase):
    def test_sector_and_holds(self):
        self.assertEqual(B.sector_of(A.NAME), "power")
        self.assertIn(A.NAME, R.STORAGE_HELD)
        with open(os.path.join(ROOT, "warehouse", "supabase", "live_set.yaml"), encoding="utf-8") as f:
            self.assertIn(f"  - {A.NAME}\n", f.read().replace("\r\n", "\n"))


if __name__ == "__main__":
    unittest.main()

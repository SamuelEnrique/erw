"""Session 2226: DESNZ's Energy Trends 4.1, the UK's natural gas supply and consumption.

Energy Research Warehouse (ERW). Tests warehouse/connectors/desnz_gas.py on a workbook built here in DESNZ's form (made
up for the test, not DESNZ's): each line a variable in snake case, its notes dropped; GWh written as MWh on the quarter's
first day; a provisional quarter marked; a blank cell not written; the page's one ET 4.1 link; a sheet missing, a header
of another form, a value not a number and a line given twice stopping the run; the sector rule and the holds. No network.

    python -m unittest tests.test_session2226 -v
"""

import io
import os
import sys
import unittest

import openpyxl

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
sys.path.insert(0, os.path.join(ROOT, "warehouse", "connectors"))
sys.path.insert(0, os.path.join(ROOT, "warehouse", "metadata"))
sys.path.insert(0, os.path.join(ROOT, "warehouse", "redivis"))
import desnz_gas as D  # noqa: E402
import build_coverage as B  # noqa: E402
import release_v1 as R  # noqa: E402


def book(rows, sheet="Quarter (GWh)"):
    wb = openpyxl.Workbook()
    ws = wb.active
    ws.title = sheet
    for r in rows:
        ws.append(r)
    n = wb.create_sheet("Notes")
    n.append(["Note 4", "Positive (+) stock change is equal to a stock draw"])
    b = io.BytesIO()
    wb.save(b)
    return b.getvalue()


HEAD = ["Column1", "2025 \n4th quarter ", "2026 \n1st quarter", "2026 \n2nd quarter [provisional]"]
ROWS = [["Table 4.1 Natural gas supply and consumption, quarterly data (GWh)"], HEAD,
        ["Indigenous production", 80000, 79000.5, 77679.17], ["Imports [note 2]", 70000, None, 73683.8], ["Iron & steel", 600, 590, 584.2]]


class Build(unittest.TestCase):
    def test_rows(self):
        t, notes = D.build(book(ROWS), "u", "r", "v")
        s = t.set_index(["variable", "ts_utc"])
        self.assertEqual(s.loc[("indigenous_production", "2026-01-01T00:00:00Z")].value, 79000500.0)
        self.assertEqual(s.loc[("indigenous_production", "2025-10-01T00:00:00Z")].x_provisional, "no")
        self.assertEqual(s.loc[("indigenous_production", "2026-04-01T00:00:00Z")].x_provisional, "yes")
        self.assertEqual(s.loc[("imports", "2025-10-01T00:00:00Z")].node, "Imports [note 2]")
        self.assertNotIn(("imports", "2026-01-01T00:00:00Z"), s.index)
        self.assertIn(("iron_steel", "2026-04-01T00:00:00Z"), s.index)
        self.assertEqual(set(t.unit), {"MWh"})
        self.assertEqual(notes, ["Note 4: Positive (+) stock change is equal to a stock draw"])

    def test_link(self):
        page = '<a href="https://assets.publishing.service.gov.uk/media/abc/ET_4.1_SEP_26.xlsx">x</a><a href="https://assets.publishing.service.gov.uk/media/d/ET_4.2_SEP_26.xlsx">y</a>'
        self.assertEqual(D.link_of(page), "https://assets.publishing.service.gov.uk/media/abc/ET_4.1_SEP_26.xlsx")
        with self.assertRaises(RuntimeError):
            D.link_of("no link")

    def test_stops(self):
        bad_head = [ROWS[0], ["Column1", "Q1 2026"], ROWS[2]]
        bad_value = ROWS[:2] + [["Indigenous production", 80000, "n/a", 1]]
        twice = ROWS + [["Indigenous production", 1, 2, 3]]
        for b in (book(ROWS, sheet="Annual (GWh)"), book(bad_head), book(bad_value), book(twice)):
            with self.assertRaises(RuntimeError):
                D.build(b, "u", "r", "v")


class Registered(unittest.TestCase):
    def test_sector_and_holds(self):
        self.assertEqual(B.sector_of(D.NAME), "gas")
        self.assertIn(D.NAME, R.STORAGE_HELD)
        with open(os.path.join(ROOT, "warehouse", "supabase", "live_set.yaml"), encoding="utf-8") as f:
            self.assertIn(f"  - {D.NAME}\n", f.read().replace("\r\n", "\n"))


if __name__ == "__main__":
    unittest.main()

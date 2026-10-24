"""Session 2174: the UK's renewable capacity and generation by technology (DESNZ, Energy Trends table 6.1).

Energy Research Warehouse (ERW). Tests warehouse/connectors/desnz_renewables.py on a workbook built here in table ET
6.1's "Quarter" form (made up for the test, not DESNZ's): the capacity and generation blocks taken, load factors and
shares left, note markers left out of the technology's name, GWh written as MWh, a quarter as its first day, "[x]" left
out, a provisional quarter marked; a sheet without the blocks, a header not a quarter and a value that is neither a number
nor "[x]" stopping the run; the sector rule and the holds. No network.

    python -m unittest tests.test_session2174 -v
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
import desnz_renewables as D  # noqa: E402
import build_coverage as B  # noqa: E402
import release_v1 as R  # noqa: E402

Q = ["2010 \n1st quarter", "2026\n2nd quarter [provisional]"]


def workbook(rows, sheet="Quarter"):
    wb = openpyxl.Workbook()
    ws = wb.active
    ws.title = sheet
    for r in rows:
        ws.append(r)
    b = io.BytesIO()
    wb.save(b)
    return b.getvalue()


ROWS = [["Renewable quarterly electricity capacity and generation"], [None],
        ["CUMULATIVE INSTALLED CAPACITY (MW) \n[note 1]"] + Q, ["Onshore wind", 3913, 15800], ["Liquid biofuels", "[x]", "[x]"],
        ["TOTAL", 8609, 66286], [None],
        ["ELECTRICITY GENERATED (GWh) [note 6]"] + Q, ["Onshore wind [note 8]", 1757.35, 9000.5], ["TOTAL", 6248.68, 27000], [None],
        ["LOAD FACTORS (%) [note 12]"] + Q, ["Onshore wind", 22.04, 30.0]]


class Build(unittest.TestCase):
    def test_rows(self):
        t = D.build(workbook(ROWS), "u", "r", "")
        self.assertEqual(set(t.variable), {"capacity", "generated"})
        c = t[(t.entity == "desnz_et61:onshore_wind") & (t.variable == "capacity") & (t.ts_utc == "2026-04-01T00:00:00Z")].iloc[0]
        self.assertEqual((c.value, c.unit, c.freq, c.geo, c.x_provisional), (15800.0, "MW", "P3M", "GB", "yes"))
        g = t[(t.entity == "desnz_et61:onshore_wind") & (t.variable == "generated") & (t.ts_utc == "2010-01-01T00:00:00Z")].iloc[0]
        self.assertEqual((g.value, g.unit, g.x_technology, g.x_provisional), (1757350.0, "MWh", "Onshore wind", "no"))
        self.assertFalse((t.entity == "desnz_et61:liquid_biofuels").any())
        self.assertEqual(len(t), 4 + 4)

    def test_stops(self):
        for bad in (workbook(ROWS, sheet="Annual"), workbook(ROWS[:7]),
                    workbook([ROWS[2][:1] + ["2010 Q1"], ROWS[3]] + ROWS[6:10]),
                    workbook(ROWS[:3] + [["Onshore wind", "n/a", 1]] + ROWS[6:10])):
            with self.assertRaises(RuntimeError):
                D.build(bad, "u", "r", "")


class Registered(unittest.TestCase):
    def test_sector_and_holds(self):
        self.assertEqual(B.sector_of(D.NAME), "power")
        self.assertIn(D.NAME, R.STORAGE_HELD)
        with open(os.path.join(ROOT, "warehouse", "supabase", "live_set.yaml"), encoding="utf-8") as f:
            self.assertIn(f"  - {D.NAME}\n", f.read().replace("\r\n", "\n"))


if __name__ == "__main__":
    unittest.main()

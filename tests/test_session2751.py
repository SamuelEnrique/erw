"""Session 2751: WAPA's energy sold and power rate by project, each fiscal year from 2008.

Energy Research Warehouse (ERW). Tests warehouse/connectors/wapa_rates_sales.py on a sheet built here (made up for the test, not
WAPA's): two tables read by their titles and the third left, footnote marks dropped from the project names, N/A given no row, the
rate stated in USD/MWh (cents/kWh times 10), the fiscal year stamped on 1 October of the year before; the projects checked against
WAPA's total; a total missed, a project given twice, a year row out of order and a cell neither a number nor N/A stopping the run;
the sector rule and the holds. No network.

    python -m unittest tests.test_session2751 -v
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
import wapa_rates_sales as A  # noqa: E402
import build_coverage as B  # noqa: E402
import release_v1 as R  # noqa: E402

Y = A.YEARS


def sheet(total=20.0, years=None, extra=None, cell=10.0):
    ys = years or Y
    e = [("Energy Sold (MWh)",) + tuple(ys), ("Alpha Project 1/",) + (10.0,) * 18, ("Beta Project",) + (cell,) + (10.0,) * 17,
         ("Gamma",) + ("N/A",) * 17 + (10.0,)]
    if extra:
        e.append(extra)
    e.append(("(WAPA Total)",) + (total,) + (20.0,) * 16 + (30.0,))
    return (e + [("Power Rate (cents/kWh)",) + tuple(Y), ("Alpha Project 3/",) + (2.5,) * 18]
            + [("Transmission Rate (dollars/kW/month)",) + tuple(Y), ("Alpha Project",) + (1.5,) * 18, ("1/ a note",)])


class Parse(unittest.TestCase):
    def test_rows(self):
        vals, nodes = A.parse_sheet(sheet())
        self.assertEqual(vals[(2025, "alpha_project", "energy_sold")], (10.0, "MWh"))
        self.assertEqual(vals[(2025, "alpha_project", "power_rate")], (25.0, "USD/MWh"))
        self.assertNotIn((2025, "gamma", "energy_sold"), vals)                 # N/A has no row
        self.assertEqual(vals[(2008, "gamma", "energy_sold")][0], 10.0)
        self.assertEqual(nodes["alpha_project"], "Alpha Project")
        self.assertFalse(any(k[2] == "transmission_rate" for k in vals))       # the third table is left
        self.assertEqual(len([k for k in vals if k[2] == "power_rate"]), 18)

    def test_frame(self):
        wb = openpyxl.Workbook()
        ws = wb.active
        ws.title = A.SHEET
        for r in sheet():
            ws.append(list(r))
        buf = io.BytesIO()
        wb.save(buf)
        t = A.parse(buf.getvalue(), dict(source="s", source_url="u", retrieved_at="r", vintage="v"))
        self.assertEqual(t.ts_utc.min(), "2007-10-01T00:00:00Z")                 # fiscal year 2008 begins 1 October 2007
        self.assertEqual(t.ts_utc.max(), "2024-10-01T00:00:00Z")
        self.assertEqual(set(t.unit), {"MWh", "USD/MWh"})
        self.assertEqual(len(t), 18 * 3 + 1 + 18)                               # three full energy rows, Gamma one, the rate

    def test_stops(self):
        for rows in (sheet(total=31.0),                                          # the projects make 20, the total 31
                     sheet(years=list(reversed(Y))),
                     sheet(extra=("Alpha Project",) + (1.0,) * 18),
                     sheet(cell="n.a.")):
            with self.assertRaises(RuntimeError):
                A.parse_sheet(rows)


class Registered(unittest.TestCase):
    def test_sector_and_holds(self):
        self.assertEqual(B.sector_of(A.NAME), "power")
        self.assertIn(A.NAME, R.STORAGE_HELD)
        with open(os.path.join(ROOT, "warehouse", "supabase", "live_set.yaml"), encoding="utf-8") as f:
            self.assertIn(f"  - {A.NAME}\n", f.read().replace("\r\n", "\n"))


if __name__ == "__main__":
    unittest.main()

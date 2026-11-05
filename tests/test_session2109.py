"""Session 2109: the California Energy Commission's Total System Electric Generation.

Energy Research Warehouse (ERW). Tests warehouse/connectors/cec_total_system.py on a workbook built here in the
Commission's form (figures made up for the test, not the Commission's): three regions, Total Imports, the Total block
with oil and other combined and its empty row, the Grand Total and the note; GWh as MWh; a dash and a blank left out;
a region that does not sum, a Total block fuel that does not match the regions and a fuel not in the map each stopping
the run; the workbook's address found on the page; the sector rule and the holds. No network.

    python -m unittest tests.test_session2109 -v
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
import cec_total_system as C  # noqa: E402
import build_coverage as B  # noqa: E402
import release_v1 as R  # noqa: E402

BASE = {"source": "s", "source_url": "u", "retrieved_at": "r", "vintage": "v"}


def book(ca_total=110, total_solar=60, fuel="Solar", nw_oil="-"):
    wb = openpyxl.Workbook()
    w = wb.active
    w.append(["", "", "", "", "Percent Change"])
    w.append(["Region", "Fuel Type", 2024, 2025, "", "2024-2025"])
    w.append(["California", "Natural Gas", 60, 50])
    w.append(["California", fuel, 50, 60])
    w.append(["California", "Oil", 1, 0])
    w.append(["", "California Total", 111, ca_total])
    w.append([])
    w.append(["Northwest", "Oil", 2, nw_oil])
    w.append(["Northwest", "Other (Waste Heat / Petroleum Coke)", 3, ""])
    w.append(["Northwest", "Unspecified", 10, 12])
    w.append(["", "Northwest Total", 15, 12])
    w.append(["Southwest", "Solar", 5, 8])
    w.append(["", "Southwest Total", 5, 8])
    w.append(["", "Total Imports", 20, 20])
    w.append(["Total", "Natural Gas", 60, 50])
    w.append(["Total", "Oil/Other", 6, 0])
    w.append(["Total", "", "", ""])
    w.append(["Total", "Solar", 55, total_solar + 8])
    w.append(["Total", "Unspecified Imports", 10, 12])
    w.append(["", "Grand Total", 131, 130])
    w.append([])
    w.append(["", "All figures are gigawatt-hours. Rounding may have been applied where necessary."])
    b = io.BytesIO()
    wb.save(b)
    return b.getvalue()


def run(content):
    rows, totals, years, dashes = C.parse(content, BASE)
    C.check(rows, totals, years)
    return rows, dashes


class Parse(unittest.TestCase):
    def test_book(self):
        rows, dashes = run(book())
        self.assertEqual(len(dashes), 2)  # Northwest's oil (a dash) and other (blank) in 2025
        by = {(r["entity"], r["ts_utc"][:4]): r for r in rows}
        r = by[("cec_tsp:california:solar", "2025")]
        self.assertEqual((r["value"], r["unit"], r["variable"], r["geo"]), (60000.0, "MWh", "in_state_generation", "US-CA"))
        self.assertEqual(by[("cec_tsp:northwest:unspecified", "2025")]["variable"], "imports")
        self.assertEqual(by[("cec_tsp:total:oil_other", "2024")]["variable"], "total_system_power")
        self.assertNotIn(("cec_tsp:northwest:oil", "2025"), by)

    def test_stops(self):
        for kw, words in [(dict(ca_total=125), "the fuels sum to"), (dict(total_solar=70), "the Total block"),
                          (dict(fuel="Tidal"), "a fuel not in the map")]:
            with self.assertRaises(RuntimeError) as c:
                run(book(**kw))
            self.assertIn(words, str(c.exception), kw)

    def test_workbook_url(self):
        page = '<a href="/sites/default/files/2026-10/Total_System_Electric_Generation_2009-2025_with_totals_ada.xlsx">x</a><a href="/y.xlsx">y</a>'
        self.assertEqual(C.workbook_url(page),
                         "https://www.energy.ca.gov/sites/default/files/2026-10/Total_System_Electric_Generation_2009-2025_with_totals_ada.xlsx")
        with self.assertRaises(RuntimeError):
            C.workbook_url('<a href="/y.xlsx">y</a>')


class Registered(unittest.TestCase):
    def test_sector_and_holds(self):
        self.assertEqual(B.sector_of(C.TABLE), "power")
        self.assertIn(C.TABLE, R.STORAGE_HELD)
        with open(os.path.join(ROOT, "warehouse", "supabase", "live_set.yaml"), encoding="utf-8") as f:
            self.assertIn(f"  - {C.TABLE}\n", f.read().replace("\r\n", "\n"))


if __name__ == "__main__":
    unittest.main()

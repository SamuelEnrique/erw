"""Session 2090: EIA's state-to-state natural gas pipeline capacity.

Energy Research Warehouse (ERW). Tests warehouse/connectors/eia_state_to_state.py on a sheet built here in EIA's form
(made up for the test, not EIA's): the newest workbook a page links, each crossing a series with its place among repeats,
MMcf a day over 1,000 in bcf/d, the state to's geo and none for a province; a sheet without its columns, a year not a
year and a capacity not a number stopping the run; the sector rule and the holds. No network.

    python -m unittest tests.test_session2090 -v
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
import eia_state_to_state as E  # noqa: E402
import build_coverage as B  # noqa: E402
import release_v1 as R  # noqa: E402

BASE = {"source": "s", "source_url": "u", "retrieved_at": "r", "vintage": "v"}


def book(rows, head=None):
    wb = openpyxl.Workbook()
    ws = wb.active
    ws.title = E.SHEET
    ws.append(["Pipeline State-to-State Capacity"])
    ws.append(head or E.NEED)
    for r in rows:
        ws.append(r)
    b = io.BytesIO()
    wb.save(b)
    return b.getvalue()


ROWS = [["2024", "Algonquin Gas Trans Co", "Northeast", "Intra-regional", "New Jersey", "Hudson", "New York", "Rockland", "1625", ""],
        ["2024", "Nat Gas P L Co Of America", "South Central", "Intra-regional", "Arkansas", "Miller", "Texas", "Cass", "460", "Phase I"],
        ["2024", "Nat Gas P L Co Of America", "South Central", "Intra-regional", "Arkansas", "Miller", "Texas", "Cass", "600", ""],
        ["2024", "Great Lakes Gas Trans", "Midwest", "Canada", "Michigan", "St. Clair", "Ontario", "Lambton", "1,200", ""]]


class Read(unittest.TestCase):
    def test_newest(self):
        page = ('<a href="/naturalgas/pipelines/EIA-StatetoStateCapacity_Jan2025.xlsx">a</a>'
                '<a href="/naturalgas/pipelines/EIA-StatetoStateCapacity_Jan2026.xlsx">b</a>')
        self.assertEqual(E.newest(page)[2], "https://www.eia.gov/naturalgas/pipelines/EIA-StatetoStateCapacity_Jan2026.xlsx")
        with self.assertRaises(RuntimeError):
            E.newest("<a href='/other.xlsx'>x</a>")

    def test_rows(self):
        s = E.build(E.read(book(ROWS)), BASE).set_index("entity")
        a = s.loc["eia_s2s:algonquin_gas_trans_co:new_jersey:hudson:new_york:rockland:1"]
        self.assertEqual((a.value, a.unit, a.geo, a.x_capacity_mmcfd), (1.625, "bcf/d", "US-NY", "1625"))
        self.assertIn("eia_s2s:nat_gas_p_l_co_of_america:arkansas:miller:texas:cass:2", s.index)
        self.assertEqual(s.loc["eia_s2s:great_lakes_gas_trans:michigan:st_clair:ontario:lambton:1"].geo, "")
        self.assertEqual(s.loc["eia_s2s:great_lakes_gas_trans:michigan:st_clair:ontario:lambton:1"].value, 1.2)

    def test_stops(self):
        with self.assertRaises(RuntimeError):
            E.read(book(ROWS, head=E.NEED[:-1]))
        with self.assertRaises(RuntimeError):
            E.read(book([["soon"] + ROWS[0][1:]]))
        with self.assertRaises(RuntimeError):
            E.read(book([ROWS[0][:8] + ["lots", ""]]))


class Registered(unittest.TestCase):
    def test_sector_and_holds(self):
        self.assertEqual(B.sector_of(E.TABLE), "gas")
        self.assertIn(E.TABLE, R.STORAGE_HELD)
        with open(os.path.join(ROOT, "warehouse", "supabase", "live_set.yaml"), encoding="utf-8") as f:
            self.assertIn(f"  - {E.TABLE}\n", f.read().replace("\r\n", "\n"))


if __name__ == "__main__":
    unittest.main()

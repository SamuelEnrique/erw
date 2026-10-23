"""Session 2031: EIA's biofuels plant production capacity.

Energy Research Warehouse (ERW). Tests warehouse/connectors/eia_biofuels_capacity.py on workbooks built here in EIA's
two forms (made up for the test, not EIA's): the 2026 combined sheet, and a 2025 single-fuel sheet with a state written
once above its plants, PADD rows, a co-processing footnote and "(s)"; a facility type not known, a plant before any
state and a capacity neither a number nor "(s)" stopping the run; the sector rule and the holds. No network.

    python -m unittest tests.test_session2031 -v
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
import eia_biofuels_capacity as C  # noqa: E402
import build_coverage as B  # noqa: E402
import release_v1 as R  # noqa: E402

BASE = {"source": "s", "source_url": "u", "retrieved_at": "r", "vintage": "v"}


def book(rows):
    wb = openpyxl.Workbook()
    ws = wb.active
    for r in rows:
        ws.append(r)
    b = io.BytesIO()
    wb.save(b)
    return b.getvalue()


HEAD26 = ["Entity", "Facility", "State", "PADD", "Capacity (MMgal/yr)", "Capacity (Mb/d)", "Facility type"]
SINGLE = [["U.S. Renewable Diesel Plant Production Capacity as of January 1, 2025"], [], ["State", "Respondent", "City", "MMgal/yr", "Mb/d"],
          ["PADD 3", None, None, 500, 33], ["Louisiana", "Refinery One 1", "Norco", 54, 4], [None, "Plant Two LLC", "Geismar", 108, 7],
          ["Texas", "Small Fuels", "Austin", 5, "(s)"], ["U.S. Total", None, None, 167, 11], ["(s)=Less than 0.5"]]


class Read(unittest.TestCase):
    def test_combined(self):
        rows = C.read_combined(book([HEAD26, ["ACE ETHANOL LLC", "STANLEY", "WI", "PADD 2", 52, 3, "Ethanol"],
                                     ["ALTAIR PARAMOUNT LLC", "PARAMOUNT", "CA", "PADD 5", 42, 3, "Renewable Diesel Fuel and Other Biofuels"]]))
        e = {r["entity_id"]: r for r in C.build(rows, 2026, BASE)}
        a = e["eia_biofuel:2026:ethanol:wi:1"]
        self.assertEqual((a["name"], a["operator"], a["geo"], a["status_date"], a["x_capacity_mmgal_per_year"]),
                         ("STANLEY", "ACE ETHANOL LLC", "US-WI", "2026-01-01", "52"))
        self.assertIn("eia_biofuel:2026:renewable_diesel_and_other:ca:1", e)

    def test_single(self):
        rows = C.read_single(book(SINGLE), "renewable_diesel_and_other", "Renewable Diesel Fuel and Other Biofuels")
        e = {r["entity_id"]: r for r in C.build(rows, 2025, BASE)}
        a, b, c = (e[f"eia_biofuel:2025:renewable_diesel_and_other:{k}"] for k in ("la:1", "la:2", "tx:1"))
        self.assertEqual((a["operator"], a["x_coprocessing"], a["x_padd"], a["x_city"]), ("Refinery One", "yes", "PADD 3", "Norco"))
        self.assertEqual((b["operator"], b["geo"], b["x_coprocessing"]), ("Plant Two LLC", "US-LA", ""))
        self.assertEqual(c["x_capacity_kbbl_per_day"], "(s)")
        self.assertEqual(len(e), 3)

    def test_stops(self):
        with self.assertRaises(RuntimeError):
            C.read_combined(book([HEAD26, ["X", "Y", "WI", "PADD 2", 1, 1, "Hydrogen"]]))
        with self.assertRaises(RuntimeError):
            C.read_single(book(SINGLE[:3] + [[None, "Orphan LLC", "Nowhere", 1, 1]]), "biodiesel", "Biodiesel")
        with self.assertRaises(RuntimeError):
            C.read_single(book(SINGLE[:4] + [["Texas", "Odd", "Austin", "about 5", 1]]), "biodiesel", "Biodiesel")


class Registered(unittest.TestCase):
    def test_sector_and_holds(self):
        self.assertEqual(B.sector_of(C.TABLE), "products")
        self.assertIn(C.TABLE, R.STORAGE_HELD)
        with open(os.path.join(ROOT, "warehouse", "supabase", "live_set.yaml"), encoding="utf-8") as f:
            self.assertIn(f"  - {C.TABLE}\n", f.read().replace("\r\n", "\n"))


if __name__ == "__main__":
    unittest.main()

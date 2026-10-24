"""Session 2155: AFDC's historical EV charging station and port counts by state.

Energy Research Warehouse (ERW). Tests warehouse/connectors/afdc_ev_charging.py on sheets built here in AFDC's form
(figures made up for the test, not AFDC's): two lines a state, commas in the numbers, the Total row checked and not
kept, a state whose levels do not sum to its ports kept as printed and listed; a Total that differs, a cell that does
not read and a state not in the map each stopping the run; the workbook's address found on the page; the sector rule
and the holds. No network.

    python -m unittest tests.test_session2155 -v
"""

import os
import sys
import unittest

import pandas as pd

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
sys.path.insert(0, os.path.join(ROOT, "warehouse", "connectors"))
sys.path.insert(0, os.path.join(ROOT, "warehouse", "metadata"))
sys.path.insert(0, os.path.join(ROOT, "warehouse", "redivis"))
import afdc_ev_charging as A  # noqa: E402
import build_coverage as B  # noqa: E402
import release_v1 as R  # noqa: E402

BASE = {"source": "s", "source_url": "u", "retrieved_at": "r", "vintage": "v"}


def sheet(total_off=0, cell=None, extra=None, odd="Montana"):
    rows = [["Station Counts by State and Fuel Type"] + [""] * 9,
            ["State", "Biodiesel", "CNG", "E85", "Electrica", "Hydrogenb", "LNG", "Propanec", "Renewable Diesel", "Totald"],
            ["", "", "", "", "(stations / charging outlets", "", "", "", "", ""],
            ["", "", "", "", "Level 1 / Level 2 / DC Fast)", "", "", "", "", ""]]
    tot = [0] * 5
    for name in list(A.STATES) + ([extra] if extra else []):
        st, l1, l2, dc = 10, 1, 1000, 200
        ports = l1 + l2 + dc + (2 if name == odd else 0)
        rows.append([name, 0, 0, 0, cell if (cell and name == "Alabama") else f"{st} | {ports:,}", "0 | 0 | 0", 0, "0 | 0 | 0", 0, 0])
        rows.append(["", "", "", "", f"{l1} | {l2:,} | {dc}", "", "", "", "", ""])
        tot = [a + b for a, b in zip(tot, [st, ports, l1, l2, dc])]
    rows.append(["Total", 0, 0, 0, f"{tot[0]} | {tot[1] + total_off:,}", "", 0, "", 0, 0])
    rows.append(["", "", "", "", f"{tot[2]} | {tot[3]:,} | {tot[4]:,}", "", "", "", "", ""])
    return pd.DataFrame(rows, dtype=object)


class Parse(unittest.TestCase):
    def test_sheet(self):
        unequal = []
        rows = A.parse_year(sheet(), 2024, BASE, unequal)
        self.assertEqual(len(rows), 51 * 5)
        self.assertEqual(unequal, ["2024 Montana 1201 of 1203"])
        al = {r["variable"]: r["value"] for r in rows if r["geo"] == "US-AL"}
        self.assertEqual(al, {"ev_stations": 10.0, "ev_ports": 1201.0, "ev_level1_ports": 1.0, "ev_level2_ports": 1000.0, "ev_dcfast_ports": 200.0})
        self.assertEqual(rows[0]["ts_utc"], "2024-01-01T00:00:00Z")

    def test_stops(self):
        for kw, words in [(dict(total_off=5), "the Total row is"), (dict(cell="ten | 2"), "whole numbers"),
                          (dict(extra="Puerto Rico"), "not a state in the map")]:
            with self.assertRaises(RuntimeError) as c:
                A.parse_year(sheet(**kw), 2024, BASE, [])
            self.assertIn(words, str(c.exception), kw)

    def test_workbook_url(self):
        page = '<a href="/files/docs/historical-station-counts.xlsx">x</a><a href="/data_download">d</a>'
        self.assertEqual(A.workbook_url(page), "https://afdc.energy.gov/files/docs/historical-station-counts.xlsx")


class Registered(unittest.TestCase):
    def test_sector_and_holds(self):
        self.assertEqual(B.sector_of(A.TABLE), "power")
        self.assertIn(A.TABLE, R.STORAGE_HELD)
        with open(os.path.join(ROOT, "warehouse", "supabase", "live_set.yaml"), encoding="utf-8") as f:
            self.assertIn(f"  - {A.TABLE}\n", f.read().replace("\r\n", "\n"))


if __name__ == "__main__":
    unittest.main()

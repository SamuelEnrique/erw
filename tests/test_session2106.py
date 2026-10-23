"""Session 2106: BLM's oil and gas statistics by state and fiscal year.

Energy Research Warehouse (ERW). Tests warehouse/connectors/blm_oil_gas_stats.py on a workbook built here in BLM's form
(figures made up for the test, not BLM's): the Summary and Tables 1 to 10, the 50 states and a total, Table 3's "FY  2020"
header with two spaces; the fiscal year's start as ts_utc; a total that differs from its states, a total that differs
from the Summary, a state not in the map, a state missing and a text cell each stopping the run; the workbook's address found on the
statistics page; the acre unit; the sector rule and the holds. No network.

    python -m unittest tests.test_session2106 -v
"""

import io
import os
import sys
import unittest

import openpyxl
import pandas as pd

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
sys.path.insert(0, os.path.join(ROOT, "warehouse", "connectors"))
sys.path.insert(0, os.path.join(ROOT, "warehouse", "metadata"))
sys.path.insert(0, os.path.join(ROOT, "warehouse", "redivis"))
sys.path.append(os.path.join(ROOT, "warehouse", "validate"))  # appended: warehouse/validate has a build_coverage.py of its own
import blm_oil_gas_stats as M  # noqa: E402
import build_coverage as B  # noqa: E402
import erw_validate as V  # noqa: E402
import release_v1 as R  # noqa: E402

BASE = {"source": "s", "source_url": "u", "retrieved_at": "r", "vintage": "v"}
SHEETS = {1: "Table 1 Number of Leases", 2: "Table 2 Acreage in Effect", 3: "Table 3 Number of New Leases ", 4: "Table 4 Acreage in New Leases ",
          5: "Table 5 Producing Leases", 6: "Table 6 Producing Acres", 7: "Table 7 Number of Approved APDs", 8: "Table 8 Wells Spud",
          9: "Table 9 Producible Well Bores", 10: "Table 10 Producible Completions"}
SUMMARY = {1: "Total Number of Leases in Effect", 2: "Total Number of Acres Leased", 3: "Total Number of New Leases Issued During the Year",
           4: "Total Number of Acres Leased During the Year", 5: "Total Number of Producing Leases on Federal Lands",
           6: "Total Number of Producing Acres on Federal Lands", 7: "1 Total Number of APDs approved by Year on Federal Lands",
           8: "1 Total Number Of Wells Started (Spud) During the Year on Federal Lands",
           9: "1  Total Number of Producible and Service Holes on Federal Lands",
           10: "1  Total Number of Producible and Service Completions on Federal Lands"}
YEARS = [2019, 2020]
ALL = [n + " " if n == "Delaware" else n for n in M.STATES]  # BLM writes "Delaware " with a space
DE = ALL.index("Delaware ")


def book(states=None, total_off=0, summary_off=0, text_cell=False):
    """Every table holds the states' figures n * 10 + k (k the state's place) in each year; the total is their sum."""
    states = states or ALL
    wb = openpyxl.Workbook()
    s = wb.active
    s.title = "Summary"
    s.append(["As of 10/01/2025"])
    s.append(["Summary Of Onshore Oil & Gas Statistics"])
    s.append([None] + [f"FY {y}" for y in YEARS])
    for n, words in SUMMARY.items():
        s.append([words] + [sum(n * 10 + k + y - 2019 for k in range(len(states))) + summary_off for y in YEARS])
    for n, title in SHEETS.items():
        w = wb.create_sheet(title)
        w.append(["As of 10/1/2025"])
        w.append(["the table's title"])
        w.append(["Geographic State"] + [("FY  %d" if n == 3 and y >= 2020 else "FY %d") % y for y in YEARS])
        for k, st in enumerate(states):
            w.append([st] + [n * 10 + k + y - 2019 for y in YEARS])
        if text_cell and n == 4:
            w.cell(row=4, column=2, value="n/a")
        w.append(["TOTAL" if n == 5 else "Total"] + [sum(n * 10 + k + y - 2019 for k in range(len(states))) + total_off for y in YEARS])
        w.append(["Note: For all years, data is Federal-only; does not include Indian leases."])
    b = io.BytesIO()
    wb.save(b)
    return pd.ExcelFile(io.BytesIO(b.getvalue()))


def rows(x):
    totals, _ = M.summary(x)
    out = []
    for n in M.TABLES:
        out += M.parse(x, n, BASE, totals)[0]
    return pd.DataFrame(out)


class Parse(unittest.TestCase):
    def test_tables(self):
        s = rows(book())
        self.assertEqual(len(s), 10 * 50 * 2)
        self.assertEqual(s.entity.nunique(), 50)
        r = s[(s.entity == "blm_oil_gas:de") & (s.variable == "new_leases_issued") & (s.x_fiscal_year == "2020")].iloc[0]
        self.assertEqual(r.value, 3 * 10 + DE + 1)  # Table 3's "FY  2020" read
        self.assertEqual(r.ts_utc, "2019-10-01T00:00:00Z")
        self.assertEqual((r.geo, r.node, r.x_table, r.x_as_of), ("US-DE", "Delaware", "Table 3", "2025-10-01"))
        self.assertEqual(set(s[s.unit == "acre"].variable), {"acres_under_lease", "acres_newly_leased", "producing_acres"})
        self.assertEqual(len(s[s.variable == "apds_approved"]), 100)

    def test_stops(self):
        for kw, words in [(dict(total_off=1), "the states sum to"), (dict(summary_off=1), "differs from the Summary"),
                          (dict(states=ALL[:-1] + ["Puerto Rico"]), "not a state in the map"),
                          (dict(states=ALL[:-1]), "49 states, not 50"), (dict(text_cell=True), "not a number")]:
            with self.assertRaises(RuntimeError) as c:
                rows(book(**kw))
            self.assertIn(words, str(c.exception), kw)

    def test_workbook_url(self):
        page = ('<a href="/sites/default/files/docs/2025-07/BLM-FY2024-Oil-and-Gas-Statistics-All-Fed-Oil-Gas-Statistics.xlsx">24</a>'
                '<a href="/sites/default/files/docs/2026-04/All%20Fed%20O_G%20Statistics%20by%20Year%20by%20State_Web%20Stats_Tabs%20w%20Table%20Numbers_FY25.xlsx">25</a>'
                '<a href="/sites/default/files/docs/2026-04/Table%2013%20EOI%20Acres%20CY%202006-2025.xlsx">13</a>')
        url, fy = M.workbook_url(page)
        self.assertEqual(fy, 2025)
        self.assertTrue(url.startswith("https://www.blm.gov/sites/default/files/docs/2026-04/All%20Fed"))
        with self.assertRaises(RuntimeError):
            M.workbook_url('<a href="/x/Table%2013.xlsx">13</a>')


class Registered(unittest.TestCase):
    def test_unit(self):
        self.assertIn("acre", V.UNITS)
        with open(os.path.join(ROOT, "docs", "datastandard.md"), encoding="utf-8") as f:
            self.assertIn("(Decision 62) `acre`", f.read())

    def test_sector_and_holds(self):
        self.assertEqual(B.sector_of(M.TABLE), "oil;gas")
        self.assertIn(M.TABLE, R.STORAGE_HELD)
        with open(os.path.join(ROOT, "warehouse", "supabase", "live_set.yaml"), encoding="utf-8") as f:
            self.assertIn(f"  - {M.TABLE}\n", f.read().replace("\r\n", "\n"))


if __name__ == "__main__":
    unittest.main()

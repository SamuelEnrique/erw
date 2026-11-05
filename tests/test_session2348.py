"""Session 2348: the Danish Energy Agency's monthly electricity supply statistics (the .xls workbook).

Energy Research Warehouse (ERW). Tests warehouse/connectors/ens_denmark_electricity.py on a workbook built here as plain
cells (made up for the test, not the agency's), given to the parser in place of xlrd's: only the monthly block is taken
(a year row, then Danish month names), each cell a row in MWh on the month's first day, a blank cell not written; the
area sheets' columns 13 and 14 named as the flows between West and East; a sheet missing, a column label changed, a month
name not Danish and a value that is not a number stopping the run; the sector rule and the holds. No network.

    python -m unittest tests.test_session2348 -v
"""

import os
import sys
import unittest
from unittest import mock

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
sys.path.insert(0, os.path.join(ROOT, "warehouse", "connectors"))
sys.path.insert(0, os.path.join(ROOT, "warehouse", "metadata"))
sys.path.insert(0, os.path.join(ROOT, "warehouse", "redivis"))
import ens_denmark_electricity as S  # noqa: E402
import build_coverage as B  # noqa: E402
import release_v1 as R  # noqa: E402

BASE = {"source": "s", "source_url": "u", "retrieved_at": "r", "vintage": "v"}


class Sheet:
    def __init__(self, name, cells):
        self.name, self.cells = name, cells
        self.nrows = max(i for i, _ in cells) + 1

    def cell_value(self, i, j):
        return self.cells.get((i, j), "")


class Book:
    def __init__(self, sheets):
        self.sheets = {s.name: s for s in sheets}

    def sheet_names(self):
        return list(self.sheets)

    def sheet_by_name(self, name):
        return self.sheets[name]


def sheet(name, area=False, monthly=((2026, "Januar", 100.0), (2026, "Februar", 110.0))):
    cells = {}
    for j, (var, words) in S.COLUMNS.items():
        cells[(6, j)] = words
        cells[(2, j)] = "dk " + var
    if area:
        cells[(6, 13)], cells[(6, 14)] = "From West to East", "From East to West"
    cells[(11, 0)] = 2025.0          # the annual block, not taken
    cells[(11, 2)] = 999.0
    row = 20
    year = None
    for y, m, v in monthly:
        if y != year:
            cells[(row, 0)] = float(y)
            year = y
            row += 1
        cells[(row, 0)] = m
        cells[(row, 2)] = v
        cells[(row, 13)] = 1.5
        row += 1
    cells[(row + 1, 0)] = "1) a footnote"
    return Sheet(name, cells)


def book(**over):
    sheets = [sheet("Hele landet (Denmark)"), sheet("Energinet.dk_Vest (West)", area=True), sheet("Energinet.dk_Øst (East)", area=True)]
    for s in sheets:
        if s.name in over:
            s.cells.update(over[s.name])
    return Book(sheets)


def parse(b):
    with mock.patch.object(S.xlrd, "open_workbook", return_value=b):
        return S.parse(b"", BASE)


class Parse(unittest.TestCase):
    def test_rows(self):
        t = parse(book())
        self.assertEqual(len(t), 12)
        n = t[(t.entity == "ens:dk") & (t.variable == "gross_production")].set_index("ts_utc")
        self.assertEqual(n.value.to_dict(), {"2026-01-01T00:00:00Z": 100000.0, "2026-02-01T00:00:00Z": 110000.0})
        self.assertEqual(set(t[t.entity == "ens:dk"].variable), {"gross_production", "net_exchange_west"})
        self.assertEqual(set(t[t.entity == "ens:dk_west"].variable), {"gross_production", "flow_west_to_east"})
        self.assertEqual(t.unit.unique().tolist(), ["MWh"])

    def test_stops(self):
        bad = [Book([sheet("Hele landet (Denmark)"), sheet("Energinet.dk_Vest (West)", area=True)]),
               book(**{"Hele landet (Denmark)": {(6, 8): "Total Solar"}}),
               book(**{"Energinet.dk_Vest (West)": {(6, 5): "Something else"}}),
               book(**{"Hele landet (Denmark)": {(22, 0): "January"}}),
               book(**{"Hele landet (Denmark)": {(21, 3): "n/a"}})]
        for b in bad:
            with self.assertRaises(RuntimeError):
                parse(b)


class Registered(unittest.TestCase):
    def test_sector_and_holds(self):
        self.assertEqual(B.sector_of(S.NAME), "power")
        self.assertIn(S.NAME, R.STORAGE_HELD)
        with open(os.path.join(ROOT, "warehouse", "supabase", "live_set.yaml"), encoding="utf-8") as f:
            self.assertIn(f"  - {S.NAME}\n", f.read().replace("\r\n", "\n"))


if __name__ == "__main__":
    unittest.main()

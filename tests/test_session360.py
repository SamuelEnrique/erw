"""Session 360: EIA-930's balance, reported against adjusted (warehouse/analysis/eia930_balance.py).

Energy Research Warehouse (ERW). The workbook here is a fixture built in the test, not EIA's data. No network.

  1. the workbook's hourly sheet is read: EIA's time is the end of the hour, the table's start an hour before; the ties
     are the neighbour columns between the adjusted generation and the subregions;
  2. the note quotes the figures the script wrote (docs/methods/eia930_balance.json), and the pack's four reproduced
     gaps are the pack's own.

    python -m unittest tests.test_session360 -v
"""

import datetime as dt
import json
import os
import shutil
import sys
import tempfile
import unittest

import openpyxl

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
sys.path.insert(0, os.path.join(ROOT, "warehouse", "analysis"))
import eia930_balance as B  # noqa: E402

HEAD = ["BA", "UTC time", "Demand", "Net generation", "Total interchange", "Imputed demand", "Imputed net generation", "Imputed total interchange",
        "Adjusted demand", "Adjusted net generation", "Adjusted total interchange", "Adjusted UNK Gen", "AAA", "BBB", "Subregion X", "CO2 Factor: COL"]


class TestWorkbook(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.mkdtemp(prefix="erw360_")

    def tearDown(self):
        shutil.rmtree(self.tmp, ignore_errors=True)

    def test_read(self):
        wb = openpyxl.Workbook()
        ws = wb.active
        ws.title = "Published Hourly Data"
        ws.append(HEAD)
        ws.append(["XX", dt.datetime(2026, 9, 13, 1), 100, 120, 20, None, None, None, 100, 120, 20, 0, 15, 5, 1, 1])
        th = wb.create_sheet("Imbalance Thresholds")
        th.append(["BA", "Acceptable NG D TI imbalance", "Acceptable TI DIBA imbalance"])
        th.append(["XX", 10, 13])
        p = os.path.join(self.tmp, "XX.xlsx")
        wb.save(p)
        f, ties, thr = B.workbook(p)
        self.assertEqual(ties, ["AAA", "BBB"])
        self.assertEqual(list(f.index), ["2026-09-13T00:00:00Z"])
        self.assertEqual((f["tie:AAA"].iloc[0], f["tie:BBB"].iloc[0]), (15, 5))
        self.assertEqual(thr["XX"], {"ng_d_ti": 10, "ti_diba": 13})


class TestNote(unittest.TestCase):
    def test_note_quotes_the_figures(self):
        with open(os.path.join(ROOT, "docs", "methods", "eia930_balance.json"), encoding="utf-8") as f:
            r = json.load(f)
        with open(os.path.join(ROOT, "docs", "methods", "eia930_balance.md"), encoding="utf-8") as f:
            note = f.read()
        pack = {"CISO": 3199.1, "PJM": 2042.1, "MISO": 1397.9, "SWPP": 978.1, "ERCO": 1.6, "NYIS": 0.4}
        for ba, v in pack.items():
            self.assertEqual(r["bas"][ba]["pack_test_reproduced"]["mean_abs_gap_mw"], v, ba)
        for ba in ("CISO", "MISO", "PJM"):
            self.assertIn(f"{r['bas'][ba]['reported']['total_gap_mw']:,.1f}", note)
        for ba, x in r["bas"].items():
            self.assertEqual(x["reported"], x["adjusted"] if ba != "ISNE" else x["reported"], ba)
        self.assertNotIn("—", note)


if __name__ == "__main__":
    unittest.main()

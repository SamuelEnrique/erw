"""Session 910: the Canada Energy Regulator's natural gas trade with the U.S.

Energy Research Warehouse (ERW). Tests warehouse/connectors/cer_gas_trade.py on a workbook built here in the CER's form
(figures made up for the test, not the CER's): the Mcf and US dollar columns taken, the cubic metre and Canadian dollar
columns not; the imports taken to December 2022 only; a heading not as read stopping the run; the sector rule and the
holds. No network.

    python -m unittest tests.test_session910 -v
"""

import io
import os
import sys
import unittest

import pandas as pd

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
sys.path.insert(0, os.path.join(ROOT, "warehouse", "connectors"))
sys.path.insert(0, os.path.join(ROOT, "warehouse", "metadata"))
sys.path.insert(0, os.path.join(ROOT, "warehouse", "redivis"))
import cer_gas_trade as G  # noqa: E402
import build_coverage as B  # noqa: E402
import release_v1 as R  # noqa: E402

D = "�"
SHEETS = {
    "Fig. 1(m) Fig. 4(m)": [["Date", f"Gas Export Volume / Volume d{D}exportation de gaz (103m3)", f"Gas Export Volume / Volume d{D}exportation de gaz (Mcf / Kpi3)",
                             f"Gas Export Value / Valeur {D} l{D}exportation de gaz ($)"],
                            ["2022-12-01", 8000, 280000, 1e9], ["2023-01-01", 9000, 310000, 1e9]],
    "Fig. 2(m)": [["Date", "West / Ouest (Mcf / Kpi3)", "Midwest (Mcf / Kpi3)", "East / Est (Mcf / Kpi3)"],
                  ["2022-12-01", 100000, 120000, 60000], ["2023-01-01", 110000, 130000, 70000]],
    "Fig. 3(m)": [["Date", f"LNG Export Volume / Volume d{D}exportation de GNL (Mcf / Kpi3)"], ["2022-12-01", 0], ["2023-01-01", 5]],
    "Fig. 5(m)": [["Date", f"Gas Export Price / Prix d{D}exportation du gaz ($CA per GJ / $CDN par GJ)",
                   f"Gas Export Price / Prix d{D}exportation du gaz ($US per MMBtu / $US par MBtu)"], ["2022-12-01", 6.1, 5.2], ["2023-01-01", 4.0, 3.1]],
    "ARCHIVED - Imports": [["Date", f"Gas Import Volume / Volume d{D}importation de gaz (Mcf / Kpi3)",
                            f"Gas Import Price / Prix d{D}importation du gaz ($US per MMBtu / $US par MBtu)",
                            f"LNG Import Volume / Volume d{D}importation de GNL (Mcf / Kpi3)"],
                           ["2022-12-01", 90000, 6.0, 90000], ["2023-01-01", 70000, 4.0, 70000]],
}


def workbook(sheets):
    buf = io.BytesIO()
    with pd.ExcelWriter(buf) as w:
        for name, rows in sheets.items():
            pd.DataFrame(rows).to_excel(w, sheet_name=name, header=False, index=False)
    return pd.ExcelFile(io.BytesIO(buf.getvalue()))


class Workbook(unittest.TestCase):
    def test_columns_units_and_the_import_cut(self):
        rows, late = G.sheet_rows(workbook(SHEETS), {"market": "", "source": "s", "source_url": "u", "retrieved_at": "r", "vintage": ""})
        t = pd.DataFrame(rows).set_index(["entity", "variable", "ts_utc"])
        self.assertEqual(t.loc[("cer_gas_trade:CA", "exports", "2023-01-01T00:00:00Z"), "value"], 310000)
        self.assertEqual(t.loc[("cer_gas_trade:CA", "exports", "2023-01-01T00:00:00Z"), "unit"], "Mcf")
        self.assertEqual(t.loc[("cer_gas_trade:CA:US_EAST", "exports", "2022-12-01T00:00:00Z"), "value"], 60000)
        self.assertEqual(t.loc[("cer_gas_trade:CA", "export_price", "2023-01-01T00:00:00Z"), "value"], 3.1)
        self.assertEqual(t.loc[("cer_gas_trade:CA", "imports", "2022-12-01T00:00:00Z"), "value"], 90000)
        self.assertNotIn(("cer_gas_trade:CA", "imports", "2023-01-01T00:00:00Z"), t.index)
        self.assertEqual(late, 2)
        self.assertEqual(len(t), 14)  # 2 + 6 + 2 exports, 2 export prices, 2 import rows of 2022; the CAD, m3 and LNG import columns none

    def test_a_heading_not_as_read_stops(self):
        bad = dict(SHEETS)
        bad["Fig. 2(m)"] = [["Date", "West / Ouest (Mcf / Kpi3)", "Midwest (Mcf / Kpi3)", "East (Mcf) / Est (Kpi3)"], ["2022-12-01", 1, 2, 3]]
        with self.assertRaises(RuntimeError):
            G.sheet_rows(workbook(bad), {})


class Registered(unittest.TestCase):
    def test_sector_and_holds(self):
        name = "cer_gas_trade"
        self.assertEqual(B.sector_of(name), "gas")
        self.assertIn(name, R.STORAGE_HELD)
        with open(os.path.join(ROOT, "warehouse", "supabase", "live_set.yaml"), encoding="utf-8") as f:
            self.assertIn(f"  - {name}\n", f.read().replace("\r\n", "\n"))


if __name__ == "__main__":
    unittest.main()

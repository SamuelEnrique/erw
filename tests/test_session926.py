"""Session 926: the World Bank's commodity prices (the Pink Sheet), energy and base metals.

Energy Research Warehouse (ERW). Tests warehouse/connectors/wb_pink_sheet.py on a sheet built here in the workbook's form
(figures made up for the test, not the World Bank's): the columns taken and their units, the note mark removed, the
sheet's "…" having no row, a column missing or a month not of the form 1960M01 stopping the run; the sector rule and the
holds. No network.

    python -m unittest tests.test_session926 -v
"""

import os
import sys
import unittest

import pandas as pd

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
sys.path.insert(0, os.path.join(ROOT, "warehouse", "connectors"))
sys.path.insert(0, os.path.join(ROOT, "warehouse", "metadata"))
sys.path.insert(0, os.path.join(ROOT, "warehouse", "redivis"))
import wb_pink_sheet as W  # noqa: E402
import build_coverage as B  # noqa: E402
import release_v1 as R  # noqa: E402

UNIT = {"Crude oil": "($/bbl)", "Coal": "($/mt)", "Natural": "($/mmbtu)", "Liquefied": "($/mmbtu)"}


def sheet(months=("2026M08", "2026M09")):
    names = [None] + [n + (" **" if n == "Coal, South African" else "") for n in W.TAKE] + ["Natural gas index", "Gold"]
    units = [None] + [next((u for k, u in UNIT.items() if n.startswith(k)), "($/mt)") for n in W.TAKE] + ["(2010=100)", "($/troy oz)"]
    rows = [["World Bank Commodity Price Data (The Pink Sheet)"] + [None] * (len(names) - 1), ["Updated on October 02, 2026"] + [None] * (len(names) - 1),
            names, units]
    for k, m in enumerate(months):
        rows.append([m] + [10.0 + k] * len(W.TAKE) + [100, 2000])
    rows[-1][1] = "…"
    return pd.DataFrame(rows)


class Sheet(unittest.TestCase):
    def test_columns_units_and_marks(self):
        out, starred = W.rows(sheet(), {"source": "s", "source_url": "u", "retrieved_at": "r", "vintage": ""})
        t = pd.DataFrame(out).set_index(["entity", "ts_utc"])
        self.assertEqual(t.loc[("wb_pink:crude_oil_brent", "2026-09-01T00:00:00Z"), "unit"], "USD/bbl")
        self.assertEqual(t.loc[("wb_pink:coal_south_african", "2026-08-01T00:00:00Z"), "node"], "Coal, South African")
        self.assertEqual(t.loc[("wb_pink:natural_gas_us", "2026-08-01T00:00:00Z"), "unit"], "USD/MMBtu")
        self.assertEqual(t.loc[("wb_pink:copper", "2026-08-01T00:00:00Z"), "unit"], "USD/t")
        self.assertNotIn(("wb_pink:crude_oil_average", "2026-09-01T00:00:00Z"), t.index)
        self.assertEqual(len(t), 2 * len(W.TAKE) - 1)
        self.assertEqual(starred, ["Coal, South African"])

    def test_stops(self):
        with self.assertRaises(RuntimeError):
            W.rows(sheet(months=("2026-09",)), {})
        bad = sheet()
        bad.iloc[2, 3] = "Crude oil, Somewhere"
        with self.assertRaises(RuntimeError):
            W.rows(bad, {})


class Registered(unittest.TestCase):
    def test_sector_and_holds(self):
        name = "wb_commodity_prices_monthly"
        self.assertEqual(B.sector_of(name), "oil;gas;coal;metals")
        self.assertIn(name, R.STORAGE_HELD)
        with open(os.path.join(ROOT, "warehouse", "supabase", "live_set.yaml"), encoding="utf-8") as f:
            self.assertIn(f"  - {name}\n", f.read().replace("\r\n", "\n"))


if __name__ == "__main__":
    unittest.main()

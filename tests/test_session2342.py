"""Session 2342 (from session 2339): EIA's API v2 route petroleum/stoc/st, petroleum product stocks at refineries, bulk
terminals and natural gas plants by state.

Energy Research Warehouse (ERW). Tests warehouse/connectors/eia_petroleum_stocks_state.py on rows built here in the
API's form (made up for the test, not EIA's): a state's, a PADD's and the U.S.'s rows, each in kbbl on the month's first
day with its area and product kept; geo US-<state> or US; a blank not written; a process, unit or area not understood
and a key given twice stopping the run; the sector rule and the holds. No network.

    python -m unittest tests.test_session2342 -v
"""

import copy
import os
import sys
import unittest

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
sys.path.insert(0, os.path.join(ROOT, "warehouse", "connectors"))
sys.path.insert(0, os.path.join(ROOT, "warehouse", "metadata"))
sys.path.insert(0, os.path.join(ROOT, "warehouse", "redivis"))
import eia_petroleum_stocks_state as S  # noqa: E402
import build_coverage as B  # noqa: E402
import release_v1 as R  # noqa: E402

ROW = {"period": "2026-07", "duoarea": "STX", "product": "EPD0", "process": "STR", "series": "M_EPD0_STR_STX_MBBL",
       "series-description": "Texas Distillate Fuel Oil Stocks at Refineries, Bulk Terminals, and Natural Gas Plants (Thousand Barrels)",
       "value": "12345", "units": "MBBL"}


def rows(**kw):
    r = dict(ROW)
    r.update(kw)
    return r


class Parse(unittest.TestCase):
    def test_rows(self):
        data = [rows(), rows(duoarea="R30", series="M_EPD0_STR_R30_MBBL"), rows(duoarea="NUS", series="M_EPD0_STR_NUS_MBBL"),
                rows(duoarea="SCA", series="M_EPD0_STR_SCA_MBBL", value=None)]
        t = S.rows(data, "u", "r").set_index("entity")
        self.assertEqual(len(t), 3)
        r = t.loc["eia_petroleum_stocks_state:M_EPD0_STR_STX_MBBL"]
        self.assertEqual((r.variable, r.ts_utc, r.value, r.unit, r.geo, r.x_area, r.x_product),
                         ("stocks_refineries_terminals_gas_plants", "2026-07-01T00:00:00Z", 12345.0, "kbbl", "US-TX", "STX", "EPD0"))
        self.assertEqual(t.loc["eia_petroleum_stocks_state:M_EPD0_STR_R30_MBBL"].geo, "US")
        self.assertEqual(t.loc["eia_petroleum_stocks_state:M_EPD0_STR_NUS_MBBL"].geo, "US")

    def test_stops(self):
        for bad in ([rows(process="SAE")], [rows(units="MMCF")], [rows(duoarea="Y35NY")], [rows(), rows()]):
            with self.assertRaises(RuntimeError):
                S.rows(copy.deepcopy(bad), "u", "r")


class Registered(unittest.TestCase):
    def test_sector_and_holds(self):
        self.assertEqual(B.sector_of(S.NAME), "products")
        self.assertIn(S.NAME, R.STORAGE_HELD)
        with open(os.path.join(ROOT, "warehouse", "supabase", "live_set.yaml"), encoding="utf-8") as f:
            self.assertIn(f"  - {S.NAME}\n", f.read().replace("\r\n", "\n"))


if __name__ == "__main__":
    unittest.main()

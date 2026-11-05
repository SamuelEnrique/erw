"""Session 528: EIA's natural gas production by state. Held on real records (January 2001, Pennsylvania and EIA's
"Other States"): the process names the variable, MMcf kept, a per-day series not taken, R98's geo is US; the table is
held from /data and Redivis v1 until uploaded.
"""

import os
import sys
import unittest

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
sys.path.insert(0, os.path.join(ROOT, "warehouse", "connectors"))
sys.path.insert(0, os.path.join(ROOT, "warehouse", "redivis"))
import eia_gas_production_state as P  # noqa: E402
import release_v1 as R  # noqa: E402


def rec(area, process, series, desc, value, units="MMCF"):
    return {"period": "2001-01", "duoarea": area, "process": process, "series": series, "series-description": desc, "value": value, "units": units}


REAL = [rec("R98", "FGW", "N9010982", "Other States Natural Gas Gross Withdrawals (MMcf)", "67526"),
        rec("SPA", "FGW", "N9010PA2", "Pennsylvania Natural Gas Gross Withdrawals (MMcf)", "11607"),
        rec("SPA", "VGV", "N9040PA2", "Pennsylvania Natural Gas Vented and Flared (MMcf)", "0")]


class TheRows(unittest.TestCase):
    def test_rows(self):
        t = P.rows(REAL, "u", "r").set_index("entity")
        r = t.loc["eia_gas_production:SPA:N9010PA"]
        self.assertEqual((r["variable"], r["value"], r["unit"]), ("gross_withdrawals", 11607.0, "MMcf"))
        self.assertEqual(t.loc["eia_gas_production:SPA:N9040PA", "variable"], "vented_flared")
        self.assertEqual(t.loc["eia_gas_production:R98:N901098", "geo"], "US")

    def test_a_per_day_series_is_not_taken(self):
        self.assertEqual(len(P.rows([rec("SPA", "FGW", "N9010PA3", "per day", "380", "MMCF/D")], "u", "r")), 0)

    def test_held_until_uploaded(self):
        with open(os.path.join(ROOT, "warehouse", "supabase", "live_set.yaml"), encoding="utf-8") as h:
            y = h.read()
        self.assertIn("  - eia_gas_production_state_monthly\n", y[y.index("catalogue_hold:"):])
        self.assertIn("upload.py eia_gas_production_state_monthly", R.STORAGE_HELD["eia_gas_production_state_monthly"])

    def test_no_em_dash(self):
        for f in ("warehouse/connectors/eia_gas_production_state.py", "tests/test_session528.py"):
            with open(os.path.join(ROOT, *f.split("/")), encoding="utf-8") as h:
                self.assertNotIn(chr(0x2014), h.read(), f)


if __name__ == "__main__":
    unittest.main()

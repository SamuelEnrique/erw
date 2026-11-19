"""Sessions 8207 to 8213 (chain 502): the forecasts family and part D's modules of the findings hunt.

Energy Research Warehouse (ERW). No warehouse file, no network, no database.
"""

import os
import sys
import unittest

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
sys.path.insert(0, os.path.join(ROOT, "warehouse", "analysis", "findings"))
sys.path.insert(0, os.path.join(ROOT, "warehouse", "analysis", "findings", "deep"))
import check_do  # noqa: E402
import cross502  # noqa: E402
import ferc714  # noqa: E402
import ops502  # noqa: E402
import partd  # noqa: E402
import seds502  # noqa: E402
import utilities861  # noqa: E402


def holds(do):
    return [p for p in check_do.problems("* Expected: x\n\n" + do, "# Expected: x\n") if "expected" not in p]


class Generators(unittest.TestCase):
    def test_every_do_file_holds(self):
        files = [ferc714.reproduce("energy_growth")("pa_58")["do"], partd.reproduce("ghg_power_state")("ghgpp_il")["do"], partd.reproduce("coal_basin_share")("cb_illinois_basin")["do"],
                 partd.reproduce("gas_net_receipts")("gn_pa")["do"], utilities861.reproduce("util_commercial")("u861_19876_va")["do"],
                 utilities861.reproduce("util_commercial_price")("u861_19547_hi")["do"], cross502.reproduce("peak_vs_5y")("xp5_pjm")["do"],
                 cross502.reproduce("energy_vs_3y")("xe3_ciso")["do"], ops502.reproduce("nuc_out_share")("nucf_6008")["do"], ops502.reproduce("coal_stocks_dec")("cst_us")["do"],
                 seds502.reproduce("seds_renew_share")("sd_us")["do"], seds502.reproduce("seds_price_ind")("sd_ca")["do"]]
        for do in files:
            self.assertEqual(holds(do), [])

    def test_the_rules_that_keep_a_draft_honest(self):
        self.assertIn("CA", utilities861.CHOICE)
        self.assertEqual(ferc714.NEWEST, 2024)
        self.assertEqual(ops502.NEWEST, 2024)
        self.assertIn("nucf_6152", ops502.SKIP)
        self.assertIn(("seds_elec_comm", "sd_tx"), seds502.SKIP)
        self.assertAlmostEqual(seds502.SERIES["seds_price_ind"][1] * 3.412, 1.0)
        self.assertEqual(seds502.SERIES["seds_elec_spend"][1], 1e9)
        self.assertEqual(cross502.MAP["PJM"], "119")

    def test_a_python_script_names_its_tables(self):
        py = cross502.reproduce("peak_vs_5y")("xp5_pjm")["py"]
        self.assertIn("<eia930_ba_demand_hourly.csv> <ferc714_planning_area_forecasts.csv>", py)
        self.assertIn("0.5 <= act[y] / fc[y] <= 2.0", py)


if __name__ == "__main__":
    unittest.main()

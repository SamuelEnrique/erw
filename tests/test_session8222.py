"""Sessions 8214 to 8222 (chain 502): part D's second round of the findings hunt.

Energy Research Warehouse (ERW). No warehouse file, no network, no database.
"""

import os
import sys
import unittest

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
sys.path.insert(0, os.path.join(ROOT, "warehouse", "analysis", "findings"))
sys.path.insert(0, os.path.join(ROOT, "warehouse", "analysis", "findings", "deep"))
import authorities  # noqa: E402
import check_do  # noqa: E402
import ferc714  # noqa: E402
import gas502  # noqa: E402
import misc502  # noqa: E402
import oilx502  # noqa: E402
import weather  # noqa: E402
import worldco2  # noqa: E402
import worldcoal  # noqa: E402


def holds(do):
    return [p for p in check_do.problems("* Expected: x\n\n" + do, "# Expected: x\n") if "expected" not in p]


class Generators(unittest.TestCase):
    def test_every_do_file_holds(self):
        files = [worldcoal.reproduce("wc_consumption")("wc_usa")["do"], worldco2.reproduce("co2_coal")("co2_worl")["do"], gas502.reproduce("s2s_out")("s2out_pennsylvania")["do"],
                 oilx502.reproduce("exp_crude_dest")("xc_nnl")["do"], oilx502.reproduce("exp_product")("xp_epc0")["do"], misc502.reproduce("quakes_m3")("eq_new_mexico")["do"],
                 misc502.reproduce("reactor_power")("rp_us")["do"], weather.reproduce("cdd")("wd_tex")["do"], authorities.reproduce("ba_top_winter")("ba_nwmt")["do"],
                 authorities.reproduce("ba_load_factor")("ba_erco")["do"], ferc714.reproduce("summer_revision")("pa_146")["do"]]
        for do in files:
            self.assertEqual(holds(do), [])

    def test_the_rules_that_keep_a_draft_honest(self):
        self.assertEqual(worldco2.FIRST, 1980)
        self.assertEqual(weather.BASE_F, 65.0)
        self.assertEqual(ferc714.AHEAD, 5)
        self.assertIn("first_words", next(P for P in oilx502.CANDIDATES if P["name"] == "exp_crude_dest"))
        self.assertNotIn("gas_res_customers", [P["name"] for P in gas502.CANDIDATES])
        self.assertIn("1980", worldco2.reproduce_py("co2_total", "co2_usa"))


if __name__ == "__main__":
    unittest.main()

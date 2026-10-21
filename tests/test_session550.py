"""Session 550: EIA's interstate and international natural gas movements by state, a year. Held on real records: the
pair stays in the entity and the first area gives the geo; Louisiana's 2016 net receipts from the United Arab Emirates,
which EIA gives under two series ids with one value, are kept once; the same key with two values stops the run; the table
is held from /data and Redivis v1 until uploaded.
"""

import os
import sys
import unittest

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
sys.path.insert(0, os.path.join(ROOT, "warehouse", "connectors"))
sys.path.insert(0, os.path.join(ROOT, "warehouse", "redivis"))
import eia_gas_interstate as G  # noqa: E402
import release_v1 as R  # noqa: E402

UAE = {"period": "2016", "duoarea": "SLA-NTC", "process": "IMB", "series": "NA1290_SLA-NTC_2",
       "series-description": "Louisiana Natural Gas Net International Receipts from United Arab Emirates (Million Cubic Feet)", "value": "-3391", "units": "MMCF"}
TWIN = dict(UAE, series="NGM_EPG0_IMB_SLA-NTC_MMCF")
TX = {"period": "2024", "duoarea": "STX-Z0R", "process": "MIE", "series": "x",
      "series-description": "Texas Natural Gas Net International & Interstate Receipts (MMcf)", "value": "-6498093", "units": "MMCF"}


class TheRows(unittest.TestCase):
    def test_a_pair_and_its_geo(self):
        r = G.rows([TX], "u", "r").iloc[0]
        self.assertEqual((r["entity"], r["variable"], r["value"], r["unit"], r["geo"]),
                         ("eia_gas_interstate:MIE:STX-Z0R", "net_receipts_imports", -6498093.0, "MMcf", "US-TX"))
        self.assertEqual(G.geo_of("R3FM-SLA"), "US")

    def test_a_twin_with_one_value_is_kept_once(self):
        self.assertEqual(len(G.rows([UAE, TWIN], "u", "r")), 1)

    def test_a_twin_with_two_values_stops(self):
        with self.assertRaises(RuntimeError):
            G.rows([UAE, dict(TWIN, value="-3000")], "u", "r")

    def test_held_until_uploaded(self):
        with open(os.path.join(ROOT, "warehouse", "supabase", "live_set.yaml"), encoding="utf-8") as h:
            y = h.read()
        self.assertIn("  - eia_gas_interstate_annual\n", y[y.index("catalogue_hold:"):])
        self.assertIn("upload.py eia_gas_interstate_annual", R.STORAGE_HELD["eia_gas_interstate_annual"])

    def test_no_em_dash(self):
        for f in ("warehouse/connectors/eia_gas_interstate.py", "tests/test_session550.py"):
            with open(os.path.join(ROOT, *f.split("/")), encoding="utf-8") as h:
                self.assertNotIn(chr(0x2014), h.read(), f)


if __name__ == "__main__":
    unittest.main()

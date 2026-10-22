"""Session 631: EIA's oxygenate plant production. Held on a real record's form (U.S. oxygenate plant production of fuel
ethanol, January 2026; Gulf Coast biofuels plant net production of other oxygenates): kbbl and kbbl/d kept, both
processes named, a refining district or an unknown process stops; the table is held from /data and Redivis v1 until
uploaded.
"""

import os
import sys
import unittest

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
sys.path.insert(0, os.path.join(ROOT, "warehouse", "connectors"))
sys.path.insert(0, os.path.join(ROOT, "warehouse", "redivis"))
import eia_oxygenate_production as O  # noqa: E402
import release_v1 as R  # noqa: E402

ETH = {"period": "2026-01", "duoarea": "NUS", "product": "EPOOXE", "process": "YOP", "series": "M_EPOOXE_YOP_NUS_1",
       "series-description": "U.S. Oxygenate Plant Production of Fuel Ethanol (Thousand Barrels)", "value": "32000", "units": "MBBL"}
OTH = {"period": "2026-01", "duoarea": "R30", "product": "EPOOXO", "process": "YNP", "series": "M_EPOOXO_YNP_R30_MBBLD",
       "series-description": "Gulf Coast (PADD 3) Biofuels Plant Net Production of Other Oxygenates (Thousand Barrels per Day)",
       "value": "10", "units": "MBBL/D"}


class TheRows(unittest.TestCase):
    def test_both_processes(self):
        t = O.rows([ETH, OTH], "u", "r")
        self.assertEqual(list(t["variable"]), ["oxygenate_plant_production", "biofuels_plant_net_production_per_day"])
        self.assertEqual(list(t["unit"]), ["kbbl", "kbbl/d"])
        self.assertEqual(t.iloc[0]["entity"], "eia_oxygenate_production:M_EPOOXE_YOP_NUS_1")

    def test_a_district_or_unknown_process_stops(self):
        for bad in (dict(ETH, duoarea="R3A"), dict(ETH, process="YPR")):
            with self.assertRaises(RuntimeError):
                O.rows([bad], "u", "r")

    def test_held_until_uploaded(self):
        with open(os.path.join(ROOT, "warehouse", "supabase", "live_set.yaml"), encoding="utf-8") as h:
            y = h.read()
        self.assertIn("  - eia_oxygenate_production_monthly\n", y[y.index("catalogue_hold:"):])
        self.assertIn("upload.py eia_oxygenate_production_monthly", R.STORAGE_HELD["eia_oxygenate_production_monthly"])

    def test_no_em_dash(self):
        for f in ("warehouse/connectors/eia_oxygenate_production.py", "tests/test_session631.py"):
            with open(os.path.join(ROOT, *f.split("/")), encoding="utf-8") as h:
                self.assertNotIn(chr(0x2014), h.read(), f)


if __name__ == "__main__":
    unittest.main()

"""Session 499: the landing of chain 022's tables, and what it needed.

Energy Research Warehouse (ERW). The daily recompute of the Research cards (session 361) committed its first run on
21 October 2026 (c8aa37ff) and moved numbers that tests a landing must pass hold; the cards were put back, and the data
machine's run now tests the cards after the recompute and puts them back when a test fails. The nine public tables of
sessions 485 to 497 are held from /data's catalogue and from Redivis v1 until they are uploaded (a person's).
"""

import os
import sys
import unittest

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
sys.path.insert(0, os.path.join(ROOT, "warehouse", "redivis"))
import release_v1 as R  # noqa: E402

NEW = ("boem_renewable_leases", "egrid_power_plants", "eia861_utility_sales", "eia_aeo_electricity",
       "eia_seds_state_energy", "eia_steo_forecasts", "epa_ghgrp_power_co2", "nlr_atb_electricity_costs",
       "uswtdb_wind_turbines")


def src(*parts):
    with open(os.path.join(ROOT, *parts), encoding="utf-8") as f:
        return f.read()


class TheCardsAreTestedAfterTheRecompute(unittest.TestCase):
    def test_the_step_runs_after_the_recompute_and_puts_the_cards_back(self):
        s = src("warehouse", "run_data_machine.sh")
        step = "PYTHONPATH=tests soft_step dm_test_findings"
        self.assertLess(s.index("soft_step dm_findings_recompute"), s.index(step))
        self.assertLess(s.index(step), s.index("put_back dm_test_findings site/data/findings site/public/findings"))

    def test_every_test_it_names_exists(self):
        s = src("warehouse", "run_data_machine.sh")
        line = next(ln for ln in s.splitlines() if "soft_step dm_test_findings" in ln)
        names = [w for w in line.split() if w.startswith("test_session")]
        self.assertEqual(len(names), 5)
        for n in names:
            self.assertTrue(os.path.exists(os.path.join(ROOT, "tests", n + ".py")), n)


class TheNewTablesAreHeld(unittest.TestCase):
    def test_held_from_the_catalogue(self):
        y = src("warehouse", "supabase", "live_set.yaml")
        hold = y[y.index("catalogue_hold"):]
        for t in NEW:
            self.assertIn(f"  - {t}\n", hold, t)

    def test_held_from_v1_until_uploaded(self):
        for t in NEW:
            self.assertIn(t, R.STORAGE_HELD)
            self.assertIn(f"upload.py {t}", R.STORAGE_HELD[t])
        self.assertEqual(R.check(), [])

    def test_no_em_dash(self):
        for f in ("tests/test_session499.py", "warehouse/run_data_machine.sh", "warehouse/redivis/release_v1.py"):
            self.assertNotIn(chr(0x2014), src(*f.split("/")), f)


if __name__ == "__main__":
    unittest.main()

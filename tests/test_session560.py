"""Session 560: EIA's energy efficiency programs by state and sector, a year. Held on a real record (Alaska, commercial,
2023, the programs' expected life cycle): EIA's time period as a slug in the entity, MWh and MW kept, thousand dollars as
USD, an unknown unit stops; the table is held from /data and Redivis v1 until uploaded.
"""

import os
import sys
import unittest

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
sys.path.insert(0, os.path.join(ROOT, "warehouse", "connectors"))
sys.path.insert(0, os.path.join(ROOT, "warehouse", "redivis"))
import eia_energy_efficiency as E  # noqa: E402
import release_v1 as R  # noqa: E402

REAL = {"period": "2023", "state": "AK", "stateName": "Alaska", "timePeriod": "Expected Life Cycle of Programs", "sector": "COM", "sectorName": "commercial",
        "energy-savings": "1200", "potential-peak-savings": "0.4", "customer-incentive": "35", "all-other-costs": "12",
        "energy-savings-units": "megawatthours", "potential-peak-savings-units": "megawatts", "customer-incentive-units": "thousand dollars",
        "all-other-costs-units": "thousand dollars"}


class TheRows(unittest.TestCase):
    def test_rows(self):
        t = E.rows([REAL], "u", "r").set_index("variable")
        self.assertEqual(set(t["entity"]), {"eia_efficiency:AK:expected_life_cycle_of_programs:COM"})
        self.assertEqual((t.loc["energy_savings", "value"], t.loc["energy_savings", "unit"]), (1200.0, "MWh"))
        self.assertEqual(t.loc["potential_peak_savings", "unit"], "MW")
        self.assertEqual((t.loc["customer_incentive", "value"], t.loc["customer_incentive", "unit"]), (35000.0, "USD"))

    def test_an_unknown_unit_stops(self):
        with self.assertRaises(RuntimeError):
            E.rows([dict(REAL, **{"all-other-costs-units": "dollars"})], "u", "r")

    def test_held_until_uploaded(self):
        with open(os.path.join(ROOT, "warehouse", "supabase", "live_set.yaml"), encoding="utf-8") as h:
            y = h.read()
        self.assertIn("  - eia_energy_efficiency_state_annual\n", y[y.index("catalogue_hold:"):])
        self.assertIn("upload.py eia_energy_efficiency_state_annual", R.STORAGE_HELD["eia_energy_efficiency_state_annual"])

    def test_no_em_dash(self):
        for f in ("warehouse/connectors/eia_energy_efficiency.py", "tests/test_session560.py"):
            with open(os.path.join(ROOT, *f.split("/")), encoding="utf-8") as h:
                self.assertNotIn(chr(0x2014), h.read(), f)


if __name__ == "__main__":
    unittest.main()

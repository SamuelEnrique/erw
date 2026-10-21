"""Session 530: EIA's energy-related CO2 by state, sector and fuel. Held on a real record (Alaska, commercial coal,
2022): million metric tons as tCO2, the entity's three codes, an unknown unit stops; the table is held from /data and
Redivis v1 until uploaded.
"""

import os
import sys
import unittest

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
sys.path.insert(0, os.path.join(ROOT, "warehouse", "connectors"))
sys.path.insert(0, os.path.join(ROOT, "warehouse", "redivis"))
import eia_co2_state as C  # noqa: E402
import release_v1 as R  # noqa: E402

REAL = {"period": "2022", "sectorId": "CC", "sector-name": "Commercial carbon dioxide emissions", "fuelId": "CO", "fuel-name": "Coal",
        "stateId": "AK", "state-name": "Alaska", "value": ".700224", "value-units": "million metric tons of CO2"}


class TheRows(unittest.TestCase):
    def test_a_row(self):
        r = C.rows([REAL], "u", "r").iloc[0]
        self.assertEqual((r["entity"], r["variable"], r["unit"], r["geo"], r["ts_utc"]), ("eia_co2:AK:CC:CO", "co2", "tCO2", "US-AK", "2022-01-01T00:00:00Z"))
        self.assertAlmostEqual(r["value"], 700224.0)

    def test_an_unknown_unit_stops(self):
        with self.assertRaises(RuntimeError):
            C.rows([dict(REAL, **{"value-units": "short tons"})], "u", "r")

    def test_held_until_uploaded(self):
        with open(os.path.join(ROOT, "warehouse", "supabase", "live_set.yaml"), encoding="utf-8") as h:
            y = h.read()
        self.assertIn("  - eia_co2_state_annual\n", y[y.index("catalogue_hold:"):])
        self.assertIn("upload.py eia_co2_state_annual", R.STORAGE_HELD["eia_co2_state_annual"])

    def test_no_em_dash(self):
        for f in ("warehouse/connectors/eia_co2_state.py", "tests/test_session530.py"):
            with open(os.path.join(ROOT, *f.split("/")), encoding="utf-8") as h:
                self.assertNotIn(chr(0x2014), h.read(), f)


if __name__ == "__main__":
    unittest.main()

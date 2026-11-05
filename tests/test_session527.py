"""Session 527: EIA's crude oil field production by state. Held on real records (Alaska, January 2001): the state and
its North Slope are two entities under one area, thousand barrels and thousand barrels a day are two variables, an area
not in the map stops; the table is held from /data and Redivis v1 until uploaded.
"""

import os
import sys
import unittest

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
sys.path.insert(0, os.path.join(ROOT, "warehouse", "connectors"))
sys.path.insert(0, os.path.join(ROOT, "warehouse", "redivis"))
import eia_crude_production_state as P  # noqa: E402
import release_v1 as R  # noqa: E402


def rec(series, desc, value, units):
    return {"period": "2001-01", "duoarea": "SAK", "process": "FPF", "series": series, "series-description": desc, "value": value, "units": units}


REAL = [rec("MANFPAK1", "Alaska North Slope Crude Oil Production (Thousand Barrels)", "29515", "MBBL"),
        rec("MANFPAK2", "Alaska North Slope Crude Oil Production (Thousand Barrels per Day)", "952", "MBBL/D"),
        rec("MCRFPAK1", "Alaska Field Production of Crude Oil (Thousand Barrels)", "30384", "MBBL"),
        rec("MCRFPAK2", "Alaska Field Production of Crude Oil (Thousand Barrels per Day)", "980", "MBBL/D")]


class TheRows(unittest.TestCase):
    def test_rows(self):
        t = P.rows(REAL, "u", "r").set_index(["entity", "variable"])
        self.assertEqual(len(t), 4)
        self.assertEqual(t.loc[("eia_crude_production:SAK:MCRFPAK", "field_production"), "value"], 30384.0)
        self.assertEqual(t.loc[("eia_crude_production:SAK:MCRFPAK", "field_production_per_day"), "unit"], "kbbl/d")
        self.assertEqual(t.loc[("eia_crude_production:SAK:MANFPAK", "field_production"), "unit"], "kbbl")

    def test_an_area_not_in_the_map_stops(self):
        with self.assertRaises(RuntimeError):
            P.rows([dict(REAL[0], duoarea="R99")], "u", "r")

    def test_held_until_uploaded(self):
        with open(os.path.join(ROOT, "warehouse", "supabase", "live_set.yaml"), encoding="utf-8") as h:
            y = h.read()
        self.assertIn("  - eia_crude_production_state_monthly\n", y[y.index("catalogue_hold:"):])
        self.assertIn("upload.py eia_crude_production_state_monthly", R.STORAGE_HELD["eia_crude_production_state_monthly"])

    def test_no_em_dash(self):
        for f in ("warehouse/connectors/eia_crude_production_state.py", "tests/test_session527.py"):
            with open(os.path.join(ROOT, *f.split("/")), encoding="utf-8") as h:
                self.assertNotIn(chr(0x2014), h.read(), f)


if __name__ == "__main__":
    unittest.main()

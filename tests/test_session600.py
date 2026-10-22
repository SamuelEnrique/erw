"""Sessions 600, 603 and 604: petroleum supply and disposition's third group of products; EIA's drilling activity; EIA's
producing natural gas wells by state. Held on records of EIA's API: the third group's ten products, rig counts as counts
with the areas EIA gives, gas wells by state; the tables are held from /data and Redivis v1 until uploaded.
"""

import os
import sys
import unittest

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
sys.path.insert(0, os.path.join(ROOT, "warehouse", "connectors"))
sys.path.insert(0, os.path.join(ROOT, "warehouse", "redivis"))
import eia_drilling as D  # noqa: E402
import eia_gas_wells as G  # noqa: E402
import eia_petroleum_snd as P  # noqa: E402
import release_v1 as R  # noqa: E402

RIGS = {"period": "2026-02", "duoarea": "RUSON", "product": "EPC0", "process": "XR0", "series": "E_ERTRR0_XR0_RUSON_C",
        "series-description": "U.S. Onshore Crude Oil and Natural Gas Rotary Rigs in Operation (Count)", "value": "530", "units": "COUNT"}
WELLS = {"period": "2020", "duoarea": "SPA", "process": "XDG", "series": "NGM_EPG0_XDG_SPA_COUNT",
         "series-description": "Pennsylvania Number of Gas and Gas Condensate Wells (Count)", "value": "71000", "units": "COUNT"}


class TheTables(unittest.TestCase):
    def test_the_third_and_fourth_groups(self):
        # session 601 added the fourth group (17 products); the third stays as session 600 read it
        self.assertEqual(len(P.GROUPS[2]), 10)
        self.assertIn("EPL0", P.GROUPS[2])
        self.assertEqual(len(P.GROUPS[3]), 17)
        # session 610 added the fifth, the last eleven
        self.assertEqual(len(P.GROUPS[4]), 11)
        self.assertIn("EPPS", P.GROUPS[4])
        self.assertEqual(len(set(P.PRODUCTS)), len(P.PRODUCTS))

    def test_rigs(self):
        r = D.rows([RIGS], "u", "r").iloc[0]
        self.assertEqual((r["entity"], r["variable"], r["value"], r["unit"], r["ts_utc"]),
                         ("eia_drilling:E_ERTRR0_XR0_RUSON_C", "rotary_rigs", 530.0, "count", "2026-02-01T00:00:00Z"))
        with self.assertRaises(RuntimeError):
            D.rows([dict(RIGS, duoarea="STX")], "u", "r")

    def test_wells(self):
        r = G.rows([WELLS], "u", "r").iloc[0]
        self.assertEqual((r["entity"], r["variable"], r["value"], r["unit"], r["geo"]), ("eia_gas_wells:XDG:SPA", "gas_wells", 71000.0, "count", "US-PA"))

    def test_held_until_uploaded(self):
        with open(os.path.join(ROOT, "warehouse", "supabase", "live_set.yaml"), encoding="utf-8") as h:
            y = h.read()
        for t in ("eia_drilling_monthly", "eia_gas_wells_annual"):
            self.assertIn(f"  - {t}\n", y[y.index("catalogue_hold:"):])
            self.assertIn(f"upload.py {t}", R.STORAGE_HELD[t])

    def test_no_em_dash(self):
        for f in ("eia_drilling.py", "eia_gas_wells.py", "eia_petroleum_snd.py"):
            with open(os.path.join(ROOT, "warehouse", "connectors", f), encoding="utf-8") as h:
                self.assertNotIn(chr(0x2014), h.read(), f)


if __name__ == "__main__":
    unittest.main()

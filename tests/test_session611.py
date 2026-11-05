"""Session 611: BOEM's offshore production by lease, from OGOR-A well production. Held on real lines of BOEM's 2024 file
(lease 00019's completion G011, January 2024, two producing intervals; a unit agreement's completion with no lease): the
intervals summed, barrels and thousand cubic feet to kbbl and MMcf, a unit's row under its unit agreement, a line given
twice or of another year stops; the table is held from /data and Redivis v1 until uploaded.
"""

import os
import sys
import unittest

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
sys.path.insert(0, os.path.join(ROOT, "warehouse", "connectors"))
sys.path.insert(0, os.path.join(ROOT, "warehouse", "redivis"))
import boem_ogor as B  # noqa: E402
import release_v1 as R  # noqa: E402

LINES = [
    '" 00019"," G011","202401","29","G","000000000","000000018","000015974","177154051401","11","ST   54","03151","COX OPERATING LLC","ST054","000000000","D01","20130620","891003444","0"',
    '" 00019"," G011","202401","01","G","000000000","000000100","000000318","177154051401","11","ST   54","03151","COX OPERATING LLC","ST054","000000000","D02","20130622","891003444","0"',
    '""," B004","202403","00","G","000000000","000000000","000000000","177064074801","14","VR  371","03672","TALOS QN EXPLORATION LLC","VR370","000000000","X01","","754393006","0"',
]


class TheRows(unittest.TestCase):
    def table(self, lines, year=2024):
        return B.rows(B.records("\n".join(lines) + "\n", year), "u", "r", "v")

    def test_intervals_summed(self):
        s = self.table(LINES[:2])
        gas = s[s["variable"] == "gas_production"].iloc[0]
        self.assertEqual((gas["entity"], gas["ts_utc"], gas["value"], gas["unit"], gas["node"]),
                         ("boem_lease:00019", "2024-01-01T00:00:00Z", 0.118, "MMcf", "COX OPERATING LLC"))
        oil = s[s["variable"] == "oil_production"].iloc[0]
        self.assertEqual((oil["value"], oil["unit"], oil["freq"], oil["geo"]), (0.0, "kbbl", "P1M", "US"))

    def test_a_unit_without_a_lease(self):
        s = self.table(LINES[2:])
        self.assertEqual(set(s["entity"]), {"boem_unit:754393006"})

    def test_twice_or_another_year_stops(self):
        # session 619: a line repeated in every field is kept once and counted; the same key with another value stops
        d = B.records("\n".join([LINES[0], LINES[0]]) + "\n", 2024)
        self.assertEqual((len(d), d.attrs["repeated"]), (1, 1))
        with self.assertRaises(RuntimeError):
            self.table([LINES[0], LINES[0].replace('"000000018"', '"000000019"')])
        with self.assertRaises(RuntimeError):
            self.table(LINES[:1], year=2025)

    def test_held_until_uploaded(self):
        with open(os.path.join(ROOT, "warehouse", "supabase", "live_set.yaml"), encoding="utf-8") as h:
            y = h.read()
        self.assertIn("  - boem_ogor_lease_production_monthly\n", y[y.index("catalogue_hold:"):])
        self.assertIn("upload.py boem_ogor_lease_production_monthly", R.STORAGE_HELD["boem_ogor_lease_production_monthly"])

    def test_no_em_dash(self):
        for f in ("warehouse/connectors/boem_ogor.py", "tests/test_session611.py"):
            with open(os.path.join(ROOT, *f.split("/")), encoding="utf-8") as h:
                self.assertNotIn(chr(0x2014), h.read(), f)


if __name__ == "__main__":
    unittest.main()

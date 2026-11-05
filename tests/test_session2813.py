"""Session 2813: Eurostat's road_if_rchevpow, European EV recharging points by power category a year.

Energy Research Warehouse (ERW). Tests warehouse/connectors/eurostat_ev_recharging_power.py on a file built here (made up for
the test, not Eurostat's): counts written per power band, EL written GR, the United Kingdom left out, a zero kept, a blank given
no row, the flag i kept; the total against AC plus DC and each current against its bands, a case off counted; a unit not NR, a
power code not expected, a value not a number, a negative value and a key given twice stopping the run; the sector rule and the
holds. No network.

    python -m unittest tests.test_session2813 -v
"""

import os
import sys
import unittest

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
sys.path.insert(0, os.path.join(ROOT, "warehouse", "connectors"))
sys.path.insert(0, os.path.join(ROOT, "warehouse", "metadata"))
sys.path.insert(0, os.path.join(ROOT, "warehouse", "redivis"))
import eurostat_ev_recharging_power as A  # noqa: E402
import build_coverage as B  # noqa: E402
import release_v1 as R  # noqa: E402

HEAD = ",".join(A.HEADER)


def line(power, geo, value, unit="NR", flag=""):
    return f"ESTAT:ROAD_IF_RCHEVPOW(1.0),13/10/26 23:00:00,A,{power},{geo},{unit},2025,{value},{flag},"


def data(total="209513", unit="NR", power="DC_KW_GE350", value="684", twice=False):
    lines = [HEAD, line("TOTAL", "NL", total, unit), line("AC", "NL", "202611"), line("DC", "NL", "6902"),
             line("AC_KW_LT7P4", "NL", "2008"), line("AC_KW_LE7P4-LE22", "NL", "200189"), line("AC_KW_GT22", "NL", "414"),
             line("DC_KW_LT50", "NL", "368"), line("DC_KW_LE50-LT150", "NL", "1716"), line("DC_KW_LE150-LT350", "NL", "4134"),
             line(power, "NL", value), line("TOTAL", "EL", "0", flag="i"), line("TOTAL", "BE", ""), line("TOTAL", "UK", "5")]
    if twice:
        lines.append(lines[1])
    return (chr(10).join(lines) + chr(10)).encode("utf-8")


class Parse(unittest.TestCase):
    def test_rows(self):
        t, counts = A.build(data(), "u", "r", "v")
        self.assertEqual(len(t), 11)                                         # the Netherlands' ten, Greece's zero
        self.assertEqual((counts["left_out_geo"], counts["zero"], counts["blank"]), (["UK"], 1, 1))
        x = t[t.entity == "eurostat_ev_power:NL:DC_KW_GE350"]
        self.assertEqual((x.value.iloc[0], x.unit.iloc[0], x.node.iloc[0]),
                         (684.0, "count", "NL recharging points, DC 350 kW and above (ultra-fast, level 2)"))
        self.assertEqual(t[t.x_geo_code == "EL"].x_flag.iloc[0], "i")
        self.assertEqual(set(t.geo), {"NL", "GR"})
        ck = A.checks(t)
        self.assertEqual((ck["total"], ck["ac"], ck["dc"]), ((1, []), (1, []), (1, [])))

    def test_counted(self):
        t, _ = A.build(data(total="209000"), "u", "r", "v")
        self.assertEqual(A.checks(t)["total"], (1, [("NL", "2025", 513.0)]))

    def test_stops(self):
        for content in (data(unit="KW"), data(power="DC_KW_GE1000"), data(value="n.a."), data(value="-1"), data(twice=True)):
            with self.assertRaises(RuntimeError):
                A.build(content, "u", "r", "v")


class Registered(unittest.TestCase):
    def test_sector_and_holds(self):
        self.assertEqual(B.sector_of(A.NAME), "power")
        self.assertIn(A.NAME, R.STORAGE_HELD)
        self.assertTrue(all(s.isascii() for s in A.BANDS.values()))
        with open(os.path.join(ROOT, "warehouse", "supabase", "live_set.yaml"), encoding="utf-8") as f:
            self.assertIn(f"  - {A.NAME}" + chr(10), f.read().replace(chr(13) + chr(10), chr(10)))


if __name__ == "__main__":
    unittest.main()

"""Session 2820: Eurostat's nrg_pc_205_v, non-household electricity by consumption band a year.

Energy Research Warehouse (ERW). Tests warehouse/connectors/eurostat_nonhousehold_bands.py on a file built here (made up for the
test, not Eurostat's): the shares written in pct, EL written GR and EU27_2020 given no geo, Kosovo left out, a blank given no
row, a zero kept; the seven bands compared with 100, a case off counted; a unit not PC, a band not expected, a value not a
number, a share above 100 and a key given twice stopping the run; the sector rule and the holds. No network.

    python -m unittest tests.test_session2820 -v
"""

import os
import sys
import unittest

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
sys.path.insert(0, os.path.join(ROOT, "warehouse", "connectors"))
sys.path.insert(0, os.path.join(ROOT, "warehouse", "metadata"))
sys.path.insert(0, os.path.join(ROOT, "warehouse", "redivis"))
import eurostat_nonhousehold_bands as A  # noqa: E402
import build_coverage as B  # noqa: E402
import release_v1 as R  # noqa: E402

HEAD = ",".join(A.HEADER)
SHARES = {"MWH_LT20": "10", "MWH20-499": "20", "MWH500-1999": "15", "MWH2000-19999": "20", "MWH20000-69999": "15",
          "MWH70000-149999": "5", "MWH_GE150000": "15"}


def line(band, geo, value, unit="PC"):
    return f"ESTAT:NRG_PC_205_V(1.0),16/10/26 11:00:00,A,{band},E7000,{unit},{geo},2024,{value},,"


def data(unit="PC", band="MWH_GE150000", value="15", twice=False):
    lines = [HEAD] + [line(band if k == "MWH_GE150000" else k, "DE", value if k == "MWH_GE150000" else v, unit) for k, v in SHARES.items()]
    lines += [line("MWH_LT20", "EL", "0"), line("MWH20-499", "EU27_2020", "25"), line("MWH_LT20", "AT", ""), line("MWH_LT20", "XK", "50")]
    if twice:
        lines.append(lines[1])
    return (chr(10).join(lines) + chr(10)).encode("utf-8")


class Parse(unittest.TestCase):
    def test_rows(self):
        t, counts = A.build(data(), "u", "r", "v")
        self.assertEqual(len(t), 7 + 2)
        self.assertEqual((counts["left_out_geo"], counts["zero"], counts["blank"]), (["XK"], 1, 1))
        self.assertEqual(set(t.geo), {"DE", "GR", ""})
        x = t[t.entity == "eurostat_nonhh_bands:DE:MWH_GE150000"]
        self.assertEqual((x.value.iloc[0], x.unit.iloc[0], x.node.iloc[0]),
                         (15.0, "pct", "DE non-household electricity, band IG, 150,000 MWh or over"))
        self.assertEqual(A.checks(t), (1, []))

    def test_counted(self):
        t, _ = A.build(data(value="17"), "u", "r", "v")
        self.assertEqual(A.checks(t), (1, [("DE", "2024", 102.0)]))

    def test_stops(self):
        for content in (data(unit="GWH"), data(band="MWH_LE149999"), data(value="n.a."), data(value="100.5"), data(twice=True)):
            with self.assertRaises(RuntimeError):
                A.build(content, "u", "r", "v")


class Registered(unittest.TestCase):
    def test_sector_and_holds(self):
        self.assertEqual(B.sector_of(A.NAME), "power")
        self.assertIn(A.NAME, R.STORAGE_HELD)
        self.assertLessEqual(len(A.NAME), 40)
        with open(os.path.join(ROOT, "warehouse", "supabase", "live_set.yaml"), encoding="utf-8") as f:
            self.assertIn(f"  - {A.NAME}" + chr(10), f.read().replace(chr(13) + chr(10), chr(10)))


if __name__ == "__main__":
    unittest.main()

"""Session 2826: Eurostat's nrg_ind_ffgae, the share of fossil fuels in gross available energy a year.

Energy Research Warehouse (ERW). Tests warehouse/connectors/eurostat_fossil_share.py on a file built here (made up for the test,
not Eurostat's): the shares written in pct, EL written GR and EU27_2020 given no geo, the United Kingdom left out, a blank given
no row, a share above 100 kept and counted; a unit not PC, a value not a number and a key given twice stopping the run; the
sector rule and the holds. No network.

    python -m unittest tests.test_session2826 -v
"""

import os
import sys
import unittest

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
sys.path.insert(0, os.path.join(ROOT, "warehouse", "connectors"))
sys.path.insert(0, os.path.join(ROOT, "warehouse", "metadata"))
sys.path.insert(0, os.path.join(ROOT, "warehouse", "redivis"))
import eurostat_fossil_share as A  # noqa: E402
import build_coverage as B  # noqa: E402
import release_v1 as R  # noqa: E402

HEAD = ",".join(A.HEADER)


def line(geo, year, value, unit="PC"):
    return f"ESTAT:NRG_IND_FFGAE(1.0),16/07/26 23:00:00,A,{unit},{geo},{year},{value},,"


def data(unit="PC", value="68.12", twice=False):
    lines = [HEAD, line("EU27_2020", 2024, value, unit), line("EL", 2024, "80.5"), line("EE", 1990, "103.79"),
             line("NO", 2024, ""), line("UK", 2024, "75.0")]
    if twice:
        lines.append(lines[1])
    return (chr(10).join(lines) + chr(10)).encode("utf-8")


class Parse(unittest.TestCase):
    def test_rows(self):
        t, counts = A.build(data(), "u", "r", "v")
        self.assertEqual(len(t), 3)
        self.assertEqual((counts["left_out_geo"], counts["blank"], counts["outside"]), (["UK"], 1, [("EE", "1990", 103.79)]))
        self.assertEqual(set(t.geo), {"", "GR", "EE"})
        x = t[t.entity == "eurostat_fossil_share:EU27_2020"]
        self.assertEqual((x.value.iloc[0], x.unit.iloc[0]), (68.12, "pct"))

    def test_stops(self):
        for content in (data(unit="KTOE"), data(value="n.a."), data(twice=True)):
            with self.assertRaises(RuntimeError):
                A.build(content, "u", "r", "v")


class Registered(unittest.TestCase):
    def test_sector_and_holds(self):
        self.assertEqual(B.sector_of(A.NAME), "power")
        self.assertIn(A.NAME, R.STORAGE_HELD)
        with open(os.path.join(ROOT, "warehouse", "supabase", "live_set.yaml"), encoding="utf-8") as f:
            self.assertIn(f"  - {A.NAME}" + chr(10), f.read().replace(chr(13) + chr(10), chr(10)))


if __name__ == "__main__":
    unittest.main()

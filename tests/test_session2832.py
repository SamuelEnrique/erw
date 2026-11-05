"""Session 2832: Eurostat's nrg_ind_di, the diversity index of energy supply a year.

Energy Research Warehouse (ERW). Tests warehouse/connectors/eurostat_supply_diversity.py on a file built here (made up for the
test, not Eurostat's): the index kept as given, EL written GR, a country outside the kept list left out, a blank given no row;
a unit not INX, a value not a number, an index above 1 and a key given twice stopping the run; the sector rule and the holds.
No network.

    python -m unittest tests.test_session2832 -v
"""

import os
import sys
import unittest

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
sys.path.insert(0, os.path.join(ROOT, "warehouse", "connectors"))
sys.path.insert(0, os.path.join(ROOT, "warehouse", "metadata"))
sys.path.insert(0, os.path.join(ROOT, "warehouse", "redivis"))
import eurostat_supply_diversity as A  # noqa: E402
import build_coverage as B  # noqa: E402
import release_v1 as R  # noqa: E402

HEAD = ",".join(A.HEADER)


def line(geo, value, unit="INX"):
    return f"ESTAT:NRG_IND_DI(1.0),16/12/25 23:00:00,A,{unit},{geo},2024,{value},,"


def data(unit="INX", value="0.1548", twice=False):
    lines = [HEAD, line("DE", value, unit), line("EL", "0.2"), line("AT", ""), line("US", "0.3")]
    if twice:
        lines.append(lines[1])
    return (chr(10).join(lines) + chr(10)).encode("utf-8")


class Parse(unittest.TestCase):
    def test_rows(self):
        t, counts = A.build(data(), "u", "r", "v")
        self.assertEqual(len(t), 2)
        self.assertEqual((counts["left_out_geo"], counts["blank"]), (["US"], 1))
        x = t[t.entity == "eurostat_supply_diversity:DE"]
        self.assertEqual((x.value.iloc[0], x.unit.iloc[0], x.node.iloc[0]), (0.1548, "index", "DE diversity index of energy supply"))
        self.assertEqual(set(t.geo), {"DE", "GR"})

    def test_stops(self):
        for content in (data(unit="PC"), data(value="n.a."), data(value="1.5"), data(twice=True)):
            with self.assertRaises(RuntimeError):
                A.build(content, "u", "r", "v")


class Registered(unittest.TestCase):
    def test_sector_and_holds(self):
        self.assertEqual(B.sector_of(A.NAME), "power;gas;oil;coal")
        self.assertIn(A.NAME, R.STORAGE_HELD)
        with open(os.path.join(ROOT, "warehouse", "supabase", "live_set.yaml"), encoding="utf-8") as f:
            self.assertIn(f"  - {A.NAME}" + chr(10), f.read().replace(chr(13) + chr(10), chr(10)))


if __name__ == "__main__":
    unittest.main()

"""Session 2821: Eurostat's nrg_ind_idogas, European natural gas import dependency by country of origin, 2015 to 2020.

Energy Research Warehouse (ERW). Tests warehouse/connectors/eurostat_gas_import_origin.py on a file built here (made up for the
test, not Eurostat's): the shares written in pct per partner, EL written GR, the United Kingdom left out as a reporter, a
country year whose every partner is zero not written and counted, another zero kept, a blank given no row; a unit not PC, a
partner not expected, a value not a number, a share above 100 and a key given twice stopping the run; the sector rule and the
holds. No network.

    python -m unittest tests.test_session2821 -v
"""

import os
import sys
import unittest

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
sys.path.insert(0, os.path.join(ROOT, "warehouse", "connectors"))
sys.path.insert(0, os.path.join(ROOT, "warehouse", "metadata"))
sys.path.insert(0, os.path.join(ROOT, "warehouse", "redivis"))
import eurostat_gas_import_origin as A  # noqa: E402
import build_coverage as B  # noqa: E402
import release_v1 as R  # noqa: E402

HEAD = ",".join(A.HEADER)


def line(partner, geo, year, value, unit="PC", flag="i"):
    return f"ESTAT:NRG_IND_IDOGAS(1.0),29/09/22 23:00:00,A,G3000,{partner},{unit},{geo},{year},{value},{flag},"


def data(unit="PC", partner="RU", value="68.66", twice=False):
    lines = [HEAD, line(partner, "DE", 2020, value, unit), line("NO", "DE", 2020, "23.79"), line("DZ", "DE", 2020, "0.00"),
             line("RU", "AT", 2020, "0.00"), line("NO", "AT", 2020, "0.00"),
             line("RU", "EL", 2020, "38.1"), line("QA", "EL", 2020, "", flag="m"), line("RU", "UK", 2020, "1.0")]
    if twice:
        lines.append(lines[1])
    return (chr(10).join(lines) + chr(10)).encode("utf-8")


class Parse(unittest.TestCase):
    def test_rows(self):
        t, counts = A.build(data(), "u", "r", "v")
        self.assertEqual(len(t), 4)                                          # Germany's three, Greece's one
        self.assertEqual((counts["unreported"], counts["zero"], counts["blank"], counts["left_out_geo"]), (["AT 2020"], 1, 1, ["UK"]))
        x = t[t.entity == "eurostat_gas_origin:DE:RU"]
        self.assertEqual((x.value.iloc[0], x.unit.iloc[0], x.node.iloc[0]), (68.66, "pct", "DE natural gas import dependency on Russia"))
        self.assertEqual(set(t.geo), {"DE", "GR"})

    def test_stops(self):
        for content in (data(unit="TJ"), data(partner="CN"), data(value="n.a."), data(value="100.5"), data(twice=True)):
            with self.assertRaises(RuntimeError):
                A.build(content, "u", "r", "v")


class Registered(unittest.TestCase):
    def test_sector_and_holds(self):
        self.assertEqual(B.sector_of(A.NAME), "gas")
        self.assertIn(A.NAME, R.STORAGE_HELD)
        with open(os.path.join(ROOT, "warehouse", "supabase", "live_set.yaml"), encoding="utf-8") as f:
            self.assertIn(f"  - {A.NAME}" + chr(10), f.read().replace(chr(13) + chr(10), chr(10)))


if __name__ == "__main__":
    unittest.main()

"""Session 2827: Eurostat's nrg_ind_ioc, the EU's energy import origin concentration index by fuel a year.

Energy Research Warehouse (ERW). Tests warehouse/connectors/eurostat_import_concentration.py on a file built here (made up for the
test, not Eurostat's): the index kept as given, a 1 kept and counted, EL written GR, a country outside the kept list left out, a
blank given no row; a unit not INX, a product not in the codelist, a value not a number, an index above 1 and a key given twice
stopping the run; the codelist read; the sector rule and the holds. No network.

    python -m unittest tests.test_session2827 -v
"""

import os
import sys
import unittest

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
sys.path.insert(0, os.path.join(ROOT, "warehouse", "connectors"))
sys.path.insert(0, os.path.join(ROOT, "warehouse", "metadata"))
sys.path.insert(0, os.path.join(ROOT, "warehouse", "redivis"))
import eurostat_import_concentration as A  # noqa: E402
import build_coverage as B  # noqa: E402
import release_v1 as R  # noqa: E402

HEAD = ",".join(A.HEADER)
NAMES = {"TOTAL": "Total", "E7000": "Electricity", "G3000": "Natural gas"}


def line(siec, geo, value, unit="INX"):
    return f"ESTAT:NRG_IND_IOC(1.0),15/07/26 23:00:00,A,{siec},{unit},{geo},2024,{value},,"


def data(unit="INX", siec="G3000", value="0.3199", twice=False):
    lines = [HEAD, line(siec, "DE", value, unit), line("E7000", "DE", "0.3065"), line("G3000", "CZ", "1.0000"),
             line("TOTAL", "EL", "0.25"), line("TOTAL", "AT", ""), line("TOTAL", "US", "0.5")]
    if twice:
        lines.append(lines[1])
    return (chr(10).join(lines) + chr(10)).encode("utf-8")


class Parse(unittest.TestCase):
    def build(self, content):
        return A.build(content, NAMES, "u", "r", "v")

    def test_rows(self):
        t, counts = self.build(data())
        self.assertEqual(len(t), 4)
        self.assertEqual((counts["left_out_geo"], counts["blank"], counts["ones"]), (["US"], 1, 1))
        x = t[t.entity == "eurostat_ioc:DE:G3000"]
        self.assertEqual((x.value.iloc[0], x.unit.iloc[0], x.node.iloc[0]), (0.3199, "index", "DE import origin concentration, Natural gas"))
        self.assertEqual(set(t.geo), {"DE", "CZ", "GR"})

    def test_stops(self):
        for content in (data(unit="PC"), data(siec="X9999"), data(value="n.a."), data(value="1.2"), data(twice=True)):
            with self.assertRaises(RuntimeError):
                self.build(content)

    def test_codelist(self):
        tsv = (chr(10).join(f"{k}\t{v}" for k, v in NAMES.items())).encode("utf-8")
        self.assertEqual(A.siec_names(tsv)["G3000"], "Natural gas")
        with self.assertRaises(RuntimeError):
            A.siec_names(b"E7000\tPower\n")


class Registered(unittest.TestCase):
    def test_sector_and_holds(self):
        self.assertEqual(B.sector_of(A.NAME), "power;gas;oil;coal")
        self.assertIn(A.NAME, R.STORAGE_HELD)
        with open(os.path.join(ROOT, "warehouse", "supabase", "live_set.yaml"), encoding="utf-8") as f:
            self.assertIn(f"  - {A.NAME}" + chr(10), f.read().replace(chr(13) + chr(10), chr(10)))


if __name__ == "__main__":
    unittest.main()

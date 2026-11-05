"""Session 2806: Eurostat's nrg_ind_re, the rate of electrification in Europe a year, by sector and branch.

Energy Research Warehouse (ERW). Tests warehouse/connectors/eurostat_electrification.py on a file built here (made up for the
test, not Eurostat's): the shares written in pct, EL written GR and EU27_2020 given no geo, the United Kingdom left out, a blank
(flag m) given no row, a zero kept; final consumption's rate compared with its three sectors' and households' and services'
with their parts, a case outside counted; a unit not PC, a balance item not in the codelist, a value not a number, a share
above 100 and a key given twice stopping the run; the codelist read; the sector rule and the holds. No network.

    python -m unittest tests.test_session2806 -v
"""

import os
import sys
import unittest

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
sys.path.insert(0, os.path.join(ROOT, "warehouse", "connectors"))
sys.path.insert(0, os.path.join(ROOT, "warehouse", "metadata"))
sys.path.insert(0, os.path.join(ROOT, "warehouse", "redivis"))
import eurostat_electrification as A  # noqa: E402
import build_coverage as B  # noqa: E402
import release_v1 as R  # noqa: E402

HEAD = ",".join(A.HEADER)
NAMES = {"FC_E": "Final consumption - energy use", "FC_IND_E": "Final consumption - industry sector - energy use",
         "FC_TRA_E": "Final consumption - transport sector - energy use", "FC_OTH_E": "Final consumption - other sectors - energy use",
         "FC_OTH_HH_E": "Final consumption - other sectors - households - energy use",
         "FC_OTH_CP_E": "Final consumption - other sectors - commercial and public services - energy use",
         "FC_OTH_HH_CP_E": "Final consumption - other sectors - households and commercial/public services - energy use"}


def line(item, geo, value, unit="PC", flag=""):
    return f"ESTAT:NRG_IND_RE(1.0),16/07/26 23:00:00,A,{item},{unit},{geo},2023,{value},{flag},"


def data(unit="PC", item="FC_TRA_E", value="2.5", final="23.0", hhcp="40.0", twice=False):
    lines = [HEAD]
    for g in ("PT", "EL", "EU27_2020", "UK"):
        lines += [line("FC_E", g, final if g == "PT" else "23.0", unit), line("FC_IND_E", g, "33.0"), line(item, g, value),
                  line("FC_OTH_E", g, "35.0"), line("FC_OTH_HH_E", g, "30.0"), line("FC_OTH_CP_E", g, "55.0"),
                  line("FC_OTH_HH_CP_E", g, hhcp if g == "PT" else "40.0")]
    lines.append(line("FC_IND_E", "NO", "", flag="m"))
    lines.append(line("FC_TRA_E", "NO", "0"))
    if twice:
        lines.append(lines[1])
    return (chr(10).join(lines) + chr(10)).encode("utf-8")


class Parse(unittest.TestCase):
    def build(self, content):
        return A.build(content, NAMES, "u", "r", "v")

    def test_rows(self):
        t, counts = self.build(data())
        self.assertEqual(len(t), 3 * 7 + 1)                                  # three areas kept, seven items; Norway's zero
        self.assertEqual((counts["left_out_geo"], counts["blank"], counts["zero"]), (["UK"], 1, 1))
        self.assertEqual(set(t.geo), {"PT", "GR", "", "NO"})
        x = t[t.entity == "eurostat_electrification:PT:FC_E"]
        self.assertEqual((x.value.iloc[0], x.unit.iloc[0], x.node.iloc[0]), (23.0, "pct", "PT electrification rate, Final consumption - energy use"))
        ck = A.checks(t)
        self.assertEqual(ck["final"], (3, []))
        self.assertEqual(ck["households_services"], (3, []))

    def test_counted(self):
        t, _ = self.build(data(final="40.0", hhcp="60.0"))                   # above every sector, above both parts
        ck = A.checks(t)
        self.assertEqual(ck["final"], (3, [("PT", "2023", 40.0)]))
        self.assertEqual(ck["households_services"], (3, [("PT", "2023", 60.0)]))

    def test_stops(self):
        for content in (data(unit="KTOE"), data(item="FC_XX_E"), data(value="n.a."), data(value="100.5"), data(twice=True)):
            with self.assertRaises(RuntimeError):
                self.build(content)

    def test_codelist(self):
        tsv = (chr(10).join(f"{k}\t{v}" for k, v in NAMES.items())).encode("utf-8")
        self.assertEqual(A.item_names(tsv)["FC_TRA_E"], "Final consumption - transport sector - energy use")
        with self.assertRaises(RuntimeError):
            A.item_names(b"FC_E\tFinal consumption\n")


class Registered(unittest.TestCase):
    def test_sector_and_holds(self):
        self.assertEqual(B.sector_of(A.NAME), "power")
        self.assertIn(A.NAME, R.STORAGE_HELD)
        with open(os.path.join(ROOT, "warehouse", "supabase", "live_set.yaml"), encoding="utf-8") as f:
            self.assertIn(f"  - {A.NAME}" + chr(10), f.read().replace(chr(13) + chr(10), chr(10)))


if __name__ == "__main__":
    unittest.main()

"""Session 2790: Eurostat's nrg_ind_id, European energy import dependency by product a year.

Energy Research Warehouse (ERW). Tests warehouse/connectors/eurostat_import_dependency.py on a file built here (made up for the
test, not Eurostat's): the shares written in pct, EL written GR and EU27_2020 given no geo, the United Kingdom left out, a negative
(a net exporter) and an extreme value kept and counted; a unit not PC, a product not in the codelist, a value not a number and a
key given twice stopping the run; the codelist read; the sector rule and the holds. No network.

    python -m unittest tests.test_session2790 -v
"""

import os
import sys
import unittest

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
sys.path.insert(0, os.path.join(ROOT, "warehouse", "connectors"))
sys.path.insert(0, os.path.join(ROOT, "warehouse", "metadata"))
sys.path.insert(0, os.path.join(ROOT, "warehouse", "redivis"))
import eurostat_import_dependency as A  # noqa: E402
import build_coverage as B  # noqa: E402
import release_v1 as R  # noqa: E402

HEAD = ",".join(A.HEADER)
NAMES = {"TOTAL": "Total", "G3000": "Natural gas", "P1100": "Peat"}


def data(unit="PC", siec="P1100", value="-3000.5", twice=False):
    lines = [HEAD]
    for g in ("NO", "EL", "EU27_2020", "UK"):
        lines.append(f"ESTAT:NRG_IND_ID(1.0),16/07/26 23:00:00,A,TOTAL,{unit},{g},2024,57.29,,")
        lines.append(f"ESTAT:NRG_IND_ID(1.0),16/07/26 23:00:00,A,G3000,{unit},{g},2024,{'-500.0' if g == 'NO' else '98.5'},,")
    lines.append(f"ESTAT:NRG_IND_ID(1.0),16/07/26 23:00:00,A,{siec},{unit},EL,2024,{value},,")
    if twice:
        lines.append(lines[1])
    return (chr(10).join(lines) + chr(10)).encode("utf-8")


class Parse(unittest.TestCase):
    def build(self, content):
        return A.build(content, NAMES, "u", "r", "v")

    def test_rows(self):
        t, counts = self.build(data())
        self.assertEqual(len(t), 3 * 2 + 1)                                  # three areas kept, two products; the extreme one
        self.assertEqual(counts["left_out_geo"], ["UK"])
        self.assertEqual(set(t.geo), {"NO", "GR", ""})
        self.assertEqual(set(t.unit), {"pct"})
        self.assertEqual(counts["extreme"], 2)                               # Norway's -500 and Greece's -3000.5, kept
        x = t[t.entity == "eurostat_import_dependency:NO:G3000"]
        self.assertEqual((x.value.iloc[0], x.node.iloc[0]), (-500.0, "NO import dependency, Natural gas"))

    def test_stops(self):
        for content in (data(unit="KTOE"), data(siec="X9999"), data(value="n.a."), data(twice=True)):
            with self.assertRaises(RuntimeError):
                self.build(content)

    def test_codelist(self):
        tsv = (chr(10).join(f"{k}\t{v}" for k, v in NAMES.items())).encode("utf-8")
        self.assertEqual(A.siec_names(tsv)["G3000"], "Natural gas")
        with self.assertRaises(RuntimeError):
            A.siec_names(b"G3000\tNatural gas\n")


class Registered(unittest.TestCase):
    def test_sector_and_holds(self):
        self.assertEqual(B.sector_of(A.NAME), "power")
        self.assertIn(A.NAME, R.STORAGE_HELD)
        with open(os.path.join(ROOT, "warehouse", "supabase", "live_set.yaml"), encoding="utf-8") as f:
            self.assertIn(f"  - {A.NAME}" + chr(10), f.read().replace(chr(13) + chr(10), chr(10)))


if __name__ == "__main__":
    unittest.main()

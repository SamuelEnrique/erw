"""Session 2798: Eurostat's nrg_d_hhq, European households' electricity by end use a year.

Energy Research Warehouse (ERW). Tests warehouse/connectors/eurostat_household_electricity.py on a file built here (made up for
the test, not Eurostat's): GWh written as MWh, EL written GR and EU27_2020 given no geo, the United Kingdom left out; a country
year whose seven items are all zero not written and counted, another zero kept; the end uses' sum checked against the total; a
unit not GWH, a balance item not expected, a value not a number, a key given twice and end uses that do not make the total
stopping the run; the sector rule and the holds. No network.

    python -m unittest tests.test_session2798 -v
"""

import os
import sys
import unittest

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
sys.path.insert(0, os.path.join(ROOT, "warehouse", "connectors"))
sys.path.insert(0, os.path.join(ROOT, "warehouse", "metadata"))
sys.path.insert(0, os.path.join(ROOT, "warehouse", "redivis"))
import eurostat_household_electricity as A  # noqa: E402
import build_coverage as B  # noqa: E402
import release_v1 as R  # noqa: E402

HEAD = ",".join(A.HEADER)
SPLIT = {"FC_OTH_HH_E_SH": 3.0, "FC_OTH_HH_E_SC": 0.0, "FC_OTH_HH_E_WH": 2.0, "FC_OTH_HH_E_CK": 1.0,
         "FC_OTH_HH_E_LE": 3.5, "FC_OTH_HH_E_OE": 0.5}


def line(item, geo, year, value, unit="GWH"):
    return f"ESTAT:NRG_D_HHQ(1.0),09/06/26 11:00:00,A,{item},E7000,{unit},{geo},{year},{value},,"


def data(unit="GWH", item="FC_OTH_HH_E_OE", value="0.5", total="10.0", twice=False):
    lines = [HEAD]
    for g in ("NO", "EL", "EU27_2020", "UK"):
        lines.append(line("FC_OTH_HH_E", g, 2024, total if g == "EL" else "10.0", unit))
        for k, v in SPLIT.items():
            lines.append(line(item if k == "FC_OTH_HH_E_OE" else k, g, 2024, value if k == "FC_OTH_HH_E_OE" else v, unit))
    for k in A.ITEMS:                                                        # Norway's 2011: the split not reported
        lines.append(line(k, "NO", 2011, "0.000"))
    if twice:
        lines.append(lines[1])
    return (chr(10).join(lines) + chr(10)).encode("utf-8")


class Parse(unittest.TestCase):
    def build(self, content):
        t, counts = A.build(content, "u", "r", "v")
        return t, counts, A.checks(t)

    def test_rows(self):
        t, counts, (compared, worst) = self.build(data())
        self.assertEqual(len(t), 3 * 7)                                      # three areas kept, seven items, one year
        self.assertEqual(counts["left_out_geo"], ["UK"])
        self.assertEqual(counts["unreported"], [("NO", "2011-01-01T00:00:00Z")])
        self.assertEqual(counts["zero"], 3)                                  # each area's space cooling, kept
        self.assertEqual(set(t.geo), {"NO", "GR", ""})
        self.assertEqual((compared, worst), (3, 0.0))
        x = t[(t.entity == "eurostat_household_electricity:EL") & (t.variable == "space_heating")]
        self.assertEqual((x.value.iloc[0], x.unit.iloc[0], x.ts_utc.iloc[0]), (3000.0, "MWh", "2024-01-01T00:00:00Z"))

    def test_stops(self):
        for content in (data(unit="KTOE"), data(item="FC_OTH_HH_E_XX"), data(value="n.a."), data(twice=True)):
            with self.assertRaises(RuntimeError):
                A.build(content, "u", "r", "v")
        with self.assertRaises(RuntimeError):                                # Greece's end uses make 10, its total 12.5
            self.build(data(total="12.5"))


class Registered(unittest.TestCase):
    def test_sector_and_holds(self):
        self.assertEqual(B.sector_of(A.NAME), "power")
        self.assertIn(A.NAME, R.STORAGE_HELD)
        with open(os.path.join(ROOT, "warehouse", "supabase", "live_set.yaml"), encoding="utf-8") as f:
            self.assertIn(f"  - {A.NAME}" + chr(10), f.read().replace(chr(13) + chr(10), chr(10)))


if __name__ == "__main__":
    unittest.main()

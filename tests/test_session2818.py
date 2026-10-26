"""Session 2818: Eurostat's nrg_d_indq_n, European industry's electricity by NACE Rev. 2 activity a year.

Energy Research Warehouse (ERW). Tests warehouse/connectors/eurostat_industry_electricity.py on a file built here (made up for
the test, not Eurostat's): GWh written as MWh, EL written GR, the United Kingdom left out; a country year with every value zero
not written, children all zero under a positive parent not written, another zero kept, a confidential observation given no
row; a group's children compared with its parent, a case off counted; a unit not GWH, an activity not in the codelist, a value
not a number, a negative value and a key given twice stopping the run; the codelist read; the sector rule and the holds. No
network.

    python -m unittest tests.test_session2818 -v
"""

import os
import sys
import unittest

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
sys.path.insert(0, os.path.join(ROOT, "warehouse", "connectors"))
sys.path.insert(0, os.path.join(ROOT, "warehouse", "metadata"))
sys.path.insert(0, os.path.join(ROOT, "warehouse", "redivis"))
import eurostat_industry_electricity as A  # noqa: E402
import build_coverage as B  # noqa: E402
import release_v1 as R  # noqa: E402

HEAD = ",".join(A.HEADER)
NAMES = {"TOTAL": "Total - all NACE activities", "C10": "Manufacture of food products", "C11": "Manufacture of beverages",
         "C12": "Manufacture of tobacco products", "C10-C12": "Manufacture of food products; beverages and tobacco products",
         "C20": "Manufacture of chemicals and chemical products", "C201": "Manufacture of basic chemicals",
         "C202": "Manufacture of pesticides", "C203": "Manufacture of paints", "C204": "Manufacture of soap",
         "C205": "Manufacture of other chemical products", "C206": "Manufacture of man-made fibres"}


def line(nace, geo, year, value, unit="GWH", conf=""):
    return f"ESTAT:NRG_D_INDQ_N(1.0),27/08/26 23:00:00,A,{unit},E7000,{nace},{geo},{year},{value},,{conf}"


def data(unit="GWH", nace="C12", value="1.0", c10_12="13.0", twice=False):
    lines = [HEAD, line("TOTAL", "AT", 2024, "100.0", unit), line("C10-C12", "AT", 2024, c10_12), line("C10", "AT", 2024, "10.0"),
             line("C11", "AT", 2024, "2.0"), line(nace, "AT", 2024, value), line("C20", "AT", 2024, "30.0")]
    lines += [line(k, "AT", 2024, "0") for k in ("C201", "C202", "C203", "C204", "C205", "C206")]    # a split not reported
    lines += [line(k, "AT", 2018, "0") for k in ("TOTAL", "C10-C12", "C10")]                         # a year not reported
    lines += [line("TOTAL", "EL", 2024, "50.0"), line("C11", "EL", 2024, "0"), line("C10", "EL", 2024, "", conf="C"),
              line("TOTAL", "UK", 2024, "5.0")]
    if twice:
        lines.append(lines[1])
    return (chr(10).join(lines) + chr(10)).encode("utf-8")


class Parse(unittest.TestCase):
    def build(self, content):
        return A.build(content, NAMES, "u", "r", "v")

    def test_rows(self):
        t, counts = self.build(data())
        self.assertEqual(counts["unreported_years"], ["AT 2018"])
        self.assertEqual(counts["unreported_splits"], [("AT", "2024", "C20")])
        self.assertEqual((counts["dropped"], counts["zero"], counts["confidential"], counts["left_out_geo"]), (3 + 6, 1, 1, ["UK"]))
        self.assertEqual(len(t), 6 + 2)                                      # Austria's six left in 2024, Greece's two
        v = {(r.x_geo_code, r.x_nace_r2): r.value for r in t.itertuples()}
        self.assertEqual(v[("AT", "C10-C12")], 13000.0)
        self.assertNotIn(("AT", "C201"), v)
        self.assertEqual(v[("EL", "C11")], 0.0)
        self.assertEqual(set(t.geo), {"AT", "GR"})
        self.assertEqual(A.checks(t), (1, []))

    def test_counted(self):
        t, _ = self.build(data(c10_12="15.0"))                               # the parts make 13, the parent 15
        self.assertEqual(A.checks(t), (1, [("AT", "2024", "C10-C12", -2.0)]))

    def test_stops(self):
        for content in (data(unit="TJ"), data(nace="C99"), data(value="n.a."), data(value="-1"), data(twice=True)):
            with self.assertRaises(RuntimeError):
                self.build(content)

    def test_codelist(self):
        tsv = (chr(10).join(f"{k}\t{v}" for k, v in NAMES.items())).encode("utf-8")
        self.assertEqual(A.nace_names(tsv)["C20"], "Manufacture of chemicals and chemical products")
        with self.assertRaises(RuntimeError):
            A.nace_names(b"C10\tFood\n")


class Registered(unittest.TestCase):
    def test_sector_and_holds(self):
        self.assertEqual(B.sector_of(A.NAME), "power")
        self.assertIn(A.NAME, R.STORAGE_HELD)
        with open(os.path.join(ROOT, "warehouse", "supabase", "live_set.yaml"), encoding="utf-8") as f:
            self.assertIn(f"  - {A.NAME}" + chr(10), f.read().replace(chr(13) + chr(10), chr(10)))


if __name__ == "__main__":
    unittest.main()

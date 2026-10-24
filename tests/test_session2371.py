"""Session 2371: the Ceylon Electricity Board's Statistical Digest, Sri Lanka's stations, capacity, generation and maximum
demand, in place of PUCSL's dispatch dashboard.

Energy Research Warehouse (ERW). Tests warehouse/connectors/ceb_srilanka.py's table reader on rows built here in the form
pdfplumber gives the digest's page 3 (made up for the test, not CEB's): an owner's rows under its label, the Total row as
owner all, the sources checked against their totals; a source not in the map, a value that is not a number and parts
not adding to their total stopping the run; the sector rule and the live-set hold (internal, so not in the release). No
network, no PDF.

    python -m unittest tests.test_session2371 -v
"""

import os
import sys
import unittest

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
sys.path.insert(0, os.path.join(ROOT, "warehouse", "connectors"))
sys.path.insert(0, os.path.join(ROOT, "warehouse", "metadata"))
import ceb_srilanka as C  # noqa: E402
import build_coverage as B  # noqa: E402


def table(ceb_total="12", hydro="7"):
    return [["head"], ["years"],
            ["CEB :", "Total", ceb_total, "13"], ["", "Major Hydro", hydro, "8"], ["", "Thermal (Coal)", "5", "5"],
            ["IPP :", "Total", "3", "4"], ["", "NCRE (Wind)", "1", "1"], ["", "NCRE(Rooftop Solar)", "2", "3"],
            ["Total Generation", None, "15", "17"]]


class Rows(unittest.TestCase):
    def test_rows(self):
        got = C.owner_rows(table(), 2, (2, 3), "generation")
        self.assertEqual(got["ceb"]["major_hydro"], [7.0, 8.0])
        self.assertEqual(got["ipp"]["ncre_rooftop_solar"], [2.0, 3.0])
        self.assertEqual(got["all"]["total"], [15.0, 17.0])

    def test_stops(self):
        for t in (table(hydro="9"), table(ceb_total="x"), table()[:3] + [["", "Gas", "1", "1"]] + table()[3:]):
            with self.assertRaises(RuntimeError):
                C.owner_rows(t, 2, (2, 3), "generation")


class Registered(unittest.TestCase):
    def test_sector_and_hold(self):
        self.assertEqual(B.sector_of(C.NAME), "power")
        with open(os.path.join(ROOT, "warehouse", "supabase", "live_set.yaml"), encoding="utf-8") as f:
            self.assertIn(f"  - {C.NAME}\n", f.read().replace("\r\n", "\n"))


if __name__ == "__main__":
    unittest.main()

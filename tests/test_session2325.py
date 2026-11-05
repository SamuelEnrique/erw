"""Session 2325: EPRA's Energy and Petroleum Statistics Reports, Kenya's capacity by technology and consumption by customer
category, a fiscal year.

Energy Research Warehouse (ERW). Tests warehouse/connectors/epra_kenya_electricity.py's table readers on tables built here
in the form pdfplumber gives EPRA's tables 2.1 and 2.2 (made up for the test, not EPRA's): a dash or blank without a
value, WHRC read as waste heat recovery, the parts checked against their totals; a header not EPRA's, a technology or
category not in the map, a value that is not a number and a part not adding to its total stopping the run; the sector
rule and the holds. No network, no PDF.

    python -m unittest tests.test_session2325 -v
"""

import os
import sys
import unittest

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
sys.path.insert(0, os.path.join(ROOT, "warehouse", "connectors"))
sys.path.insert(0, os.path.join(ROOT, "warehouse", "metadata"))
sys.path.insert(0, os.path.join(ROOT, "warehouse", "redivis"))
import epra_kenya_electricity as K  # noqa: E402
import build_coverage as B  # noqa: E402
import release_v1 as R1  # noqa: E402

HEAD = [["Technology", "Interconnected\nCapacity (MW)", None, "Captive\nCapacity (MW)", "Offgrid\nCapacity", "Total\nInstalled\nCapacity", "% Total"],
        ["", "Installed", "Effective", "", "", "", ""]]


def cap(geo_total="1,013.68"):
    return HEAD + [["Geothermal", "1,009.98", "876.10", "3.70", "", geo_total, "25%"],
                   ["WHRC", "-", "-", "83.50", "0.10", "83.60", "2%"],
                   ["Total", "1,009.98", "876.10", "87.20", "0.10", "1,097.28", "100%"]]


def use(total="12.00"):
    return [["Customer category", "Energy consumption (GWh)", "Percentage"], ["Industrial", "10.00", "80%"],
            ["E-Mobility", "2.00", "20%"], ["Total", total, "100%"]]


class Tables(unittest.TestCase):
    def test_capacity(self):
        got = K.capacity(cap(), "2026")
        self.assertEqual(got["interconnected_installed"], {"geothermal": 1009.98, "total": 1009.98})
        self.assertEqual(got["captive"]["waste_heat_recovery"], 83.5)
        self.assertNotIn("waste_heat_recovery", got["interconnected_effective"])
        self.assertEqual(got["offgrid"], {"waste_heat_recovery": 0.1, "total": 0.1})

    def test_consumption(self):
        self.assertEqual(K.consumption(use(), "2025/2026"), {"industrial": 10.0, "e_mobility": 2.0, "total": 12.0})

    def test_stops(self):
        for t in (cap(geo_total="1,020.00"), [HEAD[0], ["", "Installed", "Net", "", "", "", ""]] + cap()[2:],
                  cap()[:2] + [["Coal", "1", "1", "", "", "1", ""]], cap()[:2] + [["Geothermal", "1.0.0", "1", "", "", "1", ""]]):
            with self.assertRaises(RuntimeError):
                K.capacity(t, "2026")
        for t in (use(total="13.00"), [["Category", "GWh"]] + use()[1:], use()[:1] + [["Agriculture", "1", ""]]):
            with self.assertRaises(RuntimeError):
                K.consumption(t, "2025/2026")


class Registered(unittest.TestCase):
    def test_sector_and_holds(self):
        self.assertEqual(B.sector_of(K.NAME), "power")
        self.assertIn(K.NAME, R1.STORAGE_HELD)
        with open(os.path.join(ROOT, "warehouse", "supabase", "live_set.yaml"), encoding="utf-8") as f:
            self.assertIn(f"  - {K.NAME}\n", f.read().replace("\r\n", "\n"))


if __name__ == "__main__":
    unittest.main()

"""Session 11200 (chain 760, five-tools data request 69): SIC 1220 is named as the SEC's own SIC code list names it.

The four coal miners filed under SIC 1220 (AREC, CNR, HCC, METC) carry "Silver Ores" in their EDGAR submissions files;
the SEC's SIC code list (www.sec.gov/search-filings/standard-industrial-classification-sic-code-list, read 28 November
2026) names 1220 "BITUMINOUS COAL & LIGNITE MINING". The universe takes the list's name.
"""
import os
import sys
import unittest

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(ROOT, "warehouse", "connectors"))
import sec_edgar  # noqa: E402


class TheSicLabel(unittest.TestCase):
    def test_1220_takes_the_sec_lists_name(self):
        self.assertEqual(sec_edgar.sic_label("1220", "Silver Ores"), "Bituminous Coal & Lignite Mining")

    def test_other_codes_keep_the_submissions_label(self):
        self.assertEqual(sec_edgar.sic_label("1221", "Bituminous Coal & Lignite Surface Mining"),
                         "Bituminous Coal & Lignite Surface Mining")
        self.assertEqual(sec_edgar.sic_label("4911", "Electric Services"), "Electric Services")


if __name__ == "__main__":
    unittest.main()

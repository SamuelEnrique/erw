"""Session 1004 (chain 070): the Stata package's help, README, examples and install files. The help has its sections
(install among them); stata.toc and erw.pkg make `net install erw, from(...)` work and list files that exist;
examples.do reproduces the Grid tool's ERCOT demand and the price board's Henry Hub with erw, in the owner's style, and
the checker catches a fault in it. No request, no model call."""
import importlib.util
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
STATA = ROOT / "packages" / "stata"
spec = importlib.util.spec_from_file_location("check_ado_1004", STATA / "check_ado.py")
C = importlib.util.module_from_spec(spec)
spec.loader.exec_module(C)
DO = (STATA / "examples.do").read_text(encoding="utf-8")


class Package(unittest.TestCase):
    def test_install_files(self):
        self.assertEqual(C.check_install(), [])
        self.assertIn("f erw.ado", (STATA / "erw.pkg").read_text(encoding="utf-8"))
        hlp = (STATA / "erw.sthlp").read_text(encoding="utf-8")
        self.assertIn('net install erw, from("https://raw.githubusercontent.com/SamuelEnrique/erw/main/packages/stata/")', hlp)
        self.assertIn("net install erw", (STATA / "README.md").read_text(encoding="utf-8"))

    def test_examples_reproduce_two_charts_in_style(self):
        self.assertEqual(C.check_do(DO), [])
        self.assertIn("erw fetch eia930_all_demand, entity(eia930:ERCO) variable(demand_mw)", DO)
        self.assertIn("erw fetch eia_fuel_spot_prices, entity(eia:henry_hub)", DO)
        self.assertEqual(DO.count("graph export"), 2)

    def test_the_checker_catches_a_fault_in_the_examples(self):
        bad = DO.replace("sort ts_utc\n\nsummarize value", "sort ts_utc\nsummarize value", 1)
        self.assertTrue(C.check_do(bad))
        self.assertTrue(C.check_do(DO.replace("erw cite", "erw quote", 1)))


if __name__ == "__main__":
    unittest.main()

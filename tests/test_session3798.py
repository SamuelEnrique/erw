"""Session 3798 (chain 215): grid operators' reserve margins as their own assessments print them
(iso_reserve_margin_reports, the registry warehouse/sources/reserve_margins/). The committed registry checks clean; each
row carries its document, page and printed words; a figure is the printed number; a file with a problem is refused; a
document whose license is not public is not written; the CAISO's five figures of summer 2026 are the document's.

No network, no warehouse table, no model. Nothing here sets the environment at import.
"""
import os
import sys
import tempfile
import unittest

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(ROOT, "warehouse", "connectors"))
import reserve_margin_reports as R  # noqa: E402


class TheRegistry(unittest.TestCase):
    def test_the_committed_registry_is_clean(self):
        regs, problems = R.read_registry()
        self.assertEqual(problems, [])
        self.assertGreaterEqual(len(regs), 1)

    def test_caiso_summer_2026(self):
        regs, _ = R.read_registry()
        d = R.rows(regs)
        c = d[d["x_grid"] == "CAISO"].set_index("variable")
        self.assertEqual(c.loc["prm_achieved_pct", "value"], 30.8)
        self.assertEqual(c.loc["prm_required_pct", "value"], 25.0)
        self.assertEqual(c.loc["capacity_surplus_mw", "value"], 2547.0)
        self.assertEqual(c.loc["peak_forecast_mw", "value"], 46844.0)
        self.assertEqual(c.loc["ra_prm_load_weighted_pct", "value"], 17.5)
        self.assertTrue(all(c["ts_utc"] == "2026-06-01T00:00:00Z"))
        self.assertIn("30.8 percent", c.loc["prm_achieved_pct", "x_printed"])
        self.assertEqual(c.loc["capacity_surplus_mw", "x_page"], "3")
        self.assertTrue(all(c["source_url"].str.startswith("https://www.caiso.com/documents/")))

    def test_a_bad_file_is_refused_and_an_internal_one_not_written(self):
        folder = tempfile.mkdtemp()
        with open(os.path.join(folder, "bad.yaml"), "w", encoding="utf-8") as f:
            f.write("body: x\ngrid: X\npublisher: X\nsource: x:y\ndocument: d\ndocument_url: ftp://x\nperiod: p\nts: 2026-06\n"
                    "retrieved_at: 2026-11-12T00:00:00Z\nlicense: public\nfigures:\n  - {variable: margin, value: 1, page: 1, printed: w}\n")
        _, problems = R.read_registry(folder)
        self.assertTrue(any("document_url" in p for p in problems))
        self.assertTrue(any("ts" in p for p in problems))
        self.assertTrue(any("variable 'margin'" in p for p in problems))
        self.assertEqual(R.main(["--check", "--registry", folder]), 1)
        held = tempfile.mkdtemp()
        with open(os.path.join(held, "held.yaml"), "w", encoding="utf-8") as f:
            f.write("body: x\ngrid: X\npublisher: X\nsource: x:y\ndocument: d\ndocument_url: https://x\nperiod: p\nts: 2026-06-01\n"
                    "retrieved_at: 2026-11-12T00:00:00Z\nlicense: internal\nfigures:\n  - {variable: prm_achieved_pct, value: 1, page: 1, printed: w}\n")
        regs, problems = R.read_registry(held)
        self.assertEqual(problems, [])
        self.assertEqual(len(R.rows(regs)), 0)

    def test_no_em_dash(self):
        for f in ("warehouse/connectors/reserve_margin_reports.py", "docs/methods/reserve_margin_reports.md",
                  "warehouse/sources/reserve_margins/README.md", "warehouse/sources/reserve_margins/caiso_2026_summer_loads_and_resources_assessment.yaml",
                  "tests/test_session3798.py"):
            with open(os.path.join(ROOT, *f.split("/")), encoding="utf-8") as h:
                s = h.read()
            self.assertNotIn(chr(0x2014), s, f)
            self.assertNotIn(chr(0x2013), s, f)


if __name__ == "__main__":
    unittest.main()

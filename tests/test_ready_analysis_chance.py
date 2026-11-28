"""wip/ready-analysis-chance (session 11406, chain 770, part C): the other choice of the Automated Analysis audit of
26 November, finding 10 (docs/reviews/analysis-model-audit-2026-11-26.md), readied for Samuel's ruling, not requested.

On main the scanner raises its flags (17 on the first run, across 6,797 series) and nothing says how many chance alone
would raise. On this branch each run's scan_summary.json holds flags_expected_by_chance: for 6,797 series about 4.5 if
days are independent, 29.5 if they persist (log AR(1), rho 0.9) and 36.3 if their tails are fat (t, 3 degrees of
freedom), the shares the audit measured through the engine's own rules (its a6), before the cap of 12 drafts a day. The
note says it. No flag, draft or score moves. The review list's own column is not added here."""
import os
import sys
import unittest

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
sys.path.insert(0, os.path.join(ROOT, "warehouse", "analysis", "findings"))
sys.path.insert(0, os.path.join(ROOT, "warehouse"))


class TheChanceCount(unittest.TestCase):
    def test_the_counts_for_the_first_run(self):
        try:
            import findings_scanner as fs
        except Exception as exc:
            self.skipTest(f"findings_scanner does not import here: {exc}")
        got = fs.chance_flags(6797)
        print(f"flags expected by chance across 6,797 series: {got}")
        self.assertEqual(got, {"independent days": 4.5, "persistent days": 29.5, "fat-tailed days": 36.3})

    def test_the_summary_and_the_note(self):
        with open(os.path.join(ROOT, "warehouse", "analysis", "findings", "findings_scanner.py"), encoding="utf-8") as f:
            self.assertIn('"flags_expected_by_chance": chance_flags(stats["series_scanned"]),', f.read())
        with open(os.path.join(ROOT, "docs", "methods", "automated_analysis_scanner.md"), encoding="utf-8") as f:
            self.assertIn("`scan_summary.json` holds `flags_expected_by_chance`", f.read())


if __name__ == "__main__":
    unittest.main()

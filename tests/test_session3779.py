"""Session 3779 (chain 212): the files the replication tests hold to the page follow the data machine's refresh.

- replication/datacenter/figures_of_the_page.py writes page_figures.json from the page's own code
  (site/scripts/datacenter-page-figures.mjs) on the files as they stand; on the repository its --check passes, so the
  committed figures are the page's code, and test 1491 still holds the published mirror (a second code) to them.
- warehouse/analysis/findings/cross_check_rows.py writes our figure and the gap of the Research note's card-keyed
  cross-check rows from the cards; on the repository its --check passes, and a moved card figure moves the row's figure
  and its gap and nothing else (the published figure, the source and the reason stay).
- warehouse/run_data_machine.sh runs both, and siting-card.mjs, before the replication group's tests.

No network, no warehouse table, no model. Nothing here sets the environment at import.
"""
import importlib.util
import os
import shutil
import subprocess
import sys
import unittest

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
FIG = os.path.join(ROOT, "replication", "datacenter", "figures_of_the_page.py")
ROWS = os.path.join(ROOT, "warehouse", "analysis", "findings", "cross_check_rows.py")
RUN = os.path.join(ROOT, "warehouse", "run_data_machine.sh")


def module(path, name):
    spec = importlib.util.spec_from_file_location(name, path)
    m = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(m)
    return m


class TheRows(unittest.TestCase):
    def setUp(self):
        self.m = module(ROWS, "cross_check_rows_3779")

    def test_the_note_is_the_cards(self):
        p = subprocess.run([sys.executable, ROWS, "--check"], capture_output=True, text=True, timeout=120)
        self.assertEqual(p.returncode, 0, p.stdout + p.stderr)

    def test_a_moved_card_moves_the_figure_and_the_gap_only(self):
        cs = ["Requests withdrawn, 2000 to 2020: 75.2 percent of 3,509 GW requested (card `queue_divorce`)",
              "75 percent of 3,501 GW, the owner's thesis (not a publisher)", "the source",
              "+0.2 points, against a figure given to the whole percent; +8 GW", "the reason"]
        out = self.m.queue_row(list(cs), 75.2141195848057, 3590.66180077946)
        self.assertEqual(out[0], "Requests withdrawn, 2000 to 2020: 75.2 percent of 3,591 GW requested (card `queue_divorce`)")
        self.assertEqual(out[3], "+0.2 points, against a figure given to the whole percent; +90 GW")
        self.assertEqual(out[1:3] + out[4:], cs[1:3] + cs[4:])

    def test_a_usd_row(self):
        cs = ["ERCOT, 2025, the median real-time price: USD 25.68 per MWh (card)", "USD 25.68 per MWh, the thesis", "s", "0.00", "r"]
        self.assertEqual(self.m.usd_row(list(cs), 25.68)[3], "0.00")
        out = self.m.usd_row(list(cs), 25.7)
        self.assertIn("USD 25.70 per MWh", out[0])
        self.assertEqual(out[3], "+0.02")

    def test_the_signed_gap(self):
        self.assertEqual(self.m.signed(0.001, 2), "0.00")
        self.assertEqual(self.m.signed(-1234.4, 0), "-1,234")
        self.assertEqual(self.m.signed(0.24, 1), "+0.2")


class TheFigures(unittest.TestCase):
    def test_the_committed_figures_are_the_page_s_code(self):
        site = os.path.join(ROOT, "site")
        if shutil.which("node") is None or not os.path.isdir(os.path.join(site, "node_modules")):
            raise unittest.SkipTest("node or the site's node_modules is not here")
        if not os.path.exists(os.path.join(site, "public", "datacenter", "erw_2026_datacenter_carbon.csv")):
            raise unittest.SkipTest("the public carbon file is not in this copy")
        p = subprocess.run([sys.executable, FIG, "--check"], capture_output=True, text=True, timeout=600)
        if p.returncode == 2 and "Unknown file extension" in p.stdout:
            raise unittest.SkipTest("this node does not read TypeScript files")
        self.assertEqual(p.returncode, 0, p.stdout + p.stderr)

    def test_the_rounding_is_the_page_s(self):
        m = module(FIG, "figures_of_the_page_3779")
        self.assertEqual(m.shown(34.07007763443315, 0.005), 34.07)
        self.assertEqual(m.shown(29841980.99, 0.5), 29841981)
        self.assertEqual(m.shown(0.06909411744263043, 5e-05), 0.0691)
        self.assertEqual(m.shown(10160, 0), 10160)


class TheRun(unittest.TestCase):
    def test_the_steps_run_before_the_group(self):
        with open(RUN, encoding="utf-8") as f:
            t = f.read()
        at = t.index("group dm_test_replication ")
        for step in ("soft_step dm_siting_card ", "soft_step dm_datacenter_figures ", "soft_step dm_cross_check_rows "):
            self.assertLess(t.index(step), at, step)
        self.assertLess(t.index("soft_step dm_datacenter_carbon "), t.index("soft_step dm_datacenter_figures "))
        self.assertLess(t.index("soft_step dm_findings_recompute "), t.index("soft_step dm_cross_check_rows "))
        # session 3803: Research's replication page figures after the siting cards and the recompute
        self.assertLess(t.index("soft_step dm_siting_card "), t.index("soft_step dm_analysis_figures "))
        self.assertLess(t.index("soft_step dm_findings_recompute "), t.index("soft_step dm_analysis_figures "))
        self.assertLess(t.index("soft_step dm_analysis_figures "), at)


if __name__ == "__main__":
    unittest.main()

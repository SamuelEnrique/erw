"""Session 1420 (chain 111): the older blocks' files.

Energy Research Warehouse (ERW).

The Grid tool's blocks that stood before chain 077 and show a table of figures are named panels, each offering its
figures as a CSV written into its link by session 1182's site/components/grid/PanelFile.tsx: YourGrid's Right now
(grid_rightnow_<grid>), Batteries (grid_batteries_<grid>), What it costs (grid_cost_<grid>) and What is being built
(grid_building_<grid>); Reliability's three tables (grid_reliability_caiso, three files); the Now view's mix in that hour
(grid_nowmix_<grid>). "Yesterday" and the mix table (session 1416) and the Clean tab's carbon blocks (session 1415) had
theirs. A held grid's block draws no figure and offers no file; a held figure in a file is written "license needed".
site/scripts/test-grid-files.mjs holds every figure in its file and back on the committed fixtures, test-grid-render.mjs
has a case of each family, and check-table-downloads.mjs and check-download.mjs --grid read the new files.

    python -m unittest tests.test_session1420 -v
"""

import os
import re
import shutil
import subprocess
import unittest

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
SITE = os.path.join(ROOT, "site")
NODE = shutil.which("node")
EM = chr(0x2014)


def src(*parts):
    with open(os.path.join(ROOT, *parts), encoding="utf-8") as f:
        return f.read().replace("\r\n", "\n")


class TheBlocks(unittest.TestCase):
    def test_yourgrid_names_its_four_panels_and_files_them(self):
        y = src("site", "components", "grid", "YourGrid.tsx")
        for p in ("rightnow", "batteries", "cost", "building"):
            self.assertIn("<div data-grid-panel={`grid_%s_${g.slug}`}>" % p, y)
            self.assertIn("panel: `grid_%s_${g.slug}`" % p, y)
        self.assertEqual(y.count("<PanelFile "), 4)
        # the figures are drawn once each and filed (no key added or lost: session 473 counts 18)
        self.assertEqual(y.count("check="), 18)
        self.assertIn("<Num check={`storage|iso_mw|${g.iso}|operating`} raw={mw(op)}>", y)   # session 1180's line, kept
        self.assertIn("{opMw} MW, {opMwh} MWh", y)
        self.assertIn("{dcNum} facilities; {dcMwNum} MW where a source states it.", y)
        self.assertIn("rows={qRows.map((r) => r.cells)} />", y)
        # a held block offers no file; the datacenters' figures, held whole, are written "license needed" (Num's heldBy)
        self.assertIn("{qRows.length || !heldBy(`griddc|${g.slug}|n`) ? (", y)
        self.assertIn("if (g.hub && licenseHeldRow(T, g.hub.entity)) return <HeldLine", y)   # session 1167's, kept
        # the pinned section lines stand
        for title in ('title="Right now: demand"', 'title="Batteries"', 'title="What it costs"', 'title="What is being built"'):
            self.assertIn(title, y)
        self.assertIn('g.slug === "caiso" ? <Section id="reliability" title="Reliability"', y)

    def test_reliability_files_its_three_tables(self):
        r = src("site", "components", "grid", "Reliability.tsx")
        self.assertIn('<div data-grid-panel="grid_reliability_caiso">', r)
        for part in ("days_per_year", "highest_peaks", "latest_days"):
            self.assertIn(f'part: "{part}"', r)
        self.assertEqual(r.count("<PanelFile "), 3)
        self.assertIn("function dayParts(p: SeriesRow, x: Days, f: Unread = {}) {", r)
        self.assertIn("function RowUnread(", r)   # session 1411's, kept
        self.assertIn('{ check: "awe|rows|any", raw: notices.length }', r)
        self.assertIn('<Num check="awe|rows|any" raw={notices.length}>{count(notices.length)}</Num>', r)   # session 1166's, kept

    def test_the_now_view_files_the_mix_in_that_hour(self):
        n = src("site", "components", "grid", "NowView.tsx")
        self.assertIn("<div data-grid-panel={`grid_nowmix_${grid.slug}`}>", n)
        self.assertIn("rows={mixRows} />", n)
        self.assertIn("rows={mixRows.map((r) => r.cells)} />", n)
        self.assertEqual(n.count("<PanelFile "), 1)


class TheChecks(unittest.TestCase):
    def test_the_check_scripts_read_the_new_files(self):
        g = src("site", "scripts", "grid-files.mjs")
        for f in ("grid_rightnow_ercot", "grid_batteries_ercot", "grid_cost_ercot", "grid_nowmix_ercot", "grid_building_caiso", "grid_reliability_caiso_days_per_year",
                  "grid_reliability_caiso_highest_peaks", "grid_reliability_caiso_latest_days", "grid_yesterday_ercot", "grid_mixtable_all", "grid_carbonrank_ercot"):
            self.assertIn(f'"{f}"', g)
        self.assertIn('["/grid?grid=isone", ["grid_rightnow_isone", "grid_batteries_isone", "grid_yesterday_isone"]],', g)
        self.assertIn("the file writes \"license needed\" ${heldWritten} time(s)", g)
        self.assertIn('const held = gridFileProblems(f, raws).filter((x) => /license needed/.test(x));', src("site", "scripts", "check-table-downloads.mjs"))
        self.assertIn("Session 1420 (chain 111)", src("site", "scripts", "check-download.mjs"))

    @unittest.skipUnless(NODE, "node is not on this machine")
    def test_they_parse(self):
        for f in ("check-download.mjs", "check-table-downloads.mjs", "grid-files.mjs", "test-grid-files.mjs", "test-grid-render.mjs", "grid-render-standin.mjs"):
            r = subprocess.run([NODE, "--check", os.path.join("scripts", f)], cwd=SITE, capture_output=True, text=True, timeout=60)
            self.assertEqual(r.returncode, 0, f + r.stderr[-1000:])

    def test_the_tests_hold_the_files(self):
        t = src("site", "scripts", "test-grid-files.mjs")
        self.assertIn("the older blocks' files (1420): every figure in its block's file and back, a held grid's prices and queue never in a file", t)
        self.assertIn('fx("caiso_queue_positions.json")', t)
        r = src("site", "scripts", "test-grid-render.mjs")
        for fam in ("grid_rightnow_", "grid_batteries_", "grid_cost_", "grid_building_", "grid_reliability_", "grid_nowmix_"):
            self.assertTrue(re.search(r'^  \{"name": "%s' % fam, r, re.M), fam)
        self.assertIn('"name": "grid_cost_isone on /grid?grid=isone&view=mix"', r)


class TheMethodAndTheLetter(unittest.TestCase):
    def test_the_method_note(self):
        m = src("docs", "methods", "grid_network.md")
        self.assertIn("## The older blocks' files, anchors, method links and render cases (chain 111, 24 October 2026)", m)
        sec = m[m.index("## The older blocks' files, anchors"):m.index("## Not here")]
        self.assertIn("Decisions (chain 111, session 1420):", sec)

    def test_no_em_dash(self):
        for parts in (("site", "components", "grid", "YourGrid.tsx"), ("site", "components", "grid", "Reliability.tsx"), ("site", "components", "grid", "NowView.tsx"),
                      ("site", "scripts", "grid-files.mjs"), ("site", "scripts", "test-grid-files.mjs"), ("site", "scripts", "test-grid-render.mjs"),
                      ("site", "scripts", "grid-render-standin.mjs"), ("site", "scripts", "check-download.mjs"), ("site", "scripts", "check-table-downloads.mjs"),
                      ("site", "scripts", "test-grid-failed-reads.mjs"), ("docs", "methods", "grid_network.md"), ("tests", "test_session1420.py")):
            self.assertNotIn(EM, src(*parts), parts)
        if os.path.exists(os.path.join(ROOT, "archive", "sessions", "SESSION_1420_REPORT.md")):
            self.assertNotIn(EM, src("archive", "sessions", "SESSION_1420_REPORT.md"))


if __name__ == "__main__":
    unittest.main()

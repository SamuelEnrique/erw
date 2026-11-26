"""Session 10231 (chain 710, part D: the signature explorers audited, docs/reviews/explore-model-audit-2026-11-26.md,
finding 6; first found on 16 November, docs/reviews/interconnection-faults-2026-11-16.md, row 11, and left open there
because the file is shared).

Every figure of /explore/interconnection carries in its hover "Source: the ISO's own interconnection queue as the ERW
last pulled it". The table is rebuilt by hand on the data machine and the queues are pulled weekly, so the table is
often older than the last pull: on 26 November 2026 the catalogue (warehouse/metadata/coverage.csv) gives the table's
build as 16 November and CAISO's queue as pulled on 23 November. Words only. The tests run everywhere; the source
words are read with node where the site's packages are (skipped without site/node_modules).
"""
import csv
import os
import shutil
import subprocess
import unittest

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
SITE = os.path.join(ROOT, "site")


def src(*p):
    with open(os.path.join(ROOT, *p), encoding="utf-8") as f:
        return f.read()


class TheHoverSaysThePullTheTableWasBuiltFrom(unittest.TestCase):
    def test_the_catalogue_shows_the_table_older_than_the_last_pull(self):
        with open(os.path.join(ROOT, "warehouse", "metadata", "coverage.csv"), encoding="utf-8", newline="") as f:
            cat = {r["table"]: r for r in csv.DictReader(line for line in f if not line.startswith("#"))}
        built = cat["iso_queue_statistics"]["last_run"]
        pulled = cat["caiso_interconnection_queue"]["last_run"]
        if not built < pulled:
            self.skipTest(f"on this copy of the catalogue the table ({built}) is not older than CAISO's pull ({pulled})")
        self.assertLess(built, pulled)

    def test_the_source_words(self):
        s = src("site", "lib", "explore", "source.ts")
        self.assertNotIn("as the ERW last pulled it", s)
        self.assertIn('report: "the ISO\'s own interconnection queue as the ERW held it when the table was built (<iso>_interconnection_queue), computed by the ERW",', s)
        n = src("docs", "methods", "explorers.md")
        self.assertNotIn("as the ERW last pulled it", n)
        self.assertIn("as the ERW held it when the table was built (`<iso>_interconnection_queue`), which can be older than the ERW's last pull", n)
        self.assertIn("Session 10231 (26 November 2026, `docs/reviews/explore-model-audit-2026-11-26.md`, finding 6) changes them", src("docs", "methods", "interconnection_explorer.md"))

    @unittest.skipUnless(os.path.isdir(os.path.join(SITE, "node_modules")), "site/node_modules is not on this copy")
    def test_a_figures_hover_as_the_site_writes_it(self):
        node = shutil.which("node")
        if not node:
            self.skipTest("node is not on this machine")
        script = os.path.join(os.path.dirname(__file__), "audit_explore_7_source.mjs")
        r = subprocess.run([node, "--import", "./scripts/tsx-register.mjs", script], cwd=SITE, capture_output=True, text=True, encoding="utf-8", timeout=300)
        self.assertEqual(r.returncode, 0, r.stderr[-2000:])
        self.assertIn("iso_queue_statistics: CAISO's queue, entry year 2023, positions_entered, 2023. Source: the ISO's own interconnection queue as the ERW held it when the table was built (caiso_interconnection_queue), computed by the ERW. Method: Energy projects, Queue statistics.", r.stdout)


if __name__ == "__main__":
    unittest.main()

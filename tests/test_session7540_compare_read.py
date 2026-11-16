"""Session 7540 (chain 304, part C): "Where power is cheap" (/prices/compare) read as a fund analyst setting two hubs side
by side, and the site faults the read found.

The read is docs/reviews/compare-read-2026-11-16.md: numbered rows, each a site fault fixed with a test, a request of the
data machine, a browser read, a ruling or a license. The fixes are held on the page drawn whole by Node
(site/scripts/test-compare-read.mjs, run here) on the site's own file, with the license hold of the day.

    python -m unittest tests.test_session7540_compare_read -v
"""
import os
import re
import shutil
import subprocess
import unittest

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
SITE = os.path.join(ROOT, "site")
NODE = shutil.which("node")
EM_DASH = chr(0x2014)


def src(*parts):
    with open(os.path.join(ROOT, *parts), encoding="utf-8") as f:
        return f.read()


@unittest.skipUnless(NODE, "node is not installed")
@unittest.skipUnless(os.path.isdir(os.path.join(SITE, "node_modules")), "site/node_modules is not on this copy")
class ThePageDrawn(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        r = subprocess.run([NODE, "--import", "./scripts/tsx-register.mjs", "scripts/test-compare-read.mjs"], cwd=SITE, capture_output=True, text=True, encoding="utf-8", timeout=900)
        cls.code, cls.out, cls.err = r.returncode, r.stdout, r.stderr

    def test_every_check_passes(self):
        self.assertEqual(self.code, 0, self.out[-3000:] + self.err[-1500:])
        self.assertNotIn("FAIL", self.out)
        m = re.search(r"(\d+) of (\d+) checks pass", self.out)
        self.assertTrue(m and m.group(1) == m.group(2) and int(m.group(2)) >= 60, self.out[-500:])

    def test_each_site_row_of_the_read_has_its_check(self):
        for row in (3, 4, 6, 7, 8, 10, 12, 13):
            self.assertRegex(self.out, rf"(?m)^ok   row {row}: ", f"row {row} of the read is held on the drawn page")
        # row 1, the hold, is checked in four views by name
        self.assertGreaterEqual(len(re.findall(r"(?m)^ok   /prices/compare\?[^:]+: no marked number of a held row$", self.out)), 4)

    def test_no_held_figure_in_the_reads_files(self):
        self.assertRegex(self.out, r"(?m)^ok   docs/reviews/compare-read-2026-11-16\.md: none of the \d+ figures of a held row$")


class TheRead(unittest.TestCase):
    def test_every_row_has_a_kind_and_a_state(self):
        doc = src("docs", "reviews", "compare-read-2026-11-16.md")
        rows = re.findall(r"(?m)^\| (\d+) \| ([^|]+) \| ([^|]+) \| ([^|]+) \| (site|data machine|browser|ruling|license) \| ([^|]+) \|$", doc)
        self.assertEqual([int(r[0]) for r in rows], list(range(1, 23)))
        kinds = [r[4] for r in rows]
        self.assertEqual((kinds.count("site"), kinds.count("data machine"), kinds.count("browser"), kinds.count("ruling"), kinds.count("license")), (9, 5, 3, 4, 1))
        for r in rows:
            state = r[5].strip()
            if r[4] == "site":
                self.assertTrue(state.startswith("fixed"), r[0])
            if r[4] == "data machine":
                self.assertRegex(state, r"^requested \(row 1(39|4[0-8])\)", r[0])
            if r[4] == "browser":
                self.assertRegex(state, r"^wanted \(row 1(6[6-9]|7[0-5])\)", r[0])
            if r[4] == "ruling":
                self.assertTrue(state.startswith("default:"), r[0])

    def test_no_em_dash_in_what_the_session_wrote(self):
        for parts in (("docs", "reviews", "compare-read-2026-11-16.md"), ("site", "scripts", "test-compare-read.mjs"), ("site", "scripts", "font-stub-loader.mjs"),
                      ("site", "lib", "pricecompare.ts"), ("site", "app", "prices", "compare", "page.tsx"), ("site", "scripts", "check-prices-compare.mjs"),
                      ("tests", "test_session7540_compare_read.py")):
            self.assertNotIn(EM_DASH, src(*parts), parts)


if __name__ == "__main__":
    unittest.main()

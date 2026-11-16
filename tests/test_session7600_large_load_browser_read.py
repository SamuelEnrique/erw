"""Session 7600 (chain 305, part A): the large-load rules read in a browser, and the site faults the read found.

The read is docs/reviews/large-load-on-site/browser-read-2026-11-16.md: the two pages of chain 302 (the All grids tab of
/cost-of-power and the states' laws in the monitor of /policy) opened in a real browser at 1280 and 390 px on a build
of the stack, every hover measured, every control used. Its rows are numbered; a site fault is fixed and held here on
the drawn components by Node (site/scripts/test-large-load-read.mjs), a data fault names its request, a ruling its
default. What only a browser shows (a box inside the window, a column not printed over) is in the review's own
measures, taken before and after.
"""
import os
import re
import shutil
import subprocess
import unittest

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
SITE = os.path.join(ROOT, "site")
NODE = shutil.which("node")
EM_DASH, EN_DASH = chr(0x2014), chr(0x2013)
READ = ("docs", "reviews", "large-load-on-site", "browser-read-2026-11-16.md")


def src(*parts):
    with open(os.path.join(ROOT, *parts), encoding="utf-8") as f:
        return f.read()


@unittest.skipUnless(NODE, "node is not installed")
@unittest.skipUnless(os.path.isdir(os.path.join(SITE, "node_modules")), "site/node_modules is not on this copy")
class TheFixesDrawn(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        r = subprocess.run([NODE, "--import", "./scripts/tsx-register.mjs", "scripts/test-large-load-read.mjs"], cwd=SITE, capture_output=True, text=True, encoding="utf-8", timeout=900)
        cls.code, cls.out, cls.err = r.returncode, r.stdout, r.stderr

    def test_every_check_passes(self):
        self.assertEqual(self.code, 0, self.out[-3000:] + self.err[-1500:])
        self.assertNotIn("FAIL", self.out)
        m = re.search(r"(\d+) of (\d+) passed", self.out)
        self.assertTrue(m and m.group(1) == m.group(2) and int(m.group(2)) >= 40, self.out[-500:])

    def test_each_site_row_of_the_read_has_its_check(self):
        for row in range(1, 11):
            self.assertRegex(self.out, rf"(?m)^ok   rows? (\d+ and )?{row}\b", f"row {row} of the read is held on the drawn components")

    def test_a_box_is_inside_the_window_at_both_widths(self):
        for width in (1280, 390):
            self.assertRegex(self.out, rf"(?m)^ok   rows 1 and 2: at {width} px a hover's box is inside the window wherever its trigger stands \(\d+ places tried, 0 past an edge\)")


class TheRead(unittest.TestCase):
    def test_every_row_is_fixed_requested_or_written_for_a_ruling(self):
        doc = src(*READ)
        rows = re.findall(r"(?m)^\| (\d+) \| ([^|]+) \| ([^|]+) \| ([^|]+) \| (site|data machine|ruling) \| ([^|]+) \|$", doc)
        self.assertEqual([int(r[0]) for r in rows], list(range(1, len(rows) + 1)), "the rows are numbered in order")
        self.assertGreaterEqual(len(rows), 13)
        for n, _, _, _, kind, state in rows:
            if kind == "site":
                self.assertTrue(state.strip().startswith("fixed"), f"row {n}: a site fault is fixed")
            elif kind == "data machine":
                self.assertRegex(state, r"requested \(row \d+\)", f"row {n}: a data fault names its request")
            else:
                self.assertIn("default", state, f"row {n}: a ruling is written with its default")
        asked = sorted({int(x) for r in rows for x in re.findall(r"requested \(row (\d+)\)", r[5])})
        self.assertEqual(asked, [8, 9])
        # the requests file is written on main (session 7600 started it there); a branch cut before it does not hold it
        if not os.path.isfile(os.path.join(ROOT, "docs", "state", "data_requests_done_line.md")):
            return
        requests = src("docs", "state", "data_requests_done_line.md")
        for n in asked:
            self.assertRegex(requests, rf"(?m)^\| {n} \| 2026-11-16 \| 7600 ", f"request row {n} is in docs/state/data_requests_done_line.md")

    def test_the_read_says_what_was_opened_and_measured(self):
        doc = src(*READ)
        for words in ("1280", "390", "axe", "no rule broken", "17 of 17", "five rows", "A and B", "license needed"):
            self.assertIn(words, doc)
        for shot in re.findall(r"`(docs/reviews/large-load-on-site/[a-z0-9-]+\.png)`", doc):
            self.assertTrue(os.path.isfile(os.path.join(ROOT, *shot.split("/"))), f"{shot} is named and is in the folder")
        self.assertGreaterEqual(len(set(re.findall(r"`(docs/reviews/large-load-on-site/[a-z0-9-]+\.png)`", doc))), 12)

    def test_no_dash(self):
        for parts in (READ, ("site", "components", "largeload", "TipPlace.tsx"), ("site", "scripts", "test-large-load-read.mjs"), ("archive", "sessions", "SESSION_7600_REPORT.md")):
            path = os.path.join(ROOT, *parts)
            if not os.path.isfile(path):
                continue
            text = src(*parts)
            self.assertNotIn(EM_DASH, text, parts[-1])
            self.assertNotIn(EN_DASH, text, parts[-1])


class TheStyleSheet(unittest.TestCase):
    """What a browser needs and Node cannot draw: the rules are in the style sheet, after chain 302's own."""

    def test_the_rules_of_the_read_follow_chain_302s(self):
        css = src("site", "app", "tokens.css").replace("\r\n", "\n")
        at = css.index("chain 302 (session 7201): the large-load rules under the All grids tab")
        mine = css.index("chain 305 (session 7600): the browser read of the large-load rules")
        self.assertGreater(mine, at, "a later rule of the same weight wins: the read's rules stand after chain 302's")
        self.assertIn("overflow-wrap: anywhere;", css[mine:])
        self.assertIn("th:first-child:is(:hover, :focus-within)", css[mine:])

    def test_the_first_placing_is_still_the_style_sheets(self):
        css = src("site", "app", "tokens.css").replace("\r\n", "\n")
        self.assertRegex(css, r"\.brand-a \[data-llr\] span\.tip > \[role=\"tooltip\"\]\[data-tp\],\n\.brand-a \[data-allgrids\] \[data-llr\] span\.tip > \[role=\"tooltip\"\]\[data-tp\] \{\n  position: absolute;", "before the page's script has loaded a box is still placed under its trigger")


if __name__ == "__main__":
    unittest.main()

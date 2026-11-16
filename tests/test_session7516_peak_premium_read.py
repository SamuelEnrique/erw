"""Session 7516 (chain 304, part B): the ERCOT peak premium explorer read as its reader.

The page is drawn with the site's own code on real rows of its two tables (tests/fixtures/session7507: HB_HUBAVG and
HB_WEST) by site/scripts/test-peak-premium-read.mjs, which holds the five rows the read fixed on the page. The rest
reads the files: the figures of the two-hub table are variables the method note defines and the tables hold; the review
file opens on the reader, the five cases and how it was read, numbers its rows in order with a known kind, and ends on
five bullets; the shared explore files are not named as changed; and none of the session's files holds an em or an en
dash.
"""
import os
import re
import shutil
import subprocess
import unittest

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
SITE = os.path.join(ROOT, "site")
NODE = shutil.which("node")
FIXTURE = os.path.join(ROOT, "tests", "fixtures", "session7507")
COVERAGE = os.path.join(ROOT, "warehouse", "metadata", "coverage.csv")
REVIEW = ("docs", "reviews", "ercot-peak-premium-read-2026-11-16.md")
EM_DASH, EN_DASH = chr(0x2014), chr(0x2013)
MINE = (
    REVIEW, ("site", "scripts", "test-peak-premium-read.mjs"), ("tests", "test_session7516_peak_premium_read.py"),
    ("site", "app", "explore", "ercot-peak-premium", "page.tsx"), ("site", "app", "explore", "ercot-peak-premium", "Decisions.tsx"),
    ("site", "lib", "explore", "peakpremium.ts"), ("docs", "methods", "ercot_peak_premium.md"),
)
KINDS = {"site", "data machine", "browser", "ruling", "license", "key"}


def src(*parts):
    with open(os.path.join(ROOT, *parts), encoding="utf-8") as f:
        return f.read().replace("\r\n", "\n")


def side_variables():
    block = re.search(r"export const SIDE = \[(.*?)\] as const;", src("site", "lib", "explore", "peakpremium.ts"), re.S).group(1)
    return re.findall(r'\{ v: "([a-z0-9_]+)", label: "[^"]+", unit: "(USD/MWh|count)" \}', block)


@unittest.skipUnless(NODE, "node is not installed")
@unittest.skipUnless(os.path.isdir(os.path.join(SITE, "node_modules")), "site/node_modules is not on this copy")
class ThePageAsDrawn(unittest.TestCase):
    def test_the_rows_fixed_on_the_page(self):
        r = subprocess.run(
            [NODE, "--import", "./scripts/tsx-register.mjs", "scripts/test-peak-premium-read.mjs", os.path.join(FIXTURE, "ercot_peak_premium_annual.csv"),
             os.path.join(FIXTURE, "ercot_peak_premium_monthly.csv"), COVERAGE],
            cwd=SITE, capture_output=True, text=True, encoding="utf-8", timeout=900)
        self.assertEqual(r.returncode, 0, r.stdout[-3000:] + r.stderr[-2000:])
        m = re.search(r"(\d+) checks passed, (\d+) failed", r.stdout)
        self.assertTrue(m and int(m.group(1)) >= 100 and m.group(2) == "0", r.stdout[-600:])


class TheFiles(unittest.TestCase):
    def test_the_two_hub_figures_are_the_notes_and_the_tables(self):
        side = side_variables()
        self.assertEqual(len(side), 13)
        self.assertEqual(len({v for v, _ in side}), 13)
        note = src("docs", "methods", "ercot_peak_premium.md")
        with open(os.path.join(FIXTURE, "ercot_peak_premium_annual.csv"), encoding="utf-8") as f:
            held = {line.split(",")[1] for line in f if line.startswith("ercot:")}
        for v, unit in side:
            self.assertIn(f"`{v}`", note, v)
            self.assertIn(v, held, v)
            self.assertEqual(unit == "count", v.startswith("n_"), v)

    def test_the_page_keeps_what_it_had(self):
        page = src("site", "app", "explore", "ercot-peak-premium", "page.tsx")
        for kept in ("<HeadlineRow>", "data-thesis-chart", "The five numbers of each block", "The thesis's figures", "by month: the median of each block",
                     "data-related-view", "<PeakPremiumDecisions />", 'name: "hub"', 'name: "month"', 'name: "from"', 'name: "to"'):
            self.assertIn(kept, page, kept)
        self.assertIn('name: "vs"', page)
        self.assertNotIn('from "./', page)           # tests/test_session403.py: no private import on this page

    def test_the_review_file(self):
        text = src(*REVIEW)
        head = text.split("\n## ")[0]
        for opening in ("**The reader:**", "**The five cases:**", "**How it was read:**"):
            self.assertEqual(head.count(opening), 1, opening)
        self.assertIn("No click was made and no chart was seen", head)
        for n in range(1, 6):
            self.assertIn(f"({n})", head)
        rows = re.findall(r"^\| (\d+) \| ([^|]+) \| ([^|]+) \| ([^|]+) \| ([^|]+) \| ([^|]+) \|$", text, re.M)
        self.assertEqual([int(r[0]) for r in rows], list(range(1, len(rows) + 1)))
        self.assertGreaterEqual(len(rows), 10)
        for r in rows:
            self.assertIn(r[4].strip(), KINDS, r[0])
            self.assertTrue(r[5].strip(), r[0])
        self.assertEqual(sum(1 for r in rows if r[4].strip() == "site"), 5)
        self.assertEqual(sum(1 for r in rows if r[5].strip().startswith("fixed")), 5)
        end = text.split("## What this reader still cannot get from the tool, and why")[1]
        self.assertEqual(len(re.findall(r"^- \*\*", end, re.M)), 5)

    def test_no_dash(self):
        for parts in MINE:
            text = src(*parts)
            self.assertNotIn(EM_DASH, text, parts)
            self.assertNotIn(EN_DASH, text, parts)
            for code in ("u2014", "u2013"):
                self.assertNotIn(chr(92) + code, text, parts)      # nor the escape of one


if __name__ == "__main__":
    unittest.main()

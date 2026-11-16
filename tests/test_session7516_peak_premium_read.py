"""Session 7516 (chain 304, part B): the ERCOT peak premium explorer read as its reader.

The page is drawn with the site's own code on real rows of its two tables (tests/fixtures/session7507: HB_HUBAVG and
HB_WEST) by site/scripts/test-peak-premium-read.mjs, which holds the five rows the read fixed on the page. The rest
reads the files: the figures of the two-hub table are variables the method note defines and the tables hold; the review
file opens on the reader, the five cases and how it was read, numbers its rows in order with a known kind, and ends on
five bullets; the shared explore files are not named as changed; and none of the session's files holds an em or an en
dash.
"""
import json
import os
import re
import shutil
import subprocess
import sys
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
    ("replication", "ercot_peak_premium", "replicate.py"), ("replication", "ercot_peak_premium", "page_figures.json"),
    ("site", "scripts", "peak-premium-figures.mjs"),
)
REPLICATION = os.path.join(ROOT, "replication", "ercot_peak_premium")
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

    def test_the_replication_covers_the_second_hub_and_the_marks(self):
        """Every view of the fixture's two hubs, the pairs of years and the partial year and month among them: the
        replication (written from the note's section 10) meets the section of two hubs and every period's mark."""
        env = dict(os.environ, ERW_SPEND_CAP_USD="0")
        r = subprocess.run([sys.executable, os.path.join(REPLICATION, "replicate.py"), "--in-dir", FIXTURE, "--coverage", COVERAGE],
                           capture_output=True, text=True, encoding="utf-8", timeout=900, env=env)
        self.assertEqual(r.returncode, 0, r.stdout[-3000:] + r.stderr[-2000:])
        for pattern, least in ((r"(\d+) of (\d+) views open as the note says", 282), (r"(\d+) of (\d+) figures inside the tolerance", 2430),
                               (r"(\d+) of (\d+) figures of the section of two hubs", 1950), (r"(\d+) of (\d+) periods that head a figure are written as the note says", 5340)):
            m = re.search(pattern, r.stdout)
            self.assertTrue(m and m.group(1) == m.group(2) == str(least), (pattern, r.stdout[-900:]))
        self.assertIn("in 94 views with a second hub", r.stdout)


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

    def test_one_list_of_thirteen_in_the_note_the_replication_and_the_page(self):
        note = src("docs", "methods", "ercot_peak_premium.md").split("### 10. The section of two hubs and the marks")[1]
        in_note = re.findall(r"^\| \d+ \| `([a-z0-9_]+)` \|", note, re.M)
        if REPLICATION not in sys.path:
            sys.path.insert(0, REPLICATION)
        rep = __import__("replicate")
        self.assertEqual(in_note, rep.SIDE)
        self.assertEqual(in_note, [v for v, _ in side_variables()])
        self.assertNotIn("peakpremium", src("replication", "ercot_peak_premium", "replicate.py"))    # not from the page's library

    def test_the_committed_figures_cover_the_second_hub(self):
        doc = json.loads(src("replication", "ercot_peak_premium", "page_figures.json"))
        self.assertEqual(doc["views"], doc["views_as_the_note_says"])
        self.assertEqual(doc["figures"], doc["figures_inside_the_tolerance"])
        self.assertGreaterEqual(doc["views_with_a_second_hub"], 30)            # every ordered pair of six hubs, at least
        self.assertGreater(doc["two_hub_figures"], 0)
        self.assertEqual(doc["two_hub_figures"], doc["two_hub_figures_as_the_note_says"])
        self.assertEqual(doc["periods_that_head_a_figure"], doc["periods_written_as_the_note_says"])
        note = src("docs", "methods", "ercot_peak_premium.md")
        for line in (f"{doc['views']} of {doc['views']} views open as the note says", f"{doc['figures']} of {doc['figures']} figures inside the tolerance",
                     f"{doc['two_hub_figures']} of {doc['two_hub_figures']} figures of the section of two hubs, in {doc['views_with_a_second_hub']} views",
                     f"{doc['periods_that_head_a_figure']} of {doc['periods_that_head_a_figure']} periods that head a figure"):
            self.assertIn(line, note, line)

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

"""Session 7600 (chain 305, part A): the shoulder page read in a browser for the old laptop's rows 9 to 11 of
docs/state/browser_reads_wanted.md, and the one fault of the page's own words that the read found.

On /shoulder?grid=caiso-own the third headline of the second measure is "not held" for 2026 (the fleet is not held for
every ranked day), and the line under it kept the value's place in its sentence: "the batteries ran not held hours at
rated power in those shoulders". Where the figure is not held the line now says so of the hours. What the browser
showed (the folds' hovers past a phone's screen, the headline's box over its figure) is fixed for every page by the
placer of wip/7600-large-load-read, and is held there.
"""
import os
import re
import unittest

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
EM_DASH, EN_DASH = chr(0x2014), chr(0x2013)


def src(*parts):
    with open(os.path.join(ROOT, *parts), encoding="utf-8") as f:
        return f.read()


class TheLineUnderTheWorstDays(unittest.TestCase):
    def setUp(self):
        self.page = src("site", "app", "shoulder", "page.tsx").replace("\r\n", "\n")

    def test_a_figure_not_held_is_not_left_inside_the_sentence(self):
        # the held case keeps its words; the other case is a sentence of its own
        self.assertRegex(self.page, r'\{v\.year\.get\("year_worst10_mean_battery_hours"\)\s*\? <>the batteries ran <V row=\{v\.year\.get\("year_worst10_mean_battery_hours"\)\} /> hours at rated power in those shoulders</>')
        self.assertIn('<span data-battery-hours="not-held">the hours the batteries ran at rated power in those shoulders are <V row={undefined} /></span>', self.page)

    def test_the_value_drawer_says_not_held_for_a_missing_row(self):
        self.assertRegex(self.page, r'function V\(\{ row, unit \}[^\n]*\n\s*if \(!row\) return <span className="text-muted">not held</span>;')

    def test_the_sentence_is_drawn_once(self):
        self.assertEqual(len(re.findall(r"the batteries ran <V ", self.page)), 1)
        self.assertEqual(len(re.findall(r"hours at rated power in those shoulders", self.page)), 1)
        self.assertEqual(len(re.findall(r"at rated power in those shoulders are <V row=\{undefined\} />", self.page)), 1)


class TheFaultsFile(unittest.TestCase):
    def test_row_17_is_the_read_and_is_fixed(self):
        doc = src("docs", "reviews", "shoulder-faults-2026-11-16.md")
        rows = re.findall(r"(?m)^\| (\d+) \| ([^|]+) \| ([^|]+) \| ([^|]+) \| ([^|]+) \|$", doc)
        self.assertEqual([int(r[0]) for r in rows], list(range(1, 18)), "seventeen rows, numbered in order")
        last = rows[-1]
        self.assertIn("the batteries ran not held hours at rated power", last[2])
        self.assertIn("wip/7600-shoulder-read", last[3])
        self.assertEqual(last[4].strip(), "fixed")

    def test_no_dash(self):
        for parts in (("tests", "test_session7600_shoulder_read.py"), ("docs", "reviews", "shoulder-faults-2026-11-16.md"), ("site", "app", "shoulder", "page.tsx")):
            text = src(*parts)
            self.assertNotIn(EM_DASH, text, parts[-1])
            self.assertNotIn(EN_DASH, text, parts[-1])


if __name__ == "__main__":
    unittest.main()

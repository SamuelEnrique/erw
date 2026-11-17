"""Session 7602 (chain 305, the portable laptop): rows 80 and 82 of docs/state/browser_reads_wanted.md, read in a
browser at 390 px. On every event page the fold "Each event day's estimate" (site/components/EventStudy.tsx) held a
table 468 px wide with no frame of its own, so the page grew to 469 px and scrolled sideways once the fold was opened
(/events/covid-2020 and /events/uri-2021 measured). The table now scrolls inside its own frame, as the pooled table
above it does; the page stays 390 px wide.
Energy Research Warehouse (ERW)."""
import os
import re
import unittest

ROOT = os.path.abspath(os.path.join(os.path.dirname(os.path.abspath(__file__)), ".."))
DASHES = (chr(0x2014), chr(0x2013))


def src(*parts):
    with open(os.path.join(ROOT, *parts), encoding="utf-8") as f:
        return f.read()


class TheEventDayTableScrollsInItsFrame(unittest.TestCase):
    def setUp(self):
        self.s = src("site", "components", "EventStudy.tsx")

    def test_the_fold_table_is_inside_a_frame_that_scrolls(self):
        fold = self.s[self.s.index("Each event day&apos;s estimate"):]
        fold = fold[: fold.index("</details>")]
        frame, table = fold.index('<div className="overflow-x-auto">'), fold.index('<table className="mt-1 text-left text-xs">')
        self.assertLess(frame, table)
        self.assertLess(fold.index("</table>"), fold.rindex("</div>"))

    def test_every_table_of_the_component_has_a_frame(self):
        tables = len(re.findall(r"<table ", self.s))
        frames = len(re.findall(r'<div className="overflow-x-auto">', self.s))
        self.assertEqual(tables, frames)

    def test_no_dash(self):
        for ch in DASHES:
            self.assertNotIn(ch, self.s)


if __name__ == "__main__":
    unittest.main()

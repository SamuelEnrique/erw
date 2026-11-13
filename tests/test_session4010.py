"""A Digest's revision note survives the news index's hold (session 4010, chain 228, the landing desk).

Session 2207 writes one line under "The numbers" for a figure the warehouse revised after the issue was written; session
4009 extended it to US48 demand's peak hour. The issue of 12 November 2026 still showed no note: digest.ts spliced the
notes in at the end of "The numbers" before the news index's hold (21 October) rewrote the story sections by their first
lines' places in the issue as written. "What moved" begins where the notes went in, so the hold's splice began on the
notes and removed them. The notes now go in after the hold, at the same place (the hold changes only lines after "The
numbers"), and once a key: the US48 demand line is printed twice in an issue under one key.

Run on lab-desktop under node with the site's alias loader: before, the issue of 12 November rendered no note; after,
"The publisher revised the US48 demand peak hour for 11 November 2026 after this issue was written: the warehouse now
holds 488,341 MW; the issue printed 488,034 MW and keeps it as its record.", once; the 21 October fuel note as before."""

import os
import unittest

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))


def src(*parts):
    with open(os.path.join(ROOT, *parts), encoding="utf-8") as f:
        return f.read()


class TheNoteAfterTheHold(unittest.TestCase):
    def setUp(self):
        self.d = src("site", "lib", "digest.ts")
        self.body = self.d[self.d.index("export function digestMarkdown"):]

    def test_the_notes_go_in_after_the_story_sections_are_held(self):
        hold = self.body.index('if (licenseNeeded("news_index", now)) {')
        notes = self.body.index("out.splice(num.end, 0,")
        chart = self.body.index("const ch = secs.find((s) => isChart(s.title));")
        self.assertLess(hold, notes)
        self.assertLess(notes, chart)   # the chart's hold reads the shift from out.length, notes included

    def test_one_note_a_key(self):
        self.assertIn("all.findIndex((g) => g.key === f.key) === i", self.body)

    def test_the_demand_figure_is_read_and_said(self):
        self.assertIn('(f.part === "fuel" || f.part === "demand")', src("site", "lib", "digestLive.ts"))
        self.assertIn('const noun = f.part === "fuel" ? "close" : demand ? "peak hour" : "price";', self.body)


if __name__ == "__main__":
    unittest.main()

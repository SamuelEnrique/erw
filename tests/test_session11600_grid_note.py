"""Session 11600 (chain 780): the Grid tool's note on a day it does not hold cannot push the page sideways.

The read of 28 November (docs/reviews/browser-read-2026-11-28.md, row G2) found every address of the Grid tool that
draws "yesterday" 506 px wide on a 390 px screen (/grid, the seven /grid/<grid> addresses, /mix): under "Lower 48:
yesterday" a dashed note said the day was not held and gave the failed run's reason as run_status.csv holds it, and
that reason was one unbroken string (the body of a publisher's error page). The note had no place to break, so it was
490 px wide and took its column and the page with it.

site/components/grid/Conditions.tsx: the note about demand and the note about generation each break anywhere, and the
column the first stands in may shrink. What the notes say is not changed (the reason's words are the run log's, and
are data request 587).

    python -m pytest tests/test_session11600_grid_note.py
"""
import os
import unittest

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
EM = chr(0x2014)


def src(*parts):
    with open(os.path.join(ROOT, *parts), encoding="utf-8") as f:
        return f.read()


class TheNoteBreaks(unittest.TestCase):
    def setUp(self):
        self.view = src("site", "components", "grid", "Conditions.tsx")

    def test_the_demand_note_breaks_anywhere(self):
        self.assertIn('{r.note ? <p className="mb-2 border border-dashed border-rule bg-panel px-2 py-1 text-xs text-muted [overflow-wrap:anywhere]" data-conditions-note="demand">{r.note}</p> : null}', self.view)

    def test_the_generation_note_breaks_anywhere(self):
        self.assertIn('{r.genNote ? <span className="mb-1 block border border-dashed border-rule px-2 py-1 [overflow-wrap:anywhere]" data-conditions-note="generation">{r.genNote}</span> : null}', self.view)

    def test_the_notes_column_may_shrink(self):
        # a grid's child is as wide as its widest unbreakable word unless it may shrink
        i = self.view.index('<div className="grid gap-6 lg:grid-cols-[18rem_1fr]">')
        j = self.view.index('data-conditions-note="demand"')
        self.assertIn('<div className="min-w-0">', self.view[i:j])

    def test_every_note_of_the_file_breaks(self):
        # each dashed note of this file draws words a run wrote: none may be left that cannot break
        for line in self.view.splitlines():
            if "border-dashed" in line and ("r.note" in line or "r.genNote" in line):
                self.assertIn("[overflow-wrap:anywhere]", line, line.strip()[:120])

    def test_the_words_are_as_they_were(self):
        self.assertIn("showing ${day}, the latest complete day. Why: ${reason(dRun, yesterday)}", self.view)
        self.assertNotIn(EM, self.view)


if __name__ == "__main__":
    unittest.main()

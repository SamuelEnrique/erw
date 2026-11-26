"""Session 10238, the small pages' audit, finding 14 (docs/reviews/small-pages-audit-2026-11-26.md), a test only, not for
landing: /attention's footer note says "8119 of the 27419 stories held are classified (29.6 percent)". The builder
counts the stories before it leaves out those dated more than a day after the ERW read them (session 7003), which no
week holds; the weeks' stories held sum to 27,417. The note's figure is the builder's, so the fix moves a printed figure
(27,419 to 27,417; the percent stays 29.6) and is Samuel's ruling, default "left as it is".

The first class passes on main (it shows the finding); the second fails on main and would pass with the fix."""
import json
import os
import re
import unittest

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))


def data():
    with open(os.path.join(ROOT, "site", "data", "attention.json"), encoding="utf-8") as fh:
        return json.load(fh)


class TheFinding(unittest.TestCase):
    def test_the_note_counts_before_the_stories_dated_ahead_are_left_out(self):
        with open(os.path.join(ROOT, "warehouse", "derived", "attention_index.py"), encoding="utf-8") as fh:
            b = fh.read()
        self.assertIn('share = f"{len(c)} of the {len(stories)} stories held are classified', b)
        self.assertIn("stories = stories[~ahead].copy()", b)


class TheRuling(unittest.TestCase):
    def test_the_notes_stories_held_are_the_weeks_stories_held(self):
        f = data()
        m = re.match(r"(\d+) of the (\d+) stories held", f["note"])
        self.assertIsNotNone(m)
        self.assertEqual(int(m.group(2)), sum(d[1] for d in f["denominators"]))


if __name__ == "__main__":
    unittest.main()

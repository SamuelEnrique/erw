"""wip/ready-attention-count (session 11406, chain 770, part C): the other choice of the small pages audit of
26 November, finding 14 (docs/reviews/small-pages-audit-2026-11-26.md), readied for Samuel's ruling, not requested.

On main /attention's note says "8119 of the 27419 stories held are classified (29.6 percent)": the stories are counted
before warehouse/derived/attention_index.py leaves out those dated more than a day after they were read (session 7003),
which no week holds. On this branch the builder counts the weeks' stories: 27,417 on the page's file of today (the sum
of its denominators); the percent stays 29.6. The site file is rebuilt at landing by the desk (the builder reads the
classifier's raw rows, not on this machine). The audit's test (tests/test_audit_small_14.py on wip/audit-small-14) is
carried: its ruling class is checked on the builder's code, and the figures are measured from the page's file."""
import json
import os
import re
import unittest

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))


class TheWeeksStories(unittest.TestCase):
    def test_the_builder_counts_after_the_stories_dated_ahead_are_left_out(self):
        with open(os.path.join(ROOT, "warehouse", "derived", "attention_index.py"), encoding="utf-8") as fh:
            b = fh.read()
        self.assertIn('held = int(weeks["stories_week"].sum())', b)
        self.assertIn('share = f"{len(c)} of the {held} stories held are classified ({100.0 * len(c) / held:.1f} percent)', b)
        self.assertNotIn("of the {len(stories)} stories held", b)

    def test_the_figures_on_the_pages_file(self):
        with open(os.path.join(ROOT, "site", "data", "attention.json"), encoding="utf-8") as fh:
            f = json.load(fh)
        m = re.match(r"(\d+) of the (\d+) stories held are classified \((\d+\.\d) percent\)", f["note"])
        self.assertIsNotNone(m)
        classified, before = int(m.group(1)), int(m.group(2))
        after = sum(d[1] for d in f["denominators"])
        print(f"before {before}, after {after}, percent {100.0 * classified / after:.1f}")
        if before != after:                      # the file of main, not yet rebuilt at landing
            self.assertEqual((before, after), (27419, 27417))
        self.assertEqual(f"{100.0 * classified / after:.1f}", m.group(3))


if __name__ == "__main__":
    unittest.main()

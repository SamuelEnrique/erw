"""Session 10238, the small pages' audit, finding 12 (docs/reviews/small-pages-audit-2026-11-26.md): /attention's "What
rose" said each Attention Index is set "against the mean of the four weeks before (a week without a row counts as
zero)". Since session 7001 the builder takes the classified weeks among the four before: in the file of 16 November
the weeks of 12, 19 and 26 October are set against 1, 2 and 3 weeks; only the week of 2 November against four."""
import json
import os
import re
import unittest

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))


def src(*p):
    with open(os.path.join(ROOT, *p), encoding="utf-8") as fh:
        return fh.read()


class TheFile(unittest.TestCase):
    def test_early_weeks_are_set_against_fewer_than_four(self):
        b = src("warehouse", "derived", "attention_index.py")
        self.assertIn("before = [b for b in week_list[max(0, w_i - 4):w_i] if b in classified_weeks]", b)
        f = json.load(open(os.path.join(ROOT, "site", "data", "attention.json"), encoding="utf-8"))
        n = {}
        for r in f["rising"]:
            n.setdefault(f["weeks"][r[0]][:10], set()).add(r[6])
        self.assertTrue(any(min(v) < 4 for v in n.values()), n)


class TheWords(unittest.TestCase):
    def test_the_view_and_its_hovers_say_the_classified_weeks(self):
        v = src("site", "app", "attention", "AttentionView.tsx")
        self.assertNotIn("against the mean of the four weeks before (a week without a row counts as zero)", v)
        self.assertIn("against its mean over the classified weeks among the four before", v)
        self.assertNotIn('"Four weeks before %"', v)
        lib = src("site", "lib", "attention.ts")
        self.assertNotIn("the mean of the four weeks before", lib)
        self.assertIn("the mean over the classified weeks among the four before (data/attention.json, rising)", lib)

    def test_the_method_note_says_it(self):
        n = re.sub(r"\s+", " ", src("docs", "methods", "attention.md"))
        self.assertIn("so the first classified weeks are set against fewer than four", n)


if __name__ == "__main__":
    unittest.main()

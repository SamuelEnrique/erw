"""Session 10238, the small pages' audit, finding 3 (docs/reviews/small-pages-audit-2026-11-26.md): /about said the news
is scored by "the newest Sonnet-class Claude model the API lists". Since session 206 (the owner's ruling of 12 October
2026) scoring uses one fixed model, NEWS_SCORE_MODEL, claude-haiku-4-5; pick_model (the newest Sonnet-class model)
stays for the other steps."""
import os
import re
import unittest

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))


def src(*p):
    with open(os.path.join(ROOT, *p), encoding="utf-8") as fh:
        return fh.read()


class TheScorer(unittest.TestCase):
    def test_scoring_uses_the_fixed_haiku_model(self):
        s = src("warehouse", "news", "score.py")
        self.assertIn('NEWS_SCORE_MODEL = "claude-haiku-4-5"', s)
        self.assertIn("def pick_model(client, log):", s)


class ThePage(unittest.TestCase):
    def page(self):
        return re.sub(r"\s+", " ", src("site", "app", "about", "page.tsx"))

    def test_the_page_names_the_scoring_model(self):
        p = self.page()
        self.assertNotIn("A model (the newest Sonnet-class Claude model the API lists) scores every story", p)
        self.assertIn("A model (Claude Haiku 4.5, the one model fixed for scoring since 12 October 2026;", p)


if __name__ == "__main__":
    unittest.main()

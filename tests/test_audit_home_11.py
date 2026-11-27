"""Audit of the tour, finding 11 (session 10236, docs/reviews/home-model-audit-2026-11-26.md): the stop of /ai-energy
said "The energy a query to an AI model uses, as each publisher printed it". Of the page's 23 rows (site/data/
ai_energy.json) five are a company's whole consumption in a year, not a query's (the AI energy audit of tonight,
docs/reviews/ai-energy-model-audit-2026-11-26.md, finding 1). Only the tour's words are refiled here.

1. The page's file holds rows whose measure is not a query's. Passes on main.
2. The fix on this branch, words only: the stop says the figures are for a query, a training run or a company's whole
   fleet in a year. Fails on main.
Nothing here sets the environment, reads a table or makes a request."""
import json
import os
import unittest

ROOT = os.path.abspath(os.path.join(os.path.dirname(os.path.abspath(__file__)), ".."))


def src(*p):
    with open(os.path.join(ROOT, *p), encoding="utf-8") as f:
        return f.read()


class TheAiStop(unittest.TestCase):
    def test_not_every_row_is_a_query(self):
        rows = json.loads(src("site", "data", "ai_energy.json"))["rows"]
        self.assertEqual(len(rows), 23)
        text = [json.dumps(r).lower() for r in rows]
        self.assertTrue(any("query" not in t and "prompt" not in t for t in text))

    def test_the_stop_says_so(self):
        t = src("site", "lib", "tour.ts")
        self.assertNotIn("The energy a query to an AI model uses", t)
        # session 10201: merged with the AI energy audit's branch, whose words for this stop are kept
        self.assertIn("a company's whole fleet with AI among the rest, with who measured it and how.", t)


if __name__ == "__main__":
    unittest.main()

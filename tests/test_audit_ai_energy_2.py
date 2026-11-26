"""Audit of "Energy per AI query, as published" (/ai-energy), finding 2 (session 10221,
docs/reviews/ai-energy-model-audit-2026-11-26.md): the decision "no-pair" said "no two publications measure the same
thing in the same way", and the lead's hint said "Each publication measures something different ... The figures are not
comparable with one another". Two rows of two publications are one thing: the neural architecture search that produced
the Evolved Transformer, estimated by Strubell and others (2019) at 656,347 kWh (times PUE) and printed by Google's
authors (2022) at 7.5 MWh, under two different measures of the filter.

1. The page's file: the two rows name the same search in their subjects, under two measures. Passes on main.
2. The fix on this branch, words only: the decision, its line in the method note and the hint say that where two
   publications give a figure for the same thing both rows stand, with this case named; no ratio of the ERW's own is
   printed. Fails on main."""
import json
import os
import re
import unittest

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))


def src(*p):
    with open(os.path.join(ROOT, *p), encoding="utf-8") as f:
        return f.read()


def flat(s):
    return " ".join(s.split())


class OneSearchTwoPublications(unittest.TestCase):
    def test_two_rows_name_the_same_search(self):
        by = {r["event_id"]: r for r in json.loads(src("site", "data", "ai_energy.json"))["rows"]}
        s, p = by["ai_energy:strubell_2019_2"], by["ai_energy:patterson_2022_3"]
        for r in (s, p):
            self.assertIn("neural architecture search", r["x_subject"])
            self.assertIn("Evolved Transformer", r["x_subject"])
        self.assertNotEqual(s["x_title"], p["x_title"])
        self.assertNotEqual(s["x_measures"], p["x_measures"])
        self.assertEqual((s["x_value"], s["x_unit"], p["x_value"], p["x_unit"]), (656347.0, "kWh", 7.5, "MWh"))

    def test_the_words_say_both_rows_stand(self):
        dec = flat(src("site", "app", "ai-energy", "Decisions.tsx"))
        self.assertNotIn("since no two publications measure the same thing in the same way", dec)
        self.assertIn("where two give a figure for the same thing, both rows stand, each with its subject, and neither is preferred: the neural "
                      "architecture search that produced the Evolved Transformer", dec)
        page = flat(src("site", "app", "ai-energy", "page.tsx"))
        self.assertNotIn("Each publication measures something different", page)
        self.assertIn("Where two publications give a figure for the same thing (the search that produced the Evolved Transformer), both rows "
                      "stand, each with its subject.", page)
        note = src("docs", "methods", "ai_energy_published.md").split("### Decisions (session 8012)")[1]
        self.assertIn("where two publications give a figure for the same thing, both rows stand", note)
        self.assertNotIn("since no two publications measure the same thing", note)
        # no ratio of the ERW's own on the page or in its decisions
        self.assertIsNone(re.search(r"\b8[78](\.\d+)? times\b", dec + page))


if __name__ == "__main__":
    unittest.main()

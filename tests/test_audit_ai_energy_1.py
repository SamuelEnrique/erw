"""Audit of "Energy per AI query, as published" (/ai-energy), finding 1 (session 10221,
docs/reviews/ai-energy-model-audit-2026-11-26.md): the table was captioned "Every published figure of the energy of AI"
and the tour said the page holds "the energy a query to an AI model uses", but 5 of the 23 rows are a company's whole
consumption in a year (Google's total energy in 2019 and 2020, Microsoft's in 2020 and in fiscal 2025 with its offices,
Meta's data centers in 2024): AI and every other use together, wherever the company runs, and no row gives AI's share.

1. The page's file: five rows measure a fleet, none of them states AI's share or the United States. Passes on main.
2. The fix on this branch, words only: the section says what a fleet's figure holds, the caption and the tour no longer
   call every row AI's. Fails on main."""
import json
import os
import unittest

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))


def src(*p):
    with open(os.path.join(ROOT, *p), encoding="utf-8") as f:
        return f.read()


def flat(s):
    return " ".join(s.split())


class AFleetIsNotAI(unittest.TestCase):
    def test_five_rows_are_whole_fleets(self):
        rows = json.loads(src("site", "data", "ai_energy.json"))["rows"]
        fleet = [r for r in rows if r["x_measures"].startswith("energy of a fleet")]
        self.assertEqual(len(fleet), 5)
        for r in fleet:
            words = (r["x_subject"] + " " + r["x_basis"]).lower()
            self.assertNotIn("share", words)
            self.assertNotIn("united states", words)
        self.assertEqual(max(fleet, key=lambda r: r["x_value"] * (1 if r["x_unit"] == "MWh" else 1e6))["event_id"], "ai_energy:microsoft_2026_1")

    def test_the_page_says_what_a_fleet_holds(self):
        page = flat(src("site", "app", "ai-energy", "page.tsx"))
        self.assertIn("A fleet&apos;s figure is a company&apos;s whole consumption in a year, as the company reports it (its data centers, or its "
                      "data centers and offices together): AI and every other use in it, wherever the company runs them, not the United States alone. "
                      "No figure here gives AI&apos;s share of a fleet.", page)
        self.assertIn('caption="Every figure read, as printed: the energy of AI work, and of whole fleets that run AI among everything else"', page)
        self.assertNotIn("Every published figure of the energy of AI", page)
        tour = src("site", "lib", "tour.ts")
        self.assertIn("an AI query, a training run, or a company's whole fleet with AI among the rest", tour)
        self.assertNotIn("The energy a query to an AI model uses", tour)


if __name__ == "__main__":
    unittest.main()

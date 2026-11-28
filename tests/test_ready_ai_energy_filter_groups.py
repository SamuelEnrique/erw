"""The ruling readied for finding 7 of the audit of "Energy per AI query, as published" (/ai-energy), session 11407
(chain 770, part C; docs/reviews/ai-energy-model-audit-2026-11-26.md, carried over from wip/audit-ai-energy-7).

The other choice: the filter "What is measured" groups on the words before a measure's parenthesis, the qualifier kept in
the row. 13 choices become 8; "energy of a fleet in a year" shows all 5 fleet rows (3 before); "energy of a training run"
all 9 training rows (7 before); every row is under exactly one choice; no figure moves."""
import json
import os
import shutil
import subprocess
import unittest

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
NODE = shutil.which("node")


@unittest.skipUnless(NODE, "node is not on this machine")
class TheFilterGroupsAMeasure(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        r = subprocess.run([NODE, os.path.join(ROOT, "tests", "ready_ai_energy_filter_groups_measures.mjs")], capture_output=True, text=True, encoding="utf-8", timeout=120)
        assert r.returncode == 0, r.stderr
        cls.out = json.loads(r.stdout.strip().splitlines()[-1])

    def test_eight_choices_for_thirteen_wordings(self):
        self.assertEqual(self.out["distinct"], 13)
        self.assertEqual(len(self.out["choices"]), 8)
        self.assertFalse([c for c in self.out["choices"] if "(" in c])

    def test_the_fleet_choice_shows_all_five(self):
        self.assertEqual(self.out["shows"]["energy of a fleet in a year"],
                         ["ai_energy:patterson_2021_6", "ai_energy:patterson_2022_1", "ai_energy:patterson_2022_2",
                          "ai_energy:meta_2025_1", "ai_energy:microsoft_2026_1"])

    def test_the_training_choice_shows_all_nine(self):
        t = self.out["shows"]["energy of a training run"]
        self.assertEqual(len(t), 9)
        self.assertIn("ai_energy:strubell_2019_1", t)
        self.assertIn("ai_energy:strubell_2019_2", t)

    def test_every_row_under_one_choice(self):
        ids = [i for v in self.out["shows"].values() for i in v]
        self.assertEqual(len(ids), 23)
        self.assertEqual(len(set(ids)), 23)

    def test_the_row_keeps_its_qualifier(self):
        with open(os.path.join(ROOT, "site", "app", "ai-energy", "page.tsx"), encoding="utf-8") as f:
            page = f.read()
        self.assertIn("ofMeasure(F.rows, measure)", page)
        self.assertIn("{r.x_measures}</span>", page)


if __name__ == "__main__":
    unittest.main()

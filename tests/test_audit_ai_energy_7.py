"""Audit of "Energy per AI query, as published" (/ai-energy), finding 7 (session 10221,
docs/reviews/ai-energy-model-audit-2026-11-26.md), a test only, not for landing: the filter "What is measured" offers each
x_measures as worded, so a qualifier in parentheses makes a measure of its own. 13 choices hold 8 measures; a forecaster who
chooses "energy of a fleet in a year" sees 3 of the 5 fleet rows (Google's 2019 and 2020 and Microsoft's 2020, as Google's
papers cite them), not Meta's or Microsoft's own reports; "energy of a training run" shows 7 of the 9 training rows, not
Strubell and others' two.

Grouping on the words before the parenthesis would change which rows a choice shows: for the owner's ruling, default "left
as it is". These tests pass on main: they show the effect, they do not fix it."""
import json
import os
import shutil
import subprocess
import unittest

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
NODE = shutil.which("node")


@unittest.skipUnless(NODE, "node is not on this machine")
class TheFilterSplitsAMeasure(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        r = subprocess.run([NODE, os.path.join(ROOT, "tests", "audit_ai_energy_7_measures.mjs")], capture_output=True, text=True, encoding="utf-8", timeout=120)
        assert r.returncode == 0, r.stderr
        cls.out = json.loads(r.stdout.strip().splitlines()[-1])

    def test_thirteen_choices_for_eight_measures(self):
        self.assertEqual(len(self.out["choices"]), 13)
        self.assertEqual(len({c.split(" (")[0] for c in self.out["choices"]}), 8)

    def test_a_fleet_choice_shows_three_of_five(self):
        fleet = [c for c in self.out["choices"] if c.startswith("energy of a fleet")]
        self.assertEqual(len(fleet), 3)
        self.assertEqual(sum(len(self.out["shows"][c]) for c in fleet), 5)
        self.assertEqual(self.out["shows"]["energy of a fleet in a year"],
                         ["ai_energy:patterson_2021_6", "ai_energy:patterson_2022_1", "ai_energy:patterson_2022_2"])

    def test_a_training_choice_shows_seven_of_nine(self):
        self.assertEqual(len(self.out["shows"]["energy of a training run"]), 7)
        self.assertEqual(self.out["shows"]["energy of a training run (kWh times PUE)"], ["ai_energy:strubell_2019_1", "ai_energy:strubell_2019_2"])


if __name__ == "__main__":
    unittest.main()

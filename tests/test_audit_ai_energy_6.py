"""Audit of "Energy per AI query, as published" (/ai-energy), finding 6 (session 10221,
docs/reviews/ai-energy-model-audit-2026-11-26.md), a test only, not for landing: the page's figure() (site/lib/aienergy.ts)
says "digits as given", and the decision "as-printed" says "the number its publication printed". It writes the float, so
Google's "0.10 Wh" shows as 0.1 Wh and Luccioni and others' "1.0x10-4 kWh" as 0.0001 kWh (2 of 23 rows look different
from their printed words; no value moves). A value under 0.000001 in its unit would show as "0", and 3.4e-7 as "3.4e-7".

Showing the digits printed would change how two figures look: for the owner's ruling, default "left as it is".
These tests pass on main: they show the effect, they do not fix it."""
import json
import os
import shutil
import subprocess
import unittest

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
NODE = shutil.which("node")


@unittest.skipUnless(NODE, "node is not on this machine")
class TheFigureDropsPrintedDigits(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        r = subprocess.run([NODE, os.path.join(ROOT, "tests", "audit_ai_energy_6_figure.mjs")], capture_output=True, text=True, encoding="utf-8", timeout=120)
        assert r.returncode == 0, r.stderr
        cls.out = json.loads(r.stdout.strip().splitlines()[-1])
        with open(os.path.join(ROOT, "site", "data", "ai_energy.json"), encoding="utf-8") as f:
            cls.rows = {r["event_id"]: r for r in json.load(f)["rows"]}

    def test_two_rows_show_fewer_digits_than_printed(self):
        g, lu = self.rows["ai_energy:google_2025_3"], self.rows["ai_energy:luccioni_2024_3"]
        self.assertIn("0.10 Wh", g["x_printed"])
        self.assertEqual(self.out["rows"]["ai_energy:google_2025_3"], "0.1")
        self.assertIn("1.0×10−4 kWh", lu["x_printed"])
        self.assertEqual(self.out["rows"]["ai_energy:luccioni_2024_3"], "0.0001")

    def test_every_other_row_shows_its_printed_digits(self):
        same = [k for k, v in self.out["rows"].items() if v.replace(",", "") in self.rows[k]["x_printed"].replace(",", "")
                and k not in ("ai_energy:google_2025_3", "ai_energy:luccioni_2024_3")]
        self.assertEqual(len(same), 21)

    def test_a_small_value_would_show_as_zero(self):
        self.assertEqual(self.out["probes"], {"0.000001": "0.000001", "9e-7": "0", "3.4e-7": "3.4e-7"})


if __name__ == "__main__":
    unittest.main()

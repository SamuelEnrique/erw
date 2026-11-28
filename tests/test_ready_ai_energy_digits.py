"""The ruling readied for finding 6 of the audit of "Energy per AI query, as published" (/ai-energy), session 11407
(chain 770, part C; docs/reviews/ai-energy-model-audit-2026-11-26.md, carried over from wip/audit-ai-energy-6).

The other choice: each figure is written with the digits its publication printed. Google's "0.10 Wh" shows as 0.10, not
0.1; Luccioni and others' "1.0×10−4 kWh" as 1.0×10−4, not 0.0001; the other 21 rows unchanged; no value moves; a value
under 0.000001 is never shown as 0. The replication (replication/ai_energy/replicate.py) expects the same digits."""
import importlib.util
import json
import os
import shutil
import subprocess
import unittest

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
NODE = shutil.which("node")


def load_replicate():
    spec = importlib.util.spec_from_file_location("ready_ai_energy_replicate", os.path.join(ROOT, "replication", "ai_energy", "replicate.py"))
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


@unittest.skipUnless(NODE, "node is not on this machine")
class TheFigureKeepsPrintedDigits(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        r = subprocess.run([NODE, os.path.join(ROOT, "tests", "ready_ai_energy_digits_figure.mjs")], capture_output=True, text=True, encoding="utf-8", timeout=120)
        assert r.returncode == 0, r.stderr
        cls.out = json.loads(r.stdout.strip().splitlines()[-1])
        with open(os.path.join(ROOT, "site", "data", "ai_energy.json"), encoding="utf-8") as f:
            cls.rows = {r["event_id"]: r for r in json.load(f)["rows"]}

    def test_the_two_rows_show_their_printed_digits(self):
        self.assertIn("0.10 Wh", self.rows["ai_energy:google_2025_3"]["x_printed"])
        self.assertEqual(self.out["rows"]["ai_energy:google_2025_3"], "0.10")
        self.assertIn("1.0×10−4 kWh", self.rows["ai_energy:luccioni_2024_3"]["x_printed"])
        self.assertEqual(self.out["rows"]["ai_energy:luccioni_2024_3"], "1.0×10−4")

    def test_every_row_shows_digits_its_words_print(self):
        same = [k for k, v in self.out["rows"].items() if v.replace(",", "") in self.rows[k]["x_printed"].replace(",", "")]
        self.assertEqual(len(same), 23)
        self.assertEqual(len(self.out["rows"]), 23)

    def test_a_small_value_is_never_zero(self):
        self.assertEqual(self.out["probes"], {"0.000001": "0.000001", "9e-7": "9e-7", "3.4e-7": "3.4e-7"})
        self.assertEqual(self.out["printedProbe"], "9×10−7")

    def test_the_replication_expects_the_same_digits(self):
        rep = load_replicate()
        for k, row in self.rows.items():
            self.assertEqual(rep.printed_digits(row["x_value"], row["x_printed"]), self.out["rows"][k], k)

    def test_the_page_passes_the_words(self):
        with open(os.path.join(ROOT, "site", "app", "ai-energy", "page.tsx"), encoding="utf-8") as f:
            self.assertIn("figure(r.x_value, r.x_printed)", f.read())


if __name__ == "__main__":
    unittest.main()

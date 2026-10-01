"""Session 50: the home battery game v2.

Energy Research Warehouse (ERW). No network, no model, no database.
1. site/scripts/test-battery.mjs: the DP optimum equals brute force under each difficulty's rules (Hard: the reserve
   and the degradation cost) for four presets, the reserve is never crossed, Normal with the default battery scores as
   v1, the settings check and the presets, the replay's reasons.
2. The degradation default traces to its source: Lazard LCOS v10.0 (2025), residential standalone, 721 x 25 / 158,000.
3. Migration 014 adds columns only (no new table) and fills the old rows with the v1 preset.
4. The method and the questions file exist, cite their sources and hold no em dash; the page cites the ADER document.
5. The game keeps the tutorial in browser storage behind try/catch.

    python -m unittest tests.test_session50 -v
"""

import os
import re
import shutil
import subprocess
import unittest

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
SITE = os.path.join(ROOT, "site")


def src(*p):
    with open(os.path.join(ROOT, *p), encoding="utf-8") as f:
        return f.read()


class Rules(unittest.TestCase):
    @unittest.skipUnless(shutil.which("node"), "node is not installed")
    def test_dp_against_brute_force_under_each_preset(self):
        r = subprocess.run(["node", "scripts/test-battery.mjs"], cwd=SITE, capture_output=True, text=True, timeout=900)
        self.assertEqual(r.returncode, 0, r.stdout[-3000:] + r.stderr[-2000:])
        for label in ("hard, default battery", "hard, 5 kWh", "easy, 20 kWh", "normal, default battery"):
            self.assertIn(f"ok   {label}", r.stdout)
        self.assertIn("Normal with the default battery scores as v1", r.stdout)
        self.assertNotIn("FAIL", r.stdout)

    def test_degradation_default_traces_to_lazard(self):
        b = src("site", "lib", "battery.ts")
        self.assertIn("def: 0.11", b)
        self.assertAlmostEqual(round(721 * 25 / 158000, 2), 0.11)
        self.assertIn("Lazard", b)
        self.assertIn("158 MWh", b)

    def test_v1_defaults_unchanged(self):
        b = src("site", "lib", "battery.ts")
        for s in ("kwh: { label: \"Usable energy\", unit: \"kWh\", def: 13.5", "kw: { label: \"Continuous power\", unit: \"kW\", def: 5",
                  "rte: { label: \"Round-trip efficiency\", unit: \"percent\", def: 0.9", "reserve: { label: \"Backup reserve\", unit: \"percent\", def: 0.2"):
            self.assertIn(s, b)


class Schema(unittest.TestCase):
    def test_migration_adds_columns_only(self):
        m = src("warehouse", "supabase", "migrations", "014_game_v2.sql")
        self.assertNotRegex(m.lower(), r"create table")
        self.assertIn("default 'normal:13.5-5-90'", m)
        self.assertIn("grant insert (preset, difficulty) on public.game_scores to anon", m)
        self.assertNotRegex(m.lower(), r"grant select[^;]*game_plays")


class Docs(unittest.TestCase):
    def test_method_and_questions(self):
        meth = src("docs", "methods", "battery_game.md")
        q = src("docs", "reviews", "henry-questions.md")
        for t in (meth, q):
            self.assertNotIn("—", t)
        self.assertIn("ADER-Pilot-Project-Governing-Document-Phase-3.3.docx", meth)
        self.assertIn("What the game leaves out", meth)
        self.assertEqual(len(re.findall(r"^\d+\. \*\*", q, flags=re.M)), 10)
        self.assertEqual(q.count("*Decides:*"), 10)

    def test_page_cites_the_ader_document(self):
        p = src("site", "app", "play", "battery", "page.tsx")
        self.assertIn("ADER-Pilot-Project-Governing-Document-Phase-3.3.docx", p)
        self.assertIn("the Load Zone price", p)


class Game(unittest.TestCase):
    def test_storage_is_guarded(self):
        g = src("site", "app", "play", "battery", "Game.tsx")
        self.assertRegex(g, r"try \{ return window\.localStorage\.getItem\(key\); \} catch")
        self.assertRegex(g, r"try \{ window\.localStorage\.setItem\(key, v\); \} catch")
        self.assertIn("prefers-reduced-motion", g)
        for part in ("function Tutorial", "function HouseFlow", "function Replay", "function SettingsPanel"):
            self.assertIn(part, g)


if __name__ == "__main__":
    unittest.main()

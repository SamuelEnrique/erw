"""Session 289: the battery game, one page with three modes (version 5), as Samuel ruled on 14 October 2026.

Energy Research Warehouse (ERW). No network, no model, no browser (site/scripts/check-battery-game.mjs plays it).
1. One page (ruling 16): a mode picker, Easy chosen by default; ?mode=normal and ?mode=hard open those modes; the old
   full-game address (?more=1) redirects; the simple page is gone.
2. The rules (v5): the reserve at 25 percent (ruling 1a), so the default battery's reserve carries the house through
   Hard's outage; Hard's notice names the emergency (2a); the fleet of 10,000 homes beside the one battery (3a); presets
   end "-v5", v4 boards stay readable; migration 033 allows the suffix.
3. Kelsey's asks: Easy shows the whole day ahead; the day at a glance (lowest, average, highest) before each play,
   skippable; less on screen (the settings folded, the tutorial on request, one list of days).

    python -m unittest tests.test_session289 -v
"""

import json
import os
import re
import shutil
import subprocess
import unittest

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
SITE = os.path.join(ROOT, "site")
NODE = shutil.which("node")


def src(*p):
    with open(os.path.join(ROOT, *p), encoding="utf-8") as f:
        return f.read()


def node(code):
    r = subprocess.run([NODE, "--input-type=module", "-e", code], cwd=SITE, capture_output=True, text=True, timeout=120)
    assert r.returncode == 0, r.stderr
    return json.loads(r.stdout.strip().splitlines()[-1])


class OnePage(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.page = src("site", "app", "play", "battery", "page.tsx")
        cls.game = src("site", "app", "play", "battery", "Game.tsx")

    def test_the_old_address_redirects_and_the_mode_is_in_the_address(self):
        self.assertIn('if (q.more !== undefined) redirect("/play/battery?mode=normal");', self.page)
        self.assertIn('const mode: Difficulty = q.mode === "normal" || q.mode === "hard" ? q.mode : "easy";', self.page)
        self.assertIn("<Game levels={levels} top={first} presets={presets} initialMode={mode} />", self.page)
        self.assertNotIn("simple", re.sub(r"//.*", "", self.page))
        self.assertNotIn("?more=1", re.sub(r"//.*", "", self.game))
        self.assertNotIn("simple = false", self.game)

    def test_the_mode_picker_easy_first(self):
        self.assertIn('const MODES = ["easy", "normal", "hard"] as const;', self.game)
        self.assertIn('<div className="mb-2 flex flex-wrap gap-2" role="radiogroup" aria-label="Mode">', self.game)
        self.assertIn('initialMode = "easy"', self.game)
        self.assertIn("window.history.replaceState(null, \"\", `${window.location.pathname}${d === \"easy\" ? \"\" : `?mode=${d}`}`)", self.game)

    def test_below_the_play_area_the_rules_share_card_and_leaderboard(self):
        self.assertLess(self.page.index('<Section title="Play">'), self.page.index("<Section title=\"The game's rules (version 5)\">"))
        self.assertIn("<ShareCard level={level}", self.game)
        lb = self.game.index("<h3 className=\"mb-1 text-base\">Leaderboard,")
        self.assertNotIn("hidden", self.game[lb - 80:lb])

    def test_less_on_screen(self):
        self.assertNotIn("if (!seen) setTutorial(true);", self.game)                    # the tutorial on request only
        self.assertIn('{!easy ? <SettingsPanel', self.game)                             # no settings on Easy
        self.assertIn("<optgroup key={gr}", self.game)                                  # one list of days
        self.assertIn("{!easy ? <HouseFlow", self.game)
        self.assertNotIn('role="radiogroup" aria-label="Difficulty"', self.game)        # the panel no longer repeats the modes

    def test_the_day_at_a_glance(self):
        self.assertIn("const PREVIEW_MS = 5000;", self.game)
        self.assertIn("const avg = p.reduce((a, v) => a + v, 0) / p.length, lo = Math.min(...p), hi = Math.max(...p);", self.game)
        for w in ("lowest", "average", "highest", "Start now"):
            self.assertIn(w, self.game)
        self.assertIn('{phase === "preview" ? <Preview level={level} hard={difficulty === "hard"} onDone={begin} />', self.game)

    def test_hard_notice_names_the_emergency(self):
        self.assertIn("In 15 minutes: the grid emergency and the fleet call.", self.game)
        self.assertIn("{keepWords}", self.game)
        self.assertNotIn("keep charge for the house.", self.game)

    def test_the_fleet_beside_the_battery(self):
        self.assertIn("fleet of {FLEET.toLocaleString(\"en-US\")} homes: <span className=\"font-mono\">{usd((money - START_MONEY) * FLEET)}</span>", self.game)
        self.assertIn("the perfect battery&apos;s fleet: {usd(perfect.score * FLEET)}", self.game)

    def test_easy_draws_the_whole_day(self):
        self.assertIn("const wholeDay = forecast >= n;", self.game)
        self.assertIn("dashed: the rest of the day, shown ahead (Easy's forecast)", self.game)

    def test_settings_under_a_new_key(self):
        self.assertIn('const SETTINGS_KEY = "erw.battery.settings.v5";', self.game)


@unittest.skipUnless(NODE, "node is not installed")
class TheRules(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.r = node("""import * as b from './lib/battery.ts';
const r = b.rulesOf(b.DEFAULT_SETTINGS, 'hard');
console.log(JSON.stringify({ v: b.RULES_VERSION, reserve: b.DEFAULT_SETTINGS.reserve, reserveKwh: r.reserveKwh, need: b.outageDraw(r) * b.EMERGENCY.outageIntervals,
  easy: b.presetOf(b.DEFAULT_SETTINGS, 'easy'), hard: b.presetOf(b.DEFAULT_SETTINGS, 'hard'), v4: b.parsePreset('hard:13.5-5-90-r20-d0.11-solar-v4'),
  label4: b.presetLabel('normal:13.5-5-90-v4'), forecast: b.DIFFICULTIES.easy.forecastHours }));""")

    def test_v5_and_the_reserve(self):
        r = self.r
        self.assertEqual(r["v"], "v5")
        self.assertEqual(r["reserve"], 0.25)
        self.assertAlmostEqual(r["reserveKwh"], 3.375)
        self.assertAlmostEqual(r["need"], 3.162277660168379)
        self.assertGreaterEqual(r["reserveKwh"], r["need"])                           # ruling 1a: the reserve carries the house
        self.assertEqual((r["easy"], r["hard"]), ("easy:13.5-5-90-v5", "hard:13.5-5-90-r25-d0.11-v5"))
        self.assertEqual(r["v4"]["version"], "v4")                                     # a v4 board with an add-on stays readable
        self.assertEqual(r["v4"]["addons"], ["solar"])
        self.assertEqual(r["label4"], "Normal, the default battery (v4 rules)")
        self.assertEqual(r["forecast"], 24)

    def test_the_migration_allows_v5(self):
        sql = src("warehouse", "supabase", "migrations", "033_game_v5.sql")
        rx = re.search(r"preset ~ '([^']+)'", sql).group(1)
        self.assertEqual(sql.count(rx), 2)                                             # game_scores and game_plays
        for ok in ("easy:13.5-5-90-v5", "hard:13.5-5-90-r25-d0.11-v5", "hard:13.5-5-90-r25-d0.11-solar-v5", "hard:13.5-5-90-r20-d0.11-solar-v4",
                   "normal:13.5-5-90-v3", "normal:13.5-5-90"):
            self.assertRegex(ok, rx)
        for bad in ("normal:13.5-5-90-v6", "normal:13.5-5-90-v5-v5", "hard:13.5-5-90-r25-d0.11-solar-v3", "normal:13.5-5-90-v5 "):
            self.assertNotRegex(bad, rx)
        self.assertTrue(os.path.exists(os.path.join(ROOT, "warehouse", "supabase", "rollbacks", "033_game_v5.sql")))

    def test_the_battery_test_passes(self):
        r = subprocess.run([NODE, "scripts/test-battery.mjs"], cwd=SITE, capture_output=True, text=True, timeout=900)
        self.assertEqual(r.returncode, 0, r.stdout[-3000:])
        self.assertIn("ok   the default reserve covers the outage's need", r.stdout)


class TheMethod(unittest.TestCase):
    def test_version_5_is_written_down(self):
        m = src("docs", "methods", "battery_game.md")
        self.assertIn("## Version 5 (session 289)", m)
        self.assertIn("| Backup reserve | 25 percent of usable energy (20 until v5)", m)
        self.assertNotIn(chr(0x2014), m)


if __name__ == "__main__":
    unittest.main()

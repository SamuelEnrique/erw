"""Session 111: the battery game, checked for a demonstration.

The one change to the game (the emergency's announcement says how much the house will need), the marks the browser
check reads, and the guide's figures against the game's own model. The plays themselves are in a browser
(site/scripts/check-battery-game.mjs); nothing here opens one. No network.
"""
import json
import os
import shutil
import subprocess
import unittest

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


def src(*parts):
    with open(os.path.join(ROOT, *parts), encoding="utf-8") as f:
        return f.read()


def node(js):
    exe = shutil.which("node")
    if not exe:
        raise unittest.SkipTest("node is not on this machine")
    r = subprocess.run([exe, "--input-type=module", "-e", js], cwd=os.path.join(ROOT, "site"), capture_output=True, text=True, timeout=120)
    if r.returncode != 0:
        if "ERR_UNKNOWN_FILE_EXTENSION" in r.stderr or "Unknown file extension" in r.stderr:
            raise unittest.SkipTest("this node does not read TypeScript files")
        raise AssertionError(r.stderr[-2000:])
    return json.loads(r.stdout.strip().splitlines()[-1])


MODEL = ("import fs from 'node:fs'; const b = await import('./lib/battery.ts');"
         "const l = JSON.parse(fs.readFileSync('data/battery_levels.json', 'utf-8')).levels.find((x) => x.date === '2023-08-10');"
         "const run = (d, a) => { const r = b.rulesOf(b.DEFAULT_SETTINGS, d, a); const sun = a.length ? l.solar : undefined; const o = b.optimum(l.price, r, sun); const p = b.simulate(l.price, o.actions, r, sun);"
         " const em = b.emergencyOf(l.price, r); const idle = b.simulate(l.price, l.price.map(() => 0), r, sun);"
         " const greedy = em.outage ? b.simulate(l.price, l.price.map((_, i) => (i >= 52 && i < em.outage.first ? -1 : 0)), r, sun) : null;"
         " return { perfect: o.score, need: p.outageNeedKwh, reserve: r.reserveKwh, idle: idle.score, spike: em.spike, outage: em.outage, greedy: greedy && { why: greedy.why, penalty: greedy.penalty, at: greedy.outageStartKwh } }; };"
         "const calm = JSON.parse(fs.readFileSync('data/battery_levels.json', 'utf-8')).levels.find((x) => x.date === '2026-04-26');"
         "console.log(JSON.stringify({ normal: run('normal', []), easy: run('easy', []), hard: run('hard', []), solar: run('hard', ['solar']), low: Math.min(...l.price), high: Math.max(...l.price),"
         " calm: b.optimum(calm.price, b.rulesOf(b.DEFAULT_SETTINGS, 'normal', [])).score, label: b.SPIKE_LABEL }));")


class TheGuideAgainstTheModel(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.m = node(MODEL)
        cls.guide = " ".join(src("docs", "battery_game_demo.md").split())

    def test_the_figures_the_guide_gives_are_the_models(self):
        m = self.m
        self.assertIn(f"**${m['normal']['perfect']:.2f}**", self.guide)             # the perfect battery, the simple page (Normal)
        self.assertAlmostEqual(m["easy"]["perfect"], m["normal"]["perfect"])
        self.assertIn(f"**${m['hard']['perfect']:.2f}**", self.guide)
        self.assertIn(f"**${m['solar']['perfect']:.2f}**", self.guide)
        self.assertIn(f"doing nothing at all earns ${m['solar']['idle']:.2f}", self.guide)
        self.assertIn(f"{m['low']:.2f} USD/MWh", self.guide)
        self.assertIn(f"{m['high']:,.2f} USD/MWh", self.guide)
        self.assertIn(f"{round(m['calm'] * 100)} cents", self.guide)
        self.assertIn(m["label"], self.guide)

    def test_the_reserve_alone_does_not_carry_the_house_and_the_guide_says_so(self):
        h = self.m["hard"]
        self.assertLess(h["reserve"], h["need"])                                       # 2.70 kWh held back, 3.16 needed
        self.assertIn(f"the house needs {h['need']:.2f} kWh from the battery", self.guide)
        self.assertIn(f"the reserve line is at {h['reserve']:.2f} kWh, which is not enough by itself", self.guide)
        g = h["greedy"]                                                               # hold Sell from 13:00 to the outage: stopped at the reserve, then dark
        self.assertEqual(g["why"], "lights_out")
        self.assertAlmostEqual(g["at"], h["reserve"], places=6)
        self.assertIn(f"at a cost of ${g['penalty']:.0f}", self.guide)
        self.assertEqual((h["spike"]["first"], h["outage"]["first"], h["outage"]["last"]), (60, 64, 71))   # 15:00; 16:00 to 18:00

    def test_it_is_one_page_and_says_how_to_open_the_internal_view(self):
        text = src("docs", "battery_game_demo.md")
        self.assertLess(len(text.split()), 800)                               # one page
        self.assertIn("/internal/unlock?token=", text)
        self.assertNotIn(chr(0x2014), text)
        for heading in ("## Minute 0 to 2", "## Minute 2 to 5", "## If something goes wrong"):
            self.assertIn(heading, text)


class TheGame(unittest.TestCase):
    def test_the_announcement_says_how_much_the_house_will_need(self):
        game = src("site", "app", "play", "battery", "Game.tsx")
        self.assertIn("It will need <strong>{perfect.outageNeedKwh.toFixed(2)} kWh</strong> from the battery", game)
        self.assertIn("rules.reserveKwh < perfect.outageNeedKwh", game)
        self.assertIn("which is not enough by itself", game)

    def test_the_board_carries_the_marks_the_browser_check_reads(self):
        game = src("site", "app", "play", "battery", "Game.tsx")
        self.assertIn("data-game-phase={phase} data-game-idx={hud.idx} data-game-level={level.date}", game)
        check = src("site", "scripts", "check-battery-game.mjs")
        self.assertIn('"x-erw-check": "1"', check)                                    # the plays stay off the leaderboard
        for word in ("phone", "laptop", "Your day in three lines", "Emulation.setDeviceMetricsOverride", "Input.dispatchTouchEvent", "Input.dispatchKeyEvent"):
            self.assertIn(word, check)
        self.assertRegex(src("site", "lib", "release.ts"), r'"/play/battery":\s*"review"')

    def test_no_em_dash(self):
        for rel in ("site/scripts/check-battery-game.mjs", "tests/test_session111.py"):
            self.assertNotIn(chr(0x2014), src(*rel.split("/")), rel)


if __name__ == "__main__":
    unittest.main()

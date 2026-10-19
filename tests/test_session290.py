"""Session 290: the battery game's end table (Kelsey's ask 4 of 5 October 2026).

Energy Research Warehouse (ERW). No network, no model, no browser.
Every mode ends with one table of three rows: you, the perfect battery, no battery; each with what it earned, bought and
sold at what average price (lib/battery.ts's tally, which replays the scorer's own path), and one sentence under it on
why the battery earns what it does. The share card and the replay read it.

    python -m unittest tests.test_session290 -v
"""

import json
import os
import shutil
import subprocess
import unittest

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
SITE = os.path.join(ROOT, "site")
NODE = shutil.which("node")


def src(*p):
    with open(os.path.join(ROOT, *p), encoding="utf-8") as f:
        return f.read()


class TheTable(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.game = src("site", "app", "play", "battery", "Game.tsx")

    def test_three_rows_in_every_mode(self):
        self.assertIn('[["You", mine, mine.score], ["The perfect battery", perfect, perfect.score], ["No battery", null, none]]', self.game)
        self.assertIn("{ends ? <EndTable mine={ends.mine} perfect={ends.perfect} none={ends.none} rules={result.rules} big={easy} /> : null}", self.game)
        done = self.game[self.game.index('{phase === "done" && result ? ('):]
        self.assertLess(done.index("<EndTable"), done.index("<ShareCard"))   # not behind a mode
        for col in (">Earned<", ">Bought, kWh<", ">Sold, kWh<"):   # the unit in the head (the brand's tables)
            self.assertIn(col, self.game)

    def test_one_sentence_why(self):
        self.assertIn("A battery earns the spread: the perfect battery bought at an average of", self.game)
        self.assertIn("data-end-why", self.game)

    def test_the_share_card_and_the_replay_read_it(self):
        self.assertIn("No battery: ${usd(none)}.", self.game)
        self.assertIn("none={ends?.none ?? 0}", self.game)
        self.assertIn("earned={{ mine: result.mine.score, perfect: perfect.score }}", self.game)

    def test_the_hour_lost_stays_on_normal_and_hard(self):
        self.assertIn("{!easy ? <WorstHour level={level} rules={result.rules} mine={result.mine} perfect={perfect} /> : null}", self.game)
        self.assertNotIn("function EndLines(", self.game)


@unittest.skipUnless(NODE, "node is not installed")
class TheCounts(unittest.TestCase):
    def test_tally_against_the_scorer(self):
        r = subprocess.run([NODE, "--input-type=module", "-e", """import * as b from './lib/battery.ts'; import fs from 'node:fs';
const l = JSON.parse(fs.readFileSync('data/battery_levels.json', 'utf-8')).levels.find((x) => x.date === '2023-08-10');
const out = {};
for (const d of ['easy', 'normal', 'hard']) { const r = b.rulesOf(b.DEFAULT_SETTINGS, d); const o = b.optimum(l.price, r); const t = b.tally(l.price, o.actions, r); out[d] = { ...t, opt: o.score, none: b.noBattery(l.price, r) }; }
const rs = b.rulesOf(b.DEFAULT_SETTINGS, 'hard', ['solar']); out.solar = b.noBattery(l.price, rs, l.solar);
console.log(JSON.stringify(out));"""], cwd=SITE, capture_output=True, text=True, timeout=120)
        self.assertEqual(r.returncode, 0, r.stderr)
        o = json.loads(r.stdout.strip().splitlines()[-1])
        for d in ("easy", "normal", "hard"):
            t = o[d]
            self.assertAlmostEqual(t["score"], t["opt"], places=9)
            self.assertAlmostEqual((t["sellPrice"] * t["soldKwh"] - t["buyPrice"] * t["boughtKwh"]) / 1000, t["cash"], places=9)
            self.assertEqual(t["none"], 0)
            self.assertGreater(t["sellPrice"], t["buyPrice"])
        self.assertAlmostEqual(o["hard"]["score"], 48.36345717559472, places=6)   # the demo guide's figure (tests/test_session111.py)
        self.assertAlmostEqual(o["solar"], 34.32379413373751, places=6)            # the roof alone

    def test_the_battery_test_checks_it(self):
        r = subprocess.run([NODE, "scripts/test-battery.mjs"], cwd=SITE, capture_output=True, text=True, timeout=900)
        self.assertEqual(r.returncode, 0, r.stdout[-3000:])
        self.assertIn("ok   tally: sold x price less bought x price is the scorer's cash in 66 plays", r.stdout)


class TheMethod(unittest.TestCase):
    def test_written_down(self):
        m = src("docs", "methods", "battery_game.md")
        self.assertIn("## The end table (session 290)", m)
        self.assertIn("The perfect battery is the game's own optimum, not the battery tool's.", m)


if __name__ == "__main__":
    unittest.main()

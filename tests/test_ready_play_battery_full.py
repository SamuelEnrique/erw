"""A ready branch for Samuel's ruling (session 11407, chain 770 part C), from the play audit's finding 3 (session 10227,
docs/reviews/play-model-audit-2026-11-26.md; its test tests/test_audit_play_3.py on wip/audit-play-3, carried over here
and turned to assert the new rule): the battery game's battery ends the day as full as it began (game v6).

Until v5 the starting half charge was free and the charge left at the end worth nothing, so the perfect battery always
sold out and part of every score was the starting charge sold. Since v6 (site/lib/battery.ts, refillOf) what is missing
when a play ends is bought back at the day's dearest price a kWh could have been sold for, so the perfect battery ends
at least half full, and its score on each famous day on Normal equals the audit's independent programme with the battery
made to end at least half full (below, the same statement of the rules as tests/test_audit_play_2.py's).

No table, no request, no model call; the environment is read, never set."""
import json
import math
import os
import re
import shutil
import subprocess
import unittest

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
SITE = os.path.join(ROOT, "site")
NODE = shutil.which("node")
# the perfect score on Normal, free end (v5, the audit's) and ending at least half full (v6), USD (measured in the audit)
MEASURED = {
    "uri": (240.227397, 181.719291), "heat": (60.971012, 60.734028), "calm": (0.440601, 0.304087), "solar": (0.932816, 0.732766),
    "negative": (0.794891, 0.672323), "caiso-solar-noon": (0.826653, 0.777497), "caiso-duck": (12.980595, 12.360892),
}


def read(*p):
    with open(os.path.join(ROOT, *p), encoding="utf-8") as f:
        return f.read()


def best(prices, min_end=None, kwh=13.5, kw=5.0, rte=0.9):
    eta, g = math.sqrt(rte), kw * 0.25
    first, m = max(((i, sum(prices[i:i + 4]) / 4) for i in range(0, len(prices) - 3, 4)), key=lambda t: (t[1], -t[0]))
    bonus = max(0.0, m)
    layer = {round(kwh / 2 * 1e9): (kwh / 2, 0.0)}
    for i, p in enumerate(prices):
        nxt = {}
        for soc, v in layer.values():
            for a in (1, 0, -1):
                s2, w = soc, v
                if a == 1:
                    put = min(g * eta, kwh - soc)
                    if put > 0:
                        s2, w = (kwh if put == kwh - soc else soc + put), v - put / eta * p / 1000
                elif a == -1 and soc > 0:
                    take = min(g / eta, soc)
                    s2 = 0.0 if take == soc else soc - take
                    w = v + take * eta * (p + (bonus if first <= i <= first + 3 else 0.0)) / 1000
                if 5 + w < 0:
                    continue
                k = round(s2 * 1e9)
                if k not in nxt or w > nxt[k][1]:
                    nxt[k] = (s2, w)
        layer = nxt
    return max(w for s, w in layer.values() if min_end is None or s >= min_end - 1e-9)


def levels():
    return {l["slug"]: l for l in json.loads(read("site", "data", "battery_levels.json"))["levels"]}


class EndingAsFullAsItBegan(unittest.TestCase):
    def test_the_independent_programme(self):
        lv = levels()
        for slug, (free, held) in MEASURED.items():
            with self.subTest(slug=slug):
                p = lv[slug]["price"]
                self.assertAlmostEqual(best(p), free, places=5)
                self.assertAlmostEqual(best(p, min_end=6.75), held, places=5)
                self.assertLess(held, free)

    @unittest.skipUnless(NODE, "node is not installed")
    def test_the_sites_perfect_battery_now_ends_half_full(self):
        r = subprocess.run([NODE, "--input-type=module", "-e", """import * as b from './lib/battery.ts'; import fs from 'node:fs';
const out = {};
for (const l of JSON.parse(fs.readFileSync('data/battery_levels.json', 'utf-8')).levels) {
  const r = b.rulesOf(b.DEFAULT_SETTINGS, 'normal'); const o = b.optimum(l.price, r); const s = b.simulate(l.price, o.actions, r);
  const sell = b.simulate(l.price, l.price.map(() => -1), r);
  out[l.slug] = { opt: o.score, replay: s.score, end: s.soc[s.soc.length - 1], refill: s.refill, sell: sell.score, sellRefill: sell.refill };
}
console.log(JSON.stringify({ v: b.RULES_VERSION, start: b.rulesOf().start, out }));"""], cwd=SITE, capture_output=True, text=True, timeout=300)
        self.assertEqual(r.returncode, 0, r.stderr[-2000:])
        o = json.loads(r.stdout.strip().splitlines()[-1])
        self.assertEqual(o["v"], "v6")
        for slug, (free, held) in MEASURED.items():
            with self.subTest(slug=slug):
                x = o["out"][slug]
                self.assertAlmostEqual(x["opt"], held, places=5)          # the v6 perfect battery is the audit's held figure
                self.assertAlmostEqual(x["replay"], x["opt"], places=9)
                self.assertGreaterEqual(x["end"], o["start"] - 1e-9)       # it ends at least half full
                self.assertEqual(x["refill"], 0)
                self.assertGreater(x["sellRefill"], 0)                      # selling out is bought back
                self.assertLess(x["sell"], held)

    def test_the_rule_and_the_version_in_the_library(self):
        b = read("site", "lib", "battery.ts")
        self.assertIn('export const RULES_VERSION = "v6";', b)
        self.assertIn("export function refillOf(", b)
        self.assertIn("start: s.kwh * 0.5", b)                                 # it still starts half full

    def test_the_migration_allows_v6(self):
        sql = read("warehouse", "supabase", "migrations", "040_game_v6.sql")
        rx = re.search(r"preset ~ '([^']+)'", sql).group(1)
        self.assertEqual(sql.count(rx), 2)
        for ok in ("easy:13.5-5-90-v6", "hard:13.5-5-90-r25-d0.11-solar-v6", "hard:13.5-5-90-r25-d0.11-v5", "normal:13.5-5-90-v4", "normal:13.5-5-90"):
            self.assertRegex(ok, rx)
        for bad in ("normal:13.5-5-90-v7", "normal:13.5-5-90-v6-v6", "normal:13.5-5-90-v6 "):
            self.assertNotRegex(bad, rx)
        self.assertTrue(os.path.exists(os.path.join(ROOT, "warehouse", "supabase", "rollbacks", "040_game_v6.sql")))

    def test_the_page_and_the_note_say_it(self):
        page = " ".join(read("site", "app", "play", "battery", "page.tsx").split())
        self.assertIn("The battery starts half full and must end the day as full as it began", page)
        self.assertIn("The game's rules (version 6)", page)
        note = read("docs", "methods", "battery_game.md")
        self.assertIn("## Version 6 (session 11407): the battery ends the day as full as it began", note)
        self.assertIn("calm (2026-04-26) 0.4406 to 0.3041 (-31.0)", note)
        self.assertIn("to bring the battery back to its starting charge", read("site", "app", "play", "battery", "Game.tsx"))

    def test_no_em_dash(self):
        for p in (("tests", "test_ready_play_battery_full.py"), ("site", "lib", "battery.ts"), ("docs", "methods", "battery_game.md"),
                  ("site", "app", "play", "battery", "page.tsx"), ("warehouse", "supabase", "migrations", "040_game_v6.sql")):
            self.assertNotIn(chr(0x2014), read(*p))


if __name__ == "__main__":
    unittest.main()

"""Audit of the games under /play, finding 3 (session 10227, docs/reviews/play-model-audit-2026-11-26.md), for the
owner's ruling, not for landing: the battery game's score counts the starting half charge as free and the charge left at
the end as worth nothing, so the perfect battery always sells out and part of every score is the starting charge sold.

This test shows the size of the rule; it changes nothing and passes on main. Asking every play (and the perfect
battery) to end the day at least as full as it began would move the perfect score of each famous day on Normal as
below (an independent statement of the game's rules, the same as tests/test_audit_play_2.py's on its branch), and so
every leaderboard figure and share of perfect. Default: left as it is.

No table, no request, no model call; the environment is read, never set."""
import json
import math
import os
import unittest

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
# the perfect score on Normal, free end (the page's) and ending at least half full, USD (measured in the audit)
MEASURED = {
    "uri": (240.227397, 181.719291), "heat": (60.971012, 60.734028), "calm": (0.440601, 0.304087), "solar": (0.932816, 0.732766),
    "negative": (0.794891, 0.672323), "caiso-solar-noon": (0.826653, 0.777497), "caiso-duck": (12.980595, 12.360892),
}


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


class EndingAsFullAsItBegan(unittest.TestCase):
    def test_each_famous_day(self):
        with open(os.path.join(ROOT, "site", "data", "battery_levels.json"), encoding="utf-8") as f:
            lv = {l["slug"]: l for l in json.load(f)["levels"]}
        for slug, (free, held) in MEASURED.items():
            with self.subTest(slug=slug):
                p = lv[slug]["price"]
                self.assertAlmostEqual(best(p), free, places=5)
                self.assertAlmostEqual(best(p, min_end=6.75), held, places=5)
                self.assertLess(held, free)

    def test_the_rule_on_main_is_unchanged(self):
        with open(os.path.join(ROOT, "site", "lib", "battery.ts"), encoding="utf-8") as f:
            self.assertIn("start: s.kwh * 0.5", f.read())

    def test_no_em_dash(self):
        with open(os.path.join(ROOT, "tests", "test_audit_play_3.py"), encoding="utf-8") as f:
            self.assertNotIn(chr(0x2014), f.read())


if __name__ == "__main__":
    unittest.main()

"""Audit of the games under /play, finding 2 (session 10227, docs/reviews/play-model-audit-2026-11-26.md): the battery
game starts half full at no cost and counts nothing for the charge left at the end (site/lib/battery.ts: rulesOf sets
start to half the usable energy; simulate and optimum add no value for the final charge), so selling the starting
charge counts as earnings. The page said only "half full at the start". It now says the rule and its size on the calm
spring day; the method note gives the measured effect. Words only: no rule, score or figure changes. Fails on main,
passes on the branch.

No table, no request, no model call; the environment is read, never set."""
import json
import math
import os
import re
import unittest

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))


def read(rel):
    with open(os.path.join(ROOT, rel), encoding="utf-8") as f:
        return f.read()


def flat(s):
    return re.sub(r"\s+", " ", s)


def best(prices, min_end=None, kwh=13.5, kw=5.0, rte=0.9):
    """The best play of the three actions on Normal (an independent statement of the game's rules: full power or idle,
    the square root of the round trip each way, half full at the start, the fleet call's bonus), optionally ending at
    least min_end full."""
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


class StartingChargeIsFree(unittest.TestCase):
    def test_the_rule_in_the_code(self):
        src = flat(read("site/lib/battery.ts"))
        self.assertIn("start: s.kwh * 0.5", src)

    def test_its_size_on_the_calm_day(self):
        lv = {l["slug"]: l for l in json.loads(read("site/data/battery_levels.json"))["levels"]}
        p = lv["calm"]["price"]
        free, held = best(p), best(p, min_end=6.75)
        self.assertAlmostEqual(free, 0.440601, places=6)   # the demo note's 0.44, the page's perfect battery
        self.assertAlmostEqual(held, 0.304087, places=6)
        self.assertGreater(1 - held / free, 0.29)          # "nearly a third"

    def test_the_page_and_the_note_say_so(self):
        # session 11407 (v6, tests/test_ready_play_battery_full.py): the rule changed, the battery now ends the day as full
        # as it began; the page and the note say the new rule, and the note what it was until v5
        page = flat(read("site/app/play/battery/page.tsx"))
        self.assertIn("The battery starts half full and must end the day as full as it began", page)
        self.assertIn("so selling the starting charge never pays", page)
        self.assertIn("until v5 the starting charge was free and what was left at the end counted for nothing", read("docs/methods/battery_game.md"))

    def test_no_em_dash(self):
        for p in ("site/app/play/battery/page.tsx", "docs/methods/battery_game.md", "tests/test_audit_play_2.py"):
            self.assertNotIn(chr(0x2014), read(p))


if __name__ == "__main__":
    unittest.main()

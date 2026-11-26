"""Audit of the games under /play, finding 4 (session 10227, docs/reviews/play-model-audit-2026-11-26.md): the battery
game buys and sells at the wholesale real-time price (site/lib/battery.ts step: every kWh bought or sold at the
interval's price), which no household does. The method note said so; the page did not, and taught that a home battery
earns the wholesale spread. The page now says it, with the measured case: charged at Texas's average residential price
of April 2026 (EIA, 170.0 USD/MWh) and made to end the day at least half full, the perfect battery of the calm spring
day earns nothing. Words only: no rule, score or figure changes. Fails on main, passes on the branch.

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


def best_at_retail(prices, buy, min_end, kwh=13.5, kw=5.0, rte=0.9):
    """The best play of the three moves on Normal when every kWh bought costs `buy` USD/MWh and is sold at the real-time
    price with the fleet call's bonus, ending at least min_end full."""
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
                        s2, w = (kwh if put == kwh - soc else soc + put), v - put / eta * buy / 1000
                elif a == -1 and soc > 0:
                    take = min(g / eta, soc)
                    s2 = 0.0 if take == soc else soc - take
                    w = v + take * eta * (p + (bonus if first <= i <= first + 3 else 0.0)) / 1000
                k = round(s2 * 1e9)
                if k not in nxt or w > nxt[k][1]:
                    nxt[k] = (s2, w)
        layer = nxt
    return max(w for s, w in layer.values() if s >= min_end - 1e-9)


class WholesaleBothWays(unittest.TestCase):
    def test_the_code_trades_both_ways_at_the_interval_price(self):
        src = flat(read("site/lib/battery.ts"))
        self.assertIn("cash: (-bought * price) / 1000", src)
        self.assertIn("cash: (delivered * price) / 1000", src)

    def test_the_calm_day_at_retail_earns_nothing(self):
        lv = {l["slug"]: l for l in json.loads(read("site/data/battery_levels.json"))["levels"]}
        calm = lv["calm"]
        self.assertEqual(calm["date"], "2026-04-26")
        self.assertLess(max(calm["price"]), 170.0)          # every interval below the retail price: buying never pays
        self.assertAlmostEqual(best_at_retail(calm["price"], 170.0, 6.75), 0.0, places=9)

    def test_the_page_and_the_note_say_so(self):
        page = flat(read("site/app/play/battery/page.tsx"))
        self.assertIn("No household buys or sells at these wholesale prices.", page)
        self.assertIn("the perfect battery of the calm spring day would earn nothing", page)
        self.assertIn("What it is worth (session 10227, the play audit's finding 4", read("docs/methods/battery_game.md"))

    def test_the_page_makes_no_promise_the_usage_counter_reads(self):
        self.assertIsNone(re.search(r"sent or stored|never sent|nothing is uploaded", read("site/app/play/battery/page.tsx"), re.I))

    def test_no_em_dash(self):
        for p in ("site/app/play/battery/page.tsx", "docs/methods/battery_game.md", "tests/test_audit_play_4.py"):
            self.assertNotIn(chr(0x2014), read(p))


if __name__ == "__main__":
    unittest.main()

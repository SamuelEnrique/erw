"""Ruling alternative 1 of /play/battery (session 7718, 17 November 2026, branch wip/alt-play-battery-1; not a default on
main).

Energy Research Warehouse (ERW). The question (docs/reviews/ruling-impact-play-battery-2026-11-17.md, line 1): change the
game's battery (13.5 kWh and 5 kW, 2.7 hours) to one of the battery page's 2, 4 or 8 hour durations? On this branch it is
5 kW with 20 kWh, four hours (site/lib/battery.ts SETTINGS.kwh.def; 40 kWh, eight hours, is beyond the game's own
largest battery, 30 kWh). Pinned with the game's own rules (optimum, rulesOf) on its committed famous days
(site/data/battery_levels.json; site/scripts/alt-play-battery-figures.mjs): the perfect battery on Normal reads, Uri
USD 240.23 to 301.40 (+25.5 percent), the August 2023 heat 60.97 to 67.98 (+11.5), the negative-price day 0.79 to 1.01,
CAISO's duck day 12.98 to 13.48. Every player's score moves with it.

    python -m unittest tests.test_alt_play_battery_1 -v
"""

import json
import os
import subprocess
import unittest

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
SITE = os.path.join(ROOT, "site")


def figures(*args):
    p = subprocess.run(["node", "--import", "./scripts/tsx-register.mjs", "scripts/alt-play-battery-figures.mjs", *args], cwd=SITE, capture_output=True, text=True, timeout=300)
    if p.returncode != 0:
        raise AssertionError(p.stderr[-2000:])
    return json.loads(p.stdout)


class TheFourHourBattery(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.alt = figures()                 # the branch's defaults
        cls.main = figures("kwh=13.5")      # main's battery, with the same rules

    def test_the_default(self):
        self.assertEqual((self.alt["defaults"]["kwh"], self.alt["defaults"]["kw"]), (20, 5))

    def test_the_perfect_scores(self):
        for slug, main, alt in (("uri", 240.23, 301.40), ("heat", 60.97, 67.98), ("negative", 0.79, 1.01), ("caiso-duck", 12.98, 13.48)):
            self.assertEqual((round(self.main[slug]["perfect"], 2), round(self.alt[slug]["perfect"], 2)), (main, alt), slug)

    def test_the_start_is_half_the_battery(self):
        self.assertEqual((self.main["uri"]["start"], self.alt["uri"]["start"]), (6.75, 10))


if __name__ == "__main__":
    unittest.main()

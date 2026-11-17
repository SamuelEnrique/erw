"""Ruling alternative 2 of /play/battery (session 7718, 17 November 2026, branch wip/alt-play-battery-2; not a default on
main).

Energy Research Warehouse (ERW). The question (docs/reviews/ruling-impact-play-battery-2026-11-17.md, line 2): count the
score net of the starting charge (half full, valued at the day's first price)? On this branch every score, the player's
and the perfect battery's, subtracts the start's value (site/lib/battery.ts startValue, in simulate and optimum). Pinned
with the game's own rules on its committed famous days (site/scripts/alt-play-battery-figures.mjs): the perfect battery on
Normal, Uri USD 240.23 to 181.88 (the 6.75 kWh at the first interval's USD 8,644.11 per MWh are worth 58.35; -24.3
percent); the calm day 0.44 to 0.26; the solar day 0.93 to 0.77; the heat day 60.97 to 60.78; the negative-price day 0.79
to 1.01 (the start is worth less than nothing at -31.57). A play of no move scores minus the start's value (Uri -58.35):
the end charge is not valued, as the ruling's line does not ask it to be.

    python -m unittest tests.test_alt_play_battery_2 -v
"""

import json
import os
import subprocess
import unittest

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
SITE = os.path.join(ROOT, "site")


class NetOfTheStart(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        p = subprocess.run(["node", "--import", "./scripts/tsx-register.mjs", "scripts/alt-play-battery-figures.mjs"], cwd=SITE, capture_output=True, text=True, timeout=300)
        if p.returncode != 0:
            raise AssertionError(p.stderr[-2000:])
        cls.f = json.loads(p.stdout)

    def test_the_perfect_scores(self):
        for slug, alt in (("uri", 181.88), ("calm", 0.26), ("solar", 0.77), ("heat", 60.78), ("negative", 1.01)):
            self.assertEqual(round(self.f[slug]["perfect"], 2), alt, slug)

    def test_the_starts_value(self):
        self.assertEqual((round(self.f["uri"]["start"], 2), self.f["uri"]["first"]), (58.35, 8644.11))
        self.assertLess(self.f["negative"]["start"], 0)

    def test_a_play_of_no_move(self):
        self.assertAlmostEqual(self.f["uri"]["idle"], -self.f["uri"]["start"], places=9)


if __name__ == "__main__":
    unittest.main()

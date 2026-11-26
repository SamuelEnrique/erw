"""Audit of the games under /play, finding 6 (session 10227, docs/reviews/play-model-audit-2026-11-26.md): the battery
game's modes line said Normal and Hard have "no forecast", yet the fleet call's notice tells the player, 15 minutes
ahead, that the next hour is the day's dearest (Game.tsx: the notice at vpp.first - 1; lib/battery.ts vppHour reads the
whole day's prices). Knowing that hour is worth at least the call's bonus, 25 percent of the newest ERCOT day's perfect
score in the audit. The words now say so (lib/battery.ts DIFFICULTIES, shown in the page's rules), and the method note's
table too. Words only: no rule, score or figure changes. Fails on main, passes on the branch.

No table, no request, no model call; the environment is read, never set."""
import os
import re
import unittest

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))


def read(rel):
    with open(os.path.join(ROOT, rel), encoding="utf-8") as f:
        return f.read()


def flat(s):
    return re.sub(r"\s+", " ", s)


class TheDearestHourIsAnnounced(unittest.TestCase):
    def test_the_code_announces_it(self):
        game = flat(read("site/app/play/battery/Game.tsx"))
        self.assertIn("const notice = playing && hud.idx === vpp.first - 1;", game)
        self.assertIn("Fleet call in 15 minutes: the grid&apos;s dearest hour of the day.", game)

    def test_the_modes_say_so(self):
        src = flat(read("site/lib/battery.ts"))
        self.assertIn('what: "no forecast, except that the fleet call\'s notice names the day\'s dearest hour 15 minutes before it begins; no reserve, no degradation cost"', src)
        self.assertIn('what: "no forecast, except the same notice of the day\'s dearest hour; the backup reserve', src)
        self.assertNotIn('what: "no forecast, no reserve, no degradation cost"', src)
        self.assertIn("the play audit's finding 6", read("docs/methods/battery_game.md"))

    def test_the_page_shows_the_modes_line(self):
        page = flat(read("site/app/play/battery/page.tsx"))
        self.assertIn("Normal: {DIFFICULTIES.normal.what}. Hard: {DIFFICULTIES.hard.what}.", page)

    def test_no_em_dash(self):
        for p in ("site/lib/battery.ts", "docs/methods/battery_game.md", "tests/test_audit_play_6.py"):
            self.assertNotIn(chr(0x2014), read(p))


if __name__ == "__main__":
    unittest.main()

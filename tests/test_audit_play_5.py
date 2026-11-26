"""Audit of the games under /play, finding 5 (session 10227, docs/reviews/play-model-audit-2026-11-26.md): three words
of the battery game's end table (site/app/play/battery/Game.tsx, EndTable) said what the code does not do.

- "You" said the play is scored "on the day's real prices"; on Hard the emergency hour is traded at the game's prices
  (lib/battery.ts emergencyOf). The hover now says so on Hard.
- "The perfect battery" said "the same battery"; it is held to the game's three moves (optimum tries 1, 0 and -1 only),
  and a battery free to run at part power earns up to 2.7 percent more on the levels held. The hover now says so, and
  keeps "the most any play of this day could earn", which is true.
- The sentence under the table said "$0.11 of wear on each kWh it sells"; wear is charged per kWh taken out of the
  battery, before the outbound loss (step: wear = taken x deg), so per kWh sold it is 0.11 / sqrt(0.9) = 0.116. It now
  says "on each kWh taken out of it".

Words only: no rule, score or figure changes. Fails on main, passes on the branch.

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


class EndTableWords(unittest.TestCase):
    def test_the_code(self):
        src = flat(read("site/lib/battery.ts"))
        self.assertIn("wear: taken * r.deg", src)                     # per kWh taken out
        self.assertIn("for (const a of [1, 0, -1] as Action[])", src)  # the optimum's three moves
        self.assertIn("if (p[i] < EMERGENCY.cap) p[i] = p[i] + (EMERGENCY.cap - p[i]) * EMERGENCY.ramp[k];", src)

    def test_the_words(self):
        game = flat(read("site/app/play/battery/Game.tsx"))
        self.assertNotIn("of wear on each kWh it sells", game)
        self.assertIn("of wear on each kWh taken out of it", game)
        self.assertIn('${rules.emergency ? ", except the emergency hour, traded at the game\'s prices" : ""}', game)
        self.assertIn("held to the game's three moves (charge at full power, sell at full power, or hold)", game)
        self.assertIn("The most any play of this day could earn; a battery free to run at part power could earn a little more.", game)

    def test_no_em_dash(self):
        for p in ("site/app/play/battery/Game.tsx", "tests/test_audit_play_5.py"):
            self.assertNotIn(chr(0x2014), read(p))


if __name__ == "__main__":
    unittest.main()

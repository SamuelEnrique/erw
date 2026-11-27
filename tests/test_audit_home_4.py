"""Audit of the home page, finding 4 (session 10236, docs/reviews/home-model-audit-2026-11-26.md): the Economics figure is
l12_kw:total of the battery tool's default inputs (site/lib/batterystack.ts, inputsOf({})): ERCOT, 4 hours, strategy
"foresight", perfect foresight of prices ("energy at the hourly real-time price and ancillary services at day-ahead
prices, all known in advance", the battery page's own line). The note read "What a 100 MW, 4-hour battery in ERCOT
earned", as if it were a battery's earnings; a figure per kW does not depend on the size.

1. The default strategy is perfect foresight, and the figure is per kW. Passes on main.
2. The fix on this branch, words only: the note says it is the model's battery with perfect foresight, per kW of power.
   No figure moves. Fails on main.
Nothing here sets the environment, reads a table or makes a request."""
import os
import re
import unittest

ROOT = os.path.abspath(os.path.join(os.path.dirname(os.path.abspath(__file__)), ".."))


def src(*p):
    with open(os.path.join(ROOT, *p), encoding="utf-8") as f:
        return f.read()


class TheEconomicsNote(unittest.TestCase):
    def test_the_default_is_perfect_foresight(self):
        bs = src("site", "lib", "batterystack.ts")
        self.assertIn('const strat = (q.strat === "dayahead" ? "dayahead" : "foresight") as Strategy;', bs)
        self.assertIn('case "l12_kw": return l12 ? sumOf(l12, b) / 1000 : null;', bs)
        self.assertIn("const bx = BS.inputsOf({});", src("site", "app", "page.tsx"))

    def test_the_note_says_so(self):
        page = src("site", "app", "page.tsx")
        self.assertNotIn("What a 100 MW, 4-hour battery in ERCOT earned", page)
        self.assertIn("note: `What the model's 4-hour battery in ERCOT would have earned with perfect foresight of prices, ${BS.monthName(l12[0].m)} to ${BS.monthName(l12[11].m)}, per kW of power.`", page)


if __name__ == "__main__":
    unittest.main()

"""Audit of the project map, finding 5 (session 10216, docs/reviews/map-model-audit-2026-11-26.md): the decision on
retired units said "nothing since the inventory's month is in it", beside queue positions and datacenters of later
days (the copy of 19 November 2026: units of 2026-09, queue 2026-11-05, datacenters 2026-11-15). And a mark's
diameter is 2 + 0.2 times the square root of MW, held at 3 px below 25 MW: 69.5 percent of the operating units are
drawn at one size, and a datacenter is always one size, while the note said "its area grows with its MW" and the key
"size: MW". No figure moves.

1. Through the page's file and the drawing's rule. Passes on main.
2. The fix on this branch, words only. Fails on main."""
import json
import os
import unittest

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))


def src(*p):
    with open(os.path.join(ROOT, *p), encoding="utf-8") as f:
        return f.read()


class TheMonthAndTheSize(unittest.TestCase):
    def test_the_file_and_the_rule(self):
        f = json.loads(src("site", "data", "map.json"))
        self.assertGreater(f["vintages"]["queue"], f["vintage"], "the queue positions are of a later day than the units' month")
        self.assertGreater(f["vintages"]["datacenter"], f["vintage"])
        page = src("site", "app", "map", "ProjectMap.tsx")
        self.assertIn("Math.min(18, Math.max(3, 2 + Math.sqrt(Math.max(mw ?? 0, 0)) * 0.2))", page)
        self.assertIn('symbol: "diamond", symbolSize: 9', page)
        op = [f["mw"][i] for i in range(len(f["k"])) if f["k"][i] == 0]
        self.assertGreater(sum(1 for x in op if x < 25), len(op) / 2, "most operating units are drawn at the smallest size")

    def test_the_words(self):
        dec = src("site", "app", "map", "Decisions.tsx")
        self.assertIn("nothing since the inventory's month is in its units (the queue positions and the datacenters are of their own, later days, in the source line)", dec)
        page = src("site", "app", "map", "ProjectMap.tsx")
        self.assertIn('<li className="text-muted">size: MW, above 25 MW (smaller rows and every datacenter at one size)</li>', page)
        note = src("docs", "methods", "energy_projects.md")
        self.assertNotIn("its area grows with its MW", note)
        self.assertIn("finding 5", note)
        for text in (dec, page, note):
            self.assertNotIn(chr(0x2014), text)


if __name__ == "__main__":
    unittest.main()

"""Session 11408 (chain 770, part C): the deal comparables, the other choice of the deals audit's finding 6
(docs/reviews/deals-model-audit-2026-11-26.md): a median needs five deals that state the figure, not three. Not for
landing until the owner rules.

Measured on the warehouse's rows (583 rows, 578 deals folded), through the page's own comparables(): 13 medians on
origin/main (by type M&A 892, other 810, PPA 348, offtake 50, behind the meter 450; by technology nuclear 960, gas 896,
data center 50, solar 322, not stated 330; by grid ERCOT 222, not stated 509; by year 2026 423), 8 here (M&A's,
offtake's, behind the meter's, solar's and ERCOT's go; the rest unchanged). No median price on either.

1. Through the page's library (site/lib/deals2.ts, run by Node): the floor is five and its words "fewer than five";
   four figures give no median, five give the middle one.
2. The replication (replication/deals/replicate.py) holds the same floor.
3. The decision's words, in the decisions list and the method notes, say five."""
import json
import os
import subprocess
import unittest

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
LIB = "file:///" + os.path.join(ROOT, "site", "lib", "deals2.ts").replace("\\", "/")
JS = """
const D = await import(%s);
console.log(JSON.stringify({ min: D.MIN_DISCLOSED, fewer: D.FEWER,
  med: [D.medianOf([65, 892, 5400, 100]), D.medianOf([65, 892, 5400, 100, 300])] }));
""" % json.dumps(LIB)


def src(*p):
    with open(os.path.join(ROOT, *p), encoding="utf-8") as f:
        return f.read()


class AMedianNeedsFive(unittest.TestCase):
    def test_the_library(self):
        out = subprocess.run(["node", "--input-type=module"], input=JS, capture_output=True, text=True, timeout=120)
        self.assertEqual(out.returncode, 0, out.stderr)
        got = json.loads(out.stdout.strip().splitlines()[-1])
        self.assertEqual((got["min"], got["fewer"]), (5, "fewer than five"))
        self.assertEqual(got["med"], [None, 300])

    def test_the_replication(self):
        r = src("replication", "deals", "replicate.py")
        self.assertIn("return statistics.median(xs) if len(xs) >= 5 else None", r)
        self.assertIn("if len(ps) >= 5:", r)

    def test_the_words(self):
        self.assertIn('def: "Five deals."', src("site", "lib", "decisions.ts"))
        self.assertIn("**Default:** Five deals.", src("docs", "methods", "deal_tracker.md"))
        self.assertIn("Nothing is computed from fewer than five disclosed deals", src("docs", "methods", "energy_deals.md"))
        self.assertIn("computes nothing from fewer than five deals", src("site", "app", "deals", "Decisions.tsx"))
        for f in (("site", "lib", "decisions.ts"), ("docs", "methods", "deal_tracker.md"), ("docs", "methods", "energy_deals.md")):
            self.assertNotIn(chr(0x2014), src(*f))


if __name__ == "__main__":
    unittest.main()

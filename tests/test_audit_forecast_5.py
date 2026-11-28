"""Audit of /forecast, finding 5 (session 11402, docs/reviews/forecast-model-audit-2026-11-28.md): the backtest reads each
day's demand as revised at the build, while a live forecast reads day A as first published; the method note's "What was
known when" did not say so.

1. Against three builds of the place files a day apart (passes on main; skipped where git history is shallow):
   0cdfd65ad (tables through 24 November 2026), e5f755eda (through 25 November): the 24 November hours, first published
   in the first, changed in the second in at least 150 of 696 place-hours, by under 0.2 percent on mean, while the
   older days changed far less.
2. The fix on this branch (fails on main): the note's section 2 says it, with the measure."""
import json
import os
import subprocess
import unittest

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
NOTE = os.path.join(ROOT, "docs", "methods", "predict.md")
V1, V2 = "0cdfd65ad", "e5f755eda"


def show(commit, name):
    got = subprocess.run(["git", "-C", ROOT, "show", f"{commit}:site/data/predict/{name}"], capture_output=True)
    return json.loads(got.stdout.decode("utf-8")) if got.returncode == 0 else None


class Revisions(unittest.TestCase):
    def test_the_newest_day_is_revised_after_its_first_publication(self):
        idx = show(V1, "index.json")
        if idx is None:
            self.skipTest("the builds' commits are not in this clone")
        new = [0, 0, 0.0]
        old = [0, 0, 0.0]
        for p in idx["places"]:
            a = show(V1, p["file"])["series"]["demand"]
            b = show(V2, p["file"])["series"]["demand"]
            c = a["history_columns"]
            ia, ib = c.index("actual"), b["history_columns"].index("actual")
            last = max(r[1] for r in a["history"] if r[ia] is not None)
            B = {r[0]: r[ib] for r in b["history"]}
            for r in a["history"]:
                x, y = r[ia], B.get(r[0])
                if x is None or y is None or x <= 0:
                    continue
                g = new if r[1] == last else old
                g[0] += 1
                g[1] += abs(y - x) > 0.05
                g[2] += abs(y - x) / x * 100
        self.assertEqual(new[0], 696)
        self.assertGreaterEqual(new[1], 150)
        self.assertLess(new[2] / new[0], 0.2)
        self.assertLess(old[1] / old[0], new[1] / new[0] / 5)

    def test_the_note_says_the_backtest_reads_revised_demand(self):
        with open(NOTE, encoding="utf-8") as f:
            t = f.read()
        self.assertIn("The backtest reads the demand as revised", t)
        self.assertIn("184 of its 696 place-hours", t)


if __name__ == "__main__":
    unittest.main()

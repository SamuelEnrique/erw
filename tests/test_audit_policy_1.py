"""Audit of the policy monitor, finding 3 (session 10217, docs/reviews/policy-model-audit-2026-11-26.md): the monitor view
of /policy opens at significance 5 or more, and a record with no score is below every floor (lib/policymonitor.ts,
filterRows: `(r.significance ?? -1) >= f.minSig`). The calendar's count of the month ahead's steps the floor hides said
they are "on records scored below significance 5", and the Reset's hover named the floor alone. On the file of 25
November 2026, 56 records hold no score (44 of them of November), and 18 of the 94 hidden steps are theirs.

1. Through the page's file: records with no score exist, are left out as the view opens, and hold hidden steps. Passes
   on main.
2. The fix on this branch, words only: the lift's hover and the Reset's hover say a record not scored is below every
   floor. Fails on main."""
import datetime as dt
import json
import os
import re
import unittest

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))


def src(*p):
    with open(os.path.join(ROOT, *p), encoding="utf-8") as f:
        return f.read()


class TheFloorSaysItHidesTheUnscored(unittest.TestCase):
    def test_a_record_with_no_score_is_below_every_floor(self):
        lib = src("site", "lib", "policymonitor.ts")
        self.assertIn("(f.minSig === null || (r.significance ?? -1) >= f.minSig)", lib)
        self.assertIn("export const OPEN_FILTERS: Filters = { ...NO_FILTERS, minSig: 5 };", lib)
        rows = json.loads(src("site", "data", "policy", "monitor.json"))["rows"]
        unscored = [r for r in rows if r.get("significance") is None]
        self.assertGreater(len(unscored), 0)
        # each such record carries steps the month ahead may show, and the floor hides them all
        days = {r["date"][:7] for r in unscored}
        self.assertTrue(days)
        self.assertTrue(any(re.match(r"\d{4}-\d{2}-\d{2}$", s["date"]) for r in unscored for s in r.get("steps", [])))

    def test_the_hovers_say_it(self):
        cal = src("site", "app", "policy", "MonitorCalendar.tsx")
        view = src("site", "app", "policy", "MonitorView.tsx")
        self.assertIn("Steps on records scored below significance ${floor}, or not scored at all", cal)
        self.assertIn("A record not scored (the newest documents, and the grid operators' and FERC's large-load orders, which are never "
                      "scored) is below every floor: it is shown only with Significance set to All.", view)


if __name__ == "__main__":
    unittest.main()

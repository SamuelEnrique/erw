"""Audit of the policy monitor, finding 5 (session 10217, docs/reviews/policy-model-audit-2026-11-26.md): with a state
chosen, the states' laws block links that state's utilities' rules "(N changes in the last 90 days)". N counts every
change of the page file (site/data/siting/large_load_rules.json, built 16 November 2026 from
utility_large_load_rule_changes, "15 August to 13 November 2026"; app/policy/page.tsx, countByState over ll.changes),
whatever the page's day. Counted against the 90 days to 26 November 2026 (from 28 August), 14 of the 94 public changes
fall outside: Texas 13 against 10, Michigan 3 against 1, Pennsylvania 16 against 15.

1. Through the page's file: changes dated more than 90 days before 26 November 2026 are counted. Passes on main.
2. The fix on this branch, words only: the line says "in the 90 days to 13 November 2026", as the All grids tab's caption
   does; the note says the same. Fails on main."""
import datetime as dt
import json
import os
import re
import unittest

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))


def src(*p):
    with open(os.path.join(ROOT, *p), encoding="utf-8") as f:
        return f.read()


class TheChangesSayTheirWindow(unittest.TestCase):
    def test_every_change_of_the_file_is_counted(self):
        page = src("site", "app", "policy", "page.tsx")
        self.assertIn("changes: countByState(ll.changes.map((c) => c.state))", page)
        f = json.loads(src("site", "data", "siting", "large_load_rules.json"))
        dates = sorted(c["date"] for c in f["changes"])
        self.assertLessEqual(dates[-1], "2026-11-13")
        since = (dt.date(2026, 11, 26) - dt.timedelta(days=90)).isoformat()
        self.assertGreater(sum(1 for d in dates if d < since), 0)

    def test_the_line_says_the_window(self):
        laws = src("site", "app", "policy", "StateLaws.tsx")
        self.assertIn('changes"} in the 90 days to 13 November 2026)', laws)
        self.assertNotIn("in the last 90 days", laws)
        self.assertIn("the count of changes in the 90 days to 13 November 2026 (every change of `utility_large_load_rule_changes`",
                      src("docs", "methods", "policy_monitor.md"))
        self.assertTrue(re.search(r"changes\? in the 90 days to 13 November 2026", src("site", "scripts", "test-large-load-render.mjs")))


if __name__ == "__main__":
    unittest.main()

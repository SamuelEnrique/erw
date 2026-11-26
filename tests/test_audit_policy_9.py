"""Audit of the policy monitor, finding 3's figure (session 10217, docs/reviews/policy-model-audit-2026-11-26.md), a test
that shows it; not for landing. The words are fixed on wip/audit-policy-1; this is the other choice, for the owner.

The view opens at significance 5 or more, and a record with no score is below every floor (lib/policymonitor.ts,
filterRows). Records with no score are the newest documents (the scorer runs after the connector) and the large-load
orders of FERC and the grid operators, which are never scored (warehouse/policy/monitor_site.py, change_actions: no
significance). On the file of 25 November 2026: 56 records hold no score, 44 of them of November; 13 hold a step in the
month ahead, 18 of the 94 steps the floor hides. The other choice, a record with no score shown at the opening floor:
295 shown to 351 (+56, +19.0 percent). Default: left as it is.

1. As it opens, no record without a score is shown, and some exist. Passes on main.
2. The other choice, counted on the same file: every record of score 5 or more plus every record with none."""
import json
import os
import unittest

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))


def rows():
    with open(os.path.join(ROOT, "site", "data", "policy", "monitor.json"), encoding="utf-8") as f:
        return json.load(f)["rows"]


class RecordsWithNoScoreAreHiddenAsTheViewOpens(unittest.TestCase):
    def test_as_it_opens(self):
        rs = rows()
        opened = [r for r in rs if (r.get("significance") if r.get("significance") is not None else -1) >= 5]
        unscored = [r for r in rs if r.get("significance") is None]
        self.assertGreater(len(unscored), 0)
        self.assertFalse(any(r.get("significance") is None for r in opened))

    def test_the_other_choice(self):
        rs = rows()
        opened = sum(1 for r in rs if r.get("significance") is not None and r["significance"] >= 5)
        other = sum(1 for r in rs if r.get("significance") is None or r["significance"] >= 5)
        self.assertGreater(other, opened)


if __name__ == "__main__":
    unittest.main()

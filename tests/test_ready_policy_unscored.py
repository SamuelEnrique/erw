"""Ready branch for the policy monitor (session 11408, chain 770 part C; weekend page 2026-11-28, part 3.3, the policy
monitor; audit docs/reviews/policy-model-audit-2026-11-26.md, finding 3, test wip/audit-policy-9). Not the default:
it waits for Samuel's ruling.

The other choice: a record with no score (the newest documents and the large-load orders, never scored) passes every
significance floor, so it shows as the view opens (lib/policymonitor.ts, filterRows). On the page's file of 25 November
2026 the opening view shows 295 records on main and 351 here (+56).

1. The rule in the code and the hovers' words.
2. The count on the page's own file, by the same rule as filterRows."""
import json
import os
import unittest

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))


def src(*p):
    with open(os.path.join(ROOT, *p), encoding="utf-8") as f:
        return f.read()


def rows():
    return json.loads(src("site", "data", "policy", "monitor.json"))["rows"]


def passes(r, floor):
    s = r.get("significance")
    return floor is None or s is None or s >= floor


class ARecordWithNoScorePassesEveryFloor(unittest.TestCase):
    def test_the_rule(self):
        lib = src("site", "lib", "policymonitor.ts")
        self.assertIn("(f.minSig === null || r.significance === undefined || r.significance === null || "
                      "r.significance >= f.minSig)", lib)
        self.assertNotIn("(r.significance ?? -1) >= f.minSig", lib)
        self.assertIn("export const OPEN_FILTERS: Filters = { ...NO_FILTERS, minSig: 5 };", lib)

    def test_the_hovers(self):
        view = src("site", "app", "policy", "MonitorView.tsx")
        cal = src("site", "app", "policy", "MonitorCalendar.tsx")
        self.assertIn("passes every floor: it is shown at any significance setting.", view)
        self.assertNotIn("it is shown only with Significance set to All", view)
        self.assertIn("is shown at every floor); this lifts the floor", cal)
        self.assertIn("a record with no score\npasses every significance floor", src("docs", "methods", "policy_monitor.md"))

    def test_the_opening_count(self):
        rs = rows()
        unscored = [r for r in rs if r.get("significance") is None]
        self.assertGreater(len(unscored), 0)
        opened = [r for r in rs if passes(r, 5)]
        self.assertTrue(all(r in opened for r in unscored))
        old = sum(1 for r in rs if r.get("significance") is not None and r["significance"] >= 5)
        self.assertEqual(len(opened), old + len(unscored))


if __name__ == "__main__":
    unittest.main()

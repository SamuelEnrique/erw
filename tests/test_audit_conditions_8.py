"""Session 10219 (chain 710, the conditions audit, finding 8): /conditions said ERCOT's scarcity strip "ended on 4
December 2025" and nothing more, so its opening view (ERCOT, the newest days) reads as a grid with no scarcity signal.
The adder ended because ERCOT changed how it prices scarcity: since 5 December 2025 it clears energy and ancillary
services together in real time, and scarcity is priced through the ancillary services' own demand curves
(docs/methods/ercot_rt_price_adders.md). Words only: the decision and the empty strip say so.
docs/reviews/conditions-model-audit-2026-11-26.md.
"""
import json
import os
import unittest

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
DIR = os.path.join(ROOT, "site", "data", "conditions")


def src(*p):
    with open(os.path.join(ROOT, *p), encoding="utf-8") as fh:
        return fh.read()


class ScarcityMovedItDidNotEnd(unittest.TestCase):
    def test_the_decision_says_why_the_adder_ended(self):
        d = src("site", "app", "conditions", "Decisions.tsx")
        self.assertIn("It ended because ERCOT changed how it prices scarcity", d)
        self.assertIn("the ancillary services' own demand curves, which the page does not draw", d)

    def test_the_empty_strip_says_it_for_ercot_only(self):
        s = src("site", "app", "conditions", "page.tsx")
        self.assertIn("not because scarcity ended: since 5 December 2025", s)
        self.assertEqual(s.count('extra={f.op === "ercot" ? ERCOT_SCARCITY_WORDS : undefined} w={w}'), 2)
        self.assertIn('{extra ? ` ${extra}` : ""}', s)
        self.assertNotIn("export const ERCOT_SCARCITY_WORDS", s)

    def test_the_notes_agree(self):
        self.assertIn("8. **ERCOT's scarcity after 4 December 2025**", src("docs", "methods", "grid_conditions.md"))
        self.assertIn("Scarcity is priced through the ancillary services' own demand curves", src("docs", "methods", "ercot_rt_price_adders.md"))

    @unittest.skipUnless(os.path.exists(os.path.join(DIR, "ercot.json")), "the conditions files are not in this checkout")
    def test_the_opening_view_holds_no_adder(self):
        with open(os.path.join(DIR, "ercot.json"), encoding="utf-8") as fh:
            f = json.load(fh)
        k = f["hourly_columns"].index("adder")
        self.assertTrue(all(r[k] is None for r in f["hourly"]["recent"]))
        i = f["daily_columns"].index("adder_hours")
        self.assertEqual(max(r[0] for r in f["daily"] if r[i] is not None), "2025-12-04")


if __name__ == "__main__":
    unittest.main()

"""Session 2277 (chain 174): a project one party leads is not a deal; a facility with only a place stays.

The second read (session 2249) kept two records it read as no transaction or no facility. D055, "Abu Dhabi's G42
Leads $1 Billion Data Center Project in Vietnam", names one party and no counterparty, and leading a project is
neither a sale nor an award: warehouse/deals/fields.py (project_led) refuses it. F052, "Huge AI Data Center Planned
for Pennsylvania Coal Plant Site", has only a state; a rule refusing a facility with no operator, developer or site
would also drop F050 and F036, which the same read keeps, so F052 stays by decision.
"""

import json
import os
import sys
import unittest

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
sys.path.insert(0, os.path.join(ROOT, "warehouse", "deals"))
sys.path.insert(0, os.path.join(ROOT, "warehouse", "deals", "eval"))
import fields  # noqa: E402
import fixture  # noqa: E402


class TheRule(unittest.TestCase):
    def test_a_project_led(self):
        self.assertTrue(fields.project_led({"seller": "G42", "evidence": "Abu Dhabi's G42 Leads $1 Billion Data Center Project in Vietnam"}))

    def test_a_deal_with_a_counterparty_is_kept(self):
        self.assertEqual(fields.project_led({"buyer": "Brookfield", "seller": "Microsoft",
                                             "evidence": "Brookfield leads $10 billion project with Microsoft"}), "")
        self.assertEqual(fields.project_led({"seller": "Crescent", "evidence": "Crescent Sells Non-Op D-J Assets"}), "")


class TheSample(unittest.TestCase):
    def test_d055_has_no_row(self):
        with open(os.path.join(ROOT, "tests", "fixtures", "deals", "stories_2249.json"), encoding="utf-8") as f:
            fx = {s["event_id"]: s.get("fixture") for s in json.load(f)}
        rows, log = fixture.replay("2249")
        self.assertEqual(len(rows), 81)
        self.assertFalse(any("D055" in {fx.get(i) for i in str(r["story_ids"]).split(";")} for r in rows.to_dict("records")))
        self.assertEqual(log.count("is a project one party leads"), 1)


if __name__ == "__main__":
    unittest.main()

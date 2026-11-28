"""Audit of the policy monitor, finding 6 (session 10217, docs/reviews/policy-model-audit-2026-11-26.md): a document's
status is read as of its own date (warehouse/policy/fields.py, status: `"effective" if eff and min(eff) <= event_date
else "final"`), and the monitor's Status is its newest document's. The method note said "(a final rule is effective once
its effective date has come)", which reads as a status that moves with the day; it does not. On the file of 25 November
2026, 96 of the 126 records marked final hold an effective date on or before 26 November.

1. Through the builder's rule and the page's file: a final rule whose effective date is after its document's date is
   final, and the file holds final records whose effective date has passed. Passes on main.
2. The fix on this branch, words only: the note says the status stays final after the date. Fails on main."""
import json
import os
import sys
import unittest

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
sys.path.insert(0, os.path.join(ROOT, "warehouse", "policy"))


def src(*p):
    with open(os.path.join(ROOT, *p), encoding="utf-8") as f:
        return f.read()


class TheStatusIsAsOfTheDocument(unittest.TestCase):
    def test_a_later_effective_date_leaves_the_rule_final(self):
        import fields
        later = [("effective", "2026-12-01", "This rule is effective December 1, 2026.")]
        self.assertEqual(fields.status("rule", "rule", "Some Rule", "Final rule.", "2026-10-01", later), "final")
        self.assertEqual(fields.status("rule", "rule", "Some Rule", "Final rule.", "2026-12-02", later), "effective")
        rows = json.loads(src("site", "data", "policy", "monitor.json"))["rows"]
        passed = [r for r in rows if r["status"] == "final" and any(s["kind"] == "effective" and s["date"] <= "2026-11-26" for s in r.get("steps", []))]
        self.assertGreater(len(passed), 0)

    def test_the_note_says_it(self):
        note = src("docs", "methods", "policy_monitor.md")
        self.assertNotIn("(a final rule is effective once its effective date has come)", note)
        self.assertIn('a rule is "effective" only when its effective date is on or before the document\'s own date,\n'
                      '  and a rule whose effective date comes later stays "final" in the file. The monitor reads each record\'s status as of\n'
                      "  the page's day", note)  # ready branch wip/ready-policy-status-today (session 11408)


if __name__ == "__main__":
    unittest.main()

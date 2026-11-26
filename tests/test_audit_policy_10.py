"""Audit of the policy monitor, finding 6's figure (session 10217, docs/reviews/policy-model-audit-2026-11-26.md), a test
that shows it; not for landing. The note's words are fixed on wip/audit-policy-4; this is the other choice, for the owner.

A record's Status is its newest document's, read as of that document's date (warehouse/policy/fields.py, status), so a
final rule whose effective date came after its publication stays "Final" once that date has passed, and the Status
filter's "In effect" leaves it out. On the file of 25 November 2026, read on 26 November: 96 of the 126 records marked
final hold an effective date on or before the page's day. The other choice, a status as of the page's day: Final 126 to
30 and In effect 70 to 166; as the view opens, Final 26 to 12 and In effect 5 to 19. (Beside it, already asked of the
data machine as "Comments closed", docs/state/data_ready_c301.md row 7: 133 of the 175 records proposed or open for
comment have every comment date behind the page's day, 35 of them as the view opens.) Default: left as it is.

1. The file holds final records whose effective date has passed, and none of them reads In effect. Passes on main.
2. The other choice, counted on the same file."""
import json
import os
import unittest

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
DAY = "2026-11-26"


def rows():
    with open(os.path.join(ROOT, "site", "data", "policy", "monitor.json"), encoding="utf-8") as f:
        return json.load(f)["rows"]


def passed(r, day=DAY):
    return any(s["kind"] == "effective" and s["date"] <= day for s in r.get("steps", []))


class TheStatusIsTheNewestDocuments(unittest.TestCase):
    def test_final_records_whose_effective_date_has_passed(self):
        fin = [r for r in rows() if r["status"] == "final"]
        self.assertGreater(sum(1 for r in fin if passed(r)), 0)

    def test_the_other_choice(self):
        rs = rows()
        final_now = sum(1 for r in rs if r["status"] == "final" and not passed(r))
        effective_now = sum(1 for r in rs if r["status"] == "effective" or (r["status"] == "final" and passed(r)))
        self.assertLess(final_now, sum(1 for r in rs if r["status"] == "final"))
        self.assertGreater(effective_now, sum(1 for r in rs if r["status"] == "effective"))


if __name__ == "__main__":
    unittest.main()

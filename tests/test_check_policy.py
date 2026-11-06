"""Session 3061 (chain 166): scripts/check_policy.py, the tracer of the policy monitor's dates and figures: a key that
stands in its row is ok, one that does not is FAIL, one whose document this copy does not hold is "not here".

    .venv/Scripts/python.exe -m pytest -q tests/test_check_policy.py
"""

import os
import sys
import unittest

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
sys.path.insert(0, os.path.join(ROOT, "scripts"))
import check_policy as C  # noqa: E402

ROW = {"event_id": "federalregister:1", "event_date": "2026-09-01", "agency": "FERC", "action_type": "notice", "status": "",
       "title": "Acme Pipeline, LLC; Notice of Application", "docket": "Docket No. CP26-1-000", "abstract": "",
       "first_paragraph": ("Acme would lease 750,000 Dth/d of capacity. The deadline for filing protests, motions to intervene, "
                           "and comments is 5:00 p.m. Eastern Time on December 8, 2026.")}
HELD = dict(ROW, event_id="federalregister:2", fields_from="record and text", body="FERC", dates="effective=2026-12-28",
            figure_value="", figure_unit="")


class Trace(unittest.TestCase):
    rows = {ROW["event_id"]: ROW, HELD["event_id"]: HELD}

    def k(self, **o):
        return {"key": "k", "record": "ferc:CP26-1", "event_id": "federalregister:1", "kind": "comments_due", "date": "2026-12-08"} | o

    def test_a_step_and_a_figure_that_stand_in_the_row_are_ok(self):
        self.assertEqual(C.check(self.k(), self.rows)[0], "ok")
        self.assertEqual(C.check(self.k(kind="figure", value=750000, unit="Dth/d"), self.rows)[0], "ok")
        self.assertEqual(C.check(self.k(event_id="federalregister:2", kind="effective", date="2026-12-28"), self.rows)[0], "ok")

    def test_a_wrong_date_figure_or_record_fails(self):
        self.assertEqual(C.check(self.k(event_id="federalregister:2", kind="effective", date="2026-12-29"), self.rows)[0], "FAIL")
        self.assertEqual(C.check(self.k(kind="figure", value=760000, unit="Dth/d"), self.rows)[0], "FAIL")
        self.assertEqual(C.check(self.k(record="ferc:CP99-9"), self.rows)[0], "FAIL")

    def test_a_document_not_held_or_a_step_its_summary_does_not_state_is_not_here(self):
        self.assertEqual(C.check(self.k(event_id="federalregister:404"), self.rows)[0], "not here")
        self.assertEqual(C.check(self.k(date="2026-12-09"), self.rows)[0], "not here", "a summary-only row: its text may state it")


if __name__ == "__main__":
    unittest.main()

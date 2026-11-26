"""Audit of the contracts page, finding 3 (session 10226, docs/reviews/contracts-model-audit-2026-11-26.md): nothing on the
page says how old its file is.

The page names the quarter filed for ("Filed for 2026 Q2") and gives no retrieval date: the stored summary the page reads
(warehouse/supabase/load.py, eqr_summary) carries none, and no schedule pulls the next quarter's file (the connector is
run by hand). The newest file on the code machine is 2026 Q2's, retrieved on 4 October 2026.

1. No schedule names the connector, and the summary holds no retrieval time. Passes on main.
2. The fix on this branch, words only: the note's section 10 says so. Fails on main. No figure moves. A date on the page
   needs the stored summary to carry the file's retrieval time: a data request."""
import glob
import os
import unittest

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))


def read(*p):
    with open(os.path.join(ROOT, *p), encoding="utf-8") as f:
        return f.read()


class NoAsOfDate(unittest.TestCase):
    def test_no_schedule_and_no_retrieval_time(self):
        self.assertNotIn("ferc_eqr", read("warehouse", "run_daily.sh"))
        for wf in glob.glob(os.path.join(ROOT, ".github", "workflows", "*.yml")):
            with open(wf, encoding="utf-8") as f:
                self.assertNotIn("ferc_eqr", f.read(), wf)
        load = read("warehouse", "supabase", "load.py")
        summary = load[load.index("def eqr_summary("):load.index("def eqr_terms(")]
        self.assertNotIn("retrieved", summary)
        self.assertNotIn("retrieved", read("site", "app", "contracts", "page.tsx").lower())

    def test_the_note_says_it(self):
        note = read("docs", "methods", "contracts.md")
        ten = note[note.index("## 10. What the tool does not hold"):note.index("## 11.")]
        self.assertIn("An as-of date (session 10226", ten)
        self.assertIn("no schedule runs it", ten)
        self.assertIn("gives no retrieval date", ten)


if __name__ == "__main__":
    unittest.main()

"""Session 10219 (chain 710, the conditions audit, finding 5): /conditions opened on ERCOT says "None held in this
window" for its newest days, and the reader takes it that ERCOT issued no notice. The notices are read by a connector no
scheduled run calls (its table was read on 19 October 2026, its last notice of 15 October), and CAISO's report is held
to its revision of 9 October. Words only: the none line says the list is only as new as its source's last reading.
docs/reviews/conditions-model-audit-2026-11-26.md.
"""
import glob
import json
import os
import unittest

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
DIR = os.path.join(ROOT, "site", "data", "conditions")


def src(*p):
    with open(os.path.join(ROOT, *p), encoding="utf-8") as fh:
        return fh.read()


class TheNoneLineSaysHowNew(unittest.TestCase):
    def test_the_none_line_carries_the_words(self):
        s = src("site", "app", "conditions", "page.tsx")
        self.assertIn('"The file holds none."} {ALERT_SOURCE_WORDS}</p>', s)
        for w in ["only as new as its source's last reading", "when a session reads them, not each day",
                  "which CAISO revises from time to time", "shows none whether or not a notice was issued"]:
            self.assertIn(w, s)
        self.assertNotIn("export const ALERT_SOURCE_WORDS", s)

    def test_the_note_says_it(self):
        self.assertIn("## How new the alerts are (session 10219)", src("docs", "methods", "grid_conditions.md"))

    def test_no_scheduled_run_reads_ercots_notices(self):
        runners = glob.glob(os.path.join(ROOT, "warehouse", "*.sh")) + glob.glob(os.path.join(ROOT, ".github", "workflows", "*.yml")) + \
            glob.glob(os.path.join(ROOT, "scripts", "*.ps1"))
        for p in runners:
            with open(p, encoding="utf-8", errors="replace") as fh:
                self.assertNotIn("ercot_grid_notices.py", fh.read(), p)

    @unittest.skipUnless(os.path.exists(os.path.join(DIR, "ercot.json")), "the conditions files are not in this checkout")
    def test_the_default_view_is_a_window_after_the_last_notice(self):
        with open(os.path.join(DIR, "ercot.json"), encoding="utf-8") as fh:
            f = json.load(fh)
        rec = [w for w in f["windows"] if w["id"] == "recent"][0]
        last = max(a[0] for a in f["alerts"])
        self.assertLess(last, rec["start"], "the newest window starts after the file's last notice")


if __name__ == "__main__":
    unittest.main()

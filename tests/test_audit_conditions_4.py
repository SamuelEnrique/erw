"""Session 10219 (chain 710, the conditions audit, finding 4): /conditions draws CAISO's notices with the start and end
the table caiso_grid_emergencies holds, and that table leaves both empty for three ways CAISO prints a time frame: "at"
between the date and the hour (the Stage 3 rotating outages of 14 and 15 August 2020), the month in words with AM and
PM (the Flex Alerts of September 2022), and ISO dates (the Flex Alert of 12 July 2021). 15 rows since the page's first
day (2018-07-01), 470 since 1998. Reading them would change the cells the page draws, and the hours
scarcity_hours_by_grid counts for a notice, so the ruling is the owner's (docs/reviews/conditions-model-audit-2026-11-26.md).
These tests pass on main: they show the finding, not a fix.
"""
import datetime as dt
import json
import os
import sys
import unittest

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
DIR = os.path.join(ROOT, "site", "data", "conditions")
sys.path.insert(0, os.path.join(ROOT, "warehouse", "connectors"))


class TheConnectorLeavesTheseTimesEmpty(unittest.TestCase):
    def test_three_printed_forms_give_no_start_or_end(self):
        import caiso_emergencies as ce
        for frame, day in [("08/14/2020 at 18:36 through 08/14/2020 at 20:38", dt.date(2020, 8, 14)),
                           ("September 3 at 4:00 PM to September 3 at 9:00 PM", dt.date(2022, 9, 3)),
                           ("2021-07-12 16:00:00 through 2021-07-12 21:00:00", dt.date(2021, 7, 12))]:
            days, start, end = ce.span(frame, day)
            self.assertEqual((start, end), ("", ""), frame)

    def test_the_form_it_reads(self):
        import caiso_emergencies as ce
        days, start, end = ce.span("08/14/2020 17:00 through 08/14/2020 21:00", dt.date(2020, 8, 14))
        self.assertEqual((start, end), ("2020-08-14 17:00", "2020-08-14 21:00"))


@unittest.skipUnless(os.path.exists(os.path.join(DIR, "caiso.json")), "the conditions files are not in this checkout")
class ThePageDrawsThemBlank(unittest.TestCase):
    def test_the_stage_3_outages_of_august_2020_have_no_start_on_the_page(self):
        with open(os.path.join(DIR, "caiso.json"), encoding="utf-8") as fh:
            f = json.load(fh)
        s3 = [a for a in f["alerts"] if a[1] == "Stage 3" and a[0] in ("2020-08-14", "2020-08-15")]
        self.assertEqual(len(s3), 2)
        self.assertTrue(all(a[2] is None and a[3] is None for a in s3))
        blank = [a for a in f["alerts"] if a[0] >= "2018-07-01" and a[2] is None]
        self.assertGreaterEqual(len(blank), 14)


if __name__ == "__main__":
    unittest.main()

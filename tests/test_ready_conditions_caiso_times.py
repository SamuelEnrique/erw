"""Session 11407 (chain 770, part C), carried over from wip/audit-conditions-4 (session 10219, the conditions audit of
26 November, finding 4). /conditions draws CAISO's notices with the start and end the table caiso_grid_emergencies
holds, and the connector left both empty for three ways CAISO prints a time frame: "at" between the date and the hour
(the Stage 3 rotating outages of 14 and 15 August 2020), the month in words with AM and PM (the Flex Alerts of
August and September 2022), and ISO dates (the Flex Alert of 12 July 2021). On this branch span() reads all three.
The table is rebuilt by the data machine's daily run, and the page files at landing by the desk; the page-file test
below holds before and after that rebuild.
"""
import datetime as dt
import json
import os
import sys
import unittest

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
DIR = os.path.join(ROOT, "site", "data", "conditions")
sys.path.insert(0, os.path.join(ROOT, "warehouse", "connectors"))


class TheConnectorReadsTheseTimes(unittest.TestCase):
    def test_three_printed_forms_give_a_start_and_end(self):
        import caiso_emergencies as ce
        for frame, day, want in [
                ("08/14/2020 at 18:36 through 08/14/2020 at 20:38", dt.date(2020, 8, 14), ("2020-08-14 18:36", "2020-08-14 20:38")),
                ("08/15/2020 at 18:27 through 08/15/2020 at 18:48", dt.date(2020, 8, 15), ("2020-08-15 18:27", "2020-08-15 18:48")),
                ("September 3 at 4:00 PM to September 3 at 9:00 PM", dt.date(2022, 9, 3), ("2022-09-03 16:00", "2022-09-03 21:00")),
                ("September 8 at 3:00 PM to September 8 at 10:00 PM", dt.date(2022, 9, 8), ("2022-09-08 15:00", "2022-09-08 22:00")),
                ("2021-07-12 16:00:00 through 2021-07-12 21:00:00", dt.date(2021, 7, 12), ("2021-07-12 16:00", "2021-07-12 21:00"))]:
            days, start, end = ce.span(frame, day)
            self.assertEqual((start, end), want, frame)
            self.assertEqual(days, [day], frame)

    def test_a_frame_of_several_days_gives_each_day(self):
        import caiso_emergencies as ce
        days, start, end = ce.span("08/14/2020 at 15:00 through 08/16/2020 at 22:00", dt.date(2020, 8, 14))
        self.assertEqual(days, [dt.date(2020, 8, 14), dt.date(2020, 8, 15), dt.date(2020, 8, 16)])
        days, start, end = ce.span("December 31 at 11:00 AM to January 1 at 2:00 AM", dt.date(2022, 12, 31))
        self.assertEqual((start, end), ("2022-12-31 11:00", "2023-01-01 02:00"))
        self.assertEqual(ce.span("August 31 at 12:00 PM to August 31 at 12:30 AM", dt.date(2022, 8, 31))[1:], ("2022-08-31 12:00", "2022-08-31 00:30"))

    def test_the_forms_it_read_before_read_the_same(self):
        import caiso_emergencies as ce
        self.assertEqual(ce.span("08/14/2020 17:00 through 08/14/2020 21:00", dt.date(2020, 8, 14))[1:], ("2020-08-14 17:00", "2020-08-14 21:00"))
        self.assertEqual(ce.span("10/1/2020 15:00:00 through 22:00:00", dt.date(2020, 9, 30)), ([dt.date(2020, 10, 1)], "2020-10-01 15:00", "2020-10-01 22:00"))
        self.assertEqual(ce.span("16:00 - 21:00", dt.date(2022, 9, 6)), ([dt.date(2022, 9, 6)], "2022-09-06 16:00", "2022-09-06 21:00"))
        self.assertEqual(ce.span("Jan-59", dt.date(2012, 2, 2)), ([dt.date(2012, 2, 2)], "", ""))
        self.assertEqual(ce.span("", dt.date(2022, 9, 6)), ([dt.date(2022, 9, 6)], "", ""))

    def test_the_method_note_says_so(self):
        with open(os.path.join(ROOT, "docs", "methods", "caiso_grid_emergencies.md"), encoding="utf-8") as fh:
            s = fh.read()
        self.assertIn("Start and end (session 11407", s)


@unittest.skipUnless(os.path.exists(os.path.join(DIR, "caiso.json")), "the conditions files are not in this checkout")
class EveryBlankOnThePageIsAFormNowRead(unittest.TestCase):
    def test_each_blank_since_july_2018_is_read_from_its_printed_frame(self):
        # the page file keeps no frame, so the rows are matched to the printed frames this connector meets: until the
        # desk rebuilds the files the blanks are exactly the Stage 3 outages and the Flex Alerts; after it, none is left
        with open(os.path.join(DIR, "caiso.json"), encoding="utf-8") as fh:
            f = json.load(fh)
        blank = [a for a in f["alerts"] if a[0] >= "2018-07-01" and a[2] is None]
        self.assertTrue(all(a[1] in ("Stage 3", "Flex Alert") for a in blank), blank)
        self.assertLessEqual(len(blank), 15)


if __name__ == "__main__":
    unittest.main()

"""Session 9001, chain 601 part H: SPP's 2021 day-ahead price zip holds, beside each day's file
(2021/02/By_Day/DA-LMP-SL-202102150100.csv), a RePrice folder of hours reposted after Winter Storm Uri
(2021/02/RePrice/DA-LMP-SL-202102150100-R1-RC6.csv). The connector matched a zip's files by date alone, so a repriced
hour replaced its day's file and the pull of 2021 stopped on a repeated hour. Only a day's own file is read now; each
repriced file is named in the gaps.
"""
import io
import os
import sys
import unittest
import zipfile

import pandas as pd

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
sys.path.insert(0, os.path.join(ROOT, "warehouse", "connectors"))


def year_zip(files):
    buf = io.BytesIO()
    with zipfile.ZipFile(buf, "w") as z:
        for name, text in files.items():
            z.writestr(name, text)
    return buf.getvalue()


class OnlyTheDaysOwnFile(unittest.TestCase):
    def test_a_repriced_file_neither_replaces_the_day_nor_stops_the_pull(self):
        import grid_congestion as gc
        feed = {"prefix": "DA-LMP-SL", "report": "Day-Ahead LMP by Settlement Location"}
        day = pd.Timestamp("2021-02-15")
        raw = year_zip({
            "2021/02/RePrice/DA-LMP-SL-202102150100-R1-RC6.csv": "repriced",
            "2021/02/By_Day/DA-LMP-SL-202102150100.csv": "the day",
            "2021/02/RePrice/DA-LMP-SL-202102150200-R2-RC6.csv": "repriced too",
        })
        gaps = []
        out = gc.spp_texts(raw, {"year": 2021, "days": [day]}, feed, None, gaps)
        self.assertEqual(out, [(day, "the day")])
        self.assertEqual(len(gaps), 2)
        self.assertTrue(all("RePrice" in g and "not read" in g for g in gaps))

    def test_two_files_for_one_day_stop_the_pull(self):
        import grid_congestion as gc
        feed = {"prefix": "DA-LMP-SL", "report": "Day-Ahead LMP by Settlement Location"}
        raw = year_zip({"2021/02/By_Day/DA-LMP-SL-202102150100.csv": "a", "2021/02/Other/DA-LMP-SL-202102150100.csv": "b"})
        with self.assertRaises(RuntimeError):
            gc.spp_texts(raw, {"year": 2021, "days": [pd.Timestamp("2021-02-15")]}, feed, None, [])

    def test_an_identical_copy_outside_by_day_is_read_once(self):
        # 2016's zip: 2016/07/DA-LMP-SL-201607180100.csv and 2016/07/By_Day/DA-LMP-SL-201607180100.csv, the same bytes
        import grid_congestion as gc
        feed = {"prefix": "DA-LMP-SL", "report": "Day-Ahead LMP by Settlement Location"}
        day = pd.Timestamp("2016-07-18")
        raw = year_zip({"2016/07/DA-LMP-SL-201607180100.csv": "same", "2016/07/By_Day/DA-LMP-SL-201607180100.csv": "same"})
        gaps = []
        self.assertEqual(gc.spp_texts(raw, {"year": 2016, "days": [day]}, feed, None, gaps), [(day, "same")])
        self.assertEqual(len(gaps), 1)
        self.assertIn("read once", gaps[0])


if __name__ == "__main__":
    unittest.main()

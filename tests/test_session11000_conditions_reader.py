"""Session 11000 (chain 750, the browser read of 26 November 2026): two things a reader met on /conditions.

1. The alerts table listed the first 40 notices of a window and said nothing of the rest, under a heading that counted
   them all: CAISO over the September 2022 heat wave, "(44)" and 40 rows, the last day's four notices missing; over the
   August 2020 heat wave, "(79)" and 40 rows, nothing after 17 August. Every notice the heading counts is a row.
2. Each operator's line read "days and hours in America/Chicago clock time for days and hours": the page wrapped the
   file's `time`, which is already the whole phrase. The clock is said once.

Energy Research Warehouse (ERW). No network, no build: the page's source and the page files are read.

    python -m unittest tests.test_session11000_conditions_reader -v
"""

import glob
import json
import os
import re
import unittest

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
PAGE = os.path.join(ROOT, "site", "app", "conditions", "page.tsx")
FILES = os.path.join(ROOT, "site", "data", "conditions")


def src():
    with open(PAGE, encoding="utf-8") as f:
        return f.read()


def clock_words(time):
    """The page's clockWords(), as the source writes it."""
    return time if re.search(r"days and hours", time) else "days and hours in " + time


class TheAlertsTable(unittest.TestCase):
    def test_every_notice_the_heading_counts_is_a_row(self):
        t = src()
        self.assertIn("({alerts.length})</h4>", t)                 # the heading counts the window's notices
        self.assertIn("rows={alerts.map((a, i) =>", t)             # and the table lists that same list, whole
        self.assertIsNone(re.search(r"alerts\.slice\(", t), "the alerts list is cut again: say so on the page, or list them all")

    def test_the_files_hold_windows_the_old_cut_would_shorten(self):
        # the case is real in the files as they stand: without it this test would guard nothing
        path = os.path.join(FILES, "caiso.json")
        if not os.path.exists(path):
            self.skipTest("the page files are not in this checkout")
        with open(path, encoding="utf-8") as f:
            d = json.load(f)
        counts = {w["id"]: sum(1 for a in d["alerts"] if w["start"] <= a[0] <= w["end"]) for w in d["windows"]}
        self.assertTrue(any(n > 40 for n in counts.values()), counts)


class TheClockSaidOnce(unittest.TestCase):
    def test_the_page_uses_clock_words(self):
        t = src()
        self.assertIn("{clockWords(f.time)}", t)
        self.assertNotIn("days and hours in {f.time}", t)
        self.assertIn('return /days and hours/.test(time) ? time : `days and hours in ${time}`;', t)

    def test_no_file_reads_doubled(self):
        files = [p for p in sorted(glob.glob(os.path.join(FILES, "*.json"))) if os.path.basename(p) not in ("index.json", "congestion.json")]
        if not files:
            self.skipTest("the page files are not in this checkout")
        for p in files:
            with open(p, encoding="utf-8") as f:
                time = json.load(f)["time"]
            words = clock_words(time)
            self.assertEqual(words.count("days and hours"), 1, f"{os.path.basename(p)}: {words}")
            self.assertIn("clock time", words)

    def test_a_zone_alone_still_reads_right(self):
        self.assertEqual(clock_words("America/Chicago"), "days and hours in America/Chicago")
        self.assertEqual(clock_words("America/Chicago clock time for days and hours"), "America/Chicago clock time for days and hours")


if __name__ == "__main__":
    unittest.main()

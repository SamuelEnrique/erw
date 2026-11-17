"""Ruling alternative 1 of the Digest (session 7711, 17 November 2026, branch wip/alt-site-digest-1; not a default on main).

Energy Research Warehouse (ERW). The question (docs/reviews/ruling-impact-site-digest-2026-11-17.md, line 1): should the
Digest's US48 day stay the UTC day, which splits the US evening peak? On this branch warehouse/news/brief.py demand_lines
reads the Eastern day (DEMAND_DAY_TZ, midnight to midnight in America/New_York). The Digest is paused: no issue is written
or changed; the line is pinned with the function itself, on made-up hours and, where it is on the machine, on the local
copy of eia930_all_demand (warehouse/output, or the folder ERW_TABLES_DIR names; it holds 26 August to 12 November 2026,
the impact file read the live set, 12 October to 15 November). The issue of 18 October (yesterday 17 October): 495,806 MW
in the hour starting 00:00 UTC (the evening of 16 October, Eastern) to 448,936 MW at 23:00 UTC (-46,870 MW, -9.45
percent); the issue of 17 October: 540,657 to 514,073 MW (-4.92 percent). On the local copy 17 of 73 days move.

    python -m unittest tests.test_alt_site_digest_1 -v
"""

import os
import re
import sys
import unittest
from unittest import mock

import pandas as pd

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
sys.path.insert(0, os.path.join(ROOT, "warehouse", "news"))
sys.path.insert(0, os.path.join(ROOT, "warehouse", "connectors"))
import brief  # noqa: E402

TABLES = os.environ.get("ERW_TABLES_DIR") or os.path.join(ROOT, "warehouse", "output")
CSV = os.path.join(TABLES, "eia930_all_demand.csv")
PEAK = re.compile(r"peaked at ([\d,]+) MW in the hour starting (\d{4}-\d{2}-\d{2} \d{2}:\d{2}) UTC")


class Notes:
    def ref(self, *a):
        return "[1]"


def run(fetch, issue):
    with mock.patch.object(brief.erw, "fetch", side_effect=fetch):
        return brief.demand_lines(issue, lambda m: None, Notes())[-1]


def frame_fetch(df):
    def fetch(table, start=None, end=None, **k):
        return df[(df["ts_utc"] >= start) & (df["ts_utc"] < end)].copy()
    return fetch


class TheEasternDay(unittest.TestCase):
    def test_the_evening_peak_stays_in_its_own_day(self):
        # made-up hours: 600 at 00:00 UTC on 17 October (20:00 Eastern on 16 October), 500 at 23:00 UTC on 17 October
        hours = pd.date_range("2026-10-09", "2026-10-19", freq="h", tz="UTC", inclusive="left")
        v = [600.0 if (h.day in (10, 17) and h.hour == 0) else 500.0 if h.hour == 23 else 100.0 for h in hours]
        df = pd.DataFrame({"variable": "demand_mw", "ts_utc": hours, "value": v})
        line = run(frame_fetch(df), "2026-10-18")
        self.assertTrue(line.startswith("**US48 demand, yesterday (Eastern day):** "), line)
        self.assertEqual(PEAK.findall(line)[0], ("500", "2026-10-17 23:00"))   # main: 600 at 2026-10-17 00:00 UTC
        self.assertEqual(brief.DEMAND_DAY_TZ, "America/New_York")


@unittest.skipUnless(os.path.exists(CSV), "eia930_all_demand is not on this machine")
class OnTheLocalCopy(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        n = sum(1 for line in open(CSV, encoding="utf-8") if line.startswith("#"))
        t = pd.read_csv(CSV, skiprows=n, usecols=["entity", "variable", "ts_utc", "value"])
        t = t[(t["entity"] == "eia930:US48") & (t["variable"] == "demand_mw")].copy()
        t["ts_utc"] = pd.to_datetime(t["ts_utc"], utc=True)
        cls.fetch = staticmethod(frame_fetch(t[["variable", "ts_utc", "value"]]))

    def test_the_issue_of_18_october(self):
        self.assertEqual(PEAK.findall(run(self.fetch, "2026-10-18"))[0], ("448,936", "2026-10-17 23:00"))   # main: 495,806 at 00:00 UTC

    def test_the_issue_of_17_october(self):
        self.assertEqual(PEAK.findall(run(self.fetch, "2026-10-17"))[0][0], "514,073")   # main: 540,657


if __name__ == "__main__":
    unittest.main()

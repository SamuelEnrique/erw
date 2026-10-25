"""Session 2351 (chain 105's 2301): Svenska kraftnat's Mimer, Sweden's production an hour by type.

Energy Research Warehouse (ERW). Tests warehouse/connectors/svk_sweden.py on files built here in Mimer's form (figures
made up for the test, not Mimer's): a day's 24 hours read, the decimal comma, the Summa line checked, a day without 24
hours, an hour given twice, a blank figure and a wrong first line each stopping the run; the hour placed in UTC; the
sector rule and the hold. No network.

    python -m unittest tests.test_session2351 -v
"""

import os
import sys
import unittest

import pandas as pd

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
sys.path.insert(0, os.path.join(ROOT, "warehouse", "connectors"))
sys.path.insert(0, os.path.join(ROOT, "warehouse", "metadata"))
import svk_sweden as V  # noqa: E402
import build_coverage as B  # noqa: E402


def day(date="2024-10-27", value="1000", n=24):
    return [f"{date} {h:02d}:00;{value};2024-10-29 05:00;" for h in range(n)]


def text(rows, summa):
    return "﻿" + V.HEAD + "\r\n" + "\r\n".join(rows) + f"\r\nSumma;{summa};\r\n"


class Parse(unittest.TestCase):
    def test_rows(self):
        rows = V.parse(text(day(value="1000,5"), "24012"), "KK")
        self.assertEqual(len(rows), 24)
        self.assertEqual(rows[3], ("2024-10-27 03:00", 1000.5, "2024-10-29 05:00"))
        label = pd.to_datetime(["2024-10-27 00:00"], format="%Y-%m-%d %H:%M")
        self.assertEqual((label - V.NORMAL_TIME).strftime("%Y-%m-%dT%H:%M:%SZ")[0], "2024-10-26T23:00:00Z")

    def test_stops(self):
        cases = [
            (text(day(), "24010"), "the Summa line"),  # within 1 kWh passes (rounding)
            (text(day(n=23), "23000"), "without 24 hours"),
            (text(day() + day()[:1], "25000"), "twice"),
            (text(day()[:23] + ["2024-10-27 23:00;;2024-10-29 05:00;"], "23000"), "blank"),
            ("Period;Produktion (MWh);\r\n", "first line"),
            ("﻿" + V.HEAD + "\r\n" + "\r\n".join(day()), "no Summa"),
        ]
        for body, words in cases:
            with self.assertRaises(RuntimeError) as c:
                V.parse(body, "VI")
            self.assertIn(words, str(c.exception))


class Registered(unittest.TestCase):
    def test_sector_and_hold(self):
        self.assertEqual(B.sector_of(V.TABLE), "power")
        with open(os.path.join(ROOT, "warehouse", "supabase", "live_set.yaml"), encoding="utf-8") as f:
            self.assertIn(f"  - {V.TABLE}\n", f.read().replace("\r\n", "\n"))


if __name__ == "__main__":
    unittest.main()

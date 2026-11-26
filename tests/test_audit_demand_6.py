"""Session 10214 (chain 710, part D: the demand page audited, docs/reviews/demand-model-audit-2026-11-26.md, finding 5).
Not for landing: it shows a figure for the owner's ruling.

/demand prints "Hours left out for ERCOT: 0 that stand apart from their neighbours, 0 at or below zero, 48 blank". The
count runs from 1 January 2019 to the workbook's last row, and EIA's workbook ends with a day it has not yet filled, so
24 of the 48 are hours after the newest hour the page uses (November 2026, the day of the fetch), not gaps in the
record. From the page's own file: the hours not used inside the years it writes, against the count it prints.
"""
import json
import os
import unittest

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))


class BlankHoursAfterTheRecord(unittest.TestCase):
    def test_the_printed_count_holds_hours_after_the_newest_month(self):
        f = json.load(open(os.path.join(ROOT, "site", "data", "demand_growth.json"), encoding="utf-8"))
        after = {}
        for ba, a in f["areas"].items():
            ys = a["years"]
            inside = sum(r["hours_in_year"] - r["hours_used"] for y, r in ys.items() if "hours_used" in r)
            newest = ys[max(ys)]
            inside += newest["ytd_hours_in_window"] - newest["ytd_hours_used"]
            printed = a["screened"]["blank"] + a["screened"]["not_positive"] + a["screened"]["jumps"]
            after[ba] = printed - inside
        self.assertEqual(f["areas"]["ERCO"]["screened"]["blank"], 48)
        self.assertEqual(after["ERCO"], 24, "24 of ERCOT's 48 blank hours lie after October 2026")
        # every area: about a day (CAISO 23: its emptied hour of 2 December 2025 has no row, so it is not counted blank)
        self.assertTrue(all(23 <= v <= 25 for v in after.values()), after)


if __name__ == "__main__":
    unittest.main()

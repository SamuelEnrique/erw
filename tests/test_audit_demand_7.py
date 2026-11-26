"""Session 10214 (chain 710, part D: the demand page audited, docs/reviews/demand-model-audit-2026-11-26.md, finding 6).

The year so far on /demand ends with the newest whole month, whose hours EIA goes on revising for some weeks: the Lower
48's October 2026 is 460,894.6 MW in the page's file (built 6 November 2026) and 460,066.5 MW on EIA's hourly route as
the main copy held it on 13 November (the session 7014 replication saw 460,798.6 on 2 November and 461,062.9 on
9 November). The data test runs where the table is (warehouse/output, or a folder named by ERW_AUDIT_TABLES).
"""
import csv
import json
import os
import unittest
from datetime import datetime, timezone
from zoneinfo import ZoneInfo

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))


def src(*p):
    with open(os.path.join(ROOT, *p), encoding="utf-8") as f:
        return f.read()


class TheNewestMonthMoves(unittest.TestCase):
    def test_the_lower_48s_october_differs_on_a_later_read(self):
        path = None
        for d in (os.environ.get("ERW_AUDIT_TABLES"), os.path.join(ROOT, "warehouse", "output")):
            if d and os.path.exists(os.path.join(d, "eia930_all_demand.csv")):
                path = os.path.join(d, "eia930_all_demand.csv")
        if not path:
            self.skipTest("eia930_all_demand is not held on this machine")
        tz = ZoneInfo("America/New_York")
        vals = []
        with open(path, newline="", encoding="utf-8") as f:
            rd = csv.reader(line for line in f if not line.startswith("#"))
            head = next(rd)
            e, v, t, val = head.index("entity"), head.index("variable"), head.index("ts_utc"), head.index("value")
            for r in rd:
                if r[e] == "eia930:US48" and r[v] == "demand_mw" and r[val]:
                    ts = datetime.strptime(r[t][:19], "%Y-%m-%dT%H:%M:%S").replace(tzinfo=timezone.utc).astimezone(tz)
                    if (ts.year, ts.month) == (2026, 10):
                        vals.append(float(r[val]))
        if len(vals) < 0.95 * 744:
            self.skipTest("the table held does not hold October 2026 whole")
        page = json.loads(src("site", "data", "demand_growth.json"))["areas"]["US48"]["years"]["2026"]["avg_demand_mw_m10"]
        self.assertEqual(page, 460894.6)
        self.assertGreater(abs(sum(vals) / len(vals) - page), 100)

    def test_the_hover_says_the_newest_month_can_move(self):
        self.assertIn("EIA goes on revising its newest hours for some weeks, the Lower 48's total most, so the newest month of the year so far can move at the next build", src("site", "app", "demand", "page.tsx"))


if __name__ == "__main__":
    unittest.main()

"""wip/ready-trader-offpeak (session 11406, chain 770, part C): the other choice of the trader view audit of
26 November, finding 3 (docs/reviews/trader-model-audit-2026-11-26.md), readied for Samuel's ruling, not requested.

On main the board's week "Off-peak DA" is the mean of 7 daily off-peak means, so a weekend day's 24 off-peak hours
count as much as a weekday's 8. On this branch warehouse/derived/board_page.py (build_week) weighs each day's mean by
its off-peak hours (off_hours), which is the mean of every off-peak hour of the week. Measured on the page's own hourly
files for the week the board of 25 November 2026 shows (19 to 25 November): SP15 42.72 to 39.36, NP15 57.22 to 58.74,
SPP North 19.08 to 16.61. The site file is rebuilt at landing by the desk (iso_trader_daily on this machine stops on
22 October). The audit's test (tests/test_audit_trader_3.py on wip/audit-trader-3) is carried: the hour-weighted mean
it measures is now what build_week's rule gives from the same days."""
import collections
import datetime as dt
import json
import os
import sys
import unittest
from zoneinfo import ZoneInfo

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
SITE = os.path.join(ROOT, "site")
sys.path.insert(0, os.path.join(ROOT, "warehouse", "derived"))
sys.path.insert(0, os.path.join(ROOT, "warehouse", "connectors"))


def board():
    try:
        import board_page
    except Exception as exc:  # the builder imports the warehouse's libraries
        raise unittest.SkipTest(f"board_page does not import here: {exc}")
    return board_page


def week(hid, end, bp):
    with open(os.path.join(SITE, "public", "board", "h", hid + ".json"), encoding="utf-8") as f:
        hf = json.load(f)
    tz = ZoneInfo(hf["tz"])
    by = collections.defaultdict(list)
    for i, v in enumerate(hf["da"]):
        loc = dt.datetime.fromtimestamp((hf["t0"] + i) * 3600, tz=dt.timezone.utc).astimezone(tz)
        by[loc.date()].append((loc, v))
    days = [end - dt.timedelta(days=k) for k in range(6, -1, -1)]
    daily, weights, hours = [], [], []
    for d in days:
        work = d.weekday() < 5 and d not in bp.pb.nerc_holidays([d.year])
        off = [v for loc, v in by[d] if not (work and 6 <= loc.hour <= 21)]
        daily.append(sum(off) / len(off))
        weights.append(bp.off_hours(d.isoformat() + "T00:00:00Z", hf["tz"]))
        self_count = len(off)
        assert self_count == weights[-1], (d, self_count, weights[-1])
        hours += off
    rule = sum(x * w for x, w in zip(daily, weights)) / sum(weights)   # build_week's rule on this branch
    return sum(daily) / 7, rule, sum(hours) / len(hours)


class OffPeakWeekWeighsHours(unittest.TestCase):
    def test_off_hours(self):
        bp = board()
        self.assertEqual(bp.off_hours("2026-11-24T00:00:00Z", "America/Los_Angeles"), 8)      # a Tuesday
        self.assertEqual(bp.off_hours("2026-11-22T00:00:00Z", "America/Los_Angeles"), 24)     # a Sunday
        self.assertEqual(bp.off_hours("2026-11-26T00:00:00Z", "America/Chicago"), 24)         # Thanksgiving
        self.assertEqual(bp.off_hours("2026-11-01T00:00:00Z", "America/Chicago"), 25)         # the clocks go back, a Sunday
        self.assertEqual(bp.off_hours("2026-03-09T00:00:00Z", "America/Chicago"), 8)          # a Monday after the change

    def test_the_rule_is_in_build_week(self):
        with open(os.path.join(ROOT, "warehouse", "derived", "board_page.py"), encoding="utf-8") as f:
            src = f.read()
        self.assertIn('if v == "da_offpeak_mean_usd":', src)
        self.assertIn("w = [off_hours(d, tz) for d in ds]", src)
        self.assertIn("return sum(x * k for x, k in zip(vals, w)) / sum(w)", src)

    def test_the_figures_of_the_board_of_25_november(self):
        bp = board()
        with open(os.path.join(SITE, "data", "board.json"), encoding="utf-8") as f:
            b = json.load(f)
        pinned = b["built"].startswith("2026-11-25")   # the audit measured the board of 25 November; another file is measured and printed
        rows = {w["hub"]: w for w in b["week"]}
        for hid, before, after in (("caiso-th-sp15-gen-apnd", 42.72, 39.36), ("caiso-th-np15-gen-apnd", 57.22, 58.74), ("spp-sppnorth-hub", 19.08, 16.61)):
            m = rows[hid]["means"]["da_offpeak_mean_usd"]
            days_mean, rule, hourly = week(hid, dt.date.fromisoformat(m["end"]), bp)
            self.assertAlmostEqual(days_mean, m["v"], delta=0.005)          # the page's figure on main
            print(f"{b['built'][:10]} {hid} week to {m['end']}: before {days_mean:.2f}, after {rule:.2f}")
            if pinned:
                self.assertEqual(round(days_mean, 2), before)
            self.assertAlmostEqual(rule, hourly, places=9)                  # the branch's rule is the hour-weighted mean
            if pinned:
                self.assertEqual(round(rule, 2), after)


if __name__ == "__main__":
    unittest.main()

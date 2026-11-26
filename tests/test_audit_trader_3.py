"""Audit of the trader view, finding 3 (session 10209, docs/reviews/trader-model-audit-2026-11-26.md): the week's
"Off-peak DA" is the mean of 7 daily off-peak means (warehouse/derived/board_page.py, build_week, on
iso_trader_daily's da_offpeak_mean_usd), so a weekend day's 24 off-peak hours count as much as a weekday's 8. A
trader's off-peak week (the 7x8 and 2x16 wrap) weights every off-peak hour once. A figure: NOT for landing; for
Samuel's ruling, default "left as it is".

Measured on the page's own hourly files, the week the board of 25 November 2026 shows (19 to 25 November):
SP15 42.72 as drawn, 39.36 hour-weighted (-3.36, -7.9 percent); NP15 57.22 and 58.74 (+1.51); SPP North 19.08 and
16.61 (-2.48, -13.0 percent). Passes on main."""
import collections
import datetime as dt
import json
import os
import unittest
from zoneinfo import ZoneInfo

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
SITE = os.path.join(ROOT, "site")


def holidays(y):
    def mon(d):
        return d + dt.timedelta(days=1) if d.weekday() == 6 else d
    may31, sep1, nov1 = dt.date(y, 5, 31), dt.date(y, 9, 1), dt.date(y, 11, 1)
    return {mon(dt.date(y, 1, 1)), may31 - dt.timedelta(days=may31.weekday()), mon(dt.date(y, 7, 4)),
            sep1 + dt.timedelta(days=(7 - sep1.weekday()) % 7), nov1 + dt.timedelta(days=(3 - nov1.weekday()) % 7 + 21),
            mon(dt.date(y, 12, 25))}


def off_peak_week(hid, end):
    with open(os.path.join(SITE, "public", "board", "h", hid + ".json"), encoding="utf-8") as f:
        hf = json.load(f)
    tz = ZoneInfo(hf["tz"])
    by = collections.defaultdict(list)
    for i, v in enumerate(hf["da"]):
        loc = dt.datetime.fromtimestamp((hf["t0"] + i) * 3600, tz=dt.timezone.utc).astimezone(tz)
        by[loc.date()].append((loc, v))
    days = [end - dt.timedelta(days=k) for k in range(6, -1, -1)]
    daily, hours = [], []
    for d in days:
        work = d.weekday() < 5 and d not in holidays(d.year)
        off = [v for loc, v in by[d] if not (work and 6 <= loc.hour <= 21)]
        daily.append(sum(off) / len(off))
        hours += off
    return sum(daily) / 7, sum(hours) / len(hours), len(hours)


class OffPeakWeekWeighsDaysNotHours(unittest.TestCase):
    def test_the_week_is_a_mean_of_daily_means(self):
        with open(os.path.join(ROOT, "warehouse", "derived", "board_page.py"), encoding="utf-8") as f:
            src = f.read()
        self.assertIn('"da_offpeak_mean_usd"', src)
        self.assertIn("return sum(vals) / len(vals) if len(ds) == 7", src)      # each day's value counts once

    def test_hour_weighted_differs_on_the_board_of_25_november(self):
        with open(os.path.join(SITE, "data", "board.json"), encoding="utf-8") as f:
            b = json.load(f)
        if not b["built"].startswith("2026-11-25"):
            self.skipTest(f"the measured file was built on 25 November 2026; this one {b['built']}")
        rows = {w["hub"]: w for w in b["week"]}
        for hid, page, weighted in (("caiso-th-sp15-gen-apnd", 42.72, 39.36), ("caiso-th-np15-gen-apnd", 57.22, 58.74),
                                    ("spp-sppnorth-hub", 19.08, 16.61)):
            m = rows[hid]["means"]["da_offpeak_mean_usd"]
            a, w, n = off_peak_week(hid, dt.date.fromisoformat(m["end"]))
            self.assertEqual(n, 88)                                   # 5 weekdays of 8 hours and 2 weekend days of 24
            self.assertAlmostEqual(a, m["v"], delta=0.005)            # the page's figure, the mean of daily means
            self.assertAlmostEqual(round(a, 2), page, delta=0.001)
            self.assertAlmostEqual(round(w, 2), weighted, delta=0.001)


if __name__ == "__main__":
    unittest.main()

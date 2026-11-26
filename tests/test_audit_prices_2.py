"""Audit of the prices pages, finding 2 (session 10218, docs/reviews/prices-model-audit-2026-11-26.md), a figure, not
for landing: "Where power is cheap" (/prices/compare, site/data/price_compare.json of 17 November 2026) lacks real-time
hours that the site's own hourly price files (public/board/h, each hour the mean of its intervals, to the cent) hold.

- SPP North and SPP South, October 2026, real time: "not held" (under 95 percent of the month's hours) on the page;
  the hourly files hold all 744 hours (means 34.35 and 25.30).
- CAISO ZP26, October 2026, real time: 45.35 over 720 of 744 hours (2.08 percent below zero); over all 744 hours of the
  hourly file, 44.88 (2.96 percent).
- SPP North, the twelve months, real time: 31.66 over 8,568 of 8,760 hours; over the hourly file's 8,760, 31.77.

The rule is not at fault: the comparison was built from tables that held fewer hours. The cure is a rebuild on the data
machine (a data request), which moves these figures: Samuel's ruling on when, default "left as it is" until the data
machine's next run. This test shows the gap and passes on main."""
import json
import os
import unittest
import datetime as dt
from zoneinfo import ZoneInfo

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
SITE = os.path.join(ROOT, "site")


def hours(hid, side, start, end, tzname):
    with open(os.path.join(SITE, "public", "board", "h", hid + ".json"), encoding="utf-8") as f:
        hf = json.load(f)
    tz = ZoneInfo(tzname)
    a = int(dt.datetime(start.year, start.month, start.day, tzinfo=tz).timestamp())
    b = int(dt.datetime(end.year, end.month, end.day, tzinfo=tz).timestamp())
    return [v for i, v in enumerate(hf[side]) if v is not None and a <= (hf["t0"] + i) * 3600 < b]


class ComparisonLacksHoursTheSiteHolds(unittest.TestCase):
    def setUp(self):
        with open(os.path.join(SITE, "data", "price_compare.json"), encoding="utf-8") as f:
            self.f = json.load(f)
        if not self.f["built"].startswith("2026-11-17"):
            self.skipTest(f"measured on the copy built 17 November 2026; this one {self.f['built']}")
        self.row = lambda w, e: next(r for r in self.f[w] if r["entity"] == e)

    def test_spp_october_real_time_not_held_here_and_whole_in_the_hourly_files(self):
        oct1, nov1 = dt.date(2026, 10, 1), dt.date(2026, 11, 1)
        for e, hid, mean in (("spp:SPPNORTH_HUB", "spp-sppnorth-hub", 34.35), ("spp:SPPSOUTH_HUB", "spp-sppsouth-hub", 25.30)):
            self.assertNotIn("rtm_avg_price", self.row("month", e))
            h = hours(hid, "rt", oct1, nov1, "America/Chicago")
            self.assertEqual(len(h), 744)
            self.assertAlmostEqual(sum(h) / len(h), mean, delta=0.005)

    def test_zp26_october_real_time_on_720_hours_against_744(self):
        r = self.row("month", "caiso:TH_ZP26_GEN-APND")
        self.assertEqual((r["rtm_hours_held"], r["rtm_avg_price"], r["rtm_negative_hours_share_pct"]), (720, 45.35, 2.08))
        h = hours("caiso-th-zp26-gen-apnd", "rt", dt.date(2026, 10, 1), dt.date(2026, 11, 1), "America/Los_Angeles")
        self.assertEqual(len(h), 744)
        self.assertAlmostEqual(sum(h) / len(h), 44.88, delta=0.005)
        self.assertAlmostEqual(100 * sum(1 for v in h if v < 0) / len(h), 2.96, delta=0.005)

    def test_spp_north_twelve_months_real_time(self):
        r = self.row("year", "spp:SPPNORTH_HUB")
        self.assertEqual((r["rtm_hours_held"], r["rtm_avg_price"]), (8568, 31.66))
        h = hours("spp-sppnorth-hub", "rt", dt.date(2025, 11, 1), dt.date(2026, 11, 1), "America/Chicago")
        self.assertEqual(len(h), 8760)
        self.assertAlmostEqual(sum(h) / len(h), 31.77, delta=0.005)


if __name__ == "__main__":
    unittest.main()

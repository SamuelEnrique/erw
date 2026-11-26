"""Session 10231 (chain 710, part D: the signature explorers audited, docs/reviews/explore-model-audit-2026-11-26.md,
finding 2).

/explore/ercot-peak-premium reads "how much higher" the evening runs than midday as the peak block's median less the
midday block's median, each over every interval of the year. That is not the typical day's gap, and the page says so
for two hubs (its two-hub tip) but not for two blocks. The fix is words only. The data test recomputes the days' gaps
where an extract of HB_HUBAVG's 15-minute prices is named by ERW_AUDIT_HUBAVG (variable, ts_utc, value; the audit's
extract_hubavg.py writes one); the words test runs everywhere.
"""
import csv
import datetime as dt
import os
import statistics
import unittest

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
UTC = dt.timezone.utc


def src(*p):
    with open(os.path.join(ROOT, *p), encoding="utf-8") as f:
        return f.read()


def second_sunday_march_first_sunday_november(y):
    m = dt.date(y, 3, 1)
    m += dt.timedelta(days=(6 - m.weekday()) % 7 + 7)
    n = dt.date(y, 11, 1)
    n += dt.timedelta(days=(6 - n.weekday()) % 7)
    return dt.datetime(m.year, m.month, m.day, 8, tzinfo=UTC), dt.datetime(n.year, n.month, n.day, 7, tzinfo=UTC)


def local(t):
    a, b = second_sunday_march_first_sunday_november(t.year)
    return (t + dt.timedelta(hours=-5 if a <= t < b else -6)).replace(tzinfo=None)


class TheDifferenceOfTwoMediansIsNotTheTypicalDay(unittest.TestCase):
    def test_the_days_gaps_at_the_hub_average(self):
        path = os.environ.get("ERW_AUDIT_HUBAVG")
        if not path or not os.path.exists(path):
            self.skipTest("no extract of HB_HUBAVG's 15-minute prices is named here")
        days = {}
        with open(path, encoding="utf-8", newline="") as f:
            for r in csv.DictReader(f):
                if r["variable"] != "spp_rtm":
                    continue
                t = local(dt.datetime.strptime(r["ts_utc"], "%Y-%m-%dT%H:%M:%SZ").replace(tzinfo=UTC))
                if t.year not in (2015, 2025):
                    continue
                d = days.setdefault(t.date(), ([], []))
                if 16 <= t.hour < 21:
                    d[0].append(float(r["value"]))
                elif 12 <= t.hour < 16:
                    d[1].append(float(r["value"]))
        for y, med, share in ((2025, "18.59", "95.3"), (2015, "-0.44", "44.7")):
            gaps = [statistics.fmean(a) - statistics.fmean(b) for k, (a, b) in days.items() if k.year == y]
            self.assertEqual(len(gaps), 365)
            self.assertEqual(f"{statistics.median(gaps):.2f}", med)
            self.assertEqual(f"{100 * sum(g > 0 for g in gaps) / len(gaps):.1f}", share)

    def test_the_decision_on_the_premium_says_it(self):
        d = src("site", "app", "explore", "ercot-peak-premium", "Decisions.tsx")
        self.assertIn("The difference of the two blocks' medians is not the typical day's gap, as the difference of two hubs' medians is not theirs: taking each day's peak-block mean less its midday-block mean, the median day at the hub average is 18.59 USD/MWh in 2025, where the page's figure is 14.52, and -0.44 in 2015, where it is -0.16; the evening ran above midday on 95.3 percent of 2025's days and on 44.7 percent of 2015's.", d)
        self.assertNotIn(chr(0x2014), d)


if __name__ == "__main__":
    unittest.main()

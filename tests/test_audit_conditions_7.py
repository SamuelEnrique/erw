"""Session 10219 (chain 710, the conditions audit, finding 7): /conditions counts ERCOT's online reserve adder as
scarcity whenever its hourly mean is above zero, however small. In the COVID window the glance prints 20 such hours on
16 March 2020, a day of low demand; at USD 1 the window's most is 6 (8 April), at USD 100 it is 3. Counting at a level
would move the figure, so the ruling is the owner's (docs/reviews/conditions-model-audit-2026-11-26.md). These tests
pass on main: they show the finding, not a fix.
"""
import csv
import json
import os
import unittest
from collections import defaultdict
from datetime import datetime, timezone
from zoneinfo import ZoneInfo

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
DIR = os.path.join(ROOT, "site", "data", "conditions")
OUT = os.path.join(ROOT, "warehouse", "output", "ercot_rtm_price_adders.csv")


def ercot():
    with open(os.path.join(DIR, "ercot.json"), encoding="utf-8") as fh:
        return json.load(fh)


@unittest.skipUnless(os.path.exists(os.path.join(DIR, "ercot.json")), "the conditions files are not in this checkout")
class AboveZeroIsTheCount(unittest.TestCase):
    def test_the_builder_counts_above_zero(self):
        with open(os.path.join(ROOT, "warehouse", "derived", "conditions_page.py"), encoding="utf-8") as fh:
            self.assertIn('int((g["adder"] > 0).sum())', fh.read())

    def test_the_covid_window_prints_20_hours_on_a_day_of_cents(self):
        f = ercot()
        w = [x for x in f["windows"] if x["id"] == "covid_2020"][0]
        dc = f["daily_columns"]
        i, m = dc.index("adder_hours"), dc.index("adder_max")
        days = [r for r in f["daily"] if w["start"] <= r[0] <= w["end"] and r[i] is not None]
        top = max(days, key=lambda r: r[i])
        self.assertEqual((top[0], top[i]), ("2020-03-16", 20))
        # the page's own hours of that day, kept to 0.1: most of the 20 draw as 0.0
        hc = f["hourly_columns"]
        k = hc.index("adder")
        ct = ZoneInfo("America/Chicago")
        day = [r[k] for r in f["hourly"]["covid_2020"] if r[k] is not None and datetime.strptime(r[0], "%Y-%m-%dT%H:%M:%SZ").replace(tzinfo=timezone.utc).astimezone(ct).strftime("%Y-%m-%d") == "2020-03-16"]
        self.assertLess(sum(1 for v in day if v >= 1), 10)
        self.assertGreater(sum(1 for v in day if v == 0.0), 4, "hours counted above zero that the chart draws as 0.0")

    @unittest.skipUnless(os.path.exists(OUT), "ercot_rtm_price_adders is not on this machine")
    def test_at_one_dollar_the_window_most_is_6(self):
        f = ercot()
        w = [x for x in f["windows"] if x["id"] == "covid_2020"][0]
        ct = ZoneInfo("America/Chicago")
        by = defaultdict(list)
        with open(OUT, encoding="utf-8", newline="") as fh:
            for r in csv.DictReader(ln for ln in fh if not ln.startswith("#")):
                if r["variable"] == "rtorpa_mean" and "2020-02-29" <= r["ts_utc"][:10] <= "2020-06-01":
                    d = datetime.strptime(r["ts_utc"], "%Y-%m-%dT%H:%M:%SZ").replace(tzinfo=timezone.utc).astimezone(ct).strftime("%Y-%m-%d")
                    by[d].append(float(r["value"]))
        inw = {d: v for d, v in by.items() if w["start"] <= d <= w["end"]}
        self.assertEqual(max(sum(1 for x in v if x > 0) for v in inw.values()), 20)
        self.assertEqual(max(sum(1 for x in v if x >= 1) for v in inw.values()), 6)
        self.assertEqual(max(sum(1 for x in v if x >= 100) for v in inw.values()), 3)


if __name__ == "__main__":
    unittest.main()

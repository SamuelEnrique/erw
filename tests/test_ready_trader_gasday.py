"""wip/ready-trader-gasday (session 11406, chain 770, part C): the other choice of the trader view audit of
26 November, finding 2 (docs/reviews/trader-model-audit-2026-11-26.md), readied for Samuel's ruling, not requested.

On main the implied heat rate divides the day-ahead daily mean by the Henry Hub spot EIA dates on the operating day, or
up to 4 days before: gas traded a day after the power, and at the newest days gas up to 4 days older. On this branch
warehouse/derived/trader_view.py takes the gas of the trading day before the operating day (gas_day: weekends and NERC
holidays stepped over), and a newest day whose gas is not yet published has no heat rate. Measured from the page's own
files (the ERCOT hub average's hourly file and the Henry Hub series of the board), main's rule against the branch's
own hh_for, printed; the audit measured 0.31 MMBtu/MWh on average, at most 4.86, over 363 days to 20 November.
iso_trader_daily is rebuilt at landing by the desk. The audit's measurement (tests/test_audit_trader_2.py on
wip/audit-trader-2) is carried."""
import collections
import datetime as dt
import json
import os
import statistics
import sys
import unittest
from zoneinfo import ZoneInfo

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
SITE = os.path.join(ROOT, "site")
sys.path.insert(0, os.path.join(ROOT, "warehouse", "derived"))
sys.path.insert(0, os.path.join(ROOT, "warehouse", "connectors"))


def daily_means(hid, days=365):
    with open(os.path.join(SITE, "public", "board", "h", hid + ".json"), encoding="utf-8") as f:
        hf = json.load(f)
    tz = ZoneInfo(hf["tz"])
    by = collections.defaultdict(list)
    for i, v in enumerate(hf["da"]):
        if v is not None:
            by[dt.datetime.fromtimestamp((hf["t0"] + i) * 3600, tz=dt.timezone.utc).astimezone(tz).date()].append(v)
    out = {}
    for d, vs in by.items():
        a = dt.datetime(d.year, d.month, d.day, tzinfo=tz).astimezone(dt.timezone.utc)
        n = d + dt.timedelta(days=1)
        if len(vs) == round((dt.datetime(n.year, n.month, n.day, tzinfo=tz).astimezone(dt.timezone.utc) - a).total_seconds() / 3600):
            out[d] = sum(vs) / len(vs)
    last = max(out)
    return {d: m for d, m in out.items() if (last - d).days < days}


def henry_hub():
    with open(os.path.join(SITE, "public", "board", "s", "eia-henry-hub-spot.json"), encoding="utf-8") as f:
        s = json.load(f)
    t0 = dt.date.fromisoformat(s["t0"])
    return {t0 + dt.timedelta(days=d): v for d, v in zip(s["d"], s["v"])}


def main_rule(day, hh):
    for k in range(0, 5):
        if day - dt.timedelta(days=k) in hh:
            return hh[day - dt.timedelta(days=k)]
    return None


class TheGasOfTheTradingDayBefore(unittest.TestCase):
    def tv(self):
        try:
            import trader_view
        except Exception as exc:
            self.skipTest(f"trader_view does not import here: {exc}")
        return trader_view

    def test_gas_day(self):
        tv = self.tv()
        self.assertEqual(tv.gas_day(dt.date(2026, 11, 24)), dt.date(2026, 11, 23))   # Tuesday: Monday's gas
        self.assertEqual(tv.gas_day(dt.date(2026, 11, 23)), dt.date(2026, 11, 20))   # Monday: Friday's
        self.assertEqual(tv.gas_day(dt.date(2026, 11, 22)), dt.date(2026, 11, 20))   # Sunday: Friday's
        self.assertEqual(tv.gas_day(dt.date(2026, 11, 27)), dt.date(2026, 11, 25))   # the day after Thanksgiving
        hh = {dt.date(2026, 11, 20): 3.0}
        self.assertEqual(tv.hh_for(dt.date(2026, 11, 23), hh, None), (3.0, dt.date(2026, 11, 20)))
        self.assertEqual(tv.hh_for(dt.date(2026, 11, 25), hh, None), (None, None))   # Tuesday's gas not yet published: none

    def test_the_move_on_the_pages_files(self):
        tv = self.tv()
        hh = henry_hub()
        means = daily_means("ercot-hb-hubavg")
        diffs, lost = [], 0
        for d, m in sorted(means.items()):
            g0, (g1, _) = main_rule(d, hh), tv.hh_for(d, hh, None)
            if g0 and g0 > 0 and not g1:
                lost += 1
            if g0 and g1 and g0 > 0 and g1 > 0:
                diffs.append(m / g1 - m / g0)
        print(f"ERCOT hub average, {len(diffs)} days to {max(means)}: mean {statistics.mean(diffs):+.3f}, mean absolute "
              f"{statistics.mean(abs(x) for x in diffs):.3f}, largest {max(diffs, key=abs):+.3f} MMBtu/MWh, "
              f"more than 0.5: {sum(1 for x in diffs if abs(x) > 0.5)}, days with no heat rate now: {lost}")
        self.assertGreater(len(diffs), 200)
        self.assertGreater(statistics.mean(abs(x) for x in diffs), 0.2)

    def test_the_words(self):
        with open(os.path.join(SITE, "components", "board", "BoardView.tsx"), encoding="utf-8") as f:
            self.assertIn("over the Henry Hub spot price of the trading day before, when the day-ahead power traded", f.read())
        with open(os.path.join(ROOT, "docs", "methods", "trader_view.md"), encoding="utf-8") as f:
            self.assertIn("the one EIA dates on the trading day before the operating day", f.read())


if __name__ == "__main__":
    unittest.main()

"""Session 11407 (chain 770 part C), readied from session 10225's test of the events audit's finding 9
(wip/audit-events-9, docs/reviews/events-model-audit-2026-11-26.md): Uri's comparisons with the baseline
(demand_mwh_vs_baseline, net_generation_mwh_vs_baseline) are now against the same weekday 364 and 728 days earlier,
the rule of every later event, in place of the same calendar day of 2019 and 2020 (warehouse/derived/event_window.py,
EVENTS[0]["offsets"]). The baseline days after 24 February of 2019 and 2020 are read from the extract and not
written, so the rows the charts and the event study read do not change.

Measured by the builder of this branch and of origin/main on this machine's extract (retrieved 2026-10-04, output to
a scratch folder): Sunday 2021-02-21's shortfall of net generation, the page's largest (-186,530.50 MWh), is
-37,630.50, and the largest shortfall becomes 2021-02-24's, -140,891.00 MWh. On the published table's rows alone
(15 of 18 days, its 2019 and 2020 rows stop at 24 February) the largest would be the 21st's -37,630.50, the figure the
weekend page quotes. For the owner's ruling, not for landing alone.
"""
import csv
import datetime as dt
import os
import sys
import unittest
from unittest import mock

import pandas as pd

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
ROWS = os.path.join(ROOT, "replication", "events", "window_rows.csv")
for p in (("warehouse", "derived"), ("warehouse", "connectors")):
    if os.path.join(ROOT, *p) not in sys.path:
        sys.path.insert(0, os.path.join(ROOT, *p))


def src(*p):
    with open(os.path.join(ROOT, *p), encoding="utf-8") as fh:
        return fh.read()


@unittest.skipUnless(os.path.exists(ROWS), "the replication's public rows are not in this checkout")
class TheTwoRulesOnThePublishedRows(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        with open(ROWS, encoding="utf-8") as fh:
            cls.v = {r["ts_utc"][:10]: float(r["value"]) for r in csv.DictReader(l for l in fh if not l.startswith("#"))
                     if r["event"] == "uri_2021" and r["entity"] == "eia930:ERCO" and r["variable"] == "net_generation_mwh"}

    def test_the_calendar_rule_gave_the_page(self):
        v = self.v
        cal = {d: v[d] - (v[f"2019{d[4:]}"] + v[f"2020{d[4:]}"]) / 2 for d in v if d.startswith("2021") and f"2019{d[4:]}" in v and f"2020{d[4:]}" in v}
        lo = min(cal, key=cal.get)
        self.assertEqual((lo, round(cal[lo], 2)), ("2021-02-21", -186530.5))
        self.assertEqual([dt.date.fromisoformat(x).strftime("%A") for x in ("2021-02-21", "2019-02-21", "2020-02-21")], ["Sunday", "Thursday", "Friday"])

    def test_the_weekday_rule_on_the_rows_held(self):
        v = self.v
        wk = {}
        for d in v:
            if not d.startswith("2021"):
                continue
            t = dt.date.fromisoformat(d)
            b = [v.get((t - dt.timedelta(days=o)).isoformat()) for o in (364, 728)]
            if None not in b:
                wk[d] = v[d] - sum(b) / 2
        self.assertEqual(len(wk), 15, "the published rows hold both weekday baseline days for 15 of 18 days")
        self.assertEqual(round(wk["2021-02-21"], 2), -37630.5)
        lo = min(wk, key=wk.get)
        self.assertEqual((lo, round(wk[lo], 2)), ("2021-02-21", -37630.5))


class TheBuilderUsesTheWeekdayRule(unittest.TestCase):
    """event_window.build on a made-up extract: the comparison reads the same weekday 364 and 728 days earlier, a
    baseline day outside the written windows included, and writes no row for that day."""

    def test_the_rule_in_the_builder(self):
        import event_window as ew
        e = ew.EVENTS[0]
        self.assertEqual((e["event"], e["offsets"], e["baseline"]), ("uri_2021", [364, 728], [2019, 2020]))
        hours = pd.date_range("2019-02-01T06:00:00Z", "2021-03-02T06:00:00Z", freq="h", inclusive="left")
        day = hours.tz_convert("America/Chicago").strftime("%Y-%m-%d")
        base = pd.Series([1000.0 + 3.0 * int(d[8:]) + 400.0 * (dt.date.fromisoformat(d).weekday() == 6) + 50.0 * (int(d[:4]) - 2019) for d in day])
        x = pd.DataFrame({"ts_utc": hours.strftime("%Y-%m-%dT%H:%M:%SZ"), "demand_mwh": base + 7.0, "net_generation_mwh": base})
        # one price interval (an incomplete day, left out), so the frame keeps its columns through the builder's filter
        empty_prices = pd.DataFrame([{"entity": "ercot:HB_HUBAVG", "variable": "spp_rtm", "ts_utc": "2021-02-07T06:00:00Z", "value": 20.0,
                                      "market": "ercot_rtm", "year": "2021"}])
        empty_co2 = pd.DataFrame(columns=["entity", "variable", "ts_utc", "value", "ba"])
        env = {k: v for k, v in os.environ.items() if k != "ERW_SCREEN_TRIAL"}
        with mock.patch.dict(os.environ, env, clear=True), \
                mock.patch.object(ew.em, "latest_extract", return_value="made-up"), \
                mock.patch.object(ew.em, "extract_meta", return_value=("url", "lm", "got")), \
                mock.patch.object(ew.em, "read_extract", return_value=x), \
                mock.patch.object(ew, "stream", side_effect=lambda name, keep, cols: empty_prices.copy() if name == ew.PRICES else empty_co2.copy()):
            rows, left, _ = ew.build(e, lambda m: None, "2026-11-28T00:00:00Z")
        r = pd.DataFrame(rows)
        lvl = r[r["variable"] == "net_generation_mwh"].set_index("ts_utc")["value"]
        cmp_ = r[r["variable"] == "net_generation_mwh_vs_baseline"].set_index("ts_utc")["value"]
        daily = lambda d: 24 * (1000.0 + 3.0 * int(d[8:]) + 400.0 * (dt.date.fromisoformat(d).weekday() == 6) + 50.0 * (int(d[:4]) - 2019))  # noqa: E731
        self.assertEqual(len(cmp_), 18, "every event day has its comparison")
        # Sunday 2021-02-21 against Sundays 2020-02-23 and 2019-02-24
        self.assertAlmostEqual(cmp_["2021-02-21T00:00:00Z"], daily("2021-02-21") - (daily("2020-02-23") + daily("2019-02-24")) / 2, places=4)
        # 2021-02-24 against 2020-02-26 and 2019-02-27, days outside the written windows: read, not written
        self.assertAlmostEqual(cmp_["2021-02-24T00:00:00Z"], daily("2021-02-24") - (daily("2020-02-26") + daily("2019-02-27")) / 2, places=4)
        self.assertNotIn("2019-02-27T00:00:00Z", lvl.index)
        self.assertNotIn("2020-02-26T00:00:00Z", lvl.index)
        self.assertEqual(sorted({t[:4] for t in lvl.index}), ["2019", "2020", "2021"])
        self.assertEqual(len(lvl), 54, "the written rows stay the three calendar windows")
        self.assertEqual([x_ for x_ in left if "baseline" in x_], [])

    def test_the_page_and_notes_say_it(self):
        page = src("site", "app", "events", "uri-2021", "page.tsx")
        self.assertIn("Largest shortfall against the average of the same weekday 364 and 728 days earlier:", page)
        self.assertNotIn("Largest shortfall against the 2019 and 2020 average for the same day", page)
        self.assertIn("the shortfall the day minus the mean of the same weekday 364 and 728 days earlier", page)
        self.assertIn("The comparisons with the baseline: the same weekday 364 and 728 days earlier (session 11407).", src("site", "app", "events", "Decisions.tsx"))
        note = src("docs", "methods", "events.md")
        self.assertIn("the largest shortfall becomes 2021-02-24's, -140,891.00 MWh", note)
        for p in (("site", "app", "events", "uri-2021", "page.tsx"), ("docs", "methods", "events.md"), ("warehouse", "derived", "event_window.py")):
            self.assertNotIn(chr(0x2014), src(*p), p)


if __name__ == "__main__":
    unittest.main()

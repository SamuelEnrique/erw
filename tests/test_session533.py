"""Session 533 (21 October 2026): the Roundup's chart shows the number it calls notable.

The Roundup audit's fix 11 (docs/reviews/roundup-audit-2026-10-21.md): the chart of the week of 2026-W39 named the
latest week's peak-minus-midday gap at ERCOT HB_NORTH, 28.08 USD/MWh, and drew only the 30-day block quartiles, so no
bar held that number. Held here:
  1. warehouse/analysis/style.py: a spec's `mark` (mark_of, mark_point) is drawn as an ECharts markPoint (the site's SVG
     reader, site/lib/svgoption.ts, draws its coord and its name) and as a cardinal ring with the figure and its key on
     every PNG; the ring's value is the series' own, never one handed in with the mark.
  2. warehouse/analysis/templates/common.py: headline_mark finds the headline in the chart (its period on a category
     axis, the series' value there equal to the headline's) and result() sets the mark; a chart that does not hold the
     headline gets none.
  3. warehouse/analysis/templates/peak_premium_block.py: the chart is the peak-minus-midday spread of each 7-day window,
     and its series holds the headline value at its period (the audit's test), on a fixture of 15-minute prices.
  4. The stored record: W39's stored chart does not hold its headline (the fault, as it was), and W41's stored watch
     line does, at its period. On a machine with the tables, W39 is computed again from them and its headline, 28.08
     at 2026-09-20 to 2026-09-26, is the marked bar.
No network, no model, nothing written outside a temporary folder. Nothing here sets the environment at import.
"""
import json
import os
import sys
import tempfile
import unittest
from unittest import mock

import pandas as pd

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
ANALYSIS = os.path.join(ROOT, "warehouse", "analysis")
TEMPLATES = os.path.join(ANALYSIS, "templates")
for p in (TEMPLATES, ANALYSIS):
    if p not in sys.path:
        sys.path.insert(0, p)
import style  # noqa: E402
import common  # noqa: E402
import peak_premium_block as ppb  # noqa: E402

EM = chr(0x2014)


def stored(week):
    with open(os.path.join(ROOT, "docs", "analysis", week, "chart_of_the_week.json"), encoding="utf-8") as f:
        return json.load(f)


def weekly_spec(values, mark=None, kind="line", stacked=False, series=None):
    x = [str((pd.Timestamp("2026-08-03") + pd.Timedelta(days=7 * k)).date()) for k in range(len(values))]
    spec = {"kind": kind, "x": x, "x_label": "Week starting", "y_label": "USD/MWh", "stacked": stacked,
            "series": series or [{"name": "A measure", "values": values}], "title": "A title", "subtitle": "A subtitle",
            "source": "Source: a test fixture.", "name": "t"}
    if mark:
        spec["mark"] = mark
    return spec


class TheMarkInTheSharedStyle(unittest.TestCase):
    def test_the_option_carries_a_markpoint_at_the_value_with_its_figure_and_key(self):
        spec = weekly_spec([10.0, 12.5, 28.08], {"series": 0, "at": 2, "label": "28.08 USD/MWh", "key": "week of 2026-08-17 to 2026-08-23"})
        opt = style.echarts(spec)
        mp = opt["series"][0]["markPoint"]
        self.assertEqual(mp["data"][0]["coord"], ["2026-08-17", 28.08])
        self.assertEqual(mp["data"][0]["name"], "28.08 USD/MWh, week of 2026-08-17 to 2026-08-23")
        self.assertEqual(mp["itemStyle"]["borderColor"], style.ACCENT)
        self.assertNotIn(EM, json.dumps(opt))

    def test_the_value_is_the_series_own(self):
        m = style.mark_of(weekly_spec([10.0, 12.5, 28.08], {"series": 0, "at": 1, "label": "99 USD/MWh"}))
        self.assertEqual(m["value"], 12.5)
        self.assertEqual(m["y"], 12.5)

    def test_a_mark_on_nothing_is_not_drawn(self):
        for mark in ({"series": 0, "at": 9}, {"series": 3, "at": 0}, {"series": 0, "at": 1}):
            spec = weekly_spec([10.0, None, 3.0], mark)
            self.assertIsNone(style.mark_of(spec), mark)
            self.assertNotIn("markPoint", style.echarts(spec)["series"][0])

    def test_no_mark_no_markpoint(self):
        self.assertNotIn("markPoint", style.echarts(weekly_spec([1.0, 2.0]))["series"][0])

    def test_a_stacked_bar_s_ring_sits_on_its_segment_s_top(self):
        spec = weekly_spec([], {"series": 1, "at": 1}, kind="bar", stacked=True,
                           series=[{"name": "a", "values": [1, 2, 3]}, {"name": "b", "values": [4, 5, 6]}])
        spec["x"] = spec["x"] or ["2026-08", "2026-09", "2026-10"]
        m = style.mark_of(spec)
        self.assertEqual((m["value"], m["y"]), (5.0, 7.0))
        self.assertEqual(style.echarts(spec)["series"][1]["markPoint"]["data"][0]["coord"], ["2026-09", 7.0])

    def test_every_size_draws_with_a_mark_on_bars_lines_and_a_time_axis(self):
        specs = [weekly_spec([10.0, 12.5, 28.08], {"series": 0, "at": 2, "label": "28.08 USD/MWh", "key": "a week"}, kind=k)
                 for k in ("bar", "line")]
        t = weekly_spec([3.0, 4.0, 2.0], {"series": 0, "at": 0, "label": "3 USD/MWh", "key": "a day"})
        t.update(x_time=True, x=["2026-08-03T00:00:00Z", "2026-08-04T00:00:00Z", "2026-08-05T00:00:00Z"])
        g = weekly_spec([], {"series": 1, "at": 0, "label": "5"}, kind="bar",
                        series=[{"name": "a", "values": [1, 2]}, {"name": "b", "values": [5, 1]}])
        g["x"] = ["overnight", "midday"]
        with tempfile.TemporaryDirectory() as d:
            for i, spec in enumerate(specs + [t, g]):
                for size in style.SIZES:
                    path = os.path.join(d, f"{i}_{size}.png")
                    style.png(spec, path, size)
                    self.assertGreater(os.path.getsize(path), 5000, (i, size))


class TheHeadlineFoundInTheChart(unittest.TestCase):
    def test_a_weekly_headline_at_its_first_day(self):
        chart = weekly_spec([10.0, 12.5, 28.08])
        m = common.headline_mark(chart, {"value": 28.08, "unit": "USD/MWh", "period": "2026-08-17 to 2026-08-23"})
        self.assertEqual(m, {"series": 0, "at": 2, "label": "28.08 USD/MWh", "key": "week of 2026-08-17 to 2026-08-23"})

    def test_a_monthly_headline_and_its_key_in_words(self):
        chart = {"kind": "bar", "x": ["2026-07", "2026-08"], "series": [{"name": "a", "values": [3, 4]}, {"name": "b", "values": [6, 19]}]}
        m = common.headline_mark(chart, {"value": 19, "unit": "hours", "period": "2026-08"})
        self.assertEqual(m, {"series": 1, "at": 1, "label": "19 hours", "key": "August 2026"})

    def test_none_where_the_chart_does_not_hold_it(self):
        chart = weekly_spec([10.0, 12.5, 28.08])
        self.assertIsNone(common.headline_mark(chart, {"value": 28.07, "unit": "USD/MWh", "period": "2026-08-17 to 2026-08-23"}))
        self.assertIsNone(common.headline_mark(chart, {"value": 12.5, "unit": "USD/MWh", "period": "2026-08-17 to 2026-08-23"}))
        self.assertIsNone(common.headline_mark(chart, {"value": 28.08, "unit": "USD/MWh", "period": "2026-09"}))
        t = dict(chart, x_time=True, x=[f"{x}T00:00:00Z" for x in chart["x"]])
        self.assertIsNone(common.headline_mark(t, {"value": 28.08, "unit": "USD/MWh", "period": "2026-08-17 to 2026-08-23"}))
        s = dict(chart, kind="scatter")
        self.assertIsNone(common.headline_mark(s, {"value": 28.08, "unit": "USD/MWh", "period": "2026-08-17 to 2026-08-23"}))

    def test_result_sets_the_mark_and_keeps_one_a_template_set(self):
        with mock.patch.object(common, "source_line", lambda tables, extra="": "Source: a test fixture."), \
                mock.patch.object(common, "citations", lambda tables: []):
            h = {"label": "x", "value": 28.08, "unit": "USD/MWh", "period": "2026-08-17 to 2026-08-23", "history": []}
            r = common.result("t", {}, "T", "S", pd.DataFrame(), [], weekly_spec([10.0, 12.5, 28.08]), h, [])
            self.assertEqual(r["chart"]["mark"]["at"], 2)
            own = dict(weekly_spec([10.0, 12.5, 28.08]), mark={"series": 0, "at": 0})
            r = common.result("t", {}, "T", "S", pd.DataFrame(), [], own, h, [])
            self.assertEqual(r["chart"]["mark"], {"series": 0, "at": 0})
            r = common.result("t", {}, "T", "S", pd.DataFrame(), [], weekly_spec([10.0, 12.5, 28.0]), h, [])
            self.assertNotIn("mark", r["chart"])

    def test_the_period_s_key(self):
        self.assertEqual(common.period_key("2026-09-20 to 2026-09-26"), "week of 2026-09-20 to 2026-09-26")
        self.assertEqual(common.period_key("2026-10-02 to 2026-10-10"), "2026-10-02 to 2026-10-10")
        self.assertEqual(common.period_key("2026-08"), "August 2026")
        self.assertEqual(common.period_key("2026-09-28"), "2026-09-28")


def fixture_prices():
    """45 complete local days of 15-minute prices at a test hub, in July and August 2026 (Chicago, no clock change):
    overnight 20, midday 30, peak 40 plus the day's number in the run (so each week's gap differs). A test fixture,
    not data: it is never written anywhere."""
    tz = "America/Chicago"
    idx = pd.date_range(pd.Timestamp("2026-07-01", tz=tz), pd.Timestamp("2026-08-15", tz=tz), freq="15min", inclusive="left")
    day = (idx.normalize() - idx[0].normalize()).days
    h = idx.hour
    value = [40.0 + d if 16 <= hh < 21 else (30.0 if 12 <= hh < 16 else 20.0) for d, hh in zip(day, h)]
    return pd.DataFrame({"ts_utc": idx.tz_convert("UTC"), "value": value, "node": "TEST_HUB"}), tz


class ThePeakPremiumChartHoldsItsHeadline(unittest.TestCase):
    def compute(self, **kw):
        df, tz = fixture_prices()
        with mock.patch.object(ppb, "_prices", lambda iso, hub, history: (df, ["iso_rtm_hub_prices"], tz)), \
                mock.patch.object(common, "source_line", lambda tables, extra="": "Source: a test fixture."), \
                mock.patch.object(common, "citations", lambda tables: []):
            return ppb.compute(iso="ercot", hub="TEST_HUB", **kw)

    def test_the_chart_series_holds_the_headline_value_at_its_period(self):
        res = self.compute()
        h, c = res["headline"], res["chart"]
        at = c["x"].index(h["period"].split(" to ")[0])
        self.assertEqual(at, len(c["x"]) - 1)
        self.assertEqual(c["series"][0]["values"][at], h["value"])
        self.assertEqual(c["mark"], {"series": 0, "at": at, "label": f"{style.fmt(h['value'])} USD/MWh", "key": f"week of {h['period']}"})
        # the fixture's last window is days 38 to 44: the peak median is 40 + 41 = 81, midday 30
        self.assertEqual((h["period"], h["value"]), ("2026-08-08 to 2026-08-14", 51.0))
        opt = ppb.render(res, "site")
        self.assertEqual(opt["series"][0]["markPoint"]["data"][0]["coord"], ["2026-08-08", 51.0])

    def test_each_bar_is_one_window_s_spread_and_the_frame_holds_it(self):
        res = self.compute()
        f = res["frame"]
        weekly = f[f["measure"] == "peak minus midday median, 7 days"]
        self.assertEqual(weekly["first_day"].tolist(), res["chart"]["x"])
        self.assertEqual(weekly["value"].tolist(), res["chart"]["series"][0]["values"])
        self.assertTrue(((weekly["peak_median"] - weekly["midday_median"]).round(2) == weekly["value"]).all())
        self.assertLessEqual(len(res["chart"]["x"]), ppb.WEEKS_SHOWN)
        blocks = f[f["measure"] == "block quartile, 30 days"]
        self.assertEqual(len(blocks), 9)

    def test_the_headline_and_facts_are_as_before(self):
        res = self.compute()
        self.assertEqual(res["headline"]["label"], "peak minus midday median, latest 7 days")
        self.assertIn(f"Peak minus midday median, {res['headline']['period']}: {res['headline']['value']} USD/MWh.", res["facts"])
        self.assertTrue(res["facts"][0].startswith("ERCOT TEST_HUB real-time prices, 2026-07-16 to 2026-08-14 (30 days): median overnight"))
        self.assertTrue(res["title"].endswith(": real-time prices by time of day"))  # the Roundup prints the title

    def test_the_seven_day_window_draws_the_same_bars(self):
        a, b = self.compute(window=30), self.compute(window=7)
        self.assertEqual(a["chart"]["series"], b["chart"]["series"])
        self.assertEqual(a["headline"]["value"], b["headline"]["value"])


class TheStoredWeeks(unittest.TestCase):
    def test_w39_s_stored_chart_did_not_hold_its_headline(self):
        c = stored("2026-W39")
        self.assertEqual((c["template"], c["headline"]["value"]), ("peak_premium_block", 28.08))
        self.assertIsNone(common.headline_mark(c["chart"], c["headline"]))

    def test_w41_s_stored_watch_line_holds_its_headline_at_its_period(self):
        c = stored("2026-W41")
        m = common.headline_mark(c["chart"], c["headline"])
        self.assertEqual(m["at"], len(c["chart"]["x"]) - 1)
        self.assertEqual(m["key"], f"week of {c['headline']['period']}")

    def test_w39_computed_again_from_the_tables_marks_28_08(self):
        data = os.environ.get("ERW_DATA_DIR") or os.path.join(ROOT, "warehouse", "output")
        if not os.path.exists(os.path.join(data, "iso_rtm_hub_prices.csv")) or not os.path.exists(os.path.join(data, "ercot_all_hub_prices_history.csv")):
            raise unittest.SkipTest("the ERCOT real-time tables are not on this machine")
        c = stored("2026-W39")
        orig, cut = ppb._prices, pd.Timestamp("2026-09-26").date()

        def cut_prices(iso, hub, history):
            df, tables, tz = orig(iso, hub, history)
            return df[df["ts_utc"].dt.tz_convert(tz).dt.date <= cut], tables, tz
        with mock.patch.object(ppb, "_prices", cut_prices):
            try:
                res = ppb.compute(**c["params"])
            except common.NoData as exc:
                raise unittest.SkipTest(f"the tables here do not reach 2026-W39: {exc}")
        h = res["headline"]
        self.assertEqual((h["period"], h["value"]), (c["headline"]["period"], 28.08))
        m = res["chart"]["mark"]
        self.assertEqual(res["chart"]["x"][m["at"]], "2026-09-20")
        self.assertEqual(res["chart"]["series"][0]["values"][m["at"]], 28.08)


if __name__ == "__main__":
    unittest.main()

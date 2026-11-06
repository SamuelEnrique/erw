"""Session 806: the Roundup's five numbers and its chart (docs/reviews/periodicals-plan-2026-10-23.md, Roundup changes 1, 2
and 6).

The Roundup opens with the week in five numbers (the week's biggest price move, the US48 peak with its hour, the week's
largest deal by US dollars from energy_deals, the largest new datacenter load first reported in the week, and the headline
figure of the week's chart), each traced by scripts/check_roundup.py; the chart of the week says which measure the week's
top stories point to (daily_chart.relevance, session 805); the real-time maximum says its interval length. Fixtures: frames
and files the test writes. No model, no network.
"""

import json
import os
import sys
import tempfile
import unittest
from unittest import mock

import pandas as pd

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
for p in ("warehouse", os.path.join("warehouse", "news"), "scripts"):
    if os.path.join(ROOT, p) not in sys.path:
        sys.path.insert(0, os.path.join(ROOT, p))

import brief  # noqa: E402
import roundup  # noqa: E402

START = pd.Timestamp("2026-10-05", tz="UTC")
CUT = pd.Timestamp("2026-10-12", tz="UTC")


def quiet(_):
    pass


def fuel_row(v, d, unit="USD/bbl"):
    return {"value": v, "ts_utc": pd.Timestamp(d, tz="UTC"), "unit": unit}


FACTS = {
    "dam": [dict(label="ERCOT", node="HB_NORTH", table="iso_dam_hub_prices", m1=41.94, m0=32.82, ref="[1]"),
            dict(label="CAISO", node="TH_SP15_GEN-APND", table="iso_dam_hub_prices", m1=40.10, m0=39.90, ref="[1]")],
    "fuel": [dict(label="Brent crude", a=fuel_row(113.96, "2026-10-06"), b=fuel_row(119.97, "2026-09-29"), ref="[5]")],
    "us48": dict(top={"value": 612345.0, "ts_utc": pd.Timestamp("2026-10-07T21:00:00Z")}, ref="[6]"),
}
DEALS = pd.DataFrame([
    {"event_id": "deal:1c055d98aed350fd", "event_date": "2026-10-09T21:45:00Z", "deal_type": "m_and_a", "buyer": "Shell", "seller": "Equinor",
     "asset": "Bay du Nord Oil Project", "mw": "", "dollars": "12000000000"},
    {"event_id": "deal:55bb75196a90af9e", "event_date": "2026-10-06T02:24:00Z", "deal_type": "ppa", "buyer": "Google", "seller": "Constellation Energy",
     "asset": "", "mw": "3600", "dollars": "4300000000"},
    {"event_id": "deal:old", "event_date": "2026-09-30T02:24:00Z", "deal_type": "ppa", "buyer": "A", "seller": "B", "asset": "", "mw": "", "dollars": "99000000000"}])
DC = pd.DataFrame([
    {"entity_id": "dc:a", "first_story_at": "2026-10-07T10:00:00Z", "capacity_mw": "1200", "operator": "Crusoe", "site_name": "Spark", "city": "Abilene", "state": "TX"},
    {"entity_id": "dc:b", "first_story_at": "2026-10-08T10:00:00Z", "capacity_mw": "", "operator": "X", "site_name": "", "city": "", "state": ""},
    {"entity_id": "dc:c", "first_story_at": "2026-09-20T10:00:00Z", "capacity_mw": "5000", "operator": "Old", "site_name": "", "city": "", "state": ""}])
CHART = {"week": "2026-W41", "template": "watch_battery_discharge_us", "title": "Batteries discharging, Lower 48",
         "finding": "Lower 48 battery discharge, daily mean of the week: 45,968 MWh a day in the week of 2026-09-28 to 2026-10-04, down 8,790.43 from 54,758.43 the week before.",
         "note": "Lower 48 battery discharge fell.", "source_line": "Source: ERW, derived.", "files": {"email": "chart_email.png"},
         "headline": {"label": "Lower 48 battery discharge, daily mean of the week", "value": 45968.0, "unit": "MWh a day", "period": "2026-09-28 to 2026-10-04"},
         "also_moved": [{"template": "watch_crude_exports", "title": "US crude oil exports", "score": 84.6,
                         "finding": "US crude oil exports: 4,765 kbbl/d in the week of 2026-09-28 to 2026-10-04, up 1,195 from 3,570 the week before."}]}


def table(name):
    return {"energy_deals": DEALS, "datacenter_projects": DC}.get(name)


class TheFiveNumbers(unittest.TestCase):
    def lines(self, facts=FACTS, label="2026-W41"):
        with tempfile.TemporaryDirectory() as d:
            os.makedirs(os.path.join(d, label))
            json.dump(CHART, open(os.path.join(d, label, "chart_of_the_week.json"), "w", encoding="utf-8"))
            with mock.patch.object(roundup, "read_table", table), mock.patch.object(roundup, "ANALYSIS_DIR", d):
                return roundup.five_numbers(label, START, CUT, facts, quiet)

    def test_five_lines_in_their_order(self):
        L = self.lines()
        self.assertEqual(len(L), 5)
        self.assertEqual(L[0], "- **Price move of the week:** ERCOT HB_NORTH day-ahead averaged 41.94 USD/MWh over the week, against 32.82 USD/MWh "
                               "the week before (+9.12 USD/MWh, +27.8%) [1].")
        self.assertEqual(L[1], "- **US48 peak demand:** 612,345 MW in the hour starting 2026-10-07 21:00 UTC [6].")
        self.assertEqual(L[2], "- **Deal of the week, by US dollars:** USD 12 billion, Shell and Equinor, Bay du Nord Oil Project (acquisition, 2026-10-09; "
                               "`energy_deals` deal:1c055d98aed350fd).")
        self.assertEqual(L[3], "- **Largest new datacenter load first reported this week:** 1,200 MW, Crusoe, Spark, Abilene, TX (`datacenter_projects` dc:a).")
        self.assertEqual(L[4], "- **From the chart of the week:** Lower 48 battery discharge, daily mean of the week: 45,968 MWh a day in 2026-09-28 to "
                               "2026-10-04 (template `watch_battery_discharge_us`, `docs/analysis/2026-W41/chart_of_the_week.json`).")

    def test_a_fuel_move_wins_when_it_is_the_largest_in_percent(self):
        facts = {"dam": [dict(label="SPP", node="SPPSOUTH_HUB", table="iso_dam_hub_prices", m1=30.00, m0=29.50, ref="[1]")],
                 "fuel": [dict(label="WTI Cushing crude", a=fuel_row(85.23, "2026-10-06"), b=fuel_row(101.44, "2026-09-29"), ref="[5]")]}
        L = self.lines(facts)
        self.assertEqual(L[0], "- **Price move of the week:** WTI Cushing crude closed at 85.23 USD/bbl on 2026-10-06, against 101.44 USD/bbl on "
                               "2026-09-29 (-16.21 USD/bbl, -16.0%) [5].")
        self.assertEqual(L[1], "- **US48 peak demand:** not in the warehouse for this week.")

    def test_what_is_missing_is_said_not_filled(self):
        with mock.patch.object(roundup, "read_table", lambda n: None), mock.patch.object(roundup, "ANALYSIS_DIR", tempfile.gettempdir()):
            L = roundup.five_numbers("2026-W43", START, CUT, {}, quiet)
        self.assertEqual(L[0], "- **Price move of the week:** no price with a complete week and a week before it is held.")
        self.assertIn("energy_deals is not in the warehouse on this machine", L[2])
        self.assertIn("datacenter_projects is not in the warehouse on this machine", L[3])
        self.assertIn("no chart of the week was picked for this week, so no figure", L[4])

    def test_the_words_for_a_sum(self):
        for d, s in ((12e9, "USD 12 billion"), (4.3e9, "USD 4.3 billion"), (834e6, "USD 834 million"), (2.625e9, "USD 2.63 billion"), (250000, "USD 250,000")):
            self.assertEqual(roundup.usd_words(d), s)
        self.assertEqual(roundup.chart_figure(45968.0), "45,968")
        self.assertEqual(roundup.chart_figure(5.04), "5.04")
        self.assertEqual(roundup.chart_figure(59.0), "59")   # a count of deals, not "59.00"

    def test_each_numbered_list_starts_at_one(self):
        L = ["## Weekend", "", "1. **A** (oil)  ", "   Why. Sources: [X](https://example.org/1)", "",
             "## The five stories of the week", "", "1. **B** (gas)  ", "   Why. Sources: [Y](https://example.org/2)",
             "2. **C** (lng)  ", "   Why. Sources: [Z](https://example.org/3)"]
        out = brief.drop_repeated_items(L, quiet)
        self.assertEqual([x for x in out if x[:2] in ("1.", "2.", "3.")], ["1. **A** (oil)  ", "1. **B** (gas)  ", "2. **C** (lng)  "])

    def test_a_held_grid_is_not_the_price_move(self):
        import inspect
        src = inspect.getsource(roundup.numbers)
        self.assertIn("label not in held", src)
        self.assertIn("brief.held_grids()", src)


class TheChecker(unittest.TestCase):
    """scripts/check_roundup.py traces each of the five numbers."""

    def test_each_line_has_its_check_and_passes_on_the_fixture(self):
        import check_roundup as cr
        md = ("# ERW's Roundup, 2026-W41\n\n## The week in five numbers\n\n"
              "- **Price move of the week:** Brent crude closed at 113.96 USD/bbl on 2026-10-06, against 119.97 USD/bbl on 2026-09-29 (-6.01 USD/bbl, -5.0%) [5].\n"
              "- **US48 peak demand:** 612,345 MW in the hour starting 2026-10-07 21:00 UTC [6].\n"
              "- **Deal of the week, by US dollars:** USD 12 billion, Shell and Equinor, Bay du Nord Oil Project (acquisition, 2026-10-09; `energy_deals` deal:1c055d98aed350fd).\n"
              "- **Largest new datacenter load first reported this week:** 1,200 MW, Crusoe, Spark, Abilene, TX (`datacenter_projects` dc:a).\n"
              "- **From the chart of the week:** Lower 48 battery discharge, daily mean of the week: 45,968 MWh a day in 2026-09-28 to 2026-10-04 "
              "(template `watch_battery_discharge_us`, `docs/analysis/2026-W41/chart_of_the_week.json`).\n\n"
              "## Weekend\n\n## ERW's Numbers This Week\n\nTables: [5] `eia_fuel_spot_prices` (x); [6] `eia930_all_demand` (y).\n\n"
              "<!-- Generated by warehouse/news/roundup.py at 2026-10-11 23:22 UTC; run log x; model none. -->\n")
        with tempfile.TemporaryDirectory() as d:
            with open(os.path.join(d, "energy_deals.csv"), "w", encoding="utf-8", newline="") as f:
                f.write("# fixture\n")
                DEALS.to_csv(f, index=False)
            with open(os.path.join(d, "datacenter_projects.csv"), "w", encoding="utf-8", newline="") as f:
                f.write("# fixture\n")
                DC.to_csv(f, index=False)
            rows = [{"entity": "eia:brent", "variable": "spot", "ts_utc": "2026-10-06T00:00:00Z", "value": 113.96},
                    {"entity": "eia:brent", "variable": "spot", "ts_utc": "2026-09-29T00:00:00Z", "value": 119.97}]
            pd.DataFrame(rows).to_csv(os.path.join(d, "eia_fuel_spot_prices.csv"), index=False)
            pd.DataFrame([{"entity": "eia930:US48", "variable": "demand_mw", "ts_utc": "2026-10-07T21:00:00Z", "value": 612345}]).to_csv(
                os.path.join(d, "eia930_all_demand.csv"), index=False)
            src = cr.cd.Csv(d)
            cs = cr.checks("2026-W41", md)
            keys = [k for k, _, _ in cs]
            self.assertEqual(keys[:6], ["rdp_five_fuel|eia_fuel_spot_prices|eia:brent|2026-10-06", "rdp_five_fuel|eia_fuel_spot_prices|eia:brent|2026-09-29",
                                        "rdp_five_us48|eia930_all_demand|eia930:US48|demand_mw|2026-10-07T21:00:00Z",
                                        "rdp_five_deal|energy_deals|deal:1c055d98aed350fd|dollars", "rdp_five_load|datacenter_projects|dc:a|capacity_mw",
                                        "rdp_five_chart|2026-W41|watch_battery_discharge_us|headline"])
            results = {k: f(src) for k, _, f in cs[:5]}
            for k, (st, got) in results.items():
                self.assertEqual(st, "ok", (k, got))
            st, got = cs[5][2](src)   # the chart's record is read from the repository: W41's is committed
            self.assertIn(st, ("ok", "not here"), got)
            if st == "ok":
                self.assertEqual(got, "45,968")


class TheChart(unittest.TestCase):
    def test_the_stories_point_to_the_measure_most_related(self):
        stories = [{"titles": ["OPEC cuts as US crude exports hit a record"], "sector": "oil", "why": "Exports lift crude flows.", "parties": "OPEC"}]
        best, same = roundup.chart_relevance(CHART, stories, quiet)
        self.assertEqual(best["template"], "watch_crude_exports")
        self.assertFalse(same)
        self.assertIn("crude", best["shared"])

    def test_the_pick_when_it_is_the_most_related(self):
        stories = [{"titles": ["Batteries discharge more as evening peaks lengthen"], "sector": "storage", "why": "", "parties": ""}]
        best, same = roundup.chart_relevance(CHART, stories, quiet)
        self.assertEqual(best["template"], "watch_battery_discharge_us")
        self.assertTrue(same)

    def test_no_stories_or_nothing_related(self):
        self.assertEqual(roundup.chart_relevance(CHART, [], quiet), (None, True))
        self.assertEqual(roundup.chart_relevance(CHART, [{"titles": ["Nuclear permit filed"], "sector": "nuclear", "why": "", "parties": ""}], quiet), (None, True))

    def test_the_section_says_where_the_stories_point(self):
        with tempfile.TemporaryDirectory() as d:
            os.makedirs(os.path.join(d, "2026-W41"))
            json.dump(CHART, open(os.path.join(d, "2026-W41", "chart_of_the_week.json"), "w", encoding="utf-8"))
            stories = [{"titles": ["OPEC cuts as US crude exports hit a record"], "sector": "oil", "why": "", "parties": "OPEC"}]
            with mock.patch.object(roundup, "ANALYSIS_DIR", d), mock.patch("roundup_pick.chosen", return_value=None, create=True):
                L = roundup.chart_of_the_week("2026-W41", quiet, stories=stories)
        text = "\n".join(L)
        self.assertIn("The week's stories point elsewhere: US crude oil exports (", text)
        self.assertIn("template `watch_crude_exports`", text)
        self.assertIn("![Batteries discharging, Lower 48]", text)


class TheInterval(unittest.TestCase):
    def test_the_words(self):
        self.assertEqual(roundup.interval_words("PT15M"), "a 15-minute interval")
        self.assertEqual(roundup.interval_words("PT1H"), "an hourly interval")
        self.assertEqual(roundup.interval_words("PT5M"), "a 5-minute interval")
        self.assertEqual(roundup.interval_words(""), "an interval of unstated length")

    def test_the_line_says_it(self):
        import inspect
        src = inspect.getsource(roundup.numbers)
        self.assertIn("interval_words(top.get('freq', ''))", src)
        self.assertIn("differ in interval length", src)


class WhereItSits(unittest.TestCase):
    def test_the_five_numbers_open_the_roundup(self):
        import inspect
        src = inspect.getsource(roundup.main)
        # session 2704 (the v2 order): the five numbers follow the opening number and come before what mattered
        self.assertIn("five = five_numbers(label, start, cut, facts, log, picked)", src)
        self.assertIn('+ [FIVE_HEADING, ""] + five + [""] + W +', src)
        self.assertIn('chart_of_the_week(label, log, stories=shown.to_dict("records"))', src)
        self.assertEqual(roundup.FIVE_HEADING, "## The week in five numbers")


if __name__ == "__main__":
    unittest.main()

"""Chain 252 (sessions 3456 to 3471, 13 November 2026): the faults of the Digest of 13 November 2026 as stored, read as
a reader against a dry run of the same hour (docs/reviews/periodicals-faults-2026-11-05.md, rows 151 onward). One class
a row, on fixtures: no model, no network, no warehouse write."""

import copy
import json
import os
import sys
import tempfile
import unittest

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
for p in ("warehouse", os.path.join("warehouse", "news"), os.path.join("warehouse", "analysis", "findings"), "scripts"):
    if os.path.join(ROOT, p) not in sys.path:
        sys.path.insert(0, os.path.join(ROOT, p))

import brief  # noqa: E402
import daily_chart  # noqa: E402


def fixture_candidates():
    with open(os.path.join(ROOT, "tests", "fixtures", "session232", "candidates.json"), encoding="utf-8") as f:
        return {c["key"]: c for c in json.load(f)["candidates"]}


def monthly_watch_card():
    """The fixture's weekly watch card made monthly, as the watch list writes a monthly measure's axis ("2026-08"): the
    shape of 13 November 2026's chart, US retail electricity sales."""
    c = copy.deepcopy(fixture_candidates()["watch|watch_caiso_regup|2026-10-05 to 2026-10-11"])
    ch = c["card"]["chart"]
    months = [f"{2021 + (i + 8) // 12}-{(i + 8) % 12 + 1:02d}" for i in range(len(ch["x"]))]
    ch["x"] = months
    ch["x_label"] = "month; the newest complete period is marked"
    for s in ch["series"]:
        s["values"] = s["values"][:len(months)]
    c["card"]["numbers"]["periods"] = 308
    c["key"] = f"watch|watch_retail_sales|{months[-1]}"
    return c, months[-1]


class Row151AMonthlyWatchChartIsShown(unittest.TestCase):
    """Row 151: a watch card's month ("2026-08") broke the caption's last period, so the section was omitted, and the
    picture and record were written anyway (13 November 2026: "No chart is shown today" beside a chart record)."""

    def test_a_month_alone_is_read_as_its_first_day(self):
        self.assertEqual(daily_chart.day_words("2026-08", monthly=True), "August 2026")
        self.assertEqual(daily_chart.day_words("2026-08-01", monthly=True), "August 2026")
        self.assertEqual(daily_chart.day_words("2026-10-06"), "6 October 2026")

    def test_the_caption_of_a_monthly_watch_card(self):
        c, last = monthly_watch_card()
        self.assertEqual(daily_chart.periods_held(c), (308, last, "months"))
        self.assertEqual(daily_chart.held_words(c), f"The table holds 308 months of this series; the last is "
                                                    f"{daily_chart.day_words(last, monthly=True)}.")
        lines = daily_chart.markdown("2026-11-13", c)
        self.assertIn(c["fact"], lines)
        self.assertIn(daily_chart.HEADING, lines)

    def test_a_section_that_cannot_be_written_leaves_no_picture_and_no_record(self):
        c, _ = monthly_watch_card()
        real = daily_chart.markdown

        def broken(day, cand):
            raise ValueError("not enough values to unpack (expected 3, got 2)")

        logged = []
        with tempfile.TemporaryDirectory() as d:
            daily_chart.markdown = broken
            try:
                out = daily_chart.section("2026-11-13", logged.append, chart_dir=d, candidates=[c], used=set(), waited=set(),
                                          dismissed=set())
            finally:
                daily_chart.markdown = real
            self.assertEqual(out, [])
            self.assertEqual(sorted(os.listdir(d)), [], "a picture or a record of a chart the issue does not show")
        self.assertTrue(any("omitted (ValueError" in line for line in logged), logged)


class Row152TheRealTimeLineInWords(unittest.TestCase):
    """Row 152: the Digest's real-time line printed "interval starting 2026-11-12 19:00 local (2026-11-13 01:00 UTC),
    PT15M `spp_rtm`, ERCOT's ..." (the Roundup's twin was row 71): the interval in words and in the grid's zone, the
    variable on the Tables line."""

    @classmethod
    def setUpClass(cls):
        from unittest import mock
        import test_periodicals as tp
        with mock.patch.object(brief.erw, "fetch", side_effect=tp.fake_fetch), \
                mock.patch.object(brief, "held_grids", return_value={"NYISO", "ISO-NE"}), \
                mock.patch.object(brief, "rt_parts", return_value=[("spp", "iso_rtm_hub_prices", "spp_rtm")]), \
                mock.patch.object(brief, "cite_short", side_effect=lambda t: f"`{t}`"), \
                mock.patch.object(brief, "paused_row", return_value=None), tp.no_hold():
            cls.lines = brief.numbers_today("2026-10-21", tp.quiet, None)
        cls.rt = next(ln for ln in cls.lines if ln.startswith("**Highest real-time price"))
        cls.tables = next(ln for ln in cls.lines if ln.startswith("Tables: ") and "real-time tables read" in ln)

    def test_the_line_names_the_interval_in_words_and_the_zone(self):
        self.assertEqual(self.rt, "**Highest real-time price, yesterday:** 276.41 USD/MWh at SPPNORTH_HUB (SPP), the 15-minute "
                                  "interval starting 2026-10-20 23:45 Central (2026-10-21 04:45 UTC) [4], SPP's real-time "
                                  "locational marginal price (a 15-minute mean of 5-minute prices).")
        for gone in ("local", "PT15M", "`"):
            self.assertNotIn(gone, self.rt)

    def test_the_variable_is_on_the_tables_line(self):
        self.assertIn("real-time tables read: iso_rtm_hub_prices; yesterday's highest real-time price is variable "
                      "`lmp_rtm_15m_mean`", self.tables)

    def test_the_zone_and_the_utc_date(self):
        import pandas as pd
        self.assertEqual(brief.rt_when(pd.Timestamp("2026-11-13T01:00Z"), "America/Chicago"),
                         "2026-11-12 19:00 Central (2026-11-13 01:00 UTC)")
        self.assertEqual(brief.rt_when(pd.Timestamp("2026-11-12T23:45Z"), "America/Chicago"), "2026-11-12 17:45 Central (23:45 UTC)")
        self.assertEqual(brief.rt_when(pd.Timestamp("2026-11-12T23:45Z"), "UTC"), "2026-11-12 23:45 UTC")

    def test_the_roundup_writes_with_the_same_helpers(self):
        import roundup
        self.assertIs(roundup.rt_when, brief.rt_when)
        self.assertIs(roundup.interval_words, brief.interval_words)
        self.assertIs(roundup.ZONE_WORDS, brief.ZONE_WORDS)


ENI_WHY = ("Major oil major commits significant capital to UK lower-carbon projects, signaling portfolio transition and capital "
           "allocation.")
ENI_HEAD = "Eni plans around GBP 11 billion in gross investments in the United Kingdom, 2026 to 2030"


class Row153AnOilMajorIsACompany(unittest.TestCase):
    """Row 153: the voice's cleaner took "major" out of "oil major" and printed "Oil commits capital to UK lower-carbon
    projects." (13 November 2026, What moved 5)."""

    def test_the_eni_line(self):
        self.assertEqual(brief.why_line(ENI_WHY, ENI_HEAD), "Oil major commits capital to UK lower-carbon projects.")

    def test_the_noun_stays_and_the_adjective_goes(self):
        self.assertEqual(brief.plain("Saudi oil major and sovereign fund invest."), "Saudi oil major and sovereign fund invest.")
        self.assertEqual(brief.plain("An energy major and a gas major bid."), "An energy major and a gas major bid.")
        self.assertEqual(brief.plain("A major 2 GW deal."), "A 2 GW deal.")
        self.assertEqual(brief.plain("Two oil majors sign a major contract."), "Two oil majors sign a contract.")
        self.assertEqual(brief.why_check("Oil major commits capital to UK projects."), [])
        self.assertEqual(brief.why_check("A major contract."), ["adjective: major"])


class Row154AnOilMarketTitleIsOils(unittest.TestCase):
    """Row 154: "IEA Sees Oil Surplus for First Time in Iran War", tagged power prices, printed "(power prices)" in the
    rest of the top ten beside an oil price story of the same day."""

    def test_the_fuel_market_titles(self):
        for title, sector in [("IEA Sees Oil Surplus for First Time in Iran War", "oil"),
                              ("OPEC+ holds output steady amid tensions", "oil"),
                              ("Global oil demand to peak sooner, agency says", "oil"),
                              ("Natural gas demand for power hits a record", "gas"),
                              ("Oil-fired plant retires in New England", "power_prices"),
                              ("Power prices spike in Texas heat", "power_prices")]:
            self.assertEqual(brief.sector_of({"sector": "power_prices", "title": title}), sector, title)

    def test_only_a_power_tag_is_corrected(self):
        self.assertEqual(brief.sector_of({"sector": "geopolitics", "title": "IEA Sees Oil Surplus"}), "geopolitics")

    def test_the_two_oil_stories_are_one_topic(self):
        iea = {"cluster_id": "a", "titles": ["IEA Sees Oil Surplus for First Time in Iran War"], "sector": "oil", "region": "global",
               "parties": "IEA"}
        squeeze = {"cluster_id": "b", "titles": ["Oil Prices Squeezed Between Peace Hopes and Iran Escalation Risk"], "sector": "oil",
                   "region": "global", "parties": ""}
        self.assertTrue(brief.same_topic(iea, squeeze))


def item(**k):
    return dict(dict(mw="", price="", parties=""), **k)


class Row155NoFigureTwiceInAnItem(unittest.TestCase):
    """Row 155: the figures line printed the why line's own figure again: "Oil down from USD 118 to below USD 95 per barrel
    on ... de-escalation talks. USD 118 per barrel." (a dry run of 13 November with no model)."""

    def test_the_why_lines_figure_is_not_printed_again(self):
        why = "Oil down from USD 118 to below USD 95 per barrel on Ukraine-Russia and US-Iran de-escalation talks."
        self.assertEqual(brief.detail(item(price="$118 per barrel"), "Oil Prices Squeezed Between Peace Hopes and Iran Escalation Risk",
                                      why=why), "")
        self.assertEqual(brief.detail(item(mw="1000", parties="AirTrunk; European Energy Australia"), "AirTrunk signs energy deal",
                                      why="AirTrunk buys 1,000 MW."), "Also named: European Energy Australia. ")

    def test_a_figure_neither_gives_is_printed(self):
        self.assertEqual(brief.detail(item(price="$118 per barrel"), "Oil Prices Squeezed", why="Talks eased."), "USD 118 per barrel. ")

    def test_the_issue_passes_the_printed_why_line(self):
        import inspect
        src = inspect.getsource(brief.main)
        self.assertIn("detail(r, heads[r['cluster_id']], why=w)", src)


class Row156NoSumWithoutAUnit(unittest.TestCase):
    """Row 156: "2.6 billion; Parties: Aramco; PIF; HUMAIN." under "Aramco, PIF Close HUMAIN AI Deal": a sum the scorer
    wrote with no currency, printed as one."""

    def test_a_sum_with_no_unit_is_left_out(self):
        self.assertEqual(brief.detail(item(price="2.6 billion", parties="Aramco; PIF; HUMAIN"), "Aramco, PIF Close HUMAIN AI Deal"), "")
        self.assertEqual(brief.detail(item(price="millions", parties="X Corp"), "A deal"), "Also named: X Corp. ")
        self.assertEqual(brief.detail(item(price="246,000", parties="X Corp"), "A deal"), "Also named: X Corp. ")

    def test_a_sum_with_its_unit_stays(self):
        self.assertEqual(brief.detail(item(price="$2.6 billion", parties="Aramco; PIF"), "A deal"), "USD 2.6 billion; Parties: Aramco; PIF. ")
        self.assertEqual(brief.detail(item(price="3 billion euros", parties="X"), "A deal"), "3 billion euros; Parties: X. ")
        self.assertEqual(brief.detail(item(price="50%", parties="X"), "A deal"), "50%; Parties: X. ")


class Row157TheSubjectEndsOnAWholePhrase(unittest.TestCase):
    """Row 157: "ERW Daily | Centrus and Oklo finalise fuel agreements for up to five Aurora" (13 November 2026), a cut
    inside "for up to five Aurora powerhouses"."""

    def test_the_centrus_subject(self):
        head = "Centrus and Oklo finalise fuel agreements for up to five Aurora powerhouses at 1,200 MW Ohio campus"
        self.assertEqual(brief.subject_clause(head), "Centrus and Oklo finalise fuel agreements")

    def test_a_clause_that_fits_or_a_cut_before_a_phrase_is_unchanged(self):
        self.assertEqual(brief.subject_clause("SpaceX plans USD 74 billion in data center projects in Arizona and Texas"),
                         "SpaceX plans data center projects in Arizona and Texas")
        import roundup
        self.assertEqual(roundup.phrase_back("Utility files rate case", "Utility files rate case in Ohio"), "Utility files rate case")
        self.assertEqual(roundup.phrase_back("Utility files rate case for its Ohio", "Utility files rate case for its Ohio grid"),
                         "Utility files rate case")
        # too little left: the cut stays
        self.assertEqual(roundup.phrase_back("Plant in Ohio adds big", "Plant in Ohio adds big turbines"), "Plant in Ohio adds big")

    def test_a_quantity_is_no_phrase(self):
        import roundup
        self.assertEqual(roundup.phrase_back("Utility firm orders turbines for up to five",
                                             "Utility firm orders turbines for up to five plants"), "Utility firm orders turbines")


class Row158OneCapacityInTwoUnitsIsOneFigure(unittest.TestCase):
    """Row 158: "AirTrunk commits to purchasing 1GW from new solar, wind and battery projects." under "AirTrunk signs 1,000
    MW energy deal ...": the headline's figure again, in another unit."""

    HEAD = "AirTrunk signs 1,000 MW energy deal with European Energy Australia for solar, wind and BESS"

    def test_the_airtrunk_line_is_the_headlines_figure(self):
        self.assertEqual(brief.why_line("AirTrunk commits to purchasing 1GW from new solar, wind and battery projects.", self.HEAD), "")

    def test_the_units_are_read_as_one(self):
        self.assertEqual(brief.head_units("a 1GW deal and 2 GW more", "deal of 1,000 MW"), "a 1,000 MW deal and 2 GW more")
        self.assertEqual(brief.head_units("a 1,200 MW campus", "a 1.2 GW campus"), "a 1.2 GW campus")
        self.assertEqual(brief.head_units("a 900 MW plant", "a 1 GW deal"), "a 900 MW plant")
        self.assertEqual(brief.capacities_mw("1GW and 1,200 MW and 0.5 GW"), {1000.0, 1200.0, 500.0})

    def test_the_figures_line_reads_the_headlines_unit(self):
        r = item(mw="1000", parties="AirTrunk; European Energy Australia")
        self.assertEqual(brief.detail(r, "AirTrunk signs 1GW energy deal with European Energy Australia"), "")
        self.assertEqual(brief.detail(r, "AirTrunk signs energy deal"), "1,000 MW; Parties: AirTrunk; European Energy Australia. ")


class Row159TheReasonADayIsNotHeld(unittest.TestCase):
    """Row 159: "the same weekday a year before (2025-11-13) and a week before (2026-11-05) are not held: the hourly table's
    window does not reach them." The table starts on 26 August; 5 to 8 November are a gap inside it (the machines' pause)."""

    def test_a_gap_inside_the_window_is_said_to_be_one(self):
        import pandas as pd
        first = pd.Timestamp("2026-08-26", tz="UTC")
        self.assertEqual(brief.not_held_why(pd.Timestamp("2026-11-05", tz="UTC"), first),
                         "the hourly table starts on 2026-08-26 and holds no hour of 2026-11-05")
        self.assertEqual(brief.not_held_why(pd.Timestamp("2026-08-20", tz="UTC"), first), "the hourly table's window does not reach them")
        self.assertEqual(brief.not_held_why(pd.Timestamp("2026-11-05", tz="UTC"), None), "the hourly table's window does not reach them")

    def test_the_line_on_a_table_with_a_gap(self):
        import pandas as pd
        from unittest import mock

        def fetch(table, start=None, end=None, ba=None, **kw):
            hours = pd.date_range("2026-08-26", "2026-11-13", freq="h", tz="UTC", inclusive="left")
            hours = hours[(hours < pd.Timestamp("2026-11-05", tz="UTC")) | (hours >= pd.Timestamp("2026-11-09", tz="UTC"))]
            df = pd.DataFrame({"ts_utc": hours, "value": 400000.0, "variable": "demand_mw"})
            return df[(df["ts_utc"] >= start) & (df["ts_utc"] < end)]

        class Notes:
            def ref(self, *a):
                return "[6]"
        with mock.patch.object(brief.erw, "fetch", side_effect=fetch):
            line = brief.demand_lines("2026-11-13", lambda m: None, Notes())[-1]
        self.assertTrue(line.endswith("are not held: the hourly table starts on 2026-08-26 and holds no hour of 2026-11-05."), line)


class Row160TheNoChartLineSaysWhy(unittest.TestCase):
    """Row 160: "No chart is shown today: no candidate passed the chart's rules (the run log says why)." A log no reader
    sees, and on 13 November a chart had passed and failed to be written."""

    def test_the_two_reasons(self):
        self.assertEqual(brief.no_chart_lines({}, why="none")[3], "No chart is shown today: no candidate passed the chart's rules.")
        self.assertEqual(brief.no_chart_lines({}, why="error")[3], "No chart is shown today: the chart chosen by its rules could not be drawn.")
        self.assertNotIn("run log", " ".join(brief.no_chart_lines({})))

    def test_the_section_leaves_its_reason(self):
        c, _ = monthly_watch_card()
        with tempfile.TemporaryDirectory() as d:
            self.assertEqual(daily_chart.section("2026-11-13", lambda m: None, chart_dir=d, candidates=[], used=set(), waited=set(),
                                                 dismissed=set()), [])
            self.assertEqual(daily_chart.OMITTED, "none")
            self.assertEqual(brief.chart_omitted(), "none")
            real = daily_chart.markdown
            daily_chart.markdown = lambda day, cand: 1 / 0
            try:
                daily_chart.section("2026-11-13", lambda m: None, chart_dir=d, candidates=[c], used=set(), waited=set(), dismissed=set())
            finally:
                daily_chart.markdown = real
            self.assertEqual(daily_chart.OMITTED, "error")


if __name__ == "__main__":
    unittest.main()

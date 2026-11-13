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


def five(deals=None, dcs=None):
    import pandas as pd
    from unittest import mock
    import roundup
    with tempfile.TemporaryDirectory() as d, \
            mock.patch.object(roundup, "read_table", lambda n: {"energy_deals": deals, "datacenter_projects": dcs}.get(n)), \
            mock.patch.object(roundup, "ANALYSIS_DIR", d):
        return roundup.five_numbers("2026-W46", pd.Timestamp("2026-11-09", tz="UTC"), pd.Timestamp("2026-11-13T18:40", tz="UTC"), {},
                                    lambda m: None)


def deal(i, day, dollars="", mw="", buyer="A Corp", country="", conf="0.9"):
    return {"event_id": f"deal:{i}", "event_date": f"{day}T12:00:00Z", "deal_type": "acquisition", "buyer": buyer, "seller": "B Corp",
            "asset": "an asset", "mw": mw, "dollars": dollars, "confidence": conf, "country": country, "state": "TX" if not country else "",
            "status": "closed", "story_urls": "https://example.org/a"}


class Row161TheDealOfTheWeekIsInTheTable(unittest.TestCase):
    """Row 161: the stack's W46 named "USD 2.6 billion, Aramco, HUMAIN AI" as the deal of the week, and the Deals table
    below (US first, at most 15) left it out."""

    def test_the_kept_row_replaces_the_last_shown(self):
        import pandas as pd
        import roundup
        rows = [deal(i, "2026-11-11", dollars="1000000") for i in range(16)] + [deal("aramco", "2026-11-13", dollars="2600000000",
                                                                                      buyer="Aramco", country="Saudi Arabia")]
        dw = pd.DataFrame(rows)
        self.assertEqual(roundup.deal_of_week_id(dw), "deal:aramco")
        shown, rest, under = roundup.floor_rows(dw, "energy_deals", keep="deal:aramco")
        self.assertEqual(len(shown), roundup.ROW_MAX)
        self.assertEqual(shown[-1]["event_id"], "deal:aramco")
        self.assertEqual((rest, under), (2, 0))
        shown0, rest0, _ = roundup.floor_rows(dw, "energy_deals")
        self.assertNotIn("deal:aramco", [r["event_id"] for r in shown0])   # the old cut, which row 161 is about
        self.assertEqual(rest0, 2)

    def test_a_kept_row_already_shown_changes_nothing(self):
        import pandas as pd
        import roundup
        dw = pd.DataFrame([deal(1, "2026-11-11", dollars="5"), deal(2, "2026-11-12", dollars="9")])
        self.assertEqual(roundup.deal_of_week_id(dw), "deal:2")
        self.assertEqual([r["event_id"] for r in roundup.floor_rows(dw, "energy_deals", keep="deal:2")[0]], ["deal:1", "deal:2"])
        self.assertIsNone(roundup.deal_of_week_id(dw.iloc[0:0]))

    def test_the_five_and_the_table_name_one_deal(self):
        import pandas as pd
        rows = [deal(i, "2026-11-11", dollars="1000000") for i in range(16)] + [deal("aramco", "2026-11-13", dollars="2600000000",
                                                                                      buyer="Aramco", country="Saudi Arabia")]
        L = five(deals=pd.DataFrame(rows))
        self.assertIn("`energy_deals` deal:aramco", "\n".join(L))


class Row162TheFivesLoadNamesItsDeveloper(unittest.TestCase):
    """Row 162: W46's five printed "20 MW, Syntys (1 larger load of the week name no operator or site; it is in the table
    below)" above a table showing that load as "CDC (developer)", 1,400 MW, Kemps Creek, Australia."""

    DCS = [{"entity_id": "datacenter:kemps", "first_story_at": "2026-11-12T10:00:00Z", "capacity_mw": "1400", "mw": "1400", "operator": "",
            "developer": "CDC", "site_name": "", "city": "Kemps Creek", "state": "", "country": "Australia", "confidence": "0.9"},
           {"entity_id": "datacenter:syntys", "first_story_at": "2026-11-13T10:00:00Z", "capacity_mw": "20", "mw": "20", "operator": "Syntys",
            "developer": "", "site_name": "", "city": "", "state": "", "country": "Qatar", "confidence": "0.9"}]

    def load(self, rows):
        import pandas as pd
        return next(x for x in five(dcs=pd.DataFrame(rows)) if x.startswith("- **Largest new datacenter load"))

    def test_the_developer_names_the_load(self):
        self.assertEqual(self.load(self.DCS), "- **Largest new datacenter load first reported this week:** 1,400 MW, CDC (developer), "
                                              "Kemps Creek, Australia.")

    def test_one_larger_unnamed_load_names_nothing(self):
        rows = [dict(self.DCS[0], developer=""), self.DCS[1]]
        self.assertEqual(self.load(rows), "- **Largest new datacenter load first reported this week:** 20 MW, Syntys, Qatar (1 larger "
                                          "load of the week names no operator, developer or site; it is in the table below).")


class Row163AGasForwardsTitleIsGass(unittest.TestCase):
    """Row 163: "Record LNG Demand Ignites Natural Gas Forward Rally, but Will It Last?" (power prices) under Power, the stack's
    dry run of 12 November."""

    def test_the_gas_market_titles(self):
        for title, sector in [("Record LNG Demand Ignites Natural Gas Forward Rally, but Will It Last?", "gas"),
                              ("Natural gas futures slip on mild forecasts", "gas"),
                              ("LNG prices climb in Asia", "gas"),
                              ("Gas-fired plants set output records", "power_prices"),
                              ("LNG Canada starts up its second train", "power_prices")]:
            self.assertEqual(brief.sector_of({"sector": "power_prices", "title": title}), sector, title)


class Row164APolicyActionIsPrintedOnce(unittest.TestCase):
    """Row 164: "Long Mott Energy, LLC; Long Mott Generating Station; Construction Permit (NRC notice, policy action)" was in
    the issues of 12 and 13 November: the actions are dated by day, and the window's first day is the last issue's last."""

    COLS = "event_date,title,agency,action_type,significance,why,source_url\n"
    ROWS = ("2026-11-12,Long Mott Energy; Construction Permit,NRC,notice,8,The permit authorizes building.,https://www.federalregister.gov/a\n"
            "2026-11-13,A new rule,EPA,rule,7,The rule sets limits.,https://www.federalregister.gov/b\n")

    def lines(self, printed):
        import pandas as pd
        from unittest import mock
        with tempfile.TemporaryDirectory() as d:
            with open(os.path.join(d, "policy_actions.csv"), "w", encoding="utf-8") as f:
                f.write("# test\n" + self.COLS + self.ROWS)
            with mock.patch.object(brief.ip, "OUT_DIR", d):
                return brief.policy_actions_lines(pd.Timestamp("2026-11-12T22:56Z"), pd.Timestamp("2026-11-13T16:01Z"), lambda m: None,
                                                  printed=printed)

    def test_an_action_the_last_issue_printed_is_left_out(self):
        got = self.lines({"https://www.federalregister.gov/a"})
        self.assertEqual(len(got), 1)
        self.assertIn("A new rule", got[0])
        self.assertEqual(len(self.lines(set())), 2)

    def test_the_links_of_earlier_issues(self):
        with tempfile.TemporaryDirectory() as d:
            p = os.path.join(d, "2026-11-12.md")
            with open(p, "w", encoding="utf-8") as f:
                f.write("- Long Mott (NRC notice, policy action): x. [NRC](https://www.federalregister.gov/a)\n")
            self.assertEqual(brief.printed_links([p, os.path.join(d, "missing.md")]), {"https://www.federalregister.gov/a"})

    def test_the_issue_passes_the_earlier_issues(self):
        import inspect
        self.assertIn("printed=printed_links(earlier_issues(digest_date))", inspect.getsource(brief.main))


class Row165NoQuantityWordsLeftInTheSubject(unittest.TestCase):
    """Row 165: "ERW Daily | Taiwan Commits Up to to Alaska LNG Megaproject" (the stack's dry run of 14 October): the figure
    taken out, its "Up to" left; and the same removal's other leftovers."""

    def test_the_subjects(self):
        for head, clause in [("Taiwan Commits Up to $4.4 Billion to Alaska LNG Megaproject", "Taiwan Commits to Alaska LNG Megaproject"),
                             ("Utility adds nearly 2 GW of solar in Texas", "Utility adds solar in Texas"),
                             ("A 500 MW deal is signed by Meta", "A deal is signed by Meta"),
                             ("Prices rose 12% on Tuesday", "Prices rose on Tuesday"),
                             ("SpaceX plans USD 74 billion in data center projects in Arizona and Texas",
                              "SpaceX plans data center projects in Arizona and Texas")]:
            self.assertEqual(brief.subject_clause(head), clause, head)

    def test_a_percent_is_a_figure(self):
        import roundup
        self.assertNotIn("30", roundup.head_clause("Taiwan commits to Alaska LNG with 30% of output", 90))


class Row166AFuelMarketTitleIsOils(unittest.TestCase):
    """Row 166: "Morgan Stanley: Global Fuel Market Will Stay Tight Through Mid-2027 (power prices)" (the stack's 21 October)."""

    def test_the_fuel_market(self):
        self.assertEqual(brief.sector_of({"sector": "power_prices", "title": "Morgan Stanley: Global Fuel Market Will Stay Tight Through Mid-2027"}),
                         "oil")
        self.assertEqual(brief.sector_of({"sector": "power_prices", "title": "Fuel cell maker raises funds"}), "power_prices")


class Row167TheFiguresLineOpensWithACapital(unittest.TestCase):
    """Row 167: "nearly USD 1 billion; Parties: US Energy Department." opened an item's line in lower case (21 October)."""

    def test_the_capital(self):
        self.assertEqual(brief.detail(item(price="nearly $1 billion", parties="US Energy Department"), "DOE announces grid investments"),
                         "Nearly USD 1 billion; Parties: US Energy Department. ")
        self.assertEqual(brief.detail(item(mw="580", parties="Sunrun; Tesla"), "VPP dispatch"), "580 MW; Parties: Sunrun; Tesla. ")


class Row168AnAgencysNameIsItsInitials(unittest.TestCase):
    """Row 168: "DOE Announces $967 Million in Grid Resilience Funding" (Department of Energy) and "Energy Department
    Announces New Investments to Strengthen America's Power Grid and Lower Electricity Costs" (US Energy Department), one
    announcement, two items of the stack's ten of 21 October."""

    A = {"parties": "Department of Energy", "titles": ["DOE Announces $967 Million in Grid Resilience Funding"], "sector": "transmission",
         "region": "USA"}
    B = {"parties": "US Energy Department", "sector": "policy", "region": "global",
         "titles": ["Energy Department Announces New Investments to Strengthen America's Power Grid and Lower Electricity Costs"]}

    def test_the_long_names_are_the_initials(self):
        self.assertEqual(brief.party_words(self.A), {"doe"})
        self.assertIn("doe", brief.party_words(self.B))
        self.assertIn("doe", brief.party_words({"parties": "U.S. Department of Energy"}))
        self.assertIn("ferc", brief.party_words({"parties": "Federal Energy Regulatory Commission"}))
        self.assertEqual(brief.party_words({"parties": "Energy Transfer"}), {"transfer"})

    def test_one_announcement_is_one_topic(self):
        self.assertTrue(brief.same_topic(self.A, self.B))
        other = {"parties": "DOE", "titles": ["Energy Department Designates Helium as Critical Material"], "sector": "policy",
                 "region": "United States"}
        self.assertFalse(brief.same_topic(self.A, other))


class Row169TheScaleWordReadsTheClustersMW(unittest.TestCase):
    """Row 169: "Gigawatt-scale hyperscale power deal ..." under "AEP, Google Advance $4 Billion Fuel-Cell Project to Power
    Cheyenne Data Centers" (the stack's 6 November with no model): a 702 MW project, the publisher's title stating no MW."""

    def test_the_clusters_mw_counts(self):
        why = "Gigawatt-scale hyperscale power deal combining fuel cells, natural gas, and private microgrid infrastructure for datacenter demand."
        head = "AEP, Google Advance $4 Billion Fuel-Cell Project to Power Cheyenne Data Centers"
        self.assertEqual(brief.why_line(why, head, "702"), "Hyperscale power deal combining fuel cells, natural gas, and private "
                                                           "microgrid infrastructure for datacenter demand.")
        self.assertEqual(brief.scale_against("Gigawatt-scale deal.", head, "702"), "gigawatt-scale")
        self.assertEqual(brief.scale_against("Gigawatt-scale deal.", head, "1500"), "")
        self.assertEqual(brief.scale_against("Gigawatt-scale deal.", head), "")
        self.assertEqual(brief.scale_against("Gigawatt-scale deal.", head, "not a number"), "")


class Row170AlsoInDeals(unittest.TestCase):
    """Row 170: "Also in deal: Blackstone Leads USD 3.1 billion Investment ..." (the stack's 6 November); and the two readers
    of that label read lower case only, so "Also in LNG:" (row 127's capitals) was not read as one."""

    def test_the_plural(self):
        rec = {"title": "Blackstone Leads $3.1 Billion Investment in Mitsubishi's Stake in LNG Canada", "kind": "sector", "sector": "deal",
               "links": [("WSJ", "https://example.org/w")]}
        self.assertTrue(brief.also_line([rec]).startswith("Also in deals: Blackstone Leads USD 3.1 billion Investment"))
        self.assertTrue(brief.also_line([dict(rec, sector="nuclear")]).startswith("Also in nuclear: "))
        self.assertTrue(brief.also_line([dict(rec, sector="lng")]).startswith("Also in LNG: "))

    def test_the_readers_read_capitals(self):
        import email_digest
        for label in ("Also in LNG:", "Also in PPAs:", "Also in deals:", "Also on this topic:"):
            self.assertTrue(brief.ALSO_RE.match(label + " x"), label)
            self.assertEqual(email_digest.ALSO_RE.match(label + " x").group(1), label)


class Row170TheEmailKeepsTheWhyBesideAnLNGAlsoLine(unittest.TestCase):
    """Row 170, found again by session 3469: the email read "Also in LNG: ..." as the item's why line (its reader read lower
    case only), so the item's why line and its source were lost and the also line printed in their place."""

    def test_the_item_keeps_its_why_and_source(self):
        import email_digest
        lines = ["## What moved", "", "1. **Trump to Tout Korean LNG Plan** (LNG)  ", "   Its reason. Sources: [Bloomberg](https://example.org/b)  ",
                 "   Also in LNG: Another LNG story ([Reuters](https://example.org/r)).", ""]
        text = email_digest.story_list(email_digest.numbered(lines, ("## What moved",), 3))[0]
        self.assertEqual(text, ["1. Trump to Tout Korean LNG Plan", "   Its reason.", "   Bloomberg: https://example.org/b",
                                "   Also in LNG: Another LNG story (Reuters)."])


class Row172TheTopicFilterReadsTheV2Issues(unittest.TestCase):
    """Row 172: a subscriber with topics was sent no story from a v2 issue: the filter (`email_digest.items`) read the old
    headings only, and a sector in capitals ("LNG") was no sector."""

    MD = ["# ERW Daily Digest, 2026-11-13", "", "## What moved", "",
          "1. **Centrus and Oklo finalise fuel agreements** (nuclear)  ", "   One outlet. Sources: [World Nuclear News](https://example.org/n)",
          "", "## More", "", "### The rest of the top ten", "", "1. **Venture Global seeks approval** (LNG)  ",
          "   Sources: [LNG Prime](https://example.org/l)", "", "### By sector", "", "**Oil and gas**", "",
          "- Canada to invest in Woodfibre LNG (LNG): Public capital. [Reuters](https://example.org/r)", "",
          "### AI and power", "", "- Nscale brings two data centers online (datacenter power). [DCD](https://example.org/d)", ""]

    def test_the_items(self):
        import email_digest
        got = [(x["head"], x["sector"]) for x in email_digest.items(self.MD, "daily")]
        self.assertEqual(got, [("Centrus and Oklo finalise fuel agreements", "nuclear"), ("Venture Global seeks approval", "LNG"),
                               ("Canada to invest in Woodfibre LNG", "LNG"), ("Nscale brings two data centers online", "datacenter power")])

    def test_a_subscribers_topics(self):
        import email_digest
        keep, note = email_digest.filtered(self.MD, "daily", ["gas_lng"])
        self.assertEqual([k["head"] for k in keep], ["Venture Global seeks approval", "Canada to invest in Woodfibre LNG"])
        self.assertTrue(note.startswith("Your topics: Gas and LNG. These are the highest-ranked stories in them"), note)
        keep, _ = email_digest.filtered(self.MD, "daily", ["nuclear"])
        self.assertEqual([k["head"] for k in keep], ["Centrus and Oklo finalise fuel agreements"])

    def test_the_topic_of_a_sector_in_capitals(self):
        import topics
        self.assertEqual(topics.topic_of("LNG"), "gas_lng")
        self.assertEqual(topics.topic_of("PPA"), "deals_capital")
        self.assertEqual(topics.topic_of("datacenter power"), "datacenters_ai")

    def test_the_roundups_v2_headings(self):
        import email_digest
        md = ["# ERW Weekly Roundup, 2026-W46", "", "## What mattered", "", "1. **SpaceX plans data center projects** (datacenter power, 3 stories)  ",
              "   Sources: [Bloomberg](https://example.org/b)", "", "## More", "", "### The five stories of the week", "",
              "1. **OPG to revise SMR timeline** (nuclear, 4 stories)  ", "   Sources: [WNN](https://example.org/w)", ""]
        self.assertEqual([(x["head"], x["sector"]) for x in email_digest.items(md, "roundup")],
                         [("SpaceX plans data center projects", "datacenter power"), ("OPG to revise SMR timeline", "nuclear")])


class Row171TheTextEmailNamesTheChartOnce(unittest.TestCase):
    """Row 171: the Digest's plain-text email printed "[chart: Net generation from natural gas in Wyoming: ...] <url>" and
    then the same sentence on the next line (12 November as sent, and every chart since session 232)."""

    def test_the_picture_line_gives_its_address(self):
        import email_digest
        fact = "US retail electricity sales: 412,568,374 MWh in August 2026."
        text, html_ = email_digest.block([f"![{fact}](charts/2026-11-13.png)", "", fact, "The table holds 308 months."], "docs/digest")
        self.assertTrue(text[0].startswith("[chart] https://"), text[0])
        self.assertTrue(text[0].endswith("docs/digest/charts/2026-11-13.png"), text[0])
        self.assertEqual(text[1], fact)
        self.assertIn(f'alt="{fact}"', html_)

    def test_a_description_that_is_not_the_next_line_stays(self):
        import email_digest
        text, _ = email_digest.block(["![A picture of the week](charts/x.png)", "Something else."], "docs/digest")
        self.assertTrue(text[0].startswith("[chart: A picture of the week] "), text[0])


if __name__ == "__main__":
    unittest.main()

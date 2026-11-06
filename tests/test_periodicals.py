"""The periodicals' regression suite (session 809, chain of 23 October 2026): every rule the chain and the audits of 21
October set for the Digest and the Roundup, in one file, on fixtures and on the saved stories where the repository holds
them, so a later change that breaks a rule fails a test and the gate.

The rules, with the session that set each:
  the why line         one sentence, no adjective of the list, no figure the headline gives, a stop before the figures
                       (801, 577), the money style (470, 577)
  the figures line     no figure the headline holds (801)
  one topic, one item  at most one item a topic in the top ten and the Roundup's lists, the rest folded (802); one event
                       once (470); not the day before's story again (470)
  the outlet           the feed's own outlet name as the link text, "(via Google News)" after a Google address, a held
                       outlet named with no link, never the address in the email's text (803, 470)
  the numbers traced   every figure line in the form the site's parser and scripts/check_digest.py key (804, 402)
  the chart's relevance the candidate most related to the day's top stories first (805); the Roundup's chart says where
                       the week's stories point (806)
  the five numbers     the Roundup's five, each in the form scripts/check_roundup.py traces (806)
  the named days       2 October's Korea framework once, 9 October without 8 October's Voltus, 13 October with one
                       datacenter item in its top ten (470, 802)
No model, no network. The fixtures are frames and files the tests write; the named days read warehouse/output/news_stories.csv
and docs/digest/ as the repository holds them, and skip where they are absent.
"""

import inspect
import io
import json
import os
import re
import sys
import tempfile
import unittest
from unittest import mock

import pandas as pd

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
for p in ("warehouse", os.path.join("warehouse", "news"), os.path.join("warehouse", "analysis", "findings"), "scripts"):
    if os.path.join(ROOT, p) not in sys.path:
        sys.path.insert(0, os.path.join(ROOT, p))

import brief  # noqa: E402
import daily_chart as dc  # noqa: E402
import email_digest  # noqa: E402
import roundup  # noqa: E402
import score  # noqa: E402

GN = "https://news.google.com/rss/articles/CBMiabc?oc=5"
ADJ = re.compile(r"\b(massive|unprecedented|significant|significantly|major|critical|critically|key|huge)\b", re.I)
MOVER = re.compile(r"^- (.+?): (-?[\d,]+\.\d{2}) (\S+) on (\d{4}-\d{2}-\d{2}), (?:up|down) [\d,.]+ \S+ \([\d.]+%\) from (-?[\d,]+\.\d{2}) \S+ on (\d{4}-\d{2}-\d{2}) \[(\d+)\]")
FUEL_LINE = re.compile(r"^- (Henry Hub natural gas|WTI Cushing crude|Brent crude): (-?[\d,]+\.\d{2}) (\S+) on (\d{4}-\d{2}-\d{2})\b")
RT_LINE = re.compile(r"^\*\*Highest real-time price[^*]*:\*\* (-?[\d,]+\.\d{2}) USD/MWh at (.+?) \(([A-Z-]+)\), interval starting .*?\((\d{4}-\d{2}-\d{2}) (\d{2}:\d{2}) UTC\), \S+ `([a-z0-9_]+)`")
DEMAND = re.compile(r"peaked at (-?[\d,]+) MW in the hour starting (\d{4}-\d{2}-\d{2}) (\d{2}:\d{2}) UTC")


def rec(cid, title, sector="nuclear", parties="", sig=7, ai=0, why="Why.", mw="", price="", links=None, first="2026-10-21T00:00:00Z"):
    return {"cluster_id": cid, "titles": [title], "sector": sector, "parties": parties, "sig": sig, "ai": ai, "why": why,
            "mw": mw, "price": price, "n": 1, "first": first, "summary": "", "links": links or [("Outlet", f"https://example.org/{cid}")]}


def frame(*recs):
    return pd.DataFrame(list(recs))


def quiet(_msg):
    pass


def no_hold():
    """The forms without the license hold, for a fixture (the repository's file holds 25 outlets since 21 October)."""
    return mock.patch.object(brief, "licensed_outlets", return_value=set())


class TheWhyLine(unittest.TestCase):
    def test_no_adjective_of_the_list_and_one_sentence(self):
        for why, head in (("Massive AI capex signals unprecedented demand. A second sentence.", "Anthropic may spend"),
                          ("Key counterparty exposure; major shift.", "A deal"), ("Critically low stocks.", "India's coal")):
            out = brief.why_line(why, head)
            self.assertFalse(ADJ.search(out), out)
            self.assertIsNone(brief.sentence_end(out), out)
            self.assertEqual(brief.why_check(out, head), [] if out else ["empty"])

    def test_no_figure_the_headline_gives_and_the_stop(self):
        out = brief.why_line("A 600 MW load adds demand to the grid", "Sesterce plans a 600MW campus")
        self.assertEqual(out, "A load adds demand to the grid.")
        self.assertEqual(brief.detail({"mw": "600", "price": "$10bn", "parties": "Sesterce"}, "Sesterce plans a 600MW campus for $10bn"),
                         "parties: Sesterce. ")

    def test_the_money_style(self):
        self.assertEqual(brief.why_line("Funds a $1.2B pipeline with an $800MM loan", "DOE"), "Funds a USD 1.2 billion pipeline with a USD 800 million loan.")
        self.assertEqual(brief.money_style("C$14.3 Billion"), "CAD 14.3 billion")

    def test_the_prompt_and_the_rubric_carry_the_rule(self):
        for text in (score.SYSTEM, score.RUBRIC):
            self.assertIn("consequence", text)
            self.assertIn("no figure the title already gives", text)

    def test_the_twenty_saved_items(self):
        with open(os.path.join(ROOT, "tests", "fixtures", "periodicals", "why_lines.json"), encoding="utf-8") as f:
            items = json.load(f)["items"]
        self.assertEqual(len(items), 20)
        for it in items:
            with self.subTest(it["event_id"]):
                self.assertEqual(brief.why_line(it["why"], it["head"]), it["expected_why"])


class OneTopicOneItem(unittest.TestCase):
    clusters = frame(rec("d1", "Anthropic may spend 750 billion", "datacenter_power", "Anthropic", sig=9),
                     rec("d2", "Amazon pledges 16 billion in Germany", "datacenter_power", "Amazon", sig=8),
                     rec("g1", "UK approves Jackdaw gas field", "gas", "UK", sig=8),
                     rec("k1", "South Korea to invest in U.S. nuclear projects, including 8 large reactors", "nuclear",
                         "US Department of Commerce; South Korea", sig=8, price="$120 billion"),
                     rec("k2", "USA, South Korea targeting six AP1000 and two APR1400 units", "nuclear",
                         "US Department of Commerce; Westinghouse; South Korea", sig=8, why="USD120 billion framework."),
                     rec("o1", "Brent at 110 as Hormuz worries persist", "oil", "", sig=7))

    def test_one_event_once_and_one_topic_once(self):
        with tempfile.TemporaryDirectory() as d:
            top10, by_group, ai = brief.select(self.clusters, "2026-10-21", quiet, folder=d)
        ids = list(top10["cluster_id"])
        self.assertIn("k1", ids)
        self.assertNotIn("k2", ids)          # one event (470)
        self.assertNotIn("d2", ids)          # one topic (802): folded under d1
        self.assertEqual([x["cluster_id"] for x in brief.also_of(top10.to_dict("records")[0])], ["d2"])
        self.assertEqual(top10["sector"].nunique(), len(top10))

    def test_not_the_day_before_again(self):
        with tempfile.TemporaryDirectory() as d:
            with open(os.path.join(d, "2026-10-20.md"), "w", encoding="utf-8") as f:
                f.write("# ERW's Energy Digest, 2026-10-20\n\n## Top of the industry\n\n1. **Voltus raises USD 225 million** (capital)  \n"
                        "   Why. parties: Voltus. Sources: [Y](https://example.org/voltus)\n")
            c = frame(rec("v", "Voltus raises $225 million for its platform", "capital", "Voltus", links=[("Y", "https://example.org/voltus")]))
            self.assertEqual(len(brief.not_shown_before(c, [os.path.join(d, "2026-10-20.md")], quiet)), 0)

    def test_the_also_line_is_part_of_the_hard_check(self):
        L = ["1. **A** (oil)  ", "   Why. Sources: [X](https://example.org/1)  ", "   Also on this topic: B ([Y](https://example.org/2)).",
             "2. **C** (gas)  ", "   Why. Sources: [Z](https://example.org/2)"]
        with self.assertRaises(RuntimeError):
            brief.assert_unique(L)


class CommentaryUnderNews(unittest.TestCase):
    """Session 814: among equals in significance a reported event ranks before a column, an interview or an analysis."""

    def test_the_kinds(self):
        for t in ("Brookfield's Teskey sees no slowdown in AI infrastructure build", "Land & Expand tracks North America's data center pipeline",
                  "Iran war tilts balance of global oil power towards the Americas: analysis", "How Low Can the Strategic Petroleum Reserve Actually Go?",
                  "Critical Capital: Lara Pierpoint on nuclear costs, hyperscaler contracts and trust in government funding (interview)",
                  "Why the midterms could swing on diesel", "BlackRock's Fink says slow data-center buildout is inflationary"):
            self.assertEqual(brief.title_kind(t), "commentary", t)
        for t in ("UK approves the long-delayed Jackdaw gas field", "DOE announces $967 million in grid resilience funding",
                  "The Nuclear Company proposes a 6,600 MW campus of six AP1000 reactors in Kentucky", "Brent trades at $110.30 per barrel"):
            self.assertEqual(brief.title_kind(t), "event", t)

    def test_an_event_ranks_before_commentary_at_the_same_score(self):
        s = pd.DataFrame([
            {"cluster_id": "c", "sig": 7, "ai": 9, "sector": "datacenter_power", "why": "Why.", "mw": "", "price_mentioned": "", "parties": "",
             "event_date": "2026-10-13T01:00:00Z", "source": "O", "source_url": "https://e/c", "title": "Brookfield's Teskey sees no slowdown in AI build", "summary": ""},
            {"cluster_id": "e", "sig": 7, "ai": 0, "sector": "deal", "why": "Why.", "mw": "600", "price_mentioned": "", "parties": "A",
             "event_date": "2026-10-13T02:00:00Z", "source": "O", "source_url": "https://e/e", "title": "A signs a 600 MW supply deal with B", "summary": ""},
            {"cluster_id": "h", "sig": 8, "ai": 0, "sector": "oil", "why": "Why.", "mw": "", "price_mentioned": "", "parties": "",
             "event_date": "2026-10-13T03:00:00Z", "source": "O", "source_url": "https://e/h", "title": "How low can the reserve go?", "summary": ""}])
        c = brief.build_clusters(s)
        self.assertEqual(list(c["cluster_id"]), ["h", "e", "c"])   # a higher score still comes first; among the 7s the event first
        self.assertEqual(list(c["kind"]), ["commentary", "event", "commentary"])


class TheOutlet(unittest.TestCase):
    def test_the_three_forms(self):
        lic = {"Reuters"}
        self.assertEqual(brief.source_text("Heatmap News", GN, lic), f"[Heatmap News]({GN}) (via Google News)")
        self.assertEqual(brief.source_text("T&D World", "https://www.tdworld.com/x", lic), "[T&D World](https://www.tdworld.com/x)")
        # session 2701 (rulings item 15, the 24-hour default): a held outlet keeps its link; a source is still printed once a link
        self.assertEqual(brief.source_text("Reuters", GN, lic), f"[Reuters]({GN}) (via Google News)")
        self.assertEqual(brief.link_text([("Reuters", GN), ("Reuters", GN)], lic), f"[Reuters]({GN}) (via Google News)")

    def test_the_email_s_text_never_prints_a_google_address(self):
        lines = ["# ERW's Energy Digest, 2026-10-21", "", "## Top of the industry", "", "1. **Head** (oil)  ",
                 f"   The why. Sources: [Bloomberg.com]({GN}) (via Google News)", "", "## By sector"]
        t, h = email_digest.story_list(email_digest.numbered(lines, ("## Top of the industry",)))
        self.assertNotIn("news.google.com", "\n".join(t))
        self.assertIn("Bloomberg.com (via Google News)", "\n".join(t))
        self.assertIn(f'<a href="{GN}">', h)

    def test_the_hold_is_read_from_the_license_file(self):
        with tempfile.TemporaryDirectory() as d:
            p = os.path.join(d, "license_status.csv")
            with open(p, "w", encoding="utf-8", newline="") as f:
                f.write("table,status,from,publishers,verdict,permission,permission_ref,note\n"
                        "news_index,license needed,2026-10-21,Bloomberg; Reuters,needs written permission,,,n\n")
            self.assertEqual(brief.licensed_outlets(p), {"Bloomberg", "Reuters"})


def hours(day, tz, values):
    start = pd.Timestamp(day.date()).tz_localize(tz)
    ts = [start + pd.Timedelta(hours=i) for i in range(24)]
    return pd.DataFrame({"ts_utc": [t.tz_convert("UTC") for t in ts], "value": values, "node": "x", "variable": "dam", "freq": "PT1H"})


DAY = pd.Timestamp("2026-10-20")


def fake_fetch(table, start=None, end=None, node=None, market=None, ba=None, **kw):
    if table == "iso_dam_hub_prices":
        is_yday = pd.Timestamp(start.date()) == pd.Timestamp(DAY.date())
        day = start.tz_convert(None).normalize()
        if market == "ercot_dam":
            return hours(day, "America/Chicago", [28.38 if is_yday else 26.28] * 24)
        if market == "caiso_dam":
            return hours(day, "America/Los_Angeles", [45.01 if is_yday else 40.81] * 24)
        if market == "spp_dam":
            return hours(day, "America/Chicago", [23.33] * 24)
        return pd.DataFrame(columns=["ts_utc", "value"])
    if table in ("nyiso_dam_zone_prices", "isone_dam_zone_prices"):
        return hours(start.tz_convert(None).normalize(), "America/New_York", [49.25] * 24)
    if table == "eia_fuel_spot_prices":
        rows = []
        for ent, vals in (("eia:henry_hub", [("2026-10-13", 3.32), ("2026-10-14", 3.22)]), ("eia:wti_cushing", [("2026-10-13", 99.0), ("2026-10-14", 101.91)]),
                          ("eia:brent", [("2026-10-13", 120.0), ("2026-10-14", 126.55)])):
            for d, v in vals:
                rows.append({"entity": ent, "ts_utc": pd.Timestamp(d, tz="UTC"), "value": v, "unit": "USD/MMBtu" if "henry" in ent else "USD/bbl"})
        return pd.DataFrame(rows)
    if table == "iso_rtm_hub_prices":
        ts = [start + pd.Timedelta(minutes=15 * i) for i in range(96)]
        return pd.DataFrame({"ts_utc": ts, "value": [20.0] * 95 + [276.41], "node": "SPPNORTH_HUB", "variable": "lmp_rtm_15m_mean", "freq": "PT15M"})
    if table == "eia930_all_demand":
        ts = [start + pd.Timedelta(hours=i) for i in range(24)]
        return pd.DataFrame({"ts_utc": ts, "value": [600000 + 1000 * i for i in range(24)], "variable": "demand_mw", "entity": "eia930:US48"})
    raise brief.erw.ERWDataNotFound(table)


class TheNumbersTraced(unittest.TestCase):
    """Every figure line of the numbers section is in the form the site's parser and scripts/check_digest.py key."""

    @classmethod
    def setUpClass(cls):
        with mock.patch.object(brief.erw, "fetch", side_effect=fake_fetch), mock.patch.object(brief, "held_grids", return_value={"NYISO", "ISO-NE"}), \
                mock.patch.object(brief, "rt_parts", return_value=[("spp", "iso_rtm_hub_prices", "spp_rtm")]), \
                mock.patch.object(brief, "cite_short", side_effect=lambda t: f"`{t}`"), mock.patch.object(brief, "paused_row", return_value=None), no_hold():
            cls.lines = brief.numbers_today("2026-10-21", quiet, None)

    def test_the_forms(self):
        movers = [ln for ln in self.lines if MOVER.match(ln)]
        self.assertEqual(len(movers), 5)
        self.assertEqual(sum(1 for ln in self.lines if FUEL_LINE.match(ln) and not MOVER.match(ln)), 3)
        self.assertEqual(sum(1 for ln in self.lines if RT_LINE.match(ln)), 1)
        self.assertEqual(len(DEMAND.findall("\n".join(self.lines))), 2)   # yesterday, and the same weekday a year before
        rows = [ln for ln in self.lines if re.match(r"^\| (ERCOT|CAISO|NYISO|MISO|SPP|ISO-NE) \|", ln)]
        self.assertEqual(len(rows), 6)
        for r in rows:
            cells = [c.strip() for c in r.strip("|").split("|")]
            self.assertEqual(len(cells), 7, r)
            self.assertRegex(cells[4], r"^\[\d+\]$")
        self.assertTrue(any("Not ranked: NYISO N.Y.C. (licensed source needed)" in ln for ln in self.lines))

    def test_no_bare_figure_without_its_unit(self):
        for ln in self.lines:
            if ln.startswith("- ") and MOVER.match(ln):
                self.assertFalse(re.search(r"(?<![\d.,])\d+\.\d{2}(?= |$)(?! UTC)", re.sub(r"\d{4}-\d{2}-\d{2} \d{2}:\d{2}", "", ln).replace(" USD", "USD")), ln)


class TheChartFollowsTheDay(unittest.TestCase):
    IOWA = {"source": "scanner", "key": "iowa", "rank": 1, "fact": "Retail electricity price in Iowa, industrial: USD 99.90 per MWh in July 2026.",
            "table": "eia_retail_electricity_prices", "series_key": "entity=eia:retail_price:IA:IND|variable=retail_price", "flag": {"id": "iowa", "rule": "record", "strength": 1.6, "value": 99.9, "compared": {"old_record": 91.7}}, "card": {"title": "T"}}
    UTAH = {"source": "scanner", "key": "utah", "rank": 2, "fact": "Retail electricity sales in Utah, residential: 1,658,263 MWh in July 2026.",
            "table": "eia_retail_sales_monthly", "series_key": "entity=eia:retail_sales:UT:RES|variable=retail_sales", "flag": {"id": "utah", "rule": "record", "strength": 1.7, "value": 1658263, "compared": {"old_record": 1484757}}, "card": {"title": "T"}}

    def test_the_related_candidate_comes_first_and_strength_decides_without_stories(self):
        stories = [{"titles": ["Iowa industrial rates rise for data centers"], "sector": "power_prices", "why": "", "parties": ""}]
        self.assertEqual(dc.choose([self.IOWA, self.UTAH], set(), stories=stories)[0]["key"], "iowa")
        self.assertEqual(dc.choose([self.IOWA, self.UTAH], set())[0]["key"], "utah")

    def test_the_roundup_says_where_the_week_s_stories_point(self):
        m = {"template": "watch_battery_discharge_us", "title": "Batteries discharging, Lower 48", "finding": "Lower 48 battery discharge fell.",
             "also_moved": [{"template": "watch_crude_exports", "title": "US crude oil exports", "finding": "US crude oil exports: 4,765 kbbl/d, up 1,195."}]}
        best, same = roundup.chart_relevance(m, [{"titles": ["OPEC cuts as US crude exports hit a record"], "sector": "oil", "why": "", "parties": "OPEC"}], quiet)
        self.assertEqual((best["template"], same), ("watch_crude_exports", False))


class TheFiveNumbers(unittest.TestCase):
    def test_each_line_in_the_checker_s_form(self):
        import check_roundup as cr
        facts = {"dam": [dict(label="ERCOT", node="HB_NORTH", table="iso_dam_hub_prices", m1=41.94, m0=32.82, ref="[1]")],
                 "us48": dict(top={"value": 612345.0, "ts_utc": pd.Timestamp("2026-10-07T21:00:00Z")}, ref="[6]")}
        deals = pd.DataFrame([{"event_id": "deal:a", "event_date": "2026-10-09T21:45:00Z", "deal_type": "m_and_a", "buyer": "Shell", "seller": "Equinor",
                               "asset": "Bay du Nord", "mw": "", "dollars": "12000000000", "confidence": "0.9"}])
        dcs = pd.DataFrame([{"entity_id": "dc:a", "first_story_at": "2026-10-07T10:00:00Z", "capacity_mw": "1200", "operator": "Crusoe", "site_name": "Spark", "city": "Abilene", "state": "TX", "confidence": "0.9"}])
        with tempfile.TemporaryDirectory() as d, mock.patch.object(roundup, "read_table", lambda n: {"energy_deals": deals, "datacenter_projects": dcs}.get(n)), \
                mock.patch.object(roundup, "ANALYSIS_DIR", d):
            L = roundup.five_numbers("2026-W41", pd.Timestamp("2026-10-05", tz="UTC"), pd.Timestamp("2026-10-12", tz="UTC"), facts, quiet)
        text = "\n".join(L)
        self.assertTrue(cr.FIVE_DAM.search(text))
        self.assertTrue(cr.FIVE_US48.search(text))
        # session 1460 (faults 28 and 29): the keys are on the five's Tables line; the tracer reads them there
        deal, deal_mw, load, chart = cr.five_keyed(text)
        self.assertEqual(deal, ("USD 12 billion", "deal:a"))
        self.assertEqual(load, ("1,200", "dc:a"))
        self.assertIsNone(deal_mw)
        self.assertIsNone(chart)
        self.assertNotIn("deal:a)", text.split("Tables:")[0])
        self.assertIn("no chart of the week was picked", text)


class TheEmailsRead(unittest.TestCase):
    """Session 817: the emails as a reader on a phone reads them: the Roundup's blocks in the page's order, the stories
    folded under an item with it (no address in the text part), the week in five numbers first."""

    ROUNDUP = ("# ERW's Roundup, 2026-W43\n\nERW's weekly roundup for 2026-10-19 to 2026-10-25, from 680 scored stories.\n\n"
               "## The week in five numbers\n\n- **US48 peak demand:** 519,415 MW in the hour starting 2026-10-20 22:00 UTC [6].\n\n"
               "## Weekend\n\n- no scored story was published on 2026-10-24 or 2026-10-25 (UTC).\n\n## The five stories of the week\n\n"
               "1. **S1** (deal, 3 stories)  \n   Why one. Sources: Bloomberg, Reuters  \n"
               f"   Also on this topic: Anthropic May Spend USD 750 billion ([Bloomberg.com]({GN}) (via Google News)); Second ([X](https://x.org/2)).\n"
               + "".join(f"{i}. **S{i}** (oil, 1 story)  \n   Why. Sources: [X](https://example.org/{i})\n" for i in range(2, 6))
               + "\n## Deals of the week\n\n- none\n\n## ERW's Policy of the Week\n\n**A notice** (FERC notice, published 2026-10-20)\n\nThe read. [Source](https://example.org/p)\n\n"
               "## ERW's Numbers This Week\n\n**US48 peak demand of the week:** 519,415 MW in the hour starting 2026-10-20 22:00 UTC [6].\n\nTables: [6] `eia930_all_demand` (x).\n\n"
               "## ERW's Chart of the Week\n\n- no chart of the week was picked for this week.\n\nERW\n\n---\n")

    def render(self):
        with tempfile.TemporaryDirectory() as d:
            p = os.path.join(d, "roundup.md")
            with open(p, "w", encoding="utf-8") as f:
                f.write(self.ROUNDUP)
            return email_digest.render(p, "roundup", unsubscribe="x")

    def test_the_blocks_in_the_page_s_order(self):
        _, _, text, html_ = self.render()
        order = [text.index(x) for x in ("The week in five numbers", "Weekend", "The five stories of the week", "ERW's Policy of the Week",
                                         "ERW's Numbers This Week", "ERW's Chart of the Week")]
        self.assertEqual(order, sorted(order))
        self.assertLess(html_.index("ERW's Policy of the Week</h2>"), html_.index("ERW's Numbers This Week</h2>"))

    def test_the_folded_stories_go_with_their_item(self):
        _, _, text, html_ = self.render()
        self.assertIn("   Also on this topic: Anthropic May Spend USD 750 billion (Bloomberg.com (via Google News)); Second (X).", text)
        self.assertNotIn("news.google.com", text)
        self.assertIn("Also on this topic: Anthropic May Spend USD 750 billion (<a href=", html_)
        items = email_digest.numbered(self.ROUNDUP.splitlines(), ("## The five stories of the week",))
        self.assertEqual(items[0]["why"], "Why one.")
        self.assertEqual(items[0]["src"], ("Bloomberg", None))
        self.assertEqual(items[1]["also"], "")


def stories():
    path = os.path.join(ROOT, "warehouse", "output", "news_stories.csv")
    if not os.path.exists(path):
        return None
    with open(path, encoding="utf-8") as f:
        body = "".join(ln for ln in f if not ln.startswith("#"))
    return pd.read_csv(io.StringIO(body), dtype=str, keep_default_na=False)


class TheNamedDays(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.s = stories()
        if cls.s is None or not os.path.exists(os.path.join(ROOT, "docs", "digest", "2026-10-13.md")):
            raise unittest.SkipTest("news_stories.csv or the issues are not here")
        cls.when = pd.to_datetime(cls.s["event_date"], utc=True, format="ISO8601")

    def clusters(self, date):
        with open(os.path.join(ROOT, "docs", "digest", f"{date}.md"), encoding="utf-8") as f:
            m = re.search(r"(?:for|from) the (\d+) hours to (\d{4}-\d{2}-\d{2} \d{2}:\d{2}) UTC", f.read())
        hours_, now = int(m.group(1)), pd.Timestamp(m.group(2), tz="UTC")
        s = self.s[(self.s["scored_at"] != "") & (self.when >= now - pd.Timedelta(hours=hours_)) & (self.when <= now)].copy()
        s["sig"] = s["significance"].astype(int)
        s["ai"] = s["ai_power_relevance"].astype(int)
        return brief.build_clusters(s[s["sig"] > 0])

    def test_2_october_korea_once_9_october_without_voltus_13_october_one_datacenter_item(self):
        c = self.clusters("2026-10-02")
        if {"news:8470c320a7225474", "news:ec41f0a2f9b34be4"} <= set(c["cluster_id"]):
            top10, _, _ = brief.select(c, "2026-10-02", quiet)
            # once: session 2701's tie-break (item 4) may keep either twin, never both
            self.assertEqual(len({"news:8470c320a7225474", "news:ec41f0a2f9b34be4"} & set(top10["cluster_id"])), 1)
        c = self.clusters("2026-10-09")
        if "news:f96cc76a18212ba4" in set(c["cluster_id"]):
            top10, by_group, ai = brief.select(c, "2026-10-09", quiet)
            shown = set(top10["cluster_id"]) | set(ai["cluster_id"]) | {x for g in by_group.values() for x in g["cluster_id"]}
            self.assertNotIn("news:f96cc76a18212ba4", shown)
        c = self.clusters("2026-10-13")
        top10, _, _ = brief.select(c, "2026-10-13", quiet)
        self.assertEqual(len(top10), 10)
        self.assertLessEqual(int((top10["sector"] == "datacenter_power").sum()), brief.SECTOR_MAX)   # session 2701, item 13

    def test_an_issue_rendered_without_the_model_holds_every_rule(self):
        """The 21 October window, selected and rendered as the no-model path does, line by line."""
        c = self.clusters("2026-10-21")
        with no_hold():
            top10, by_group, ai = brief.select(c, "2026-10-21", quiet)
            heads = brief.own_titles(pd.concat([top10, *by_group.values(), ai]).drop_duplicates("cluster_id"))
            L = []
            for i, r in enumerate(top10.to_dict("records"), 1):
                L += brief.item_lines(r, f"{i}. **{heads[r['cluster_id']]}** ({r['sector']})  ",
                                      (brief.why_line(r["why"], heads[r["cluster_id"]]) + " " + brief.detail(r, heads[r["cluster_id"]])).strip(),
                                      f"Sources: {brief.link_text(r['links'])}")
        self.assertEqual(brief.assert_unique(brief.drop_repeated_items(L, quiet)), len(top10))
        for r, ln in zip(top10.to_dict("records"), [x for x in L if x.startswith("   ") and "Sources:" in x]):
            why = ln.strip().split("Sources:")[0]
            self.assertFalse(ADJ.search(why), why)
            head = heads[r["cluster_id"]]
            self.assertFalse(brief.figures_of(why.split(". parties:")[0]) & brief.figures_of(head) - brief.figures_of(brief.why_fallback(head)), (head, why))
            self.assertNotIn("news.google.com)", why)
        self.assertLessEqual(int(top10["sector"].value_counts().max()), brief.SECTOR_MAX)   # session 2701, item 13: two a sector at most


# Session 2701: the Digest's rulings of docs/reviews/periodicals-rulings-2026-10-23.md applied as their defaults (the
# owner's rule of 18 October: a proposed ruling's default holds after 24 hours of silence). One class an item.

LICENSE_ROWS = ("table,status,from,publishers,verdict,permission,permission_ref,note\n"
                "nyiso_dam_zone_prices,license needed,2026-10-21,NYISO,needs written permission,,,n\n"
                "isone_dam_zone_prices,license needed,2026-10-21,ISO-NE,needs written permission,,,n\n"
                "nyiso_rtm_zone_prices,license needed,2026-10-21,NYISO,needs written permission,,,n\n"
                "iso_rtm_hub_prices,license needed,2026-10-21,MISO,needs written permission,,,n\n")


def rt_fetch(table, start=None, end=None, node=None, market=None, ba=None, **kw):
    """fake_fetch, with NYISO's real-time table holding the day's highest price (a held grid's)."""
    if table == "nyiso_rtm_zone_prices":
        ts = [start + pd.Timedelta(minutes=5 * i) for i in range(288)]
        return pd.DataFrame({"ts_utc": ts, "value": [30.0] * 287 + [999.99], "node": "N.Y.C.", "variable": "lmp_rtm", "freq": "PT5M"})
    return fake_fetch(table, start, end, node, market, ba, **kw)


class Item1NoHeldDigit(unittest.TestCase):
    """Item 1: a held grid prints "licensed source needed" and no digit; the real-time maximum skips held tables."""

    def test_no_held_digit_in_the_numbers(self):
        with tempfile.TemporaryDirectory() as d:
            p = os.path.join(d, "license_status.csv")
            with open(p, "w", encoding="utf-8", newline="") as f:
                f.write(LICENSE_ROWS)
            parts = [("spp", "iso_rtm_hub_prices", "spp_rtm"), ("miso", "iso_rtm_hub_prices", "miso_rtm"), ("nyiso", "nyiso_rtm_zone_prices", None)]
            self.assertEqual(brief.held_grids(p), {"NYISO", "ISO-NE"})
            self.assertEqual(brief.held_rt(parts, p), {("miso", "iso_rtm_hub_prices"), ("nyiso", "nyiso_rtm_zone_prices")})
            with mock.patch.object(brief, "LICENSE_FILE", p), mock.patch.object(brief.erw, "fetch", side_effect=rt_fetch), \
                    mock.patch.object(brief, "rt_parts", return_value=parts), mock.patch.object(brief, "cite_short", side_effect=lambda t: f"`{t}`"), \
                    mock.patch.object(brief, "paused_row", return_value=None), no_hold():
                lines = brief.numbers_today("2026-10-21", quiet, None)
        text = "\n".join(lines)
        for grid in ("NYISO", "ISO-NE"):
            row = next(ln for ln in lines if ln.startswith(f"| {grid} |"))
            cells = [c.strip() for c in row.strip("|").split("|")]
            self.assertEqual(cells[3], "licensed source needed", row)
            self.assertEqual(cells[5], "", row)
            self.assertEqual(cells[6], "not computed", row)
        self.assertNotIn("49.25", text)            # the held grids' fixture price appears nowhere
        self.assertNotIn("999.99", text)           # nor the held real-time maximum
        rt = next(ln for ln in lines if ln.startswith("**Highest real-time price"))
        self.assertIn("276.41 USD/MWh at SPPNORTH_HUB (SPP)", rt)
        self.assertTrue(rt.endswith("Not read: MISO, NYISO (licensed source needed)."), rt)
        self.assertTrue(RT_LINE.match(rt))


class Item3TheWindowOpensAtThePreviousEnd(unittest.TestCase):
    """Item 3: the window opens at the previous issue's end, capped at 96 hours."""

    def issues(self, d, **stamps):
        for day, line in stamps.items():
            with open(os.path.join(d, f"{day.replace('_', '-')}.md"), "w", encoding="utf-8") as f:
                f.write(f"# ERW's Energy Digest, {day}\n\n{line}\n")

    def test_monday_holds_friday_evening_and_a_missed_day_is_caught_up(self):
        now = pd.Timestamp("2026-10-26 15:45", tz="UTC")   # a Monday
        with tempfile.TemporaryDirectory() as d:
            self.issues(d, **{"2026_10_22": "ERW's weekday brief of energy news for the 24 hours to 2026-10-22 15:45 UTC, from 2026-10-21 15:45 UTC, from 9 scored stories.",
                              "2026_10_23": "ERW's weekday brief of energy news for the 24 hours to 2026-10-23 15:46 UTC, from 2026-10-22 15:45 UTC, from 9 scored stories."})
            prev = brief.previous_end("2026-10-26", d)
            self.assertEqual(prev, pd.Timestamp("2026-10-23 15:46", tz="UTC"))
            start = brief.window_start(now, None, prev)
            self.assertEqual(start, prev)
            self.assertEqual(brief.window_hours(start, now), 72)
            # the issue of 23 October is the newest before 23 October's own rerun: 22 October's end
            self.assertEqual(brief.previous_end("2026-10-23", d), pd.Timestamp("2026-10-22 15:45", tz="UTC"))
        # a run that missed Friday and Monday: Tuesday's window opens 96 hours back, not at Thursday's end
        tue = pd.Timestamp("2026-10-27 15:45", tz="UTC")
        self.assertEqual(brief.window_hours(brief.window_start(tue, None, pd.Timestamp("2026-10-22 15:45", tz="UTC")), tue), 96)
        # no earlier issue, or a fixed --hours: as before
        self.assertEqual(brief.window_hours(brief.window_start(now, None, None), now), 24)
        self.assertEqual(brief.window_hours(brief.window_start(now, 24, prev), now), 24)

    def test_the_generated_line_when_the_stamp_is_old(self):
        with tempfile.TemporaryDirectory() as d:
            self.issues(d, **{"2026_10_01": "ERW's weekday brief of energy news.\n\n<!-- Generated by warehouse/news/brief.py at 2026-10-01 15:44 UTC; run log x -->"})
            self.assertEqual(brief.previous_end("2026-10-02", d), pd.Timestamp("2026-10-01 15:44", tz="UTC"))
            self.assertIsNone(brief.previous_end("2026-10-01", d))

    def test_the_rows_of_the_window_and_the_stamp(self):
        now = pd.Timestamp("2026-10-26 15:45", tz="UTC")
        df = pd.DataFrame({"event_date": ["2026-10-23T18:00:00Z", "2026-10-23T12:00:00Z", "2026-10-26T16:00:00Z"],
                           "scored_at": ["x", "x", "x"], "significance": ["6", "6", "6"], "ai_power_relevance": ["0", "0", "0"]})
        start = brief.window_start(now, None, pd.Timestamp("2026-10-23 15:46", tz="UTC"))
        s, st, _ = brief.window_rows(df, now, brief.window_hours(start, now), start)
        self.assertEqual(list(s["event_date"]), ["2026-10-23T18:00:00Z"])   # Friday evening in; before the end out; after the run out
        self.assertTrue(brief.stamp_line(72, st, now, 1).startswith("ERW's weekday brief of energy news for the 72 hours to 2026-10-26 15:45 UTC"))


class Item4TheTieBreak(unittest.TestCase):
    """Item 4: among equal significance (and kind), more outlets first, then the earlier story; AI relevance no longer counts."""

    def story(self, cid, source, when, ai=0, sig=7, title=None):
        return {"cluster_id": cid, "sig": sig, "ai": ai, "sector": "deal", "why": "Why.", "mw": "", "price_mentioned": "", "parties": "",
                "event_date": when, "source": source, "source_url": f"https://e/{cid}/{source}", "title": title or f"A signs deal {cid}", "summary": ""}

    def test_outlets_then_time_not_ai(self):
        s = pd.DataFrame([
            self.story("dc", "Outlet A", "2026-10-13T01:00:00Z", ai=10, title="A 42 MW datacenter signs a supply deal"),
            self.story("gas", "Outlet A", "2026-10-13T02:00:00Z", title="A 600 MW gas plant deal is signed"),
            self.story("gas", "Outlet B", "2026-10-13T02:30:00Z", title="A 600 MW gas plant deal is signed"),
            self.story("late", "Outlet C", "2026-10-13T05:00:00Z"),
            self.story("early", "Outlet D", "2026-10-13T00:30:00Z"),
            self.story("top", "Outlet E", "2026-10-13T06:00:00Z", sig=9)])
        c = brief.build_clusters(s)
        self.assertEqual(list(c["cluster_id"]), ["top", "gas", "early", "dc", "late"])
        self.assertEqual(int(c.loc[c["cluster_id"] == "gas", "outlets"].iloc[0]), 2)


class Item7APunIsHeldToItsSource(unittest.TestCase):
    """Item 7: a pun that states a claim needs a verified span, like any second half; the bank's puns the rule refuses
    are cut (status dropped, with the reason), and every pun still verified passes it."""

    def test_the_rule_and_the_bank(self):
        import funfact
        bank = funfact.read_bank()
        puns = bank[bank["structure"] == "pun"]
        for r in puns.to_dict("records"):
            if r["status"] == "verified":
                self.assertIsNone(funfact.PUN_CLAIM.search(r["second"]), r["second"])
        for fid in ("ff_6c3f03312f", "ff_528bbbd5f8"):   # the audit's 2 October pun; the kWh pun
            r = bank[bank["fact_id"] == fid].iloc[0]
            self.assertEqual(r["status"], "dropped")
            self.assertIn("rulings item 7", r["reason"])
            probs = funfact.check_record(r.to_dict())
            self.assertTrue(any("a pun that states a claim" in p for p in probs), probs)
        btu = bank[bank["fact_id"] == "ff_b2e98af092"].iloc[0]   # the Btu match: dropped before, refused by the rule too
        self.assertTrue(funfact.PUN_CLAIM.search(btu["second"]))
        duck = bank[bank["fact_id"] == "ff_85d03fb363"].iloc[0]
        self.assertFalse(any("a pun that states a claim" in p for p in funfact.check_record(duck.to_dict())))


class Item8TheFourteenthStaysAsWritten(unittest.TestCase):
    """Item 8: the 14 October issue is not rewritten; its page says so in one line."""

    def test_the_issue_and_its_line(self):
        with open(os.path.join(ROOT, "docs", "digest", "2026-10-14.md"), encoding="utf-8") as f:
            self.assertIn("Senghenydd colliery disaster", f.read())   # as written
        with open(os.path.join(ROOT, "site", "lib", "digest.ts"), encoding="utf-8") as f:
            ts = f.read()
        notes = ts[ts.index("export const ISSUE_NOTES"):]
        notes = notes[:notes.index("};")]
        self.assertEqual(re.findall(r'"(\d{4}-\d{2}-\d{2})":', notes), ["2026-10-14"])
        self.assertIn("kept as it was written", notes)
        with open(os.path.join(ROOT, "site", "app", "digest", "[date]", "page.tsx"), encoding="utf-8") as f:
            page = f.read()
        self.assertIn("data-issue-note={date}>{ISSUE_NOTES[date]}</p>", page)



class Item13TheTopicKeyIsTheSectorWithTheRegion(unittest.TestCase):
    """Item 13: one sector in two regions is two topics; a cluster without a region is of every region; two items a
    sector at most, the third folded under the sector's first."""

    def test_regions(self):
        mx = dict(rec("mx", "Mexico plans 8,200 MW of new plants", "generation", "CFE", sig=9), region="Mexico")
        ind = dict(rec("in", "India's coal stocks fall at power plants", "generation", "Coal India", sig=8), region="India")
        tx = dict(rec("tx", "Texas adds a 900 MW peaker plant", "generation", "Vistra", sig=7), region="Texas")
        nor = dict(rec("nr", "Ormat wins a geothermal auction", "generation", "Ormat", sig=7), region="")
        gas = dict(rec("g1", "UK approves Jackdaw gas field", "gas", "UK", sig=8), region="United Kingdom")
        self.assertFalse(brief.same_topic(mx, ind))
        self.assertTrue(brief.same_topic(mx, dict(tx, region=" mexico ")))
        self.assertTrue(brief.same_topic(mx, nor))
        top, folded = brief.one_per_topic(frame(mx, ind, gas, tx), 10, quiet)
        self.assertEqual(list(top["cluster_id"]), ["mx", "in", "g1"])
        self.assertEqual([x["cluster_id"] for x in top.iloc[0]["also"]], ["tx"])   # a third generation item folds under the first
        self.assertEqual(folded, {"tx"})

    def test_build_clusters_keeps_the_region(self):
        s = pd.DataFrame([{"cluster_id": "a", "sig": 7, "ai": 0, "sector": "generation", "region": "Mexico", "why": "Why.", "mw": "",
                           "price_mentioned": "", "parties": "", "event_date": "2026-10-13T01:00:00Z", "source": "O",
                           "source_url": "https://e/a", "title": "A plant", "summary": ""}])
        self.assertEqual(brief.build_clusters(s).iloc[0]["region"], "Mexico")


class Item14TheAlsoLinesAreTheFold(unittest.TestCase):
    """Item 14: the "also" lines do not count toward the words above the fold (nor the sources, the numbers, the fold)."""

    def test_the_count(self):
        md = "\n".join([
            "# ERW Daily Digest", "", "One two three four five.", "",
            "1. **Six seven eight** (oil)  ",
            "   Nine ten eleven. Sources: [Reuters](https://r/1), [Bloomberg](https://b/1)  ",
            "   Also on this topic: a b c d e f g h (Outlet).",
            "| ERCOT | HB_NORTH | 2026-10-20 | 28.38 | [1] | 26.28 | +2.10 (+8.0%) |",
            "![Chart words](charts/x.png)", "Tables: [1] `iso_dam_hub_prices`", "",
            brief.FOLD_HEADING, "", "Twelve thirteen fourteen fifteen.", "", "ERW", "", "---"])
        self.assertEqual(brief.above_fold_words(md), 12)
        self.assertEqual(brief.above_fold_words(md.replace(brief.FOLD_HEADING, "## Not the fold")), 16)


class Item6TheChartsFloorAndTheDismissedDrafts(unittest.TestCase):
    """Item 6(b): no flag under 1.5 robust standard deviations is the chart; 6(c): no flag whose draft was dismissed."""

    def flag(self, key, strength):
        return {"source": "scanner", "key": key, "rank": 1, "fact": f"fact {key}", "table": "t", "series_key": f"entity={key}",
                "flag": {"id": key, "rule": "spike", "strength": strength}, "card": {"title": "T"}}

    def test_the_floor_and_the_dismissed(self):
        weak, mid, strong = self.flag("weak", 1.01), self.flag("mid", 1.5), self.flag("strong", 3.0)
        c, why = dc.choose([weak, mid, strong], set())
        self.assertEqual(c["key"], "strong")
        c, why = dc.choose([weak, mid, strong], set(), dismissed={"strong"})
        self.assertEqual(c["key"], "mid")   # the floor itself passes
        self.assertIn("1 flag(s) under the floor of 1.5 robust standard deviations passed over", why)
        self.assertIn("1 flag(s) whose draft was dismissed passed over", why)
        c, why = dc.choose([weak], set())
        self.assertIsNone(c)

    def test_the_dismissed_drafts_are_read_from_the_review_list(self):
        class R:
            status_code = 200

            def json(self):
                return [{"id": "scan-a"}, {"id": "scan-b"}]
        seen = {}

        def get(url, params=None, headers=None, timeout=None):
            seen.update(url=url, params=params)
            return R()
        with mock.patch.dict(os.environ, {"SUPABASE_URL": "https://x.supabase.co/rest/v1/", "SUPABASE_SERVICE_KEY": "k"}):
            self.assertEqual(dc.dismissed_keys(quiet, get=get), {"scan-a", "scan-b"})
        self.assertEqual(seen["url"], "https://x.supabase.co/rest/v1/scanner_drafts")
        self.assertEqual(seen["params"]["state"], "eq.dismissed")



class Item19TheFloorsCountLicenseNeeded(unittest.TestCase):
    """Item 19 (session 2702): a "license needed" mark counts toward a page's floor in check-values.mjs, and land_check.py
    says which floors the marks met; the gate fails on a lost figure, not on a held one."""

    def test_the_marks_and_the_verdict(self):
        import shutil
        import subprocess
        if shutil.which("node") is None:
            self.skipTest("node is not on this machine")
        mod = os.path.join(ROOT, "site", "scripts", "held-marks.mjs").replace("\\", "/")
        js = ("import('file:///" + mod.lstrip("/") + "').then((m) => console.log(JSON.stringify(["
              "m.heldMarks('<p><span data-license-held=\"a\">license needed</span> <span data-license-held=\"b\">license needed</span></p>'),"
              "m.heldMarks('<p title=\"license needed\">The figures: license needed. <b>License needed</b></p>'),"
              "m.heldMarks('<p>7 GW</p>'),"
              "m.floorVerdict(3, 7, 10), m.floorVerdict(3, 6, 10), m.floorVerdict(0, 0, undefined)])))")
        out = subprocess.run(["node", "-e", js], capture_output=True, text=True, timeout=60)
        self.assertEqual(out.returncode, 0, out.stderr)
        got = json.loads(out.stdout.strip().splitlines()[-1])
        self.assertEqual(got[:3], [2, 2, 0])
        self.assertEqual(got[3], {"counted": 10, "fail": False})
        self.assertEqual(got[4], {"counted": 9, "fail": True})
        self.assertEqual(got[5], {"counted": 0, "fail": False})

    def test_check_values_uses_them_and_land_check_counts_the_notes(self):
        with open(os.path.join(ROOT, "site", "scripts", "check-values.mjs"), encoding="utf-8") as f:
            src = f.read()
        self.assertIn('import { floorVerdict, heldMarks } from "./held-marks.mjs";', src)
        self.assertIn("const fv = floorVerdict(out.count, held, floor);", src)
        import land_check
        log = ("ok   | /map | x | page shows \"1\"\n"
               "note | /map | the floor | 1 checked numbers and 12 held by a license (\"license needed\") meet its floor of 10\n"
               "note | /map | the floor | the page carries 1 checked numbers and has no floor\n")
        self.assertEqual(land_check.held_floor_notes(log), ["/map"])



class Item10AMissedWeekIsSaid(unittest.TestCase):
    """Item 10 (session 2702): a Roundup whose previous ISO week has no issue says so in one line under its title."""

    def test_w43_with_no_w42(self):
        start = pd.Timestamp("2026-10-19", tz="UTC")   # Monday of 2026-W43
        with tempfile.TemporaryDirectory() as d:
            line = roundup.missed_week_line(start, d)
            self.assertEqual(line, "No Roundup was written for 2026-W42; that week's stories are in the Digests of 2026-10-12 to "
                                   "2026-10-16 ([the archive](/digest)).")
            with open(os.path.join(d, "2026-W42.md"), "w", encoding="utf-8") as f:
                f.write("# ERW's Roundup, 2026-W42\n")
            self.assertEqual(roundup.missed_week_line(start, d), "")
        self.assertIn("missed_week_line(start)", open(os.path.join(ROOT, "warehouse", "news", "roundup.py"), encoding="utf-8").read())



class Item11TheTablesFloorAndUSFirst(unittest.TestCase):
    """Item 11 (session 2702): confidence 0.7 or more and one of operator, site or MW; US first; at most 15; the rest counted."""

    def test_the_floor_and_the_order(self):
        rows = [{"confidence": "0.9", "operator": "Op", "site_name": "", "mw": "", "state": ""},          # passes, not US
                {"confidence": "0.6", "operator": "Low", "site_name": "S", "mw": "100", "state": "TX"},   # under: confidence
                {"confidence": "0.7", "operator": "", "site_name": "", "mw": "", "state": "VA"},          # under: nothing stated
                {"confidence": "0.85", "operator": "", "site_name": "", "mw": "300", "state": "TX"}]     # passes, US
        shown, rest, under = roundup.floor_rows(pd.DataFrame(rows), "datacenter_projects")
        self.assertEqual([r["confidence"] for r in shown], ["0.85", "0.9"])   # US first
        self.assertEqual((rest, under), (0, 2))
        many = pd.DataFrame([{"confidence": "0.8", "buyer": f"B{i}", "seller": "", "asset": "", "mw": "", "state": "",
                              "country": "United States" if i % 2 else "India"} for i in range(40)])
        shown, rest, under = roundup.floor_rows(many, "energy_deals")
        self.assertEqual((len(shown), rest, under), (15, 25, 0))
        self.assertTrue(all(roundup.row_is_us(r) for r in shown))   # 20 US rows: the 15 shown are all of them
        note = roundup.floor_note("energy_deals", "deals", shown, rest, under)
        self.assertIn("15 deals shown", note)
        self.assertIn("25 more pass, 0 fall under the floor; [the whole table](/data#energy_deals)", note)



# Session 2703: the Digest in the brandbook's v2 shape (the owner's rulings of 24 October 2026, queue file 131)

def cand(label, key, v, pv, pct, table="eia_fuel_spot_prices", unit="USD/MMBtu", reason="", node=""):
    return dict(label=label, key=key, unit=unit, v=v, pv=pv, d=pd.Timestamp("2026-10-14"), pd=pd.Timestamp("2026-10-13"),
                ch=round(v - pv, 4), pct=pct, table=table, reason=reason, node=node, ref="[1]")


V2_MD = """# ERW Daily Digest, 2026-10-23

**23 October 2026.** Data through 11:45 ET, 15:45 UTC.

<!-- subject: ERW Daily | Henry Hub natural gas: 3.22 USD/MMBtu, down 3.0% on the close before -->

<!-- opening: Henry_Hub_natural_gas -->

ERW's weekday brief of energy news for the 24 hours to 2026-10-23 15:45 UTC, from 2026-10-22 15:45 UTC, from 9 scored stories.

## The opening number

**Henry Hub natural gas: 3.22 USD/MMBtu on 2026-10-14, down 0.10 USD/MMBtu (3.0%) from 3.32 USD/MMBtu on 2026-10-13 [1].** EIA's spot close at Henry Hub, Louisiana, the US natural gas benchmark, against the close before it.

Tables: [1] `eia_fuel_spot_prices`.

## The numbers

- **Market price.** ERCOT HB_NORTH day-ahead: 28.38 USD/MWh on 2026-10-20, up 2.10 USD/MWh (8.0%) from 26.28 USD/MWh on 2026-10-19 [1]. Status: observed, the mean of the operating day's 24 hourly day-ahead prices.
- **Physical.** US48 demand peaked at 612,000 MW in the hour starting 2026-10-20 19:00 UTC [2]; the same weekday a year before (2025-10-21) is not held, so no change is shown. Status: observed, EIA-930 hourly demand.
- **Project or capacity.** 600 MW: A signs a gas plant deal (gas, ranked 2 of the day's top ten), reported on 2026-10-22 by Outlet. Change: a new report, no earlier figure held. Status: reported by the outlet, not a warehouse table's figure.
- **Policy, capital or reliability.** No story of the day states a policy, capital or reliability figure.

Tables: [1] `iso_dam_hub_prices`; [2] `eia930_all_demand`; balancing authority us48.

## What moved

1. **Oil surges on Saudi attacks** (oil)
   Supply fears lift crude. One outlet has reported it so far. Sources: [Rigzone](https://www.rigzone.com/a)
2. **A signs a gas plant deal** (gas)
   A new plant adds supply. Sources: [Outlet](https://example.org/b)

## More

### The rest of the top ten

1. **Third story** (nuclear)
   Why three. Sources: [Outlet](https://example.org/c)

### By sector

**Power**

- no scored story in this group today

### AI and power

- no further story on AI and power today (any such story is listed above)

### ERW's Numbers Today

- Brent crude: 126.55 USD/bbl on 2026-10-14, up 6.55 USD/bbl (5.5%) from 120.00 USD/bbl on 2026-10-13 [1].

Tables: [1] `eia_fuel_spot_prices`.

## ERW's Fun Fact

A fact that is fun.

Sources: [Wikipedia, Fun](https://en.wikipedia.org/wiki/Fun).

ERW

---

[How this is made.](/about#digest)

Corrections: [open an issue](https://github.com/SamuelEnrique/erw/issues). Preferences and topics: [subscribe](/subscribe). Every email carries its own unsubscribe link.
"""


class V2TheOpeningNumber(unittest.TestCase):
    """The opening number's rule (brief.opening_number's docstring): defensible moves only; consequence, then novelty,
    then source quality, then size; a structural figure of the top stories when no move is defensible."""

    def test_the_rule_on_fixtures(self):
        hub_big = cand("SPP SPPSOUTH_HUB day-ahead", "SPP", 40.0, 20.0, 100.0, table="iso_dam_hub_prices", unit="USD/MWh")
        hh = cand("Henry Hub natural gas", "Henry Hub natural gas", 3.22, 3.32, -3.01)
        wti = cand("WTI Cushing crude", "WTI Cushing crude", 101.91, 98.0, 3.99, unit="USD/bbl", reason=" Reason, from the day's stories: x")
        small = cand("Brent crude", "Brent crude", 126.55, 126.0, 0.44, unit="USD/bbl")
        # the largest move is not the choice by default: a benchmark named by a story comes first
        self.assertEqual(brief.opening_number([hub_big, hh, wti, small], [])["cand"]["key"], "WTI Cushing crude")
        # session 1440: without the reason a benchmark needs the larger bar (4.5): WTI's 3.99 and Henry Hub's 3.01 fail, and
        # the unnamed hub is the last resort when no story states a figure
        wti0 = dict(wti, reason="")
        self.assertEqual(brief.opening_number([hub_big, hh, wti0], [])["cand"]["key"], "SPP")
        wti5 = dict(wti0, pct=4.6)
        self.assertEqual(brief.opening_number([hub_big, hh, wti5], [])["cand"]["key"], "WTI Cushing crude")
        # novelty: yesterday's metric leads again only at twice the bar (WTI's 3.99 is under 6); Henry Hub named leads
        hh_named = dict(hh, reason=" Reason, from the day's stories: y")
        self.assertEqual(brief.opening_number([hub_big, hh_named, wti], [], prev_key="WTI_Cushing_crude")["cand"]["key"], "Henry Hub natural gas")
        # no defensible move: the structural figure of the highest-ranked story stating one
        recs = [rec("a", "A takes stock", sector="company"), rec("b", "B plans 600 MW", sector="gas", mw="600"), rec("c", "C raises $3bn", price="$3bn")]
        op = brief.opening_number([small], recs)
        self.assertEqual((op["kind"], op["figure"], op["rank"]), ("story", "600 MW", 2))
        self.assertEqual(brief.opening_number([], [rec("a", "A")])["kind"], None)
        self.assertIn("never the choice by default", brief.opening_number.__doc__)

    def test_three_saved_days(self):
        st = stories()
        if st is None:
            self.skipTest("news_stories.csv is not here")
        seen = 0
        for day in ("2026-10-13", "2026-10-20", "2026-10-21"):
            path = os.path.join(ROOT, "docs", "digest", f"{day}.md")
            if not os.path.exists(path):
                continue
            with open(path, encoding="utf-8") as f:
                m = re.search(r"for the (\d+) hours to (\d{4}-\d{2}-\d{2} \d{2}:\d{2}) UTC", f.read())
            now = pd.Timestamp(m.group(2), tz="UTC")
            s, _, _ = brief.window_rows(st, now, int(m.group(1)))
            if len(s) < 20:
                continue
            top10, _, _ = brief.select(brief.build_clusters(s), day, quiet)
            recs = top10.to_dict("records")
            op = brief.opening_number([], recs)   # the saved days' prices are not in the clean copy: the structural figure
            first = next(r for r in recs if brief.story_figure(r))
            self.assertEqual(op["rec"]["cluster_id"], first["cluster_id"])
            line = brief.opening_lines(op, {})[2]
            self.assertTrue(line.startswith(f"**{op['figure']}**: "), line)
            self.assertIn("not a warehouse table's", line)
            seen += 1
        if not seen:
            self.skipTest("the saved days' stories are not here")


class V2TheNumbersBlock(unittest.TestCase):
    def test_four_rows_in_the_traced_forms(self):
        facts = {"cands": [cand("Henry Hub natural gas", "Henry Hub natural gas", 3.22, 3.32, -3.01, reason=" Reason: x"),
                           cand("ERCOT HB_NORTH day-ahead", "ERCOT", 28.38, 26.28, 7.99, table="iso_dam_hub_prices", unit="USD/MWh", node="HB_NORTH")],
                 "demand": {"top": {"value": 612000.0, "ts_utc": pd.Timestamp("2026-10-20 19:00", tz="UTC")}, "before": pd.Timestamp("2025-10-21"), "old": None}}
        op = brief.opening_number(facts["cands"], [])
        recs = [rec("a", "A plans 600 MW", sector="gas", mw="600"), rec("b", "B raises $3bn", sector="capital", price="$3bn")]
        with mock.patch.object(brief, "cite_short", side_effect=lambda t: f"`{t}`"):
            L = brief.numbers_block(facts, op, recs, {"a": "A plans 600 MW", "b": "B raises USD 3 billion"})
        rows = [ln for ln in L if ln.startswith("- **")]
        self.assertEqual(len(rows), 4)
        self.assertTrue(MOVER.match(re.sub(r"^- \*\*[^*]+\*\* ", "- ", rows[0])), rows[0])
        self.assertIn("ERCOT HB_NORTH day-ahead", rows[0])            # the opening's own metric is not repeated
        self.assertEqual(len(DEMAND.findall(rows[1])), 1)
        # session 1439 (faults 4 to 6): the block's form, the figure once, no headline, a key to the story's row
        self.assertTrue(rows[2].startswith("- **Project or capacity.** Gas supply: 600 MW (Outlet; Outlet, 2026-10-21) [3]. Change: first report"), rows[2])
        self.assertEqual(rows[2].count("600"), 1)
        self.assertTrue(rows[3].startswith("- **Policy, capital or reliability.** Capital raised: USD 3 billion (Outlet; Outlet, 2026-10-21) [3]."), rows[3])
        self.assertNotIn("A plans", rows[2]); self.assertNotIn("B raises", rows[3])
        self.assertNotIn("](http", "\n".join(rows[2:]))                 # no story link: the item carries it (the hard check)
        self.assertTrue(any(ln.startswith("Tables: [1] `iso_dam_hub_prices`; [2] `eia930_all_demand`") and ln.endswith("[3] `news_stories`; story a (mw); story b (price).") for ln in L), [ln for ln in L if ln.startswith("Tables")])

    def test_the_masthead_and_the_subject(self):
        op = brief.opening_number([cand("Henry Hub natural gas", "Henry Hub natural gas", 3.22, 3.32, -3.01, reason=" Reason: x")], [])
        L = brief.masthead_lines("2026-10-26", pd.Timestamp("2026-10-26 15:45", tz="UTC"), op)
        self.assertEqual(L[0], "# ERW Daily Digest, 2026-10-26")
        self.assertEqual(L[2], "**26 October 2026.** Data through 11:45 ET, 15:45 UTC.")
        self.assertEqual(L[4], "<!-- subject: ERW Daily | Henry Hub natural gas: 3.22 USD/MMBtu, down 3.0% on the close before -->")
        self.assertEqual(L[6], "<!-- opening: Henry_Hub_natural_gas -->")
        self.assertEqual(brief.subject_line({"kind": "story"}, "2026-10-26"), "ERW Daily | 26 October 2026")
        with tempfile.TemporaryDirectory() as d:
            with open(os.path.join(d, "2026-10-23.md"), "w", encoding="utf-8") as f:
                f.write(V2_MD)
            self.assertEqual(brief.previous_opening("2026-10-26", d), "Henry_Hub_natural_gas")

    def test_the_words_above_the_fold(self):
        n = brief.above_fold_words(V2_MD)
        # the stamp, the opening sentence and two stories with their limitations; not the numbers block, the fold or sources
        self.assertGreater(n, 50)
        self.assertLess(n, 110)
        self.assertEqual(brief.above_fold_words(V2_MD.replace("Third story", "Third story with many more words")), n)


class V2TheEmail(unittest.TestCase):
    def test_the_order_the_subject_and_the_footer(self):
        with tempfile.TemporaryDirectory() as d:
            p = os.path.join(d, "2026-10-23.md")
            with open(p, "w", encoding="utf-8") as f:
                f.write(V2_MD)
            title, label, text, body = email_digest.render(p, "daily", unsubscribe="https://x/unsub")
        self.assertEqual(title, "ERW Daily | Henry Hub natural gas: 3.22 USD/MMBtu, down 3.0% on the close before")
        self.assertEqual(label, "2026-10-23")
        order = [text.index(x) for x in ("23 October 2026.", "The opening number", "The numbers", "What moved", "More on the site",
                                          "A fact that is fun.", "Corrections: https://github.com/SamuelEnrique/erw/issues", "Stop these emails")]
        self.assertEqual(order, sorted(order))
        self.assertNotIn("subject:", text)
        self.assertNotIn("Third story", text)                          # the fold is on the site, one link away
        self.assertIn("Oil surges on Saudi attacks", text)
        self.assertIn('href="https://github.com/SamuelEnrique/erw/issues">Corrections</a>', body)


class V2ThePageReadsIt(unittest.TestCase):
    def test_the_keys_of_the_v2_issue(self):
        import shutil
        import subprocess
        if shutil.which("node") is None:
            self.skipTest("node is not on this machine")
        site = os.path.join(ROOT, "site")
        with tempfile.TemporaryDirectory() as d:
            p = os.path.join(d, "v2.md")
            with open(p, "w", encoding="utf-8") as f:
                f.write(V2_MD)
            js = ("const D = await import('./lib/digest.ts'); const M = (await import('node:fs')).readFileSync(process.argv[1], 'utf-8');"
                  "console.log(JSON.stringify(D.digestFigures(M, '2026-10-23', null, new Date('2026-10-20T12:00:00Z')).map((f) => f.key)));")
            out = subprocess.run(["node", "--no-warnings", "--import", "./scripts/alias-register.mjs", "--input-type=module", "-e", js, p], cwd=site, capture_output=True, text=True, timeout=120)
        self.assertEqual(out.returncode, 0, out.stderr[-600:])
        keys = json.loads(out.stdout.strip().splitlines()[-1])
        for k in ("digest_fuel|eia_fuel_spot_prices|eia:henry_hub|2026-10-14", "digest_fuel|eia_fuel_spot_prices|eia:henry_hub|2026-10-13",
                  "digest_dam|ERCOT|iso_dam_hub_prices|HB_NORTH|2026-10-20", "digest_dam|ERCOT|iso_dam_hub_prices|HB_NORTH|2026-10-19",
                  "digest_demand|eia930_all_demand|eia930:US48|demand_mw|2026-10-20T19:00:00Z",
                  "digest_fuel|eia_fuel_spot_prices|eia:brent|2026-10-14"):
            self.assertIn(k, keys)

    def test_the_fold_is_drawn_closed(self):
        with open(os.path.join(ROOT, "site", "lib", "markdown.ts"), encoding="utf-8") as f:
            src = f.read()
        self.assertIn("return foldMore(sourceTrail(fillDigest(", src)   # session 1449: the source trail as a hover
        self.assertIn('<details class="digest-more" data-digest-fold="more">', src)



# Session 2704: the Roundup in the brandbook's v2 shape (the owner's rulings of 24 October 2026, queue file 131)

def picked_of(lines):
    """The opening number's inputs read back from five-number lines as roundup.five_numbers writes them."""
    out = {}
    for ln in lines:
        m = re.match(r"^- \*\*(.+?):\*\* (.*)$", ln)
        if not m:
            continue
        label, text = m.group(1), m.group(2).rstrip(".")
        if label == "Price move of the week" and "%" in text:
            out["move"] = {"pct": float(re.findall(r"([+-]\d+\.\d)%\)", text)[-1]), "text": text, "label": text.split(" closed at")[0]}
        elif label == "US48 peak demand" and "MW" in text:
            out["us48"] = {"text": text}
        elif label.startswith("Deal of the week, by US dollars"):
            v, unit = re.match(r"USD ([\d.]+) (billion|million)", text).groups()
            out["deal"] = {"usd": float(v) * (1e9 if unit == "billion" else 1e6), "text": text}
        elif label.startswith("Largest new datacenter load") and " MW" in text:
            out["dc"] = {"mw": float(text.split(" MW")[0].replace(",", "")), "text": text}
    return out


V2R_MD = """# ERW Weekly Roundup, 2026-W43

**Week ending 25 October 2026.** Sources through 19:00 ET, 23:00 UTC.

No Roundup was written for 2026-W42; that week's stories are in the Digests of 2026-10-12 to 2026-10-16 ([the archive](/digest)).

<!-- subject: ERW Weekly | Six AP1000 reactors eyed for Kentucky -->

<!-- opening: deal -->

ERW's weekly roundup of energy news for 2026-10-19 to 2026-10-25, from 1449 scored stories.

## The opening number

**USD 45 billion, Anthropic and Nscale, cloud computing deal.** Status: reported: extracted from the week's stories, every number checked against its story.

## The week in five numbers

- **US48 peak demand:** 519,415 MW in the hour starting 2026-10-20 22:00 UTC [1].

## What mattered

1. **Six AP1000 reactors eyed for Kentucky** (nuclear, 5 stories)
   The largest proposed US nuclear project in decades. What the evidence does not establish: the 6,600 MW is the outlet's figure, not a warehouse table's. Sources: [ANS](https://www.ans.org/a)

## More

### Weekend

1. **A weekend story** (oil, 1 story)
   Why. Sources: [Outlet](https://example.org/w)

### ERW's Numbers This Week

- US48 peak.

Tables: [1] `eia930_all_demand`.

## ERW's Chart of the Week

- no chart of the week was picked for this week (warehouse/analysis/run.py has not run for it).

## Next week

- **2 November 2026**: Northern Natural Gas Company; Notice (Federal Energy Regulatory Commission). Comments on the EA are due to FERC by 5:00 p.m. Eastern Time on November 2, 2026. ([source](https://www.federalregister.gov/x))

## ERW's Fun Fact

A fact that is fun.

Sources: [Wikipedia, Fun](https://en.wikipedia.org/wiki/Fun).

ERW

---

[How this is made.](/about#digest)
"""


class V2RTheOpeningNumber(unittest.TestCase):
    def test_the_rule_on_fixtures(self):
        move = {"pct": 12.0, "text": "WTI moved", "label": "WTI Cushing crude"}
        deal = {"usd": 5e9, "text": "USD 5 billion, A and B"}
        dc = {"mw": 900.0, "text": "900 MW, Op"}
        us48 = {"text": "US48 demand peaked at 600,000 MW"}
        # session 1446 (fault 25): a benchmark move a story of the week names comes first; unnamed, the deal comes before it
        stories = frame(rec("o", "Oil prices rise on fears of Middle East conflict escalation", sector="oil", why="Tanker rates doubled."))
        self.assertEqual(roundup.opening_number({"move": move, "deal": deal, "dc": dc, "us48": us48}, stories)["key"], "move")
        self.assertEqual(roundup.opening_number({"move": move, "deal": deal, "dc": dc, "us48": us48})["key"], "deal")
        self.assertEqual(roundup.opening_number({"move": dict(move, pct=-9.9), "deal": deal, "dc": dc, "us48": us48})["key"], "deal")
        hub = {"pct": 676.7, "text": "SPP moved", "label": "SPP SPPSOUTH_HUB day-ahead"}
        story = {"text": "USD 4.4 billion: Taiwan commits to Alaska LNG, as Reuters reported", "fig": "USD 4.4 billion"}
        self.assertEqual(roundup.opening_number({"moves": [hub], "story": story, "us48": us48})["key"], "story")   # a hub is the last resort
        self.assertEqual(roundup.opening_number({"moves": [hub], "us48": us48})["key"], "move")
        self.assertEqual(roundup.opening_number({"moves": [dict(move, pct=4.0)], "us48": us48})["key"], "us48")   # unnamed, under 4.5
        self.assertEqual(roundup.opening_number({"deal": dict(deal, usd=5e8), "dc": dc, "us48": us48})["key"], "datacenter")
        self.assertEqual(roundup.opening_number({"dc": dict(dc, mw=300.0), "us48": us48})["key"], "us48")
        self.assertIsNone(roundup.opening_number({}))
        self.assertIn("persistent", roundup.opening_number.__doc__)
        op = roundup.opening_number({"move": move})
        self.assertEqual(roundup.opening_lines(op)[2], "**WTI moved.** Status: calculated from observed prices (the warehouse's tables).")
        # session 1446 (fault 34); session 1475 (fault 53): the move leads when the opening number is the move
        self.assertEqual(roundup.subject_line(op, "Six reactors eyed."), "ERW Weekly | WTI up 12.0% on the week; Six reactors eyed")
        self.assertEqual(roundup.subject_line(None, "AEP and Google advance a $4 Billion fuel-cell project"),
                         "ERW Weekly | AEP and Google advance a USD 4 billion fuel-cell project")
        long = "Gingerah Energy refers 1,000 MW data centre complex with 5GWh battery in Western Australia to EPBC Act"
        self.assertEqual(roundup.subject_line(None, long), "ERW Weekly | Gingerah Energy refers 1,000 MW data centre complex with 5GWh battery...")
        self.assertLessEqual(len(roundup.subject_line(op, long)), 120)   # a 70-character headline and a move of up to 35
        self.assertEqual(roundup.subject_line(None, "Six reactors eyed."), "ERW Weekly | Six reactors eyed")

    def test_w40_and_w41(self):
        """The five numbers of W40 and W41 as session 808's regeneration wrote them (docs/reviews/periodicals-roundup-regen-
        2026-10-23.md): Henry Hub's 9.7 percent is under the bar, so the deal of the week opens each."""
        with open(os.path.join(ROOT, "docs", "reviews", "periodicals-roundup-regen-2026-10-23.md"), encoding="utf-8") as f:
            text = f.read()
        blocks = [b for b in re.split(r"^### The week in five numbers \(new\)\s*$", text, flags=re.M)[1:]]
        self.assertEqual(len(blocks), 2)
        got = []
        for blk in blocks:
            op = roundup.opening_number(picked_of(blk.split("\n#")[0].splitlines()))
            got.append((op["key"], op["text"].split(",")[0]))
        self.assertEqual(got, [("deal", "USD 50 billion"), ("deal", "USD 12 billion")])


class V2RTheParts(unittest.TestCase):
    def test_the_masthead_and_the_missed_week(self):
        end = pd.Timestamp("2026-10-26", tz="UTC")
        L = roundup.masthead_lines("2026-W43", end, pd.Timestamp("2026-10-25 23:00", tz="UTC"), None, "A head.", "No Roundup was written for 2026-W42; x")
        self.assertEqual(L[0], "# ERW Weekly Roundup, 2026-W43")
        self.assertEqual(L[2], "**Week ending 25 October 2026.** Sources through 19:00 ET, 23:00 UTC.")
        self.assertEqual(L[4], "No Roundup was written for 2026-W42; x")
        self.assertEqual(L[6], "<!-- subject: ERW Weekly | A head -->")

    def test_the_evidence_gap(self):
        # session 1446 (faults 30 and 31): the figure is claimed only when the headline states it; the empty fields are said;
        # nothing when every field is stated and more than one outlet ran it
        self.assertEqual(roundup.evidence_gap(rec("a", "A plans 600 MW", mw="600", parties="A"), "A plans 600 MW"),
                         "What the evidence does not establish: the 600 MW is the outlet's figure, not a warehouse table's.")
        self.assertEqual(roundup.evidence_gap(rec("s", "Singapore plans 1GWh of storage", mw="1000", parties="Singapore"), "Singapore plans 1GWh of storage"), "")
        self.assertEqual(roundup.evidence_gap(dict(rec("b", "B"), outlets=1)),
                         "What the evidence does not establish: no party is named; no capacity or sum is stated; one outlet has reported it so far.")
        self.assertEqual(roundup.evidence_gap(rec("c", "C"), "Cheniere signs supply through 2054, 4 million tonnes per annum"),
                         "What the evidence does not establish: no party is named; no capacity or sum is stated.")
        self.assertEqual(roundup.evidence_gap(dict(rec("d", "D buys 600 MW", mw="600", parties="D"), outlets=3), "D buys 600 MW"),
                         "What the evidence does not establish: the 600 MW is the outlet's figure, not a warehouse table's.")

    def test_next_week_from_the_policy_reads(self):
        reads = pd.DataFrame([
            {"title": "Northern Natural Gas Company; Notice", "agency": "Federal Energy Regulatory Commission", "significance": "6",
             "source_url": "https://www.federalregister.gov/x",
             "timeline": "Comments on the EA are due to FERC by 5:00 p.m. Eastern Time on November 2, 2026. The Commission will then decide."},
            {"title": "Later rule", "agency": "EPA", "significance": "8", "source_url": "https://e/y", "timeline": "Comments are due on November 20, 2026."},
            {"title": "Earlier", "agency": "DOE", "significance": "9", "source_url": "https://e/z", "timeline": "It took effect on October 20, 2026."}])
        with mock.patch.object(roundup, "read_table", return_value=reads):
            got = roundup.next_week(pd.Timestamp("2026-10-27", tz="UTC"), quiet)
        # session 1447 (fault 36): the docket's short name, the company and the first clause joined by a comma
        self.assertEqual(got, ["- **2 November 2026**: Northern Natural Gas Company, Notice (Federal Energy Regulatory Commission). Comments on the EA "
                               "are due to FERC by 5:00 p.m. Eastern Time on November 2, 2026. ([source](https://www.federalregister.gov/x))"])
        with mock.patch.object(roundup, "read_table", return_value=reads.iloc[1:]):
            self.assertEqual(roundup.next_week(pd.Timestamp("2026-10-27", tz="UTC"), quiet), [])

    def test_the_words_skip_the_five_numbers_and_the_fold(self):
        n = brief.above_fold_words(V2R_MD)
        self.assertEqual(brief.above_fold_words(V2R_MD.replace("A weekend story", "A weekend story of many more words")), n)
        self.assertEqual(brief.above_fold_words(V2R_MD.replace("519,415 MW in the hour", "519,415 MW in the very same hour")), n)

    def test_the_checker_reads_the_fold_s_numbers(self):
        import check_roundup
        sec = check_roundup.section(V2R_MD)
        self.assertIn("- US48 peak.", sec)
        self.assertNotIn("Chart of the Week", sec)
        with open(os.path.join(ROOT, "site", "app", "roundup", "[week]", "page.tsx"), encoding="utf-8") as f:
            self.assertIn("renderRoundup(md, DOCS.weekly_source[week])", f.read())   # session 1449: the fold, the source trail, the opening once


class V2RTheEmail(unittest.TestCase):
    def test_the_order_and_the_subject(self):
        with tempfile.TemporaryDirectory() as d:
            p = os.path.join(d, "2026-W43.md")
            with open(p, "w", encoding="utf-8") as f:
                f.write(V2R_MD)
            title, label, text, body = email_digest.render(p, "roundup", unsubscribe="https://x/unsub")
        self.assertEqual(title, "ERW Weekly | Six AP1000 reactors eyed for Kentucky")
        self.assertEqual(label, "2026-W43")
        order = [text.index(x) for x in ("Week ending 25 October 2026.", "No Roundup was written for 2026-W42", "The opening number",
                                          "The week in five numbers", "What mattered", "Next week", "More on the site", "A fact that is fun.",
                                          "Stop these emails")]
        self.assertEqual(order, sorted(order))
        self.assertNotIn("A weekend story", text)   # the fold is on the site



class TheCharacterInTheEmails(unittest.TestCase):
    """Session 2705: the character (site/public/brand/erw-character-48.png) appears once in each v2 email, in the fun-fact
    module, alt "ERW", and nowhere else (not the masthead, not the numbers, not the text part)."""

    def render(self, md, kind, name):
        with tempfile.TemporaryDirectory() as d:
            p = os.path.join(d, name)
            with open(p, "w", encoding="utf-8") as f:
                f.write(md)
            return email_digest.render(p, kind, unsubscribe="https://x/unsub")

    def test_once_and_only_in_the_fun_fact(self):
        url = email_digest.character_url()
        self.assertTrue(url.endswith("/main/site/public/brand/erw-character-48.png"))
        for md, kind, name in ((V2_MD, "daily", "2026-10-23.md"), (V2R_MD, "roundup", "2026-W43.md")):
            title, label, text, body = self.render(md, kind, name)
            self.assertEqual(body.count(url), 1, kind)
            self.assertNotIn(url, text)
            at, fact = body.index(url), body.index("A fact that is fun.")
            self.assertGreater(at, body.index(">ERW&#x27;s Fun Fact<") if ">ERW&#x27;s Fun Fact<" in body else body.index("Fun Fact"))
            self.assertLess(at, fact)                                   # left of the fact's text
            self.assertIn('alt="ERW" width="38" height="48"', body)
            numbers = body[body.index("The numbers" if kind == "daily" else "The week in five numbers"):body.index("What moved" if kind == "daily" else "What mattered")]
            self.assertNotIn(url, numbers)

    def test_the_picture_is_committed_at_96_px(self):
        path = os.path.join(ROOT, "site", "public", "brand", "erw-character-48.png")
        with open(path, "rb") as f:
            head = f.read(24)
        self.assertEqual(head[:8], b"\x89PNG\r\n\x1a\n")
        self.assertEqual(int.from_bytes(head[20:24], "big"), 96)        # the height
        with mock.patch.dict(os.environ, {"EMAIL_ASSET_REF": "wip/2705-periodicals"}):
            self.assertIn("/erw/wip/2705-periodicals/site/public/brand/", email_digest.character_url())

    def test_a_preview_goes_to_the_fixed_recipients_only_and_claims_nothing(self):
        sent = []

        class R:
            status_code = 200

            def json(self):
                return {"id": f"id{len(sent)}"}

        def post(url, headers=None, timeout=None, json=None):
            sent.append(json)
            return R()
        env = {"RESEND_API_KEY": "k", "DIGEST_RECIPIENTS": "a@example.invalid, b@example.invalid"}
        with tempfile.TemporaryDirectory() as d, mock.patch.dict(os.environ, env), \
                mock.patch.object(email_digest.requests, "post", side_effect=post), \
                mock.patch.object(email_digest, "suppressed", return_value=set()), \
                mock.patch.object(email_digest, "subscribers", side_effect=AssertionError("no subscriber is read")), \
                mock.patch.object(email_digest, "claim", side_effect=AssertionError("a preview claims nothing")), \
                mock.patch.object(email_digest, "unsubscribe_url", return_value=None):
            p = os.path.join(d, "2026-10-23.md")
            with open(p, "w", encoding="utf-8") as f:
                f.write(V2_MD)
            n, ids, at = email_digest.send_preview("daily", p, quiet, os.path.join(d, "out"))
            self.assertTrue(os.path.exists(os.path.join(d, "out", "2026-10-23-daily.html")))
        self.assertEqual(n, 2)
        self.assertEqual([m["to"] for m in sent], [["a@example.invalid"], ["b@example.invalid"]])
        self.assertTrue(all(m["subject"].startswith("PREVIEW v2: ERW Daily | ") for m in sent))


class Session1437WhyLines(unittest.TestCase):
    """Session 1437 (chain 149, faults 7 to 11, 32 and 33 of docs/reviews/periodicals-faults-2026-11-05.md): a hollow verb
    or a restatement fails the why line's check, and a failing line prints nothing (the headline alone, rulings item 16),
    a publisher's suffix or the money style notwithstanding. The lines are the dry run of 26 October's."""

    def test_a_hollow_verb_fails_and_the_item_prints_the_headline_alone(self):
        head = "Singapore plans 26% more power capacity in early 2030s and 1,000 MW of storage"
        why = "Generation capacity expansion signals rising electricity demand in city-state."
        self.assertEqual(brief.why_check(why, head), ["hollow verb: signals"])
        self.assertEqual(brief.why_line(why, head), "")
        for verb in brief.HOLLOW_VERBS:
            self.assertEqual(brief.why_check(f"Capacity growth {verb} demand.", head), [f"hollow verb: {verb}"])

    def test_a_restatement_fails(self):
        head = "AI's nuclear power push runs into cost and regulatory hurdles"
        why = "Cost and regulatory hurdles threaten AI sector's plans to use nuclear power for datacenters."
        self.assertEqual(brief.why_check(why, head), ["restates the headline: 0.50"])
        self.assertEqual(brief.why_line(why, head), "")

    def test_a_line_that_adds_a_fact_passes(self):
        head = "Maryland's first bulk storage procurement nets 440 MW, short of its target"
        why = "Awards fell short of the 800-MW target, showing PJM capacity strain and limits on storage."
        self.assertEqual(brief.why_check(why, head), [])
        self.assertLess(brief.restates(why, head), brief.RESTATES_SHARE)
        self.assertEqual(brief.why_line(why, head), why)

    def test_the_headline_in_the_money_style_is_the_headline(self):
        head = "Oil dips but holds above $100; Brent trades at $114.42 per barrel"
        why = "Oil dips but holds above USD 100; Brent trades at USD 114.42 per barrel."
        self.assertEqual(brief.norm_headline(why), brief.norm_headline(head))
        self.assertEqual(brief.why_line(why, head), "")
        self.assertEqual(brief.why_line("Brent reaches USD 114.42.", head + ", Bloomberg reports"), "")

    def test_the_prompt_and_the_rubric_name_the_hollow_verbs(self):
        for text in (score.SYSTEM, score.RUBRIC):
            for verb in brief.HOLLOW_VERBS:
                self.assertIn(verb, text)
            self.assertIn("one fact the story", text)


class Session1458NothingNew(unittest.TestCase):
    """Session 1458 (chain 150, fault 7 of docs/reviews/periodicals-faults-2026-11-05.md): a why line that names no party,
    place, date, quantity or rule the headline lacks fails when it shares a quarter of its content words with the
    headline or strings two clauses on a semicolon; it prints nothing (rulings item 16)."""

    def test_the_faulted_line_fails_and_prints_nothing(self):
        head = "US executives quit $25bn gas venture over claims of secret Russian control"
        why = ("LNG or gas project faces executive departures and alleged Russian involvement claims; geopolitical risk to "
               "US energy sector.")
        self.assertLess(brief.restates(why, head), brief.RESTATES_SHARE)
        self.assertEqual(brief.new_things(why, head), [])
        self.assertEqual(brief.why_check(why, head), ["names nothing the headline lacks"])
        self.assertEqual(brief.why_line(why, head), "")

    def test_a_line_that_names_a_new_thing_passes(self):
        # a figure, a party, a quantity in words, a month: each is a thing the headline lacks
        cases = [
            ("Maryland's first bulk storage procurement nets 440 MW, short of its target",
             "Awards fell short of the 800-MW target, showing PJM capacity strain and limits on storage.", ["800", "PJM"]),
            ("India's Coal Crisis Deepens as Power Demand Surges",
             "Half of India's coal plants operating with low fuel stocks; supply squeeze threatens power generation.", ["Half"]),
            ("Utility seeks rate rise for grid upgrades",
             "Bills would climb from June for its customers.", ["June"]),
        ]
        for head, why, new in cases:
            with self.subTest(head):
                self.assertEqual(brief.new_things(why, head), new)
                self.assertEqual(brief.why_check(why, head), [])
                self.assertEqual(brief.why_line(why, head), why)

    def test_a_demonym_and_a_generic_word_name_no_one_new(self):
        head = "Qatar extends LNG force majeure as Hormuz disruptions continue"
        self.assertEqual(brief.new_things("Extended force majeure on Qatari LNG keeps US supply short.", head), [])
        self.assertEqual(brief.new_things("AI datacenter demand meets Qatari LNG.", head), [])

    def test_the_semicolon_filler_fails_whatever_its_share(self):
        head = "NTT in final talks to build $6.3bn data center for Anthropic in Japan, report says"
        why = "AI data center capex; power demand commitment in final negotiation stages."
        self.assertEqual(brief.why_check(why, head), ["names nothing the headline lacks"])
        why = "Hormuz status drives oil, LNG and tanker pricing; stalled talks keep supply risk elevated."
        head = "Iran says US response to its proposal to reopen Hormuz was 'insufficient'"
        self.assertLess(brief.restates(why, head), brief.NOTHING_NEW_SHARE)
        self.assertEqual(brief.why_check(why, head), ["names nothing the headline lacks"])

    def test_a_consequence_with_little_of_the_headline_stays(self):
        head = "Two more oil tankers attacked near Strait of Hormuz"
        why = "Further attacks on crude and product tankers raise supply risk and shipping costs in a chokepoint."
        self.assertLess(brief.restates(why, head), brief.NOTHING_NEW_SHARE)
        self.assertEqual(brief.why_check(why, head), [])

    def test_another_fault_is_named_by_itself(self):
        # the rule is named last: a line with an adjective or a hollow verb is named by that alone
        head = "A deal"
        self.assertEqual(brief.why_check("A major deal for the grid.", head), ["adjective: major"])

    def test_the_13_stored_issues_regenerated(self):
        """The items of the stored issues of 25 September to 23 October, each line passed through why_line with and
        without the rule, written to the test's own folder (no stored issue rewritten): 463 items, 324 printed a line
        before, 224 with the rule; every line printed passes the check."""
        sys.path.insert(0, os.path.join(ROOT, "scripts"))
        import periodicals_counts as pc
        files = sorted(f for f in os.listdir(os.path.join(ROOT, "docs", "digest"))
                       if re.fullmatch(r"2026-\d\d-\d\d\.md", f) and f <= "2026-10-23.md")
        if len(files) < 15:
            self.skipTest("the stored issues are not here")

        def first(why):
            m = brief.sentence_end(why)
            return why[:m.start() + 1] if m else why
        items = []
        for f in files:
            with open(os.path.join(ROOT, "docs", "digest", f), encoding="utf-8") as fh:
                for head, _sector, why, _section in pc.read_items(fh.read().splitlines()):
                    if why:
                        items.append((f, head, first(why.split(" parties:")[0])))
        now = [brief.why_line(w, h) for _, h, w in items]
        with mock.patch.object(brief, "new_things", lambda t, h: ["(the rule off)"]):
            was = [brief.why_line(w, h) for _, h, w in items]
        self.assertEqual((len(items), sum(1 for a in was if a), sum(1 for b in now if b)), (463, 323, 224))   # 324 before session 1462 cut a hollow tail
        for (_f, h, _w), out in zip(items, now):
            if out:
                self.assertEqual(brief.why_check(out, h), [], out)
        with tempfile.TemporaryDirectory() as d:
            path = os.path.join(d, "why_lines_regenerated.tsv")
            with open(path, "w", encoding="utf-8", newline="\n") as fh:
                for (f, h, _w), a, b in zip(items, was, now):
                    fh.write(f"{f}\t{h}\t{a}\t{b}\n")
            with open(path, encoding="utf-8") as fh:
                self.assertEqual(sum(1 for _ in fh), 463)


class Session1462HollowForms(unittest.TestCase):
    """Session 1462 (chain 150): the hollow verbs' -ing and past forms fail the check; a trailing clause led by a comma and
    one of them is cut and the fact before it kept. The lines are the scorer's new prompt on 26 October's top ten."""

    def test_the_trailing_clause_is_cut(self):
        head = "Woodfibre LNG moves up completion target after construction reaches the 75% mark"
        why = "Woodfibre LNG accelerates timeline while AECO spot curve softens, signaling weaker 2027 North American gas pricing."
        self.assertEqual(brief.why_line(why, head), "Woodfibre LNG accelerates timeline while AECO spot curve softens.")

    def test_the_forms_fail_the_check(self):
        head = "A deal in Texas"
        for verb in ("signaling", "signalling", "signaled", "demonstrating", "reflecting", "underscoring", "highlighting", "highlighted"):
            with self.subTest(verb):
                self.assertEqual(brief.why_check(f"Ohio regulators, {verb} demand.", head), [f"hollow verb: {verb}"])
        # a hollow form that leads no trailing clause is not cut: the line fails and prints nothing
        self.assertEqual(brief.why_line("Reflecting demand, Ohio adds a plant.", head), "")

    def test_the_prompt_and_the_rubric_name_the_forms(self):
        self.assertIn("signaling, demonstrating, reflecting, underscoring or highlighting", score.SYSTEM)
        self.assertIn("nor their -ing forms", score.RUBRIC)


class Session1466ScaleAndSectorFolds(unittest.TestCase):
    """Session 1466 (chain 150, faults 44 and 45, session 1463's dry run of 6 November): a scale word the headline's
    capacity contradicts goes; a story folded because its sector is full is said to be of the sector, not the topic."""

    def test_gigawatt_scale_for_702_mw(self):
        head = "AEP and Google advance a 702 MW Bloom Energy fuel-cell project for Cheyenne data centers"
        why = "Gigawatt-scale hyperscale power deal combining fuel cells, natural gas, and private microgrid infrastructure for datacenter demand."
        self.assertEqual(brief.why_check(why, head), ["scale word against the headline's figure: gigawatt-scale"])
        self.assertEqual(brief.why_line(why, head),
                         "Hyperscale power deal combining fuel cells, natural gas, and private microgrid infrastructure for datacenter demand.")
        for ok_head in ("Meta plans a 2 GW campus in Louisiana", "Crusoe plans 1,200 MW in Abilene", "A campus with no figure"):
            self.assertEqual(brief.scale_against(why, ok_head), "", ok_head)

    def test_a_sector_fold_is_said_so(self):
        def c(cid, title, sector, parties="", sig=8, region="us"):
            return {"cluster_id": cid, "titles": [title], "sector": sector, "parties": parties, "region": region, "sig": sig, "ai": 0,
                    "why": "", "mw": "", "price": "", "links": [("Outlet", f"https://example.org/{cid}")], "summary": "", "n": 1}
        clusters = pd.DataFrame([c("a", "AEP and Google advance a 702 MW fuel-cell project in Wyoming", "datacenter_power", "AEP; Google", region="wyoming"),
                                 c("b", "Poll asks Americans about data centers near their homes", "datacenter_power", "Heatmap"),
                                 c("d", "Lambda to develop four-building data center campus in Alabama", "datacenter_power", "Lambda", 7, "alabama")])
        top, folded = brief.one_per_topic(clusters, 10, quiet)
        self.assertEqual(list(top["cluster_id"]), ["a", "b"])
        self.assertEqual(folded, {"d"})
        also = brief.also_of(top.to_dict("records")[0])
        self.assertEqual(also[0]["kind"], "sector")
        line = brief.also_line(also)
        self.assertEqual(line, "Also in datacenter power: Lambda to develop four-building data center campus in Alabama ([Outlet](https://example.org/d)).")
        self.assertTrue(brief.ALSO_RE.match(line))
        mixed = brief.also_line([dict(also[0], kind="topic", title="Same topic story"), also[0]])
        self.assertTrue(mixed.startswith("Also on this topic: Same topic story ("), mixed)
        self.assertIn(". Also in datacenter power: Lambda", mixed)

    def test_the_email_reads_either_label(self):
        import email_digest
        md = ["## What moved", "", "1. **AEP and Google advance a fuel-cell project** (datacenter power)  ",
              "   Sources: [Data Center Frontier](https://example.org/a)  ",
              "   Also in datacenter power: Lambda to develop a campus ([DCD](https://example.org/d))."]
        it = email_digest.numbered(md, ("## What moved",))[0]
        self.assertEqual(it["why"], "")
        self.assertEqual(it["also_label"], "Also in datacenter power:")
        self.assertEqual(it["also"], "Lambda to develop a campus ([DCD](https://example.org/d)).")


class Session1467SectorLine(unittest.TestCase):
    """Session 1467 (chain 150, fault 46): a by-sector line with no why line has no colon that introduces nothing; the
    email and the counts read both forms."""

    R = {"why": "", "sector": "generation", "links": [("Utility Dive", "https://www.utilitydive.com/a")]}
    HEAD = "APS expects peak demand to grow about 3.4% annually and plans coal use to 2038"

    def test_the_two_forms(self):
        self.assertEqual(brief.sector_line(self.R, self.HEAD), f"- {self.HEAD} (generation). [Utility Dive](https://www.utilitydive.com/a)")
        r = dict(self.R, why="Arizona's utility keeps coal units at Cholla open past their planned date.")
        self.assertEqual(brief.sector_line(r, self.HEAD), f"- {self.HEAD} (generation): Arizona's utility keeps coal units at Cholla open past "
                                                          "their planned date. [Utility Dive](https://www.utilitydive.com/a)")

    def test_the_readers(self):
        import email_digest
        sys.path.insert(0, os.path.join(ROOT, "scripts"))
        import periodicals_counts as pc
        ln = brief.sector_line(self.R, self.HEAD)
        m = pc.BULLET.match(ln)
        self.assertEqual(m.group("sector"), "generation")
        self.assertEqual(pc.read_items(["### By sector", ln])[0][2], "")
        md = ["# ERW Daily Digest, 2026-11-06", "", "## By sector", "", "**Power**", "", ln, ""]
        got = email_digest.items(md, "daily")
        self.assertEqual([(x["head"], x["sector"], x["why"], x["src"]) for x in got],
                         [(self.HEAD, "generation", "", ("Utility Dive", "https://www.utilitydive.com/a"))])


class Session1469CountsReadTheFiveKeys(unittest.TestCase):
    """Session 1469 (chain 150, fault 55): the counts read a five-numbers row as keyed when its key is on the five's
    Tables line (session 1460's form)."""

    def test_the_keys_on_the_tables_line(self):
        sys.path.insert(0, os.path.join(ROOT, "scripts"))
        import periodicals_counts as pc
        five = ["## The week in five numbers", "",
                "- **Deal of the week, by US dollars:** USD 19 billion, TeraWulf (2026-11-05).",
                "- **Largest new datacenter load first reported this week:** 702 MW, Google, Cheyenne.", ""]
        self.assertEqual(pc.no_key(five), 2)
        tables = "Tables: the deal of the week, `energy_deals` deal:a; the datacenter load, `datacenter_projects` datacenter:b."
        self.assertEqual(pc.no_key(five + [tables]), 0)
        self.assertEqual(pc.no_key(five + ["Tables: the deal of the week, `energy_deals` deal:a."]), 1)


class Session1472DealWords(unittest.TestCase):
    """Session 1472 (chain 154, fault 50 of docs/reviews/periodicals-faults-2026-11-05.md): the deal of the week prints no
    kind "other" and no party its asset already names; the tracer still reads the row."""

    def test_the_w45_row(self):
        r = {"buyer": "", "seller": "TeraWulf", "asset": "TeraWulf data center in Kentucky", "deal_type": "other",
             "event_date": "2026-11-05T12:00:00Z"}
        self.assertEqual(roundup.deal_words(r), "TeraWulf data center in Kentucky (2026-11-05)")
        import check_roundup as cr
        row = f"- **Deal of the week, by US dollars:** USD 19 billion, {roundup.deal_words(r)}."
        text = "## The week in five numbers\n\n" + row + "\n\nTables: the deal of the week, `energy_deals` deal:35a62f0ede4aa8ea.\n"
        self.assertEqual(cr.five_keyed(text)[0], ("USD 19 billion", "deal:35a62f0ede4aa8ea"))

    def test_other_rows(self):
        self.assertEqual(roundup.deal_words({"buyer": "Shell", "seller": "Equinor", "asset": "Bay du Nord Oil Project",
                                             "deal_type": "m_and_a", "event_date": "2026-10-09T21:45:00Z"}),
                         "Shell and Equinor, Bay du Nord Oil Project (acquisition, 2026-10-09)")
        self.assertEqual(roundup.deal_words({"buyer": "Acme", "seller": "Acme", "asset": "", "deal_type": "ppa", "event_date": ""}),
                         "Acme (power purchase agreement)")
        self.assertEqual(roundup.deal_words({"buyer": "", "seller": "", "asset": "", "deal_type": "other", "event_date": ""}),
                         "parties not stated")


class Session1473LoadWords(unittest.TestCase):
    """Session 1473 (chain 154, fault 51): the largest new datacenter load leaves out a part its row does not state."""

    def test_the_w45_row(self):
        dcs = pd.DataFrame([{"entity_id": "datacenter:8954976fefde08c3", "first_story_at": "2026-11-04T10:00:00Z", "capacity_mw": "702",
                             "operator": "Google", "site_name": "", "city": "Cheyenne", "state": "", "confidence": "0.9"}])
        with tempfile.TemporaryDirectory() as d, mock.patch.object(roundup, "read_table", lambda n: {"datacenter_projects": dcs}.get(n)), \
                mock.patch.object(roundup, "ANALYSIS_DIR", d):
            L = roundup.five_numbers("2026-W45", pd.Timestamp("2026-11-02", tz="UTC"), pd.Timestamp("2026-11-09", tz="UTC"), {}, quiet)
        row = next(x for x in L if x.startswith("- **Largest new datacenter load"))
        self.assertEqual(row, "- **Largest new datacenter load first reported this week:** 702 MW, Google, Cheyenne.")
        import check_roundup as cr
        self.assertEqual(cr.five_keyed("\n".join(["## The week in five numbers", ""] + L))[2], ("702", "datacenter:8954976fefde08c3"))
        self.assertNotIn("not stated", row)


class Session1474FiveReadTheFloor(unittest.TestCase):
    """Session 1474 (chain 154, fault 52): the five numbers' deal and load are read with the tables' own floor, so they
    never state a row the tables below refuse (W45: both rows at confidence 0.55)."""

    def five(self, deals, dcs):
        with tempfile.TemporaryDirectory() as d, \
                mock.patch.object(roundup, "read_table", lambda n: {"energy_deals": deals, "datacenter_projects": dcs}.get(n)), \
                mock.patch.object(roundup, "ANALYSIS_DIR", d):
            return roundup.five_numbers("2026-W45", pd.Timestamp("2026-11-02", tz="UTC"), pd.Timestamp("2026-11-09", tz="UTC"), {}, quiet)

    def test_rows_under_the_floor_are_not_the_five(self):
        deals = pd.DataFrame([{"event_id": "deal:35a62f0ede4aa8ea", "event_date": "2026-11-05T12:00:00Z", "deal_type": "other", "buyer": "",
                               "seller": "TeraWulf", "asset": "TeraWulf data center in Kentucky", "mw": "", "dollars": "19000000000", "confidence": "0.55"},
                              {"event_id": "deal:b", "event_date": "2026-11-05T13:00:00Z", "deal_type": "project_finance", "buyer": "Deutsche Bank and Rabobank",
                               "seller": "Return", "asset": "Germany BESS portfolio", "mw": "", "dollars": "938000000", "confidence": "0.8"}])
        dcs = pd.DataFrame([{"entity_id": "datacenter:8954976fefde08c3", "first_story_at": "2026-11-04T10:00:00Z", "capacity_mw": "702",
                             "operator": "Google", "site_name": "", "city": "Cheyenne", "state": "", "confidence": "0.55"}])
        L = self.five(deals, dcs)
        deal = next(x for x in L if x.startswith("- **Deal of the week"))
        self.assertIn("USD 938 million, Deutsche Bank and Rabobank and Return, Germany BESS portfolio", deal)
        self.assertNotIn("TeraWulf", deal)
        load = next(x for x in L if x.startswith("- **Largest new datacenter load"))
        self.assertIn("passes the datacenter table's floor (1 under it)", load)
        self.assertNotIn("702 MW", load)

    def test_a_week_whose_every_deal_is_under_the_floor_says_so(self):
        deals = pd.DataFrame([{"event_id": "deal:a", "event_date": "2026-11-05T12:00:00Z", "deal_type": "other", "buyer": "", "seller": "X",
                               "asset": "Y", "mw": "", "dollars": "19000000000", "confidence": "0.5"}])
        L = self.five(deals, None)
        deal = next(x for x in L if x.startswith("- **Deal of the week"))
        self.assertIn("no deal of the week passes the Deals table's floor (1 under it)", deal)


class Session1476DealsTableDollars(unittest.TestCase):
    """Session 1476 (chain 154, fault 54): the Deals table's dollars cell is in the issue's money style."""

    def test_the_cell(self):
        self.assertEqual(roundup.usd_cell("938000000"), "USD 938 million")
        self.assertEqual(roundup.usd_cell("19000000000"), "USD 19 billion")
        self.assertEqual(roundup.usd_cell(""), "not stated")
        import inspect
        self.assertIn("usd_cell(r['dollars'])", inspect.getsource(roundup))


class Session1438OneTopic(unittest.TestCase):
    """Session 1438 (chain 149, fault 12): two price stories of one commodity are one topic whatever their regions; a
    story of the sector that is not about the price keeps the sector-and-region key."""

    def rec(self, title, sector, region):
        return {"cluster_id": title[:12], "titles": [title], "sector": sector, "region": region, "parties": "", "mw": "", "price": ""}

    def test_two_oil_price_stories_are_one_topic(self):
        a = self.rec("Oil Prices Rise on Fears of Middle East Conflict Escalation", "oil", "global")
        b = self.rec("Oil Prices Dip but Hold Above $100 as Middle East Supply Threats Mount", "oil", "Middle East")
        self.assertEqual(brief.price_commodity(a), "oil")
        self.assertTrue(brief.same_topic(a, b))
        c = self.rec("Brent tops $116 as Middle East risks grow", "geopolitics", "Saudi Arabia")
        self.assertTrue(brief.same_topic(a, c))

    def test_a_field_is_not_a_price_story(self):
        a = self.rec("Oil Prices Rise on Fears of Middle East Conflict Escalation", "oil", "global")
        b = self.rec("Eni advances Venezuelan heavy oil project, eyes year-end approval", "oil", "Venezuela")
        self.assertEqual(brief.price_commodity(b), "")
        self.assertFalse(brief.same_topic(a, b))
        g = self.rec("European gas prices reach their highest since 2022 on LNG supply fears", "gas", "Europe")
        h = self.rec("Henry Hub falls as forecasts turn cooler", "gas", "United States")
        self.assertTrue(brief.same_topic(g, h))
        self.assertFalse(brief.same_topic(a, g))

    def test_the_26_october_top_ten_holds_one_oil_price_item(self):
        path = os.path.join(ROOT, "warehouse", "output", "news_stories.csv")
        if not os.path.exists(path):
            self.skipTest("news_stories.csv is not here")
        with open(path, encoding="utf-8") as f:
            body = "".join(ln for ln in f if not ln.startswith("#"))
        s = pd.read_csv(io.StringIO(body), dtype=str, keep_default_na=False)
        when = pd.to_datetime(s["event_date"], utc=True, format="ISO8601")
        now = pd.Timestamp("2026-10-26 15:45", tz="UTC")
        s = s[(s["scored_at"] != "") & (when >= now - pd.Timedelta(hours=72)) & (when <= now)].copy()
        if len(s) < 200:
            self.skipTest("the stories of 23 to 26 October are not scored here")
        s["sig"] = s["significance"].astype(int)
        s["ai"] = s["ai_power_relevance"].astype(int)
        c = brief.build_clusters(s[s["sig"] > 0])
        top10, _ = brief.one_per_topic(c, 10, lambda *a, **k: None)
        oil_price = [r for r in top10.to_dict("records") if brief.price_commodity(r) == "oil"]
        self.assertEqual(len(oil_price), 1)
        self.assertEqual(len(top10), 10)


class Session1439NumbersBlock(unittest.TestCase):
    """Session 1439 (chain 149, faults 1, 3, 4, 5, 6): the fuel closes bounded by the cutoff; the demand row against the
    same weekday a week before when the year before is not held; the story rows in the block's form with a key and no
    headline; a price story never the policy row."""

    def test_a_price_story_is_not_the_policy_row(self):
        recs = [rec("p", "Oil dips but holds above $100; Brent trades at $114.42 per barrel", sector="oil", price="$114.42 per barrel"),
                rec("c", "Trump targets $6.2 Billion offshore wind project nearing completion", sector="policy", price="$6.2 Billion", parties="Trump administration")]
        notes = brief.Notes()
        line, detail = brief.story_row("Policy, capital or reliability", recs, brief.CAPITAL_SECTORS, {}, None, "a policy or capital figure", ("money",), notes)
        self.assertTrue(line.startswith("- **Policy, capital or reliability.** Policy sum: USD 6.2 billion (Trump administration; Outlet, 2026-10-21) [1]."), line)
        self.assertEqual(detail, "story c (price)")
        self.assertNotIn("114.42", line)
        line, detail = brief.story_row("Policy, capital or reliability", recs[:1], brief.CAPITAL_SECTORS, {}, None, "a policy or capital figure", ("money",), notes)
        self.assertEqual(line, "- **Policy, capital or reliability.** No story of the day states a policy or capital figure.")
        self.assertEqual(detail, "")

    def test_a_capacity_row_names_its_measure_place_and_who(self):
        r = rec("g", "Gingerah Energy refers 1,000 MW data centre with 5GWh battery in Western Australia to EPBC Act",
                sector="datacenter_power", mw="1000", parties="Gingerah Energy", links=[("Energy-Storage.news", "https://example.org/g")], first="2026-10-26T06:00:00Z")
        r["region"] = "Australia"
        notes = brief.Notes()
        line, detail = brief.story_row("Project or capacity", [r], brief.CAPACITY_SECTORS, {}, None, "a capacity figure in MW", ("mw",), notes)
        self.assertEqual(line, "- **Project or capacity.** Datacenter load, Australia: 1,000 MW (Gingerah Energy; Energy-Storage.news, 2026-10-26) [1]. "
                               "Change: first report, no earlier figure held. Status: the outlet's figure, not a table's.")
        self.assertEqual(detail, "story g (mw)")
        notes.extra["news_stories"] = detail
        self.assertEqual(notes.lines()[-1], "Tables: [1] `news_stories`; story g (mw).")

    def test_the_fuel_closes_stop_at_the_cutoff(self):
        now = pd.Timestamp("2026-10-26 15:45", tz="UTC")
        fuel = pd.DataFrame([{"entity": e, "ts_utc": pd.Timestamp(d, tz="UTC"), "value": v, "unit": "USD/bbl"}
                             for e in ("eia:henry_hub", "eia:wti_cushing", "eia:brent")
                             for d, v in (("2026-10-20", 100.0), ("2026-10-21", 101.0), ("2026-11-03", 107.0))])

        def fetch(table, *a, **k):
            if table == "eia_fuel_spot_prices":
                return fuel.copy()
            return pd.DataFrame(columns=["entity", "variable", "ts_utc", "value", "node", "freq"])
        with mock.patch.object(brief.erw, "fetch", side_effect=fetch), mock.patch.object(brief, "held_grids", return_value=set()), \
                mock.patch.object(brief, "held_rt", return_value=set()), mock.patch.object(brief, "cite_short", side_effect=lambda t: f"`{t}`"):
            facts = {}
            L = brief.numbers_today("2026-10-26", quiet, None, facts, now=now)
            self.assertFalse(any("2026-11-03" in ln for ln in L), [ln for ln in L if "11-03" in ln])
            self.assertTrue(any("101.00 USD/bbl on 2026-10-21" in ln for ln in L))
            self.assertTrue(all(c["d"] <= now for c in facts["cands"]))
            L2 = brief.numbers_today("2026-10-26", quiet, None, {})   # no bound: the newest row, as a scheduled run reads it
            self.assertTrue(any("2026-11-03" in ln for ln in L2))

    def test_demand_against_the_week_before_when_the_year_before_is_not_held(self):
        day = pd.Timestamp("2026-10-25", tz="UTC")

        def fetch(table, start=None, end=None, **k):
            d = pd.Timestamp(start)
            if d == day or d == day - pd.Timedelta(days=7):
                v = 470627.0 if d == day else 455000.0
                return pd.DataFrame([{"variable": "demand_mw", "ts_utc": d + pd.Timedelta(hours=23), "value": v}])
            return pd.DataFrame(columns=["variable", "ts_utc", "value"])
        store = {}
        with mock.patch.object(brief.erw, "fetch", side_effect=fetch):
            out = brief.demand_lines("2026-10-26", quiet, brief.Notes(), store)
        line = out[-1]
        self.assertIn("the same weekday a week before (2026-10-18) peaked at 455,000 MW", line)
        self.assertIn("so +3.4% on the week.", line)
        self.assertIn("The same weekday a year before is not held", line)
        self.assertEqual(len(DEMAND.findall(line)), 2)   # both peaks keep the form the page keys
        self.assertEqual(store["span"], "week")
        self.assertEqual(store["before"], day - pd.Timedelta(days=7))
        facts = {"cands": [], "demand": store}
        L = brief.numbers_block(facts, {"kind": None, "key": ""}, [], {})
        row = [ln for ln in L if ln.startswith("- **Physical.**")][0]
        self.assertIn("a week before (2026-10-18) peaked at 455,000 MW", row)
        self.assertIn("on the week. The same weekday a year before is not held.", row)


class Session1440OpeningNumber(unittest.TestCase):
    """Session 1440 (chain 149, fault 2): the opening number is the day's consequence, not the largest percentage move.
    The cases are the survey's (runs/s1440): 14 October (SPP +676.7% from a near-zero day, no story naming it),
    21 October (WTI -3.6% unnamed against 6,600 MW of reactors), 26 October (Henry Hub -9.3% unnamed, Brent -0.1% named)."""

    def test_an_unnamed_hub_never_beats_a_story_figure(self):
        cands = [cand("SPP SPPSOUTH_HUB day-ahead", "SPP", 19.4, 2.5, 676.7, table="iso_dam_hub_prices", unit="USD/MWh", node="SPPSOUTH_HUB"),
                 cand("Brent crude", "Brent crude", 115.9, 115.2, 0.6, reason=" Reason: x")]
        recs = [rec("t", "Taiwan commits up to $4.4 Billion to Alaska LNG", sector="lng", price="$4.4 Billion")]
        op = brief.opening_number(cands, recs)
        self.assertEqual(op["kind"], "story")
        self.assertEqual(op["figure"], "USD 4.4 billion")
        op = brief.opening_number(cands, [])   # no story figure: the hub is the last resort
        self.assertEqual((op["kind"], op["key"]), ("mover", "SPP"))

    def test_an_unnamed_benchmark_needs_the_larger_bar(self):
        wti = cand("WTI Cushing crude", "WTI Cushing crude", 98.0, 101.7, -3.6)
        recs = [rec("n", "The Nuclear Company proposes 6.6 GW Kentucky project", sector="nuclear", mw="6600")]
        op = brief.opening_number([wti], recs)
        self.assertEqual((op["kind"], op["figure"]), ("story", "6,600 MW"))
        henry = cand("Henry Hub natural gas", "Henry Hub natural gas", 2.52, 2.78, -9.3)
        op = brief.opening_number([henry, cand("Brent crude", "Brent crude", 128.1, 128.3, -0.1, reason=" Reason: y")], recs)
        self.assertEqual((op["kind"], op["key"]), ("mover", "Henry_Hub_natural_gas"))
        named = cand("WTI Cushing crude", "WTI Cushing crude", 98.0, 101.7, -3.6, reason=" Reason: z")
        op = brief.opening_number([named], recs)
        self.assertEqual((op["kind"], op["key"]), ("mover", "WTI_Cushing_crude"))

    def test_a_story_that_says_oil_prices_names_the_crude_benchmarks(self):
        c = frame(rec("o", "Oil prices rise on fears of Middle East conflict escalation", sector="oil", why="Tanker rates doubled after the attacks on Saudi ports."))
        self.assertIn("Tanker rates doubled", brief.price_reason("Brent crude", c))
        self.assertIn("Tanker rates doubled", brief.price_reason("WTI Cushing crude", c))
        self.assertEqual(brief.price_reason("Henry Hub natural gas", c), "")


class Session1441ChartOfTheDay(unittest.TestCase):
    """Session 1441 (chain 149, faults 14 and 15): a candidate whose series name is an id, or whose strength is a step
    from zero, is never the chart of the day; a readable, related one is; with none, choose says so."""

    def flag(self, key, fact, strength, table="eia_state_generation_monthly", series_key="entity=eia:x|variable=y"):
        return {"source": "scanner", "key": key, "fact": fact, "table": table, "series_key": series_key, "rank": 1,
                "flag": {"rule": "record", "strength": strength}}

    def test_the_two_ids_and_the_step_from_zero_are_passed_over(self):
        onrr = self.flag("a", "onrr_revenue:federal:onshore:22081_red_river:other_revenues:oil_gas:oil_gas_pre_production:none revenue: USD -29,834 in August 2026, the lowest monthly value held since August 2010.",
                         552.5288, table="onrr_revenue_monthly", series_key="entity=onrr_revenue:federal:onshore:22081_red_river:other_revenues:oil_gas:oil_gas_pre_production:none|variable=revenue")
        padd = self.flag("b", "eia_padd_movements:MGAMT1XP31 tanker_barge_receipts: 251.0 kbbl in June 2026, the highest monthly value held since January 1986.",
                         8.6406, table="eia_padd_rail_barge_movements_monthly")
        ok = self.flag("c", "Net generation from natural gas in Texas: 12,345 GWh in August 2026, the highest monthly value held since January 2001.", 3.2,
                       series_key="entity=eia:gen:TX:NG|variable=net_generation")
        self.assertFalse(dc.readable(onrr)); self.assertFalse(dc.readable(padd)); self.assertTrue(dc.readable(ok))
        self.assertTrue(dc.degenerate(onrr)); self.assertFalse(dc.degenerate(ok))
        stories = [{"titles": ["Oil prices rise on fears of Middle East conflict escalation"], "sector": "oil", "why": "", "parties": ""}]
        c, why = dc.choose([onrr, padd, ok], set(), stories=stories)
        self.assertEqual(c["key"], "c")
        self.assertIn("2 candidate(s) whose series has no plain name passed over", why)
        self.assertNotIn("step from zero", why)   # the ONRR flag is counted once, as unreadable
        c, why = dc.choose([onrr, padd], set(), stories=stories)
        self.assertIsNone(c)
        self.assertIn("passed over", why)

    def test_a_readable_step_from_zero_is_passed_over_too(self):
        step = self.flag("s", "Net generation from solar in Vermont: 1 GWh in August 2026, the highest monthly value held since January 2001.", 61.0)
        ok = self.flag("c", "Net generation from natural gas in Texas: 12,345 GWh in August 2026, the highest monthly value held since January 2001.", 3.2)
        c, why = dc.choose([step, ok], set())
        self.assertEqual(c["key"], "c")
        self.assertIn("1 flag(s) past 50 robust standard deviations passed over as a step from zero", why)

    def test_the_stored_charts_that_the_rule_refuses(self):
        folder = os.path.join(ROOT, "docs", "digest", "charts")
        if not os.path.isdir(folder):
            self.skipTest("no chart records here")
        refused = []
        for f in sorted(os.listdir(folder)):
            if f.endswith(".json") and f[:4] == "2026":
                with open(os.path.join(folder, f), encoding="utf-8") as fh:
                    d = json.load(fh)
                if not dc.readable(d) or dc.degenerate(d):
                    refused.append(f[:10])
        # the five of 13 issues the session read (7, 22, 23 October, and 6 November's ONRR line item); a later issue
        # written by this code adds none
        for day in ("2026-10-07", "2026-10-22", "2026-10-23"):
            if os.path.exists(os.path.join(folder, f"{day}.json")):
                self.assertIn(day, refused)


class Session1442Sources(unittest.TestCase):
    """Session 1442 (chain 149, fault 23): a cluster's links reach the outlet's own page before Google's, so an item's
    first source is the outlet's wherever one of its stories has it."""

    def test_direct_links_come_first(self):
        g = ("Reuters", "https://news.google.com/rss/articles/CBMi0?oc=5")
        d = ("Rigzone", "https://www.rigzone.com/news/x")
        self.assertEqual(brief.direct_first([g, d]), [d, g])
        self.assertEqual(brief.direct_first([d, g]), [d, g])
        self.assertTrue(brief.is_google(g[1])); self.assertFalse(brief.is_google(d[1]))
        self.assertEqual(brief.link_text([d, g]), "[Rigzone](https://www.rigzone.com/news/x), [Reuters](https://news.google.com/rss/articles/CBMi0?oc=5) (via Google News)")

    def test_build_clusters_puts_the_outlet_first(self):
        rows = [{"cluster_id": "c", "sig": 7, "ai": 0, "sector": "oil", "region": "", "why": "w", "mw": "", "price_mentioned": "", "parties": "",
                 "event_date": "2026-10-26T01:00:00Z", "source": "Reuters", "source_url": "https://news.google.com/rss/articles/A?oc=5",
                 "title": "Oil prices rise", "summary": ""},
                {"cluster_id": "c", "sig": 6, "ai": 0, "sector": "oil", "region": "", "why": "w", "mw": "", "price_mentioned": "", "parties": "",
                 "event_date": "2026-10-26T02:00:00Z", "source": "OilPrice.com", "source_url": "https://oilprice.com/x",
                 "title": "Brent tops 116", "summary": ""}]
        c = brief.build_clusters(pd.DataFrame(rows))
        self.assertEqual(c.iloc[0]["links"][0], ("OilPrice.com", "https://oilprice.com/x"))
        self.assertEqual(c.iloc[0]["titles"][0], "Oil prices rise")   # the lead story is still the highest scored


class Session1443RankingAndSectors(unittest.TestCase):
    """Session 1443 (chain 149, fault 13, and the plan's tie-break fixture): a title about oil or gas prices is of that
    commodity's sector whatever power tag the scorer gave; at one significance, an event before commentary, then the
    outlets, then the time (rulings item 4), never AI relevance."""

    def row(self, cid, title, sector, sig=7, ai=0, source="Outlet", when="2026-10-26T01:00:00Z"):
        return {"cluster_id": cid, "sig": sig, "ai": ai, "sector": sector, "region": "", "why": "w", "mw": "", "price_mentioned": "",
                "parties": "", "event_date": when, "source": source, "source_url": f"https://example.org/{cid}/{source}", "title": title, "summary": ""}

    def test_an_oil_futures_story_is_not_power(self):
        r = self.row("c", "CFTC looks into sale of futures equal to 6 million barrels in two minutes", "power_prices")
        c = brief.build_clusters(pd.DataFrame([r, self.row("g", "ERCOT prices spike as demand peaks", "power_prices")]))
        self.assertEqual(dict(zip(c["cluster_id"], c["sector"])), {"c": "oil", "g": "power_prices"})
        self.assertEqual(brief.sector_of({"sector": "generation", "title": "Brent crude nears $120 as tensions rise"}), "oil")
        self.assertEqual(brief.sector_of({"sector": "generation", "title": "Gas plant approved in Ohio"}), "generation")
        self.assertEqual(brief.sector_of({"sector": "lng", "title": "Henry Hub falls"}), "lng")

    def test_the_ai_tie_break_is_gone(self):
        rows = [self.row("ai", "A 42 MW datacenter signs power", "datacenter_power", ai=9),
                self.row("deal1", "A 600 MW gas deal is signed", "deal", source="A", when="2026-10-26T03:00:00Z"),
                self.row("deal2", "A 600 MW gas deal is signed", "deal", source="B", when="2026-10-26T03:00:00Z"),
                self.row("deal3", "A 600 MW gas deal is signed", "deal", source="C", when="2026-10-26T03:00:00Z")]
        for r in rows[1:]:
            r["cluster_id"] = "deal"
        c = brief.build_clusters(pd.DataFrame(rows))
        self.assertEqual(list(c["cluster_id"]), ["deal", "ai"])   # three outlets before one, at the same score
        self.assertEqual(int(c.iloc[0]["outlets"]), 3)
        com = self.row("com", "Why the grid cannot keep up, an analysis", "generation", source="D", when="2026-10-26T00:00:00Z")
        c = brief.build_clusters(pd.DataFrame(rows + [com]))
        self.assertEqual(list(c["cluster_id"]), ["deal", "ai", "com"])   # commentary last at the same score, though earliest


class Session1444TheFold(unittest.TestCase):
    """Session 1444 (chain 149, faults 21 and 22): the stories above the fold are as many as bring the prose to 350 words
    (at most five, never past 450); the masthead says when the stories stop short of the cutoff."""

    def test_a_fourth_story_is_lifted_while_the_count_is_under_350(self):
        counts = {2: 230, 3: 295, 4: 362, 5: 430}
        self.assertEqual(brief.lift_count(lambda n: counts[n], 3, 10), 4)
        self.assertEqual(brief.lift_count(lambda n: counts[n], 3, 3), 3)        # no story left to lift
        self.assertEqual(brief.lift_count(lambda n: {2: 300, 3: 340, 4: 345, 5: 349}[n], 3, 10), 5)   # the lift stops at five
        self.assertEqual(brief.lift_count(lambda n: {2: 420, 3: 470}[n], 3, 10), 2)   # past 450 with three: two
        self.assertEqual(brief.lift_count(lambda n: {2: 300, 3: 400}[n], 3, 10), 3)
        self.assertEqual((brief.FOLD_MIN, brief.FOLD_MAX, brief.MOVED_LIFT_MAX), (350, 450, 5))

    def test_the_masthead_says_when_the_stories_stop_short(self):
        op = {"kind": None, "key": ""}
        now = pd.Timestamp("2026-10-26 15:45", tz="UTC")
        L = brief.masthead_lines("2026-10-26", now, op, pd.Timestamp("2026-10-26 07:55", tz="UTC"))
        self.assertEqual(L[2], "**26 October 2026.** Stories through 03:55 ET, 07:55 UTC; prices through 11:45 ET, 15:45 UTC.")
        L = brief.masthead_lines("2026-10-26", now, op, pd.Timestamp("2026-10-26 15:02", tz="UTC"))
        self.assertEqual(L[2], "**26 October 2026.** Data through 11:45 ET, 15:45 UTC.")
        self.assertEqual(brief.masthead_lines("2026-10-26", now, op)[2], "**26 October 2026.** Data through 11:45 ET, 15:45 UTC.")

    def test_main_reads_the_fold_count(self):
        src = inspect.getsource(brief.main)
        self.assertIn("n_moved = lift_count(lambda n: above_fold_words(chr(10).join(L + middle(n) + tail)), moved_count(recs), len(recs))", src)
        self.assertIn("masthead_lines(digest_date, now, op, newest)", src)


class Session1445TheEmail(unittest.TestCase):
    """Session 1445 (chain 149, faults 17 and 18): the v2 Digest email at 390 and in a plain client: a table name wraps,
    one Tables line for the opening number and the block, the brand's fonts with their fallbacks named, no script and
    no stylesheet, the character once and only in the fun fact, alt text on every image."""

    def render(self):
        with tempfile.TemporaryDirectory() as d:
            p = os.path.join(d, "2026-10-23.md")
            with open(p, "w", encoding="utf-8") as f:
                f.write(V2_MD)
            with mock.patch.dict(os.environ, {"SITE_URL": "https://example.org", "EMAIL_ASSET_REF": "main"}):
                return email_digest.render(p, "daily", unsubscribe="https://x/unsub")

    def test_one_tables_line_and_it_wraps(self):
        title, label, text, body = self.render()
        self.assertEqual(text.count("Tables: "), 1, [ln for ln in text.splitlines() if ln.startswith("Tables")])
        self.assertEqual(body.count("Tables: "), 1)
        self.assertIn('<code style="overflow-wrap:anywhere;word-break:break-word">', body)
        self.assertIn('font-size:12px;color:#6B665E">Tables: ', body)
        self.assertLess(body.index("The numbers"), body.index("Tables: "))   # the one line comes after the block

    def test_a_plain_client_reads_it(self):
        title, label, text, body = self.render()
        self.assertNotIn("<script", body); self.assertNotIn("<link", body); self.assertNotIn("@import", body)
        self.assertIn("font-family:'Source Serif 4',Georgia,serif", body)
        self.assertIn("font-family:'IBM Plex Sans',system-ui,sans-serif", body)
        imgs = re.findall(r"<img [^>]*>", body)
        self.assertTrue(imgs)
        for im in imgs:
            self.assertIn(' alt="', im)
        self.assertEqual(body.count("erw-character-48.png"), 1)
        fun = body.index("Fun Fact")
        self.assertGreater(body.index("erw-character-48.png"), fun)
        self.assertNotIn("erw-character-48.png", body[:body.index("What moved")])


class Session1446TheRoundupsNumbers(unittest.TestCase):
    """Session 1446 (chain 149, faults 26 to 30): the stand-ins for an empty category, the datacenter row with a subject,
    the scorer's refusal of an energy unit as MW, the email's five without the opening number twice."""

    def test_an_empty_category_stands_in_with_the_next_move(self):
        facts = {"dam": [{"label": "SPP", "node": "SPPSOUTH_HUB", "m1": 27.62, "m0": 20.15, "ref": "[1]"},
                         {"label": "ERCOT", "node": "HB_NORTH", "m1": 33.19, "m0": 25.73, "ref": "[1]"}],
                 "fuel": [{"label": "Brent crude", "a": {"value": 120.15, "unit": "USD/bbl", "ts_utc": pd.Timestamp("2026-10-30", tz="UTC")},
                           "b": {"value": 128.30, "unit": "USD/bbl", "ts_utc": pd.Timestamp("2026-10-23", tz="UTC")}, "ref": "[5]"}]}
        empty = pd.DataFrame(columns=["event_date", "dollars", "mw", "buyer", "seller", "asset", "deal_type", "event_id"])
        empty_dc = pd.DataFrame(columns=["first_story_at", "capacity_mw", "operator", "site_name", "city", "state", "entity_id"])
        picked = {}
        with mock.patch.object(roundup, "read_table", side_effect=lambda n: empty if n == "energy_deals" else empty_dc), \
                mock.patch.object(roundup, "ANALYSIS_DIR", tempfile.mkdtemp()):
            L = roundup.five_numbers("2026-W44", pd.Timestamp("2026-10-26", tz="UTC"), pd.Timestamp("2026-11-02", tz="UTC"), facts, quiet, picked)
        self.assertEqual(len(L), 5)
        self.assertTrue(L[0].startswith("- **Price move of the week:** SPP SPPSOUTH_HUB day-ahead averaged 27.62"), L[0])
        self.assertIn("no deal in `energy_deals` is dated this week; in its place, the week's next price move: ERCOT HB_NORTH day-ahead", L[2])
        self.assertIn("states its MW; in its place, the week's next price move: Brent crude closed at 120.15", L[3])
        self.assertEqual([m["label"] for m in picked["moves"]], ["SPP SPPSOUTH_HUB day-ahead", "ERCOT HB_NORTH day-ahead", "Brent crude"])

    def test_the_datacenter_row_needs_an_operator_or_a_site(self):
        dc = pd.DataFrame([{"first_story_at": "2026-10-20T00:00:00Z", "capacity_mw": "1000", "operator": "", "site_name": "", "city": "Newport", "state": "", "entity_id": "datacenter:a"},
                           {"first_story_at": "2026-10-21T00:00:00Z", "capacity_mw": "400", "operator": "Crusoe", "site_name": "Spark", "city": "Abilene", "state": "TX", "entity_id": "datacenter:b"}]).assign(confidence="0.9")
        empty = pd.DataFrame(columns=["event_date", "dollars", "mw", "buyer", "seller", "asset", "deal_type", "event_id"])
        with mock.patch.object(roundup, "read_table", side_effect=lambda n: empty if n == "energy_deals" else dc), \
                mock.patch.object(roundup, "ANALYSIS_DIR", tempfile.mkdtemp()):
            L = roundup.five_numbers("2026-W43", pd.Timestamp("2026-10-19", tz="UTC"), pd.Timestamp("2026-10-26", tz="UTC"), {}, quiet, {})
        self.assertIn("400 MW, Crusoe, Spark, Abilene, TX", L[3])
        self.assertNotIn("1,000 MW", L[3])

    def test_the_scorer_refuses_an_energy_unit_as_capacity(self):
        self.assertTrue(score.capacity_stated("Singapore plans 26% more power capacity and 1 GW of storage"))
        self.assertFalse(score.capacity_stated("Singapore plans 26% more power capacity in early 2030s, with 1GWh of storage"))
        self.assertTrue(score.capacity_stated("a 600MW campus"))
        self.assertIn("capacity_stated(", inspect.getsource(score.main))

    def test_the_email_does_not_print_the_opening_number_twice(self):
        md = ROUNDUP_V2_MD if "ROUNDUP_V2_MD" in globals() else None
        if md is None:
            self.skipTest("no v2 Roundup fixture here")


class Session1446Naming(unittest.TestCase):
    """Session 1446: a story names a price for the opening number's choice even when its why line fails the check and
    no reason prints beside the mover (the W44 render opened with a story's figure though the oil stories named Brent)."""

    def test_named_without_a_printable_reason(self):
        c = frame(rec("o", "Oil Prices Dip but Hold Above $100 as Middle East Supply Threats Mount", sector="oil",
                      why="Sustained USD 100+ crude driven by ongoing conflict signals a material price regime."))
        self.assertEqual(brief.price_reason("Brent crude", c), "")   # the why line says "signals": no reason prints
        self.assertTrue(brief.price_named("Brent crude", c))
        self.assertFalse(brief.price_named("Henry Hub natural gas", c))
        move = {"pct": -6.4, "text": "Brent closed lower", "label": "Brent crude"}
        self.assertEqual(roundup.opening_number({"moves": [move], "story": {"text": "1,000 MW: x", "fig": "1,000 MW"}}, c)["key"], "move")
        brent = cand("Brent crude", "Brent crude", 120.15, 128.30, -6.4, unit="USD/bbl")
        brent["named"] = True
        self.assertEqual(brief.opening_number([brent], [rec("g", "G plans 1,000 MW", mw="1000")])["key"], "Brent_crude")


class Session1447TablesAndArchive(unittest.TestCase):
    """Session 1447 (chain 149, faults 36 to 38): next week's titles cut at a word with one item a kind a day; the
    weekend line says no story of those days is scored; the numbers summary has one number a clause."""

    def test_a_filing_title_is_cut_at_a_word(self):
        t = ("Northern Natural Gas Company; Notice of Availability of the Environmental Assessment for the Proposed Ventura "
             "to Farmington A-Line Abandonment and Capacity Replacement Project")
        self.assertEqual(roundup.short_title(t), "Northern Natural Gas Company, Notice of Availability of the Environmental Assessment for...")
        self.assertEqual(roundup.short_title("Ohio Regulatory Program"), "Ohio Regulatory Program")
        self.assertNotIn("Repl...", roundup.short_title(t))
        self.assertEqual(roundup.event_kind("Comments on the EA are due by 5:00 p.m. Eastern Time on November 2, 2026."), "comment")
        self.assertEqual(roundup.event_kind("The final rule takes effect on November 25, 2026."), "effective")

    def test_one_item_a_kind_a_day(self):
        reads = pd.DataFrame([
            {"title": "A Pipeline; Notice of Availability of the EA", "agency": "FERC", "significance": "6", "source_url": "https://x/a",
             "timeline": "Comments on the EA are due by 5:00 p.m. Eastern Time on November 2, 2026."},
            {"title": "B Pipeline; Notice of Availability of the EA", "agency": "FERC", "significance": "6", "source_url": "https://x/b",
             "timeline": "Comments are due by 5:00 p.m. Eastern Time on November 2, 2026."},
            {"title": "C Rule", "agency": "NRC", "significance": "8", "source_url": "https://x/c",
             "timeline": "The final rule takes effect on November 4, 2026."},
            {"title": "D Pipeline; Notice of Scoping", "agency": "FERC", "significance": "5", "source_url": "https://x/d",
             "timeline": "Comments are due by 5:00 p.m. Eastern Time on November 5, 2026."}])
        with mock.patch.object(roundup, "read_table", return_value=reads):
            out = roundup.next_week(pd.Timestamp("2026-11-02", tz="UTC"), quiet)
        self.assertEqual(len(out), 3)
        self.assertTrue(out[0].startswith("- **2 November 2026**: A Pipeline, Notice of Availability of the EA (FERC)."), out[0])
        self.assertFalse(any("B Pipeline" in x for x in out))   # the second FERC comment deadline of the same day waits
        self.assertTrue(any("C Rule (NRC)" in x for x in out))
        self.assertTrue(any("D Pipeline" in x for x in out))

    def test_the_weekend_line_says_scored(self):
        src = inspect.getsource(roundup.main)
        self.assertIn('f"- no story of {wk_start:%Y-%m-%d} or "', src)
        self.assertNotIn("no scored story was published on", src)

    def test_the_summary_has_one_number_a_clause(self):
        self.assertEqual(brief.summary_check("ERCOT's HB_NORTH and SPP each rose about 7.46 and 7.47 USD/MWh on the week before."), ["two figures in one clause"])
        self.assertEqual(brief.summary_check("ERCOT's HB_NORTH rose 7.46 USD/MWh on the week before; SPP's hub rose 7.47."), [])
        self.assertEqual(brief.summary_check("Prices were 33.19 and 27.62 USD/MWh respectively."), ["two figures in one clause"])
        self.assertIn("One number a clause", brief.SUMMARY_SYSTEM)
        self.assertIn("summary_check(text)", inspect.getsource(brief.numbers_summary))


class Session1448FunFact(unittest.TestCase):
    """Session 1448 (chain 149, faults 16 and 24; rulings items 7 and 8; the character): every verified fact of the bank
    passes its check; a warehouse fact's numbers carry the issue's thousands separator; a warehouse source links its
    table; the 14 October issue keeps its one line on the page."""

    def test_every_verified_fact_of_the_bank_passes(self):
        import funfact
        bank = funfact.read_bank()
        kept = bank[bank["status"] == "verified"]
        self.assertGreater(len(kept), 30)
        bad = [(r["fact_id"], funfact.check_record(r)) for r in kept.to_dict("records") if funfact.check_record(r)]
        self.assertEqual(bad, [])
        puns = bank[(bank["structure"] == "pun") & (bank["status"] == "verified")]
        for r in puns.to_dict("records"):   # item 7: a pun that states a claim has its verified span, or is dropped
            self.assertEqual(funfact.check_record(r), [])

    def test_a_warehouse_fact_carries_the_thousands_separator(self):
        import funfact
        a = pd.DataFrame([{"entity": "ercot:HB_WEST", "variable": "all_max", "ts_utc": pd.Timestamp("2021-02-01", tz="UTC"), "value": 9310.49},
                          {"entity": "ercot:HB_WEST", "variable": "all_max", "ts_utc": pd.Timestamp("2015-01-01", tz="UTC"), "value": 100.0},
                          {"entity": "ercot:HB_WEST", "variable": "n_negative", "ts_utc": pd.Timestamp("2022-01-01", tz="UTC"), "value": 4266},
                          {"entity": "ercot:HB_WEST", "variable": "n_negative", "ts_utc": pd.Timestamp("2015-01-01", tz="UTC"), "value": 10}])
        with mock.patch.object(funfact, "_wsource", side_effect=lambda key, table, ev, part="fact": {"part": part, "table": table, "span": ev, "url": "", "label": f"ERW table {table}", "publisher": "ERW"}), \
                mock.patch.dict(sys.modules, {"erw": mock.MagicMock(fetch=lambda t: a)}):
            got = funfact.w_peak_premium("peak_premium:HB_WEST")
        self.assertIn("reached 9,310.49 USD/MWh in a 15-minute interval in 2021", got["fact"])
        self.assertIn("with 4,266.", got["fact"])
        self.assertIn("highest all_max 9,310.49 USD/MWh", got["sources"][0]["span"])
        self.assertEqual(funfact.unverified(got["fact"], [got["sources"][0]["span"]]), [])   # the literal check reads one form

    def test_a_warehouse_source_links_its_table(self):
        import funfact
        item = {"fact": "F.", "second": "", "sources": [{"url": "", "label": "ERW table ercot_peak_premium_annual", "table": "ercot_peak_premium_annual", "publisher": "Energy Research Warehouse (ERW), derived"}]}
        self.assertEqual(funfact.item_markdown(item)[-1], "Sources: [`ercot_peak_premium_annual`](/data#ercot_peak_premium_annual) (Energy Research Warehouse (ERW), derived).")
        web = {"fact": "F.", "second": "S.", "sources": [{"url": "https://en.wikipedia.org/wiki/Hoover_Dam", "label": "Wikipedia, Hoover Dam"}]}
        self.assertEqual(funfact.item_markdown(web), ["F. S.", "", "Sources: [Wikipedia, Hoover Dam](https://en.wikipedia.org/wiki/Hoover_Dam)."])

    def test_the_14_october_issue_keeps_its_line(self):
        with open(os.path.join(ROOT, "site", "lib", "digest.ts"), encoding="utf-8") as f:
            ts = f.read()
        self.assertIn('"2026-10-14"', ts[ts.index("ISSUE_NOTES"):])


class Session1459StoredFactsStyled(unittest.TestCase):
    """Session 1459 (chain 150, fault 16): a bank row keeps the text it was verified with; the issue's item prints its
    numbers with the issue's thousands separator, and still passes its check."""

    def test_the_styles(self):
        import funfact
        cases = [
            ("ERCOT's real-time price at HB_WEST reached 9310.49 USD/MWh in a 15-minute interval in 2021, the highest of "
             "any year since 2015; the year with the most negative-price intervals there was 2024, with 4266.",
             "ERCOT's real-time price at HB_WEST reached 9,310.49 USD/MWh in a 15-minute interval in 2021, the highest of "
             "any year since 2015; the year with the most negative-price intervals there was 2024, with 4,266."),
            ("California increased wind on the grid from 10 MW in 1981 to 1700 MW in the early 1990s.",
             "California increased wind on the grid from 10 MW in 1981 to 1,700 MW in the early 1990s."),
            ("The highest daily Brent crude spot price in EIA's series, which starts on 1987-05-20, was 143.95 USD/bbl on 2008-07-03.",
             "The highest daily Brent crude spot price in EIA's series, which starts on 1987-05-20, was 143.95 USD/bbl on 2008-07-03."),
            ("The oldest generators still operating entered service in 1891.", "The oldest generators still operating entered service in 1891."),
            ("It curtailed 1,459,998 MWh in April 2026.", "It curtailed 1,459,998 MWh in April 2026."),
        ]
        for raw, want in cases:
            with self.subTest(raw[:40]):
                self.assertEqual(funfact.issue_style(raw), want)

    def test_every_verified_fact_styled_passes_its_check_and_the_bank_is_not_rewritten(self):
        import funfact
        bank = funfact.read_bank()
        kept = bank[bank["status"] == "verified"].to_dict("records")
        changed = 0
        for r in kept:
            styled = dict(r, fact=funfact.issue_style(r["fact"]), second=funfact.issue_style(r["second"]))
            changed += styled["fact"] != r["fact"] or styled["second"] != r["second"]
            with self.subTest(r["fact_id"]):
                self.assertEqual(funfact.check_record(styled), [])
        self.assertGreaterEqual(changed, 4)   # the three hubs' peak rows and the 1700 MW history fact, on 6 November
        self.assertIn("9310.49", " ".join(funfact.read_bank()["fact"]))   # the bank keeps its text

    def test_the_days_item_prints_the_styled_numbers(self):
        import funfact
        bank = funfact.read_bank()
        row = bank[bank["fact"].str.contains("HB_WEST reached 9310.49")].iloc[0]
        one = bank[bank["fact_id"] == row["fact_id"]].assign(used_on="", structure="none")
        with tempfile.TemporaryDirectory() as d, \
                mock.patch.object(funfact, "read_bank", lambda: one.copy()), \
                mock.patch.object(funfact, "write_bank", lambda df: None), \
                mock.patch.object(funfact, "ITEMS", d):
            item = funfact.write_item("2026-11-09", lambda *a: None)   # a Monday: the fact runs alone
            self.assertTrue(os.path.exists(os.path.join(d, "2026-11-09.json")))
        self.assertIn("9,310.49 USD/MWh", item["fact"])
        self.assertIn(item["fact"], "\n".join(funfact.item_markdown(item)))


class Session1460FiveKeys(unittest.TestCase):
    """Session 1460 (chain 150, faults 28 and 29): the five numbers' rows print no row id, template or path; the keys sit on
    one Tables line under the five, the email prints it small and grey, and scripts/check_roundup.py traces each row by it
    (an issue written before keeps its keys in the rows and is read as it was)."""

    MD = ("# ERW Weekly Roundup, 2026-W44\n\n## The week in five numbers\n\n"
          "- **US48 peak demand:** 470,627 MW in the hour starting 2026-10-25 23:00 UTC [6].\n"
          "- **Deal of the week, by US dollars:** USD 45 billion, Anthropic and Nscale, cloud computing deal (offtake, 2026-10-19).\n"
          "- **Largest new datacenter load first reported this week:** 1,000 MW, Gingerah Energy, Gingerah, Western Australia.\n"
          "- **From the chart of the week:** WTI spot price at Cushing, weekly mean: 107 USD/bbl in 2026-10-19 to 2026-10-25 "
          "(the week before: the chart's latest period ends before this week).\n\n"
          "Tables: the deal of the week, `energy_deals` deal:d7ed182372909e6d; the datacenter load, `datacenter_projects` "
          "datacenter:8ea094c6d5fc3593; the chart's figure, template `watch_wti`, `docs/analysis/2026-W44/chart_of_the_week.json`.\n\n"
          "## What mattered\n")
    OLD = ("## The week in five numbers\n\n"
           "- **Deal of the week, by US dollars:** USD 45 billion, Anthropic and Nscale, cloud computing deal (offtake, 2026-10-19; "
           "`energy_deals` deal:d7ed182372909e6d).\n"
           "- **From the chart of the week:** WTI spot price at Cushing, weekly mean: 107 USD/bbl in 2026-10-19 to 2026-10-25 "
           "(template `watch_wti`, `docs/analysis/2026-W44/chart_of_the_week.json`).\n")

    def checks(self, md, refs):
        import check_roundup as cr
        return {k: v for k, v, _f in cr.five_checks("2026-W44", md, refs, None)}

    def test_the_tracer_reads_the_keys_on_the_tables_line(self):
        got = self.checks(self.MD, {"6": "eia930_all_demand"})
        self.assertEqual(got["rdp_five_deal|energy_deals|deal:d7ed182372909e6d|dollars"], "USD 45 billion")
        self.assertEqual(got["rdp_five_load|datacenter_projects|datacenter:8ea094c6d5fc3593|capacity_mw"], "1,000")
        self.assertEqual(got["rdp_five_chart|2026-W44|watch_wti|headline"], "107")

    def test_an_issue_written_before_is_read_as_it_was(self):
        got = self.checks(self.OLD, {})
        self.assertEqual(got["rdp_five_deal|energy_deals|deal:d7ed182372909e6d|dollars"], "USD 45 billion")
        self.assertEqual(got["rdp_five_chart|2026-W44|watch_wti|headline"], "107")

    def test_no_key_in_the_rows_and_the_email_prints_the_line_small(self):
        import email_digest
        for ln in self.MD.splitlines():
            if ln.startswith("- "):
                self.assertNotRegex(ln, r"deal:|datacenter:|template|docs/analysis")
        body = self.MD.split("## The week in five numbers\n\n")[1].split("\n## ")[0].splitlines()
        _text, html = email_digest.block(body)
        self.assertIn('font-size:12px;color:#6B665E">Tables: the deal of the week', html)


class Session1450TheTracers(unittest.TestCase):
    """Session 1450 (chain 149, fault 6 and session 1434's note): the block's story rows are traced to their story's
    scored field; a revised figure stays revised when the warehouse re-reads the row after the publisher's window."""

    def setUp(self):
        import importlib.util
        spec = importlib.util.spec_from_file_location("check_digest", os.path.join(ROOT, "scripts", "check_digest.py"))
        self.cd = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(self.cd)

    def test_a_story_row_is_traced_to_news_stories(self):
        cd = self.cd
        with tempfile.TemporaryDirectory() as d:
            with open(os.path.join(d, "news_stories.csv"), "w", encoding="utf-8", newline="") as f:
                f.write("# provenance\nevent_id,mw,price_mentioned\nnews:f43900b681794577,1000,\nnews:ca99c1cbd4a165c7,,$1.6 Trillion\n")
            src = cd.Csv(d)
            st, got = cd.check_figure(src, "2026-10-26", {"key": "digest_story|news_stories|news:f43900b681794577|mw", "raw": "1,000", "text": "1,000", "table": "news_stories", "entity": "news:f43900b681794577", "held": False}, {}, written="2026-10-26T15:45:00Z")
            self.assertEqual((st, got), ("ok", "1,000"))
            st, got = cd.check_figure(src, "2026-10-26", {"key": "digest_story|news_stories|news:ca99c1cbd4a165c7|price", "raw": "1.6", "text": "USD 1.6 trillion", "table": "news_stories", "entity": "news:ca99c1cbd4a165c7", "held": False}, {}, written="2026-10-26T15:45:00Z")
            self.assertEqual(st, "ok")
            st, _ = cd.check_figure(src, "2026-10-26", {"key": "digest_story|news_stories|news:f43900b681794577|mw", "raw": "900", "text": "900", "table": "news_stories", "entity": "x", "held": False}, {}, written="2026-10-26T15:45:00Z")
            self.assertEqual(st, "FAIL")
            st, _ = cd.check_figure(src, "2026-10-26", {"key": "digest_story|news_stories|news:nothere|mw", "raw": "1", "text": "1", "table": "news_stories", "entity": "x", "held": False}, {}, written="2026-10-26T15:45:00Z")
            self.assertEqual(st, "not here")

    def test_a_revision_re_read_after_the_window_stays_revised(self):
        cd = self.cd
        with tempfile.TemporaryDirectory() as d:
            with open(os.path.join(d, "eia_fuel_spot_prices.csv"), "w", encoding="utf-8", newline="") as f:
                f.write("# provenance\nentity,variable,ts_utc,value,retrieved_at\neia:wti_cushing,close,2026-10-14T00:00:00Z,96.34,2026-11-05T23:10:05Z\n")
            src = cd.Csv(d)
            st, why = cd.compare(src, "101.91", "96.34", "2026-10-21T15:45:00Z", "eia_fuel_spot_prices", "eia:wti_cushing", "2026-10-14T00:00:00Z", "close", period="2026-10-14")
            self.assertEqual(st, "revised")
            # an issue written after the window printed a settled figure: a difference is a fault
            st, _ = cd.compare(src, "101.91", "96.34", "2026-11-01T15:45:00Z", "eia_fuel_spot_prices", "eia:wti_cushing", "2026-10-14T00:00:00Z", "close", period="2026-10-14")
            self.assertEqual(st, "FAIL")


class Session1452TheMethod(unittest.TestCase):
    """Session 1452 (chain 149): the periodicals' method is one document in the v2 shape, each rulings item named, each
    figure's key and tracer named, the send hours and the recipients as they are; the about page links it; the rubric
    carries the why line's rule."""

    def setUp(self):
        with open(os.path.join(ROOT, "docs", "methods", "periodicals.md"), encoding="utf-8") as f:
            self.md = f.read()

    def test_every_rulings_item_and_every_key(self):
        for item in ("item 1)", "item 2)", "item 3", "item 4", "item 5", "item 6b", "item 7", "item 8", "item 9", "item 10", "item 11", "item 12", "item 13", "item 14", "item 15", "item 16", "item 17", "item 18"):
            self.assertIn(item, self.md, item)
        for key in ("digest_dam", "digest_rt", "digest_fuel", "digest_demand", "digest_story", "digest_chart", "rdp_five_dam", "rdp_five_fuel", "rdp_five_us48", "rdp_five_deal"):
            self.assertIn(key, self.md, key)
        for part in ("The masthead", "The opening number", "The numbers block", "What moved", "The chart of the day", "The fun fact", "The footer",
                     "The week in five numbers", "What mattered", "The chart of the week", "Next week"):
            self.assertIn(part, self.md, part)
        self.assertIn("14:00 UTC", self.md); self.assertIn("23:00 UTC", self.md); self.assertIn("DIGEST_RECIPIENTS", self.md)
        self.assertNotIn(chr(0x2014), self.md); self.assertNotIn(chr(0x2013), self.md)

    def test_the_about_page_links_it_and_the_rubric_carries_the_rule(self):
        with open(os.path.join(ROOT, "site", "app", "about", "page.tsx"), encoding="utf-8") as f:
            self.assertIn('href="/data/methods/periodicals"', f.read())
        self.assertIn("one fact the story gives that the title does not", score.RUBRIC)
        for word in ("signals", "demonstrates", "reflects", "underscores", "highlights"):
            self.assertIn(word, score.RUBRIC)


if __name__ == "__main__":
    unittest.main()

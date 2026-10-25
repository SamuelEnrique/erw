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
                               "asset": "Bay du Nord", "mw": "", "dollars": "12000000000"}])
        dcs = pd.DataFrame([{"entity_id": "dc:a", "first_story_at": "2026-10-07T10:00:00Z", "capacity_mw": "1200", "operator": "Crusoe", "site_name": "Spark", "city": "Abilene", "state": "TX"}])
        with tempfile.TemporaryDirectory() as d, mock.patch.object(roundup, "read_table", lambda n: {"energy_deals": deals, "datacenter_projects": dcs}.get(n)), \
                mock.patch.object(roundup, "ANALYSIS_DIR", d):
            L = roundup.five_numbers("2026-W41", pd.Timestamp("2026-10-05", tz="UTC"), pd.Timestamp("2026-10-12", tz="UTC"), facts, quiet)
        text = "\n".join(L)
        self.assertTrue(cr.FIVE_DAM.search(text))
        self.assertTrue(cr.FIVE_US48.search(text))
        self.assertTrue(cr.FIVE_DEAL.search(text))
        self.assertTrue(cr.FIVE_LOAD.search(text))
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
        # without the reason, a benchmark before a hub, however large the hub's move
        wti0 = dict(wti, reason="")
        self.assertEqual(brief.opening_number([hub_big, hh, wti0], [])["cand"]["key"], "WTI Cushing crude")
        # novelty: yesterday's metric leads again only at twice the bar (WTI's 3.99 is under 6)
        self.assertEqual(brief.opening_number([hub_big, hh, wti0], [], prev_key="WTI_Cushing_crude")["cand"]["key"], "Henry Hub natural gas")
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
        facts = {"cands": [cand("Henry Hub natural gas", "Henry Hub natural gas", 3.22, 3.32, -3.01),
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
        self.assertIn("600 MW: A plans 600 MW", rows[2])
        self.assertIn("USD 3 billion: B raises USD 3 billion", rows[3])
        self.assertNotIn("](http", "\n".join(rows[2:]))                 # no story link: the item carries it (the hard check)
        self.assertTrue(any(ln.startswith("Tables: [1] `iso_dam_hub_prices`; [2] `eia930_all_demand`") for ln in L))

    def test_the_masthead_and_the_subject(self):
        op = brief.opening_number([cand("Henry Hub natural gas", "Henry Hub natural gas", 3.22, 3.32, -3.01)], [])
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
        self.assertIn("return foldMore(fillDigest(", src)
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
        self.assertEqual(roundup.opening_number({"move": move, "deal": deal, "dc": dc, "us48": us48})["key"], "move")
        self.assertEqual(roundup.opening_number({"move": dict(move, pct=-9.9), "deal": deal, "dc": dc, "us48": us48})["key"], "deal")
        self.assertEqual(roundup.opening_number({"deal": dict(deal, usd=5e8), "dc": dc, "us48": us48})["key"], "datacenter")
        self.assertEqual(roundup.opening_number({"dc": dict(dc, mw=300.0), "us48": us48})["key"], "us48")
        self.assertIsNone(roundup.opening_number({}))
        self.assertIn("persistent", roundup.opening_number.__doc__)
        op = roundup.opening_number({"move": move})
        self.assertEqual(roundup.opening_lines(op)[2], "**WTI moved.** Status: calculated from observed prices (the warehouse's tables).")
        self.assertEqual(roundup.subject_line(op, "Six reactors eyed."), "ERW Weekly | Six reactors eyed; WTI Cushing crude +12.0% on the week")
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
        self.assertEqual(roundup.evidence_gap(rec("a", "A", mw="600")),
                         "What the evidence does not establish: the 600 MW is the outlet's figure, not a warehouse table's.")
        self.assertEqual(roundup.evidence_gap(dict(rec("b", "B"), outlets=1)),
                         "What the evidence does not establish: the stories give no figure for it. One outlet has reported it so far.")

    def test_next_week_from_the_policy_reads(self):
        reads = pd.DataFrame([
            {"title": "Northern Natural Gas Company; Notice", "agency": "Federal Energy Regulatory Commission", "significance": "6",
             "source_url": "https://www.federalregister.gov/x",
             "timeline": "Comments on the EA are due to FERC by 5:00 p.m. Eastern Time on November 2, 2026. The Commission will then decide."},
            {"title": "Later rule", "agency": "EPA", "significance": "8", "source_url": "https://e/y", "timeline": "Comments are due on November 20, 2026."},
            {"title": "Earlier", "agency": "DOE", "significance": "9", "source_url": "https://e/z", "timeline": "It took effect on October 20, 2026."}])
        with mock.patch.object(roundup, "read_table", return_value=reads):
            got = roundup.next_week(pd.Timestamp("2026-10-27", tz="UTC"), quiet)
        self.assertEqual(got, ["- **2 November 2026**: Northern Natural Gas Company; Notice (Federal Energy Regulatory Commission). Comments on the EA "
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
            self.assertIn("foldMore(render(md, DOCS.weekly_source[week]))", f.read())


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


if __name__ == "__main__":
    unittest.main()

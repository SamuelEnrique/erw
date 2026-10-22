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


class TheOutlet(unittest.TestCase):
    def test_the_three_forms(self):
        lic = {"Reuters"}
        self.assertEqual(brief.source_text("Heatmap News", GN, lic), f"[Heatmap News]({GN}) (via Google News)")
        self.assertEqual(brief.source_text("T&D World", "https://www.tdworld.com/x", lic), "[T&D World](https://www.tdworld.com/x)")
        self.assertEqual(brief.source_text("Reuters", GN, lic), "Reuters")
        self.assertEqual(brief.link_text([("Reuters", GN), ("Reuters", "https://r/2")], lic), "Reuters")

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
            "table": "eia_retail_electricity_prices", "series_key": "entity=eia:retail_price:IA:IND|variable=retail_price", "flag": {"id": "iowa", "rule": "record", "strength": 0.8, "value": 99.9, "compared": {"old_record": 91.7}}, "card": {"title": "T"}}
    UTAH = {"source": "scanner", "key": "utah", "rank": 2, "fact": "Retail electricity sales in Utah, residential: 1,658,263 MWh in July 2026.",
            "table": "eia_retail_sales_monthly", "series_key": "entity=eia:retail_sales:UT:RES|variable=retail_sales", "flag": {"id": "utah", "rule": "record", "strength": 1.01, "value": 1658263, "compared": {"old_record": 1484757}}, "card": {"title": "T"}}

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
            self.assertIn("news:8470c320a7225474", set(top10["cluster_id"]))
            self.assertNotIn("news:ec41f0a2f9b34be4", set(top10["cluster_id"]))
        c = self.clusters("2026-10-09")
        if "news:f96cc76a18212ba4" in set(c["cluster_id"]):
            top10, by_group, ai = brief.select(c, "2026-10-09", quiet)
            shown = set(top10["cluster_id"]) | set(ai["cluster_id"]) | {x for g in by_group.values() for x in g["cluster_id"]}
            self.assertNotIn("news:f96cc76a18212ba4", shown)
        c = self.clusters("2026-10-13")
        top10, _, _ = brief.select(c, "2026-10-13", quiet)
        self.assertEqual(len(top10), 10)
        self.assertLessEqual(int((top10["sector"] == "datacenter_power").sum()), 1)

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
        self.assertEqual(top10["sector"].nunique(), len(top10))


if __name__ == "__main__":
    unittest.main()

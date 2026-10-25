"""Session 470: the fixes of the Digest and Roundup audits of 21 October 2026 that need no ruling
(docs/reviews/digest-audit-2026-10-21.md and roundup-audit-2026-10-21.md, on wip/441-450-third).

No test here calls a model or reaches the network. The fixtures are small frames and files written by the test; the
tests on 2 and 9 October read warehouse/output/news_stories.csv and docs/digest/ as the repository holds them, and skip
where those are absent.
"""

import io
import os
import re
import sys
import tempfile
import unittest

import pandas as pd

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
for p in ("warehouse", os.path.join("warehouse", "news")):
    if os.path.join(ROOT, p) not in sys.path:
        sys.path.insert(0, os.path.join(ROOT, p))

import brief  # noqa: E402

GN = "https://news.google.com/rss/articles/CBMiabc"


def rec(cid, title, sector="nuclear", parties="", sig=7, ai=0, why="", mw="", price="", links=None):
    return {"cluster_id": cid, "titles": [title], "sector": sector, "parties": parties, "sig": sig, "ai": ai, "why": why,
            "mw": mw, "price": price, "n": 1, "first": "2026-10-02T00:00:00Z", "summary": "",
            "links": links or [("Outlet", f"https://example.org/{cid}")]}


def frame(*recs):
    return pd.DataFrame(list(recs))


class Quiet:
    def __init__(self):
        self.lines = []

    def __call__(self, msg):
        self.lines.append(msg)


class NoIssueLostToARepeat(unittest.TestCase):
    """Digest audit fix 3: 5 and 6 October were lost to assert_unique."""

    def test_two_new_policy_lines_of_one_title_keep_one(self):
        log = Quiet()
        new = ["- Exemptions from Materials Licensing (NRC notice, policy action): why [NRC](https://www.nrc.gov/a)",
               "- Exemptions from Materials Licensing (NRC notice, policy action): why [NRC](https://www.nrc.gov/b)"]
        out = brief.without_repeats(new, ["## By sector", ""], log)
        self.assertEqual(len(out), 1)
        self.assertTrue(any("dropped a repeat" in x for x in log.lines))

    def test_a_later_item_at_an_address_shown_above_is_dropped_and_the_issue_passes(self):
        doe = "https://www.energy.gov/articles/energy-department-announces-42-billion"
        L = ["## Top of the industry", "",
             "1. **First story** (oil)  ", f"   Why one. Sources: [Reuters](https://example.org/1)",
             "2. **Second story** (gas)  ", f"   Why two. Sources: [DOE]({doe})",
             "3. **Third story** (lng)  ", f"   Why three. Sources: [AP](https://example.org/3)",
             "", "## By sector", "", "**Policy**", "",
             f"- DOE announces 42 billion (DOE news release, policy action): why [DOE]({doe})",
             "", "## AI and power", "", "- no further story on AI and power today (any such story is listed above)"]
        with self.assertRaises(RuntimeError):
            brief.assert_unique(L)
        log = Quiet()
        out = brief.drop_repeated_items(L, log)
        self.assertEqual(brief.assert_unique(out), 3)
        self.assertEqual(len(log.lines), 1)
        self.assertIn("dropped a repeated item", log.lines[0])

    def test_a_dropped_top_item_takes_its_line_and_the_rest_are_numbered_again(self):
        L = ["1. **A** (oil)  ", "   Why. Sources: [X](https://example.org/1)",
             "2. **A** (oil)  ", "   Why. Sources: [Y](https://example.org/2)",
             "3. **C** (gas)  ", "   Why. Sources: [Z](https://example.org/3)"]
        out = brief.drop_repeated_items(L, Quiet())
        self.assertEqual([x for x in out if re.match(r"^\d+\. ", x)], ["1. **A** (oil)  ", "2. **C** (gas)  "])
        self.assertEqual(len(out), 4)

    def test_a_cluster_prints_an_address_once(self):
        s = pd.DataFrame([
            {"cluster_id": "c1", "sig": 7, "ai": 0, "sector": "oil", "why": "w", "mw": "", "price_mentioned": "",
             "parties": "", "event_date": "2026-10-06T01:00:00Z", "source": "DOE", "source_url": "https://doe.gov/x",
             "title": "t1", "summary": "s"},
            {"cluster_id": "c1", "sig": 6, "ai": 0, "sector": "oil", "why": "w", "mw": "", "price_mentioned": "",
             "parties": "", "event_date": "2026-10-06T02:00:00Z", "source": "DOE newsroom", "source_url": "https://doe.gov/x",
             "title": "t2", "summary": "s"}])
        c = brief.build_clusters(s)
        self.assertEqual(len(c.iloc[0]["links"]), 1)


# session 802: one topic (sector) one item in the top ten, so a fixture of ten distinct stories gives each its own sector
SECTORS = ["oil", "gas", "lng", "power_prices", "generation", "renewables", "storage", "transmission", "grid_conditions",
           "interconnection", "ppa", "policy"]


class OneEventOneItem(unittest.TestCase):
    """Digest audit fix 5, Roundup audit fix 1."""

    korea1 = rec("k1", "South Korea to invest in U.S. nuclear projects, including 8 large reactors",
                 parties="US Department of Commerce; South Korea", why="A $120 billion framework.", price="$200 billion")
    korea2 = rec("k2", "USA, South Korea targeting six AP1000 and two APR1400 units",
                 parties="US Department of Commerce; Westinghouse; South Korea", why="USD120 billion framework.")
    aramco1 = rec("a1", "Saudi Aramco Headquarters Hit as Houthi Attacks Escalate", sector="oil",
                  parties="Saudi Aramco; Houthis")
    aramco2 = rec("a2", "Aramco Headquarters Hit During Houthi Attack on Saudi Arabia", sector="oil",
                  parties="Aramco; Houthi")

    def test_the_named_pairs_are_one_event(self):
        self.assertTrue(brief.same_event(self.korea1, self.korea2))   # 2 October, top 1 and 2
        self.assertTrue(brief.same_event(self.aramco1, self.aramco2))  # 14 October, top 6 and 7

    def test_two_stories_that_share_a_large_party_and_a_round_sum_are_not(self):
        firmus = rec("f", "Nvidia-backed Firmus scraps $5 billion Australia IPO", sector="capital", parties="Firmus; Nvidia")
        dmatrix = rec("d", "Report: Nvidia plans to invest in inference chip startup d-Matrix", sector="other",
                      parties="Nvidia; d-Matrix", why="A $5 billion round.")
        self.assertFalse(brief.same_event(firmus, dmatrix))

    def test_two_market_reports_with_no_party_are_not(self):
        g1 = rec("g1", "Natural Gas Futures Hit a Speed Bump on the Road to Winter", sector="natural_gas")
        g2 = rec("g2", "Natural Gas Futures Forfeit Momentum as Weather Forecasts Lean Bearish", sector="natural_gas")
        self.assertFalse(brief.same_event(g1, g2))

    def test_a_dated_notice_is_not_one_event_by_its_date(self):
        n1 = rec("n1", "Agenda-Bi-weekly Market Update Oct 15, 2026", sector="other", parties="California ISO")
        n2 = rec("n2", "Market Design Initiative Updates - Oct 2026", sector="other", parties="California ISO")
        self.assertFalse(brief.same_event(n1, n2))

    def test_the_top_ten_keeps_ten_items_when_a_twin_is_left_out(self):
        # session 802: a sector each, and a party of its own word each ("Party1" and "Party2" are both the word "party")
        recs = [self.korea1, self.korea2] + [rec(f"x{i}", f"Distinct story number {i} about thing{i}", sector=SECTORS[i],
                                                 parties=f"Owner{chr(97 + i)}corp") for i in range(12)]
        log = Quiet()
        with tempfile.TemporaryDirectory() as d:
            top10, by_group, ai = brief.select(frame(*recs), "2026-10-02", log, folder=d)
        self.assertEqual(len(top10), 10)
        self.assertNotIn("k2", set(top10["cluster_id"]))
        self.assertTrue(any("the same event as k1" in x for x in log.lines))

    def test_unique_items_drops_a_later_cluster_at_any_shown_address(self):
        a = rec("a", "One", links=[("X", "https://e.org/1"), ("Y", "https://e.org/2")])
        b = rec("b", "Two", sector="oil", links=[("Z", "https://e.org/3"), ("Y", "https://e.org/2")])
        out = brief.unique_items({"top": frame(a), "ai": frame(b)}, {"a": "One", "b": "Two"}, Quiet())
        self.assertTrue(out["ai"].empty)


class NotTheDayBeforeAgain(unittest.TestCase):
    """Digest audit fix 4: Voltus's USD 225 million on 8, 9 and 12 October."""

    def issue(self, d, date, lines):
        with open(os.path.join(d, f"{date}.md"), "w", encoding="utf-8") as f:
            f.write("\n".join([f"# ERW's Energy Digest, {date}", "", "intro", "", "## By sector", ""] + lines) + "\n")

    def test_a_story_an_earlier_issue_printed_is_left_out(self):
        voltus = rec("v", "Voltus raises $225 million in anticipation of 20 GW demand flexibility portfolio",
                     sector="capital", parties="Voltus", why="Raises $225 million.", links=[("pv", "https://pv.example/v")])
        other = rec("o", "A different story entirely about pipelines", sector="natural_gas", parties="Kinder Morgan")
        with tempfile.TemporaryDirectory() as d:
            self.issue(d, "2026-10-08", ["- Voltus raises $225 million to scale BYOC for data centers (datacenter power): "
                                         "Capital for a demand-flexibility aggregator. [Latitude Media](https://lm.example/v)"])
            log = Quiet()
            out = brief.not_shown_before(frame(voltus, other), brief.earlier_issues("2026-10-09", folder=d), log)
        self.assertEqual(list(out["cluster_id"]), ["o"])
        self.assertIn("shown in an earlier Digest", log.lines[0])

    def test_a_new_sum_makes_it_news_again(self):
        priced = rec("p", "Voltus deal price disclosed at $300 million", sector="capital", parties="Voltus",
                     why="Valued at $300 million.", links=[("lm", "https://lm.example/v")])
        with tempfile.TemporaryDirectory() as d:
            self.issue(d, "2026-10-08", ["- Voltus raises $225 million (capital): why [Latitude Media](https://lm.example/v)"])
            out = brief.not_shown_before(frame(priced), brief.earlier_issues("2026-10-09", folder=d), Quiet())
        self.assertEqual(len(out), 1)

    def test_a_day_s_market_report_is_never_a_repeat_by_its_title(self):
        oil = rec("oil", "Oil Prices Climb Above $106 as Supply Risks Intensify", sector="oil", parties="")
        with tempfile.TemporaryDirectory() as d:
            self.issue(d, "2026-10-13", ["- Oil prices climb above $106 as supply risks intensify again (oil): why "
                                         "[Reuters](https://r.example/1)"])
            out = brief.not_shown_before(frame(oil), brief.earlier_issues("2026-10-14", folder=d), Quiet())
        self.assertEqual(len(out), 1)

    def test_only_the_seven_days_before_are_read(self):
        with tempfile.TemporaryDirectory() as d:
            for day in ("2026-09-30", "2026-10-01", "2026-10-08", "2026-10-09"):
                self.issue(d, day, [])
            got = [os.path.basename(p) for p in brief.earlier_issues("2026-10-09", folder=d)]
        self.assertEqual(got, ["2026-10-08.md"])


class TheAISection(unittest.TestCase):
    """Digest audit fix 16: 28 September listed two stories the scorer itself called commentary, at 3."""

    def test_commentary_under_5_is_left_out(self):
        recs = [rec(f"t{i}", f"Top story {i} with words{i}", sector=SECTORS[i], parties=f"Owner{chr(97 + i)}corp", sig=8)
                for i in range(10)]
        recs += [rec("ai3", "From data centers to AI factories", sector="datacenter_power", sig=3, ai=9),
                 rec("ai6", "Utility signs 300 MW data center contract", sector="datacenter_power", sig=6, ai=9,
                     parties="Utility Co")]
        with tempfile.TemporaryDirectory() as d:
            _, by_group, ai = brief.select(frame(*recs), "2026-09-28", Quiet(), folder=d)
        shown = set(ai["cluster_id"]) | {c for g in by_group.values() for c in g["cluster_id"]}
        self.assertNotIn("ai3", set(ai["cluster_id"]))
        self.assertIn("ai6", shown)


class Wording(unittest.TestCase):
    def test_a_google_news_address_says_where_it_goes(self):
        t = brief.link_text([("Reuters", GN), ("POWER", "https://www.powermag.com/x")], licensed=set())   # 803: no hold
        self.assertIn(f"[Reuters]({GN}) (via Google News)", t)
        self.assertNotIn("powermag.com/x) (via", t)

    def test_one_style_for_a_sum_of_money(self):
        cases = {"$45 Billion": "USD 45 billion", "$800MM": "USD 800 million", "C$14.3 Billion": "CAD 14.3 billion",
                 "US$2bn": "USD 2 billion", "$93.78 per barrel": "USD 93.78 per barrel", "USD120 billion": "USD 120 billion"}
        for a, b in cases.items():
            self.assertEqual(brief.money_style(a), b)

    def test_detail_prints_the_price_in_that_style(self):
        self.assertEqual(brief.detail({"mw": "", "price": "$4.3 Billion", "parties": ""}), "USD 4.3 billion. ")

    def test_the_adjectives_the_voice_cuts(self):
        self.assertEqual(brief.plain("A major 2 GW deal."), "A 2 GW deal.")
        self.assertEqual(brief.plain("Massive outage hits Texas. A significant expansion of a major utility."),
                         "Outage hits Texas. An expansion of a utility.")
        self.assertEqual(brief.plain("a huge uranium deal"), "a uranium deal")
        self.assertEqual(brief.plain("It significantly raises costs"), "It raises costs")
        self.assertEqual(brief.plain("No adjective here."), "No adjective here.")

    def test_the_real_time_price_is_named_for_a_reader(self):
        self.assertEqual(brief.rt_label("ercot", "spp_rtm"), "ERCOT's real-time settlement point price")
        self.assertEqual(brief.rt_label("nyiso", "lmp_rtm_15m_mean"), "NYISO's real-time locational marginal price")

    def test_the_real_time_line_still_reads_for_the_site_parser(self):
        # session 402's site/lib/digest.ts reads the variable in backticks after the interval's frequency
        line = ("**Highest real-time price, yesterday:** 512.30 USD/MWh at HB_NORTH (ERCOT), interval starting "
                "2026-10-07 17:00 local (2026-10-07 22:00 UTC), PT15M `spp_rtm`, "
                f"{brief.rt_label('ercot', 'spp_rtm')} [2].")
        rx = (r"^\*\*Highest real-time price[^*]*:\*\* (-?[\d,]+\.\d{2}) USD/MWh at (.+?) \(([A-Z-]+)\), interval starting "
              r".*?\((\d{4}-\d{2}-\d{2}) (\d{2}:\d{2}) UTC\), \S+ `([a-z0-9_]+)`(.*)$")
        self.assertEqual(re.match(rx, line).group(6), "spp_rtm")

    def test_miso_is_absent_because_it_is_paused(self):
        r = brief.paused_row("MISO")
        if r is None:
            self.skipTest("paused_sources.csv holds no MISO row")
        self.assertEqual(r["paused_on"], "2026-10-04")
        self.assertIsNone(brief.paused_row("ERCOT"))


import roundup  # noqa: E402
import email_digest  # noqa: E402

# EIA's closes (eia_fuel_spot_prices): 18 and 22 September as the table held them on portable-laptop (retrieved to
# 2026-09-22); 24 to 29 September as the Roundup audit of 21 October read them (roundup-audit, "How the numbers were
# traced"); 23 September is not in either and is left out
CLOSES = {"eia:wti_cushing": [("2026-09-18", 101.44), ("2026-09-22", 96.41), ("2026-09-24", 95.88), ("2026-09-25", 85.23),
                              ("2026-09-28", 99.37), ("2026-09-29", 96.16)],
          "eia:brent": [("2026-09-18", 119.66), ("2026-09-22", 114.89), ("2026-09-24", 120.92), ("2026-09-25", 116.01),
                        ("2026-09-28", 119.97), ("2026-09-29", 113.96)]}


def fuel_series():
    return {e: pd.DataFrame({"ts_utc": [pd.Timestamp(d, tz="UTC") for d, _ in v], "value": [x for _, x in v],
                             "unit": "USD/bbl"}) for e, v in CLOSES.items()}


class TheRoundup(unittest.TestCase):
    def test_the_fuel_change_is_a_week_not_two_trading_days(self):
        # W40 printed WTI +12.8 percent: 29 September against 25 September, one outlying close
        a, b, flags = roundup.fuel_change(fuel_series(), "eia:wti_cushing", pd.Timestamp("2026-10-05", tz="UTC"))
        self.assertEqual((f"{a['ts_utc']:%Y-%m-%d}", a["value"]), ("2026-09-29", 96.16))
        self.assertEqual((f"{b['ts_utc']:%Y-%m-%d}", b["value"]), ("2026-09-22", 96.41))
        self.assertEqual(flags, [])

    def test_an_outlying_close_is_flagged(self):
        a, b, flags = roundup.fuel_change(fuel_series(), "eia:wti_cushing", pd.Timestamp("2026-09-26", tz="UTC"))
        self.assertEqual(f"{a['ts_utc']:%Y-%m-%d}", "2026-09-25")
        self.assertEqual(len(flags), 1)
        self.assertIn("2026-09-25 moved -11.1% in a day while Brent moved -4.1%", flags[0])

    def test_no_two_closes_a_week_apart_is_none(self):
        s = fuel_series()
        s["eia:wti_cushing"] = s["eia:wti_cushing"].iloc[-2:]
        self.assertIsNone(roundup.fuel_change(s, "eia:wti_cushing", pd.Timestamp("2026-10-05", tz="UTC")))

    def test_the_policy_section_s_words(self):
        t = ("Sabine Pass Liquefaction, LLC, Sabine Pass Liquefaction Stage V, LLC, Sabine Crossing Pipeline, LLC, Cheniere "
             "Creole Trail Pipeline, L.P.; Notice of Availability of the Final Environmental Impact Statement for the "
             "Proposed Sabine Pass Stage 5 Expansion Project")
        self.assertEqual(roundup.policy_title(t), "Notice of Availability of the Final Environmental Impact Statement for "
                                                  "the Proposed Sabine Pass Stage 5 Expansion Project")
        self.assertEqual(roundup.policy_title("Short title; with a subject"), "Short title; with a subject")
        self.assertEqual(roundup.dockets("Docket No. CP24-75-001;Docket No. CP25-505-000"), "dockets CP24-75-001, CP25-505-000")
        self.assertNotIn("Docket", roundup.dockets("Docket No. CP24-75-001"))
        self.assertEqual(roundup.dated({"action_type": "press_release", "event_date": "2026-09-29T00:00:00Z"}),
                         "released 2026-09-29")
        self.assertEqual(roundup.dated({"action_type": "notice", "event_date": "2026-09-30"}), "published 2026-09-30")

    def test_every_deal_type_is_a_word(self):
        sys.path.insert(0, os.path.join(ROOT, "warehouse", "deals"))
        src = open(os.path.join(ROOT, "warehouse", "deals", "extract.py"), encoding="utf-8").read()
        types = re.findall(r'"([a-z_]+)"', re.search(r"DEAL_TYPES = \[(.*?)\]", src, re.S).group(1))
        for t in types:
            self.assertIn(t, roundup.DEAL_LABEL)
            self.assertNotIn("_", roundup.DEAL_LABEL[t])

    def test_the_week_before(self):
        self.assertEqual(roundup.previous_week(pd.Timestamp("2026-10-05", tz="UTC")), "2026-W40")
        self.assertEqual(roundup.previous_week(pd.Timestamp("2026-01-05", tz="UTC")), "2026-W01")


class TheEmail(unittest.TestCase):
    """Roundup audit fix 5 and Digest audit fix 17."""

    def test_the_roundup_email_carries_the_page_s_disclosures(self):
        p = os.path.join(ROOT, "docs", "roundup", "2026-W41.md")
        if not os.path.exists(p):
            self.skipTest("W41 is not here")
        _, _, text, body = email_digest.render(p, "roundup")
        self.assertIn("publishers' own titles", text)
        self.assertIn("1806 scored stories", text)
        self.assertIn("publishers' own titles", body)
        self.assertNotRegex(text, r"(?<![\w*])\*\S")

    def test_no_link_to_a_page_in_review(self):
        rel = {"/digest": "review", "/about": "review", "/board": "live"}
        self.assertFalse(email_digest.live("/digest/2026-10-20", rel))
        self.assertTrue(email_digest.live("/board?x=1", rel))
        self.assertFalse(email_digest.live("/nowhere", rel))
        self.assertEqual(email_digest.gate_links("see [the method](/about#digest) and [prices](/board)", rel),
                         "see the method and [prices](/board)")

    def test_while_every_page_is_in_review_the_email_links_github(self):
        p = os.path.join(ROOT, "docs", "digest", "2026-10-20.md")
        if not os.path.exists(p) or any(v == "live" for v in email_digest.release().values()):
            self.skipTest("a page is live, or the issue is not here")
        old = os.environ.get("SITE_URL")
        os.environ["SITE_URL"] = "https://erw-flame.vercel.app"
        try:
            _, _, text, body = email_digest.render(p, "daily")
        finally:
            if old is None:
                os.environ.pop("SITE_URL")
            else:
                os.environ["SITE_URL"] = old
        self.assertNotIn("erw-flame.vercel.app", text)
        self.assertNotIn("erw-flame.vercel.app", body)
        self.assertIn("github.com/SamuelEnrique/erw/blob/main/docs/digest/2026-10-20.md", text)

    def test_a_google_news_link_says_so_in_the_email(self):
        t, h = email_digest.story_list([{"head": "H", "why": "", "src": ("Reuters", GN)}])
        self.assertIn("Reuters (via Google News)", t[1])
        self.assertIn("</a> (via Google News)", h)


class TheFunFactAndTheChart(unittest.TestCase):
    def test_deaths_and_disasters_are_not_a_fun_fact(self):
        import funfact
        p = os.path.join(ROOT, "warehouse", "news", "facts", "items", "2026-10-14.json")
        if os.path.exists(p):
            import json
            item = json.load(open(p, encoding="utf-8"))
            self.assertTrue(any("not a fun fact" in x for x in funfact.check_record(item)))
        r = {"fact": "Pearl Street Station opened in 1882.", "second": "On this day in 1913 a colliery disaster claimed "
             "the lives of 439 miners.", "structure": "on_this_day", "sources": []}
        self.assertTrue(any("not a fun fact" in x for x in funfact.check_record(r)))
        ok = {"fact": "Pearl Street Station opened in 1882.", "second": "", "structure": "none", "sources": []}
        self.assertFalse(any("not a fun fact" in x for x in funfact.check_record(ok)))

    def test_the_bank_holds_no_grave_fact(self):
        import csv
        import funfact
        p = os.path.join(ROOT, "warehouse", "news", "facts", "bank.csv")
        if not os.path.exists(p):
            self.skipTest("the bank is not here")
        rows = list(csv.DictReader(open(p, encoding="utf-8")))
        self.assertEqual([r["fact"][:60] for r in rows if funfact.GRAVE.search(r["fact"] + " " + (r.get("second") or ""))], [])

    def test_the_peak_premium_fact_states_its_hours(self):
        sys.path.insert(0, os.path.join(ROOT, "warehouse", "analysis"))
        from templates import peak_premium_block as ppb
        self.assertEqual(ppb.BLOCK_HOURS["midday"], "midday (12:00 to 15:59 local)")
        for b, rule in ppb.BLOCKS.items():
            hours = [h for h in range(24) if bool(rule(pd.Series([h])).iloc[0])]
            first, last = re.search(r"(\d{2}):00 to (\d{2}):59", ppb.BLOCK_HOURS[b]).groups()
            self.assertEqual(hours[0] if b != "overnight" else 21, int(first))
            self.assertEqual((hours[-1] if b != "overnight" else 11), int(last))


def stories():
    path = os.path.join(ROOT, "warehouse", "output", "news_stories.csv")
    if not os.path.exists(path):
        return None
    with open(path, encoding="utf-8") as f:
        body = "".join(ln for ln in f if not ln.startswith("#"))
    return pd.read_csv(io.StringIO(body), dtype=str, keep_default_na=False)


def window_of(date):
    with open(os.path.join(ROOT, "docs", "digest", f"{date}.md"), encoding="utf-8") as f:
        m = re.search(r"for the (\d+) hours to (\d{4}-\d{2}-\d{2} \d{2}:\d{2}) UTC", f.read())
    return int(m.group(1)), pd.Timestamp(m.group(2), tz="UTC")


class TheNamedDays(unittest.TestCase):
    """The audits' named days, their selection rebuilt from the stories as the repository holds them, no model."""

    @classmethod
    def setUpClass(cls):
        cls.s = stories()
        if cls.s is None or not os.path.exists(os.path.join(ROOT, "docs", "digest", "2026-10-02.md")):
            raise unittest.SkipTest("news_stories.csv or the issues are not here")

    def clusters(self, date):
        hours, now = window_of(date)
        when = pd.to_datetime(self.s["event_date"], utc=True, format="ISO8601")
        s = self.s[(self.s["scored_at"] != "") & (when >= now - pd.Timedelta(hours=hours)) & (when <= now)].copy()
        s["sig"] = s["significance"].astype(int)
        s["ai"] = s["ai_power_relevance"].astype(int)
        return brief.build_clusters(s[s["sig"] > 0])

    def test_2_october_shows_korea_s_framework_once(self):
        c = self.clusters("2026-10-02")
        if not {"news:8470c320a7225474", "news:ec41f0a2f9b34be4"} <= set(c["cluster_id"]):
            self.skipTest("the 2 October clusters are not as scored on 21 October")
        top10, _, _ = brief.select(c, "2026-10-02", Quiet())
        ids = set(top10["cluster_id"])
        # once: since session 2701 (rulings item 4: outlets, then time, break a tie) either twin may be the one kept
        self.assertEqual(len({"news:8470c320a7225474", "news:ec41f0a2f9b34be4"} & ids), 1)
        self.assertEqual(len(top10), 10)

    def test_9_october_leaves_out_voltus_shown_on_8_october(self):
        c = self.clusters("2026-10-09")
        if "news:f96cc76a18212ba4" not in set(c["cluster_id"]):
            self.skipTest("the 9 October clusters are not as scored on 21 October")
        log = Quiet()
        top10, by_group, ai = brief.select(c, "2026-10-09", log)
        shown = set(top10["cluster_id"]) | set(ai["cluster_id"]) | {x for g in by_group.values() for x in g["cluster_id"]}
        self.assertNotIn("news:f96cc76a18212ba4", shown)


if __name__ == "__main__":
    unittest.main()

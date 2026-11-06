"""Session 802: one topic, one item, the rest below (docs/reviews/periodicals-plan-2026-10-23.md, Digest change 2).

At most one item a topic in "Top of the industry" (brief.same_topic: the scorer's sector, or a party in common and
TOPIC_WORDS title words); a later cluster of a topic already in the ten folds under its item as an "also" line with its
outlet (brief.one_per_topic, at most ALSO_MAX an item), so no story is lost. The Roundup's weekend and five of the week take
the same rule. Proved on fixtures and, where the repository holds them, on the saved stories of the 13 issues (no model).
"""

import io
import os
import re
import sys
import unittest

import pandas as pd

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
for p in ("warehouse", os.path.join("warehouse", "news")):
    if os.path.join(ROOT, p) not in sys.path:
        sys.path.insert(0, os.path.join(ROOT, p))

import brief  # noqa: E402
import email_digest  # noqa: E402
import roundup  # noqa: E402


def rec(cid, title, sector="nuclear", parties="", sig=7, ai=0, why="Why.", mw="", price="", links=None):
    return {"cluster_id": cid, "titles": [title], "sector": sector, "parties": parties, "sig": sig, "ai": ai, "why": why,
            "mw": mw, "price": price, "n": 1, "first": "2026-10-21T00:00:00Z", "summary": "",
            "links": links or [("Outlet", f"https://example.org/{cid}")]}


def frame(*recs):
    return pd.DataFrame(list(recs))


class Quiet:
    def __init__(self):
        self.lines = []

    def __call__(self, msg):
        self.lines.append(msg)


class OneTopic(unittest.TestCase):
    def test_one_sector_is_one_topic(self):
        self.assertTrue(brief.same_topic(rec("a", "Anthropic may spend", "datacenter_power", "Anthropic"),
                                         rec("b", "Amazon pledges", "datacenter_power", "Amazon")))

    def test_two_sectors_with_a_party_and_two_title_words_are_one_topic(self):
        a = rec("a", "Saudi Aramco headquarters hit as Houthi attacks escalate", "oil", "Saudi Aramco; Houthis")
        b = rec("b", "Houthi strike hits building at Saudi Aramco headquarters", "geopolitics", "Saudi Aramco; Houthis")
        self.assertTrue(brief.same_topic(a, b))

    def test_two_sectors_without_a_party_in_common_are_not(self):
        self.assertFalse(brief.same_topic(rec("a", "Oil jumps on Hormuz attacks", "oil", "Iran"),
                                          rec("b", "Hormuz tanker rates triple", "geopolitics", "Goldman Sachs")))

    def test_the_constants_say_their_reasoning(self):
        self.assertEqual(brief.TOPIC_WORDS, 2)
        self.assertEqual(brief.ALSO_MAX, 3)
        src = open(brief.__file__, encoding="utf-8").read()
        self.assertIn("TOPIC_WORDS content", src)
        self.assertIn("ALSO_MAX stories", src)


class TheFold(unittest.TestCase):
    def clusters(self):
        return frame(rec("d1", "Anthropic may spend 750 billion", "datacenter_power", "Anthropic", sig=9),
                     rec("d2", "Amazon pledges 16 billion in Germany", "datacenter_power", "Amazon", sig=8),
                     rec("g1", "UK approves Jackdaw gas field", "gas", "UK", sig=8),
                     rec("d3", "Nextdc cuts outlook as backlash delays power", "datacenter_power", "Nextdc", sig=7),
                     rec("n1", "Six AP1000 reactors proposed in Kentucky", "nuclear", "The Nuclear Company", sig=7),
                     rec("d4", "Crusoe plans modular data center", "datacenter_power", "Crusoe", sig=7),
                     rec("d5", "Georgia cooperative plans 50 MW home batteries", "datacenter_power", "Georgia EMC", sig=6),
                     rec("o1", "Brent at 110 as Hormuz worries persist", "oil", "", sig=7))

    def test_one_item_a_topic_and_the_rest_fold_under_it(self):
        log = Quiet()
        top, folded = brief.one_per_topic(self.clusters(), 3, log)
        self.assertEqual(list(top["cluster_id"]), ["d1", "g1", "n1"])
        # d4 ranks after the third topic filled the three: it is not folded, and stays for the sections below
        self.assertEqual([x["cluster_id"] for x in brief.also_of(top.to_dict("records")[0])], ["d2", "d3"])
        self.assertEqual(folded, {"d2", "d3"})
        self.assertTrue(any("folded under d1" in x for x in log.lines))

    def test_past_also_max_a_story_is_left_for_the_sections_below(self):
        log = Quiet()
        top, folded = brief.one_per_topic(self.clusters(), 4, log)
        self.assertEqual(list(top["cluster_id"]), ["d1", "g1", "n1", "o1"])
        self.assertNotIn("d5", folded)
        self.assertTrue(any("left for the sections below" in x and "d5" in x for x in log.lines))

    def test_the_select_marks_folded_clusters_as_used(self):
        top10, by_group, ai = brief.select(self.clusters(), "2026-10-21", Quiet(), folder=os.devnull)
        shown = set(top10["cluster_id"]) | {x for g in by_group.values() for x in g["cluster_id"]} | set(ai["cluster_id"])
        self.assertEqual(len(top10), 4)   # four topics among the eight clusters
        self.assertNotIn("d2", shown)
        self.assertIn("d5", {x for g in by_group.values() for x in g["cluster_id"]})   # the fifth of the topic, below

    def test_an_empty_frame(self):
        top, folded = brief.one_per_topic(self.clusters().head(0), 10, Quiet())
        self.assertEqual(len(top), 0)
        self.assertEqual(folded, set())


class TheAlsoLine(unittest.TestCase):
    def test_the_lines_of_an_item(self):
        r = dict(rec("d1", "T", "datacenter_power"), also=[
            {"cluster_id": "d2", "title": "Amazon pledges 16 billion in Germany.", "sector": "datacenter_power",
             "links": [("Data Center Dynamics", "https://example.org/d2")], "parties": "Amazon"},
            {"cluster_id": "d3", "title": "Nextdc cuts outlook", "sector": "datacenter_power",
             "links": [("Reuters", "https://news.google.com/rss/articles/x")], "parties": "Nextdc"}])
        brief._LICENSED[brief.LICENSE_FILE] = set()   # session 803: the form without the license hold
        try:
            L = brief.item_lines(r, "1. **Head** (datacenter power)  ", "Why. parties: A. ", "Sources: [O](https://example.org/d1)")
        finally:
            brief._LICENSED.pop(brief.LICENSE_FILE, None)
        self.assertEqual(L[0], "1. **Head** (datacenter power)  ")
        self.assertEqual(L[1], "   Why. parties: A. Sources: [O](https://example.org/d1)  ")
        self.assertTrue(L[1].endswith("Sources: [O](https://example.org/d1)  "))
        self.assertEqual(L[2], "   Also on this topic: Amazon pledges 16 billion in Germany ([Data Center Dynamics](https://example.org/d2)); "
                               "Nextdc cuts outlook ([Reuters](https://news.google.com/rss/articles/x) (via Google News)).")
        self.assertNotIn(chr(0x2014), L[2])

    def test_no_also_line_without_folded_stories(self):
        L = brief.item_lines(rec("a", "T"), "1. **Head** (oil)  ", "Why.", "Sources: [O](u)")
        self.assertEqual(len(L), 2)
        self.assertFalse(L[1].endswith("  "))

    def test_the_hard_check_counts_the_also_line_s_addresses(self):
        L = ["1. **A** (oil)  ", "   Why. Sources: [X](https://example.org/1)  ",
             "   Also on this topic: B ([Y](https://example.org/2)).",
             "2. **C** (gas)  ", "   Why. Sources: [Z](https://example.org/2)"]
        with self.assertRaises(RuntimeError):
            brief.assert_unique(L)
        out = brief.drop_repeated_items(L, Quiet())
        self.assertEqual(brief.assert_unique(out), 1)

    def test_a_dropped_item_takes_its_also_line_with_it(self):
        L = ["1. **A** (oil)  ", "   Why. Sources: [X](https://example.org/1)",
             "2. **A** (oil)  ", "   Why. Sources: [Y](https://example.org/9)  ", "   Also on this topic: B ([Z](https://example.org/3)).",
             "3. **C** (gas)  ", "   Why. Sources: [W](https://example.org/4)"]
        out = brief.drop_repeated_items(L, Quiet())
        self.assertEqual(len(out), 4)
        self.assertFalse(any("Also on this topic" in x for x in out))

    def test_a_folded_story_counts_as_shown_the_next_day(self):
        import tempfile
        with tempfile.TemporaryDirectory() as d:
            with open(os.path.join(d, "2026-10-20.md"), "w", encoding="utf-8") as f:
                f.write("# ERW's Energy Digest, 2026-10-20\n\n## Top of the industry\n\n"
                        "1. **Head** (oil)  \n   Why. parties: Iran. Sources: [X](https://example.org/1)  \n"
                        "   Also on this topic: Voltus raises USD 225 million ([Y](https://example.org/voltus)).\n")
            items = brief.issue_items([os.path.join(d, "2026-10-20.md")])
            self.assertEqual(len(items), 1)
            self.assertIn("https://example.org/voltus", items[0]["urls"])
            self.assertIn(("usd", 225), items[0]["figs"])
            c = frame(rec("v", "Voltus raises $225 million", "capital", "Voltus", links=[("Y", "https://example.org/voltus")]))
            kept = brief.not_shown_before(c, [os.path.join(d, "2026-10-20.md")], Quiet())
            self.assertEqual(len(kept), 0)

    def test_the_email_keeps_the_why_line_not_the_also_line(self):
        lines = ["# ERW's Energy Digest, 2026-10-21", "", "## Top of the industry", "",
                 "1. **Head** (oil)  ", "   The why. Sources: [X](https://example.org/1)  ",
                 "   Also on this topic: B ([Y](https://example.org/2)).", "", "## By sector"]
        items = email_digest.numbered(lines, ("## Top of the industry",))
        self.assertEqual(items[0]["why"], "The why.")
        self.assertEqual(items[0]["src"], ("X", "https://example.org/1"))

    def test_unique_items_drops_a_folded_story_at_an_address_shown_above(self):
        top = frame(dict(rec("a", "A", "oil", links=[("O", "https://example.org/a")]), also=[
            {"cluster_id": "b", "title": "B", "sector": "oil", "links": [("O", "https://example.org/a")], "parties": ""}]))
        secs = brief.unique_items({"top": top}, {"a": "A head"}, Quiet())
        self.assertEqual(brief.also_of(secs["top"].to_dict("records")[0]), [])


class TheRoundupTakesIt(unittest.TestCase):
    def test_the_source_folds_the_weekend_and_the_five(self):
        import inspect
        src = inspect.getsource(roundup.main)
        self.assertIn('brief.one_per_topic(wk_c, WEEKEND_N, log, "the weekend")', src)
        self.assertIn('brief.one_per_topic(rest, 5, log, "the five of the week")', src)
        self.assertEqual(src.count("brief.item_lines("), 2)


def stories():
    path = os.path.join(ROOT, "warehouse", "output", "news_stories.csv")
    if not os.path.exists(path):
        return None
    with open(path, encoding="utf-8") as f:
        body = "".join(ln for ln in f if not ln.startswith("#"))
    return pd.read_csv(io.StringIO(body), dtype=str, keep_default_na=False)


class TheNamedDays(unittest.TestCase):
    """13 October 2026 held five datacenter items in its top ten; by selection alone (no model) it now holds one, with the
    rest folded under it, and the day's top ten still has ten items."""

    @classmethod
    def setUpClass(cls):
        cls.s = stories()
        if cls.s is None or not os.path.exists(os.path.join(ROOT, "docs", "digest", "2026-10-13.md")):
            raise unittest.SkipTest("news_stories.csv or the issues are not here")

    def clusters(self, date):
        with open(os.path.join(ROOT, "docs", "digest", f"{date}.md"), encoding="utf-8") as f:
            m = re.search(r"for the (\d+) hours to (\d{4}-\d{2}-\d{2} \d{2}:\d{2}) UTC", f.read())
        hours, now = int(m.group(1)), pd.Timestamp(m.group(2), tz="UTC")
        when = pd.to_datetime(self.s["event_date"], utc=True, format="ISO8601")
        s = self.s[(self.s["scored_at"] != "") & (when >= now - pd.Timedelta(hours=hours)) & (when <= now)].copy()
        s["sig"] = s["significance"].astype(int)
        s["ai"] = s["ai_power_relevance"].astype(int)
        return brief.build_clusters(s[s["sig"] > 0])

    def test_13_october_holds_one_datacenter_item_in_its_top_ten(self):
        c = self.clusters("2026-10-13")
        if len(c) < 20:
            self.skipTest("the 13 October clusters are not as scored on 21 October")
        top10, _, _ = brief.select(c, "2026-10-13", Quiet())
        self.assertEqual(len(top10), 10)
        self.assertLessEqual(int((top10["sector"] == "datacenter_power").sum()), 1)
        self.assertEqual(top10["sector"].nunique(), 10)


if __name__ == "__main__":
    unittest.main()

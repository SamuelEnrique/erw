"""Audit of the Digest and the Roundup, finding 7 (session 10235, docs/reviews/digest-model-audit-2026-11-26.md): beside a
story's figure the Digest names the outlet of the cluster's first link and the date of the cluster's earliest story
(brief.opening_lines and brief.story_row print r["first"], the cluster's first event_date), so when the scorer joined
an earlier story of another outlet to the cluster, the outlet is given a date it did not report on. The Digest of 12
November, by the stored rows of warehouse/output/news_stories.csv:

  the opening number: "SpaceX plans USD 74 billion ..., as Bloomberg.com reported on 2026-11-11": Bloomberg's story is of
    2026-11-12 17:28 UTC; 2026-11-11 is Hart Energy's "SpaceX Plans $24B Texas Power Project" (another figure), the
    cluster's first story;
  the numbers, Policy, capital or reliability: "Deal value: USD 2.1 billion (Strathcona, Greenfire; JPT Homepage,
    2026-11-11)": JPT's story is of 2026-11-12 18:01 UTC; 2026-11-11 is Hart Energy's "$2B" story.

The tests rebuild both clusters from those rows (titles, outlets, dates, scores as stored) with brief.build_clusters and
write the opening and the block row with the brief's own functions, no model, no network. They pass on main. Printing
the named outlet's own date changes what an issue says, so it is for Samuel's ruling."""
import os
import sys
import unittest

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
for p in ("warehouse", os.path.join("warehouse", "news")):
    if os.path.join(ROOT, p) not in sys.path:
        sys.path.insert(0, os.path.join(ROOT, p))


def story(eid, date, source, url, title, sig, price="", sector="datacenter_power", parties=""):
    return {"event_id": eid, "cluster_id": CL[eid], "event_date": date, "source": source, "source_url": url, "title": title,
            "summary": f"{title} {source}", "sig": sig, "ai": 5, "sector": sector, "region": "Texas", "why": "", "mw": "",
            "price_mentioned": price, "parties": parties}


CL = {"news:d824995d3d0b202d": "news:d824995d3d0b202d", "news:64c28dd916cdf441": "news:d824995d3d0b202d",
      "news:808f73a07b2ad109": "news:808f73a07b2ad109", "news:f3e71677b34cfdb7": "news:808f73a07b2ad109"}
SPACEX = [story("news:d824995d3d0b202d", "2026-11-11T00:21:28Z", "Hart Energy", "https://news.google.com/rss/articles/hart",
                "SpaceX Plans $24B Texas Power Project to Fuel Computing Ambitions", 7, "$24B"),
          story("news:64c28dd916cdf441", "2026-11-12T17:28:48Z", "Bloomberg.com", "https://news.google.com/rss/articles/bloomberg",
                "SpaceX Plans $74 Billion Data Center Projects in Arizona, Texas", 9, "$74 billion")]
STRATHCONA = [story("news:808f73a07b2ad109", "2026-11-11T04:52:11Z", "Hart Energy", "https://news.google.com/rss/articles/hart2",
                    "Strathcona's $2B Greenfire Deal Leaves Few Oil Sands Targets Standing", 6, "$2B", "deal", "Strathcona; Greenfire"),
              story("news:f3e71677b34cfdb7", "2026-11-12T18:01:03Z", "JPT Homepage", "https://news.google.com/rss/articles/jpt",
                    "Strathcona Pursues Growth With $2.1 Billion Greenfire Deal", 7, "$2.1 billion", "deal", "Strathcona; Greenfire")]


def clusters(rows):
    try:
        import brief  # noqa: E402
        import pandas as pd
    except ImportError as exc:
        raise unittest.SkipTest(f"brief does not import here: {exc}")
    df = pd.DataFrame(rows)
    df["event_date"] = pd.to_datetime(df["event_date"], utc=True)
    return brief, brief.build_clusters(df).to_dict("records")


class TheOutletIsGivenTheClustersFirstDate(unittest.TestCase):
    def test_the_opening_gives_bloomberg_hart_energys_date(self):
        brief, recs = clusters(SPACEX)
        r = recs[0]
        self.assertEqual(r["links"][0][0], "Bloomberg.com")   # the lead story's outlet is named
        op = {"kind": "story", "key": f"story:{r['cluster_id']}", "rec": r, "figure": "USD 74 billion", "rank": 1}
        heads = {r["cluster_id"]: "SpaceX plans USD 74 billion in data center projects in Arizona and Texas"}
        line = brief.opening_lines(op, heads)[2]
        self.assertIn("as Bloomberg.com reported on 2026-11-11", line)   # Bloomberg's own story is of 2026-11-12

    def test_the_block_row_gives_jpt_hart_energys_date(self):
        brief, recs = clusters(STRATHCONA)
        line, _ = brief.story_row("Policy, capital or reliability", recs, brief.CAPITAL_SECTORS, {}, None,
                                  "a policy or capital figure", ("money",))
        self.assertIn("JPT", line)
        self.assertIn("2026-11-11)", line)   # JPT's own story is of 2026-11-12


if __name__ == "__main__":
    unittest.main()

"""Session 1908: the open part of the Roundup's faults file row 63 (docs/reviews/periodicals-faults-2026-11-05.md), proved on
fixtures and on the stored Digests of docs/digest/ (in git). No model call, no network, no warehouse table read.

Row 63, the line: "AEP and Google advance a USD 4 billion, 702 MW Bloom Energy fuel-cell project in Cheyenne" / "What the
evidence does not establish: the 702 MW is the outlet's figure, not a warehouse table's; one outlet has reported it so far."
The fix asked: "`evidence_gap` reads `energy_deals` (and the earlier issues' items) before it writes 'not a warehouse
table's' or 'one outlet'". Session 1894 read energy_deals; the earlier issues' items were left open. Now, where no row of
energy_deals matches, an earlier Digest's item with two of the story's parties and the same MW (else the same sum) makes the
story a step: "A step in a story first carried before this week: the Digest of 2026-10-14, item 1 ("Google signs 20-year
PPA with AEP for 702 MW Wyoming fuel cell project")."; the item ranks below the week's first reports."""

import os
import sys
import tempfile
import unittest

import pandas as pd

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
sys.path.insert(0, os.path.join(ROOT, "warehouse", "news"))
import roundup  # noqa: E402

START = pd.Timestamp("2026-11-02", tz="UTC")
STORY = dict(cluster_id="news:aep", parties="AEP; Google", mw="702", price="$4 billion", outlets=1, kind="event", why="",
             titles=["AEP and Google advance Bloom Energy fuel-cell project in Cheyenne"])
HEAD = "AEP and Google advance a USD 4 billion, 702 MW Bloom Energy fuel-cell project in Cheyenne"
ISSUE = """# ERW Energy Digest, 14 October 2026

## Top of the industry

1. **Google signs 20-year PPA with AEP for 702 MW Wyoming fuel cell project** (ppa)
   Major datacenter power deal: 702MW fuel cell capacity under long-term contract. 702 MW; $4 billion; parties: Google; AEP; Bloom Energy. Sources: [Data Center Dynamics](https://example.com/a)
2. **Taiwan commits up to $4.4 Billion to Alaska LNG, Trump says, with 30% of output** (lng)
   Major LNG offtake commitment from Taiwan for 20-year supply agreement $4.4 Billion; parties: Taiwan; Trump; Alaska LNG. Sources: [OilPrice.com](https://example.com/b)
3. **Brent trades at $106.37 per barrel as Iran threatens more tanker strikes** (oil)
   Geopolitical supply risk drives significant crude price move. $106.37; parties: Iran. Sources: [OilPrice.com](https://example.com/c)
"""
LINE = ('A step in a story first carried before this week: the Digest of 2026-10-14, item 1 ("Google signs 20-year PPA with AEP '
        'for 702 MW Wyoming fuel cell project").')


def folder(files):
    d = tempfile.mkdtemp()
    for name, text in files.items():
        with open(os.path.join(d, name), "w", encoding="utf-8") as f:
            f.write(text)
    return d


class TheItems(unittest.TestCase):
    def test_an_item_s_fields_are_read(self):
        items = roundup.issue_items(ISSUE)
        self.assertEqual([(n, mw, usd) for n, _, _, mw, usd in items], [(1, 702.0, 4e9), (2, None, 4.4e9)])
        self.assertEqual(items[0][2], {"google", "aep", "bloom energy"})

    def test_an_item_with_no_quantity_is_not_kept(self):
        self.assertNotIn(3, [n for n, *_ in roundup.issue_items(ISSUE)])

    def test_only_dated_digests_are_read(self):
        ix = roundup.issue_index(folder({"2026-10-14.md": ISSUE, "latest.md": ISSUE}))
        self.assertEqual({x[4]["date"] for x in ix}, {"2026-10-14"})

    def test_no_folder_no_index(self):
        self.assertEqual(roundup.issue_index(os.path.join(tempfile.mkdtemp(), "none")), [])


class TheStep(unittest.TestCase):
    def ix(self):
        return roundup.issue_index(folder({"2026-10-14.md": ISSUE}))

    def test_the_w45_story_is_a_step_in_the_digest_s_item(self):
        d = roundup.prior_item(STORY, self.ix(), START)
        self.assertEqual((d["date"], d["n"]), ("2026-10-14", 1))
        self.assertEqual(roundup.step_line(d), LINE)

    def test_the_gap_after_the_fix(self):
        d = roundup.prior_item(STORY, self.ix(), START)
        self.assertEqual(roundup.evidence_gap(STORY, HEAD, d),
                         LINE + " What the evidence does not establish: what the week's step changes in that story; the 702 MW "
                                "is the outlets' figure, not a warehouse table's.")

    def test_an_issue_of_the_week_or_later_is_not_earlier(self):
        self.assertIsNone(roundup.prior_item(STORY, self.ix(), pd.Timestamp("2026-10-14", tz="UTC")))

    def test_one_party_in_common_is_not_a_step(self):
        self.assertIsNone(roundup.prior_item(dict(STORY, parties="Google; Microsoft"), self.ix(), START))

    def test_another_quantity_is_not_a_step(self):
        self.assertIsNone(roundup.prior_item(dict(STORY, mw="900"), self.ix(), START))

    def test_the_table_s_row_still_comes_first(self):
        deal = {"event_date": "2026-10-14", "buyer": "Google", "seller": "AEP", "asset": "Wyoming fuel cell project", "mw": "702",
                "dollars": "4000000000", "deal_type": "ppa", "term_years": "20"}
        gap = roundup.evidence_gap(STORY, HEAD, deal)
        self.assertTrue(gap.startswith("A step in a deal first reported before this week: in `energy_deals` since 2026-10-14"), gap)

    def test_more_says_the_step(self):
        d = roundup.prior_item(STORY, self.ix(), START)
        self.assertIn(LINE, roundup.more_why(STORY, {"news:aep": HEAD}, {"news:aep": d}))

    def test_a_step_ranks_below_the_first_reports(self):
        c = pd.DataFrame([{"cluster_id": "news:aep"}, {"cluster_id": "news:new"}])
        d = roundup.prior_item(STORY, self.ix(), START)
        self.assertEqual(list(roundup.first_reports_first(c, {"news:aep": d})["cluster_id"]), ["news:new", "news:aep"])

    def test_the_stored_digest_of_14_october(self):
        ix = roundup.issue_index()
        if not any(x[4]["date"] == "2026-10-14" for x in ix):
            self.skipTest("docs/digest/2026-10-14.md is not in this copy")
        d = roundup.prior_item(STORY, ix, START)
        self.assertEqual(roundup.step_line(d), LINE)

    def test_main_reads_the_digests_where_no_row_matches(self):
        with open(os.path.join(ROOT, "warehouse", "news", "roundup.py"), encoding="utf-8") as f:
            src = f.read()
        a, b = src.index("d = prior_deal(r, deal_ix, start)"), src.index("d = prior_item(r, item_ix, start)")
        self.assertLess(a, b)
        self.assertLess(b, src.index("clusters = first_reports_first(clusters, steps)"))


if __name__ == "__main__":
    unittest.main()

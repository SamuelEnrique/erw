"""Session 1894: the Roundup's fault of W45 in docs/reviews/periodicals-faults-2026-11-05.md, row 63, proved on fixtures.

Row 63, the line: "AEP and Google advance a USD 4 billion, 702 MW Bloom Energy fuel-cell project in Cheyenne" / "What the
evidence does not establish: the 702 MW is the outlet's figure, not a warehouse table's; one outlet has reported it so far."
The fault: "Not the week's news, and both halves of the limitation false: the deal was the Digest of 14 October's first
item ... and is in `energy_deals` (Google and AEP, Wyoming fuel cell project, 702 MW, USD 4 billion, dated 2026-10-14,
confidence 0.85). The week's top development is a step in a month-old deal."
The fix: "AEP and Google advance their Cheyenne fuel-cell project (first reported 2026-10-14: 702 MW, USD 4 billion, a
20-year purchase agreement; `energy_deals`)", ranked below developments first reported this week; `evidence_gap` reads
`energy_deals` ... before it writes "not a warehouse table's" or "one outlet"."

The code: roundup.deal_index and roundup.prior_deal find the held deal (two or more shared parties, the same MW or sum, a
date before the week); roundup.evidence_gap says the step with the row's date and figures; roundup.first_reports_first
ranks the week's first reports above a step in What mattered; roundup.more_why says the step under More. No model call,
no network, no warehouse table read: every frame is written here."""

import os
import sys
import unittest

import pandas as pd

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
sys.path.insert(0, os.path.join(ROOT, "warehouse", "news"))
import brief  # noqa: E402
import roundup  # noqa: E402

UTC = "UTC"
START = pd.Timestamp("2026-11-02", tz=UTC)

# the energy_deals row W45's first item is a step in (deal:c9b891f5c1a59116, its cells as the table holds them)
HELD = dict(event_id="deal:c9b891f5c1a59116", event_date="2026-10-14T12:40:03Z", parties="Google;AEP;Bloom Energy", mw="702",
            deal_type="ppa", buyer="Google", seller="AEP", other_parties="Bloom Energy", asset="Wyoming fuel cell project",
            state="WY", country="", dollars="4000000000", term_years="20", confidence="0.85", buyer_name="Google",
            seller_name="American Electric Power", buyer_parent="", seller_parent="")
# the W45 cluster, as build_clusters writes it from the Data Center Frontier story of 4 November
STEP = dict(cluster_id="news:ba054773bb4b12df", parties="AEP; Google; Bloom Energy", mw="702", price="$4 Billion", outlets=1,
            kind="event", why="Gigawatt-scale hyperscale power deal combining fuel cells, natural gas, and private microgrid "
                              "infrastructure for datacenter demand.",
            titles=["AEP, Google Advance $4 Billion Fuel-Cell Project to Power Cheyenne Data Centers"])
HEAD = "AEP and Google advance a USD 4 billion, 702 MW Bloom Energy fuel-cell project in Cheyenne"
OLD_GAP = ("What the evidence does not establish: the 702 MW is the outlet's figure, not a warehouse table's; one outlet has "
           "reported it so far.")
NEW_GAP = ("A step in a deal first reported before this week: in `energy_deals` since 2026-10-14 (Google and AEP, Wyoming fuel "
           "cell project, 702 MW, USD 4 billion, a 20-year power purchase agreement). What the evidence does not establish: "
           "what the week's step changes in that deal.")


def index(*rows):
    return roundup.deal_index(pd.DataFrame(list(rows)))


class Row63TheHeldDealIsFound(unittest.TestCase):
    def test_the_w45_story_is_a_step_in_the_october_deal(self):
        d = roundup.prior_deal(STEP, index(HELD), START)
        self.assertIsNotNone(d)
        self.assertEqual(d["event_id"], "deal:c9b891f5c1a59116")

    def test_a_deal_dated_in_the_week_is_not_an_earlier_one(self):
        self.assertIsNone(roundup.prior_deal(STEP, index(dict(HELD, event_date="2026-11-04T18:29:06Z")), START))

    def test_another_quantity_is_another_deal(self):
        self.assertIsNone(roundup.prior_deal(STEP, index(dict(HELD, mw="450")), START))

    def test_one_shared_party_is_not_the_same_parties(self):
        self.assertIsNone(roundup.prior_deal(STEP, index(dict(HELD, parties="Google;Bloom", buyer="Google", seller="NextEra",
                                                                other_parties="", seller_name="NextEra")), START))

    def test_the_sum_matches_when_no_mw_is_stated(self):
        d = roundup.prior_deal(dict(STEP, mw=""), index(HELD), START)
        self.assertEqual(d["event_id"], "deal:c9b891f5c1a59116")
        self.assertIsNone(roundup.prior_deal(dict(STEP, mw="", price="$3 billion"), index(HELD), START))

    def test_a_row_under_the_floor_is_not_read(self):
        self.assertIsNone(roundup.prior_deal(STEP, index(dict(HELD, confidence="0.55")), START))

    def test_the_earliest_row_wins(self):
        later = dict(HELD, event_id="deal:later", event_date="2026-10-20T00:00:00Z")
        self.assertEqual(roundup.prior_deal(STEP, index(later, HELD), START)["event_id"], "deal:c9b891f5c1a59116")

    def test_no_table_no_step(self):
        self.assertEqual(roundup.deal_index(None), [])
        self.assertIsNone(roundup.prior_deal(STEP, roundup.deal_index(None), START))


class Row63TheLimitation(unittest.TestCase):
    def test_the_w45_line_before_the_fix(self):
        self.assertEqual(roundup.evidence_gap(STEP, HEAD), OLD_GAP)

    def test_the_line_names_the_row_and_its_date(self):
        got = roundup.evidence_gap(STEP, HEAD, roundup.prior_deal(STEP, index(HELD), START))
        self.assertEqual(got, NEW_GAP)
        self.assertNotIn("one outlet", got)
        self.assertNotIn("not a warehouse table's", got)
        self.assertIn("in `energy_deals` since 2026-10-14", got)

    def test_an_analysis_piece_is_still_said(self):
        got = roundup.evidence_gap(dict(STEP, kind="commentary"), HEAD, HELD)
        self.assertTrue(got.endswith("what the week's step changes in that deal; an analysis piece, not a reported event."), got)

    def test_no_dash_in_the_line(self):
        self.assertFalse({chr(0x2014), chr(0x2013)} & set(NEW_GAP))


class Row63TheRanking(unittest.TestCase):
    def clusters(self):
        return pd.DataFrame([dict(STEP, sig=8, sector="datacenter_power"),
                             dict(cluster_id="news:new1", parties="Orsted", mw="704", price="", sig=7, sector="renewables"),
                             dict(cluster_id="news:new2", parties="NRC", mw="", price="", sig=7, sector="nuclear")])

    def test_a_step_ranks_below_the_week_s_first_reports(self):
        c = self.clusters()
        out = roundup.first_reports_first(c, {STEP["cluster_id"]: HELD})
        self.assertEqual(list(out["cluster_id"]), ["news:new1", "news:new2", "news:ba054773bb4b12df"])

    def test_no_step_keeps_the_order(self):
        c = self.clusters()
        self.assertEqual(list(roundup.first_reports_first(c, {})["cluster_id"]), list(c["cluster_id"]))

    def test_under_more_the_step_is_said(self):
        heads = {STEP["cluster_id"]: HEAD}
        got = roundup.more_why(STEP, heads, {STEP["cluster_id"]: HELD})
        self.assertTrue(got.endswith("A step in a deal first reported before this week: in `energy_deals` since 2026-10-14 "
                                     "(Google and AEP, Wyoming fuel cell project, 702 MW, USD 4 billion, a 20-year power "
                                     "purchase agreement)."), got)
        self.assertEqual(roundup.more_why(STEP, heads, {}), brief.why_line(STEP["why"], HEAD))

    def test_main_reads_the_table_and_passes_the_step(self):
        with open(roundup.__file__, encoding="utf-8") as f:
            src = f.read()
        self.assertIn("deal_ix = deal_index(read_table(\"energy_deals\"))", src)
        self.assertIn("brief.one_per_topic(first_reports_first(clusters, steps), WHAT_MATTERED_N, log, \"what mattered\")", src)
        self.assertIn("evidence_gap(r, heads[r['cluster_id']], steps.get(r['cluster_id']))", src)


class Row63TheWords(unittest.TestCase):
    def test_money(self):
        self.assertEqual(roundup.money_value("$4 Billion"), 4e9)
        self.assertEqual(roundup.money_value("USD 938 million"), 938e6)
        self.assertEqual(roundup.money_value("US$1.2bn"), 1.2e9)
        self.assertIsNone(roundup.money_value("702 MW"))

    def test_party_keys(self):
        self.assertEqual(roundup.party_key("AEP, Inc."), "aep")
        self.assertEqual(roundup.party_key(" Bloom Energy "), "bloom energy")

    def test_a_financing_summary(self):
        fin = dict(event_date="2026-10-01T00:00:00Z", deal_type="project_finance", buyer="Deutsche Bank", seller="Return",
                   asset="Germany BESS portfolio", dollars="938000000", mw="")
        self.assertEqual(roundup.deal_summary(fin), "Deutsche Bank's financing of Return's Germany battery storage portfolio, "
                                                    "USD 938 million")


if __name__ == "__main__":
    unittest.main()

"""Session 2233 (chain 156): one record a deal (warehouse/deals/dedupe.py).

The fixture: twelve stories about four deals, as `news_stories` holds them (titles, and the summary where a figure is
read from it): AEP and Amazon's 960 MW nuclear project ("explore", "planning", "signs", one story naming "American
Electric Power"), Devon's purchase of Coterra (USD 21.5 and 21.4 billion; a third story giving the combined company's
USD 58 billion), Williams and Momentum Midstream (signed 3 August, closed 4 September: 32 days), and the Department of
Energy's loan to Vistra (the DOE's own release names no borrower). Each story is its own cluster and comes on its own
run, and the fake model never marks same_as, so only the code can fold them. No model, no network, a temporary folder.
"""

import json
import os
import shutil
import sys
import tempfile
import types
import unittest
from unittest import mock

import pandas as pd

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
for p in (os.path.join(ROOT, "warehouse", "deals"), os.path.join(ROOT, "warehouse", "deals", "eval")):
    if p not in sys.path:
        sys.path.insert(0, p)

import dedupe  # noqa: E402
import fixture  # noqa: E402


def story(sid, date, source, title, summary=""):
    return {"event_id": sid, "event_date": date, "event_type": "news", "source": source,
            "source_url": f"https://example.org/{sid.split(':')[1]}", "title": title, "summary": summary or title,
            "significance": "8", "sector": "deal", "cluster_id": sid, "scored_at": "2026-11-06T00:00:00Z"}


S = {
    "a1": story("news:89a25920bbf1b233", "2026-10-19T13:00:00Z", "Bloomberg.com",
                "Amazon and AEP Explore 960-Megawatt Nuclear Project in Indiana"),
    "a2": story("news:ea68ebe1d13353f6", "2026-10-19T15:00:00Z", "World Nuclear News",
                "AEP, Amazon and X-energy planning 12-SMR plant",
                "US utility American Electric Power and X-energy have signed a joint development agreement to evaluate a "
                "potential 960 MW project at a former coal plant site in Indiana"),
    "a3": story("news:c9a091768991ffeb", "2026-10-19T18:00:00Z", "Utility Dive",
                "AEP signs 960-MW Indiana nuclear pact with Amazon, X-energy",
                "If the project is developed, Amazon would purchase the power under a long-term contract that covers "
                "the cost of the facility and its operations, the companies said."),
    "b1": story("news:dd8c701b262f8542", "2026-02-02T11:00:00Z", "WSJ",
                "Devon Energy to Buy Coterra for $21.5 Billion to Create Shale Giant"),
    "b2": story("news:6626c372364c2645", "2026-02-02T13:00:00Z", "Bloomberg",
                "Devon Agrees to Buy US Shale Rival Coterra for $21.4 Billion"),
    "b3": story("news:c6d7f2ffc5bb9488", "2026-02-02T15:00:00Z", "Reuters",
                "Devon, Coterra will merge to create $58 billion US shale giant"),
    "c1": story("news:5549283a0f9e98d6", "2026-08-03T12:00:00Z", "Bloomberg",
                "Williams Agrees to Buy Momentum Midstream for $5.5 Billion"),
    "c2": story("news:da89e33005f678f9", "2026-08-03T16:00:00Z", "Hart Energy",
                "Williams Clinches $5.5B Momentum Midstream Deal to Dominate Haynesville-to-LNG Corridor"),
    "c3": story("news:2d438d588872a468", "2026-09-04T12:00:00Z", "Hart Energy",
                "Williams Closes $5.5B Momentum Deal as Haynesville M&A Surges"),
    "d1": story("news:42140c47d3602872", "2026-10-05T14:00:00Z", "DOE newsroom",
                "Energy Department Announces $4.2 Billion Investment to Boost Nuclear Power and Help Lower Energy Costs"),
    "d2": story("news:8080802f867bd3fe", "2026-10-05T16:46:31Z", "POWER Magazine",
                "Vistra in Line for $4.2B DOE Loan Package to Uprate Nuclear Plants in Ohio and Pennsylvania"),
    "d3": story("news:770d3d0d2d796613", "2026-10-06T12:00:00Z", "Utility Dive",
                "DOE intends to loan Vistra $4.2B for nuclear fleet improvements",
                "The loan would cover 433 MW of uprates at Vistra's nuclear plants"),
}


def ans(key, deal_type, buyer, seller, asset, stage, stage_text, status, status_text, **nums):
    d = {k: "" for k in ("mw", "mw_text", "mwh", "mwh_text", "dollars", "dollars_text", "price_value", "price_unit",
                         "price_text", "term_years", "term_text", "state", "country", "state_text", "country_text",
                         "announced_date", "technology", "same_as", "confidence_basis")}
    d.update(deal_type=deal_type, buyer=buyer, seller=seller, other_parties=[], asset=asset, ai_power=False,
             confidence=0.85, evidence=S[key]["title"], story_id=S[key]["event_id"], kind="",
             stage=stage, stage_text=stage_text, status=status, status_text=status_text)
    d.update(nums)
    return d


A = {
    "a1": [ans("a1", "ppa", "Amazon", "AEP", "960-Megawatt Nuclear Project", "rumored", "Explore", "rumored", "Explore",
               mw="960", mw_text="960-Megawatt")],
    "a2": [ans("a2", "ppa", "", "American Electric Power", "12-SMR plant", "announced", "planning", "announced", "planning",
               mw="960", mw_text="960 MW", other_parties=["X-energy"])],
    "a3": [ans("a3", "ppa", "Amazon", "AEP", "Indiana nuclear pact", "signed", "signs", "signed", "signs",
               mw="960", mw_text="960-MW")],
    "b1": [ans("b1", "m_and_a", "Devon Energy", "Coterra", "Coterra", "announced", "to Buy", "announced", "to Buy",
               dollars="21500000000", dollars_text="$21.5 Billion")],
    "b2": [ans("b2", "m_and_a", "Devon", "Coterra", "Coterra", "signed", "Agrees to Buy", "signed", "Agrees",
               dollars="21400000000", dollars_text="$21.4 Billion")],
    "b3": [ans("b3", "m_and_a", "Devon", "Coterra", "Coterra", "announced", "will merge", "announced", "will merge")],
    "c1": [ans("c1", "m_and_a", "Williams", "Momentum Midstream", "Momentum Midstream", "signed", "Agrees to Buy", "signed",
               "Agrees", dollars="5500000000", dollars_text="$5.5 Billion")],
    "c2": [ans("c2", "m_and_a", "Williams", "Momentum Midstream", "Momentum Midstream", "signed", "Clinches", "signed",
               "Clinches", dollars="5500000000", dollars_text="$5.5B")],
    "c3": [ans("c3", "m_and_a", "Williams", "Momentum", "Momentum", "closed", "Closes", "closed", "Closes",
               dollars="5500000000", dollars_text="$5.5B")],
    "d1": [ans("d1", "debt", "Energy Department", "", "nuclear power", "announced", "Announces", "announced", "Announces",
               dollars="4200000000", dollars_text="$4.2 Billion")],
    "d2": [ans("d2", "debt", "DOE", "Vistra", "nuclear plants in Ohio and Pennsylvania", "", "", "", "",
               dollars="4200000000", dollars_text="$4.2B")],
    "d3": [ans("d3", "debt", "DOE", "Vistra", "nuclear fleet improvements", "", "", "", "",
               dollars="4200000000", dollars_text="$4.2B", mw="433", mw_text="433 MW")],
}
BY_SID = {S[k]["event_id"]: v for k, v in A.items()}
DAYS = [["a1", "b1", "c1", "d1"], ["a2", "b2", "c2", "d2"], ["a3", "b3", "c3", "d3"]]


class Fake:
    def __init__(self):
        self.messages = self

    def create(self, **kw):
        items = json.loads(kw["messages"][0]["content"].split("Clusters (JSON):\n", 1)[1])
        text = json.dumps({"results": [{"cluster_id": i["cluster_id"], "deals": BY_SID[i["cluster_id"]]} for i in items]})
        return types.SimpleNamespace(
            usage=types.SimpleNamespace(input_tokens=1, output_tokens=1, cache_creation_input_tokens=0,
                                        cache_read_input_tokens=0),
            stop_reason="end_turn", content=[types.SimpleNamespace(type="text", text=text)], _request_id="req_test")


class ThreeDays(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        ex = fixture.load_extract()
        with fixture.sandbox(ex, Fake(), "replay") as tmp:
            sent = []
            for day in DAYS:
                sent += [S[k] for k in day]
                fixture.write_news(ex, tmp, sent)
                assert ex.main([]) == 0, fixture.log_of(tmp)[-800:]
            cls.rows = fixture.rows_of(ex, tmp)
            cls.log = fixture.log_of(tmp)

    def rec(self, seller_word):
        r = self.rows[self.rows["seller"].str.contains(seller_word) | self.rows["buyer"].str.contains(seller_word)]
        self.assertEqual(len(r), 1, f"{seller_word}: {r[['event_id', 'buyer', 'seller']].to_dict('records')}")
        return r.iloc[0]

    def test_twelve_stories_make_four_records(self):
        self.assertEqual(len(self.rows), 4, self.rows[["buyer", "seller", "event_date"]].to_dict("records"))
        self.assertTrue((self.rows["n_stories"] == "3").all())

    def test_a_name_and_its_initials_and_a_later_stage(self):
        r = self.rec("AEP")
        self.assertEqual(r["stage"], "signed")
        self.assertEqual(r["status"], "signed")
        hist = r["status_history"].split("; ")
        self.assertEqual([h.split(" ")[1] for h in hist], ["rumored", "announced", "signed"])
        self.assertIn(S["a3"]["event_id"], hist[-1])

    def test_the_combined_value_is_not_the_purchase(self):
        r = self.rec("Coterra")
        self.assertEqual(r["dollars"], "21500000000")   # the first story's sum is kept; 21.4 is within the tolerance
        self.assertEqual(r["stage"], "signed")
        self.assertEqual(r["event_date"][:10], "2026-02-02")

    def test_a_closing_a_month_later_is_the_same_deal(self):
        r = self.rec("Momentum")
        self.assertEqual(r["stage"], "closed")
        self.assertEqual(r["status"], "closed")
        self.assertEqual(r["event_date"][:10], "2026-08-03")
        self.assertIn("2026-09-04 closed", r["status_history"])

    def test_one_party_named_and_the_size_agreeing(self):
        r = self.rec("Vistra")
        self.assertEqual(r["seller"], "Vistra")        # filled from the second story
        self.assertEqual(r["mw"], "433")              # filled from the third
        self.assertEqual(r["event_date"][:10], "2026-10-05")
        self.assertEqual(len(r["story_urls"].split(";")), 3)

    def test_the_log_says_each_merge(self):
        # (two runs in the same second share a log file, so the count is of what each kept file says, not of 8)
        self.assertGreaterEqual(self.log.count("warehouse/deals/dedupe.py): merged, not a new row"), 4)


class Rules(unittest.TestCase):
    def test_initials(self):
        self.assertTrue(dedupe.same_party("AEP", "American Electric Power"))
        self.assertTrue(dedupe.same_party("American Electric Power Co", "AEP"))
        self.assertFalse(dedupe.same_party("AES", "American Electric Power"))

    def test_another_sum_keeps_two_records(self):
        a = {"deal_type": "m_and_a", "buyer": "Devon", "seller": "Coterra", "dollars": "21500000000",
             "event_date": "2026-02-02"}
        b = dict(a, dollars="58000000000")
        self.assertFalse(dedupe.same_record(b, a))

    def test_one_party_without_a_size_is_not_enough(self):
        held = {"deal_type": "debt", "buyer": "DOE", "seller": "Vistra", "dollars": "4200000000", "event_date": "2026-10-05"}
        self.assertFalse(dedupe.same_record({"deal_type": "debt", "buyer": "DOE", "seller": "", "event_date": "2026-10-06"}, held))
        self.assertFalse(dedupe.same_record({"deal_type": "debt", "buyer": "DOE", "seller": "Holtec",
                                             "dollars": "4200000000", "event_date": "2026-10-06"}, held))

    def test_a_same_stage_story_a_year_later_is_a_new_deal(self):
        held = {"deal_type": "ppa", "buyer": "Google", "seller": "NextEra", "mw": "600", "event_date": "2025-09-01",
                "stage": "signed"}
        self.assertFalse(dedupe.same_record(dict(held, event_date="2026-06-01"), held))
        self.assertTrue(dedupe.same_record(dict(held, event_date="2026-06-01", stage="operating"), held))

    def test_an_earlier_story_moves_the_date_and_a_stated_date_stays(self):
        row = {"event_date": "2026-10-06T12:00:00Z", "date_basis": "first_story_published", "stage": "signed"}
        dedupe.merge(row, {"stage": "announced"}, "2026-10-01T00:00:00Z", "news:x")
        self.assertEqual(row["event_date"], "2026-10-01T00:00:00Z")
        self.assertEqual(row["stage"], "signed")   # an earlier stage never replaces a later one
        row = {"event_date": "2026-10-06", "date_basis": "stated"}
        dedupe.merge(row, {}, "2026-10-01T00:00:00Z", "news:x")
        self.assertEqual(row["event_date"], "2026-10-06")


if __name__ == "__main__":
    unittest.main()

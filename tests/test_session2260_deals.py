"""Session 2260 (chain 159): a party a later story names joins the record it is folded into.

The second read (session 2249) found 3 of 106 sampled deals with a party missed. One (D045) was the fold: the model
named Engine No. 1 in the cluster "Microsoft, Chevron and Engine No. 1 sign exclusive deal for power supply", and
that deal was folded into the earlier record "Chevron, Microsoft Eye Massive Texas Power Project", whose
other_parties stayed empty (dedupe.merge filled an empty buyer or seller, never another party). warehouse/deals/
dedupe.py now adds the later story's other parties not yet on the record and rebuilds the record's parties
(buyer;seller;other_parties). The two others (D104, D105: the company acquired, with no seller named) are left for the
owner's ruling: seller is a field the Roundup prints as the party selling.
"""

import json
import os
import sys
import unittest

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
sys.path.insert(0, os.path.join(ROOT, "warehouse", "deals"))
sys.path.insert(0, os.path.join(ROOT, "warehouse", "deals", "eval"))
import dedupe  # noqa: E402
import fixture  # noqa: E402


class TheFold(unittest.TestCase):
    def test_a_later_party_joins(self):
        row = {"buyer": "Microsoft", "seller": "Chevron", "other_parties": "", "parties": "Microsoft;Chevron",
               "event_date": "2026-01-28T12:00:00Z", "date_basis": "first_story_published"}
        changes = dedupe.merge(row, {"buyer": "Microsoft", "seller": "Chevron", "other_parties": ["Engine No. 1"]},
                               "2026-01-29T12:00:00Z", "news:x")
        self.assertEqual(row["other_parties"], "Engine No. 1")
        self.assertEqual(row["parties"], "Microsoft;Chevron;Engine No. 1")
        self.assertIn("party Engine No. 1 added", changes)

    def test_a_party_already_there_is_not_added_twice(self):
        row = {"buyer": "Microsoft", "seller": "Chevron", "other_parties": "Engine No. 1",
               "parties": "Microsoft;Chevron;Engine No. 1", "date_basis": "stated"}
        dedupe.merge(row, {"buyer": "", "seller": "", "other_parties": ["engine no. 1", "Chevron"]}, "", "news:y")
        self.assertEqual(row["other_parties"], "Engine No. 1")
        self.assertEqual(row["parties"], "Microsoft;Chevron;Engine No. 1")

    def test_a_filled_seller_is_in_the_parties(self):
        row = {"buyer": "Eaton", "seller": "", "other_parties": "", "parties": "Eaton", "date_basis": "stated"}
        dedupe.merge(row, {"seller": "COL Group", "other_parties": []}, "", "news:z")
        self.assertEqual(row["parties"], "Eaton;COL Group")


class TheSample(unittest.TestCase):
    def test_d045_keeps_engine_no_1(self):
        with open(os.path.join(ROOT, "tests", "fixtures", "deals", "stories_2249.json"), encoding="utf-8") as f:
            fx = {s["event_id"]: s.get("fixture") for s in json.load(f)}
        rows, log = fixture.replay("2249")
        got = [r for r in rows.to_dict("records") if "D045" in {fx.get(i) for i in str(r["story_ids"]).split(";")}]
        self.assertEqual(len(got), 1)
        self.assertEqual(got[0]["other_parties"], "Engine No. 1")
        self.assertEqual(log.count("added"), 1)


if __name__ == "__main__":
    unittest.main()

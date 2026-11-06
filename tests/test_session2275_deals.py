"""Session 2275 (chain 174): the provider of credit is the buyer.

The second read (session 2249) found 1 of 106 sampled deals with a party wrong: "Google to serve as credit backstop
for TeraWulf data center in Kentucky" was stored with Google as the seller and no buyer, though the prompt's rule
for debt and project finance makes the investors or lenders the buyer. warehouse/deals/fields.py (credit_parties)
moves the seller the evidence names as providing credit to buyer, and takes the company the credit is for ("for
TeraWulf data center") as the seller, out of other_parties. On the replayed answers: 1 to 0, no other row's parties
changing on the three deal fixtures.
"""

import json
import os
import sys
import unittest

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
sys.path.insert(0, os.path.join(ROOT, "warehouse", "deals"))
sys.path.insert(0, os.path.join(ROOT, "warehouse", "deals", "eval"))
import deal_fields as fields  # noqa: E402  session 3233: by its own name (deal_fields.py)
import fixture  # noqa: E402


class TheRule(unittest.TestCase):
    def test_the_credit_provider(self):
        d = {"buyer": "", "seller": "Google", "evidence": "Google to serve as credit backstop for TeraWulf data center in Kentucky"}
        self.assertEqual(fields.credit_parties(d), ("Google", "TeraWulf"))
        d = {"buyer": "", "seller": "Apollo", "evidence": "Apollo provides $3.5 billion financing"}
        self.assertEqual(fields.credit_parties(d), ("Apollo", ""))

    def test_left_as_it_is(self):
        self.assertIsNone(fields.credit_parties({"buyer": "Meta", "seller": "Google",
                                                 "evidence": "Google to serve as credit backstop for Meta"}))   # a buyer named
        self.assertIsNone(fields.credit_parties({"buyer": "", "seller": "Shell",
                                                 "evidence": "Shell to offload Jiffy Lube to Monomoy Capital"}))
        self.assertIsNone(fields.credit_parties({"buyer": "", "seller": "Crescent",
                                                 "evidence": "Crescent Sells Non-Op D-J Assets"}))


class TheSample(unittest.TestCase):
    def test_d001(self):
        with open(os.path.join(ROOT, "tests", "fixtures", "deals", "stories_2249.json"), encoding="utf-8") as f:
            fx = {s["event_id"]: s.get("fixture") for s in json.load(f)}
        rows, _ = fixture.replay("2249")
        got = [r for r in rows.to_dict("records") if "D001" in {fx.get(i) for i in str(r["story_ids"]).split(";")}]
        self.assertEqual([(r["buyer"], r["seller"], r["other_parties"]) for r in got], [("Google", "TeraWulf", "Anthropic")])


if __name__ == "__main__":
    unittest.main()

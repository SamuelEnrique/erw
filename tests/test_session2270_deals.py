"""Session 2270 (chain 174): a datacenter word that names a motive or a market is not an AI-power load.

The second read (session 2249) found 2 of 106 sampled deals tagged AI power by a datacenter word that is not the load
the deal serves: "India's Welspun bags $580 million US gas pipeline order tied to data centre buildout" (a motive)
and "Eaton signs agreement to acquire COL Group, expanding manufacturing capacity ... for data center and utility
markets" (a market). warehouse/deals/fields.py takes such phrases out of the text before the load check
(DATACENTER_GENERIC). On the replayed 2249 answers: 2 to 0, no other row's tag changing.
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
    def ai(self, text, **d):
        return fields.ai_of(d, fields.plain(text))[0]

    def test_a_motive_or_a_market_is_not_a_load(self):
        self.assertFalse(self.ai("welspun bags $580 million us gas pipeline order tied to data centre buildout", seller="Welspun"))
        self.assertFalse(self.ai("expanding manufacturing capacity for data center and utility markets in emea", buyer="Eaton"))
        self.assertFalse(self.ai("gas turbines ordered amid the ai boom", buyer="Utility Co"))

    def test_a_load_is_still_a_load(self):
        self.assertTrue(self.ai("utility to supply 500 mw to a data center campus in ohio", buyer="Utility Co"))
        self.assertTrue(self.ai("gas plant to power texas data center", buyer="Utility Co"))
        self.assertTrue(self.ai("deal tied to data center buildout", buyer="Microsoft"))   # a named AI party


class TheSample(unittest.TestCase):
    def test_ai_tag_two_to_none(self):
        with open(os.path.join(ROOT, "tests", "fixtures", "deals", "stories_2249.json"), encoding="utf-8") as f:
            fx = {s["event_id"]: s.get("fixture") for s in json.load(f)}
        rows, _ = fixture.replay("2249")
        got = {}
        for r in rows.to_dict("records"):
            for sid in str(r["story_ids"]).split(";"):
                if fx.get(sid) in ("D005", "D104"):
                    got[fx[sid]] = r["ai_power"]
        self.assertEqual(got, {"D005": "false", "D104": "false"})
        self.assertEqual(int((rows["ai_power"] == "true").sum()), 34)   # 35 until session 2277 refused D055, a project led


if __name__ == "__main__":
    unittest.main()

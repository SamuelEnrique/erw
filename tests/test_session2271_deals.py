"""Session 2271 (chain 174): a contract's sum that is another thing's.

The second read (session 2249) found 2 of 106 sampled deals with a figure of another thing: the PPA of Microsoft,
Chevron and Engine No. 1 kept "$7 Billion" from "Over $7 Billion Texas Power Plant" (the plant's cost), and
Nvidia's data-center lease kept "$3.8 Billion" from "Funded by $3.8 Billion of Junk Bonds" (the building's funding).
For a power purchase, an offtake, a lease or a fuel supply, warehouse/deals/fields.py (sum_of_other) now refuses a
USD figure whose words go on to its funding or to a plant, project, facility, campus or building no deal word
follows; the cross-check reads the headline the same way, so the row is not flagged for a figure it refused.
On the replayed 2249 answers: 2 to 0, no other row's sum or flag changing.
"""

import json
import os
import sys
import unittest

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
sys.path.insert(0, os.path.join(ROOT, "warehouse", "deals"))
sys.path.insert(0, os.path.join(ROOT, "warehouse", "deals", "eval"))
import crosscheck  # noqa: E402
import fields  # noqa: E402
import fixture  # noqa: E402


class TheRule(unittest.TestCase):
    def test_another_things_sum(self):
        self.assertTrue(fields.sum_of_other("lease", "$3.8 Billion", "nvidia to lease data center funded by $3.8 billion of junk bonds"))
        self.assertTrue(fields.sum_of_other("ppa", "$7 Billion", "microsoft in talks over $7 billion texas power plant"))

    def test_the_contracts_own_sum(self):
        self.assertEqual(fields.sum_of_other("lease", "$7.5 billion", "applied digital signs $7.5 billion ai data center lease"), "")
        self.assertEqual(fields.sum_of_other("lease", "$19 billion", "terawulf jumps on $19 billion data center lease deal"), "")
        self.assertEqual(fields.sum_of_other("ppa", "$2 billion", "a $2 billion power plant supply deal"), "")
        self.assertEqual(fields.sum_of_other("debt", "$3.8 billion", "raises $3.8 billion of bonds"), "")   # a debt deal's own
        self.assertEqual(fields.sum_of_other("m_and_a", "$7 billion", "buys a $7 billion texas power plant"), "")

    def test_the_cross_check_reads_the_headline_the_same_way(self):
        t = "Nvidia to Lease Data Center Funded by $3.8 Billion of Junk Bonds"
        self.assertEqual(crosscheck.stated(t, "lease")["usd"], [])
        self.assertEqual(crosscheck.stated(t, "debt")["usd"], [3.8e9])


class TheSample(unittest.TestCase):
    def test_two_to_none(self):
        with open(os.path.join(ROOT, "tests", "fixtures", "deals", "stories_2249.json"), encoding="utf-8") as f:
            fx = {s["event_id"]: s.get("fixture") for s in json.load(f)}
        rows, log = fixture.replay("2249")
        got = {}
        for r in rows.to_dict("records"):
            for sid in str(r["story_ids"]).split(";"):
                if fx.get(sid) in ("D045", "D053"):
                    got[fx[sid]] = (r["dollars"], r["flags"])
        self.assertEqual(got, {"D045": ("", ""), "D053": ("", "")})
        self.assertEqual(log.count("is another thing's sum"), 2)


if __name__ == "__main__":
    unittest.main()

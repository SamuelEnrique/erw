"""Session 2284 (chain 179): the third read's fixtures, replayed.

50 deal clusters and 30 facility clusters, the latest eligible ones no earlier fixture held, with the model's answers
recorded under the rules of chains 156 to 174 (docs/reviews/deals-audit-2026-11-06.md, "Session 2284"). The replay
gives 9 deal rows and 4 facility rows; the read found four one-record faults, the open rows of sessions 2288 to 2291.
"""

import json
import os
import sys
import unittest

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
sys.path.insert(0, os.path.join(ROOT, "warehouse", "deals", "eval"))
sys.path.insert(0, os.path.join(ROOT, "warehouse", "datacenters", "eval"))
import fixture  # noqa: E402
import dc_fixture  # noqa: E402


class TheThirdRead(unittest.TestCase):
    def test_the_fixtures(self):
        for folder, n in (("deals", 50), ("datacenters", 30)):
            with open(os.path.join(ROOT, "tests", "fixtures", folder, "stories_2284.json"), encoding="utf-8") as f:
                self.assertEqual(len({s["cluster_id"] for s in json.load(f)}), n)
            with open(os.path.join(ROOT, "tests", "fixtures", folder, "recorded_2284.json"), encoding="utf-8") as f:
                self.assertLess(json.load(f)["usd"], 0.10)

    def test_the_replay(self):
        rows, _ = fixture.replay("2284")
        self.assertGreaterEqual(len(rows), 8)
        frows, _ = dc_fixture.replay("2284")
        self.assertGreaterEqual(len(frows), 4)


if __name__ == "__main__":
    unittest.main()

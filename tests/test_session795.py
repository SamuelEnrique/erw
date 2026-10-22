"""Session 795 (chain 065): the nodes that settle alike. The builder groups the nodes whose day-ahead basis is the same on
every day node_basis_daily holds, with the same days (exact equality of the table's values); a node's panel names the
others. Session 723's pair (BBREEZE_1_2, ELSAUZ_ALL) is alike only to two decimals, so it is not grouped. No request, no model call."""
import json
import os
import unittest

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))


def src(*parts):
    with open(os.path.join(ROOT, *parts), encoding="utf-8") as f:
        return f.read()


class Alike(unittest.TestCase):
    def test_the_groups_are_symmetric_and_name_the_known_pair(self):
        n = {k["id"]: k for k in json.loads(src("site", "data", "siting", "nodes.json"))["nodes"]}
        self.assertEqual(sorted(n["AE_RN"].get("same", [])), ["BCH_RN", "MYR_ALL"])
        # session 723's pair is equal over twelve months to two decimals, not on every day: July 2026's means differ by
        # 0.0001, so the exact rule leaves them apart
        self.assertNotIn("ELSAUZ_ALL", n["BBREEZE_1_2"].get("same", []))
        for i, k in n.items():
            for o in k.get("same", []):
                self.assertIn(i, n[o].get("same", []), (i, o))
                self.assertEqual(k["dam_basis"], n[o]["dam_basis"], (i, o))     # the same months, figures and days

    def test_the_panel_names_them(self):
        self.assertIn('data-node-same="1"', src("site", "app", "cost-of-power", "AllGridsView.tsx"))


if __name__ == "__main__":
    unittest.main()

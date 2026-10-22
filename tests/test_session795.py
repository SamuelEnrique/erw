"""Session 795 (chain 065): the nodes that settle alike. The builder groups the nodes whose day-ahead basis is the same on
every day node_basis_daily holds, with the same days (exact equality of the table's values); a node's panel names the
others. Session 723's walk found BBREEZE_1_2 and ELSAUZ_ALL alike. No request, no model call."""
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
        self.assertIn("ELSAUZ_ALL", n["BBREEZE_1_2"].get("same", []))
        self.assertIn("BBREEZE_1_2", n["ELSAUZ_ALL"].get("same", []))
        for i, k in n.items():
            for o in k.get("same", []):
                self.assertIn(i, n[o].get("same", []), (i, o))
                self.assertEqual(k["dam_basis"], n[o]["dam_basis"], (i, o))     # the same months, figures and days

    def test_the_panel_names_them(self):
        self.assertIn('data-node-same="1"', src("site", "app", "cost-of-power", "AllGridsView.tsx"))


if __name__ == "__main__":
    unittest.main()

"""Session 746 (chain 063): the node's day-ahead intraday swing. node_basis_daily's dam_spread_4h (each day's four dearest
hours' mean less its four cheapest) over the node file's twelve months: its mean, 10th and 90th percentile and days in
nodes.json; a sortable column of the node list and a line of the node's panel, keyed allgrids|nodeswing|<node>[|10|90];
the replication computes the mean from the table. No request, no model call."""
import json
import os
import unittest

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))


def src(*parts):
    with open(os.path.join(ROOT, *parts), encoding="utf-8") as f:
        return f.read()


class Swing(unittest.TestCase):
    def test_the_file_holds_each_node_s_swing(self):
        n = json.loads(src("site", "data", "siting", "nodes.json"))
        held = [k for k in n["nodes"] if k.get("swing")]
        self.assertGreater(len(held), 800)
        for k in held[:50]:
            mean, p10, p90, days = k["swing"]
            self.assertLessEqual(p10, p90)
            self.assertGreaterEqual(mean, 0)                 # the dearest four hours less the cheapest four
            self.assertGreater(days, 0)

    def test_the_list_the_panel_and_the_key(self):
        n = src("site", "app", "cost-of-power", "AllGridsNodes.tsx")
        self.assertIn('swing: "Intraday swing"', n)
        self.assertIn("data-check={`allgrids|nodeswing|${r.id}`}", n)
        self.assertIn("swing_usd_mwh", n)                       # the download carries it
        v = src("site", "app", "cost-of-power", "AllGridsView.tsx")
        self.assertIn('data-node-swing="1"', v)
        s = src("site", "lib", "siting.ts")
        self.assertIn('"spread", "swing", "allin"', s)
        self.assertIn('if (p[1] === "nodeswing")', s)
        self.assertIn('"/cost-of-power?view=allgrids&rows=nodes&nsort=swing&ndir=desc"', src("site", "scripts", "check-values.mjs"))
        self.assertIn('allgrids|nodeswing|', src("warehouse", "replication", "siting.py"))


if __name__ == "__main__":
    unittest.main()

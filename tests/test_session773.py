"""Session 773 (chain 064): the third research card (site/data/findings/siting_battery_swing.json), written by
site/scripts/siting-card.mjs from the node file: ERCOT's storage nodes holding at least 90 percent of the days, by their
day-ahead intraday swing (746). Its figures are the node file's (the script's --check), it states no verdict and says the
swing is not a battery's earnings, and it was never posted or sent. No request, no model call."""
import json
import os
import unittest

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))


def src(*parts):
    with open(os.path.join(ROOT, *parts), encoding="utf-8") as f:
        return f.read()


class Card(unittest.TestCase):
    def test_the_card_is_the_node_file_s(self):
        c = json.loads(src("site", "data", "findings", "siting_battery_swing.json"))
        n = json.loads(src("site", "data", "siting", "nodes.json"))
        sw = {k["id"]: k["swing"] for k in n["nodes"] if k.get("swing")}
        self.assertEqual(c["numbers"]["widest"], sw[c["numbers"]["widest_node"]][0])
        self.assertEqual(c["numbers"]["narrowest"], sw[c["numbers"]["narrowest_node"]][0])
        self.assertEqual(sum(c["chart"]["series"][0]["values"]), c["numbers"]["nodes"])
        self.assertEqual(c["engine"], "site/scripts/siting-card.mjs")

    def test_no_verdict_and_the_limit_said(self):
        c = json.loads(src("site", "data", "findings", "siting_battery_swing.json"))
        for w in ("best", "should", "recommend", "winner", "ideal"):
            self.assertNotIn(w, (c["why"] + c["subtitle"]).lower(), w)
        self.assertIn("not a battery's earnings", c["why"])
        self.assertNotIn(chr(0x2014), json.dumps(c, ensure_ascii=False))
        self.assertIn('"/research/card/siting_battery_swing",', src("site", "scripts", "check-values.mjs"))


if __name__ == "__main__":
    unittest.main()

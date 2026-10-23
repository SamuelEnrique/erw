"""Session 734 (chain 062): the All grids tab's second research card (site/data/findings/siting_flexible.json), written by
site/scripts/siting-card.mjs from the tab's own functions: under the flexible compute profile, the hours a 1 GW load
gives up at each ERCOT hub and zone and what it saves per MWh all-in against a flat load. Its figures are the tab's
(the script's --check), it states no verdict, and it was never posted or sent. No request, no model call."""
import json
import os
import unittest

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))


def src(*parts):
    with open(os.path.join(ROOT, *parts), encoding="utf-8") as f:
        return f.read()


class Card(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.c = json.loads(src("site", "data", "findings", "siting_flexible.json"))

    def test_the_card_s_shape_and_figures(self):
        c = self.c
        self.assertEqual(c["engine"], "site/scripts/siting-card.mjs")
        self.assertEqual(c["chart"]["kind"], "bars_free")
        self.assertEqual(len(c["callouts"]), 3)
        n = c["numbers"]
        self.assertEqual(n["rows"], 14)
        self.assertLessEqual(n["saved_least"], n["saved_most"])
        self.assertLessEqual(n["lost_fewest"], n["lost_most"])
        self.assertAlmostEqual(n["hub_flat"] - n["hub_flex"], c["chart"]["series"][0]["values"][c["chart"]["x"].index("HB_HUBAVG")] - c["chart"]["series"][1]["values"][c["chart"]["x"].index("HB_HUBAVG")], places=9)
        # most of the saving is the four-peak charge (USD 7.83 at every ERCOT row), as the why line says
        self.assertGreater(7.83, n["saved_least"] / 2)

    def test_no_verdict_and_no_dash(self):
        c = self.c
        for w in ("best", "should", "recommend", "winner", "ideal"):
            self.assertNotIn(w, (c["why"] + c["subtitle"]).lower(), w)
        self.assertNotIn(chr(0x2014), json.dumps(c, ensure_ascii=False))
        for t in c["tables"]:
            self.assertIn(t, c["source_line"] + c["footnote"])

    def test_never_posted_and_read_by_check_values(self):
        for root in (os.path.join(ROOT, "docs", "digest"), os.path.join(ROOT, "docs", "weekly")):
            if os.path.isdir(root):
                for dp, _, fs in os.walk(root):
                    for f in fs:
                        with open(os.path.join(dp, f), encoding="utf-8", errors="ignore") as fh:
                            self.assertNotIn("siting_flexible", fh.read(), f)
        self.assertIn('"/research/card/siting_flexible",', src("site", "scripts", "check-values.mjs"))


if __name__ == "__main__":
    unittest.main()

"""Session 720: the All grids tab's research card (site/data/findings/siting_gigawatt.json), in the findings pipeline's
format, written by site/scripts/siting-card.mjs from the tab's own functions: its figures are the tab's for the same
load (the script's --check), it names its generator, it states no verdict, and it was never posted or sent (no channel
of the pipeline names it). No request, no model call."""
import json
import os
import shutil
import subprocess
import unittest

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
SITE = os.path.join(ROOT, "site")


def src(*parts):
    with open(os.path.join(ROOT, *parts), encoding="utf-8") as f:
        return f.read()


class Card(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.c = json.loads(src("site", "data", "findings", "siting_gigawatt.json"))

    def test_the_card_is_the_tab_s_figures(self):
        exe = shutil.which("node")
        if not exe:
            raise unittest.SkipTest("node is not on this machine")
        r = subprocess.run([exe, "scripts/siting-card.mjs", "--check"], cwd=SITE, capture_output=True, text=True, timeout=600, encoding="utf-8")
        if r.returncode != 0 and "Unknown file extension" in r.stderr:
            raise unittest.SkipTest("this node does not read TypeScript files")
        self.assertEqual(r.returncode, 0, r.stdout + r.stderr)

    def test_the_card_s_shape_and_words(self):
        c = self.c
        for k in ("id", "card_id", "title", "kind", "subtitle", "chart", "callouts", "why", "footnote", "numbers", "source_line", "tables", "method"):
            self.assertIn(k, c)
        self.assertEqual(c["engine"], "site/scripts/siting-card.mjs")
        self.assertEqual(len(c["callouts"]), 3)
        self.assertEqual(c["chart"]["kind"], "bars_free")
        self.assertLessEqual(c["numbers"]["least_allin"], c["numbers"]["most_allin"])
        for w in ("best", "should", "recommend", "winner", "ideal"):
            self.assertNotIn(w, (c["why"] + c["subtitle"]).lower(), w)   # no verdict
        self.assertNotIn(chr(0x2014), json.dumps(c, ensure_ascii=False))
        for t in c["tables"]:
            self.assertIn(t, c["source_line"] + c["footnote"])

    def test_never_posted_or_sent(self):
        # no channel of the pipeline (the Roundup's chart, the posting queue, the hunt) names the card
        for root in (os.path.join(ROOT, "docs", "digest"), os.path.join(ROOT, "docs", "weekly")):
            if os.path.isdir(root):
                for dp, _, fs in os.walk(root):
                    for f in fs:
                        with open(os.path.join(dp, f), encoding="utf-8", errors="ignore") as fh:
                            self.assertNotIn("siting_gigawatt", fh.read(), f)

    def test_check_values_reads_the_card(self):
        self.assertIn('"/research/card/siting_gigawatt",', src("site", "scripts", "check-values.mjs"))


if __name__ == "__main__":
    unittest.main()

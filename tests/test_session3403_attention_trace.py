"""Session 3403 (chain 202): the tracer reproduces every index value from the link rows, and the headline backfill.

The ten-story corpus of test_session3402_attention_index.py goes through attention_index.build; attention_trace.trace
then walks from each cell's values back to the link rows and must find every value reproduced. A wrong value planted
in a table must be found. The headline backfill's merge is tested on a temporary raw directory.
"""
import json
import os
import sys
import tempfile
import unittest

import pandas as pd

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
sys.path.insert(0, os.path.join(ROOT, "warehouse", "derived"))
sys.path.insert(0, os.path.join(ROOT, "warehouse"))
sys.path.insert(0, os.path.dirname(__file__))
import attention_classify as ac  # noqa: E402
import attention_index as ai  # noqa: E402
import attention_trace as at  # noqa: E402
from test_session3402_attention_index import CLASSIFIED, NOW, STORIES, W_A, W_B  # noqa: E402


class Trace(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        stories = pd.DataFrame(list(STORIES.values())).astype(str)
        links, att, fri, _, _ = ai.build(stories, pd.DataFrame(CLASSIFIED), NOW)
        # the tables as a reader gets them back: every column text
        cls.links, cls.att, cls.fri = links.astype(str), att.astype(str), fri.astype(str)

    def test_every_cell_is_reproduced_from_the_links(self):
        cells = self.att[self.att["entity"] != "attention:corpus:all"][["entity", "ts_utc"]].drop_duplicates()
        self.assertGreater(len(cells), 5)
        for r in cells.itertuples():
            ok, lines = at.trace(self.att, self.fri, self.links, r.entity, r.ts_utc, quiet=True)
            self.assertTrue(ok, "\n".join(lines))

    def test_the_stories_are_listed_with_their_links(self):
        ok, lines = at.trace(self.att, self.fri, self.links, "attention:datacenters:US-TX", W_A[:10])
        self.assertTrue(ok)
        self.assertTrue(any("https://x.test/1" in l and "moratorium" in l for l in lines))
        self.assertTrue(any("https://x.test/2" in l for l in lines))

    def test_a_planted_wrong_value_is_found(self):
        fri = self.fri.copy()
        m = (fri["entity"] == "attention:datacenters:all") & (fri["ts_utc"] == W_B) & (fri["variable"] == "friction_index")
        fri.loc[m, "value"] = "50.0"   # the links say 100
        ok, lines = at.trace(self.att, fri, self.links, "attention:datacenters:all", W_B, quiet=True)
        self.assertFalse(ok)
        self.assertTrue(any("friction_index" in l and "DIFFERS" in l for l in lines))

    def test_a_cell_without_a_row_says_so(self):
        ok, lines = at.trace(self.att, self.fri, self.links, "attention:nuclear:all", W_A, quiet=True)
        self.assertIsNone(ok)
        self.assertIn("no row", lines[0])


class HeadlineBackfill(unittest.TestCase):
    def test_a_backfilled_headline_fills_an_empty_one_only(self):
        with tempfile.TemporaryDirectory() as tmp:
            raw = os.path.join(tmp, "raw")
            os.makedirs(raw)
            a = dict(CLASSIFIED[0], headline="")            # story 1: no headline
            b = dict(CLASSIFIED[1], headline="Kept as is")   # story 2: the scorer's
            with open(os.path.join(raw, "classified_1.jsonl"), "w", encoding="utf-8") as f:
                f.write(json.dumps(a) + "\n" + json.dumps(b) + "\n")
            with open(os.path.join(raw, "headlines_1.jsonl"), "w", encoding="utf-8") as f:
                f.write(json.dumps(dict(event_id="news:1", headline="County pauses data center approvals", model_id="m", headlined_at=NOW)) + "\n")
                f.write(json.dumps(dict(event_id="news:2", headline="Would replace", model_id="m", headlined_at=NOW)) + "\n")
            c = ai.read_classified(raw, tmp).set_index("event_id")
            self.assertEqual(c.at["news:1", "headline"], "County pauses data center approvals")
            self.assertEqual(c.at["news:2", "headline"], "Kept as is")
            self.assertEqual(ac.read_headlines(raw)["news:1"], "County pauses data center approvals")

    def test_the_model_headline_is_normalised_and_kept_apart(self):
        r = ac.norm_row(dict(sector="gas", us=True, state="TX", place="", place_kind="", opposition=False, kind="none", tone=0,
                             headline="Pipeline approved " + chr(0x2014) + " 200 miles"))
        self.assertEqual(r["model_headline"], "Pipeline approved - 200 miles")
        self.assertNotIn(chr(0x2014), r["model_headline"])


if __name__ == "__main__":
    unittest.main()

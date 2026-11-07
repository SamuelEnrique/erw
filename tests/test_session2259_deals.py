"""Session 2259 (chain 159): a deal's stage and status from its own words, where the model gave none.

The second read (session 2249) found 7 of 106 sampled deals whose stage was stated and left empty ("to serve as",
"will become", "Joins Mercuria to Develop", "Partner to Develop", "partners with", "lease deal with", "picks ...
source says"). warehouse/deals/fields.py reads the stage from the deal's evidence sentence when the model gave none
(stage_from_words: cancelled, rumored, closed, financed, signed, announced, the first that matches), and the extractor
gives an empty status the stage when it is one of the five words the Roundup prints. On the replayed 2249 answers:
status missed 7 to 0; no row's stage or status the model gave is changed.
"""

import json
import os
import sys
import unittest

import pandas as pd

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
sys.path.insert(0, os.path.join(ROOT, "warehouse", "deals"))
sys.path.insert(0, os.path.join(ROOT, "warehouse", "deals", "eval"))
import deal_fields as fields  # noqa: E402  session 3233: by its own name (deal_fields.py)
import fixture  # noqa: E402


class TheWords(unittest.TestCase):
    def test_each_stage(self):
        for text, want in (("Google to serve as credit backstop for TeraWulf data center", "announced"),
                           ("Hess Midstream will become independent", "announced"),
                           ("Phillips 66 Joins Mercuria to Develop", "signed"),
                           ("ADQ partners with ECP", "signed"),
                           ("Meta picks Morgan Stanley, JPMorgan for debt deal, source says", "rumored"),
                           ("NextEra, Dominion in talks to create $400 billion US utility", "rumored"),
                           ("Oracle and OpenAI scrap deal to expand flagship Texas data centre", "cancelled"),
                           ("Oracle and OpenAI End Plans to Expand Flagship Data Center", "cancelled"),
                           ("Vistra completes acquisition of Cogentrix", "closed"),
                           ("Fermi closes loan for Project Matador", "financed"),
                           ("Shell to offload Jiffy Lube to Monomoy Capital", "")):
            self.assertEqual(fields.stage_from_words(text)[0], want, text)

    def test_the_span_is_the_storys_words(self):
        s, span = fields.stage_from_words("Meta picks Morgan Stanley, JPMorgan ... source says")
        self.assertEqual((s, span), ("rumored", "source says"))

    def test_the_models_stage_is_kept(self):
        row, _ = fields.finish({"stage": "signed", "stage_text": "signed", "deal_type": "ppa"},
                               "x signed a ppa; it will expand", {}, "X signed a PPA")
        self.assertEqual(row["stage"], "signed")


class TheSample(unittest.TestCase):
    def test_status_missed_seven_to_none(self):
        with open(os.path.join(ROOT, "tests", "fixtures", "deals", "stories_2249.json"), encoding="utf-8") as f:
            fx = {s["event_id"]: s.get("fixture") for s in json.load(f)}
        rows, _ = fixture.replay("2249")
        got = {}
        for r in rows.to_dict("records"):
            for sid in str(r["story_ids"]).split(";"):
                if fx.get(sid):
                    got[fx[sid]] = (r["stage"], r["status"])
        want = {"D001": "announced", "D020": "announced", "D047": "signed", "D051": "announced", "D063": "signed",
                "D074": "signed", "D081": "rumored"}
        for n, s in want.items():
            self.assertEqual(got.get(n), (s, s), n)
        self.assertIsInstance(rows, pd.DataFrame)


if __name__ == "__main__":
    unittest.main()

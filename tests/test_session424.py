"""Session 424: why test_session156 failed on every whole-suite run of 20 and 21 October 2026, and its two fixes.

1. Drift of the fixture. Since session 314 (19 October) docs/grids/grid_tables.json scopes iso_rtm_hub_prices to
   ERCOT by its entity (entity=like.ercot:*); the recording of 8 October (tests/fixtures/session156/form_reads.json)
   keyed its two reads of the table with market=like.ercot*. The tool's request was not in the fixture, so the
   recorded call newest_quarter_hours failed (site/scripts/test-ask-ready.mjs tests 1 and 10). The two keys are now
   the ones the tool sends; each read names entity ercot:HB_HUBAVG, so the rows are the same rows.
2. A frozen figure set against a moving file. Question p14 of warehouse/chat/eval_ercot_pages.json is frozen with the
   dated inputs it names (session 199); test 18 set it against today's site/data/curtailment/ercot.json within 2
   points, and the share had moved from 4.46 to 6.53 by 20 October. It is now set against the dated inputs, exactly.

No test here calls a model or reaches the network.
"""

import json
import os
import unittest
from urllib.parse import parse_qs, urlparse

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
DASH = chr(0x2014)
EN = chr(0x2013)


def src(*p):
    with open(os.path.join(ROOT, *p), encoding="utf-8") as f:
        return f.read()


class TheFixtureKeysAreTheToolsOwn(unittest.TestCase):
    def setUp(self):
        self.fix = json.loads(src("tests", "fixtures", "session156", "form_reads.json"))
        self.grid = json.loads(src("docs", "grids", "grid_tables.json"))

    def test_the_rule_scopes_the_table_by_entity(self):
        bys = [g.get("by", {}).get("iso_rtm_hub_prices") for g in self.grid["grids"].values()] if isinstance(self.grid.get("grids"), dict) else []
        text = json.dumps(self.grid)
        self.assertIn('"iso_rtm_hub_prices": "entity"', text)
        self.assertNotIn("market", [b for b in bys if b])

    def test_every_read_of_the_table_is_scoped_by_entity_and_names_the_hub(self):
        keys = [k for k in self.fix["reads"] if "table_name=eq.iso_rtm_hub_prices" in k]
        self.assertEqual(len(keys), 2)
        for k in keys:
            q = parse_qs(urlparse(k).query)
            self.assertEqual(q.get("entity"), ["like.ercot:*"], k)
            self.assertNotIn("market", q, k)
            self.assertIn('entity.eq."ercot:HB_HUBAVG"', q["and"][0], k)

    def test_the_rows_are_the_recorded_rows(self):
        n = {k: len(v) for k, v in self.fix["reads"].items() if "table_name=eq.iso_rtm_hub_prices" in k}
        self.assertEqual(sorted(n.values()), [96, 700])
        self.assertEqual(self.fix["recorded_at"], "2026-10-08T09:06:29.247Z")

    def test_the_fixture_says_what_changed_and_when(self):
        self.assertIn("Session 424 (21 October 2026)", self.fix["_"])
        self.assertIn("session 314 (19 October)", self.fix["_"])


class TheFrozenFigureIsSetAgainstItsDatedInputs(unittest.TestCase):
    def test_p14_equals_the_share_of_the_inputs_it_names(self):
        pages = json.loads(src("warehouse", "chat", "eval_ercot_pages.json"))
        p14 = next(q for q in pages["questions"] if q["id"] == "p14")
        dated = json.loads(src(*pages["built_from"]["inputs"].split("/")))
        self.assertEqual(p14["expect"], [dated["files"]["curtailment/ercot.json"]["window"]["both"]["share_pct"]])

    def test_the_node_test_reads_the_dated_inputs_and_no_longer_todays_file_within_two_points(self):
        t = src("site", "scripts", "test-ask-ready.mjs")
        self.assertIn("PAGES.built_from.inputs", t)
        self.assertIn('dated.files["curtailment/ercot.json"].window.both.share_pct', t)
        self.assertNotIn("Math.abs(p14.expect[0] - texas.window.both.share_pct) < 2", t)


class NoDash(unittest.TestCase):
    def test_no_em_or_en_dash_in_what_this_session_wrote(self):
        for p in (("tests", "test_session424.py"), ("site", "scripts", "test-ask-ready.mjs"), ("tests", "fixtures", "session156", "form_reads.json")):
            s = src(*p)
            self.assertNotIn(DASH, s, p)
            self.assertNotIn(EN, s, p)


if __name__ == "__main__":
    unittest.main()

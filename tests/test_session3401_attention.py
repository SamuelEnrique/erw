"""Session 3401 (chain 202): the classification behind the Attention and Friction indices, tested offline.

The hand-labeled set tests/fixtures/attention/labeled_200.csv (200 stories drawn by attention_classify.draw_sample with
seed 3400, half from stories whose text holds an opposition word, labeled by the session from their titles and summaries)
and the two models' stored answers (model_200_sonnet.csv, model_200_haiku.csv, the trial of 6 November 2026) are read
here; no model is called. The floors are set under the measured accuracy of the model the run uses (Sonnet 5.5:
opposition 0.985, friction F1 0.914, sector 0.92, state 0.985, us 0.93), so that a changed fixture or prompt that
loses accuracy fails the suite.
"""
import os
import sys
import unittest

import pandas as pd

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
sys.path.insert(0, os.path.join(ROOT, "warehouse", "derived"))
sys.path.insert(0, os.path.join(ROOT, "warehouse"))
import attention_classify as ac  # noqa: E402

FIX = os.path.join(ROOT, "tests", "fixtures", "attention")


def read(name):
    return pd.read_csv(os.path.join(FIX, name), dtype=str, keep_default_na=False)


class LabeledSet(unittest.TestCase):
    def setUp(self):
        self.lab = read("labeled_200.csv")

    def test_200_stories_half_from_opposition_words(self):
        self.assertEqual(len(self.lab), 200)
        self.assertEqual(self.lab["event_id"].nunique(), 200)
        self.assertEqual((self.lab["drawn_from"] == "opposition_words").sum(), 100)

    def test_every_label_in_the_vocabulary(self):
        self.assertTrue(set(self.lab["sector"]) <= set(ac.SECTORS))
        self.assertTrue(set(self.lab["kind"]) <= set(ac.KINDS))
        self.assertTrue(set(self.lab["place_kind"]) <= set(ac.PLACE_KINDS))
        self.assertTrue(set(self.lab["tone"]) <= {"-1", "0", "1"})
        self.assertTrue(set(self.lab["us"]) <= {"True", "False"})
        self.assertTrue(set(self.lab["opposition"]) <= {"True", "False"})
        for s in self.lab["state"]:
            self.assertTrue(s == "" or s in ac.STATES, s)

    def test_opposition_rows_have_a_kind_and_the_rest_none(self):
        opp = self.lab["opposition"] == "True"
        self.assertEqual(int(opp.sum()), 18)
        self.assertTrue((self.lab.loc[opp, "kind"] != "none").all())
        self.assertTrue((self.lab.loc[~opp, "kind"] == "none").all())

    def test_the_opposition_word_rule_marks_the_first_half(self):
        hit = [ac.has_opposition_word(t, s) for t, s in zip(self.lab["title"], self.lab["summary"])]
        drawn = (self.lab["drawn_from"] == "opposition_words").tolist()
        self.assertEqual(hit, drawn)


class Normalisation(unittest.TestCase):
    def test_a_clean_row_passes_unchanged(self):
        r = ac.norm_row(dict(sector="datacenters", us=True, state="TX", place="Loudoun County", place_kind="county",
                             opposition=True, kind="moratorium", tone=-1))
        self.assertEqual(r["fixed"], "")
        self.assertEqual((r["sector"], r["state"], r["kind"], r["tone"]), ("datacenters", "TX", "moratorium", -1))

    def test_a_state_written_in_words_becomes_its_code(self):
        self.assertEqual(ac.norm_state("Texas"), "TX")
        self.assertEqual(ac.norm_state("US-VA"), "VA")
        self.assertEqual(ac.norm_state("Ontario"), "")
        self.assertEqual(ac.norm_state(""), "")

    def test_values_outside_the_vocabulary_are_emptied_not_guessed(self):
        r = ac.norm_row(dict(sector="coal", us="yes", state="Mars", place="", place_kind="village", opposition="true",
                             kind="riot", tone=7))
        self.assertEqual(r["sector"], "other_energy")
        self.assertTrue(r["us"])
        self.assertEqual(r["state"], "")
        self.assertEqual(r["place_kind"], "")
        self.assertEqual(r["kind"], "other_opposition")
        self.assertEqual(r["tone"], 0)
        for word in ("sector:coal", "state:Mars", "place_kind:village", "kind:riot", "tone:7"):
            self.assertIn(word, r["fixed"])

    def test_kind_follows_opposition(self):
        self.assertEqual(ac.norm_row(dict(sector="gas", us=False, state="", place="", place_kind="", opposition=False,
                                          kind="lawsuit", tone=0))["kind"], "none")
        r = ac.norm_row(dict(sector="gas", us=False, state="", place="", place_kind="", opposition=True, kind="none", tone=0))
        self.assertEqual(r["kind"], "other_opposition")
        self.assertIn("kind_none_with_opposition", r["fixed"])

    def test_a_state_without_us_is_dropped(self):
        r = ac.norm_row(dict(sector="gas", us=False, state="TX", place="", place_kind="", opposition=False, kind="none", tone=0))
        self.assertEqual(r["state"], "")
        self.assertIn("state_without_us:TX", r["fixed"])

    def test_the_schema_and_the_prompt_agree_with_the_constants(self):
        props = ac.SCHEMA["properties"]["results"]["items"]["properties"]
        self.assertEqual(props["s"]["enum"], ac.SECTORS)
        self.assertEqual(props["k"]["enum"], ac.KINDS)
        self.assertEqual(props["pk"]["enum"], ac.PLACE_KINDS)
        self.assertEqual(props["t"]["enum"], ac.TONES)
        self.assertEqual(set(ac.KEYS), set(props))
        for s in ac.SECTORS + ac.KINDS:
            self.assertIn(s, ac.SYSTEM, s)
        self.assertNotIn(chr(0x2014), ac.SYSTEM)
        self.assertNotIn(chr(0x2013), ac.SYSTEM)

    def test_the_batch_index_maps_back_to_the_story(self):
        rows = pd.DataFrame([dict(event_id="news:a", title="A", summary="a"), dict(event_id="news:b", title="B", summary="b")])
        items = ac.items_of(rows)
        self.assertEqual([i["i"] for i in items], [0, 1])
        self.assertEqual(items[1]["title"], "B")


class Accuracy(unittest.TestCase):
    """The stored answers of the trial of 6 November 2026 against the hand labels."""

    def setUp(self):
        self.lab = read("labeled_200.csv")

    def test_sonnet_the_run_model_meets_the_floors(self):
        r = ac.accuracy(self.lab, read("model_200_sonnet.csv"))
        self.assertEqual(r["n"], 200)
        self.assertGreaterEqual(r["by_field"]["opposition"], 0.95)
        self.assertGreaterEqual(r["friction"]["f1"], 0.85)
        self.assertGreaterEqual(r["friction"]["precision"], 0.9)
        self.assertGreaterEqual(r["by_field"]["sector"], 0.9)
        self.assertGreaterEqual(r["sector_index"], 0.95)
        self.assertGreaterEqual(r["by_field"]["state"], 0.95)
        self.assertGreaterEqual(r["by_field"]["us"], 0.9)
        self.assertGreaterEqual(r["by_field"]["tone"], 0.8)

    def test_haiku_the_comparison_is_recorded_and_weaker_on_us(self):
        r = ac.accuracy(self.lab, read("model_200_haiku.csv"))
        self.assertEqual(r["n"], 200)
        self.assertGreaterEqual(r["by_field"]["opposition"], 0.9)
        self.assertLess(r["by_field"]["us"], 0.9)

    def test_accuracy_counts_disagreements_once_a_field(self):
        ans = self.lab.copy()
        ans.loc[0, "sector"] = "zzz"
        r = ac.accuracy(self.lab, ans)
        self.assertEqual(r["by_field"]["sector"], 0.995)
        self.assertEqual(len(r["disagreements"]), 1)
        self.assertEqual(r["by_field"]["opposition"], 1.0)
        self.assertEqual(r["friction"]["f1"], 1.0)


if __name__ == "__main__":
    unittest.main()

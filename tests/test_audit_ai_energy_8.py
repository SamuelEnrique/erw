"""Audit of "Energy per AI query, as published" (/ai-energy), finding 8 (session 10221,
docs/reviews/ai-energy-model-audit-2026-11-26.md): the method note (docs/methods/ai_energy_published.md, Limits) said of
the figures that are one publisher's estimate of another's model "`x_basis` says so". The three rows' basis says "the
paper's estimate" and names no other maker; GPT-3's subject names OpenAI, the search's names So and others, BERT's names
no maker.

1. The page's file: the three rows' basis names no other maker; the subjects as said. Passes on main.
2. The fix on this branch, words only: the note says what the rows say. Fails on main."""
import json
import os
import unittest

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))


def src(*p):
    with open(os.path.join(ROOT, *p), encoding="utf-8") as f:
        return f.read()


class TheNoteSaysWhatTheRowsSay(unittest.TestCase):
    def test_the_basis_names_no_other_maker(self):
        by = {r["event_id"]: r for r in json.loads(src("site", "data", "ai_energy.json"))["rows"]}
        for k in ("ai_energy:strubell_2019_1", "ai_energy:strubell_2019_2", "ai_energy:patterson_2021_5"):
            self.assertTrue(by[k]["x_basis"].startswith("the paper's estimate"), k)
            for maker in ("Google", "OpenAI", "So et al"):
                self.assertNotIn(maker, by[k]["x_basis"], k)
        self.assertIn("OpenAI's model", by["ai_energy:patterson_2021_5"]["x_subject"])
        self.assertIn("So et al.", by["ai_energy:strubell_2019_2"]["x_subject"])
        self.assertEqual(by["ai_energy:strubell_2019_1"]["x_subject"], "BERT base on 64 V100 GPUs")

    def test_the_note_says_what_the_rows_say(self):
        note = " ".join(src("docs", "methods", "ai_energy_published.md").split())
        self.assertNotIn("a neural architecture search); `x_basis` says so.", note)
        self.assertIn("`x_basis` says \"the paper's estimate\" on each, and names no other maker; the subject names it for GPT-3", note)


if __name__ == "__main__":
    unittest.main()

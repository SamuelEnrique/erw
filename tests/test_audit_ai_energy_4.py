"""Audit of "Energy per AI query, as published" (/ai-energy), finding 4 (session 10221,
docs/reviews/ai-energy-model-audit-2026-11-26.md): the headline said "2 of them peer-reviewed papers", a fact as a reader
takes it. The count is of rows whose publisher kind is "peer-reviewed paper", and the method note's rule says yes only
where the page read names the venue (ACL 2019; ACM FAccT '24). A paper that appeared in a journal whose arXiv page does not
name it is counted as a preprint, and the publisher kind puts a venue where a publisher belongs (Hugging Face's FAccT
paper is "peer-reviewed paper", its BLOOM paper "model maker").

1. The page's file: 2 titles of publisher kind "peer-reviewed paper", each naming its venue in x_peer_reviewed; the method
   note holds the rule. Passes on main.
2. The fix on this branch, words only: the headline note says the count follows that rule. Fails on main."""
import json
import os
import unittest

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))


def src(*p):
    with open(os.path.join(ROOT, *p), encoding="utf-8") as f:
        return f.read()


class TheCountSaysItsRule(unittest.TestCase):
    def test_two_by_the_rule(self):
        rows = json.loads(src("site", "data", "ai_energy.json"))["rows"]
        peer = {r["x_title"]: r["x_peer_reviewed"] for r in rows if r["x_publisher_kind"] == "peer-reviewed paper"}
        self.assertEqual(sorted(peer.values()), ["yes (ACL 2019)", "yes (ACM FAccT '24)"])
        self.assertIn("says yes only where the page read names the venue", src("docs", "methods", "ai_energy_published.md"))
        kinds = {r["parties"]: r["x_publisher_kind"] for r in rows}
        self.assertEqual(kinds["Hugging Face and Carnegie Mellon University"], "peer-reviewed paper")
        self.assertEqual(kinds["Hugging Face (BigScience) with Graphcore and LISN"], "model maker")

    def test_the_headline_note_says_the_rule(self):
        self.assertIn("note={`${peer} of them peer-reviewed papers, counted only where the page the ERW read names the venue`}",
                      src("site", "app", "ai-energy", "page.tsx"))


if __name__ == "__main__":
    unittest.main()

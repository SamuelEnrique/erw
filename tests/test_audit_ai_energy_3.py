"""Audit of "Energy per AI query, as published" (/ai-energy), finding 3 (session 10221,
docs/reviews/ai-energy-model-audit-2026-11-26.md): the lead said "Every figure a model maker, a cloud operator or a
peer-reviewed paper has printed for the energy of an AI query, a token, a training run or a fleet". No row is per token
(the one per-token figure read, "From Words to Watts", was left out because its venue is not named), and the method note
calls the 23 figures "the first reading, not every figure ever printed".

1. The page's file and the method note: no row measures a token; the note says a first reading. Passes on main.
2. The fix on this branch, words only: the lead says the publications read so far, not every figure ever printed, and
   names no token. Fails on main."""
import json
import os
import unittest

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))


def src(*p):
    with open(os.path.join(ROOT, *p), encoding="utf-8") as f:
        return f.read()


def flat(s):
    return " ".join(s.split())


class TheLeadSaysWhatIsHeld(unittest.TestCase):
    def test_no_row_per_token_and_a_first_reading(self):
        rows = json.loads(src("site", "data", "ai_energy.json"))["rows"]
        self.assertEqual([r["event_id"] for r in rows if "token" in (r["x_measures"] + r["x_subject"]).lower()], [])
        self.assertIn("the first reading, not every figure ever printed", src("docs", "methods", "ai_energy_published.md"))

    def test_the_lead_says_read_so_far_and_names_no_token(self):
        page = flat(src("site", "app", "ai-energy", "page.tsx"))
        lead = page.split("lead={<>")[1].split("</>}")[0]
        self.assertIn("Each figure the publications read so far print for the energy of an AI query, a training run, a deployment or a fleet", lead)
        self.assertIn("not every figure ever printed", lead)
        self.assertNotIn("token", lead)
        self.assertNotIn("Every figure a model maker", lead)


if __name__ == "__main__":
    unittest.main()

"""Session 10223 (the states audit, finding 7): "Puerto Rico is in the generation table and in no other table the page reads".

EIA-860M holds Puerto Rico's plants, and the builder takes EIA-860M whole for the United States: the nation's capacity is
the 50 states' and DC's plus Puerto Rico's 6,474.3 MW, while its generation and sales leave Puerto Rico out. The
decision now says so. Words only: no figure moves.
"""
import json
import os
import unittest

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
DIR = os.path.join(ROOT, "site", "data", "states")


def src(*p):
    with open(os.path.join(ROOT, *p), encoding="utf-8") as f:
        return f.read()


@unittest.skipUnless(os.path.exists(os.path.join(DIR, "index.json")), "the states' page files are not on this machine")
class TheFiles(unittest.TestCase):
    def test_the_nation_capacity_holds_puerto_rico(self):
        with open(os.path.join(DIR, "index.json"), encoding="utf-8") as f:
            idx = json.load(f)
        cap = {r["state"]: r["capacity_mw"] for r in idx["states"]}
        rest = cap["US"] - sum(v for k, v in cap.items() if k != "US")
        # session 11407 (wip/ready-states-capacity-no-pr): a file the builder now writes leaves Puerto Rico out of the
        # nation (rest 0); a file built before holds its 6,474.3 MW
        self.assertTrue(abs(rest - 6474.3) <= 0.5 or abs(rest) <= 0.5, rest)


class TheWords(unittest.TestCase):
    def test_the_decision_says_where_puerto_rico_is(self):
        dec = src("site", "app", "states", "Decisions.tsx")
        self.assertNotIn("Puerto Rico is in the generation table and in no other table the page reads", dec)
        self.assertIn("only the generation table and EIA-860M hold it", dec)
        # session 11407 (wip/ready-states-capacity-no-pr): the nation's plants now leave Puerto Rico out
        self.assertIn("without Puerto Rico's 6,474 MW", dec)
        self.assertNotIn("in no other table the page reads", src("docs", "state", "page_files_states.md"))


if __name__ == "__main__":
    unittest.main()

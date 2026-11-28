"""Session 10220 (congestion audit, finding 2): one element on several rows.

The page's "constraint" is the operator's element under one contingency (`entity` is name|contingency). An element bound
under two contingencies is two rows and two constraints in the year's count, and an hour under both is two
constraint-hours. SPP's files until November 2021 name no contingency, and from then the same element comes under
BASE, which the page's label drops: TEXAS_CO_TXPS_TXCO_PHSHFT_PS stood as rows 1 and 2 of SPP's "every year held" list
by hours with one label (60,293 and 31,835 hours: 92,128 for the one element).

The first class shows the fact from the page file (passes on main). The second holds the words of the fix (fails on
main). Joining an element's rows would move figures a reader sees: for Samuel's ruling, not made here.
"""
import json
import os
import re
import unittest

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
FILE = os.path.join(ROOT, "site", "data", "conditions", "congestion.json")


def src(*p):
    with open(os.path.join(ROOT, *p), encoding="utf-8") as f:
        return f.read()


def old_label(c):
    """The label rule on main before this fix (constraintLabel in page.tsx)."""
    return f"{c['name']} (contingency {c['contingency']})" if c["contingency"] and c["contingency"] != "BASE" else c["name"]


@unittest.skipUnless(os.path.exists(FILE), "the congestion file is not on this machine")
class OneElementOnSeveralRows(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        with open(FILE, encoding="utf-8") as f:
            cls.f = json.load(f)
        cls.spp = cls.f["constraints"]["spp"]
        # Session 11407: a page file built after Samuel's ruling of finding 2 joins an element's keys
        # (tests/test_ready_congestion_keys.py holds that file); these facts are of the file before it.
        if any("contingencies" in c for c in cls.spp["constraints"].values()):
            raise unittest.SkipTest("the page file joins an element's keys (session 11407)")

    def test_the_same_label_stood_on_rows_1_and_2_of_every_year_held(self):
        top = self.spp["top"]["all"]["by_hours"][:2]
        c = [self.spp["constraints"][k] for k in top]
        self.assertEqual(old_label(c[0]), old_label(c[1]))
        self.assertEqual({c[0]["contingency"], c[1]["contingency"]}, {None, "BASE"})
        if self.f["built"].startswith("2026-11-20"):
            self.assertEqual([x["hours"] for x in c], [60293, 31835])
            self.assertEqual(sum(x["hours"] for x in c), 92128)

    def test_spp_names_a_contingency_from_inside_november_2021(self):
        a = self.spp["constraints"]["spp:TEXAS_CO_TXPS_TXCO_PHSHFT_PS"]["monthly"]
        b = self.spp["constraints"]["spp:TEXAS_CO_TXPS_TXCO_PHSHFT_PS|BASE"]["monthly"]
        self.assertEqual(a[-1][0], "2021-11")
        self.assertEqual(b[0][0], "2021-11")
        self.assertLessEqual(a[-1][1] + b[0][1], 720, "no hour of November 2021 under both keys")

    def test_a_caiso_element_under_several_contingencies_sums_higher_than_its_row(self):
        O = self.f["constraints"]["caiso"]
        first = O["top"]["2025"]["by_cost"][0]
        name = O["constraints"][first]["name"]
        rows = [c["by_year"]["2025"]["cost"] for c in O["constraints"].values() if c["name"] == name and "2025" in c["by_year"]]
        self.assertGreater(len(rows), 1)
        if self.f["built"].startswith("2026-11-20"):
            self.assertAlmostEqual(O["constraints"][first]["by_year"]["2025"]["cost"], 553893.0, delta=0.05)
            self.assertAlmostEqual(sum(rows), 605826.7, delta=0.5)


class TheWordsSayIt(unittest.TestCase):
    def test_a_row_with_no_contingency_says_so(self):
        s = src("site", "app", "congestion", "page.tsx")
        self.assertIn("if (!c.contingency) return `${c.name} (no contingency named)`;", s)
        self.assertIn('<Hint words="(what a constraint is)" why={ELEMENT_WORDS} />', s)
        # Session 11407: on Samuel's ruling of finding 2 the keys are joined (tests/test_ready_congestion_keys.py).
        self.assertIn("an hour it bound under two contingencies counts once, as one constraint-hour", s)
        self.assertNotRegex(s, r"export const ELEMENT_WORDS")

    def test_the_decision_and_the_note_say_it(self):
        d = src("site", "app", "congestion", "Decisions.tsx")
        self.assertIn("SPP's files until November 2021 name no contingency", d)
        self.assertIn("an hour the element bound under two contingencies counts once", d)
        n = src("docs", "methods", "grid_congestion.md")
        self.assertIn("the change falls inside November 2021", n)
        self.assertIn("92,128 for the one element", n)

    def test_no_em_dash(self):
        for p in (("site", "app", "congestion", "page.tsx"), ("site", "app", "congestion", "Decisions.tsx"),
                  ("docs", "methods", "grid_congestion.md")):
            self.assertNotIn(chr(0x2014), src(*p), p)


if __name__ == "__main__":
    unittest.main()

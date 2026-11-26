"""Session 10220 (congestion audit, finding 1): a congestion part is measured against its own operator's reference.

Each operator splits its day-ahead price into energy, congestion and loss (and greenhouse gas at CAISO) against its own
reference: the energy part is the same at every place of one operator in every month the page file holds, so a
congestion part compares places of one operator only. /congestion ranks SPP's and CAISO's places in one table ("the
largest addition first") and said the part is "the part of each hub's and zone's price that came from congestion".

The first class shows the fact from the page file (it passes on main). The second holds the words the fix adds to the
page, its decisions and its method note (it fails on main). Ranking each operator's places apart would move the order
a reader sees: for Samuel's ruling, not made here.
"""
import json
import os
import unittest

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
FILE = os.path.join(ROOT, "site", "data", "conditions", "congestion.json")


def src(*p):
    with open(os.path.join(ROOT, *p), encoding="utf-8") as f:
        return f.read()


@unittest.skipUnless(os.path.exists(FILE), "the congestion file is not on this machine")
class TheReferenceIsEachOperatorsOwn(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        with open(FILE, encoding="utf-8") as f:
            cls.f = json.load(f)

    def test_the_energy_part_is_the_same_at_every_place_of_an_operator(self):
        for op, places in self.f["places"].items():
            months = {}
            for p in places:
                for m in p["monthly"]:
                    if m[3] is not None:
                        months.setdefault(m[0], set()).add(m[3])
            self.assertTrue(months, op)
            for mon, e in months.items():
                self.assertEqual(len(e), 1, f"{op} {mon}: {e}")

    def test_the_places_table_ranks_both_operators_in_one_list(self):
        y = "2026"
        rows = sorted(((p["id"], p["by_year"][y]["congestion_mean"]) for ps in self.f["places"].values() for p in ps
                       if y in p["by_year"]), key=lambda t: -t[1])
        ops = [pid.split(":")[0] for pid, _ in rows]
        self.assertEqual(set(ops), {"spp", "caiso"})
        # as measured on the file of 20 November 2026: SDG&E's load area first, SPP North second
        if self.f["built"].startswith("2026-11-20"):
            self.assertEqual([pid for pid, _ in rows[:2]], ["caiso:DLAP_SDGE-APND", "spp:SPPNORTH_HUB"])

    def test_two_places_spread_is_their_congestion_and_loss_parts(self):
        P = {p["id"]: p for ps in self.f["places"].values() for p in ps}

        def ymean(pid, y, col):
            ms = [m for m in P[pid]["monthly"] if m[0][:4] == y]
            return sum(m[1] * m[col] for m in ms) / sum(m[1] for m in ms)
        a, b, y = "caiso:TH_SP15_GEN-APND", "caiso:TH_NP15_GEN-APND", "2025"
        spread = ymean(a, y, 2) - ymean(b, y, 2)
        cong = ymean(a, y, 4) - ymean(b, y, 4)
        loss = ymean(a, y, 5) - ymean(b, y, 5)
        self.assertAlmostEqual(spread, cong + loss, delta=0.02)
        self.assertAlmostEqual(cong, -4.99, delta=0.01)
        self.assertAlmostEqual(loss, -1.02, delta=0.01)


class TheWordsSayIt(unittest.TestCase):
    def test_the_page_says_what_the_part_is_measured_against(self):
        s = src("site", "app", "congestion", "page.tsx")
        self.assertIn('data-reference-line="1"', s)
        self.assertIn("Each operator splits its price against its own reference", s)
        self.assertIn("a rank across the two operators means nothing", s)
        self.assertIn("with the difference of their loss parts", s)
        self.assertIn("measured against its own reference price", s)
        self.assertNotIn("price that came from congestion", s)
        self.assertNotIn("export const REFERENCE_WORDS", s, "a page file exports only what Next.js allows")

    def test_the_decision_and_the_note_say_it(self):
        self.assertIn("not SPP's with CAISO's", src("site", "app", "congestion", "Decisions.tsx"))
        note = src("docs", "methods", "grid_congestion.md")
        self.assertIn("measured against the operator's own reference price", note)
        self.assertIn("a rank that mixes SPP's places with CAISO's means nothing", note)

    def test_no_em_dash(self):
        for p in (("site", "app", "congestion", "page.tsx"), ("site", "app", "congestion", "Decisions.tsx"),
                  ("docs", "methods", "grid_congestion.md")):
            self.assertNotIn(chr(0x2014), src(*p), p)


if __name__ == "__main__":
    unittest.main()

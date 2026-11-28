"""Session 11407 (chain 770, part C): the ruling on congestion audit finding 1 readied, the places table holds only the
chosen operator's places.

Each operator splits its day-ahead price against its own reference (the energy part is the same at every place of one
operator in every month the page file holds), so a congestion part compares places of one operator only. Carried over
from tests/test_audit_congestion_1.py (branch wip/audit-congestion-1), which showed /congestion ranking SPP's and CAISO's
places in one table; here the page ranks the chosen operator's places alone. On the file built 2026-11-28: the SPP view
goes from 9 rows to 2 (SPP North 1 of 9 becomes 1 of 2), the CAISO view from 9 rows to 7 (PG&E 3 of 9 becomes 2 of 7).
"""
import json
import os
import unittest

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
FILE = os.path.join(ROOT, "site", "data", "conditions", "congestion.json")


def src(*p):
    with open(os.path.join(ROOT, *p), encoding="utf-8") as f:
        return f.read()


def ranked(f, op, py):
    """The places table as page.tsx now builds it: the chosen operator's places, the largest mean congestion part first."""
    rows = [p for ps in f["places"].values() for p in ps if p["id"].startswith(f"{op}:") and py in p["by_year"]]
    return sorted(rows, key=lambda p: -(p["by_year"][py]["congestion_mean"] or 0))


@unittest.skipUnless(os.path.exists(FILE), "the congestion file is not on this machine")
class EachOperatorsPlacesApart(unittest.TestCase):
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

    def test_each_view_holds_its_own_operators_places_only(self):
        y = "2026"
        for op in ("spp", "caiso"):
            rows = ranked(self.f, op, y)
            self.assertTrue(rows, op)
            self.assertEqual({p["id"].split(":")[0] for p in rows}, {op})
            self.assertEqual(len(rows), len([p for p in self.f["places"][op] if y in p["by_year"]]))
        self.assertEqual({p["id"] for p in ranked(self.f, "spp", y)}, {"spp:SPPNORTH_HUB", "spp:SPPSOUTH_HUB"})
        self.assertEqual(len(ranked(self.f, "caiso", y)), 7)
        if self.f["built"].startswith("2026-11-28"):
            self.assertEqual(ranked(self.f, "spp", y)[0]["id"], "spp:SPPNORTH_HUB")
            self.assertEqual([p["id"] for p in ranked(self.f, "caiso", y)][:2], ["caiso:DLAP_SDGE-APND", "caiso:DLAP_PGAE-APND"])


class ThePageDoesIt(unittest.TestCase):
    def test_the_table_filters_by_the_chosen_operator(self):
        s = src("site", "app", "congestion", "page.tsx")
        self.assertIn("const ranked = PLACES.filter((p) => p.id.startsWith(`${op}:`) && p.by_year[py])", s)
        self.assertIn("caption={`${F.operators.find((o) => o.id === op)?.name}: hubs and zones by their mean congestion part", s)
        self.assertIn("the table holds only the chosen operator's places: a rank across the two operators means nothing", s)
        self.assertNotIn("SPP's and CAISO's places are ranked in one table here", s)
        self.assertNotRegex(s, r"export const REFERENCE_WORDS")

    def test_the_decision_and_the_note_say_it(self):
        self.assertIn("The places table holds only the chosen operator's places.", src("site", "app", "congestion", "Decisions.tsx"))
        note = src("docs", "methods", "grid_congestion.md")
        self.assertIn("the page's places table holds only the chosen operator's places", note)

    def test_no_em_dash(self):
        for p in (("site", "app", "congestion", "page.tsx"), ("site", "app", "congestion", "Decisions.tsx"),
                  ("docs", "methods", "grid_congestion.md")):
            self.assertNotIn(chr(0x2014), src(*p), p)


if __name__ == "__main__":
    unittest.main()

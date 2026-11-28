"""Session 8014, chain 581 (part C): where and when power is spare (/curtailment/where-when) and its page file."""
import json
import os
import re
import unittest

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
FILE = os.path.join(ROOT, "site", "data", "curtailment", "where_when.json")


def src(*p):
    with open(os.path.join(ROOT, *p), encoding="utf-8") as f:
        return f.read()


@unittest.skipUnless(os.path.exists(FILE), "the where-and-when file is not on this machine")
class TheFile(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        with open(FILE, encoding="utf-8") as f:
            cls.f = json.load(f)

    def test_no_held_grid_is_drawn(self):
        drawn = {p["grid"] for p in self.f["prices"]}
        for g in ("nyiso", "isone", "miso", "pjm"):
            self.assertNotIn(g, drawn)
            self.assertIn(g, self.f["price_blank"])
        self.assertIn("license needed", self.f["price_blank"]["nyiso"]["words"])

    def test_ercot_curtailment_is_not_drawn(self):
        self.assertEqual([c["id"] for c in self.f["curtailment"]], ["caiso", "spp"])
        self.assertIn("ERCOT publishes no curtailment", self.f["curtailment_not_held"]["ercot"])

    def test_cells_are_twelve_by_twenty_four_and_counts_fit(self):
        for p in self.f["prices"]:
            for y, m in p["matrix"].items():
                self.assertEqual(len(m["negative"]), 12)
                for i in range(12):
                    self.assertEqual(len(m["held"][i]), 24)
                    for h in range(24):
                        self.assertLessEqual(m["negative"][i][h], m["held"][i][h])
                self.assertEqual(sum(map(sum, m["negative"])), p["by_year"][y]["negative"], f"{p['id']} {y}")

    def test_a_partial_year_has_no_share(self):
        for p in self.f["prices"]:
            for y, r in p["by_year"].items():
                if not r["whole"]:
                    self.assertIsNone(r["share_negative_pct"])

    def test_caiso_years_sum_their_months(self):
        with open(os.path.join(ROOT, "site", "data", "curtailment_profile.json"), encoding="utf-8") as f:
            prof = json.load(f)
        c = self.f["curtailment"][0]
        s = sum(r["curtailed_solar_mwh"] for m, r in prof["months"].items() if m.startswith("2025"))
        self.assertAlmostEqual(c["by_year"]["2025"]["solar"], s, delta=1)
        self.assertFalse(c["by_year"][c["years"][-1]]["whole"] and c["years"][-1] == "2026")

    def test_ranked_leaves_out_averages(self):
        self.assertTrue(self.f["ranked_negative"])
        self.assertNotIn("average", {r["kind"] for r in self.f["ranked_negative"]})
        shares = [r["share_negative_pct"] for r in self.f["ranked_negative"]]
        self.assertEqual(shares, sorted(shares, reverse=True))


class TheView(unittest.TestCase):
    def setUp(self):
        self.page = src("site", "app", "curtailment", "where-when", "page.tsx")

    def test_the_page_as_it_is_does_not_change(self):
        self.assertNotIn("where_when", src("site", "app", "curtailment", "page.tsx"))

    def test_two_places_and_no_advice(self):
        self.assertIn('name="a"', self.page)
        self.assertIn('name="b"', self.page)
        self.assertIn("no advice on where to put a load", self.page)

    def test_in_no_menu(self):
        self.assertIn('{ href: "/curtailment/where-when", label: "Where and when power is spare"', src("site", "lib", "pages.ts"))   # session 11405 (decision 4 of the weekend page of 28 November 2026, readied): in the menu under its own name
        self.assertNotIn("/curtailment/where-when", src("site", "lib", "release.ts"))

    def test_no_em_dash(self):
        for p in (("site", "app", "curtailment", "where-when", "page.tsx"), ("site", "app", "curtailment", "where-when", "Decisions.tsx"),
                  ("site", "lib", "wherewhen.ts"), ("warehouse", "derived", "where_when.py"), ("docs", "methods", "where_when.md"),
                  ("docs", "state", "page_files_curtailment.md")):
            self.assertNotIn(chr(0x2014), src(*p))

    def test_the_fold_and_the_note_are_one_list(self):
        keys = re.findall(r'\{ key: "([a-z0-9-]+)", session: "', src("site", "app", "curtailment", "where-when", "Decisions.tsx"))
        note = src("docs", "methods", "where_when.md").split("### Decisions (session 8014)")[1]
        self.assertEqual(re.findall(r"^\| `([a-z0-9-]+)` \|", note, re.M), keys)
        self.assertEqual(len(keys), 8)


if __name__ == "__main__":
    unittest.main()

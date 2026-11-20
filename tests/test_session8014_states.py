"""Session 8014, chain 581 (part B): every state on one page (/states) and its page files (site/data/states/)."""
import json
import os
import re
import unittest

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
DIR = os.path.join(ROOT, "site", "data", "states")
PARTS = ["generation", "retail", "plants", "co2", "gas", "energy", "disposition", "serving", "large_load_laws", "severance"]
SOURCES = ["coal", "natural_gas", "nuclear", "hydro", "wind", "solar", "other_renewables", "oil_and_other", "not_itemized"]


def src(*p):
    with open(os.path.join(ROOT, *p), encoding="utf-8") as f:
        return f.read()


def load(name):
    with open(os.path.join(DIR, name), encoding="utf-8") as f:
        return json.load(f)


@unittest.skipUnless(os.path.exists(os.path.join(DIR, "index.json")), "the states' page files are not on this machine")
class TheFiles(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.index = load("index.json")
        cls.files = {r["state"]: load(r["file"]) for r in cls.index["states"]}

    def test_fifty_states_dc_and_the_nation(self):
        codes = set(self.files)
        self.assertEqual(len(codes), 52)
        self.assertIn("DC", codes)
        self.assertIn("US", codes)
        self.assertNotIn("PR", codes)
        self.assertEqual(self.index["contract"], "docs/state/page_files_states.md")

    def test_every_part_names_its_table(self):
        for st, f in self.files.items():
            self.assertEqual(f["license"], "public")
            for p in PARTS:
                self.assertIn(p, f, f"{st} {p}")
                self.assertTrue(f[p].get("table") or f[p].get("file"), f"{st} {p}")

    def test_monthly_since_2001_and_never_hourly(self):
        for st, f in self.files.items():
            g = f["generation"]
            self.assertEqual(g["months"][0], "2001-01", st)
            self.assertIsNone(g["hourly"])
            self.assertIn("by the hour", g["hourly_reason"])
            for k in SOURCES:
                self.assertEqual(len(g["by_source"][k]), len(g["months"]))

    def test_a_missing_source_is_null_not_zero(self):
        # Vermont has had no coal or nuclear generation in EIA's table since its last plant closed
        vt = self.files["VT"]["generation"]["last12"]
        self.assertIsNone(vt["mwh"]["nuclear"])
        self.assertIsNone(vt["share_pct"]["nuclear"])
        dc = self.files["DC"]["gas"]
        self.assertIsNone(dc["marketed_production"])
        self.assertTrue(dc["production_reason"])

    def test_shares_sum_to_the_whole(self):
        for st, f in self.files.items():
            s = sum(v for v in f["generation"]["last12"]["share_pct"].values() if v is not None)
            self.assertAlmostEqual(s, 100, delta=0.1, msg=st)
            if f["serving"].get("by_authority") and not f["serving"].get("shares_reason"):
                self.assertAlmostEqual(sum(a["share_pct"] for a in f["serving"]["by_authority"]), 100, delta=0.1, msg=st)

    def test_revenue_is_sales_times_price(self):
        r = self.files["CA"]["retail"]
        for i in (-1, -13, 0):
            s, p, v = r["sales_mwh"]["residential"][i], r["price_usd_per_mwh"]["residential"][i], r["revenue_usd"]["residential"][i]
            if s is not None and p is not None:
                self.assertAlmostEqual(v, s * p, delta=1)

    def test_generation_matches_the_state_profile(self):
        for st in ("CA", "TX", "NY", "WV", "VT"):
            f = self.files[st]
            g, d = f["generation"], f["disposition"]
            mine = g["annual"]["total"][g["years"].index("2024")]
            prof = d["values"]["total_net_generation"][d["years"].index("2024")]
            self.assertLess(abs(mine - prof) / prof, 1e-4, st)

    def test_connecticut_has_no_share_by_people(self):
        ct = self.files["CT"]["serving"]
        self.assertTrue(ct["shares_reason"])
        self.assertTrue(all(a["share_pct"] is None for a in ct["by_authority"]))
        self.assertEqual(ct["by_authority"][0]["code"], "ISNE")

    def test_ten_largest_plants_in_order(self):
        for st, f in self.files.items():
            mw = [p["nameplate_mw"] for p in f["plants"]["largest"] or []]
            self.assertLessEqual(len(mw), 10)
            self.assertEqual(mw, sorted(mw, reverse=True), st)


class ThePage(unittest.TestCase):
    def setUp(self):
        self.page = src("site", "app", "states", "page.tsx")

    def test_it_reads_the_files_not_the_database(self):
        self.assertIn("readState", self.page)
        self.assertNotIn("supabase", self.page.lower())

    def test_in_no_menu_and_in_review(self):
        self.assertNotIn('"/states"', src("site", "lib", "pages.ts"))
        self.assertNotIn('"/states"', src("site", "lib", "release.ts"))

    def test_two_side_by_side_and_monthly_said_once(self):
        self.assertIn('name="a"', self.page)
        self.assertIn('name="b"', self.page)
        self.assertEqual(self.page.count("data-monthly-note"), 1)

    def test_no_em_dash(self):
        for p in (("site", "app", "states", "page.tsx"), ("site", "app", "states", "Decisions.tsx"), ("site", "lib", "states.ts"),
                  ("warehouse", "derived", "states_page.py"), ("docs", "methods", "states_page.md"), ("docs", "state", "page_files_states.md")):
            self.assertNotIn(chr(0x2014), src(*p))


class TheDecisions(unittest.TestCase):
    def test_the_fold_and_the_note_are_one_list(self):
        keys = re.findall(r'\{ key: "([a-z0-9-]+)", session: "', src("site", "app", "states", "Decisions.tsx"))
        note = src("docs", "methods", "states_page.md").split("### Decisions (session 8014)")[1]
        self.assertEqual(re.findall(r"^\| `([a-z0-9-]+)` \|", note, re.M), keys)
        self.assertEqual(len(keys), 10)


if __name__ == "__main__":
    unittest.main()

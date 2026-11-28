"""Session 11407 (chain 770, part C): the owner's other choice on the companies audit's finding 2 (session 10228,
docs/reviews/companies-model-audit-2026-11-26.md; the audit's test was tests/test_audit_companies_8.py on
wip/audit-companies-8), readied, not landed until Samuel rules.

/companies orders by the footprint. On origin/main the page files' footprint (warehouse/derived/companies_page.py,
figures) adds a company's operating MW (every generator it operates, whole) and its owned MW (its share of each jointly
owned generator), so a jointly owned generator it also operates counts twice. On this branch the builder leaves that
share out of the footprint; owned_mw itself is unchanged.

The committed page files (site/data/companies/, the desk's rebuild of 26 November) are not rebuilt here: the builder
reads company_directory, company_aliases and company_links, which this machine does not hold. Each listed company's
public links are in its shard, so this test runs the branch's figures() on them: every figure but the footprint is the
file's, and the footprint is the file's less the double count. The site files are rebuilt at landing by the desk
(python warehouse/derived/companies_page.py); until then tests/test_session3304_companies.py's shard test fails for the
companies whose footprint falls, by design.

Measured on the committed files: 106 companies hold a double count, 62,735.8 MW; in the new order 5 of the first 10
change places (Entergy Louisiana seventh to fourth, Georgia Power fourth to sixth, Virginia Electric fifth to seventh,
Duke Energy Carolinas sixth to fifth) and PacifiCorp leaves the first 10 for RWE Americas (the audit, on the files of
16 November, named DTE Electric; the files were rebuilt since); 41 of the first 50 move and 2 leave."""
import json
import os
import sys
import unittest

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
sys.path.insert(0, os.path.join(ROOT, "warehouse", "derived"))
import companies_page as P  # noqa: E402


def load():
    d = os.path.join(ROOT, "site", "data", "companies")
    with open(os.path.join(d, "index.json"), encoding="utf-8") as f:
        ix = json.load(f)
    comp = {}
    for name in os.listdir(os.path.join(d, "c")):
        with open(os.path.join(d, "c", name), encoding="utf-8") as f:
            comp.update(json.load(f))
    return ix, comp


def overlap(c, tables):
    operated = {tuple(l[2].split(":")[1:3]) for l in c["links"] if tables[l[1]] == "eia860m_operating_generators"}
    return sum(float(l[6]) for l in c["links"]
               if tables[l[1]] == "eia860_generator_owners" and l[6] != "" and tuple(l[2].split(":")[1:3]) in operated)


class TheFootprintCountsEachGeneratorOnce(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.ix, cls.comp = load()
        t = cls.ix["tables"]
        cls.rows = [dict(zip(cls.ix["columns"], r)) for r in cls.ix["rows"]]
        cls.ov = {r["id"]: overlap(cls.comp[r["id"]], t) for r in cls.rows}
        cls.new = {}
        for r in cls.rows:
            links = [dict(input_table=t[l[1]], input_row=l[2], role=l[3], mw=l[6], usd=l[7], date=l[8], fuel=l[9],
                          state=l[10], grid=l[11], detail=l[12]) for l in cls.comp[r["id"]]["links"]]
            cls.new[r["id"]] = P.figures(links)[0]

    def test_the_size_of_the_double_count(self):
        twice = {k: v for k, v in self.ov.items() if v}
        self.assertEqual(len(twice), 106)
        self.assertAlmostEqual(sum(twice.values()), 62735.8, delta=0.1)

    def test_only_the_footprint_changes_and_by_the_double_count(self):
        for r in self.rows:
            new, old = dict(self.new[r["id"]]), dict(self.comp[r["id"]]["figures"])
            self.assertAlmostEqual(new.pop("footprint_mw"), old.pop("footprint_mw") - self.ov[r["id"]], delta=0.21, msg=r["id"])
            self.assertEqual(new, old, r["id"])
        f = self.new["eia-6452"]                        # Florida Power & Light: St. Lucie unit 2's share among its rows
        self.assertAlmostEqual(f["footprint_mw"], f["plants_mw"] + f["owned_mw"] + f["planned_mw"] + f["queue_mw"]
                               - self.ov["eia-6452"], delta=0.11)
        self.assertGreater(self.ov["eia-6452"], 900)

    def test_the_new_order(self):
        base = [r["id"] for r in self.rows]
        alt = [r["id"] for r in sorted(self.rows, key=lambda r: (-self.new[r["id"]]["footprint_mw"], -r["n_links"], r["id"]))]
        self.assertEqual(sum(1 for i in base[:10] if alt.index(i) != base.index(i)), 5)
        self.assertIn("eia-14354", base[:10])          # PacifiCorp
        self.assertNotIn("eia-14354", alt[:10])
        self.assertIn("eia-67192", alt[:10])           # RWE Americas
        self.assertEqual(alt.index("eia-11241"), 3)    # Entergy Louisiana, seventh to fourth
        self.assertEqual(sum(1 for i in base[:50] if alt.index(i) != base.index(i)), 41)
        self.assertEqual(len(set(base[:50]) - set(alt[:50])), 2)

    def test_the_builder_and_the_words(self):
        with open(os.path.join(ROOT, "warehouse", "derived", "companies_page.py"), encoding="utf-8") as f:
            b = f.read()
        self.assertIn('out["plants_mw"] + out["owned_mw"] - r1(both)', b)
        with open(os.path.join(ROOT, "site", "app", "companies", "page.tsx"), encoding="utf-8") as f:
            self.assertIn("counts once, whole in operating MW, its share in owned MW left out of the sum", f.read())


if __name__ == "__main__":
    unittest.main()

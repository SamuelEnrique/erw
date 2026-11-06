"""Sessions 3304 to 3306 (chain 200): the company pages (/companies, /companies/<id>) and their files.

Energy Research Warehouse (ERW). Runs the pure rules' tests (site/scripts/test-companies.mjs) where node and the site's
packages are installed; traces the committed files of site/data/companies/ (warehouse/derived/companies_page.py): every
listed company has its shard, the index's figures are the shard's, the shard's figures are recomputed from its own rows,
no row of a held table is in a file, and the held counts add up; and reads the site's wiring (the menu, the redirect,
the tracing). No network, no data lock.

    python -m unittest tests.test_session3304_companies -v
"""

import hashlib
import json
import os
import shutil
import subprocess
import sys
import unittest
from collections import Counter

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
DATA = os.path.join(ROOT, "site", "data", "companies")
sys.path.insert(0, os.path.join(ROOT, "warehouse", "derived"))
import companies_page as P  # noqa: E402


def src(*parts):
    with open(os.path.join(ROOT, *parts), encoding="utf-8") as f:
        return f.read()


@unittest.skipUnless(os.path.exists(os.path.join(DATA, "index.json")), "site/data/companies is not built")
class TheFiles(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        with open(os.path.join(DATA, "index.json"), encoding="utf-8") as f:
            cls.ix = json.load(f)
        cls.shards = {}
        for name in os.listdir(os.path.join(DATA, "c")):
            with open(os.path.join(DATA, "c", name), encoding="utf-8") as f:
                cls.shards[name[:-5]] = json.load(f)

    def test_every_listed_company_has_its_shard(self):
        cols = self.ix["columns"]
        ids = [r[cols.index("id")] for r in self.ix["rows"]]
        self.assertEqual(len(ids), self.ix["n_listed"])
        self.assertEqual(len(set(ids)), len(ids))
        for cid in ids:
            key = hashlib.sha1(f"company:{cid}".encode("utf-8")).hexdigest()[:2]
            self.assertIn(cid, self.shards[key], cid)
        self.assertEqual(sum(len(s) for s in self.shards.values()), len(ids))
        self.assertEqual(self.ix["n_listed"] + self.ix["held_only"], self.ix["n_directory"])

    def test_the_index_figures_are_the_shards(self):
        cols = self.ix["columns"]
        figs = [c for c in cols if c.startswith("n_") and c != "n_links" or c.endswith("_mw")]
        for r in self.ix["rows"]:
            row = dict(zip(cols, r))
            c = self.shards[hashlib.sha1(f"company:{row['id']}".encode()).hexdigest()[:2]][row["id"]]
            for k in figs:
                self.assertEqual(row[k], c["figures"][k], (row["id"], k))
            self.assertEqual(row["n_links"], len(c["links"]))

    def test_a_shard_figures_are_its_own_rows(self):
        tables, rules = self.ix["tables"], self.ix["rules"]
        n = 0
        for s in self.shards.values():
            for cid, c in s.items():
                links = [dict(input_table=tables[l[1]], input_row=l[2], role=l[3], mw=l[6], usd=l[7], date=l[8],
                              fuel=l[9], state=l[10], grid=l[11], detail=l[12]) for l in c["links"]]
                fig, fuel, years, quarters = P.figures(links)
                self.assertEqual(fig, c["figures"], cid)
                self.assertEqual(fuel, c["fuel"], cid)
                self.assertEqual([list(y) for y in years], [list(y) for y in c["years"]], cid)
                for l in c["links"]:
                    self.assertIn(rules[l[5]], P.RULES)
                n += 1
        self.assertGreater(n, 1000)

    def test_no_held_row_is_in_a_file(self):
        held = set(self.ix["held_tables"])
        pos = {i for i, t in enumerate(self.ix["tables"]) if t in held}
        counts = Counter()
        for s in self.shards.values():
            for cid, c in s.items():
                self.assertFalse([l for l in c["links"] if l[1] in pos], cid)
                self.assertTrue(set(c["held"]) <= held, cid)
                counts.update(c["held"])
                for name in c["names"]:
                    self.assertNotIn(name[1], held, cid)
        for t, k in counts.items():
            self.assertLessEqual(k, self.ix["held_links"][t])
        if "energy_deals" in held:
            self.assertNotIn("n_deals", self.ix["columns"])
        if "datacenter_facilities" in held:
            self.assertNotIn("n_facilities", self.ix["columns"])

    def test_the_index_is_in_footprint_order(self):
        cols = self.ix["columns"]
        f = [r[cols.index("footprint_mw")] for r in self.ix["rows"]]
        self.assertEqual(f, sorted(f, reverse=True))


class TheSite(unittest.TestCase):
    def test_companies_is_a_page_under_infrastructure(self):
        pages = src("site", "lib", "pages.ts")
        infra = pages[pages.index('label: "Infrastructure"'):pages.index('label: "Analysis"')]
        self.assertIn('{ href: "/companies", label: "Companies"', infra)
        self.assertNotIn('source: "/companies", destination', src("site", "next.config.ts"))
        self.assertNotIn('"/companies": "/deals?tab=companies"', src("site", "lib", "tabs.ts"))
        self.assertIn('"/companies/[id]": ["./data/companies/**/*.json"]', src("site", "next.config.ts"))

    def test_release_is_untouched_and_the_pages_are_in_review(self):
        rel = src("site", "lib", "release.ts")
        self.assertIn('"/companies": "review"', rel)
        self.assertNotIn('"/companies": "live"', rel)

    def test_every_figure_is_keyed(self):
        page = src("site", "app", "companies", "[id]", "page.tsx")
        self.assertIn("data-n={`company_directory|${c.entity_id}|${col}`}", page)
        self.assertIn("data-n={`company_links|${r.link}|mw`}", page)
        index = src("site", "app", "companies", "page.tsx")
        self.assertIn("data-n={`company_directory|company:${id}|${col}`}", index)

    def test_the_pure_rules(self):
        exe = shutil.which("node")
        if not exe:
            self.skipTest("node is not on this machine")
        if not os.path.isdir(os.path.join(ROOT, "site", "node_modules")):
            self.skipTest("the site's packages are not installed on this machine (npm ci)")
        r = subprocess.run([exe, "--import", "./scripts/alias-register.mjs", "scripts/test-companies.mjs"],
                           cwd=os.path.join(ROOT, "site"), capture_output=True, text=True, timeout=180)
        self.assertEqual(r.returncode, 0, r.stdout[-2000:] + r.stderr[-2000:])
        self.assertIn("10 tests passed", r.stdout)


if __name__ == "__main__":
    unittest.main()

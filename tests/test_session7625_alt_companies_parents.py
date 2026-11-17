"""Session 7625: the other choice of the ruling on parents' figures on /companies (branch wip/alt-companies-1, not
landed). Each legal entity keeps its own figures and none is summed into a parent; under the other choice a parent's
page sums its listed subsidiaries' operating and owned MW, each subsidiary listed.

What is held to:
  on the page's own files (site/data/companies/c/*.json, built 16 November 2026), the companies whose record states a
    parent with MW: Duke Energy 0 to 38,147.3 MW operating and 0 to 543.8 MW owned (2 subsidiaries); Dominion
    Generation 0 to 28,681.0 and 0 to 5,821.5 (3 subsidiaries); no other parent's page moves (Energy Harbor Corp.'s
    own owned share 1,144.8 stays, its one subsidiary holds no MW); Constellation Energy Corporation stays 0;
  the page reads the subsidiaries from every shard (lib/companydata.ts, subsidiaries) and draws the summed figures and
    the list only where a subsidiary holds MW.

No request, no model call."""
import glob
import json
import os
import unittest

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))


def src(*parts):
    with open(os.path.join(ROOT, *parts), encoding="utf-8") as f:
        return f.read()


class ParentsSumTheirSubsidiaries(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.all = {}
        for p in glob.glob(os.path.join(ROOT, "site", "data", "companies", "c", "*.json")):
            with open(p, encoding="utf-8") as f:
                cls.all.update(json.load(f))
        kids = {}
        for k, c in cls.all.items():
            if c.get("parent_id") and (c["figures"]["plants_mw"] > 0 or c["figures"]["owned_mw"] > 0):
                kids.setdefault(c["parent_id"], []).append(c)
        cls.kids = kids

    def summed(self, pid):
        p, ks = self.all[pid], self.kids[pid]
        return (round(p["figures"]["plants_mw"] + sum(k["figures"]["plants_mw"] for k in ks), 1),
                round(p["figures"]["owned_mw"] + sum(k["figures"]["owned_mw"] for k in ks), 1), len(ks))

    def test_the_two_parents_that_move(self):
        self.assertEqual(sorted(self.kids), ["dominion-generation", "duke-energy"])
        self.assertEqual(self.summed("duke-energy"), (38147.3, 543.8, 2))
        self.assertEqual(self.summed("dominion-generation"), (28681.0, 5821.5, 3))
        self.assertEqual((self.all["duke-energy"]["figures"]["plants_mw"], self.all["dominion-generation"]["figures"]["plants_mw"]), (0.0, 0.0))

    def test_the_page_draws_them(self):
        d = src("site", "lib", "companydata.ts")
        self.assertIn("export function subsidiaries(id: string): Company[]", d)
        p = src("site", "app", "companies", "[id]", "page.tsx")
        self.assertIn("const subs = subsidiaries(c.id).filter((s) => s.figures.plants_mw > 0 || s.figures.owned_mw > 0);", p)
        self.assertIn('"Operating, with its subsidiaries"', p)
        self.assertIn('<ToolSection title="Subsidiaries" id="subsidiaries">', p)
        for t in (d, p):
            self.assertNotIn(chr(0x2014), t)


if __name__ == "__main__":
    unittest.main()

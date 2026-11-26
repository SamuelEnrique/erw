"""Audit of the company database, finding 2, the figure for the owner's ruling (session 10228,
docs/reviews/companies-model-audit-2026-11-26.md). A test only, not for landing: it changes nothing and shows what the
other choice would do.

/companies orders by the footprint, which adds a company's operating MW (every generator it operates, whole) and its
owned MW (its share of each jointly owned generator), so a jointly owned generator it also operates counts twice. In the
page files of 16 November 2026: 360 generators at 106 companies, 62,736 MW counted twice. The other choice, the
footprint without the share of a generator the company already counts whole: 5 of the first 10 change places and
PacifiCorp leaves them for DTE Electric; 41 of the first 50 move and 2 leave. Default: left as it is."""
import json
import os
import unittest

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))


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


class TheFootprintWithoutTheDoubleCount(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.ix, cls.comp = load()
        cls.rows = [dict(zip(cls.ix["columns"], r)) for r in cls.ix["rows"]]
        cls.ov = {r["id"]: overlap(cls.comp[r["id"]], cls.ix["tables"]) for r in cls.rows}

    def test_the_size_of_the_double_count(self):
        twice = {k: v for k, v in self.ov.items() if v}
        self.assertEqual(len(twice), 106)
        self.assertAlmostEqual(sum(twice.values()), 62735.8, delta=0.1)

    def test_the_order_without_it(self):
        base = [r["id"] for r in self.rows]
        alt = [r["id"] for r in sorted(self.rows, key=lambda r: (-(r["footprint_mw"] - self.ov[r["id"]]), -r["n_links"], r["id"]))]
        self.assertEqual(sum(1 for i in base[:10] if alt.index(i) != base.index(i)), 5)
        self.assertIn("eia-14354", base[:10])          # PacifiCorp
        self.assertNotIn("eia-14354", alt[:10])
        self.assertIn("eia-5109", alt[:10])            # DTE Electric
        self.assertEqual(sum(1 for i in base[:50] if alt.index(i) != base.index(i)), 41)


if __name__ == "__main__":
    unittest.main()

"""Session 8012, chain 505 (part C): every balancing authority's own facts (site/data/regions/authority/)."""
import json
import os
import re
import unittest

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
DIR = os.path.join(ROOT, "site", "data", "regions", "authority")
PARTS = ("owns", "coming", "burns", "trades", "size", "large_loads")


def load(name):
    with open(os.path.join(DIR, name), encoding="utf-8") as f:
        return json.load(f)


@unittest.skipUnless(os.path.isdir(DIR), "the authority files are not on this checkout")
class TheFiles(unittest.TestCase):
    def setUp(self):
        self.index = json.load(open(os.path.join(ROOT, "site", "data", "regions", "index.json"), encoding="utf-8"))
        self.names = sorted(os.listdir(DIR))

    def test_one_file_an_authority_and_a_region(self):
        bas = {b["code"].lower() + ".json" for b in self.index["bas"] if b.get("us") and b.get("files_eia930")}
        regions = {f"region-{r['code'].lower()}.json" for r in self.index["regions"]}
        self.assertEqual(set(self.names) - bas - regions, set())
        self.assertEqual(bas - set(self.names), set())

    def test_every_part_names_its_table_and_a_null_says_why(self):
        for n in self.names:
            d = load(n)
            for part in PARTS:
                self.assertIn(part, d, n)
                self.assertIn("table", d[part], (n, part))
            o = d["owns"]
            if o["total_mw"] is None:
                self.assertTrue(o.get("why"), n)
            if d["burns"]["co2"]["intensity_kg_per_mwh"] is None:
                self.assertTrue(d["burns"]["co2"].get("why"), n)

    def test_no_zero_stands_for_a_missing_source(self):
        for n in self.names:
            d = load(n)
            self.assertNotEqual(d["owns"]["total_mw"], 0, n)

    def test_shares_sum_to_a_hundred(self):
        for n in self.names:
            s = load(n)["burns"].get("share_pct")
            if s:
                self.assertAlmostEqual(sum(v for v in s.values() if v is not None), 100.0, delta=0.1, msg=n)

    def test_a_region_sums_its_authorities_capacity(self):
        for r in self.index["regions"]:
            p = f"region-{r['code'].lower()}.json"
            if p not in self.names:
                continue
            d = load(p)
            parts = [load(b.lower() + ".json")["owns"]["total_mw"] for b in d["bas"]]
            if d["owns"]["total_mw"] is not None:
                self.assertAlmostEqual(d["owns"]["total_mw"], sum(x for x in parts if x), delta=1.0, msg=p)

    def test_the_largest_plants_are_ten_or_fewer_largest_first(self):
        for n in self.names:
            pl = load(n)["owns"]["largest_plants"] or []
            self.assertLessEqual(len(pl), 10)
            self.assertEqual([p["mw"] for p in pl], sorted([p["mw"] for p in pl], reverse=True), n)

    def test_carbon_only_where_eia_estimates(self):
        for n in self.names:
            co2 = load(n)["burns"]["co2"]
            if co2["intensity_kg_per_mwh"] is not None:
                self.assertIn(n, {"ciso.json", "erco.json", "isne.json", "miso.json", "nyis.json", "pjm.json", "swpp.json"})

    def test_a_regions_flows_are_positive_with_a_direction(self):
        for n in self.names:
            if n.startswith("region-"):
                for p in load(n)["trades"]["partners"] or []:
                    self.assertGreaterEqual(p["flow_mwh"], 0, n)
                    self.assertIn(p["direction"], ("into", "out of"))

    def test_no_em_dash(self):
        for n in self.names:
            with open(os.path.join(DIR, n), encoding="utf-8") as f:
                self.assertNotIn(chr(0x2014), f.read())


class TheContract(unittest.TestCase):
    def test_section_ten_names_every_part(self):
        c = open(os.path.join(ROOT, "docs", "state", "page_files_regions.md"), encoding="utf-8").read()
        sec = c.split("## 10.")[1].split("## Changes")[0]
        for part in PARTS:
            self.assertIn(f"`{part}.", sec)
        self.assertTrue(re.search(r"never a zero", sec))


if __name__ == "__main__":
    unittest.main()

"""Session 8014, chain 581 (part D): the project map's line layers (site/data/map_layers/, warehouse/connectors/hifld_lines.py)."""
import json
import os
import unittest

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
LAYERS = os.path.join(ROOT, "site", "data", "map_layers")


def src(*p):
    with open(os.path.join(ROOT, *p), encoding="utf-8") as f:
        return f.read()


class TheWebFiles(unittest.TestCase):
    def test_each_under_two_mb_and_in_columns(self):
        for name in ("transmission_230kv.json", "hgl_pipelines.json"):
            p = os.path.join(LAYERS, name)
            self.assertLess(os.path.getsize(p), 2 * 1024 ** 2, name)
            f = json.load(open(p, encoding="utf-8"))
            self.assertEqual(f["license"], "public")
            self.assertEqual(len(f["rows"]), len(f["paths"]))
            self.assertEqual(len(f["rows"]), f["lines"])
            for row in f["rows"][:50]:
                self.assertEqual(len(row), len(f["fields"]))
            for part in f["paths"][0]:
                self.assertEqual(len(part) % 2, 0)

    def test_every_line_is_230_kv_or_above(self):
        f = json.load(open(os.path.join(LAYERS, "transmission_230kv.json"), encoding="utf-8"))
        k = f["fields"].index("kv")
        kvs = [r[k] for r in f["rows"] if r[k] is not None]
        self.assertTrue(kvs)
        self.assertGreaterEqual(min(kvs), 230)

    def test_text_is_read_through_names(self):
        f = json.load(open(os.path.join(LAYERS, "hgl_pipelines.json"), encoding="utf-8"))
        j = f["fields"].index("name")
        self.assertIn("name", f["text_fields"])
        self.assertTrue(any(isinstance(r[j], int) and 0 <= r[j] < len(f["names"]) for r in f["rows"]))


class TheMap(unittest.TestCase):
    def test_each_layer_is_a_switch_off_as_the_page_opens(self):
        m = src("site", "app", "map", "ProjectMap.tsx")
        self.assertIn("useState<string[]>([])", m)
        self.assertIn("data-map-line=", m)
        self.assertIn("fetch(`/map/lines/${key}`)", m)

    def test_the_route_serves_the_two_fixed_files(self):
        r = src("site", "app", "map", "lines", "[name]", "route.ts")
        self.assertIn('import transmission from "@/data/map_layers/transmission_230kv.json";', r)
        self.assertIn("dynamicParams = false", r)

    def test_the_refused_host_is_named_and_not_read(self):
        c = src("warehouse", "connectors", "hifld_lines.py")
        self.assertNotIn("services7.arcgis.com/FGr1D95XCGALKXqM", c.split('"""', 2)[2])
        self.assertIn("services7.arcgis.com", src("docs", "methods", "map_layers.md"))

    def test_no_em_dash(self):
        for p in (("site", "lib", "maplayers.ts"), ("site", "app", "map", "lines", "[name]", "route.ts"), ("warehouse", "connectors", "hifld_lines.py"),
                  ("docs", "methods", "map_layers.md")):
            self.assertNotIn(chr(0x2014), src(*p))


if __name__ == "__main__":
    unittest.main()

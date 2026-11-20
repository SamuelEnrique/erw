"""Session 8613 (chain 504, 19 November 2026): the resource map's browser check reads both lists of layers.

Energy Research Warehouse (ERW). The data machine's coal layer reached main on 19 November in a list of its own
(site/data/resources/manifest_added.json, data request 542). The page has read both lists as one since session 8607;
the browser check (site/scripts/check-resources.mjs) still read the first alone, so the added layer was never switched
on by it. What is held here: the check joins the lists by the page's rule, written out on its own, and the merge of
main kept both rules of test 8603's guard. Nothing here sets the environment or makes a request.
"""

import json
import os
import unittest

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
SITE = os.path.join(ROOT, "site")
EM = chr(0x2014)


def src(*p):
    with open(os.path.join(ROOT, *p), encoding="utf-8") as f:
        return f.read()


class TheCheckReadsBothLists(unittest.TestCase):
    def test_the_second_list_is_read_when_it_is_there(self):
        s = src("site", "scripts", "check-resources.mjs")
        self.assertIn('const addedPath = path.join(here, "..", "data", "resources", "manifest_added.json");', s)
        self.assertIn("const ADDED = fs.existsSync(addedPath) ? JSON.parse(fs.readFileSync(addedPath, \"utf-8\")) : null;", s)
        self.assertIn("if (!ADDED) return FIRST;", s)

    def test_the_first_list_wins_a_name(self):
        s = src("site", "scripts", "check-resources.mjs")
        self.assertIn("!layers.some((x) => x.id === l.id)", s)
        self.assertIn("missing.some((y) => y.id === x.id) || layers.some((l) => l.id === x.id)", s)

    def test_the_layers_checked_come_from_the_joined_list(self):
        s = src("site", "scripts", "check-resources.mjs")
        at = s.index("const MANIFEST = (() => {")
        self.assertLess(at, s.index("const LAYERS = (MANIFEST.layers ?? [])"))
        self.assertEqual(s.count("JSON.parse(fs.readFileSync(manifestPath"), 1)

    def test_an_added_layer_on_this_machine_names_its_source(self):
        p = os.path.join(SITE, "data", "resources", "manifest_added.json")
        if not os.path.exists(p):
            self.skipTest("no manifest_added.json on this machine")
        with open(p, encoding="utf-8") as f:
            added = json.load(f)
        self.assertTrue(added["layers"])
        for l in added["layers"]:
            self.assertTrue(l.get("source_url") and l.get("source_sha256") and l.get("retrieved_at_utc"), l.get("id"))
            self.assertTrue(os.path.exists(os.path.join(SITE, "data", "resources", "layers", l["file"])), l.get("file"))


class TheMergedGuard(unittest.TestCase):
    def test_test_8603_keeps_both_rules(self):
        s = src("tests", "test_session8603.py")
        self.assertNotIn("<<<<<<<", s)
        self.assertNotIn(">>>>>>>", s)
        self.assertIn("not any(n.startswith(i) for i in ids) and n not in sourced", s)

    def test_no_em_dash(self):
        for p in (("site", "scripts", "check-resources.mjs"), ("tests", "test_session8613_resources.py")):
            self.assertNotIn(EM, src(*p), p)


if __name__ == "__main__":
    unittest.main()

"""Session 8618 (chain 504, 19 November 2026): the resource map reads the data machine's added hover fields.

Energy Research Warehouse (ERW). Row 10 of docs/reviews/resources-read-2026-11-19.md: two point layers named no hover
fields, so a hover showed their files' column names raw ("resource: 8.35; capacity ac mw: 282"). The data machine
answered data request 553 with a new file, site/data/resources/hover_fields_added.json, in the publishers' own words
(the list of layers itself is not changed). The page reads it where a layer's own entry names no fields. The names and
words below are made up for the tests and are in no page. Nothing here sets the environment or makes a request.
"""

import json
import os
import shutil
import subprocess
import unittest

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
SITE = os.path.join(ROOT, "site")
NODE = shutil.which("node")
EM = chr(0x2014)


def src(*p):
    with open(os.path.join(ROOT, *p), encoding="utf-8") as f:
        return f.read()


@unittest.skipUnless(NODE, "node is not installed")
class TheAddedHoverFields(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        code = (
            "import { withHoverFields as w } from './lib/resources.ts';"
            "const m = { built_at_utc: 'A', added_built_at_utc: 'B', missing: [{ id: 'gone' }], layers: ["
            " { id: 'own', kind: 'points', title: 'Own', hover_fields: [['a', 'Its own words']] },"
            " { id: 'bare', kind: 'points', title: 'Bare', file: 'bare.json' },"
            " { id: 'empty', kind: 'points', title: 'Empty', hover_fields: [] },"
            " { id: 'other', kind: 'shapes', title: 'Other' } ] };"
            "const added = { built_at_utc: 'C', layers: { own: { hover_fields: [['a', 'The added words']] }, bare: { hover_fields: [['x', 'Speed, m/s'], ['y', 'Size, km2']], name_column: { column: 'name' } },"
            " empty: { hover_fields: [['z', 'Depth, m'], 7, ['only one']] }, other: { hover_fields: 'not a list' }, stranger: { hover_fields: [['q', 'Q']] } } };"
            "const out = w(m, added);"
            "console.log(JSON.stringify({ out, same: [w(m, null) === m, w(m, undefined) === m, w(m, {}) === m, w(m, { layers: 'x' }) === m, w(m, { layers: null }) === m], untouched: JSON.stringify(m.layers[1]) }));"
        )
        r = subprocess.run([NODE, "--input-type=module", "-e", code], cwd=SITE, capture_output=True, text=True, encoding="utf-8", timeout=120)
        assert r.returncode == 0, r.stderr
        cls.d = json.loads(r.stdout.strip().splitlines()[-1])
        cls.by = {l["id"]: l for l in cls.d["out"]["layers"]}

    def test_a_layer_that_names_its_own_keeps_them(self):
        self.assertEqual(self.by["own"]["hover_fields"], [["a", "Its own words"]])

    def test_a_layer_that_names_none_takes_the_added_ones(self):
        self.assertEqual(self.by["bare"]["hover_fields"], [["x", "Speed, m/s"], ["y", "Size, km2"]])
        self.assertEqual(self.by["bare"]["file"], "bare.json")              # nothing else of the layer is touched
        self.assertNotIn("name_column", self.by["bare"])                    # the name's own words are not the page's to use yet

    def test_an_empty_list_counts_as_none_and_only_pairs_are_taken(self):
        self.assertEqual(self.by["empty"]["hover_fields"], [["z", "Depth, m"]])

    def test_what_cannot_be_read_as_fields_changes_nothing(self):
        self.assertNotIn("hover_fields", self.by["other"])
        self.assertEqual([l["id"] for l in self.d["out"]["layers"]], ["own", "bare", "empty", "other"])   # a layer the list does not hold is not added

    def test_the_rest_of_the_list_is_as_it_was(self):
        self.assertEqual(self.d["out"]["built_at_utc"], "A")
        self.assertEqual(self.d["out"]["added_built_at_utc"], "B")
        self.assertEqual(self.d["out"]["missing"], [{"id": "gone"}])

    def test_no_file_or_a_file_of_another_shape_gives_the_list_back(self):
        self.assertEqual(self.d["same"], [True, True, True, True, True])

    def test_the_list_handed_in_is_not_changed(self):
        self.assertEqual(json.loads(self.d["untouched"]), {"id": "bare", "kind": "points", "title": "Bare", "file": "bare.json"})


class ThePageReadsTheFile(unittest.TestCase):
    def setUp(self):
        self.s = src("site", "lib", "resourcesdata.ts")

    def test_the_file_is_read_after_the_added_list_and_before_the_layers_are_kept(self):
        a = self.s.index('"manifest_added.json")')
        b = self.s.index('const hoverPath = path.join(process.cwd(), "data", "resources", "hover_fields_added.json");')
        c = self.s.index("const layers: Layer[] = [], missing = [...(raw.missing ?? [])];")
        self.assertLess(a, b)
        self.assertLess(b, c)
        self.assertIn("raw = withHoverFields(raw, JSON.parse(fs.readFileSync(hoverPath, \"utf8\")) as HoverFieldsAdded);", self.s)

    def test_a_file_that_is_not_there_is_no_fault_and_one_that_cannot_be_read_is_said(self):
        self.assertIn("if (fs.existsSync(hoverPath)) {", self.s)
        self.assertIn("reason = reason ?? `The added hover fields (hover_fields_added.json) could not be read on the server", self.s)

    def test_the_hover_shows_a_pair_as_written(self):
        m = src("site", "app", "resources", "ResourceMap.tsx")
        self.assertIn("return (l.hover_fields ?? []).flatMap(([field, words]) => { const v = get(field); return v === null || v === undefined || v === \"\" ? [] : [`${words}: ${fieldText(v)}`]; });", m)
        self.assertIn("hover_fields: hoverPairs(l.hover_fields),", src("site", "app", "resources", "view.tsx"))


class TheRealFile(unittest.TestCase):
    """Where the data machine's file is on the machine, its layers are layers of the lists and its columns are in their files."""

    def test_every_layer_and_column_it_names_is_there(self):
        p = os.path.join(SITE, "data", "resources", "hover_fields_added.json")
        if not os.path.exists(p):
            self.skipTest("no hover_fields_added.json on this machine yet (it lands with the data machine's stack)")
        with open(p, encoding="utf-8") as f:
            added = json.load(f)
        layers = []
        for name in ("manifest.json", "manifest_added.json"):
            q = os.path.join(SITE, "data", "resources", name)
            if os.path.exists(q):
                with open(q, encoding="utf-8") as f:
                    layers += json.load(f).get("layers", [])
        by = {l["id"]: l for l in layers}
        for lid, entry in added["layers"].items():
            self.assertIn(lid, by, lid)
            self.assertFalse(by[lid].get("hover_fields"), lid)        # only layers whose own entry names none
            with open(os.path.join(SITE, "data", "resources", "layers", by[lid]["file"]), encoding="utf-8") as f:
                columns = json.load(f)["columns"]
            for field, words in entry["hover_fields"]:
                self.assertIn(field, columns, (lid, field))
                self.assertTrue(words.strip(), (lid, field))


class TheRest(unittest.TestCase):
    def test_the_row_says_what_was_done(self):
        r = src("docs", "reviews", "resources-read-2026-11-19.md")
        self.assertRegex(r, r"(?m)^\| 10 \|.*session 8618")

    def test_no_em_dash(self):
        for p in (("site", "lib", "resources.ts"), ("site", "lib", "resourcesdata.ts"), ("tests", "test_session8618_resources.py"), ("docs", "methods", "resources.md")):
            self.assertNotIn(EM, src(*p), p)


if __name__ == "__main__":
    unittest.main()

"""Session 146, the page half: "Where the resources are" (/resources, in review).

Energy Research Warehouse (ERW). No request is made, no model is called and nothing is written anywhere.

    PureFunctions  site/scripts/test-resources.mjs: the grid decoding, the cell a place falls in, the level drawn at a
                   zoom, the plane and its inverse, the address, shapes, the toggles made from a manifest (Node runs
                   site/lib/resources.ts as it is). Where the data side's files are on the machine it also decodes
                   every grid file of the manifest; on a machine without them it says so and passes.
    ThePage        the page's rules, read from its source: in review, under Projects, no menu over eight, in the route
                   check and the tools inventory; its layer files and overlays are read through addresses the release
                   gate covers, and from nowhere else; the face holds no method words, no hub and no zone, no em dash;
                   the Method note is closed; nothing a live page reads is imported by a live page from here.
    TheManifest    where site/data/resources/manifest.json is on the machine: every layer of it becomes a toggle and
                   names a kind the page draws.
On the built site: node site/scripts/check-resources.mjs <base> (run here when ERW_SITE_URL names a served site).

    python -m unittest tests.test_session146_page
"""

import json
import os
import re
import shutil
import subprocess
import unittest

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
SITE = os.path.join(ROOT, "site")
NODE = shutil.which("node")
MANIFEST = os.path.join(SITE, "data", "resources", "manifest.json")
PAGE_FILES = (
    ("site", "app", "resources", "page.tsx"), ("site", "app", "resources", "ResourceMap.tsx"), ("site", "app", "resources", "grid.worker.ts"),
    ("site", "app", "resources", "layer", "[name]", "route.ts"), ("site", "app", "resources", "overlay", "plants", "route.ts"),
    ("site", "app", "resources", "overlay", "queue", "route.ts"), ("site", "app", "resources", "overlay", "datacenters", "route.ts"),
    ("site", "lib", "resources.ts"), ("site", "lib", "resourcesdata.ts"),
    ("site", "scripts", "check-resources.mjs"), ("site", "scripts", "test-resources.mjs"), ("site", "scripts", "frametime-resources.mjs"),
    ("tests", "test_session146_page.py"),
)
# words of method or limitation: none belongs on the page's face (they are in the Method note)
METHOD_WORDS = re.compile(r"siting study|before losses|limitation|caveat|assum|interpolat|simplified|smooth|squeezed|cosine|methodology|not a plant|census of", re.I)


def src(*parts):
    with open(os.path.join(ROOT, *parts), encoding="utf-8") as f:
        return f.read()


def node(code):
    r = subprocess.run([NODE, "--input-type=module", "-e", code], cwd=SITE, capture_output=True, text=True, timeout=120)
    assert r.returncode == 0, r.stderr
    return json.loads(r.stdout.strip().splitlines()[-1])


@unittest.skipUnless(NODE, "node is not installed")
class PureFunctions(unittest.TestCase):
    def test_the_node_tests_pass(self):
        r = subprocess.run([NODE, "scripts/test-resources.mjs"], cwd=SITE, capture_output=True, text=True, timeout=300)
        self.assertEqual(r.returncode, 0, r.stdout[-3000:] + r.stderr[-1000:])
        self.assertRegex(r.stdout, r"all \d+ passed")
        self.assertNotIn("FAIL", r.stdout)


class ThePage(unittest.TestCase):
    def test_in_review_and_under_projects(self):
        self.assertRegex(src("site", "lib", "release.ts"), r'"/resources": "review",\s*// session 146')
        self.assertIn('"/resources"', src("site", "scripts", "check-routes.mjs"))
        self.assertIn("`/resources`", src("docs", "tools.md"))

    @unittest.skipUnless(NODE, "node is not installed")
    def test_its_files_are_behind_the_gate(self):
        got = node("import { statusOf, exempt } from './lib/release.ts'; import { layerHref } from './lib/resources.ts';"
                   "const h = layerHref('wind_speed_100m_0p05.json');"
                   "console.log(JSON.stringify({ h, status: [statusOf('/resources'), statusOf(h), statusOf('/resources/overlay/queue')], exempt: [exempt(h), exempt('/resources/overlay/plants'), exempt('/resources-data/x.json')] }));")
        self.assertEqual(got["h"], "/resources/layer/wind_speed_100m_0p05")
        self.assertEqual(got["status"], ["review", "review", "review"])
        self.assertEqual(got["exempt"], [False, False, True])     # a file under public/ passes the gate: the page never asks for one
        comp = src("site", "app", "resources", "ResourceMap.tsx")
        asked = re.findall(r'getJson<.*?>\(("/resources/overlay/[a-z]+"|R\.layerHref\()', comp)
        self.assertEqual(len(asked), 6, asked)                    # a grid's level (twice: with no reader thread), a shape or point file, and the three overlays
        self.assertEqual(comp.count("getJson<"), len(asked) + 1)  # and no other call than these (the one more is its definition)
        self.assertEqual(comp.count("fetch("), 1)                 # the one reader, same origin
        worker = src("site", "app", "resources", "grid.worker.ts")
        self.assertEqual(worker.count("fetch("), 1)               # and the one of the grid reader, of the address it is handed
        self.assertIn('fetch(url, { credentials: "same-origin" })', worker)
        self.assertIn("url: new URL(R.layerHref(file), window.location.origin).href", comp)
        for rel in (("site", "app", "resources", "ResourceMap.tsx"), ("site", "app", "resources", "page.tsx")):
            self.assertNotRegex(src(*rel), r"https?://(?!www\.w3\.org)", "/".join(rel))    # no address of another site in the page
            self.assertNotIn("resources-data", src(*rel), "/".join(rel))
        for name in ("plants", "queue", "datacenters"):
            self.assertIn('export const dynamic = "force-static"', src("site", "app", "resources", "overlay", name, "route.ts"))
        self.assertIn("generateStaticParams", src("site", "app", "resources", "layer", "[name]", "route.ts"))

    def test_the_face_holds_no_method_and_the_note_is_closed(self):
        page = src("site", "app", "resources", "page.tsx")
        at = page.index("<details")
        note, face = page[at:page.index("</details>")], page[page.index("export default function"):at]
        self.assertRegex(note, r'<details className="[^"]*" data-method-note="1">')
        self.assertNotRegex(note[:200], r"<details[^>]*\sopen")
        self.assertIn("Method note", note)
        for words in ("not a siting study", "A request is not a plant", "It is not a census of every facility", "none is invented"):
            self.assertIn(words, note)                             # the limits are said, in the note
        text = lambda s: " ".join(re.findall(r">([^<>{}]+)<", s))  # the words between tags
        comp = src("site", "app", "resources", "ResourceMap.tsx")
        shown = text(face) + " " + text(comp[comp.index("  return (\n    <div"):]) + " " + " ".join(re.findall(r'title="([^"]*)"', comp))
        self.assertIn("The project map shows what is built; this shows the natural resource itself", shown)
        self.assertIsNone(METHOD_WORDS.search(shown), METHOD_WORDS.search(shown))
        self.assertNotRegex(shown, r"\bhubs?\b|\bzones?\b")        # no hub or zone on this map
        self.assertNotRegex(comp + page, r"MISO|PJM")              # neither is a source here
        for words in ("no value in the source here", "A county, not a site", "not held", "not drawn"):
            self.assertIn(words, comp + src("site", "lib", "resources.ts"))

    def test_real_data_only(self):
        # the page makes no number: its code holds no value of a layer, and reads every one from a file or a table
        comp = src("site", "app", "resources", "ResourceMap.tsx")
        self.assertIn("R.valueAt(img.grid, lon, lat)", comp)
        self.assertNotRegex(comp, r"Math\.random|placeholder=")
        data = src("site", "lib", "resourcesdata.ts")
        self.assertIn('"extra->>kind": "eq.queue"', data)
        self.assertIn("@/data/map_v2.json", data)                  # the project map's own copy of EIA-860M, not a new one
        self.assertIn("eq.datacenter_facilities", data)

    def test_no_em_dash(self):
        for rel in PAGE_FILES:
            self.assertNotIn(chr(0x2014), src(*rel), "/".join(rel))

    def test_the_live_pages_do_not_read_it(self):
        for rel in (("site", "app", "network"), ("site", "app", "storage"), ("site", "app", "cost-of-power", "battery")):
            for base, _dirs, files in os.walk(os.path.join(ROOT, *rel)):
                for f in files:
                    if f.endswith((".ts", ".tsx")):
                        with open(os.path.join(base, f), encoding="utf-8") as fh:
                            self.assertNotRegex(fh.read(), r"lib/resources|app/resources", os.path.join(base, f))


@unittest.skipUnless(NODE and os.path.exists(MANIFEST), "node or the manifest of resource layers is not on this machine")
class TheManifest(unittest.TestCase):
    def test_every_layer_is_a_toggle(self):
        with open(MANIFEST, encoding="utf-8") as f:
            m = json.load(f)
        got = node("import fs from 'node:fs'; import { toggleGroups, filesOf } from './lib/resources.ts';"
                   "const m = JSON.parse(fs.readFileSync('./data/resources/manifest.json', 'utf-8'));"
                   "console.log(JSON.stringify({ groups: toggleGroups(m).map((g) => ({ id: g.id, held: g.items.filter((i) => i.held).map((i) => i.layer.id), missing: g.items.filter((i) => !i.held).map((i) => [i.label, i.reason]) })), files: m.layers.map((l) => filesOf(l).length) }));")
        held = [i for g in got["groups"] for i in g["held"]]
        self.assertEqual(sorted(held), sorted(layer["id"] for layer in m["layers"]))
        self.assertEqual([g["id"] for g in got["groups"]][:7], ["wind", "solar", "geothermal", "oil_gas", "hydropower", "biomass", "offshore_wind"])
        for layer in m["layers"]:
            self.assertIn(layer["kind"], ("grid", "shapes", "points"), layer["id"])
        self.assertTrue(all(n >= 1 for n in got["files"]))
        for g in got["groups"]:
            for label, reason in g["missing"]:
                self.assertGreater(len(reason), 5, label)          # a placeholder always says why


@unittest.skipUnless(NODE and os.environ.get("ERW_SITE_URL"), "ERW_SITE_URL names no served site")
class OnTheBuiltSite(unittest.TestCase):
    def test_the_browser_check(self):
        r = subprocess.run([NODE, "scripts/check-resources.mjs", os.environ["ERW_SITE_URL"]], cwd=SITE, capture_output=True, text=True, timeout=1500)
        self.assertEqual(r.returncode, 0, r.stdout[-4000:])


if __name__ == "__main__":
    unittest.main()

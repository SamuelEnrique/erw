"""Session 8603 (chain 504, 19 November 2026): the natural resource map (the Resources tab of /map) set beside the
owner's list, and taken to the done line.

Energy Research Warehouse (ERW). The map has drawn the resource layers since sessions 146 and 159; it was not built
again. What is held here:
- a line under each switch that says what the layer measures: every layer of the list of layers has one, each one
  short sentence; a layer the page does not know says its own line, or the source's label;
- coal, uranium and critical minerals are named: with no layer among the files each is a greyed switch that says why,
  and the day a layer of the kind is in the list its switch is the layer's (never a made-up layer);
- the decisions fold of the tab, and the method note's list, one list;
- the replication of one layer from its publisher's file (its recorded result, 556 of 556, and its arithmetic on a
  shape whose area is known), and the two cross-checks, figure for figure against the layer's file;
- no em dash.
Nothing here sets the environment, reads a table or makes a request.
"""

import csv
import importlib.util
import json
import os
import re
import shutil
import subprocess
import unittest

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
SITE = os.path.join(ROOT, "site")
REP = os.path.join(ROOT, "replication", "resources")
NODE = shutil.which("node")
EM = chr(0x2014)


def src(*p):
    with open(os.path.join(ROOT, *p), encoding="utf-8") as f:
        return f.read()


def node(code):
    r = subprocess.run([NODE, "--input-type=module", "-e", code], cwd=SITE, capture_output=True, text=True, encoding="utf-8", timeout=120)
    assert r.returncode == 0, r.stderr
    return json.loads(r.stdout.strip().splitlines()[-1])


def rows(name):
    with open(os.path.join(REP, name), encoding="utf-8", newline="") as f:
        return list(csv.DictReader(line for line in f if not line.startswith("#")))


MANIFEST = json.loads(src("site", "data", "resources", "manifest.json"))


@unittest.skipUnless(NODE, "node is not installed")
class TheLineUnderEachSwitch(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.d = node("import fs from 'node:fs'; import * as R from './lib/resources.ts';"
                     "const m = JSON.parse(fs.readFileSync('./data/resources/manifest.json', 'utf-8'));"
                     "console.log(JSON.stringify({ lines: Object.fromEntries(m.layers.map((l) => [l.id, R.measureLine(l)])), known: Object.keys(R.MEASURE),"
                     " other: [R.measureLine({ id: 'x', measure: 'What a new layer measures' }), R.measureLine({ id: 'x', value_label: 'Thickness of the seam, feet' }), R.measureLine({ id: 'x', measure: 'Already a sentence.' }), R.measureLine({ id: 'x' })],"
                     " groups: R.toggleGroups(m).map((g) => ({ id: g.id, label: g.label, items: g.items.map((i) => (i.held ? { held: true, id: i.layer.id } : { held: false, label: i.label, reason: i.reason })) })) }));")

    def test_every_layer_of_the_list_has_a_line(self):
        self.assertEqual(len(MANIFEST["layers"]), 14)
        for l in MANIFEST["layers"]:
            line = self.d["lines"][l["id"]]
            self.assertIn(l["id"], self.d["known"], l["id"])
            self.assertTrue(20 <= len(line) <= 120 and line.endswith("."), (l["id"], line))
            self.assertEqual(line.count(". "), 0, line)                 # one sentence
            self.assertNotIn(EM, line)

    def test_the_lines_are_plain_words_not_field_names(self):
        for line in self.d["lines"].values():
            self.assertIsNone(re.search(r"[A-Za-z]+_[A-Za-z]+|MWe|kWh|GHI|DNI|EGS|NPD|NSD", line), line)

    def test_a_layer_the_page_does_not_know(self):
        self.assertEqual(self.d["other"], ["What a new layer measures.", "Thickness of the seam, feet.", "Already a sentence.", ""])

    def test_the_line_is_drawn_under_the_switch(self):
        m = src("site", "app", "resources", "ResourceMap.tsx")
        self.assertIn('{R.measureLine(it.layer) ? <span className="block pb-1 pl-6 text-xs leading-snug text-ink" data-measure={it.layer.id}>{R.measureLine(it.layer)}</span> : null}', m)
        # the switch itself is as it was
        self.assertIn('<input type="checkbox" className={check} checked={on.includes(it.layer.id)} onChange={() => toggle(it.layer.id)} data-toggle={it.layer.id} />', m)

    def test_the_kinds_of_the_owners_list_are_all_named(self):
        ids = [g["id"] for g in self.d["groups"]]
        self.assertEqual(ids, ["wind", "solar", "geothermal", "oil_gas", "hydropower", "biomass", "offshore_wind", "coal", "uranium", "critical_minerals"])
        by = {g["id"]: g for g in self.d["groups"]}
        self.assertEqual([g["label"] for g in self.d["groups"]][7:], ["Coal", "Uranium", "Critical minerals"])
        for kind in ("coal", "uranium", "critical_minerals"):
            items = by[kind]["items"]
            self.assertEqual(len(items), 1)
            self.assertFalse(items[0]["held"])                          # no layer of the kind is among the files: greyed, never made up
            self.assertIn("is among the resource files of the site yet", items[0]["reason"])
            self.assertIn("nothing is drawn in its place", items[0]["reason"])
        # the fourteen layers held are where they were
        self.assertEqual(sum(1 for g in self.d["groups"] for i in g["items"] if i["held"]), 14)
        self.assertEqual([i.get("id") for i in by["wind"]["items"] if i["held"]], ["wind_speed_100m", "wind_capacity_factor"])

    def test_no_layer_file_of_the_three_kinds_was_written_by_this_session(self):
        names = os.listdir(os.path.join(SITE, "data", "resources", "layers"))
        ids = [l["id"] for l in MANIFEST["layers"]]
        # session 8009 (chain 501's desk): the data machine adds a layer in manifest_added.json, a new file in the
        # manifest's form (manifest.json itself is not changed under chain 501's rule); its layers count as listed
        added = os.path.join(SITE, "data", "resources", "manifest_added.json")
        if os.path.exists(added):
            ids += [l["id"] for l in json.load(open(added, encoding="utf-8"))["layers"]]
        made_up = [n for n in names if re.search(r"coal|uranium|mineral", n) and not any(n.startswith(i) for i in ids)]
        self.assertEqual(made_up, [])


class TheDecisions(unittest.TestCase):
    def test_the_fold_and_the_note_are_one_list(self):
        page = src("site", "app", "resources", "Decisions.tsx")
        keys = re.findall(r'\{ key: "([a-z-]+)", session: "', page)
        self.assertEqual(keys, ["one-file", "the-resource", "kinds-named", "plain-line", "opens-on-wind", "grid-level", "outline-area", "simplified", "one-tab"])
        note = src("docs", "methods", "resources.md").split("### Decisions (session 8603)")[1].split("<!-- The sections below")[0]
        self.assertEqual(re.findall(r"^\| `([a-z-]+)` \|", note, re.M), keys)
        for field in ("text:", "def:", "source:"):
            self.assertEqual(page.count("    " + field), len(keys))
        self.assertIn('data-decisions="resources"', page)
        self.assertIn("<strong>Default:</strong>", page)
        self.assertIn("<strong>Source:</strong>", page)

    def test_it_is_mounted_under_the_map_and_above_the_method_note(self):
        v = src("site", "app", "resources", "view.tsx")
        self.assertLess(v.index("<ResourceMap layers={layers} groups={groups} manifestReason={reason} />"), v.index("<ResourceDecisions />"))
        self.assertLess(v.index("<ResourceDecisions />"), v.index('data-method-note="1"'))

    def test_the_sections_are_above_the_mark_the_connector_rewrites_under(self):
        note = src("docs", "methods", "resources.md")
        mark = "<!-- The sections below are written from the manifest by resource_layers.py --method-doc -->"
        self.assertEqual(note.count(mark), 1)
        self.assertLess(note.index("## Session 8603 (19 November 2026)"), note.index(mark))
        self.assertLess(note.index("### Decisions (session 8603)"), note.index(mark))


class TheReplication(unittest.TestCase):
    def test_every_figure_of_the_layer_is_the_publishers(self):
        figures = rows("oil_gas_plays_figures.csv")
        self.assertEqual(len(figures), 556)
        self.assertTrue(all(r["same"] == "yes" for r in figures))
        layer = json.loads(src("site", "data", "resources", "layers", "oil_gas_plays.json"))
        self.assertEqual(len(layer["features"]), 50)
        by = {r["figure"]: r for r in figures}
        for ft in layer["features"]:
            p = ft["properties"]
            r = by["%s: area, square miles (the hover's figure; the source's Area_sq_mi)" % p["ID"]]
            self.assertAlmostEqual(float(r["the_map"]), p["value"], places=6)          # the csv's figure is the layer file's today
            self.assertAlmostEqual(float(r["the_publisher"]), p["value"], places=6)
        self.assertIn("**Result: 556 of 556 figures are the publisher's.**", src("docs", "methods", "resources.md"))

    def test_the_file_named_is_the_one_the_layer_was_built_from(self):
        entry = [l for l in MANIFEST["layers"] if l["id"] == "oil_gas_plays"][0]
        script = src("replication", "resources", "replicate.py")
        self.assertIn('SHA256 = "%s"' % entry["source_sha256"], script)
        self.assertIn(entry["source_url"], script)
        self.assertIn(entry["source_sha256"], src("replication", "resources", "replicate.do"))

    def test_the_scripts_area_on_shapes_whose_area_is_known(self):
        spec = importlib.util.spec_from_file_location("replicate_resources", os.path.join(REP, "replicate.py"))
        mod = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(mod)
        # the whole WGS 84 ellipsoid: 510,065,621.724 square kilometers
        globe = [[(-180.0, -90.0), (180.0, -90.0), (180.0, 90.0), (-180.0, 90.0), (-180.0, -90.0)]]
        self.assertAlmostEqual(mod.area_sq_mi(globe) * mod.SQ_M_PER_SQ_MI / 1e6, 510065621.724, delta=1.0)
        # a hole is taken off: a ring that runs the other way round inside the first
        outer = [(0.0, 0.0), (0.0, 2.0), (2.0, 2.0), (2.0, 0.0), (0.0, 0.0)]
        hole = [(0.5, 0.5), (1.5, 0.5), (1.5, 1.5), (0.5, 1.5), (0.5, 0.5)]
        whole, holed, inner = mod.area_sq_mi([outer]), mod.area_sq_mi([outer, hole]), mod.area_sq_mi([hole])
        self.assertAlmostEqual(holed, whole - inner, places=6)
        self.assertGreater(inner, 4700)        # a square of one degree near the equator is about 4,750 square miles
        self.assertLess(inner, 4800)
        self.assertTrue(mod.same(2223.55155189, 2223.55155189) and not mod.same(2223.55, 2223.56) and mod.same("", None))

    def test_the_script_is_written_from_the_publishers_file_not_from_the_sites_code(self):
        script = src("replication", "resources", "replicate.py")
        for word in ("resource_layers", "import shapefile", "import geopandas", "import requests", "urllib"):
            self.assertNotIn(word, script)

    def test_cross_check_1_the_area_of_the_publishers_own_outline(self):
        check = rows("crosscheck.csv")
        self.assertEqual(len(check), 50)
        self.assertTrue(all(abs(float(r["difference_pct"])) <= 0.04 for r in check))
        theirs, mine = sum(float(r["area_sq_mi_publisher"]) for r in check), sum(float(r["area_sq_mi_of_its_outline"]) for r in check)
        self.assertEqual((round(theirs), round(mine)), (514017, 514014))
        note = src("docs", "methods", "resources.md")
        self.assertIn("514,017 square miles by the publisher's field and 514,014 by its outlines", note)

    def test_cross_check_2_the_areas_the_publisher_printed_in_2011(self):
        pub = rows("crosscheck_published.csv")
        self.assertEqual(len(pub), 9)
        layer = {f["properties"]["ID"]: f["properties"] for f in json.loads(src("site", "data", "resources", "layers", "oil_gas_plays.json"))["features"]}
        note = src("docs", "methods", "resources.md")
        for r in pub:
            ours, theirs = float(r["ours_sq_mi"]), float(r["published_sq_mi"])
            self.assertEqual(ours, round(layer[r["play_id"]]["value"], 1), r["play_id"])        # ours is the layer's own figure
            self.assertAlmostEqual(float(r["difference_sq_mi"]), ours - theirs, places=1)      # nothing adjusted: the difference is the difference
            self.assertIn(format(int(theirs), ","), r["published_words"])                       # the review's own words carry its figure
            self.assertTrue(r["pdf_page"].isdigit() and r["why_they_differ"].endswith("."))
            self.assertIn("| %s | %s |" % (format(ours, ",.1f"), format(int(theirs), ",")), note)
        self.assertIn("No figure is adjusted to match.", note)

    def test_the_decision_on_the_page_carries_the_cross_checks_figure(self):
        page = src("site", "app", "resources", "Decisions.tsx")
        layer = {f["properties"]["ID"]: f["properties"] for f in json.loads(src("site", "data", "resources", "layers", "oil_gas_plays.json"))["features"]}
        self.assertEqual(round(layer["MARP01"]["value"]), 58326)
        self.assertIn("the Marcellus is 95,000 square miles there and 58,326 here", page)

    def test_the_host_that_refuses_is_named(self):
        note = src("docs", "methods", "resources.md")
        self.assertIn("ScienceBase, whose robots file names Claude's agents and disallows every path for them", note)


class TheWords(unittest.TestCase):
    def test_no_em_dash(self):
        for parts in (("site", "lib", "resources.ts"), ("site", "app", "resources", "Decisions.tsx"), ("site", "app", "resources", "ResourceMap.tsx"), ("site", "app", "resources", "view.tsx"),
                      ("site", "scripts", "test-resources.mjs"), ("replication", "resources", "replicate.py"), ("replication", "resources", "replicate.do"),
                      ("replication", "resources", "crosscheck_published.csv"), ("replication", "resources", "crosscheck.csv"), ("docs", "methods", "resources.md"), ("tests", "test_session8603.py")):
            self.assertNotIn(EM, src(*parts), parts)

    def test_the_page_stays_in_review_and_a_tab(self):
        self.assertIn('  "/resources": "review",', src("site", "lib", "release.ts"))
        self.assertIn('{ source: "/resources", destination: "/map?tab=resources", permanent: true },', src("site", "next.config.ts"))


if __name__ == "__main__":
    unittest.main()

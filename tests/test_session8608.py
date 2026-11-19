"""Session 8608 (chain 504, 19 November 2026): the reader's read of the natural resource map, and what it found.

Energy Research Warehouse (ERW). Five cases a named reader would bring were taken in a browser on a build that holds
the data machine's coal layer (docs/reviews/resources-read-2026-11-19.md). What is held here:
- row 1 of that read: the hover gave a latitude and a longitude and no place. It now names the state under the
  pointer, from the states' outlines the map already draws; at sea, or in no state's outline, it names none.
The squares below are made up for the tests and are on no map. Nothing here sets the environment or makes a request.
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
EM = chr(0x2014)


def src(*p):
    with open(os.path.join(ROOT, *p), encoding="utf-8") as f:
        return f.read()


def node(code):
    r = subprocess.run([NODE, "--input-type=module", "-e", code], cwd=SITE, capture_output=True, text=True, encoding="utf-8", timeout=120)
    assert r.returncode == 0, r.stderr
    return json.loads(r.stdout.strip().splitlines()[-1])


@unittest.skipUnless(NODE, "node is not installed")
class TheStateUnderThePointer(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.d = node("import { stateShapes, stateAt } from './lib/resources.ts';"
                     "const sq = (w, s, e, n) => ({ type: 'Polygon', coordinates: [[[w, s], [e, s], [e, n], [w, n], [w, s]]] });"
                     # a square with a square hole in it, a square beside it, and two squares far apart that are one state
                     "const west = { type: 'Polygon', coordinates: [[[0, 0], [10, 0], [10, 10], [0, 10], [0, 0]], [[4, 4], [6, 4], [6, 6], [4, 6], [4, 4]]] };"
                     "const isles = { type: 'MultiPolygon', coordinates: [sq(30, 0, 31, 1).coordinates, sq(40, 0, 41, 1).coordinates] };"
                     "const shapes = stateShapes([{ name: 'West', geometry: west }, { name: 'East', geometry: sq(10, 0, 20, 10) }, { name: 'Isles', geometry: isles }, { name: null, geometry: sq(50, 0, 60, 10) }, { name: 'Empty', geometry: null }]);"
                     "console.log(JSON.stringify({ names: shapes.map((s) => s.name), box: shapes[0].box, at: [[2, 2], [15, 5], [5, 5], [30.5, 0.5], [40.5, 0.5], [35, 0.5], [55, 5], [-5, 5], [2, 20]].map(([x, y]) => stateAt(shapes, x, y)), none: stateAt([], 2, 2) }));")

    def test_a_shape_needs_a_name_and_an_outline(self):
        self.assertEqual(self.d["names"], ["West", "East", "Isles"])
        self.assertEqual(self.d["box"], [0, 0, 10, 10])                     # west, south, east, north

    def test_a_point_inside_a_state_names_it(self):
        self.assertEqual(self.d["at"][0], "West")
        self.assertEqual(self.d["at"][1], "East")
        self.assertEqual(self.d["at"][3:5], ["Isles", "Isles"])           # each part of a state of several parts

    def test_a_point_in_no_outline_names_none_never_the_nearest(self):
        self.assertIsNone(self.d["at"][2])                                  # in the hole of West
        self.assertIsNone(self.d["at"][5])                                  # between the two parts of Isles, inside their common box
        self.assertIsNone(self.d["at"][6])                                  # an outline with no name
        self.assertIsNone(self.d["at"][7])
        self.assertIsNone(self.d["at"][8])
        self.assertIsNone(self.d["none"])

    def test_the_real_outlines_place_five_known_points(self):
        d = node("import fs from 'node:fs'; import { feature } from 'topojson-client'; import { stateShapes, stateAt } from './lib/resources.ts';"
                 "const topo = JSON.parse(fs.readFileSync('./node_modules/us-atlas/states-10m.json', 'utf-8'));"
                 "const shapes = stateShapes(feature(topo, topo.objects.states).features.map((f) => ({ name: f.properties.name, geometry: f.geometry })));"
                 "console.log(JSON.stringify([[-112.07, 33.45], [-81.5, 38.0], [-99.5, 41.5], [-116.5, 38.5], [-70.0, 38.0]].map(([x, y]) => stateAt(shapes, x, y))));")
        self.assertEqual(d, ["Arizona", "West Virginia", "Nebraska", "Nevada", None])   # Phoenix, Charleston, the Plains, central Nevada, the Atlantic


class TheHover(unittest.TestCase):
    def setUp(self):
        self.m = src("site", "app", "resources", "ResourceMap.tsx")

    def test_the_outlines_are_the_ones_the_map_already_draws(self):
        self.assertIn('import statesTopo from "us-atlas/states-10m.json";', self.m)
        self.assertIn("stateShapes.current = R.stateShapes(feature(topo, topo.objects.states).features.map(", self.m)
        self.assertEqual(len(re.findall(r'from "us-atlas/', self.m)), 1)   # no second file is loaded for it

    def test_the_hover_says_the_state_after_the_coordinates_and_nothing_when_there_is_none(self):
        self.assertIn("const state = R.stateAt(stateShapes.current, lon, lat);", self.m)
        self.assertIn("{hover.state ? <>, in <span data-hover-state={hover.state}>{hover.state}</span></> : null}", self.m)

    def test_no_value_of_a_layer_is_touched(self):
        self.assertIn("return { x, y, w, h, lon, lat, state, rows };", self.m)


class TheRead(unittest.TestCase):
    def test_it_is_written_with_five_cases_and_every_row_has_a_state(self):
        read = src("docs", "reviews", "resources-read-2026-11-19.md")
        for case in ("transmission planner", "power trader", "student", "siting analyst", "battery developer"):
            self.assertIn(case, read)
        rows = re.findall(r"^\| (\d+) \| .* \| (fixed|data machine|ruling|not a fault|waiting)[^|]*\|$", read, re.M)
        self.assertGreaterEqual(len(rows), 6)
        self.assertEqual([int(r[0]) for r in rows], list(range(1, len(rows) + 1)))
        self.assertNotIn(EM, read)

    def test_no_em_dash(self):
        for p in (("site", "app", "resources", "ResourceMap.tsx"), ("site", "lib", "resources.ts"), ("tests", "test_session8608.py")):
            self.assertNotIn(EM, src(*p), p)


if __name__ == "__main__":
    unittest.main()

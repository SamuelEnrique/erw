"""Session 8601 (chain 504, 19 November 2026): the Grid tool's map of the balancing authorities, made whole.

Energy Research Warehouse (ERW). The map has been a shape of the network since session 180 (tests/test_session180.py,
test_session193.py). This session added to it and took nothing away. What is held here:
- the reader of the whole country's boundary file (the contract docs/state/page_files_regions.md, section 1), run in
  Node on the tests' own made-up squares: the largest first, a point inside every shape, the file's source kept, no
  derived label, and an error (never a partial drawing) for anything that is not the file whole;
- the two views show the same megawatts for the same pair and hour: one function feeds both, and the map's own sum of
  a grid's ties is the number the page prints under the network, pinned for the seven grids on the committed snapshot;
- the carbon scale is one scale: the sphere and the region are colored by one call on one range;
- the network's own markup when the map has never been opened: the map is loaded only when chosen, and what the map
  needs is not computed in the network's shape;
- the words of a tie's hover, the batteries' ring, the zoom's arithmetic, the nearest tie to the pointer;
- the address the file is read through (under /grid, so the release gate covers it), the switch whose label could not
  be read when on, and no em dash.
The browser's proof is site/scripts/check-grid-map.mjs on a built site (its run is in the session's report).
Nothing here sets the environment, reads a table or makes a request.
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
FIXTURE = os.path.join(ROOT, "tests", "fixtures", "session8601", "ba_boundaries_contract_fixture.json")


def src(*p):
    with open(os.path.join(ROOT, *p), encoding="utf-8") as f:
        return f.read()


def node(code):
    r = subprocess.run([NODE, "--input-type=module", "-e", code], cwd=SITE, capture_output=True, text=True, encoding="utf-8", timeout=120)
    assert r.returncode == 0, r.stderr
    return json.loads(r.stdout.strip().splitlines()[-1])


READ = ("import fs from 'node:fs'; import * as m from './lib/networkMap.ts';"
        "const f = JSON.parse(fs.readFileSync(" + json.dumps(FIXTURE.replace(os.sep, "/")) + ", 'utf-8'));")


@unittest.skipUnless(NODE, "node is not installed")
class TheBoundaryFileOfTheContract(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.d = node(READ + "const h = m.readGeoBoundaries(f);"
                     "console.log(JSON.stringify({ state: h.state, ids: h.file.regions.map((r) => r.id), inside: h.file.regions.map((r) => m.insideRings(r.point, r.rings)),"
                     " points: Object.fromEntries(h.file.regions.map((r) => [r.id, r.point])), rings: Object.fromEntries(h.file.regions.map((r) => [r.id, r.rings.length])),"
                     " prov: h.file.provenance, label: m.derivedLabel(h.file), without: h.file.nodes_without_shape, strays: h.file.shapes_without_node, matched: h.file.matched,"
                     " bad: [m.readGeoBoundaries({ ...f, source: '' }).state, m.readGeoBoundaries({ ...f, retrieved_at: undefined }).state, m.readGeoBoundaries({ ...f, features: [{ properties: {}, geometry: null }] }).state,"
                     "  m.readGeoBoundaries({ held: false }).state, m.readGeoBoundaries(null).state, m.readGeoBoundaries({ ...f, features: [{ properties: { code: 'X' }, geometry: { type: 'Polygon', coordinates: [[[0, 0], [1, 1]]] } }] }).state] }));")

    def test_one_region_an_authority_the_largest_first(self):
        self.assertEqual(self.d["state"], "held")
        self.assertEqual(self.d["ids"], ["MISO", "SWPP", "CISO", "PJM", "ERCO", "ZZZZ", "BANC"])
        self.assertEqual(self.d["matched"], 7)

    def test_every_shape_has_a_point_inside_it(self):
        self.assertTrue(all(self.d["inside"]))
        self.assertEqual(self.d["points"]["MISO"], [-91, 42])                 # a plain square: its middle
        x, y = self.d["points"]["SWPP"]                                       # a ring: the middle is a hole
        self.assertFalse(-100 <= x <= -97 and 35.5 <= y <= 38.5, (x, y))
        self.assertEqual(self.d["rings"]["PJM"], 2)                           # two parts: both kept
        self.assertEqual(self.d["points"]["PJM"], [-80, 39])                  # the point in the larger

    def test_the_source_is_kept_and_the_file_is_not_called_derived(self):
        p = self.d["prov"]
        self.assertEqual(p["source"], "TEST FIXTURE: made-up squares, not boundaries")
        self.assertEqual(p["retrieved_utc"], "2026-11-19T00:00:00Z")
        self.assertEqual(p["simplification"]["tolerance_degrees"], 0.01)
        self.assertIsNone(self.d["label"])
        self.assertEqual([x["id"] for x in self.d["without"]], ["NYIS", "ISNE"])
        self.assertEqual(self.d["strays"], [{"code": "fixture-stray", "name": "A square that matches no code"}])

    def test_anything_else_is_an_error_never_a_partial_drawing(self):
        self.assertEqual(self.d["bad"], ["error"] * 6)

    def test_the_fixture_is_the_contracts_form_and_says_it_is_made_up(self):
        f = json.loads(src("tests", "fixtures", "session8601", "ba_boundaries_contract_fixture.json"))
        self.assertEqual(f["type"], "FeatureCollection")
        for k in ("built", "tables", "method", "license", "source", "source_url", "retrieved_at", "simplify_tolerance_deg", "bas_without_polygon", "polygons_without_ba"):
            self.assertIn(k, f)
        for ft in f["features"]:
            self.assertEqual(sorted(ft["properties"]), ["area_km2", "code", "fixture", "name", "region", "source_id"])
            self.assertEqual(ft["properties"]["fixture"], "a made-up square, not a boundary")
        self.assertIn("TEST FIXTURE", f["source"])
        # never shipped: nothing under site/ names the fixture but the two checks
        for rel in (("site", "app", "network", "NetworkMap.tsx"), ("site", "lib", "networkMap.ts"), ("site", "lib", "regionsdata.ts"), ("site", "app", "grid", "boundaries", "route.ts")):
            self.assertNotIn("session8601", src(*rel))


@unittest.skipUnless(NODE, "node is not installed")
class TheSameMegawattsInBothViews(unittest.TestCase):
    def test_one_function_feeds_the_scene_and_the_map(self):
        n = src("site", "app", "network", "Network.tsx")
        self.assertIn("g.graphData({ nodes, links: linksAt(hour) });", n)                                                  # the 3D scene, each hour
        self.assertIn('const mapFlows = useMemo(() => (shape === "map" ? linksAt(hour) : []), [shape, linksAt, hour]);', n)  # the map, the same hour
        self.assertEqual(n.count("const linksAt = useCallback("), 1)
        m = src("site", "app", "network", "NetworkMap.tsx")
        self.assertIn("data-flow={`${f.source}>${f.target}`} data-mw={f.mw}", m)
        self.assertIn('"data-mw": String(f.mw)', m)                                                                        # the hover's megawatts are the line's

    def test_the_maps_sum_is_the_number_under_the_network_for_the_seven_grids(self):
        got = node("import fs from 'node:fs'; import { netOf } from './lib/networkMap.ts'; import { netValue } from './lib/network.ts'; import { completeHour } from './lib/networkV3.ts';"
                   "import { netImportAt } from './lib/networkGravity.ts';"
                   "const s = JSON.parse(fs.readFileSync('./data/grid_network.json', 'utf-8')); const c = completeHour(s.hours, s.links); const hour = c.hour ?? s.hours[s.hours.length - 1]; const h = s.hours.indexOf(hour);"
                   "console.log(JSON.stringify(['ERCO', 'CISO', 'PJM', 'MISO', 'NYIS', 'ISNE', 'SWPP'].map((ba) => { const m = netOf(s.links, ba, h);"
                   " return [ba, m.net, netValue(s, `net|import|${ba}|${hour}`) ?? null, m.ties, netValue(s, `net|ties|${ba}|${hour}`) ?? 0, netImportAt(s.links, ba, h)]; })));")
        self.assertEqual(len(got), 7)
        for ba, net, page, ties, page_ties, panel in got:
            self.assertEqual(net, page, ba)          # the figure the page prints under the network (lib/network.ts, net|import)
            self.assertEqual(ties, page_ties, ba)
            self.assertEqual(net, panel, ba)         # the panel's own sum (lib/networkGravity.ts netImportAt)
        self.assertTrue(any(t > 0 for _, _, _, t, _, _ in got))

    def test_the_sum_on_typed_cases(self):
        got = node("import { netOf } from './lib/networkMap.ts';"
                   "const links = [{ a: 'CISO', b: 'BPAT', mw: [-300, null, 0] }, { a: 'AZPS', b: 'CISO', mw: [200, null, 0] }, { a: 'CISO', b: 'NEVP', mw: [50, null, null] }];"
                   "console.log(JSON.stringify([netOf(links, 'CISO', 0), netOf(links, 'CISO', 1), netOf(links, 'CISO', 2), netOf(links, 'ERCO', 0)]));")
        self.assertEqual(got, [{"net": 450, "ties": 3}, {"net": None, "ties": 0}, {"net": 0, "ties": 2}, {"net": None, "ties": 0}])


class OneCarbonScale(unittest.TestCase):
    def test_the_sphere_and_the_region_are_colored_by_one_call_on_one_range(self):
        n = src("site", "app", "network", "Network.tsx")
        self.assertIn("color: colorOf(view.intensity(n.id, hour), lo, hi)", n)                    # the sphere
        self.assertIn("colorOf={(id) => colorOf(view.intensity(id, hour), lo, hi)}", n)           # the region (and the gravity circle)
        self.assertEqual(n.count("function colorOf("), 1)
        self.assertEqual(n.count("const lo = Math.min(...held), hi = Math.max(...held);"), 1)
        # one key under either shape, the network's own; the map adds no scale of its own
        self.assertEqual(n.count("Carbon intensity of generation:"), 1)
        m = src("site", "app", "network", "NetworkMap.tsx")
        self.assertNotIn("intensity-low", m)
        self.assertNotIn("linear-gradient", m)


class TheNetworkWhenTheMapHasNeverBeenOpened(unittest.TestCase):
    def setUp(self):
        self.n = src("site", "app", "network", "Network.tsx")

    def test_the_map_is_loaded_only_when_chosen(self):
        self.assertIn('const NetworkMap = dynamic(() => import("./NetworkMap").then((m) => m.NetworkMap), { ssr: false });', self.n)
        self.assertIn('import type { MapFigures, MapFrame } from "./NetworkMap";', self.n)   # a type only: no code of the map in the network's own chunk
        self.assertIn('const shape: Shape = v3 ? ownShape ?? parseShape(search) : "network";', self.n)
        self.assertIn('{shape === "map" ? (\n          <NetworkMap ', self.n.replace("\r\n", "\n"))

    def test_what_the_map_needs_is_not_computed_in_the_networks_shape(self):
        self.assertIn('const mapFrame: MapFrame | undefined = shape !== "map" ? undefined : {', self.n)
        self.assertIn('const mapFlows = useMemo(() => (shape === "map" ? linksAt(hour) : []), [shape, linksAt, hour]);', self.n)

    def test_the_networks_own_markup_stands(self):
        # the frame of the 3D scene, its key and its hint, word for word as before this session
        for words in (
            '<div ref={box} className="w-full min-w-0 cursor-grab overflow-hidden border border-rule" style={{ height: "min(72vh, 620px)", minHeight: 420 }}',
            'aria-label="A 3D network of the US balancing authorities and their interchange; drag to rotate, scroll to zoom, click a grid for its panel" role="img" />',
            '"Drag to rotate, scroll to zoom, click a grid; it turns slowly until touched."',
            "<span>Sphere: demand (the seven ISOs) or interchange volume (the others)</span>",
            '{batteriesOn && shape === "network" ? <span>Ring: batteries reported for the hour, fuller as they discharge, emptier as they charge.</span> : null}',
            '(["map", "network", "gravity"] as const)',
            '<button type="button" role="switch" aria-checked={batteriesOn} onClick={() => setBatteriesOn(!batteriesOn)}',
        ):
            self.assertIn(words, self.n)

    def test_the_boundary_file_is_asked_for_by_the_map_alone(self):
        self.assertNotIn("/grid/boundaries", self.n)
        self.assertNotIn("ba_boundaries", self.n)
        m = src("site", "app", "network", "NetworkMap.tsx")
        self.assertLess(m.index("fetch(PUBLISHED_FILE)"), m.index(".then((published) => published ?? derivedFile())"))
        self.assertIn('export const PUBLISHED_FILE = "/grid/boundaries";', m)
        self.assertIn('export const BOUNDARY_FILE = "/network/ba_boundaries.json";', m)


@unittest.skipUnless(NODE, "node is not installed")
class TheHoversTheRingAndTheZoom(unittest.TestCase):
    def test_a_ties_hover(self):
        got = node("import { flowTip, reportedBy } from './lib/networkMap.ts';"
                   "const t = (side, unit) => flowTip({ from: 'ERCO', to: 'SWPP', fromName: 'ERCOT', toName: 'Southwest Power Pool', mw: 219.6, when: '2026-11-17 04:00 UTC', unit, a: 'ERCO', b: 'SWPP', aName: 'ERCOT', bName: 'Southwest Power Pool', side });"
                   "console.log(JSON.stringify([t(null, 'hour'), t('first', 'hour').lines[2], t('second', 'day').lines, reportedBy(undefined, 3), reportedBy([3], 3), reportedBy([2], 3)]));")
        self.assertEqual(got[0]["head"], "ERCOT (ERCO) to Southwest Power Pool (SWPP)")
        self.assertEqual(got[0]["lines"][:2], ["220 MW", "2026-11-17 04:00 UTC"])
        self.assertEqual(got[0]["lines"][2], "Reported by ERCOT (ERCO), the first of the two by code; where it filed nothing for this hour, by Southwest Power Pool (SWPP). The file does not mark which.")
        self.assertEqual(got[1], "Reported by ERCOT (ERCO).")
        self.assertEqual(got[2], ["220 MW on average over the day", "2026-11-17 04:00 UTC", "Reported by Southwest Power Pool (SWPP): ERCOT (ERCO) filed nothing for this day."])
        self.assertEqual(got[3:], [None, "second", "first"])

    def test_the_batteries_ring_is_the_networks_rule(self):
        got = node("import { batteryFill, arcPath } from './lib/networkMap.ts';"
                   "console.log(JSON.stringify([batteryFill(100, 100), batteryFill(-100, 100), batteryFill(0, 100), batteryFill(-50, 100), arcPath(10, 10, 5, 0.25), arcPath(10, 10, 5, 0.75), arcPath(10, 10, 5, 1).split('A').length]));")
        self.assertEqual(got, [1, 0.02, 0.5, 0.25, "M10,5A5,5 0 0 1 15,10", "M10,5A5,5 0 1 1 5,10", 3])
        # the same arithmetic as the 3D ring
        self.assertIn("const f = Math.max(0.02, Math.min(1, 0.5 + 0.5 * (mw / batteryMax[n.id])));", src("site", "app", "network", "Network.tsx"))
        self.assertIn("Math.max(0.02, Math.min(1, 0.5 + 0.5 * (mw / (max || 1))))", src("site", "lib", "networkMap.ts"))

    def test_the_zoom(self):
        got = node("import { MAP_HOME, MAP_ZOOM, clampMapView, zoomMapAt } from './lib/networkMap.ts';"
                   "console.log(JSON.stringify([MAP_ZOOM, zoomMapAt(MAP_HOME, 2, 100, 100, 975, 610), zoomMapAt({ k: 2, x: -100, y: -100 }, 0.25, 100, 100, 975, 610), clampMapView({ k: 2, x: 500, y: -5000 }, 975, 610), zoomMapAt(MAP_HOME, 100, 0, 0, 975, 610).k]));")
        self.assertEqual(got, [[1, 12], {"k": 2, "x": -100, "y": -100}, {"k": 1, "x": 0, "y": 0}, {"k": 2, "x": 0, "y": -610}, 12])

    def test_the_nearest_tie_and_its_ends(self):
        got = node("import { nearestLine, onTheLine } from './lib/networkMap.ts';"
                   "const lines = [{ from: [0, 0], to: [100, 0] }, { from: [40, 1], to: [60, 1] }];"
                   "console.log(JSON.stringify([nearestLine([50, 0], lines).index, nearestLine([50, 0.9], lines).index, nearestLine([-5, 0], lines).distance, nearestLine([1, 1], []),"
                   " onTheLine({ along: 0.5, length: 100 }, 8), onTheLine({ along: 0.05, length: 100 }, 8), onTheLine({ along: 0.5, length: 6 }, 8), onTheLine({ along: 0.1, length: 6 }, 8)]));")
        self.assertEqual(got, [0, 1, 5, None, True, False, True, False])


class ThePageAroundTheMap(unittest.TestCase):
    def test_a_grid_with_no_boundary_is_listed_not_dropped(self):
        m = src("site", "app", "network", "NetworkMap.tsx")
        self.assertIn("data-map-listed={noShape.length}", m)
        self.assertIn("Not on the map: no boundary in the file ({noShape.length})", m)
        self.assertIn("data-listed={n.id} onClick={() => onPick(n.id)}", m)

    def test_the_file_is_read_under_the_tools_own_address(self):
        r = src("site", "app", "grid", "boundaries", "route.ts")
        self.assertIn('export const dynamic = "force-static";', r)
        self.assertIn("JSON.stringify({ held: false,", r)
        self.assertIn('path.join(process.cwd(), "data", "regions", rel)', src("site", "lib", "regionsdata.ts"))
        rel = src("site", "lib", "release.ts")
        self.assertIn('  "/grid": "review",', rel)
        self.assertNotIn("/grid/boundaries", rel)      # no line of its own: an address under a page takes the page's status

    @unittest.skipUnless(NODE, "node is not installed")
    def test_the_address_is_in_review_as_the_page_is(self):
        got = node("import { statusOf, exempt } from './lib/release.ts'; console.log(JSON.stringify([statusOf('/grid/boundaries'), statusOf('/grid'), exempt('/grid/boundaries')]));")
        self.assertEqual(got, ["review", "review", False])

    def test_a_switch_that_is_on_can_be_read(self):
        css = src("site", "app", "tokens.css")
        self.assertIn('.brand-a button[type="button"]:not([aria-pressed="true"]):not([aria-checked="true"]):not([data-bar]) {', css)
        self.assertIn('.brand-a button[type="button"]:not([aria-pressed="true"]):not([aria-checked="true"]):not([data-bar]):hover:not(:disabled) {', css)
        self.assertNotIn('.brand-a button[type="button"]:not([aria-pressed="true"]):not([data-bar])', css)

    def test_the_method_note_says_what_the_map_now_does(self):
        note = src("docs", "methods", "grid_network.md")
        for words in ("## The map made whole (session 8601)", "docs/state/page_files_regions.md", "The file does not mark which", "Not on the map: no boundary in the file"):
            self.assertIn(words, note)

    def test_no_em_dash(self):
        for parts in (("site", "app", "network", "NetworkMap.tsx"), ("site", "app", "network", "Network.tsx"), ("site", "lib", "networkMap.ts"), ("site", "lib", "regionsdata.ts"),
                      ("site", "app", "grid", "boundaries", "route.ts"), ("site", "scripts", "check-grid-map.mjs"), ("site", "scripts", "check-network-map.mjs"),
                      ("tests", "fixtures", "session8601", "make_contract_8601.py"), ("tests", "fixtures", "session8601", "ba_boundaries_contract_fixture.json"),
                      ("docs", "methods", "grid_network.md"), ("tests", "test_session8601.py")):
            self.assertNotIn(EM, src(*parts), parts)


if __name__ == "__main__":
    unittest.main()

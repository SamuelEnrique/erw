"""Session 1156 (chain 077): the network map.

- the map keeps the project map's projection and now draws the project map's state outlines (us-atlas's
  states-albers-10m, on the same plane), under and over the derived areas, whose label is unchanged;
- each interchange edge is drawn between two areas from its exporter to its importer (an arrowhead at the importer),
  only with a figure in the frame (site/lib/networkMap.ts edgesAt, the network's rule moved there unchanged); its middle
  answers a hover with its direction, its window and its source;
- a line's MW is written only where the server panel under the map (grid_network_<grid>, session 1151) holds that same
  figure: a tie of the grid in view, in the hour that panel is of (edgeHeld); no other number is written on the map;
- every line is EIA-930's public interchange, for every grid, and no price is drawn on the map; the note says both and
  that the panel under the map carries the checked figures;
- one of the seven ISO grids clicked (other than the grid in view) is a link to its row on the Grid tool, the map and
  the moment shown carried; any other balancing authority opens its panel, as before.
"""

import os
import re
import shutil
import subprocess
import unittest

ROOT = os.path.abspath(os.path.join(os.path.dirname(os.path.abspath(__file__)), ".."))
SITE = os.path.join(ROOT, "site")
EM = chr(0x2014)


def src(*parts):
    with open(os.path.join(ROOT, *parts), encoding="utf-8") as f:
        return f.read()


class TheMap(unittest.TestCase):
    def test_the_project_maps_projection_and_outlines(self):
        m = src("site", "app", "network", "NetworkMap.tsx")
        p = src("site", "app", "map", "ProjectMap.tsx")
        self.assertIn("geoAlbersUsa().scale(1300).translate([W / 2, H / 2])", m)
        self.assertIn("const W = 975, H = 610;", m)
        self.assertIn("geoAlbersUsa().scale(1300).translate([487.5, 305])", p)
        self.assertIn('import statesTopo from "us-atlas/states-albers-10m.json";', m)
        self.assertIn('import statesTopo from "us-atlas/states-albers-10m.json";', src("site", "app", "map", "page.tsx"))
        self.assertIn("mesh(topo, topo.objects.states, (a, b) => a !== b)", m)
        self.assertIn('data-map-state-lines="1"', m)
        self.assertIn('data-map-nation="1"', m)
        # the outlines take no pointer, and the derived label stands as it did
        self.assertIn('pointerEvents="none" data-map-state-lines="1"', m)
        self.assertIn('const derived = held.state === "held" ? derivedLabel(held.file) : null;', m)

    def test_edges_with_a_figure_their_direction_and_their_hover(self):
        lib = src("site", "lib", "networkMap.ts")
        self.assertIn("export function edgesAt(links: MapTie[], h: number): MapEdge[] {", lib)
        self.assertIn("l.mw[h] !== null && l.mw[h] !== undefined && l.mw[h] !== 0", lib)
        self.assertIn("source: v > 0 ? l.a : l.b, target: v > 0 ? l.b : l.a", lib)
        n = src("site", "app", "network", "Network.tsx")
        self.assertIn("const linksAt = useCallback((h: number) => edgesAt(view.links, h), [view]);", n)
        m = src("site", "app", "network", "NetworkMap.tsx")
        self.assertIn('markerEnd={`url(#${dim ? "erw-flow-head-dim" : "erw-flow-head"})`}', m)   # the arrowhead at the importer, as since session 180
        self.assertIn("hitSegment(point(f.source), point(f.target))", m)
        self.assertIn('onPointerMove={hoverAt(`${f.a}-${f.b}`, "edge")}', m)
        self.assertIn("edgeTip(hoveredEdge, nameOf, panel, win, shown)", m)
        self.assertIn('data-map-hover-kind="edge"', m)

    def test_no_figure_the_panel_does_not_hold(self):
        lib = src("site", "lib", "networkMap.ts")
        self.assertIn("return !!panel && !!panel.ba && (e.a === panel.ba || e.b === panel.ba) && !w.day && w.refresh !== null && w.at === panel.hour;", lib)
        m = src("site", "app", "network", "NetworkMap.tsx")
        self.assertNotIn("check=", m)          # the map draws no key: the panel under it carries them
        self.assertNotIn("price", m.lower().replace("no price is drawn here", ""))
        n = src("site", "app", "network", "Network.tsx")
        self.assertIn("mapPanelOf(page.keep, GRID_CHOICES, v3?.complete?.hour ?? null, snap.hours)", n)
        self.assertIn('win={{ at: ts, refresh: view.kind === "live" && view.key === "live" ? snap.built : null, day: isDayView }}', n)
        # the hour the map reads for the panel is the hour the panel is drawn for (lib/gridKeys.ts shownHour)
        self.assertIn("return complete.hour ?? snap.hours[snap.hours.length - 1];", src("site", "lib", "gridKeys.ts"))
        self.assertIn("const hour = complete ?? hours[hours.length - 1];", lib)

    def test_the_note_says_public_and_checked(self):
        n = src("site", "app", "network", "Network.tsx")
        self.assertIn('data-map-public="1">The lines are EIA-930&apos;s public interchange, for every grid', n)
        self.assertIn("no price is drawn on the map", n)
        self.assertIn('data-map-checked="1">The panel under the map carries the checked figures', n)
        # the session 193 words stay
        self.assertIn("the line on the map says what that file is", n)
        self.assertNotIn("published boundary", n)

    def test_a_grid_clicked(self):
        lib = src("site", "lib", "networkMap.ts")
        self.assertIn("export function regionSlug(id: string, choices: readonly MapChoice[], inView: string | null): string | null {", lib)
        n = src("site", "app", "network", "Network.tsx")
        self.assertIn('carryMoment(gridHref(slug, "network", { shape: "map" }), shared)', n)
        # the panel opens as before for every other balancing authority, on the map and on the gravity shape
        self.assertEqual(n.count("onPick={(id) => setPick(snap.nodes.find((n) => n.id === id) ?? null)} />"), 2)
        m = src("site", "app", "network", "NetworkMap.tsx")
        self.assertIn("return href ? <a key={r.id} href={href}", m)
        self.assertIn('{ tabIndex: 0, role: "button", "aria-label": names.get(r.id), onClick: () => onPick(r.id),', m)

    def test_the_method_note(self):
        note = src("docs", "methods", "grid_network.md")
        self.assertIn("**The outlines, the lines and a click (session 1156, 23 October 2026).**", note)
        self.assertLess(note.index("## The map (session 180)"), note.index("(session 1156, 23 October 2026)"))
        self.assertLess(note.index("(session 1156, 23 October 2026)"), note.index("## The gravity shape (session 266)"))

    def test_no_new_dependency(self):
        pkg = src("site", "package.json")
        deps = re.findall(r'^    "([^"]+)": "', pkg, re.M)
        for d in ("d3-geo", "topojson-client", "us-atlas"):
            self.assertIn(d, deps)
        m = src("site", "app", "network", "NetworkMap.tsx")
        imports = re.findall(r'^import .* from "([^"]+)";', m, re.M)
        self.assertEqual(sorted(imports), sorted(["d3-geo", "react", "topojson-client", "topojson-specification", "us-atlas/states-albers-10m.json", "@/lib/format", "@/lib/networkMap"]))

    def test_no_em_dash(self):
        for parts in (("site", "app", "network", "NetworkMap.tsx"), ("site", "app", "network", "Network.tsx"), ("site", "lib", "networkMap.ts"),
                      ("site", "scripts", "test-network-map.mjs"), ("site", "scripts", "check-network-map.mjs"), ("docs", "methods", "grid_network.md"),
                      ("tests", "test_session1156.py")):
            self.assertNotIn(EM, src(*parts), "/".join(parts))
        report = os.path.join(ROOT, "archive", "sessions", "SESSION_1156_REPORT.md")
        if os.path.exists(report):
            self.assertNotIn(EM, src("archive", "sessions", "SESSION_1156_REPORT.md"))


class TheNodeTest(unittest.TestCase):
    @unittest.skipUnless(shutil.which("node"), "node is not installed")
    def test_the_node_test_passes(self):
        r = subprocess.run(["node", os.path.join("scripts", "test-network-map.mjs")], cwd=SITE, capture_output=True, text=True, timeout=120)
        self.assertEqual(r.returncode, 0, r.stdout + r.stderr)
        self.assertIn("9 tests passed", r.stdout)


if __name__ == "__main__":
    unittest.main()

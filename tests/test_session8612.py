"""Session 8612 (chain 504, 19 November 2026): a second reader's read of the Grid tool's map, and its two faults.

Energy Research Warehouse (ERW). Five more cases were taken in a browser on a build, on what the first read did not
touch: a day replayed from the archive, the June 2025 heat story, a region's own Network tab in the Map shape, the
year played, and the batteries of a grid other than California (docs/reviews/grid-map-read-2026-11-19.md, rows 34 on).
What is held here:
- row 35: in the Map shape, a click on an authority in a region's list opened its panel in the 3D network and the map
  was gone. The link now keeps the shape the reader is in;
- row 36: with the Batteries switch on, the map opened on an hour with no battery report, drew no ring and said
  nothing. It now says so under the map, and where the newest report of the view is.
The browser's proof is site/scripts/check-grid-map.mjs and check-grid-regions.mjs. Nothing here makes a request.
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


def node(code):
    r = subprocess.run([NODE, "--input-type=module", "-e", code], cwd=SITE, capture_output=True, text=True, encoding="utf-8", timeout=120)
    assert r.returncode == 0, r.stderr
    return json.loads(r.stdout.strip().splitlines()[-1])


@unittest.skipUnless(NODE, "node is not installed")
class TheLinkKeepsTheShape(unittest.TestCase):
    """Row 35."""

    @classmethod
    def setUpClass(cls):
        link = "/grid?region=sw&view=network&node=SRP"
        cls.d = node("import { keepShape } from './lib/gridregions.ts';"
                     f"const link = {json.dumps(link)};"
                     "console.log(JSON.stringify({ map: keepShape(link, '?region=sw&view=network&shape=map'), gravity: keepShape(link, '?shape=gravity'), none: keepShape(link, '?region=sw&view=network'),"
                     " other: keepShape(link, '?shape=globe'), empty: keepShape(link, ''), has: keepShape(link + '&shape=gravity', '?shape=map'), bare: keepShape('/grid', '?shape=map') }));")
        cls.link = link

    def test_in_the_map_or_the_gravity_shape_the_link_keeps_it(self):
        self.assertEqual(self.d["map"], self.link + "&shape=map")
        self.assertEqual(self.d["gravity"], self.link + "&shape=gravity")
        self.assertEqual(self.d["bare"], "/grid?shape=map")

    def test_in_the_network_shape_the_link_is_as_it_was(self):
        self.assertEqual(self.d["none"], self.link)
        self.assertEqual(self.d["empty"], self.link)

    def test_a_shape_the_tool_does_not_have_is_not_carried_and_a_link_that_names_one_keeps_its_own(self):
        self.assertEqual(self.d["other"], self.link)
        self.assertEqual(self.d["has"], self.link + "&shape=gravity")

    def test_the_regions_list_uses_it_and_leaves_a_new_tab_to_the_browser(self):
        v = src("site", "components", "grid", "RegionViews.tsx")
        self.assertIn('<BaLink href={regionHref(region.code, "network", { node: code })} title={tip}', v)
        b = src("site", "components", "grid", "BaLink.tsx")
        self.assertIn("const to = keepShape(href, window.location.search);", b)
        self.assertIn("if (e.defaultPrevented || e.button !== 0 || e.metaKey || e.ctrlKey || e.shiftKey || e.altKey) return;", b)
        self.assertIn("return <SiteLink href={href} {...rest} onClick={follow} />;", b)        # the site's own link: the release gate still decides


@unittest.skipUnless(NODE, "node is not installed")
class TheNewestBatteryReport(unittest.TestCase):
    """Row 36."""

    @classmethod
    def setUpClass(cls):
        cls.d = node("import { newestBatteryFrame } from './lib/networkV3.ts';"
                     "const b = { A: [5, -3, null, null, null], B: [null, 7, 2, null, null], C: [null, null, null, null, null] };"
                     "const at = (ids, n = 5) => newestBatteryFrame(n, ids, (id, h) => b[id][h] ?? null);"
                     "console.log(JSON.stringify({ all: at(['A', 'B', 'C']), a: at(['A']), c: at(['C']), none: at([]), short: at(['A', 'B'], 2), zero: newestBatteryFrame(3, ['Z'], () => 0) }));")

    def test_the_newest_frame_any_grid_reports_in_and_how_many_do(self):
        self.assertEqual(self.d["all"], {"frame": 2, "grids": 1})
        self.assertEqual(self.d["a"], {"frame": 1, "grids": 1})
        self.assertEqual(self.d["short"], {"frame": 1, "grids": 2})

    def test_no_report_at_all_is_none(self):
        self.assertIsNone(self.d["c"])
        self.assertIsNone(self.d["none"])

    def test_a_report_of_zero_megawatts_is_a_report(self):
        self.assertEqual(self.d["zero"], {"frame": 2, "grids": 1})

    def test_the_map_says_it_only_when_the_switch_is_on_and_no_ring_is_drawn(self):
        m = src("site", "app", "network", "NetworkMap.tsx")
        self.assertIn("{battery && !regions.some((r) => { const b = battery(r.id); return !!b && b.mw !== null && !!b.max; }) ? (", m)
        self.assertIn('data-map-battery-none={batteryNewest ? batteryNewest.when : "none"}', m)
        self.assertIn("No battery is reported for this {unit}.", m)
        self.assertIn("<>None is reported in this view.</>", m)
        n = src("site", "app", "network", "Network.tsx")
        self.assertIn('if (shape !== "map" || !batteriesOn) return undefined;', n)                 # nothing is computed for the 3D network
        self.assertIn("battery={batteriesOn ? mapBattery : undefined} batteryNewest={mapBatteryNewest} sideOf={mapSide} />", n)


class TheRest(unittest.TestCase):
    def test_the_address_while_a_story_plays_is_the_networks_own_rule_and_is_left(self):
        # row 34: found by the read, on production too; a choice of the network's, not changed here
        n = src("site", "app", "network", "Network.tsx")
        self.assertIn("if (!v3 || !restored || playing) return;  // while it plays the address would change five times a second", n)

    def test_the_checks_read_both(self):
        self.assertIn("data-map-battery-none", src("site", "scripts", "check-grid-map.mjs"))
        self.assertIn("shape=map", src("site", "scripts", "check-grid-regions.mjs"))

    def test_no_em_dash(self):
        for p in (("site", "components", "grid", "BaLink.tsx"), ("site", "app", "network", "NetworkMap.tsx"), ("site", "app", "network", "Network.tsx"), ("site", "lib", "networkV3.ts"), ("site", "lib", "gridregions.ts"), ("tests", "test_session8612.py")):
            self.assertNotIn(EM, src(*p), p)


if __name__ == "__main__":
    unittest.main()

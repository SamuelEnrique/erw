"""Session 468: the datacenter tracker by grid (/datacenters?view=grids).

Energy Research Warehouse (ERW), chain 019. No network, no model, no site. The grouping of the sites a public source
names (lib/datacenter/bygrid.ts) on rows written here; each complete year the chart and its fold show equal to the
cost-of-power calculator's own months for that region; the view's tab, keys, checks and note.

    python -m unittest tests.test_session468 -v
"""

import json
import os
import shutil
import subprocess
import unittest

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
SITE = os.path.join(ROOT, "site")
NODE = shutil.which("node")


def read(*p):
    with open(os.path.join(ROOT, *p), encoding="utf-8") as f:
        return f.read()


def node(js):
    r = subprocess.run([NODE, "--input-type=module", "-e", js], cwd=SITE, capture_output=True, text=True, timeout=600)
    if r.returncode != 0:
        raise AssertionError(r.stdout + r.stderr)
    return json.loads(r.stdout.strip().splitlines()[-1])


@unittest.skipUnless(NODE, "node is not installed")
class TheGroups(unittest.TestCase):
    def test_a_site_without_a_zone_stands_beside_the_whole_grid_and_one_with_a_zone_beside_its_zone(self):
        out = node("""
const B = await import("./lib/datacenter/bygrid.ts");
const sites = [
  { table_name: "ercot_interconnection_queue", capacity_mw: 133, zone: null },
  { table_name: "ercot_interconnection_queue", capacity_mw: "58.26", zone: "" },
  { table_name: "caiso_interconnection_queue", capacity_mw: null, zone: "SCE" },
];
const active = [
  { table_name: "ercot_interconnection_queue", capacity_mw: 100, zone: null },
  { table_name: "ercot_interconnection_queue", capacity_mw: null, zone: "X" },
  { table_name: "caiso_interconnection_queue", capacity_mw: 50, zone: "SCE" },
  { table_name: "caiso_interconnection_queue", capacity_mw: 70, zone: "PGE" },
];
const g = B.groups(sites, active);
console.log(JSON.stringify({ g, s: B.groupStat(g, "ercot", "-", "mw_asked"), w: B.groupStat(g, "caiso", "SCE", "sites_with_mw"), none: B.groupStat(g, "spp", "-", "sites") ?? null }));
""")
        ercot, caiso = out["g"]
        self.assertEqual((ercot["grid"], ercot["zone"], ercot["sites"], ercot["sitesWithMw"]), ("ercot", "-", 2, 2))
        self.assertAlmostEqual(ercot["mwAsked"], 191.26)
        self.assertEqual((ercot["activePositions"], ercot["activeMw"]), (2, 100))   # the whole grid's queue, a blank MW counted as a position only
        self.assertEqual((caiso["zone"], caiso["sites"], caiso["sitesWithMw"], caiso["mwAsked"]), ("SCE", 1, 0, 0))
        self.assertEqual((caiso["activePositions"], caiso["activeMw"]), (1, 50))    # only its zone
        self.assertAlmostEqual(out["s"], 191.26)
        self.assertEqual(out["w"], 0)
        self.assertIsNone(out["none"])


@unittest.skipUnless(NODE, "node is not installed")
class TheYears(unittest.TestCase):
    def test_each_complete_year_is_the_calculators_own(self):
        out = node("""
const W = await import("./scripts/datacenter-ways.mjs");
const L = await import("./lib/datacenter.ts");
const res = [];
for (const grid of Object.keys(W.INDEX.grids)) {
  for (const c of L.regionCosts(W.yearFiles(grid), W.INDEX.grids[grid], ["zone"])) {
    const p = W.pageOf({ grid, region: c.id });
    const theirs = L.years(p.ms).filter((y) => y.complete && y.per !== null).map((y) => [y.y, y.per]);
    res.push({ grid, id: c.id, mine: c.years.map((y) => [y.y, y.per]), theirs });
  }
}
console.log(JSON.stringify(res));
""")
        self.assertGreater(len(out), 10)
        for r in out:
            self.assertEqual([y for y, _ in r["mine"]], [y for y, _ in r["theirs"]], r["id"])
            for (_, a), (_, b) in zip(r["mine"], r["theirs"]):
                self.assertAlmostEqual(a, b, places=9, msg=r["id"])


class TheView(unittest.TestCase):
    def test_the_tab_and_the_page(self):
        self.assertIn('"/datacenters": { param: "view", name: "Datacenter tracker", tabs: [["facilities", "Facilities"], ["grids", "By grid"]] }', read("site", "lib", "tabs.ts"))
        page = read("site", "app", "datacenters", "page.tsx")
        self.assertIn('<Tabs page="/datacenters" active="grids" />', page)
        self.assertIn('<Tabs page="/datacenters" active="facilities" />', page)
        self.assertIn('one(await searchParams).view === "grids"', page)
        self.assertIn("<GridsView sites={queues} active={active} />", page)
        self.assertNotIn("release.ts", page)

    def test_the_checks_know_the_view(self):
        cv = read("site", "scripts", "check-values.mjs")
        self.assertIn('"/datacenters?view=grids"', cv)
        self.assertIn('if (p[0] === "dcq")', cv)
        self.assertIn("B.QUEUE_SITE_PATTERN", cv)    # the same pattern the page reads with
        self.assertIn('if (p[3] === "year")', cv)
        self.assertIn('"/datacenters?view=grids"', read("site", "scripts", "check-routes.mjs"))

    @unittest.skipUnless(NODE, "node is not installed")
    def test_check_methods_reads_every_key_as_named(self):
        out = node("""
import fs from "node:fs";
import * as M from "./scripts/check-methods.mjs";
const note = M.noteWords(fs.readFileSync("../docs/methods/datacenter_facilities.md", "utf-8"));
const keys = ["dcq|ercot|-|sites", "dcq|ercot|-|sites_with_mw", "dcq|ercot|-|mw_asked", "dcq|ercot|-|active_positions", "dcq|ercot|-|active_mw",
  "dcpow|ercot|LZ_WEST|year|2024", "dcpow|ercot|LZ_NORTH|per"];
console.log(JSON.stringify(keys.map((k) => M.figures(k).every((f) => M.named(note, f)))));
""")
        self.assertEqual(out, [True] * 7)

    def test_no_dash(self):
        for p in (("site", "app", "datacenters", "GridsView.tsx"), ("site", "lib", "datacenter", "bygrid.ts"), ("docs", "methods", "datacenter_facilities.md"), ("tests", "test_session468.py")):
            t = read(*p)
            self.assertNotIn(chr(0x2014), t, p)
            self.assertNotIn(chr(0x2013), t, p)


if __name__ == "__main__":
    unittest.main()

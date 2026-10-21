"""Session 467: the datacenter tracker on the power side (/datacenters, "On the power side").

Energy Research Warehouse (ERW), chain 019. No network, no model, no site. The section reads the queue positions that
name a datacenter or a large load from each ISO's own queue table (never the held datacenter_facilities), with the
builder's own pattern and grids; its cost figures are the cost-of-power calculator's headline for each region, computed
again here from the page's own price files by the calculator's steps; the value check knows the new key, the method note
names it, and the page's server trace carries the price files.

    python -m unittest tests.test_session467 -v
"""

import json
import os
import re
import shutil
import subprocess
import sys
import unittest

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
SITE = os.path.join(ROOT, "site")
NODE = shutil.which("node")
sys.path.insert(0, os.path.join(ROOT, "warehouse", "derived"))


def read(*p):
    with open(os.path.join(ROOT, *p), encoding="utf-8") as f:
        return f.read()


def node(js):
    r = subprocess.run([NODE, "--input-type=module", "-e", js], cwd=SITE, capture_output=True, text=True, timeout=600)
    if r.returncode != 0:
        raise AssertionError(r.stdout + r.stderr)
    return json.loads(r.stdout.strip().splitlines()[-1])


class TheReader(unittest.TestCase):
    def test_the_pattern_is_the_builders(self):
        import datacenter_facilities as dc
        m = re.search(r'export const QUEUE_SITE_PATTERN = "([^"]+)";', read("site", "lib", "data.ts"))
        self.assertIsNotNone(m)
        self.assertEqual(m.group(1), dc.QUEUE_PATTERN.pattern)
        self.assertTrue(dc.QUEUE_PATTERN.flags & re.I)   # the page matches case-blind (imatch) as the builder does

    def test_the_grids_are_the_builders(self):
        import energy_projects as ep
        m = re.search(r"export const QUEUE_GRIDS = \[([^\]]+)\] as const;", read("site", "lib", "data.ts"))
        self.assertEqual(re.findall(r'"([a-z]+)"', m.group(1)), list(ep.QUEUE_ISOS))

    def test_the_held_table_is_never_read_by_the_section(self):
        data = read("site", "lib", "data.ts")
        body = data[data.index("export async function queueSites"):]
        self.assertNotIn("datacenter_facilities", body)
        self.assertIn("licenseNeeded(table)", body)      # a queue held itself is named, not asked for
        side = read("site", "app", "datacenters", "PowerSide.tsx")
        self.assertNotIn("datacenters(", side)
        self.assertNotIn("eq.datacenter_facilities", side)
        page = read("site", "app", "datacenters", "page.tsx")
        self.assertIn("attempt(queueSites)", page)
        self.assertIn("<PowerSide read={queues} />", page)

    def test_a_held_grid_shows_no_price(self):
        self.assertIn("!licenseHeldGrid(g)", read("site", "app", "datacenters", "PowerSide.tsx"))


@unittest.skipUnless(NODE, "node is not installed")
class TheCosts(unittest.TestCase):
    def test_each_region_is_the_calculators_headline(self):
        out = node("""
const W = await import("./scripts/datacenter-ways.mjs");
const L = await import("./lib/datacenter.ts");
const res = [];
for (const grid of Object.keys(W.INDEX.grids)) {
  for (const c of L.regionCosts(W.yearFiles(grid), W.INDEX.grids[grid], ["zone"])) {
    const p = W.pageOf({ grid, region: c.id });
    res.push({ grid, id: c.id, buy: c.buy, per: c.per, pbuy: p.x.buy, pper: p.s12?.per ?? null, from: c.from, pfrom: p.l12?.[0]?.m ?? null });
  }
}
console.log(JSON.stringify(res));
""")
        self.assertGreater(len(out), 10)
        for r in out:
            self.assertEqual(r["buy"], r["pbuy"], r)
            self.assertEqual(r["from"], r["pfrom"], r)
            self.assertAlmostEqual(r["per"], r["pper"], places=9, msg=r)

    def test_ercot_shows_its_load_zones_not_its_hubs(self):
        out = node("""
const W = await import("./scripts/datacenter-ways.mjs");
const L = await import("./lib/datacenter.ts");
console.log(JSON.stringify(L.regionCosts(W.yearFiles("ercot"), W.INDEX.grids.ercot, ["zone"]).map((c) => [c.id, c.main])));
""")
        ids = [x[0] for x in out]
        self.assertTrue(ids and all(i.startswith("LZ_") for i in ids), ids)
        self.assertEqual([x[0] for x in out if x[1]], ["LZ_NORTH"])   # the calculator's default region, marked


class TheChecks(unittest.TestCase):
    def test_check_values_knows_the_key(self):
        cv = read("site", "scripts", "check-values.mjs")
        self.assertIn('if (p[0] === "dcpow")', cv)
        self.assertIn("W.pageOf({ grid: p[1], region: p[2] })", cv)

    def test_the_note_names_the_figures(self):
        note = read("docs", "methods", "datacenter_facilities.md")
        self.assertIn("`dcpow|<grid>|<region>|per`", note)
        for t in ("ercot_interconnection_queue", "caiso_interconnection_queue", "spp_interconnection_queue", "capacity_mw"):
            self.assertIn(t, note)

    @unittest.skipUnless(NODE, "node is not installed")
    def test_check_methods_reads_the_keys_as_named(self):
        out = node("""
import fs from "node:fs";
import * as M from "./scripts/check-methods.mjs";
const note = M.noteWords(fs.readFileSync("../docs/methods/datacenter_facilities.md", "utf-8"));
const keys = ["dcpow|ercot|LZ_NORTH|per", "dcpow|caiso|TH_SP15_GEN-APND|per", "entity|ercot_interconnection_queue|ercot_queue:25INR0688|capacity_mw"];
console.log(JSON.stringify(keys.map((k) => M.figures(k).every((f) => M.named(note, f)))));
""")
        self.assertEqual(out, [True, True, True])

    def test_the_server_trace_carries_the_price_files(self):
        self.assertIn('"/datacenters": ["./data/datacenter/*.json"]', read("site", "next.config.ts"))

    def test_no_dash(self):
        for p in (("site", "app", "datacenters", "PowerSide.tsx"), ("docs", "methods", "datacenter_facilities.md"), ("tests", "test_session467.py")):
            t = read(*p)
            self.assertNotIn(chr(0x2014), t, p)
            self.assertNotIn(chr(0x2013), t, p)


if __name__ == "__main__":
    unittest.main()

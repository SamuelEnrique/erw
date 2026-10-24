"""Session 1180 (chain 091): a test that failed on Windows, and the storage units and the snapshot, read once.

Energy Research Warehouse (ERW).

Part 1: site/scripts/test-network-split.mjs (session 1175) matched LF line endings in the sources it reads, which a
Windows checkout holds with CRLF (core.autocrlf), so it exited 1 there; it now reads them with line endings normalised.

Part 2: the Mix and Clean tabs of an ISO grid read storage_capacity whole and kept the grid's units (lib/grid.ts load);
now lib/gridReads.ts gridStorageUnits asks for the grid's ISO only and the three columns the Batteries block draws, in
the whole read's order. The Gravity tab read the network's hourly snapshot twice (the network component with a
one-hour revalidation, the Exchange blocks fresh); now the render reads it once, fresh (freshSnapshot, React's cache).
site/scripts/test-grid-units.mjs holds both on a committed fixture of real rows and on the committed snapshot;
site/scripts/same-figures.mjs draws the pages with two trees on the same live answers.

    python -m unittest tests.test_session1180 -v
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
MODULES = all(os.path.isdir(os.path.join(SITE, "node_modules", p)) for p in ("typescript", "react"))
NEW = [("site", "scripts", "test-grid-units.mjs"), ("site", "scripts", "same-figures.mjs"),
       ("site", "scripts", "fixtures", "grid_units.json"), ("tests", "test_session1180.py")]
CHANGED = [("site", "scripts", "test-network-split.mjs"), ("site", "lib", "gridReads.ts"), ("site", "lib", "grid.ts"),
           ("site", "components", "grid", "YourGrid.tsx"), ("site", "components", "grid", "NetworkView.tsx"),
           ("site", "components", "grid", "ExchangeView.tsx"), ("docs", "methods", "grid_network.md")]


def src(*parts):
    with open(os.path.join(ROOT, *parts), encoding="utf-8") as f:
        return f.read()


def node_env():
    return {k: v for k, v in os.environ.items()
            if k not in ("SUPABASE_URL", "SUPABASE_ANON_KEY", "SUPABASE_SERVICE_KEY", "NEXT_PHASE", "NEXT_RUNTIME", "ERW_PAGES_TOGETHER", "ERW_READ_TIMING")}


@unittest.skipUnless(NODE and MODULES, "node or site/node_modules (typescript, react) is not on this machine")
class TheNodeTests(unittest.TestCase):
    def test_every_case_holds(self):
        r = subprocess.run([NODE, "--import", "./scripts/alias-register.mjs", "--import", "./scripts/tsx-register.mjs", "scripts/test-grid-units.mjs"],
                           cwd=SITE, capture_output=True, text=True, timeout=300, env=node_env())
        self.assertEqual(r.returncode, 0, r.stdout[-3000:] + r.stderr[-3000:])
        self.assertIn("every case holds", r.stdout)
        self.assertNotIn("FAIL", r.stdout)
        self.assertGreaterEqual(len(re.findall(r"^ok   ", r.stdout, re.M)), 20)

    def test_the_split_test_passes_on_this_checkout(self):
        r = subprocess.run([NODE, "scripts/test-network-split.mjs"], cwd=SITE, capture_output=True, text=True, timeout=300, env=node_env())
        self.assertEqual(r.returncode, 0, r.stdout[-3000:] + r.stderr[-3000:])
        self.assertIn("7 tests passed", r.stdout)


class TheLineEndings(unittest.TestCase):
    def test_the_split_test_reads_its_sources_as_lf(self):
        t = src("site", "scripts", "test-network-split.mjs")
        self.assertIn('const lf = (s) => s.replace(/\\r\\n/g, "\\n");', t)
        self.assertIn('const read = (r) => lf(fs.readFileSync(path.join(SITE, r), "utf-8"));', t)
        self.assertIn('  const text = lf(fs.readFileSync(file, "utf-8"));', t)
        # the assertion that failed on Windows, unchanged
        self.assertIn('assert.ok(s.includes("graph.current = g;\\n      setSceneReady(true);"), "ready once the graph is built");', t)


class TheUnits(unittest.TestCase):
    def test_the_grid_reads_its_own_units_and_the_columns_drawn(self):
        g = src("site", "lib", "gridReads.ts")
        self.assertIn('return { select: "capacity_mw,status,mwh:extra->>energy_capacity_mwh", table_name: "eq.storage_capacity", "extra->>iso": `eq.${iso}`, order: "entity_id" };', g)
        self.assertIn('return rest<GridUnit>("entities", gridUnitsQuery(iso), HOURLY, 20_000);', g)
        self.assertIn("export type GridUnit = { capacity_mw: number | null; status: string | null; mwh: string | null };", g)
        load = src("site", "lib", "grid.ts")
        self.assertIn('safe("units", () => gridStorageUnits(g.iso), []),', load)
        self.assertNotIn('safe("units", storageUnits, [])', load)
        self.assertNotIn("units.filter((u) => u.iso === g.iso)", load)
        self.assertIn("units: GridUnit[];", load)
        y = src("site", "components", "grid", "YourGrid.tsx")
        self.assertIn('const mw = (us: GridData["units"]) => Math.round(us.reduce((a, u) => a + (u.capacity_mw ?? 0), 0) * 10) / 10;', y)
        self.assertIn('const mwh = (us: GridData["units"]) => Math.round(us.filter((u) => u.mwh).reduce((a, u) => a + Number(u.mwh), 0) * 10) / 10;', y)
        self.assertIn("<Num check={`storage|iso_mw|${g.iso}|operating`} raw={mw(op)}>", y)

    def test_the_whole_fleet_read_is_unchanged(self):
        d = src("site", "lib", "data.ts")
        self.assertIn('{ select: "entity_id,capacity_mw,status,state:extra->>state,iso:extra->>iso,planned_year:extra->>planned_year,mwh:extra->>energy_capacity_mwh", table_name: "eq.storage_capacity", order: "entity_id" },', d)
        self.assertIn("attempt(storageUnits),", src("site", "app", "storage", "page.tsx"))

    def test_the_fixture_is_real_rows_with_their_read(self):
        f = json.loads(src("site", "scripts", "fixtures", "grid_units.json"))
        self.assertEqual(f["whole_table_rows"], 1627)
        self.assertTrue(f["read_at"].startswith("2026-10-24T"))
        by = {}
        for u in f["rows"]:
            by[u["iso"]] = by.get(u["iso"], 0) + 1
        for iso in ("PJM", "SPP", "MISO"):
            self.assertEqual(by[iso], f["whole_table_by_iso"][iso], iso)
        ids = [u["entity_id"] for u in f["rows"]]
        self.assertEqual(len(ids), len(set(ids)))   # in the warehouse's order by entity_id (its collation), each unit once


class TheSnapshot(unittest.TestCase):
    def test_the_gravity_tab_reads_it_once_fresh(self):
        g = src("site", "lib", "gridReads.ts")
        self.assertIn("export const freshSnapshot = cache((): Promise<unknown> => fetchHourly(0));", g)
        n = src("site", "components", "grid", "NetworkView.tsx")
        self.assertIn('const { snap, from } = shape === "gravity" ? pickSnapshot(await freshSnapshot(), committed) : pickSnapshot(await fetchHourly(HOURLY), committed);', n)
        x = src("site", "components", "grid", "ExchangeView.tsx")
        self.assertIn("const { snap } = pickSnapshot(await freshSnapshot(), committed);", x)
        self.assertNotIn("fetchHourly(0)", x)
        # the Now view keeps its own fresh read; the Gravity tab is the only one that passes shape="gravity"
        self.assertIn("fetchHourly(FRESH),", src("site", "components", "grid", "NowView.tsx"))
        self.assertIn('<NetworkView keep={keep} node={p.node} shape="gravity" grid={grid} day={p.day} />', src("site", "app", "grid", "page.tsx"))
        # lib/network.ts keeps no imports beyond types
        imports = [l for l in src("site", "lib", "network.ts").splitlines() if l.startswith("import ")]
        self.assertTrue(imports and all(l.startswith("import type ") for l in imports), imports)


class TheProofTool(unittest.TestCase):
    def test_the_proxy_keeps_answers_in_memory_and_writes_only_figures(self):
        s = src("site", "scripts", "same-figures.mjs")
        for w in ('server.listen(0, "127.0.0.1", r)', "kept.set(key, got);", "delete childEnv.SUPABASE_SERVICE_KEY;",
                  '"figures_before.json"', '"figures_after.json"', "globalThis.__erwRequestCache = new Map();",
                  "export function compareFigures(before, after)", "export async function figuresOf(", "asked only after:"):
            self.assertIn(w, s, w)
        self.assertNotIn("writeFileSync(path.join(work, \"answers", s)


class TheNote(unittest.TestCase):
    def test_the_method_note_says_it(self):
        n = src("docs", "methods", "grid_network.md").replace("\r\n", "\n")
        i = n.index("## The storage units and the snapshot, read once (chain 091, 24 October 2026)")
        sec = n[i:n.index("## Not here")]
        for w in ("Chain 091 in this note (sessions 1178 to 1189): session 1180.", "Decisions (chain 091):", "gridStorageUnits",
                  "freshSnapshot", "2,569 figures", "674 requests to 660", "same-figures.mjs", "test-grid-units.mjs",
                  "session 237"):
            self.assertIn(w, sec, w)


class TheFiles(unittest.TestCase):
    def test_no_em_dash(self):
        for parts in NEW + CHANGED + [("archive", "sessions", "SESSION_1180_REPORT.md")]:
            p = os.path.join(ROOT, *parts)
            if os.path.exists(p):
                self.assertNotIn(chr(0x2014), src(*parts), "/".join(parts))


if __name__ == "__main__":
    unittest.main()

"""Session 1179 (chain 091): one read of a grid's generation a page.

Energy Research Warehouse (ERW). The Mix tab read the grid in view's eia930_all_generation four times a render, each
for its own window (45 days in lib/grid.ts load, 34 in lib/gridReads.ts latestHour, 10 in components/grid/Conditions.tsx
loadConditions, 9 in components/grid/MixView.tsx). Now lib/gridReads.ts shareGeneration starts one read at the widest
window and keeps it for the render (React's cache); generationSince and latestHour take each reader's own days from it,
from the start the reader computed as before. The seven ISO grids share load's 45 days; the Lower 48's Mix tab shares
10 days (app/grid/page.tsx). site/scripts/test-grid-generation.mjs proves the slices on real rows; scripts/tsx-loader.mjs
keeps React's cache for one render (globalThis.__erwRequestCache) so time-grid-reads.mjs walks a page as Next renders it.

    python -m unittest tests.test_session1179 -v
"""

import os
import re
import shutil
import subprocess
import unittest

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
SITE = os.path.join(ROOT, "site")
NODE = shutil.which("node")
MODULES = all(os.path.isdir(os.path.join(SITE, "node_modules", p)) for p in ("typescript", "react"))
NEW = [("site", "scripts", "test-grid-generation.mjs"), ("tests", "test_session1179.py")]
CHANGED = [("site", "lib", "gridReads.ts"), ("site", "lib", "grid.ts"), ("site", "components", "grid", "MixView.tsx"),
           ("site", "components", "grid", "Conditions.tsx"), ("site", "app", "grid", "page.tsx"),
           ("site", "scripts", "tsx-loader.mjs"), ("site", "scripts", "time-grid-reads.mjs"),
           ("docs", "methods", "generation_mix_hourly.md")]


def src(*parts):
    with open(os.path.join(ROOT, *parts), encoding="utf-8") as f:
        return f.read()


def node_env():
    return {k: v for k, v in os.environ.items()
            if k not in ("SUPABASE_URL", "SUPABASE_ANON_KEY", "SUPABASE_SERVICE_KEY", "NEXT_PHASE", "NEXT_RUNTIME", "ERW_PAGES_TOGETHER", "ERW_READ_TIMING")}


@unittest.skipUnless(NODE and MODULES, "node or site/node_modules (typescript, react) is not on this machine")
class TheNodeTest(unittest.TestCase):
    def test_every_case_holds(self):
        r = subprocess.run([NODE, "--import", "./scripts/alias-register.mjs", "--import", "./scripts/tsx-register.mjs", "scripts/test-grid-generation.mjs"],
                           cwd=SITE, capture_output=True, text=True, timeout=300, env=node_env())
        self.assertEqual(r.returncode, 0, r.stdout[-3000:] + r.stderr[-3000:])
        self.assertIn("every case holds", r.stdout)
        self.assertNotIn("FAIL", r.stdout)
        self.assertGreaterEqual(len(re.findall(r"^ok   ", r.stdout, re.M)), 20)


class TheOneRead(unittest.TestCase):
    def test_the_shared_read_is_kept_for_the_render(self):
        g = src("site", "lib", "gridReads.ts")
        self.assertIn('import { cache } from "react";', g)
        self.assertIn('export const GENERATION = "eia930_all_generation";', g)
        self.assertIn("const sharedReads = cache((): Map<string, Shared> => new Map());", g)
        self.assertIn("const covers = (w: Shared | undefined, since: string): w is Shared => !!w && Date.parse(w.since) <= Date.parse(since);", g)
        self.assertIn("return covers(w, since) ? rowsSince(await w.rows, since) : series(GENERATION, { entity, since });", g)
        self.assertIn("if (covers(w, since)) return latestHourOf(await w.rows, variable, since);", g)
        # session 1160's two requests stay, after the shared branch
        self.assertLess(g.index("if (covers(w, since)) return latestHourOf("), g.index("return series(table, { entity, since: top[0].ts_utc });"))

    def test_each_reader_keeps_its_own_start(self):
        load = src("site", "lib", "grid.ts")
        self.assertIn("const genSince = daysAgo(45);\n  shareGeneration(g.entity, genSince);", load)
        self.assertIn('safe("gen", () => generationSince(g.entity, genSince), []),', load)
        self.assertNotIn('series("eia930_all_generation", { entity: g.entity, since: daysAgo(45) })', load)
        self.assertLess(load.index("shareGeneration(g.entity, genSince);"), load.index("await Promise.all(["))
        mix = src("site", "components", "grid", "MixView.tsx")
        self.assertIn("attempt(() => generationSince(b.entity, daysAgo(9)))", mix)
        self.assertNotIn("series(table, { entity: b.entity, since: daysAgo(9) })", mix)
        c = src("site", "components", "grid", "Conditions.tsx")
        self.assertIn("const g = await attempt(() => generationSince(ba.entity, daysAgo(10)));", c)
        self.assertNotIn("series(gt, { entity: ba.entity, since: daysAgo(10) })", c)
        # the calls session 1160 pinned, unchanged
        self.assertIn("BAS.map((b) => loadConditions(b, yesterday, { weather: false }))", c)
        self.assertIn("const r = await loadConditions(ba, conditionsDay());", c)
        now = src("site", "components", "grid", "NowView.tsx")
        self.assertIn('attempt(() => latestHour(GEN, entity, "net_generation_mw", daysAgo(34)))', now)

    def test_the_lower_48_shares_ten_days_before_its_tab_is_drawn(self):
        p = src("site", "app", "grid", "page.tsx")
        line = 'if (!cfg && view === "mix") shareGeneration(`eia930:${grid.ba}`, daysAgo(10));'
        self.assertIn(line, p)
        self.assertLess(p.index('const data = cfg && (view === "mix" || view === "clean") ? await load(cfg) : null;'), p.index(line))
        self.assertLess(p.index(line), p.index("  return (\n    <Brand>"))
        self.assertIn("<MixTable />", p)

    def test_the_walk_is_one_render_a_page(self):
        t = src("site", "scripts", "time-grid-reads.mjs")
        self.assertIn("globalThis.__erwRequestCache = new Map();", t)
        self.assertIn("delete globalThis.__erwRequestCache;", t)
        self.assertLess(t.index("globalThis.__erwRequestCache = new Map();"), t.index("const ctx = await walk(fn({ searchParams: Promise.resolve(p.sp) }));"))
        self.assertIn('const onlyList = only ? only.split(",") : null;', t)
        l = src("site", "scripts", "tsx-loader.mjs")
        self.assertIn('if (specifier === "react" && context.parentURL?.startsWith("file:") && !context.parentURL.includes("/node_modules/")) return { url: "erw-tsx-stub:react", shortCircuit: true };', l)
        self.assertIn('"    if (!(scope instanceof Map)) return fn.apply(null, args);",', l)

    def test_the_method_note_says_it(self):
        n = src("docs", "methods", "generation_mix_hourly.md")
        i = n.index("## One read of a grid's generation a page (chain 091, 24 October 2026)")
        sec = n[i:n.index("## The figures on the page and their keys")]
        for w in ("Decisions (chain 091):", "shareGeneration", "generationSince", "latestHour", "45 days", "10 days",
                  "2,232 figures", "test-grid-generation.mjs", "__erwRequestCache"):
            self.assertIn(w, sec, w)


class TheFiles(unittest.TestCase):
    def test_no_em_dash(self):
        for parts in NEW + CHANGED + [("archive", "sessions", "SESSION_1179_REPORT.md")]:
            p = os.path.join(ROOT, *parts)
            if os.path.exists(p):
                self.assertNotIn(chr(0x2014), src(*parts), "/".join(parts))


if __name__ == "__main__":
    unittest.main()

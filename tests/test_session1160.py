"""Session 1160 (chain 077): the Grid tool's reads, timed, and three made smaller.

Energy Research Warehouse (ERW). site/scripts/time-grid-reads.mjs calls the Grid tool's pages as they are (no build,
no server: site/scripts/tsx-loader.mjs transpiles the components and stands in for the browser's ones), records every
Supabase request they make and times each three times, one at a time. Three reads were made smaller, with the rows a
page draws unchanged:
  - the Now view's mix (components/grid/NowView.tsx) reads the newest hour of the total and that hour's rows
    (lib/gridReads.ts latestHour) in place of the grid's last 34 days, and nothing for California, whose EIA-930
    generation it does not draw;
  - "Generation mix, as a table" (components/grid/Conditions.tsx MixTable) no longer reads the stations' temperatures
    it never drew;
  - every CAISO notice (lib/reliability.ts gridNotices with no bounds) is read once per render, through React's cache.
site/scripts/test-grid-reads.mjs proves each on real rows with a stand-in for PostgREST, and the timing script's pure
parts. Migration 036 is untouched: no read of the three pages took a second (21:21 UTC on 23 October 2026).

    python -m unittest tests.test_session1160 -v
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
NEW = [("site", "lib", "gridReads.ts"), ("site", "scripts", "time-grid-reads.mjs"), ("site", "scripts", "tsx-loader.mjs"),
       ("site", "scripts", "tsx-register.mjs"), ("site", "scripts", "test-grid-reads.mjs"), ("tests", "test_session1160.py")]


def src(*parts):
    with open(os.path.join(ROOT, *parts), encoding="utf-8") as f:
        return f.read()


def node_env():
    return {k: v for k, v in os.environ.items()
            if k not in ("SUPABASE_URL", "SUPABASE_ANON_KEY", "SUPABASE_SERVICE_KEY", "NEXT_PHASE", "NEXT_RUNTIME", "ERW_PAGES_TOGETHER", "ERW_READ_TIMING")}


@unittest.skipUnless(NODE and MODULES, "node or site/node_modules (typescript, react) is not on this machine")
class TheNodeTest(unittest.TestCase):
    def test_every_case_holds(self):
        r = subprocess.run([NODE, "--import", "./scripts/alias-register.mjs", "--import", "./scripts/tsx-register.mjs", "scripts/test-grid-reads.mjs"],
                           cwd=SITE, capture_output=True, text=True, timeout=300, env=node_env())
        self.assertEqual(r.returncode, 0, r.stdout[-3000:] + r.stderr[-3000:])
        self.assertIn("every case holds", r.stdout)
        self.assertNotIn("FAIL", r.stdout)
        self.assertGreaterEqual(len(re.findall(r"^ok   ", r.stdout, re.M)), 20)


class TheReads(unittest.TestCase):
    def test_the_now_view_reads_the_newest_hour_and_nothing_for_california(self):
        now = src("site", "components", "grid", "NowView.tsx")
        self.assertIn('const withheld = grid.slug === "caiso";', now)   # session 118's rule, as test_session237 pins it
        self.assertIn('withheld ? Promise.resolve({ ok: true as const, data: [] as SeriesRow[] }) : attempt(() => latestHour(GEN, entity, "net_generation_mw", daysAgo(34)))', now)
        self.assertNotIn("series(GEN, { entity, since: daysAgo(34) })", now)
        self.assertLess(now.index("const withheld ="), now.index("await Promise.all(["))
        reads = src("site", "lib", "gridReads.ts")
        self.assertIn('variable: `eq.${variable}`,\n    ts_utc: `gte.${since}`,\n    order: "ts_utc.desc",\n  }, HOURLY, 1);', reads)
        self.assertIn("return series(table, { entity, since: top[0].ts_utc });", reads)
        self.assertIn('import "server-only";', reads)

    def test_the_mix_table_reads_no_station(self):
        c = src("site", "components", "grid", "Conditions.tsx")
        self.assertIn("{ weather = true }: { weather?: boolean } = {}", c)
        self.assertIn("const w = weather && ba.station ? await attempt(", c)
        self.assertIn("BAS.map((b) => loadConditions(b, yesterday, { weather: false }))", c)
        self.assertIn("const r = await loadConditions(ba, conditionsDay());", c)   # the grid's own block reads its station

    def test_every_notice_is_read_once_per_render(self):
        r = src("site", "lib", "reliability.ts")
        self.assertIn('import { cache } from "react";', r)
        self.assertIn("return from && to ? noticesBetween(from, to) : everyNotice();", r)
        self.assertIn('const everyNotice = cache(async (): Promise<Notice[]> => rest<Notice>("events", noticesQuery(), HOURLY, 20_000));', r)
        for f in (("components", "grid", "CaisoAlertState.tsx"), ("components", "grid", "Reliability.tsx"), ("components", "grid", "ScarcityPanel.tsx")):
            self.assertIn("gridNotices()", src("site", *f))

    def test_the_timing_script_sends_only_to_supabase_and_never_writes_the_key(self):
        t = src("site", "scripts", "time-grid-reads.mjs")
        self.assertIn("if (u.origin !== origin) {", t)
        self.assertIn('process.env.ERW_PAGES_TOGETHER = "1";', t)
        self.assertIn("delete process.env.SUPABASE_SERVICE_KEY;", t)
        self.assertIn("(SUPABASE_URL|SUPABASE_ANON_KEY)", t)
        self.assertIn("const key = u.pathname + u.search;", t)   # a request is named by its path and query; the key is a header
        self.assertNotIn("console.log(env", t)

    def test_migration_036_is_unchanged(self):
        m = src("warehouse", "supabase", "migrations", "036_slow_read_indexes.sql")
        self.assertEqual(len(re.findall(r"^create index if not exists", m, re.M)), 2)
        self.assertNotIn("1160", m)


class TheFiles(unittest.TestCase):
    def test_no_em_dash(self):
        for parts in NEW + [("site", "components", "grid", "NowView.tsx"), ("site", "components", "grid", "Conditions.tsx"), ("site", "lib", "reliability.ts"),
                            ("archive", "sessions", "SESSION_1160_REPORT.md")]:
            p = os.path.join(ROOT, *parts)
            if os.path.exists(p):
                self.assertNotIn(chr(0x2014), src(*parts), "/".join(parts))


if __name__ == "__main__":
    unittest.main()

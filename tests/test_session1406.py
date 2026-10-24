"""Session 1406 (chain 100): the Lower 48 on the Network tab.

Energy Research Warehouse (ERW).

The Lower 48's Network panel (grid_network_us48, site/components/grid/NetworkFigures.tsx) listed the seven ISO grids'
net exchange in the hour the network opens on. Under that table, which stands as it was, it now draws for the same hour
(site/components/grid/Lower48Demand.tsx, figures by site/lib/gridKeys.ts lower48Demand): each grid's demand, keyed as the
grid in view's own (netsnap|... or series|eia930_all_demand|...), the Lower 48's own (EIA-930's US48), the seven's sum and
its share of the Lower 48 (calc|add and calc|addpct, two ops of site/scripts/check-calc.mjs), and the seven's exchange
with the grids around them in words, with the rest of the Lower 48 and with Canada's and Mexico's operators. The method
is docs/methods/grid_network.md, section "The Lower 48 on the Network tab (chain 100, 24 October 2026)".

    python -m unittest tests.test_session1406 -v
"""

import os
import shutil
import subprocess
import unittest

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
SITE = os.path.join(ROOT, "site")
NODE = shutil.which("node")
EM = chr(0x2014)
HEADING = "## The Lower 48 on the Network tab (chain 100, 24 October 2026)"
FILES = [("site", "components", "grid", "Lower48Demand.tsx"), ("site", "lib", "gridKeys.ts"), ("site", "scripts", "check-calc.mjs"),
         ("site", "scripts", "test-grid-lower48.mjs"), ("site", "scripts", "fixtures", "lower48_demand.json"),
         ("tests", "test_session1406.py"), ("archive", "sessions", "SESSION_1406_REPORT.md")]


def src(*parts):
    with open(os.path.join(ROOT, *parts), encoding="utf-8") as f:
        return f.read().replace("\r\n", "\n")


def node_env():
    return {k: v for k, v in os.environ.items()
            if k not in ("SUPABASE_URL", "SUPABASE_ANON_KEY", "SUPABASE_SERVICE_KEY", "NEXT_PHASE", "NEXT_RUNTIME", "ERW_PAGES_TOGETHER", "ERW_READ_TIMING",
                         "GRID_FILES_OUT", "ERW_SIZES")}


class TheLower48(unittest.TestCase):
    def test_the_panel_draws_the_block_once_and_keeps_its_table(self):
        n = src("site", "components", "grid", "NetworkFigures.tsx")
        self.assertEqual(n.count("<Lower48Demand snap={snap} hour={hour} live={live} grids={ISO_GRIDS} />"), 1)
        # the seven grids' table stands as it was (sessions 1151 and 1182)
        self.assertIn('const head48 = ["Grid", "Net export, MW", "Ties reporting"];', n)
        self.assertIn("const rows = lower48Panel(snap, ISO_GRIDS.map((g) => g.ba), hour);", n)

    def test_the_keys_and_the_read(self):
        k = src("site", "lib", "gridKeys.ts")
        for w in ("export function lower48Demand(", "export function lower48DemandAt(", 'export const OUTSIDE_US48 = ["AESO", "BCHA", "CEN", "HQT", "IESO", "MHEB", "NBSO", "SPC"] as const;',
                  "check: `series|eia930_all_demand|eia930:US48|demand_mw|${hour}`", "check: `calc|add|${ks.join(\"|\")}`",
                  "check: `calc|addpct|${ks.join(\"|\")}|${us48.check.replaceAll(\"|\", \"~\")}`",
                  "const rows = bas.map((ba) => ({ ba, demand: demandAt(snap, ba, hour, demand[ba]) }));"):
            self.assertIn(w, k)
        c = src("site", "scripts", "check-calc.mjs")
        self.assertIn("const ARITY = { ratio: 2, diff: 2, pct: 2, bal: 3 };", c)  # session 1165's line, kept
        self.assertIn("const AT_LEAST = { add: 2, addpct: 3 };", c)
        d = src("site", "app", "network", "data.ts")
        self.assertIn('const us48 = dem.data.filter((r) => r.entity === "eia930:US48");', d)
        self.assertIn("if (us48.length) out.demand.US48 = align(hourly(us48, 1));", d)

    def test_a_failed_read_says_so(self):
        b = src("site", "components", "grid", "Lower48Demand.tsx")
        self.assertIn('<Missing key={key} words="could not be read" why={`${DEMAND_TABLE} could not be read just now: ${failed}`} />', b)
        self.assertNotIn("fetch(", b)
        self.assertIn("<PanelFile of={file} columns={head} rows={rows.map((r) => r.cells)} />", b)
        self.assertIn('id={LOWER48_DEMAND_ANCHOR}', b)
        self.assertIn("<Link href={METHOD_NETWORK_US48}>Method: the Lower 48 on the Network tab</Link>", b)
        a = src("site", "lib", "gridAnchors.ts")
        self.assertIn('export const METHOD_NETWORK_US48 = "/data/methods/grid_network#the-lower-48-on-the-network-tab-chain-100-24-october-2026";', a)

    def test_the_method_section_and_its_decisions(self):
        m = src("docs", "methods", "grid_network.md")
        self.assertEqual(m.count(HEADING), 1)
        sec = m[m.index(HEADING):m.index("## Not here")]
        for w in ("Decisions (session 1406):", "`calc|addpct|<D1>|...|<D7>|<US48>`", "OUTSIDE_US48", "could not be read", "`grid_network_us48_demand`"):
            self.assertIn(w, sec)
        self.assertIn("- Chain 100 (24 October 2026), session 1406, the Lower 48 on the Network tab", m)

    def test_the_older_tests_are_extended(self):
        r = src("site", "scripts", "test-grid-render.mjs")
        self.assertIn('"anchors": ["network-figures", "lower48-demand"], "methods": ["METHOD_NETWORK", "METHOD_NETWORK_US48"], "files": ["grid_network_us48", "grid_network_us48_demand"]', r)
        self.assertIn('raw === "NaN"', r)
        self.assertIn("grid_network_us48 (1406), eia930_all_demand", src("site", "scripts", "test-grid-failed-reads.mjs"))
        self.assertIn("the Lower 48's Network panel: the seven's demand and the Lower 48's", src("site", "scripts", "test-grid-files.mjs"))
        self.assertIn('"components/grid/Lower48Demand.tsx": 1,', src("tests", "test_session473.py"))

    def test_no_em_dash(self):
        for parts in FILES:
            if os.path.exists(os.path.join(ROOT, *parts)):
                self.assertNotIn(EM, src(*parts), parts)

    @unittest.skipUnless(NODE, "node is not on this machine")
    def test_the_node_test_passes(self):
        r = subprocess.run([NODE, "scripts/test-grid-lower48.mjs"], cwd=SITE, capture_output=True, text=True, encoding="utf-8", env=node_env(), timeout=300)
        self.assertEqual(r.returncode, 0, r.stdout[-3000:] + r.stderr[-2000:])
        self.assertIn("every test holds (8 tests)", r.stdout)


if __name__ == "__main__":
    unittest.main()

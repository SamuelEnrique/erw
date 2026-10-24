"""Session 1165 (chain 078): the Network tab's balance, the Grid pack's blind spot 3, said where the figures are.

Under the grid's ties in the panel grid_network_<grid> (site/components/grid/NetworkFigures.tsx, function Balance), for
each of the seven ISO grids: in the hour shown, net generation, demand, the net export over the ties and the gap (net
generation less demand less net export, keyed calc|bal|<G>|<D>|<X>); over the snapshot's week, the mean size of the gap
and its hours (netbal|absmean and netbal|hours, a new key kind recomputed in check-values by lib/gridKeys.ts
netbalValue). The hover tip names session 360's split in one line. The node test runs the functions on a committed
fixture of real rows (site/scripts/fixtures/grid_balance.json).
"""

import json
import os
import shutil
import subprocess
import unittest

ROOT = os.path.abspath(os.path.join(os.path.dirname(os.path.abspath(__file__)), ".."))
SITE = os.path.join(ROOT, "site")
NODE = shutil.which("node")
EM = chr(0x2014)


def src(*parts):
    with open(os.path.join(ROOT, *parts), encoding="utf-8") as f:
        return f.read()


class ThePanel(unittest.TestCase):
    def test_under_the_ties_inside_the_network_panel(self):
        f = src("site", "components", "grid", "NetworkFigures.tsx")
        net = f[f.index("export function NetworkFigures("):f.index("function Balance(")]
        self.assertIn("data-grid-panel={panel}", net)
        call = "<Balance b={balancePanel(snap, grid.ba, hour, live.generation?.[grid.ba], live.demand[grid.ba], p.demand)} label={grid.label} />"
        self.assertIn(call, net)
        self.assertLess(net.index("</ToolSection>"), net.index(call))
        # the Lower 48 returns before it: the balance is for the seven ISO grids, each of them
        self.assertLess(net.index('if (grid.slug === "us48")'), net.index(call))

    def test_the_block_keys_every_figure_and_says_where_the_gap_sits(self):
        f = src("site", "components", "grid", "NetworkFigures.tsx")
        b = f[f.index("function Balance("):f.index("export function GravityFigures")]
        self.assertIn("data-grid-balance={b.ba}", b)
        for fig in ("b.gen", "b.demand", "b.net", "b.gap", "b.hours", "b.absmean"):
            self.assertIn(f"<F key=\"v\" f={{{fig}}} />" if fig not in ("b.hours", "b.absmean") else f"<F f={{{fig}}} />", b)
        # also covered by site/scripts/test-grid-render.mjs: balance_ERCO on /grid?grid=ercot&view=network
        self.assertIn("session 360 found the gap {b.where}", b)
        # also covered by site/scripts/test-grid-render.mjs: balance_ERCO on /grid?grid=ercot&view=network
        self.assertIn('href="/data/methods/eia930_balance"', b)
        self.assertIn("EIA-930&apos;s total, the figure the gravity shape draws", b)
        self.assertIn("California&apos;s hourly mix by fuel stays withheld", b)

    def test_the_keys(self):
        k = src("site", "lib", "gridKeys.ts")
        # also covered by site/scripts/test-grid-render.mjs: balance_ERCO on /grid?grid=ercot&view=network
        self.assertIn("check: `calc|bal|${k(gen)}|${k(demand)}|${k(net)}`", k)
        # also covered by site/scripts/test-grid-render.mjs: balance_ERCO on /grid?grid=ercot&view=network
        self.assertIn("check: `netbal|absmean|${ba}|${from}|${to}`", k)
        # also covered by site/scripts/test-grid-render.mjs: balance_ERCO on /grid?grid=ercot&view=network
        self.assertIn("check: `netbal|hours|${ba}|${from}|${to}`", k)
        # also covered by site/scripts/test-grid-render.mjs: balance_ERCO on /grid?grid=ercot&view=network
        self.assertIn("check: `net|export|${ba}|${hour}`", k)
        self.assertIn("${BALANCE_SPLIT}", k)
        # the gravity panel's generation key is unchanged, now drawn through generationAt
        # also covered by site/scripts/test-grid-render.mjs: grid_mix_ercot on /grid?grid=ercot&view=mix
        self.assertIn("check: `series|eia930_all_generation|eia930:${ba}|net_generation_mw|${hour}`", k)
        self.assertIn("const genOf = (ba: string): Fig | null => generationAt(snap, ba, hour, generation?.[ba]);", k)


class TheChecker(unittest.TestCase):
    def test_check_values_recomputes_calc_bal_and_netbal(self):
        c = src("site", "scripts", "check-values.mjs")
        self.assertIn('import * as CALC from "./check-calc.mjs";', c)
        self.assertIn("for (const k of CALC.calcOperands(parts)) xs.push(Number(await truth(k)));", c)
        self.assertIn("return CALC.calcOf(op, xs);", c)
        self.assertIn('if (p[0] === "netbal") {', c)
        self.assertIn("return K.netbalValue(check, snaps, gen, dem);", c)
        for t in ('read("eia930_all_generation", "net_generation_mw")', 'read("eia930_all_demand", "demand_mw")'):
            self.assertIn(t, c)

    def test_calc_keeps_its_three_old_ops(self):
        m = src("site", "scripts", "check-calc.mjs")
        self.assertIn("const ARITY = { ratio: 2, diff: 2, pct: 2, bal: 3 };", m)
        self.assertIn('op === "ratio" ? x / y : op === "diff" ? x - y : op === "pct" ? (x / y) * 100 : x - y - w', m)

    def test_check_methods_reads_every_operand(self):
        m = src("site", "scripts", "check-methods.mjs")
        self.assertIn('if (head === "calc" && p.length >= 4) return p.slice(2).flatMap((x) => figures(x.replaceAll("~", "|")));', m)


class TheNotesAndTheFixture(unittest.TestCase):
    def test_the_method_note_names_the_keys(self):
        n = src("docs", "methods", "grid_network.md")
        s = n[n.index("## The balance, said where the figures are (chain 078, 24 October 2026)"):n.index("## Not here")]
        for words in ("`calc|bal|<G>|<D>|<X>`", "`netbal|absmean|<BA>|<from>|<to>`", "`netbal|hours|<BA>|<from>|<to>`",
                      "Decisions (chain 078):", "eia930_all_generation", "eia930_all_demand", "session 118 ruling"):
            self.assertIn(words, s)
        self.assertIn("`netbal|absmean|<BA>|<from>|<to>`", n[n.index("## The figures on the page and their keys"):])
        self.assertIn("## On the Grid tool (session 1165, chain 078)", src("docs", "methods", "eia930_balance.md"))

    def test_the_fixture_is_the_seven_grids_week(self):
        fx = json.loads(src("site", "scripts", "fixtures", "grid_balance.json"))
        self.assertEqual(sorted(fx["generation"]), ["CISO", "ERCO", "ISNE", "MISO", "NYIS", "PJM", "SWPP"])
        self.assertEqual(sorted(fx["demand"]), sorted(fx["generation"]))
        self.assertEqual(len(fx["hours"]), 168)
        self.assertTrue(all(len(l["mw"]) == len(fx["hours"]) for l in fx["links"]))
        self.assertIn("anon key", fx["about"])
        self.assertTrue(fx["read_at"].endswith("Z") and fx["snapshot_built"].endswith("Z"))

    def test_no_em_dash(self):
        for parts in (("site", "components", "grid", "NetworkFigures.tsx"), ("site", "lib", "gridKeys.ts"), ("site", "scripts", "check-calc.mjs"),
                      ("site", "scripts", "test-grid-balance.mjs"), ("site", "scripts", "check-values.mjs"), ("docs", "methods", "grid_network.md"),
                      ("docs", "methods", "eia930_balance.md")):
            self.assertNotIn(EM, src(*parts), parts)


@unittest.skipUnless(NODE, "node is not installed")
class TheNodeTest(unittest.TestCase):
    def test_the_balance_on_the_fixture(self):
        r = subprocess.run([NODE, "scripts/test-grid-balance.mjs"], cwd=SITE, capture_output=True, text=True, timeout=120)
        self.assertEqual(r.returncode, 0, r.stdout[-2000:] + r.stderr[-2000:])
        self.assertIn("11 tests passed", r.stdout)


if __name__ == "__main__":
    unittest.main()

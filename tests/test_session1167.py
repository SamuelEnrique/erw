"""Session 1167 (chain 078): no held grid's rows on the Grid tool, and the Exchange blocks under the gravity shape.

Part 1, the standing rule (site/lib/license.ts; chain 077's rules: "no held grid's rows are drawn"):
- the Clean tab's "The seven grids" (site/components/mix/views.tsx CleanView): ISO-NE's, MISO's and NYISO's cells read
  "license needed" in the view's own placeholder, as every other block of the view; the four other grids' as they were;
- the hub price beside the mix (DayView, DuckView, factor=price): a held grid's reads "license needed";
- the network's replayed and story prices (site/app/network/Network.tsx): a held grid's are left out of each view;
- ISO-NE's queue positions of energy_projects (site/lib/grid.ts, site/components/grid/YourGrid.tsx) and a held grid's
  hub prices there read "license needed"; the rule in one place, site/lib/gridHeld.ts.
Part 2, the Exchange blocks (site/components/grid/ExchangeView.tsx): each neighbour's week keyed by a new kind,
nettie|<mean|min|max|hours>|<BA>|<other>|<from>|<to> (site/lib/gridKeys.ts nettieValue, run by check-values), the
direction in words, the hour's age said once (net|lag).
The node tests: site/scripts/test-grid-held.mjs and site/scripts/test-grid-exchange.mjs.
"""

import os
import re
import shutil
import subprocess
import unittest

ROOT = os.path.abspath(os.path.join(os.path.dirname(os.path.abspath(__file__)), ".."))
SITE = os.path.join(ROOT, "site")
NODE = shutil.which("node")
MODULES = all(os.path.isdir(os.path.join(SITE, "node_modules", p)) for p in ("typescript", "react"))
EM = chr(0x2014)
NEW = [("site", "lib", "gridHeld.ts"), ("site", "scripts", "test-grid-held.mjs"), ("site", "scripts", "test-grid-exchange.mjs"), ("tests", "test_session1167.py")]
CHANGED = [("site", "components", "mix", "views.tsx"), ("site", "components", "grid", "YourGrid.tsx"), ("site", "components", "grid", "ExchangeView.tsx"),
           ("site", "app", "network", "Network.tsx"), ("site", "lib", "grid.ts"), ("site", "lib", "gridtables.ts"), ("site", "lib", "gridKeys.ts"),
           ("site", "scripts", "check-values.mjs"), ("site", "scripts", "check-network-v3.mjs"), ("docs", "methods", "grid_network.md"),
           ("docs", "methods", "generation_mix_hourly.md")]


def src(*parts):
    with open(os.path.join(ROOT, *parts), encoding="utf-8") as f:
        return f.read()


def node_env():
    return {k: v for k, v in os.environ.items() if k not in ("SUPABASE_URL", "SUPABASE_ANON_KEY", "SUPABASE_SERVICE_KEY", "NEXT_PHASE", "NEXT_RUNTIME")}


class TheHeldGrids(unittest.TestCase):
    def test_the_clean_views_seven_grids_hold_the_held_grids_first(self):
        v = src("site", "components", "mix", "views.tsx")
        self.assertIn("if (held(g)) return { key: g, on: c.grids.includes(g), cells: [nameOf(g), ...Array.from({ length: 6 }, (_, i) => <LW key={i} />)] };", v)
        self.assertLess(v.index("if (held(g)) return { key: g, on: c.grids.includes(g)"), v.index("const cf = `clean/${g}.json`, y = `years.${year}`, key = !held(g);"))
        # the price beside the mix: held unless the file says paused
        self.assertIn('const hp = f.price_da.status === "paused" ? null : heldGridPrice(g);', v)

    def test_the_network_leaves_a_held_grids_price_out_of_each_view(self):
        n = src("site", "app", "network", "Network.tsx")
        # session 124's line stands; each view's own price goes through shownPrice
        self.assertIn("const priceOf = (view: View, v3on: boolean, id: string, h: number) => (v3on && PAUSED_PRICE[id] ? null : view.price(id, h));", n)
        self.assertEqual(n.count("shownPrice(id, "), 3)
        self.assertNotIn("hub_prices[id]?.[h] ?? null", n)
        self.assertIn("data-price-held={pick.id}", n)

    def test_the_queue_and_the_prices_of_a_held_grid(self):
        g = src("site", "lib", "grid.ts")
        self.assertIn('return shownQueue(await rest<QueueRow>("entities", {', g)
        y = src("site", "components", "grid", "YourGrid.tsx")
        self.assertIn("} else if (heldQueue(g.queue_table)) {", y)
        self.assertIn("if (g.hub && licenseHeldRow(T, g.hub.entity)) return <HeldLine", y)
        self.assertIn('import { Missing } from "@/components/mix/Now";', y)

    def test_the_license_lines_name_the_hub_price_table(self):
        t = src("site", "lib", "gridtables.ts")
        self.assertEqual(t.count('"iso_hub_prices_history"'), 3)


class TheExchange(unittest.TestCase):
    def test_the_week_is_keyed_and_checked(self):
        k = src("site", "lib", "gridKeys.ts")
        self.assertIn("export function nettieValue(check: string, snaps: Snapshot[]): number | undefined {", k)
        c = src("site", "scripts", "check-values.mjs")
        self.assertIn('if (p[0] === "nettie") {', c)
        self.assertIn("return K.nettieValue(check, [stored, committed].filter((s) => s && N.isSnapshot(s)));", c)
        e = src("site", "components", "grid", "ExchangeView.tsx")
        # also covered by site/scripts/test-grid-render.mjs: view_exchange on /grid?grid=ercot&view=gravity
        self.assertIn("<Num check={`net|tie|${ba}|${t.other}|${hour}`} raw={t.mw}>{shown(t.mw)}</Num>", e)
        # also covered by site/scripts/test-grid-render.mjs: view_exchange on /grid?grid=ercot&view=gravity
        self.assertIn("<Num check={`net|lag|${hour}|${built}`} raw={lag}>{shown(lag)}</Num>", e)
        self.assertEqual(e.count("<Age hour={hour} built={snap.built} />"), 2)

    def test_the_note_names_the_new_keys(self):
        m = src("docs", "methods", "grid_network.md")
        for w in ("nettie|mean|<BA>|<other>|<from>|<to>", "nettie|min|", "nettie|max|", "nettie|hours|", "### The Exchange blocks under the gravity shape (session 1167)", "Decisions (session 1167):"):
            self.assertIn(w, m)
        self.assertIn("Session 1167 (the standing rule", src("docs", "methods", "generation_mix_hourly.md"))


class TheFiles(unittest.TestCase):
    def test_no_em_dash(self):
        for parts in NEW + CHANGED:
            self.assertNotIn(EM, src(*parts), parts)


@unittest.skipUnless(NODE and MODULES, "node or site/node_modules (typescript, react) is not on this machine")
class TheNodeTests(unittest.TestCase):
    def test_held(self):
        r = subprocess.run([NODE, "--import", "./scripts/alias-register.mjs", "--import", "./scripts/tsx-register.mjs", "scripts/test-grid-held.mjs"],
                           cwd=SITE, capture_output=True, text=True, timeout=300, env=node_env())
        self.assertEqual(r.returncode, 0, r.stdout[-3000:] + r.stderr[-3000:])
        self.assertIsNotNone(re.search(r"^\S* ?pass 6", r.stdout, re.M), r.stdout[-1500:])

    def test_exchange(self):
        r = subprocess.run([NODE, "scripts/test-grid-exchange.mjs"], cwd=SITE, capture_output=True, text=True, timeout=300, env=node_env())
        self.assertEqual(r.returncode, 0, r.stdout[-3000:] + r.stderr[-3000:])
        self.assertIsNotNone(re.search(r"^\S* ?pass 7", r.stdout, re.M), r.stdout[-1500:])


if __name__ == "__main__":
    unittest.main()

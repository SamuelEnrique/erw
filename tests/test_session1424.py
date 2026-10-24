"""Session 1424 (chain 111): the Gravity tab's blocks at 390 pixels, from the code.

Session 1158's rules (scroll frames a keyboard reaches, captions, header cells with a scope, row headers where a row names
a tie or a grid, no fixed width above 358 px outside a frame, long words breaking) read on the blocks chains 078 to 100
added under and beside the gravity shape: the gravity table, the Exchange blocks (session 1167's seven-column ties table,
the twelve months, the Lower 48's seven grids), the gravity day line (1170), the balance (1165) and the replayed day's
table. Every table is the shared ToolTable and held already; one miss mended in markup and classes only: a failed read's
reason (which can hold the database's answer, a long run without a space) now breaks, on the Gravity tab's twelve months
and the network's line. The render test's Gravity cases carry their tables (site/scripts/test-grid-render.mjs `tables`,
read from the drawn markup by grid-render-standin.mjs); site/scripts/test-gravity-390.mjs holds the source. No figure
moved: same-figures.mjs on the Gravity tab of ERCOT, CAISO and the Lower 48, 190 figures, every page the same.
"""

import json
import os
import shutil
import subprocess
import unittest

ROOT = os.path.abspath(os.path.join(os.path.dirname(os.path.abspath(__file__)), ".."))
SITE = os.path.join(ROOT, "site")
NODE = shutil.which("node")
MODULES = all(os.path.isdir(os.path.join(SITE, "node_modules", p)) for p in ("typescript", "react"))
EM = chr(0x2014)
CHANGED = [("site", "components", "grid", "ExchangeView.tsx"), ("site", "components", "grid", "NetworkView.tsx"),
           ("site", "scripts", "grid-render-standin.mjs"), ("site", "scripts", "test-grid-render.mjs"), ("site", "scripts", "test-gravity-390.mjs"),
           ("docs", "methods", "grid_network.md"), ("tests", "test_session1424.py")]


def src(*parts):
    with open(os.path.join(ROOT, *parts), encoding="utf-8") as f:
        return f.read().replace("\r\n", "\n")


def node_env():
    return {k: v for k, v in os.environ.items()
            if k not in ("SUPABASE_URL", "SUPABASE_ANON_KEY", "SUPABASE_SERVICE_KEY", "NEXT_PHASE", "NEXT_RUNTIME", "ERW_PAGES_TOGETHER", "ERW_READ_TIMING",
                         "GRID_FILES_OUT", "ERW_SIZES")}


class TheMarkup(unittest.TestCase):
    def test_a_failed_reads_reason_breaks(self):
        self.assertIn('<div className="break-words" data-reason-wraps="1"><NoData what="the twelve months" reason={sup.reason} /></div>',
                      src("site", "components", "grid", "ExchangeView.tsx"))
        self.assertIn('<p className="mt-2 text-sm text-muted break-words" role="status" data-reason-wraps="1">The last twelve months could not be read',
                      src("site", "components", "grid", "NetworkView.tsx"))

    def test_the_tables_are_the_shared_table_with_captions(self):
        for name, n in (("ExchangeView.tsx", 3), ("NetworkFigures.tsx", 4), ("ReplayDay.tsx", 1)):
            s = src("site", "components", "grid", name)
            self.assertEqual(s.count("<ToolTable "), n, name)
            self.assertEqual(s.count("<ToolTable caption="), n, name)


class TheRenderCases(unittest.TestCase):
    def test_the_gravity_cases_carry_their_tables(self):
        cases = [json.loads(line.strip().rstrip(",")) for line in src("site", "scripts", "test-grid-render.mjs").split("\n") if line.startswith('  {"name": ')]
        mine = [c for c in cases if c["block"].startswith(("grid_gravity_", "view_exchange", "gravityday", "balance_"))]
        self.assertEqual(len(mine), 13)
        for c in mine:
            self.assertIsInstance(c.get("tables"), list, c["name"])
        by = {c["name"]: c for c in cases}
        self.assertEqual(by["view_exchange on /grid?grid=ercot&view=gravity"]["tables"], ["ERCOT's ties in the hour", "ERCOT's neighbours over twelve months"])
        self.assertEqual(by["grid_gravity_us48 on /grid?grid=us48&view=gravity"]["tables"], ["The seven grids in the gravity shape, the hour shown"])
        self.assertEqual(by["gravityday on /grid?grid=ercot&view=gravity&net=day&t=2020-08-14"]["tables"], [])

    def test_the_stand_in_reads_the_tables(self):
        s = src("site", "scripts", "grid-render-standin.mjs")
        self.assertIn("const newBlock = () => ({ nums: [], all: [], text: [], hover: [], heads: [], ids: [], methods: [], files: [], errors: [], tables: [], wide: [] });", s)
        self.assertIn("export function widthOver(type, props) {", s)
        # the blocks the page names are as they were (sessions 1404, 1412, 1422)
        self.assertIn('export const BLOCKS = [["data-grid-panel", (v) => v],', s)


class TheNote(unittest.TestCase):
    def test_the_decisions(self):
        g = src("docs", "methods", "grid_network.md")
        self.assertIn("Session 1424, the Gravity tab's blocks at 390 pixels, from the code.", g)
        self.assertIn("Decisions (chain 111, session 1424):", g)


class TheFiles(unittest.TestCase):
    def test_no_em_dash(self):
        for parts in CHANGED:
            self.assertNotIn(EM, src(*parts), parts)


@unittest.skipUnless(NODE, "node is not on this machine")
class TheNodeTests(unittest.TestCase):
    def test_the_source_test(self):
        r = subprocess.run([NODE, os.path.join("scripts", "test-gravity-390.mjs")], cwd=SITE, capture_output=True, text=True, encoding="utf-8", timeout=120)
        self.assertEqual(r.returncode, 0, r.stdout + r.stderr)
        self.assertIn("6 tests passed", r.stdout)

    @unittest.skipUnless(MODULES, "site/node_modules (typescript, react) is needed")
    def test_the_render_test(self):
        r = subprocess.run([NODE, "--import", "./scripts/alias-register.mjs", "--import", "./scripts/tsx-register.mjs", "scripts/test-grid-render.mjs"],
                           cwd=SITE, capture_output=True, text=True, encoding="utf-8", env=node_env(), timeout=600)
        self.assertEqual(r.returncode, 0, r.stdout[-3000:] + r.stderr[-2000:])
        self.assertIn("ok   the 390 reader finds what it is asked to (1424)", r.stdout)
        self.assertIn("ok   view_exchange on /grid?grid=ercot&view=gravity (an ISO with prices (ERCOT))", r.stdout)


if __name__ == "__main__":
    unittest.main()

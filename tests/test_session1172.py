"""Session 1172 (chain 078): every old address of the Grid tool, tested.

site/scripts/test-grid-addresses.mjs follows every redirect to /grid in site/next.config.ts as Next applies it (the
rules' order, their query conditions and named groups, the request's query under the destination's) and /ask's own
redirect (site/app/ask/page.tsx), then reads the landed query through lib/gridtool.ts gridPick as app/grid/page.tsx
does: each old address and each old view word (OLD_VIEWS now, exchange, ask; mix=clean; shape=gravity; grid=ERCO,
ba=erco, grids=pjm,miso, node=BPAT) opens the tab that holds its blocks, with the grid it named, its own words kept.
The round trips: gridHref, the picker's carried day, the map's region link and the network's own writes read back to
the same grid and tab. The route check lists one address of each rule and word (scripts/check-routes.mjs).
No code of gridtool.ts changed: every case passed as the code stands.
"""

import os
import re
import shutil
import subprocess
import unittest

ROOT = os.path.abspath(os.path.join(os.path.dirname(os.path.abspath(__file__)), ".."))
SITE = os.path.join(ROOT, "site")
NODE = shutil.which("node")
EM = chr(0x2014)
NEW = [("site", "scripts", "test-grid-addresses.mjs"), ("tests", "test_session1172.py")]
CHANGED = [("site", "scripts", "check-routes.mjs"), ("docs", "methods", "grid_network.md")]


def src(*parts):
    with open(os.path.join(ROOT, *parts), encoding="utf-8") as f:
        return f.read()


def node_env():
    return {k: v for k, v in os.environ.items() if k not in ("SUPABASE_URL", "SUPABASE_ANON_KEY", "SUPABASE_SERVICE_KEY", "NEXT_PHASE", "NEXT_RUNTIME")}


class TheRouteCheck(unittest.TestCase):
    def test_the_old_addresses_are_listed(self):
        routes = src("site", "scripts", "check-routes.mjs")
        for a in ("/network?view=live&grid=BPAT", "/network?shape=gravity&grid=ERCO", "/network?shape=map&grid=NYIS", "/mix?view=clean",
                  "/mix?view=now&ba=erco&mixp=month", "/mix?view=day&grids=pjm,miso&period=2026-04", "/grid/ercot?view=network",
                  "/ask?grid=ercot&q=What+was+the+peak%3F", "/grid?grid=caiso&view=now&mixp=month", "/grid?grid=nyiso&view=mix&mix=clean",
                  "/grid?grid=ercot&view=network&shape=gravity", "/grid?grid=ERCO&view=network", "/grid?view=mix&ba=erco",
                  "/grid?view=mix&mix=day&grids=pjm,miso", "/grid?grid=ercot&view=network&net=day&t=2021-02-15&node=BPAT"):
            self.assertIn(f'"{a}"', routes)
        # the addresses listed before stay
        for a in ("/network", "/mix", "/emissions", "/mix/clean", "/mix/stress", "/network/v3", "/grid/ercot", "/grid?grid=ercot&view=now", "/grid?grid=caiso&ask=1"):
            self.assertIn(f'"{a}"', routes)

    def test_the_method_note_names_the_test(self):
        self.assertIn("site/scripts/test-grid-addresses.mjs", src("docs", "methods", "grid_network.md"))

    def test_no_em_dash(self):
        for parts in NEW + CHANGED:
            self.assertNotIn(EM, src(*parts), "/".join(parts))


@unittest.skipUnless(NODE, "node is not on this machine")
class TheNodeTest(unittest.TestCase):
    def test_every_old_address(self):
        r = subprocess.run([NODE, "--import", "./scripts/alias-register.mjs", "scripts/test-grid-addresses.mjs"],
                           cwd=SITE, capture_output=True, text=True, timeout=120, env=node_env())
        self.assertEqual(r.returncode, 0, r.stdout[-3000:] + r.stderr[-3000:])
        m = re.search(r"^(\d+) tests passed, (\d+) addresses", r.stdout, re.M)
        self.assertIsNotNone(m, r.stdout[-1500:])
        self.assertGreaterEqual(int(m.group(1)), 8)
        self.assertGreaterEqual(int(m.group(2)), 60)


if __name__ == "__main__":
    unittest.main()

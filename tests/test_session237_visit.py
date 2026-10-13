"""Session 237, at the landing (13 October 2026): /network redirects into the Grid tool, and GitHub's check failed at
its warm-up step, which asked each listed page with redirect "manual" and counted a 308 as a page that never answered.
The snapshot would have failed the same way after the deploy (a status other than 200 makes a snapshot incomplete).
Both scripts now follow a redirect inside the site, as a visitor's browser does, and name the hops.

    python -m unittest tests.test_session237_visit
"""
import os
import unittest

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
EM = chr(0x2014)


def src(*parts):
    with open(os.path.join(ROOT, *parts), encoding="utf-8") as f:
        return f.read()


class TheVisit(unittest.TestCase):
    def test_the_snapshot_follows_a_redirect_inside_the_site_and_keeps_the_hops(self):
        s = src("site", "scripts", "snapshot-live.mjs")
        self.assertIn("export async function visit(base, page, init = {}) {", s)
        self.assertIn('const res = await fetch(url, { ...init, redirect: "manual" });', s)               # still asked by hand: a hop is seen, not hidden
        self.assertIn("if (next.origin === new URL(base).origin) {", s)                                   # never followed off the site
        self.assertIn("if (hop < 3 && [301, 302, 303, 307, 308].includes(res.status) && to) {", s)        # three hops at most
        self.assertIn("const { res, via } = await visit(base, page, { signal: AbortSignal.timeout(REQUEST_MS), headers: { \"cache-control\": \"no-cache\" } });", s)
        self.assertIn('if (via.length) text.unshift(`[redirected: ${via.join(", then ")}]`);', s)         # the hops are compared with the text
        self.assertIn("if (res.status !== 200) failed++;", s)                                             # the page a visitor ends on must still answer 200

    def test_the_list_of_pages_is_as_it_was(self):
        s = src("site", "scripts", "snapshot-live.mjs")
        self.assertIn('export const LIVE_PAGES = ["/", "/about", "/storage", "/cost-of-power/seller", "/network", "/cost-of-power/battery", ...BATTERY, ...SELLER, ...WORDS];', s)

    def test_the_warm_up_follows_it_too(self):
        w = src("site", "scripts", "warm-live.mjs")
        self.assertIn('import { visit } from "./snapshot-live.mjs";', w)
        self.assertIn("const { res, via } = await visit(base, page, { signal: AbortSignal.timeout(REQUEST_MS) });", w)
        self.assertIn("ok = res.status === 200;", w)

    def test_the_network_address_redirects_into_the_grid_tool(self):
        self.assertIn('{ source: "/network", destination: "/grid?view=network", permanent: true },', src("site", "next.config.ts"))

    def test_no_em_dash(self):
        for f in ("site/scripts/snapshot-live.mjs", "site/scripts/warm-live.mjs", "tests/test_session237_visit.py"):
            self.assertNotIn(EM, src(*f.split("/")), f)


if __name__ == "__main__":
    unittest.main()

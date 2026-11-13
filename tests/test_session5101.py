"""Session 5101: the curtain covers the App Router's transport addresses (site/proxy.ts).

Energy Research Warehouse (ERW). No network, no model, no build. docs/reviews/security-faults-2026-11-13.md, row 1: on
13 November 2026 a visitor could read a page in review at <page>.segments/<segment>.segment.rsc, because the proxy's
matcher left every address with an extension alone. The node tests of site/scripts/test-curtain.mjs hold the fix (the
matcher compiled as Next compiles it runs on those addresses; the rule answers 404 without the internal cookie); this
file runs them, pins the lines other sessions' tests and the fix depend on, and tests the deployed site's check
(site/scripts/check-curtain.mjs) on canned answers.

    python -m unittest tests.test_session5101 -v
"""

import json
import os
import shutil
import subprocess
import unittest

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
SITE = os.path.join(ROOT, "site")


def src(*parts):
    with open(os.path.join(ROOT, *parts), encoding="utf-8") as f:
        return f.read()


def node():
    n = shutil.which("node")
    if not n:
        raise unittest.SkipTest("node is not on the path")
    return n


class TheCurtain(unittest.TestCase):
    def test_node_tests_pass(self):
        r = subprocess.run([node(), "--no-warnings", "--import", "./scripts/alias-register.mjs", "scripts/test-curtain.mjs"],
                           cwd=SITE, capture_output=True, text=True, timeout=180)
        self.assertEqual(r.returncode, 0, (r.stdout + r.stderr)[-4000:])
        self.assertIn("8 tests passed", r.stdout)

    def test_the_matcher_runs_on_rsc_addresses_and_on_no_other_extension(self):
        p = src("site", "proxy.ts")
        matcher = p.split("matcher:")[1]
        # the exception to "anything with an extension is left alone" is .rsc, in any case
        self.assertIn("(?!.*\\\\.[rR][sS][cC]$).*\\\\.[a-zA-Z0-9]+$", matcher)
        for kept in ("api/", "internal/", "_next/", "in-review$"):
            self.assertIn(kept, matcher)

    def test_the_cookie_is_asked_before_the_404_and_the_release_list_is_not_touched(self):
        p = src("site", "proxy.ts")
        # session 371's line, word for word (tests/test_session371.py pins it too)
        self.assertIn("if (await cookieOpens(have, token)) return NextResponse.next();", p)
        self.assertLess(p.index("if (await cookieOpens(have, token))"), p.index('new NextResponse("Not found", { status: 404'))
        self.assertIn('import { COOKIE, cookieOpens, exempt, statusOf } from "@/lib/release";', p)
        # the rule lives in the proxy: lib/release.ts still reads any extension as never behind the curtain
        self.assertIn("|| /\\.[a-z0-9]+$/i.test(path);", src("site", "lib", "release.ts"))

    def test_no_em_or_en_dash(self):
        for parts in (("site", "proxy.ts"), ("site", "scripts", "test-curtain.mjs"), ("site", "scripts", "check-curtain.mjs"),
                      ("docs", "reviews", "security-faults-2026-11-13.md")):
            t = src(*parts)
            self.assertNotIn("—", t, parts)
            self.assertNotIn("–", t, parts)


class TheDeployedCheck(unittest.TestCase):
    """check-curtain.mjs reads a deployed site; here its three functions are given canned answers."""

    def run_js(self, code):
        r = subprocess.run([node(), "--no-warnings", "--input-type=module", "-e", code], cwd=SITE, capture_output=True, text=True, timeout=60)
        self.assertEqual(r.returncode, 0, r.stderr[-2000:])
        return json.loads(r.stdout)

    def test_the_addresses_read_for_a_page(self):
        out = self.run_js('import { transportOf } from "./scripts/check-curtain.mjs"; console.log(JSON.stringify([transportOf("/about"), transportOf("/")]));')
        self.assertEqual(out[0], ["/about.rsc", "/about.segments/_tree.segment.rsc", "/about.segments/_full.segment.rsc", "/about.segments/about/__PAGE__.segment.rsc"])
        self.assertEqual(out[1][0], "/index.rsc")
        self.assertEqual(out[1][3], "/index.segments/index/__PAGE__.segment.rsc")

    def test_the_answers_of_13_november_fail_and_the_fixed_ones_pass(self):
        code = '''
import { reading, verdict } from "./scripts/check-curtain.mjs";
// production on 13 November 2026, as a visitor (runs/s5101 of session 5101)
const before = [
  { address: "/about.rsc", status: 200, matched: "/in-review" },
  { address: "/about.segments/_tree.segment.rsc", status: 200, matched: "/about.segments/_tree.segment.rsc" },
  { address: "/about.segments/_full.segment.rsc", status: 200, matched: "/about.segments/_full.segment.rsc" },
  { address: "/about.segments/about/__PAGE__.segment.rsc", status: 200, matched: "/about.segments/about/__PAGE__.segment.rsc" },
].map((a) => ({ ...a, reading: reading(a) }));
const after = before.map((a, i) => (i === 0 ? a : { ...a, status: 404, matched: null })).map((a) => ({ ...a, reading: reading(a) }));
const own = reading({ status: 200, matched: "/in-review" });
console.log(JSON.stringify({
  own,
  before: verdict(own, before), after: verdict(own, after),
  live: verdict(reading({ status: 200, matched: "/about" }), before),
  nameless: reading({ status: 200, matched: null, body: '0:{"q":"?path=%2Fabout"}' }),
  namelessPage: reading({ status: 200, matched: null, body: "the page itself" }),
}));
'''
        out = self.run_js(code)
        self.assertEqual(out["own"], "curtain")
        self.assertFalse(out["before"]["ok"])
        self.assertEqual(out["before"]["open"], ["/about.segments/_tree.segment.rsc", "/about.segments/_full.segment.rsc", "/about.segments/about/__PAGE__.segment.rsc"])
        self.assertTrue(out["after"]["ok"])
        self.assertEqual(out["after"]["open"], [])
        self.assertTrue(out["live"]["live"])
        self.assertEqual(out["nameless"], "curtain")
        self.assertEqual(out["namelessPage"], "page")

    def test_no_request_without_an_origin(self):
        r = subprocess.run([node(), "--no-warnings", "scripts/check-curtain.mjs"], cwd=SITE, capture_output=True, text=True, timeout=60)
        self.assertEqual(r.returncode, 2)
        self.assertIn("usage:", r.stderr)


if __name__ == "__main__":
    unittest.main()

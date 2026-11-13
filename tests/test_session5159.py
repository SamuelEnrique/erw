"""Session 5159: the fresh pass of the security review, the headers and the internal view
(docs/reviews/security-faults-2026-11-13.md, row 27 and what was read again).

Energy Research Warehouse (ERW). No network, no model, no build: the configuration is evaluated by node with a
stand-in for the environment, and the source is read.

    row 27   the policy lets a browser connect to this site's own Supabase project, not to every project
    read     every page and route handler of the internal view asks for the internal cookie (or is one of the three
             doors), a page answers 404 without it and is never indexed

    python -m unittest tests.test_session5159 -v
"""

import json
import os
import re
import shutil
import subprocess
import unittest

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
SITE = os.path.join(ROOT, "site")
APP = os.path.join(SITE, "app")


def src(*parts):
    with open(os.path.join(ROOT, *parts), encoding="utf-8") as f:
        return f.read()


def policy(supabase_url):
    """The enforced policy as site/next.config.ts writes it when SUPABASE_URL is `supabase_url` (None: not set)."""
    node = shutil.which("node")
    if not node:
        raise unittest.SkipTest("node is not on the path")
    env = {k: v for k, v in os.environ.items() if k != "SUPABASE_URL"}
    if supabase_url is not None:
        env["SUPABASE_URL"] = supabase_url
    code = ('const cfg = (await import("./next.config.ts")).default; const h = await cfg.headers();'
            'console.log(JSON.stringify(h.find((r) => r.source === "/:path*").headers.find((x) => x.key === "Content-Security-Policy").value));')
    r = subprocess.run([node, "--no-warnings", "--import", "./scripts/alias-register.mjs", "--input-type=module", "-e", code],
                       cwd=SITE, capture_output=True, text=True, timeout=120, env=env)
    if r.returncode != 0:
        raise AssertionError(r.stderr[-2000:])
    return dict((d.split(" ", 1) + [""])[:2] for d in json.loads(r.stdout).split("; "))


class TheBrowserConnectsToThisSitesProjectOnly(unittest.TestCase):
    def test_the_projects_own_origin_is_named(self):
        for given in ("https://abcdefghijklmnop.supabase.co", "https://abcdefghijklmnop.supabase.co/", "https://abcdefghijklmnop.supabase.co/rest/v1/"):
            self.assertEqual(policy(given)["connect-src"], "'self' https://abcdefghijklmnop.supabase.co", given)

    def test_without_the_variable_the_wider_name_stands(self):
        self.assertEqual(policy(None)["connect-src"], "'self' https://*.supabase.co")
        self.assertEqual(policy("")["connect-src"], "'self' https://*.supabase.co")

    def test_an_address_that_is_no_supabase_project_is_never_written_into_the_policy(self):
        for given in ("not an address", "http://abcdefghijklmnop.supabase.co", "https://example.com", "https://supabase.co.example.com",
                      "https://abc.supabase.co.evil.example", "https://abc.supabase.co:8443", "https://a b.supabase.co", "https://*.example.com; script-src *"):
            csp = policy(given)
            self.assertEqual(csp["connect-src"], "'self' https://*.supabase.co", given)
            self.assertEqual(csp["script-src"], "'self' 'unsafe-inline' https://cdnjs.cloudflare.com", given)

    def test_nothing_else_of_the_policy_moves_with_the_variable(self):
        a, b = policy(None), policy("https://abcdefghijklmnop.supabase.co")
        self.assertEqual({k: v for k, v in a.items() if k != "connect-src"}, {k: v for k, v in b.items() if k != "connect-src"})
        self.assertEqual(list(a), list(b))


GUARDS = ("internalOk(", "internalOpen(", "cookieOpens(")
# The three doors of the internal view: the form, its target, and the lock. None shows anything of the internal view.
DOORS = {"/internal/open/page.tsx", "/internal/unlock/route.ts", "/internal/lock/route.ts"}


class TheInternalView(unittest.TestCase):
    def files(self):
        out = []
        for base, _dirs, names in os.walk(os.path.join(APP, "internal")):
            out += [os.path.join(base, n) for n in names if n in ("page.tsx", "route.ts")]
        return sorted(out)

    def name(self, f):
        return "/" + os.path.relpath(f, APP).replace(os.sep, "/")

    def test_every_page_and_route_asks_for_the_cookie_or_is_a_door(self):
        files = self.files()
        self.assertGreaterEqual(len(files), 14)
        seen_doors = set()
        for f in files:
            t, name = open(f, encoding="utf-8").read(), self.name(f)
            if name in DOORS:
                seen_doors.add(name)
                continue
            self.assertTrue(any(g in t for g in GUARDS), f"{name}: an internal address that does not ask for the internal cookie")
        self.assertEqual(seen_doors, DOORS)

    def test_a_page_answers_404_without_it_and_is_never_indexed(self):
        for f in self.files():
            t, name = open(f, encoding="utf-8").read(), self.name(f)
            if not f.endswith("page.tsx"):
                continue
            self.assertRegex(t, r"robots:\s*\{\s*index:\s*false,\s*follow:\s*false\s*\}", name)
            if name not in DOORS:
                self.assertIn("notFound()", t, name)
                self.assertIn('dynamic = "force-dynamic"', t, name)

    def test_a_route_that_changes_something_names_its_origin(self):
        for f in self.files():
            t, name = open(f, encoding="utf-8").read(), self.name(f)
            if f.endswith("route.ts") and re.search(r"export (?:async )?function POST\b", t):
                self.assertIn("sameOrigin(", t, name)

    def test_the_cookie_is_compared_in_constant_time_in_both_places(self):
        for parts, fn in ((("site", "lib", "release.ts"), "cookieOpens"), (("site", "lib", "thesis", "server.ts"), "internalOk")):
            t = src(*parts)
            body = t[t.index(f"export async function {fn}("):]
            body = body[:body.index("\n}")]
            self.assertIn("if (have.length !== want.length) return false;", body, fn)
            self.assertIn("d |= have.charCodeAt(i) ^ want.charCodeAt(i);", body, fn)
            self.assertNotRegex(body, r"have\s*[!=]==\s*want\b", fn)

    def test_the_configuration_hides_every_internal_address(self):
        c = src("site", "next.config.ts")
        rule = c[c.index('source: "/internal/:path*"'):]
        rule = rule[:rule.index("]")]
        for want in ('"Cache-Control", value: "private, no-store"', '"X-Robots-Tag", value: "noindex"', '"Referrer-Policy", value: "no-referrer"'):
            self.assertIn(want, rule)


class TheRecords(unittest.TestCase):
    def test_the_list(self):
        row = [line for line in src("docs", "reviews", "security-faults-2026-11-13.md").splitlines() if line.startswith("| 27 |")]
        self.assertEqual(len(row), 1)
        self.assertIn("**fixed**", row[0])
        self.assertIn("tests/test_session5159.py", row[0])

    def test_no_em_or_en_dash(self):
        for parts in (("tests", "test_session5159.py"), ("site", "next.config.ts")):
            t = src(*parts)
            self.assertNotIn(chr(0x2014), t, parts)
            self.assertNotIn(chr(0x2013), t, parts)


if __name__ == "__main__":
    unittest.main()

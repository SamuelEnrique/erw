"""Session 1501 (chain 158): security, the headers and the internal routes. The report-only policy is dropped (M4, due on
or after 26 October 2026), the enforced policy the one header; every internal route answers only the internal view's
cookie (404 otherwise), but the three doors (open, unlock, lock); the cookie is httpOnly, same-site, secure on https,
90 days (L4 stays the owner's: a fixed digest).

No network, no build, no model. Nothing here sets the environment at import.
"""
import os
import re
import unittest

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
INTERNAL = os.path.join(ROOT, "site", "app", "internal")
DOORS = {"open/page.tsx", "unlock/route.ts", "lock/route.ts"}


def src(*parts):
    with open(os.path.join(ROOT, *parts), encoding="utf-8") as f:
        return f.read()


class TheHeaders(unittest.TestCase):
    def test_one_policy_enforced(self):
        c = src("site", "next.config.ts")
        headers = c.split("const SECURITY_HEADERS")[1].split("];")[0]
        self.assertIn('{ key: "Content-Security-Policy", value: CSP_ENFORCED },', headers)
        self.assertNotIn("Report-Only", headers)
        for k in ("Strict-Transport-Security", "X-Content-Type-Options", "X-Frame-Options", "Referrer-Policy", "Permissions-Policy"):
            self.assertIn(f'"{k}"', headers)

    def test_the_security_check_wants_no_report_only_header(self):
        self.assertIn('h("content-security-policy-report-only") === ""', src("site", "scripts", "check-security.mjs"))


class TheInternalRoutes(unittest.TestCase):
    def test_every_internal_route_is_guarded_or_a_door(self):
        found = []
        for d, _, files in os.walk(INTERNAL):
            for f in files:
                if f in ("route.ts", "page.tsx"):
                    rel = os.path.relpath(os.path.join(d, f), INTERNAL).replace(os.sep, "/")
                    found.append(rel)
                    if rel in DOORS:
                        continue
                    t = src("site", "app", "internal", *rel.split("/"))
                    self.assertRegex(t, r"cookieOpens|internalOk|internalView|isInternal", rel)
        self.assertGreaterEqual(len(found), 14)
        self.assertTrue(DOORS <= set(found))

    def test_the_proxy_leaves_the_internal_routes_to_their_own_guard(self):
        self.assertIn("internal/", src("site", "proxy.ts").split("matcher:")[1])

    def test_the_cookie(self):
        t = src("site", "app", "internal", "unlock", "route.ts")
        self.assertIn('res.cookies.set(COOKIE, await digest(token), { httpOnly: true, secure, sameSite: "lax", path: "/", maxAge: MAX_AGE });', t)
        self.assertIn("export const MAX_AGE = 90 * 24 * 3600;", src("site", "lib", "release.ts"))


if __name__ == "__main__":
    unittest.main()

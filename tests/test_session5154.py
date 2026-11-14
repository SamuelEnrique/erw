"""Session 5154: row 23 of the security list (docs/reviews/security-faults-2026-11-13.md): the usage count's daily code
is an identifier for a day, and the roadmap's item 7 says "no identifier".

Energy Research Warehouse (ERW). No network, no model, no build: the source is read (the behaviour itself is tested by
site/scripts/test-usage.mjs, which tests/test_session5102.py runs).

    the default is unchanged: the daily code, as since session 177
    USAGE_VISITORS=off: the route sends a value made of the page's path alone; the address and the user agent are not
    read for the count
    the count sets no cookie and reads none but the internal view's, keeps nothing in the browser, and sends a path
    without its query

    python -m unittest tests.test_session5154 -v
"""

import os
import re
import unittest

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))


def src(*parts):
    with open(os.path.join(ROOT, *parts), encoding="utf-8") as f:
        return f.read()


def code(text):
    """The text without its comments, line by line (session 5169: a comment of several lines is one whose first line
    begins with its opening mark; a slash and a star inside a string no longer take code out with them)."""
    out, inside = [], False
    for line in text.splitlines():
        s = line.strip()
        if inside:
            inside = "*/" not in s
            continue
        if s.startswith(("/*", "{/*")):
            if "*/" not in s:
                inside = True
                continue
            line = line.split("*/", 1)[1]
        line = re.sub(r"\{/\*.*?\*/\}", "", line)
        out.append(re.sub(r"(^|\s)//.*$", "", line))
    return "\n".join(out)


class TheSwitch(unittest.TestCase):
    def test_the_guard_has_the_switch_and_the_value_of_nobody(self):
        g = src("site", "lib", "guard.ts")
        self.assertIn('return (env.USAGE_VISITORS ?? "").trim().toLowerCase() === "off";', g)
        nobody = g[g.index("export function usageNobody("):]
        nobody = nobody[:nobody.index("\n}")]
        self.assertIn("export function usageNobody(path: string, secret: string): string", nobody)
        self.assertIn("erw-usage-nobody", nobody)
        for word in ("ip", "ua", "req", "headers"):
            self.assertNotRegex(nobody, rf"\b{word}\b", f"the value of nobody reads {word}")

    def test_the_route_reads_the_address_for_the_count_only_when_visitors_are_counted(self):
        r = src("site", "app", "api", "usage", "route.ts")
        self.assertIn('const visitor = usageVisitorsOff() ? usageNobody(path, secret) : usageVisitor(ip, req.headers.get("user-agent") ?? "", secret);', r)
        self.assertIn("p_visitor: visitor }", r)
        self.assertEqual(code(r).count("usageVisitor("), 1)
        # the order: refused requests first, the limit, then the count
        self.assertLess(r.index('req.headers.get("dnt") === "1"'), r.index("await req.text()"))
        self.assertLess(r.index('limited(req, "usage", 600, 3600)'), r.index('rpc("site_usage_record"'))

    def test_the_node_test_covers_the_switch(self):
        t = src("site", "scripts", "test-usage.mjs")
        self.assertIn('guard.usageVisitorsOff({ USAGE_VISITORS: "off" }), true', t)
        self.assertIn("guard.usageVisitorsOff({}), false", t)
        self.assertIn('guard.usageNobody("/storage", SALT)', t)


class NoCookieNoStorage(unittest.TestCase):
    """The half of "no cookie and no identifier" that holds whatever the ruling on row 23."""

    def test_the_route_sets_no_cookie(self):
        r = code(src("site", "app", "api", "usage", "route.ts"))
        self.assertNotRegex(r, r"Set-Cookie|cookies\(\)\.set|\.cookies\.set")
        # the one cookie it reads is the internal view's, to name a page in review "opened" for a reviewer
        self.assertEqual(re.findall(r"cookieOf\(req, (\w+)\)", r), ["COOKIE"])

    def test_the_browser_side_keeps_nothing_and_sends_no_query(self):
        for parts in (("site", "components", "Usage.tsx"), ("site", "lib", "usage.ts")):
            t = code(src(*parts))
            for word in ("document.cookie", "localStorage", "sessionStorage", "indexedDB", "navigator.userAgent", "document.referrer", "location.search", "location.href"):
                self.assertNotIn(word, t, f"{'/'.join(parts)} names {word}")
        u = code(src("site", "lib", "usage.ts"))
        self.assertIn("location.pathname", u)

    def test_the_database_keeps_counts_only_of_an_earlier_day(self):
        m = src("warehouse", "supabase", "migrations", "028_security_usage.sql")
        daily = m[m.index("create table if not exists public.site_usage_daily"):]
        daily = daily[:daily.index(");")]
        self.assertNotIn("visitor ", daily)          # no code in the table of earlier days
        self.assertIn("visitors integer", daily)     # a number


class TheRecords(unittest.TestCase):
    def test_the_method_note_and_the_list(self):
        n = src("docs", "methods", "usage_counts.md")
        self.assertIn("## Counting with no code at all", n)
        self.assertIn("USAGE_VISITORS=off", n)
        row = [line for line in src("docs", "reviews", "security-faults-2026-11-13.md").splitlines() if line.startswith("| 23 |")]
        self.assertEqual(len(row), 1)
        self.assertIn("**ruling**", row[0])
        self.assertIn("USAGE_VISITORS=off", row[0])

    def test_no_em_or_en_dash(self):
        for parts in (("tests", "test_session5154.py"), ("site", "lib", "guard.ts"), ("site", "app", "api", "usage", "route.ts"), ("docs", "methods", "usage_counts.md")):
            t = src(*parts)
            self.assertNotIn(chr(0x2014), t, parts)
            self.assertNotIn(chr(0x2013), t, parts)


if __name__ == "__main__":
    unittest.main()

"""Session 5160: the fresh pass of the security review, input limits and rate limits, route by route
(docs/reviews/security-faults-2026-11-13.md, "The fresh pass", rows 29 and 30).

Energy Research Warehouse (ERW). No network, no model, no build: the source is read.

tests/test_session5102.py holds the bodies (a body is never read without a cap; every POST asks the guard). This holds
the other way a request brings words in: the address. Every route handler that reads the address is in the list below
with the line that bounds what it reads; a handler that starts to read the address, or loses its bound, fails here
until it is read and listed.

    python -m unittest tests.test_session5160 -v
"""

import os
import re
import unittest

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
SITE = os.path.join(ROOT, "site")
APP = os.path.join(SITE, "app")


def src(*parts):
    with open(os.path.join(ROOT, *parts), encoding="utf-8") as f:
        return f.read()


def routes():
    out = []
    for base, dirs, names in os.walk(APP):
        dirs[:] = [d for d in dirs if d != "_retired"]
        if "route.ts" in names:
            out.append(os.path.join(base, "route.ts"))
    return sorted(out)


def rel(f):
    return os.path.relpath(f, SITE).replace(os.sep, "/")


TOOLS = "the tool's own parsers (window P1's file on 13 November 2026; read, not pinned word by word)"
# route handler -> the lines that bound what it reads from the address (each must be in the file), or a note
READS_THE_ADDRESS = {
    "app/api/analysis/route.ts": ["if (!/^[A-Za-z0-9-]{6,60}$/.test(id)) return json({ request: null, reason: \"no such request\" }, 400);"],
    "app/api/download/route.ts": ['if (!/^[a-z0-9_]{3,64}$/.test(table)) return text("table must be an ERW table name", 400);', "downloadFilter(shape as Shape, {"],
    "app/api/entity/route.ts": ["if (!TABLES.has(table) || !id || id.length > 200) {"],
    "app/api/play/top/route.ts": ["if (!parsePreset(preset)) return fail(", "level = await levelFor(date);"],
    "app/api/subscribe/confirm/route.ts": ['if (!email || email.length > 254 || !/^[^@\\s]+@[^@\\s]+\\.[^@\\s]+$/.test(email) || !/^[0-9a-f]{64}$/.test(token)) return back("badlink");'],
    "app/api/thesis/run/route.ts": ['if (!RUN_ID.test(id)) return json({ status: null, note: "" }, 404);'],
    "app/api/unsubscribe/route.ts": ['if (!email || email.length > 254 || !/^[^@\\s]+@[^@\\s]+\\.[^@\\s]+$/.test(email) || !/^[0-9a-f]{64}$/.test(token)) return "badlink";'],
    "app/companies/rows/route.ts": ["const q = queryOf(Object.fromEntries(u.searchParams.entries()), ix);"],
    "app/cost-of-power/battery/months.csv/route.ts": TOOLS,
    "app/cost-of-power/months.csv/route.ts": TOOLS,
    "app/cost-of-power/seller/months.csv/route.ts": TOOLS,
    "app/cost-of-power/seller/tables.csv/route.ts": TOOLS,
    "app/cost-of-power/tables.csv/route.ts": TOOLS,
    "app/internal/findings/file/route.ts": ["if (!ID.test(id) || !FILE_NAME.test(name) || !name.startsWith(id) || !type) return hidden();"],
    "app/internal/unlock/route.ts": "the old link's token, or nothing once the link is retired (rows 3 and 4); the form's door reads the body, capped at 2,000 characters",
    "app/severance/finder/download/route.ts": "the internal token, or nothing once the link is retired (rows 3 and 4)",
}
ADDRESS = re.compile(r"searchParams|nextUrl\.search\b|\.search\b(?!Params)|req\.url\b[^)]*\)\.(?:search|hash)")


class EveryWordFromTheAddressIsBounded(unittest.TestCase):
    def test_the_handlers_that_read_the_address_are_the_listed_ones(self):
        reads = sorted(rel(f) for f in routes() if re.search(r"searchParams", open(f, encoding="utf-8").read()))
        listed = sorted(k for k in READS_THE_ADDRESS)
        # a listed handler may stop reading the address (the retirement of the old link does that to two): that is no failure
        self.assertEqual([r for r in reads if r not in listed], [], "a route handler now reads the address: bound what it reads and list it in READS_THE_ADDRESS")
        for name in listed:
            self.assertTrue(os.path.exists(os.path.join(SITE, *name.split("/"))), name)

    def test_each_bound_is_in_its_file(self):
        for name, bounds in READS_THE_ADDRESS.items():
            if isinstance(bounds, str):
                continue
            t = src("site", *name.split("/"))
            for line in bounds:
                self.assertIn(line, t, f"{name}: the line that bounded what it reads from the address is gone")

    def test_the_bound_comes_before_the_database_is_asked(self):
        e = src("site", "app", "api", "entity", "route.ts")
        self.assertLess(e.index("id.length > 200"), e.index("await entity(table, id)"))
        c = src("site", "app", "api", "subscribe", "confirm", "route.ts")
        self.assertLess(c.index("email.length > 254"), c.index('rpc<boolean>("subscribe_confirm"'))
        d = src("site", "app", "api", "download", "route.ts")
        self.assertLess(d.index("/^[a-z0-9_]{3,64}$/.test(table)"), d.index("downloadFilter(shape as Shape"))

    def test_the_filters_the_download_and_the_companies_list_lean_on(self):
        f = src("site", "lib", "downloadfilter.ts")
        self.assertIn("if (!VALUE.test(v)) return { error:", f)
        self.assertIn("if (t && !TIME.test(t)) return { error:", f)
        q = src("site", "lib", "companydb.ts")
        self.assertIn('q: one("q").slice(0, 80)', q)
        self.assertIn("const pick = (v: string, have: Record<string, number>) => (v in have ? v : \"\");", q)
        lv = src("site", "lib", "levels.ts")
        self.assertIn(r"if (!/^\d{4}-\d{2}-\d{2}$/.test(date)) return null;", lv)

    def test_a_path_segment_is_looked_up_never_used_as_a_path(self):
        # the three handlers with a segment of the address in their path: each looks it up in a list the site holds
        self.assertIn("const meta = SETS.find((s) => s.slug === slug);", src("site", "app", "learn", "problems", "[slug]", "data.csv", "route.ts"))
        self.assertIn("const c = company(id);", src("site", "app", "companies", "[id]", "rows", "route.ts"))
        layer = src("site", "app", "resources", "layer", "[name]", "route.ts")
        self.assertIn('export const dynamic = "force-static";', layer)
        self.assertIn("export function generateStaticParams()", layer)


class EveryLimitHasAName(unittest.TestCase):
    def test_the_limits_as_they_stand(self):
        found = {}
        for f in routes():
            for bucket, limit, window in re.findall(r'limited\(req, "(\w+)", ([\w. /*]+), ([\w. /*]+?)[,)]', open(f, encoding="utf-8").read()):
                found.setdefault(bucket, set()).add((limit.strip(), window.strip()))
        self.assertEqual(sorted(found), ["ask_hour", "confirm", "download", "entity", "findings_state", "pitchbook", "play", "play_top", "subscribe", "subscribe_day", "unlock", "unsubscribe", "usage"],
                         "a limit was added or removed: say so in docs/security.md's list of limits")
        # one name, one limit: two routes that share a bucket share its numbers
        for bucket, pairs in found.items():
            self.assertEqual(len(pairs), 1, bucket)
        # the name is one the database's function takes (migration 028: a lower-case name of 3 to 32 characters)
        for bucket in found:
            self.assertRegex(bucket, r"^[a-z][a-z0-9_]{2,31}$")


class TheRecords(unittest.TestCase):
    def test_the_list(self):
        t = src("docs", "reviews", "security-faults-2026-11-13.md")
        rows = {line.split("|")[1].strip(): line for line in t.splitlines() if re.match(r"^\| \d+ \|", line)}
        self.assertIn("noted", rows["29"])
        self.assertIn("noted", rows["30"])
        self.assertIn("**Session 5160, input limits and rate limits.**", t)

    def test_no_em_or_en_dash(self):
        t = src("tests", "test_session5160.py")
        self.assertNotIn(chr(0x2014), t)
        self.assertNotIn(chr(0x2013), t)


if __name__ == "__main__":
    unittest.main()

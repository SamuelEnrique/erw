"""Session 1502 (chain 158): security, what a visitor can spend and fetch. The Ask route answers only the site's own
pages, counts each visitor's questions by the hour in the database, and asks the database before every model call
whether the day's and the month's ceilings hold; the service key is read only by server-only code and is in no file the browser is sent; the
download route refuses a held table by name, a table not public, and everything outside the internal view until the
owner rules.

No network, no model. The built files are read where this copy holds a build (site/.next), and the test is skipped
otherwise. Nothing here sets the environment at import, and no key is printed.
"""
import os
import re
import unittest

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SITE = os.path.join(ROOT, "site")


def src(*parts):
    with open(os.path.join(ROOT, *parts), encoding="utf-8") as f:
        return f.read()


class TheAskRoute(unittest.TestCase):
    def test_its_guards(self):
        t = src("site", "app", "api", "ask", "route.ts")
        self.assertIn('if (!sameOrigin(req)) return NextResponse.json({ error: "this route answers this site\'s own pages" }, { status: 403 });', t)
        self.assertIn('const hour = await limited(req, "ask_hour", LIMIT, WINDOW_MS / 1000);', t)
        self.assertIn("the spending ceilings and the visitor's daily number, counted by the database", t)
        self.assertIn("export const maxDuration = 120;", t)


class TheServiceKey(unittest.TestCase):
    def test_server_only_in_the_sites_code(self):
        # the key is read by the server's writes (lib/supabase.ts, writeConfig, session 301); a file that names it is a
        # server-only module, and nothing names it for the browser (NEXT_PUBLIC_)
        named = []
        for d, _, files in os.walk(SITE):
            if "node_modules" in d or os.sep + ".next" in d:
                continue
            for f in files:
                if f.endswith((".ts", ".tsx", ".mjs", ".js")):
                    path = os.path.join(d, f)
                    t = open(path, encoding="utf-8", errors="replace").read()
                    self.assertNotIn("NEXT_PUBLIC_SUPABASE_SERVICE", t, path)
                    if "SUPABASE_SERVICE_KEY" in t and os.sep + "scripts" + os.sep not in path:
                        named.append(os.path.relpath(path, SITE))
                        self.assertIn('import "server-only";', t, path)
        self.assertIn(os.path.join("lib", "supabase.ts"), named)

    def test_not_in_the_built_files(self):
        static = os.path.join(SITE, ".next", "static")
        if not os.path.isdir(static):
            raise unittest.SkipTest("no build in this copy")
        key = ""
        for path in (os.path.join(ROOT, ".env"), os.path.join(os.path.dirname(ROOT), "erw", ".env")):
            if os.path.exists(path):
                for ln in open(path, encoding="utf-8"):
                    if ln.startswith("SUPABASE_SERVICE_KEY="):
                        key = ln.split("=", 1)[1].strip().strip('"')
                break
        claim = re.compile(rb"c2VydmljZV9yb2xl|\"role\":\"service_role\"")
        for d, _, files in os.walk(static):
            for f in files:
                b = open(os.path.join(d, f), "rb").read()
                self.assertIsNone(claim.search(b), f)
                if len(key) > 20:
                    self.assertNotIn(key.encode(), b, f"the service key is in {f}")


class TheDownloads(unittest.TestCase):
    def test_the_refusals(self):
        t = src("site", "app", "api", "download", "route.ts")
        self.assertIn('return text("the download is open to the internal view only, until the owner rules whether it is public", 403);', t)
        self.assertIn("if (licenseNeeded(table)) return text(`${table} is held: license needed", t)
        self.assertIn('if (!cat.length || cat[0].license !== "public") return text(`${table} is not a public ERW table`, 404);', t)


if __name__ == "__main__":
    unittest.main()

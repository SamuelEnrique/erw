"""Session 5102: the standing tests of the security list (docs/reviews/security-faults-2026-11-13.md, rows 2 and 15 to 21).

Energy Research Warehouse (ERW). No network, no model, no build: the source is read, and two node tests are run.

    row 2    site/scripts/test-usage.mjs, the review's proof of the guards, runs in the suite (it had failed on main
             unseen, because no test ran it)
    row 15   /internal/lock clears nothing at another site's request
    row 16   the email's two token doors (unsubscribe, confirm) are limited
    row 17   /api/entity is limited
    row 18   /api/play/top is counted by the guard as well as by one instance's memory
    row 19   every route handler that reads a body caps it, never reads it as JSON unseen, and every route that spends,
             writes or asks the database with a visitor's own words asks the guard first
    row 20   no secret can reach a browser: no NEXT_PUBLIC_ variable, no client file names process.env, no module a
             client file imports (at any depth) names a secret, and no literal shaped like a key is in the site's source
    row 21   the headers of site/next.config.ts, read from the config itself, without a build

    python -m unittest tests.test_session5102 -v
"""

import importlib.util
import json
import os
import re
import shutil
import subprocess
import unittest

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
SITE = os.path.join(ROOT, "site")
SOURCE_DIRS = ("app", "lib", "components")
SOURCE_EXT = (".ts", ".tsx")


def src(*parts):
    with open(os.path.join(ROOT, *parts), encoding="utf-8") as f:
        return f.read()


def node():
    n = shutil.which("node")
    if not n:
        raise unittest.SkipTest("node is not on the path")
    return n


def site_files():
    """Every source file of the site a build compiles: app/, lib/, components/, the proxy and the config."""
    out = []
    for d in SOURCE_DIRS:
        for base, _dirs, names in os.walk(os.path.join(SITE, d)):
            out += [os.path.join(base, n) for n in names if n.endswith(SOURCE_EXT)]
    out += [os.path.join(SITE, "proxy.ts"), os.path.join(SITE, "next.config.ts")]
    return sorted(out)


def rel(path):
    return os.path.relpath(path, SITE).replace(os.sep, "/")


def routes():
    return [f for f in site_files() if os.path.basename(f) == "route.ts"]


def methods(text):
    return set(re.findall(r"export (?:async )?function (GET|POST|PUT|PATCH|DELETE)\b", text))


# ----------------------------------------------------------------------------------------------------------------------
# row 2
# ----------------------------------------------------------------------------------------------------------------------
class TheGuardsOwnProof(unittest.TestCase):
    def test_test_usage_runs_and_passes(self):
        r = subprocess.run([node(), "--no-warnings", "--import", "./scripts/alias-register.mjs", "scripts/test-usage.mjs"],
                           cwd=SITE, capture_output=True, text=True, timeout=180)
        self.assertEqual(r.returncode, 0, (r.stdout + r.stderr)[-3000:])
        self.assertRegex(r.stdout, r"\d+ tests passed")

    def test_a_sub_groups_pages_have_their_names(self):
        self.assertIn("[...g.pages, ...(g.sub?.pages ?? [])]", src("site", "lib", "usagepath.ts"))


# ----------------------------------------------------------------------------------------------------------------------
# rows 15 to 18
# ----------------------------------------------------------------------------------------------------------------------
class TheSmallDoors(unittest.TestCase):
    def test_the_lock_clears_nothing_at_another_sites_request(self):
        t = src("site", "app", "internal", "lock", "route.ts")
        refuse = t.index('if (req.headers.get("sec-fetch-site") === "cross-site") return res;')
        self.assertLess(refuse, t.index("res.cookies.set(COOKIE"))
        self.assertLess(refuse, t.index("res.cookies.set(VIEW"))
        # the answer is the same redirect either way, and is never cached
        self.assertLess(t.index('res.headers.set("Cache-Control", "private, no-store");'), refuse)

    def test_the_emails_two_token_doors_are_limited(self):
        u = src("site", "app", "api", "unsubscribe", "route.ts")
        post = u[u.index("export async function POST"):]
        self.assertLess(post.index('limited(req, "unsubscribe", 120, 3600)'), post.index("await req.text()"))
        self.assertIn("status: 429", post)
        # a GET still changes nothing and asks the database nothing (sessions 58 and 59)
        get = u[u.index("export async function GET"):u.index("export async function POST")]
        self.assertNotIn("rpc", get)
        c = src("site", "app", "api", "subscribe", "confirm", "route.ts")
        self.assertLess(c.index('limited(req, "confirm", 60, 3600)'), c.index('rpc<boolean>("subscribe_confirm"'))
        # the form of the link is checked before the limit is counted: a malformed link costs nothing
        self.assertLess(c.index('return back("badlink");'), c.index('limited(req, "confirm"'))

    def test_the_maps_card_is_limited(self):
        e = src("site", "app", "api", "entity", "route.ts")
        self.assertLess(e.index("!TABLES.has(table)"), e.index('limited(req, "entity", 600, 3600)'))
        self.assertLess(e.index('limited(req, "entity", 600, 3600)'), e.index("await entity(table, id)"))

    def test_the_leaderboard_is_counted_by_the_guard_too(self):
        p = src("site", "app", "api", "play", "top", "route.ts")
        self.assertIn('if (!allowRead(clientIp(req)) || !(await limited(req, "play_top", 240, 3600)).ok)', p)


# ----------------------------------------------------------------------------------------------------------------------
# row 19
# ----------------------------------------------------------------------------------------------------------------------
# Routes that take a POST and may be called with no Origin check, with the reason. Every other POST asks sameOrigin.
NO_ORIGIN_CHECK = {
    "app/api/unsubscribe/route.ts": "a mail client's one-click button posts here (RFC 8058); the signed token is the credential",
    "app/api/thesis/pitchbook/route.ts": "the PitchBook stage posts from outside a browser; the run's one-time key is the credential",
}
# Route handlers that answer a GET by asking the database with a parameter the visitor chose: each is limited.
GET_ASKS_DATABASE = ("app/api/entity/route.ts", "app/api/play/top/route.ts", "app/api/subscribe/confirm/route.ts", "app/api/download/route.ts")
# What stands behind a POST: the guard's limit, or the internal view (whose routes count their day in the database).
GUARD = re.compile(r"\blimited\(|\binternalOk\(|\binternalOpen\(")


class EveryRoute(unittest.TestCase):
    def test_there_are_routes_and_the_list_is_read_from_the_tree(self):
        self.assertGreaterEqual(len(routes()), 40)

    def test_a_body_is_never_read_without_a_cap(self):
        for f in routes():
            t = open(f, encoding="utf-8").read()
            name = rel(f)
            # the request's own .json() reads any size and throws on anything else: no route uses it
            self.assertNotRegex(t, r"\breq(?:uest)?\.json\(\)", f"{name}: reads the body with req.json(); read text and cap it")
            self.assertNotRegex(t, r"\breq(?:uest)?\.(?:arrayBuffer|blob)\(\)", name)
            for m in re.finditer(r"(?:const|let)?\s*(\w+)\s*=\s*await req(?:uest)?\.text\(\)", t):
                after = t[m.end():m.end() + 400]
                self.assertRegex(after, rf"\b{m.group(1)}\.length\s*>\s*[A-Z_0-9+ ]+", f"{name}: {m.group(1)} = await req.text() is not followed by a cap on its length")
            if re.search(r"\breq(?:uest)?\.formData\(\)", t):
                before = t[:re.search(r"\breq(?:uest)?\.formData\(\)", t).start()]
                self.assertRegex(before, r'content-length', f"{name}: a form is read with no cap on the request's size")
            if "req.body" in t:
                self.assertIn("MAX_BODY", t, name)

    def test_a_route_reads_a_body_only_if_it_is_listed_here(self):
        reads = sorted(rel(f) for f in routes() if re.search(r"\breq(?:uest)?\.(?:text|formData)\(\)|\breq\.body\b", open(f, encoding="utf-8").read()))
        self.assertEqual(reads, [
            "app/api/analysis/route.ts", "app/api/ask/route.ts", "app/api/play/finish/route.ts", "app/api/play/score/route.ts", "app/api/subscribe/route.ts",
            "app/api/thesis/pitchbook/route.ts", "app/api/thesis/provider/route.ts", "app/api/thesis/run/route.ts", "app/api/unsubscribe/route.ts", "app/api/usage/route.ts",
            "app/internal/findings/state/route.ts", "app/internal/unlock/route.ts",
        ], "a route that reads a body was added or removed: cap it, guard it, and bring this list up to date")

    def test_every_post_asks_the_guard_and_names_its_origin(self):
        posts = [f for f in routes() if "POST" in methods(open(f, encoding="utf-8").read())]
        self.assertGreaterEqual(len(posts), 12)
        for f in posts:
            t, name = open(f, encoding="utf-8").read(), rel(f)
            self.assertRegex(t, GUARD, f"{name}: a POST with neither the guard's limit nor the internal view")
            if name in NO_ORIGIN_CHECK:
                self.assertNotIn("sameOrigin(", t, f"{name} now checks its origin: take it off NO_ORIGIN_CHECK")
            else:
                self.assertIn("sameOrigin(", t, f"{name}: a POST that another site's page could send")
        for name in NO_ORIGIN_CHECK:
            self.assertTrue(os.path.exists(os.path.join(SITE, name)), name)

    def test_only_get_and_post(self):
        for f in routes():
            self.assertLessEqual(methods(open(f, encoding="utf-8").read()), {"GET", "POST"}, rel(f))

    def test_a_get_that_asks_the_database_with_the_visitors_words_is_limited(self):
        for name in GET_ASKS_DATABASE:
            self.assertIn("limited(", src("site", *name.split("/")), name)

    def test_the_sign_up_form_is_capped_before_it_is_read(self):
        t = src("site", "app", "api", "subscribe", "route.ts")
        self.assertLess(t.index('req.headers.get("content-length")'), t.index("await req.formData()"))


# ----------------------------------------------------------------------------------------------------------------------
# row 20
# ----------------------------------------------------------------------------------------------------------------------
SECRET_NAME = re.compile(r"process\.env\.([A-Z0-9_]*(?:KEY|TOKEN|SECRET|SALT|PASSWORD|DSN)[A-Z0-9_]*)")
IMPORT = re.compile(r"""(?:^|\n)\s*(?:import|export)\s+(?!type\b)(?:[^'";]*?\sfrom\s+)?['"]([^'"]+)['"]|\bimport\(\s*['"]([^'"]+)['"]\s*\)""")


def resolve(spec, importer):
    if spec.startswith("@/"):
        base = os.path.join(SITE, *spec[2:].split("/"))
    elif spec.startswith("."):
        base = os.path.normpath(os.path.join(os.path.dirname(importer), *spec.split("/")))
    else:
        return None                                   # a package: not the site's own source
    for cand in (base, base + ".ts", base + ".tsx", os.path.join(base, "index.ts"), os.path.join(base, "index.tsx")):
        if os.path.isfile(cand) and cand.endswith(SOURCE_EXT):
            return cand
    return None


def reach(start):
    """Every source file of the site that `start` imports, at any depth (type-only imports left out)."""
    seen, todo = {}, [(start, None)]
    while todo:
        f, via = todo.pop()
        if f in seen:
            continue
        seen[f] = via
        t = open(f, encoding="utf-8").read()
        for m in IMPORT.finditer(t):
            got = resolve(m.group(1) or m.group(2), f)
            if got and got not in seen:
                todo.append((got, f))
    return seen


class NoSecretReachesABrowser(unittest.TestCase):
    def clients(self):
        return [f for f in site_files() if re.match(r"""\s*(?://[^\n]*\n\s*)*['"]use client['"]""", open(f, encoding="utf-8").read())]

    def test_no_public_variable_exists(self):
        for f in site_files():
            for line in open(f, encoding="utf-8").read().splitlines():
                if "NEXT_PUBLIC_" in line:
                    self.assertTrue(line.lstrip().startswith("//") or line.lstrip().startswith("*"), f"{rel(f)}: {line.strip()[:120]}")

    def test_no_client_file_names_the_environment(self):
        clients = self.clients()
        self.assertGreaterEqual(len(clients), 20, "the scan found too few client files to mean anything")
        for f in clients:
            self.assertNotIn("process.env", open(f, encoding="utf-8").read(), rel(f))

    def test_no_module_a_client_file_imports_names_a_secret(self):
        for c in self.clients():
            for f, via in reach(c).items():
                t = open(f, encoding="utf-8").read()
                m = SECRET_NAME.search(t)
                self.assertIsNone(m, f"{rel(c)} imports {rel(f)}{' (through ' + rel(via) + ')' if via else ''}, which reads {m.group(1) if m else ''}")
                self.assertNotRegex(t, r"""import\s+['"]server-only['"]""", f"{rel(c)} imports {rel(f)}, which is marked server-only")

    # A module that reads a secret and does not carry the marker yet, with whose it is. Row 26 of the list.
    UNMARKED = {"app/cost-of-power/battery/read.ts": "the battery page's read, window P1's file on 13 November 2026: one line, import \"server-only\""}

    def test_every_module_that_reads_a_secret_is_server_only_or_a_server_entry(self):
        # a route handler, a page, a layout and the proxy run on the server alone; any other module that reads a secret
        # says so with the marker, so a client import of it fails the build
        marker = r"""import\s+['"]server-only['"]"""
        for f in site_files():
            t = open(f, encoding="utf-8").read()
            if not SECRET_NAME.search(t):
                continue
            base = os.path.basename(f)
            entry = base in ("route.ts", "page.tsx", "layout.tsx", "proxy.ts", "next.config.ts")
            if entry:
                continue
            if rel(f) in self.UNMARKED:
                self.assertNotRegex(t, marker, f"{rel(f)} carries the marker now: take it off UNMARKED")
                continue
            self.assertRegex(t, marker, f"{rel(f)} reads {SECRET_NAME.search(t).group(1)} and is not marked server-only")
        for name in self.UNMARKED:
            self.assertTrue(os.path.exists(os.path.join(SITE, name)), name)

    def test_no_literal_shaped_like_a_key_in_the_sites_source(self):
        spec = importlib.util.spec_from_file_location("scan_git_secrets", os.path.join(ROOT, "scripts", "scan_git_secrets.py"))
        scan = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(scan)
        kinds = [(k, p) for k, p in scan.PATTERNS if k != "named_literal"]
        self.assertGreaterEqual(len(kinds), 9)
        for f in site_files():
            t = open(f, encoding="utf-8").read()
            for kind, pat in kinds:
                self.assertIsNone(pat.search(t), f"{rel(f)} holds text shaped like a {kind}")


# ----------------------------------------------------------------------------------------------------------------------
# row 21
# ----------------------------------------------------------------------------------------------------------------------
class TheHeaders(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        code = ('const cfg = (await import("./next.config.ts")).default;'
                'console.log(JSON.stringify({ headers: await cfg.headers(), powered: cfg.poweredByHeader ?? null }));')
        # session 5159 (row 27): the policy names this site's own Supabase project when SUPABASE_URL is set; these tests
        # read the configuration without it, whatever the machine's environment holds (tests/test_session5159.py reads it with)
        env = {k: v for k, v in os.environ.items() if k != "SUPABASE_URL"}
        r = subprocess.run([node(), "--no-warnings", "--import", "./scripts/alias-register.mjs", "--input-type=module", "-e", code],
                           cwd=SITE, capture_output=True, text=True, timeout=120, env=env)
        if r.returncode != 0:
            raise AssertionError(r.stderr[-2000:])
        cls.rules = json.loads(r.stdout)["headers"]

    def of(self, source):
        hit = [r for r in self.rules if r["source"] == source]
        self.assertEqual(len(hit), 1, source)
        return {h["key"]: h["value"] for h in hit[0]["headers"]}

    def test_every_answer_carries_the_six(self):
        h = self.of("/:path*")
        self.assertEqual(h["Strict-Transport-Security"], "max-age=63072000; includeSubDomains; preload")
        self.assertEqual(h["X-Content-Type-Options"], "nosniff")
        self.assertEqual(h["X-Frame-Options"], "DENY")
        self.assertEqual(h["Referrer-Policy"], "strict-origin-when-cross-origin")
        for off in ("camera=()", "microphone=()", "geolocation=()", "payment=()"):
            self.assertIn(off, h["Permissions-Policy"])
        self.assertIn("Content-Security-Policy", h)
        self.assertNotIn("Content-Security-Policy-Report-Only", h)          # session 1501

    def test_the_policy_enforced(self):
        csp = dict((d.split(" ", 1) + [""])[:2] for d in self.of("/:path*")["Content-Security-Policy"].split("; "))
        self.assertEqual(csp["default-src"], "'self'")
        for name, value in (("base-uri", "'self'"), ("object-src", "'none'"), ("frame-ancestors", "'none'"), ("form-action", "'self'"), ("frame-src", "'none'")):
            self.assertEqual(csp[name], value, name)
        for name, value in csp.items():
            self.assertNotIn("'unsafe-eval'", value, name)
            self.assertNotRegex(value, r"(?<![\w.])\*(?![\w.])", f"{name} allows any host")
            self.assertNotRegex(value, r"\bhttp:", f"{name} allows a host without TLS")
        # another host is named in two directives only: the chart library's, and the database's storage
        outside = {name: re.findall(r"https://\S+", value) for name, value in csp.items() if "https://" in value}
        self.assertEqual(set(outside), {"script-src", "connect-src"})
        self.assertEqual(outside["connect-src"], ["https://*.supabase.co"])
        self.assertEqual(len(outside["script-src"]), 1)
        self.assertTrue(outside["script-src"][0].startswith("https://cdnjs.cloudflare.com"))

    def test_the_internal_addresses_are_never_cached_indexed_or_named_to_another_site(self):
        h = self.of("/internal/:path*")
        self.assertEqual(h["Referrer-Policy"], "no-referrer")
        self.assertEqual(h["Cache-Control"], "private, no-store")
        self.assertEqual(h["X-Robots-Tag"], "noindex")
        self.assertEqual(self.of("/internal/open"), {"Referrer-Policy": "same-origin"})
        # the general rule comes first, so the internal one overrides it
        order = [r["source"] for r in self.rules]
        self.assertLess(order.index("/:path*"), order.index("/internal/:path*"))
        self.assertLess(order.index("/internal/:path*"), order.index("/internal/open"))


class NoDash(unittest.TestCase):
    def test_no_em_or_en_dash(self):
        for parts in (("tests", "test_session5102.py"), ("site", "app", "internal", "lock", "route.ts"), ("site", "app", "api", "unsubscribe", "route.ts"),
                      ("site", "app", "api", "subscribe", "confirm", "route.ts"), ("site", "app", "api", "entity", "route.ts"), ("site", "app", "api", "play", "top", "route.ts"),
                      ("site", "app", "api", "subscribe", "route.ts"), ("site", "lib", "usagepath.ts")):
            t = src(*parts)
            self.assertNotIn(chr(0x2014), t, parts)
            self.assertNotIn(chr(0x2013), t, parts)


if __name__ == "__main__":
    unittest.main()

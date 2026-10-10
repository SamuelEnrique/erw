"""Session 177: the security audit's fixes and the usage counts.

What is held here, without a network and without a database: verify_rls.py reads PostgREST's answers as it says and
its expected list is whole; the history scan finds each kind of secret and never writes a value; migration 028 and its
rollback hold what the audit asked (and the rollback is where apply.py's full run cannot reach it); the site's routes
carry their guards; the security headers are in next.config.ts; the usage counts send no identifier; and what /privacy
and /terms say matches the code. The site's own rules (the guards, the limit, the paths) are tested by
site/scripts/test-usage.mjs.
"""
import importlib.util
import os
import re
import sys
import unittest

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


def src(*parts):
    with open(os.path.join(ROOT, *parts), encoding="utf-8") as f:
        return f.read()


def load(name, *parts):
    """A script by its path, under a name of its own (the whole suite runs in one process: the first import wins)."""
    spec = importlib.util.spec_from_file_location(name, os.path.join(ROOT, *parts))
    m = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(m)
    return m


class VerifyRls(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.v = load("s177_verify_rls", "warehouse", "supabase", "verify_rls.py")

    def test_classify(self):
        c = self.v.classify
        self.assertEqual(c(200, "[]"), "public")
        self.assertEqual(c(401, '{"code":"42501","message":"permission denied for table site_api_calls"}'), "blocked")
        self.assertEqual(c(403, '{"code":"42501"}'), "blocked")
        self.assertEqual(c(404, '{"code":"PGRST205","message":"Could not find the table"}'), "absent")
        self.assertEqual(c(404, '{"code":"PGRST202"}'), "absent")
        self.assertEqual(c(500, '{"code":"57014","message":"canceling statement due to statement timeout"}'), "error")
        self.assertEqual(c(500, "not json"), "error")

    def test_compare(self):
        expected = {"series": "public", "subscribers": "blocked", "site_usage_salt": "blocked"}
        self.assertEqual(self.v.compare(expected, {"series": "public", "subscribers": "blocked", "site_usage_salt": "blocked"}), [])
        self.assertEqual(self.v.compare(expected, {"series": "blocked", "subscribers": "public", "site_usage_salt": "blocked"}),
                         [("series", "public", "blocked"), ("subscribers", "blocked", "public")])
        # before the migration its tables may be absent, and only then
        seen = {"series": "public", "subscribers": "blocked", "site_usage_salt": "absent"}
        self.assertEqual(self.v.compare(expected, seen), [("site_usage_salt", "blocked", "absent")])
        self.assertEqual(self.v.compare(expected, seen, ("site_usage_salt",)), [])
        self.assertEqual(self.v.compare({"x": "public"}, {}), [("x", "public", "not asked")])

    def test_the_expected_list(self):
        e = self.v.EXPECTED
        public = sorted(t for t, w in e.items() if w == "public")
        self.assertEqual(public, ["catalogue", "entities", "events", "game_scores", "headers", "latest_prices", "series", "sources"])
        for t in ("subscribers", "site_api_calls", "site_ask_counts", "game_plays", "thesis_runs", "analysis_requests", "erw_health",
                  "erw_locks", "email_suppressions", "digest_sends", "thesis_provider_results") + self.v.NEW_IN_028:
            self.assertEqual(e[t], "blocked", t)
        self.assertEqual(self.v.PROOF_TABLE, "site_api_calls")
        self.assertEqual(e[self.v.PROOF_TABLE], "blocked")

    def test_every_table_the_site_reads_is_public_in_the_list(self):
        """Derived from the code, not from memory: each table named in a rest/restCount call of the site."""
        found = set()
        for base, _, files in os.walk(os.path.join(ROOT, "site")):
            if "node_modules" in base or ".next" in base or os.sep + "scripts" in base:
                continue
            for f in files:
                if f.endswith((".ts", ".tsx")):
                    text = open(os.path.join(base, f), encoding="utf-8").read()
                    found.update(re.findall(r"\b(?:rest|restCount|restPaged)(?:<[^()]*?>)?\(\s*\"([a-z_0-9]+)\"", text))
        self.assertTrue({"series", "entities", "events", "catalogue", "latest_prices", "game_scores"} <= found, found)
        for t in found:
            self.assertEqual(self.v.EXPECTED.get(t), "public", f"the site reads {t} with the anon key")

    def test_it_only_reads(self):
        text = src("warehouse", "supabase", "verify_rls.py")
        self.assertNotIn("PATCH", text)
        self.assertNotIn("DELETE", text.replace("deleted", ""))
        self.assertIn("set transaction read only", text)
        # the only POSTs are the read functions behind the token, called with a wrong token
        for fn, _ in self.v.TOKEN_FUNCTIONS:
            self.assertRegex(fn, r"^(internal_|thesis_list|analysis_requests_list)")
        self.assertNotIn(self.v.WRONG_TOKEN, src("warehouse", "supabase", "migrations", "028_security_usage.sql"))


class HistoryScan(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.s = load("s177_scan_git_secrets", "scripts", "scan_git_secrets.py")

    def kinds(self, line):
        out = set()
        for kind, pat in self.s.PATTERNS:
            for m in pat.finditer(line):
                value = m.group(1) if kind == "named_literal" else m.group(0)
                if kind == "named_literal" and self.s.NOT_A_VALUE.match(value):
                    continue
                out.add(kind)
        return out

    def test_each_kind_is_found(self):
        # every sample is put together here, so no line of this file is itself shaped like a secret
        a, b = "A" * 40, "b" * 30
        self.assertIn("jwt", self.kinds("key = " + "ey" + "J" + "x" * 20 + "." + "ey" + "J" + "y" * 30 + "." + "z" * 40))
        self.assertIn("anthropic_key", self.kinds("sk-" + "ant-" + a))
        self.assertIn("github_token", self.kinds("gh" + "p_" + a))
        self.assertIn("github_token", self.kinds("github" + "_pat_" + "A1" * 30))
        self.assertIn("resend_key", self.kinds("r" + "e_" + "Ab12Cd34" + "_" + a))
        self.assertIn("supabase_access_token", self.kinds("sb" + "p_" + "a1" * 20))
        self.assertIn("postgres_url_password", self.kinds("postgres" + "ql://user:" + "hunter2hunter2" + "@db.example.com:5432/postgres"))
        self.assertIn("url_password", self.kinds("https" + "://user:" + "hunter2hunter2" + "@example.com/x"))
        self.assertIn("private_key_block", self.kinds("-----BEGIN " + "PRIVATE KEY-----"))
        self.assertIn("named_literal", self.kinds("RESEND_API" + "_KEY=" + b))
        self.assertIn("named_literal", self.kinds('INTERNAL_COSTS' + '_TOKEN: "' + b + '"'))

    def test_what_is_not_a_secret(self):
        for line in ("SUPABASE_ANON_KEY: ${{ secrets.SUPABASE_ANON_KEY }}", "const key = process.env.SUPABASE_ANON_KEY;",
                     "ANTHROPIC_API_KEY=<your key here, never commit it>", "key = os.environ.get('RESEND_API_KEY')",
                     "postgresql://user:<password>@host/db", "see https://github.com/SamuelEnrique/erw for the code"):
            self.assertEqual(self.kinds(line), set(), line)

    def test_a_role_is_read_and_nothing_else(self):
        import base64
        import json
        payload = base64.urlsafe_b64encode(json.dumps({"role": "anon", "iss": "supabase", "ref": "abcdefgh"}).encode()).decode().rstrip("=")
        token = "ey" + "Jhbgc" + "x" * 10 + "." + payload + "." + "s" * 40
        self.assertEqual(self.s.jwt_role(token), "role=anon iss=supabase")
        self.assertEqual(self.s.jwt_role("not.a.token"), "")

    def test_a_value_is_never_written(self):
        text = src("scripts", "scan_git_secrets.py")
        self.assertEqual(len(self.s.fingerprint("anything")), 8)
        fields = re.search(r'fields = \[(.*?)\]', text).group(1)
        self.assertNotIn("value", fields)
        self.assertNotRegex(text, r"(?<![a-z])print\((value|line|raw)")     # fingerprint(value) is the only thing made of a value

    def test_known_values(self):
        import tempfile
        with tempfile.TemporaryDirectory() as d:
            p = os.path.join(d, "env")
            with open(p, "w", encoding="utf-8") as f:
                f.write("# a note\nSHORT=abc\nA_TOKEN=" + "t" * 30 + "\nSITE_URL=https://example.com\n"
                        "DB_URL=postgres" + "ql://u:" + "p" * 12 + "@h:5432/d\nMAIL=someone@example.com\n")
            k = self.s.known_values([p])
        self.assertEqual(k["t" * 30], "A_TOKEN")
        self.assertEqual(k["p" * 12], "DB_URL (the password in it)")
        self.assertNotIn("abc", k)
        self.assertNotIn("https://example.com", k)
        self.assertNotIn("someone@example.com", k)


class Migration028(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.sql = src("warehouse", "supabase", "migrations", "028_security_usage.sql")
        cls.rb = src("warehouse", "supabase", "rollbacks", "028_security_usage.sql")

    def test_the_four_tables_are_internal(self):
        for t in ("site_rate_counts", "site_usage_events", "site_usage_daily", "site_usage_salt"):
            self.assertIn(f"create table if not exists public.{t}", self.sql)
            self.assertIn(f"alter table public.{t} enable row level security", self.sql)
            self.assertIn(f"revoke all on public.{t} from public, anon, authenticated", self.sql)
            self.assertIn(f"drop table if exists public.{t}", self.rb)
        self.assertNotIn("create policy", self.sql.split("-- B and C: the tables")[1])       # no policy on an internal table
        self.assertNotRegex(self.sql, r"grant (select|insert|update|delete|all)[^;]*on public\.site_")

    def test_part_a_changes_nothing_that_already_holds(self):
        a = self.sql.split("-- B and C: the tables")[0]
        self.assertIn("not c.relrowsecurity", a)                      # row-level security only where it is off
        self.assertNotIn("drop policy", self.sql)
        self.assertNotIn("drop table", self.sql)
        self.assertNotIn("disable row level security", self.sql + self.rb)
        for t in ("series", "entities", "events", "latest_prices", "catalogue", "sources", "headers"):
            self.assertIn(f"'{t}'", a)
        for t in ("subscribers", "site_api_calls", "thesis_runs", "analysis_requests", "game_plays"):
            self.assertIn(f"'{t}'", a)

    def test_every_function_checks_the_token_and_pins_its_search_path(self):
        fns = re.findall(r"create or replace function (public|erw_private)\.(\w+)\((.*?)\)\s*returns (.*?) as \$\$(.*?)\$\$;", self.sql, re.S)
        self.assertEqual(sorted(n for s, n, *_ in fns if s == "public"), ["internal_usage", "site_rate_admit", "site_usage_record"])
        for schema, name, _args, head, body in fns:
            self.assertIn("security definer", head, name)
            self.assertIn("set search_path = ''", head, name)
            if schema == "public":
                self.assertIn("erw_private.site_token_ok(p_token)", body, name)
                self.assertIn("'42501'", body, name)
                self.assertRegex(self.sql, rf"revoke all on function public\.{name}\([^)]*\) from public;")
            else:
                self.assertRegex(self.sql, rf"revoke all on function erw_private\.{name}\([^)]*\) from public, anon, authenticated;")
            self.assertIn(f"drop function if exists {schema}.{name}(", self.rb)

    def test_the_salt_is_random_and_leaves_with_its_day(self):
        self.assertIn("extensions.gen_random_bytes(32)", self.sql)
        self.assertIn("delete from public.site_usage_salt where day < today", self.sql)
        self.assertIn("delete from public.site_usage_events where day < today", self.sql)
        self.assertIn("extensions.hmac(decode(p_visitor, 'hex'), s, 'sha256')", self.sql)
        daily = re.search(r"create table if not exists public\.site_usage_daily \((.*?)\);", self.sql, re.S).group(1)
        self.assertNotIn("visitor ", daily)                             # counts only: no hash is kept of an earlier day
        events = re.search(r"create table if not exists public\.site_usage_events \((.*?)\);", self.sql, re.S).group(1)
        for col in ("day", "path", "tool", "event", "visitor", "n"):
            self.assertRegex(events, rf"\b{col}\b")
        for word in ("address", "user_agent", "referrer", "ip "):
            self.assertNotIn(word, events)
        self.assertIn("'tool opened', 'input changed', 'scenario compared', 'download'", events)

    def test_the_rollback_is_out_of_the_full_run(self):
        mig = os.listdir(os.path.join(ROOT, "warehouse", "supabase", "migrations"))
        self.assertEqual([f for f in mig if "rollback" in f], [])
        numbers = [f[:3] for f in mig if f.endswith(".sql")]
        self.assertEqual(len(numbers), len(set(numbers)), "two migrations with one number collide in --only")
        a = load("s177_apply", "warehouse", "supabase", "apply.py")
        files = [os.path.join("m", f) for f in sorted(mig) if f.endswith(".sql")]
        self.assertEqual([os.path.basename(f) for f in a.select(files, "028")], ["028_security_usage.sql"])
        text = src("warehouse", "supabase", "apply.py")
        self.assertIn('"rollbacks" if args.rollback else "migrations"', text)
        self.assertIn("--only and --rollback are not given together", text)

    def test_no_em_dash(self):
        for parts in (("warehouse", "supabase", "migrations", "028_security_usage.sql"), ("warehouse", "supabase", "rollbacks", "028_security_usage.sql"),
                      ("warehouse", "supabase", "verify_rls.py"), ("scripts", "scan_git_secrets.py"), ("docs", "methods", "usage_counts.md"),
                      ("docs", "reviews", "2026-10-10-security.md"), ("site", "lib", "guard.ts"), ("site", "lib", "usage.ts"), ("site", "lib", "usagepath.ts"),
                      ("site", "components", "Usage.tsx"), ("site", "app", "api", "usage", "route.ts"), ("site", "app", "privacy", "page.tsx"),
                      ("site", "app", "internal", "usage", "page.tsx"), ("site", "app", "internal", "open", "page.tsx"), ("site", "app", "terms", "page.tsx"),
                      ("site", "next.config.ts"), ("tests", "test_session177.py"), ("site", "scripts", "test-usage.mjs"), ("site", "scripts", "check-security.mjs"),
                      ("site", "scripts", "check-csp.mjs"), ("site", "scripts", "test-markdown-safe.mjs"), ("site", "lib", "markdown.ts"), ("site", "components", "echarts.ts"),
                      ("docs", "release-gate.md"), ("warehouse", "supabase", "README.md"), ("archive", "sessions", "SESSION_177_REPORT.md")):
            self.assertNotIn(chr(0x2014), src(*parts), "/".join(parts))


class Site(unittest.TestCase):
    def test_the_routes_carry_their_guards(self):
        ask = src("site", "app", "api", "ask", "route.ts")
        for word in ("sameOrigin(req)", "scripted(req)", 'typed(req, "json")', 'limited(req, "ask_hour"', "site_ask_admit", "MAX_BODY"):
            self.assertIn(word, ask)
        self.assertLess(ask.index("sameOrigin(req)"), ask.index("site_ask_admit"))         # refused before anything is counted or spent
        sub = src("site", "app", "api", "subscribe", "route.ts")
        for word in ("sameOrigin(req)", "scripted(req)", 'limited(req, "subscribe", 5, 3600)', 'limited(req, "subscribe_day", 200, 86400, { everybody: true })', '"website"'):
            self.assertIn(word, sub)
        self.assertLess(sub.index('"subscribe_day"'), sub.index("insertRow("))             # the day's ceiling stands before a row or an email
        for route in ("finish", "score"):
            play = src("site", "app", "api", "play", route, "route.ts")
            self.assertIn('limited(req, "play", 30, 3600)', play)
            self.assertIn("sameOrigin(req)", play)
        self.assertIn('limited(req, "download", 60, 3600)', src("site", "app", "api", "download", "route.ts"))
        self.assertIn('limited(req, "pitchbook", 60, 3600)', src("site", "app", "api", "thesis", "pitchbook", "route.ts"))
        for parts in (("thesis", "run"), ("thesis", "provider"), ("analysis",)):
            text = src("site", "app", "api", *parts, "route.ts")
            self.assertLess(text.index("if (!sameOrigin(req)) return hidden();"), text.index("internalOk(req.cookies.get(COOKIE)?.value)"))
        for parts in (("subscribe", "confirm"), ("unsubscribe",)):
            self.assertIn("email.length > 254", src("site", "app", "api", *parts, "route.ts"))

    def test_the_limit_falls_back_and_stores_no_address(self):
        g = src("site", "lib", "guard.ts")
        self.assertIn("visitorKey(who, utcDay(o.now), o.salt)", g)
        self.assertIn('by: "memory"', g)
        self.assertIn("site_rate_admit", g)
        self.assertNotIn("console.log", g)
        self.assertNotIn("headlesschrome", g.split("const STOCK")[1].split("\n")[0].lower())   # the ERW's own browser checks pass

    def test_the_unlock_keeps_its_link_and_gains_a_form(self):
        r = src("site", "app", "internal", "unlock", "route.ts")
        get, post = r.split("export async function POST")
        # the old link, word for word as session 67 wrote it
        self.assertIn('const given = req.nextUrl.searchParams.get("token");', get)
        self.assertIn("if (!token || !given || given !== token) return new NextResponse(\"Not found\", { status: 404", get)
        self.assertIn("res.cookies.set(COOKIE, await digest(token), { httpOnly: true, secure, sameSite: \"lax\", path: \"/\", maxAge: MAX_AGE });", get)
        # the form: the token from the body, never from the address; the same two cookies; a right token is never limited
        self.assertNotIn("searchParams", post)
        self.assertIn('form.get("token")', post)
        self.assertIn("sameSecret(given, token)", post)
        self.assertIn("res.cookies.set(COOKIE, await digest(token), { httpOnly: true, secure, sameSite: \"lax\", path: \"/\", maxAge: MAX_AGE });", post)
        self.assertIn('res.cookies.set(VIEW, "internal"', post)
        self.assertLess(post.index("sameSecret(given, token)"), post.index('limited(req, "unlock", 10, 3600)'))
        self.assertIn('"Referrer-Policy": "no-referrer"', post)
        self.assertIn('"Cache-Control": "private, no-store"', post)
        self.assertNotIn("console.", post)
        form = src("site", "app", "internal", "open", "page.tsx")
        self.assertIn('method="post" action="/internal/unlock"', form)
        self.assertIn('name="token" type="password"', form)
        self.assertNotIn("INTERNAL_COSTS_TOKEN}", form)
        # a browser posts a form with "Origin: null" from a page whose policy is no-referrer: the form's page is same-origin,
        # the guard takes "null" only with the browser's own same-origin word, and a real browser submits the form in check-csp
        self.assertIn('referrer: "same-origin"', form)
        self.assertNotIn('referrer: "no-referrer"', form)
        self.assertIn('if (origin === "null") return site === "same-origin";', src("site", "lib", "guard.ts"))
        csp = src("site", "scripts", "check-csp.mjs")
        self.assertIn("i.form.requestSubmit()", csp)
        self.assertIn('base + "/internal/open"', csp)
        self.assertNotIn("process.env", form)

    def test_the_internal_pages_open_with_the_cookie(self):
        for page, fn in (("costs", "internal_costs"), ("ask", "internal_ask_spend"), ("usage", "internal_usage")):
            text = src("site", "app", "internal", page, "page.tsx")
            self.assertIn("token !== want && !(await internalOk((await cookies()).get(COOKIE)?.value))", text, page)
            self.assertIn(f'"{fn}", {{ p_token: want }}', text, page)
            self.assertIn("robots: { index: false, follow: false }", text)

    def test_the_security_headers(self):
        c = src("site", "next.config.ts")
        for word in ('"Strict-Transport-Security"', "max-age=63072000; includeSubDomains; preload", '"X-Content-Type-Options", value: "nosniff"',
                     '"X-Frame-Options", value: "DENY"', '"Referrer-Policy", value: "strict-origin-when-cross-origin"', '"Permissions-Policy"',
                     '"Content-Security-Policy", value: CSP_ENFORCED', '"Content-Security-Policy-Report-Only", value: CSP_REPORT_ONLY',
                     "base-uri 'self'; object-src 'none'; frame-ancestors 'none'; form-action 'self'", 'source: "/:path*", headers: SECURITY_HEADERS',
                     'source: "/internal/:path*"', '{ source: "/internal/open", headers: [{ key: "Referrer-Policy", value: "same-origin" }] }'):
            self.assertIn(word, c)
        self.assertIn("poweredByHeader: false", c)
        self.assertIn("async redirects()", c)                           # the redirects are as they were
        self.assertIn('{ source: "/markets", destination: "/board", permanent: true }', c)

    def test_markdown_is_not_markup(self):
        m = src("site", "lib", "markdown.ts")
        for word in ("export function safeHtml(raw: string): string", "export function safeHref(href: string): boolean", "return safeHtml(token.raw ?? token.text);",
                     'if (!safeHref(t.href)) { t.href = "#"; return; }', "^(https?:|mailto:)"):
            self.assertIn(word, m)
        self.assertLess(m.index("if (!safeHref(t.href))"), m.index("t.href = sitePath("))      # checked before a link is rewritten
        self.assertEqual(m.count("new Marked("), 1)                                            # one renderer: nothing goes round it
        # every page that writes markdown into the page does it through render()
        for base, _, files in os.walk(os.path.join(ROOT, "site", "app")):
            for f in files:
                if f.endswith(".tsx"):
                    text = open(os.path.join(base, f), encoding="utf-8").read()
                    for use in re.findall(r"dangerouslySetInnerHTML=\{\{ __html: (\w+)", text):
                        self.assertEqual(use, "render", os.path.join(base, f))

    def test_the_chart_library_is_pinned_by_its_hash(self):
        e = src("site", "components", "echarts.ts")
        self.assertRegex(e, r'export const ECHARTS_SRI = "sha384-[A-Za-z0-9+/]{64}";')
        self.assertIn("s.integrity = ECHARTS_SRI;", e)
        self.assertIn('s.crossOrigin = "anonymous";', e)
        self.assertLess(e.index("s.integrity = ECHARTS_SRI;"), e.index("document.head.appendChild(s);"))
        self.assertIn("/ajax/libs/echarts/5.6.0/echarts.min.js", e)       # the hash is of this version: a new version needs a new hash
        self.assertIn("https://cdnjs.cloudflare.com", src("site", "next.config.ts"))

    def test_next_is_the_patched_release(self):
        import json
        pkg = json.loads(src("site", "package.json"))
        self.assertEqual(pkg["dependencies"]["next"], "16.3.8")
        self.assertEqual(pkg["devDependencies"]["eslint-config-next"], "16.3.8")
        lock = json.loads(src("site", "package-lock.json"))
        self.assertEqual(lock["packages"]["node_modules/next"]["version"], "16.3.8")
        self.assertEqual(pkg["dependencies"]["react"], "19.2.8")           # nothing else moved

    def test_the_usage_counts_send_no_identifier(self):
        u = src("site", "lib", "usage.ts")
        head = u.split("\n")[:3]
        self.assertTrue(head[0].startswith('// track("scenario compared")'))                 # the lines session 179 reads
        self.assertIn("export function track(event: UsageEvent, detail?: { path?: string }): void", u)
        for word in ("navigator.sendBeacon", "keepalive: true", "optedOut(", "globalPrivacyControl", "doNotTrack", "catch {"):
            self.assertIn(word, u)
        code = "\n".join(line for line in (u + src("site", "components", "Usage.tsx")).split("\n") if not line.strip().startswith(("//", "*", "/*")))
        for word in ("localStorage", "sessionStorage", "document.cookie", "document.referrer", "location.search", "location.href", ".value", "indexedDB", "userAgent"):
            self.assertNotIn(word, code, word)
        self.assertIn("window.location.pathname", code)
        route = src("site", "app", "api", "usage", "route.ts")
        for word in ('req.headers.get("dnt") === "1"', 'req.headers.get("sec-gpc") === "1"', "cleanPath(body.path)", "toolOf(path)", "usageVisitor(ip,",
                     "site_usage_record", "status: 204"):
            self.assertIn(word, route)
        route_code = "\n".join(line for line in route.split("\n") if not line.strip().startswith("//"))
        self.assertNotIn("console.", route_code)                          # nothing about a request is logged
        self.assertNotIn("cookies.set", route_code)
        self.assertNotIn("Set-Cookie", route_code)
        self.assertNotIn("referer", route_code.lower())
        layout = src("site", "app", "layout.tsx")
        self.assertEqual(layout.count("<Usage />"), 1)
        self.assertIn('<Link href="/privacy">Privacy</Link>', layout)

    def test_no_file_of_the_two_folders_held_by_other_sessions_names_this_one(self):
        for folder in (("site", "app", "cost-of-power", "battery"), ("site", "app", "network")):
            for base, _, files in os.walk(os.path.join(ROOT, *folder)):
                for f in files:
                    self.assertNotIn("session 177", open(os.path.join(base, f), encoding="utf-8").read(), f)

    def test_privacy_and_terms_say_what_the_code_does(self):
        rel = src("site", "lib", "release.ts")
        self.assertIn('"/privacy": "review"', rel)
        self.assertNotIn('": "live"', rel.split("export const RELEASE")[1].split("};")[0])  # every page stays in review
        p = src("site", "app", "privacy", "page.tsx")
        cookie, view = re.search(r'export const COOKIE = "(\w+)"', rel).group(1), re.search(r'export const VIEW = "(\w+)"', rel).group(1)
        self.assertIn(cookie, p)
        self.assertIn(view, p)
        self.assertIn("90 days", p)
        self.assertIn("90 * 24 * 3600", rel)
        # every cookie the site can set is one of the two named
        for base, _, files in os.walk(os.path.join(ROOT, "site", "app")):
            for f in files:
                if f.endswith((".ts", ".tsx")):
                    for name in re.findall(r"cookies\.set\((\w+)", open(os.path.join(base, f), encoding="utf-8").read()):
                        self.assertIn(name, ("COOKIE", "VIEW"), f)
        # the only browser storage is the game's two keys
        users = []
        for top in ("app", "components", "lib"):
            for base, _, files in os.walk(os.path.join(ROOT, "site", top)):
                for f in files:
                    if f.endswith((".ts", ".tsx")):
                        text = open(os.path.join(base, f), encoding="utf-8").read()
                        code = "\n".join(line for line in text.split("\n") if not line.strip().startswith(("//", "*", "/*")))
                        if re.search(r"window\.localStorage|sessionStorage\.|indexedDB\.", code):
                            users.append(f)
        self.assertEqual(users, ["Game.tsx"])
        self.assertIn("tutorial", p)
        self.assertIn("settings you last chose", p)
        for word in ("sets no tracking cookies", "Do Not Track", "Global Privacy Control", "a tool was opened, an input was changed, a scenario was compared, a file was downloaded",
                     "cdnjs", "Vercel", "Supabase", "Never recorded"):
            self.assertIn(word, p)
        t = src("site", "app", "terms", "page.tsx")
        for word in ("This site sets no tracking cookies.", "a tool opened, an input changed, a scenario compared, a download", 'id="usage"', '<Link href="/privacy">Privacy</Link>',
                     "keyed code of the address for that day only"):
            self.assertIn(word, t)
        self.assertIn('<Section title="Subscribers" id="subscribers">', t)   # nothing the page showed is dropped
        self.assertIn('<Section title="Data licensing, per source" id="licensing">', t)

    def test_the_method_note_and_the_review_exist(self):
        m = src("docs", "methods", "usage_counts.md")
        for word in ("gen_random_bytes", "ASK_VISITOR_SALT", "Backups", "Do Not Track", "site_usage_daily", "browser-days"):
            self.assertIn(word, m)
        r = src("docs", "reviews", "2026-10-10-security.md")
        for word in ("Ranked by severity", "What is exposed", "The fix", "The risk of the fix", "## High", "## Medium", "## Low", "row-level security", "npm audit", "pip-audit", "git history", "bucket"):
            self.assertIn(word, r)


if __name__ == "__main__":
    unittest.main()

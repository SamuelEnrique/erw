"""Session 371: the documents an agent reads first, and the security review's open items.

Energy Research Warehouse (ERW). Held here, with no network and no database:
1. todo 007 is in queue/done/ with its line naming session 371, and no longer in queue/todo/;
2. ARCHITECTURE.md says how the data lock and sync's restore work, and links docs/machines.md;
3. the runbook says the outside trigger is done (pg_cron, session 59) and keeps the GitHub-side steps as the fallback;
4. docs/security.md lists every item of the review (H1 to H3, M1 to M8, L1 to L13) and the three this session found;
5. S1: the proxy and the battery page compare the internal cookie in constant time (cookieOpens), and no file of the
   site compares a cookie with the token's digest by ===;
6. S2: the five internal addresses open with the internal cookie, the finder writes the token into a link only when
   its address brought it, and check-values no longer writes the token into an address;
7. no em dash in any file this session wrote.
"""
import os
import re
import unittest

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


def src(*parts):
    with open(os.path.join(ROOT, *parts), encoding="utf-8") as f:
        return f.read()


class Docs(unittest.TestCase):
    def test_todo_007_is_done(self):
        self.assertFalse(os.path.exists(os.path.join(ROOT, "queue", "todo", "007-code-docs-for-machines.md")))
        t = src("queue", "done", "007-code-docs-for-machines.md")
        self.assertTrue(t.startswith("---"))   # the front matter stays first, so taskqueue.py still reads the file
        body = re.sub(r"^---\r?\n.*?\r?\n---\r?\n", "", t, count=1, flags=re.S)
        self.assertTrue(body.startswith("Done by session 371"), body[:80])

    def test_architecture_names_the_lock_and_the_restore(self):
        a = src("ARCHITECTURE.md")
        for w in ("docs/machines.md", "warehouse/lock.py", "erw_locks", "scripts/sync.py", "warehouse/restore_tables.py",
                  "warehouse/archive/restore.py", "export ceiling"):
            self.assertIn(w, a, w)

    def test_runbook_says_the_trigger_is_done(self):
        r = src("docs", "runbook.md")
        self.assertIn("**Done: no step for Samuel here.**", r)
        self.assertIn('"The schedule"', r)
        self.assertIn("The steps below stay as the fallback", r)
        self.assertIn("scheduler.py --set-token", r)
        # session 58's steps are still there (tests/test_session58.py holds them too)
        self.assertIn("### 2. The scheduler: cron-job.org (free)", r)


class SecurityList(unittest.TestCase):
    def test_every_item_is_listed(self):
        s = src("docs", "security.md")
        items = [f"H{i}" for i in range(1, 4)] + [f"M{i}" for i in range(1, 9)] + [f"L{i}" for i in range(1, 14)] + ["S1", "S2", "S3", "S4"]
        for i in items:
            self.assertRegex(s, rf"\n\| {i} \|", i)
        self.assertIn("reviews/2026-10-10-security.md", s)
        self.assertIn("## What needs Samuel, with the choice", s)


class ConstantTime(unittest.TestCase):
    def test_s1_cookie_compared_in_constant_time(self):
        rel = src("site", "lib", "release.ts")
        self.assertIn("export async function cookieOpens(", rel)
        self.assertIn("d |= have.charCodeAt(i) ^ want.charCodeAt(i);", rel)
        self.assertNotIn("import ", rel.split("export async function cookieOpens(")[1].split("\n}")[0])
        self.assertIn("if (await cookieOpens(have, token)) return NextResponse.next();", src("site", "proxy.ts"))
        self.assertIn("return cookieOpens(have, token);", src("site", "app", "cost-of-power", "battery", "read.ts"))
        site = os.path.join(ROOT, "site")
        for d in ("app", "lib", "components"):
            for dp, _, fs in os.walk(os.path.join(site, d)):
                for f in fs:
                    if f.endswith((".ts", ".tsx")):
                        t = open(os.path.join(dp, f), encoding="utf-8").read()
                        self.assertNotRegex(t, r"===\s*\(await digest\(", os.path.join(dp, f))
        self.assertNotRegex(src("site", "proxy.ts"), r"===\s*\(await digest\(")


class TokenOutOfAddresses(unittest.TestCase):
    def test_s2_pages_open_with_the_cookie(self):
        gate = "if (want.length < 24 || (token !== want && !(await internalOk((await cookies()).get(COOKIE)?.value)))) notFound();"
        for page in ("shape-premium", "ai-gigawatts"):
            self.assertIn(gate, src("site", "app", "reports", "draft", page, "page.tsx"), page)
        fin = src("site", "lib", "finder.ts")
        self.assertIn("export async function internalOpen(", fin)
        self.assertIn("(tokenOk(token) || (await cookieOpens(cookie, want)))", fin)
        self.assertIn("internalOpen(token, (await cookies()).get(COOKIE)?.value)", src("site", "app", "severance", "lease", "real", "page.tsx"))
        self.assertIn("internalOpen(token, (await cookies()).get(COOKIE)?.value)", src("site", "app", "severance", "finder", "page.tsx"))
        self.assertIn('internalOpen(new URL(req.url).searchParams.get("token"), (await cookies()).get(COOKIE)?.value)',
                      src("site", "app", "severance", "finder", "download", "route.ts"))

    def test_s2_no_link_carries_the_token_unless_it_came_in(self):
        page = src("site", "app", "severance", "finder", "page.tsx")
        self.assertIn('const q = token ? `token=${encodeURIComponent(token)}&` : "";', page)
        self.assertIn('{token ? <input type="hidden" name="token" value={token} /> : null}', page)
        real = src("site", "app", "severance", "lease", "real", "page.tsx")
        self.assertIn('{token ? <input type="hidden" name="token" value={token} /> : null}', real)
        for t in (page, real):
            self.assertEqual(t.count('name="token" value={token}'), t.count('{token ? <input type="hidden" name="token" value={token} /> : null}'))

    def test_s2_check_values_reads_the_drafts_with_the_cookie(self):
        cv = src("site", "scripts", "check-values.mjs")
        self.assertIn("if (tok) urls.push(...INTERNAL.filter(wanted).map((page) => ({ page, url: page, internal: true })));", cv)
        self.assertNotIn("url: `${page}?token=", cv)


class CspProbe(unittest.TestCase):
    def test_s4_the_library_probe_opens_a_page_that_loads_it(self):
        csp = src("site", "scripts", "check-csp.mjs")
        self.assertIn('await go(base + "/map");', csp)
        self.assertIn('/map: the chart library loaded and drew', csp)
        self.assertIn('useEChart', src("site", "app", "map", "ProjectMap.tsx"))


class NoDash(unittest.TestCase):
    def test_no_em_dash(self):
        for p in (("ARCHITECTURE.md",), ("docs", "runbook.md"), ("docs", "security.md"), ("queue", "done", "007-code-docs-for-machines.md"),
                  ("site", "lib", "release.ts"), ("site", "lib", "finder.ts"), ("site", "proxy.ts"),
                  ("site", "app", "cost-of-power", "battery", "read.ts"), ("site", "app", "severance", "finder", "page.tsx"),
                  ("site", "app", "severance", "finder", "download", "route.ts"), ("site", "app", "severance", "lease", "real", "page.tsx"),
                  ("site", "app", "reports", "draft", "shape-premium", "page.tsx"), ("site", "app", "reports", "draft", "ai-gigawatts", "page.tsx"),
                  ("site", "scripts", "check-values.mjs"), ("site", "scripts", "check-csp.mjs"), ("tests", "test_session371.py")):
            self.assertNotIn(chr(0x2014), src(*p), "/".join(p))


if __name__ == "__main__":
    unittest.main()

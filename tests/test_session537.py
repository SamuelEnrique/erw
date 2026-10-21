"""Session 537: a build does not keep a failed read.

Energy Research Warehouse (ERW). On a slow database a build cached a page whose optional read had failed, and the page
showed "no data" until its interval turned or the next build (session 461's check-routes: 15 pages). Since this session a
read that fails in site/lib/supabase.ts asks Next, through unstable_cache, for a revalidation of RETRY (60) seconds for
the page being rendered, so the page is made again on a request a minute later; a page whose reads all succeeded asks for
nothing and keeps its interval. A read held for a license and a server with no database named are not failed reads.
required() reads keep failing the build.

The behaviour is proved in node by site/scripts/test-failed-read.mjs, which imports lib/supabase.ts as it is, fails reads
on purpose with a stand-in for fetch, and counts the marks (no request leaves the machine; the alias loader stands in for
next/cache). The tests here run it and hold the code to the rule. site/scripts/failing-read-proxy.mjs is the
pass-through that fails one table's reads for a real build (the report's "To finish" or its results).

    python -m unittest tests.test_session537 -v
"""

import os
import re
import shutil
import subprocess
import unittest

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
SITE = os.path.join(ROOT, "site")


def src(*parts):
    with open(os.path.join(ROOT, *parts), encoding="utf-8") as f:
        return f.read()


SB = ("site", "lib", "supabase.ts")


class TheNodeTest(unittest.TestCase):
    def test_reads_failed_on_purpose_mark_the_page_and_reads_that_succeed_do_not(self):
        node = shutil.which("node")
        if not node:
            self.skipTest("node is not on this machine")
        # the child's environment only: no database, no build phase, no switch of the reader
        env = {k: v for k, v in os.environ.items() if k not in ("SUPABASE_URL", "SUPABASE_ANON_KEY", "NEXT_PHASE", "NEXT_RUNTIME", "ERW_PAGES_TOGETHER")}
        r = subprocess.run([node, "--import", "./scripts/alias-register.mjs", "scripts/test-failed-read.mjs"], cwd=SITE,
                           capture_output=True, text=True, timeout=300, env=env)
        self.assertEqual(r.returncode, 0, r.stdout[-2000:] + r.stderr[-2000:])
        self.assertIn("every case holds", r.stdout)
        self.assertNotIn("FAIL", r.stdout)
        self.assertGreaterEqual(r.stdout.count("\nok   ") + r.stdout.startswith("ok   "), 12)


class TheCode(unittest.TestCase):
    def setUp(self):
        self.s = src(*SB)

    def test_retry_is_a_minute(self):
        self.assertIn("export const RETRY = 60;", self.s)

    def test_every_reader_marks_a_failure_once_and_rethrows_it(self):
        self.assertIn("const rows = await askAgainOnFailure(() => restPages<T>(table, query, revalidate, max, together));", self.s)
        self.assertIn("return askAgainOnFailure(() => countOf(table, query, revalidate));", self.s)
        f = self.s[self.s.index("async function askAgainOnFailure"):]
        f = f[:f.index("\n}\n")]
        self.assertIn("await markFailedRead(e);", f)
        self.assertIn("throw e;", f)

    def test_the_mark_is_unstable_cache_with_retry_and_never_for_a_license_or_no_database(self):
        m = self.s[self.s.index("export async function markFailedRead"):]
        m = m[:m.index("\n}\n")]
        self.assertIn("if (e instanceof LicenseNeeded || e instanceof NotConfigured) return false;", m)
        self.assertIn("if (!process.env.NEXT_RUNTIME) return false;", m)
        self.assertIn('await import("next/cache")', m)
        self.assertIn('unstable_cache(async () => true, ["erw-failed-read"], { revalidate: RETRY })', m)
        self.assertIn("catch (m)", m)                       # the mark itself never fails a page
        self.assertNotIn("fetch(", m)                       # nothing is read from the database for the mark
        self.assertNotIn('from "next/cache"', self.s)       # imported inside Next only, so the node scripts load as before

    def test_required_still_throws_and_the_build_still_takes_turns(self):
        self.assertIn("throw e instanceof DataError ? e : new DataError(reason);", self.s)
        self.assertIn("const BUILD_READS = 2;", self.s)
        self.assertIn("const WAITS = BUILDING ? [1000, 3000, 5000, 8000, 12000] : [1000, 3000];", self.s)

    def test_a_read_that_succeeds_sends_its_own_revalidation(self):
        self.assertIn("next: { revalidate, tags: [table] },", self.s)
        self.assertEqual(self.s.count("next: { revalidate, tags: [table] },"), 2)


class TheProxy(unittest.TestCase):
    def test_its_default_host_is_not_a_stand_in_so_required_reads_still_fail_a_build(self):
        p = src("site", "scripts", "failing-read-proxy.mjs")
        host = re.search(r'opt\("--host", "([0-9.]+)"\)', p).group(1)
        rx = re.search(r"const standIn = \(\) => /(.+?)/\.test", self.s_()).group(1).replace("\\/", "/")
        self.assertIsNone(re.match(rx, f"http://{host}:54537"))
        self.assertIsNotNone(re.match(rx, "http://127.0.0.1:54537"))
        self.assertIn('if (req.method !== "GET"', p)       # reads only: it can write nothing
        self.assertIn("fs.existsSync(flag)", p)

    def s_(self):
        return src(*SB)


class TheWords(unittest.TestCase):
    def test_no_em_dash(self):
        for p in (SB, ("site", "scripts", "test-failed-read.mjs"), ("site", "scripts", "failing-read-proxy.mjs"),
                  ("site", "scripts", "alias-loader.mjs"), ("tests", "test_session537.py")):
            self.assertNotIn(chr(0x2014), src(*p), p)
        rp = os.path.join(ROOT, "archive", "sessions", "SESSION_537_REPORT.md")
        if os.path.exists(rp):
            self.assertNotIn(chr(0x2014), src("archive", "sessions", "SESSION_537_REPORT.md"))


if __name__ == "__main__":
    unittest.main()

"""Session 580: the database's heavier reads, measured.

Energy Research Warehouse (ERW). site/lib/supabase.ts prints one "[erw-read]" line a request (table, query, status,
Content-Range and milliseconds) when the server or the build is started with ERW_READ_TIMING=1, and nothing otherwise:
off, no clock is read and no line printed, and the request is the one it was. site/scripts/test-read-timing.mjs proves both ways in node with a
stand-in for fetch (no request leaves the machine); site/scripts/slow-reads.mjs turns a build's log into the table of
docs/reviews/slow-reads-2026-10-22.md. Migration 036 holds the indexes that review proposes; it is written and not
applied (applying it is Samuel's or the data machine's), and its rollback is beside it.

    python -m unittest tests.test_session580 -v
"""

import os
import re
import shutil
import subprocess
import unittest

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
SITE = os.path.join(ROOT, "site")
MIG = os.path.join(ROOT, "warehouse", "supabase", "migrations")
ROLL = os.path.join(ROOT, "warehouse", "supabase", "rollbacks")


def src(*parts):
    with open(os.path.join(ROOT, *parts), encoding="utf-8") as f:
        return f.read()


def node_env(**extra):
    env = {k: v for k, v in os.environ.items()
           if k not in ("SUPABASE_URL", "SUPABASE_ANON_KEY", "NEXT_PHASE", "NEXT_RUNTIME", "ERW_PAGES_TOGETHER", "ERW_READ_TIMING")}
    env.update(extra)
    return env


class TheNodeTest(unittest.TestCase):
    def run_mode(self, mode):
        node = shutil.which("node")
        if not node:
            self.skipTest("node is not on this machine")
        r = subprocess.run([node, "--import", "./scripts/alias-register.mjs", "scripts/test-read-timing.mjs", mode], cwd=SITE,
                           capture_output=True, text=True, timeout=300, env=node_env())
        self.assertEqual(r.returncode, 0, r.stdout[-2000:] + r.stderr[-2000:])
        self.assertIn(f"every case holds (timing {mode})", r.stdout)
        self.assertNotIn("FAIL", r.stdout)
        self.assertGreaterEqual(len(re.findall(r"^ok   ", r.stdout, re.M)), 7)

    def test_off_prints_nothing_and_changes_no_read(self):
        self.run_mode("off")

    def test_on_prints_one_line_a_request(self):
        self.run_mode("on")


class TheSummary(unittest.TestCase):
    def test_slow_reads_groups_and_sorts_a_log(self):
        node = shutil.which("node")
        if not node:
            self.skipTest("node is not on this machine")
        tmp = os.path.join(ROOT, "runs", "test_session580_log.txt")
        os.makedirs(os.path.dirname(tmp), exist_ok=True)
        lines = [
            "noise",
            '[erw-read] {"kind":"rows","table":"series","query":"select=a&table_name=eq.x&order=ts_utc&limit=1000&offset=0","status":"200","range":"0-999/*","ms":900}',
            '[erw-read] {"kind":"rows","table":"series","query":"select=a&table_name=eq.x&order=ts_utc&limit=1000&offset=0","status":"200","range":"0-999/*","ms":3}',
            '[erw-read] {"kind":"count","table":"events","query":"table_name=eq.y&limit=1","status":"200","range":"0-0/42","ms":1500}',
            '[erw-read] {"kind":"rows","table":"entities","query":"table_name=eq.z&limit=1000&offset=0","status":"200","range":"*/*","ms":10}',
            '[erw-read] {"kind": cut',
        ]
        with open(tmp, "w", encoding="utf-8") as f:
            f.write("\n".join(lines) + "\n")
        try:
            r = subprocess.run([node, "scripts/slow-reads.mjs", tmp, "5"], cwd=SITE, capture_output=True, text=True,
                               timeout=120, env=node_env())
        finally:
            os.remove(tmp)
        self.assertEqual(r.returncode, 0, r.stdout + r.stderr)
        self.assertIn("4 requests, 3 distinct reads", r.stdout)
        rows = [l for l in r.stdout.splitlines() if re.match(r"^\| \d", l)]
        self.assertEqual(len(rows), 3)
        self.assertTrue(rows[0].startswith("| 1 | 1500 | count | events | table_name=eq.y |"), rows[0])
        self.assertIn("| 900 | rows | series | table_name=eq.x | ts_utc | 0 | 1000 | 2 | 200 |", rows[1])
        self.assertIn("| 10 | rows | entities | table_name=eq.z |  | 0 | 0 | 1 |", rows[2])

    def test_a_log_without_timing_lines_exits_2(self):
        node = shutil.which("node")
        if not node:
            self.skipTest("node is not on this machine")
        tmp = os.path.join(ROOT, "runs", "test_session580_empty.txt")
        os.makedirs(os.path.dirname(tmp), exist_ok=True)
        with open(tmp, "w", encoding="utf-8") as f:
            f.write("a build without the switch\n")
        try:
            r = subprocess.run([node, "scripts/slow-reads.mjs", tmp], cwd=SITE, capture_output=True, text=True,
                               timeout=120, env=node_env())
        finally:
            os.remove(tmp)
        self.assertEqual(r.returncode, 2, r.stdout + r.stderr)


class TheCode(unittest.TestCase):
    def setUp(self):
        self.s = src("site", "lib", "supabase.ts")

    def test_the_switch_is_off_by_default_and_off_reads_no_clock_and_prints_nothing(self):
        self.assertIn("const READ_TIMING = readTiming(process.env.ERW_READ_TIMING);", self.s)
        f = self.s[self.s.index("export function readTiming"):]
        self.assertIn('return v === "1";', f[:f.index("\n}\n")])
        c = self.s[self.s.index("function readClock("):]
        self.assertIn("return READ_TIMING ? performance.now() : 0;", c[:c.index("\n}\n")])
        l = self.s[self.s.index("function readLine("):]
        l = l[:l.index("\n}\n")]
        self.assertEqual(l.split("\n")[1].strip(), "if (!READ_TIMING) return;", l)

    def test_both_readers_are_timed_inside_the_turn_and_send_the_request_they_sent(self):
        # session 148's test holds that one place sends a page's request, by this very line
        self.assertEqual(self.s.count("await fetch(`${base}/rest/v1/${table}?${qs}`"), 1)
        self.assertIn("          r = await fetch(`${base}/rest/v1/${table}?${qs}`, {\n"
                      "            headers: { apikey: key, Authorization: `Bearer ${key}` },\n"
                      "            next: { revalidate, tags: [table] },\n"
                      "          });\n"
                      "        } finally {\n"
                      '          readLine("rows", table, qs, t0, r);', self.s)
        self.assertIn("      r = await fetch(url, {\n"
                      '        headers: { apikey: key, Authorization: `Bearer ${key}`, Prefer: "count=exact" },\n'
                      "        next: { revalidate, tags: [table] },\n"
                      "      });\n"
                      "    } finally {\n"
                      '      readLine("count", table, qs, t0, r);', self.s)
        self.assertIn("[res, body] = await turn(async () => {", self.s)
        self.assertIn("const res = await turn(async () => {", self.s)
        self.assertEqual(self.s.count("readClock();"), 2)

    def test_sessions_537_and_499_stand(self):
        self.assertIn("const rows = await askAgainOnFailure(() => restPages<T>(table, query, revalidate, max, together));", self.s)
        self.assertIn("const rows = await askAgainOnFailure(() => restPages<T>(table, publicRowsQuery(query), revalidate, max, together));", self.s)
        self.assertIn("return askAgainOnFailure(() => countOf(table, query, revalidate));", self.s)
        # session 589: main carries session 562's form of the same count (chain 023 landed by session 563)
        self.assertIn("return restCountRaw(table, licenseHold(query).byRow ? publicRowsQuery(query) : query, revalidate);", self.s)

    def test_the_timing_writes_no_file_and_sends_nothing(self):
        t = self.s[self.s.index("function readLine("):]
        t = t[:t.index("\n}\n")]
        self.assertIn("console.log(`[erw-read] ${JSON.stringify({ kind, table, query: qs.toString(), status, range, ms })}`);", t)
        self.assertNotIn("fs", re.sub(r"[^a-zA-Z]", " ", t).split())
        self.assertNotIn("headers:", t)   # the key never reaches the line
        self.assertNotIn('from "node:fs"', self.s)


class TheMigration(unittest.TestCase):
    def test_036_is_indexes_only_and_has_its_rollback(self):
        names = [n for n in os.listdir(MIG) if n.startswith("036_")]
        self.assertEqual(len(names), 1, names)
        m = src("warehouse", "supabase", "migrations", names[0])
        body = "\n".join(l for l in m.splitlines() if not l.strip().startswith("--")).lower()
        stmts = [s.strip() for s in body.split(";") if s.strip()]
        self.assertTrue(stmts)
        for s in stmts:
            self.assertTrue(s.startswith("create index if not exists") or s.startswith("analyze "), s)
        self.assertIn("not applied", m)
        r = src("warehouse", "supabase", "rollbacks", names[0])
        rbody = "\n".join(l for l in r.splitlines() if not l.strip().startswith("--")).lower()
        created = re.findall(r"create index if not exists (\w+)", body)
        dropped = re.findall(r"drop index if exists public\.(\w+)", rbody)
        self.assertEqual(sorted(created), sorted(dropped))
        self.assertNotIn(chr(0x2014), m + r)


class NoEmDash(unittest.TestCase):
    def test_files_of_this_session(self):
        for p in (("site", "lib", "supabase.ts"), ("site", "scripts", "test-read-timing.mjs"), ("site", "scripts", "slow-reads.mjs"),
                  ("docs", "reviews", "slow-reads-2026-10-22.md")):
            self.assertNotIn(chr(0x2014), src(*p), p)


if __name__ == "__main__":
    unittest.main()

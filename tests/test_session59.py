"""Session 59: the machines. The data lock's rule (warehouse/lock.py), the queue (scripts/taskqueue.py: task files, the
log, a claim race between two clones of one origin, finishing with a report and the day's summary), the worker's parsing
of Claude's result and of a usage limit (scripts/worker.py), sync's row count (scripts/sync.py), the starter export's
suspect rule (warehouse/exports/redivis_starter.py), and the unsubscribe route's two steps. No network: the race runs
against a bare repository in a temporary folder."""

import importlib
import os
import shutil
import subprocess
import sys
import tempfile
import unittest
from unittest import mock

ROOT = os.path.abspath(os.path.join(os.path.dirname(os.path.abspath(__file__)), ".."))
sys.path.insert(0, os.path.join(ROOT, "scripts"))
sys.path.insert(0, os.path.join(ROOT, "warehouse"))
sys.path.insert(0, os.path.join(ROOT, "warehouse", "exports"))

import lock  # noqa: E402
import taskqueue as tq  # noqa: E402
import worker  # noqa: E402

TASK = """---
role: code
spend_cap_usd: 3   # dollars
timeout_minutes: 90
permission_mode: auto
---
# Fix the thing

Do the thing, completely.
"""


def run(cwd, *args):
    subprocess.run(list(args), cwd=cwd, check=True, capture_output=True, text=True)


class LockRule(unittest.TestCase):
    def test_exempt_and_outside_output(self):
        with mock.patch.dict(os.environ, {"ERW_LOCK_EXEMPT": "1"}):
            lock.require(os.path.join(ROOT, "warehouse", "output", "x.csv"))  # passes
        with mock.patch.dict(os.environ, {"ERW_LOCK_EXEMPT": ""}), mock.patch.object(sys, "argv", ["connector.py"]):
            lock.require(os.path.join(tempfile.gettempdir(), "x.csv"))  # not a data write

    def test_refuses_without_the_lock(self):
        env = {"ERW_LOCK_EXEMPT": "", "ERW_LOCK_TOKEN": ""}
        with mock.patch.dict(os.environ, env), mock.patch.object(sys, "argv", ["connector.py"]), \
                mock.patch.object(lock, "token", return_value=None):
            with self.assertRaises(SystemExit) as c:
                lock.require(os.path.join(ROOT, "warehouse", "output", "x.csv"), "writing x")
            self.assertIn("refuses to run without the data lock", str(c.exception))

    def test_expired_lock_refuses(self):
        with mock.patch.dict(os.environ, {"ERW_LOCK_EXEMPT": ""}), mock.patch.object(sys, "argv", ["load.py"]), \
                mock.patch.object(lock, "token", return_value="t-expired"), mock.patch.object(lock, "rpc", return_value=False):
            with self.assertRaises(SystemExit):
                lock.require(what="the Supabase load")

    def test_code_machine_cannot_take_it(self):
        with mock.patch.object(lock, "machine", return_value={"name": "portable", "role": "code"}):
            with self.assertRaises(SystemExit) as c:
                lock.acquire("x")
            self.assertIn("only a data machine", str(c.exception))


class TaskFiles(unittest.TestCase):
    def setUp(self):
        self.d = tempfile.mkdtemp()
        os.makedirs(os.path.join(self.d, "todo"))
        self.p = os.path.join(self.d, "todo", "007-code-fix-thing.md")
        open(self.p, "w", encoding="utf-8").write(TASK)

    def tearDown(self):
        shutil.rmtree(self.d, ignore_errors=True)

    def test_parse(self):
        t = tq.Task(self.p)
        self.assertEqual((t.id, t.role, t.slug, t.cap, t.timeout, t.mode), ("007", "code", "fix-thing", 3.0, 90, "auto"))
        self.assertEqual(t.branch, "task/007-fix-thing")
        self.assertTrue(t.prompt.startswith("# Fix the thing"))

    def test_log_and_claim(self):
        t = tq.Task(self.p)
        t.text = t.with_log("2026-10-01T10:00:00Z claimed by home-laptop")
        t.text = t.with_log("2026-10-01T11:00:00Z requeued by lab: stale")
        t.text = t.with_log("2026-10-01T12:00:00Z claimed by lab")
        who, when = t.last_claim()
        self.assertEqual(who, "lab")
        self.assertEqual(when.hour, 12)
        self.assertNotIn("Queue log", t.prompt)
        t.text = t.with_log("2026-10-01T13:00:00Z done on lab", extra="## Report\n\n- Status: done")
        self.assertTrue(t.text.rstrip().endswith("- Status: done"))
        self.assertEqual(len(t.log_lines()), 4)

    def test_role_mismatch_and_bad_name(self):
        open(self.p, "w", encoding="utf-8").write(TASK.replace("role: code", "role: data"))
        with self.assertRaises(ValueError):
            tq.Task(self.p)
        bad = os.path.join(self.d, "todo", "7-other-x.md")
        open(bad, "w").write(TASK)
        with self.assertRaises(ValueError):
            tq.Task(bad)


class QueueFiles(unittest.TestCase):
    def test_every_task_parses(self):
        for s in tq.STATES:
            d = os.path.join(ROOT, "queue", s)
            for f in (os.listdir(d) if os.path.isdir(d) else []):
                if f.endswith(".md"):
                    t = tq.Task(os.path.join(d, f))  # a bad name, role or front matter raises
                    self.assertGreater(t.cap, 0, f)
                    self.assertGreater(len(t.prompt), 200, f)


class ClaimRace(unittest.TestCase):
    """Two machines claim the same task: the one that pushes first gets it, the other moves on to the next task."""

    def setUp(self):
        self.d = tempfile.mkdtemp()
        self.origin = os.path.join(self.d, "origin.git")
        run(self.d, "git", "init", "-q", "--bare", "-b", "main", self.origin)
        self.a, self.b = os.path.join(self.d, "a"), os.path.join(self.d, "b")
        run(self.d, "git", "clone", "-q", self.origin, self.a)
        for c in (self.a,):
            run(c, "git", "config", "user.name", "t")
            run(c, "git", "config", "user.email", "t@example.invalid")
            run(c, "git", "switch", "-q", "-c", "main")
        os.makedirs(os.path.join(self.a, "queue", "todo"))
        for n in ("001-code-first", "002-code-second", "003-data-third"):
            open(os.path.join(self.a, "queue", "todo", n + ".md"), "w", encoding="utf-8").write(TASK.replace("role: code", "role: " + n.split("-")[1]))
        run(self.a, "git", "add", "-A")
        run(self.a, "git", "commit", "-q", "-m", "tasks")
        run(self.a, "git", "push", "-q", "origin", "main")
        run(self.d, "git", "clone", "-q", self.origin, self.b)
        run(self.b, "git", "config", "user.name", "t")
        run(self.b, "git", "config", "user.email", "t@example.invalid")

    def tearDown(self):
        shutil.rmtree(self.d, ignore_errors=True)

    def at(self, clone):
        return mock.patch.multiple(tq, ROOT=clone, Q=os.path.join(clone, "queue"))

    def test_race_and_finish(self):
        real_sync = tq.sync_main
        with self.at(self.a):
            a_task = tq.claim("code", "machine-a", log=lambda m: None)
        self.assertEqual(a_task.file, "001-code-first.md")
        calls = []

        def stale_then_real():  # B read the queue before A's push landed
            calls.append(1)
            if len(calls) > 1:
                real_sync()
        msgs = []
        with self.at(self.b), mock.patch.object(tq, "sync_main", side_effect=stale_then_real):
            b_task = tq.claim("code", "machine-b", log=msgs.append)
        self.assertTrue(any("lost the race for 001-code-first.md" in m for m in msgs), msgs)
        self.assertEqual(b_task.file, "002-code-second.md")
        with self.at(self.b):
            self.assertEqual([t.file for t in tq.tasks("doing")], ["001-code-first.md", "002-code-second.md"])
            self.assertEqual(tq.find("001").last_claim()[0], "machine-a")
            self.assertIsNone(tq.claim("code", "machine-b", log=lambda m: None))  # nothing left for code
            done = tq.finish(tq.find("002"), "done", "## Report\n\n- Status: done", "machine-b", "12:00 002-code-second.md: done")
        self.assertEqual(done.state, "done")
        with self.at(self.a):
            tq.sync_main()
            self.assertEqual([t.file for t in tq.tasks("done")], ["002-code-second.md"])
            self.assertIn("## Report", tq.find("002").text)
            summ = os.listdir(os.path.join(self.a, "queue", "summary"))
            self.assertEqual(len(summ), 1)
            self.assertTrue(summ[0].endswith("-machine-b.md"))

    def test_stale_goes_back(self):
        with self.at(self.a):
            t = tq.claim("code", "machine-a", log=lambda m: None)
            t.text = t.text.replace("claimed by machine-a", "claimed by machine-a")  # claimed just now: within the grace
            with mock.patch.object(tq, "heartbeat_status", return_value=None):
                self.assertEqual(tq.requeue_stale("machine-b", log=lambda m: None), [])  # too new
                with mock.patch.object(tq, "GRACE_MINUTES", -1):
                    self.assertEqual(tq.requeue_stale("machine-b", log=lambda m: None, skip_holder="machine-a"), [])
                    self.assertEqual(tq.requeue_stale("machine-b", log=lambda m: None), ["001-code-first.md"])
            with mock.patch.object(tq, "heartbeat_status", side_effect=RuntimeError("no network")), mock.patch.object(tq, "GRACE_MINUTES", -1):
                tq.claim("code", "machine-a", log=lambda m: None)
                self.assertEqual(tq.requeue_stale("machine-b", log=lambda m: None), [])  # without Supabase, nothing is stale
            self.assertIn("requeued by machine-b", tq.find("001").text)


class WorkerParsing(unittest.TestCase):
    def test_result_json(self):
        out = 'some log line\n{"type":"result","subtype":"success","is_error":false,"result":"ok","total_cost_usd":0.42,"session_id":"s1"}\n'
        r = worker.parse_result(out)
        self.assertEqual((r["result"], r["total_cost_usd"], r["session_id"]), ("ok", 0.42, "s1"))
        self.assertEqual(worker.parse_result("not json"), {})

    def test_usage_limit(self):
        self.assertTrue(worker.USAGE_RE.search("Claude AI usage limit reached|1790000000"))
        self.assertTrue(worker.USAGE_RE.search("You've hit your limit · resets 3pm"))
        self.assertFalse(worker.USAGE_RE.search("Built the page; tests pass."))
        with mock.patch.dict(os.environ, {"ERW_USAGE_WAIT_SECONDS": ""}):
            self.assertEqual(worker.reset_wait("no time given"), 1800)
            with mock.patch.object(worker.time, "time", return_value=1_790_000_000):
                self.assertEqual(worker.reset_wait("usage limit reached|1790003600"), 3660)
                self.assertEqual(worker.reset_wait("usage limit reached|1790000001"), 300)

    def test_run_claude_pauses_then_resumes(self):
        t = tq.Task.__new__(tq.Task)
        t.cap, t.timeout, t.mode, t.file = 1.0, 5, "auto", "001-code-x.md"
        stub = [sys.executable, os.path.join(ROOT, "tests", "worker_stub.py")]
        env = {**os.environ, "ERW_QUEUE_TASK": "unit-" + str(os.getpid())}
        with mock.patch.dict(os.environ, {"ERW_USAGE_WAIT_SECONDS": "0"}):
            status, res, spent, pauses = worker.run_claude(t, stub, "STUB: usage-limit-once\n", env, beat=None)
        self.assertEqual((status, pauses), ("done", 1))
        self.assertIn("resumed after a usage limit", res["result"])


class SyncRows(unittest.TestCase):
    def test_local_rows(self):
        sync = importlib.import_module("sync")
        p = os.path.join(tempfile.mkdtemp(), "t.csv")
        open(p, "w", encoding="utf-8").write("# Source: x, https://e.org/a#b\n# Retrieved: now\nentity,value\na,1\nb,2\n")
        self.assertEqual(sync.local_rows(p), 2)


class StarterSuspect(unittest.TestCase):
    def test_rule(self):
        import pandas as pd
        import redivis_starter as rs
        t = pd.Series(pd.date_range("2020-07-13", periods=7, freq="h", tz="UTC"))
        mw = pd.Series([128_000, 128_526, 224_345, 122_315, 120_000, 0, 119_000])
        self.assertEqual(rs.suspect(t, mw).tolist(), [False, False, True, False, False, True, False])


class Unsubscribe(unittest.TestCase):
    def test_get_changes_nothing(self):
        with open(os.path.join(ROOT, "site", "app", "api", "unsubscribe", "route.ts"), encoding="utf-8") as f:
            src = f.read()
        get = src[src.index("export async function GET"):src.index("export async function POST")]
        self.assertNotIn("run(", get)  # a GET (a mail scanner following the link) unsubscribes no one
        self.assertIn('confirm: "1"', get)
        self.assertIn('form.get("confirm") === "yes"', src)
        self.assertIn("List-Unsubscribe=One-Click", src)


if __name__ == "__main__":
    unittest.main()

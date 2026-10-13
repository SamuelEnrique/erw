"""Session 188: the chain queue (scripts/chain_queue.py; queue/README.md).

Energy Research Warehouse (ERW). What is held to:

  queue/next/NNN-<slug>.md are taken in the order of their numbers; a name that is not one, and a name of session 59's
    task queue (NNN-code-, NNN-data-), is left where it is and never run;
  `next` moves the first file to queue/done/ in one commit that holds that move and nothing else (in a repository made
    for the test), and prints the file's new path last;
  with nothing waiting it writes one row to the health table through the injected writer (step idle, a status the
    table accepts), sends one line through the injected sender, takes the machine off duty and exits 3;
  a dry run moves, commits, writes and sends nothing.

No test here writes to Supabase, sends anything or reaches a network; the environment is read, never set.

    python -m unittest tests.test_session188_queue -v
"""

import datetime as dt
import os
import shutil
import subprocess
import sys
import tempfile
import unittest
from unittest import mock

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
sys.path.insert(0, os.path.join(ROOT, "scripts"))
sys.path.insert(0, os.path.join(ROOT, "warehouse"))
import chain_queue as cq  # noqa: E402

UTC = dt.timezone.utc
EM = chr(0x2014)
NOW = dt.datetime(2026, 10, 11, 6, 12, tzinfo=UTC)
GIT = shutil.which("git")


def src(*parts):
    with open(os.path.join(ROOT, *parts), encoding="utf-8") as f:
        return f.read()


def read(*parts):
    with open(os.path.join(*parts), encoding="utf-8") as f:
        return f.read()


def git(cwd, *args):
    r = subprocess.run(["git", *args], cwd=cwd, capture_output=True, text=True, stdin=subprocess.DEVNULL)
    if r.returncode != 0:
        raise AssertionError(f"git {' '.join(args)}: {r.stderr or r.stdout}")
    return r.stdout


class Folder(unittest.TestCase):
    """A stand-in repository root with a queue in it."""

    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory(ignore_cleanup_errors=True)
        self.root = self.tmp.name
        os.makedirs(os.path.join(self.root, "queue", "next"))
        os.makedirs(os.path.join(self.root, "queue", "done"))
        self.rows, self.sent, self.offs, self.printed = [], [], [], []

    def tearDown(self):
        self.tmp.cleanup()

    def put(self, name, text="# A chain\n\nRun it.\n", where="next"):
        with open(os.path.join(self.root, "queue", where, name), "w", encoding="utf-8", newline="\n") as f:
            f.write(text)

    def take(self, **kw):
        def rec(step, status, reason, wf):
            self.rows.append((step, status, reason, wf))
            return True

        def send(subject, line, dry_run=False):
            self.sent.append((subject, line, dry_run))
            return 2

        def off():
            self.offs.append(1)
            return "test-laptop is off duty"
        kw.setdefault("rec", rec)
        kw.setdefault("send", send)
        kw.setdefault("off", off)
        kw.setdefault("held", lambda: {"token": "t", "what": "session 188"})   # session 243: the machine was on duty
        kw.setdefault("mover", lambda name, who, root: (shutil.move(os.path.join(root, "queue", "next", name), os.path.join(root, "queue", "done", name)), f"queue/done/{name}")[1])
        return cq.take(root=self.root, who="test-laptop", now=NOW, out=self.printed.append, **kw)


class TheOrder(Folder):
    def test_files_are_taken_in_the_order_of_their_numbers(self):
        for name in ("100-later.md", "002-second.md", "010-third.md", "001-first.md", "1000-last.md"):
            self.put(name)
        good, odd = cq.waiting(self.root)
        self.assertEqual(good, ["001-first.md", "002-second.md", "010-third.md", "100-later.md", "1000-last.md"])
        self.assertEqual(odd, [])

    def test_a_name_that_is_not_this_queues_is_left_and_never_run(self):
        for name in ("001-chain.md", "notes.md", "2-short.md", "003-Upper.md", "004-code-fix-x.md", "005-data-pull-y.md", "006-ok.txt", "README.md", ".gitkeep", "_draft.md"):
            self.put(name)
        os.makedirs(os.path.join(self.root, "queue", "next", "007-a-folder.md"))
        good, odd = cq.waiting(self.root)
        self.assertEqual(good, ["001-chain.md"])
        self.assertEqual(odd, ["003-Upper.md", "004-code-fix-x.md", "005-data-pull-y.md", "006-ok.txt", "2-short.md", "notes.md"])

    def test_no_folder_is_an_empty_queue(self):
        shutil.rmtree(os.path.join(self.root, "queue", "next"))
        self.assertEqual(cq.waiting(self.root), ([], []))

    def test_the_task_queue_never_reads_a_chain_file_and_this_queue_never_takes_a_task(self):
        import taskqueue
        for name in ("188-plumbing.md", "190-night-of-12-october.md"):
            self.assertIsNone(taskqueue.NAME_RE.match(name), name)
            self.assertIsNotNone(cq.NAME_RE.match(name), name)
        for name in os.listdir(os.path.join(ROOT, "queue", "todo")) + os.listdir(os.path.join(ROOT, "queue", "done")):
            if taskqueue.NAME_RE.match(name):
                self.assertIsNotNone(cq.TASK_RE.match(name), f"{name} is a task's name and must be refused here")


class TheNextStep(Folder):
    def test_a_waiting_file_is_moved_and_its_path_is_the_last_line(self):
        self.put("002-b.md")
        self.put("001-a.md", "# First\n")
        code = self.take()
        self.assertEqual(code, 0)
        path = self.printed[-1]
        self.assertEqual(os.path.normcase(path), os.path.normcase(os.path.join(self.root, "queue", "done", "001-a.md")))
        self.assertEqual(read(path), "# First\n", "the file is the prompt as it was written")
        self.assertFalse(os.path.exists(os.path.join(self.root, "queue", "next", "001-a.md")))
        self.assertIn("taken: 001-a.md by test-laptop (1 more waiting)", self.printed[-2])
        self.assertEqual((self.rows, self.sent, self.offs), ([], [], []), "a machine with work is not idle")

    def test_nothing_waiting_is_idle_recorded_said_and_off_duty(self):
        code = self.take()
        self.assertEqual(code, cq.IDLE_EXIT)
        self.assertEqual(cq.IDLE_EXIT, 3)
        # session 243, the email rule: the row is what the chain watch reads 15 minutes later; nothing is emailed here
        self.assertEqual(self.rows, [("idle", "ok", 'ready for review: queue/next/ is empty: test-laptop has nothing left to run after "session 188"', "local:test-laptop")])
        self.assertEqual(self.sent, [], "the idle step emails nothing: the machine's one line goes 15 minutes later, from the chain watch")
        self.assertIn("the one email follows 15 minutes from now", self.printed[-2])
        self.assertEqual(self.offs, [1], "a machine that declared idle is off duty: the idle alarm does not also report it")
        # asked again, off duty: idle already. The row does not begin with the mark, so no second line follows
        self.rows.clear()
        self.assertEqual(self.take(held=lambda: None), 3)
        self.assertEqual(self.rows, [("idle", "ok", "queue/next/ is empty: test-laptop has nothing left to run (it was not on duty: idle already, no line follows)", "local:test-laptop")])
        self.assertFalse(self.rows[0][2].startswith(cq.alert.READY_MARK))
        self.assertEqual(self.sent, [])

    def test_only_odd_names_waiting_is_idle_and_the_line_counts_them(self):
        self.put("004-code-fix-x.md")
        self.put("notes.md")
        code = self.take()
        self.assertEqual(code, 3)
        self.assertIn("left where they are: 004-code-fix-x.md, notes.md", self.printed[0])
        self.assertIn("queue/next/ is empty (2 files there with a name this queue does not take)", self.rows[0][2])
        self.assertTrue(os.path.exists(os.path.join(self.root, "queue", "next", "notes.md")))

    def test_a_dry_run_moves_writes_and_sends_nothing(self):
        self.put("001-a.md")
        code = self.take(dry_run=True)
        self.assertEqual(code, 0)
        self.assertTrue(os.path.exists(os.path.join(self.root, "queue", "next", "001-a.md")))
        self.assertIn("would take queue/next/001-a.md", self.printed[-1])
        os.remove(os.path.join(self.root, "queue", "next", "001-a.md"))
        code = self.take(dry_run=True)
        self.assertEqual(code, 3)
        self.assertEqual((self.rows, self.offs), ([], []))
        self.assertEqual(self.sent, [], "session 243: no sender is asked for anything")
        self.assertIn("would write to erw_health: step idle, status ok, workflow local:test-laptop", self.printed[1])
        self.assertIn("would send nothing here (the email rule, session 243)", self.printed[2])

    def test_a_row_or_a_line_that_fails_is_said_and_the_rest_still_happens(self):
        def no_line(subject, line, dry_run=False):
            raise RuntimeError("Resend HTTP 500 after 0 of 2 sent")
        with mock.patch("sys.stderr"):
            code = self.take(rec=lambda *a: False, send=no_line)
        self.assertEqual(code, 1, "a row that was not written is the failure now: without it no line follows")
        self.assertEqual(self.offs, [1])

    def test_the_idle_row_goes_through_health_pys_own_writer_with_a_status_the_table_accepts(self):
        import health
        with mock.patch.object(health, "record", return_value=True) as record:
            self.assertTrue(cq.health_row("idle", "ok", "queue/next/ is empty", "local:test-laptop"))
        record.assert_called_once_with("idle", "ok", "queue/next/ is empty", 0, wf="local:test-laptop")
        table = src("warehouse", "supabase", "migrations", "017_health.sql")
        self.assertIn("status in ('ok', 'skipped', 'retried', 'failed')", table, "the table's own list of statuses: idle is a step, not a status")
        self.assertIn("step text not null", table)


@unittest.skipUnless(GIT, "no git on this machine")
class TheMoveIsOneCommit(Folder):
    def setUp(self):
        super().setUp()
        git(self.root, "init", "-q")
        git(self.root, "config", "user.name", "A Test")
        git(self.root, "config", "user.email", "test@example.invalid")
        git(self.root, "config", "commit.gpgsign", "false")
        git(self.root, "config", "core.hooksPath", os.path.join(self.root, "no-hooks"))
        self.put("001-a.md", "# First\n")
        self.put("002-b.md", "# Second\n")
        self.put("000-before.md", "# Taken earlier\n", where="done")
        with open(os.path.join(self.root, "other.txt"), "w", encoding="utf-8") as f:
            f.write("one\n")
        git(self.root, "add", "-A")
        git(self.root, "commit", "-q", "-m", "start")

    def test_a_tracked_file_moves_in_a_commit_of_that_move_alone(self):
        with open(os.path.join(self.root, "other.txt"), "w", encoding="utf-8") as f:
            f.write("two\n")
        git(self.root, "add", "other.txt")   # something else staged by the session: it must stay out of the commit
        before = git(self.root, "rev-list", "--count", "HEAD").strip()
        dst = cq.move("001-a.md", "test-laptop", root=self.root)
        self.assertEqual(dst, "queue/done/001-a.md")
        self.assertEqual(int(git(self.root, "rev-list", "--count", "HEAD")) - int(before), 1, "one commit")
        self.assertEqual(git(self.root, "show", "--name-status", "-M", "--format=%s", "HEAD").split("\n\n", 1)[1].split(),
                         ["R100", "queue/next/001-a.md", "queue/done/001-a.md"])
        self.assertEqual(git(self.root, "log", "-1", "--format=%s").strip(), "Queue: 001-a.md taken by test-laptop (queue/next to queue/done)")
        self.assertEqual(git(self.root, "status", "--porcelain").strip(), "M  other.txt", "what the session had staged is still staged, and not committed")
        self.assertEqual(read(os.path.join(self.root, "queue", "done", "001-a.md")), "# First\n")

    def test_a_file_dropped_in_without_a_commit_is_taken_too(self):
        self.put("003-new.md", "# Dropped in\n")
        dst = cq.move("003-new.md", "test-laptop", root=self.root)
        self.assertEqual(git(self.root, "show", "--name-status", "--format=%s", "HEAD").split("\n\n", 1)[1].split(), ["A", dst])
        self.assertFalse(os.path.exists(os.path.join(self.root, "queue", "next", "003-new.md")))
        self.assertEqual(git(self.root, "status", "--porcelain").strip(), "")

    def test_a_name_already_taken_is_refused_and_nothing_moves(self):
        self.put("000-before.md", "# Again\n")
        with self.assertRaises(RuntimeError) as e:
            cq.move("000-before.md", "test-laptop", root=self.root)
        self.assertIn("already exists", str(e.exception))
        self.assertTrue(os.path.exists(os.path.join(self.root, "queue", "next", "000-before.md")))
        self.assertEqual(read(os.path.join(self.root, "queue", "done", "000-before.md")), "# Taken earlier\n")

    def test_next_takes_the_files_one_after_another_and_then_says_idle(self):
        codes = [self.take(mover=cq.move), self.take(mover=cq.move), self.take(mover=cq.move)]
        self.assertEqual(codes, [0, 0, 3])
        self.assertEqual(sorted(os.listdir(os.path.join(self.root, "queue", "done"))), ["000-before.md", "001-a.md", "002-b.md"])
        self.assertEqual(git(self.root, "rev-list", "--count", "HEAD").strip(), "3")
        self.assertEqual(len(self.rows), 1)


class TheDocuments(unittest.TestCase):
    def test_the_readme_describes_both_queues(self):
        readme = src("queue", "README.md")
        for word in ("queue/next/", "queue/done/", "queue/todo/", "queue/doing/", "queue/summary/", "python scripts/chain_queue.py next", "python scripts/taskqueue.py",
                     "NNN-<slug>.md", "NNN-<role>-<slug>.md", "CHAIN_TEMPLATE.md", "idle"):
            self.assertIn(word, readme, word)
        self.assertNotIn(EM, readme)

    def test_the_template_is_not_taken_as_a_prompt_and_the_folder_is_in_git(self):
        self.assertIsNone(cq.NAME_RE.match("CHAIN_TEMPLATE.md"))
        self.assertTrue(os.path.isdir(os.path.join(ROOT, "queue", "next")), "queue/next/ must exist in a fresh clone")
        self.assertEqual(cq.waiting(ROOT)[1], [], "nothing in queue/next/ has a name the queue does not take")

    def test_the_machines_document_says_what_idle_does(self):
        doc = src("docs", "machines.md")
        for word in ("python scripts/chain_queue.py next", "queue/next/", "step `idle`", "exit 3"):
            self.assertIn(word, doc, word)


if __name__ == "__main__":
    unittest.main()

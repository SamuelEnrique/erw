"""Session 365: the chain queue knows which machine a prompt file is for (scripts/chain_queue.py; queue/README.md).

Energy Research Warehouse (ERW). What is held to, each in a git repository made for the test, never the repository's
own queue, with the machine's role handed in and every health row, sign-off and duty mark a stand-in:

  a file marked `machine: data` is left by a code machine, and named in what `next` prints and in the idle line;
  a file with no such line is taken by any machine;
  a matching file is taken in the order of the numbers, past a lower-numbered file left for the other machine;
  a machine whose role is not known takes only files with no line;
  `next --file <name>` takes that one file with the same move and commit; it refuses a name not in queue/next/, a
    name of the task queue, and a file marked for the other role (nothing moves); a dry run moves nothing;
  `list` shows each file's machine;
  with nothing for this machine and the planner on, the planner still drafts, and its chain is the one taken.

No test here writes to Supabase, sends anything or reaches a network; the environment is read, never set.

    python -m unittest tests.test_session365 -v
"""

import datetime as dt
import os
import shutil
import subprocess
import sys
import tempfile
import unittest

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
sys.path.insert(0, os.path.join(ROOT, "scripts"))
sys.path.insert(0, os.path.join(ROOT, "warehouse"))
import chain_queue as cq  # noqa: E402
import planner  # noqa: E402

UTC = dt.timezone.utc
EM = chr(0x2014)
NOW = dt.datetime(2026, 10, 12, 14, 30, tzinfo=UTC)     # inside the sample roadmap's start hours
GIT = shutil.which("git")
SAMPLE = os.path.join(ROOT, "tests", "fixtures", "roadmap_sample.md")


def src(*parts):
    with open(os.path.join(ROOT, *parts), encoding="utf-8") as f:
        return f.read()


def git(cwd, *args):
    r = subprocess.run(["git", *args], cwd=cwd, capture_output=True, text=True, stdin=subprocess.DEVNULL)
    if r.returncode != 0:
        raise AssertionError(f"git {' '.join(args)}: {r.stderr or r.stdout}")
    return r.stdout


def chain(title, machine=None):
    """A prompt file as the template shapes it: the title, then the machine's line when there is one."""
    return f"# {title}\n\n" + (f"machine: {machine}\n\n" if machine else "") + "Run it.\n"


@unittest.skipUnless(GIT, "no git on this machine")
class Repo(unittest.TestCase):
    """A repository made for the test, with a queue in it and every file committed."""

    files = {}

    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory(ignore_cleanup_errors=True)
        self.root = self.tmp.name
        for d in ("next", "done"):
            os.makedirs(os.path.join(self.root, "queue", d))
        git(self.root, "init", "-q")
        git(self.root, "config", "user.name", "A Test")
        git(self.root, "config", "user.email", "test@example.invalid")
        git(self.root, "config", "commit.gpgsign", "false")
        git(self.root, "config", "core.hooksPath", os.path.join(self.root, "no-hooks"))
        for name, text in self.files.items():
            self.put(name, text)
        with open(os.path.join(self.root, "queue", "done", ".keep"), "w", encoding="utf-8") as f:
            f.write("")
        git(self.root, "add", "-A")
        git(self.root, "commit", "-q", "-m", "start")
        self.printed, self.rows, self.offs = [], [], []

    def tearDown(self):
        self.tmp.cleanup()

    def put(self, name, text):
        with open(os.path.join(self.root, "queue", "next", name), "w", encoding="utf-8", newline="\n") as f:
            f.write(text)

    def next_(self, role="code", **kw):
        self.printed = []

        def rec(step, status, reason, wf):
            self.rows.append((step, status, reason, wf))
            return True

        def off():
            self.offs.append(1)
            return "testbox is off duty"
        kw.setdefault("planner", None)
        return cq.take(root=self.root, who="testbox", now=NOW, out=self.printed.append, rec=rec, off=off,
                       held=lambda: {"token": "t", "what": "session 365"}, role=role, mover=cq.move, **kw)

    def said(self):
        return "\n".join(str(x) for x in self.printed)

    def waiting(self):
        return sorted(os.listdir(os.path.join(self.root, "queue", "next")))

    def taken(self):
        return sorted(f for f in os.listdir(os.path.join(self.root, "queue", "done")) if not f.startswith("."))

    def commits(self):
        return int(git(self.root, "rev-list", "--count", "HEAD"))


class TheMark(unittest.TestCase):
    def test_the_line_is_read_in_the_first_ten_lines_only(self):
        self.assertEqual(cq.mark_of(chain("A chain", "data")), "data")
        self.assertEqual(cq.mark_of("# A chain\n\nMachine:  Code \n"), "code")
        self.assertIsNone(cq.mark_of(chain("A chain")))
        self.assertIsNone(cq.mark_of("# A chain\n" + "\n" * 10 + "machine: data\n"), "a line past the first ten is the body's, not the file's mark")
        self.assertEqual(cq.mark_of("# A chain\n\nmachine: <code or data>\n"), "<code or data>")
        self.assertIsNone(cq.mark_of("# A chain\n\nThe machine: code runs it.\n"), "a sentence that says machine: is not the line")

    def test_the_repositorys_own_chain_files_carry_the_line(self):
        # the two chains of 20 October, the forms the line was written in first
        self.assertEqual(cq.mark_of(src("queue", "done", "012-day-20-october-code.md")), "code")


class ACodeMachineLeavesADataFile(Repo):
    files = {"011-day-data.md": chain("Data chain", "data"), "012-day-any.md": chain("Any machine's chain"), "013-day-code.md": chain("Code chain", "code")}

    def test_the_data_file_is_left_and_named_and_the_file_with_no_line_is_taken(self):
        before = self.commits()
        self.assertEqual(self.next_(), 0, self.said())
        self.assertEqual(self.taken(), ["012-day-any.md"], "the lowest-numbered file for this machine: no line is any machine's")
        self.assertIn("011-day-data.md", self.waiting())
        self.assertIn("for another machine (testbox is a code machine), left where they are: 011-day-data.md (machine: data)", self.said())
        self.assertTrue(str(self.printed[-1]).endswith(os.path.join("queue", "done", "012-day-any.md")))
        self.assertEqual(self.commits() - before, 1, "the same move in one commit")
        self.assertEqual(git(self.root, "log", "-1", "--format=%s").strip(), "Queue: 012-day-any.md taken by testbox (queue/next to queue/done)")

    def test_a_matching_file_is_taken_in_number_order_past_a_skipped_one(self):
        self.assertEqual(self.next_(), 0)
        self.assertEqual(self.next_(), 0, self.said())
        self.assertEqual(self.taken(), ["012-day-any.md", "013-day-code.md"])
        self.assertEqual(self.waiting(), ["011-day-data.md"])

    def test_when_only_the_other_machines_file_waits_the_idle_line_says_so(self):
        self.next_(), self.next_()
        self.assertEqual(self.next_(), cq.IDLE_EXIT)
        self.assertEqual(self.waiting(), ["011-day-data.md"], "the data file is never moved by a code machine")
        self.assertEqual(len(self.rows), 1)
        reason = self.rows[0][2]
        self.assertTrue(reason.startswith(cq.alert.READY_MARK), reason)
        self.assertIn("queue/next/ holds nothing for testbox (code): 1 file there waits for another machine (011-day-data.md)", reason)
        self.assertEqual(self.offs, [1])

    def test_a_data_machine_takes_the_data_file_first(self):
        self.assertEqual(self.next_(role="data"), 0)
        self.assertEqual(self.taken(), ["011-day-data.md"])
        self.assertIn("013-day-code.md (machine: code)", self.said())

    def test_a_machine_whose_role_is_not_known_takes_only_a_file_with_no_line(self):
        for role in ("", "planner", "Lab"):
            self.assertEqual(self.next_(role=role, dry_run=True), 0)
            self.assertIn("would take queue/next/012-day-any.md", self.said(), role)
            self.assertIn("role is not known", self.said(), role)
        self.assertEqual(self.next_(role=""), 0)
        self.assertEqual(self.next_(role=""), cq.IDLE_EXIT)
        self.assertEqual(self.waiting(), ["011-day-data.md", "013-day-code.md"])

    def test_a_dry_run_names_the_skipped_file_and_moves_nothing(self):
        before = self.commits()
        self.assertEqual(self.next_(dry_run=True), 0)
        self.assertIn("011-day-data.md (machine: data)", self.said())
        self.assertIn("would take queue/next/012-day-any.md", self.said())
        self.assertEqual((self.commits(), len(self.waiting()), self.rows), (before, 3, []))

    def test_a_file_marked_with_this_machines_own_name_is_its(self):
        self.put("010-for-testbox.md", chain("Named", "testbox"))
        self.put("009-for-labbox.md", chain("Named", "labbox"))
        self.assertEqual(self.next_(), 0)
        self.assertEqual(self.taken(), ["010-for-testbox.md"])
        self.assertIn("009-for-labbox.md (machine: labbox)", self.said())


class TakingOneFileByName(Repo):
    files = {"011-day-data.md": chain("Data chain", "data"), "012-day-any.md": chain("Any machine's chain"), "014-later.md": chain("Later", "code")}

    def test_file_takes_the_named_file_with_the_same_move_and_commit(self):
        before = self.commits()
        self.assertEqual(self.next_(file="014-later.md"), 0, self.said())
        self.assertEqual(self.taken(), ["014-later.md"], "the named file, not the lowest-numbered one")
        self.assertEqual(self.commits() - before, 1)
        self.assertEqual(git(self.root, "show", "--name-status", "-M", "--format=%s", "HEAD").split("\n\n", 1)[1].split(),
                         ["R100", "queue/next/014-later.md", "queue/done/014-later.md"])
        self.assertTrue(str(self.printed[-1]).endswith(os.path.join("queue", "done", "014-later.md")))
        self.assertEqual((self.rows, self.offs), ([], []), "taking by name never idles")

    def test_file_accepts_the_path_in_queue_next_and_a_dry_run_moves_nothing(self):
        before = self.commits()
        self.assertEqual(self.next_(file="queue/next/012-day-any.md", dry_run=True), 0)
        self.assertIn("would take queue/next/012-day-any.md by name", self.said())
        self.assertEqual((self.commits(), self.taken()), (before, []))

    def test_file_refuses_an_unknown_name_and_a_task_name_and_moves_nothing(self):
        before = self.commits()
        for name, words in (("099-not-here.md", "there is no 099-not-here.md in queue/next/"), ("015-code-fix-x.md", "a name of the task queue"),
                            ("notes.md", "not a name this queue takes"), ("../done/011-day-data.md", "--file takes a file's name in queue/next/"), ("", "--file takes")):
            self.assertEqual(self.next_(file=name), cq.BAD_INPUT, name)
            self.assertIn(words, self.said(), name)
        self.assertEqual((self.commits(), self.taken(), len(self.waiting())), (before, [], 3))

    def test_file_refuses_a_file_marked_for_the_other_role_unless_the_role_is_not_known(self):
        self.assertEqual(self.next_(file="011-day-data.md"), cq.BAD_INPUT)
        self.assertIn("011-day-data.md is marked machine: data, and testbox is a code machine", self.said())
        self.assertEqual(self.taken(), [])
        self.assertEqual(self.next_(role="", file="011-day-data.md"), 0, self.said())
        self.assertIn("taken because a person named it", self.said())
        self.assertEqual(self.taken(), ["011-day-data.md"])

    def test_the_command_line_takes_file(self):
        calls = []
        real = cq.take
        cq.take = lambda dry_run=False, **kw: calls.append((dry_run, kw)) or 0
        try:
            self.assertEqual(cq.main(["next", "--file", "014-later.md", "--dry-run"]), 0)
            self.assertEqual(cq.main(["list", "--file", "014-later.md"]), cq.BAD_INPUT)
        finally:
            cq.take = real
        self.assertEqual(calls, [(True, {"file": "014-later.md"})])


class TheListShowsMachines(Repo):
    files = {"011-day-data.md": chain("Data chain", "data"), "012-day-any.md": chain("Any machine's chain"), "013-day-code.md": chain("Code chain", "code")}

    def test_list_shows_each_files_machine(self):
        out = []
        self.assertEqual(cq.listing(root=self.root, role="code", who="testbox", out=out.append), 0)
        self.assertEqual(out, ["3 waiting in queue/next/ (2 for testbox, a code machine):",
                               "  011-day-data.md  machine: data  (left for another machine)",
                               "  012-day-any.md  machine: any (no line)",
                               "  013-day-code.md  machine: code"])
        out = []
        cq.listing(root=self.root, role="", who="testbox", out=out.append)
        self.assertIn("(1 for testbox, a machine whose role is not known)", out[0])


class ThePlannerPath(Repo):
    """Nothing for this machine, the planner on: the planner drafts, and its chain, marked for this machine, is taken."""

    files = {"011-day-data.md": chain("Data chain", "data")}

    def setUp(self):
        super().setUp()
        os.makedirs(os.path.join(self.root, "docs"))
        os.makedirs(os.path.join(self.root, "archive", "sessions"))
        shutil.copy(SAMPLE, os.path.join(self.root, "docs", "roadmap.md"))
        shutil.copy(os.path.join(ROOT, "queue", "CHAIN_TEMPLATE.md"), os.path.join(self.root, "queue", "CHAIN_TEMPLATE.md"))
        self.git_calls = []

    def plan(self, who, root, dry_run, out):
        def fake_git(*args, root=None):
            self.git_calls.append(args)
            if args[0] == "push":
                return ""
            return git(self.root, *args)
        stamp = planner.sessions_today
        planner.sessions_today = lambda *a, **k: 0          # the test's repository has no history of sessions to count
        try:
            return cq.plan(who, root, dry_run, out, git=fake_git, role="code", now=NOW)
        finally:
            planner.sessions_today = stamp

    def test_the_planner_drafts_past_the_other_machines_file_and_its_chain_is_taken(self):
        self.assertEqual(self.next_(planner=self.plan), 0, self.said())
        done = self.taken()
        self.assertEqual(len(done), 1)
        self.assertRegex(done[0], r"-planned-")
        with open(os.path.join(self.root, "queue", "done", done[0]), encoding="utf-8") as f:
            self.assertEqual(cq.mark_of(f.read()), "code", "the planner marks its chain for the role it drafted for")
        self.assertEqual(self.waiting(), ["011-day-data.md"])
        self.assertEqual([a[0] for a in self.git_calls], ["add", "commit", "push"])
        self.assertEqual(self.rows, [], "not idle")


class TheDocuments(unittest.TestCase):
    def test_the_template_readme_and_machines_document_say_it(self):
        template = src("queue", "CHAIN_TEMPLATE.md")
        body = template[template.index("\n---\n") + 5:]
        self.assertIn("machine: <code or data>", body.lstrip("\n").split("\n")[2], "the line sits under the title of the part a person copies")
        self.assertIn("The line `machine: code` or `machine: data` under the title (session 365)", template)
        readme = src("queue", "README.md")
        for words in ("**Which machine (session 365):**", "`machine: code` or `machine: data`", "python scripts/chain_queue.py next --file NNN-<slug>.md"):
            self.assertIn(words, readme, words)
        machines = src("docs", "machines.md")
        part = machines[machines.index("### The chain queue: what a machine runs next"):machines.index("### The idle alarm")]
        self.assertIn("**A file says its machine** (session 365)", part)
        for f in ("queue/CHAIN_TEMPLATE.md", "queue/README.md", "docs/machines.md", "scripts/chain_queue.py", "scripts/planner.py", "tests/test_session365.py"):
            self.assertNotIn(EM, src(*f.split("/")), f)


if __name__ == "__main__":
    unittest.main()

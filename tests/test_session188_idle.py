"""Session 188: a machine on duty and the idle alarm (scripts/duty.py, scripts/githooks/, the chain watch's second step).

Energy Research Warehouse (ERW). docs/machines.md, "Continuous work". What is held to:

  a machine goes on duty as one row, duty:<machine>, of erw_locks, through the lock's own functions (no new table, no
    migration); a commit, a push or a beat renews it; declaring idle or signing off removes it;
  the check, with the clock given: quiet under 30 minutes, one line at 30 minutes, again every hour after and not in
    between; a mark that lapsed is said once; each machine on duty is judged by itself;
  one machine's line that cannot be sent does not cost another's; nothing is sent in a dry run;
  the git hooks send a beat on a machine on duty, from its main checkout and from a worktree of it, do nothing on a
    machine that is not, and never fail or hold a commit; the chain's own beat is as it was;
  the workflow's step mirrors the chain's: it runs under warehouse/health.py, after the duplicate-start step, with read
    permissions only.

No test here writes to Supabase, sends anything or reaches a network: the database, the clock and the sender are
stand-ins. The environment is read, never set.

    python -m unittest tests.test_session188_idle -v
"""

import datetime as dt
import json
import os
import shutil
import subprocess
import sys
import tempfile
import time
import types
import unittest

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
sys.path.insert(0, os.path.join(ROOT, "scripts"))
import alert  # noqa: E402
import duty  # noqa: E402

UTC = dt.timezone.utc
EM = chr(0x2014)


def src(*parts):
    with open(os.path.join(ROOT, *parts), encoding="utf-8") as f:
        return f.read()


def load(*parts):
    with open(os.path.join(*parts), encoding="utf-8") as f:
        return json.load(f)


def at(h, m=0, day=11):
    return dt.datetime(2026, 10, day, h, m, tzinfo=UTC)


def a_row(name="old-laptop", acquired=at(5, 0), renewed=None, expires=at(21, 0), task="session 900"):
    return {"name": f"duty:{name}", "holder": name, "task": task, "acquired": acquired, "renewed": renewed or acquired, "expires": expires}


class Locks:
    """A stand-in for the erw_locks functions of migration 016: one row a name, taken only when free or lapsed."""

    def __init__(self):
        self.rows, self.calls, self.n = {}, [], 0

    def __call__(self, fn, **a):
        self.calls.append((fn, a))
        name = a["p_name"]
        if fn == "erw_lock_acquire":
            if name in self.rows:
                return None
            self.n += 1
            self.rows[name] = {"token": f"token-{self.n}", "holder": a["p_holder"], "task": a["p_task"], "minutes": a["p_minutes"]}
            return self.rows[name]["token"]
        held = name in self.rows and self.rows[name]["token"] == a["p_token"]
        if fn == "erw_lock_renew":
            if held:
                self.rows[name]["minutes"] = a["p_minutes"]
            return held
        if fn == "erw_lock_release":
            if held:
                del self.rows[name]
            return held
        raise AssertionError(fn)


class OnDuty(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.state = os.path.join(self.tmp.name, ".erw")
        self.db = Locks()

    def tearDown(self):
        self.tmp.cleanup()

    def test_going_on_duty_is_one_row_of_the_locks_table_named_for_the_machine(self):
        said = duty.start("Old Laptop", "session 900", hours=16, rpc=self.db, state=self.state, now=at(5, 0))
        self.assertEqual(said, 'old-laptop is on duty for "session 900" until 2026-10-11 21:00 UTC')
        self.assertEqual(self.db.calls, [("erw_lock_acquire", {"p_name": "duty:old-laptop", "p_holder": "old-laptop", "p_task": "session 900", "p_minutes": 960})])
        held = load(os.path.join(self.state, "duty.json"))
        self.assertEqual(held, {"token": "token-1", "machine": "old-laptop", "what": "session 900", "started": "2026-10-11T05:00:00+00:00", "until": "2026-10-11T21:00:00+00:00"})
        self.assertEqual(duty.PREFIX, "duty:")
        self.assertNotEqual(duty.row_name("x"), alert.MARK, "not the chain's mark")
        self.assertNotEqual(duty.row_name("data"), "data", "never the data lock's row")

    def test_a_beat_renews_the_mark_for_the_time_it_has_left(self):
        duty.start("old-laptop", "session 900", hours=16, rpc=self.db, state=self.state, now=at(5, 0))
        self.assertTrue(duty.beat(rpc=self.db, state=self.state, now=at(9, 30)))
        self.assertEqual(self.db.calls[-1], ("erw_lock_renew", {"p_name": "duty:old-laptop", "p_token": "token-1", "p_minutes": 690}))
        # a machine that is not on duty sends nothing
        other = os.path.join(self.tmp.name, "other")
        n = len(self.db.calls)
        self.assertFalse(duty.beat(rpc=self.db, state=other))
        self.assertEqual(len(self.db.calls), n)

    def test_a_second_precheck_names_the_new_work(self):
        duty.start("old-laptop", "session 900", rpc=self.db, state=self.state, now=at(5, 0))
        said = duty.start("old-laptop", "session 901", rpc=self.db, state=self.state, now=at(8, 0))
        self.assertIn('on duty for "session 901"', said)
        self.assertIn('it was on duty for "session 900"', said)
        self.assertEqual([c[0] for c in self.db.calls], ["erw_lock_acquire", "erw_lock_release", "erw_lock_acquire"])
        self.assertEqual(self.db.rows["duty:old-laptop"]["task"], "session 901")
        self.assertEqual(load(os.path.join(self.state, "duty.json"))["token"], "token-2")

    def test_a_mark_held_by_another_token_is_not_taken(self):
        self.db.rows["duty:old-laptop"] = {"token": "someone-else", "holder": "old-laptop", "task": "x", "minutes": 60}
        with self.assertRaises(RuntimeError) as e:
            duty.start("old-laptop", "session 900", rpc=self.db, state=self.state, now=at(5, 0))
        self.assertIn("a token this checkout does not hold", str(e.exception))
        self.assertFalse(os.path.exists(os.path.join(self.state, "duty.json")))

    def test_off_duty_removes_the_row_and_the_note(self):
        duty.start("old-laptop", "session 900", rpc=self.db, state=self.state, now=at(5, 0))
        self.assertEqual(duty.off(rpc=self.db, state=self.state), "old-laptop is off duty")
        self.assertEqual(self.db.rows, {})
        self.assertFalse(os.path.exists(os.path.join(self.state, "duty.json")))
        self.assertIn("not on duty", duty.off(rpc=self.db, state=self.state))

    def test_a_worktree_uses_the_main_checkouts_state(self):
        main = os.path.join(self.tmp.name, "main")
        tree = os.path.join(self.tmp.name, "tree")
        os.makedirs(os.path.join(main, ".erw"))
        os.makedirs(tree)
        self.assertEqual(duty.state_dir(tree, main=lambda root: main), os.path.join(main, ".erw"))
        self.assertEqual(duty.state_dir(main, main=lambda root: main), os.path.join(main, ".erw"))
        self.assertEqual(duty.state_dir(tree, main=lambda root: None), os.path.join(tree, ".erw"), "git cannot say: this folder's own")
        self.assertIsNone(duty.machine(os.path.join(tree, ".erw")))


class TheRows(unittest.TestCase):
    ENV = staticmethod(lambda name: {"SUPABASE_URL": "https://abc.supabase.co/rest/v1/", "SUPABASE_SERVICE_KEY": "service-key"}.get(name, ""))

    def test_every_machine_on_duty_is_read_with_the_service_key(self):
        asked = []

        def get(url, headers=None, timeout=None):
            asked.append((url, headers))
            return types.SimpleNamespace(status_code=200, text="", json=lambda: [
                {"name": "duty:old-laptop", "holder": "old-laptop", "task": "session 900", "acquired": "2026-10-11T05:00:00+00:00",
                 "renewed": "2026-10-11T05:40:00.5+00:00", "expires": "2026-10-11T21:00:00Z"},
                {"name": "data", "holder": "x", "task": "y", "acquired": "2026-10-11T05:00:00+00:00", "renewed": None, "expires": "2026-10-11T07:00:00+00:00"}])
        rows = duty.rows(get=get, env=self.ENV)
        self.assertEqual(len(rows), 1, "only duty rows, whatever the database answered")
        self.assertEqual(rows[0]["acquired"], at(5, 0))
        self.assertEqual(rows[0]["expires"], at(21, 0))
        url, headers = asked[0]
        self.assertEqual(url, "https://abc.supabase.co/rest/v1/erw_locks?select=name,holder,task,acquired,renewed,expires&name=like.duty:*&order=name")
        self.assertEqual(headers["apikey"], "service-key")
        self.assertNotIn("token", url, "the tokens are never read")

    def test_a_database_that_does_not_answer_is_an_error_not_silence(self):
        with self.assertRaises(RuntimeError):
            duty.rows(get=lambda *a, **k: types.SimpleNamespace(status_code=401, text="no", json=lambda: None), env=self.ENV)
        with self.assertRaises(RuntimeError):
            duty.rows(get=None, env=lambda name: "")


class TheCheck(unittest.TestCase):
    def test_under_30_minutes_is_quiet(self):
        for now in (at(5, 0), at(5, 15), at(5, 29)):
            subject, why = duty.decide(now, a_row())
            self.assertIsNone(subject, now)
            self.assertIn("ran something", why)

    def test_30_minutes_is_said_once_and_then_every_hour(self):
        row = a_row()
        said = [m for m in range(0, 331) if duty.decide(at(5, 0) + dt.timedelta(minutes=m), row)[0]]
        self.assertEqual(said, [m for start in (30, 90, 150, 210, 270, 330) for m in range(start, start + 15) if m <= 330])
        # the check runs every 15 minutes: whenever it starts, each window is met once
        for offset in range(15):
            ticks = [m for m in range(offset, 331, 15) if duty.decide(at(5, 0) + dt.timedelta(minutes=m), row)[0]]
            self.assertEqual(len(ticks), 6 if offset == 0 else 5, offset)
        subject, line = duty.decide(at(5, 37), row)
        self.assertEqual(subject, "ERW: a machine has run nothing for 30 minutes")
        self.assertEqual(line, 'The machine old-laptop, on duty for "session 900", has run nothing for 37 minutes: its last sign of work was its precheck at 05:00 UTC. '
                               "On duty since 05:00 UTC.")
        subject, line = duty.decide(at(6, 32), row)
        self.assertEqual(subject, "ERW: a machine is still running nothing")
        self.assertIn("for 92 minutes", line)
        self.assertEqual((alert.QUIET_MIN, alert.AGAIN_MIN, alert.EVERY_MIN), (30, 60, 15), "the chain check's own numbers")

    def test_a_commit_a_push_or_a_beat_is_a_sign_of_work(self):
        row = a_row(renewed=at(6, 50))
        self.assertIsNone(duty.decide(at(7, 10), row)[0])
        subject, line = duty.decide(at(7, 25), row)
        self.assertEqual(subject, "ERW: a machine has run nothing for 30 minutes")
        self.assertIn("for 35 minutes: its last sign of work was a commit, a push or a beat at 06:50 UTC. On duty since 05:00 UTC.", line)

    def test_a_mark_that_lapsed_is_said_once(self):
        row = a_row(expires=at(9, 0))
        subject, line = duty.decide(at(9, 10), row)
        self.assertEqual(subject, "ERW: a machine's duty mark lapsed")
        self.assertIn("until 09:00 UTC and never declared idle or signed off", line)
        self.assertIsNone(duty.decide(at(9, 20), row)[0])
        self.assertIsNone(duty.decide(at(9, 0, day=12), row)[0])

    def test_every_line_is_one_line_within_300_characters_without_an_em_dash(self):
        row = a_row(name="m" * 40, task="a very long name of a chain " * 12)
        for now in (at(5, 37), at(6, 32), at(21, 5)):
            subject, line = duty.decide(now, row)
            self.assertIsNotNone(subject)
            self.assertLessEqual(len(line), 300)
            self.assertNotIn("\n", line)
            self.assertNotIn(EM, line)

    def run_check(self, rows, now, send=None, dry_run=False):
        sent, printed = [], []

        def default(subject, line, dry=False):
            sent.append((subject, line, dry))
            return 2
        code = duty.check(dry_run, now=now, read=lambda: rows, send=send or default, out=printed.append)
        return code, sent, printed

    def test_each_machine_is_judged_by_itself(self):
        # at 07:05: one worked ten minutes ago, one is 35 minutes quiet (its first line), one 95 (its second), one 65 (between lines)
        rows = [a_row("a", renewed=at(6, 55)), a_row("b", acquired=at(6, 30)), a_row("c", acquired=at(5, 30)), a_row("d", acquired=at(6, 0))]
        code, sent, printed = self.run_check(rows, at(7, 5))
        self.assertEqual(code, 0)
        self.assertEqual([s[0] for s in sent], ["ERW: a machine has run nothing for 30 minutes", "ERW: a machine is still running nothing"])
        self.assertIn("The machine b,", sent[0][1])
        self.assertIn("The machine c,", sent[1][1])
        self.assertEqual(len([p for p in printed if p.startswith("quiet: ")]), 2)

    def test_the_idle_machine_among_several_is_the_one_named(self):
        rows = [a_row("old-laptop", renewed=at(6, 55)), a_row("video-laptop", acquired=at(6, 30), task="the video chain")]
        code, sent, printed = self.run_check(rows, at(7, 5))
        self.assertEqual((code, len(sent)), (0, 1))
        self.assertIn('The machine video-laptop, on duty for "the video chain", has run nothing for 35 minutes', sent[0][1])
        self.assertFalse(sent[0][2])
        self.assertIn("sent to 2 fixed recipients", printed[-1])
        self.assertIn("quiet: old-laptop ran something 10 minutes ago", printed[0])

    def test_no_machine_on_duty_says_so_and_sends_nothing(self):
        code, sent, printed = self.run_check([], at(7, 5))
        self.assertEqual((code, sent, printed), (0, [], ["quiet: no machine is on duty"]))

    def test_a_dry_run_asks_the_sender_to_print(self):
        code, sent, _ = self.run_check([a_row()], at(5, 40), dry_run=True)
        self.assertEqual((code, [s[2] for s in sent]), (0, [True]))

    def test_one_line_that_fails_does_not_cost_another_and_all_failing_is_exit_1(self):
        rows = [a_row("a"), a_row("b")]
        tried = []

        def one_fails(subject, line, dry=False):
            tried.append(line)
            if "machine a," in line:
                raise RuntimeError("Resend HTTP 500 after 0 of 2 sent")
            return 2
        code, _, printed = self.run_check(rows, at(5, 40), send=one_fails)
        self.assertEqual((code, len(tried)), (0, 2))
        self.assertTrue(any(p.startswith("alert: not sent (RuntimeError") for p in printed))

        def all_fail(subject, line, dry=False):
            raise RuntimeError("not sent: RESEND_API_KEY not set")
        code, _, _ = self.run_check(rows, at(5, 40), send=all_fail)
        self.assertEqual(code, 1, "health.py records it as failed; the job itself still passes")


STAND_IN = ("import os, sys\nopen(os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'asked.txt'), 'a').write(' '.join(sys.argv[1:]) + '\\n')\n"
            "sys.exit(1)\n")  # and fails, as a beat does when the mark is gone: the hook must not care


def wait_for(path, lines, seconds=20):
    for _ in range(seconds * 5):
        if len(said(path)) >= lines:
            break
        time.sleep(0.2)
    return said(path)


def said(path):
    if not os.path.exists(path):
        return []
    with open(path, encoding="utf-8") as f:
        return f.read().splitlines()


class TheGitHooks(unittest.TestCase):
    HOOKS = ("post-commit", "pre-push")

    def setUp(self):
        self.sh = shutil.which("sh") or shutil.which("bash")
        if not self.sh:
            self.skipTest("no sh on this machine")

    def fake(self, d, on_duty, chain=False):
        """A stand-in repository root: the two hooks, and a duty.py and an alert.py that write down what they were asked."""
        os.makedirs(os.path.join(d, "scripts", "githooks"))
        for name in self.HOOKS:
            shutil.copy(os.path.join(ROOT, "scripts", "githooks", name), os.path.join(d, "scripts", "githooks", name))
        for name in ("duty.py", "alert.py"):
            with open(os.path.join(d, "scripts", name), "w", encoding="utf-8") as f:
                f.write(STAND_IN)
        if on_duty or chain:
            os.makedirs(os.path.join(d, ".erw"))
        if on_duty:
            with open(os.path.join(d, ".erw", "duty.json"), "w", encoding="utf-8") as f:
                json.dump({"token": "t", "machine": "old-laptop"}, f)
        if chain:
            with open(os.path.join(d, ".erw", "chain.json"), "w", encoding="utf-8") as f:
                json.dump({"token": "t", "name": "a chain"}, f)

    def run_hooks(self, d):
        for name in self.HOOKS:
            t0 = time.time()
            r = subprocess.run([self.sh, "scripts/githooks/" + name], cwd=d, input="refs/heads/x 1 refs/heads/x 0\n", capture_output=True, text=True, timeout=60)
            self.assertEqual((r.returncode, r.stdout, r.stderr), (0, "", ""), name)
            self.assertLess(time.time() - t0, 30, f"{name} held the commit")

    def test_a_commit_or_a_push_on_a_machine_on_duty_sends_a_beat(self):
        with tempfile.TemporaryDirectory(ignore_cleanup_errors=True) as d:
            self.fake(d, on_duty=True)
            self.run_hooks(d)
            asked = wait_for(os.path.join(d, "asked.txt"), 2)
            self.assertEqual(len(asked), 2)
            for line in asked:
                words = line.split()
                self.assertEqual(words[:2], ["beat", "--state"])
                self.assertEqual(os.path.basename(words[2].rstrip("/")), ".erw")

    def test_a_machine_that_is_not_on_duty_sends_nothing(self):
        with tempfile.TemporaryDirectory(ignore_cleanup_errors=True) as d:
            self.fake(d, on_duty=False)
            self.run_hooks(d)
            time.sleep(1.0)
            self.assertFalse(os.path.exists(os.path.join(d, "asked.txt")))

    def test_a_machine_on_duty_in_a_marked_chain_sends_both_beats(self):
        with tempfile.TemporaryDirectory(ignore_cleanup_errors=True) as d:
            self.fake(d, on_duty=True, chain=True)
            self.run_hooks(d)
            asked = wait_for(os.path.join(d, "asked.txt"), 4)
            self.assertEqual(sorted(a.split()[0] for a in asked), ["beat", "beat", "chain", "chain"])

    def test_a_commit_in_a_worktree_is_the_machines(self):
        if not shutil.which("git"):
            self.skipTest("no git on this machine")
        with tempfile.TemporaryDirectory(ignore_cleanup_errors=True) as d:
            main, tree = os.path.join(d, "main"), os.path.join(d, "tree")
            os.makedirs(main)
            self.fake(main, on_duty=False)

            def git(cwd, *args):
                r = subprocess.run(["git", *args], cwd=cwd, capture_output=True, text=True, stdin=subprocess.DEVNULL)
                self.assertEqual(r.returncode, 0, r.stderr)
            git(main, "init", "-q")
            git(main, "config", "user.name", "A Test")
            git(main, "config", "user.email", "test@example.invalid")
            git(main, "config", "commit.gpgsign", "false")
            git(main, "config", "core.hooksPath", os.path.join(d, "no-hooks"))
            git(main, "add", "-A")
            git(main, "commit", "-q", "-m", "start")
            git(main, "worktree", "add", "-q", tree, "-b", "wip/x")
            # the machine goes on duty in its main checkout; .erw/ is not in git, so the worktree has none
            os.makedirs(os.path.join(main, ".erw"))
            with open(os.path.join(main, ".erw", "duty.json"), "w", encoding="utf-8") as f:
                json.dump({"token": "t", "machine": "old-laptop"}, f)
            self.assertFalse(os.path.exists(os.path.join(tree, ".erw")))
            self.run_hooks(tree)
            asked = wait_for(os.path.join(tree, "asked.txt"), 2)
            self.assertEqual(len(asked), 2, "the worktree's commit and push each sent a beat")
            for line in asked:
                self.assertTrue(os.path.samefile(line.split()[2], os.path.join(main, ".erw")), line)

    def test_the_hooks_are_as_session_116_left_them_but_for_the_duty_block(self):
        for name in self.HOOKS:
            with open(os.path.join(ROOT, "scripts", "githooks", name), "rb") as f:
                raw = f.read()
            self.assertNotIn(b"\r", raw, f"{name}: a hook with Windows line ends does not run")
            text = raw.decode("utf-8")
            self.assertEqual(text.count("duty.py\" beat --state"), 1, name)
            self.assertLess(text.index("duty.py\" beat"), text.index('[ -f "$root/.erw/chain.json" ] || exit 0'), f"{name}: the duty beat comes before the chain's early exit")
            self.assertIn("&", text.split('duty.py" beat', 1)[1].splitlines()[0], f"{name}: the beat runs in the background")
            self.assertEqual(text.rstrip().splitlines()[-1], "exit 0", name)
            self.assertNotIn("set -e", text)


class TheWorkflow(unittest.TestCase):
    def test_the_idle_alarm_is_a_second_step_of_the_chain_watch_and_mirrors_it(self):
        wf = src(".github", "workflows", "chain-watch.yml")
        with open(os.path.join(ROOT, ".github", "workflows", "chain-watch.yml"), "rb") as f:
            self.assertNotIn(b"\r", f.read())
        chain = 'python warehouse/health.py run --step "chain watch" -- python scripts/alert.py chain check'
        idle = 'python warehouse/health.py run --step "idle alarm" -- python scripts/duty.py check'
        self.assertIn(chain, wf)
        self.assertIn(idle, wf)
        self.assertLess(wf.index("python warehouse/health.py dedupe --workflow-file chain-watch.yml --minutes 15"), wf.index(chain))
        self.assertLess(wf.index(chain), wf.index(idle))
        step = wf.split("- name: Has a machine on duty run anything in 30 minutes", 1)[1]
        self.assertIn("if: steps.dedupe.outputs.skip != '1'", step)
        for secret in ("SUPABASE_URL", "SUPABASE_SERVICE_KEY", "RESEND_API_KEY", "DIGEST_RECIPIENTS", "DIGEST_FROM"):
            self.assertIn("${{ secrets." + secret + " }}", step)
        self.assertEqual(wf.count("${{ secrets."), 12, "no secret the workflow did not already use")
        self.assertIn('- cron: "*/15 * * * *"', wf)
        self.assertIn("contents: read", wf)
        for never in ("contents: write", "git push", "lock.py", "--strict", "continue-on-error"):
            self.assertNotIn(never, wf, never)
        self.assertNotIn(EM, wf)

    def test_the_workflow_parses_and_its_steps_are_the_six(self):
        try:
            import yaml
        except ImportError:
            self.skipTest("PyYAML is not installed here")
        d = yaml.safe_load(src(".github", "workflows", "chain-watch.yml"))
        job = d["jobs"]["watch"]
        self.assertEqual(len(job["steps"]), 6)
        self.assertEqual([s.get("id") for s in job["steps"]].count("dedupe"), 1)
        last, before = job["steps"][-1], job["steps"][-2]
        self.assertEqual(last["if"], before["if"])
        self.assertEqual(set(last["env"]), set(before["env"]) - {"GITHUB_TOKEN"}, "the idle check reads the marks, not GitHub")
        self.assertLessEqual(job["timeout-minutes"], 10)

    def test_the_check_runs_on_what_the_workflow_installs(self):
        # the runner installs requests for health.py and nothing else: duty.py and alert.py need the standard library alone
        for rel in ("duty.py", "alert.py"):
            top = {ln.split()[1].split(".")[0] for ln in src("scripts", rel).splitlines() if ln.startswith(("import ", "from "))}
            self.assertEqual(top - {"argparse", "datetime", "json", "os", "socket", "subprocess", "sys", "time", "types", "urllib", "alert"}, set(), rel)

    def test_no_migration_was_needed(self):
        names = sorted(os.listdir(os.path.join(ROOT, "warehouse", "supabase", "migrations")))
        self.assertFalse([n for n in names if "duty" in n or "idle" in n], "the idle alarm uses migration 016's table and functions")
        m = src("warehouse", "supabase", "migrations", "016_locks.sql")
        for fn in ("erw_lock_acquire", "erw_lock_renew", "erw_lock_release"):
            self.assertIn(f"function public.{fn}(", m)
            self.assertIn(fn, src("scripts", "duty.py"))
        self.assertIn("name      text primary key", m)

    def test_the_document_says_how_a_machine_goes_on_and_off_duty(self):
        doc = src("docs", "machines.md")
        for word in ("python scripts/duty.py", "duty:<machine>", "once at 30 minutes and again every hour after", "idle alarm", "python scripts/duty.py off",
                     "python scripts/duty.py beat"):
            self.assertIn(word, doc, word)
        self.assertNotIn(EM, doc)


if __name__ == "__main__":
    unittest.main()

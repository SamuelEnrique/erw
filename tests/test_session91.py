"""Session 91: alerts (scripts/alert.py, .claude/settings.json, .github/workflows/chain-watch.yml).

Energy Research Warehouse (ERW). One line by email when a session waits for input or a permission (Claude Code's
Notification hook), and when a chain marked as running has saved nothing for 30 minutes (the scheduled check). No test
here sends anything or reaches a network: the sender, the database and GitHub are stand-ins.

    python -m unittest tests.test_session91 -v
"""

import datetime as dt
import json
import os
import subprocess
import sys
import tempfile
import types
import unittest

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
sys.path.insert(0, os.path.join(ROOT, "scripts"))
import alert  # noqa: E402

UTC = dt.timezone.utc


def src(*parts):
    with open(os.path.join(ROOT, *parts), encoding="utf-8") as f:
        return f.read()


def envs(**kv):
    return lambda name: kv.get(name, "")


KEYS = dict(RESEND_API_KEY="k", DIGEST_RECIPIENTS="a@example.invalid, b@example.invalid", DIGEST_FROM="ERW <e@example.invalid>")


class Sender:
    def __init__(self, status=200):
        self.calls, self.status = [], status

    def __call__(self, url, headers=None, timeout=None, json=None):
        self.calls.append((url, headers, json))
        return types.SimpleNamespace(status_code=self.status, text="{}")


class TheLine(unittest.TestCase):
    def test_one_message_to_each_fixed_recipient_and_nothing_but_the_line(self):
        post = Sender()
        n = alert.send("ERW: x", "  a line\n over two   rows ", post=post, env=envs(**KEYS))
        self.assertEqual(n, 2)
        self.assertEqual([c[2]["to"] for c in post.calls], [["a@example.invalid"], ["b@example.invalid"]])
        self.assertTrue(all(c[0] == "https://api.resend.com/emails" and set(c[2]) == {"from", "to", "subject", "text"} for c in post.calls))
        self.assertEqual(post.calls[0][2]["text"], "a line over two rows\n")

    def test_nothing_is_sent_without_a_key_or_a_recipient_or_on_a_dry_run(self):
        post = Sender()
        with self.assertRaises(RuntimeError):
            alert.send("s", "l", post=post, env=envs(DIGEST_RECIPIENTS="a@example.invalid"))
        with self.assertRaises(RuntimeError):
            alert.send("s", "l", post=post, env=envs(RESEND_API_KEY="k"))
        with self.assertRaises(ValueError):
            alert.send("s", "   ", post=post, env=envs(**KEYS))
        self.assertEqual(alert.send("s", "l", dry_run=True, post=post, env=envs(**KEYS)), 0)
        self.assertEqual(post.calls, [])

    def test_a_refusal_names_no_address_and_a_long_line_is_cut(self):
        with self.assertRaises(RuntimeError) as c:
            alert.send("s", "l", post=Sender(403), env=envs(**KEYS))
        self.assertNotIn("example.invalid", str(c.exception))
        self.assertEqual(len(alert.one_line("x" * 900)), 300)
        self.assertNotIn(chr(0x2014), alert.one_line("a " + chr(0x2014) + " b"))


ENV_FILE = chr(10).join(["# a comment", "RESEND_API_KEY=abc", 'DIGEST_FROM="ERW <e@example.invalid>"', "", "export X = 'y'", "BROKEN", ""])
EVENT = {"session_id": "f4e41419-407b-49cc-b49e-648b9a0ccade", "transcript_path": "C:\\x\\t.jsonl", "cwd": "C:\\Users\\x\\Documents\\erw",
         "hook_event_name": "Notification", "message": "Claude needs your permission to use Bash", "notification_type": "permission_prompt"}


class ASessionWaits(unittest.TestCase):
    def test_the_line_says_what_it_waits_for_where_and_which_session(self):
        subject, line = alert.hook_line(EVENT, machine="oldlaptop", chain="night of 4 October")
        self.assertEqual(subject, "ERW: a session waits for a permission")
        self.assertEqual(line, "A Claude Code session waits for a permission on oldlaptop (session f4e41419, in erw), in the chain "
                               "\"night of 4 October\": Claude needs your permission to use Bash")
        subject, line = alert.hook_line({**EVENT, "notification_type": "idle_prompt", "message": "Claude is waiting for your input"}, machine="m")
        self.assertEqual(subject, "ERW: a session waits for input")
        self.assertIn("waits for input on m (session f4e41419, in erw): Claude is waiting for your input", line)
        self.assertEqual(len(line.splitlines()), 1)

    def test_only_a_wait_is_an_alert(self):
        for kind in ("auth_success", "agent_completed", "something_new"):
            self.assertIsNone(alert.hook_line({**EVENT, "notification_type": kind}))
        self.assertIsNone(alert.hook_line({}))
        self.assertIsNone(alert.hook_line({"message": "Login successful"}))
        # an event that names no kind is read from its message
        self.assertEqual(alert.wait_kind({"message": "Claude needs your permission to use Bash"}), "permission_prompt")
        self.assertEqual(alert.wait_kind({"message": "Claude is waiting for your input"}), "idle_prompt")
        self.assertIn("waits for input", alert.hook_line({**EVENT, "notification_type": "agent_needs_input"}, machine="m")[1])

    def test_one_email_per_session_and_kind_every_ten_minutes(self):
        with tempfile.TemporaryDirectory() as d:
            post = Sender()
            run = lambda e, now: alert.hook(json.dumps(e), post=post, env=envs(**KEYS), state_dir=d, now=now)  # noqa: E731
            self.assertIn("sent to 2", run(EVENT, 1000.0))
            self.assertIn("less than 10 minutes", run(EVENT, 1300.0))
            self.assertEqual(len(post.calls), 2)
            # another kind, and another session, are not held back by the first
            self.assertIn("sent to 2", run({**EVENT, "notification_type": "idle_prompt"}, 1300.0))
            self.assertIn("sent to 2", run({**EVENT, "session_id": "another"}, 1300.0))
            self.assertIn("sent to 2", run(EVENT, 1000.0 + 601))
            self.assertEqual(len(post.calls), 8)

    def test_the_hook_never_raises_and_never_blocks_a_session(self):
        with tempfile.TemporaryDirectory() as d:
            self.assertIn("not sent", alert.hook("not json at all", post=Sender(), env=envs(**KEYS), state_dir=d))
            self.assertIn("not sent", alert.hook(json.dumps(EVENT), post=Sender(500), env=envs(**KEYS), state_dir=d, now=1.0))
            # a send that failed does not silence the next try
            self.assertIn("sent to 2", alert.hook(json.dumps(EVENT), post=Sender(), env=envs(**KEYS), state_dir=d, now=2.0))
            self.assertIn("not sent", alert.hook(json.dumps({**EVENT, "session_id": "s2"}), post=Sender(), env=envs(), state_dir=d, now=1.0))
            self.assertEqual(alert.hook("", post=Sender(), env=envs(**KEYS), state_dir=d), "nothing to send")
        # as a process: bad input on stdin, and no key in the environment: exit 0 and nothing printed
        e = {k: v for k, v in os.environ.items() if k not in ("RESEND_API_KEY", "DIGEST_RECIPIENTS")}
        e["ERW_ALERTS"] = "off"
        r = subprocess.run([sys.executable, os.path.join(ROOT, "scripts", "alert.py"), "hook"], input="{broken", capture_output=True, text=True, timeout=60, env=e)
        self.assertEqual((r.returncode, r.stdout, r.stderr), (0, "", ""))
        r = subprocess.run([sys.executable, os.path.join(ROOT, "scripts", "alert.py"), "hook"], input=json.dumps(EVENT), capture_output=True, text=True, timeout=60, env=e)
        self.assertEqual((r.returncode, r.stdout, r.stderr), (0, "", ""))

    def test_it_can_be_silenced(self):
        old = os.environ.get("ERW_ALERTS")
        os.environ["ERW_ALERTS"] = "off"
        try:
            with tempfile.TemporaryDirectory() as d:
                post = Sender()
                self.assertEqual(alert.hook(json.dumps(EVENT), post=post, env=envs(**KEYS), state_dir=d, now=1.0), "nothing to send")
                self.assertEqual(post.calls, [])
        finally:
            os.environ.pop("ERW_ALERTS") if old is None else os.environ.__setitem__("ERW_ALERTS", old)


def at(h, m=0):
    return dt.datetime(2026, 10, 4, h, m, tzinfo=UTC)


def a_mark(acquired=at(5, 52), renewed=None, expires=at(20, 0)):
    return {"holder": "oldlaptop/f4e41419", "task": "night of 4 October", "acquired": acquired, "renewed": renewed or acquired, "expires": expires, "expired": False}


class AChainSavesNothing(unittest.TestCase):
    def test_no_chain_marked_is_quiet(self):
        self.assertEqual(alert.decide(at(7), None, None), (None, "no chain is marked as running"))

    def test_a_save_in_the_last_30_minutes_is_quiet(self):
        subject, why = alert.decide(at(7, 10), a_mark(), (at(6, 48), "wip/090-fixes", "Session 90 report"))
        self.assertIsNone(subject)
        self.assertIn("saved 22 minutes ago (a push to wip/090-fixes, 06:48 UTC)", why)

    def test_30_minutes_without_a_save_is_one_line(self):
        subject, line = alert.decide(at(7, 25), a_mark(), (at(6, 48), "wip/090-fixes", "Session 90 report"))
        self.assertEqual(subject, "ERW: a chain has saved nothing for 30 minutes")
        self.assertEqual(line, "The chain \"night of 4 October\" (oldlaptop/f4e41419) has saved nothing for 37 minutes: its last save was a push to "
                               "wip/090-fixes at 06:48 UTC. Marked as running since 05:52 UTC.")
        self.assertEqual(len(line.splitlines()), 1)

    def test_it_says_so_once_then_every_hour_not_every_quarter(self):
        push = (at(6, 0), "wip/090-fixes", "x")
        said = [m for m in range(0, 300, 15) if alert.decide(at(6, 0) + dt.timedelta(minutes=m + 7), a_mark(), push)[0]]
        self.assertEqual(said, [30, 90, 150, 210, 270])   # the checks at 37, 97, 157, ... minutes of silence
        self.assertEqual(alert.decide(at(7, 37), a_mark(), push)[0], "ERW: a chain is still saving nothing")

    def test_a_beat_is_a_save_and_so_is_the_start(self):
        old = (at(4, 0), "wip/089-findings", "x")
        self.assertIsNone(alert.decide(at(6, 10), a_mark(), old)[0])                                   # started 18 minutes ago
        self.assertIsNotNone(alert.decide(at(6, 25), a_mark(), old)[0])                                # 33 minutes after its start
        self.assertIn("its start at 05:52 UTC", alert.decide(at(6, 25), a_mark(), old)[1])
        self.assertIsNone(alert.decide(at(6, 25), a_mark(renewed=at(6, 5)), old)[0])                   # a beat 20 minutes ago
        self.assertIn("a beat at 06:05 UTC", alert.decide(at(6, 40), a_mark(renewed=at(6, 5)), old)[1])
        self.assertIsNotNone(alert.decide(at(6, 25), a_mark(), None)[0])                               # no push at all on GitHub

    def test_a_mark_that_lapsed_is_said_once(self):
        m = a_mark(expires=at(8, 0))
        subject, line = alert.decide(at(8, 7), m, (at(7, 59), "wip/x", "x"))
        self.assertEqual(subject, "ERW: a chain's mark lapsed")
        self.assertIn("was marked as running until 08:00 UTC and was never marked done", line)
        self.assertIsNone(alert.decide(at(8, 22), m, None)[0])
        self.assertIsNone(alert.decide(at(23, 0), m, None)[0])

    def test_the_newest_push_is_read_from_every_branch(self):
        # session 116: this test pinned that only wip/ and task/ branches were read. A landing leaves its commits on
        # main and deletes the task branch, so the watch read it as silence; every branch is read now, each with its
        # newest commits and their authors (tests/test_session116_alerts.py has the rule of which commits count).
        commit = lambda when, head: {"committedDate": when, "messageHeadline": head, "author": {"name": "Samuel Enrique", "email": "s@example.invalid"}}  # noqa: E731
        branch = lambda name, *commits: {"name": name, "target": {"history": {"nodes": list(commits)}}}  # noqa: E731
        answer = {"data": {"repository": {"refs": {"nodes": [
            branch("wip/091-alerts", commit("2026-10-04T07:10:00Z", "Session 91")),
            branch("wip/090-fixes", commit("2026-10-04T06:48:00Z", "Session 90 report")),
            branch("task/092-x", commit("2026-10-04T07:20:00+00:00", "later"))]}}}}
        asked = []

        def post(url, json=None, timeout=None, headers=None):
            asked.append((url, json["query"], headers))
            return types.SimpleNamespace(status_code=200, json=lambda: answer, text="")
        t, branch, head = alert.newest_push(token="t", post=post)
        self.assertEqual((t, branch, head), (at(7, 20), "task/092-x", "later"))
        self.assertEqual(asked[0][0], "https://api.github.com/graphql")
        self.assertIn('refPrefix: "refs/heads/"', asked[0][1])
        self.assertNotIn('refPrefix: "refs/heads/wip/"', asked[0][1])
        empty = {"data": {"repository": {"refs": {"nodes": []}}}}
        self.assertIsNone(alert.newest_push(token="t", post=lambda *a, **k: types.SimpleNamespace(status_code=200, json=lambda: empty, text="")))
        with self.assertRaises(RuntimeError):
            alert.newest_push(token="t", post=lambda *a, **k: types.SimpleNamespace(status_code=401, json=lambda: {}, text="Bad credentials"))


class TheWiring(unittest.TestCase):
    def test_the_workflow_checks_every_15_minutes_and_cannot_fail_or_write(self):
        wf = src(".github", "workflows", "chain-watch.yml")
        self.assertIn('- cron: "*/15 * * * *"', wf)
        self.assertIn('python warehouse/health.py run --step "chain watch" -- python scripts/alert.py chain check', wf)
        self.assertIn("python warehouse/health.py dedupe --workflow-file chain-watch.yml --minutes 15", wf)
        self.assertIn("contents: read", wf)
        self.assertNotIn("contents: write", wf)
        for secret in ("SUPABASE_URL", "SUPABASE_SERVICE_KEY", "RESEND_API_KEY", "DIGEST_RECIPIENTS"):
            self.assertIn("${{ secrets." + secret + " }}", wf)
        self.assertNotIn("git push", wf)
        self.assertNotIn("lock.py", wf)
        # the script needs nothing the workflow does not install
        imports = {ln.split()[1].split(".")[0] for ln in src("scripts", "alert.py").splitlines() if ln.startswith(("import ", "from "))}
        self.assertEqual(imports - {"argparse", "datetime", "json", "os", "socket", "sys", "time", "types", "urllib"}, set(), "the hook must run on the standard library alone")

    def test_the_env_file_is_read_without_a_package(self):
        with tempfile.TemporaryDirectory() as d:
            p = os.path.join(d, ".env")
            with open(p, "w", encoding="utf-8") as f:
                f.write(ENV_FILE)
            self.assertEqual(alert.dotenv(p), {"RESEND_API_KEY": "abc", "DIGEST_FROM": "ERW <e@example.invalid>", "X": "y"})
            self.assertEqual(alert.dotenv(os.path.join(d, "absent")), {})

    def test_the_schedule_is_in_the_database_and_the_summary_expects_it(self):
        m = src("warehouse", "supabase", "migrations", "022_chain_watch.sql")
        self.assertIn("cron.schedule('erw-chain-watch', '*/15 * * * *'", m)
        self.assertIn("erw_dispatch('chain-watch.yml')", m)
        sys.path.insert(0, os.path.join(ROOT, "warehouse"))
        import health
        self.assertEqual(health.EXPECTED["chain watch"], 96)

    def test_the_mark_is_a_row_of_the_locks_table_and_not_the_data_lock(self):
        self.assertEqual(alert.MARK, "chain")
        sys.path.insert(0, os.path.join(ROOT, "warehouse"))
        import lock
        self.assertNotEqual(alert.MARK, lock.NAME)
        s = src("scripts", "alert.py")
        for fn in ("erw_lock_acquire", "erw_lock_renew", "erw_lock_release", "erw_lock_status"):
            self.assertIn(fn, s)
            self.assertIn(f"function public.{fn}", src("warehouse", "supabase", "migrations", "016_locks.sql"))

    def test_no_em_dash_in_what_the_session_wrote(self):
        for rel in ("tests/test_session91.py", "scripts/alert.py", ".github/workflows/chain-watch.yml", "warehouse/supabase/migrations/022_chain_watch.sql",
                    ".claude/settings.json", "docs/machines.md"):
            self.assertNotIn(chr(0x2014), src(*rel.split("/")), rel)


class TheSettings(unittest.TestCase):
    def setUp(self):
        self.s = json.loads(src(".claude", "settings.json"))
        self.allow, self.deny = self.s["permissions"]["allow"], self.s["permissions"]["deny"]

    def test_each_kind_of_wait_pipes_to_the_alert_and_cannot_hold_a_session(self):
        groups = {g["matcher"]: g["hooks"] for g in self.s["hooks"]["Notification"]}
        self.assertEqual(set(groups), set(alert.WAITS))
        for kind, hooks in groups.items():
            self.assertEqual(len(hooks), 1, kind)
            h = hooks[0]
            self.assertEqual((h["type"], h["command"], h["async"]), ("command", 'python "$CLAUDE_PROJECT_DIR/scripts/alert.py" hook', True))
            self.assertLessEqual(h["timeout"], 60)
        self.assertEqual(len(self.s["hooks"]["SessionStart"]), 1, "the session-start hook was there before and stays")

    def test_the_hook_command_runs_as_written_and_exits_0(self):
        import shutil
        bash = shutil.which("bash")
        if not bash:
            self.skipTest("bash is not on this machine")
        cmd = self.s["hooks"]["Notification"][0]["hooks"][0]["command"]
        e = dict(os.environ, CLAUDE_PROJECT_DIR=ROOT.replace(os.sep, "/"), ERW_ALERTS="off")
        r = subprocess.run([bash, "-c", cmd], input=json.dumps(EVENT), capture_output=True, text=True, timeout=60, env=e)
        self.assertEqual((r.returncode, r.stdout, r.stderr), (0, "", ""))

    def test_a_force_push_is_denied_in_the_spellings_a_session_writes(self):
        import fnmatch

        def matches(rule, tool, command):
            if not rule.startswith(tool + "("):
                return False
            pat = rule[len(tool) + 1:-1]
            if pat.endswith(":*"):
                pat = pat[:-2] + " *"
            # the reference: a trailing " *" that is the rule's only wildcard also matches the bare command
            return fnmatch.fnmatchcase(command, pat) or (pat.endswith(" *") and pat.count("*") == 1 and command == pat[:-2])
        self.matches = matches
        for tool in ("Bash", "PowerShell"):
            for cmd in ("git push --force origin wip/x", "git push -f origin wip/x", "git push origin wip/x --force", "git push origin wip/x -f",
                        "git push --force-with-lease origin wip/x", "git push origin wip/x --force-with-lease", "git push origin -f wip/x"):
                self.assertTrue(any(matches(r, tool, cmd) for r in self.deny), f"{tool}: {cmd} is not denied")
            for cmd in ("git push origin wip/091-alerts", "git push origin main", "git push -u origin wip/091-alerts", "git push origin wip/090-fixes:task/090-fixes"):
                self.assertFalse(any(matches(r, tool, cmd) for r in self.deny), f"{tool}: {cmd} is denied")
            self.assertTrue(any(matches(r, tool, "git push origin wip/091-alerts") for r in self.allow))

    def test_the_list_is_routine_actions_and_nothing_wider(self):
        for r in self.allow:
            tool, _, rest = r.partition("(")
            pat = rest[:-1]
            if tool not in ("Bash", "PowerShell"):
                continue
            head = pat.split("*")[0].replace(":", " ").split()
            # the reference: the words before the first * are what limit a rule; a program alone allows all it can do
            self.assertGreaterEqual(len(head), 2, f"{r}: a wildcard before the subcommand")
            self.assertNotIn(pat.rstrip(":* "), ("python", "git", "git push", "node", "npm", "npx", "bash", "git push origin"), r)
        text = "\n".join(self.allow)
        for never in ("warehouse/connectors", "apply.py", "chat/ask.py", "python -c", "node -e", "rm ", "Remove-Item", "curl", "--force", "task/", "git reset", "git clean", "git rebase"):
            self.assertNotIn(never, text, f"the allowlist names {never}")
        for kept in ("Bash(python warehouse/supabase/load.py:*)", "Bash(npm run build)", "Bash(git push origin main)"):
            self.assertIn(kept, self.allow, "a rule that was there before is gone")
        self.assertNotIn("defaultMode", self.s["permissions"])
        self.assertNotIn("ask", self.s["permissions"])
        # every script the list names exists
        for r in self.allow:
            for word in r.split("(", 1)[-1].rstrip(")").replace(":*", "").split():
                if word.endswith((".py", ".mjs")) and "*" not in word:
                    p = word if os.path.exists(os.path.join(ROOT, word)) else os.path.join("site", word.lstrip("./"))
                    self.assertTrue(os.path.exists(os.path.join(ROOT, p)), f"{r} names {word}, which is not in the repository")

    def test_the_document_says_what_the_settings_do(self):
        doc = src("docs", "machines.md")
        for said in ("## Alerts: when an unattended session needs a person", "python scripts/alert.py chain start", "permission_prompt", "idle_prompt",
                     "ERW_ALERTS=off", "chain-watch.yml", "once at 30 minutes and again every hour after", "### The permission allowlist",
                     "https://code.claude.com/docs/en/hooks", "https://code.claude.com/docs/en/permissions", "wip/x:task/x"):
            self.assertIn(said, doc)


if __name__ == "__main__":
    unittest.main()

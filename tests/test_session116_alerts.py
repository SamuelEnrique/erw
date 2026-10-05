"""Session 116: the alerts (scripts/alert.py, scripts/githooks/, .github/workflows/chain-watch.yml).

Energy Research Warehouse (ERW). Two corrections to session 91's alerts:

- the chain watch counted only pushes to wip/ and task/ branches, so it reported silence during a landing (the
  workflow merges the task branch into main and deletes it). It now counts any commit or push by the running chain: a
  commit on any branch on GitHub that a scheduled workflow did not write, the workflow's merge of a task/ branch, and
  the beat the git hooks send at each commit and push on the chain's machine;
- the waiting-for-input alert stays quiet for ten minutes after a session has said REPORT READY or CHAIN DONE.

No test here sends anything or reaches a network: the sender, the database, GitHub and the transcripts are stand-ins.

    python -m unittest tests.test_session116_alerts -v
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

UTC = dt.timezone.utc
KEYS = dict(RESEND_API_KEY="k", DIGEST_RECIPIENTS="a@example.invalid, b@example.invalid", DIGEST_FROM="ERW <e@example.invalid>")
BOT = {"name": "github-actions[bot]", "email": "41898282+github-actions[bot]@users.noreply.github.com"}
SAM = {"name": "Samuel Enrique", "email": "s@example.invalid"}


def src(*parts):
    with open(os.path.join(ROOT, *parts), encoding="utf-8") as f:
        return f.read()


def envs(**kv):
    return lambda name: kv.get(name, "")


class Sender:
    def __init__(self, status=200):
        self.calls, self.status = [], status

    def __call__(self, url, headers=None, timeout=None, json=None):
        self.calls.append((url, headers, json))
        return types.SimpleNamespace(status_code=self.status, text="{}")


def at(h, m=0):
    return dt.datetime(2026, 10, 5, h, m, tzinfo=UTC)


def a_mark(acquired=at(2, 0), renewed=None, expires=at(18, 0)):
    return {"holder": "oldlaptop/e4b617a1", "task": "session 116", "acquired": acquired, "renewed": renewed or acquired, "expires": expires, "expired": False}


def commit(when, head, author=SAM):
    return {"committedDate": when.strftime("%Y-%m-%dT%H:%M:%SZ"), "messageHeadline": head, "author": author}


def github(*branches):
    """A stand-in for GitHub's answer: each branch is (name, its commits, newest first)."""
    answer = {"data": {"repository": {"refs": {"nodes": [{"name": n, "target": {"history": {"nodes": list(cs)}}} for n, cs in branches]}}}}
    asked = []

    def post(url, json=None, timeout=None, headers=None):
        asked.append(json["query"])
        return types.SimpleNamespace(status_code=200, json=lambda: answer, text="")
    post.asked = asked
    return post


# ---------------------------------------------------------------------------------------------------------------------
# the chain watch: any commit or push by the running chain

class WhatCountsAsASave(unittest.TestCase):
    def test_a_commit_on_main_by_the_chain_is_a_save_and_a_workflows_is_not(self):
        post = github(("main", [commit(at(4, 20), "Daily prices 2026-10-05: ok: all; failed: none", BOT),
                                commit(at(4, 15), "Health summary 2026-10-04 (warehouse/health.py)", BOT),
                                commit(at(4, 2), "Session 116: the freeze rule")]),
                      ("wip/115-storage-awards", [commit(at(3, 30), "Session 115 report")]))
        save = alert.newest_save(token="t", post=post)
        self.assertEqual(save, (at(4, 2), "main", "Session 116: the freeze rule"))
        self.assertEqual(alert.save_words(save), "a commit on main")
        # every branch is asked for, main included, with each commit's author
        self.assertIn('refPrefix: "refs/heads/"', post.asked[0])
        self.assertIn("author { name email }", post.asked[0])
        self.assertIn("history(first:", post.asked[0])
        # the workflows' commits alone are no save at all
        only_bots = github(("main", [commit(at(4, 20), "Daily prices 2026-10-05", BOT), commit(at(4, 15), "Energy Roundup 2026-W40", BOT)]))
        self.assertIsNone(alert.newest_save(token="t", post=only_bots))

    def test_the_workflows_named_in_the_repository_commit_as_the_bot_this_passes_over(self):
        import glob
        names = set()
        for p in glob.glob(os.path.join(ROOT, ".github", "workflows", "*.yml")):
            with open(p, encoding="utf-8") as f:
                for ln in f:
                    if "git config user.name" in ln:
                        names.add(ln.split("git config user.name", 1)[1].strip().strip('"'))
        self.assertTrue(names, "no workflow sets a commit author: the rule has nothing to rest on")
        self.assertEqual(names - set(alert.BOTS), set(), "a workflow commits under a name the chain watch would take for the chain's")
        self.assertTrue(alert.is_workflow({"author": BOT}))
        self.assertTrue(alert.is_workflow({"author": {"name": "another[bot]", "email": "1+another[bot]@users.noreply.github.com"}}))
        self.assertFalse(alert.is_workflow({"author": SAM}))
        self.assertFalse(alert.is_workflow({}))

    def test_a_landing_is_not_silence(self):
        # the task branch was pushed at 03:54, the workflow merged it at 04:00 and deleted it: the commits are on main
        # only, and the newest on any wip/ branch is 50 minutes old
        landed = github(("main", [commit(at(4, 0), "Merge task/115-storage-awards: checks passed (run 37261258743)", BOT),
                                  commit(at(3, 50), "Session 115: session 108's test tells its sample from the approved table")]),
                        ("wip/115-storage-awards", [commit(at(3, 12), "Session 115: the connector")]))
        save = alert.newest_save(token="t", post=landed)
        self.assertEqual(save[:2], (at(4, 0), "main"))
        self.assertEqual(alert.save_words(save), "the landing of task/115-storage-awards on main")
        subject, why = alert.decide(at(4, 7), a_mark(acquired=at(3, 0)), save)
        self.assertIsNone(subject)
        self.assertIn("saved 7 minutes ago (the landing of task/115-storage-awards on main, 04:00 UTC)", why)
        # what session 91 read, the wip/ branch alone, was a silence of 55 minutes at the same moment
        old = (at(3, 12), "wip/115-storage-awards", "Session 115: the connector")
        self.assertIn("has saved nothing for 55 minutes", alert.decide(at(4, 7), a_mark(acquired=at(3, 0)), old)[1])
        self.assertEqual(alert.decide(at(3, 50), a_mark(acquired=at(3, 0)), old)[0], "ERW: a chain has saved nothing for 30 minutes")
        # GitHub's own merge of a pull request from a task branch is a landing too; a merge of anything else by the bot is not
        self.assertEqual(alert.landing({"messageHeadline": "Merge pull request #12 from SamuelEnrique/task/116-storage-offers"}), "task/116-storage-offers")
        self.assertIsNone(alert.landing({"messageHeadline": "Merge branch 'main' into wip/x"}))
        self.assertIsNone(alert.landing({"messageHeadline": "Daily prices 2026-10-05"}))

    def test_the_chains_commits_reached_through_a_merge_count_even_when_the_merge_is_old(self):
        # main's history lists the commits a merge brought in: the chain's own, not the bot's, whichever is newest
        post = github(("main", [commit(at(4, 30), "Health summary 2026-10-04", BOT), commit(at(4, 10), "Session 116 report"),
                                commit(at(4, 0), "Merge task/116-storage-offers: checks passed (run 1)", BOT)]))
        self.assertEqual(alert.newest_save(token="t", post=post), (at(4, 10), "main", "Session 116 report"))

    def test_a_push_to_any_other_branch_counts_and_the_line_names_the_last_save(self):
        post = github(("main", [commit(at(1, 0), "Daily prices", BOT)]), ("task/116-storage-offers", [commit(at(4, 40), "Session 116: the offers")]),
                      ("wip/116-storage-offers", [commit(at(4, 41), "Session 116 report")]), ("fix/a-typo", [commit(at(4, 45), "A typo")]))
        save = alert.newest_save(token="t", post=post)
        self.assertEqual(save, (at(4, 45), "fix/a-typo", "A typo"))
        subject, line = alert.decide(at(5, 20), a_mark(), save)
        self.assertEqual(subject, "ERW: a chain has saved nothing for 30 minutes")
        self.assertEqual(line, "The chain \"session 116\" (oldlaptop/e4b617a1) has saved nothing for 35 minutes: its last save was a push to fix/a-typo at "
                               "04:45 UTC. Marked as running since 02:00 UTC.")
        self.assertIn("its last save was a commit on main at 04:45 UTC", alert.decide(at(5, 20), a_mark(), (at(4, 45), "main", "Session 116 report"))[1])
        self.assertIn("its last save was the landing of task/x on main at 04:45 UTC",
                      alert.decide(at(5, 20), a_mark(), (at(4, 45), "main", "Merge task/x: checks passed (run 2)"))[1])

    def test_a_local_commits_beat_counts(self):
        # a commit that is not pushed is seen by nobody on GitHub; the hook's beat renews the mark, and that is a save
        stale = (at(3, 0), "wip/116-storage-offers", "an hour ago")
        self.assertIsNotNone(alert.decide(at(3, 35), a_mark(), stale)[0])                       # 35 minutes after its last push
        subject, why = alert.decide(at(3, 35), a_mark(renewed=at(3, 25)), stale)                # the same moment, a commit at 03:25
        self.assertIsNone(subject)
        self.assertIn("saved 10 minutes ago (a beat, 03:25 UTC)", why)
        self.assertIn("its last save was a beat at 03:25 UTC", alert.decide(at(4, 0), a_mark(renewed=at(3, 25)), stale)[1])

    def test_github_refusing_is_an_error_and_not_a_silence(self):
        with self.assertRaises(RuntimeError):
            alert.newest_save(token="t", post=lambda *a, **k: types.SimpleNamespace(status_code=401, json=lambda: {}, text="Bad credentials"))
        with self.assertRaises(RuntimeError):
            alert.newest_save(token="t", post=lambda *a, **k: types.SimpleNamespace(status_code=200, json=lambda: {"errors": [{"message": "x"}]}, text=""))
        # a branch that points at nothing readable is passed over, not a crash
        odd = {"data": {"repository": {"refs": {"nodes": [{"name": "x", "target": None}, {"name": "y", "target": {}}]}}}}
        self.assertIsNone(alert.newest_save(token="t", post=lambda *a, **k: types.SimpleNamespace(status_code=200, json=lambda: odd, text="")))


class TheGitHooks(unittest.TestCase):
    HOOKS = ("post-commit", "pre-push")

    def test_each_hook_beats_only_for_a_marked_chain_and_cannot_fail(self):
        for name in self.HOOKS:
            with open(os.path.join(ROOT, "scripts", "githooks", name), "rb") as f:
                raw = f.read()
            self.assertNotIn(b"\r", raw, f"{name}: a hook with Windows line ends does not run")
            text = raw.decode("utf-8")
            self.assertTrue(text.startswith("#!/bin/sh\n"), name)
            self.assertIn('[ -f "$root/.erw/chain.json" ] || exit 0', text)
            self.assertIn("chain beat", text)
            self.assertIn("&", text.split("chain beat", 1)[1].splitlines()[0], f"{name}: the beat runs in the background")
            self.assertEqual(text.rstrip().splitlines()[-1], "exit 0", name)
            self.assertNotIn("set -e", text)
            self.assertNotIn(chr(0x2014), text)
        attrs = src(".gitattributes")
        self.assertIn("scripts/githooks/* text eol=lf", attrs)

    def _fake_repo(self, d, marked):
        """A stand-in repository root: the two hooks, and an alert.py that writes down what it was asked."""
        os.makedirs(os.path.join(d, "scripts", "githooks"))
        for name in self.HOOKS:
            shutil.copy(os.path.join(ROOT, "scripts", "githooks", name), os.path.join(d, "scripts", "githooks", name))
        with open(os.path.join(d, "scripts", "alert.py"), "w", encoding="utf-8") as f:
            f.write("import os, sys\nopen(os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'asked.txt'), 'a').write(' '.join(sys.argv[1:]) + '\\n')\n"
                    "sys.exit(1)\n")  # and fails, as a beat does when the mark is gone: the hook must not care
        if marked:
            os.makedirs(os.path.join(d, ".erw"))
            with open(os.path.join(d, ".erw", "chain.json"), "w", encoding="utf-8") as f:
                json.dump({"token": "t", "name": "a chain"}, f)

    def test_a_commit_or_a_push_on_the_chains_machine_sends_a_beat_and_elsewhere_nothing(self):
        sh = shutil.which("sh") or shutil.which("bash")
        if not sh:
            self.skipTest("no sh on this machine")
        for marked in (True, False):
            with tempfile.TemporaryDirectory(ignore_cleanup_errors=True) as d:  # Windows: a beat still ending holds the folder
                self._fake_repo(d, marked)
                for name in self.HOOKS:
                    t0 = time.time()
                    r = subprocess.run([sh, "scripts/githooks/" + name], cwd=d, input="refs/heads/x 1 refs/heads/x 0\n", capture_output=True, text=True, timeout=60)
                    self.assertEqual((r.returncode, r.stdout, r.stderr), (0, "", ""), f"{name}, marked={marked}")
                    self.assertLess(time.time() - t0, 30, f"{name} held the commit")
                asked = os.path.join(d, "asked.txt")
                if marked:
                    for _ in range(100):  # the beats run in the background: wait for both, at most 20 seconds
                        if os.path.exists(asked) and len(open(asked).read().splitlines()) >= 2:
                            break
                        time.sleep(0.2)
                    self.assertEqual(open(asked).read().splitlines(), ["chain beat", "chain beat"])
                else:
                    time.sleep(1.0)
                    self.assertFalse(os.path.exists(asked), "a machine that marked no chain sent a beat")

    def test_the_setup_scripts_install_the_hooks_and_leave_a_checkouts_own_alone(self):
        for rel in ("setup.sh", "setup.ps1"):
            s = src("scripts", rel)
            self.assertIn("git config core.hooksPath scripts/githooks", s, rel)
            self.assertIn("git config --get core.hooksPath", s, rel)
            self.assertIn("left alone", s, rel)
            self.assertNotIn(chr(0x2014), s, rel)
        self.assertNotIn("\r", open(os.path.join(ROOT, "scripts", "setup.sh"), "rb").read().decode("utf-8"))


# ---------------------------------------------------------------------------------------------------------------------
# the waiting-for-input alert: quiet for ten minutes after REPORT READY or CHAIN DONE

NOW = dt.datetime(2026, 10, 5, 5, 10, tzinfo=UTC).timestamp()
EVENT = {"session_id": "e4b617a1-9339-44ec-8f1f-eea309003636", "cwd": "C:\\Users\\x\\Documents\\erw", "hook_event_name": "Notification",
         "notification_type": "idle_prompt", "message": "Claude is waiting for your input"}


def entry(kind, minutes_ago, text=None, blocks=None, **more):
    """One line of a transcript as Claude Code writes it (the shape read from a real one on 5 October 2026)."""
    when = dt.datetime.fromtimestamp(NOW - minutes_ago * 60, UTC).strftime("%Y-%m-%dT%H:%M:%S.000Z")
    e = {"type": kind, "isSidechain": False, "timestamp": when, "sessionId": EVENT["session_id"], "uuid": "u"}
    if kind in ("user", "assistant"):
        e["message"] = {"role": kind, "content": blocks if blocks is not None else [{"type": "text", "text": text or ""}]}
    e.update(more)
    return json.dumps(e)


class AfterReportReady(unittest.TestCase):
    def setUp(self):
        self.d = tempfile.TemporaryDirectory()
        self.addCleanup(self.d.cleanup)
        self.post = Sender()

    def transcript(self, *lines):
        p = os.path.join(self.d.name, "t.jsonl")
        with open(p, "w", encoding="utf-8") as f:
            f.write("\n".join(lines) + "\n")
        return p

    def run_hook(self, path, kind="idle_prompt", now=NOW, session=None):
        e = {**EVENT, "notification_type": kind, "transcript_path": path}
        if session:
            e["session_id"] = session
        if kind == "permission_prompt":
            e["message"] = "Claude needs your permission to use Bash"
        return alert.hook(json.dumps(e), post=self.post, env=envs(**KEYS), state_dir=os.path.join(self.d.name, "state"), now=now)

    def a_finished_session(self, words, minutes_ago):
        """A session's end as the real transcripts show it: a tool result, the last words, then notes that are nobody's."""
        return self.transcript(
            entry("user", minutes_ago + 30, "run session 116"),
            entry("assistant", minutes_ago + 2, blocks=[{"type": "tool_use", "id": "x", "name": "Bash", "input": {}}]),
            entry("user", minutes_ago + 1, blocks=[{"type": "tool_result", "tool_use_id": "x", "content": "sent"}]),
            entry("assistant", minutes_ago, blocks=[{"type": "thinking", "thinking": "done"}]),
            entry("assistant", minutes_ago, f"{words}\n\nThe report is on `wip/116-storage-offers`, and the one-line email is sent."),
            entry("system", minutes_ago, subtype="turn_duration"),
            json.dumps({"type": "cost-state", "sessionId": EVENT["session_id"]}))

    def test_report_ready_5_minutes_ago_quiets_an_idle_alert_and_11_minutes_ago_does_not(self):
        said = self.run_hook(self.a_finished_session("REPORT READY", 5))
        self.assertIn("quiet: the session said REPORT READY 5 minutes ago", said)
        self.assertEqual(self.post.calls, [])
        said = self.run_hook(self.a_finished_session("REPORT READY", 11))
        self.assertIn("sent to 2", said)
        self.assertEqual(len(self.post.calls), 2)
        self.assertIn("waits for input", self.post.calls[0][2]["text"])

    def test_chain_done_likewise(self):
        self.assertIn("quiet: the session said CHAIN DONE 5 minutes ago", self.run_hook(self.a_finished_session("CHAIN DONE", 5)))
        self.assertEqual(self.post.calls, [])
        self.assertIn("sent to 2", self.run_hook(self.a_finished_session("CHAIN DONE", 11)))
        # the edge: quiet for ten minutes, not ten minutes and a second
        self.assertIn("quiet", self.run_hook(self.a_finished_session("CHAIN DONE", 9.9), session="s2"))
        self.assertIn("sent to 2", self.run_hook(self.a_finished_session("CHAIN DONE", 10), session="s3"))

    def test_a_background_session_that_needs_input_is_quieted_the_same_way(self):
        self.assertIn("quiet", self.run_hook(self.a_finished_session("REPORT READY", 1), kind="agent_needs_input"))
        self.assertEqual(self.post.calls, [])

    def test_a_permission_prompt_is_not_quieted(self):
        path = self.a_finished_session("REPORT READY", 1)
        self.assertIn("sent to 2", self.run_hook(path, kind="permission_prompt"))
        self.assertIn("waits for a permission", self.post.calls[0][2]["text"])
        self.assertIn("sent to 2", self.run_hook(path, kind="elicitation_dialog", session="s2"))

    def test_a_session_that_did_not_say_it_is_a_wait(self):
        path = self.transcript(entry("user", 9, "which of the two?"), entry("assistant", 2, "Which table do you mean? I can report when ready."))
        self.assertIn("sent to 2", self.run_hook(path))
        # the words are the two phrases as a session says them, not any mention of a report
        self.assertIsNone(alert.said_done({"transcript_path": path}, NOW))

    def test_a_new_prompt_after_the_words_ends_the_quiet(self):
        # it said REPORT READY three minutes ago, a person typed since, and the session waits again: that is a wait
        path = self.transcript(entry("assistant", 3, "REPORT READY"), entry("user", 2, "one more thing"),
                               entry("assistant", 1, blocks=[{"type": "tool_use", "id": "y", "name": "Read", "input": {}}]))
        self.assertIsNone(alert.said_done({"transcript_path": path}, NOW))
        self.assertIn("sent to 2", self.run_hook(path))
        # and its later words, which are not the phrase, are what counts
        path = self.transcript(entry("assistant", 3, "REPORT READY"), entry("user", 2, "one more thing"), entry("assistant", 1, "Which one?"))
        self.assertIn("sent to 2", self.run_hook(path, session="s2"))

    def test_a_side_chains_words_are_not_the_sessions(self):
        path = self.transcript(entry("assistant", 4, "Shall I go on?"), entry("assistant", 1, "REPORT READY", isSidechain=True))
        self.assertIsNone(alert.said_done({"transcript_path": path}, NOW))
        self.assertEqual(alert.last_words(path)[0], "Shall I go on?")

    def test_a_transcript_that_cannot_be_read_does_not_break_the_hook_and_does_not_quiet_it(self):
        cases = {
            "absent": os.path.join(self.d.name, "no-such-file.jsonl"),
            "a folder": self.d.name,
            "not json": self.transcript("{broken", "REPORT READY", "\x00\x01"),
            "empty": self.transcript(""),
            "another shape": self.transcript(json.dumps(["REPORT READY"]), json.dumps({"type": "assistant", "message": "REPORT READY"}),
                                             json.dumps({"type": "assistant", "message": {"content": 7}})),
        }
        for i, (what, path) in enumerate(cases.items()):
            before = len(self.post.calls)
            self.assertIn("sent to 2", self.run_hook(path, session=f"s{i}"), what)
            self.assertEqual(len(self.post.calls), before + 2, what)
        # no transcript named at all, as an older Claude Code sends the event
        e = {k: v for k, v in EVENT.items()}
        self.assertIn("sent to 2", alert.hook(json.dumps(e), post=self.post, env=envs(**KEYS), state_dir=os.path.join(self.d.name, "state"), now=NOW + 5000))
        self.assertIsNone(alert.said_done({}, NOW))
        self.assertIsNone(alert.said_done({"transcript_path": None}, NOW))

    def test_an_entry_without_its_time_is_dated_by_the_file(self):
        e = json.loads(entry("assistant", 0, "CHAIN DONE"))
        del e["timestamp"]
        path = self.transcript(json.dumps(e))
        wrote = os.path.getmtime(path)
        self.assertEqual(alert.said_done({"transcript_path": path}, wrote + 120)[0], "CHAIN DONE")
        self.assertIsNone(alert.said_done({"transcript_path": path}, wrote + 601))

    def test_only_the_end_of_a_long_transcript_is_read(self):
        long_line = entry("user", 60, "x" * 5000)
        path = self.transcript(*([long_line] * 40), entry("assistant", 2, "REPORT READY"))
        self.assertEqual(alert.last_words(path, tail=3000)[0], "REPORT READY")   # the tail cuts a line in two: it is passed over
        self.assertEqual(alert.said_done({"transcript_path": path}, NOW)[0], "REPORT READY")

    def test_the_quiet_does_not_spend_the_sessions_ten_minute_allowance(self):
        # nothing was sent while quiet, so the first real wait afterwards is said at once
        path = self.a_finished_session("REPORT READY", 5)
        self.assertIn("quiet", self.run_hook(path))
        self.assertIn("sent to 2", self.run_hook(path, now=NOW + 6 * 60))   # eleven minutes after the words

    def test_as_a_process_it_prints_nothing_and_exits_0(self):
        path = self.a_finished_session("REPORT READY", 5)
        e = {k: v for k, v in os.environ.items() if k not in ("RESEND_API_KEY", "DIGEST_RECIPIENTS")}
        e["ERW_ALERTS"] = "off"
        for p in (path, os.path.join(self.d.name, "absent.jsonl")):
            r = subprocess.run([sys.executable, os.path.join(ROOT, "scripts", "alert.py"), "hook"], input=json.dumps({**EVENT, "transcript_path": p}),
                               capture_output=True, text=True, timeout=60, env=e)
            self.assertEqual((r.returncode, r.stdout, r.stderr), (0, "", ""))


class TheWords(unittest.TestCase):
    def test_the_rule_is_ten_minutes_two_phrases_and_the_waits_for_input(self):
        self.assertEqual(alert.DONE_QUIET_S, 600)
        self.assertEqual(set(alert.DONE_WORDS), {"REPORT READY", "CHAIN DONE"})
        self.assertEqual(set(alert.DONE_KINDS), {"idle_prompt", "agent_needs_input"})
        self.assertTrue(set(alert.DONE_KINDS) < set(alert.WAITS))

    def test_the_documents_say_what_a_save_is_now(self):
        doc, wf, script = src("docs", "machines.md"), src(".github", "workflows", "chain-watch.yml"), src("scripts", "alert.py")
        for text, what in ((doc, "docs/machines.md"), (wf, "chain-watch.yml"), (script, "alert.py")):
            self.assertIn("main included", text, what)
            self.assertIn("github-actions[bot]", text, what)
            self.assertIn("scripts/githooks/", text, what)
            self.assertNotIn(chr(0x2014), text, what)
        self.assertIn("REPORT READY", doc)
        self.assertIn("CHAIN DONE", doc)
        self.assertIn("transcript_path", doc)
        self.assertNotIn("A save** is a commit pushed to a `wip/` or `task/` branch (read from GitHub), or a beat.", doc)
        self.assertNotIn(chr(0x2014), src("tests", "test_session116_alerts.py"))

    def test_the_hook_still_needs_only_the_standard_library(self):
        imports = {ln.split()[1].split(".")[0] for ln in src("scripts", "alert.py").splitlines() if ln.startswith(("import ", "from "))}
        self.assertEqual(imports - {"argparse", "datetime", "json", "os", "socket", "sys", "time", "types", "urllib"}, set())


if __name__ == "__main__":
    unittest.main()

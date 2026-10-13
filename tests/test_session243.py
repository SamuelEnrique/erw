"""Session 243: the email rule (the owner's ruling of 12 October 2026).

Energy Research Warehouse (ERW). docs/machines.md, "The email rule". A person gets two emails from the machinery and
no other: one for a machine, 15 minutes after it went idle, saying it is ready for review; and one a UTC day when the
daily run is red. Every other check still runs and records, and emails nothing.

What is held here: the check that sends a machine's one line (scripts/alert.py ready), the gate in the sender itself,
the wiring of the workflow, and the documents. The daily run's email is held in tests/test_session202.py beside the
failures it reads; the idle step, the precheck, the idle alarm, the hook and the chain watch in the tests of the
sessions that wrote them (188, 91, 116), each changed to the rule.

No request, no email, no model call: the table, the sender and the clock are stand-ins.
"""

import datetime as dt
import io
import json
import os
import sys
import types
import unittest
import urllib.parse
from contextlib import redirect_stdout

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
for p in ("scripts", "warehouse"):
    sys.path.insert(0, os.path.join(ROOT, p))
import alert  # noqa: E402
import chain_queue  # noqa: E402
import duty  # noqa: E402
import notify  # noqa: E402

UTC = dt.timezone.utc
EM = chr(0x2014)
ENV = {"SUPABASE_URL": "https://x.supabase.co/rest/v1/", "SUPABASE_SERVICE_KEY": "k", "RESEND_API_KEY": "r", "DIGEST_RECIPIENTS": "a@x, b@x", "DIGEST_FROM": "ERW <e@x>"}
env = lambda name: ENV.get(name, "")  # noqa: E731


def at(h, m=0, day=13):
    return dt.datetime(2026, 10, day, h, m, tzinfo=UTC)


def src(*parts):
    with open(os.path.join(ROOT, *parts), encoding="utf-8") as f:
        return f.read()


def idle(machine, when, reason=None, status="ok"):
    return {"at": when.isoformat(), "workflow": f"local:{machine}", "run_id": None, "step": "idle", "status": status,
            "reason": alert.READY_MARK + f"queue/next/ is empty: {machine} has nothing left to run after \"the night's chain\"" if reason is None else reason}


class Table:
    """A stand-in for erw_health behind PostgREST, and for the sender: get() answers the queries scripts/alert.py
    makes, post() adds a row or keeps an email."""

    def __init__(self, rows=()):
        self.rows, self.mails, self.now, self.refuse = list(rows), [], at(8, 0), False

    def get(self, url, headers=None, timeout=30):
        q = dict((k, v[0]) for k, v in urllib.parse.parse_qs(url.split("?", 1)[1]).items())
        out = list(self.rows)
        for k, v in q.items():
            if k in ("select", "order", "limit"):
                continue
            op, _, val = v.partition(".")
            if k == "at":
                t = alert.parse(val)
                out = [r for r in out if (alert.parse(r["at"]) >= t if op == "gte" else alert.parse(r["at"]) < t)]
            elif op == "eq":
                out = [r for r in out if str(r.get(k)) == val]
            elif op == "neq":
                out = [r for r in out if str(r.get(k)) != val]
            elif op == "like":
                out = [r for r in out if str(r.get(k) or "").startswith(val.rstrip("*"))]
        out.sort(key=lambda r: r["at"], reverse=q.get("order") == "at.desc")
        if q.get("limit"):
            out = out[:int(q["limit"])]
        text = json.dumps(out)
        return types.SimpleNamespace(status_code=200, text=text, json=lambda: json.loads(text))

    def post(self, url, headers=None, timeout=30, json=None):
        if "resend" in url:
            if self.refuse:
                return types.SimpleNamespace(status_code=500, text="no", json=lambda: {})
            self.mails.append(json)
            return types.SimpleNamespace(status_code=200, text="{}", json=lambda: {})
        self.rows.append({"at": self.now.isoformat(), **json})
        return types.SimpleNamespace(status_code=201, text="", json=lambda: None)

    def memory(self):
        return [r["reason"] for r in self.rows if r["workflow"] == "alerts"]


def check(t, now, marks=None, **kw):
    t.now = now
    out = io.StringIO()
    with redirect_stdout(out):
        code = alert.ready(now=now, get=t.get, post=t.post, env=env, on_duty=lambda: marks or {}, **kw)
    return code, out.getvalue()


class AMachineIsReadyForReview(unittest.TestCase):
    def test_one_email_15_minutes_after_the_machine_went_idle_and_never_again(self):
        t = Table([idle("lab-desktop", at(7, 40))])
        for now in (at(7, 41), at(7, 50), at(7, 54)):
            code, said = check(t, now)
            self.assertEqual((code, t.mails), (0, []), now)
            self.assertIn("its line goes 15 minutes after", said)
        code, said = check(t, at(7, 56))
        self.assertEqual(code, 0)
        self.assertEqual([m["to"] for m in t.mails], [["a@x"], ["b@x"]])                    # one message to each fixed recipient
        self.assertEqual(t.mails[0]["subject"], "ERW: lab-desktop is ready for review")
        self.assertEqual(t.mails[0]["text"], "The machine lab-desktop is ready for review. Idle since 07:40 UTC: queue/next/ is empty: lab-desktop has "
                                             "nothing left to run after \"the night's chain\".\n")
        self.assertEqual(set(t.mails[0]), {"from", "to", "subject", "text"})
        self.assertEqual(t.memory(), ["ready|lab-desktop|2026-10-13T07:40"])
        for now in (at(8, 11), at(9, 26), at(13, 30)):                                      # every later check: nothing
            code, said = check(t, now)
            self.assertEqual((code, len(t.mails)), (0, 2), now)
        self.assertEqual(alert.READY_MIN, 15)

    def test_a_check_that_runs_late_still_sends_it_once(self):
        t = Table([idle("lab-desktop", at(7, 40))])
        check(t, at(9, 5))                                                                  # GitHub's schedule ran late
        self.assertEqual(len(t.mails), 2)
        check(t, at(9, 20))
        self.assertEqual(len(t.mails), 2)

    def test_a_machine_on_duty_again_is_not_ready(self):
        t = Table([idle("lab-desktop", at(7, 40))])
        code, said = check(t, at(8, 0), marks={"lab-desktop": at(7, 48)})                   # the next chain's precheck passed at 07:48
        self.assertEqual((code, t.mails, t.memory()), (0, [], []))
        self.assertIn("lab-desktop went idle at 07:40 UTC and is on duty again since 07:48 UTC", said)
        # a mark taken before it went idle is the one it gave up: it does not hold the line back
        check(t, at(8, 0), marks={"lab-desktop": at(6, 7)})
        self.assertEqual(len(t.mails), 2)

    def test_each_machine_gets_its_own_and_only_its_own(self):
        t = Table([idle("lab-desktop", at(7, 40)), idle("samueloldlaptop", at(7, 52))])
        check(t, at(7, 58))
        self.assertEqual([m["subject"] for m in t.mails], ["ERW: lab-desktop is ready for review"] * 2)
        check(t, at(8, 13))
        self.assertEqual([m["subject"] for m in t.mails][2:], ["ERW: samueloldlaptop is ready for review"] * 2)
        check(t, at(8, 28))
        self.assertEqual(len(t.mails), 4)

    def test_a_row_without_the_mark_is_never_a_line(self):
        # a machine that asked while off duty (idle already), an idle row written before this session, and a row that
        # is not an idle declaration at all
        t = Table([idle("lab-desktop", at(7, 40), reason="queue/next/ is empty: lab-desktop has nothing left to run (it was not on duty: idle already, no line follows)"),
                   idle("samueloldlaptop", at(7, 40), reason="queue/next/ is empty: samueloldlaptop has nothing left to run"),
                   {**idle("other", at(7, 40)), "step": "dm_sync"}, {**idle("failed-row", at(7, 40)), "status": "failed"}])
        code, said = check(t, at(8, 0))
        self.assertEqual((code, t.mails), (0, []))
        self.assertIn("quiet: no machine went idle in the last 6 hours", said)

    def test_a_failed_precheck_is_the_machines_one_line_with_its_reason(self):
        line = "Precheck failed on lab-desktop at 06:07 UTC (session 243): 1 of 6 checks. push_dry_run: git push --dry-run: exit 128. No work was started."
        t = Table([idle("lab-desktop", at(6, 7), reason=alert.READY_MARK + line)])
        check(t, at(6, 25))
        self.assertEqual(t.mails[0]["text"], "The machine lab-desktop is ready for review. Idle since 06:07 UTC: " + line + "\n")
        # several sessions of a chain each failed their precheck: the newest row is the one judged, so one line
        t = Table([idle("lab-desktop", at(6, 7), reason=alert.READY_MARK + line), idle("lab-desktop", at(6, 9), reason=alert.READY_MARK + line),
                   idle("lab-desktop", at(6, 11), reason=alert.READY_MARK + line)])
        check(t, at(6, 23))
        self.assertEqual(t.mails, [])                                                       # the newest is 12 minutes old
        check(t, at(6, 38))
        self.assertEqual((len(t.mails), t.memory()), (2, ["ready|lab-desktop|2026-10-13T06:11"]))

    def test_without_the_memory_only_the_check_in_the_quarter_of_an_hour_after_15_minutes_sends(self):
        class NoMemory(Table):
            def get(self, url, headers=None, timeout=30):
                if "workflow=eq.alerts" in url:
                    raise OSError("no answer")
                return super().get(url, headers, timeout)
        sent = []
        for minutes in range(0, 120, 15):
            t = NoMemory([idle("lab-desktop", at(7, 40))])
            check(t, at(7, 40) + dt.timedelta(minutes=minutes + 4))
            if t.mails:
                sent.append(minutes)
        self.assertEqual(sent, [15])                                                        # the check at 19 minutes, and no other

    def test_a_line_that_cannot_be_sent_is_exit_1_and_is_tried_again(self):
        t = Table([idle("lab-desktop", at(7, 40))])
        t.refuse = True
        code, said = check(t, at(7, 56))
        self.assertEqual((code, t.memory()), (1, []))
        self.assertIn("alert: not sent (RuntimeError: Resend HTTP 500", said)
        t.refuse = False
        code, _ = check(t, at(8, 11))
        self.assertEqual((code, len(t.mails)), (0, 2))

    def test_a_dry_run_prints_the_line_and_sends_and_remembers_nothing(self):
        t = Table([idle("lab-desktop", at(7, 40))])
        code, said = check(t, at(8, 0), dry_run=True)
        self.assertEqual((code, t.mails, t.memory()), (0, [], []))
        self.assertIn("Subject: ERW: lab-desktop is ready for review", said)

    def test_marks_that_cannot_be_read_do_not_lose_the_line(self):
        def broken():
            raise RuntimeError("erw_locks: HTTP 503")
        t = Table([idle("lab-desktop", at(7, 40))])
        t.now = at(8, 0)
        with redirect_stdout(io.StringIO()):
            code = alert.ready(now=at(8, 0), get=t.get, post=t.post, env=env, on_duty=broken)
        self.assertEqual((code, len(t.mails)), (0, 2))

    def test_the_line_is_one_line_within_300_characters_without_an_em_dash(self):
        subject, line = alert.ready_line("m" * 40, at(7, 40), alert.READY_MARK + "a very long reason " * 40 + EM)
        self.assertLessEqual(len(line), 300)
        self.assertNotIn("\n", line)
        self.assertNotIn(EM, line)
        self.assertNotIn("@", subject + line)


class NothingElseIsEmailed(unittest.TestCase):
    def test_the_sender_refuses_every_kind_but_the_two(self):
        t = Table()
        self.assertEqual(alert.MAILED, ("ready", "daily red"))
        with redirect_stdout(io.StringIO()) as out:
            for kind in (None, "chain watch", "idle alarm", "failure", "morning summary", "session waits", "precheck", "notify", "Ready"):
                self.assertEqual(alert.send("ERW: x", "a line", post=t.post, env=env, kind=kind), 0, kind)
                self.assertEqual(alert.deliver("ERW: x", "a line\n", "<p>a line</p>", post=t.post, env=env, kind=kind), 0, kind)
        self.assertEqual(t.mails, [])
        self.assertIn("not emailed (the email rule, session 243; kind: chain watch): ERW: x: a line", out.getvalue())
        for kind in alert.MAILED:
            self.assertEqual(alert.send("ERW: x", "a line", post=t.post, env=env, kind=kind), 2, kind)
        self.assertEqual(len(t.mails), 4)

    def test_the_resend_address_is_reached_from_one_function_of_the_alert_scripts(self):
        # scripts/alert.py's deliver() is the only place of the machinery's own scripts that posts to the sender, and it
        # holds the gate; notify.py keeps its sender for a dry run's message and its main() never calls it
        text = src("scripts", "alert.py")
        self.assertEqual(text.count("post(RESEND"), 1)
        body = text.split("def deliver(", 1)[1].split("\ndef ", 1)[0]
        self.assertLess(body.index("if kind not in MAILED:"), body.index("post(RESEND"))
        for rel in ("duty.py", "chain_queue.py", "precheck.py"):
            self.assertNotIn("api.resend.com", src("scripts", rel), rel)
        self.assertNotIn("alert_mail", src("warehouse", "health.py"))
        sent = []
        keep, notify.send = notify.send, lambda *a, **k: sent.append(a) or 2
        try:
            with redirect_stdout(io.StringIO()):
                for extra in ([], ["--failed"]):
                    self.assertEqual(notify.main(["--session", "243", "--branch", "task/243-email-rule", "--line", "landed"] + extra), 0)
        finally:
            notify.send = keep
        self.assertEqual(sent, [])

    def test_the_idle_step_writes_the_row_the_check_reads(self):
        rows, printed = [], []
        code = chain_queue.take(root=os.path.join(ROOT, "tests", "fixtures", "no-such-root"), who="lab-desktop", now=at(7, 40), out=printed.append, planner=None,
                                rec=lambda step, status, reason, wf: rows.append({"at": at(7, 40).isoformat(), "workflow": wf, "run_id": None, "step": step,
                                                                                   "status": status, "reason": reason}) or True,
                                off=lambda: "lab-desktop is off duty", held=lambda: {"token": "t", "what": "chain of 12 to 13 October, sessions 243 to 250"})
        self.assertEqual(code, chain_queue.IDLE_EXIT)
        t = Table(rows)
        check(t, at(7, 50))
        self.assertEqual(t.mails, [])
        check(t, at(8, 0))
        self.assertEqual(t.mails[0]["text"], "The machine lab-desktop is ready for review. Idle since 07:40 UTC: queue/next/ is empty: lab-desktop has nothing "
                                             "left to run after \"chain of 12 to 13 October, sessions 243 to 250\".\n")

    def test_the_names_agree_between_the_idle_row_and_the_duty_mark(self):
        # the check matches a machine's idle row (local:<name>) with its duty mark (duty:<name>): both are duty.clean()
        self.assertEqual(duty.row_name("Lab Desktop"), duty.PREFIX + "lab-desktop")
        self.assertIn('f"local:{who}"', src("scripts", "chain_queue.py"))
        self.assertIn("who = who or duty.clean(", src("scripts", "chain_queue.py"))
        self.assertIn('f"local:{name}"', src("scripts", "precheck.py"))


class TheWiring(unittest.TestCase):
    def test_the_chain_watch_runs_the_check_and_only_two_steps_hold_the_key_that_sends(self):
        wf = src(".github", "workflows", "chain-watch.yml")
        ready = 'python warehouse/health.py run --step "ready for review" --retries 0 -- python scripts/alert.py ready'
        self.assertIn(ready, wf)
        self.assertLess(wf.index('--step "idle alarm"'), wf.index(ready))
        self.assertLess(wf.index(ready), wf.index('--step "new failures"'))
        steps = wf.split("      - name: ")[1:]
        holds = [s.splitlines()[0] for s in steps if "secrets.RESEND_API_KEY" in s]
        self.assertEqual(holds, ["A machine that went idle 15 minutes ago is ready for review", "Record new failures; one email a day when the daily run is red"])
        self.assertIn('- cron: "*/15 * * * *"', wf)
        self.assertNotIn(EM, wf)
        with open(os.path.join(ROOT, ".github", "workflows", "chain-watch.yml"), "rb") as f:
            self.assertNotIn(b"\r", f.read())

    def test_the_check_needs_only_what_the_runner_installs(self):
        for rel in ("alert.py", "duty.py"):
            top = {ln.split()[1].split(".")[0] for ln in src("scripts", rel).splitlines() if ln.startswith(("import ", "from "))}
            self.assertEqual(top - {"argparse", "datetime", "json", "os", "socket", "subprocess", "sys", "time", "types", "urllib", "alert"}, set(), rel)

    def test_the_rule_is_written_where_a_session_reads_it(self):
        doc = src("docs", "machines.md")
        self.assertIn("### The email rule (session 243)", doc)
        for words in ("ready for review", "15 minutes after", "The daily run is red", "python scripts/alert.py ready", "recorded, not emailed",
                      "The digest and the Roundup are the product"):
            self.assertIn(words, doc, words)
        template = src("queue", "CHAIN_TEMPLATE.md")
        self.assertIn("15 minutes later", template)
        self.assertNotIn("sent one line by email", template)
        self.assertNotIn("is reported by email", template)

    def test_no_em_dash_in_what_the_session_wrote(self):
        for f in ("scripts/alert.py", "scripts/duty.py", "scripts/notify.py", "scripts/chain_queue.py", "scripts/precheck.py", "warehouse/health.py",
                  ".github/workflows/chain-watch.yml", "docs/machines.md", "queue/CHAIN_TEMPLATE.md", "queue/README.md", "tests/test_session243.py"):
            self.assertNotIn(EM, src(*f.split("/")), f)


if __name__ == "__main__":
    unittest.main()

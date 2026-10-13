#!/usr/bin/env python3
"""The precheck: what every session runs first, and what every chain file names (session 188).

Energy Research Warehouse (ERW). docs/machines.md, "Continuous work". An unattended session that finds out an hour in
that it cannot push, that Claude Code is signed out, or that a key is missing has spent the hour and then waits for a
person. This asks first, in under a minute, and does not wait: a failed precheck writes a short report, sends one line
to the fixed recipients (scripts/alert.py's sender: DIGEST_RECIPIENTS, never printed) and exits 1.

    python scripts/precheck.py --what "session 188"            the checks; on a pass the machine goes on duty
    python scripts/precheck.py --what "session 188" --dry-run  the same checks; the line is printed, not sent, and the
                                                               machine is not put on duty

The checks, each a named line with pass or fail and a plain reason:

    github_credentials   a way to sign in to GitHub is on the machine: GH_TOKEN (or GITHUB_TOKEN), a git credential
                         helper, or an ssh address for origin. Names only: no value is read out
    push_dry_run         git push --dry-run origin HEAD:refs/heads/wip/precheck-<machine> answers. A dry run signs in
                         and creates nothing. It never asks at the keyboard (GIT_TERMINAL_PROMPT=0) and stops at 90 s
    claude_signed_in     claude auth status says loggedIn (no session is started and no prompt is sent: no model call).
                         A CLI too old for that command is read from its credentials file or the environment instead
    role_file            .erw/machine.json is there and names the machine and its role (data or code). A git worktree
                         has no .erw/ and reads the main checkout's
    env_keys             .env (or the environment) holds every key the role needs, the list of scripts/setup.sh, and
                         the two the alerts need. Names only
    daily_cap            the daily cap of the scheduled model steps can be read, as warehouse/health.py budget reads
                         it: DAILY_MODEL_USD is a number of dollars (or unset: the default), and the day's spend
                         answers from the cost ledger on this machine or from Supabase's copy of it

All pass: exit 0, and the machine is on duty (scripts/duty.py start: the idle alarm watches it from now until it
declares idle or signs off; --no-duty leaves that out). Any fails: exit 1, a report in runs/precheck/, one line by
email, and nothing else: the session stops there and starts no work. Exit 2 is bad input.

Needs only Python's standard library for everything but daily_cap, which imports warehouse/health.py (requests).

Session 243, the email rule (the owner's ruling of 12 October 2026; docs/machines.md, "The email rule"): a failed
precheck no longer sends its line. It writes the report as before and records the machine as idle in erw_health with
the line as the reason; the chain watch sends the machine's one email 15 minutes later (python scripts/alert.py
ready), which says it is ready for review and carries that reason. A precheck that passes in those 15 minutes puts
the machine on duty, and then nothing is sent.
"""

import argparse
import datetime as dt
import json
import os
import shutil
import subprocess
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.abspath(os.path.join(HERE, ".."))
sys.path.insert(0, HERE)
import alert  # noqa: E402  (one line, 300 characters)
import duty  # noqa: E402   (the role file, the keys, the sender, and the mark a passing precheck writes)

UTC = dt.timezone.utc
PUSH_TIMEOUT_S = 90
# scripts/setup.sh and setup.ps1: the keys each role needs
ROLE_KEYS = {
    "code": ("SUPABASE_URL", "SUPABASE_SERVICE_KEY", "SUPABASE_ANON_KEY"),
    "data": ("SUPABASE_URL", "SUPABASE_SERVICE_KEY", "SUPABASE_ANON_KEY", "SUPABASE_DB_URL", "EIA_API_KEY", "REDIVIS_API_TOKEN",
             "REDIVIS_OWNER", "ANTHROPIC_API_KEY"),
}
# without these an unattended machine can tell nobody anything (scripts/alert.py)
ALERT_KEYS = ("RESEND_API_KEY", "DIGEST_RECIPIENTS")
CHECKS = ("github_credentials", "push_dry_run", "claude_signed_in", "role_file", "env_keys", "daily_cap")


def sh(cmd, cwd=ROOT, timeout=60, env=None):
    """(exit code, output) of a command; never raises: a command that is absent or hangs is exit 127 or 124."""
    try:
        r = subprocess.run(cmd, cwd=cwd, capture_output=True, text=True, encoding="utf-8", errors="replace", timeout=timeout,
                           stdin=subprocess.DEVNULL, env={**os.environ, **(env or {})})
        return r.returncode, ((r.stdout or "") + (r.stderr or "")).strip()
    except subprocess.TimeoutExpired:
        return 124, f"no answer in {timeout} seconds"
    except OSError as exc:
        return 127, f"{type(exc).__name__}: {exc}"


def last_line(text, limit=160):
    lines = [ln.strip() for ln in str(text).splitlines() if ln.strip()]
    return alert.one_line(lines[-1], limit) if lines else ""


def check_github_credentials(env=duty.env, run=sh):
    have = [n for n in ("GH_TOKEN", "GITHUB_TOKEN") if env(n)]
    code, helper = run(["git", "config", "--get", "credential.helper"])
    helper = helper.splitlines()[0].strip() if code == 0 and helper else ""
    _, origin = run(["git", "remote", "get-url", "origin"])
    ssh = origin.startswith(("git@", "ssh://"))
    found = ([f"{' and '.join(have)} set"] if have else []) + ([f"git's credential helper is \"{helper}\""] if helper else []) + (["origin is an ssh address"] if ssh else [])
    if not found:
        return False, "no GH_TOKEN or GITHUB_TOKEN in .env or the environment, no git credential helper, and origin is not an ssh address"
    return True, "; ".join(found)


def check_push_dry_run(machine_name="machine", run=sh):
    ref = f"refs/heads/wip/precheck-{duty.clean(machine_name)}"
    code, out = run(["git", "push", "--dry-run", "origin", f"HEAD:{ref}"], timeout=PUSH_TIMEOUT_S,
                    env={"GIT_TERMINAL_PROMPT": "0", "GCM_INTERACTIVE": "never"})
    if code != 0:
        return False, f"git push --dry-run to {ref[11:]}: exit {code}: {last_line(out) or 'no output'}"
    return True, f"git push --dry-run to {ref[11:]} answered (a dry run creates nothing)"


def check_claude_signed_in(run=sh, env=duty.env, home=None, which=shutil.which):
    exe = which("claude")
    if not exe:
        return False, "the claude command is not on PATH (Claude Code is not installed for this user)"
    code, out = run([exe, "auth", "status", "--json"], timeout=45)
    try:
        said = json.loads(out[out.index("{"):out.rindex("}") + 1])
    except ValueError:
        said = None
    if isinstance(said, dict) and "loggedIn" in said:
        if said["loggedIn"]:
            return True, f"claude auth status: signed in ({alert.one_line(said.get('authMethod') or 'method not named', 40)})"
        return False, "claude auth status: not signed in (claude auth login, at the keyboard)"
    # a CLI without "auth status": what it would sign in with
    cred = os.path.join(home or os.path.expanduser("~"), ".claude", ".credentials.json")
    if os.path.exists(cred) and os.path.getsize(cred) > 2:
        return True, "claude auth status is not offered by this CLI; its credentials file is present"
    for n in ("CLAUDE_CODE_OAUTH_TOKEN", "ANTHROPIC_API_KEY"):
        if env(n):
            return True, f"claude auth status is not offered by this CLI; {n} is set"
    return False, f"claude auth status did not answer (exit {code}) and no credentials file or key was found"


def check_role_file(state=None):
    state = state or duty.state_dir()
    path = os.path.join(state, "machine.json")
    if not os.path.exists(path):
        return False, ".erw/machine.json is absent (python warehouse/lock.py role code --name <name>, or scripts/setup)"
    m = duty.machine(state)
    if not m:
        return False, ".erw/machine.json cannot be read as JSON"
    if not m.get("name") or m.get("role") not in ROLE_KEYS:
        return False, f".erw/machine.json names {m.get('name')!r} with the role {m.get('role')!r}: a name and data or code are needed"
    return True, f"{m['name']} is a {m['role']} machine"


def check_env_keys(role=None, env=duty.env):
    if role not in ROLE_KEYS:
        return False, "the role is not known (role_file), so the keys it needs are not known"
    need = ROLE_KEYS[role] + tuple(k for k in ALERT_KEYS if k not in ROLE_KEYS[role])
    missing = [k for k in need if not env(k)]
    if missing:
        return False, f"no value for {', '.join(missing)} in .env or the environment (needed by a {role} machine; values are never shown)"
    return True, f"{len(need)} keys a {role} machine needs are set (values not shown)"


def check_daily_cap(env=duty.env, day=None, health=None, ledger=None, get=None):
    raw = env("DAILY_MODEL_USD")
    if raw:
        try:
            if float(raw) < 0:
                raise ValueError(raw)
        except ValueError:
            return False, "DAILY_MODEL_USD is set but is not a number of dollars"
    try:
        if health is None:
            sys.path.insert(0, os.path.join(ROOT, "warehouse"))
            import health  # the reading warehouse/health.py budget makes (session 176)
        cap = float(raw) if raw else health.MODEL_CAP_DEFAULT
        day = day or dt.datetime.now(UTC).date().isoformat()
        seen = []

        if get is None:
            import requests
            get = requests.get

        def watched(*a, **k):  # the same request, watched: did Supabase's copy of the ledger answer?
            r = get(*a, **k)
            seen.append(r.status_code)
            return r
        local = ledger or os.path.join(ROOT, "warehouse", "output", health.LEDGER + ".csv")
        spent, calls = health.model_spend(day, path=local, get=watched)
    except Exception as exc:
        return False, f"the day's spend could not be read ({type(exc).__name__}: {alert.one_line(exc, 120)})"
    remote = bool(seen) and all(s < 300 for s in seen)
    if not remote and not os.path.exists(local):
        return False, "the day's spend could not be read: Supabase's copy of the cost ledger did not answer and this machine holds no ledger file"
    return True, (f"USD {cap:.2f} a UTC day ({'DAILY_MODEL_USD' if raw else 'the default: DAILY_MODEL_USD is not set'}); USD {spent:.2f} spent today "
                  f"in {calls} calls of the scheduled model steps, read from "
                  + " and ".join((["Supabase's copy of the ledger"] if remote else []) + (["this machine's ledger file"] if os.path.exists(local) else [])))


def default_checks(state=None):
    """The six checks in order, as (name, function). The role file is read once: two checks need what it says."""
    state = state or duty.state_dir()
    m = duty.machine(state) or {}
    return [
        ("github_credentials", check_github_credentials),
        ("push_dry_run", lambda: check_push_dry_run(m.get("name") or "machine")),
        ("claude_signed_in", check_claude_signed_in),
        ("role_file", lambda: check_role_file(state)),
        ("env_keys", lambda: check_env_keys(m.get("role"))),
        ("daily_cap", check_daily_cap),
    ]


def run_checks(checks):
    """[(name, passed, reason)]. A check that raises has failed, with what it raised as the reason."""
    out = []
    for name, fn in checks:
        try:
            ok, why = fn()
        except Exception as exc:
            ok, why = False, f"the check itself failed ({type(exc).__name__}: {alert.one_line(exc, 120)})"
        out.append((name, bool(ok), alert.one_line(why, 280)))
    return out


def failure_line(results, machine_name, what, now):
    """The one line a failed precheck sends: which checks failed and why, within alert.py's 300 characters."""
    bad = [(n, why) for n, ok, why in results if not ok]
    head = f"Precheck failed on {machine_name} at {now:%H:%M} UTC" + (f" ({alert.one_line(what, 40)})" if what else "") + f": {len(bad)} of {len(results)} checks. "
    room = max(30, (alert.MAX_LINE - len(head) - 22) // len(bad) - 4)
    return alert.one_line(head + "; ".join(f"{n}: {why}"[:room].rstrip() for n, why in bad) + ". No work was started.")


def report_text(results, machine_name, what, now, sent):
    bad = [r for r in results if not r[1]]
    lines = [f"# Precheck on {machine_name}, {now:%Y-%m-%d %H:%M} UTC: {'failed' if bad else 'passed'}", "",
             f"- For: {what or 'not named'}",
             f"- Checks: {len(results) - len(bad)} of {len(results)} passed",
             f"- The line: {sent}",
             "- Written by `python scripts/precheck.py` (docs/machines.md, \"Continuous work\"). No work was started." if bad else
             "- Written by `python scripts/precheck.py` (docs/machines.md, \"Continuous work\").",
             "", "| Check | Result | Reason |", "|---|---|---|"]
    lines += [f"| `{n}` | {'pass' if ok else '**fail**'} | {why.replace('|', '/')} |" for n, ok, why in results]
    return "\n".join(lines) + "\n"


def record_idle(reason, workflow):
    """One row of erw_health, step "idle", through scripts/alert.py's own writer (the standard library alone), with the
    keys as scripts/duty.py finds them. True when it was written."""
    return alert.write_row(workflow, "idle", "ok", reason, env=duty.env)


def precheck(what="", dry_run=False, no_duty=False, hours=duty.HOURS, checks=None, record=record_idle, on_duty=duty.start,
             state=None, report_dir=None, now=None, out=print, send=None):  # send: accepted, never called (session 243)
    """Run the checks, print a line for each, and on a failure write the report and record the machine as idle with
    the line as the reason (session 243, the email rule: nothing is emailed here; the machine's one email, 15 minutes
    later, says it is ready for review and why). Returns (exit code, results, the report's path or None)."""
    now = now or dt.datetime.now(UTC)
    state = state or duty.state_dir()
    m = duty.machine(state) or {}
    name = duty.clean(m.get("name") or os.environ.get("COMPUTERNAME") or os.environ.get("HOSTNAME") or "machine")
    results = run_checks(checks if checks is not None else default_checks(state))
    for n, ok, why in results:
        out(f"{'pass' if ok else 'FAIL'}  {n:<19} {why}")
    bad = [r for r in results if not r[1]]
    if not bad:
        if dry_run or no_duty:
            out(f"precheck passed: {len(results)} of {len(results)}" + ("; dry run, so the machine is not put on duty" if dry_run else "; --no-duty, so the machine is not put on duty"))
            return 0, results, None
        try:
            out("precheck passed: " + on_duty(name, what, hours, state=state))
        except Exception as exc:  # the checks passed: a mark that could not be written is said, and the session runs
            out(f"precheck passed, but the machine could not be put on duty ({type(exc).__name__}: {alert.one_line(exc, 160)}): the idle alarm does not watch it")
        return 0, results, None
    line = failure_line(results, name, what, now)
    follows = f"the machine's one email follows {alert.READY_MIN} minutes later (python scripts/alert.py ready)"
    if dry_run:
        out(line)
        sent = "printed, not recorded (dry run)"
    else:
        try:
            sent = (f"recorded as idle in erw_health; {follows}" if record(alert.one_line(alert.READY_MARK + line, 480), f"local:{name}")
                    else "NOT recorded in erw_health: no email will follow")
        except Exception as exc:
            sent = f"NOT recorded in erw_health: no email will follow ({type(exc).__name__}: {alert.one_line(exc, 160)})"
    report_dir = report_dir or os.path.join(ROOT, "runs", "precheck")
    os.makedirs(report_dir, exist_ok=True)
    path = os.path.join(report_dir, f"{now:%Y%m%dT%H%M%SZ}-{name}.md")
    with open(path, "w", encoding="utf-8", newline="\n") as f:
        f.write(report_text(results, name, what, now, sent))
    out(f"precheck FAILED: {len(bad)} of {len(results)} checks; the line was {sent}; report: {os.path.relpath(path, ROOT)}")
    return 1, results, path


def main(argv=None):
    ap = argparse.ArgumentParser(description="The precheck every session runs first (session 188)")
    ap.add_argument("--what", default="", help="what is about to run (a session, a chain): named in the line and on the duty mark")
    ap.add_argument("--dry-run", action="store_true", help="run the checks; print the line instead of sending it; do not go on duty")
    ap.add_argument("--no-duty", action="store_true", help="a pass does not put the machine on duty")
    ap.add_argument("--hours", type=float, default=duty.HOURS, help="the duty mark lapses by itself after this long (default 16)")
    a = ap.parse_args(argv)
    code, _, _ = precheck(a.what, a.dry_run, a.no_duty, a.hours)
    return code


if __name__ == "__main__":
    sys.exit(main())

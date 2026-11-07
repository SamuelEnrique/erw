#!/usr/bin/env python3
"""A bot's push to main, refused when it would make main red (session 3713, chain 208).

Energy Research Warehouse (ERW). docs/state/main_red_2026-11-06.md: the daily run's "Daily prices 2026-11-06" commit
(e2794ff06) reached main at 01:32 UTC with eleven tests of seven modules failing on a clean checkout, and the data
machine's page-file commits of 30 October rewrote files tests held to dated figures; nothing ran the suite on either
before the push. Every automated commit to main now passes through this first:

    python scripts/push_guard.py --who "daily prices" --step "commit" [--ref HEAD] [--red-branch wip/red-daily-2026-11-06]

It runs the whole suite on a clean copy of the commit (scripts/suite_gate.py --ref: no warehouse/output, no key, as
on GitHub's runner). Passed: exit 0, and the caller pushes to main. Failed:

- the failing tests are printed one a line, and appended to GitHub's step summary when GITHUB_STEP_SUMMARY is set, so
  the run's log names them;
- with --red-branch, the commit is pushed to that wip/ branch instead (never to main, never to task/), for a session
  to repair: nothing of the run is lost;
- with --step, one failed row of erw_health is written for that step (warehouse/health.py record), its reason
  "push to main refused: N failing tests: <the first names>". For the daily run and the data machine's run that row
  is what the one "daily red" email of the email rule (docs/machines.md) is read from: no new notification;
- exit 1, and the caller does not push to main.

--dry-run runs the suite and prints what would be done, and pushes and records nothing. Exit 2: bad input. The suite's
log is runs/suite_gate/<sha>.out. Standard library only (and suite_gate.py beside it).
"""

import argparse
import os
import subprocess
import sys
import tempfile

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.abspath(os.path.join(HERE, ".."))
sys.path.insert(0, HERE)
import suite_gate  # noqa: E402

MAX_NAMES_IN_REASON = 6


def git(args, cwd=ROOT):
    return subprocess.run(["git", *args], cwd=cwd, capture_output=True, text=True, encoding="utf-8", errors="replace", stdin=subprocess.DEVNULL)


def reason_of(names):
    """The row's reason: how many tests failed and the first of them."""
    shown = ", ".join(names[:MAX_NAMES_IN_REASON])
    more = f" and {len(names) - MAX_NAMES_IN_REASON} more" if len(names) > MAX_NAMES_IN_REASON else ""
    return f"push to main refused: {len(names)} failing tests: {shown}{more}"[:400]


def guard(ref, who, step=None, red_branch=None, dry_run=False, python=sys.executable, run=None, record=None, push=None):
    """Run the suite on ref; on a failure name the tests, push to red_branch and record the step. Returns the exit code.
    run, record and push stand in for the suite, the health row and the push in tests."""
    sha = git(["rev-parse", ref]).stdout.strip()
    if not sha:
        print(f"push_guard: not a commit here: {ref}")
        return 2
    if red_branch and not red_branch.startswith("wip/"):
        print(f"push_guard: --red-branch must be a wip/ branch, not {red_branch}")
        return 2
    with tempfile.TemporaryDirectory() as tmp:
        names = os.path.join(tmp, "names.txt")
        code = (run or _run)(sha, names, python)
        failing = []
        if os.path.exists(names):
            with open(names, encoding="utf-8") as f:
                failing = [ln.strip() for ln in f if ln.strip()]
    if code == 0:
        print(f"push_guard: {who}: the suite passed on {sha[:9]}; the push to main may go ahead")
        return 0
    if code not in (0, 1):
        print(f"push_guard: {who}: the suite could not run on {sha[:9]} (exit {code}); the push to main is refused")
        failing = failing or ["the suite did not run"]
    why = reason_of(failing or ["the suite stopped before naming a test"])
    print(f"::error title={who}: push to main refused::{why}")
    if dry_run:
        print(f"push_guard: dry run: would push {sha[:9]} to {red_branch or '(no branch)'} and record {step or '(no step)'}")
        return 1
    if red_branch:
        rc = (push or _push)(sha, red_branch)
        print(f"push_guard: the commit {sha[:9]} {'was pushed to ' + red_branch if rc == 0 else 'could not be pushed to ' + red_branch + f' (exit {rc})'}")
    if step:
        (record or _record)(step, why, python)
    return 1


def _run(sha, names, python):
    summary = os.environ.get("GITHUB_STEP_SUMMARY")
    argv = [python, os.path.join(HERE, "suite_gate.py"), "--ref", sha, "--names", names]
    if summary:
        argv += ["--summary", summary]
    return subprocess.run(argv, cwd=ROOT, stdin=subprocess.DEVNULL).returncode


def _push(sha, branch):
    return subprocess.run(["git", "push", "--force", "origin", f"{sha}:refs/heads/{branch}"], cwd=ROOT, stdin=subprocess.DEVNULL).returncode


def _record(step, why, python):
    subprocess.run([python, os.path.join(ROOT, "warehouse", "health.py"), "record", "--step", step, "--status", "failed", "--reason", why],
                   cwd=ROOT, stdin=subprocess.DEVNULL)


def main(argv):
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    ap.add_argument("--who", required=True, help="the job, for the log line (\"daily prices\", \"data machine daily\")")
    ap.add_argument("--ref", default="HEAD")
    ap.add_argument("--step", help="record a failed row of erw_health for this step on a refusal")
    ap.add_argument("--red-branch", help="on a refusal, push the commit to this wip/ branch")
    ap.add_argument("--dry-run", action="store_true")
    a = ap.parse_args(argv)
    return guard(a.ref, a.who, a.step, a.red_branch, a.dry_run)


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))

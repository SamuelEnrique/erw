#!/usr/bin/env python3
"""The whole suite on a clean checkout, the failing tests named (session 3712, chain 208).

Energy Research Warehouse (ERW). docs/state/main_red_2026-11-06.md: main was red from 31 October to 5 November 2026 and
again on 6 November from 01:32 UTC because commits reached main that no one had run the whole suite on. GitHub's merge
gate tested a task/ branch's own head, not the branch merged with the main it would land on, and the bots' commits (the
daily run's, the data machine's) were pushed with no suite at all; the daily run's own step that ran the suite recorded
"Warning: The 'generic' unit for NumPy timedelta is deprecated" as the reason, not the tests that failed. This runs the
suite the way GitHub's runner does and says which tests failed:

    python scripts/suite_gate.py                       the suite on this checkout as it is
    python scripts/suite_gate.py --ref HEAD            the suite on a clean copy of a commit (git worktree add --detach): no
                                                       warehouse/output, no .env, no untracked file, as on GitHub's runner
    python scripts/suite_gate.py --ref HEAD --log runs/suite.out --summary "$GITHUB_STEP_SUMMARY"

The tests run as `python -m unittest discover -s tests` with ERW_LOCK_EXEMPT=1 and every key taken out of the
environment (the names scripts/land_check.py takes out: Supabase, Anthropic, tokens, secrets), so a test cannot reach a
store. The output goes to the log (default runs/suite_gate/<sha>.out). At the end it prints one line a failing test,
"FAIL <module.Class.test>" or "ERROR <...>", then "failing tests: N" or "the suite passed: N tests". With --summary the
same list is appended to that file (GitHub's step summary). With --names FILE the failing names are written one a line.

Exit codes: 0 the suite passed; 1 a test failed or errored, or the suite stopped before its summary line; 2 bad input
(not a git checkout, the ref not a commit). Standard library only.
"""

import argparse
import os
import re
import shutil
import subprocess
import sys
import tempfile

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.abspath(os.path.join(HERE, ".."))
# scripts/land_check.py SECRET_NAME: names whose values never reach the suite (GitHub's test step has no secret)
SECRET_NAME = re.compile(r"SUPABASE|ANTHROPIC|OPENAI|API_KEY|TOKEN|SECRET|PASSWORD|RESEND|REDIVIS|DB_URL", re.I)
FAILED = re.compile(r"^(FAIL|ERROR): (\S+) \(([^)]+)\)\s*$")
RAN = re.compile(r"^Ran (\d+) tests? in ")
VERDICT = re.compile(r"^(OK|FAILED)\b(.*)$")


def clean_env(env=None):
    """The environment the suite runs in: no key, the lock exemption on."""
    env = dict(os.environ if env is None else env)
    for k in list(env):
        if SECRET_NAME.search(k):
            del env[k]
    env["ERW_LOCK_EXEMPT"] = "1"
    env["PYTHONIOENCODING"] = "utf-8"
    return env


def failing(lines):
    """The failing tests named in unittest's output: [(kind, name)], each once, in order. unittest writes
    "FAIL: test_x (tests.test_mod.Class.test_x)" (Python 3.11 on) or "FAIL: test_x (tests.test_mod.Class)" (older), and
    "ERROR: setUpClass (tests.test_mod.Class)" or "ERROR: test_mod (unittest.loader._FailedTest.test_mod)" for a class or
    a module that could not run."""
    out, seen = [], set()
    for line in lines:
        m = FAILED.match(line.rstrip("\r\n"))
        if not m:
            continue
        kind, test, where = m.groups()
        name = where if where.endswith("." + test) or where.startswith("unittest.loader") else f"{where}.{test}"
        if where.startswith("unittest.loader"):
            name = f"{test} (the module could not be imported)"
        if (kind, name) not in seen:
            seen.add((kind, name))
            out.append((kind, name))
    return out


def verdict(lines):
    """(tests run or None, "OK" or "FAILED" or None) from the suite's last lines."""
    ran = ok = None
    for line in lines:
        m = RAN.match(line)
        if m:
            ran = int(m.group(1))
        v = VERDICT.match(line.strip())
        if v and ran is not None:
            ok = v.group(1)
    return ran, ok


def git(args, cwd):
    return subprocess.run(["git", *args], cwd=cwd, capture_output=True, text=True, encoding="utf-8", errors="replace", stdin=subprocess.DEVNULL)


def run_suite(root, log, python=sys.executable, env=None, timeout=None):
    """The suite in root, its output into log. Returns (exit code or None at the timeout, the log's lines)."""
    os.makedirs(os.path.dirname(os.path.abspath(log)), exist_ok=True)
    with open(log, "w", encoding="utf-8", errors="replace") as f:
        try:
            p = subprocess.run([python, "-m", "unittest", "discover", "-s", "tests"], cwd=root, env=clean_env(env),
                               stdout=f, stderr=subprocess.STDOUT, stdin=subprocess.DEVNULL, timeout=timeout)
            code = p.returncode
        except subprocess.TimeoutExpired:
            code = None
    with open(log, encoding="utf-8", errors="replace") as f:
        return code, f.read().splitlines()


MAX_DETAIL_LINES = 400


def details(lines):
    """unittest's report of the failures (from its first line of '=' to the end), at most MAX_DETAIL_LINES: the
    tracebacks, which a run's log should show beside the names, since the suite's own output goes to a file."""
    for i, line in enumerate(lines):
        if line.startswith("=" * 20):
            out = lines[i:]
            return out[:MAX_DETAIL_LINES] + ([f"... ({len(out) - MAX_DETAIL_LINES} more lines in the log)"] if len(out) > MAX_DETAIL_LINES else [])
    return []


def report(code, lines, summary=None, names=None, label=""):
    """Print the failing tests and the verdict; append them to a step summary. The exit code: 0 or 1."""
    bad = failing(lines)
    ran, ok = verdict(lines)
    if bad:
        print("\n".join(details(lines)))
    for kind, name in bad:
        print(f"{kind} {name}")
    passed = code == 0 and ok == "OK" and not bad
    if passed:
        line = f"the suite passed{label}: {ran} tests"
    elif ran is None:
        line = f"the suite stopped before its summary line{label} (exit {code}); failing tests named so far: {len(bad)}"
    else:
        line = f"failing tests{label}: {len(bad)} of {ran}"
    print(line)
    if summary:
        with open(summary, "a", encoding="utf-8") as f:
            f.write(f"### {line}\n\n" + "".join(f"- {kind} `{name}`\n" for kind, name in bad) + "\n")
    if names:
        with open(names, "w", encoding="utf-8") as f:
            f.write("".join(f"{name}\n" for _, name in bad))
    return 0 if passed else 1


def main(argv):
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    ap.add_argument("--ref", help="test a clean copy of this commit instead of the checkout as it is")
    ap.add_argument("--root", default=ROOT, help="the checkout (default: this repository)")
    ap.add_argument("--log", help="the suite's output (default runs/suite_gate/<sha>.out)")
    ap.add_argument("--summary", help="append the failing tests to this file (GitHub's step summary)")
    ap.add_argument("--names", help="write the failing tests' names to this file, one a line")
    ap.add_argument("--timeout-min", type=float, default=90.0)
    a = ap.parse_args(argv)
    root = os.path.abspath(a.root)
    head = git(["rev-parse", a.ref or "HEAD"], root)
    if head.returncode != 0:
        print(f"not a commit here: {a.ref or 'HEAD'} ({head.stdout.strip() or head.stderr.strip()})")
        return 2
    sha = head.stdout.strip()
    log = a.log or os.path.join(root, "runs", "suite_gate", f"{sha}.out")
    if not a.ref:
        code, lines = run_suite(root, log, timeout=a.timeout_min * 60)
        return report(code, lines, a.summary, a.names)
    tmp = tempfile.mkdtemp(prefix="erw-suite-")
    work = os.path.join(tmp, "checkout")
    add = git(["worktree", "add", "--detach", work, sha], root)
    if add.returncode != 0:
        print(f"git worktree add failed: {add.stderr.strip()[:400]}")
        shutil.rmtree(tmp, ignore_errors=True)
        return 2
    try:
        code, lines = run_suite(work, log, timeout=a.timeout_min * 60)
        return report(code, lines, a.summary, a.names, f" on {sha[:9]}")
    finally:
        git(["worktree", "remove", "--force", work], root)
        shutil.rmtree(tmp, ignore_errors=True)


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))

"""Runs the test suite with the clock moved forward, to find tests that pin a day (session 534).

    .venv/Scripts/python.exe scripts/suite_shifted.py --copy ../erw-clean --days 0 7 30 --out runs/x

For each number of days it runs `python -m unittest discover -s tests` in the copy
(a clean worktree of the commit, so no warehouse/output and no .env), with
scripts/clock_shift/ first on PYTHONPATH and NODE_OPTIONS requiring its Date shim, so
the suite and every python or node process it starts read a clock that many days
ahead (0 runs it unshifted, the baseline). The tests themselves are never patched.
It then lists every test that fails only with the clock moved. A shift of whole days
keeps the time of day: from 21 October 2026, 7 days reads 28 October and 30 days
20 November, at the hour the run starts.

Keys that write (the Supabase service key, the model's key, the mail key, GitHub's
token) are removed from the suite's environment, so a shifted test cannot write a
row dated in the future or reach the model. Exit 0 when no test fails only shifted,
1 when some do, 2 when the shift could not be confirmed in a child process.

`--tests mod1 mod2` runs those test modules (dotted, under tests/) instead of the
whole suite, to check a fix.
"""
from __future__ import annotations

import argparse
import os
import re
import subprocess
import sys
from datetime import datetime, timedelta, timezone
from pathlib import Path

HERE = Path(__file__).resolve().parent
SHIM_DIR = HERE / "clock_shift"
NODE_SHIM = SHIM_DIR / "date_shift.cjs"
DROP_KEYS = re.compile(r"^(SUPABASE_SERVICE.*|SUPABASE_DB_.*|ANTHROPIC.*|RESEND.*|GH_TOKEN|GITHUB_TOKEN|REDIVIS.*|ERW_CLOCK_SHIFT_SECONDS)$", re.I)
RESULT = re.compile(r"^(FAIL|ERROR): (\S+) \((\S+?)\)", re.M)


def child_env(days: int) -> dict[str, str]:
    env = {k: v for k, v in os.environ.items() if not DROP_KEYS.match(k)}
    env["ERW_LOCK_EXEMPT"] = "1"
    env["PYTHONIOENCODING"] = "utf-8"
    if days:
        env["ERW_CLOCK_SHIFT_SECONDS"] = str(days * 86400)
        env["PYTHONPATH"] = os.pathsep.join([str(SHIM_DIR)] + ([env["PYTHONPATH"]] if env.get("PYTHONPATH") else []))
        shim = "--require " + NODE_SHIM.as_posix()
        env["NODE_OPTIONS"] = (shim + " " + env["NODE_OPTIONS"]) if env.get("NODE_OPTIONS") else shim
    return env


def confirm_shift(days: int, env: dict[str, str], cwd: Path) -> str | None:
    """The day a python child and a node child read, against the day expected. None when both agree."""
    want = (datetime.now(timezone.utc) + timedelta(days=days)).date().isoformat()
    py = subprocess.run([sys.executable, "-c", "import datetime,time;print(datetime.datetime.now(datetime.timezone.utc).date().isoformat(), time.strftime('%Y-%m-%d', time.gmtime()))"],
                        env=env, cwd=cwd, capture_output=True, text=True)
    node = subprocess.run(["node", "-e", "console.log(new Date().toISOString().slice(0,10), new Date(Date.now()).toISOString().slice(0,10))"],
                          env=env, cwd=cwd, capture_output=True, text=True, shell=(os.name == "nt"))
    seen = (py.stdout.split() + node.stdout.split())
    if len(seen) != 4 or any(s != want for s in seen):
        return f"wanted {want} in every child, python said {py.stdout.strip()!r} {py.stderr.strip()[-200:]!r}, node said {node.stdout.strip()!r} {node.stderr.strip()[-200:]!r}"
    return None


def failures(text: str) -> set[str]:
    return {f"{m.group(1)} {m.group(3)}" for m in RESULT.finditer(text)}


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    ap.add_argument("--copy", default=str(HERE.parent), help="the repository copy to run the suite in")
    ap.add_argument("--days", type=int, nargs="+", default=[0, 7, 30])
    ap.add_argument("--out", required=True, help="a folder for each run's output and the comparison")
    ap.add_argument("--tests", nargs="*", default=None, help="test modules to run instead of the whole suite")
    a = ap.parse_args(argv)
    copy, out = Path(a.copy).resolve(), Path(a.out).resolve()
    out.mkdir(parents=True, exist_ok=True)
    cmd = [sys.executable, "-m", "unittest", "discover", "-s", "tests"]
    if a.tests:
        cmd = [sys.executable, "-m", "unittest"] + [t if t.startswith("tests.") else f"tests.{t}" for t in a.tests]
    found: dict[int, set[str]] = {}
    summary = []
    for days in a.days:
        env = child_env(days)
        bad = confirm_shift(days, env, copy)
        if bad:
            print(f"days={days}: the shift could not be confirmed: {bad}", file=sys.stderr)
            return 2
        started = datetime.now(timezone.utc)
        log = out / f"suite_days{days}.out"
        with open(log, "w", encoding="utf-8", errors="replace") as fh:
            rc = subprocess.run(cmd, cwd=copy, env=env, stdout=fh, stderr=subprocess.STDOUT).returncode
        text = log.read_text(encoding="utf-8", errors="replace")
        found[days] = failures(text)
        ran = re.findall(r"^Ran (\d+) tests? in ([\d.]+)s", text, re.M)
        tail = re.findall(r"^(OK.*|FAILED.*)$", text, re.M)
        line = f"days={days} exit={rc} ran={ran[-1][0] if ran else '?'} in {ran[-1][1] if ran else '?'}s {tail[-1] if tail else ''} (started {started:%Y-%m-%d %H:%M} UTC, clock read {(started + timedelta(days=days)).date()})"
        print(line)
        summary.append(line)
        (out / f"failures_days{days}.txt").write_text("".join(f"{f}\n" for f in sorted(found[days])), encoding="utf-8")
    base = found.get(0, set())
    only = sorted(set().union(*(v for d, v in found.items() if d)) - base) if any(d for d in found) else []
    lines = summary + ["", f"failing only with the clock moved: {len(only)}"]
    for f in only:
        lines.append(f + "  [" + " ".join(f"+{d}" for d in sorted(found) if d and f in found[d]) + "]")
    (out / "shifted_only.txt").write_text("\n".join(lines) + "\n", encoding="utf-8")
    print("\n".join(lines[len(summary):]))
    return 1 if only else 0


if __name__ == "__main__":
    sys.exit(main())

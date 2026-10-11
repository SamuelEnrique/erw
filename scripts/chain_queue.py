#!/usr/bin/env python3
"""The chain queue: the prompt files a machine runs next, in order (session 188).

Energy Research Warehouse (ERW). queue/README.md; docs/machines.md, "Continuous work". A chain of sessions ends, and the
machine then sits until a person pastes the next prompt. The next prompts are files instead:

    queue/next/NNN-<slug>.md    a whole prompt file (a chain, or one session), waiting; taken in name order
    queue/done/NNN-<slug>.md    taken: the file as it was run

    python scripts/chain_queue.py list
    python scripts/chain_queue.py next [--dry-run]

`next` is the last step of a chain's last session. With a file waiting it moves the first one to queue/done/ in one
commit of that move alone and prints the file's new path on its last line: the session then reads that file and runs
it. With nothing waiting it writes one row to the health table erw_health (step "idle", through warehouse/health.py's
own writer), sends one line to the fixed recipients (scripts/alert.py's sender; no address is printed), and takes the
machine off duty (scripts/duty.py), so the idle alarm does not also report a machine that has said it is idle.
--dry-run prints what would happen and moves, commits, writes and sends nothing.

This is not session 59's task queue (queue/todo, doing, done as scripts/taskqueue.py and the worker use them): that
one hands single tasks to whichever worker claims them, by role. A name beginning NNN-code- or NNN-data- is a task's
and is refused here, so the two never read each other's files.

The move is a commit on the branch the session is on; it is not pushed here (a push to main deploys: CLAUDE.md rule
8). One machine draws from queue/next/ at a time: a second machine that has not pulled the move would take the same file.

A file in queue/next/ whose name is not NNN-<slug>.md is left where it is and named in what is printed (and counted
in the idle line): it is never run.

Exit codes: 0 a file was taken (its path is the last line printed), or list; 3 nothing waits (idle: recorded and
said); 1 could not (git refused the move, or the idle row, the line or the duty mark failed); 2 bad input.
"""

import argparse
import datetime as dt
import os
import re
import shutil
import subprocess
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.abspath(os.path.join(HERE, ".."))
sys.path.insert(0, HERE)
import alert  # noqa: E402
import duty  # noqa: E402

NAME_RE = re.compile(r"^(\d{3,})-([a-z0-9][a-z0-9-]*)\.md$")
TASK_RE = re.compile(r"^\d{3,}-(code|data)-")   # scripts/taskqueue.py's names: not this queue's
IDLE_EXIT = 3
UTC = dt.timezone.utc


def waiting(root=ROOT):
    """(the prompt files of queue/next/ in order, the names there that are not NNN-<slug>.md). README.md and files
    whose name begins with a dot or an underscore are notes, not prompts."""
    d = os.path.join(root, "queue", "next")
    good, odd = [], []
    for f in sorted(os.listdir(d)) if os.path.isdir(d) else []:
        if f.startswith((".", "_")) or f.lower() == "readme.md" or not os.path.isfile(os.path.join(d, f)):
            continue
        (good if NAME_RE.match(f) and not TASK_RE.match(f) else odd).append(f)
    good.sort(key=lambda f: (int(NAME_RE.match(f).group(1)), f))
    return good, odd


def git(*args, root=ROOT):
    r = subprocess.run(["git", *args], cwd=root, capture_output=True, text=True, stdin=subprocess.DEVNULL)
    if r.returncode != 0:
        raise RuntimeError(f"git {' '.join(args[:2])}: {(r.stderr or r.stdout).strip()[:300]}")
    return r.stdout


def move(name, who, root=ROOT, git=git):
    """queue/next/<name> to queue/done/<name>, in one commit that holds that move and nothing else. A file a person
    put in queue/next/ without committing it is taken too: its commit then holds the file in queue/done/ only."""
    src, dst = f"queue/next/{name}", f"queue/done/{name}"
    if os.path.exists(os.path.join(root, dst)):
        raise RuntimeError(f"{dst} already exists: a file of that name was taken before; rename the one in queue/next/")
    os.makedirs(os.path.join(root, "queue", "done"), exist_ok=True)
    if git("ls-files", "--", src, root=root).strip():
        git("mv", src, dst, root=root)
        paths = [src, dst]
    else:
        shutil.move(os.path.join(root, src), os.path.join(root, dst))
        git("add", "--", dst, root=root)
        paths = [dst]
    git("commit", "-m", f"Queue: {name} taken by {who} (queue/next to queue/done)", "--", *paths, root=root)
    return dst


def health_row(step, status, reason, wf):
    """One row of erw_health through warehouse/health.py's own writer; True when it was written."""
    sys.path.insert(0, os.path.join(ROOT, "warehouse"))
    import health
    return health.record(step, status, reason, 0, wf=wf)


def take(dry_run=False, root=ROOT, who=None, rec=health_row, send=None, off=None, mover=move, now=None, out=print):
    """The `next` command. Returns the exit code."""
    send, off = send or duty.send, off or duty.off
    now = now or dt.datetime.now(UTC)
    who = who or duty.clean((duty.machine() or {}).get("name") or os.environ.get("COMPUTERNAME") or os.environ.get("HOSTNAME") or "machine")
    good, odd = waiting(root)
    if odd:
        out("not prompt files of this queue (NNN-<slug>.md; NNN-code- and NNN-data- are the task queue's), left where they are: " + ", ".join(odd))
    if good:
        name = good[0]
        if dry_run:
            out(f"would take queue/next/{name}, move it to queue/done/{name} in one commit, and print that path ({len(good) - 1} more waiting)")
            return 0
        dst = mover(name, who, root)
        out(f"taken: {name} by {who} ({len(good) - 1} more waiting); read the file below and run it")
        out(os.path.join(root, *dst.split("/")))
        return 0
    left = f" ({len(odd)} file{'s' if len(odd) != 1 else ''} there with a name this queue does not take)" if odd else ""
    why = f"queue/next/ is empty{left}: {who} has nothing left to run"
    line = alert.one_line(f"The machine {who} is idle since {now:%H:%M} UTC: queue/next/ is empty{left}. "
                          "Put the next prompt file there (NNN-<slug>.md) and start a session.")
    if dry_run:
        out(f"would write to erw_health: step idle, status ok, workflow local:{who}, reason: {why}")
        send("ERW: a machine is idle", line, True)
        out("would take the machine off duty (python scripts/duty.py off)")
        return IDLE_EXIT
    problems = []
    try:
        if not rec("idle", "ok", why, f"local:{who}"):
            problems.append("the row of erw_health was not written")
    except Exception as exc:
        problems.append(f"the row of erw_health was not written ({type(exc).__name__}: {alert.one_line(exc, 120)})")
    try:
        n = send("ERW: a machine is idle", line, False)
        out(f"idle: {why}; said to {n} fixed recipient{'s' if n != 1 else ''}")
    except Exception as exc:
        problems.append(f"the line was not sent ({type(exc).__name__}: {alert.one_line(exc, 120)})")
        out(f"idle: {why}")
    try:
        out(off())
    except Exception as exc:
        problems.append(f"the duty mark was not removed ({type(exc).__name__}: {alert.one_line(exc, 120)})")
    for p in problems:
        print(f"chain_queue: {p}", file=sys.stderr)
    return 1 if problems else IDLE_EXIT


def main(argv=None):
    ap = argparse.ArgumentParser(description="The chain queue: the prompt files a machine runs next (session 188)")
    ap.add_argument("action", choices=["next", "list"])
    ap.add_argument("--dry-run", action="store_true", help="next: say what would happen; move, commit, write and send nothing")
    a = ap.parse_args(argv)
    try:
        if a.action == "list":
            good, odd = waiting()
            print(f"{len(good)} waiting in queue/next/" + (":" if good else ""))
            for f in good:
                print(f"  {f}")
            if odd:
                print("not this queue's (left where they are): " + ", ".join(odd))
            return 0
        return take(a.dry_run)
    except Exception as exc:
        print(f"chain_queue: {type(exc).__name__}: {str(exc)[:300]}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    sys.exit(main())

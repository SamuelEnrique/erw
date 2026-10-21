#!/usr/bin/env python3
"""The build lock: one heavy process at a time on a machine (session 504).

Energy Research Warehouse (ERW). docs/machines.md, "Other checkouts". Chain files have named runs/build.lock since
19 October 2026 ("one heavy process at a time"), and no tool held it until chain 019's helper of 21 October
(runs/chain_019/buildlock.py, not in git), whose file format this keeps, so a lock it holds is honoured. A heavy
process is a site build, the whole suite, a browser check or Lighthouse.

    python scripts/buildlock.py acquire <who>      wait until free, then hold it (exit 0); exit 1 after the wait
    python scripts/buildlock.py release <who>      free it if <who> holds it (exit 0); held by another: left, exit 1
    python scripts/buildlock.py status             who holds it and since when (exit 0 free, 1 held)

    --wait-min N     acquire: minutes to wait before giving up (default 180)
    --stale-hours H  a lock older than this is taken as stale and removed (default 3)

The lock is one file, runs/build.lock in the main checkout, holding "<who> <UTC time>". A git worktree finds the main
checkout as scripts/duty.py does (git rev-parse --git-common-dir), so every worktree of one checkout shares one lock.
No path is passed on the command line, so Git Bash's MSYS_NO_PATHCONV=1 cannot hide the lock (session 422's first run
lost it that way, calling chain 019's helper by a /c/ path). ERW_BUILD_LOCK names another file (tests only).

Standard library only. Exit 2 is bad input.
"""

import argparse
import os
import subprocess
import sys
import time

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.abspath(os.path.join(HERE, ".."))
POLL_S = 20


def main_checkout(root=ROOT):
    """The main checkout this folder is a worktree of (or the folder itself); the folder itself when git cannot say."""
    try:
        r = subprocess.run(["git", "rev-parse", "--path-format=absolute", "--git-common-dir"], cwd=root,
                           capture_output=True, text=True, timeout=20, stdin=subprocess.DEVNULL)
        common = r.stdout.strip()
        if r.returncode == 0 and common:
            return os.path.abspath(os.path.join(common, ".."))
    except (OSError, subprocess.SubprocessError):
        pass
    return root


def lock_path(root=ROOT):
    """runs/build.lock in the main checkout, or ERW_BUILD_LOCK when it is set."""
    return os.environ.get("ERW_BUILD_LOCK") or os.path.join(main_checkout(root), "runs", "build.lock")


def holder(path):
    """(who, since) of the lock, or None when it is free or cannot be read."""
    try:
        with open(path, encoding="utf-8") as f:
            parts = f.read().split()
    except OSError:
        return None
    return (parts[0] if parts else "", parts[1] if len(parts) > 1 else "")


def stale(path, stale_hours, now=None):
    """Whether the lock file is older than stale_hours."""
    try:
        return (now or time.time()) - os.path.getmtime(path) > stale_hours * 3600
    except OSError:
        return False


def try_acquire(path, who):
    """Create the lock for who if no lock exists. True when it now holds it."""
    os.makedirs(os.path.dirname(path), exist_ok=True)
    try:
        fd = os.open(path, os.O_CREAT | os.O_EXCL | os.O_WRONLY)
    except FileExistsError:
        return False
    with os.fdopen(fd, "w", encoding="utf-8") as f:
        f.write(f"{who} {time.strftime('%Y-%m-%dT%H:%M:%SZ', time.gmtime())}")
    return True


def acquire(who, path=None, wait_min=180, stale_hours=3, poll_s=POLL_S, out=print):
    path = path or lock_path()
    t0 = time.time()
    while True:
        if try_acquire(path, who):
            out(f"build.lock held by {who} ({path})")
            return 0
        if stale(path, stale_hours):
            h = holder(path)
            out(f"build.lock: {h[0] if h else '?'}'s lock is older than {stale_hours} h: taken as stale and removed")
            try:
                os.remove(path)
            except OSError:
                pass
            continue
        if time.time() - t0 >= wait_min * 60:
            h = holder(path)
            out(f"build.lock: still held by {h[0] if h else '?'} after {wait_min} min: given up")
            return 1
        time.sleep(poll_s)


def release(who, path=None, out=print):
    path = path or lock_path()
    h = holder(path)
    if h is None:
        out("build.lock: not held")
        return 0
    if h[0] != who:
        out(f"build.lock held by {h[0]}, not {who}: left")
        return 1
    os.remove(path)
    out(f"build.lock released by {who}")
    return 0


def status(path=None, out=print):
    path = path or lock_path()
    h = holder(path)
    if h is None:
        out(f"build.lock is free ({path})")
        return 0
    out(f"build.lock held by {h[0]} since {h[1] or 'an unknown time'} ({path})")
    return 1


def main(argv=None):
    ap = argparse.ArgumentParser(description="The build lock: one heavy process at a time (session 504)")
    ap.add_argument("command", choices=["acquire", "release", "status"])
    ap.add_argument("who", nargs="?")
    ap.add_argument("--wait-min", type=float, default=180)
    ap.add_argument("--stale-hours", type=float, default=3)
    a = ap.parse_args(argv)
    if a.command in ("acquire", "release") and (not a.who or any(c.isspace() for c in a.who)):
        print("buildlock: acquire and release need a name without spaces", file=sys.stderr)
        return 2
    if a.command == "acquire":
        return acquire(a.who, wait_min=a.wait_min, stale_hours=a.stale_hours)
    if a.command == "release":
        return release(a.who)
    return status()


if __name__ == "__main__":
    sys.exit(main())

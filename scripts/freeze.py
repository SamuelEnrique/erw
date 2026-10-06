#!/usr/bin/env python3
"""Is the live site frozen? (session 116; CLAUDE.md, rule 9)

Energy Research Warehouse (ERW). A freeze is declared by a file named REVIEW_FREEZE in the repository root and by
nothing else. The file holds the freeze's first and last day:

    start: 2026-10-03
    end: 2026-10-06

Days are UTC calendar days and both are included. A line beginning with # is a note; any other "key: value" line is
kept for people (who the reviewer is) and not read. Only a person creates or removes the file.

    python scripts/freeze.py status          # says which holds; run it before a push that deploys
    python scripts/freeze.py hold            # for a scheduled job: "run" or "hold" (session 131, docs/freeze_hold.md)

What holds:
    no file                                  no freeze: a deploy with rule 8's snapshot is allowed            exit 0
    the file, and today before its start     no freeze yet: it begins on the start day                        exit 0
    the file, and today from start to end    FROZEN: nothing a visitor sees on a live page changes            exit 1
    the file, and today after its end        no freeze: it ended; a person may remove the file                exit 0
    the file, and it cannot be read as two   FROZEN until a person corrects or removes it: a file that says   exit 2
    dates (or its end is before its start)   "freeze" and cannot say until when is not read as permission

The hold (session 131). A scheduled job asks `hold` whether to run as usual or to hold everything a visitor would see
(the load into the live set, the commit to main) until the freeze ends. It answers "hold" only when both are true: the
site is frozen (status 1 or 2), and the hold is switched on, which is one line, `enabled: true`, in
warehouse/config/freeze_hold.yaml. A person writes that line; while it says false, is missing or cannot be read, the
answer is always "run" and every scheduled job does exactly what it did before session 131. `hold` always exits 0, so
it can never fail a job. With --github-output it writes hold=1 or hold=0 for the workflow's later steps, and with
--github-env ERW_FREEZE_HOLD=1 or 0 for the scripts they run.

Needs only Python's standard library. It reads two files and writes nothing but those two GitHub files when asked.
"""

import argparse
import datetime as dt
import os
import sys

ROOT = os.path.abspath(os.path.join(os.path.dirname(os.path.abspath(__file__)), ".."))
NAME = "REVIEW_FREEZE"
HOLD_SWITCH = os.path.join("warehouse", "config", "freeze_hold.yaml")


def read(root=None):
    """The freeze file's (start, end) as dates, or None when there is no file. Raises ValueError for a file that is
    there and cannot be read as two dates in order."""
    path = os.path.join(root or ROOT, NAME)
    if not os.path.lexists(path):
        return None
    try:
        with open(path, encoding="utf-8-sig") as f:
            lines = f.read().splitlines()
    except (OSError, UnicodeError) as e:
        raise ValueError(f"{NAME} cannot be read ({type(e).__name__})")
    got = {}
    for ln in lines:
        ln = ln.strip()
        if not ln or ln.startswith("#") or ":" not in ln:
            continue
        k, v = ln.split(":", 1)
        k = k.strip().lower()
        if k in ("start", "end"):
            if k in got:
                raise ValueError(f"{NAME} states its {k} twice")
            try:
                got[k] = dt.date.fromisoformat(v.strip())
            except ValueError:
                raise ValueError(f"{NAME}: its {k} is not a date written YYYY-MM-DD")
    missing = [k for k in ("start", "end") if k not in got]
    if missing:
        raise ValueError(f"{NAME} does not state its {' or its '.join(missing)}")
    if got["end"] < got["start"]:
        raise ValueError(f"{NAME}: its end, {got['end']}, is before its start, {got['start']}")
    return got["start"], got["end"]


def status(root=None, today=None):
    """(exit code, one line): 0 no freeze, 1 frozen, 2 the file cannot be read (frozen until a person corrects it)."""
    today = today or dt.datetime.now(dt.timezone.utc).date()
    try:
        got = read(root)
    except ValueError as e:
        return 2, f"FROZEN: {e}. A freeze file that cannot be read is a freeze until a person corrects or removes it."
    if got is None:
        return 0, f"no freeze: no file named {NAME} in the repository root. A deploy with a before and after snapshot is allowed."
    start, end = got
    if today < start:
        return 0, f"no freeze yet: {NAME} begins on {start} and ends on {end} (today is {today}, UTC). A deploy with a before and after snapshot is allowed."
    if today > end:
        return 0, f"no freeze: {NAME} ended on {end} (today is {today}, UTC). A person may remove the file. A deploy with a before and after snapshot is allowed."
    return 1, (f"FROZEN from {start} to {end}, both days included (today is {today}, UTC): no change to what a visitor sees on a live page, or to a table a live "
               "page reads, unless the session's prompt names the one deploy that may. Push to a wip/ branch and write the remaining commands under \"To finish\".")


def hold_enabled(root=None):
    """True only when the switch file's `enabled` line says true. Missing, unreadable, or anything else: False. The
    hold changes what the scheduled jobs do, so nothing but a person's plain line switches it on."""
    try:
        with open(os.path.join(root or ROOT, HOLD_SWITCH), encoding="utf-8-sig") as f:
            lines = f.read().splitlines()
    except (OSError, UnicodeError):
        return False
    said = [ln.split(":", 1)[1].split("#", 1)[0].strip().lower() for ln in lines
            if ln.strip().lower().startswith("enabled:")]
    return said == ["true"]


def hold(root=None, today=None):
    """(True to hold or False to run, one line) for a scheduled job."""
    code, line = status(root, today)
    if not hold_enabled(root):
        frozen = " A freeze is on, and the scheduled jobs do not hold for it." if code else ""
        return False, f"run: the freeze hold is not switched on ({HOLD_SWITCH.replace(os.sep, '/')} does not say enabled: true).{frozen}"
    if code == 0:
        return False, f"run: {line}"
    return True, (f"hold: {line} The scheduled jobs keep the 15-minute prices and the hourly network, fetch everything else, and hold "
                  "the load into the live set and the commit to main until the freeze ends (docs/freeze_hold.md).")


def main(argv=None):
    ap = argparse.ArgumentParser(description="Is the live site frozen? (CLAUDE.md, rule 9)")
    ap.add_argument("action", choices=["status", "hold"])
    ap.add_argument("--root", help="another checkout's root (default: this one)")
    ap.add_argument("--github-output", action="store_true", help="hold: also write hold=1 or hold=0 to $GITHUB_OUTPUT")
    ap.add_argument("--github-env", action="store_true", help="hold: also write ERW_FREEZE_HOLD=1 or 0 to $GITHUB_ENV")
    a = ap.parse_args(argv)
    if a.action == "hold":
        held, line = hold(a.root)
        print(line)
        for flag, var, text in ((a.github_output, "GITHUB_OUTPUT", f"hold={int(held)}"), (a.github_env, "GITHUB_ENV", f"ERW_FREEZE_HOLD={int(held)}")):
            if flag and os.environ.get(var):
                with open(os.environ[var], "a", encoding="utf-8") as f:
                    f.write(text + "\n")
        return 0
    code, line = status(a.root)
    print(line)
    return code


if __name__ == "__main__":
    sys.exit(main())

#!/usr/bin/env python3
"""The chain queue: the prompt files a machine runs next, in order (session 188).

Energy Research Warehouse (ERW). queue/README.md; docs/machines.md, "Continuous work". A chain of sessions ends, and the
machine then sits until a person pastes the next prompt. The next prompts are files instead:

    queue/next/NNN-<slug>.md    a whole prompt file (a chain, or one session), waiting; taken in name order
    queue/done/NNN-<slug>.md    taken: the file as it was run

    python scripts/chain_queue.py list
    python scripts/chain_queue.py next [--dry-run] [--file NNN-<slug>.md]

`next` is the last step of a chain's last session. With a file waiting it moves the first one to queue/done/ in one
commit of that move alone and prints the file's new path on its last line: the session then reads that file and runs
it. With nothing waiting it writes one row to the health table erw_health (step "idle", through warehouse/health.py's
own writer) and takes the machine off duty (scripts/duty.py), so the idle alarm does not also record a machine that
has said it is idle. --dry-run prints what would happen and moves, commits, writes and sends nothing.

Session 243, the email rule (the owner's ruling of 12 October 2026): `next` sends no email itself. The row it writes
is what the chain watch reads: 15 minutes after it, the machine's one email says it is ready for review
(python scripts/alert.py ready), unless the machine has gone on duty again by then.

Session 197, the planner: with nothing waiting and "planner: on" in docs/roadmap.md, `next` first runs
scripts/planner.py (`draft`). A chain it writes into queue/next/ is committed alone, pushed to a wip/ branch of its
own name (no deploy) and taken as the next file, exit 0. When the planner is off, which is the default, or refuses,
the machine idles as before.

This is not session 59's task queue (queue/todo, doing, done as scripts/taskqueue.py and the worker use them): that
one hands single tasks to whichever worker claims them, by role. A name beginning NNN-code- or NNN-data- is a task's
and is refused here, so the two never read each other's files.

The move is a commit on the branch the session is on; it is not pushed here (a push to main deploys: CLAUDE.md rule
8). One machine draws from queue/next/ at a time: a second machine that has not pulled the move would take the same file.

A file in queue/next/ whose name is not NNN-<slug>.md is left where it is and named in what is printed (and counted
in the idle line): it is never run.

Session 365, the machine a file is for. A prompt file may carry a line `machine: code` or `machine: data` in its first
ten lines (queue/CHAIN_TEMPLATE.md puts it under the title). `next` takes the lowest-numbered file whose line names
this machine's role (duty.machine()["role"], from .erw/machine.json) or this machine's own name, or that has no such
line; a file marked for another machine is left where it is and named in what is printed. When only such files wait,
the machine is idle as with an empty queue (the planner path included) and the idle line says the files wait for
another machine. A machine whose role is not known takes only files with no line: it cannot tell whose a marked file
is. A line with a value that is neither code, data nor this machine's name marks a file for no machine this one can
be: it is left too.

    python scripts/chain_queue.py next --file NNN-<slug>.md [--dry-run]

takes that one file by name, with the same move and commit, so a person can start a named chain on a machine. It
refuses (exit 2, nothing moved) a name that is not in queue/next/, a name of the task queue, and a file marked for
another machine; a machine whose role is not known takes a marked file by name (a person named it), and says so.
`list` shows each file's machine.

Exit codes: 0 a file was taken (its path is the last line printed), or list; 3 nothing waits (idle: recorded); 1
could not (git refused the move, or the idle row or the duty mark failed); 2 bad input (a --file that is refused).
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
BAD_INPUT = 2
UTC = dt.timezone.utc
ROLES = ("code", "data")
MACHINE_RE = re.compile(r"^\s*machine\s*:\s*(.*?)\s*$", re.I)   # session 365: "machine: code" or "machine: data"
MARK_LINES = 10                                                    # the line counts only within a file's first ten lines


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


def mark_of(text):
    """Session 365. The machine a prompt file is for: the value of its first line "machine: <value>" within its first
    ten lines, lower case, or None when it has no such line. "machine: code" and "machine: data" are the roles; a value
    that is neither is returned as it stands (a machine's name, or a blank of the template left unfilled)."""
    for line in (text or "").replace("\r\n", "\n").split("\n")[:MARK_LINES]:
        m = MACHINE_RE.match(line)
        if m:
            return m.group(1).strip().rstrip(".").lower() or "(empty)"
    return None


def mark(name, root=ROOT):
    """The mark of queue/next/<name> (mark_of), read from the file; a file that cannot be read is "(unreadable)"."""
    try:
        with open(os.path.join(root, "queue", "next", name), encoding="utf-8", errors="replace") as f:
            head = "".join(f.readline() for _ in range(MARK_LINES))
    except OSError:
        return "(unreadable)"
    return mark_of(head)


def known(role):
    """This machine's role when it is code or data, else None (not known)."""
    r = (role or "").strip().lower()
    return r if r in ROLES else None


def this_role():
    return (duty.machine() or {}).get("role")


def for_this(m, role, who=None):
    """Whether a file whose mark is m is for this machine: no mark, or its role, or its own name. A machine whose role
    is not known takes only a file with no mark."""
    if m is None:
        return True
    if known(role) is None:
        return False
    return m == known(role) or (who is not None and m == duty.clean(who))


def split(names, role, who=None, root=ROOT):
    """(the files of `names` for this machine, in order; [(name, mark)] of those left for another machine)."""
    mine, others = [], []
    for f in names:
        m = mark(f, root)
        (mine.append(f) if for_this(m, role, who) else others.append((f, m)))
    return mine, others


def others_line(others):
    return ", ".join(f"{f} (machine: {m})" for f, m in others)


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


def plan(who, root=ROOT, dry_run=False, out=print, git=git, role=None, now=None):
    """Session 197. With nothing waiting: when docs/roadmap.md says "planner: on", run the planner for this machine.
    Returns the name of the chain it wrote into queue/next/, committed alone and pushed to a wip/ branch of its own
    name (a wip/ branch does not deploy), or None when the planner is off, cannot read the roadmap, or refuses. With
    dry_run nothing is written: what the planner would do is printed, and None is returned."""
    import planner
    try:
        text = planner.read(os.path.join(root, planner.ROADMAP))
    except OSError:
        return None
    if not planner.status(text)["on"]:
        return None
    role = role or (duty.machine() or {}).get("role")
    if dry_run:
        out("the planner is on (docs/roadmap.md): python scripts/planner.py check says")
        planner.run("check", who, role, root=root, out=out, now=now)
        return None
    out("queue/next/ is empty and the planner is on (docs/roadmap.md): python scripts/planner.py draft")
    code, dest = planner.run("draft", who, role, root=root, out=out, now=now)
    if code != 0 or not dest:
        return None
    name = os.path.basename(dest)
    git("add", "--", f"queue/next/{name}", root=root)
    git("commit", "-m", f"Planner: {name} drafted for {who} from docs/roadmap.md", "--", f"queue/next/{name}", root=root)
    try:
        git("push", "origin", f"HEAD:refs/heads/wip/{name[:-3]}", root=root)
        out(f"planned chain committed and pushed to wip/{name[:-3]}")
    except RuntimeError as exc:
        out(f"planned chain committed; the push to wip/{name[:-3]} failed and is left for the chain's first save ({alert.one_line(exc, 160)})")
    return name


def by_name(name, role, who, root=ROOT, dry_run=False, mover=move, out=print):
    """Session 365, `next --file <name>`: take that one file of queue/next/, with the same move and commit as `next`.
    Returns the exit code: 0 taken (its path the last line printed), 2 refused and nothing moved."""
    given = (name or "").strip().replace("\\", "/")
    if given.startswith("queue/next/"):
        given = given[len("queue/next/"):]
    if not given or "/" in given:
        out(f"refused: --file takes a file's name in queue/next/ (NNN-<slug>.md), not {name!r}")
        return BAD_INPUT
    if TASK_RE.match(given):
        out(f"refused: {given} is a name of the task queue (NNN-code-, NNN-data-: scripts/taskqueue.py), not a prompt file of this queue")
        return BAD_INPUT
    if not NAME_RE.match(given):
        out(f"refused: {given} is not a name this queue takes (NNN-<slug>.md)")
        return BAD_INPUT
    good, _ = waiting(root)
    if given not in good:
        out(f"refused: there is no {given} in queue/next/ ({len(good)} waiting" + (f": {', '.join(good)})" if good else ")"))
        return BAD_INPUT
    m = mark(given, root)
    if not for_this(m, role, who):
        if known(role) is not None:
            out(f"refused: {given} is marked machine: {m}, and {who} is a {known(role)} machine; run it on a machine of that role, or change its line")
            return BAD_INPUT
        out(f"{who}'s role is not known (.erw/machine.json): {given}, marked machine: {m}, is taken because a person named it")
    rest = len(good) - 1
    if dry_run:
        out(f"would take queue/next/{given} by name, move it to queue/done/{given} in one commit, and print that path ({rest} more waiting)")
        return 0
    dst = mover(given, who, root)
    out(f"taken by name: {given} by {who} ({rest} more waiting); read the file below and run it")
    out(os.path.join(root, *dst.split("/")))
    return 0


def take(dry_run=False, root=ROOT, who=None, rec=health_row, send=None, off=None, mover=move, now=None, out=print, planner=plan, held=None, role=None, file=None):
    """The `next` command. Returns the exit code. `send` is accepted for a caller that still hands one in and is never
    called (session 243: this command emails nothing). `role` is this machine's (None: read from .erw/machine.json;
    anything but code or data: not known). `file`: take that one file by name (by_name)."""
    off, held = off or duty.off, held or duty.held
    now = now or dt.datetime.now(UTC)
    who = who or duty.clean((duty.machine() or {}).get("name") or os.environ.get("COMPUTERNAME") or os.environ.get("HOSTNAME") or "machine")
    role = this_role() if role is None else role
    if file is not None:
        return by_name(file, role, who, root, dry_run, mover, out)
    good, odd = waiting(root)
    if odd:
        out("not prompt files of this queue (NNN-<slug>.md; NNN-code- and NNN-data- are the task queue's), left where they are: " + ", ".join(odd))
    good, others = split(good, role, who, root)
    if others:
        if known(role) is None:
            out(f"{who}'s role is not known (.erw/machine.json): only files with no machine: line are taken; left where they are: " + others_line(others))
        else:
            out(f"for another machine ({who} is a {known(role)} machine), left where they are: " + others_line(others))
    if not good and planner is not None:
        # session 197: nothing waits for this machine. With "planner: on" the planner drafts the next chain; off (the default), nothing happens here
        try:
            planned = planner(who, root, dry_run, out)
            if planned:
                # the planner drafted it for this machine's role (machine: <role>, session 365): it is the file taken
                good = [planned] if planned in waiting(root)[0] else split(waiting(root)[0], role, who, root)[0]
        except Exception as exc:
            print(f"chain_queue: the planner could not run ({type(exc).__name__}: {alert.one_line(exc, 200)}); idle as without it", file=sys.stderr)
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
    head = "queue/next/ is empty"
    if others:
        # session 365: files wait, none of them for this machine
        n = len(others)
        head = (f"queue/next/ holds nothing for {who} ({known(role) or 'role not known'}): {n} file{'s' if n != 1 else ''} there "
                f"wait{'' if n != 1 else 's'} for another machine ({', '.join(f for f, _ in others)})")
    # Session 243, the email rule: nothing is emailed here. A machine that was on duty went idle: its row's reason
    # begins with alert.READY_MARK, and the chain watch sends its one line 15 minutes later (scripts/alert.py ready),
    # unless it has gone on duty again by then. A machine that was not on duty was idle already: its row says so and
    # no line follows, so asking twice is one email, not two.
    try:
        mark = held()
    except Exception:
        mark = None
    what = alert.one_line((mark or {}).get("what") or "", 120)
    why = f"{head}{left}: {who} has nothing left to run" + (f" after \"{what}\"" if what else "")
    why = alert.one_line(alert.READY_MARK + why if mark else why + " (it was not on duty: idle already, no line follows)", 480)
    follows = (f"the one email follows {alert.READY_MIN} minutes from now, from the chain watch (python scripts/alert.py ready), unless the machine is on duty again by then"
               if mark else "no email follows: the machine was not on duty")
    if dry_run:
        out(f"would write to erw_health: step idle, status ok, workflow local:{who}, reason: {why}")
        out(f"would send nothing here ({alert.RULE}): {follows}")
        out("would take the machine off duty (python scripts/duty.py off)")
        return IDLE_EXIT
    problems = []
    try:
        if not rec("idle", "ok", why, f"local:{who}"):
            problems.append("the row of erw_health was not written" + (": no email will follow" if mark else ""))
    except Exception as exc:
        problems.append(f"the row of erw_health was not written ({type(exc).__name__}: {alert.one_line(exc, 120)})")
    out(f"idle: {why}; {follows}")
    try:
        out(off())
    except Exception as exc:
        problems.append(f"the duty mark was not removed ({type(exc).__name__}: {alert.one_line(exc, 120)})")
    for p in problems:
        print(f"chain_queue: {p}", file=sys.stderr)
    return 1 if problems else IDLE_EXIT


def listing(root=ROOT, role=None, who=None, out=print):
    """The `list` command: each waiting file with its machine (session 365), and whether `next` here would take it."""
    role = this_role() if role is None else role
    who = who or duty.clean((duty.machine() or {}).get("name") or os.environ.get("COMPUTERNAME") or os.environ.get("HOSTNAME") or "machine")
    good, odd = waiting(root)
    mine, _ = split(good, role, who, root)
    out(f"{len(good)} waiting in queue/next/ ({len(mine)} for {who}, a {(known(role) + ' machine') if known(role) else 'machine whose role is not known'})" + (":" if good else ""))
    for f in good:
        m = mark(f, root)
        out(f"  {f}  machine: {m or 'any (no line)'}" + ("" if f in mine else "  (left for another machine)"))
    if odd:
        out("not this queue's (left where they are): " + ", ".join(odd))
    return 0


def main(argv=None):
    ap = argparse.ArgumentParser(description="The chain queue: the prompt files a machine runs next (session 188)")
    ap.add_argument("action", choices=["next", "list"])
    ap.add_argument("--dry-run", action="store_true", help="next: say what would happen; move, commit, write and send nothing")
    ap.add_argument("--file", metavar="NAME", help="next: take this one file of queue/next/ by name (session 365)")
    a = ap.parse_args(argv)
    try:
        if a.action == "list":
            if a.file is not None:
                print("chain_queue: --file goes with next, not list", file=sys.stderr)
                return BAD_INPUT
            return listing()
        return take(a.dry_run, file=a.file)
    except Exception as exc:
        print(f"chain_queue: {type(exc).__name__}: {str(exc)[:300]}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    sys.exit(main())

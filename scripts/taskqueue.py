#!/usr/bin/env python3
"""The task queue (session 59): work for the machines, as files in git. docs/machines.md.

Energy Research Warehouse (ERW).

    queue/todo/NNN-<role>-<slug>.md     waiting; role is code or data
    queue/doing/NNN-<role>-<slug>.md    claimed by a machine
    queue/done/NNN-<role>-<slug>.md     finished, with its report appended
    queue/summary/YYYY-MM-DD-<machine>.md   one line per task a machine finished that day

A task file is front matter, then the full prompt:

    ---
    role: code                # code or data; must match the file name
    spend_cap_usd: 4          # the most the task may spend on the Claude API
    timeout_minutes: 240      # the run is stopped after this (pauses for a usage limit do not count)
    permission_mode: auto     # Claude Code's --permission-mode; the repo's .claude/settings.json applies too
    ---
    # Title
    The prompt, complete: everything the task needs, since nobody will be there to answer.

Claiming is a commit that moves the file from todo/ to doing/ (and adds a line to its log), pushed to main. Two machines
claiming the same task: one push wins; the other undoes its commit, pulls, and moves on to the next task. A machine
working a task keeps a heartbeat, a row task:NNN in the Supabase table erw_locks (migration 016) renewed every 10
minutes and expiring after 30. A task in doing/ whose heartbeat has expired (a laptop closed, a machine crashed) is
stale: any worker moves it back to todo/ (requeue). Tasks are taken in number order.

    python scripts/taskqueue.py list
    python scripts/taskqueue.py new --role code --slug fix-x --title "Fix x" --cap 3 --prompt-file p.md
    python scripts/taskqueue.py requeue-stale [--dry-run]
    python scripts/taskqueue.py heartbeats
"""

import argparse
import datetime as dt
import json
import os
import re
import subprocess
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.abspath(os.path.join(HERE, ".."))
Q = os.path.join(ROOT, "queue")
STATES = ("todo", "doing", "done")
NAME_RE = re.compile(r"^(\d{3,})-(code|data)-([a-z0-9][a-z0-9-]*)\.md$")
HEARTBEAT_MINUTES = 30
GRACE_MINUTES = 15  # a task claimed less than this long ago is never stale: its worker may still be starting
DEFAULTS = {"spend_cap_usd": 2.0, "timeout_minutes": 240, "permission_mode": "auto"}

sys.path.insert(0, os.path.join(ROOT, "warehouse"))
import lock  # noqa: E402  (the machine's name and role, and the erw_locks functions)


def now():
    return dt.datetime.now(dt.timezone.utc).replace(microsecond=0)


def stamp(t=None):
    return (t or now()).strftime("%Y-%m-%dT%H:%M:%SZ")


def git(*args, check=True):
    r = subprocess.run(["git", *args], cwd=ROOT, capture_output=True, text=True)
    if check and r.returncode != 0:
        raise RuntimeError(f"git {' '.join(args)}: {(r.stderr or r.stdout).strip()[:400]}")
    return r


class Task:
    def __init__(self, path):
        self.path = path
        self.file = os.path.basename(path)
        self.state = os.path.basename(os.path.dirname(path))
        m = NAME_RE.match(self.file)
        if not m:
            raise ValueError(f"{self.file}: not NNN-<code|data>-<slug>.md")
        self.id, self.role, self.slug = m.group(1), m.group(2), m.group(3)
        self.text = open(path, encoding="utf-8").read()
        self.meta = dict(DEFAULTS)
        fm = re.match(r"^---\n(.*?)\n---\n", self.text, re.S)
        if fm:
            for ln in fm.group(1).splitlines():
                k, _, v = ln.partition(":")
                v = v.split("#", 1)[0].strip()
                if k.strip() and v:
                    self.meta[k.strip()] = v
        if self.meta.get("role", self.role) != self.role:
            raise ValueError(f"{self.file}: role {self.meta['role']!r} in the front matter, {self.role!r} in the name")
        self.cap = float(self.meta["spend_cap_usd"])
        self.timeout = int(self.meta["timeout_minutes"])
        self.mode = str(self.meta["permission_mode"])
        self.heartbeat_name = f"task:{self.id}"
        self.branch = f"task/{self.id}-{self.slug}" if self.role == "code" else "main"

    @property
    def prompt(self):
        """The prompt: the file after the front matter, without the worker's log and report sections."""
        body = re.sub(r"^---\n.*?\n---\n", "", self.text, count=1, flags=re.S)
        return re.split(r"\n## Queue log\n", body, maxsplit=1)[0].strip()

    def log_lines(self):
        m = re.search(r"\n## Queue log\n(.*?)(?=\n## |\Z)", self.text, re.S)
        return [ln[2:] for ln in m.group(1).splitlines() if ln.startswith("- ")] if m else []

    def last_claim(self):
        """(holder, time) of the latest claim in the log, or (None, None)."""
        for ln in reversed(self.log_lines()):
            m = re.match(r"(\S+) claimed by (\S+)", ln)
            if m:
                return m.group(2), dt.datetime.strptime(m.group(1), "%Y-%m-%dT%H:%M:%SZ").replace(tzinfo=dt.timezone.utc)
        return None, None

    def with_log(self, line, extra=""):
        """The file's text with a line added to its queue log (and an extra section after it)."""
        t = self.text.rstrip("\n")
        if "\n## Queue log\n" in t:
            head, _, rest = t.partition("\n## Queue log\n")
            log, sep, after = rest.partition("\n## ")
            t = head + "\n## Queue log\n" + log.rstrip("\n") + f"\n- {line}" + (("\n\n## " + after) if sep else "")
        else:
            t += f"\n\n## Queue log\n- {line}"
        return t + "\n" + (("\n" + extra.rstrip("\n") + "\n") if extra else "")


def tasks(state):
    d = os.path.join(Q, state)
    if not os.path.isdir(d):
        return []
    out = []
    for f in sorted(os.listdir(d)):
        if f.endswith(".md") and NAME_RE.match(f):
            out.append(Task(os.path.join(d, f)))
    return sorted(out, key=lambda t: int(t.id))


def find(task_id):
    for s in STATES:
        for t in tasks(s):
            if t.id == task_id:
                return t
    return None


def next_id():
    ids = [int(t.id) for s in STATES for t in tasks(s)]
    return f"{(max(ids) + 1) if ids else 1:03d}"


def sync_main():
    """Fetch and bring main up to origin/main: a fast-forward, or a merge; never a force or a rebase."""
    git("fetch", "-q", "origin", "main")
    if git("merge", "--ff-only", "-q", "origin/main", check=False).returncode != 0:
        git("merge", "--no-edit", "-q", "origin/main")


def on_main_clean():
    br = git("rev-parse", "--abbrev-ref", "HEAD").stdout.strip()
    if br != "main":
        raise RuntimeError(f"the queue is changed on main only; this checkout is on {br}")
    dirty = [ln for ln in git("status", "--porcelain", "--", "queue").stdout.splitlines()]
    if dirty:
        raise RuntimeError(f"queue/ has uncommitted changes: {dirty[:3]}")


def move(task, to, line, extra="", message=None):
    """Move a task file to another state with a log line, as one commit (not pushed)."""
    dst = os.path.join(Q, to, task.file)
    os.makedirs(os.path.dirname(dst), exist_ok=True)
    text = task.with_log(line, extra)
    git("mv", os.path.relpath(task.path, ROOT), os.path.relpath(dst, ROOT))
    with open(dst, "w", encoding="utf-8", newline="\n") as f:
        f.write(text)
    git("add", os.path.relpath(dst, ROOT))
    git("commit", "-q", "-m", message or f"queue: {task.file} {task.state} to {to}: {line}")
    return Task(dst)


def push_or_undo():
    """Push main. On a rejection (another machine pushed first), undo the last commit, pull, return False."""
    if git("push", "-q", "origin", "main", check=False).returncode == 0:
        return True
    git("reset", "-q", "--keep", "HEAD~1")
    sync_main()
    return False


def push_persist(tries=5):
    """Push main, merging origin/main between tries (a finish must not be lost to a race)."""
    for _ in range(tries):
        if git("push", "-q", "origin", "main", check=False).returncode == 0:
            return True
        sync_main()
    return False


# heartbeats: rows task:NNN in erw_locks

def heartbeat_status(task):
    rows = lock.rpc("erw_lock_status", p_name=task.heartbeat_name)
    return rows[0] if rows else None


def heartbeat_take(task, holder, token=None):
    """Renew this worker's heartbeat with its token, or take it if free or expired. Returns the token or None."""
    if token and lock.rpc("erw_lock_renew", p_name=task.heartbeat_name, p_token=token, p_minutes=HEARTBEAT_MINUTES):
        return token
    return lock.rpc("erw_lock_acquire", p_name=task.heartbeat_name, p_holder=holder, p_task=task.file, p_minutes=HEARTBEAT_MINUTES)


def heartbeat_renew(task, token):
    return bool(lock.rpc("erw_lock_renew", p_name=task.heartbeat_name, p_token=token, p_minutes=HEARTBEAT_MINUTES))


def heartbeat_release(task, token):
    if token:
        lock.rpc("erw_lock_release", p_name=task.heartbeat_name, p_token=token)


def is_stale(task):
    """A task in doing/ is stale when it was claimed more than GRACE_MINUTES ago and its heartbeat is missing or expired.
    Without Supabase (no answer), nothing is called stale."""
    _, when = task.last_claim()
    if when is not None and (now() - when).total_seconds() < GRACE_MINUTES * 60:
        return False
    try:
        hb = heartbeat_status(task)
    except Exception:
        return False
    return hb is None or bool(hb.get("expired"))


# the worker's steps

def claim(role, holder, log=print):
    """Claim the first todo task for this role: commit, push; a lost race undoes and tries the next. Returns a Task or None."""
    on_main_clean()
    sync_main()
    tried = set()
    while True:
        cands = [t for t in tasks("todo") if t.role == role and t.file not in tried]
        if not cands:
            return None
        t = cands[0]
        tried.add(t.file)
        moved = move(t, "doing", f"{stamp()} claimed by {holder}", message=f"queue: {holder} claims {t.file}")
        if push_or_undo():
            log(f"claimed {t.file}")
            return moved
        log(f"lost the race for {t.file} (main moved); next task")


def requeue_stale(holder, dry_run=False, log=print, skip_holder=None):
    """Move every stale task in doing/ back to todo/. Returns the files moved. A worker passes its own name as skip_holder:
    its own tasks it resumes instead (a laptop that slept past its heartbeat)."""
    on_main_clean()
    sync_main()
    moved = []
    for t in tasks("doing"):
        who, when = t.last_claim()
        if (skip_holder and who == skip_holder) or not is_stale(t):
            continue
        if dry_run:
            moved.append(t.file)
            continue
        move(t, "todo", f"{stamp()} requeued by {holder}: stale (heartbeat expired; claimed by {who} at {stamp(when) if when else '?'})",
             message=f"queue: {t.file} back to todo (stale)")
        if push_or_undo():
            log(f"requeued {t.file} (stale)")
            moved.append(t.file)
    return moved


def finish(task, status, report, holder, summary_line):
    """Move a doing task to done/ with its report and the day's summary line, as one commit pushed to main."""
    on_main_clean()
    sync_main()
    cur = find(task.id)
    if cur is None or cur.state != "doing":
        raise RuntimeError(f"{task.file} is no longer in doing/ (it is in {cur.state if cur else 'no folder'}): another worker requeued it")
    done = move(cur, "done", f"{stamp()} {status} on {holder}", extra=report, message=f"queue: {cur.file} {status} ({holder})")
    day = now().strftime("%Y-%m-%d")
    safe = re.sub(r"[^A-Za-z0-9_.-]+", "-", holder)
    sp = os.path.join(Q, "summary", f"{day}-{safe}.md")
    os.makedirs(os.path.dirname(sp), exist_ok=True)
    first = not os.path.exists(sp)
    with open(sp, "a", encoding="utf-8", newline="\n") as f:
        if first:
            f.write(f"# Worker summary, {day}, {holder}\n\nOne line per task this machine finished (UTC). The tasks' reports are in queue/done/.\n\n")
        f.write(f"- {summary_line}\n")
    git("add", os.path.relpath(sp, ROOT))
    git("commit", "-q", "--amend", "--no-edit")
    if not push_persist():
        raise RuntimeError("could not push the finish to main after 5 tries; it is committed here and goes with the next push")
    return done


def new(role, slug, title, cap, prompt, timeout=240, mode="auto"):
    tid = next_id()
    p = os.path.join(Q, "todo", f"{tid}-{role}-{slug}.md")
    os.makedirs(os.path.dirname(p), exist_ok=True)
    with open(p, "w", encoding="utf-8", newline="\n") as f:
        f.write(f"---\nrole: {role}\nspend_cap_usd: {cap:g}\ntimeout_minutes: {timeout}\npermission_mode: {mode}\n---\n# {title}\n\n{prompt.strip()}\n")
    Task(p)  # parses, or fails
    return p


def main(argv=None):
    ap = argparse.ArgumentParser(description="ERW task queue (session 59)")
    sub = ap.add_subparsers(dest="cmd", required=True)
    sub.add_parser("list")
    sub.add_parser("heartbeats")
    rq = sub.add_parser("requeue-stale")
    rq.add_argument("--dry-run", action="store_true")
    nw = sub.add_parser("new")
    nw.add_argument("--role", choices=["code", "data"], required=True)
    nw.add_argument("--slug", required=True)
    nw.add_argument("--title", required=True)
    nw.add_argument("--cap", type=float, required=True)
    nw.add_argument("--timeout", type=int, default=240)
    nw.add_argument("--prompt-file", required=True)
    a = ap.parse_args(argv)
    if a.cmd == "list":
        for s in STATES:
            ts = tasks(s)
            print(f"{s}: {len(ts)}")
            for t in ts:
                who, when = t.last_claim()
                print(f"  {t.file}  cap USD {t.cap:g}" + (f"  claimed by {who} {stamp(when)}" if who and s == "doing" else ""))
    elif a.cmd == "heartbeats":
        for t in tasks("doing"):
            print(t.file, json.dumps(heartbeat_status(t), default=str))
    elif a.cmd == "requeue-stale":
        print(requeue_stale(lock.machine()["name"], a.dry_run) or "nothing stale")
    elif a.cmd == "new":
        print(new(a.role, a.slug, a.title, a.cap, open(a.prompt_file, encoding="utf-8").read(), a.timeout))


if __name__ == "__main__":
    main()

#!/usr/bin/env python3
"""The worker (session 59): a machine takes tasks from the queue and runs them with Claude Code, unattended. docs/machines.md.

Energy Research Warehouse (ERW).

    python scripts/worker.py               # loop: sync, requeue stale tasks, claim, run, report, finish; wait when empty
    python scripts/worker.py --once        # at most one task, then stop
    scripts/worker.ps1 / scripts/worker.sh # the same, from PowerShell or bash

Each turn of the loop:
1. Sync (scripts/sync.py): pull main; a data machine also restores any warehouse table missing here from Redivis.
2. Requeue stale tasks: a task in queue/doing/ whose heartbeat expired goes back to queue/todo/ (scripts/taskqueue.py).
3. Take a task: first one this machine was already working (doing/, claimed by this machine: an interrupted run, a
   restart); else claim the first task in todo/ for this machine's role (a commit moving it to doing/, pushed; a lost
   push race moves on to the next). A data machine takes the data lock (warehouse/lock.py) before claiming a data task,
   and holds it until the task's commits are pushed.
4. Run it: Claude Code headless (claude -p) in this checkout, with the repo's permission settings (.claude/settings.json)
   and the task's --permission-mode, its spend cap as --max-budget-usd, and its timeout. A code task works on its branch
   task/NNN-<slug>, pushed every 10 minutes to wip/NNN-<slug> (so a laptop that closes loses nothing: the next machine to
   take the task starts from there); at the end it is pushed to task/NNN-<slug>, where .github/workflows/code-branch.yml
   runs the tests and checks and merges it. A data task works on main under the data lock and is pushed to main.
   A usage limit is not a failure: the worker waits (until the reset time Claude names, else 30 minutes) and resumes the
   same Claude session, as often as it takes; the heartbeat keeps running, and the pause does not count against the
   timeout.
5. Report and finish: the task file moves to queue/done/ with a report (status, machine, times, spend, branch, commits,
   Claude's last message), and a line goes into queue/summary/<day>-<machine>.md, the day's summary; one commit, pushed.

The worker's own log is .erw/worker/<day>.log (not in git). A stub can stand in for Claude (--runner, for the tests and
the end-to-end check): it gets the prompt on stdin and prints Claude's JSON result.
"""

import argparse
import datetime as dt
import json
import os
import re
import shlex
import shutil
import signal
import subprocess
import sys
import threading
import time

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.abspath(os.path.join(HERE, ".."))
sys.path.insert(0, HERE)
sys.path.insert(0, os.path.join(ROOT, "warehouse"))
import lock  # noqa: E402
import taskqueue as tq  # noqa: E402

STATE = os.path.join(ROOT, ".erw", "worker")
RENEW_SECONDS = 600
USAGE_RE = re.compile(r"usage limit|hit your limit|limit reached|out of extra usage|rate[_ ]limit|overloaded", re.I)
LOGF = None


def log(msg):
    line = f"{dt.datetime.now(dt.timezone.utc).strftime('%H:%M:%S')} {msg}"
    print(line, flush=True)
    if LOGF:
        with open(LOGF, "a", encoding="utf-8") as f:
            f.write(line + "\n")


def git(*args, check=True):
    return tq.git(*args, check=check)


def sh(cmd, env=None):
    return subprocess.run(cmd, cwd=ROOT, capture_output=True, text=True, env=env)


def sync(role):
    args = [sys.executable, os.path.join(HERE, "sync.py")] + ([] if role == "data" else ["--check"])
    r = sh(args)
    for ln in (r.stdout or "").splitlines()[:6]:
        log(f"  sync: {ln}")
    if r.returncode != 0:
        log(f"  sync: exit {r.returncode}: {(r.stderr or '').strip()[-300:]}")


def claude_cmd(runner):
    if runner:
        cmd = shlex.split(runner, posix=os.name != "nt")
        if cmd and cmd[0] in ("python", "python3"):  # this interpreter (the .venv), not whichever python Windows finds first
            cmd[0] = sys.executable
        return cmd
    exe = os.environ.get("ERW_CLAUDE") or shutil.which("claude")
    if not exe:
        raise SystemExit("Claude Code is not installed here (npm install -g @anthropic-ai/claude-code), or set ERW_CLAUDE")
    return [exe]


def kill_tree(p):
    if os.name == "nt":
        subprocess.run(["taskkill", "/T", "/F", "/PID", str(p.pid)], capture_output=True)
    else:
        try:
            os.killpg(p.pid, signal.SIGKILL)
        except OSError:
            p.kill()


def parse_result(out):
    """Claude's --output-format json result: the last line of stdout that parses as a JSON object."""
    for ln in reversed((out or "").strip().splitlines()):
        ln = ln.strip()
        if ln.startswith("{"):
            try:
                return json.loads(ln)
            except ValueError:
                continue
    try:
        return json.loads(out)
    except ValueError:
        return {}


def reset_wait(text):
    """Seconds to wait for a usage limit: until the reset Claude names (an epoch after '|', as Claude Code prints it),
    else 30 minutes. At least 5 minutes, at most 6 hours. ERW_USAGE_WAIT_SECONDS overrides it (the tests)."""
    if os.environ.get("ERW_USAGE_WAIT_SECONDS"):
        return float(os.environ["ERW_USAGE_WAIT_SECONDS"])
    m = re.search(r"\|(\d{10})\b", text or "")
    if m:
        return min(max(int(m.group(1)) - time.time() + 60, 300), 6 * 3600)
    return 1800


def preamble(task, machine, lock_held):
    role = (f"This is a code task. You are on the branch {task.branch}, made for it from main. Commit after each unit of work "
            "on this branch. Do not push, do not switch branches and do not merge: the worker pushes the branch when you stop, and "
            ".github/workflows/code-branch.yml merges it into main when tests/ and the site's checks pass. Write no warehouse data "
            "(warehouse/output, Supabase, Redivis): a code machine holds no data lock and every data writer refuses without it.")
    if task.role == "data":
        role = ("This is a data task. You are on main and this machine holds the data lock (ERW_LOCK_TOKEN is set; "
                "warehouse/lock.py), so the data writers will run. Commit after each unit of work on main. Do not push: the "
                "worker merges origin/main and pushes when you stop, then releases the lock." if lock_held else "")
    return (f"You are running unattended as the ERW queue worker on the machine {machine['name']} (role {machine['role']}), "
            f"task {task.file}. Nobody will answer questions: when a decision has to be made, make a reasonable one, write it "
            f"down, and continue. Read CLAUDE.md first and follow it. {role} Your spend cap for this task is USD {task.cap:g}. "
            "End with a short report as your final message: what you did, what you decided, what failed, and anything Samuel "
            "must do (exact steps). The task follows.\n\n---\n\n")


class Beat:
    """Renews the task's heartbeat (and the data lock) every 10 minutes; for a code task, pushes the branch to wip/."""

    def __init__(self, task, hb_token, data_token, wip):
        self.task, self.hb, self.data, self.wip = task, hb_token, data_token, wip
        self.lost = False
        self.stop = threading.Event()
        self.t = threading.Thread(target=self.loop, daemon=True)
        self.t.start()

    def loop(self):
        while not self.stop.wait(RENEW_SECONDS):
            try:
                if not tq.heartbeat_renew(self.task, self.hb):
                    self.lost = True
                    log(f"  WARNING: the heartbeat of {self.task.file} had expired; another worker may requeue it")
                if self.data and not lock.renew(self.data, minutes=120):
                    log("  WARNING: the data lock could not be renewed")
            except Exception as exc:
                log(f"  WARNING: renewing: {type(exc).__name__}: {str(exc)[:150]}")
            if self.wip:
                push_wip(self.task)

    def end(self):
        self.stop.set()


def push_wip(task):
    """Push the task's branch to wip/NNN-<slug> (never forced: a rejection is skipped)."""
    r = sh(["git", "push", "-q", "origin", f"refs/heads/{task.branch}:refs/heads/wip/{task.id}-{task.slug}"])
    return r.returncode == 0


def start_branch(task):
    """Switch to the task's branch: this machine's own (an interrupted run), else origin's wip/ copy, else new from main."""
    git("fetch", "-q", "origin")
    wip = f"origin/wip/{task.id}-{task.slug}"
    if git("rev-parse", "--verify", "-q", f"refs/heads/{task.branch}", check=False).returncode == 0:
        git("switch", "-q", task.branch)
        how = "this machine's branch"
    elif git("rev-parse", "--verify", "-q", wip, check=False).returncode == 0:
        git("switch", "-q", "-c", task.branch, wip)
        how = wip
    else:
        git("switch", "-q", "-c", task.branch, "origin/main")
        return "new from origin/main"
    if git("merge", "--no-edit", "-q", "origin/main", check=False).returncode != 0:
        git("merge", "--abort", check=False)
        return how + " (origin/main not merged: conflicts; left to the checks)"
    return how + ", origin/main merged"


def commit_leftovers(task):
    """Commit tracked changes the run left uncommitted (untracked files are reported, never added)."""
    st = git("status", "--porcelain").stdout.splitlines()
    tracked = [ln for ln in st if not ln.startswith("??")]
    untracked = [ln[3:] for ln in st if ln.startswith("??")]
    if tracked:
        git("add", "-u")
        git("commit", "-q", "-m", f"queue task {task.id}: changes the run left uncommitted\n\nCommitted by scripts/worker.py.")
    return len(tracked), untracked


def run_claude(task, cmd0, prompt, env, beat, spent0=0.0):
    """Run Claude until it ends, pausing and resuming on a usage limit. Returns (status, result json, spent, pauses)."""
    spent, pauses, session, res = spent0, 0, None, {}
    deadline = time.time() + task.timeout * 60
    while True:
        left = task.cap - spent
        if left <= 0.01:
            return "capped", res, spent, pauses
        cmd = cmd0 + ["-p", "--output-format", "json", "--permission-mode", task.mode, "--max-budget-usd", f"{left:.2f}"]
        text = prompt
        if session:
            cmd += ["--resume", session]
            text = "Continue the task from where you stopped (a usage limit paused you). Finish it, then write the report as your final message."
        p = subprocess.Popen(cmd, cwd=ROOT, env=env, stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.PIPE,
                             text=True, encoding="utf-8", errors="replace", start_new_session=(os.name != "nt"))
        try:
            out, err = p.communicate(text, timeout=max(deadline - time.time(), 60))
        except subprocess.TimeoutExpired:
            kill_tree(p)
            out, err = p.communicate()
            res = parse_result(out)
            spent += float(res.get("total_cost_usd") or 0)
            return "timeout", res, spent, pauses
        res = parse_result(out)
        spent += float(res.get("total_cost_usd") or 0)
        session = res.get("session_id") or session
        blob = " ".join(str(x) for x in (res.get("result"), res.get("subtype"), err[-2000:] if err else "", out[-2000:] if not res else ""))
        failed = p.returncode != 0 or res.get("is_error") or not res
        if failed and USAGE_RE.search(blob):
            wait = reset_wait(blob)
            pauses += 1
            deadline += wait  # the pause does not count against the timeout
            log(f"  usage limit (pause {pauses}): waiting {wait / 60:.0f} minutes, then resuming the session")
            time.sleep(wait)
            continue
        if "budget" in str(res.get("subtype", "")):
            return "capped", res, spent, pauses
        if failed:
            res.setdefault("result", (err or out or "")[-3000:])
            return "failed", res, spent, pauses
        return "done", res, spent, pauses


def run_task(task, machine, runner, data_token=None):
    t0 = tq.now()
    hb_file = os.path.join(STATE, f"heartbeat-{task.id}.json")
    old = json.load(open(hb_file, encoding="utf-8")).get("token") if os.path.exists(hb_file) else None
    hb = tq.heartbeat_take(task, machine["name"], old)
    if not hb:
        log(f"  {task.file}: its heartbeat is held by another worker; skipped")
        return None
    json.dump({"token": hb, "task": task.file}, open(hb_file, "w", encoding="utf-8"))
    how = "main"
    base = git("rev-parse", "HEAD").stdout.strip()
    if task.role == "code":
        how = start_branch(task)
        base = git("merge-base", "HEAD", "origin/main").stdout.strip()
    log(f"  running {task.file} on {task.branch} ({how}); cap USD {task.cap:g}, timeout {task.timeout} minutes")
    env = {**os.environ, "ERW_QUEUE_TASK": task.file}
    if data_token:
        env["ERW_LOCK_TOKEN"] = data_token
    else:
        env.pop("ERW_LOCK_TOKEN", None)
    beat = Beat(task, hb, data_token, wip=(task.role == "code"))
    try:
        status, res, spent, pauses = run_claude(task, claude_cmd(runner), preamble(task, machine, bool(data_token)) + task.prompt, env, beat)
    except Exception as exc:
        status, res, spent, pauses = "failed", {"result": f"the worker could not run Claude: {type(exc).__name__}: {exc}"}, 0.0, 0
    finally:
        beat.end()
    left_tracked, untracked = commit_leftovers(task)
    commits = git("log", "--format=%h %s", f"{base}..HEAD").stdout.strip().splitlines()
    pushed = ""
    if task.role == "code":
        if commits:
            target = task.branch if status == "done" else f"wip/{task.id}-{task.slug}"
            r = sh(["git", "push", "-q", "origin", f"refs/heads/{task.branch}:refs/heads/{target}"])
            pushed = f"pushed to {target}" if r.returncode == 0 else f"push to {target} failed: {r.stderr.strip()[:200]}"
            if status == "done":
                pushed += " (code-branch.yml runs the checks and merges it into main when they pass)"
        else:
            pushed = "no commits"
        git("switch", "-q", "main")
    else:
        pushed = "pushed to main" if (not commits or tq.push_persist()) else "push to main failed; committed here"
    if beat.lost and not tq.heartbeat_take(task, machine["name"], hb):
        log(f"  {task.file}: another worker took it over while this run was paused; its work is on wip/ or main, not finished here")
        return {"status": "lost"}
    took = (tq.now() - t0).total_seconds() / 60
    final = str(res.get("result") or "").strip()
    report = "\n".join([
        "## Report",
        "",
        f"- Status: {status}",
        f"- Machine: {machine['name']} (role {machine['role']})",
        f"- Started {tq.stamp(t0)}, ended {tq.stamp()}: {took:.0f} minutes" + (f", {pauses} pauses for a usage limit" if pauses else ""),
        f"- Spend: USD {spent:.2f} of the cap USD {task.cap:g}",
        f"- Branch: {task.branch}; {pushed}",
        f"- Commits ({len(commits)}):" + ("".join(f"\n  - {c}" for c in commits[:40]) if commits else " none"),
    ] + ([f"- Tracked changes left uncommitted by the run, committed by the worker: {left_tracked} files"] if left_tracked else [])
      + ([f"- Untracked files left in the checkout (not committed): {', '.join(untracked[:10])}"] if untracked else []) + [
        "",
        "### Claude's final message",
        "",
        final[:8000] if final else "(none)",
    ])
    summary = f"{tq.stamp()[11:16]} {task.file}: {status}, {took:.0f} minutes, USD {spent:.2f}, {len(commits)} commits, {pushed}"
    try:
        tq.finish(task, status, report, machine["name"], summary)
        log(f"  finished {task.file}: {status}")
    except Exception as exc:
        log(f"  FAILED to finish {task.file}: {exc}")
    tq.heartbeat_release(task, hb)
    if os.path.exists(hb_file):
        os.remove(hb_file)
    return {"status": status, "spent": spent}


def turn(machine, runner, log_sync=True):
    """One turn: sync, requeue stale, take and run one task. Returns the result, or None if there was nothing to do."""
    role = machine["role"]
    if log_sync:
        sync(role)
    try:
        tq.requeue_stale(machine["name"], log=lambda m: log("  " + m), skip_holder=machine["name"])
    except Exception as exc:
        log(f"  requeue-stale: {exc}")
    mine = [t for t in tq.tasks("doing") if t.role == role and t.last_claim()[0] == machine["name"]]
    data_token = None
    if role == "data" and (mine or any(t.role == "data" for t in tq.tasks("todo"))):
        try:
            data_token = lock.acquire("queue worker", minutes=120, wait=0)
        except SystemExit as exc:
            log(f"  data tasks wait: {exc}")
            return None
    try:
        task = mine[0] if mine else tq.claim(role, machine["name"], log=lambda m: log("  " + m))
        if task is None:
            return None
        if mine:
            log(f"  resuming {task.file} (claimed by this machine before)")
        return run_task(task, machine, runner, data_token) or {"status": "skipped"}
    finally:
        if data_token:
            lock.release(data_token)


def main(argv=None):
    global LOGF
    ap = argparse.ArgumentParser(description="ERW queue worker (session 59)")
    ap.add_argument("--once", action="store_true", help="at most one task, then stop")
    ap.add_argument("--max-tasks", type=int, default=0, help="stop after this many tasks (0: no limit)")
    ap.add_argument("--idle-minutes", type=int, default=15, help="wait between turns when the queue is empty")
    ap.add_argument("--runner", help="a command standing in for claude (tests): gets the prompt on stdin, prints Claude's JSON")
    ap.add_argument("--no-sync", action="store_true", help="skip scripts/sync.py (the queue still pulls main)")
    a = ap.parse_args(argv)
    os.makedirs(STATE, exist_ok=True)
    LOGF = os.path.join(STATE, dt.datetime.now(dt.timezone.utc).strftime("%Y-%m-%d") + ".log")
    machine = lock.machine()
    log(f"worker on {machine['name']} (role {machine['role']}), {ROOT}")
    if git("rev-parse", "--abbrev-ref", "HEAD").stdout.strip() != "main":
        git("switch", "-q", "main")
    n = 0
    while True:
        try:
            r = turn(machine, a.runner, log_sync=not a.no_sync)
        except Exception as exc:
            log(f"  turn failed: {type(exc).__name__}: {str(exc)[:300]}")
            r = None
            if git("rev-parse", "--abbrev-ref", "HEAD", check=False).stdout.strip() != "main":
                git("switch", "-q", "main", check=False)
        if r is not None:
            n += 1
        if a.once or (a.max_tasks and n >= a.max_tasks):
            break
        if r is None:
            log(f"  nothing to do; next turn in {a.idle_minutes} minutes")
            time.sleep(a.idle_minutes * 60)
    log(f"worker stopped: {n} tasks")


if __name__ == "__main__":
    main()

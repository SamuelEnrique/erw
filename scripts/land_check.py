#!/usr/bin/env python3
"""The landing gate in one script, without the push (session 579).

Energy Research Warehouse (ERW). docs/machines.md, "The landing gate". Every landing since 19 October 2026 ran the same
gate by hand, and two let a step slip (session 64 piped the coverage build and loaded on stale coverage; session 139
chained the before snapshot behind a check and pushed without it). This runs the gate for one commit, each step as its
own process whose exit code is read (never piped), and writes one line a step:

    python scripts/land_check.py                       the current HEAD
    python scripts/land_check.py --ref wip/579-s       a branch (or any commit)
        --task 579-landing    the task/ branch named in the printed push command (default: the branch's own name,
                              wip/ replaced by task/)
        --port 3700           the port the build is served on for the page checks
        --build-min 30        the build is stopped after this many minutes
        --lock-as WHO         the build lock's holder name (default land-<sha8>); a lock already held by WHO is used
                              and left held, so a session holding it under its own name passes that name
        --keep-worktree       leave the clean worktree in place at the end (default: removed; it holds no branch)

The steps, in order:

    freeze          python scripts/freeze.py status (CLAUDE.md rule 9). Frozen (1) or unreadable (2) is a fail that does
                    not stop the other steps: their result is still worth having, but no push command is printed
    main_merged     git fetch origin main; git merge-base --is-ancestor origin/main <sha> (merge origin/main first)
    task_branches   git ls-remote --heads origin task/*; for each not on main, git merge-tree --write-tree with the
                    commit (exit 1 is a conflict). Branches in flight are named in the line
    db_probe        python scripts/db_probe.py (exit 1: no build now; the gate stops)
    build_lock      python scripts/buildlock.py acquire <who> (it waits); released at the end whatever happened
    worktree        git worktree add --detach <main>-land-<sha8> <sha>: a clean copy, no warehouse/output, no .env
    suite           python -m unittest discover -s tests in the clean copy, ERW_LOCK_EXEMPT=1, with every key
                    (Supabase, Anthropic, tokens, secrets) taken out of its environment, as on GitHub's runner
    npm_ci          npm ci in the clean copy's site/, after site/.env.local is copied in (never printed)
    build           npm run build, stopped after --build-min minutes; a log holding "statement timeout" is built once
                    more (a build can bake a database timeout into a page), and a second such log fails
    serve           next start on --port (refused if the port is taken), then warm-live.mjs (its exit is noted only)
    check_values    node scripts/check-values.mjs; exit 3 (pages not read) is resumed with CHECK_VALUES_RESUME=1 until
                    0 or 1, at most three tries. Exit 1 whose only failures are the floors of the ten pages the license
                    holds of 21 October empty (session 408's list, session 415's report), each page showing "license
                    needed" when read with the internal cookie, is a pass, said so
    check_routes, check_cross_checks, check_csp    node scripts/<name>.mjs <base>
    stop            the server's process tree is stopped by its PID, then whatever still listens on the port, by PID

The first failing step stops the gate (except freeze); the steps after it are written as "skip". The lines go to
runs/land_check/<sha>.txt (appended, one run after another), each step's output to runs/land_check/<sha>/<step>.out.
At the end, when every step passed, the script PRINTS the commands that remain, each to be run as its own command
with its exit code read: the freeze status again, the snapshot before, the push to task/, the snapshot after and the
comparison. It never runs them: it never pushes, never takes a snapshot and never deletes a branch.

Exit codes: 0 every step passed; 1 a step failed (or the site is frozen); 2 bad input (the ref is not a commit).
Standard library only.
"""

import argparse
import datetime as dt
import http.client
import os
import re
import shutil
import socket
import subprocess
import sys
import time
import urllib.error
import urllib.parse
import urllib.request

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.abspath(os.path.join(HERE, ".."))

STEPS = ["freeze", "main_merged", "task_branches", "db_probe", "build_lock", "worktree", "suite", "npm_ci", "build",
         "serve", "check_values", "check_routes", "check_cross_checks", "check_csp", "stop"]
CHECK_VALUES_TRIES = 3
SUITE_MIN = 60
NPM_CI_MIN = 20
CHECK_MIN = 45
# Session 408's list: the ten pages whose figures the license holds of 21 October replace with "license needed", so
# their floors in site/scripts/check-values-floor.json fail on every build until Samuel rules on lowering them
# (session 415's report, item 2; session 531's report). A pass for this gate only when each shows "license needed".
HELD_FLOOR_PAGES = ("/deals", "/map", "/events", "/events/uri-2021", "/events/covid-2020", "/events/caiso-heat-2020",
                    "/events/caiso-heat-2022", "/events/east-heat-2025", "/learn/bill", "/research/card/gas_sets_price")
# names whose values never reach the suite: GitHub's test step has no secret in its environment
SECRET_NAME = re.compile(r"SUPABASE|ANTHROPIC|OPENAI|API_KEY|TOKEN|SECRET|PASSWORD|RESEND|REDIVIS|DB_URL", re.I)


def utc_now():
    return dt.datetime.now(dt.timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


class Ops:
    """Everything that touches the machine. The tests replace each method; the gate itself only decides."""

    def run(self, step, argv, cwd, log, env=None, timeout=None):
        """Run argv as its own process, its output (both streams) written to log. Its exit code, or None when it was
        stopped at the timeout (its whole process tree)."""
        os.makedirs(os.path.dirname(log), exist_ok=True)
        with open(log, "ab") as f:
            f.write(f"\n$ {' '.join(argv)}    (cwd {cwd}, {utc_now()})\n".encode("utf-8"))
            f.flush()
            kw = {"creationflags": subprocess.CREATE_NEW_PROCESS_GROUP} if os.name == "nt" else {"start_new_session": True}
            p = subprocess.Popen(argv, cwd=cwd, env=env, stdout=f, stderr=subprocess.STDOUT, stdin=subprocess.DEVNULL, **kw)
            try:
                return p.wait(timeout=timeout)
            except subprocess.TimeoutExpired:
                self.kill_tree(p.pid)
                try:
                    p.wait(timeout=60)
                except subprocess.TimeoutExpired:
                    pass
                f.write(f"\n[land_check: stopped after {timeout} s]\n".encode("utf-8"))
                return None

    def kill_tree(self, pid):
        if os.name == "nt":
            subprocess.run(["taskkill", "/PID", str(pid), "/T", "/F"], capture_output=True, stdin=subprocess.DEVNULL)
        else:
            import signal
            try:
                os.killpg(pid, signal.SIGKILL)
            except OSError:
                pass

    def output(self, argv, cwd):
        """A short git command's (exit code, stdout)."""
        r = subprocess.run(argv, cwd=cwd, capture_output=True, text=True, stdin=subprocess.DEVNULL, timeout=300)
        return r.returncode, r.stdout

    def read(self, path):
        try:
            with open(path, encoding="utf-8", errors="replace") as f:
                return f.read()
        except OSError:
            return ""

    def exists(self, path):
        return os.path.exists(path)

    def copy(self, src, dst):
        shutil.copyfile(src, dst)

    def port_busy(self, port):
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            s.settimeout(2)
            return s.connect_ex(("127.0.0.1", port)) == 0

    def start_server(self, site_dir, port, log):
        os.makedirs(os.path.dirname(log), exist_ok=True)
        f = open(log, "ab")
        kw = {"creationflags": subprocess.CREATE_NEW_PROCESS_GROUP} if os.name == "nt" else {"start_new_session": True}
        node = shutil.which("node") or "node"
        p = subprocess.Popen([node, os.path.join("node_modules", "next", "dist", "bin", "next"), "start", "-p", str(port)],
                             cwd=site_dir, stdout=f, stderr=subprocess.STDOUT, stdin=subprocess.DEVNULL, **kw)
        return (p, f)

    def wait_ready(self, base, seconds=180):
        t0 = time.time()
        while time.time() - t0 < seconds:
            try:
                urllib.request.urlopen(base + "/", timeout=30).read(1)
                return True
            except urllib.error.HTTPError:
                return True   # it answers; what it answers is the checks' business
            except (urllib.error.URLError, OSError):
                time.sleep(3)
        return False

    def listeners(self, port):
        """PIDs listening on the port (Windows: Get-NetTCPConnection; elsewhere none known)."""
        if os.name != "nt":
            return []
        r = subprocess.run(["powershell", "-NoProfile", "-Command",
                            f"Get-NetTCPConnection -LocalPort {int(port)} -State Listen -ErrorAction SilentlyContinue "
                            "| Select-Object -ExpandProperty OwningProcess"],
                           capture_output=True, text=True, stdin=subprocess.DEVNULL, timeout=60)
        return sorted({int(x) for x in r.stdout.split() if x.strip().isdigit() and int(x) > 0})

    def stop_server(self, handle, port):
        """Stop the server by its PID (its tree), then any process still listening on the port, by PID. A note."""
        p, f = handle
        self.kill_tree(p.pid)
        try:
            p.wait(timeout=30)
        except subprocess.TimeoutExpired:
            pass
        f.close()
        left = self.listeners(port)
        for pid in left:
            self.kill_tree(pid)
        still = self.listeners(port)
        return f"server {p.pid} stopped" + (f"; {left} still listened on {port} and were stopped" if left else "") + \
            (f"; {still} STILL listen on {port}" if still else "")

    def held_pages(self, base, token, pages):
        """{page: shows "license needed"}, each page read with the internal cookie (the form's door, as check-values
        opens it), so a page in review is read as it is and not as the in-review page."""
        u = urllib.parse.urlsplit(base)
        cookie = ""
        if token:
            c = http.client.HTTPConnection(u.hostname, u.port, timeout=60)
            body = urllib.parse.urlencode({"token": token})
            c.request("POST", "/internal/unlock", body=body, headers={
                "Content-Type": "application/x-www-form-urlencoded", "Origin": f"{u.scheme}://{u.netloc}",
                "User-Agent": "erw-check (land_check)"})
            r = c.getresponse()
            r.read()
            cookie = "; ".join(v.split(";")[0] for v in (r.headers.get_all("Set-Cookie") or []))
            c.close()
        out = {}
        for page in pages:
            try:
                req = urllib.request.Request(base + page, headers={"Cookie": cookie} if cookie else {})
                html = urllib.request.urlopen(req, timeout=120).read().decode("utf-8", "replace")
                out[page] = 'data-in-review="1"' not in html and "license needed" in html.lower()
            except (urllib.error.URLError, OSError):
                out[page] = False
        return out


def env_value(path, name, ops):
    """One NAME=value line of an env file, never printed."""
    for line in ops.read(path).splitlines():
        m = re.match(r"^([A-Z_]+)=(.*)$", line)
        if m and m.group(1) == name:
            return m.group(2).strip().strip('"')
    return None


def suite_env(environ):
    """The suite's environment: the caller's with every key taken out, ERW_LOCK_EXEMPT=1."""
    env = {k: v for k, v in environ.items() if not SECRET_NAME.search(k)}
    env["ERW_LOCK_EXEMPT"] = "1"
    return env


def held_floor_failures(text):
    """For a check-values log: the held pages whose floor failed, when the floors of session 408's held pages are its
    only failures; None when anything else failed or a page was not read."""
    pages = []
    for line in text.splitlines():
        s = line.strip()
        if s.startswith("check-values FAILED") or s.startswith("not read |"):
            return None
        if s.startswith("FAIL |"):
            parts = [x.strip() for x in s.split("|")]
            if len(parts) < 3 or parts[2] != "the floor" or parts[1] not in HELD_FLOOR_PAGES:
                return None
            pages.append(parts[1])
    return pages or None


class Gate:
    def __init__(self, sha, args, ops, root=ROOT, main=None, out=print):
        self.sha, self.a, self.ops, self.root, self.out = sha, args, ops, root, out
        self.main = main or root
        self.short = sha[:8]
        self.dir = os.path.join(root, "runs", "land_check", sha)
        self.record = os.path.join(root, "runs", "land_check", f"{sha}.txt")
        self.wt = args.worktree or os.path.join(os.path.dirname(self.main), f"{os.path.basename(self.main)}-land-{self.short}")
        self.site = os.path.join(self.wt, "site")
        self.base = f"http://localhost:{args.port}"
        self.py = sys.executable
        self.who = args.lock_as or f"land-{self.short}"
        self.results = []          # (step, state, exit, note)
        self.lock_ours = False
        self.made_worktree = False
        self.server = None

    def log(self, step):
        return os.path.join(self.dir, f"{step}.out")

    def line(self, step, state, code, secs, note=""):
        os.makedirs(os.path.dirname(self.record), exist_ok=True)
        text = f"{utc_now()} | {step} | {state} | exit {'-' if code is None else code} | {secs:.0f} s | {note}".rstrip(" |")
        with open(self.record, "a", encoding="utf-8") as f:
            f.write(text + "\n")
        self.out(text)
        self.results.append((step, state, code, note))

    def run(self, step, argv, cwd, env=None, timeout=None):
        return self.ops.run(step, argv, cwd, self.log(step), env=env, timeout=timeout)

    def beat(self):
        self.run("duty_beat", [self.py, os.path.join(self.root, "scripts", "duty.py"), "beat"], self.root)

    # the steps: each returns (state, exit, note); state is "pass" or "fail"

    def s_freeze(self):
        c = self.run("freeze", [self.py, os.path.join(self.root, "scripts", "freeze.py"), "status"], self.root)
        note = {0: "no freeze", 1: "FROZEN: push to wip/ and write To finish", 2: "the freeze file cannot be read: frozen"}
        return ("pass" if c == 0 else "fail"), c, note.get(c, "unexpected exit")

    def s_main_merged(self):
        c = self.run("main_merged", ["git", "fetch", "origin", "main"], self.root, timeout=300)
        if c != 0:
            return "fail", c, "git fetch origin main failed"
        c = self.run("main_merged", ["git", "merge-base", "--is-ancestor", "origin/main", self.sha], self.root)
        return ("pass", c, "origin/main is in the commit") if c == 0 else ("fail", c, "origin/main is not in the commit: merge it first")

    def s_task_branches(self):
        c, text = self.ops.output(["git", "ls-remote", "--heads", "origin", "task/*"], self.root)
        if c != 0:
            return "fail", c, "git ls-remote failed"
        flight, conflict = [], []
        for ln in text.splitlines():
            parts = ln.split()
            if len(parts) != 2:
                continue
            bsha, ref = parts
            name = ref.replace("refs/heads/", "")
            if self.run("task_branches", ["git", "fetch", "origin", name], self.root, timeout=300) != 0:
                return "fail", 1, f"git fetch origin {name} failed"
            if self.run("task_branches", ["git", "merge-base", "--is-ancestor", bsha, "origin/main"], self.root) == 0:
                continue   # already on main
            flight.append(name)
            if self.run("task_branches", ["git", "merge-tree", "--write-tree", bsha, self.sha], self.root) != 0:
                conflict.append(name)
        if conflict:
            return "fail", 1, f"conflicts with {', '.join(conflict)} in flight: wait for it to merge, merge main, run again"
        return "pass", 0, (f"in flight, merging cleanly: {', '.join(flight)}" if flight else "none in flight")

    def s_db_probe(self):
        c = self.run("db_probe", [self.py, os.path.join(self.root, "scripts", "db_probe.py")], self.root, timeout=300)
        return ("pass", c, "") if c == 0 else ("fail", c, "the database is slow or failed: no build now")

    def s_build_lock(self):
        lock = os.path.join(self.root, "scripts", "buildlock.py")
        c, text = self.ops.output([self.py, lock, "status"], self.root)
        if c == 1 and f"held by {self.who} " in text:
            return "pass", 0, f"already held by {self.who}: used, and left held"
        c = self.run("build_lock", [self.py, lock, "acquire", self.who], self.root)
        if c == 0:
            self.lock_ours = True
            return "pass", c, f"held by {self.who}"
        return "fail", c, "the build lock could not be taken"

    def s_worktree(self):
        if self.ops.exists(self.wt):
            return "fail", 1, f"{self.wt} exists: remove it (git worktree remove --force) or name another with --worktree"
        c = self.run("worktree", ["git", "worktree", "add", "--detach", self.wt, self.sha], self.root, timeout=900)
        if c == 0:
            self.made_worktree = True
            return "pass", c, self.wt
        return "fail", c, "git worktree add failed"

    def s_suite(self):
        self.beat()
        c = self.run("suite", [self.py, "-m", "unittest", "discover", "-s", "tests"], self.wt,
                     env=suite_env(os.environ), timeout=SUITE_MIN * 60)
        if c is None:
            return "fail", None, f"stopped after {SUITE_MIN} minutes"
        tail = [x for x in self.ops.read(self.log("suite")).splitlines() if x.startswith(("Ran ", "OK", "FAILED"))]
        return ("pass" if c == 0 else "fail"), c, "; ".join(tail[-2:])

    def s_npm_ci(self):
        src = os.path.join(self.main, "site", ".env.local")
        if not self.ops.exists(src):
            return "fail", 1, f"{src} is missing: the build would have no data"
        self.ops.copy(src, os.path.join(self.site, ".env.local"))
        c = self.run("npm_ci", [shutil.which("npm") or "npm", "ci"], self.site, timeout=NPM_CI_MIN * 60)
        return ("pass" if c == 0 else "fail"), c, ("" if c == 0 else f"npm ci failed{' (stopped)' if c is None else ''}")

    def s_build(self):
        notes = []
        for attempt in (1, 2):
            self.beat()
            log = self.log("build")
            before = len(self.ops.read(log))
            c = self.run("build", [shutil.which("npm") or "npm", "run", "build"], self.site, timeout=self.a.build_min * 60)
            if c is None:
                return "fail", None, f"stopped after {self.a.build_min} minutes"
            if c != 0:
                return "fail", c, "; ".join(notes + ["the build failed"])
            if "statement timeout" not in self.ops.read(log)[before:]:
                return "pass", c, "; ".join(notes)
            notes.append(f"build {attempt}'s log holds \"statement timeout\"")
        return "fail", 1, "; ".join(notes) + ": not taken (a page may hold a database timeout)"

    def s_serve(self):
        if self.ops.port_busy(self.a.port):
            return "fail", 1, f"port {self.a.port} is taken: name another with --port"
        self.server = self.ops.start_server(self.site, self.a.port, self.log("serve"))
        if not self.ops.wait_ready(self.base):
            return "fail", 1, f"{self.base} did not answer"
        w = self.run("serve", ["node", "scripts/warm-live.mjs", self.base], self.site, timeout=CHECK_MIN * 60)
        return "pass", 0, f"{self.base}; warm-live exit {'-' if w is None else w}"

    def s_check_values(self):
        log = self.log("check_values")
        state = os.path.join(self.dir, "check-values-state.json")
        code, tries = None, 0
        for tries in range(1, CHECK_VALUES_TRIES + 1):
            env = dict(os.environ, CHECK_VALUES_STATE=state)
            env.pop("CHECK_VALUES_PAGES", None)   # the gate of a landing is the full run
            if tries > 1:
                env["CHECK_VALUES_RESUME"] = "1"
            before = len(self.ops.read(log))
            code = self.run("check_values", ["node", "scripts/check-values.mjs", self.base], self.site, env=env,
                            timeout=CHECK_MIN * 60)
            if code != 3:
                break
        note = f"{tries} {'try' if tries == 1 else 'tries'}"
        if code == 0:
            return "pass", 0, note
        if code == 3:
            return "fail", 3, note + ": pages still not read"
        if code == 1:
            held = held_floor_failures(self.ops.read(log)[before:])
            if held:
                token = env_value(os.path.join(self.site, ".env.local"), "INTERNAL_COSTS_TOKEN", self.ops)
                shown = self.ops.held_pages(self.base, token, held)
                missing = [p for p in held if not shown.get(p)]
                if not missing:
                    return "pass", 1, (note + f": only the license holds' floors failed ({len(held)}: "
                                       f"{', '.join(held)}), each showing \"license needed\" (session 408's list)")
                return "fail", 1, note + f": held floors, but not showing \"license needed\": {', '.join(missing)}"
        return "fail", code, note

    def node_check(self, step, script, extra=()):
        c = self.run(step, ["node", f"scripts/{script}", self.base, *extra], self.site, timeout=CHECK_MIN * 60)
        return ("pass" if c == 0 else "fail"), c, ("" if c is not None else "stopped")

    def s_check_routes(self):
        return self.node_check("check_routes", "check-routes.mjs")

    def s_check_cross_checks(self):
        return self.node_check("check_cross_checks", "check-cross-checks.mjs")

    def s_check_csp(self):
        return self.node_check("check_csp", "check-csp.mjs")

    def s_stop(self):
        if not self.server:
            return "pass", 0, "no server was started"
        note = self.ops.stop_server(self.server, self.a.port)
        self.server = None
        return ("fail" if "STILL" in note else "pass"), 0, note

    def cleanup(self):
        if self.server:
            self.line("stop", *self.timed(self.s_stop))
        if self.made_worktree and not self.a.keep_worktree:
            c = self.run("cleanup", ["git", "worktree", "remove", "--force", self.wt], self.root, timeout=1800)
            self.line("cleanup", "pass" if c == 0 else "fail", c, 0, f"worktree {self.wt} removed" if c == 0 else
                      f"remove it by hand: git worktree remove --force {self.wt}")
        if self.lock_ours:
            c = self.run("build_lock", [self.py, os.path.join(self.root, "scripts", "buildlock.py"), "release", self.who], self.root)
            self.line("release", "pass" if c == 0 else "fail", c, 0, f"build lock released by {self.who}")

    def timed(self, fn):
        t0 = time.time()
        state, code, note = fn()
        return state, code, time.time() - t0, note

    def go(self):
        os.makedirs(os.path.dirname(self.record), exist_ok=True)
        with open(self.record, "a", encoding="utf-8") as f:
            f.write(f"# {utc_now()} land_check of {self.sha} ({self.a.ref}), logs in runs/land_check/{self.sha}/\n")
        stopped = None
        try:
            for step in STEPS:
                if stopped:
                    self.line(step, "skip", None, 0, f"not run: {stopped} failed")
                    continue
                state, code, secs, note = self.timed(getattr(self, f"s_{step}"))
                self.line(step, state, code, secs, note)
                if state == "fail" and step != "freeze":
                    stopped = step
        finally:
            self.cleanup()
        failed = [s for s, st, _, _ in self.results if st == "fail"]
        return 1 if failed else 0, failed

    def finish(self, failed):
        if failed:
            self.out(f"\nNOT READY to land {self.sha}: {', '.join(failed)} failed (runs/land_check/{self.sha}.txt). "
                     "No push command is printed.")
            if failed == ["freeze"]:
                self.out("Every other step passed: push to a wip/ branch and write the push under To finish.")
            return
        task = self.a.task or task_name(self.a.ref, self.ops, self.root)
        b, af = f"before-{self.short}", f"after-{self.short}"
        py = os.path.relpath(self.py, self.root) if self.py.startswith(self.root) else self.py
        self.out(f"\nEvery step passed for {self.sha}. This script does not push. What remains, each as its own command, "
                 "its exit code read before the next (never chained with && or ;):")
        for cmd in [f"{py} scripts/freeze.py status",
                    'git ls-remote --heads origin "task/*"     (again: anything new in flight since the gate is trial-merged first)',
                    f"node site/scripts/snapshot-live.mjs take {b}",
                    f"git push origin {self.sha}:refs/heads/task/{task}",
                    "(wait for the merge on main, then for production to serve the new build: a mark of the commit on "
                    "the site, not GitHub's deployment record)",
                    f"node site/scripts/snapshot-live.mjs take {af}",
                    f"node site/scripts/snapshot-live.mjs compare {b} {af}     (every difference listed in the report, "
                    "each marked expected or not)"]:
            self.out("  " + cmd)


def task_name(ref, ops, root):
    """The task/ branch name: --ref's branch (or HEAD's) with its wip/ or task/ prefix taken off."""
    name = ref
    if ref == "HEAD":
        c, text = ops.output(["git", "rev-parse", "--abbrev-ref", "HEAD"], root)
        name = text.strip() if c == 0 else "HEAD"
    name = re.sub(r"^(origin/)?(wip|task)/", "", name)
    return name if name and name != "HEAD" else "<name>"


def main_checkout(root=ROOT):
    try:
        r = subprocess.run(["git", "rev-parse", "--path-format=absolute", "--git-common-dir"], cwd=root,
                           capture_output=True, text=True, timeout=20, stdin=subprocess.DEVNULL)
        if r.returncode == 0 and r.stdout.strip():
            return os.path.abspath(os.path.join(r.stdout.strip(), ".."))
    except (OSError, subprocess.SubprocessError):
        pass
    return root


def parse(argv=None):
    ap = argparse.ArgumentParser(description="The landing gate in one script, without the push (session 579)")
    ap.add_argument("--ref", default="HEAD")
    ap.add_argument("--task", default=None)
    ap.add_argument("--port", type=int, default=3700)
    ap.add_argument("--build-min", type=float, default=30)
    ap.add_argument("--lock-as", default=None)
    ap.add_argument("--worktree", default=None)
    ap.add_argument("--keep-worktree", action="store_true")
    return ap.parse_args(argv)


def main(argv=None, ops=None, root=ROOT, main=None, out=print):
    a = parse(argv)
    ops = ops or Ops()
    if a.lock_as and any(ch.isspace() for ch in a.lock_as):
        out("land_check: --lock-as takes a name without spaces")
        return 2
    c, text = ops.output(["git", "rev-parse", "--verify", f"{a.ref}^{{commit}}"], root)
    sha = text.strip()
    if c != 0 or not re.fullmatch(r"[0-9a-f]{40}", sha):
        out(f"land_check: {a.ref} is not a commit")
        return 2
    g = Gate(sha, a, ops, root=root, main=main or main_checkout(root), out=out)
    code, failed = g.go()
    g.finish(failed)
    return code


if __name__ == "__main__":
    sys.exit(main())

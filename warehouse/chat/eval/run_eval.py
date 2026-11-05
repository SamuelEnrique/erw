#!/usr/bin/env python3
"""Session 1128 (chain 076): an evaluation of Ask as one command.

Energy Research Warehouse (ERW). Chain 075 ran an evaluation by hand in nine steps (sessions 1113 and 1114's reports,
"To finish"); this is those steps in order, each its own process whose exit code is read:

    python warehouse/chat/eval/run_eval.py --set s320 --cap 6 --dry-run      prints the plan; starts, sends and writes nothing
    python warehouse/chat/eval/run_eval.py --set s1114 --cap 6 --only t01,t02
        --port 3713          the local server's port (refused when it is taken)
        --min-free-gb 3      a build needs this much memory free (chain 075's wait was stopped by the machine's low memory)
        --lock-as WHO        the build lock's holder (default eval-<set>); waited for at most --lock-min minutes (20)
        --no-build           serve the build already in site/.next (it must be of this copy's HEAD: the step says so)

The steps:

    probe      python scripts/db_probe.py (exit 1: no build now; the run stops)
    memory     the machine's free memory against --min-free-gb (Windows: wmic; elsewhere /proc/meminfo)
    lock       python scripts/buildlock.py acquire WHO --wait-min N; released at the end whatever happened
    build      npm run build in site/ with ERW_READ_TIMING=1, its log under runs/eval/
    serve      npx next start -p PORT with ASK_VISITOR_SALT from the root .env and ASK_EVAL_DAILY_USD at the server's own
               value plus the cap (the run's own cap is checked before every question), until /api/ask answers
    keys       the set's keys from the live set, the same hour (eval_s1113.py --keys, or expected_s1114.py)
    ask        eval_s1113.py --ask --set SET --base URL --cap CAP [--only ...]: the spend checked before each question
    grade      eval_s1113.py --grade --set SET
    stop       the server's process tree by its process id

Nothing here writes warehouse data. The model is called only in `ask`, through the site's route, as an evaluation.
"""
import argparse
import json
import os
import re
import shutil
import socket
import subprocess
import sys
import time
import urllib.error
import urllib.request

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.abspath(os.path.join(HERE, "..", "..", ".."))
MAIN = ROOT if os.path.exists(os.path.join(ROOT, ".env")) else os.path.join(os.path.dirname(ROOT), "erw")   # a worktree's keys are the main checkout's
PY = sys.executable
SETS = {"s320": {"keys": [PY, os.path.join(HERE, "eval_s1113.py"), "--keys"]},
        "s1114": {"keys": [PY, os.path.join(HERE, "expected_s1114.py")]}}


def env_value(path, name):
    if not os.path.exists(path):
        return ""
    with open(path, encoding="utf-8") as f:
        for line in f:
            m = re.match(rf"^{name}=(.*)$", line.strip())
            if m:
                return m.group(1).strip().strip('"')
    return ""


def plan(which, cap, port, only=None, lock_as=None, lock_min=20, min_free=3.0, build=True):
    """The steps, in order: (name, what it runs, a sentence). Pure: nothing is run."""
    base = f"http://localhost:{port}"
    who = lock_as or f"eval-{which}"
    ask = [PY, os.path.join(HERE, "eval_s1113.py"), "--ask", "--set", which, "--base", base, "--cap", str(cap)] + (["--only", ",".join(sorted(only))] if only else [])
    steps = [
        ("probe", [PY, os.path.join(MAIN, "scripts", "db_probe.py")], "the database answers (exit 1: no build now)"),
        ("memory", None, f"at least {min_free:g} GB of memory free"),
        ("lock", [PY, os.path.join(MAIN, "scripts", "buildlock.py"), "acquire", who, "--wait-min", str(lock_min)], f"the build lock, as {who}, waited for at most {lock_min} minutes"),
    ]
    if build:
        steps.append(("build", ["npm", "run", "build"], "a production build of this copy, ERW_READ_TIMING=1, its log under runs/eval/"))
    steps += [
        ("serve", ["npx", "next", "start", "-p", str(port)], f"the build served on {base} with the visitor salt and the evaluation's ceiling"),
        ("keys", SETS[which]["keys"], f"the keys of {which} from the live set, the hour of the asking"),
        ("ask", ask, f"the questions of {which} asked as an evaluation, the spend checked before each against USD {cap:g}"),
        ("grade", [PY, os.path.join(HERE, "eval_s1113.py"), "--grade", "--set", which], f"the answers of {which} graded, no model"),
        ("stop", None, "the server's process tree stopped by its process id"),
        ("release", [PY, os.path.join(MAIN, "scripts", "buildlock.py"), "release", who], "the build lock released"),
    ]
    return steps


def free_gb():
    if os.name == "nt":
        out = subprocess.run(["wmic", "OS", "get", "FreePhysicalMemory", "/value"], capture_output=True, text=True).stdout
        m = re.search(r"FreePhysicalMemory=(\d+)", out)
        return int(m.group(1)) / 1024 / 1024 if m else None
    with open("/proc/meminfo") as f:
        m = re.search(r"MemAvailable:\s+(\d+)", f.read())
    return int(m.group(1)) / 1024 / 1024 if m else None


def port_taken(port):
    with socket.socket() as s:
        return s.connect_ex(("127.0.0.1", port)) == 0


def run(steps, which, cap, port, min_free, log_dir):
    os.makedirs(log_dir, exist_ok=True)
    server, held, code = None, None, 0
    try:
        for name, cmd, what in steps:
            print(f"{name:8} {what}", flush=True)
            if name == "memory":
                gb = free_gb()
                if gb is not None and gb < min_free:
                    print(f"         stopped: {gb:.1f} GB free"); return 1
                continue
            if name == "stop":
                continue
            if name == "release":
                continue
            if name == "serve":
                if port_taken(port):
                    print(f"         stopped: port {port} is taken"); return 1
                e = dict(os.environ)
                e["ASK_VISITOR_SALT"] = env_value(os.path.join(MAIN, ".env"), "ASK_VISITOR_SALT")
                own = float(env_value(os.path.join(ROOT, "site", ".env.local"), "ASK_EVAL_DAILY_USD") or 0)
                e["ASK_EVAL_DAILY_USD"] = str(own + cap)
                out = open(os.path.join(log_dir, f"serve_{which}.out"), "w", encoding="utf-8")
                server = subprocess.Popen(cmd, cwd=os.path.join(ROOT, "site"), env=e, stdout=out, stderr=subprocess.STDOUT, shell=(os.name == "nt"))
                for _ in range(120):
                    try:
                        urllib.request.urlopen(f"http://localhost:{port}/api/ask", timeout=5)
                        break
                    except urllib.error.HTTPError:
                        break          # the route answers (a GET is refused): the server is up
                    except Exception:  # noqa: BLE001: not listening yet
                        time.sleep(2)
                else:
                    print("         stopped: the server did not answer in 4 minutes"); return 1
                continue
            cwd = os.path.join(ROOT, "site") if name == "build" else ROOT
            e = dict(os.environ, ERW_READ_TIMING="1") if name == "build" else None
            with open(os.path.join(log_dir, f"{name}_{which}.out"), "w", encoding="utf-8") as out:
                r = subprocess.run(cmd, cwd=cwd, env=e, stdout=out, stderr=subprocess.STDOUT, shell=(os.name == "nt" and cmd[0] in ("npm", "npx")))
            print(f"         exit {r.returncode}", flush=True)
            if name == "lock" and r.returncode == 0:
                held = steps[[s[0] for s in steps].index("release")][1]
            if r.returncode != 0 and name != "grade":
                code = r.returncode
                return code
        return code
    finally:
        if server is not None:
            subprocess.run(["taskkill", "/PID", str(server.pid), "/T", "/F"] if os.name == "nt" else ["kill", str(server.pid)], capture_output=True)
            print("stop     the server stopped")
        if held:
            subprocess.run(held, capture_output=True)
            print("release  the build lock released")


def main(argv=None):
    ap = argparse.ArgumentParser(description="an evaluation of Ask as one command")
    ap.add_argument("--set", default="s320", choices=sorted(SETS))
    ap.add_argument("--cap", type=float, required=True)
    ap.add_argument("--port", type=int, default=3713)
    ap.add_argument("--only")
    ap.add_argument("--lock-as")
    ap.add_argument("--lock-min", type=int, default=20)
    ap.add_argument("--min-free-gb", type=float, default=3.0)
    ap.add_argument("--no-build", action="store_true")
    ap.add_argument("--dry-run", action="store_true")
    a = ap.parse_args(argv)
    only = set(a.only.split(",")) if a.only else None
    steps = plan(a.set, a.cap, a.port, only, a.lock_as, a.lock_min, a.min_free_gb, build=not a.no_build)
    if a.dry_run:
        for name, cmd, what in steps:
            print(f"{name:8} {what}" + (f"\n         {' '.join(cmd)}" if cmd else ""))
        return 0
    return run(steps, a.set, a.cap, a.port, a.min_free_gb, os.path.join(MAIN, "runs", "eval"))


if __name__ == "__main__":
    sys.exit(main())

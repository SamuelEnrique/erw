#!/usr/bin/env python3
"""The data lock and the machine's role (session 59): several machines, and GitHub's daily job, never write the warehouse
at once.

Energy Research Warehouse (ERW). docs/machines.md.

Roles. Each machine has one setting, its role, in .erw/machine.json (not in git): "data" (pulls, warehouse writes,
Supabase loads, Redivis uploads, archive writes) or "code" (the site, docs, derived pages from loaded data, tests).
Switching a machine is one command: python warehouse/lock.py role data (or code). A GitHub workflow is a data machine
named github:<workflow>#<run id>.

The lock. One row of the Supabase table erw_locks (migration 016), name "data": holder, task, acquired, expires. Taken
before any data write and released after; it expires after a set time (default 120 minutes) unless the holder renews it,
so a machine that closes, sleeps or crashes cannot hold it forever. Every data writer calls require(): the connectors'
writer (iso_prices.write_csv, write_snapshot), the Supabase loader, the Redivis uploader and the archive. Without the
lock it refuses to run. Writes into a directory other than warehouse/output (tests, scratch) are not data writes, and
neither is a test run (python -m unittest, pytest, or ERW_LOCK_EXEMPT=1).

    python warehouse/lock.py role data                 # this machine's role (data or code), and its name
    python warehouse/lock.py acquire --task daily [--minutes 120] [--wait 60]   # prints the token; saved in .erw/lock.json
    python warehouse/lock.py run --task daily -- bash warehouse/run_daily.sh    # take, renew every 10 minutes, run, release
    python warehouse/lock.py release
    python warehouse/lock.py status

Needs SUPABASE_URL and SUPABASE_SERVICE_KEY (.env or the environment); never printed.
"""

import argparse
import datetime as dt
import json
import os
import socket
import subprocess
import sys
import threading
import time

import requests

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.abspath(os.path.join(HERE, ".."))
STATE = os.path.join(ROOT, ".erw")
MACHINE = os.path.join(STATE, "machine.json")
LOCKFILE = os.path.join(STATE, "lock.json")
OUTPUT = os.path.normcase(os.path.abspath(os.path.join(ROOT, "warehouse", "output")))
NAME = "data"
_checked = {}


def env(name):
    v = os.environ.get(name)
    if not v:
        try:
            from dotenv import dotenv_values
            v = dotenv_values(os.path.join(ROOT, ".env")).get(name)
        except ImportError:
            v = None
    return (v or "").strip()


def machine():
    """This machine's name and role. A GitHub Actions run is the data machine github:<workflow>#<run id>."""
    if os.environ.get("GITHUB_ACTIONS") == "true":
        return {"name": f"github:{os.environ.get('GITHUB_WORKFLOW', 'workflow')}#{os.environ.get('GITHUB_RUN_ID', '')}", "role": "data"}
    m = {"name": socket.gethostname(), "role": "code"}
    if os.path.exists(MACHINE):
        m.update(json.load(open(MACHINE, encoding="utf-8")))
    if env("ERW_ROLE"):
        m["role"] = env("ERW_ROLE")
    return m


def set_role(role, name=None):
    if role not in ("data", "code"):
        raise SystemExit("role: data or code")
    os.makedirs(STATE, exist_ok=True)
    m = machine() if os.path.exists(MACHINE) else {"name": socket.gethostname()}
    m.update(role=role, **({"name": name} if name else {}))
    json.dump(m, open(MACHINE, "w", encoding="utf-8"), indent=1)
    return m


def rpc(fn, **args):
    url, key = env("SUPABASE_URL"), env("SUPABASE_SERVICE_KEY")
    if not url or not key:
        raise SystemExit("the data lock needs SUPABASE_URL and SUPABASE_SERVICE_KEY (.env or the environment)")
    import urllib.parse
    u = urllib.parse.urlparse(url)
    r = requests.post(f"{u.scheme}://{u.netloc}/rest/v1/rpc/{fn}", json=args, timeout=30,
                      headers={"apikey": key, "Authorization": f"Bearer {key}", "Content-Type": "application/json"})
    if r.status_code != 200:
        raise RuntimeError(f"{fn}: HTTP {r.status_code} {r.text[:200]}")
    return r.json()


def status():
    rows = rpc("erw_lock_status", p_name=NAME)
    return rows[0] if rows else None


def acquire(task, minutes=120, wait=0):
    """Take the data lock for this machine; returns the token, saved in .erw/lock.json and ERW_LOCK_TOKEN. Waits up to
    `wait` minutes for another holder to release it or let it expire."""
    m = machine()
    if m["role"] != "data":
        raise SystemExit(f"this machine ({m['name']}) has the role {m['role']!r}; only a data machine takes the data lock "
                         "(python warehouse/lock.py role data)")
    deadline = time.time() + wait * 60
    while True:
        tok = rpc("erw_lock_acquire", p_name=NAME, p_holder=m["name"], p_task=task, p_minutes=minutes)
        if tok:
            os.makedirs(STATE, exist_ok=True)
            json.dump({"token": tok, "holder": m["name"], "task": task, "acquired": dt.datetime.now(dt.timezone.utc).isoformat()},
                      open(LOCKFILE, "w", encoding="utf-8"), indent=1)
            os.environ["ERW_LOCK_TOKEN"] = tok
            return tok
        s = status()
        if time.time() >= deadline:
            raise SystemExit(f"the data lock is held by {s['holder']} for {s['task']!r} until {s['expires']}; not taken")
        print(f"the data lock is held by {s['holder']} ({s['task']}) until {s['expires']}; waiting", flush=True)
        time.sleep(60)


def token():
    t = os.environ.get("ERW_LOCK_TOKEN")
    if not t and os.path.exists(LOCKFILE):
        t = json.load(open(LOCKFILE, encoding="utf-8")).get("token")
    return t


def renew(tok=None, minutes=120):
    return bool(rpc("erw_lock_renew", p_name=NAME, p_token=tok or token(), p_minutes=minutes))


def release(tok=None):
    tok = tok or token()
    ok = bool(rpc("erw_lock_release", p_name=NAME, p_token=tok)) if tok else False
    if os.path.exists(LOCKFILE) and (not tok or json.load(open(LOCKFILE, encoding="utf-8")).get("token") == tok):
        os.remove(LOCKFILE)
    os.environ.pop("ERW_LOCK_TOKEN", None)
    return ok


def require(path=None, what="this data write"):
    """Refuse a data write without the data lock. A write outside warehouse/output (tests, scratch: path given and not
    under it) is not a data write. ERW_LOCK_EXEMPT=1 (set by the test runners) also passes."""
    if os.environ.get("ERW_LOCK_EXEMPT") == "1" or any(x in (sys.argv[0] if sys.argv else "") for x in ("unittest", "pytest")):
        return
    if path is not None and not os.path.normcase(os.path.abspath(path)).startswith(OUTPUT):
        return
    tok = token()
    if not tok:
        raise SystemExit(f"{what} refuses to run without the data lock (python warehouse/lock.py acquire --task <task>, "
                         "or run it through: python warehouse/lock.py run --task <task> -- <command>)")
    now = time.time()
    if _checked.get(tok, 0) > now - 300:
        return
    if not rpc("erw_lock_check", p_name=NAME, p_token=tok):
        raise SystemExit(f"{what} refuses to run: this machine's data lock has expired or was taken by another holder")
    _checked[tok] = now


def run(task, cmd, minutes=120, wait=0):
    """Take the lock, run the command with ERW_LOCK_TOKEN set, renew every 10 minutes, release after (always)."""
    tok = acquire(task, minutes, wait)
    stop = threading.Event()

    def keep():
        while not stop.wait(600):
            try:
                if not renew(tok, minutes):
                    print("WARNING: the data lock could not be renewed", file=sys.stderr, flush=True)
            except Exception as exc:  # a network blip: the next try may work; the lock lasts `minutes`
                print(f"WARNING: renewing the data lock: {exc}", file=sys.stderr, flush=True)
    threading.Thread(target=keep, daemon=True).start()
    try:
        return subprocess.call(cmd, env={**os.environ, "ERW_LOCK_TOKEN": tok})
    finally:
        stop.set()
        release(tok)


def main(argv=None):
    ap = argparse.ArgumentParser(description="ERW data lock and machine role (session 59)")
    ap.add_argument("action", choices=["role", "acquire", "release", "renew", "status", "run"])
    ap.add_argument("value", nargs="?")
    ap.add_argument("--task", default="")
    ap.add_argument("--minutes", type=int, default=120)
    ap.add_argument("--wait", type=int, default=0, help="minutes to wait for another holder")
    ap.add_argument("--name", help="role: this machine's name (default its host name)")
    ap.add_argument("--github-env", action="store_true", help="acquire: append ERW_LOCK_TOKEN to $GITHUB_ENV")
    a, rest = ap.parse_known_args(argv)
    if a.action == "role":
        print(json.dumps(set_role(a.value, a.name) if a.value else machine()))
    elif a.action == "acquire":
        try:
            tok = acquire(a.task or "unnamed", a.minutes, a.wait)
        except SystemExit as e:
            if str(e).startswith("the data lock is held") and os.environ.get("ERW_SKIP_EXIT"):
                # session 61: a scheduled job that finds the lock held should not run: a success with the reason
                print(f"skipped: {e}")
                sys.exit(int(os.environ["ERW_SKIP_EXIT"]))
            raise
        if a.github_env and os.environ.get("GITHUB_ENV"):
            open(os.environ["GITHUB_ENV"], "a", encoding="utf-8").write(f"ERW_LOCK_TOKEN={tok}\n")
        print(f"data lock taken by {machine()['name']} for {a.task!r}, {a.minutes} minutes")
    elif a.action == "release":
        print("data lock released" if release() else "no data lock held by this machine")
    elif a.action == "renew":
        print("renewed" if renew(minutes=a.minutes) else "not held")
    elif a.action == "status":
        s = status()
        print(json.dumps(s, default=str) if s else "the data lock is free")
    elif a.action == "run":
        cmd = rest[1:] if rest[:1] == ["--"] else rest
        if not cmd:
            raise SystemExit("run: the command after --")
        try:
            sys.exit(run(a.task or " ".join(cmd)[:80], cmd, a.minutes, a.wait))
        except SystemExit as e:
            if isinstance(e.code, str) and e.code.startswith("the data lock is held") and os.environ.get("ERW_SKIP_EXIT"):
                print(f"skipped: {e.code}")
                sys.exit(int(os.environ["ERW_SKIP_EXIT"]))
            raise


if __name__ == "__main__":
    main()

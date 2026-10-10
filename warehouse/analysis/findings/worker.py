#!/usr/bin/env python3
"""The findings worker (session 170): the data machine takes queued requests from /analysis and runs them.

Energy Research Warehouse (ERW).

    python warehouse/analysis/findings/worker.py --once            # one turn: take every queued request, run each, stop
    python warehouse/analysis/findings/worker.py --loop 60         # a turn every 60 seconds, until stopped
    python warehouse/analysis/findings/worker.py --status          # is it registered, is it alive, what did it last take
    python warehouse/analysis/findings/worker.py --local-dir DIR   # the queue as JSON files in DIR (tests, a machine
                                                                   # without the migration): DIR/<id>.json is a row

How a request waits: a row of public.analysis_requests (migration 027) with status queued and the time it was asked.
This machine is the data machine, the one that holds the full histories (ERW_DATA_DIR, else warehouse/output). When it
is off the row stays queued and /analysis says so with the time; when it wakes, this worker takes the oldest queued row,
marks it running with the machine's name, runs the finding (run_finding.run) against the histories here, and writes the
card into the row (status done, card_id, card) or the plain reason (status failed). Supabase is reached with the
service role (SUPABASE_URL and SUPABASE_SERVICE_KEY from .env, as warehouse/lock.py reads them), which bypasses row
level security.

A service since session 181 (scripts/register_findings_worker.ps1 registers it with the Task Scheduler; this file is
what makes it safe to leave running):

    one instance   a lock file (runs/findings_worker.lock, or next to a --local-dir queue) holds the process id. A
                   second worker that finds the holder alive says so in one line and exits 0. A lock whose process is
                   gone (a restart, a killed process) is recovered and the recovery is logged.
    it stays up    a turn that fails (no network, Supabase answering an error) is one log line; the wait doubles from
                   the loop's seconds up to 15 minutes and goes back after a good turn. It never exits on such an error.
                   A request this machine left running when it died is put back to queued (older than
                   --stale-running-minutes) when the worker starts, and once an hour after.
    it stops       Ctrl-C, a terminate signal, Ctrl-Break on Windows, or a file named runs/findings_worker.stop: the
                   request in hand is finished, the lock is released, the exit is 0. The wait is in one second steps.
    the data lock  is never taken, not for one request and not at all: a finding and the scanner read tables and write
                   cards, drafts and the queue row; they write no warehouse table. So a daily run is never kept waiting.
    no model       nothing here or in the findings calls a model. The words on a card are written by code.
    the scanner    a queued row whose finding is scanner_daily is the daily scan (findings_scanner.daily_request): it
                   ends done with the scan's note and no card. Every other row is a finding of run_finding.FINDINGS
                   (the impact study among them).
    the state      runs/findings_worker.state.json: the heartbeat of each turn, the last request it took, the counts
                   since it started. --status reads it, with the lock, the scheduled task and the queue's length.

Starting it by hand: a PowerShell window, `C:\\Users\\lossa\\Documents\\erw\\.venv\\Scripts\\python.exe
warehouse\\analysis\\findings\\worker.py --loop 60`.
"""

import argparse
import datetime as dt
import importlib
import json
import os
import signal
import socket
import subprocess
import sys
import time
import traceback
import urllib.parse

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.abspath(os.path.join(HERE, "..", "..", ".."))
sys.path.insert(0, HERE)
sys.path.insert(0, os.path.join(ROOT, "warehouse"))
import findings_common as common  # noqa: E402
import run_finding  # noqa: E402

TABLE = "analysis_requests"
TASK_NAME = "ERW findings worker"          # the scheduled task scripts/register_findings_worker.ps1 registers
SCANNER = "scanner_daily"                  # a queued row with this finding is the daily scan, not a card
OWN_FILES = "findings_worker."             # the lock, the state and the stop file begin so; never a queue row
MAX_WAIT = 900                             # seconds: the longest wait after turns that failed
_sleep = time.sleep                        # the tests put a counter here


def now():
    return dt.datetime.now(dt.timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def log(msg):
    print(f"{now()[11:19]} {msg}", flush=True)


class Supabase:
    """The queue as rows of the request table, read and written with the service role."""

    def __init__(self):
        import lock
        import requests
        self.requests = requests
        url, key = lock.env("SUPABASE_URL"), lock.env("SUPABASE_SERVICE_KEY")
        if not url or not key:
            raise SystemExit("the worker needs SUPABASE_URL and SUPABASE_SERVICE_KEY (.env or the environment)")
        u = urllib.parse.urlparse(url)
        self.base = f"{u.scheme}://{u.netloc}/rest/v1/{TABLE}"
        self.h = {"apikey": key, "Authorization": f"Bearer {key}", "Content-Type": "application/json"}

    def queued(self):
        r = self.requests.get(self.base, params={"kind": "eq.run", "status": "eq.queued", "order": "asked_at.asc", "limit": "20"},
                              headers=self.h, timeout=30)
        r.raise_for_status()
        return r.json()

    def running(self, machine):
        r = self.requests.get(self.base, params={"kind": "eq.run", "status": "eq.running", "machine": f"eq.{machine}", "select": "id,started_at,machine", "limit": "50"},
                              headers=self.h, timeout=30)
        r.raise_for_status()
        return r.json()

    def queued_count(self):
        r = self.requests.get(self.base, params={"kind": "eq.run", "status": "eq.queued", "select": "id", "limit": "1000"}, headers=self.h, timeout=30)
        r.raise_for_status()
        return len(r.json())

    def update(self, rid, fields):
        r = self.requests.patch(self.base, params={"id": f"eq.{rid}"}, json=fields, headers={**self.h, "Prefer": "return=minimal"}, timeout=60)
        r.raise_for_status()


class LocalDir:
    """The queue as JSON files (one row each) in a folder: the tests, and a machine without the migration."""

    def __init__(self, d):
        self.d = d
        os.makedirs(d, exist_ok=True)

    def rows(self):
        out = []
        for f in sorted(os.listdir(self.d)):
            if f.endswith(".json") and not f.startswith(OWN_FILES):
                with open(os.path.join(self.d, f), encoding="utf-8") as fh:
                    out.append(json.load(fh))
        return out

    def queued(self):
        return sorted([r for r in self.rows() if r.get("kind", "run") == "run" and r.get("status") == "queued"], key=lambda r: r.get("asked_at", ""))

    def running(self, machine):
        return [r for r in self.rows() if r.get("kind", "run") == "run" and r.get("status") == "running" and r.get("machine", "") == machine]

    def queued_count(self):
        return len(self.queued())

    def update(self, rid, fields):
        p = os.path.join(self.d, rid + ".json")
        with open(p, encoding="utf-8") as fh:
            row = json.load(fh)
        row.update(fields)
        with open(p, "w", encoding="utf-8", newline="\n") as fh:
            json.dump(row, fh, indent=1, default=common.round6)


# ----------------------------------------------------------------------------------------------------------------------
# one instance: the lock file
# ----------------------------------------------------------------------------------------------------------------------
def pid_alive(pid):
    """Is a process with this id running on this machine?"""
    try:
        pid = int(pid)
    except (TypeError, ValueError):
        return False
    if pid <= 0:
        return False
    if os.name == "nt":
        import ctypes
        from ctypes import wintypes
        k = ctypes.WinDLL("kernel32", use_last_error=True)
        k.OpenProcess.restype = wintypes.HANDLE
        k.OpenProcess.argtypes = [wintypes.DWORD, wintypes.BOOL, wintypes.DWORD]
        k.GetExitCodeProcess.argtypes = [wintypes.HANDLE, ctypes.POINTER(wintypes.DWORD)]
        k.CloseHandle.argtypes = [wintypes.HANDLE]
        h = k.OpenProcess(0x1000, False, pid)          # PROCESS_QUERY_LIMITED_INFORMATION
        if not h:
            return ctypes.get_last_error() == 5        # access denied: a process is there, another account's
        try:
            code = wintypes.DWORD()
            return bool(k.GetExitCodeProcess(h, ctypes.byref(code))) and code.value == 259   # STILL_ACTIVE
        finally:
            k.CloseHandle(h)
    try:
        os.kill(pid, 0)
    except ProcessLookupError:
        return False
    except PermissionError:
        return True
    except OSError:
        return False
    return True


def proc_started(pid):
    """When the process began, as seconds since 1970 (Windows; None where it cannot be read). After a restart Windows
    hands old process ids to new processes: a lock whose id is alive but began at another time is not its holder."""
    if os.name != "nt":
        return None
    try:
        import ctypes
        from ctypes import wintypes
        k = ctypes.WinDLL("kernel32", use_last_error=True)
        k.OpenProcess.restype = wintypes.HANDLE
        k.OpenProcess.argtypes = [wintypes.DWORD, wintypes.BOOL, wintypes.DWORD]
        k.CloseHandle.argtypes = [wintypes.HANDLE]
        h = k.OpenProcess(0x1000, False, int(pid))
        if not h:
            return None
        try:
            c, e, kt, ut = wintypes.FILETIME(), wintypes.FILETIME(), wintypes.FILETIME(), wintypes.FILETIME()
            k.GetProcessTimes.argtypes = [wintypes.HANDLE] + [ctypes.POINTER(wintypes.FILETIME)] * 4
            if not k.GetProcessTimes(h, ctypes.byref(c), ctypes.byref(e), ctypes.byref(kt), ctypes.byref(ut)):
                return None
            return round(((c.dwHighDateTime << 32) + c.dwLowDateTime) / 1e7 - 11644473600, 3)
        finally:
            k.CloseHandle(h)
    except Exception:
        return None


def read_lock(path):
    try:
        with open(path, encoding="utf-8") as f:
            return json.load(f)
    except (OSError, ValueError):
        return None


def holder_alive(held):
    """Is the process a lock names still that process? Alive, and begun when the lock says it began (where known)."""
    if not isinstance(held, dict) or not pid_alive(held.get("pid")):
        return False
    then, began = held.get("proc_started"), proc_started(held.get("pid"))
    if then is None or began is None:
        return True
    return abs(float(then) - began) < 2.0


def take_lock(path, machine):
    """(True, note) when this process now holds the lock; (False, the one line to print) when a live worker does."""
    os.makedirs(os.path.dirname(os.path.abspath(path)), exist_ok=True)
    mine = {"pid": os.getpid(), "started_at": now(), "machine": machine, "proc_started": proc_started(os.getpid())}
    note = ""
    for _ in range(3):
        try:
            fd = os.open(path, os.O_CREAT | os.O_EXCL | os.O_WRONLY)
        except FileExistsError:
            held = read_lock(path)
            if held is not None and holder_alive(held):
                return False, f"another worker holds the lock, pid {held.get('pid')} (since {held.get('started_at', '?')}, {path})"
            # stale: its process is gone (or the file cannot be read). Only one process can move it aside.
            aside = f"{path}.stale.{os.getpid()}"
            try:
                os.replace(path, aside)
                os.remove(aside)
            except OSError:
                pass
            note = f"a stale lock was recovered (pid {held.get('pid') if isinstance(held, dict) else 'unreadable'} is not running)"
            continue
        with os.fdopen(fd, "w", encoding="utf-8") as f:
            json.dump(mine, f)
        if note:
            _sleep(0.2)                                  # two workers recovering one stale lock: the later file wins
            held = read_lock(path)
            if not isinstance(held, dict) or held.get("pid") != os.getpid():
                return False, f"another worker holds the lock, pid {held.get('pid') if isinstance(held, dict) else '?'} ({path})"
        return True, note
    return False, f"the lock could not be taken ({path})"


def release_lock(path):
    held = read_lock(path)
    if isinstance(held, dict) and held.get("pid") == os.getpid():
        try:
            os.remove(path)
        except OSError:
            pass


# ----------------------------------------------------------------------------------------------------------------------
# the state file
# ----------------------------------------------------------------------------------------------------------------------
class State:
    """What the worker last did, for --status: written whole each time, through a temporary file."""

    def __init__(self, path, machine):
        self.path = path
        self.d = {"pid": os.getpid(), "machine": machine, "started_at": now(), "heartbeat_at": None, "turns": 0, "done": 0, "failed": 0,
                  "last_request": None, "last_error": None}

    def write(self):
        if not self.path:
            return
        try:
            os.makedirs(os.path.dirname(os.path.abspath(self.path)), exist_ok=True)
            tmp = f"{self.path}.{os.getpid()}.tmp"
            with open(tmp, "w", encoding="utf-8", newline="\n") as f:
                json.dump(self.d, f, indent=1)
                f.write("\n")
            os.replace(tmp, self.path)
        except OSError as exc:
            log(f"the state file could not be written: {exc}")

    def beat(self, error=None):
        self.d["heartbeat_at"] = now()
        self.d["turns"] += 1
        if error:
            self.d["last_error"] = {"at": now(), "error": error}
        self.write()

    def took(self, row, status):
        self.d["last_request"] = {"id": row.get("id"), "finding": row.get("finding"), "status": status, "at": now()}
        self.d["done" if status == "done" else "failed"] += 1
        self.write()


# ----------------------------------------------------------------------------------------------------------------------
# a request
# ----------------------------------------------------------------------------------------------------------------------
def run_scanner(q, row, params, in_dir):
    """The daily scan, asked through the queue: findings_scanner.daily_request scans the tables here and loads the
    drafts; the row ends done with the scan's note and no card."""
    scanner = importlib.import_module("findings_scanner")
    out = scanner.daily_request(params, in_dir, lambda m: log("  " + m)) or {}
    note = str(out.get("note") or f"{out.get('flags', 0)} flags, {out.get('drafts', 0)} drafts, {out.get('loaded', 0)} loaded")
    q.update(row["id"], {"status": "done", "done_at": now(), "note": note[:200]})
    log(f"  done: {note[:200]}")


def run_one(q, row, machine, in_dir, card_dir, download_dir):
    rid = row["id"]
    params = row.get("params") or {}
    if isinstance(params, str):
        params = json.loads(params or "{}")
    log(f"request {rid}: {row['finding']} {params} (asked {row.get('asked_at', '?')})")
    q.update(rid, {"status": "running", "started_at": now(), "machine": machine})
    try:
        if row["finding"] == SCANNER:
            run_scanner(q, row, params, in_dir)
            return "done"
        path, card = run_finding.run(row["finding"], params, in_dir, card_dir, download_dir, log=lambda m: log("  " + m))
        q.update(rid, {"status": "done", "done_at": now(), "card_id": card["card_id"], "card": json.loads(json.dumps(card, default=common.round6)), "note": ""})
        log(f"  done: {card['card_id']}")
        return "done"
    except common.NoData as exc:
        q.update(rid, {"status": "failed", "done_at": now(), "note": f"a table is not on the data machine: {str(exc)[:200]}"})
        log(f"  failed (no data): {exc}")
    except ValueError as exc:
        q.update(rid, {"status": "failed", "done_at": now(), "note": str(exc)[:200]})
        log(f"  failed (input): {exc}")
    except Exception as exc:
        q.update(rid, {"status": "failed", "done_at": now(), "note": f"{type(exc).__name__}: {str(exc)[:160]}"})
        log(f"  FAILED: {traceback.format_exc()}")
    return "failed"


def turn(q, machine, in_dir, card_dir, download_dir, state=None, should_stop=None):
    rows = q.queued()
    if not rows:
        return 0
    n = 0
    for row in rows:
        if should_stop is not None and should_stop():
            break                                        # the request in hand was finished; the rest stay queued
        status = run_one(q, row, machine, in_dir, card_dir, download_dir)
        n += 1
        if state is not None:
            state.took(row, status)
    return n


def requeue_stale(q, machine, minutes):
    """A request this machine marked running and never finished (the worker died): back to queued, to be taken again."""
    cut = (dt.datetime.now(dt.timezone.utc) - dt.timedelta(minutes=minutes)).strftime("%Y-%m-%dT%H:%M:%SZ")
    n = 0
    for r in q.running(machine):
        started = str(r.get("started_at") or "")[:19].replace(" ", "T") + "Z"
        if len(started) == 20 and started < cut:
            q.update(r["id"], {"status": "queued", "started_at": None, "machine": "", "note": f"put back: left running by a worker that stopped ({started})"})
            log(f"request {r['id']}: put back to queued (running since {started}, no worker held it)")
            n += 1
    return n


def wait(seconds, should_stop):
    """Sleep in one second steps, so that a stop is answered within a second."""
    left = float(seconds)
    while left > 0 and not should_stop():
        _sleep(min(1.0, left))
        left -= 1.0


# ----------------------------------------------------------------------------------------------------------------------
# --status
# ----------------------------------------------------------------------------------------------------------------------
def task_state():
    """Is the scheduled task registered? A read of the Task Scheduler; nothing is changed."""
    if os.name != "nt":
        return "not on Windows"
    try:
        r = subprocess.run(["schtasks", "/Query", "/TN", TASK_NAME, "/FO", "LIST"], capture_output=True, text=True, timeout=20)
    except (OSError, subprocess.SubprocessError) as exc:
        return f"could not be asked ({type(exc).__name__})"
    if r.returncode != 0:
        return "not registered"
    wanted = [ln.strip() for ln in r.stdout.splitlines() if ln.split(":")[0].strip().lower() in ("status", "next run time")]
    return "registered" + (" (" + "; ".join(wanted) + ")" if wanted else "")


def status(a, out=None):
    out = out or print
    lock_file, state_file, _ = own_paths(a)
    out(f'scheduled task "{TASK_NAME}": {task_state()}')
    held = read_lock(lock_file)
    if held is None:
        out(f"process: not running (no lock at {lock_file})")
    elif holder_alive(held):
        out(f"process: alive, pid {held.get('pid')} on {held.get('machine', '?')}, since {held.get('started_at', '?')}")
    else:
        out(f"process: not running (a stale lock names pid {held.get('pid')}, since {held.get('started_at', '?')}; the next worker recovers it)")
    st = read_lock(state_file)
    if not isinstance(st, dict):
        out(f"heartbeat: none recorded ({state_file} is not there)")
        out("last request: none recorded")
    else:
        out(f"heartbeat: {st.get('heartbeat_at') or 'none yet'} (turn {st.get('turns', 0)} since {st.get('started_at', '?')}; {st.get('done', 0)} done, {st.get('failed', 0)} failed)")
        last = st.get("last_request")
        out(f"last request: {last['id']} {last['finding']} {last['status']} at {last['at']}" if last else "last request: none since it started")
        if st.get("last_error"):
            out(f"last failed turn: {st['last_error'].get('at')} {st['last_error'].get('error')}")
    try:
        q = LocalDir(a.local_dir) if a.local_dir else Supabase()
        out(f"queued: {q.queued_count()} request(s) in {'the files of ' + a.local_dir if a.local_dir else 'Supabase ' + TABLE}")
    except SystemExit as exc:
        out(f"queued: not asked ({exc})")
    except Exception as exc:
        out(f"queued: could not be asked ({type(exc).__name__}: {str(exc)[:120]})")
    return 0


def own_paths(a):
    """The lock, the state and the stop file: under runs/ of this checkout, or next to a --local-dir queue."""
    home = a.local_dir if a.local_dir else os.path.join(ROOT, "runs")
    lock_file = a.lock_file or os.path.join(home, OWN_FILES + "lock")
    state_file = a.state_file or os.path.join(home, OWN_FILES + "state.json")
    stop_file = a.stop_file or os.path.join(os.path.dirname(os.path.abspath(lock_file)), OWN_FILES + "stop")
    return lock_file, state_file, stop_file


def main(argv=None):
    ap = argparse.ArgumentParser(description="ERW findings worker (session 170; a service since session 181)")
    ap.add_argument("--once", action="store_true", help="one turn, then stop")
    ap.add_argument("--loop", type=int, default=0, metavar="SECONDS", help="a turn every SECONDS until stopped")
    ap.add_argument("--status", action="store_true", help="say whether it is registered and alive, what it last took, how many wait")
    ap.add_argument("--local-dir", help="the queue as JSON files in this folder instead of Supabase")
    ap.add_argument("--in-dir", default=common.DEFAULT_IN_DIR, help="the warehouse's output directory")
    ap.add_argument("--card-dir", help="where cards are written (default site/data/findings)")
    ap.add_argument("--download-dir", help="where downloads are written (default site/public/findings)")
    ap.add_argument("--machine", default=socket.gethostname())
    ap.add_argument("--lock-file", help="the one-instance lock (default runs/findings_worker.lock, or in --local-dir)")
    ap.add_argument("--state-file", help="the heartbeat and the last request (default runs/findings_worker.state.json, or in --local-dir)")
    ap.add_argument("--stop-file", help="a file whose presence stops the worker at its next turn (default findings_worker.stop next to the lock)")
    ap.add_argument("--stale-running-minutes", type=int, default=60, help="a request this machine left running longer than this is put back to queued")
    a = ap.parse_args(argv)
    if a.status:
        return status(a)
    if not a.once and not a.loop:
        ap.error("--once, --loop SECONDS or --status")
    lock_file, state_file, stop_file = own_paths(a)
    ok, note = take_lock(lock_file, a.machine)
    if not ok:
        log(note)
        return 0
    stop = {"flag": False, "why": ""}

    def ask_stop(signum, _frame):
        stop["flag"], stop["why"] = True, f"signal {signum}"

    def should_stop():
        if not stop["flag"] and os.path.exists(stop_file):
            stop["flag"], stop["why"] = True, f"the stop file {stop_file}"
            try:
                os.remove(stop_file)
            except OSError:
                pass
        return stop["flag"]

    old = {}
    for name in ("SIGINT", "SIGTERM", "SIGBREAK"):
        sig = getattr(signal, name, None)
        if sig is not None:
            try:
                old[sig] = signal.signal(sig, ask_stop)
            except (ValueError, OSError):
                pass                                     # not the main thread (a test): Ctrl-C still raises below
    state = State(state_file, a.machine)
    try:
        if note:
            log(note)
        if os.path.exists(stop_file):                    # a stop asked before this worker started is not for it
            try:
                os.remove(stop_file)
                log(f"an old stop file was removed ({stop_file})")
            except OSError:
                pass
        q = LocalDir(a.local_dir) if a.local_dir else Supabase()
        log(f"findings worker on {a.machine}, pid {os.getpid()}, tables in {a.in_dir}, queue {'files in ' + a.local_dir if a.local_dir else 'Supabase ' + TABLE}")
        state.write()
        pause, checked_stale = a.loop, 0.0
        while True:
            if should_stop():
                break
            error = None
            try:
                if time.time() - checked_stale >= 3600:
                    requeue_stale(q, a.machine, a.stale_running_minutes)
                    checked_stale = time.time()
                n = turn(q, a.machine, a.in_dir, a.card_dir, a.download_dir, state, should_stop)
                if n:
                    log(f"turn: {n} request(s)")
                pause = a.loop
            except KeyboardInterrupt:
                stop["flag"], stop["why"] = True, "Ctrl-C"
            except Exception as exc:
                error = f"{type(exc).__name__}: {str(exc)[:200]}"
                pause = min(max(pause, 1) * 2, MAX_WAIT) if a.loop else 0
                log(f"turn failed: {error}" + (f"; the next try in {pause} seconds" if a.loop else ""))
            state.beat(error)
            if a.once or should_stop():
                break
            try:
                wait(pause, should_stop)
            except KeyboardInterrupt:
                stop["flag"], stop["why"] = True, "Ctrl-C"
        if stop["flag"]:
            log(f"stopped ({stop['why']})")
        return 0
    finally:
        for sig, handler in old.items():
            try:
                signal.signal(sig, handler)
            except (ValueError, OSError):
                pass
        release_lock(lock_file)


if __name__ == "__main__":
    sys.exit(main())

#!/usr/bin/env python3
"""A machine on duty, and the idle alarm: one line by email when it has run nothing for 30 minutes (session 188).

Energy Research Warehouse (ERW). docs/machines.md, "Continuous work". The chain watch (scripts/alert.py, session 91)
asks whether one marked chain has saved anything, and reads GitHub for it; GitHub cannot say which machine pushed a
commit. This asks the question per machine: a machine is on duty from its precheck (scripts/precheck.py) until it
declares idle (scripts/chain_queue.py, when queue/next/ is empty) or signs off, and while it is on duty every commit,
push or beat made on it is a sign of work.

    python scripts/duty.py start --what "session 188" [--hours 16]   on duty (the precheck does this when it passes)
    python scripts/duty.py beat          a sign of work nothing else shows (a long build or pull commits nothing). The
                                         git hooks in scripts/githooks/ send one at each commit and each push made on a
                                         machine on duty, from its main checkout or from any worktree of it
    python scripts/duty.py off [--reason "signed off"]    off duty: the mark is removed
    python scripts/duty.py status        this machine's mark, and what the check would say of every machine on duty
    python scripts/duty.py check [--dry-run]    the scheduled check (.github/workflows/chain-watch.yml, every 15
                                         minutes): emails when a machine on duty has run nothing for 30 minutes

A machine on duty is one row, "duty:<machine>", of the Supabase table erw_locks (migration 016: the data lock's own
table and functions, as the chain's mark uses them, so no new table and no migration): the machine, what it is on duty
for, since when, its last sign of work (the row's "renewed"), and when the mark lapses by itself. It is not the data
lock and blocks nothing. The token is kept in .erw/duty.json of the machine's main checkout; a git worktree has no
.erw/ of its own and uses the main checkout's, so a session in a worktree is the machine too.

The check emails once when the silence passes 30 minutes, and not again for that silence (session 202, the one alert
policy: until then it said so again every hour), as the chain check does, through scripts/alert.py's sender: to the
fixed recipients only, and no address is ever printed. A new commit, push or beat ends the silence; a later one is a new
one. A mark that lapsed without "off" is said once. What was said is remembered in erw_health (scripts/alert.py, told
and say). No model call. Needs only Python's standard library.

Exit codes: 0 done (for check: nothing to say, or the lines were sent); 1 could not (no key, the database did not
answer, Resend refused every line); 2 bad input.
"""

import argparse
import datetime as dt
import json
import os
import subprocess
import sys
import types
import urllib.error
import urllib.parse
import urllib.request

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.abspath(os.path.join(HERE, ".."))
sys.path.insert(0, HERE)
import alert  # noqa: E402  (the sender, the erw_locks functions, the 30 minutes and the hour)

PREFIX = "duty:"        # the rows of erw_locks: duty:<machine>
HOURS = 16.0            # a mark lapses by itself after this long without a new start
UTC = dt.timezone.utc


_main = {}


def main_checkout(root=ROOT):
    """The main checkout this folder is a worktree of (or the folder itself), or None when git cannot say."""
    if root not in _main:
        try:
            r = subprocess.run(["git", "rev-parse", "--path-format=absolute", "--git-common-dir"], cwd=root, capture_output=True, text=True,
                               timeout=20, stdin=subprocess.DEVNULL)
            common = r.stdout.strip()
            _main[root] = os.path.abspath(os.path.join(common, "..")) if r.returncode == 0 and common else None
        except (OSError, subprocess.SubprocessError):
            _main[root] = None
    return _main[root]


def env(name):
    """A key from the environment or .env, as scripts/alert.py reads it; in a git worktree that holds no .env of its
    own, from the main checkout's. Never printed."""
    v = alert.env(name)
    if v:
        return v
    m = main_checkout()
    if m and os.path.normcase(m) != os.path.normcase(ROOT):
        return (alert.dotenv(os.path.join(m, ".env")).get(name) or "").strip()
    return ""


def rpc(fn, **args):
    """One of the erw_locks functions of migration 016, with the service key, as scripts/alert.py calls them."""
    url, key = env("SUPABASE_URL"), env("SUPABASE_SERVICE_KEY")
    if not url or not key:
        raise RuntimeError("SUPABASE_URL or SUPABASE_SERVICE_KEY is not set")
    u = urllib.parse.urlparse(url)
    r = alert.http_post(f"{u.scheme}://{u.netloc}/rest/v1/rpc/{fn}", json=args, timeout=30, headers={"apikey": key, "Authorization": f"Bearer {key}"})
    if r.status_code != 200:
        raise RuntimeError(f"{fn}: HTTP {r.status_code} {r.text[:200]}")
    return r.json()


def send(subject, line, dry_run=False):
    """scripts/alert.py's sender (one line, the fixed recipients only), with the keys as env() above finds them."""
    return alert.send(subject, line, dry_run, env=env)


def state_dir(root=ROOT, main=main_checkout):
    """Where this machine keeps its role and its marks: the .erw/ that holds the role file machine.json. That is this
    folder's own, or, in a git worktree (whose .erw/, if it has one at all, holds no role file), the main checkout's."""
    here = os.path.join(root, ".erw")
    if os.path.exists(os.path.join(here, "machine.json")):
        return here
    m = main(root)
    there = os.path.join(m, ".erw") if m else None
    return there if there and os.path.exists(os.path.join(there, "machine.json")) else here


def machine(state=None):
    """{name, role} from the role file .erw/machine.json, or None when it is absent or cannot be read."""
    try:
        with open(os.path.join(state or state_dir(), "machine.json"), encoding="utf-8") as f:
            m = json.load(f)
    except (OSError, ValueError):
        return None
    return m if isinstance(m, dict) else None


def clean(name):
    """A machine's name as a row's name and a branch's: lower case letters, digits and hyphens."""
    s = "".join(c if c.isalnum() else "-" for c in str(name or "").lower()).strip("-")
    return s[:40] or "machine"


def row_name(name):
    return PREFIX + clean(name)


def _file(state):
    return os.path.join(state or state_dir(), "duty.json")


def held(state=None):
    """What this machine wrote when it went on duty ({token, machine, what, started, until}), or None."""
    try:
        with open(_file(state), encoding="utf-8") as f:
            h = json.load(f)
    except (OSError, ValueError):
        return None
    return h if isinstance(h, dict) and h.get("token") else None


def start(name, what, hours=HOURS, rpc=None, state=None, now=None):
    """Put the machine on duty, or renew its mark when it already is. Returns the line that says which."""
    rpc = rpc or globals()["rpc"]
    state = state or state_dir()
    now = now or dt.datetime.now(UTC)
    what = alert.one_line(what or "unnamed work", 120)
    minutes = max(1, int(hours * 60))
    until = now + dt.timedelta(hours=hours)
    mine = held(state)
    if mine:  # this machine's own mark, from an earlier precheck: given up, so that the new one names the new work
        rpc("erw_lock_release", p_name=row_name(name), p_token=mine["token"])
    tok = rpc("erw_lock_acquire", p_name=row_name(name), p_holder=clean(name), p_task=what, p_minutes=minutes)
    if not tok:
        if mine and os.path.exists(_file(state)):
            os.remove(_file(state))
        raise RuntimeError(f"{clean(name)} is marked on duty by a token this checkout does not hold; not marked again "
                           "(python scripts/duty.py off, where it was started, ends it; the mark lapses by itself)")
    _write(state, {"token": tok, "machine": clean(name), "what": what, "started": now.isoformat(), "until": until.isoformat()})
    return (f"{clean(name)} is on duty for \"{what}\" until {until:%Y-%m-%d %H:%M} UTC"
            + (f" (it was on duty for \"{mine.get('what')}\")" if mine else ""))


def _write(state, h):
    os.makedirs(state, exist_ok=True)
    with open(_file(state), "w", encoding="utf-8") as f:
        json.dump(h, f, indent=1)


def beat(rpc=None, state=None, now=None):
    """A sign of work: renews the mark for the time it has left. True when the mark was renewed."""
    rpc = rpc or globals()["rpc"]
    h = held(state)
    if not h:
        return False
    now = now or dt.datetime.now(UTC)
    left = max(1, int((alert.parse(h["until"]) - now).total_seconds() // 60))
    return bool(rpc("erw_lock_renew", p_name=row_name(h["machine"]), p_token=h["token"], p_minutes=left))


def off(rpc=None, state=None):
    """Off duty: the mark is removed (the machine declared idle, or signed off). Returns the line that says so."""
    rpc = rpc or globals()["rpc"]
    h = held(state)
    if not h:
        return "this machine is not on duty (.erw/duty.json is absent)"
    ok = rpc("erw_lock_release", p_name=row_name(h["machine"]), p_token=h["token"])
    os.remove(_file(state))
    return f"{h['machine']} is off duty" if ok else f"the mark of {h['machine']} was already gone; this machine's note of it is removed"


def http_get(url, headers=None, timeout=30):
    """requests.get's shape (status_code, text, json()) on the standard library."""
    req = urllib.request.Request(url, method="GET", headers={"User-Agent": "erw-alert/1", **(headers or {})})
    try:
        with urllib.request.urlopen(req, timeout=timeout) as r:
            status, text = r.status, r.read().decode("utf-8", "replace")
    except urllib.error.HTTPError as e:
        status, text = e.code, e.read().decode("utf-8", "replace")
    return types.SimpleNamespace(status_code=status, text=text, json=lambda: json.loads(text or "null"))


def rows(get=http_get, env=None):
    """Every machine marked on duty: the duty:* rows of erw_locks, times as datetimes. Read with the service key, which
    is the only key the table answers (row-level security on, nothing granted to the site's key)."""
    env = env or globals()["env"]
    url, key = env("SUPABASE_URL"), env("SUPABASE_SERVICE_KEY")
    if not url or not key:
        raise RuntimeError("SUPABASE_URL or SUPABASE_SERVICE_KEY is not set")
    u = urllib.parse.urlparse(url)
    r = get(f"{u.scheme}://{u.netloc}/rest/v1/erw_locks?select=name,holder,task,acquired,renewed,expires&name=like.{PREFIX}*&order=name",
            headers={"apikey": key, "Authorization": f"Bearer {key}"}, timeout=30)
    if r.status_code != 200:
        raise RuntimeError(f"erw_locks: HTTP {r.status_code} {r.text[:200]}")
    out = []
    for m in r.json() or []:
        if str(m.get("name") or "").startswith(PREFIX):
            out.append({**m, **{k: alert.parse(m.get(k)) for k in ("acquired", "renewed", "expires")}})
    return out


def last_sign(row):
    """(when, what) of a machine's newest sign of work: its precheck, or a commit, a push or a beat since."""
    if row.get("renewed") and row["renewed"] > row["acquired"]:
        return row["renewed"], "a commit, a push or a beat"
    return row["acquired"], "its precheck"


def key_of(now, row):
    """What the memory holds for the line decide() would send now: the lapse of this mark, or this silence (named by
    the sign of work it began at, so that a later sign makes a later silence a new one)."""
    name = str(row["name"])[len(PREFIX):]
    if row["expires"] < now:
        return f"lapsed|{name}|{row['expires']:%Y-%m-%dT%H:%M}"
    return f"quiet|{name}|{last_sign(row)[0]:%Y-%m-%dT%H:%M}"


def decide(now, row, memory=None):
    """What the check says of one machine on duty: (subject, line) to send, or (None, why it stays quiet). `memory` is
    the set of keys already said (alert.told), or None when it cannot be read: the line is then due only in the quarter
    of an hour after the silence passed 30 minutes."""
    name = str(row["name"])[len(PREFIX):]
    what = alert.one_line(row.get("task") or "unnamed work", 80)
    hm = lambda t: t.strftime("%H:%M")  # noqa: E731
    key = key_of(now, row)
    if row["expires"] < now:
        late = (now - row["expires"]).total_seconds() / 60
        if late < alert.LAPSE_HOURS * 60 and alert.due(late, 0, key, memory):
            return ("ERW: a machine's duty mark lapsed", alert.one_line(
                f"The machine {name} was on duty for \"{what}\" until {hm(row['expires'])} UTC and never declared idle or signed off: "
                "it ran past its time or stopped without saying so."))
        return None, f"the mark of {name} lapsed {late:.0f} minutes ago; already said"
    last, sign = last_sign(row)
    quiet = (now - last).total_seconds() / 60
    if quiet < alert.QUIET_MIN:
        return None, f"{name} ran something {quiet:.0f} minutes ago ({sign}, {hm(last)} UTC)"
    if not alert.due(quiet, alert.QUIET_MIN, key, memory):
        return None, f"{name} has run nothing for {quiet:.0f} minutes; said once, and not again for this silence"
    return ("ERW: a machine has run nothing for 30 minutes", alert.one_line(
        f"The machine {name}, on duty for \"{what}\", has run nothing for {quiet:.0f} minutes: its last sign of work was {sign} at {hm(last)} UTC. "
        f"On duty since {hm(row['acquired'])} UTC. Said once: no further email for this silence."))


def check(dry_run=False, now=None, read=None, send=None, out=print, told=None, say=None):
    """The scheduled check: one line, once, for each machine on duty that has run nothing for 30 minutes. Returns 0
    when there was nothing to say or a line went out, 1 when every line that was due could not be sent."""
    now = now or dt.datetime.now(UTC)
    read, send = read or rows, send or globals()["send"]
    told = told or (lambda t: alert.told(t, env=env))
    say = say or (lambda kind, key: alert.say(kind, key, env=env))
    marked = read()
    if not marked:
        out("quiet: no machine is on duty")
        return 0
    memory = told(now)
    due = failed = 0
    for row in marked:
        subject, line = decide(now, row, memory)
        if subject is None:
            out(f"quiet: {line}")
            continue
        due += 1
        try:
            n = send(subject, line, dry_run)
            if not dry_run:
                say("idle alarm", key_of(now, row))
                out(f"alert: {line} (sent to {n} fixed recipient{'s' if n != 1 else ''})")
        except Exception as exc:  # one machine's line must not cost another's
            failed += 1
            out(f"alert: not sent ({type(exc).__name__}: {str(exc)[:160]}): {line}")
    return 1 if due and failed == due else 0


def main(argv=None):
    ap = argparse.ArgumentParser(description="A machine on duty, and the idle alarm (session 188)")
    ap.add_argument("action", choices=["start", "beat", "off", "status", "check"])
    ap.add_argument("--what", default="", help="start: what the machine is on duty for (a session, a chain)")
    ap.add_argument("--hours", type=float, default=HOURS, help="start: the mark lapses by itself after this long (default 16)")
    ap.add_argument("--reason", default="", help="off: why, for the line printed")
    ap.add_argument("--state", help="the folder that holds machine.json and duty.json (default: .erw of the main checkout)")
    ap.add_argument("--dry-run", action="store_true", help="check: print the lines, send nothing")
    a = ap.parse_args(argv)
    try:
        if a.action == "check":  # on GitHub: it reads the marks and needs nothing of a machine
            return check(a.dry_run)
        state = a.state or state_dir()
        if a.action == "start":
            m = machine(state)
            if not m or not m.get("name"):
                print("duty start: the role file .erw/machine.json is absent or names no machine (python warehouse/lock.py role code --name <name>)", file=sys.stderr)
                return 2
            print(start(m["name"], a.what, a.hours, state=state))
            return 0
        if a.action == "beat":
            ok = beat(state=state)
            print("beat" if ok else "this machine is not on duty, or its mark is gone or has lapsed; not renewed")
            return 0 if ok else 1
        if a.action == "off":
            print(off(state=state) + (f" ({alert.one_line(a.reason, 120)})" if a.reason else ""))
            return 0
        h = held(state)
        print(f"this machine: on duty for \"{h.get('what')}\" since {h.get('started', '')[:16]} UTC" if h else "this machine: not on duty")
        now = dt.datetime.now(UTC)
        for row in rows():
            made = decide(now, row, alert.told(now, env=env))
            print(("the check would send: " if made[0] else "the check would stay quiet: ") + made[1])
        return 0
    except Exception as exc:
        print(f"duty: {type(exc).__name__}: {str(exc)[:300]}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    sys.exit(main())

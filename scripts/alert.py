#!/usr/bin/env python3
"""One line by email when an unattended session needs a person (session 91).

Energy Research Warehouse (ERW). docs/machines.md, "Alerts". Two things can leave a night's chain of sessions standing
still with nobody told: a session that waits for input or for a permission, and a chain that stopped saving (a closed
laptop, a crash, a usage limit, a command that hangs). Each gets one line by email, through the sender the digest and
scripts/notify.py use (Resend: RESEND_API_KEY, DIGEST_FROM), to the fixed recipients only (DIGEST_RECIPIENTS): never to
a subscriber, and no address is ever printed or logged. No model call. Needs only Python's standard library: a hook
runs with whatever interpreter the machine has, and must not fail for a missing package.

    The hook (a session waits)
    python scripts/alert.py hook            Claude Code's Notification hook (.claude/settings.json) pipes its JSON here.
                                            Sends one line for a wait for permission or for input, at most one per
                                            session and kind every 10 minutes. Always exits 0: it never stops a session.
                                            ERW_ALERTS=off in the environment (or the file .erw/alerts_off) silences it.

    The chain (nothing saved for 30 minutes)
    python scripts/alert.py chain start --name "night of 4 October, sessions 90 to 101" [--hours 16]
    python scripts/alert.py chain beat      a save that is not a push: renews the mark (a long pull pushes nothing)
    python scripts/alert.py chain done      the chain finished: the mark is removed
    python scripts/alert.py chain status
    python scripts/alert.py chain check [--dry-run]     the scheduled check (.github/workflows/chain-watch.yml, every 15
                                            minutes): emails when a marked chain has saved nothing for 30 minutes

    python scripts/alert.py send --subject "..." --line "..." [--dry-run]

A chain is marked as running by one row, "chain", of the Supabase table erw_locks (migration 016: the data lock's own
table and functions, so no new table): who started it, its name, when, and when the mark lapses by itself. The token is
kept in .erw/chain.json on the machine that started it. A save is a commit pushed to a wip/ or task/ branch of the
repository (read from GitHub, so the check needs nothing from the machine that may have died) or a beat. The check
emails once when the silence passes 30 minutes and again every hour after (at 90, 150, ... minutes), not every 15
minutes. A mark that has lapsed is a chain nobody ended: the check says so once, in the first quarter of an hour after
it lapsed, and then stays quiet.

Exit codes: 0 done (for check: nothing to say, or the email was sent); 1 could not (no key, the database or GitHub did
not answer, Resend refused); 2 bad input.
"""

import argparse
import datetime as dt
import json
import os
import socket
import sys
import time
import types
import urllib.error
import urllib.parse
import urllib.request

ROOT = os.path.abspath(os.path.join(os.path.dirname(os.path.abspath(__file__)), ".."))
STATE = os.path.join(ROOT, ".erw")
RESEND = "https://api.resend.com/emails"
REPO = "SamuelEnrique/erw"
MARK = "chain"          # the row of erw_locks
QUIET_MIN = 30          # a chain that saved nothing for this long is reported
AGAIN_MIN = 60          # and again every this many minutes
EVERY_MIN = 15          # how often the check runs: the width of the window an alert falls in
HOOK_GAP_S = 600        # one email per session and kind every 10 minutes
MAX_LINE = 300
# the kinds of Notification this alerts on, and how the line names them (Claude Code's notification_type)
WAITS = {"permission_prompt": "a permission", "idle_prompt": "input", "elicitation_dialog": "an answer", "agent_needs_input": "input"}


def dotenv(path=None):
    """The KEY=VALUE lines of .env, read here so that the hook needs no package."""
    out = {}
    try:
        with open(path or os.path.join(ROOT, ".env"), encoding="utf-8") as f:
            for ln in f:
                ln = ln.strip()
                if ln and not ln.startswith("#") and "=" in ln:
                    k, v = ln.split("=", 1)
                    v = v.strip()
                    out[k.strip().removeprefix("export ").strip()] = v[1:-1] if len(v) >= 2 and v[0] == v[-1] and v[0] in "\"'" else v
    except OSError:
        pass
    return out


def env(name):
    return (os.environ.get(name) or dotenv().get(name) or "").strip()


def http_post(url, headers=None, timeout=30, json=None):
    """requests.post's shape (status_code, text, json()) on the standard library."""
    import json as _json
    req = urllib.request.Request(url, data=_json.dumps(json).encode("utf-8"), method="POST",
                                 headers={"Content-Type": "application/json", "User-Agent": "erw-alert/1", **(headers or {})})
    try:
        with urllib.request.urlopen(req, timeout=timeout) as r:
            status, text = r.status, r.read().decode("utf-8", "replace")
    except urllib.error.HTTPError as e:
        status, text = e.code, e.read().decode("utf-8", "replace")
    return types.SimpleNamespace(status_code=status, text=text, json=lambda: _json.loads(text or "null"))


def one_line(text, limit=MAX_LINE):
    """Text on one line, without an em dash, at most `limit` characters."""
    s = " ".join(str(text).replace(chr(0x2014), ", ").split())
    return s if len(s) <= limit else s[:limit - 3].rstrip() + "..."


def send(subject, line, dry_run=False, post=http_post, env=env):
    """One message to each fixed recipient: the line and nothing else. Returns the number sent."""
    line = one_line(line)
    if not line:
        raise ValueError("the line is empty")
    if dry_run:
        print(f"Subject: {subject}\n\n{line}\n")
        return 0
    key = env("RESEND_API_KEY")
    to = [a.strip() for a in env("DIGEST_RECIPIENTS").split(",") if a.strip()]
    if not key or not to:
        raise RuntimeError("not sent: " + ", ".join(n for n, v in (("RESEND_API_KEY", key), ("DIGEST_RECIPIENTS", to)) if not v) + " not set")
    sender = env("DIGEST_FROM") or "ERW Energy Digest <onboarding@resend.dev>"
    sent = 0
    for addr in to:
        r = post(RESEND, headers={"Authorization": f"Bearer {key}"}, timeout=30,
                 json={"from": sender, "to": [addr], "subject": subject, "text": line + "\n"})
        if r.status_code >= 300:
            raise RuntimeError(f"Resend HTTP {r.status_code} after {sent} of {len(to)} sent")
        sent += 1
    return sent


# ---------------------------------------------------------------------------------------------------------------------
# the hook: a session waits

def hook_line(event, machine=None, chain=None):
    """(subject, line) for a Notification the owner should hear of, or None for one that is not a wait."""
    kind = wait_kind(event)
    if kind is None:
        return None
    session = str(event.get("session_id") or "")[:8] or "unknown"
    where = os.path.basename(str(event.get("cwd") or "").rstrip("/\\")) or "an unknown folder"
    said = one_line(event.get("message") or event.get("title") or "", 140)
    line = (f"A Claude Code session waits for {WAITS[kind]} on {machine or socket.gethostname()} (session {session}, in {where})"
            + (f", in the chain \"{chain}\"" if chain else "") + (f": {said}" if said else "."))
    return f"ERW: a session waits for {WAITS[kind]}", one_line(line)


def wait_kind(event):
    """The kind of wait an event is, or None. Claude Code names it in notification_type; an event that names none is
    read from its message (the settings' matchers let only waits through, so a wait is the likely reading)."""
    kind = str(event.get("notification_type") or "")
    if kind:
        return kind if kind in WAITS else None
    said = str(event.get("message") or "").lower()
    return "permission_prompt" if "permission" in said else "idle_prompt" if "waiting for" in said or "input" in said else None


def hook_due(session, kind, now, state_dir=None, gap=HOOK_GAP_S, record=False):
    """True when no email went out for this session and kind in the last `gap` seconds. With record, notes that one
    just did (only a line that was sent is noted, so a send that failed does not silence the next)."""
    d = os.path.join(state_dir or STATE, "alerts")
    os.makedirs(d, exist_ok=True)
    f = os.path.join(d, "".join(c for c in session if c.isalnum() or c in "-_")[:40] + ".json")
    last = {}
    if os.path.exists(f):
        try:
            last = json.load(open(f, encoding="utf-8"))
        except (OSError, ValueError):
            last = {}
    if record:
        last[kind] = now
        json.dump(last, open(f, "w", encoding="utf-8"))
        return True
    return kind not in last or now - float(last[kind]) >= gap


def silenced():
    return env("ERW_ALERTS").lower() in ("off", "0", "no") or os.path.exists(os.path.join(STATE, "alerts_off"))


def local_chain():
    """The name of the chain this machine marked as running, or None."""
    f = os.path.join(STATE, "chain.json")
    try:
        return json.load(open(f, encoding="utf-8")).get("name") if os.path.exists(f) else None
    except (OSError, ValueError):
        return None


def hook(stdin=None, post=http_post, env=env, state_dir=None, now=None):
    """Reads the hook's JSON and sends the line. Never raises and never blocks: a session must not stop on its alert."""
    try:
        event = json.loads((stdin if stdin is not None else sys.stdin.read()) or "{}")
        made = hook_line(event, chain=local_chain())
        if made is None or silenced():
            return "nothing to send"
        session, kind, now = str(event.get("session_id") or "unknown"), wait_kind(event), time.time() if now is None else now
        if not hook_due(session, kind, now, state_dir):
            return "sent less than 10 minutes ago for this session and kind"
        n = send(made[0], made[1], post=post, env=env)
        hook_due(session, kind, now, state_dir, record=True)
        return f"sent to {n} fixed recipient{'s' if n != 1 else ''}"
    except Exception as exc:  # the hook's failure is the hook's alone
        return f"not sent: {type(exc).__name__}: {str(exc)[:160]}"


# ---------------------------------------------------------------------------------------------------------------------
# the chain: nothing saved for 30 minutes

def rpc(fn, **args):
    url, key = env("SUPABASE_URL"), env("SUPABASE_SERVICE_KEY")
    if not url or not key:
        raise RuntimeError("SUPABASE_URL or SUPABASE_SERVICE_KEY is not set")
    u = urllib.parse.urlparse(url)
    r = http_post(f"{u.scheme}://{u.netloc}/rest/v1/rpc/{fn}", json=args, timeout=30, headers={"apikey": key, "Authorization": f"Bearer {key}"})
    if r.status_code != 200:
        raise RuntimeError(f"{fn}: HTTP {r.status_code} {r.text[:200]}")
    return r.json()


def parse(ts):
    return dt.datetime.fromisoformat(str(ts).replace("Z", "+00:00")).astimezone(dt.timezone.utc) if ts else None


def mark():
    """The chain marked as running: {holder, task, acquired, renewed, expires, expired}, times as datetimes; or None."""
    rows = rpc("erw_lock_status", p_name=MARK)
    if not rows:
        return None
    m = rows[0]
    return {**m, **{k: parse(m.get(k)) for k in ("acquired", "renewed", "expires")}}


def newest_push(token=None, repo=REPO, post=http_post):
    """The newest commit on any wip/ or task/ branch on GitHub: (time, branch, headline), or None when there is none."""
    token = token or env("GH_TOKEN") or env("GITHUB_TOKEN")
    if not token:
        raise RuntimeError("GH_TOKEN (or GITHUB_TOKEN) is not set")
    owner, name = repo.split("/")
    part = lambda alias, prefix: (f'{alias}: refs(refPrefix: "refs/heads/{prefix}/", first: 3, orderBy: {{field: TAG_COMMIT_DATE, direction: DESC}}) '
                                  "{ nodes { name target { ... on Commit { committedDate messageHeadline } } } }")  # noqa: E731
    q = f'query {{ repository(owner: "{owner}", name: "{name}") {{ {part("wip", "wip")} {part("task", "task")} }} }}'
    r = post("https://api.github.com/graphql", json={"query": q}, timeout=30, headers={"Authorization": f"Bearer {token}"})
    if r.status_code != 200 or "errors" in r.json():
        raise RuntimeError(f"GitHub: HTTP {r.status_code} {str(r.json().get('errors') if r.status_code == 200 else r.text)[:200]}")
    best = None
    for prefix in ("wip", "task"):
        for n in r.json()["data"]["repository"][prefix]["nodes"]:
            t = parse((n.get("target") or {}).get("committedDate"))
            if t and (best is None or t > best[0]):
                best = (t, f"{prefix}/{n['name']}", n["target"].get("messageHeadline") or "")
    return best


def decide(now, m, push):
    """What the check says: (subject, line) to send, or (None, why it stays quiet). `m` is the mark, `push` the newest
    push as newest_push gives it."""
    if m is None:
        return None, "no chain is marked as running"
    name = one_line(m.get("task") or "unnamed", 80)
    hm = lambda t: t.strftime("%H:%M")  # noqa: E731
    if m["expires"] < now:
        late = (now - m["expires"]).total_seconds() / 60
        if late < EVERY_MIN:
            return ("ERW: a chain's mark lapsed", one_line(
                f"The chain \"{name}\" ({m['holder']}) was marked as running until {hm(m['expires'])} UTC and was never marked done: "
                "it ran past its time or stopped without saying so."))
        return None, f"the mark of \"{name}\" lapsed {late:.0f} minutes ago; already said"
    saves = [(m["acquired"], "its start")]
    if m.get("renewed") and m["renewed"] > m["acquired"]:
        saves.append((m["renewed"], "a beat"))
    if push:
        saves.append((push[0], f"a push to {push[1]}"))
    last, what = max(saves, key=lambda s: s[0])
    quiet = (now - last).total_seconds() / 60
    if quiet < QUIET_MIN:
        return None, f"\"{name}\" saved {quiet:.0f} minutes ago ({what}, {hm(last)} UTC)"
    if (quiet - QUIET_MIN) % AGAIN_MIN >= EVERY_MIN:
        return None, f"\"{name}\" has saved nothing for {quiet:.0f} minutes; said at {QUIET_MIN} minutes and every {AGAIN_MIN} after"
    return ("ERW: a chain has saved nothing for 30 minutes" if quiet < QUIET_MIN + EVERY_MIN else "ERW: a chain is still saving nothing", one_line(
        f"The chain \"{name}\" ({m['holder']}) has saved nothing for {quiet:.0f} minutes: its last save was {what} at {hm(last)} UTC. "
        f"Marked as running since {hm(m['acquired'])} UTC."))


def holder():
    s = "".join(c for c in (os.environ.get("ERW_SESSION") or os.environ.get("CLAUDE_CODE_SESSION_ID") or "") if c.isalnum() or c in "-_")
    return f"{socket.gethostname()}/{s[:8]}" if s else socket.gethostname()


def chain(a):
    f = os.path.join(STATE, "chain.json")
    held = json.load(open(f, encoding="utf-8")) if os.path.exists(f) else None
    now = dt.datetime.now(dt.timezone.utc)
    if a.action == "start":
        if not a.name:
            print("chain start: --name", file=sys.stderr)
            return 2
        tok = rpc("erw_lock_acquire", p_name=MARK, p_holder=holder(), p_task=one_line(a.name, 120), p_minutes=int(a.hours * 60))
        if not tok:
            m = mark()
            print(f"a chain is already marked as running: \"{m['task']}\" by {m['holder']} until {m['expires']:%Y-%m-%d %H:%M} UTC; not marked "
                  "(python scripts/alert.py chain done, on the machine that started it, ends it)", file=sys.stderr)
            return 1
        os.makedirs(STATE, exist_ok=True)
        until = now + dt.timedelta(hours=a.hours)
        json.dump({"token": tok, "name": one_line(a.name, 120), "holder": holder(), "started": now.isoformat(), "until": until.isoformat()},
                  open(f, "w", encoding="utf-8"), indent=1)
        print(f"chain \"{one_line(a.name, 120)}\" marked as running by {holder()} until {until:%Y-%m-%d %H:%M} UTC")
        return 0
    if a.action in ("beat", "done"):
        if not held:
            print("this machine marked no chain (.erw/chain.json is absent)", file=sys.stderr)
            return 1
        if a.action == "beat":
            left = max(1, int((parse(held["until"]) - now).total_seconds() // 60))
            ok = rpc("erw_lock_renew", p_name=MARK, p_token=held["token"], p_minutes=left)
            print("beat" if ok else "the mark is gone or has lapsed; not renewed")
            return 0 if ok else 1
        ok = rpc("erw_lock_release", p_name=MARK, p_token=held["token"])
        os.remove(f)
        print(f"chain \"{held['name']}\" marked done" if ok else "the mark was already gone; this machine's note of it is removed")
        return 0
    m = mark()
    push = newest_push() if m else None
    made = decide(now, m, push)
    if a.action == "status":
        print("no chain is marked as running" if m is None else
              f"\"{m['task']}\" by {m['holder']}, since {m['acquired']:%Y-%m-%d %H:%M} UTC, until {m['expires']:%Y-%m-%d %H:%M} UTC"
              + (f"; newest push {push[0]:%H:%M} UTC to {push[1]}" if push else "; no push found"))
        print("the check would send: " + made[1] if made[0] else "the check would stay quiet: " + made[1])
        return 0
    if made[0] is None:  # check
        print(f"quiet: {made[1]}")
        return 0
    n = send(made[0], made[1], dry_run=a.dry_run)
    if not a.dry_run:
        print(f"alert: {made[1]} (sent to {n} fixed recipient{'s' if n != 1 else ''})")
    return 0


def main(argv=None):
    ap = argparse.ArgumentParser(description="One line by email when an unattended session needs a person")
    sub = ap.add_subparsers(dest="cmd", required=True)
    sub.add_parser("hook", help="Claude Code's Notification hook: its JSON on stdin")
    c = sub.add_parser("chain", help="mark a chain as running, and the check of it")
    c.add_argument("action", choices=["start", "beat", "done", "status", "check"])
    c.add_argument("--name")
    c.add_argument("--hours", type=float, default=16.0, help="start: the mark lapses by itself after this long (default 16)")
    c.add_argument("--dry-run", action="store_true", help="check: print the message, send nothing")
    s = sub.add_parser("send", help="one line, now")
    s.add_argument("--subject", required=True)
    s.add_argument("--line", required=True)
    s.add_argument("--dry-run", action="store_true")
    a = ap.parse_args(argv)
    if a.cmd == "hook":
        hook()  # what it did is not printed: a hook's output may be shown to the session
        return 0
    try:
        if a.cmd == "chain":
            return chain(a)
        n = send(a.subject, a.line, a.dry_run)
        if not a.dry_run:
            print(f"alert: sent to {n} fixed recipient{'s' if n != 1 else ''}")
        return 0
    except ValueError as exc:
        print(f"alert: {exc}", file=sys.stderr)
        return 2
    except Exception as exc:
        print(f"alert: {type(exc).__name__}: {str(exc)[:300]}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    sys.exit(main())

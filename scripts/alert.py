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
                                            A wait for input is not said for ten minutes after the session's last words
                                            held REPORT READY or CHAIN DONE (session 116): it has finished, and says so.

    The chain (nothing saved for 30 minutes)
    python scripts/alert.py chain start --name "night of 4 October, sessions 90 to 101" [--hours 16]
    python scripts/alert.py chain beat      a save GitHub cannot see: renews the mark (a long pull pushes nothing). The
                                            git hooks in scripts/githooks/ send one at each commit and each push made on
                                            the machine that marked the chain (session 116)
    python scripts/alert.py chain done      the chain finished: the mark is removed
    python scripts/alert.py chain status
    python scripts/alert.py chain check [--dry-run]     the scheduled check (.github/workflows/chain-watch.yml, every 15
                                            minutes): emails when a marked chain has saved nothing for 30 minutes

    python scripts/alert.py send --subject "..." --line "..." [--dry-run]

    The one alert policy (session 202; docs/machines.md, "One alert policy")
    python scripts/alert.py failures [--dry-run]    the scheduled check (chain-watch.yml, every 15 minutes): one email for
                                            each step of a scheduled job newly recorded as failed in erw_health. A step
                                            that failed at its run before is the same failure and is not said again; a
                                            retry that passed is not a failure; more than five at once are one email.
                                            The Roundup's failures are told by its own workflow's last step, not here
    python scripts/alert.py summary [--dry-run] [--html FILE] [--force]    the morning summary, 07:00 Pacific, once a
                                            day (the same workflow asks every 15 minutes): the runs since the last
                                            morning, one line each, green or red
    A silence (a chain that saved nothing, a machine on duty that ran nothing) is said once, not again every hour: a new
    sign of work is what makes a later silence a new one. Successes send nothing. What was said is remembered as rows
    of erw_health (workflow "alerts"), so a late or a doubled run of the check neither loses a line nor repeats one.

A chain is marked as running by one row, "chain", of the Supabase table erw_locks (migration 016: the data lock's own
table and functions, so no new table): who started it, its name, when, and when the mark lapses by itself. The token is
kept in .erw/chain.json on the machine that started it.

A save (session 116: it was a push to a wip/ or task/ branch only, so a landing read as silence) is any of:
  - a commit on any branch of the repository on GitHub, main included, that a scheduled workflow did not write (the
    daily run, the roundup and the vacuum commit as github-actions[bot]: those are not the chain's). Read from GitHub,
    so the check needs nothing from the machine that may have died;
  - the workflow's merge of a task/ branch into main: the landing of the chain's own push, written by the same bot;
  - a beat: by hand, or sent by the git hooks at each commit and each push on the chain's machine (a commit that is
    not pushed yet is seen by nobody else).
The check emails once when the silence passes 30 minutes, and not again for that silence (session 202: until then it said
so again every hour). A mark that has lapsed is a chain nobody ended: the check says so once and then stays quiet.

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
QUIET_MIN = 30          # a chain that saved nothing for this long is reported, once (session 202: not again every hour)
EVERY_MIN = 15          # how often the check runs: the width of the window an alert falls in when the memory cannot be read
MEMORY = "alerts"       # the workflow name of the erw_health rows that remember what was already said (session 202)
MEMORY_HOURS = 30       # how far back the memory is read: longer than any silence or failure is told for
LAPSE_HOURS = 6         # a lapsed mark found later than this is not said at all
MANY = 5                # more new failures than this in one check are one email, not one each
SUMMARY_HOUR = 7        # the morning summary: 07:00 Pacific
HOOK_GAP_S = 600        # one email per session and kind every 10 minutes
DONE_WORDS = ("REPORT READY", "CHAIN DONE")   # a session that ends on one of these has finished and says so
DONE_QUIET_S = 600      # a wait for input is not said for this long after them (session 116)
DONE_KINDS = ("idle_prompt", "agent_needs_input")   # the waits for input; a wait for a permission is always said
TAIL_BYTES = 512_000    # how much of a transcript's end is read for the session's last words
BOTS = ("github-actions[bot]",)   # who the scheduled workflows commit as (.github/workflows/*.yml)
REFS, COMMITS = 20, 30  # the newest branches read from GitHub, and the newest commits of each
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


def deliver(subject, text, html=None, post=http_post, env=env):
    """One message to each fixed recipient, and to nobody else. Returns the number sent."""
    key = env("RESEND_API_KEY")
    to = [a.strip() for a in env("DIGEST_RECIPIENTS").split(",") if a.strip()]
    if not key or not to:
        raise RuntimeError("not sent: " + ", ".join(n for n, v in (("RESEND_API_KEY", key), ("DIGEST_RECIPIENTS", to)) if not v) + " not set")
    sender = env("DIGEST_FROM") or "ERW Energy Digest <onboarding@resend.dev>"
    sent = 0
    for addr in to:
        body = {"from": sender, "to": [addr], "subject": subject, "text": text}
        if html:
            body["html"] = html
        r = post(RESEND, headers={"Authorization": f"Bearer {key}"}, timeout=30, json=body)
        if r.status_code >= 300:
            raise RuntimeError(f"Resend HTTP {r.status_code} after {sent} of {len(to)} sent")
        sent += 1
    return sent


def send(subject, line, dry_run=False, post=http_post, env=env):
    """One message to each fixed recipient: the line and nothing else. Returns the number sent."""
    line = one_line(line)
    if not line:
        raise ValueError("the line is empty")
    if dry_run:
        print(f"Subject: {subject}\n\n{line}\n")
        return 0
    return deliver(subject, line + "\n", post=post, env=env)


# ---------------------------------------------------------------------------------------------------------------------
# the hook: a session waits

def hook_line(event, machine=None, chain=None):
    """(subject, line) for a Notification the owner should hear of, or None for one that is not a wait."""
    kind = wait_kind(event)
    if kind is None:
        return None
    session = str(event.get("session_id") or "")[:8] or "unknown"
    # the folder's own name, whichever machine wrote the path: a Windows path read on Linux has no "/" to split at
    # (session 102: the test of this line failed on GitHub's runner, where os.path.basename left the path whole)
    where = str(event.get("cwd") or "").replace("\\", "/").rstrip("/").split("/")[-1] or "an unknown folder"
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


def last_words(path, tail=TAIL_BYTES):
    """The session's last words in its transcript (Claude Code's JSONL, one entry a line): (the text, when it was said as
    seconds since the epoch), or None when the newest entry is the person's, or the session has said nothing.

    Read from the end. An entry that is neither the person's nor the session's (a system note, an attachment) and a
    side chain's are passed over, and so is a session's entry with no text in it (thinking, a tool call). A person's
    entry met first means the session has not answered it yet: what it said before no longer stands."""
    with open(path, "rb") as f:
        f.seek(0, os.SEEK_END)
        size = f.tell()
        f.seek(max(0, size - tail))
        lines = f.read().decode("utf-8", "replace").splitlines()
    for ln in reversed(lines):
        try:
            e = json.loads(ln)
        except ValueError:
            continue  # the cut line at the start of the tail, or a line half written
        if not isinstance(e, dict) or e.get("isSidechain") or e.get("type") not in ("user", "assistant"):
            continue
        if e["type"] == "user":
            return None
        content = (e.get("message") or {}).get("content")
        text = content if isinstance(content, str) else " ".join(
            str(b.get("text") or "") for b in content or [] if isinstance(b, dict) and b.get("type") == "text")
        if not text.strip():
            continue
        try:
            when = parse(e.get("timestamp")).timestamp()
        except (TypeError, ValueError, AttributeError):
            when = os.path.getmtime(path)  # an entry without its time: when the transcript was last written
        return text, when
    return None


def said_done(event, now, quiet=DONE_QUIET_S):
    """(the words, seconds ago) when the session's last words held REPORT READY or CHAIN DONE less than `quiet` seconds
    ago; None otherwise, and None whenever the transcript cannot be read: an alert too many, never one too few."""
    try:
        got = last_words(str(event.get("transcript_path") or ""))
    except Exception:  # no path, no file, not a transcript: nothing is known, so nothing is quieted
        return None
    if not got:
        return None
    word = next((w for w in DONE_WORDS if w in got[0]), None)
    ago = now - got[1]
    return (word, ago) if word and 0 <= ago < quiet else None


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
        done = said_done(event, now) if kind in DONE_KINDS else None
        if done:
            return f"quiet: the session said {done[0]} {done[1] / 60:.0f} minutes ago; a wait for input is not said for {DONE_QUIET_S // 60} minutes after"
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


def is_workflow(commit):
    """True for a commit a scheduled workflow wrote (github-actions[bot]): the daily run's metadata, not the chain's work."""
    author = commit.get("author") or {}
    return str(author.get("name") or "") in BOTS or "[bot]@" in str(author.get("email") or "")


def landing(commit):
    """The task/ branch a commit landed on main, or None: the workflow's merge of the chain's own push
    (.github/workflows/code-branch.yml: "Merge task/x: checks passed", or GitHub's "Merge pull request #n from owner/task/x")."""
    head = str(commit.get("messageHeadline") or "")
    if head.startswith("Merge task/"):
        return head.split()[1].rstrip(":")
    if head.startswith("Merge pull request #") and "/task/" in head:
        return "task/" + head.split("/task/", 1)[1].split()[0]
    return None


def newest_save(token=None, repo=REPO, post=http_post):
    """The newest commit on any branch on GitHub that is the chain's: (time, branch, headline), or None when there is none.

    Every branch is read, main included (session 116: only wip/ and task/ were, so a landing, which leaves its commits
    on main and deletes the task branch, read as silence). A commit a scheduled workflow wrote is not the chain's and
    is passed over; the workflow's merge of a task/ branch is the chain's landing and counts."""
    token = token or env("GH_TOKEN") or env("GITHUB_TOKEN")
    if not token:
        raise RuntimeError("GH_TOKEN (or GITHUB_TOKEN) is not set")
    owner, name = repo.split("/")
    q = (f'query {{ repository(owner: "{owner}", name: "{name}") {{ refs(refPrefix: "refs/heads/", first: {REFS}, orderBy: {{field: TAG_COMMIT_DATE, direction: DESC}}) '
         f"{{ nodes {{ name target {{ ... on Commit {{ history(first: {COMMITS}) {{ nodes {{ committedDate messageHeadline author {{ name email }} }} }} }} }} }} }} }} }}")
    r = post("https://api.github.com/graphql", json={"query": q}, timeout=30, headers={"Authorization": f"Bearer {token}"})
    if r.status_code != 200 or "errors" in r.json():
        raise RuntimeError(f"GitHub: HTTP {r.status_code} {str(r.json().get('errors') if r.status_code == 200 else r.text)[:200]}")
    best = None
    for ref in r.json()["data"]["repository"]["refs"]["nodes"]:
        for c in (((ref.get("target") or {}).get("history") or {}).get("nodes") or []):
            t = parse(c.get("committedDate"))
            if not t or (is_workflow(c) and not landing(c)):
                continue
            # a commit on several branches (a wip/ copy and main) is named by the first branch that shows it
            if best is None or t > best[0]:
                best = (t, ref["name"], c.get("messageHeadline") or "")
    return best


newest_push = newest_save  # the name it had while only wip/ and task/ branches were read (session 91)


def save_words(save):
    """How the line names a save read from GitHub: (time, branch, headline) as newest_save gives it."""
    if save[1] != "main":
        return f"a push to {save[1]}"
    task = landing({"messageHeadline": save[2] if len(save) > 2 else ""})
    return f"the landing of {task} on main" if task else "a commit on main"


def last_save(m, push):
    """(when, what) of a marked chain's newest save: its start, a beat, or the newest save GitHub shows."""
    saves = [(m["acquired"], "its start")]
    if m.get("renewed") and m["renewed"] > m["acquired"]:
        saves.append((m["renewed"], "a beat"))
    if push:
        saves.append((push[0], save_words(push)))
    return max(saves, key=lambda s: s[0])


def chain_key(now, m, push):
    """What the memory holds for the line decide() would send now: the lapse of this mark, or this silence (named by
    the save it began at, so that a later save makes a later silence a new one)."""
    if m["expires"] < now:
        return f"lapsed|chain|{m['holder']}|{m['expires']:%Y-%m-%dT%H:%M}"
    return f"quiet|chain|{m['holder']}|{last_save(m, push)[0]:%Y-%m-%dT%H:%M}"


def decide(now, m, push, memory=None):
    """What the check says: (subject, line) to send, or (None, why it stays quiet). `m` is the mark, `push` the newest
    save on GitHub as newest_save gives it, `memory` the keys already said (told()), or None when that cannot be read:
    the line is then due only in the quarter of an hour after the silence passed 30 minutes, as before session 202."""
    if m is None:
        return None, "no chain is marked as running"
    name = one_line(m.get("task") or "unnamed", 80)
    hm = lambda t: t.strftime("%H:%M")  # noqa: E731
    key = chain_key(now, m, push)
    if m["expires"] < now:
        late = (now - m["expires"]).total_seconds() / 60
        if late < LAPSE_HOURS * 60 and due(late, 0, key, memory):
            return ("ERW: a chain's mark lapsed", one_line(
                f"The chain \"{name}\" ({m['holder']}) was marked as running until {hm(m['expires'])} UTC and was never marked done: "
                "it ran past its time or stopped without saying so."))
        return None, f"the mark of \"{name}\" lapsed {late:.0f} minutes ago; already said"
    last, what = last_save(m, push)
    quiet = (now - last).total_seconds() / 60
    if quiet < QUIET_MIN:
        return None, f"\"{name}\" saved {quiet:.0f} minutes ago ({what}, {hm(last)} UTC)"
    if not due(quiet, QUIET_MIN, key, memory):
        return None, f"\"{name}\" has saved nothing for {quiet:.0f} minutes; said once, and not again for this silence"
    return ("ERW: a chain has saved nothing for 30 minutes", one_line(
        f"The chain \"{name}\" ({m['holder']}) has saved nothing for {quiet:.0f} minutes: its last save was {what} at {hm(last)} UTC. "
        f"Marked as running since {hm(m['acquired'])} UTC. Said once: no further email for this silence."))


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
    push = newest_save() if m else None
    made = decide(now, m, push, told(now) if m else None)
    if a.action == "status":
        print("no chain is marked as running" if m is None else
              f"\"{m['task']}\" by {m['holder']}, since {m['acquired']:%Y-%m-%d %H:%M} UTC, until {m['expires']:%Y-%m-%d %H:%M} UTC"
              + (f"; newest save on GitHub {push[0]:%H:%M} UTC, {save_words(push)}" if push else "; no commit of the chain's found on GitHub"))
        print("the check would send: " + made[1] if made[0] else "the check would stay quiet: " + made[1])
        return 0
    if made[0] is None:  # check
        print(f"quiet: {made[1]}")
        return 0
    n = send(made[0], made[1], dry_run=a.dry_run)
    if not a.dry_run:
        say("chain watch", chain_key(now, m, push))
        print(f"alert: {made[1]} (sent to {n} fixed recipient{'s' if n != 1 else ''})")
    return 0


# ---------------------------------------------------------------------------------------------------------------------
# the one alert policy (session 202): what was already said, a new failure, the morning summary

UTC = dt.timezone.utc
CAP_MARK = "daily model cap"  # warehouse/health.py's own words for a step the daily model cap skipped
EXPECT = ("latest prices", "hourly network", "daily prices", "chain watch")  # the jobs that run every day (warehouse/health.py, EXPECTED)
OWN_ALERT = ("energy roundup",)  # jobs whose own last step tells a failed run (warehouse/health.py alert): not told here a second time
DAYS_FILE = os.path.join(ROOT, "site", "data", "health_days.json")  # warehouse/health.py writes it; the streak is read from it
GREEN, RED, OPEN = "green", "red", "open"


def http_get(url, headers=None, timeout=30):
    """requests.get's shape (status_code, text, json()) on the standard library."""
    req = urllib.request.Request(url, method="GET", headers={"User-Agent": "erw-alert/1", **(headers or {})})
    try:
        with urllib.request.urlopen(req, timeout=timeout) as r:
            status, text = r.status, r.read().decode("utf-8", "replace")
    except urllib.error.HTTPError as e:
        status, text = e.code, e.read().decode("utf-8", "replace")
    return types.SimpleNamespace(status_code=status, text=text, json=lambda: json.loads(text or "null"))


def iso(t):
    return t.astimezone(UTC).strftime("%Y-%m-%dT%H:%M:%SZ")


def health_api(env=env):
    """(the address of erw_health, the headers) with the service key, the only key the table answers."""
    url, key = env("SUPABASE_URL"), env("SUPABASE_SERVICE_KEY")
    if not url or not key:
        raise RuntimeError("SUPABASE_URL or SUPABASE_SERVICE_KEY is not set")
    u = urllib.parse.urlparse(url)
    return f"{u.scheme}://{u.netloc}/rest/v1/erw_health", {"apikey": key, "Authorization": f"Bearer {key}"}


def health_rows(query, get=http_get, env=env, limit=6000):
    """Rows of erw_health for a PostgREST query, a list of (name, value) pairs. A thousand at a time, up to `limit`."""
    url, headers = health_api(env)
    out, start = [], 0
    while True:
        r = get(url + "?" + urllib.parse.urlencode(query), headers={**headers, "Range-Unit": "items", "Range": f"{start}-{start + 999}"}, timeout=40)
        if r.status_code not in (200, 206):
            raise RuntimeError(f"erw_health: HTTP {r.status_code} {r.text[:160]}")
        batch = r.json() or []
        out += batch
        if len(batch) < 1000 or len(out) >= limit:
            return out
        start += 1000


def in_a_test(transport, own):
    """True when a test suite is loaded and the caller did not hand in a transport of its own. The memory is a table of
    the live database: a test that forgets to stand in for it must neither read nor write it (session 202: five such
    rows were written from a test run on the machine that holds the service key, before this was here)."""
    return transport is own and "unittest" in sys.modules and os.environ.get("ERW_ALERT_MEMORY") != "live"


def told(now, get=http_get, env=env):
    """The keys of the lines already sent in the last MEMORY_HOURS hours, as a set; None when the memory cannot be read
    (no key, the database did not answer). A caller then falls back to the quarter-hour window, which never repeats."""
    if in_a_test(get, http_get):
        return None
    try:
        rows = health_rows([("select", "reason"), ("workflow", f"eq.{MEMORY}"), ("at", f"gte.{iso(now - dt.timedelta(hours=MEMORY_HOURS))}")], get, env)
        return {r.get("reason") or "" for r in rows}
    except Exception:
        return None


def say(kind, key, post=http_post, env=env):
    """Remember that a line was sent: one row of erw_health, workflow "alerts", the key as its reason. Never raises;
    False when the row was not written (the line may then be said once more by the next check)."""
    if in_a_test(post, http_post):
        return False
    try:
        url, headers = health_api(env)
        r = post(url, headers={**headers, "Prefer": "return=minimal"}, timeout=30,
                 json={"workflow": MEMORY, "run_id": os.environ.get("GITHUB_RUN_ID"), "step": kind, "status": "ok", "reason": str(key)[:500]})
        return r.status_code < 300
    except Exception:
        return False


def due(quiet, threshold, key, memory):
    """Whether a line is due: the silence (minutes) has passed the threshold and the line was not sent before. Without
    the memory it is due only in the first quarter of an hour past the threshold: one run of the check, so one line."""
    if quiet < threshold:
        return False
    if memory is None:
        return quiet < threshold + EVERY_MIN
    return key not in memory


def failure_key(row):
    return f"failed|{row['workflow']}|{row['step']}|{str(row['at'])[:16]}"


def previous_failed(row, get=http_get, env=env):
    """Whether the step's outcome before this row (skips left out) was a failure too: the same failure, still there."""
    prev = health_rows([("select", "at,status"), ("workflow", f"eq.{row['workflow']}"), ("step", f"eq.{row['step']}"), ("status", "neq.skipped"),
                        ("at", f"lt.{row['at']}"), ("order", "at.desc"), ("limit", "1")], get, env)
    return bool(prev) and prev[0].get("status") == "failed"


def new_failures(now, minutes=60, memory=None, get=http_get, env=env, before=previous_failed):
    """The failures to tell now, as (key, row): each step recorded as failed in the last `minutes` whose run before
    did not fail and which was not told yet. A retry that passed is recorded as "retried", never as failed, so it is
    not here. Without the memory only the last quarter of an hour is read."""
    since = now - dt.timedelta(minutes=minutes if memory is not None else EVERY_MIN)
    rows = health_rows([("select", "at,workflow,run_id,step,status,reason"), ("status", "eq.failed"), ("workflow", f"neq.{MEMORY}"),
                        ("at", f"gte.{iso(since)}"), ("order", "at")], get, env)
    out = []
    for r in rows:
        key = failure_key(r)
        if r["workflow"] in OWN_ALERT or (memory is not None and key in memory):
            continue
        if before(r, get, env):
            continue
        out.append((key, r))
    return out


def cap_skips(now, minutes=60, memory=None, get=http_get, env=env):
    """(key, rows) for the steps the daily model cap skipped (session 176), told once a UTC day; None when there is
    nothing to tell."""
    since = now - dt.timedelta(minutes=minutes if memory is not None else EVERY_MIN)
    rows = health_rows([("select", "at,workflow,step,reason"), ("status", "eq.skipped"), ("reason", f"like.{CAP_MARK}*"), ("at", f"gte.{iso(since)}"),
                        ("order", "at")], get, env)
    key = f"cap|{now:%Y-%m-%d}"
    if not rows or (memory is not None and key in memory):
        return None
    return key, rows


def failure_line(row):
    at = parse(row["at"])
    run = f" (run {row['run_id']})" if row.get("run_id") else ""
    reason = " ".join(str(row.get("reason") or "no reason recorded").split())
    tail = " Said once: while it keeps failing it is a red line of the morning summary."
    head = f"{row['step']} of {row['workflow']} failed at {at:%H:%M} UTC{run}: "
    return (one_line(f"ERW: {row['step']} failed ({row['workflow']})", 120),
            one_line(head + one_line(reason, max(40, MAX_LINE - len(head) - len(tail))).rstrip(".") + "." + tail))


def failures(minutes=60, dry_run=False, now=None, get=http_get, post=http_post, env=env, send=None):
    """The scheduled check: one email for each new failure (more than MANY at once: one for all of them), and one a
    day for the steps the model cap skipped. Returns 0 when there was nothing to say or a line went out, 1 when every
    line that was due could not be sent."""
    now = now or dt.datetime.now(UTC)
    send = send or (lambda subject, line, dry: globals()["send"](subject, line, dry, post=post, env=env))
    memory = told(now, get, env)
    new = new_failures(now, minutes, memory, get, env)
    cap = cap_skips(now, minutes, memory, get, env)
    if not new and not cap:
        print(f"quiet: no step newly failed in the last {minutes if memory is not None else EVERY_MIN} minutes"
              + ("" if memory is not None else " (the memory could not be read: the last quarter of an hour only)"))
        return 0
    mails = []  # (subject, line, [keys])
    if len(new) > MANY:
        names = ", ".join(dict.fromkeys(f"{r['step']} ({r['workflow']})" for _, r in new))
        mails.append((f"ERW: {len(new)} scheduled steps failed",
                      one_line(f"{len(new)} steps newly failed since {parse(new[0][1]['at']):%H:%M} UTC: {names}"), [k for k, _ in new]))
    else:
        mails += [(*failure_line(r), [k]) for k, r in new]
    if cap:
        steps = ", ".join(dict.fromkeys(r["step"] for r in cap[1]))
        said = str(cap[1][0].get("reason") or "")[len(CAP_MARK):].split(";")[0].strip()
        mails.append((f"ERW: the daily model cap skipped {len(cap[1])} step{'s' if len(cap[1]) != 1 else ''}",
                      one_line(f"The {CAP_MARK} {said}: not run today: {steps}."), [cap[0]]))
    sent = 0
    for subject, line, keys in mails:
        try:
            n = send(subject, line, dry_run)
            if not dry_run:
                for k in keys:
                    say("failure", k, post, env)
                print(f"alert: {line} (sent to {n} fixed recipient{'s' if n != 1 else ''})")
            sent += 1
        except Exception as exc:  # one line must not cost another
            print(f"alert: not sent ({type(exc).__name__}: {str(exc)[:160]}): {line}")
    return 0 if sent else 1


def pacific(now):
    """`now` on the Pacific clock. From the time-zone table when the machine has one; otherwise by the United States
    rule since 2007 (daylight time from the second Sunday of March to the first Sunday of November)."""
    try:
        import zoneinfo
        return now.astimezone(zoneinfo.ZoneInfo("America/Los_Angeles"))
    except Exception:
        def sunday(month, n):
            first = dt.date(now.year, month, 1)
            return first + dt.timedelta(days=(6 - first.weekday()) % 7 + 7 * (n - 1))
        start = dt.datetime.combine(sunday(3, 2), dt.time(10), UTC)   # 02:00 Pacific standard time
        end = dt.datetime.combine(sunday(11, 1), dt.time(9), UTC)     # 02:00 Pacific daylight time
        return now.astimezone(dt.timezone(dt.timedelta(hours=-7 if start <= now < end else -8)))


def morning(now):
    """The newest 07:00 Pacific at or before `now`, as a Pacific datetime."""
    p = pacific(now)
    m = p.replace(hour=SUMMARY_HOUR, minute=0, second=0, microsecond=0)
    return m if p >= m else m - dt.timedelta(days=1)


def landings(since, get=http_get, env=env):
    """The runs of the "code branch" workflow created since `since`, newest first: [{branch, conclusion, id, at}]. A
    landing is a task/ branch whose checks passed (the workflow then merges it). None when GitHub could not be read."""
    token = env("GH_TOKEN") or env("GITHUB_TOKEN")
    if not token:
        return None
    q = urllib.parse.urlencode({"created": f">={iso(since)}", "per_page": "100"})
    try:
        r = get(f"https://api.github.com/repos/{REPO}/actions/workflows/code-branch.yml/runs?{q}", timeout=40,
                headers={"Authorization": f"Bearer {token}", "Accept": "application/vnd.github+json"})
        if r.status_code != 200:
            return None
        return [{"branch": w.get("head_branch") or "", "conclusion": w.get("conclusion") or w.get("status") or "", "id": w.get("id"),
                 "at": parse(w.get("created_at"))} for w in (r.json() or {}).get("workflow_runs", [])]
    except Exception:
        return None


def streak_words(path=None):
    """The line of the green streak, from the file warehouse/health.py writes; "" when the file is not there."""
    try:
        with open(path or DAYS_FILE, encoding="utf-8") as f:
            d = json.load(f)
        n, to = int(d["green_days"]), d.get("counted_to") or "no day"
        return f"Scheduled jobs green for {n} day{'s' if n != 1 else ''} (counted to {to}, UTC)."
    except (OSError, ValueError, KeyError, TypeError):
        return ""


def summary_lines(rows, runs):
    """The morning summary's lines, (color, text), red first: one for each scheduled job, one for each machine that
    recorded a step, one for each landing. `rows` are erw_health's of the window, `runs` landings() or None."""
    by = {}
    for r in rows:
        if r.get("workflow") != MEMORY:
            by.setdefault(r["workflow"], []).append(r)
    out = []
    for wf in sorted(set(by) | set(EXPECT)):
        rs = by.get(wf, [])
        local = wf.startswith("local:")
        name = f"machine {wf[6:]}" if local else wf
        if not rs:
            out.append((RED, f"{name}: no run recorded"))
            continue
        n = len({r["run_id"] for r in rs if r.get("run_id")}) or len(rs)
        unit = "step" if local else "run"
        count = f"{n} {unit}{'s' if n != 1 else ''}"
        fails = [r for r in rs if r["status"] == "failed"]
        retried = sum(1 for r in rs if r["status"] == "retried")
        if fails:
            steps = list(dict.fromkeys(r["step"] for r in fails))
            first = {s: next(" ".join(str(r.get("reason") or "").split()) for r in fails if r["step"] == s) for s in steps[:3]}
            what = "; ".join(f"{s} ({one_line(first[s], 70)})" if first[s] else s for s in steps[:3])
            more = f"; and {len(steps) - 3} more" if len(steps) > 3 else ""
            out.append((RED, one_line(f"{name}: {len(fails)} failed in {count}: {what}{more}", 400)))
        else:
            last = max(rs, key=lambda r: str(r["at"]))
            tail = f"; last: {last['step']} at {parse(last['at']):%H:%M} UTC" if local else (f"; {retried} passed at the second try" if retried else "")
            out.append((GREEN, f"{name}: {count}, no failure{tail}"))
    if runs is None:
        out.append((OPEN, "landings: GitHub could not be read from here"))
    else:
        seen = set()
        for w in runs:  # newest first: one line a branch, its newest run
            if w["branch"] in seen or not w["branch"]:
                continue
            seen.add(w["branch"])
            if w["conclusion"] == "success":
                out.append((GREEN, f"{w['branch']}: checks passed" + (", merged into main" if w["branch"].startswith("task/") else "")))
            elif w["conclusion"] in ("failure", "cancelled", "timed_out", "startup_failure"):
                out.append((RED, f"{w['branch']}: checks {w['conclusion']} (run {w['id']}), not merged"))
            else:
                out.append((OPEN, f"{w['branch']}: checks {w['conclusion'] or 'not finished'}"))
    order = {RED: 0, OPEN: 1, GREEN: 2}
    return sorted(out, key=lambda x: order[x[0]])


def summary_mail(now, lines, streak=""):
    """(subject, text, html) of the morning summary."""
    m = morning(now)
    start, day = m - dt.timedelta(days=1) if now - m.astimezone(UTC) < dt.timedelta(hours=12) else m, m.date()
    g, r = sum(1 for c, _ in lines if c == GREEN), sum(1 for c, _ in lines if c == RED)
    title = f"ERW morning summary, {day.day} {day:%B %Y}"
    subject = f"{title}: {g} green, {r} red"
    span = f"The runs from {start.astimezone(UTC):%d %B %H:%M} to {now:%d %B %H:%M} UTC, one line each. A success sends no other email."
    text = "\n".join([title, "", span] + ([streak] if streak else []) + [""] + [f"{c:<5}  {t}" for c, t in lines]) + "\n"
    esc = lambda s: str(s).replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")  # noqa: E731
    color = {GREEN: "#175E54", RED: "#8C1515", OPEN: "#6B665E"}
    trs = "".join(
        f'<tr><td style="padding:4px 10px 4px 0;white-space:nowrap;vertical-align:top;color:{color[c]};font-weight:600">'
        f'<span style="display:inline-block;width:9px;height:9px;background:{color[c]};margin-right:6px"></span>{c}</td>'
        f'<td style="padding:4px 0;border-bottom:1px solid #E3DED1">{esc(t)}</td></tr>' for c, t in lines)
    html = (f'<!doctype html><html lang="en"><head><meta charset="utf-8"><title>{esc(title)}</title></head>'
            f'<body style="margin:0;padding:20px;background:#FFFFFF;color:#2E2D29;font-family:Arial,Helvetica,sans-serif;font-size:14px;line-height:1.45">'
            f'<h1 style="font-size:20px;font-weight:600;margin:0 0 6px 0">{esc(title)}</h1>'
            f'<p style="margin:0 0 4px 0;color:#6B665E">{esc(span)}</p>'
            + (f'<p style="margin:0 0 12px 0"><strong>{esc(streak)}</strong></p>' if streak else '<p style="margin:0 0 12px 0"></p>')
            + f'<p style="margin:0 0 8px 0">{g} green, {r} red.</p>'
            f'<table style="border-collapse:collapse;width:100%;max-width:760px">{trs}</table>'
            f'<p style="margin:14px 0 0 0;color:#6B665E;font-size:12px">Written by scripts/alert.py summary from the table erw_health and '
            f'GitHub\'s record of the code branch checks. To the fixed recipients only.</p></body></html>')
    return subject, text, html


def summary(dry_run=False, html_path=None, force=False, now=None, get=http_get, post=http_post, env=env):
    """The morning summary: sent by the first check at or after 07:00 Pacific, once a day. Returns 0 when it was sent,
    was not due, or was printed; 1 when it was due and could not be read or sent."""
    now = now or dt.datetime.now(UTC)
    p = pacific(now)
    key = f"summary|{p:%Y-%m-%d}"
    if not dry_run and not force:
        if p.hour < SUMMARY_HOUR:
            print(f"quiet: it is {p:%H:%M} Pacific; the morning summary goes out at {SUMMARY_HOUR:02d}:00")
            return 0
        memory = told(now, get, env)
        if memory is None and not (p.hour == SUMMARY_HOUR and p.minute < EVERY_MIN):
            print("quiet: the memory could not be read, and the first quarter of an hour after 07:00 Pacific has passed")
            return 0
        if memory is not None and key in memory:
            print(f"quiet: the morning summary of {p:%Y-%m-%d} was sent")
            return 0
    m = morning(now)
    since = (m - dt.timedelta(days=1) if now - m.astimezone(UTC) < dt.timedelta(hours=12) else m).astimezone(UTC)
    rows = health_rows([("select", "at,workflow,run_id,step,status,reason"), ("at", f"gte.{iso(since)}"), ("order", "at")], get, env)
    subject, text, html = summary_mail(now, summary_lines(rows, landings(since, get, env)), streak_words())
    if html_path:
        os.makedirs(os.path.dirname(os.path.abspath(html_path)), exist_ok=True)
        with open(html_path, "w", encoding="utf-8", newline="\n") as f:
            f.write(html)
    if dry_run:
        print(f"Subject: {subject}\n\n{text}")
        return 0
    n = deliver(subject, text, html, post=post, env=env)
    say("morning summary", key, post, env)
    print(f"summary: \"{subject}\" sent to {n} fixed recipient{'s' if n != 1 else ''}")
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
    f = sub.add_parser("failures", help="one email for each step newly recorded as failed (the scheduled check)")
    f.add_argument("--minutes", type=int, default=60, help="how far back a failed row is looked for (default 60)")
    f.add_argument("--dry-run", action="store_true")
    m = sub.add_parser("summary", help="the morning summary: the runs since the last morning, one line each")
    m.add_argument("--dry-run", action="store_true", help="print the summary, send nothing, remember nothing")
    m.add_argument("--html", help="also write the email's HTML body to this file")
    m.add_argument("--force", action="store_true", help="whatever the hour, and whether or not today's was sent")
    a = ap.parse_args(argv)
    if a.cmd == "hook":
        hook()  # what it did is not printed: a hook's output may be shown to the session
        return 0
    try:
        if a.cmd == "chain":
            return chain(a)
        if a.cmd == "failures":
            return failures(a.minutes, a.dry_run)
        if a.cmd == "summary":
            return summary(a.dry_run, a.html, a.force)
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

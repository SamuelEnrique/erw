#!/usr/bin/env python3
"""The health of scheduled jobs (session 61): skips are successes with a reason, real failures retry once and are
recorded, and one daily summary says what happened. Nothing here makes a GitHub job fail, so GitHub never emails.

Energy Research Warehouse (ERW). docs/machines.md, "The schedule". Needs only requests (the hourly job installs nothing
else); SUPABASE_URL and SUPABASE_SERVICE_KEY from the environment or .env.

    python warehouse/health.py run --step "latest prices" -- python warehouse/connectors/latest_prices.py
        runs the command with ERW_SKIP_EXIT=75 set. Exit 0: ok. Exit 75: the command decided it should not run (the data
        lock is held, the day's work is done, the source has nothing new): skipped, its last line the reason. Any other
        exit: wait a minute and run it once more; then retried (passed the second time) or failed. Every outcome is a
        row of the Supabase table erw_health (migration 017) and status=<outcome> in GITHUB_OUTPUT; the exit is 0.
    python warehouse/health.py record --step "daily run" --status skipped --reason "..."
    python warehouse/health.py dedupe --workflow-file latest-prices.yml --minutes 15
        skip=1 in GITHUB_OUTPUT (and a skipped row) for a duplicate start: GitHub's own schedule and the database's
        (migration 015, a workflow_dispatch) both start the scheduled jobs, and GitHub's runs late. The database is the
        schedule: a run GitHub's schedule started is skipped when a dispatched run started in the last N minutes (the job's
        interval); a dispatched run is skipped only when another dispatched run started in the last 5 minutes.
    python warehouse/health.py summary [--day 2026-10-02 | yesterday]
        writes queue/summary/<day>-health.md from erw_health: per workflow, runs against the expected count, and every
        skip reason, retry and failure.
    python warehouse/health.py alert [--run-id 37207629600] [--day today] [--dry-run]
        session 119: one line by email, to the fixed recipients only, when a step of this run (or of the day) is
        recorded as failed; nothing when none is. No job fails on GitHub, so GitHub sends no email, and the summary
        above is written the day after: on 4 October 2026 the battery page's refresh failed at 14:45 UTC and a person
        learned of it from a document a session wrote that evening. Never raises and always exits 0.
    python warehouse/health.py budget --step news_score
        session 176: the daily cap for all scheduled model steps together, DAILY_MODEL_USD (default 1.00). Sums the
        day's (UTC) spend of the scheduled model steps from the cost ledger (warehouse/output/api_cost_ledger.csv on
        this machine, and Supabase's copy of it for the rows another runner wrote today). Under the cap: exit 0, and
        the step runs. At or over it: the step is not run; a row of erw_health says so (status skipped, its reason
        beginning "daily model cap"), a warning is printed, the same-day email (alert, above) carries it, and the exit
        is 75. warehouse/run_daily.sh asks before each model step; the digest and the Roundup are then written with
        --no-model (without the model-written parts) and still publish. A budget that cannot be read never switches a
        step off: the step runs, and a failed row of erw_health says the budget could not be read.
"""

import argparse
import csv
import datetime as dt
import os
import subprocess
import sys
import time
import urllib.parse

import requests

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.abspath(os.path.join(HERE, ".."))
SKIP = 75
TABLE = "erw_health"
EXPECTED = {  # runs a day, as migration 015 schedules them (the weekly jobs on Sundays)
    "latest prices": 96, "hourly network": 23, "daily prices": 1, "energy roundup": 0, "weekly vacuum": 0,
    "chain watch": 96,  # session 91: every 15 minutes, whether or not a chain is marked (migration 022)
}
# Session 176: the daily cap for all scheduled model steps together (docs/methods/api_cost_ledger.md, "The daily cap").
MODEL_CAP_DEFAULT = 1.00  # USD a UTC day; DAILY_MODEL_USD in the environment replaces it
CAP_MARK = "daily model cap"  # a capped step's reason begins with it: the summary and the same-day email read it
LEDGER = "api_cost_ledger"
# The ledger's step names of the model steps that run on a clock (warehouse/run_daily.sh and roundup.yml). A call of
# any other step (a session's work, the Thesis Builder, the site's own ledger) is not counted and not capped here.
SCHEDULED_MODEL_STEPS = ("news_score", "news_score_shadow", "policy_score", "policy_reads", "deals_extract",
                         "datacenters_extract", "funfact", "digest", "roundup", "analysis_note")


def env(name):
    v = os.environ.get(name)
    if not v and os.path.exists(os.path.join(ROOT, ".env")):
        try:
            from dotenv import dotenv_values
            v = dotenv_values(os.path.join(ROOT, ".env")).get(name)
        except ImportError:
            v = None
    return (v or "").strip()


def rest():
    u = urllib.parse.urlparse(env("SUPABASE_URL"))
    key = env("SUPABASE_SERVICE_KEY")
    if not u.netloc or not key:
        return None, None
    return f"{u.scheme}://{u.netloc}/rest/v1/{TABLE}", {"apikey": key, "Authorization": f"Bearer {key}", "Content-Type": "application/json"}


def workflow():
    return os.environ.get("GITHUB_WORKFLOW") or f"local:{os.environ.get('COMPUTERNAME') or os.environ.get('HOSTNAME') or 'machine'}"


def record(step, status, reason="", seconds=None, wf=None, post=requests.post):
    """One row of erw_health. A failure to record is a warning, never an error: the job's own log still says it."""
    url, headers = rest()
    row = {"workflow": wf or workflow(), "run_id": os.environ.get("GITHUB_RUN_ID"), "step": step, "status": status,
           "reason": (reason or "")[:500], "seconds": round(seconds, 1) if seconds is not None else None}
    if url is None:
        print(f"::warning::health not recorded (no SUPABASE_URL or SUPABASE_SERVICE_KEY): {row}")
        return False
    try:
        r = post(url, json=row, headers={**headers, "Prefer": "return=minimal"}, timeout=30)
        if r.status_code >= 300:
            print(f"::warning::health not recorded: HTTP {r.status_code} {r.text[:150]}")
            return False
    except requests.RequestException as exc:
        print(f"::warning::health not recorded: {type(exc).__name__}")
        return False
    return True


def output(**kv):
    path = os.environ.get("GITHUB_OUTPUT")
    if path:
        with open(path, "a", encoding="utf-8") as f:
            for k, v in kv.items():
                f.write(f"{k}={v}\n")


def reason_of(lines, failed):
    """The line that says why: for a failure the last line naming an error, else the last line written."""
    lines = [ln.strip() for ln in lines if ln.strip()]
    if failed:
        hits = [ln for ln in lines if any(w in ln for w in ("FAILED", "Error", "error", "refused", "Traceback"))]
        if hits:
            return hits[-1][:400]
    return lines[-1][:400] if lines else ""


def attempt(cmd):
    """Run once, streaming the output and keeping its last lines. (exit code, last lines, seconds)."""
    t0 = time.time()
    p = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True, encoding="utf-8", errors="replace",
                         env={**os.environ, "ERW_SKIP_EXIT": str(SKIP)}, cwd=ROOT)
    tail = []
    for line in p.stdout:
        sys.stdout.write(line)
        tail = (tail + [line.rstrip("\n")])[-60:]
    sys.stdout.flush()
    return p.wait(), tail, time.time() - t0


def run(step, cmd, retries=1, wait=60, strict=False, attempt=attempt, sleep=time.sleep, rec=record):
    """Run a scheduled step; returns its outcome (ok, skipped, retried, failed). See the module's docstring."""
    code, tail, secs = attempt(cmd)
    first = None
    tries = 0
    while code not in (0, SKIP) and tries < retries:
        first = reason_of(tail, True)
        tries += 1
        print(f"::notice::{step}: failed ({first}); one more try in {wait} s")
        sleep(wait)
        code, tail, more = attempt(cmd)
        secs += more
    if code == 0:
        status, why = ("retried", f"failed once, then passed: {first}") if first else ("ok", "")
    elif code == SKIP:
        status, why = "skipped", reason_of(tail, False)
        print(f"::notice::{step} skipped: {why}")
    else:
        status, why = "failed", reason_of(tail, True)
        print(f"::warning title={step} failed{' after a retry' if retries else ''}::{why}")
    rec(step, status, why, secs)
    output(status=status)
    return 1 if (strict and status == "failed") else 0, status


def model_cap():
    """DAILY_MODEL_USD as a number; unset, empty or unreadable gives the default (a value that cannot be read is said)."""
    raw = env("DAILY_MODEL_USD")
    if not raw:
        return MODEL_CAP_DEFAULT
    try:
        v = float(raw)
        if v < 0:
            raise ValueError(raw)
        return v
    except ValueError:
        print(f"::warning::DAILY_MODEL_USD={raw!r} is not a number of dollars; the default USD {MODEL_CAP_DEFAULT:.2f} is used")
        return MODEL_CAP_DEFAULT


def ledger_session():
    """The session name warehouse/llm.py writes for this process: ERW_SESSION, else daily on GitHub and local elsewhere."""
    s = os.environ.get("ERW_SESSION", "").strip()
    return s or ("daily" if os.environ.get("GITHUB_ACTIONS") == "true" else "local")


def ledger_local(day, path=None):
    """{event_id: (step, session, usd)} of the day's rows of the ledger on this machine; an absent file is no rows."""
    path = path or os.path.join(ROOT, "warehouse", "output", LEDGER + ".csv")
    if not os.path.exists(path):
        return {}
    out = {}
    with open(path, encoding="utf-8", newline="") as f:
        for r in csv.DictReader(ln for ln in f if not ln.startswith("#")):
            if (r.get("ts_utc") or r.get("event_date") or "")[:10] == day:
                out[r["event_id"]] = (r.get("step", ""), r.get("session", ""), float(r.get("usd") or 0))
    return out


def ledger_remote(day, get=requests.get):
    """The same from Supabase's copy (public.events, table_name api_cost_ledger): the rows another runner wrote today
    and the loader carried. No keys or no answer is no rows, with a notice: the local file is then the whole count."""
    u = urllib.parse.urlparse(env("SUPABASE_URL"))
    key = env("SUPABASE_SERVICE_KEY")
    if not u.netloc or not key:
        return {}
    d1 = (dt.date.fromisoformat(day) + dt.timedelta(days=1)).isoformat()
    out, start = {}, 0
    while True:
        r = get(f"{u.scheme}://{u.netloc}/rest/v1/events", timeout=40,
                headers={"apikey": key, "Authorization": f"Bearer {key}", "Range-Unit": "items", "Range": f"{start}-{start + 999}"},
                params={"select": "event_id,extra", "table_name": f"eq.{LEDGER}",
                        "and": f"(event_date.gte.{day}T00:00:00Z,event_date.lt.{d1}T00:00:00Z)"})
        if r.status_code >= 300:
            print(f"::notice::model budget: Supabase's copy of the ledger not read (HTTP {r.status_code}); this machine's file is the count")
            return out
        batch = r.json()
        for row in batch:
            x = row.get("extra") or {}
            out[row["event_id"]] = (x.get("step", ""), x.get("session", ""), float(x.get("usd") or 0))
        if len(batch) < 1000:
            return out
        start += 1000


def model_spend(day, session=None, path=None, get=requests.get):
    """(USD, calls) of the day's scheduled model steps: the union, by event_id, of the ledger on this machine and
    Supabase's copy, for this process's ledger session and the steps of SCHEDULED_MODEL_STEPS."""
    session = session or ledger_session()
    rows = ledger_local(day, path)
    try:
        for k, v in ledger_remote(day, get).items():
            rows.setdefault(k, v)
    except (requests.RequestException, ValueError, KeyError, TypeError) as exc:
        print(f"::notice::model budget: Supabase's copy of the ledger not read ({type(exc).__name__}); this machine's file is the count")
    mine = [usd for step, ses, usd in rows.values() if ses == session and step in SCHEDULED_MODEL_STEPS]
    return sum(mine), len(mine)


def budget(step, day=None, rec=record, spend=model_spend, cap=None):
    """Session 176: may a scheduled model step run? (exit code, line). 0: the day's spend is under DAILY_MODEL_USD.
    75: it has reached the cap; the step is not run, and a skipped row of erw_health, a warning and the same-day email
    say so. A budget that cannot be read is exit 0 with a failed row: it never switches a step off by itself."""
    day = day or dt.datetime.now(dt.timezone.utc).date().isoformat()
    cap = model_cap() if cap is None else cap
    try:
        spent, calls = spend(day)
    except Exception as exc:  # an unreadable ledger must not stop the news; it is said, and the step runs
        why = f"the model budget could not be read ({type(exc).__name__}: {str(exc)[:160]}); {step} runs uncapped"
        print(f"::warning title=model budget not read::{why}")
        rec("model budget", "failed", why, 0)
        return 0, why
    if spent >= cap:
        why = (f"{CAP_MARK} reached: USD {spent:.2f} spent today ({day} UTC, {calls} calls of the scheduled model steps) "
               f"of USD {cap:.2f} (DAILY_MODEL_USD); {step} not run")
        print(f"::warning title={step} skipped by the daily model cap::{why}")
        rec(step, "skipped", why, 0)
        return SKIP, why
    line = f"model budget: USD {spent:.2f} of {cap:.2f} spent today ({day} UTC, {calls} calls); {step} runs"
    print(line)
    return 0, line


def dedupe(workflow_file, minutes, rec=record, get=requests.get, dispatch_minutes=5):
    """skip=1 for a duplicate start (see the module's docstring). Only runs that are running, queued or succeeded count."""
    me = os.environ.get("GITHUB_RUN_ID")
    mine = os.environ.get("GITHUB_EVENT_NAME", "workflow_dispatch")
    repo, token = os.environ.get("GITHUB_REPOSITORY"), os.environ.get("GITHUB_TOKEN") or env("GH_TOKEN")
    if not (me and repo and token):
        output(skip=0)
        return False
    window = minutes if mine == "schedule" else dispatch_minutes
    since = (dt.datetime.now(dt.timezone.utc) - dt.timedelta(minutes=window)).strftime("%Y-%m-%dT%H:%M:%SZ")
    try:
        r = get(f"https://api.github.com/repos/{repo}/actions/workflows/{workflow_file}/runs",
                params={"created": f">={since}", "per_page": 50}, headers={"Authorization": f"Bearer {token}"}, timeout=30)
        runs = r.json().get("workflow_runs", []) if r.status_code == 200 else []
    except (requests.RequestException, ValueError):
        runs = []
    others = [x for x in runs if str(x["id"]) != str(me) and int(x["id"]) < int(me) and x.get("event") == "workflow_dispatch"
              and (x["status"] in ("in_progress", "queued") or x.get("conclusion") == "success")]
    if others:  # a run that was itself skipped as a duplicate did nothing, so it does not count
        others = [x for x in others if str(x["id"]) not in skipped_starts([str(x["id"]) for x in others], get)]
    if others:
        o = others[0]
        why = f"another run of {workflow_file} started at {o['created_at']} ({o['event']}, {o['status']}): this one is a duplicate"
        print(f"::notice::skipped: {why}")
        rec("start", "skipped", why, 0)
        output(skip=1)
        return True
    output(skip=0)
    return False


def skipped_starts(run_ids, get=requests.get):
    """The run ids among these whose start erw_health records as skipped (a duplicate that did nothing)."""
    url, headers = rest()
    if url is None or not run_ids:
        return set()
    try:
        r = get(url, headers=headers, params={"select": "run_id", "step": "eq.start", "status": "eq.skipped",
                                              "run_id": f"in.({','.join(run_ids)})"}, timeout=30)
        rows = r.json() if r.status_code == 200 else []
        return {str(x.get("run_id")) for x in rows if isinstance(x, dict)} if isinstance(rows, list) else set()
    except (requests.RequestException, ValueError):
        return set()


def fetch(day, get=requests.get):
    url, headers = rest()
    d0 = dt.datetime.fromisoformat(day).replace(tzinfo=dt.timezone.utc)
    d1 = d0 + dt.timedelta(days=1)
    rows, start = [], 0
    while True:
        r = get(url, headers={**headers, "Range-Unit": "items", "Range": f"{start}-{start + 999}"}, timeout=60,
                params={"select": "at,workflow,run_id,step,status,reason", "and": f"(at.gte.{d0.isoformat()},at.lt.{d1.isoformat()})", "order": "at"})
        r.raise_for_status()
        batch = r.json()
        rows += batch
        if len(batch) < 1000:
            return rows
        start += 1000


def render(day, rows):
    """The day's summary, Markdown."""
    weekday = dt.date.fromisoformat(day).weekday()
    expected = dict(EXPECTED, **({"energy roundup": 1, "weekly vacuum": 1} if weekday == 6 else {}))
    by = {}
    for r in rows:
        by.setdefault(r["workflow"], []).append(r)
    fails = [r for r in rows if r["status"] == "failed"]
    lines = [f"# Health of the scheduled jobs, {day} (UTC)", "",
             "Written by `warehouse/health.py summary` from the Supabase table erw_health (session 61). A skip is a run that should not have "
             "done anything (the data lock held, the day's work done, nothing new at the source, a duplicate start); a retry failed once "
             "and then passed; a failure failed twice. No job fails on GitHub for any of these, so this file is where they are read.", "",
             f"**{len(fails)} failure{'s' if len(fails) != 1 else ''}** over {len(rows)} recorded steps.", "",
             "| Workflow | Runs started | Expected | ok | skipped | retried | failed |", "|---|---|---|---|---|---|---|"]
    names = sorted(set(by) | {k for k, v in expected.items() if v})
    flags = []
    for w in names:
        rs = by.get(w, [])
        runs = len({r["run_id"] for r in rs if r.get("run_id")}) or len(rs)
        c = {s: sum(1 for r in rs if r["status"] == s) for s in ("ok", "skipped", "retried", "failed")}
        exp = expected.get(w)
        lines.append(f"| {w} | {runs} | {exp if exp is not None else ''} | {c['ok']} | {c['skipped']} | {c['retried']} | {c['failed']} |")
        if exp and runs < exp / 2:
            flags.append(f"- **{w}**: {runs} runs against {exp} expected: the schedule may have stopped (migration 015, "
                         "`python warehouse/supabase/scheduler.py --status`).")
    if flags:
        lines += ["", "## Fewer runs than scheduled", ""] + flags
    for status, title in (("failed", "Failures (failed twice)"), ("retried", "Retries (failed once, then passed)")):
        sel = [r for r in rows if r["status"] == status]
        if sel:
            lines += ["", f"## {title}", ""]
            lines += [f"- {r['at'][11:16]} UTC, {r['workflow']}, {r['step']} (run {r.get('run_id') or 'local'}): {r.get('reason') or ''}" for r in sel]
    sk = {}
    for r in rows:
        if r["status"] == "skipped":
            k = (r["workflow"], r["step"], (r.get("reason") or "")[:160])
            sk[k] = sk.get(k, 0) + 1
    if sk:
        lines += ["", "## Skips, by reason", ""]
        lines += [f"- {w}, {s}: {n} x {why}" for (w, s, why), n in sorted(sk.items(), key=lambda kv: -kv[1])]
    return "\n".join(lines) + "\n"


def summary(day, out_dir=None, rows=None):
    rows = fetch(day) if rows is None else rows
    out_dir = out_dir or os.path.join(ROOT, "queue", "summary")
    os.makedirs(out_dir, exist_ok=True)
    path = os.path.join(out_dir, f"{day}-health.md")
    with open(path, "w", encoding="utf-8", newline="\n") as f:
        f.write(render(day, rows))
    return path, rows


def alert_line(day, rows, run_id=None, workflow=None):
    """(subject, line) for the steps recorded as failed among `rows` (of one run when run_id is given), or None when
    none failed. The line names each step and the start of its reason, and stays within 300 characters."""
    mine = [r for r in rows if (not run_id or str(r.get("run_id") or "") == str(run_id)) and (not workflow or r["workflow"] == workflow)]
    fails = [r for r in mine if r["status"] == "failed"]
    # session 176: the steps the daily model cap skipped are told the same day too, after any failure
    capped = [r for r in mine if r["status"] == "skipped" and (r.get("reason") or "").startswith(CAP_MARK)]
    if capped:
        steps = ", ".join(dict.fromkeys(r["step"] for r in capped))
        m = [x for x in (r.get("reason") or "" for r in capped)][0]
        said = m[len(CAP_MARK):].split(";")[0].strip()  # "reached: USD 1.10 spent today (...) of USD 1.00 (DAILY_MODEL_USD)"
        tail = f"The {CAP_MARK} {said}: {len(capped)} model step{'s' if len(capped) != 1 else ''} not run ({steps})."
        if not fails:
            return f"ERW: the daily model cap skipped {len(capped)} step{'s' if len(capped) != 1 else ''}", tail[:300]
        subject, line = alert_line(day, [r for r in mine if r not in capped], run_id, workflow)
        return subject + f", the model cap skipped {len(capped)}", (line[:150] + " " + tail)[:300]
    if not fails:
        return None
    what = sorted({r["workflow"] for r in fails})
    head = (f"{len(fails)} step{'s' if len(fails) != 1 else ''} of {', '.join(what)} failed on {day} UTC"
            + (f" (run {run_id})" if run_id else "") + ": ")
    room = max(40, (300 - len(head)) // len(fails) - 4)
    parts = [" ".join(f"{r['step']}: {(r.get('reason') or 'no reason recorded')}".split())[:room] for r in fails]
    return f"ERW: {len(fails)} scheduled step{'s' if len(fails) != 1 else ''} failed", (head + "; ".join(parts))[:300]


def alert(day, run_id=None, dry_run=False, rows=None, send=None):
    """Sends the line when a step failed. Returns the number of failed steps told of (0: nothing sent)."""
    rows = fetch(day) if rows is None else rows
    got = alert_line(day, rows, run_id)
    if got is None:
        print(f"health alert: no failed step recorded{' for run ' + str(run_id) if run_id else ''} on {day}; nothing sent")
        return 0
    subject, line = got
    if send is None:
        sys.path.insert(0, os.path.join(ROOT, "scripts"))
        import alert as alert_mail  # the sender the digest uses: Resend, the fixed recipients only
        send = alert_mail.send
    send(subject, line, dry_run)
    print(f"health alert: {'would send' if dry_run else 'sent'}: {line}")
    return line.count(";") + 1


def main(argv=None):
    ap = argparse.ArgumentParser(description="ERW scheduled-job health (session 61)")
    sub = ap.add_subparsers(dest="cmd", required=True)
    r = sub.add_parser("run")
    r.add_argument("--step", required=True)
    r.add_argument("--retries", type=int, default=1)
    r.add_argument("--wait", type=int, default=60)
    r.add_argument("--strict", action="store_true", help="exit 1 on a failure (a person's run)")
    rc = sub.add_parser("record")
    rc.add_argument("--step", required=True)
    rc.add_argument("--status", required=True, choices=["ok", "skipped", "retried", "failed"])
    rc.add_argument("--reason", default="")
    d = sub.add_parser("dedupe")
    d.add_argument("--workflow-file", required=True)
    d.add_argument("--minutes", type=int, default=10)
    s = sub.add_parser("summary")
    s.add_argument("--day", default="yesterday")
    s.add_argument("--out")
    al = sub.add_parser("alert")
    al.add_argument("--day", default="today")
    al.add_argument("--run-id", default="")
    al.add_argument("--dry-run", action="store_true")
    b = sub.add_parser("budget")  # session 176
    b.add_argument("--step", required=True)
    b.add_argument("--day", default="today")
    a, rest_ = ap.parse_known_args(argv)
    if a.cmd == "budget":
        code, _ = budget(a.step, None if a.day == "today" else a.day)
        return code
    if a.cmd == "alert":  # session 119: never raises: an alert that cannot be sent must not fail the job it reports on
        try:
            day = a.day if a.day != "today" else dt.datetime.now(dt.timezone.utc).date().isoformat()
            alert(day, a.run_id or None, a.dry_run)
        except Exception as exc:
            print(f"health alert: not sent: {type(exc).__name__}: {str(exc)[:200]}")
        return 0
    if a.cmd == "run":
        cmd = rest_[1:] if rest_[:1] == ["--"] else rest_
        if not cmd:
            raise SystemExit("run: the command after --")
        code, _ = run(a.step, cmd, a.retries, a.wait, a.strict)
        return code
    if a.cmd == "record":
        record(a.step, a.status, a.reason)
        return 0
    if a.cmd == "dedupe":
        dedupe(a.workflow_file, a.minutes)
        return 0
    if a.cmd == "summary":
        day = a.day if a.day != "yesterday" else (dt.datetime.now(dt.timezone.utc).date() - dt.timedelta(days=1)).isoformat()
        path, rows = summary(day, a.out)
        print(f"{os.path.relpath(path, ROOT)}: {len(rows)} steps recorded")
        return 0


if __name__ == "__main__":
    sys.exit(main())

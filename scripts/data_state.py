#!/usr/bin/env python3
"""The state of every table of the warehouse, read from this machine's own files (session 200).

Energy Research Warehouse (ERW). Writes one document, docs/state/data_<day>.md: a row per table of
warehouse/metadata/coverage.csv, then the tables whose last row is older than their cadence. Read only: no request to
a publisher, no data lock, nothing under warehouse/output is written. Nothing is taken from memory: every figure is
read by this script from a file it names.

    python scripts/sync.py --check --no-git > runs/session200/sync_check.out 2>&1      # Redivis's state, first
    python scripts/data_state.py --data-root <the checkout that holds warehouse/output> \
        --sync-out runs/session200/sync_check.out --day 2026-10-11 --out docs/state/data_2026-10-11.md

What each column is read from:
  rows, first, last     the table's own CSV in warehouse/output: its records after the '#' header lines, and the
                        smallest and largest value of its time column (ts_utc, else event_date, else date: the columns
                        scripts/sync.py compares)
  days                  from the last row to the time this script started (UTC)
  interval, license,
  last run              coverage.csv (interval, license, last_run)
  public site           the license, and warehouse/supabase/live_set.yaml as load.py reads it (full, recent,
                        catalogue_hold, review_hold)
  written by            the script named in the file's own "Retrieved: ... by <script>" header line; where the header
                        names none, the connector of the table's newest row in run_status.csv
  daily run             run_status.csv: the table (or a table that table_migrations.csv folds into it) has a row of
                        the GitHub runner on at least two of its three newest run days; the data machine's own steps
                        are named in DATA_MACHINE below, from warehouse/run_data_machine.sh
  archive               archive_manifest.csv (rows, archived_at)
  Redivis               redivis_uploads.csv (dataset, uploaded_at) and the class scripts/sync.py --check gave the table

The cadence rule of "Stale or stuck" is STALE_DAYS below: the finest interval coverage gives a table decides how old
its last row may be. An event or snapshot table has no row cadence; it is listed when its last run is older than
NO_CADENCE_RUN_DAYS. A reason is written only where a file gives one: paused_sources.csv, known_gaps.csv, the newest
row of run_status.csv, and the hand-written reasons file (--reasons: table, reason, evidence), each named in its line.
--notes puts a hand-written Markdown file under "Read these first"; the script says there that it is written by hand.
"""

import argparse
import csv
import datetime as dt
import json
import os
import re
import sys

import pandas as pd
import yaml

TIME_COLUMNS = ("ts_utc", "event_date", "date")   # as scripts/sync.py
# how old a table's last row may be, in days, by the finest interval coverage.csv gives it
STALE_DAYS = {"PT5M": 3, "PT15M": 3, "PT1H": 3, "PT168H": 14, "P1D": 3, "P1W": 14, "P1M": 62, "P3M": 184, "P1Y": 730}
ORDER = ["PT5M", "PT15M", "PT1H", "P1D", "PT168H", "P1W", "P1M", "P3M", "P1Y"]
NO_CADENCE_RUN_DAYS = 8
# the tables the data machine's own daily run writes (warehouse/run_data_machine.sh: the step that writes each)
DATA_MACHINE = {"ercot_zone_prices_history": "dm_ercot_zone_prices"}


def read_csv(path):
    return pd.read_csv(path, dtype=str, keep_default_na=False)


def header_lines(path):
    out = []
    with open(path, encoding="utf-8", newline="") as f:
        for line in f:
            if not line.startswith("#"):
                break
            out.append(line[1:].strip())
    return out


def file_state(path):
    """(rows, time column, first, last, header lines) of a table's CSV. One pass over one column."""
    head = header_lines(path)
    cols = list(pd.read_csv(path, skiprows=len(head), nrows=0, dtype=str).columns)
    col = next((c for c in TIME_COLUMNS if c in cols), None)
    n, first, last = 0, None, None
    for chunk in pd.read_csv(path, skiprows=len(head), usecols=[col or cols[0]], dtype=str, keep_default_na=False, na_values=[], chunksize=2_000_000):
        n += len(chunk)
        if col:
            s = chunk[col].str.strip()
            s = s[s != ""]
            if len(s):
                lo, hi = s.min(), s.max()
                first = lo if first is None or lo < first else first
                last = hi if last is None or hi > last else last
    return n, col, first, last, head


def short(ts):
    """A timestamp as the table writes it, without a midnight and without seconds."""
    if not ts:
        return ""
    t = ts.replace(" ", "T")
    m = re.match(r"^(\d{4}-\d{2}-\d{2})(?:T(\d{2}:\d{2}))?", t)
    if not m:
        return ts[:20]
    return m.group(1) if not m.group(2) or m.group(2) == "00:00" else f"{m.group(1)} {m.group(2)}"


def age_days(ts, now):
    if not ts:
        return None
    try:
        t = pd.Timestamp(ts)
    except (ValueError, TypeError):
        return None
    if pd.isna(t):
        return None
    t = t.tz_localize("UTC") if t.tzinfo is None else t.tz_convert("UTC")
    return (now - t).total_seconds() / 86400


def finest(interval):
    parts = [p for p in interval.split(";") if p in ORDER]
    return min(parts, key=ORDER.index) if parts else None


def writer_of(head):
    """The script the header names: the one of its "Retrieved:" line first; a rebuild from the archive
    (warehouse/archive/restore.py) only when the header names no other."""
    found = []
    for line in sorted(head, key=lambda ln: not ln.startswith("Retrieved")):
        found += re.findall(r"\bby ((?:warehouse|scripts)/[\w./-]+\.py)", line)
    own = [f for f in found if not f.endswith("archive/restore.py")]
    return (own or found or [None])[0]


def schedule_texts(root):
    """{file: text} of every script that starts something on a clock: the run scripts, the step list and the workflows."""
    import glob
    paths = (glob.glob(os.path.join(root, "warehouse", "*.sh")) + [os.path.join(root, "warehouse", "scheduled.py")]
             + glob.glob(os.path.join(root, ".github", "workflows", "*.yml")))
    out = {}
    for p in sorted(paths):
        with open(p, encoding="utf-8", errors="replace") as f:
            out[os.path.relpath(p, root).replace(os.sep, "/")] = f.read()
    return out


def lag_note(head):
    """A publisher's lag the file's own header states, or ''."""
    text = " ".join(head)
    if re.search(r"plus 60 days|60-Day|60 days after", text):
        return "ERCOT discloses these files 60 days after the operating day (the file's own header)"
    return ""


def parse_sync(path):
    """{table: class} for every table scripts/sync.py --check named, and its summary line. A table it did not name is
    'current' when the summary counts no unread table."""
    named, summary = {}, ""
    with open(path, "rb") as f:
        raw = f.read()
    # a shell's redirect may have written UTF-16 or UTF-8 with a mark at the start
    text = raw.decode("utf-16") if raw[:2] in (b"\xff\xfe", b"\xfe\xff") else raw.decode("utf-8-sig", errors="replace")
    for line in text.splitlines():
        t = line.strip()
        if t.startswith("tables in coverage:"):
            summary = t
        m = re.match(r"^(behind|diverged|AHEAD, not overwritten|not on Redivis): ([\w]+)", t)
        if m:
            named[m.group(2)] = {"AHEAD, not overwritten": "ahead"}.get(m.group(1), m.group(1))
    return named, summary


def live_state(table, live):
    """What live_set.yaml says of a table, as load.py reads it."""
    held = set(live.get("catalogue_hold") or [])
    review = set(live.get("review_hold") or [])
    if any(re.match(p, table) for p in live["full"]):
        rule = "loaded whole"
    elif any(re.match(p, table) for p in live["recent"]["tables"]):
        rule = f"loaded, newest {live['recent']['days']} days"
    else:
        return "not loaded"
    if table in held:
        return "held out of the live set (catalogue_hold)"
    return rule + (", held for review" if table in review else "")


def main(argv=None):
    ap = argparse.ArgumentParser(description="The state of every table, from this machine's own files")
    ap.add_argument("--data-root", required=True, help="the checkout that holds warehouse/output and warehouse/metadata")
    ap.add_argument("--sync-out", required=True, help="the saved output of scripts/sync.py --check --no-git")
    ap.add_argument("--day", required=True, help="the day the document is named for, YYYY-MM-DD")
    ap.add_argument("--reasons", help="hand-written reasons: a CSV of table, reason, evidence")
    ap.add_argument("--ceiling-log", help="the data machine's daily run log, for ERCOT's ceiling line")
    ap.add_argument("--notes", help="hand-written lines for 'Read these first', a Markdown file; each names its evidence")
    ap.add_argument("--cache", help="a JSON file that keeps each table's pass beside its file's size and time (under runs/)")
    ap.add_argument("--machine", default="lab-desktop")
    ap.add_argument("--out", required=True)
    a = ap.parse_args(argv)
    root = os.path.abspath(a.data_root)
    meta = os.path.join(root, "warehouse", "metadata")
    out_dir = os.path.join(root, "warehouse", "output")
    now = pd.Timestamp.now(tz="UTC")

    cov = read_csv(os.path.join(meta, "coverage.csv"))
    manifest = read_csv(os.path.join(meta, "archive_manifest.csv")).drop_duplicates("table", keep="last").set_index("table")
    uploads = read_csv(os.path.join(meta, "redivis_uploads.csv")).drop_duplicates("table", keep="last").set_index("table")
    runs = read_csv(os.path.join(meta, "run_status.csv"))
    migr = read_csv(os.path.join(meta, "table_migrations.csv"))
    folded = dict(zip(migr["old_table"], migr["new_table"]))
    runs["into"] = runs["table"].map(lambda t: folded.get(t, t))
    runs["day"] = runs["run_id"].str[:8]
    gh = runs[runs["runner"] == "github"]
    run_days = sorted(set(gh["day"]))[-3:]
    paused = read_csv(os.path.join(meta, "paused_sources.csv"))
    gaps = read_csv(os.path.join(meta, "known_gaps.csv")).set_index("table")
    with open(os.path.join(root, "warehouse", "supabase", "live_set.yaml"), encoding="utf-8") as f:
        live = yaml.safe_load(f)
    sync_named, sync_summary = parse_sync(a.sync_out)
    unread = int(re.search(r"unread: (\d+)", sync_summary).group(1)) if sync_summary else None
    reasons = {}
    if a.reasons:
        with open(a.reasons, encoding="utf-8", newline="") as f:
            for r in csv.DictReader(f):
                reasons[r["table"]] = (r["reason"], r["evidence"])

    # --cache: a table's pass is kept beside its file's size and time, so a second run reads only the files that changed
    cache = {}
    if a.cache and os.path.exists(a.cache):
        with open(a.cache, encoding="utf-8") as f:
            cache = json.load(f)
    rows, total = [], 0
    for _, c in cov.iterrows():
        t = c["table"]
        path = os.path.join(out_dir, t + ".csv")
        r = {"table": t, "interval": c["interval"], "license": c["license"], "last_run": c["last_run"], "cov_rows": c["n_rows"], "derived": c["derived"]}
        if not os.path.exists(path):
            r.update(here=False)
            rows.append(r)
            continue
        key = f"{os.path.getsize(path)}:{os.path.getmtime(path)}"
        if cache.get(t, {}).get("key") == key:
            n, col, first, last, head = cache[t]["state"]
        else:
            n, col, first, last, head = file_state(path)
            cache[t] = {"key": key, "state": [n, col, first, last, head]}
        total += n
        tr = runs[runs["into"] == t]
        newest = tr.iloc[-1] if len(tr) else None
        days_in = sorted(set(gh.loc[gh["into"] == t, "day"]) & set(run_days))
        r.update(here=True, rows=n, col=col, first=first, last=last, age=age_days(last, now), run_age=age_days(c["last_run"], now), lag=lag_note(head),
                 writer=writer_of(head) or (f"run_status: {newest['connector']}" if newest is not None else "not named in the header or in run_status"),
                 runner_days=days_in, newest_status=(newest["status"], newest["run_id"], newest["detail"], newest["runner"]) if newest is not None else None,
                 live=live_state(t, live))
        rows.append(r)
        print(f"{t}: {n} rows, {first} to {last}", flush=True)
    if a.cache:
        os.makedirs(os.path.dirname(os.path.abspath(a.cache)), exist_ok=True)
        with open(a.cache, "w", encoding="utf-8") as f:
            json.dump(cache, f)

    def daily(r):
        if r["table"] in DATA_MACHINE:
            return f"yes: the data machine's run (`{DATA_MACHINE[r['table']]}`)"
        if len(r["runner_days"]) >= 2:
            st = r["newest_status"]
            return "yes: the runner" + ("" if st[0] == "ok" else f" (newest row: {st[0]}, {st[1][:8]})")
        return "no"

    def site(r):
        if r["license"] != "public":
            return f"{r['license']}: may not; {r['live']}"
        return f"public: may; {r['live']}"

    def archive(r):
        t = r["table"]
        if t not in manifest.index:
            return "not in the manifest"
        m = manifest.loc[t]
        same = "same rows" if str(m["rows"]) == str(r["rows"]) else f"{int(m['rows']):,} rows there"
        return f"{same}, {m['archived_at'][:10]}"

    def redivis(r):
        t = r["table"]
        cls = sync_named.get(t, "current" if unread == 0 else "not named by the check")
        if t not in uploads.index:
            return f"{cls}; no upload recorded"
        u = uploads.loc[t]
        ds = "internal" if u["dataset"].endswith("_internal") else "public"
        rows_note = "" if str(u["rows"]) == str(r["rows"]) else f", {int(u['rows']):,} rows uploaded"
        return f"{cls}; {ds} draft, {u['uploaded_at'][:10]}{rows_note}"

    sched = schedule_texts(root)

    def scheduled_in(r):
        """The schedule scripts that name the table's writer (its file name), or the table itself."""
        w_ = os.path.basename(r["writer"]) if r["writer"].endswith(".py") else None
        return [p for p, text in sched.items() if (w_ and w_ in text) or re.search(rf"\b{re.escape(r['table'])}\b", text)]

    def facts(r):
        """What the machine's files say of a table nothing has refreshed: who writes it, what starts that, its newest run."""
        named = scheduled_in(r)
        st = r["newest_status"]
        where = ("named in " + ", ".join(f"`{p}`" for p in named)) if named else "named in no run script or workflow: started by hand or by a session"
        last = f"; newest run {st[1][:8]} by {'the runner' if st[3] == 'github' else 'a machine'} (`{st[0]}`)" if st else ""
        return f"written by `{r['writer']}`, {where}{last}"

    def auto_reason(r):
        t = r["table"]
        if t in reasons:
            return f"{reasons[t][0]} ({reasons[t][1]})"
        for _, p in paused.iterrows():
            if re.match(rf"^{re.escape(p['scope'])}_", t):
                return f"{p['publisher']} is paused since {p['paused_on']}: {p['reason']} (`paused_sources.csv`)"
        if t in gaps.index:
            g = gaps.loc[t, "reason"]
            return f"a known gap since {gaps.loc[t, 'since']}: {g[:200]}{'...' if len(g) > 200 else ''} (`known_gaps.csv`)"
        st = r["newest_status"]
        if st and st[0] != "ok":
            d = " ".join(st[2].split())
            return f"its newest run, {st[1]} ({'the runner' if st[3] == 'github' else 'a machine'}), is `{st[0]}`: {d[:200]}{'...' if len(d) > 200 else ''} (`run_status.csv`)"
        said = facts(r)
        if r["lag"]:
            return f"{r['lag']}; and no run since {r['last_run'][:10]}: {said}"
        return "No reason is written in the machine's files. " + said[0].upper() + said[1:]

    here = [r for r in rows if r["here"]]
    absent = [r for r in rows if not r["here"]]
    stale, quiet = [], []
    for r in here:
        f = finest(r["interval"])
        if f and r["age"] is not None:
            if r["age"] > STALE_DAYS[f]:
                stale.append((r, f))
        elif r["run_age"] is not None and r["run_age"] > NO_CADENCE_RUN_DAYS:
            quiet.append(r)

    def lagging(r):
        """Refreshed in the last three days with a run that ended ok: the pull works, the source has nothing newer."""
        st = r["newest_status"]
        return r["run_age"] is not None and r["run_age"] <= 3 and (st is None or st[0] == "ok") and r["table"] not in reasons

    lag_list = [(r, f) for r, f in stale if lagging(r)]
    stuck = [(r, f) for r, f in stale if not lagging(r)]

    ceiling = ""
    if a.ceiling_log and os.path.exists(a.ceiling_log):
        with open(a.ceiling_log, encoding="utf-8", errors="replace") as f:
            hits = [ln.strip() for ln in f if ln.startswith("counted against the ceiling:")]
        ceiling = hits[-1] if hits else ""
    zones = next((r for r in here if r["table"] == "ercot_zone_prices_history"), None)

    own_root = os.path.abspath(os.path.join(os.path.dirname(os.path.abspath(__file__)), ".."))

    def shown(p):
        """A path as the document prints it: from the checkout's root, whichever checkout the file is in."""
        p = os.path.abspath(p)
        for base in (root, own_root):
            if p.startswith(base + os.sep):
                return os.path.relpath(p, base).replace(os.sep, "/")
        return p.replace(os.sep, "/")

    stamp = now.strftime("%Y-%m-%d %H:%M UTC")
    day = dt.date.fromisoformat(a.day)
    L = []
    w = L.append
    w(f"# State of the data, {day.day} {day:%B %Y}")
    w("")
    w(f"Every table of the Energy Research Warehouse (ERW) as it stands on `{a.machine}`, the data machine, read at {stamp} by "
      "`scripts/data_state.py` from the machine's own files. Nothing here is from memory: each column names the file it is read from, and the commands "
      "are at the end. This document makes no ruling and changes no table.")
    w("")
    if a.notes:
        w("## Read these first")
        w("")
        w(f"Written by hand by the session that ran the script (`{shown(a.notes)}`); each line names its evidence. Everything below this section is generated.")
        w("")
        with open(a.notes, encoding="utf-8") as f:
            w(f.read().strip())
        w("")
    w("## The count")
    w("")
    n_pub = sum(1 for r in here if r["license"] == "public")
    w(f"- Tables in `warehouse/metadata/coverage.csv`: **{len(cov)}**. On this machine: {len(here)}, holding **{total:,} rows** "
      f"({n_pub} public, {len(here) - n_pub} internal). Not on this machine: {len(absent)}" + (": " + ", ".join(f"`{r['table']}`" for r in absent) if absent else "") + ".")
    off = [r for r in here if str(r["rows"]) != str(r["cov_rows"])]
    w(f"- Tables whose file holds another row count than coverage says: {len(off)}"
      + (": " + "; ".join(f"`{r['table']}` (the file {r['rows']:,}, coverage {int(r['cov_rows']):,})" for r in off) if off else "") + ".")
    w(f"- Redivis, from `scripts/sync.py --check --no-git`: {sync_summary or 'the check wrote no summary line'}.")
    cls = {}
    for r in here:
        cls.setdefault(sync_named.get(r["table"], "current"), []).append(r["table"])
    for k in ("ahead", "behind", "diverged", "not on Redivis"):
        if cls.get(k):
            w(f"  - {k}: " + ", ".join(f"`{t}`" for t in cls[k]))
    no_arch = [r["table"] for r in here if r["table"] not in manifest.index]
    arch_off = [r["table"] for r in here if r["table"] in manifest.index and str(manifest.loc[r["table"], "rows"]) != str(r["rows"])]
    w(f"- The archive, from `warehouse/metadata/archive_manifest.csv`: {len(here) - len(no_arch) - len(arch_off)} tables with the rows this machine holds, "
      f"{len(arch_off)} with another count" + (" (" + ", ".join(f"`{t}`" for t in arch_off) + ")" if arch_off else "") + f", {len(no_arch)} not in the manifest"
      + (" (" + ", ".join(f"`{t}`" for t in no_arch) + ")" if no_arch else "") + ".")
    apart = [r["table"] for r in here if r["table"] in manifest.index and r["table"] in uploads.index
             and manifest.loc[r["table"], "data_sha256"] != uploads.loc[r["table"], "data_sha256"]]
    w(f"- The archive against the Redivis draft, by the hash of the file's data both records keep (`data_sha256`): {len(apart)} tables whose file archived last is "
      "not, byte for byte, the file uploaded last" + (": " + ", ".join(f"`{t}`" for t in apart) if apart else "") + ". A retrieval stamp alone can make that "
      "difference; the hashes do not say what differs. `sync.py` compares rows and the newest timestamp only, so it reads all of these as current.")
    n_run = sum(1 for r in here if daily(r).startswith("yes: the runner"))
    n_dm = sum(1 for r in here if r["table"] in DATA_MACHINE)
    w(f"- Refreshed by a daily run: {n_run} by the GitHub runner's (a row in `run_status.csv` on at least two of its three newest run days, "
      f"{', '.join(f'{d[:4]}-{d[4:6]}-{d[6:]}' for d in run_days)}), {n_dm} by the data machine's (`warehouse/run_data_machine.sh`). The other {len(here) - n_run - n_dm} are "
      "written by a weekly or monthly step, by a session, or once.")
    w("")
    w("## ERCOT's ceiling")
    w("")
    if ceiling:
        m = re.search(r"([\d,]+) load zone rows.*ceiling ([\d,]+)", ceiling)
        used, cap = (int(m.group(1).replace(",", "")), int(m.group(2).replace(",", ""))) if m else (None, None)
        w(f"- The load zone price pull (`ercot_zone_prices.py --refresh`, approved ceiling 3,000,000 rows): the newest daily run's own line, in `{shown(a.ceiling_log)}`:")
        w(f"  - \"{ceiling}\"")
        if used:
            w(f"- Position: **{used:,} of {cap:,} rows, {used / cap:.1%}; {cap - used:,} rows of room.**")
    else:
        w("- The daily run's log holds no line \"counted against the ceiling\": the position is not known from this machine's files.")
    if zones:
        w(f"- The table it fills, `ercot_zone_prices_history`: {zones['rows']:,} rows, {short(zones['first'])} to {short(zones['last'])} (its own file).")
    w("")
    w("## Every table")
    w("")
    w("Columns: **Rows**, **First** and **Last** are read from the table's own file (the time column is `ts_utc`, else `event_date`, else `date`; "
      "a table with none shows no dates). **Days** is from the last row to the time above. **Interval**, **license** and **Last run** are coverage's. "
      "**Public site** is the license and `warehouse/supabase/live_set.yaml`: a public table may reach the site, an internal one may not; \"loaded\" means the "
      "live set takes it. **Written by** is the script the file's own header names. **Daily run** is read from `run_status.csv`. **Archive** and **Redivis** "
      "compare the rows recorded there with the rows here; the Redivis class is `sync.py`'s (rows and newest timestamp), and every upload is a draft.")
    w("")
    w("| Table | Rows | First | Last | Days | Interval | Public site | Written by | Last run | Daily run | Archive | Redivis |")
    w("|---|---:|---|---|---:|---|---|---|---|---|---|---|")
    for r in rows:
        if not r["here"]:
            w(f"| `{r['table']}` | not on this machine | | | | {r['interval']} | {r['license']} | | {r['last_run'][:10]} | | | |")
            continue
        age = "" if r["age"] is None else f"{r['age']:.1f}"
        w(f"| `{r['table']}` | {r['rows']:,} | {short(r['first'])} | {short(r['last'])} | {age} | {r['interval'] or 'none'} | {site(r)} | "
          f"`{r['writer']}` | {r['last_run'][:10]} | {daily(r)} | {archive(r)} | {redivis(r)} |")
    w("")
    w("## Stale or stuck")
    w("")
    w("The rule: the finest interval coverage gives a table decides how old its last row may be: "
      + ", ".join(f"{k} {v} days" for k, v in STALE_DAYS.items()) + ". A table over its limit is listed, oldest first within its interval. "
      "A reason is given only where a file gives one, and the file is named; \"not known\" is said where none does. A publisher's own lag "
      "(a report that appears 60 days later, a monthly figure two months behind) reads as stale by this rule and is said in the reason where it is known.")
    w("")
    w(f"**{len(stale)} of {len(here)} tables are over their limit: {len(stuck)} that nothing has refreshed in the last three days or whose newest run did not end ok, "
      f"and {len(lag_list)} that a run refreshed in the last three days without a newer row.**")
    w("")
    w(f"### Stuck, or not on a schedule ({len(stuck)})")
    w("")
    w("Over the limit, and either no run has rewritten the table in the last three days or its newest run did not end `ok`. Where no file gives a reason, "
      "the line says what the files do say: the script that writes the table, which run script or workflow names that script, and the table's newest row in `run_status.csv`.")
    w("")
    w("| Table | Interval | Last row | Days | Limit | Last run | Reason, if known |")
    w("|---|---|---|---:|---:|---|---|")
    for r, f in sorted(stuck, key=lambda x: (ORDER.index(x[1]), -x[0]["age"])):
        w(f"| `{r['table']}` | {f} | {short(r['last'])} | {r['age']:.1f} | {STALE_DAYS[f]} | {r['last_run'][:10]} | {auto_reason(r)} |")
    w("")
    w(f"### Refreshed, and the source gave nothing newer ({len(lag_list)})")
    w("")
    w("Over the limit, but a run rewrote the table in the last three days and its newest row in `run_status.csv` is `ok`: the pull works and the last row is the "
      "newest the run brought. That is a publisher's lag or a study's fixed window, not a stuck pull; the note says which where the file's own header does.")
    w("")
    w("| Table | Interval | Last row | Days | Limit | Last run | Note |")
    w("|---|---|---|---:|---:|---|---|")
    for r, f in sorted(lag_list, key=lambda x: (ORDER.index(x[1]), -x[0]["age"])):
        w(f"| `{r['table']}` | {f} | {short(r['last'])} | {r['age']:.1f} | {STALE_DAYS[f]} | {r['last_run'][:10]} | {r['lag'] or facts(r)} |")
    w("")
    w(f"### No row cadence: event and snapshot tables whose last run is more than {NO_CADENCE_RUN_DAYS} days old")
    w("")
    w("An event table (a row per deal, filing or outage) and a snapshot table (a row per thing, as of one pull) have no interval, so their last row "
      "says little. These are the ones nothing has rewritten for more than "
      f"{NO_CADENCE_RUN_DAYS} days ({len(quiet)} tables). Many are meant to be pulled once or by hand; the reason is given where a file gives one.")
    w("")
    w("| Table | Interval | Rows | Last run | Days since | Reason, if known |")
    w("|---|---|---:|---|---:|---|")
    for r in sorted(quiet, key=lambda x: -x["run_age"]):
        w(f"| `{r['table']}` | {r['interval'] or 'none'} | {r['rows']:,} | {r['last_run'][:10]} | {r['run_age']:.1f} | {auto_reason(r)} |")
    w("")
    w("## The commands")
    w("")
    w("Run on `" + a.machine + "` in the checkout that holds the tables, with `.venv\\Scripts\\python.exe`. None is piped; each exit code is in the session report.")
    w("")
    w("```")
    w("python scripts/sync.py --check --no-git > runs/session200/sync_check.out 2>&1")
    w("python scripts/data_state.py --data-root . --sync-out " + shown(a.sync_out) + " --day " + a.day
      + (" --reasons " + shown(a.reasons) if a.reasons else "") + (" --notes " + shown(a.notes) if a.notes else "")
      + (" --ceiling-log " + shown(a.ceiling_log) if a.ceiling_log else "")
      + " --out " + shown(a.out))
    w("```")
    w("")
    w("- Rows, first, last: each table's CSV in `warehouse/output`, one pass by `scripts/data_state.py` (`file_state`).")
    w("- Interval, license, last run: `warehouse/metadata/coverage.csv`. Archive: `warehouse/metadata/archive_manifest.csv`. Redivis: "
      "`warehouse/metadata/redivis_uploads.csv` and the saved output of `scripts/sync.py --check --no-git`.")
    w("- Daily run: `warehouse/metadata/run_status.csv` and `warehouse/metadata/table_migrations.csv`; the data machine's steps from `warehouse/run_data_machine.sh`.")
    w("- Public site: `warehouse/supabase/live_set.yaml`. Paused publishers: `warehouse/metadata/paused_sources.csv`. Known gaps: `warehouse/metadata/known_gaps.csv`.")
    w("- ERCOT's ceiling: the line the daily refresh writes into its own log.")
    w("")
    os.makedirs(os.path.dirname(os.path.abspath(a.out)), exist_ok=True)
    with open(a.out, "w", encoding="utf-8", newline="\n") as f:
        f.write("\n".join(L))
    print(f"{a.out}: {len(rows)} tables, {total:,} rows, {len(stale)} over their limit ({len(stuck)} stuck or unscheduled, {len(lag_list)} refreshed without a newer row), "
          f"{len(quiet)} with no cadence and an old run")
    return 0


if __name__ == "__main__":
    sys.exit(main())

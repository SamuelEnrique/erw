#!/usr/bin/env python3
"""The planner: the next chain, drafted from the roadmap when the chain queue is empty (session 197).

Energy Research Warehouse (ERW). queue/README.md; docs/machines.md, "Continuous work", "The planner". A chain ends on
the queue step (scripts/chain_queue.py). When queue/next/ is empty the machine idles until a person writes the next
prompt. The planner writes that prompt file from what the owner has already written down: docs/roadmap.md.

    python scripts/planner.py check [--machine <name>] [--role code|data]
    python scripts/planner.py draft [--machine <name>] [--role code|data] [--dry-run] [--roadmap <file>]

It is a prompt builder, not a writer of prompts: no model call. Every sentence of a planned chain is copied from
docs/roadmap.md (the item, its rulings, the section "Rulings", the section "Holds") or from queue/CHAIN_TEMPLATE.md
(every rule), or is one of the fixed lines below. It reads, and never edits, the roadmap, the session reports since
archive/sessions/LAST_ANSWERED, what waits for the owner (site/content/waits.json, written by
site/scripts/build-waits.mjs) and the template. `draft` writes queue/next/NNN-planned-<slug>.md, NNN being the chain's
first session number, and prints its path on the last line. `--dry-run` prints the file and writes nothing. `check`
prints why it would or would not run.

docs/roadmap.md, as the planner reads it (the file's own lines say the same):

    ## Status       planner: on | off        (absent, or anything else: off)
                    budget: N sessions a day per machine
                    earliest start: HH:MM UTC     latest start: HH:MM UTC
                    deploy cutoffs: HH:MM to HH:MM UTC; HH:MM to HH:MM UTC     (or: none)
    ## This week    numbered items: "N. [ ] title" is open, "N. [x] title" is closed; under it, indented, one a line:
                    machine: code | data | <a machine's name>      where: <the page or table>
                    done: <what done means>      rulings: <a ruling already made>   (rulings: may repeat)
                    session: <one session's work>   (one to three; none: the title is the one session)
                    cap: USD <n>   (model spend for the chain; absent: USD 0)      lands: yes | no
    ## Rulings, ## Holds     pasted into the chain as they stand
    ## Input from Ben and Khalid, ## Review log     read by people; the planner does not use them

It refuses to run, and says every reason, when: the planner is off; the roadmap is older than 7 days; "This week" has
no open item for this machine's role that was not planned before; queue/next/ already holds a file; the machine's
sessions of the UTC day are at the budget; the hour is outside the start hours; the Status section does not state the
budget, the start hours or the deploy cutoffs.

Hard stops, in the code and in tests/test_planner.py:
  - the budget and the start hours of "Status";
  - the deploy cutoffs of "Status" are copied into every planned chain, with the start hours;
  - a planned chain never names a pull, a migration, a secret, a release-gate change, a change to CLAUDE.md or to a
    permission file, or a deletion: an item whose words do is refused and waits for a person's own prompt;
  - a planned chain holds one to three sessions, and at most one of them lands: the last;
  - an item is planned once: an item already in a planned chain (queue/next/ or queue/done/) is not taken again;
  - the file written is checked before it is kept: its name by the chain queue's own rule, its first line, the
    precheck as its first rule, the queue step as its last, no em dash, no unfilled blank.

The planner is off by default. Only a person sets "planner: on", in docs/roadmap.md.

Exit codes: 0 a chain was drafted (its path is the last line printed), or check found nothing against running;
3 refused (every reason printed); 1 could not (a file could not be read or written); 2 bad input.
"""

import argparse
import datetime as dt
import json
import os
import re
import subprocess
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.abspath(os.path.join(HERE, ".."))
sys.path.insert(0, HERE)

UTC = dt.timezone.utc
ROADMAP = os.path.join("docs", "roadmap.md")
TEMPLATE = os.path.join("queue", "CHAIN_TEMPLATE.md")
MAX_AGE_DAYS = 7
MAX_SESSIONS = 3
REFUSED = 3
FIRST_LINE = "PLANNED by scripts/planner.py from docs/roadmap.md as of "
ITEM_LINE = "Roadmap item: "
EM = chr(0x2014)
NAME_RE = re.compile(r"^(\d{3,})-([a-z0-9][a-z0-9-]*)\.md$")     # scripts/chain_queue.py's own rule
TASK_RE = re.compile(r"^\d{3,}-(code|data)-")
SECTIONS = ("Status", "This week", "Rulings", "Holds", "Input from Ben and Khalid", "Review log")

# What a planned chain never names. An item whose words match is refused: a person writes that prompt.
NEVER = (
    ("a pull", re.compile(r"\bpulls?\b|\bpulling\b|\bdownload\w*|\bscrap\w*|\bcrawl\w*|\bfetch\w*|\bnew (source|connector|host)\b", re.I)),
    ("a migration", re.compile(r"\bmigrat\w*|\balter table\b|\bcreate table\b", re.I)),
    ("a secret", re.compile(r"\bsecrets?\b|\bapi[ _-]?keys?\b|\btokens?\b|\bpasswords?\b|\bcredentials?\b|\.env\b", re.I)),
    ("a release-gate change", re.compile(r"release\.ts|\brelease gate\b|\bgo(es)? live\b|\bmake\b.{0,40}\blive\b|\bto live\b|REVIEW_FREEZE|\bunfreez\w*|\bpublish\w* to redivis\b|\brelease\w* (a|the) redivis\b", re.I)),
    ("a change to CLAUDE.md or to a permission file", re.compile(r"CLAUDE\.md|\.claude\b|settings(\.local)?\.json|\ballowlist\b", re.I)),
    ("a deletion", re.compile(r"\bdelet\w*|\bdrop (the |a )?(table|column|branch|bucket)\b|\btruncat\w*|\bwipe\w*|\berase\w*|\brm -", re.I)),
)


def read(path):
    with open(path, encoding="utf-8") as f:
        return f.read()


def sections(text):
    """{heading: [its lines]} for the level-two headings of a document."""
    out, cur = {}, None
    for line in text.replace("\r\n", "\n").split("\n"):
        m = re.match(r"^##\s+(.+?)\s*$", line)
        if m:
            cur = m.group(1)
            out[cur] = []
        elif cur is not None:
            out[cur].append(line)
    return out


def _field(lines, key):
    """The value of the first line "key: value" (a list mark before it is allowed), or None."""
    for line in lines:
        m = re.match(rf"^\s*(?:[-*]\s+)?{re.escape(key)}\s*:\s*(.+?)\s*$", line, re.I)
        if m:
            return m.group(1)
    return None


def _clock(text):
    m = re.fullmatch(r"(\d{1,2}):(\d{2})(?:\s*UTC)?", (text or "").strip(), re.I)
    if not m or int(m.group(1)) > 23 or int(m.group(2)) > 59:
        return None
    return int(m.group(1)) * 60 + int(m.group(2))


def hhmm(minutes):
    return f"{minutes // 60:02d}:{minutes % 60:02d}"


def status(text):
    """The Status section: {on, budget, earliest, latest, cutoffs, problems}. Times are minutes of the UTC day. A line
    that cannot be read is a problem, never a guess; the planner is on only when the line says exactly "on"."""
    lines = sections(text).get("Status", [])
    s = {"on": (_field(lines, "planner") or "off").strip().lower() == "on", "budget": None, "earliest": None, "latest": None, "cutoffs": None, "problems": []}
    b = _field(lines, "budget")
    m = re.match(r"^(\d+)\s+sessions?\s+a\s+day\b", b or "", re.I)
    if m:
        s["budget"] = int(m.group(1))
    else:
        s["problems"].append('Status does not state the budget ("budget: N sessions a day per machine")')
    for key in ("earliest", "latest"):
        v = _clock(_field(lines, f"{key} start"))
        if v is None:
            s["problems"].append(f'Status does not state the {key} hour a session may start ("{key} start: HH:MM UTC")')
        s[key] = v
    c = _field(lines, "deploy cutoffs")
    if c is None:
        s["problems"].append('Status does not state the deploy cutoffs ("deploy cutoffs: HH:MM to HH:MM UTC", or "deploy cutoffs: none")')
    elif c.strip().lower().rstrip(".") == "none":
        s["cutoffs"] = []
    else:
        got = []
        for part in c.split(";"):
            m = re.fullmatch(r"\s*(\d{1,2}:\d{2})\s+to\s+(\d{1,2}:\d{2})\s*UTC\s*\.?\s*", part, re.I)
            a, z = (_clock(m.group(1)), _clock(m.group(2))) if m else (None, None)
            if a is None or z is None:
                s["problems"].append(f'a deploy cutoff cannot be read: "{part.strip()}" (HH:MM to HH:MM UTC)')
                got = None
                break
            got.append((a, z))
        s["cutoffs"] = got
    return s


def within(minute, start, end):
    """Whether a minute of the day is from start to end, where the span may pass midnight."""
    return start <= minute <= end if start <= end else (minute >= start or minute <= end)


def items(text):
    """The numbered items of "This week": {n, open, title, machine, where, done, rulings, sessions, cap, lands, words}."""
    out, cur = [], None
    for line in sections(text).get("This week", []):
        m = re.match(r"^(\d+)\.\s+\[( |x|X)\]\s+(.+?)\s*$", line)
        if m:
            cur = {"n": int(m.group(1)), "open": m.group(2) == " ", "title": m.group(3), "machine": None, "where": None, "done": None, "rulings": [], "sessions": [], "cap": None, "lands": None, "words": [m.group(3)]}
            out.append(cur)
            continue
        f = re.match(r"^\s+(?:[-*]\s+)?(machine|where|done|rulings?|session|cap|lands)\s*:\s*(.+?)\s*$", line, re.I)
        if cur is None or not f:
            if line.strip() and not line.startswith((" ", "\t")):
                cur = None                                   # a line of prose ends the item above it
            continue
        key, val = f.group(1).lower(), f.group(2)
        cur["words"].append(val)
        if key in ("ruling", "rulings"):
            cur["rulings"].append(val)
        elif key == "session":
            cur["sessions"].append(val)
        elif key == "cap":
            c = re.fullmatch(r"USD\s*(\d+(?:\.\d{1,2})?)", val, re.I)
            cur["cap"] = float(c.group(1)) if c else val     # a cap that cannot be read is kept, and refused later
        elif key == "lands":
            cur["lands"] = val.strip().lower()
        else:
            cur[key] = val
    return out


def never(item):
    """[(what a planned chain never names, the word found)] in an item's own words."""
    text = " \n ".join(item["words"])
    return [(what, m.group(0)) for what, rx in NEVER for m in [rx.search(text)] if m]


def git(*args, root=ROOT):
    r = subprocess.run(["git", *args], cwd=root, capture_output=True, text=True, stdin=subprocess.DEVNULL, encoding="utf-8", errors="replace")
    return r.stdout if r.returncode == 0 else ""


def last_changed(path, root=ROOT, git=git):
    """When the roadmap last changed: its last commit when the file is as committed, else the file's own time (an edit
    not yet committed). A checkout sets a file's time to now, so the commit is what counts for a committed file."""
    rel = os.path.relpath(path, root).replace(os.sep, "/")
    mtime = dt.datetime.fromtimestamp(os.path.getmtime(path), UTC)
    if rel.startswith(".."):
        return mtime
    if git("status", "--porcelain", "--", rel, root=root).strip():
        return mtime
    stamp = git("log", "-1", "--format=%cI", "--", rel, root=root).strip()
    try:
        return dt.datetime.fromisoformat(stamp).astimezone(UTC) if stamp else mtime
    except ValueError:
        return mtime


def chain_files(root=ROOT):
    """[(folder, name, text)] of the chain queue's files, waiting and taken."""
    out = []
    for folder in ("next", "done"):
        d = os.path.join(root, "queue", folder)
        for f in sorted(os.listdir(d)) if os.path.isdir(d) else []:
            if NAME_RE.match(f) and not TASK_RE.match(f):
                try:
                    out.append((folder, f, read(os.path.join(d, f))))
                except OSError:
                    pass
    return out


def planned_before(root=ROOT):
    """The roadmap items already in a planned chain: {(number, title)}."""
    got = set()
    for _, _, text in chain_files(root):
        if not text.startswith(FIRST_LINE):
            continue
        for m in re.finditer(rf"(?m)^{re.escape(ITEM_LINE)}(\d+)\. (.+?)\s*$", text):
            got.add((int(m.group(1)), m.group(2)))
    return got


def sessions_in(text):
    return len(re.findall(r"(?m)^## Session \d+", text))


def sessions_today(machine, now, root=ROOT, git=git):
    """The sessions this machine has run or holds for the UTC day: the sessions of the chain files it took from the
    queue today (the take is a commit, "Queue: <name> taken by <machine>"), and the session reports first committed
    today that name the machine, whichever count is larger. A chain pasted by hand whose reports do not name the machine
    is not seen: the count is a floor."""
    since = now.strftime("%Y-%m-%dT00:00:00+00:00")
    taken = 0
    for subject in git("log", "--all", f"--since={since}", "--format=%s", root=root).splitlines():
        m = re.match(r"^Queue: (\S+\.md) taken by (\S+)", subject)
        if m and m.group(2) == machine:
            for folder, name, text in chain_files(root):
                if name == m.group(1):
                    taken += sessions_in(text)
                    break
    reports = 0
    seen = set()
    for line in git("log", "--all", f"--since={since}", "--diff-filter=A", "--name-only", "--format=", "--", "archive/sessions", root=root).splitlines():
        f = line.strip()
        if re.search(r"SESSION_\d+[a-z]?_REPORT\.md$", f) and f not in seen:
            seen.add(f)
            body = git("log", "--all", "-1", "--format=%H", "--", f, root=root).strip()
            text = git("show", f"{body}:{f}", root=root) if body else ""
            if machine and machine.lower() in text.lower():
                reports += 1
    return max(taken, reports)


def next_session_number(root=ROOT, git=git):
    """The next free session number: one above the highest known. Known are the reports and prompts of
    archive/sessions/ in this checkout and on every branch git holds here, the sessions named in the chain queue's
    files, and the sessions named in the subjects of the last 30 days' commits ("Session 198: ..."), since another
    machine's session may have no report on this branch yet."""
    top = 0
    names = set(os.listdir(os.path.join(root, "archive", "sessions"))) if os.path.isdir(os.path.join(root, "archive", "sessions")) else set()
    names |= {os.path.basename(x.strip()) for x in git("log", "--all", "--diff-filter=A", "--name-only", "--format=", "--", "archive/sessions", root=root).splitlines() if x.strip()}
    for f in names:
        m = re.match(r"^SESSION_(\d+)[a-z]?_(REPORT|PROMPT)\.md$", f)
        if m:
            top = max(top, int(m.group(1)))
    for _, _, text in chain_files(root):
        for m in re.finditer(r"(?m)^## Session (\d+)", text):
            top = max(top, int(m.group(1)))
    for subject in git("log", "--all", "--since=30 days ago", "--format=%s", root=root).splitlines():
        m = re.match(r"^Session (\d+)\b", subject)
        if m:
            top = max(top, int(m.group(1)))
    return top + 1


def unanswered(root=ROOT):
    """(the last report answered, [the report files after it, oldest first], how many items wait or None when the
    site's waits file is not on this machine)."""
    last = None
    try:
        v = _field(read(os.path.join(root, "archive", "sessions", "LAST_ANSWERED")).split("\n"), "last_answered")
        m = re.match(r"^(\d+)", v or "")
        last = int(m.group(1)) if m else None
    except OSError:
        pass
    d = os.path.join(root, "archive", "sessions")
    files = []
    for f in os.listdir(d) if os.path.isdir(d) else []:
        m = re.match(r"^SESSION_(\d+)([a-z]?)_REPORT\.md$", f)
        if m and (last is None or int(m.group(1)) > last):
            files.append((int(m.group(1)), m.group(2), f))
    waits = None
    try:
        data = json.loads(read(os.path.join(root, "site", "content", "waits.json")))
        waits = sum(len(r.get("waits", [])) for r in data.get("reports", []))
    except (OSError, ValueError):
        pass
    return last, [f for _, _, f in sorted(files)], waits


def template_rules(text):
    """The numbered rules of queue/CHAIN_TEMPLATE.md, as they stand."""
    body = text.replace("\r\n", "\n")
    part = body[body.index("## Rules for every session of this chain"):]
    rules = []
    for line in part.split("\n")[1:]:
        m = re.match(r"^(\d+)\.\s+(.+)$", line)
        if m:
            rules.append(m.group(2))
        elif line.startswith("---") or line.startswith("## "):
            break
        elif line.strip() and rules:
            rules[-1] += " " + line.strip()
    return rules


def slug(title):
    s = re.sub(r"[^a-z0-9]+", "-", title.lower()).strip("-")
    return (s[:40].rstrip("-")) or "item"


def choose(text, machine, role, root=ROOT):
    """(the first open item of "This week" for this machine that was not planned before, or None; why not, in words)."""
    done = planned_before(root)
    mine = [i for i in items(text) if (i["machine"] or "").strip().lower() in {x for x in (role, (machine or "").lower()) if x}]
    open_ = [i for i in mine if i["open"]]
    fresh = [i for i in open_ if (i["n"], i["title"]) not in done]
    if fresh:
        return fresh[0], ""
    if open_:
        return None, f'"This week" has no open item for {machine} ({role}) that was not planned before: {len(open_)} open, each already in a planned chain'
    return None, f'"This week" has no open item for {machine} ({role})'


def item_problems(item):
    """Why an item cannot be planned by a machine: every reason."""
    out = [f'the item names {what} ("{word}"): a planned chain never does; a person writes that prompt' for what, word in never(item)]
    if not item["where"]:
        out.append('the item does not say where (the page or table): "where: ..."')
    if not item["done"]:
        out.append('the item does not say what done means: "done: ..."')
    if len(item["sessions"]) > MAX_SESSIONS:
        out.append(f"the item asks for {len(item['sessions'])} sessions: a planned chain holds one to {MAX_SESSIONS}")
    if item["cap"] is not None and not isinstance(item["cap"], float):
        out.append(f'the item\'s cap cannot be read: "{item["cap"]}" (cap: USD <n>)')
    if item["lands"] not in (None, "yes", "no"):
        out.append(f'the item\'s "lands" is neither yes nor no: "{item["lands"]}"')
    return out


def refusals(text, machine, role, now, root=ROOT, changed=None, sessions=None):
    """Every reason the planner will not run now; empty when it will. `changed` is when the roadmap last changed."""
    s = status(text)
    out = []
    if not s["on"]:
        out.append("planner: off (docs/roadmap.md, Status). Only a person turns it on")
    if changed is not None:
        age = (now - changed).total_seconds() / 86400
        if age > MAX_AGE_DAYS:
            out.append(f"the roadmap is {age:.1f} days old (last changed {changed:%Y-%m-%d %H:%M} UTC): older than {MAX_AGE_DAYS} days, it is not planned from")
    out += s["problems"]
    held = [name for folder, name, _ in chain_files(root) if folder == "next"]
    if held:
        out.append(f"queue/next/ already holds a file ({', '.join(held)}): the queue is not empty")
    if role not in ("code", "data"):
        out.append(f"the machine's role is not known ({role!r}): .erw/machine.json, or --role")
    if s["budget"] is not None:
        n = sessions(machine, now) if sessions else sessions_today(machine, now, root)
        if n >= s["budget"]:
            out.append(f"the budget is reached: {machine} has {n} session{'s' if n != 1 else ''} for {now:%Y-%m-%d} UTC, and the budget is {s['budget']} a day per machine")
    if s["earliest"] is not None and s["latest"] is not None:
        minute = now.hour * 60 + now.minute
        if not within(minute, s["earliest"], s["latest"]):
            out.append(f"it is {hhmm(minute)} UTC: a session may start from {hhmm(s['earliest'])} to {hhmm(s['latest'])} UTC")
    item, why = choose(text, machine, role, root)
    if item is None:
        out.append(why)
    else:
        out += [f'item {item["n"]}, "{item["title"]}": {p}' for p in item_problems(item)]
    return out


def chain(text, template, machine, role, now, root=ROOT, changed=None, number=None):
    """(the file's name, the planned chain) for the first open item. The caller has checked `refusals`."""
    s = status(text)
    item, _ = choose(text, machine, role, root)
    parts = item["sessions"] or [item["title"]]
    first = number if number is not None else next_session_number(root)
    last = first + len(parts) - 1
    cap = item["cap"] or 0.0
    lands = item["lands"] == "yes" or (item["lands"] is None and item["where"].strip().startswith("/"))
    sec = sections(text)
    # a section still holding only the template's own line ("What goes here: ...") is empty
    block = lambda name: [x for x in sec.get(name, []) if x.strip() and not x.strip().startswith("What goes here")]
    answered, reports, waits = unanswered(root)
    name = f"{first:03d}-planned-{slug(item['title'])}.md"
    branch = lambda n: f"{slug(item['title'])[:30].rstrip('-')}"
    money = lambda v: f"{v:.2f}".rstrip("0").rstrip(".") if v else "0"
    hours = f"from {hhmm(s['earliest'])} to {hhmm(s['latest'])} UTC"
    cut = "; ".join(f"{hhmm(a)} to {hhmm(z)} UTC" for a, z in s["cutoffs"]) if s["cutoffs"] else ""

    out = [f"{FIRST_LINE}{now:%Y-%m-%d %H:%M} UTC (the roadmap last changed {changed:%Y-%m-%d %H:%M} UTC)." if changed else f"{FIRST_LINE}{now:%Y-%m-%d %H:%M} UTC.", ""]
    out += [f"# Planned chain of {now.day} {now:%B}: session{'s' if last > first else ''} {first}{f' to {last}' if last > first else ''}", ""]
    out += [f"The machine {machine} ({role}), unattended. No person wrote this file: scripts/planner.py built it from docs/roadmap.md, whose words are quoted below as they stand, and from queue/CHAIN_TEMPLATE.md. It was built because the chain queue was empty and the roadmap says \"planner: on\".", ""]
    out += [f"{ITEM_LINE}{item['n']}. {item['title']}", f"- Where: {item['where']}", f"- Done means: {item['done']}"]
    out += [f"- Ruling already made: {r}" for r in item["rulings"]] or ["- Rulings already made on this item: none written in the roadmap."]
    out += ["", "## Rules for every session of this chain", ""]
    rules = template_rules(template)
    own = [f"**This chain's own rules, from the roadmap's Status.** No session starts outside the start hours, {hours}: a session whose turn comes outside them is not started, and the chain goes to its last step."]
    own.append(f"No landing in a deploy cutoff ({cut}): a session whose landing would fall in one waits for it to pass, `python scripts/duty.py beat` first." if cut else "The roadmap states no deploy cutoff.")
    own.append("Only the chain's last session lands, and only if its part says so. This chain names no pull, no migration, no secret, no change to `site/lib/release.ts` or to any release gate, no change to `CLAUDE.md` or to a permission file, and no deletion: a session that finds it needs one stops that step and writes it under \"For Samuel's ruling\".")
    for i, rule in enumerate(rules, 1):
        if re.search(r"<Any rule of this chain alone", rule):
            rule = " ".join(own)
        rule = rule.replace("Total for the chain: USD <total>.", f"Total for the chain: USD {money(cap)}.")
        if rule.startswith("**Pulls:**"):
            rule = "**Pulls:** none. This chain approves no pull. No request to a paused publisher (`warehouse/metadata/paused_sources.csv`)."
        out.append(f"{i}. {rule}")
    out += ["", "## What the owner has ruled, from the roadmap", ""]
    out += block("Rulings") or ["The roadmap's section \"Rulings\" is empty."]
    out += ["", "## Holds: what no session may touch, from the roadmap", ""]
    out += block("Holds") or ["The roadmap's section \"Holds\" is empty."]
    out += ["", "## What is not yet answered", ""]
    out.append(f"- The last report whose rulings the owner has answered: session {answered} (`archive/sessions/LAST_ANSWERED`)." if answered is not None else "- `archive/sessions/LAST_ANSWERED` could not be read.")
    out.append(f"- {len(reports)} report{'s' if len(reports) != 1 else ''} after it on this branch" + (f": {reports[0]} to {reports[-1]}" if len(reports) > 1 else f": {reports[0]}" if reports else "") + (f"; {waits} item{'s' if waits != 1 else ''} wait for the owner (`site/content/waits.json`)." if waits is not None else "; the site's file of what waits is not built on this machine."))
    out.append("- An item that waits in one of those reports is not ruled. Do not act as if it were: where this chain's work meets one, take the reversible option and say so.")
    for k, what in enumerate(parts):
        n = first + k
        final = k == len(parts) - 1
        share = cap / len(parts) if cap else 0.0
        out += ["", f"## Session {n}: {what}", ""]
        out.append(f"Long end 2:30. Model spend cap USD {money(int(share * 100) / 100)}. Pulls: none. Branch `{'task' if final and lands else 'wip'}/{n}-{branch(n)}`.")
        out.append("")
        out.append(f"- What to build, in the roadmap's words: {what}")
        out.append(f"- Where: {item['where']}")
        out += [f"- Ruling: {r}" for r in item["rulings"]]
        if final:
            out.append(f"- Done means, in the roadmap's words: {item['done']}")
            out.append("- **Landing: this session lands**, by rule 4, with a snapshot before and after." if lands else "- **This session does not land.** Its work stays on its `wip/` branch, pushed to GitHub; its report says what a landing would need.")
        else:
            out.append(f"- This session does not land: it leaves its work on its `wip/` branch, pushed to GitHub, and session {n + 1} starts from that branch.")
        out.append("- The report: `archive/sessions/SESSION_" + str(n) + "_REPORT.md`, by rule 10. A check that fails is fixed and run again; the report lists every run.")
    return name, "\n".join(out) + "\n"


def problems_of(name, text, cutoffs=None):
    """What is wrong with a planned chain file; empty when it may be kept. The last hard stop: nothing is written
    that fails here."""
    out = []
    if not NAME_RE.match(name) or TASK_RE.match(name) or "-planned-" not in name:
        out.append(f"the name {name} is not NNN-planned-<slug>.md by the chain queue's rule")
    if not text.startswith(FIRST_LINE):
        out.append("the first line does not say the file was planned")
    if EM in text:
        out.append("an em dash")
    rules = re.findall(r"(?m)^(\d+)\. (.+)$", text[text.find("## Rules for every session of this chain"):text.find("## What the owner has ruled")])
    if not rules or not rules[0][1].startswith("**Precheck first.**") or "python scripts/precheck.py" not in rules[0][1]:
        out.append("the first rule is not the precheck")
    if not rules or "python scripts/chain_queue.py next" not in rules[-1][1] or "queue" not in rules[-1][1].lower():
        out.append("the last rule is not the queue step")
    n = sessions_in(text)
    if not 1 <= n <= MAX_SESSIONS:
        out.append(f"{n} sessions: a planned chain holds one to {MAX_SESSIONS}")
    if text.count("**Landing: this session lands**") > 1:
        out.append("more than one session lands")
    blank = re.search(r"<(?!N>)[A-Za-z][^>\n]{0,80}>", text)       # "<N>" stands for each session's own number, in the rules
    if blank:
        out.append(f"a blank of the template was not filled: {blank.group(0)}")
    if "Pulls: none." not in text or "**Pulls:** none." not in text:
        out.append("the chain does not say that it approves no pull")
    for a, z in cutoffs or []:
        if f"{hhmm(a)} to {hhmm(z)} UTC" not in text:
            out.append(f"the deploy cutoff {hhmm(a)} to {hhmm(z)} UTC is not in the chain")
    return out


def machine_of(args):
    """(name, role) of the machine: as given, else this machine's own role file."""
    import duty
    m = duty.machine() or {}
    name = duty.clean(args.machine or m.get("name") or os.environ.get("COMPUTERNAME") or os.environ.get("HOSTNAME") or "machine")
    role = args.role or (m.get("role") if not args.machine or duty.clean(m.get("name") or "") == name else None)
    return name, role


def run(action, machine, role, roadmap=None, dry_run=False, now=None, root=ROOT, out=print, sessions=None):
    """`check` or `draft`. Returns (the exit code, the path written or None)."""
    now = now or dt.datetime.now(UTC)
    path = roadmap or os.path.join(root, ROADMAP)
    try:
        text = read(path)
    except OSError as exc:
        out(f"planner: off: the roadmap cannot be read ({type(exc).__name__}: {path})")
        return REFUSED, None
    changed = last_changed(path, root)
    why = refusals(text, machine, role, now, root, changed, sessions)
    on = status(text)["on"]
    out(f"planner: {'on' if on else 'off'}")
    if why:
        out(f"refused for {machine} ({role}), {now:%Y-%m-%d %H:%M} UTC:")
        for w in why:
            out(f"  - {w}")
        return REFUSED, None
    try:
        template = read(os.path.join(root, TEMPLATE))
    except OSError as exc:
        out(f"planner: {TEMPLATE} cannot be read ({type(exc).__name__})")
        return 1, None
    name, body = chain(text, template, machine, role, now, root, changed)
    bad = problems_of(name, body, status(text)["cutoffs"])
    if bad:
        out(f"refused: the chain drafted for {machine} does not pass its own checks, and is not written:")
        for b in bad:
            out(f"  - {b}")
        return REFUSED, None
    if action == "check":
        out(f"would draft queue/next/{name} for {machine} ({role}): {sessions_in(body)} session{'s' if sessions_in(body) != 1 else ''}")
        return 0, None
    if dry_run:
        out(f"would write queue/next/{name}:")
        out(body)
        return 0, None
    dest = os.path.join(root, "queue", "next", name)
    if os.path.exists(dest) or os.path.exists(os.path.join(root, "queue", "done", name)):
        out(f"refused: a file named {name} is already in the queue")
        return REFUSED, None
    os.makedirs(os.path.dirname(dest), exist_ok=True)
    with open(dest, "w", encoding="utf-8", newline="\n") as f:
        f.write(body)
    out(f"drafted: {name} for {machine} ({role}), {sessions_in(body)} session{'s' if sessions_in(body) != 1 else ''}; not committed, not pushed")
    out(dest)
    return 0, dest


def main(argv=None):
    ap = argparse.ArgumentParser(description="The planner: the next chain, drafted from docs/roadmap.md (session 197). No model call.")
    ap.add_argument("action", choices=["check", "draft"])
    ap.add_argument("--machine", help="the machine to plan for (default: this machine, from .erw/machine.json)")
    ap.add_argument("--role", choices=["code", "data"], help="its role (default: this machine's own)")
    ap.add_argument("--roadmap", help="another roadmap file than docs/roadmap.md (a sample, for a dry run)")
    ap.add_argument("--dry-run", action="store_true", help="draft: print the file; write nothing")
    a = ap.parse_args(argv)
    try:
        name, role = machine_of(a)
        code, _ = run(a.action, name, role, a.roadmap, a.dry_run)
        return code
    except Exception as exc:
        print(f"planner: {type(exc).__name__}: {str(exc)[:300]}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    sys.exit(main())

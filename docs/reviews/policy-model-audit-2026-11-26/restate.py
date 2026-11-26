"""Session 10217: an independent restatement of every figure the monitor view of /policy prints as it opens.

Written from the words, not from the page's code: docs/methods/policy_monitor.md (sections 10, 12, 16 and 18) and the
hovers the components print (MonitorView.tsx's column and filter hovers, MonitorCalendar.tsx's headings, StateLaws.tsx's
line). Where the words leave a rule open, the plainest reading is taken and named here, so a difference from the page is
a difference between what the page says and what it does:

  - the view opens on "significance 5 or more, any date" (the Reset's hover); a record with no score is below any floor;
  - each filter's count is "what ticking it gives", the other filters kept;
  - "the past week" is "the seven days to" its last day (the hover): seven calendar days, both ends counted;
  - "the month ahead" is "from this page's day to thirty days on": the page's day and the thirty days after it;
  - the floor's hidden steps are the month ahead's steps of records below the floor;
  - the next step is "the first dated step any document of the record states on or after this page's day; else its
    last step, marked passed";
  - the charts are of "every record of the monitor's file"; top six bodies by count, the rest "Other"; twelve sectors;
    the figures by month "the largest of each unit";
  - "changes in the last 90 days" are the changes dated in the 90 days to the page's day.

    python runs/c10217/restate.py <worktree root> <today YYYY-MM-DD> <out.json>
"""
import collections
import datetime as dt
import json
import os
import re
import sys

root, today, out_path = sys.argv[1], sys.argv[2], sys.argv[3]
m = json.load(open(os.path.join(root, "site", "data", "policy", "monitor.json"), encoding="utf-8"))
ll = json.load(open(os.path.join(root, "site", "data", "siting", "large_load_rules.json"), encoding="utf-8"))
rows = m["rows"]
out = {}
D = lambda s: dt.date.fromisoformat(s)
iso = lambda d: d.isoformat()

INSTR = {"rule": "Final rule", "proposed_rule": "Proposed rule", "order": "Order", "guidance": "Guidance", "approval": "Approval",
         "lease_sale": "Lease sale", "award": "Award", "application": "Application", "complaint": "Complaint",
         "environmental_review": "Environmental review", "meeting": "Meeting or hearing", "decision": "Decision", "notice": "Notice",
         "announcement": "Announcement"}
STAT = {"proposed": "Proposed", "final": "Final", "effective": "In effect", "stayed": "Stayed", "vacated": "Vacated",
        "withdrawn": "Withdrawn", "filed": "Filed", "open": "Open for comment", "scheduled": "Scheduled", "issued": "Issued",
        "announced": "Announced"}
KIND = {"effective": "takes effect", "expires": "ends", "comments_due": "comments due",
        "intervention_due": "interventions or hearing requests due", "review_due": "environmental document due",
        "decision_due": "decision due", "meeting": "meeting or session", "filing_due": "filings due",
        "review_petition_due": "petitions for judicial review due"}
GRID = {"ercot": "ERCOT", "pjm": "PJM", "miso": "MISO", "caiso": "CAISO", "nyiso": "NYISO", "isone": "ISO-NE", "spp": "SPP"}
SECT = {"policy": "Policy", "nuclear": "Nuclear", "renewables": "Renewables", "gas": "Gas", "generation": "Generation", "oil": "Oil",
        "other": "Other", "lng": "LNG", "storage": "Storage", "transmission": "Transmission", "transport": "Transport",
        "grid_conditions": "Grid conditions", "power_prices": "Power prices", "geopolitics": "Geopolitics",
        "interconnection": "Interconnection", "capital": "Capital", "company": "Company", "deal": "Deal"}


def floor_ok(r, floor=5):
    s = r.get("significance")
    return s is not None and s >= floor


opened = [r for r in rows if floor_ok(r)]
out["count|shown"] = len(opened)
out["count|held"] = m["records"]
out["count|rows"] = len(rows)
out["built"] = m["built"]

# each filter's choices: every value the file holds, counted over the records the other filters leave (here the floor)
LISTS = {"bodies": (lambda r: [r["body"]], lambda k: k), "instruments": (lambda r: [r["instrument"]], lambda k: INSTR.get(k, k)),
         "sectors": (lambda r: [r.get("sector")], lambda k: SECT.get(k, k.replace("_", " "))),
         "grids": (lambda r: r.get("grids", []), lambda k: GRID.get(k, k)), "states": (lambda r: r.get("states", []), lambda k: k),
         "statuses": (lambda r: [r["status"]], lambda k: STAT.get(k, k))}
for name, (vals, label) in LISTS.items():
    every = {v for r in rows for v in vals(r) if v}
    n = collections.Counter(v for r in opened for v in set(x for x in vals(r) if x))
    order = sorted(every, key=lambda k: (-n.get(k, 0), label(k)))
    for k in order:
        out[f"option|{name}|{k}"] = n.get(k, 0)
        out[f"optionlabel|{name}|{k}"] = label(k)
    out[f"optorder|{name}"] = ",".join(order)

# the calendar
last = max(r["date"] for r in rows)
out["calendar|last"] = last
stale = last < today
to = D(last) if stale else D(today)
frm = to - dt.timedelta(days=6)          # "the seven days to" its last day
out["calendar|stale"] = stale
out["calendar|weekFrom"] = iso(frm)
out["calendar|weekTo"] = iso(to)
ahead_to = D(today) + dt.timedelta(days=30)
out["calendar|aheadTo"] = iso(ahead_to)
week = sorted([r for r in opened if iso(frm) <= r["date"] <= iso(to)], key=lambda r: (r["date"], -0), reverse=False)
week = sorted(week, key=lambda r: r["id"])
week = sorted(week, key=lambda r: r["date"], reverse=True)
out["calendar|week|n"] = len(week)
for i, r in enumerate(week[:60]):
    out[f"calendar|week|{i}"] = f"{r['date']}|{r['id']}|{r['body']}|{INSTR.get(r['instrument'], r['instrument'])}|{STAT.get(r['status'], r['status']).lower()}"


def steps_in(recs):
    got = []
    for r in recs:
        for s in r.get("steps", []):
            if today <= s["date"] <= iso(ahead_to):
                got.append((s["date"], r["id"], s["kind"], s))
    return sorted(got, key=lambda x: (x[0], x[1], x[2]))


ahead = steps_in(opened)
out["calendar|ahead|n"] = len(ahead)
for i, (d, rid, k, s) in enumerate(ahead[:80]):
    out[f"calendar|ahead|{i}"] = f"{d}|{KIND.get(k, k)}|{rid}|{s['event_id']}"
out["calendar|hidden"] = len(steps_in([r for r in rows if not floor_ok(r)]))


# the table, newest first, ties by record id
def next_step(r):
    st = sorted(r.get("steps", []), key=lambda s: (s["date"], s["kind"], s["event_id"]))
    if st:
        for s in st:
            if s["date"] >= today:
                return s["date"], s["kind"], False
        return st[-1]["date"], st[-1]["kind"], True
    if r.get("next"):
        return r["next"]["date"], r["next"]["step"], r["next"]["date"] < today
    return None


def money(v):
    def fmt(x):
        s = f"{x:,.2f}".rstrip("0").rstrip(".")
        return s
    if v >= 1e9:
        return f"USD {fmt(v / 1e9)} billion"
    if v >= 1e6:
        return f"USD {fmt(v / 1e6)} million"
    return f"USD {fmt(v)}"


def fig_text(f):
    if f["unit"] == "USD":
        return money(f["value"])
    v = f["value"]
    s = f"{v:,.3f}".rstrip("0").rstrip(".") if v != int(v) else f"{int(v):,}"
    return f"{s} {f['unit']}"


table = sorted(sorted(opened, key=lambda r: r["id"]), key=lambda r: r["date"], reverse=True)
out["table|page"] = 50
for i, r in enumerate(table[:50]):
    nx = next_step(r)
    nxw = f"{nx[0]} {KIND.get(nx[1], nx[1])}{', passed' if nx[2] else ''}" if nx else ""
    out[f"table|{i}"] = "|".join(str(x) for x in [r["id"], r["date"], r["body"], INSTR.get(r["instrument"], r["instrument"]),
                                                   STAT.get(r["status"], r["status"]), SECT.get(r.get("sector") or "", (r.get("sector") or "").replace("_", " ")),
                                                   r.get("significance", ""), nxw, fig_text(r["figure"]) if r.get("figure") else "", r["n"]])
nxs = [next_step(r) for r in table]
out["table|next|ahead"] = sum(1 for x in nxs if x and not x[2])
out["table|next|passed"] = sum(1 for x in nxs if x and x[2])
out["table|next|none"] = sum(1 for x in nxs if not x)
out["table|figure|n"] = sum(1 for r in table if r.get("figure"))

# the charts: every record of the file
months = sorted({r["date"][:7] for r in rows})
lastday = D(last)
month_end = (lastday.replace(day=28) + dt.timedelta(days=4)).replace(day=1) - dt.timedelta(days=1)
def ordinal(n):
    return f"{n}{'th' if 11 <= n % 100 <= 13 else {1: 'st', 2: 'nd', 3: 'rd'}.get(n % 10, 'th')}"
labels = [f"{mo} to the {ordinal(lastday.day)}" if mo == last[:7] and lastday < month_end else mo for mo in months]
out["chart|bodymonth|months"] = ",".join(labels)
bc = collections.Counter(r["body"] for r in rows)
top = [b for b, _ in sorted(bc.items(), key=lambda x: (-x[1], x[0]))[:6]]
for b in top + (["Other"] if len(bc) > 6 else []):
    out[f"chart|bodymonth|{b}"] = ",".join(str(sum(1 for r in rows if r["date"][:7] == mo and ((r["body"] == b) if b != "Other" else r["body"] not in top))) for mo in months)
scored = [r for r in rows if r.get("sector") and r.get("significance") is not None]
sc = collections.Counter(r["sector"] for r in scored)
sectors = [s for s, _ in sorted(sc.items(), key=lambda x: (-x[1], x[0]))[:12]]
out["chart|sigsector|sectors"] = ",".join(sectors)
for name, lo, hi in [("0 to 4", 0, 4), ("5 to 6", 5, 6), ("7 to 10", 7, 10)]:
    out[f"chart|sigsector|{name}"] = ",".join(str(sum(1 for r in scored if r["sector"] == s and lo <= r["significance"] <= hi)) for s in sectors)
figs = collections.defaultdict(list)
for r in rows:
    if r.get("figure"):
        figs[(r["date"][:7], r["figure"]["unit"])].append(r)
for (mo, unit), rs in figs.items():
    best = sorted(rs, key=lambda r: (-r["figure"]["value"], r["id"]))[0]
    out[f"chart|fig|{mo}|{unit}"] = f"{len(rs)}|{best['id']}|{fig_text(best['figure'])}"

# the laws block, no state chosen (docs/methods/policy_monitor.md section 18)
laws, held = ll["laws"], ll["held_laws"]
out["laws|public"] = len(laws)
out["laws|held"] = len(held)
for s, n in collections.Counter(l["status"] for l in laws).items():
    out[f"laws|status|{s}"] = n
out["laws|shown"] = out["laws|total"] = len(laws) + len(held)
have = {l["state"] for l in laws} | {l["state"] for l in held}
searched = [x for x in ll.get("law_searches", []) if x["state"] not in have]
out["laws|withheldRows"] = sum(1 for x in searched if x["kind"] == "withheld")
out["laws|searched|n"] = len(searched)
out["laws|searched|list"] = ",".join(f"{x['state']}:{x['kind']}" for x in searched)
out["laws|states"] = len(have)
rv = ll["retrieved"]["state_large_load_laws"][:8]
out["laws|retrievedWords"] = f"{rv[:4]}-{rv[4:6]}-{rv[6:8]}"
for l in laws:
    st_date = l["status_date"] if re.fullmatch(r"\d{4}-\d{2}(-\d{2})?", l["status_date"] or "") else f"date {l['status_date'] or 'not published'}"
    eff = l["effective"] if re.fullmatch(r"\d{4}-\d{2}(-\d{2})?", l["effective"] or "") else (l["effective"] or "not published")
    topics = [p.split(":")[0].strip() if re.match(r"^[a-z][a-z ,/-]*: ", p.strip()) else "other" for p in (l["requirements"] or "").split(" || ") if p.strip()]
    thr = "threshold" if l["threshold"] and l["threshold"] != "not published" else "not published"
    out[f"law|{l['id']}"] = "|".join([l["state"], l["bill"], l["status"], st_date, eff, thr, ";".join(topics)])
# the rules and changes a chosen state links: by each two-letter state a row names
for key, recs in (("rules", ll["rules"] + ll["held_rules"]), ("changes", ll["changes"])):
    c = collections.Counter(s for r in recs for s in set(re.findall(r"\b[A-Z]{2}\b", r.get("state") or "")))
    for s, n in c.items():
        out[f"laws|{key}|{s}"] = n
# the same changes, counted as the words say: the 90 days to the page's day
since90 = iso(D(today) - dt.timedelta(days=90))
c90 = collections.Counter(s for r in ll["changes"] if r["date"] >= since90 for s in set(re.findall(r"\b[A-Z]{2}\b", r.get("state") or "")))
for s, n in c90.items():
    out[f"laws90|changes|{s}"] = n

# the paused line
p = json.load(open(os.path.join(root, "site", "data", "policy", "paused.json"), encoding="utf-8"))
out["paused|words"] = f"{len(p['sources'])} sources paused"
MON = ["Jan", "Feb", "Mar", "Apr", "May", "Jun", "Jul", "Aug", "Sep", "Oct", "Nov", "Dec"]
short = {"miso": "MISO", "vascc": "Virginia SCC"}
for s in p["sources"]:
    d = D(s["paused_on"])
    out[f"paused|{s['key']}"] = f"{short.get(s['key'], s['publisher'])}, paused since {d.day} {MON[d.month - 1]} {d.year}"

# the week view's docket rows: every row of state_rules.json dated in the window
sr = json.load(open(os.path.join(root, "site", "data", "policy", "state_rules.json"), encoding="utf-8"))
for days in (7, 30):
    since = iso(D(today) - dt.timedelta(days=days))
    inw = [r for r in sr["rows"] if re.fullmatch(r"\d{4}-\d{2}-\d{2}", str(r.get("date") or "")) and r["date"] >= since]
    out[f"week|{days}|since"] = since
    out[f"week|{days}|inwindow"] = len(inw)
    out[f"week|{days}|shown"] = len(inw)
    out[f"week|{days}|dropped"] = 0
    for k, n in collections.Counter(r.get("regulator_key") for r in inw).items():
        out[f"week|{days}|body|{k}"] = n
out["week|statefile|built"] = sr["built_at_utc"]
out["week|statefile|rows"] = len(sr["rows"])

json.dump(out, open(out_path, "w", encoding="utf-8"), indent=1)
print(f"{len(out)} keys written to {out_path}")

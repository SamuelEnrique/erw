"""Session 10217: follow-ups to measures.py: the calendar's hidden steps by why they are hidden; the records that share a
body and a title; the one law whose status and effective date disagree (its cites, as the file prints them).
    python runs/c10217/measures2.py <worktree root> <today>
"""
import collections
import datetime as dt
import json
import os
import re
import sys

root, today = sys.argv[1], sys.argv[2]
m = json.load(open(os.path.join(root, "site", "data", "policy", "monitor.json"), encoding="utf-8"))
ll = json.load(open(os.path.join(root, "site", "data", "siting", "large_load_rules.json"), encoding="utf-8"))
rows = m["rows"]
ahead_to = (dt.date.fromisoformat(today) + dt.timedelta(days=30)).isoformat()

hid = collections.Counter()
for r in rows:
    s = r.get("significance")
    if s is not None and s >= 5:
        continue
    for st in r.get("steps", []):
        if today <= st["date"] <= ahead_to:
            hid["not scored" if s is None else "scored below 5"] += 1
print("hidden steps of the month ahead, by why:", dict(hid))


def norm(t):
    return re.sub(r"[^a-z0-9]+", " ", t.lower()).strip()


groups = collections.defaultdict(list)
for r in rows:
    groups[(r["body"], norm(r["title"]))].append(r)
dups = [v for v in groups.values() if len(v) > 1]
dups.sort(key=lambda v: -len(v))
print("groups of records with one body and one title:", len(dups))
for v in dups[:12]:
    print(f"  {len(v)} records, {v[0]['body']}, title {v[0]['title'][:90]!r}: ids {[r['id'] for r in v][:5]} dates {sorted(r['date'] for r in v)[:5]}")
close = []
for v in dups:
    ds = sorted(v, key=lambda r: r["date"])
    for a, b in zip(ds, ds[1:]):
        gap = (dt.date.fromisoformat(b["date"]) - dt.date.fromisoformat(a["date"])).days
        if gap <= 45 and not a["id"].startswith("doc:") is False:
            pass
        if gap <= 45 and a["id"].startswith("doc:") and b["id"].startswith("doc:"):
            close.append((a["id"], b["id"], gap, a["title"][:70]))
print("pairs of records with no proceeding id, one body and one title, within 45 days (the repeat rule should join them):", len(close))
for c in close[:8]:
    print("  ", c)
gen = collections.Counter()
for v in dups:
    t = v[0]["title"].lower()
    gen["generic title (notice of, sunshine, meeting, biweekly, combined)" if re.search(r"biweekly|sunshine|combined notice|meeting|notice of|environmental assessment|information collection", t) else "other"] += 1
print("the groups by kind of title:", dict(gen))

for l in ll["laws"]:
    if l["state"] == "MD" or l["status"] in ("enacted",):
        print(f"law {l['id']} {l['state']} {l['bill'][:60]!r}: status {l['status']} dated {l['status_date']} ({l['date_kind']}); effective {l['effective']!r}")
        print(f"   status cite: {l['status_cite'][:400]!r}")

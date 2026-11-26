# Session 10211: how even the tracker's news window is. By month of publication (event_date): the stories in news_stories
# the scorer gave the sector datacenter_power, those of them scored, and those the extractor was sent
# (warehouse/datacenters/checked.csv, in git). Counts only; no story text is printed.
#   python runs/c10211/window.py <warehouse output dir> <checked.csv>
import csv
import json
import os
import sys
from collections import Counter

OUT, CHECKED = sys.argv[1], sys.argv[2]
csv.field_size_limit(10 ** 9)
with open(os.path.join(OUT, "news_stories.csv"), encoding="utf-8", newline="") as f:
    news = list(csv.DictReader(ln for ln in f if not ln.startswith("#")))
with open(CHECKED, encoding="utf-8", newline="") as f:
    sent = {r["story_id"] for r in csv.DictReader(f)}
dc = Counter(r["event_date"][:7] for r in news if r["sector"] == "datacenter_power")
sc = Counter(r["event_date"][:7] for r in news if r["scored_at"])
allm = Counter(r["event_date"][:7] for r in news)
se = Counter(r["event_date"][:7] for r in news if r["event_id"] in sent)
months = sorted(set(allm) | set(se))
out = {m: {"stories": allm[m], "scored": sc[m], "datacenter_power": dc[m], "sent_to_extractor": se[m]} for m in months if m >= "2025-01"}
print(json.dumps({"by_month": out, "sent_total": len(sent), "sent_found": sum(se.values()),
                  "sent_since_2026_09": sum(v for k, v in se.items() if k >= "2026-09")}, indent=1))

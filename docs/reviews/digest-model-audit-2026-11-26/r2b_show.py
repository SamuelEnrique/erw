"""Session 10235: print the stored rows (title, summary, the scorer's fields, date, outlet) of the stories whose title
matches each pattern given, for the reading by hand of r2_stories.out. Also policy_actions rows by title.

Run: python r2b_show.py <output dir> <pattern> [<pattern> ...]
"""
import csv
import os
import re
import sys

csv.field_size_limit(10 ** 9)
OUT = sys.argv[1]
pats = [re.compile(p, re.I) for p in sys.argv[2:]]
for name in ("news_stories", "policy_actions"):
    with open(os.path.join(OUT, name + ".csv"), encoding="utf-8", newline="") as f:
        for r in csv.DictReader(ln for ln in f if not ln.startswith("#")):
            if any(p.search(r.get("title", "")) for p in pats):
                print(f"[{name}] {r.get('event_id')} {r.get('event_date')} {r.get('source')} cluster {r.get('cluster_id', '')}")
                print(f"  title: {r.get('title')}")
                print(f"  summary: {r.get('summary', r.get('abstract', ''))[:700]}")
                print(f"  why: {r.get('why')} | mw: {r.get('mw')} | price: {r.get('price_mentioned')} | sig {r.get('significance')}")
                print(f"  url: {r.get('source_url')}")

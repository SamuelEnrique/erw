"""Session 10235: the fun facts of the ten newest Digests and three newest Roundups, traced to their stored sources.

For each issue: the fun fact as printed; the item that holds it (warehouse/news/facts/items/<date>.json, or for a
Roundup the item whose fact the issue prints); each source's stored raw file; whether each part's quoted span stands in
that raw file word for word; whether the printed sentences are the item's; and every number of the printed fact found
in the span of its part (a number in no span is listed). A warehouse-kind fact names its table and figure instead: its
numbers are listed for the hand reading.

Run: python r4_funfacts.py <repo root> > r4_funfacts.out
"""
import glob
import json
import os
import re
import sys

ROOT = sys.argv[1]
ISSUES = [("docs/digest", d) for d in ["2026-10-09", "2026-10-12", "2026-10-13", "2026-10-14", "2026-10-20", "2026-10-21",
                                       "2026-10-22", "2026-10-23", "2026-11-06", "2026-11-12"]]
ISSUES += [("docs/roundup", w) for w in ["2026-W43", "2026-W44", "2026-W45"]]
items = {}
for p in glob.glob(os.path.join(ROOT, "warehouse", "news", "facts", "items", "*.json")):
    with open(p, encoding="utf-8") as f:
        items[os.path.basename(p)[:-5]] = json.load(f)
NUM = re.compile(r"(?<![\w.])\d[\d,]*(?:\.\d+)?")


def norm(s):
    return re.sub(r"\s+", " ", s.replace(",", "")).strip()


for folder, name in ISSUES:
    md = open(os.path.join(ROOT, folder, name + ".md"), encoding="utf-8").read()
    m = re.search(r"## ERW's Fun Fact\n\n(.*?)(?:\n\nSources?: (.*?))?\n\n", md, re.S)
    print(f"\n== {name}")
    if not m:
        print("  no fun fact section")
        continue
    printed, srcline = m.group(1).strip(), (m.group(2) or "").strip()
    print(f"  printed: {printed}")
    print(f"  sources line: {srcline[:300] or 'NONE'}")
    item = items.get(name) if folder == "docs/digest" else None
    if item is None:
        for k, it in items.items():
            if it.get("fact") and norm(it["fact"])[:60] in norm(printed):
                item = it
                print(f"  item found by its text: {k}")
                break
    if item is None:
        print("  NO ITEM holds this fact")
        continue
    parts = {"fact": item.get("fact", ""), "second": item.get("second", "")}
    for k, t in parts.items():
        print(f"  item {k} {'printed as stored' if t and norm(t) in norm(printed) else 'NOT printed as stored'}: {t}")
    spans = {}
    for s in item.get("sources", []):
        raw = os.path.join(ROOT, s.get("raw", ""))
        ok = os.path.exists(raw)
        body = open(raw, encoding="utf-8", errors="replace").read() if ok else ""
        sp = s.get("span", "")
        inraw = bool(sp) and norm(sp) in norm(body)
        spans.setdefault(s.get("part", "?"), []).append(sp)
        print(f"  source [{s.get('part')}] {s.get('label')} raw {'present' if ok else 'MISSING'}; span {'in the raw file' if inraw else 'NOT FOUND in the raw file' if sp else 'none (a warehouse figure?)'}: {sp[:200]}")
        if s.get("table"):
            print(f"    warehouse source: table {s.get('table')} {json.dumps({k: v for k, v in s.items() if k not in ('label', 'url', 'raw', 'span')})[:300]}")
    for k, t in parts.items():
        for n in NUM.findall(t):
            pool = " ".join(spans.get(k, []))
            if n.replace(",", "") not in pool.replace(",", ""):
                print(f"  NUMBER {n} of the {k} is in no span of its part")

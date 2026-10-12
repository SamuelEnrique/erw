"""Session 200: every item the waits script lists is named in the rulings document, and no reference is to a line it does not list.

    python check_rulings.py <waits_all.json> <rulings.md>
"""
import json
import re
import sys

waits = json.load(open(sys.argv[1], encoding="utf-8"))
want = {f"{r['id']}:{w['line']}" for r in waits["reports"] for w in r["waits"]}
text = open(sys.argv[2], encoding="utf-8").read()
entries, cur = [], None
for line in text.splitlines():
    m = re.match(r"^\*\*([A-Z])(\d+)\. ", line)
    if m:
        cur = {"id": m.group(1) + m.group(2), "group": m.group(1), "refs": re.findall(r"`(\d{3}b?:\d+)`", line), "body": []}
        entries.append(cur)
    elif cur is not None and line.startswith("- "):
        cur["body"].append(line)
got = {x for e in entries for x in e["refs"]}
print(f"items listed by the script: {len(want)}; references in entry titles: {len(got)} distinct")
print("listed and not named in the document:", sorted(want - got))
print("named in the document and not listed:", sorted(got - want))
groups = {}
for e in entries:
    groups[e["group"]] = groups.get(e["group"], 0) + 1
print(f"entries: {len(entries)}; by group: {groups}")
done = [e["id"] for e in entries if any(re.match(r"^- (Looks (done|answered|overtaken)|Still so)", b) and "Looks" in b for b in e["body"])]
nothing = [e["id"] for e in entries if any(re.match(r"^- (Asked nothing|They ask nothing|A decision already described)", b) for b in e["body"])]
part = [e["id"] for e in entries if any(re.match(r"^- (\(a\) looks answered|Half done)", b) for b in e["body"])]
print(f"looks done or answered: {len(done)} {done}")
print(f"ask nothing: {len(nothing)} {nothing}")
print(f"answered in part: {len(part)} {part}")
print(f"open: {len(entries) - len(done) - len(nothing)} (of them in part answered: {len(part)})")
no_rec = [e["id"] for e in entries if not any(b.startswith("- Recommendation:") for b in e["body"])]
print("entries without a Recommendation line:", no_rec)
print("em dashes:", text.count(chr(0x2014)), "en dashes:", text.count(chr(0x2013)))

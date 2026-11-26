"""Session 10218: are the marked figures (data-n) of a branch's drawing those of main's, every one, in order?

    python numbers_same.py <main draw_compare.json> <view> <branch jsonl> <line index>
"""
import json
import sys

a = json.load(open(sys.argv[1], encoding="utf-8"))[sys.argv[2]]["marked"]
lines = [json.loads(x) for x in open(sys.argv[3], encoding="utf-8") if x.startswith("{")]
b = lines[int(sys.argv[4])]["marked"]
same = list(a.items()) == list(b.items())
print(f"main {len(a)} marked figures, branch {len(b)}; identical in keys, values and order: {same}")
for k in sorted(set(a) | set(b)):
    if a.get(k) != b.get(k):
        print("  differs:", k, a.get(k), b.get(k))

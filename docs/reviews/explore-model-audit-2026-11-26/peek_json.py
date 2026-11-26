"""Print the structure of a figures file's first view (keys, a few slots)."""
import json
import sys

d = json.load(open(sys.argv[1], encoding="utf-8"))
print("top keys:", list(d.keys()))
v = d["views"][0]
print("view keys:", list(v.keys()))
for k, x in v.items():
    s = json.dumps(x)
    print(k, ":", s[:1500])

"""Session 10225: print restate.json's picks (day and value) and the drawn page's shown text for the doc's tables."""
import json
import sys

d = json.load(open(sys.argv[1], encoding="utf-8"))
for k, v in d["info"].items():
    if ".study." in k or ".wc." in k:
        continue
    print(k, v)
for k, v in d["info"].items():
    if ".wc.reached" in k:
        print(k, v)
for k, v in sorted(d["figures"].items()):
    if "|pooled" in k or "weather_share" in k:
        print(k, round(v, 4))

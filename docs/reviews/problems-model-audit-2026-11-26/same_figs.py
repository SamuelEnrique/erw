"""Session 10229: are the keyed figures of two drawings the same (key, value, printed string), set by set?"""
import json
import sys

a, b = (json.load(open(p, encoding="utf-8")) for p in sys.argv[1:3])
for slug in a:
    fa = [(q["id"], f["k"], f["v"], f["shown"]) for q in a[slug]["questions"] for f in q["figures"]]
    fb = [(q["id"], f["k"], f["v"], f["shown"]) for q in b[slug]["questions"] for f in q["figures"]]
    print(f"{slug}: {len(fa)} and {len(fb)} figures; {'the same' if sorted(fa) == sorted(fb) else 'DIFFERENT'}")

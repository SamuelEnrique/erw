# Session 10215: prints the keys of a figures file (lib.json or restate.json) whose names start with any of the
# prefixes given, sorted, plus the words of lib.json.
#   python runs/c10215/show.py <file.json> <prefix> [prefix ...]
import json
import sys

d = json.load(open(sys.argv[1], encoding="utf-8"))
for k in sorted(d["figures"]):
    if any(k.startswith(p) for p in sys.argv[2:]):
        print(f"{k} = {d['figures'][k]}")
for k, v in sorted(d.get("words", {}).items()):
    if any(k.startswith(p) for p in sys.argv[2:]):
        print(f"[words] {k} = {v}")

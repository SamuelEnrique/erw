"""Session 11402: print the shape of the forecast's page files (keys, a few values), read only."""
import json
import os
import sys

D = os.path.join(os.path.dirname(__file__), "..", "..", "..", "site", "data", "predict")


def shape(x, depth=0, maxd=4):
    pad = "  " * depth
    if isinstance(x, dict):
        for k, v in list(x.items())[:40]:
            if isinstance(v, (dict, list)) and depth < maxd:
                n = len(v)
                print(f"{pad}{k}: {type(v).__name__}[{n}]")
                if isinstance(v, list) and v and not isinstance(v[0], (dict, list)):
                    print(f"{pad}  e.g. {v[:6]}")
                elif isinstance(v, list) and v:
                    shape(v[0], depth + 1, maxd)
                else:
                    shape(v, depth + 1, maxd)
            else:
                s = repr(v)
                print(f"{pad}{k}: {s[:160]}")
    elif isinstance(x, list):
        print(f"{pad}{repr(x)[:200]}")


for name in sys.argv[1:]:
    with open(os.path.join(D, name), encoding="utf-8") as f:
        d = json.load(f)
    print("=====", name)
    shape(d)

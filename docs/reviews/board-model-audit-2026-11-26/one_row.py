# Session 10206: one public row of the board against its series file's last points (ids given; held grids refused).
import datetime as dt
import json
import os
import sys

SITE = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "..", "site")
B = json.load(open(os.path.join(SITE, "data", "board.json"), encoding="utf-8"))
for rid in sys.argv[1:]:
    if rid.startswith(("nyiso", "isone", "miso", "pjm")):
        print(rid, "held: not printed")
        continue
    r = next(x for x in B["rows"] if x["id"] == rid)
    print(json.dumps({k: v for k, v in r.items() if k != "spark"})[:2500])
    sp = r.get("spark")
    if sp:
        t0 = dt.date.fromisoformat(sp["t0"])
        print("trend:", [(str(t0 + dt.timedelta(days=d)), v) for d, v in zip(sp["d"], sp["v"])][-40:])
    f = json.load(open(os.path.join(SITE, "public", "board", "s", rid + ".json"), encoding="utf-8"))
    t0 = dt.date.fromisoformat(f["t0"])
    print("series, last 40:", [(str(t0 + dt.timedelta(days=d)), v) for d, v in zip(f["d"], f["v"])][-40:])

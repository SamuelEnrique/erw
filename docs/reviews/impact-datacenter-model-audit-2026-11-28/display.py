"""Session 11404: every printed text of page.json written again from the restated figure, by the rule the page's note
gives (jobs one decimal under 100 and whole from 100; dollars in billions to two decimals, millions to one, else whole)."""
import json
from decimal import ROUND_HALF_EVEN, ROUND_HALF_UP, Decimal

P = json.load(open("runs/c770/s11404/page.json"))
R = json.load(open("runs/c770/s11404/restated.json"))["runs"]


def fmt(v, d):
    # toLocaleString rounds half away from zero (halfExpand) on the exact binary value; Decimal(v) is that exact value
    q = Decimal(v).quantize(Decimal(1).scaleb(-d), rounding=ROUND_HALF_UP)
    s = f"{q:,.{d}f}"
    if "." in s:
        s = s.rstrip("0").rstrip(".")
    return s


def text(name, v):
    p = name.split(":")
    if "jobs" in p[1:3]:
        return fmt(v, 1 if v < 100 else 0)
    a = abs(v)
    if a >= 1e9:
        return f"USD {fmt(v / 1e9, 2)} billion"
    if a >= 1e6:
        return f"USD {fmt(v / 1e6, 1)} million"
    return f"USD {fmt(round(v), 0)}"


key = {"c:jobs:total": "cjobs", "c:earnings:total": "cearn", "o:jobs:total": "ojobs", "o:earnings:total": "oearn"}
n = bad = 0
for cid, c in P.items():
    if cid.startswith("_") or not c["ok"]:
        continue
    r = R[cid]
    for name, f in c["figs"].items():
        if f["v"] is None:
            continue
        if name in key:
            v = r[key[name]]
        elif name.startswith("sum:") and name[4:] in r["sum"]:
            v = r["sum"][name[4:]]
        elif name.startswith("pv:") and name[3:] in r["pv"]:
            v = r["pv"][name[3:]]
        elif name.startswith("y1:") and name[3:] in r["y1"]:
            v = r["y1"][name[3:]]
        else:
            continue
        n += 1
        if text(name, v) != f["text"]:
            bad += 1
            print(cid, name, f["text"], "restated:", text(name, v))
print(f"printed texts compared {n}, differences {bad}")

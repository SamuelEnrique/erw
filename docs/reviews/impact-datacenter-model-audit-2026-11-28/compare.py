"""Session 11404: the page's own figures (page.json, dc_page.mjs) against the restatement (restated.json, restate.py)."""
import json

P = json.load(open("runs/c770/s11404/page.json"))
R = json.load(open("runs/c770/s11404/restated.json"))
TOL = 1e-9


def same(a, b):
    if a is None or b is None:
        return a is None and b is None
    return abs(a - b) <= TOL * max(1.0, abs(a))


n = 0
bad = []
for cid, rr in R["runs"].items():
    pp = P[cid]
    x = rr["x"]
    for k, v in x.items():
        pv = pp["x"].get(k)
        n += 1
        if isinstance(v, (int, float)) and not isinstance(v, bool) and isinstance(pv, (int, float)) and not isinstance(pv, bool):
            if not same(v, pv):
                bad.append((cid, "input " + k, pv, v))
        elif v != pv:
            bad.append((cid, "input " + k, pv, v))
    if not pp["ok"]:
        bad.append((cid, "page not ok", pp["why"], None))
        continue
    f = pp["figs"]
    pairs = [("c:jobs:total", rr["cjobs"]), ("c:earnings:total", rr["cearn"]), ("o:jobs:total", rr["ojobs"]), ("o:earnings:total", rr["oearn"]),
             ("c:jobs:onsite", rr["c_onsite"]), ("o:jobs:onsite", rr["o_onsite"]), ("sum:jobs", rr["sum"]["jobs"]), ("sum:earnings", rr["sum"]["earnings"]),
             ("y1:property", rr["y1"]["property"]), ("y1:propb", rr["y1"]["propb"]), ("y1:prope", rr["y1"]["prope"]), ("y1:elec", rr["y1"]["elec"]),
             ("pv:taxes", rr["pv"]["taxes"]), ("pv:earnings", rr["pv"]["earnings"])]
    for s in ("property", "sales", "income", "salesbefore", "forgone"):
        pairs.append((f"sum:{s}", rr["sum"][s]))
    for s in ("sales", "income", "property", "elec", "forgone"):
        pairs.append((f"pv:{s}", rr["pv"][s]))
    for name, v in pairs:
        n += 1
        if not same(f[name]["v"], v):
            bad.append((cid, name, f[name]["v"], v))
    for py, ry in zip(pp["years"], rr["years"]):
        for k in ("jobs", "earnings", "equipment", "property", "propb", "prope", "salesbefore", "forgone", "sales", "income", "elec"):
            n += 1
            if not same(py[k], ry[k]):
                bad.append((cid, f"{py['year']} {k}", py[k], ry[k]))
    if len(pp["years"]) != len(rr["years"]):
        bad.append((cid, "years", len(pp["years"]), len(rr["years"])))
print(f"cases {len(R['runs'])}, numbers compared {n}, differences {len(bad)}")
for b in bad[:60]:
    print(b)

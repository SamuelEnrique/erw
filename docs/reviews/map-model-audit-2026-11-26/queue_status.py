"""Session 10216: the queue positions' own status words (the card's) against the map's status, by grid, from map.json."""
import collections
import json
import os

HERE = os.path.dirname(os.path.abspath(__file__))
SITE = os.path.abspath(os.path.join(HERE, "..", "..", "site"))
f = json.load(open(os.path.join(SITE, "data", "map.json"), encoding="utf-8"))
q0 = f["kinds"][2]["start"]
mq = f["more"]["queue"]
c = collections.Counter()
mw = collections.Counter()
prop = collections.Counter()
for j in range(f["kinds"][2]["rows"]):
    i = q0 + j
    key = (f["grids"][f["g"][i]]["slug"], f["statuses"][f["st"][i]]["slug"], mq["statuses"][mq["status"][j]])
    c[key] += 1
    mw[key] += f["mw"][i] or 0
    prop[(key[0], key[1], bool(mq["proposed"][j]))] += 1
for k in sorted(c):
    print(k, c[k], round(mw[k], 1))
print("proposed date held, by grid and status:", sorted(prop.items()))
# the ERCOT completed rows: their dates (entry to queue) and proposed in-service dates
er = [q0 + j for j in range(f["kinds"][2]["rows"]) if f["grids"][f["g"][q0 + j]]["slug"] == "ercot" and f["statuses"][f["st"][q0 + j]]["slug"] == "q-completed"]
pd_ = [mq["proposed"][i - q0] for i in er]
print("ERCOT completed:", len(er), "proposed dates before 2026-11:", sum(1 for d in pd_ if d and d < 20261100), "after:", sum(1 for d in pd_ if d and d >= 20261100), "none:", sum(1 for d in pd_ if not d))

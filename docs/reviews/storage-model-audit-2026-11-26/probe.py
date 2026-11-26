"""Session 10212 (storage audit): what the main copy holds for the storage page's tables (read only)."""
import csv
import collections
import os
import sys

SRC = sys.argv[1]


def rows(name):
    with open(os.path.join(SRC, name + ".csv"), encoding="utf-8", newline="") as f:
        head = []
        lines = []
        for line in f:
            if line.startswith("#"):
                head.append(line.rstrip())
            else:
                lines.append(line)
        return head, csv.DictReader(lines)


for t in ["storage_capacity", "eia860m_operating_generators", "eia860m_planned_generators", "eia860m_retired_generators"]:
    head, r = rows(t)
    vint = collections.Counter()
    st = collections.Counter()
    n = 0
    for x in r:
        if t != "storage_capacity" and x.get("prime_mover") != "BA":
            continue
        n += 1
        vint[x.get("vintage")] += 1
        st[(x.get("status"), x.get("eia_status"))] += 1
    print(t, n, dict(vint), dict(st))
    for h in head[:3]:
        print("   ", h[:200])

for t in ["storage_daily_cycle", "eia930_all_storage", "caiso_battery_storage", "storage_buildout_monthly"]:
    head, r = rows(t)
    rng = {}
    for x in r:
        k = (x["entity"], x["variable"])
        a = rng.get(k)
        ts = x["ts_utc"]
        if a is None:
            rng[k] = [ts, ts, 1]
        else:
            a[0] = min(a[0], ts)
            a[1] = max(a[1], ts)
            a[2] += 1
    print(t, len(rng), "keys")
    for k, v in sorted(rng.items())[:40]:
        print("   ", k, v)
    for h in head[:3]:
        print("   ", h[:200])

"""Session 10212 (storage audit): the rows the storage page's live reads would get, from the trial folder's tables.

    python fixture.py <trial dir> <out fixture.json> <since ts for the hourly and 5-minute reads>

The fleet tab reads storage_capacity (entities: entity_id, capacity_mw, status and five fields of extra), the daily
cycle since 45 days before "now", eia930_all_storage and caiso_battery_storage since 31 days before "now". The build-out
tab reads storage_buildout_monthly. Rows are written as the live set returns them (numbers as numbers, extra fields as
text, an empty extra field as null).
"""
import csv
import json
import os
import sys

src, out, since = sys.argv[1], sys.argv[2], sys.argv[3]


def read(name):
    with open(os.path.join(src, name + ".csv"), encoding="utf-8", newline="") as f:
        return list(csv.DictReader(line for line in f if not line.startswith("#")))


fx = {}
units = []
for x in read("storage_capacity"):
    units.append({
        "entity_id": x["entity_id"], "capacity_mw": float(x["capacity_mw"]) if x["capacity_mw"] != "" else None,
        "status": x["status"] or None, "state": x["state"] or None, "iso": x["iso"] or None,
        "planned_year": x["planned_year"] or None, "mwh": x["energy_capacity_mwh"] or None, "vintage": x["vintage"] or None,
    })
units.sort(key=lambda r: r["entity_id"])
fx["storage_capacity"] = units


def series(name, keep):
    rows = []
    for x in read(name):
        if not keep(x):
            continue
        rows.append({"entity": x["entity"], "variable": x["variable"], "ts_utc": x["ts_utc"], "value": float(x["value"]),
                     "unit": x["unit"], "freq": x["freq"]})
    rows.sort(key=lambda r: (r["entity"], r["variable"], r["ts_utc"]))
    return rows


fx["storage_daily_cycle"] = series("storage_daily_cycle", lambda x: x["ts_utc"] >= "2026-09-01")
fx["eia930_all_storage"] = series("eia930_all_storage", lambda x: x["ts_utc"] >= since)
fx["caiso_battery_storage"] = series("caiso_battery_storage", lambda x: x["ts_utc"] >= since and x["variable"] == "batteries_mw")
fx["storage_buildout_monthly"] = series("storage_buildout_monthly", lambda x: True)
for k, v in fx.items():
    print(k, len(v))
with open(out, "w", encoding="utf-8") as f:
    json.dump(fx, f)

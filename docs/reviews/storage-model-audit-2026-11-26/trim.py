"""Session 10212 (storage audit): copy the storage page's inputs from the main copy (read only) into a trial folder.

    python trim.py <main copy warehouse/output> <trial dir> <first ts_utc kept for the hourly and 5-minute tables>

The EIA-860M tables are copied whole. eia930_all_storage and caiso_battery_storage are copied line by line from the
first timestamp kept (this machine reads no more than a year of an hourly table at once); header lines are kept.
Nothing is written to the main copy.
"""
import os
import shutil
import sys

src, dst, first = sys.argv[1], sys.argv[2], sys.argv[3]
os.makedirs(dst, exist_ok=True)
for t in ["eia860m_operating_generators", "eia860m_planned_generators", "eia860m_retired_generators"]:
    shutil.copyfile(os.path.join(src, t + ".csv"), os.path.join(dst, t + ".csv"))
    print("copied", t)
for t in ["eia930_all_storage", "caiso_battery_storage"]:
    kept = dropped = 0
    with open(os.path.join(src, t + ".csv"), encoding="utf-8", newline="") as f, \
            open(os.path.join(dst, t + ".csv"), "w", encoding="utf-8", newline="") as g:
        cols = None
        ts_i = None
        for line in f:
            if line.startswith("#"):
                g.write(line)
                continue
            if cols is None:
                cols = line.rstrip("\r\n").split(",")
                ts_i = cols.index("ts_utc")
                g.write(line)
                continue
            ts = line.split(",")[ts_i]
            if ts >= first:
                g.write(line)
                kept += 1
            else:
                dropped += 1
    print(t, "kept", kept, "dropped", dropped)

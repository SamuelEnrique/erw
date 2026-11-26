# Session 10206: copies of the main copy's table files for drawing /cost-of-power, cut to one year so no more than one
# year of an hourly table is held at once. The main copy is read only; the copies go to runs/c10206/tables.
import os
import shutil
import sys

SRC = r"C:\Users\lossa\Documents\erw\warehouse\output"
DST = os.path.join(os.path.dirname(os.path.abspath(__file__)), "tables")
CUT = "2025-11-01"
WHOLE = sys.argv[1:] or ["carbon_intensity_monthly", "ercot_4cp_intervals"]
BAS = ("eia930:ERCO", "eia930:CISO", "eia930:NYIS", "eia930:ISNE", "eia930:SWPP")

FILTERS = {
    "carbon_intensity_hourly": lambda f: f[0] in BAS and f[1] == "intensity_demand",
    "ercot_rtm_price_adders": lambda f: f[0] == "ercot:system" and f[1] == "rtorpa_mean",
    "scarcity_hours_by_grid": lambda f: f[1] in ("rt_hour_ge_1000", "own_signal"),
}

os.makedirs(DST, exist_ok=True)
for name in WHOLE:
    p = os.path.join(SRC, name + ".csv")
    if os.path.exists(p):
        shutil.copyfile(p, os.path.join(DST, name + ".csv"))
        print("copied", name)
    else:
        print("not on this machine", name)

for name, keep in FILTERS.items():
    n = 0
    with open(os.path.join(SRC, name + ".csv"), encoding="utf-8") as src, open(os.path.join(DST, name + ".csv"), "w", encoding="utf-8", newline="") as out:
        head = None
        for line in src:
            if head is None:
                if line.startswith("#"):
                    out.write(line)
                    continue
                head = line
                out.write(line)
                continue
            f = line.split(",", 3)
            if len(f) < 4 or f[2] < CUT:
                continue
            if keep(f):
                out.write(line)
                n += 1
    print(name, n, "rows from", CUT)

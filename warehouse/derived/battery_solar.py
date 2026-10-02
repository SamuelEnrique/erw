#!/usr/bin/env python3
"""The home battery game's solar shapes (session 66): for each famous day in site/data/battery_levels.json, the hourly
output of the grid's whole solar fleet per MW installed, on that day, written into the level as `solar` (one value per
15-minute interval: each hour's value on its four intervals) with `solar_source`. The game's rooftop solar add-on (a
5 kW array, a game rule; site/lib/battery.ts) multiplies it by 5 kW.

Energy Research Warehouse (ERW). The shape is the one the cost-of-power seller tab uses for a solar farm
(warehouse/derived/merchant_revenue.py, whose functions this script calls, so the two cannot differ):

    EIA-930 hourly generation by fuel, the balancing authority's "Adjusted SUN Gen" (MWh in the hour, from the BA
    workbook under warehouse/raw/eia930_emissions/), over the solar nameplate installed in that balancing authority at
    the start of the day's month (EIA-860M operating and retired generators, by operating and retirement month).

It is a fleet average, not one roof, and the page says so. ERCOT levels read ERCO, CAISO levels CISO.

Real data only. A level gets a shape only when every hour of its day is held with a number and the month's installed
solar capacity is above zero; otherwise the level is left without one (any older `solar` is removed), the reason is
logged in the file's `solar_log`, and the add-on is unavailable for that level. Nothing is filled, carried forward or
interpolated. Values are written as EIA reports them, negative hours (station use at night) and hours above nameplate
(EIA-860M lists new plants late) included; the game keeps them between 0 and 1 when it uses them, and says so.

The prices, dates and every other field of each level are left exactly as they are. Run it after
warehouse/derived/battery_levels.py, which writes the California levels anew (without a shape) each time it runs.

    python warehouse/derived/battery_solar.py            # write the shapes into site/data/battery_levels.json
    python warehouse/derived/battery_solar.py --dry-run  # say what would be written, write nothing

Needs the BA workbooks (raw files, not in git) and warehouse/output/eia860m_operating_generators.csv and
eia860m_retired_generators.csv, so it runs on the machine that holds them. Session 66 wrote it and did not run it.
"""

import datetime as dt
import json
import os
import sys

import pandas as pd

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.abspath(os.path.join(HERE, "..", ".."))
OUT = os.path.join(ROOT, "site", "data", "battery_levels.json")
GRID_BA = {"ERCOT": "ERCO", "CAISO": "CISO"}  # a level's grid to its EIA-930 balancing authority
SOURCE_URL = "https://www.eia.gov/electricity/gridmonitor/"


def shape_for(level, fuel, cap_mw):
    """The level's solar shape, or (None, why). fuel: a frame indexed by the UTC start of each hour with a column `sun`
    (MWh in the hour); cap_mw: the solar nameplate installed that month. One value per interval of the level: the
    interval's hour's output over the nameplate, as EIA reports it. Every hour must be held with a number."""
    if not cap_mw or cap_mw <= 0:
        return None, "no solar nameplate installed that month in EIA-860M"
    out = []
    for ts in level["ts_utc"]:
        t = pd.Timestamp(ts)
        hour = (t.tz_localize("UTC") if t.tzinfo is None else t.tz_convert("UTC")).floor("h")
        if hour not in fuel.index:
            return None, f"the hour {hour:%Y-%m-%dT%H:00Z} is not in the EIA-930 workbook"
        v = fuel.at[hour, "sun"]
        if pd.isna(v):
            return None, f"the hour {hour:%Y-%m-%dT%H:00Z} has no solar generation in the EIA-930 workbook"
        out.append(round(float(v) / float(cap_mw), 6))
    return out, ""


def build(levels, fuel_of, cap_of, built):
    """Write `solar` and `solar_source` into each level that has a whole shape, remove them from each that has not.
    fuel_of(ba) -> (frame, where it was read from); cap_of(ba, month) -> (MW, the EIA-860M vintages). Returns the log."""
    log = []
    for lv in levels:
        grid = lv.get("grid", "ERCOT")
        lv.pop("solar", None)
        lv.pop("solar_source", None)
        ba = GRID_BA.get(grid)
        if ba is None:
            log.append(f"{lv['date']} ({lv['slug']}): no balancing authority for the grid {grid}; no shape")
            continue
        fuel, where = fuel_of(ba)
        month = lv["date"][:7]
        cap, vint = cap_of(ba, month)
        shape, why = shape_for(lv, fuel, cap)
        if shape is None:
            log.append(f"{lv['date']} ({lv['slug']}): no shape, {why} ({ba}, {where}); the rooftop add-on is unavailable for this level")
            continue
        lv["solar"] = shape
        lv["solar_source"] = (f"EIA-930 hourly generation by fuel, {ba} (Adjusted SUN Gen; {where}; {SOURCE_URL}), over the "
                              f"{cap:,.1f} MW of solar nameplate installed in {ba} in {month} (EIA-860M operating and retired "
                              f"generators, {', '.join(vint)}): the whole fleet's output per MW installed, not one roof's. "
                              f"Read {built} by warehouse/derived/battery_solar.py.")
        log.append(f"{lv['date']} ({lv['slug']}): {len(shape)} intervals, {ba}, highest hour {max(shape):.4f} of nameplate, "
                   f"lowest {min(shape):.4f}, over {cap:,.1f} MW")
    return log


def main(argv=None):
    argv = sys.argv[1:] if argv is None else argv
    dry = "--dry-run" in argv
    sys.path.insert(0, os.path.join(ROOT, "warehouse", "connectors"))
    sys.path.insert(0, HERE)
    import merchant_revenue as mr  # noqa: E402  (the seller tab's own shape: workbook_of, fuel_hours, read_gens, capacity)

    built = dt.datetime.now(dt.timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
    with open(OUT, encoding="utf-8") as f:
        doc = json.load(f)
    gens, vint = mr.read_gens()
    fuels = {}

    def fuel_of(ba):
        if ba not in fuels:
            path, _ = mr.workbook_of(ba)  # raises, loudly, when the workbook is not on this machine
            fuels[ba] = (mr.fuel_hours(path), os.path.relpath(path, ROOT).replace(os.sep, "/"))
        return fuels[ba]

    log = build(doc["levels"], fuel_of, lambda ba, month: (mr.capacity(gens, ba, "SUN", month), vint), built)
    doc["solar_log"] = log
    doc["solar_note"] = ("Session 66: `solar` is the grid's solar fleet on the level's day, output per MW installed, one value per "
                         "15-minute interval (each hour's value on its four intervals), as EIA reports it; a level without it has no "
                         f"shape held and the game's rooftop add-on is unavailable for it. Written by warehouse/derived/battery_solar.py on {built}.")
    for x in log:
        print(x)
    if dry:
        print("dry run: nothing written")
        return 0
    with open(OUT, "w", encoding="utf-8", newline="\n") as f:
        json.dump(doc, f, indent=1)
        f.write("\n")
    n = sum(1 for lv in doc["levels"] if "solar" in lv)
    print(f"wrote {os.path.relpath(OUT, ROOT)}: a solar shape on {n} of {len(doc['levels'])} levels")
    return 0


if __name__ == "__main__":
    sys.exit(main())

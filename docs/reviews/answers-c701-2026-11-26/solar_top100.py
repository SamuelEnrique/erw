"""Data request 9 of docs/state/data_requests_five_tools.md (the Automated Analysis audit, finding 3): ERCOT's solar in
the 100 hours of highest DEMAND each year, as a percent of its installed capacity, beside grid_stress_yearly's figure for
the 100 hours of highest NET LOAD. Runs warehouse/derived/mix_stress.py's own grid_rows (its hour rules, its capacity from
EIA's generator inventory) twice, the second time with the ranking key "net" read as "demand". Writes nothing under
warehouse/output; prints a table."""
import os
import sys

import pandas as pd

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
sys.path.insert(0, os.path.join(ROOT, "warehouse", "derived"))
sys.path.insert(0, os.path.join(ROOT, "warehouse", "connectors"))
import mix_stress as ms  # noqa: E402

log = lambda m: None  # noqa: E731
caps = ms.capacity()
x, path = ms.mp.hours_of("ercot", log)
mw, mwh = ms.fleet("ercot")
by_net = ms.grid_rows("ercot", x, caps, mw, mwh, "", log)

orig = pd.DataFrame.nlargest


def by_demand(self, n, columns, keep="first"):
    return orig(self, n, "demand" if columns == "net" else columns, keep)


pd.DataFrame.nlargest = by_demand
try:
    by_dem = ms.grid_rows("ercot", x, caps, mw, mwh, "", log)
finally:
    pd.DataFrame.nlargest = orig


def pick(rows, var):
    return {r["ts_utc"][:4]: r["value"] for r in rows if r["variable"] == var}


net = pick(by_net, "tight_solar_share_of_capacity_pct")
dem = pick(by_dem, "tight_solar_share_of_capacity_pct")
cap = pick(by_net, "capacity_solar_mw")
print("source:", os.path.relpath(path, ROOT))
print("year | solar, 100 highest-demand hours, pct of capacity | solar, 100 highest-net-load hours (grid_stress_yearly's rule) | difference")
for y in sorted(set(net) | set(dem)):
    if "2019" <= y <= "2025":
        a, b = dem.get(y), net.get(y)
        print(f"{y} | {a} | {b} | {None if a is None or b is None else round(a - b, 3)}")

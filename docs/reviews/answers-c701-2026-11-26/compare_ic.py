"""Window D's data request 54, the second half: the interconnection explorer's default view (CAISO, positions, entry years
1999 to 2023; and the three queues' entry year 2023) restated by the explorers audit's own restate_ic.stats from the queue
pulls the 23 November build of iso_queue_statistics read (restored from the ERW's archive as of that run), beside the
table's rows (positions_entered, _operating, _withdrawn, _waiting, _status_not_stated). Counts only."""
import importlib.util
import sys

import pandas as pd

sys.path.insert(0, "warehouse/connectors")
import iso_prices as ip  # noqa: E402

spec = importlib.util.spec_from_file_location("restate_ic", "runs/c701/queues/restate_ic.py")
R = importlib.util.module_from_spec(spec)
spec.loader.exec_module(R)
p = "warehouse/output/iso_queue_statistics.csv"
q = pd.read_csv(p, skiprows=ip.header_rows(p), dtype=str, keep_default_na=False)
rows, diffs = 0, []
for iso, years in (("caiso", range(1999, 2024)), ("ercot", [2023]), ("spp", [2023])):
    S = R.stats(iso, f"runs/c701/queues/{iso}_run.csv")
    t = q[q["x_iso"].str.lower() == iso]
    for y in years:
        for k in ("entered", "operating", "withdrawn", "waiting", "status_not_stated"):
            mine = S.get(y, {}).get(k, 0)
            x = t[(t["variable"] == f"positions_{k}") & (t["x_entry_year"] == str(y))]["value"]
            table = int(float(x.iloc[0])) if len(x) else None
            rows += 1
            if table != mine:
                diffs.append((iso, y, k, mine, table))
print("figures compared:", rows, "| equal:", rows - len(diffs), "| differ:", len(diffs))
for d in diffs[:30]:
    print("  differs:", d)

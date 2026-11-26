"""Session 10214 (demand audit): how many hours of EIA's "Adjusted demand" are not the balancing authority's own reported
"Demand": held where Demand is blank (EIA filled the hour), or held with another value (EIA replaced it). From the
extract of the workbooks of 3 October 2026 (extract.py), local years 2019 to 2025. Standard library; each file streamed.

Usage: python imputed.py <hours dir> <out json>
"""
import csv
import json
import sys
from collections import defaultdict
from datetime import datetime, timezone
from zoneinfo import ZoneInfo

AREAS = {"ERCO": "America/Chicago", "CISO": "America/Los_Angeles", "PJM": "America/New_York", "MISO": "America/Chicago",
         "SWPP": "America/Chicago", "NYIS": "America/New_York", "ISNE": "America/New_York"}


def main(hours, out):
    res = {}
    for ba, tzn in AREAS.items():
        tz = ZoneInfo(tzn)
        c = defaultdict(lambda: {"hours": 0, "filled": 0, "replaced": 0, "replaced_abs_mwh": 0.0, "net_mwh": 0.0, "largest": 0.0})
        with open(f"{hours}/{ba}.csv", newline="", encoding="utf-8") as f:
            for r in csv.DictReader(f):
                ts = datetime.strptime(r["ts_start_utc"], "%Y-%m-%dT%H:%M:%SZ").replace(tzinfo=timezone.utc)
                y = ts.astimezone(tz).year
                if not 2019 <= y <= 2025:
                    continue
                x = c[y]
                x["hours"] += 1
                d = float(r["demand"]) if r["demand"] else None
                a = float(r["adjusted_demand"]) if r["adjusted_demand"] else None
                if a is None:
                    continue
                if d is None:
                    x["filled"] += 1
                    x["net_mwh"] += a
                elif abs(a - d) > 0.5:
                    x["replaced"] += 1
                    x["replaced_abs_mwh"] += abs(a - d)
                    x["net_mwh"] += a - d
                    x["largest"] = max(x["largest"], abs(a - d))
        res[ba] = {str(y): v for y, v in sorted(c.items())}
        tot = {k: sum(v[k] for v in c.values()) for k in ("hours", "filled", "replaced")}
        print(f"{ba}: {tot['filled']:,} hours filled and {tot['replaced']:,} replaced by EIA of {tot['hours']:,} (2019 to 2025); by year: "
              + "; ".join(f"{y} {v['filled']}+{v['replaced']} (net {v['net_mwh'] / v['hours']:+.1f} MW on the year's mean, largest change {v['largest']:,.0f})" for y, v in sorted(c.items())))
    json.dump(res, open(out, "w", encoding="utf-8"), indent=1)


if __name__ == "__main__":
    main(sys.argv[1], sys.argv[2])

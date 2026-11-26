"""Session 10225: CAISO's notices of 14 and 15 August 2020 in caiso_grid_emergencies (main copy, read only): kind, start,
end and the printed time frame, short."""
import csv
import sys

with open(sys.argv[1], encoding="utf-8") as fh:
    rows = list(csv.DictReader(l for l in fh if not l.startswith("#")))
cols = list(rows[0].keys())
print(cols)
for r in rows:
    if r.get("event_date", "")[:10] in ("2020-08-14", "2020-08-15"):
        print({k: (r[k] or "")[:100] for k in ("event_date", "event_type", "x_label", "x_region", "x_time_frame", "x_start", "x_end")})

"""Session 11404: every construction headcount the announced rows state, against the default campus's 10,000 a year."""
import json

A = json.load(open("site/data/forecast/datacenter_announced.json", encoding="utf-8"))
rows = [(r["construction_jobs"]["value"], r["id"], (r.get("investment") or {}).get("value"), r["construction_jobs"].get("measure"), r.get("to_date", False))
        for r in A["rows"] if r.get("construction_jobs")]
rows.sort(reverse=True)
print("rows stating construction jobs:", len(rows))
for v, i, inv, m, td in rows[:8]:
    print(f"  {v:>6} {i} invest {inv} | {m} | to_date {td}")
print("default campus: invest 12,000 million, workers a year", round(12 * A["defaults"]["construction_jobs_per_billion"]["median"], 1))

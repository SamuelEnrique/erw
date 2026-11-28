"""Session 11404: the investment a MW of each row in the median, and the counts the note's decisions quote."""
import json
import statistics

A = json.load(open("site/data/forecast/datacenter_announced.json", encoding="utf-8"))
idx = json.load(open("site/data/forecast/deflator.json"))["index"]
rows = {r["id"]: r for r in A["rows"]}
v = []
for i in A["defaults"]["investment_per_mw"]["rows"]:
    r = rows[i]
    inv = r["investment"]["value"] * (idx["2025"] / idx[str(r["investment"]["year"])] if str(r["investment"]["year"]) in idx else 1)
    v.append(inv / 1e6 / r["mw"]["value"])
    print(f"  {i}: {v[-1]:.2f}")
print("mean", round(statistics.mean(v), 4), "median", statistics.median(v))
print("rows in medians (not to date):", sum(1 for r in A["rows"] if not r.get("to_date")))
print("n by default:", {k: d["n"] for k, d in A["defaults"].items()})
d = A["defaults"]
print("by investment for the default:", round(1000 * d["investment_per_mw"]["median"] / 1000 * d["permanent_jobs_per_billion"]["median"], 1),
      "by MW:", round(1000 * d["permanent_jobs_per_mw"]["median"], 1))

"""Window D's data request 59 (the Digest audit): the charts of 22 October, 23 October and 6 November 2026 re-done from the
tables this machine holds. For each chart record (docs/digest/charts/<date>.json): its series (entity, variable) in its
table as held now, the value of the month the fact names, the record before it (the highest, or for 6 November the lowest,
earlier value) and its month, and the record's figures beside them. Counts only."""
import json
import sys

import pandas as pd

sys.path.insert(0, "warehouse/connectors")
import iso_prices as ip  # noqa: E402

CASES = [("2026-10-22", "2026-07", "max"), ("2026-10-23", "2026-06", "max"), ("2026-11-06", "2026-08", "min")]
for date, month, kind in CASES:
    c = json.load(open(f"docs/digest/charts/{date}.json", encoding="utf-8"))
    sk = dict(x.split("=", 1) for x in c["series_key"].split("|"))
    p = f"warehouse/output/{c['table']}.csv"
    parts = []
    for ch in pd.read_csv(p, skiprows=ip.header_rows(p), dtype=str, keep_default_na=False, chunksize=500000,
                          usecols=["entity", "variable", "ts_utc", "value"]):
        parts.append(ch[(ch["entity"] == sk["entity"]) & (ch["variable"] == sk["variable"])])
    s = pd.concat(parts)
    s["m"] = s["ts_utc"].str[:7]
    s["v"] = pd.to_numeric(s["value"], errors="coerce")
    s = s.sort_values("m")
    cur = s[s["m"] == month]["v"]
    before = s[s["m"] < month]
    rec = before.loc[before["v"].idxmax()] if kind == "max" else before.loc[before["v"].idxmin()]
    print(f"== {date} ({c['table']}): {len(s)} months held, {s['m'].min()} to {s['m'].max()}")
    print(f"   {month}: {cur.iloc[0] if len(cur) else 'not held'} | the record before it: {rec['v']} in {rec['m']}")
    print(f"   the record's fact: {c['fact'][:300]}")
    print(f"   the record's numbers: {json.dumps(c.get('numbers'))[:300]}")

"""Request 57 (chain 701): each held table built without and with the impossible-values rule (runs/c701/trial57/before and
after, from the same inputs of 26 November). Prints, per table: rows before and after, keys gone and new, numeric values
that change (by more than 1e-9 relative), the largest change with its key, and main's own copy's rows for reference.
Counts and single cells only; the tables are the ERW's derived tables."""
import os
import sys

import pandas as pd

sys.path.insert(0, "warehouse/connectors")
import iso_prices as ip  # noqa: E402

TABLES = ["carbon_intensity_hourly", "carbon_intensity_daily", "carbon_intensity_monthly", "cost_of_power_monthly",
          "cost_of_power_carbon", "ai_power_regions", "caiso_reliability_daily", "event_window_daily"]
SKIP = {"retrieved_at", "vintage", "source", "source_url", "unit", "freq", "note", "method", "built_utc"}


def read(p):
    return pd.read_csv(p, skiprows=ip.header_rows(p), dtype=str, keep_default_na=False)


for t in TABLES:
    b = read(f"runs/c701/trial57/before/{t}.csv")
    a = read(f"runs/c701/trial57/after/{t}.csv")
    m = read(f"warehouse/output/{t}.csv")
    key = [c for c in ("entity", "variable", "ts_utc") if c in b.columns]
    if not key:
        key = [c for c in b.columns if not pd.to_numeric(b[c], errors="coerce").notna().all() and c not in SKIP][:4]
    num = [c for c in b.columns if c not in key and c not in SKIP and pd.to_numeric(b[c].replace("", None), errors="coerce").notna().any()]
    kb, ka = set(map(tuple, b[key].values)), set(map(tuple, a[key].values))
    j = b.merge(a, on=key, suffixes=("_b", "_a"))
    changed, big = 0, (0.0, None)
    for c in num:
        x = pd.to_numeric(j[c + "_b"], errors="coerce")
        y = pd.to_numeric(j[c + "_a"], errors="coerce")
        d = ((x - y).abs() > 1e-9 * x.abs().clip(lower=1)) | (x.isna() != y.isna())
        changed += int(d.sum())
        rel = ((y - x).abs() / x.abs().clip(lower=1e-9)).where(d)
        if rel.notna().any():
            i = rel.idxmax()
            if rel[i] > big[0]:
                big = (float(rel[i]), (c, tuple(j.loc[i, key]), j.loc[i, c + "_b"], j.loc[i, c + "_a"]))
    print(f"{t}: key {key}; rows before {len(b):,}, after {len(a):,} (main's copy {len(m):,}); keys gone {len(kb - ka):,}, new {len(ka - kb):,}; "
          f"values changed {changed:,} in {len(num)} numeric columns")
    if big[1]:
        c, k, x, y = big[1]
        print(f"   largest change: {c} at {k}: {x} -> {y}")
    gone = sorted(kb - ka)
    if gone:
        ents = pd.Series([g[0] for g in gone]).value_counts().head(5).to_dict()
        print(f"   keys gone by {key[0]} (first 5): {ents}")

#!/usr/bin/env python3
"""Print what a table holds, for writing a grid's table guide (session 92; warehouse/chat/ercot.py CARDS).

Energy Research Warehouse (ERW).   python warehouse/chat/look_tables.py <table> [<table> ...]

For a series table: its entities (those that look like ERCOT's first), partition columns, variables, units, frequency
and span. For an entities or events table: the values of its short text columns. Reads the erw package's backend.
"""
import sys, json
sys.path.insert(0, "package/src")
import erw, pandas as pd
erw.set_backend()
names = sys.argv[1:]
for n in names:
    try:
        df = erw.fetch(n, ba="erco") if n in ("eia930_all_demand","eia930_all_generation","eia930_all_storage","storage_daily_cycle","carbon_intensity_daily","carbon_intensity_monthly") else erw.fetch(n)
    except Exception as e:
        print(n, "FETCH FAILED", type(e).__name__, str(e)[:200]); continue
    cols = list(df.columns)
    print(f"== {n}: {len(df)} rows; cols {cols}")
    if "entity" in cols:
        ents = sorted(df["entity"].unique())
        er = [e for e in ents if "ercot" in e.lower() or "erco" in e.lower() or e.lower().endswith(":tx")]
        print("   entities", len(ents), "ercot-like:", er[:25], "| sample:", ents[:8])
        for c in ("ba", "market", "event", "year", "iso"):
            if c in cols: print("   ", c, sorted(map(str, df[c].unique()))[:20])
        sub = df[df["entity"].isin(er)] if er else df
        vs = sorted(sub["variable"].unique())
        print("   variables", len(vs), vs[:45])
        print("   units", sorted(sub["unit"].unique())[:8], "freq", sorted(sub["freq"].unique()), "span", sub["ts_utc"].min(), sub["ts_utc"].max(), "rows", len(sub))
    else:
        for c in cols:
            if df[c].dtype == object and c not in ("entity_id","event_id","name","source_url"):
                vc = df[c].value_counts()
                if len(vc) <= 25: print("   ", c, dict(list(vc.items())[:25]))
                elif any("ERCO" in str(k).upper() for k in vc.index[:3000]): print("   ", c, "has ERCO-like:", [k for k in vc.index if "ERCO" in str(k).upper()][:8], "n distinct", len(vc))

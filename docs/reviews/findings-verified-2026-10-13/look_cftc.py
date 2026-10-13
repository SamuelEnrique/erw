"""Session 252: the CFTC draft's weekly change against the contract's whole held history, both names of the contract
joined (the table's node column changed name on 2022-02-08, so the scanner's series begins there)."""
import os

import pandas as pd

ROOT = os.path.dirname(os.path.abspath(__file__))
while not os.path.exists(os.path.join(ROOT, "ARCHITECTURE.md")):   # the repository root, from runs/ or from docs/
    ROOT = os.path.dirname(ROOT)
t = pd.read_csv(os.path.join(ROOT, "warehouse", "output", "cftc_cot_positions.csv"), comment="#", dtype=str, keep_default_na=False)
g = t[(t["entity"] == "cftc:023651") & (t["variable"] == "managed_money_long")].sort_values("ts_utc")
v = pd.to_numeric(g["value"]).reset_index(drop=True)
d = pd.to_datetime(g["ts_utc"].str[:10]).reset_index(drop=True)
ch = v.diff()
ch[d.diff().dt.days > 8] = float("nan")
i = int(d[d == "2026-09-29"].index[0])
prior = ch[:i].dropna()
pc = (v.diff() / v.shift())[:i + 1].dropna()
print(f"weeks held before the flagged one, both names: {len(prior)}, from {d.iloc[0].date()}")
print(f"the flagged change: {ch[i]}; falls larger than it before: {(prior < ch[i]).sum()}; the largest fall before: {prior.min()} on {d[prior.idxmin()].date()}")
print("the five largest falls held:", [(str(d[j].date()), float(ch[j])) for j in ch.dropna().sort_values().head(5).index])
print(f"percent change {pc.iloc[-1] * 100:.2f}; larger percent falls before: {(pc[:-1] < pc.iloc[-1]).sum()} of {len(pc) - 1}")

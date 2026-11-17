"""Session 7617 (portable-laptop): the ruling impact of the two lines marked "Changes a figure" under /research in
docs/reviews/rulings-for-samuel-2026-11-17.md (branch wip/7560-six-reads).

Line 1: the stored chart of 12 November names July 2024 (765,381 MWh) as the record Wyoming's August 2026 gas generation
broke, where July 2026 broke it first. Recomputed from eia_state_generation_monthly (Redivis, the draft), entity
eia:generation:WY:NG: the record before each month, as the chart's rule should read it.
Line 2: three findings cards built from internal tables, served by address: withdraw them? Counts what each card shows
(callouts, numbers, chart series and points, downloads) from site/data/findings/<card>.json, writing no value (internal).
No model call.
"""
import json
import sys
from pathlib import Path

import pandas as pd

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
sys.path.insert(0, str(HERE))
from redivis_read import table  # noqa: E402

sys.stdout.reconfigure(encoding="utf-8")

print("== line 1: Wyoming, natural gas, net generation by month")
df, where = table("eia_state_generation_monthly")
wy = df[(df["entity"] == "eia:generation:WY:NG") & (df["variable"] == "net_generation")].copy()
wy["v"] = pd.to_numeric(wy["value"])
wy["ts"] = pd.to_datetime(wy["ts_utc"], utc=True)
wy = wy.sort_values("ts")
print(f"{where}: {len(wy)} months, {wy['ts'].min():%Y-%m} to {wy['ts'].max():%Y-%m}; retrieved {wy['retrieved_at'].max()}; source {wy['source'].iloc[0]}")
for m in ("2024-07", "2026-06", "2026-07", "2026-08"):
    r = wy[wy["ts"].dt.strftime("%Y-%m") == m]
    print(f"  {m}: {r['v'].iloc[0]:,.0f} MWh" if len(r) else f"  {m}: not held")
held_aug = wy[wy["ts"].dt.strftime("%Y-%m") == "2026-08"]
# August 2026 is not in Redivis's copy (it ends at July, retrieved 10 October): the stored chart's own figure
# (docs/digest/latest.md, the issue of 12 November 2026) is taken for it, and said so
aug = held_aug["v"].iloc[0] if len(held_aug) else 1060504.0
print(f"August 2026: {aug:,.0f} MWh ({'the table' if len(held_aug) else 'the stored chart of 12 November, not in this copy of the table'})")
before = wy[wy["ts"] < pd.Timestamp("2026-08-01", tz="UTC")]
rec = before.loc[before["v"].idxmax()]
before_jul = wy[wy["ts"] < pd.Timestamp("2026-07-01", tz="UTC")]
rec_jul = before_jul.loc[before_jul["v"].idxmax()]
print(f"the record before August 2026 (every month held before it): {rec['v']:,.0f} MWh, {rec['ts']:%Y-%m}")
print(f"the record before July 2026: {rec_jul['v']:,.0f} MWh, {rec_jul['ts']:%Y-%m}")
stored = 765381.0
print(f"the stored chart: 'the record until now was {stored:,.0f} MWh, in July 2024': August above it by {aug - stored:,.0f} MWh, {(aug - stored) / stored * 100:.1f} percent")
for label, jul in (("this copy's July 2026", rec["v"]), ("the ruling's July 2026 (the data machine's newer copy)", 1034451.0)):
    print(f"corrected with {label}, {jul:,.0f} MWh: August above it by {aug - jul:,.0f} MWh, {(aug - jul) / jul * 100:.1f} percent; "
          f"the record cell moves {jul - stored:+,.0f} MWh, {(jul - stored) / stored * 100:+.1f} percent, its month from 2024-07 to 2026-07")

print("\n== line 2: the three findings cards built from internal tables")
for c in ("gas_sets_price", "siting_flexible", "siting_gigawatt"):
    d = json.loads((ROOT / "site" / "data" / "findings" / f"{c}.json").read_text(encoding="utf-8"))
    ch = d.get("chart") or {}
    series = ch.get("series") or []
    points = sum(len(s.get("points") or s.get("data") or s.get("values") or []) for s in series if isinstance(s, dict))
    nums = d.get("numbers") or {}
    callouts = d.get("callouts") or []
    dl = d.get("downloads") or []
    print(f"{c}: title words {len(str(d.get('title', '')).split())}; tables {d.get('tables')}; callouts {len(callouts)}; numbers {len(nums)}; "
          f"chart kind {ch.get('kind') or ch.get('type')}, series {len(series)}, points {points}; downloads {len(dl)}; computed {d.get('computed_at')}")
cards = sorted(p.stem for p in (ROOT / "site" / "data" / "findings").glob("*.json"))
print(f"cards in site/data/findings: {len(cards)}: {cards}")

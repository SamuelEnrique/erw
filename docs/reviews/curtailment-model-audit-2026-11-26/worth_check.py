"""Session 10210 (curtailment audit): "What it is worth" restated from the tables, independent of curtailment_worth.py
(standard library only, written from docs/methods/curtailment.md "What it is worth"), for one calendar year at a time,
and the measures of the audit on the same hours.

    python worth_check.py <main copy warehouse/output> <year> <out.json>

Reads caiso_curtailment_intervals (CAISO's five-minute MW to 2025, hourly MWh from 2026, and its covered-day rows) and
the CAISO hubs' prices (iso_hub_prices_history first, then iso_rtm_hub_prices and iso_dam_hub_prices, the first table
that holds an hour wins), only the rows of the year asked (and a day either side). Nothing is written but out.json.

Rules restated: a five-minute MW is MW x 5/60 MWh; an hour's curtailment is the sum of its intervals (UTC hour); a
month (Pacific) is valued when its covered days are at least 90 percent of its days, over the hours of its covered
days (an hour with no row had none curtailed); real time is the mean of an hour's four 15-minute prices, all four held
(or the hourly price where that resolution holds more hours); an hour with no price is left out of both sides.
"""
import csv
import json
import os
import sys
from collections import defaultdict
from datetime import datetime, timedelta, timezone
from zoneinfo import ZoneInfo

src, year, out = sys.argv[1], int(sys.argv[2]), sys.argv[3]
PT = ZoneInfo("America/Los_Angeles")
lo, hi = f"{year - 1}-12-31", f"{year + 1}-01-02"
HUBS = ["caiso:TH_SP15_GEN-APND", "caiso:TH_NP15_GEN-APND"]
RTM = {"lmp_rtm_15m_mean", "spp_rtm", "lmp_rtm"}
DAM = {"lmp_dam", "spp_dam"}


def rows(path):
    with open(path, encoding="utf-8", newline="") as f:
        yield from csv.DictReader(line for line in f if not line.startswith("#"))


def utc(s):
    return datetime.strptime(s, "%Y-%m-%dT%H:%M:%SZ").replace(tzinfo=timezone.utc)


# curtailment: hourly MWh (UTC hour), the five-minute intervals (for the battery rule), covered days
hour = defaultdict(float)
iv = defaultdict(float)          # interval start -> MWh, all variables summed (as the builder's battery rule)
ivdur = {}
covered = set()
vars_seen = defaultdict(set)
for r in rows(os.path.join(src, "caiso_curtailment_intervals.csv")):
    t = r["ts_utc"]
    if not (lo <= t[:10] <= hi):
        continue
    fq = r["freq"]
    vars_seen[fq].add(r["variable"])
    if fq == "P1D":
        covered.add(t[:10])
        continue
    if fq not in ("PT5M", "PT1H"):
        continue
    v = float(r["value"])
    mwh = v * 5 / 60 if fq == "PT5M" else v
    ts = utc(t)
    hour[ts.replace(minute=0, second=0)] += mwh
    iv[ts] += mwh
    ivdur[ts] = 5 / 60 if fq == "PT5M" else 1.0

# prices: (hub, side, freq, ts) -> value, the first table that holds it wins
price_raw = {}
for tname in ["iso_hub_prices_history", "iso_dam_hub_prices", "iso_rtm_hub_prices"]:
    p = os.path.join(src, f"{tname}.csv")
    if not os.path.exists(p):
        continue
    for r in rows(p):
        if r["entity"] not in HUBS or not (lo <= r["ts_utc"][:10] <= hi):
            continue
        side = "rt" if r["variable"] in RTM else "da" if r["variable"] in DAM else None
        if not side:
            continue
        k = (r["entity"], side, r["freq"], r["ts_utc"])
        if k not in price_raw:
            price_raw[k] = float(r["value"])
by = defaultdict(lambda: defaultdict(list))
for (e, side, fq, t), v in price_raw.items():
    ts = utc(t)
    by[(e, side, fq)][ts.replace(minute=0, second=0)].append(v)
prices = {}
for e in HUBS:
    for side in ("rt", "da"):
        best = None
        for fq in ("PT15M", "PT1H", "PT5M"):
            g = by.get((e, side, fq))
            if not g:
                continue
            need = {"PT15M": 4, "PT5M": 12, "PT1H": 1}[fq]
            h = {ts: round(sum(v) / len(v), 9) for ts, v in g.items() if len(v) == need}
            if best is None or len(h) > len(best[1]):
                best = (fq, h)
        if best:
            prices[(e, side)] = best


def month_hours(y, m):
    a = datetime(y, m, 1, tzinfo=PT).astimezone(timezone.utc)
    b = datetime(y + (m == 12), m % 12 + 1, 1, tzinfo=PT).astimezone(timezone.utc)
    out, t = [], a
    while t < b:
        out.append(t)
        t += timedelta(hours=1)
    return out


def days_in(y, m):
    return (datetime(y + (m == 12), m % 12 + 1, 1) - datetime(y, m, 1)).days


res = {"year": year, "variables": {k: sorted(v) for k, v in vars_seen.items()}, "price_basis": {f"{e}|{s}": v[0] for (e, s), v in prices.items()}, "months": {}}
for m in range(1, 13):
    cov = sorted(d for d in covered if d.startswith(f"{year}-{m:02d}"))
    if len(cov) < 0.9 * days_in(year, m):
        continue
    hs = [t for t in month_hours(year, m) if t.astimezone(PT).strftime("%Y-%m-%d") in cov]
    mrec = {"days_held": len(cov), "hours": len(hs)}
    for e in HUBS:
        for side in ("rt", "da"):
            if (e, side) not in prices:
                continue
            P = prices[(e, side)][1]
            ok = [(hour.get(t, 0.0), P[t]) for t in hs if t in P]
            allh = len(month_hours(year, m))
            if len(ok) < 0.95 * allh:
                mrec[f"{e}|{side}"] = {"missing": f"{len(ok)} of {allh} hours priced"}
                continue
            mwh = sum(c for c, _ in ok)
            usd = sum(c * p for c, p in ok)
            cur = [(c, p) for c, p in ok if c > 0]
            rec = {"hours_priced": len(ok), "hours_curtailed_priced": len(cur), "curtailed_mwh_priced": mwh, "value_usd": usd,
                   "usd_per_mwh": usd / mwh if mwh else None, "neg_pct": 100 * sum(c for c, p in ok if p < 0) / mwh if mwh else None,
                   "under5_pct": 100 * sum(c for c, p in ok if p < 5) / mwh if mwh else None,
                   "price_all": sum(p for _, p in ok) / len(ok), "price_curtailed": sum(p for _, p in cur) / len(cur) if cur else None}
            for th in (1, 10, 100):
                sel = [p for c, p in ok if c >= th]
                rec[f"hours_ge{th}"] = len(sel)
                rec[f"price_ge{th}"] = sum(sel) / len(sel) if sel else None
            rec["mwh_in_hours_under10"] = sum(c for c, _ in ok if 0 < c < 10)
            rec["mwh_in_hours_under100"] = sum(c for c, _ in ok if 0 < c < 100)
            mrec[f"{e}|{side}"] = rec
    # the battery rule per MW, D = 4: on the intervals as held, and on the same energy summed to the hour first
    covs = set(cov)
    day_iv, day_h = defaultdict(float), defaultdict(float)
    for ts, mwh in iv.items():
        d = ts.astimezone(PT).strftime("%Y-%m-%d")
        if d not in covs or mwh <= 0:
            continue
        day_iv[d] += min(1.0 * ivdur[ts], mwh)
    for ts, mwh in hour.items():
        d = ts.astimezone(PT).strftime("%Y-%m-%d")
        if d not in covs or mwh <= 0:
            continue
        day_h[d] += min(1.0, mwh)
    for D in (2, 4, 8):
        mrec[f"absorb{D}_intervals"] = sum(min(v, D) for v in day_iv.values())
        mrec[f"absorb{D}_hourly"] = sum(min(v, D) for v in day_h.values())
    mrec["curtailed_mwh_all"] = sum(hour.get(t, 0.0) for t in hs)
    res["months"][f"{year}-{m:02d}"] = mrec
with open(out, "w", encoding="utf-8") as f:
    json.dump(res, f, indent=1, default=str)
print("months", list(res["months"]), "price basis", res["price_basis"])
print("variables", {k: len(v) for k, v in res["variables"].items()})

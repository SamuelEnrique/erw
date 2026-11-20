"""Replication of site/data/regions/prices_map.json (session 8013, chain 505, part E4), from the method note and the
rows alone: docs/methods/prices_map.md. Not from the builder's code.

    python replication/prices_map/replicate.py --tables <folder of the price tables' CSVs> [--file site/data/regions/prices_map.json]

For each hub the file shows: its day-ahead prices are read from every table the file names (the first table that holds an
hour wins, in the file's order), a 15-minute price is made hourly by the mean of an hour's four (only when all four are
held), and the day's mean, on-peak and off-peak means, the four dearest less four cheapest hours, and the 30-day and
365-day means and shares below zero are computed in the grid's local time. Each figure is compared with the file's; a
difference over 0.005 is named. Prints N of N.
"""
import argparse
import datetime as dt
import json
import os
import sys

import pandas as pd

DAM = {"lmp_dam", "spp_dam"}
TZ = {"CAISO": "America/Los_Angeles", "ERCOT": "America/Chicago", "SPP": "America/Chicago", "ISO-NE": "America/New_York", "NYISO": "America/New_York", "MISO": "America/Chicago"}
PEAK_SAT = {"CAISO"}


def holidays(years):
    out = set()
    for y in years:
        days = [dt.date(y, 1, 1), dt.date(y, 7, 4), dt.date(y, 12, 25)]
        m = dt.date(y, 5, 31); days.append(m - dt.timedelta(days=m.weekday()))
        s = dt.date(y, 9, 1); days.append(s + dt.timedelta(days=(7 - s.weekday()) % 7))
        n = dt.date(y, 11, 1); days.append(n + dt.timedelta(days=(3 - n.weekday()) % 7 + 21))
        for d in days:
            out.add(d + dt.timedelta(days=1) if d.weekday() == 6 else d)
    return out


def skip(path):
    n = 0
    with open(path, encoding="utf-8") as f:
        for line in f:
            if not line.startswith("#"):
                return n
            n += 1
    return n


def main(argv=None):
    ap = argparse.ArgumentParser()
    ap.add_argument("--tables", required=True)
    ap.add_argument("--file", default=os.path.join(os.path.dirname(__file__), "..", "..", "site", "data", "regions", "prices_map.json"))
    a = ap.parse_args(argv)
    doc = json.load(open(a.file, encoding="utf-8"))
    want = {h["entity"] for h in doc["hubs"]}
    since = (pd.Timestamp(min(h["day"] for h in doc["hubs"] if h.get("day"))) - pd.Timedelta(days=370)).strftime("%Y-%m-%d")
    frames = []
    for rank, t in enumerate(doc["tables"]):
        p = os.path.join(a.tables, t + ".csv")
        if not os.path.exists(p):
            continue
        for ch in pd.read_csv(p, skiprows=skip(p), usecols=["entity", "variable", "ts_utc", "value", "freq"], chunksize=500_000):
            ch = ch[ch["entity"].isin(want) & ch["variable"].isin(DAM) & (ch["ts_utc"] >= since)]
            if len(ch):
                frames.append(ch.assign(rank=rank))
    x = pd.concat(frames)
    x["ts"] = pd.to_datetime(x["ts_utc"], utc=True)
    x = x.sort_values("rank").drop_duplicates(["entity", "freq", "ts"], keep="first")
    hol = holidays(range(2024, 2029))
    n = ok = 0
    named = []
    for h in doc["hubs"]:
        if not h.get("day"):
            continue
        tz = TZ[h["grid"]]
        e = x[x["entity"] == h["entity"]]
        parts = []
        for f, g in e.groupby("freq"):
            s = g.set_index("ts")["value"].sort_index()
            if f != "PT1H":
                gg = s.groupby(s.index.floor("h"))
                s = gg.mean()[gg.size() == 4].round(9)
            parts.append(s)
        s = pd.concat(parts).sort_index()
        s = s[~s.index.duplicated(keep="first")]
        day = dt.date.fromisoformat(h["day"])
        a0 = pd.Timestamp(day, tz=tz).tz_convert("UTC"); a1 = pd.Timestamp(day + dt.timedelta(days=1), tz=tz).tz_convert("UTC")
        d = s[(s.index >= a0) & (s.index < a1)]
        loc = d.index.tz_convert(tz)
        days_ok = {0, 1, 2, 3, 4, 5} if h["grid"] in PEAK_SAT else {0, 1, 2, 3, 4}
        pk = (pd.Series(loc.weekday, index=d.index).isin(days_ok) & pd.Series(loc.hour, index=d.index).between(6, 21) & (day not in hol)).to_numpy()
        mine = {"day_avg": d.mean(), "day_on_peak": d[pk].mean() if pk.any() else None, "day_off_peak": d[~pk].mean() if (~pk).any() else None,
                "day_spread_top4_bottom4": d.nlargest(4).mean() - d.nsmallest(4).mean()}
        for k, nd in (("30d", 30), ("12m", 365)):
            b0 = pd.Timestamp(day - dt.timedelta(days=nd - 1), tz=tz).tz_convert("UTC")
            w = s[(s.index >= b0) & (s.index < a1)]
            need = int((a1 - b0) / pd.Timedelta(hours=1))
            mine[f"avg_{k}"] = w.mean() if len(w) >= 0.95 * need else None
            mine[f"negative_share_{k}_pct"] = 100 * (w < 0).mean() if len(w) >= 0.95 * need else None
        for k, v in mine.items():
            n += 1
            theirs = h.get(k)
            if v is None or theirs is None:
                good = v is None and theirs is None
            else:
                good = abs(round(float(v), 2) - theirs) <= 0.005 + 1e-9
            ok += good
            if not good:
                named.append(f"{h['entity']} {k}: file {theirs}, here {None if v is None else round(float(v), 4)}")
    for m in named:
        print("DIFFERS", m)
    print(f"{ok} of {n} figures reproduced")
    return 0 if ok == n else 1


if __name__ == "__main__":
    sys.exit(main())

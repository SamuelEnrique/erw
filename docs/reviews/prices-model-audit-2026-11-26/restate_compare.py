"""Session 10218: an independent restatement of site/data/price_compare.json (the page /prices/compare reads it).

Written from docs/methods/hub_price_comparison.md, not from warehouse/derived/price_compare.py: standard library only
(csv, zoneinfo, statistics). Public grids only (CAISO, ERCOT, SPP): no row of a held or paused grid is read.

    python restate_compare.py <warehouse output dir> <site dir> <out json>

The note's rules, written again:
  - two windows in each grid's local time: the twelve months and the last month, ending with the file's end_month
  - the tables in the note's order; a row held in two tables is read once, from the first of the list
  - an hour of real time is the mean of its four 15-minute prices, held only when all four are (rounded to 9 places,
    so four prices summing to zero are an hour of zero)
  - a side held at two steps uses the one that holds more of the window, never mixed
  - a market of a hub is written when at least 95 percent of the window's hours are held
  - average: the mean of the hourly prices; below zero: share of hours < 0; above 200: share of hours > 200
  - spread: the average day (each local hour's mean over the window), four dearest less four cheapest
  - daily spread: each whole local day's four dearest less four cheapest, the mean over those days, and their count
  - carbon: the mean of the grid's daily intensity of generation over the window's days, when 90 percent are held
"""
import collections
import datetime as dt
import json
import os
import sys
from zoneinfo import ZoneInfo

OUT, SITE, DEST = sys.argv[1], sys.argv[2], sys.argv[3]
UTC = dt.timezone.utc
ORDER = ["iso_hub_prices_history", "ercot_all_hub_prices_history", "iso_dam_hub_prices", "iso_rtm_hub_prices",
         "ercot_zone_prices_history"]  # the note's list, the held grids' own tables (isone_*, nyiso_*) left out
PUBLIC = {"caiso": ("CAISO", "America/Los_Angeles", "CISO"), "ercot": ("ERCOT", "America/Chicago", "ERCO"),
          "spp": ("SPP", "America/Chicago", "SWPP")}
DA = {"lmp_dam", "spp_dam"}
RT = {"lmp_rtm_15m_mean", "spp_rtm", "lmp_rtm"}
LO, HI = "2025-10-31", "2026-11-02"

f = json.load(open(os.path.join(SITE, "data", "price_compare.json"), encoding="utf-8"))
end_month = f["end_month"]


def month_start(ym, back=0):
    y, m = int(ym[:4]), int(ym[5:7]) - back
    while m < 1:
        m, y = m + 12, y - 1
    return dt.date(y, m, 1)


em = month_start(end_month)
nxt = dt.date(em.year + (em.month == 12), em.month % 12 + 1, 1)
WINDOWS = {"year": (month_start(end_month, 11), nxt), "month": (em, nxt)}

store = {}      # (entity, side, freq) -> {ts epoch seconds: value}

log = []
for t in ORDER:
    path = os.path.join(OUT, t + ".csv")
    n_used = 0
    with open(path, encoding="utf-8") as fh:
        for line in fh:
            if line.startswith("#") or line.startswith("entity,"):
                continue
            p = line.split(",", 6)
            ent, var, ts = p[0], p[1], p[2]
            if ts < LO or ts >= HI:
                continue
            iso = ent.split(":", 1)[0]
            if iso not in PUBLIC:
                continue
            side = "dam" if var in DA else "rtm" if var in RT else None
            if side is None:
                continue
            freq = p[5]
            sec = int(dt.datetime.strptime(ts, "%Y-%m-%dT%H:%M:%SZ").replace(tzinfo=UTC).timestamp())
            d = store.setdefault((ent, side, freq), {})
            if sec in d:  # held in an earlier table of the list: read once, from the first
                continue
            d[sec] = float(p[3])
            n_used += 1
    log.append(f"{t}: {n_used:,} rows used")



def hours_of(vals, freq):
    """{hour start epoch: price} from a side's values at one step."""
    if freq == "PT1H":
        return dict(vals)
    if freq != "PT15M":
        return {}
    by = collections.defaultdict(list)
    for s, v in vals.items():
        by[s - s % 3600].append(v)
    return {h: round(sum(v) / 4, 9) for h, v in by.items() if len(v) == 4}


def local_midnight(d, tz):
    return int(dt.datetime(d.year, d.month, d.day, tzinfo=tz).timestamp())


def top_bottom(vals):
    s = sorted(vals)
    return sum(s[-4:]) / 4 - sum(s[:4]) / 4


def measures(h, tz, a, b):
    n = (b - a) // 3600
    hs = {k: v for k, v in h.items() if a <= k < b}
    if len(hs) < 0.95 * n:
        return None, len(hs), n
    vals = list(hs.values())
    by_hour = collections.defaultdict(list)
    by_day = collections.defaultdict(list)
    for k, v in hs.items():
        loc = dt.datetime.fromtimestamp(k, tz)
        by_hour[loc.hour].append(v)
        by_day[loc.date()].append(v)
    if len(by_hour) < 24:
        return None, len(hs), n
    avg_day = [sum(v) / len(v) for v in by_hour.values()]
    out = {"avg_price": sum(vals) / len(vals), "negative_hours_share_pct": 100 * sum(1 for v in vals if v < 0) / len(vals),
           "above_200_hours_share_pct": 100 * sum(1 for v in vals if v > 200) / len(vals),
           "day_spread_top4_bottom4": top_bottom(avg_day), "hours_held": len(hs), "hours_in_window": n}
    spreads = []
    for d, v in by_day.items():
        need = (local_midnight(d + dt.timedelta(days=1), tz) - local_midnight(d, tz)) // 3600
        if len(v) == need:
            spreads.append(top_bottom(v))
    if spreads:
        out["daily_spread_mean_top4_bottom4"] = sum(spreads) / len(spreads)
        out["daily_spread_days"] = len(spreads)
    return out, len(hs), n


# carbon: eia930:<BA> intensity_generation by day
carbon = collections.defaultdict(dict)
with open(os.path.join(OUT, "carbon_intensity_daily.csv"), encoding="utf-8") as fh:
    for line in fh:
        if line.startswith("#") or line.startswith("entity,"):
            continue
        p = line.split(",", 4)
        if p[1] != "intensity_generation" or p[0] not in {"eia930:" + v[2] for v in PUBLIC.values()}:
            continue
        carbon[p[0]][p[2][:10]] = float(p[3])

# Optional (argv 4 == "fill"): hours of real time this machine's tables lack, taken from the page's own hourly files
# (site/public/board/h/<hub>.json, each hour the mean of its intervals, to the cent), only inside the two windows and
# only where no 15-minute hour is held here. Kept apart as a step "PT1H-fill" of its own and merged into the 15-minute
# hours, and every hour so filled is listed by day.
FILL = len(sys.argv) > 4 and sys.argv[4] == "fill"
filled = collections.Counter()
if FILL:
    y0 = local_midnight(WINDOWS["year"][0], ZoneInfo("America/New_York")) - 86400
    y1 = local_midnight(WINDOWS["year"][1], ZoneInfo("America/Los_Angeles")) + 86400
    for ent in sorted({k[0] for k in store}):
        hid = ent.replace(":", "-").replace("_", "-").replace(".", "-").lower()
        path = os.path.join(SITE, "public", "board", "h", hid + ".json")
        if not os.path.exists(path):
            continue
        hf = json.load(open(path, encoding="utf-8"))
        q = store.get((ent, "rtm", "PT15M"))
        if q is None:
            continue
        # only where the file says the month held every hour of real time, and only inside that month
        fr = next((x for x in f["month"] if x["entity"] == ent), {})
        if not fr.get("rtm_hours_held") or fr.get("rtm_hours_held") != fr.get("rtm_hours_in_window"):
            continue
        tz0 = ZoneInfo(PUBLIC[ent.split(":")[0]][1])
        y0, y1 = local_midnight(WINDOWS["month"][0], tz0), local_midnight(WINDOWS["month"][1], tz0)
        have = set(hours_of(q, "PT15M"))
        add = {}
        for i, v in enumerate(hf.get("rt") or []):
            s = (hf["t0"] + i) * 3600
            if v is None or not (y0 <= s < y1) or s in have:
                continue
            add[s] = float(v)
        if add:
            store[(ent, "rtm", "FILL")] = add
            for s in add:
                filled[(ent, dt.datetime.fromtimestamp(s, UTC).date().isoformat())] += 1
    _hours_of = hours_of

    def hours_of(vals, freq):  # noqa: F811  the filled hours join the 15-minute hours of the same side
        return dict(vals) if freq == "FILL" else _hours_of(vals, freq)

rows = {"year": {}, "month": {}}
not_written = []
entities = sorted({k[0] for k in store})
for ent in entities:
    iso = ent.split(":", 1)[0]
    grid, tzname, ba = PUBLIC[iso]
    tz = ZoneInfo(tzname)
    for w, (d0, d1) in WINDOWS.items():
        a, b = local_midnight(d0, tz), local_midnight(d1, tz)
        rec = {"entity": ent, "grid": grid}
        for side in ("dam", "rtm"):
            best = None
            for (e, s, fq), vals in store.items():
                if e != ent or s != side or fq == "FILL":
                    continue
                h = hours_of(vals, fq)
                if fq == "PT15M" and (e, s, "FILL") in store:
                    h = {**store[(e, s, "FILL")], **h}
                inw = sum(1 for k in h if a <= k < b)
                if best is None or inw > best[2]:
                    best = (h, fq, inw)
            if best is None:
                continue
            m, held, due = measures(best[0], tz, a, b)
            if m is None:
                not_written.append(f"{w} {ent} {side}: {held} of {due} hours")
                continue
            rec[f"{side}_basis"] = best[1]
            for k, v in m.items():
                rec[f"{side}_{k}"] = v
        if not any(k.startswith(("dam_", "rtm_")) for k in rec):
            continue
        days = [(d0 + dt.timedelta(days=i)).isoformat() for i in range((d1 - d0).days)]
        got = [carbon["eia930:" + ba][d] for d in days if d in carbon["eia930:" + ba]]
        rec["grid_carbon_days_held"], rec["grid_carbon_days_due"] = len(got), len(days)
        if len(got) >= 0.9 * len(days):
            rec["grid_carbon_intensity"] = sum(got) / len(got)
        rows[w][ent] = rec

json.dump({"filled": {f"{k[0]} {k[1]}": v for k, v in sorted(filled.items())}, "windows": {k: [v[0].isoformat(), v[1].isoformat()] for k, v in WINDOWS.items()}, "log": log,
           "not_written": not_written, "rows": rows}, open(DEST, "w", encoding="utf-8"), indent=0)
print("\n".join(log))
print("not written:", not_written)
print("written", DEST)

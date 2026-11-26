"""Session 10218: one rule changed at a time, for /prices/compare and the Grid map's price colors. Public grids only.

    python measures.py <warehouse output dir> <site dir>

A. The twelve months' day-ahead average: simple (the page) against weighted by the grid's own hourly load (ERCOT's
   system load, CAISO's CA ISO-TAC), over the hours both hold.
B. Hours the comparison lacks and the page's own hourly files hold (site/public/board/h): the figure with them.
C. The grid's carbon intensity: the mean of daily intensities (the page) against the days weighted by their net
   generation (eia930_all_history), over the days both hold.
D. Hours above USD 200 (the page) against above USD 100, twelve months, day-ahead.
E. The map: each area by another hub of its grid, and on the newest day all three areas hold in the page's hourly files.
"""
import collections
import datetime as dt
import json
import os
import sys
from zoneinfo import ZoneInfo

OUT, SITE = sys.argv[1], sys.argv[2]
UTC = dt.timezone.utc
ORDER = ["iso_hub_prices_history", "ercot_all_hub_prices_history", "iso_dam_hub_prices", "iso_rtm_hub_prices", "ercot_zone_prices_history"]
PUBLIC = {"caiso": ("CAISO", "America/Los_Angeles", "CISO"), "ercot": ("ERCOT", "America/Chicago", "ERCO"), "spp": ("SPP", "America/Chicago", "SWPP")}
cmp = json.load(open(os.path.join(SITE, "data", "price_compare.json"), encoding="utf-8"))


def mid(d, tz):
    return int(dt.datetime(d.year, d.month, d.day, tzinfo=tz).timestamp())


def sec(ts):
    return int(dt.datetime.strptime(ts, "%Y-%m-%dT%H:%M:%SZ").replace(tzinfo=UTC).timestamp())


# day-ahead hours of the public hubs and zones, the first table of the list holding each hour
dam = collections.defaultdict(dict)
for t in ORDER:
    with open(os.path.join(OUT, t + ".csv"), encoding="utf-8") as fh:
        for line in fh:
            if line.startswith("#") or line.startswith("entity,"):
                continue
            p = line.split(",", 6)
            if p[2] < "2025-10-31" or p[2] >= "2026-11-02" or p[0].split(":")[0] not in PUBLIC or p[1] not in ("lmp_dam", "spp_dam") or p[5] != "PT1H":
                continue
            s = sec(p[2])
            if s not in dam[p[0]]:
                dam[p[0]][s] = float(p[3])
Y0, Y1 = dt.date(2025, 11, 1), dt.date(2026, 11, 1)


def year_hours(ent):
    tz = ZoneInfo(PUBLIC[ent.split(":")[0]][1])
    a, b = mid(Y0, tz), mid(Y1, tz)
    return {s: v for s, v in dam[ent].items() if a <= s < b}


print("== A. twelve months' day-ahead average, simple against load-weighted, over the hours both hold")
load = {"ercot": {}, "caiso": {}}
for f, ent, g in (("ercot_zone_load_hourly.csv", "ercot:system", "ercot"), ("caiso_area_load_hourly.csv", "caiso:system", "caiso")):
    with open(os.path.join(OUT, f), encoding="utf-8") as fh:
        for line in fh:
            if not line.startswith(ent + ","):
                continue
            p = line.split(",", 4)
            if p[1] == "load" and "2025-10-31" <= p[2] < "2026-11-02":
                load[g][sec(p[2])] = load[g].get(sec(p[2]), 0) + float(p[3])  # the repeated autumn hour, twice in ERCOT's file, summed as one hour's energy
for g in ("ercot", "caiso"):
    ks = sorted(load[g])
    print(f"  {g} load: {len(ks):,} hours, {dt.datetime.fromtimestamp(ks[0], UTC).isoformat()} to {dt.datetime.fromtimestamp(ks[-1], UTC).isoformat()}")
for ent in sorted(dam):
    g = ent.split(":")[0]
    if g not in load:
        continue
    h = year_hours(ent)
    both = [s for s in h if s in load[g]]
    if not both:
        continue
    simple = sum(h[s] for s in both) / len(both)
    w = sum(h[s] * load[g][s] for s in both) / sum(load[g][s] for s in both)
    page = next((r.get("dam_avg_price") for r in cmp["year"] if r["entity"] == ent), None)
    print(f"  {ent}: page {page}; over the {len(both):,} hours with load: simple {simple:.2f}, load-weighted {w:.2f}, gap {w - simple:+.2f} ({100 * (w - simple) / simple:+.1f} percent)")

print("== B. hours the comparison lacks that the page's own hourly files hold")
for ent, side, win in (("spp:SPPNORTH_HUB", "rt", "year"), ("spp:SPPNORTH_HUB", "da", "month"), ("spp:SPPNORTH_HUB", "rt", "month"),
                       ("spp:SPPSOUTH_HUB", "da", "month"), ("spp:SPPSOUTH_HUB", "rt", "month"), ("caiso:TH_ZP26_GEN-APND", "rt", "month")):
    tz = ZoneInfo(PUBLIC[ent.split(":")[0]][1])
    a, b = (mid(Y0, tz), mid(Y1, tz)) if win == "year" else (mid(dt.date(2026, 10, 1), tz), mid(Y1, tz))
    hid = ent.replace(":", "-").replace("_", "-").lower()
    hf = json.load(open(os.path.join(SITE, "public", "board", "h", hid + ".json"), encoding="utf-8"))
    hrs = [v for i, v in enumerate(hf.get(side) or []) if v is not None and a <= (hf["t0"] + i) * 3600 < b]
    row = next((r for r in cmp[win] if r["entity"] == ent), {})
    m = "dam" if side == "da" else "rtm"
    neg = 100 * sum(1 for v in hrs if v < 0) / len(hrs) if hrs else None
    print(f"  {ent} {m} {win}: the comparison {row.get(m + '_avg_price', 'not written')} over {row.get(m + '_hours_held', '-')} of {(b - a) // 3600} hours; "
          f"the page's hourly file {sum(hrs) / len(hrs):.2f} over {len(hrs)} hours (below zero {neg:.2f} percent; the comparison {row.get(m + '_negative_hours_share_pct', '-')})")

print("== C. carbon intensity: mean of daily figures against generation-weighted days")
gen = collections.defaultdict(lambda: collections.defaultdict(float))
cnt = collections.defaultdict(lambda: collections.Counter())
with open(os.path.join(OUT, "eia930_all_generation.csv"), encoding="utf-8") as fh:
    for line in fh:
        p = line.split(",", 6)
        if len(p) < 6 or p[1] != "net_generation_mw" or p[0] not in ("eia930:CISO", "eia930:ERCO", "eia930:SWPP"):
            continue
        ba = p[0].split(":")[1]
        tz = ZoneInfo({"CISO": "America/Los_Angeles", "ERCO": "America/Chicago", "SWPP": "America/Chicago"}[ba])
        d = dt.datetime.fromtimestamp(sec(p[2]), tz).date().isoformat()  # the BA's local day, as EIA's daily figures are
        gen[ba][d] += float(p[3])
        cnt[ba][d] += 1
ci = collections.defaultdict(dict)
with open(os.path.join(OUT, "carbon_intensity_daily.csv"), encoding="utf-8") as fh:
    for line in fh:
        p = line.split(",", 4)
        if len(p) > 3 and p[1] == "intensity_generation" and p[0] in ("eia930:CISO", "eia930:ERCO", "eia930:SWPP"):
            ci[p[0].split(":")[1]][p[2][:10]] = float(p[3])
for ba in ("CISO", "ERCO", "SWPP"):
    days = [d for d in ci[ba] if cnt[ba].get(d) == 24]
    if not days:
        print(f"  {ba}: no day both hold")
        continue
    simple = sum(ci[ba][d] for d in days) / len(days)
    w = sum(ci[ba][d] * gen[ba][d] for d in days) / sum(gen[ba][d] for d in days)
    print(f"  {ba}: {len(days)} days ({min(days)} to {max(days)}): mean of days {simple:.2f}, generation-weighted {w:.2f} kg/MWh, gap {w - simple:+.2f} ({100 * (w - simple) / simple:+.2f} percent)")
    octd = [d for d in days if d.startswith("2026-10")]
    if octd:
        s2 = sum(ci[ba][d] for d in octd) / len(octd)
        w2 = sum(ci[ba][d] * gen[ba][d] for d in octd) / sum(gen[ba][d] for d in octd)
        print(f"    October 2026 ({len(octd)} days): mean of days {s2:.2f}, generation-weighted {w2:.2f}, gap {w2 - s2:+.2f} ({100 * (w2 - s2) / s2:+.2f} percent)")

print("== D. hours above USD 200 against above USD 100, twelve months, day-ahead")
for ent in sorted(dam):
    h = year_hours(ent)
    if len(h) < 0.95 * 8760:
        continue
    v = list(h.values())
    print(f"  {ent}: above 200 {100 * sum(1 for x in v if x > 200) / len(v):.2f} percent, above 100 {100 * sum(1 for x in v if x > 100) / len(v):.2f} percent")

print("== E. the map: another hub for an area, and a newer day")
pm = json.load(open(os.path.join(SITE, "data", "regions", "prices_map.json"), encoding="utf-8"))
hubs = {h["entity"]: h for h in pm["hubs"]}


def scale(vals):
    lo, hi = min(vals.values()), max(vals.values())
    return {k: round((v - lo) / ((hi - lo) or 1), 2) for k, v in vals.items()}


base = {"CISO": "caiso:TH_SP15_GEN-APND", "ERCO": "ercot:HB_HUBAVG", "SWPP": "spp:SPPNORTH_HUB"}
for meas in ("day_avg", "avg_12m"):
    print(f"  {meas} as drawn: {{{', '.join(f'{k}: {hubs[v][meas]}' for k, v in base.items())}}} positions {scale({k: hubs[v][meas] for k, v in base.items()})}")
    for ba, alt in (("CISO", "caiso:TH_NP15_GEN-APND"), ("SWPP", "spp:SPPSOUTH_HUB"), ("ERCO", "ercot:HB_WEST"), ("ERCO", "ercot:LZ_WEST")):
        if hubs[alt].get(meas) is None:
            print(f"    {ba} by {alt}: not held for {meas}")
            continue
        vals = {k: hubs[v][meas] for k, v in base.items()}
        vals[ba] = hubs[alt][meas]
        print(f"    {ba} by {alt} ({hubs[alt][meas]}, day {hubs[alt]['day']}): positions {scale(vals)}")
    for ba in base:
        grid = [h for h in pm["hubs"] if h["ba"] == ba and h.get(meas) is not None]
        print(f"    within {ba}: {min(h[meas] for h in grid)} to {max(h[meas] for h in grid)} over {len(grid)} hubs and zones")
# the newest day all three main hubs hold whole in the page's hourly files
days = {}
for ba, ent in base.items():
    tz = ZoneInfo(PUBLIC[ent.split(":")[0]][1])
    hf = json.load(open(os.path.join(SITE, "public", "board", "h", ent.replace(":", "-").replace("_", "-").lower() + ".json"), encoding="utf-8"))
    by = collections.defaultdict(list)
    for i, v in enumerate(hf.get("da") or []):
        if v is not None:
            by[dt.datetime.fromtimestamp((hf["t0"] + i) * 3600, tz).date()].append(v)
    days[ba] = {d: sum(v) / len(v) for d, v in by.items() if len(v) == (mid(d + dt.timedelta(days=1), tz) - mid(d, tz)) // 3600}
common = sorted(set.intersection(*(set(v) for v in days.values())))
d = common[-1]
vals = {ba: round(days[ba][d], 2) for ba in base}
print(f"  newest day all three areas hold whole in the page's hourly files: {d}: {vals} positions {scale(vals)} (the map: {pm['bas']['CISO']['day']})")
for ba in base:
    print(f"    {ba} newest whole day in its hourly file: {max(days[ba])}")

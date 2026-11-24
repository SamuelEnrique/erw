"""Session 9900: the number check. For each post spec, re-read the source each row came from, independently of the
script that wrote the spec, and compare the drawn text with the source value rounded half up to the drawn digits.
Writes one markdown table a spec into <out_dir>/<id>.md and exits 1 on any mismatch.
Usage: numcheck.py <out_dir>"""
import csv
import json
import statistics
import sys
from decimal import ROUND_HALF_UP, Decimal
from pathlib import Path

OUT = Path(sys.argv[1])
OUT.mkdir(parents=True, exist_ok=True)
SPECS = Path("motion/specs/posts")
WH = "C:/Users/Shared/Documents/erw/warehouse/output/"
bad = 0


def r(v, dec):
    return Decimal(str(v)).quantize(Decimal(1).scaleb(-dec), ROUND_HALF_UP)


def table(spec_id, lines):
    global bad
    md = ["| Row | Drawn | Second figure | Source value | Source | Equal to the last digit |", "|---|---|---|---|---|---|"]
    for label, drawn, second, src_val, src, ok in lines:
        bad += not ok
        md.append(f"| {label} | {drawn} | {second} | {src_val} | {src} | {'yes' if ok else 'NO'} |")
    (OUT / f"{spec_id}.md").write_text("\n".join(md) + "\n", encoding="utf-8")
    print(spec_id, "rows", len(lines), "mismatches", sum(not l[5] for l in lines))


# B2: medians recomputed from the per-day peaks
peaks = list(csv.DictReader(open("docs/research/motion/posts/data/thanksgiving_peak_hour_days.csv")))
LAB = {"Plains": "SWPP", "Midwest": "MISO", "Mid-Atlantic": "PJM", "New York": "NYIS", "Texas": "ERCO",
       "New England": "ISNE", "California": "CISO"}


def clock(he):
    he = int(he)
    return "noon" if he == 12 else f"{he if he < 12 else he - 12} {'am' if he < 12 else 'pm'}"


spec = json.load(open(SPECS / "thanksgiving_peak_hour.json"))
lines = []
for row in spec["rows"]:
    ba = LAB[row["label"]]
    tg = statistics.median(int(p["peak_hour_ending"]) for p in peaks if p["ba"] == ba and p["kind"] == "thanksgiving")
    nt = statistics.median(int(p["peak_hour_ending"]) for p in peaks if p["ba"] == ba and p["kind"] != "thanksgiving")
    shift = int(nt - tg)
    sec = f"{clock(nt)} to {clock(tg)}"
    ok = row["display"] == f"{shift} h" and row["second"] == sec and row["value"] == shift
    lines.append((row["label"], row["display"], row["second"], f"{ba}: normal HE {int(nt)}, Thanksgiving HE {int(tg)}, shift {shift}",
                  "eia930_ba_demand_hourly (20261123T193514Z), per-day peaks", ok))
table(spec["id"], lines)

# B3: the warehouse table, and EIA's API for the newest week
g = {}
with open(WH + "eia_retail_fuel_prices.csv", newline="") as f:
    for row in csv.DictReader(l for l in f if not l.startswith("#")):
        if row["entity"] == "eia:EMM_EPMR_PTE_NUS_DPG":
            g[row["ts_utc"][:10]] = row["value"]
api = json.load(open("docs/research/motion/posts/data/eia_fuel_latest_2026-11-24.json"))
api_g = {d["period"]: d["value"] for d in api["response"]["response"]["data"] if d["series"] == "EMM_EPMR_PTE_NUS_DPG"}
WEEK = {"2020": "2020-11-23", "2021": "2021-11-22", "2022": "2022-11-21", "2023": "2023-11-20", "2024": "2024-11-25",
        "2025": "2025-11-24", "2026": "2026-11-16"}
for v in "ab":
    spec = json.load(open(SPECS / f"thanksgiving_gasoline_{v}.json"))
    lines = []
    for row in spec["rows"]:
        wk = WEEK[row["label"]]
        sv = g[wk]
        ok = row["display"] == f"${r(sv, 2)}" and abs(row["value"] - float(sv)) < 1e-12
        extra = f"; EIA API {api_g[wk]}" if wk in api_g else ""
        if wk in api_g:
            ok = ok and str(api_g[wk]) == sv
        lines.append((row["label"], row["display"], "", f"{sv} (week of {wk}{extra})", "eia_retail_fuel_prices, EMM_EPMR_PTE_NUS_DPG", ok))
    table(spec["id"], lines)

# Part C: the reproductions' printed output
SEC = {"us_share_world_oil_a": "37", "us_share_world_oil_b": "37", "texas_cold_peak": "21", "uranium_us_origin_a": "24",
       "uranium_us_origin_b": "24", "dominion_mean_hour": "1", "canada_new_york_flow": "8", "caiso_battery_peak": "10",
       "ercot_solar_tight_hours": "3"}
for sid, s in SEC.items():
    spec = json.load(open(SPECS / f"{sid}.json"))
    printed = {}
    for line in open(f"docs/research/motion/posts/data/shortlist_s{s}_reproduce_2026-11-24.txt"):
        p = line.split()
        if len(p) >= 2 and p[0].isdigit():
            printed[p[0]] = p[1]
    lines = []
    for row in spec["rows"]:
        sv = printed[row["label"]]
        dec = spec["decimals"]
        q = r(sv, dec)
        want = f"{q}%" if row["display"].endswith("%") else f"{q:,} MW"
        ok = row["display"] == want and abs(row["value"] - float(sv)) < 1e-9
        lines.append((row["label"], row["display"], "", sv, f"section {s} reproduce.py, run 2026-11-24", ok))
    table(sid, lines)
print("mismatches", bad)
sys.exit(1 if bad else 0)

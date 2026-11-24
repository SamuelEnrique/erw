"""B2, session 9900: write motion/specs/posts/thanksgiving_peak_hour.json from summary.csv (peaks.py)."""
import csv
import json
import sys

summ = {r["ba"]: r for r in csv.DictReader(open(sys.argv[1]))}
out = sys.argv[2]
LABEL = {"SWPP": "Plains", "MISO": "Midwest", "PJM": "Mid-Atlantic", "NYIS": "New York", "ERCO": "Texas",
         "ISNE": "New England", "CISO": "California"}
OPER = {"SWPP": "SPP", "MISO": "MISO", "PJM": "PJM", "NYIS": "NYISO", "ERCO": "ERCOT", "ISNE": "ISO-NE", "CISO": "CAISO"}


def clock(he):
    he = int(float(he))
    if he == 12:
        return "noon"
    if he in (0, 24):
        return "midnight"
    return f"{he if he < 12 else he - 12} {'am' if he < 12 else 'pm'}"


order = sorted(summ, key=lambda b: -float(summ[b]["shift_hours"]))  # stable: ties keep LABEL's order below
order = sorted(LABEL, key=lambda b: -float(summ[b]["shift_hours"]))
rows = []
for b in order:
    s = summ[b]
    sh = float(s["shift_hours"])
    assert sh == int(sh)
    rows.append({"label": LABEL[b], "value": int(sh), "display": f"{int(sh)} h",
                 "second": f"{clock(s['median_thursday'])} to {clock(s['median_thanksgiving'])}"})
spec = {
    "id": "thanksgiving_peak_hour", "type": "post", "width": 1080, "height": 1080, "frames": 450, "decimals": 0,
    "max": max(r["value"] for r in rows), "labelWidth": 300,
    "title": "Hours early the grid peaks on Thanksgiving",
    "source": "Source: EIA, Hourly Electric Grid Monitor (EIA-930), demand, 2019-2025. Hour of peak demand, local time, "
              "end of hour: median of seven Thanksgivings against the 21 Thursdays before them. Grids: "
              + ", ".join(OPER[b] for b in order) + " (MISO in Central time).",
    "rows": rows,
    "_numbers_from": "eia930_ba_demand_hourly (retrieved 20261123T193514Z), demand_mw; runs/posts9900/b2/peaks.py, summary.csv",
}
json.dump(spec, open(out, "w"), indent=1)
for r in rows:
    print(r)

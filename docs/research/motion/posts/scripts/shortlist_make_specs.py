"""Part C, session 9900: write the shortlist posts' specs from the reproductions' printed output (runs/posts9900/c/sN.out).
Each figure is formatted from the printed digits, rounded half up (never JavaScript's toFixed). Usage:
make_specs.py <out_dir_of_sN.out> <specs_dir> [section ...]"""
import json
import sys
from decimal import ROUND_HALF_UP, Decimal
from pathlib import Path

src, dst = Path(sys.argv[1]), Path(sys.argv[2])
only = set(sys.argv[3:])
B = "https://github.com/SamuelEnrique/erw/blob/main/docs/findings/"


def fmt(v, dec, unit):
    q = Decimal(v).quantize(Decimal(1).scaleb(-dec), ROUND_HALF_UP)
    if unit == "%":
        return f"{q}%"
    return f"{q:,} {unit}".strip()


POSTS = {
    "37": dict(id="us_share_world_oil", years=[1995, 2000, 2005, 2010, 2015, 2020, 2025], dec=1, unit="%",
               title="US share of world oil and liquids production",
               source="Source: EIA, International Energy Statistics. US production of petroleum and other liquids as a "
                      "percent of the world's, every fifth year, 1995-2025. Other producers' figures are EIA estimates "
                      "and are revised.",
               repro="oil_products_world/us-liquids-share-us-world-liquids.reproduce.py", table="eia_world_oil_monthly",
               alt_max=True),
    "21": dict(id="texas_cold_peak", years=list(range(2020, 2027)), dec=0, unit="MW",
               title="Texas's highest hour of demand in late January",
               source="Source: EIA, Hourly Electric Grid Monitor (EIA-930), Texas region demand. The highest hour "
                      "from 23 January to 2 February (UTC days), 2020-2026. The window is the days the ERW gives to "
                      "the January 2026 cold; another window moves the peaks.",
               repro="events/cold-2026-tex.reproduce.py", table="eia930_ba_demand_hourly"),
    "24": dict(id="uranium_us_origin", years=[2003, 2007, 2010, 2014, 2018, 2021, 2025], dec=1, unit="%",
               title="Uranium bought for US reactors that was of US origin",
               source="Source: EIA, Uranium Marketing Annual Report. US-origin uranium as a percent of all uranium "
                      "bought by the owners and operators of US reactors, 2003-2025, origin as the owners report it. "
                      "2025 is preliminary.",
               repro="coal_uranium_metals/us-origin-uranium-us-uranium-origin.reproduce.py",
               table="eia_uranium_marketing_annual", alt_max=True),
    "1": dict(id="dominion_mean_hour", years=list(range(2019, 2026)), dec=0, unit="MW",
              title="Mean hour of demand in Dominion's Virginia zone",
              source="Source: EIA, Hourly Electric Grid Monitor (EIA-930), demand by subregion. The mean hour of "
                     "demand in PJM's Dominion zone (DOM), local years 2019-2025, as PJM reports it to EIA; a change "
                     "of the zone's bounds or of PJM's reporting would move the level.",
              repro="demand/sub-mean-pjm-sub-dom.reproduce.py", table="eia930_subba_demand_hourly_2019 to _2025"),
    "8": dict(id="canada_new_york_flow", years=list(range(2019, 2026)), dec=0, unit="MW",
              title="Mean hourly flow of power from Canada to New York",
              source="Source: EIA, Hourly Electric Grid Monitor (EIA-930), interchange between EIA's regions. The "
                     "mean hourly flow from Canada to New York, 2019-2025, from EIA's region-pair series; the two "
                     "sides' reports of the same flow differ.",
              repro="trade/pair-flow-rp-can-ny.reproduce.py", table="eia930_region_pair_hourly"),
    "10": dict(id="caiso_battery_peak", years=list(range(2019, 2026)), dec=1, unit="%",
               title="California's battery fleet against its peak-day demand",
               source="Source: EIA, Preliminary Monthly Electric Generator Inventory (EIA-860M) and EIA-930. CAISO's "
                      "battery capacity at year's end as a percent of the mean demand of its ten highest days, "
                      "2019-2025. Batteries do not all run at full output at once.",
               repro="cross_family/battery-per-peak-caiso-bat-peak.reproduce.py",
               table="storage_buildout_monthly, eia930_daily_demand"),
    "3": dict(id="ercot_solar_tight_hours", years=list(range(2019, 2026)), dec=1, unit="%",
              title="Solar's output in ERCOT's tightest hours",
              source="Source: EIA-930 hourly demand and generation, EIA-860M capacity (ERW grid stress table). Solar "
                     "output in ERCOT's 100 hours of highest net load a year, percent of solar capacity, 2019-2025. "
                     "Another definition of the tightest hours gives another share.",
              repro="markets_operations/tight-solar-ercot-tight-solar.reproduce.py", table="grid_stress_yearly"),
    "9": dict(id="new_england_export_hours", years=list(range(2019, 2026)), dec=1, unit="%",
              title="Share of hours New England exported power",
              source="Source: EIA, Hourly Electric Grid Monitor (EIA-930), total interchange of EIA's New England "
                     "region. The share of each year's hours with net exports, 2019-2025. Sign as reported; an "
                     "hour's error near zero flips the count.",
              repro="trade/region-against-rn-ne.reproduce.py", table="eia930_region_hourly"),
    "12": dict(id="us_datacenter_construction", years=[2014, 2016, 2018, 2020, 2021, 2023, 2025], dec=1, unit="",
               prefix="$", suffix="B",
               title="Private data center construction in the US, USD billion",
               source="Source: US Census Bureau, Construction Spending (C30), private data center construction put "
                      "in place, USD billion, nominal, 2014-2025. Census revises the series each July: this is the "
                      "vintage of 24 October 2026.",
               repro="queues_deals_datacenters/dc-construction-us-dc-build.reproduce.py",
               table="census_c30_construction_monthly"),
}

for sec, p in POSTS.items():
    if only and sec not in only:
        continue
    printed = {}
    for line in (src / f"s{sec}.out").read_text().splitlines():
        parts = line.split()
        if len(parts) >= 2 and parts[0].isdigit():
            printed[int(parts[0])] = parts[1]
    rows = []
    for y in p["years"]:
        v = printed[y]
        disp = fmt(v, p["dec"], p["unit"])
        if "prefix" in p:
            disp = p["prefix"] + str(Decimal(v).quantize(Decimal(1).scaleb(-p["dec"]), ROUND_HALF_UP)) + p["suffix"]
        rows.append({"label": str(y), "value": float(v), "display": disp})
    vals = [r["value"] for r in rows]
    versions = [("", 100.0 if p["unit"] == "%" else max(vals))]
    if p.get("alt_max"):
        versions = [("_a", 100.0), ("_b", max(vals))]
    for suf, mx in versions:
        spec = {"id": p["id"] + suf, "type": "post", "width": 1080, "height": 1080, "frames": 450, "decimals": p["dec"],
                "max": mx, "title": p["title"], "source": p["source"], "rows": rows,
                "_numbers_from": f"shortlist section {sec}; {B}{p['repro']} run 2026-11-24 on {p['table']}, "
                                 f"output runs/posts9900/c/s{sec}.out"}
        (dst / f"{p['id']}{suf}.json").write_text(json.dumps(spec, indent=1))
        print(sec, p["id"] + suf, "max", mx, [r["display"] for r in rows])

"""Session 9901 (25 November 2026): the nine batch-2 posts' numbers, from the ERW tables and the reproduce runs saved
in ../data/, written to one data file a post (../data/<post>.json: every value with its ERW table and original source)
and to the two specs a post (motion/specs/posts/batch2/<post>_<a|b>.json). Every drawn figure is rounded half up
from the source digits (never JavaScript's rounding). Reads only; writes no warehouse table.

    python build_9901.py
"""
import csv
import json
import os
import statistics
from collections import defaultdict
from datetime import date, datetime, timedelta, timezone
from decimal import ROUND_HALF_UP, Decimal
from zoneinfo import ZoneInfo

HERE = os.path.dirname(os.path.abspath(__file__))
BATCH = os.path.dirname(HERE)
DATA = os.path.join(BATCH, "data")
REPO = os.path.abspath(os.path.join(BATCH, "..", "..", "..", "..", ".."))
SPECS = os.path.join(REPO, "motion", "specs", "posts", "batch2")
OUT = "C:/Users/Shared/Documents/erw/warehouse/output"
RAP = "\u2019"  # the curved apostrophe
os.makedirs(SPECS, exist_ok=True)


def r(x, nd):
    q = Decimal(1).scaleb(-nd) if nd else Decimal(1)
    return Decimal(str(x)).quantize(q, rounding=ROUND_HALF_UP)


def mw(x):
    return f"{int(r(x, 0)):,} MW"


def pct(x, nd=1):
    return f"{r(x, nd)}%"


def usd(x):
    return f"${r(x, 2)}"


def read_repro(name):
    rows = {}
    for line in open(os.path.join(DATA, name), encoding="utf-8"):
        p = line.split()
        if len(p) >= 2:
            rows[int(p[0])] = float(p[1])
    return rows


def header_line(path, starts):
    for line in open(path, encoding="utf-8"):
        if not line.startswith("#"):
            break
        if line.startswith(starts):
            return line[1:].strip()
    return ""


def retrieved(table):
    return header_line(os.path.join(OUT, table + ".csv"), "# Retrieved:")


def write_data(post, payload):
    payload["post"] = post
    payload["built_by"] = "docs/research/motion/posts/batch_2026-11-25/scripts/build_9901.py"
    payload["built_at"] = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
    json.dump(payload, open(os.path.join(DATA, post + ".json"), "w", encoding="utf-8"), indent=1, ensure_ascii=False)


def write_spec(post, option, typ, title, source, **kw):
    spec = {"id": f"{post}_{option}", "post": post, "option": option, "type": typ, "width": 1080, "height": 1080,
            "frames": 450, "title": title, "source": source}
    spec.update(kw)
    json.dump(spec, open(os.path.join(SPECS, f"{post}_{option}.json"), "w", encoding="utf-8"), indent=1, ensure_ascii=False)


def clock(he):
    """hour ending (1..24) as a clock time: 12 is noon, 24 is midnight"""
    if he == 12:
        return "noon"
    if he == 24:
        return "midnight"
    return f"{he % 12} {'am' if he < 12 else 'pm'}"


# ---- 1. Thanksgiving peak hour --------------------------------------------------------------------------------------
NAMES = {"SWPP": "Plains", "MISO": "Midwest", "PJM": "Mid-Atlantic", "NYIS": "New York", "ERCO": "Texas",
         "ISNE": "New England", "CISO": "California"}
summ = list(csv.DictReader(open(os.path.join(DATA, "thanksgiving_peak_hour_summary_rerun.csv"), encoding="utf-8")))
rows1 = []
for s in summ:
    n, t = float(s["median_thursday"]), float(s["median_thanksgiving"])
    assert n == int(n) and t == int(t), s
    n, t = int(n), int(t)
    sh = n - t
    rows1.append({"code": s["ba"], "label": NAMES[s["ba"]], "normal": n, "tg": t, "normalText": clock(n), "tgText": clock(t),
                  "shift": sh, "shiftText": f"{sh} h earlier" if sh else "same hour"})
rows1.sort(key=lambda x: -x["shift"])
expected1 = {"SWPP": (19, 10), "MISO": (18, 11), "PJM": (19, 12), "NYIS": (18, 13), "ERCO": (16, 12), "ISNE": (18, 15), "CISO": (18, 18)}
for x in rows1:
    assert (x["normal"], x["tg"]) == expected1[x["code"]], x

# B: the Mid-Atlantic grid's average hour, Thanksgiving against the three Thursdays before, 2019-2025
TZ = {"PJM": "America/New_York"}


def thanksgiving(y):
    d = date(y, 11, 1)
    return d + timedelta(days=(3 - d.weekday()) % 7 + 21)


days = {}
for y in range(2019, 2026):
    t = thanksgiving(y)
    days[t] = "tg"
    for k in (1, 2, 3):
        days[t - timedelta(days=7 * k)] = "normal"
H = defaultdict(dict)
with open(os.path.join(OUT, "eia930_ba_demand_hourly.csv"), encoding="utf-8") as f:
    for line in f:
        if not line.startswith("eia930:PJM,demand_mw,20"):
            continue
        row = line.rstrip("\n").split(",")
        if not ("2019" <= row[2][:4] <= "2025") or row[2][5:7] not in ("10", "11", "12"):
            continue
        ts = datetime.strptime(row[2], "%Y-%m-%dT%H:%M:%SZ").replace(tzinfo=timezone.utc)
        e = (ts + timedelta(hours=1)).astimezone(ZoneInfo("America/New_York"))
        he = e.hour if e.hour else 24
        d = e.date() if e.hour else e.date() - timedelta(days=1)
        if d in days and row[3] != "":
            H[d][he] = float(row[3])
prof = {}
for kind in ("normal", "tg"):
    ds = sorted(d for d in days if days[d] == kind)
    full = [d for d in ds if len(H[d]) == 24]
    assert len(full) == (21 if kind == "normal" else 7), (kind, len(full))
    prof[kind] = [statistics.mean(H[d][h] for d in full) for h in range(1, 25)]
pk = {k: max(range(24), key=lambda i: prof[k][i]) + 1 for k in prof}
assert pk == {"normal": 19, "tg": 12}, pk
data1 = {
    "title": "Hour of peak power demand, Thanksgiving vs normal days",
    "original_source": "EIA Form EIA-930, Hourly Electric Grid Monitor, six-month files",
    "erw_table": "eia930_ba_demand_hourly", "table_retrieved": retrieved("eia930_ba_demand_hourly"),
    "method_a": "For each grid, the local hour (hour ending, local prevailing time; MISO in Central) of highest demand on each Thanksgiving 2019-2025 and on the three Thursdays before each; the median of the 21 Thursdays and of the 7 Thanksgivings (scripts/thanksgiving_peaks.py of session 9900, rerun 25 November 2026, identical to the 24 November summary).",
    "rows_a": rows1,
    "method_b": "Mid-Atlantic grid (PJM), Eastern time: each hour ending's mean demand over the 7 Thanksgivings 2019-2025 and over the 21 Thursdays before them (all 24 hours present on every day).",
    "profile_b_mw": {k: [round(v, 3) for v in prof[k]] for k in prof},
    "peaks_b": {k: {"hour_ending": pk[k], "mw": round(max(prof[k]), 3)} for k in prof},
}
write_data("thanksgiving_peak_hour", data1)
T1 = "Hour of peak power demand, Thanksgiving vs normal days"
write_spec("thanksgiving_peak_hour", "a", "clockshift", T1,
           "Source: EIA-930 hourly demand, ERW table eia930_ba_demand_hourly. Median hour of peak demand (local time, hour ending) on Thanksgiving 2019-2025 and the three Thursdays before each. California" + RAP + "s recent midday peaks are battery charging counted as demand.",
           rows=[{k: x[k] for k in ("label", "normal", "tg", "normalText", "tgText", "shiftText")} for x in rows1],
           legend={"normal": "Normal Thursday", "tg": "Thanksgiving"})
ymax1 = 100000
write_spec("thanksgiving_peak_hour", "b", "curves", T1,
           "Source: EIA-930 hourly demand, ERW table eia930_ba_demand_hourly. Mid-Atlantic grid (PJM), Eastern time: the average of each hour (hour ending) over Thanksgiving 2019-2025 and over the three Thursdays before each.",
           caption="Mid-Atlantic grid (PJM), demand by hour",
           normal=[round(v, 3) for v in prof["normal"]], tg=[round(v, 3) for v in prof["tg"]],
           peaks={"normal": {"he": pk["normal"], "label": "Normal Thursday", "text": f"{clock(pk['normal'])}, {mw(max(prof['normal']))}"},
                  "tg": {"he": pk["tg"], "label": "Thanksgiving", "text": f"{clock(pk['tg']).capitalize()}, {mw(max(prof['tg']))}"}},
           yMax=ymax1, yTicks=[{"v": v, "label": f"{v:,}"} for v in (0, 25000, 50000, 75000, 100000)],
           yUnit="MW", xTicks=[{"he": h, "label": clock(h)} for h in (6, 12, 18, 24)])

# ---- 2. Thanksgiving gasoline -----------------------------------------------------------------------------------------
api = json.load(open(os.path.join(DATA, "eia_gasoline_weekly_2026-11-25.json"), encoding="utf-8"))
apiv = {x["period"]: float(x["value"]) for x in api["response"]["response"]["data"]}
erw = {}
with open(os.path.join(OUT, "eia_retail_fuel_prices.csv"), encoding="utf-8") as f:
    for row in csv.DictReader(l for l in f if not l.startswith("#")):
        if row["entity"] == "eia:EMM_EPMR_PTE_NUS_DPG":
            erw[row["ts_utc"][:10]] = float(row["value"])
weeks = sorted(d for d in apiv if d >= "2020-01-06")
for d in weeks:
    if d in erw:
        assert erw[d] == apiv[d], d
series2 = [{"week": d, "value": erw.get(d, apiv[d]), "from": "eia_retail_fuel_prices" if d in erw else "EIA API v2 (retrieved " + api["retrieved_at"] + ")"} for d in weeks]
tgw = []
for y in range(2020, 2027):
    m = (thanksgiving(y) - timedelta(days=3)).isoformat()
    v = erw.get(m, apiv.get(m))
    tgw.append({"year": y, "week_of": m, "value": v, "display": usd(v), "from": "eia_retail_fuel_prices" if m in erw else "EIA API v2"})
assert [x["display"] for x in tgw] == ["$2.10", "$3.40", "$3.65", "$3.29", "$3.04", "$3.06", "$3.64"], tgw
assert max(x["value"] for x in tgw) == 3.648
write_data("thanksgiving_gasoline", {
    "title": "U.S. gasoline price on Thanksgiving week, 2020-2026",
    "original_source": "EIA, Gasoline and Diesel Fuel Update, weekly U.S. regular all formulations retail price (series EMM_EPMR_PTE_NUS_DPG), dollars per gallon",
    "erw_table": "eia_retail_fuel_prices", "table_retrieved": retrieved("eia_retail_fuel_prices"),
    "api_read": {"retrieved_at": api["retrieved_at"], "file": "data/eia_gasoline_weekly_2026-11-25.json", "note": "the week of 2026-11-23 is not yet in the ERW table; every one of the 359 overlapping weeks from 2020-01-06 equals the table"},
    "thanksgiving_weeks": tgw, "note": "2026 ($3.642) is not a record: 2022 was $3.648. Weekly high since 2020: $5.006 on 2022-06-13.",
    "weekly_series": series2,
})
T2 = "U.S. gasoline price on Thanksgiving week, 2020-2026"
S2 = "Source: EIA weekly U.S. regular retail gasoline price, ERW table eia_retail_fuel_prices (the week of 23 November 2026 from EIA" + RAP + "s API). Thanksgiving week is its Monday" + RAP + "s price. Dollars per gallon, not adjusted for inflation."
idx = {d: i for i, d in enumerate(weeks)}
write_spec("thanksgiving_gasoline", "a", "weekline", T2, S2,
           values=[x["value"] for x in series2], dots=[{"i": idx[x["week_of"]], "label": x["display"], **({"below": True} if x["year"] in (2020, 2024, 2026) else {})} for x in tgw],
           yMax=5.5, yTicks=[{"v": v, "label": f"${v}"} for v in range(0, 6)],
           xTicks=[{"i": next(i for i, d in enumerate(weeks) if d >= f"{y}-01-01"), "label": str(y)} for y in range(2020, 2027)])
write_spec("thanksgiving_gasoline", "b", "columns", T2, S2,
           rows=[{"label": str(x["year"]), "value": x["value"], "display": x["display"]} for x in tgw], highlight=6, max=4.2)

# ---- 3. California batteries against peak-day demand ------------------------------------------------------------------
s10 = read_repro("s10_caiso_battery.txt")
st3 = [{"year": y, "value": s10[y], "display": pct(s10[y])} for y in range(2019, 2026)]
assert [x["display"] for x in st3] == ["0.6%", "1.5%", "7.5%", "13.4%", "24.0%", "32.8%", "46.6%"]
write_data("caiso_battery_peak", {
    "title": "California" + RAP + "s battery power vs peak-day demand, 2019-2025",
    "original_source": "EIA-860M (operating battery capacity, CAISO, December of each year) via ERW storage_buildout_monthly; EIA-930 daily demand (CISO) via ERW eia930_daily_demand",
    "erw_tables": ["storage_buildout_monthly", "eia930_daily_demand"],
    "tables_retrieved": [retrieved("storage_buildout_monthly"), retrieved("eia930_daily_demand")],
    "method": "battery_operating_mw of iso:caiso at December's end, as a percent of the mean of the year's ten highest daily demands of CISO divided by 24 (average MW); docs/findings/cross_family/battery-per-peak-caiso-bat-peak.reproduce.py, rerun 25 November 2026",
    "values": st3,
})
T3 = "California" + RAP + "s battery power vs peak-day demand, 2019-2025"
S3 = "Source: EIA-860M battery capacity in December and EIA-930 demand, ERW tables storage_buildout_monthly and eia930_daily_demand. Peak-day demand: CAISO" + RAP + "s average demand on its ten highest days of the year."
write_spec("caiso_battery_peak", "a", "fillblock", T3, S3, steps=st3, blockLabel="Peak-day demand", fillLabel="Installed battery power")
write_spec("caiso_battery_peak", "b", "yearline", T3, S3, mode="area", points=st3, yMax=50,
           yTicks=[{"v": v, "label": f"{v}%"} for v in (0, 10, 20, 30, 40, 50)], xTicks=list(range(2019, 2026)))

# ---- 4. Canada to New York ----------------------------------------------------------------------------------------------
s8 = read_repro("s8_canada_ny.txt")
st4 = [{"year": y, "value": s8[y], "display": mw(s8[y])} for y in range(2019, 2026)]
assert [x["display"] for x in st4] == ["1,992 MW", "1,975 MW", "1,889 MW", "1,655 MW", "778 MW", "553 MW", "211 MW"]
write_data("canada_new_york_flow", {
    "title": "Power flow from Canada to New York, 2019-2025",
    "original_source": "EIA Form EIA-930, region-pair interchange (six-month files), Canada (CAN) to New York (NY)",
    "erw_table": "eia930_region_pair_hourly", "table_retrieved": retrieved("eia930_region_pair_hourly"),
    "method": "mean of the hourly interchange_mw of eia930:CAN-NY (MW sent from Canada to New York) by UTC year, an hour above three times the year's 99th percentile of absolute flow dropped; docs/findings/trade/pair-flow-rp-can-ny.reproduce.py, rerun 25 November 2026",
    "values": st4,
})
T4 = "Power flow from Canada to New York, 2019-2025"
S4 = "Source: EIA-930 interchange between regions, ERW table eia930_region_pair_hourly. The average hourly flow of power from Canada into New York in each year, in megawatts."
write_spec("canada_new_york_flow", "a", "flowband", T4, S4, steps=st4, fromLabel="Canada", toLabel="New York")
write_spec("canada_new_york_flow", "b", "columns", T4, S4,
           rows=[{"label": str(x["year"]), "value": x["value"], "display": x["display"]} for x in st4], highlight=6, max=2300)

# ---- 5. Dominion ----------------------------------------------------------------------------------------------------------
s1 = read_repro("s1_dominion.txt")
lv = [{"year": y, "value": s1[y], "display": mw(s1[y])} for y in range(2019, 2026)]
steps5 = []
for a, b in zip(lv, lv[1:]):
    d = b["value"] - a["value"]
    steps5.append({"label": str(b["year"]), "from": a["value"], "to": b["value"], "delta": d,
                   "display": ("+" if d >= 0 else "-") + f"{int(r(abs(d), 0)):,}"})
tot = lv[-1]["value"] - lv[0]["value"]
assert [x["display"] for x in steps5] == ["-177", "+909", "+699", "+157", "+923", "+1,204"], steps5
write_data("dominion_mean_hour", {
    "title": "Power demand in Dominion" + RAP + "s Virginia zone, 2019-2025",
    "original_source": "EIA Form EIA-930 subregion demand (PJM, Dominion zone, eia930_subba:PJM:DOM)",
    "erw_tables": [f"eia930_subba_demand_hourly_{y}" for y in range(2019, 2026)],
    "tables_retrieved": [retrieved(f"eia930_subba_demand_hourly_{y}") for y in (2019, 2025)],
    "method": "mean hourly demand by local year (America/New_York), an hour at or below zero or above three times its year's median dropped; docs/findings/demand/sub-mean-pjm-sub-dom.reproduce.py, rerun 25 November 2026",
    "levels": lv, "steps": steps5, "total_change": tot, "total_display": "+" + f"{int(r(tot, 0)):,} MW",
    "rounding_note": "each step is rounded from its own unrounded change; the six rounded steps sum to 3,715 while the rounded total is 3,716",
})
T5 = "Power demand in Dominion" + RAP + "s Virginia zone, 2019-2025"
S5 = "Source: EIA-930 subregion demand, ERW tables eia930_subba_demand_hourly_2019 to _2025. PJM" + RAP + "s Dominion zone. Average hourly demand in each calendar year, Eastern time. Changes are rounded one by one."
write_spec("dominion_mean_hour", "a", "staircase", T5, S5,
           base={"label": "2019", "value": lv[0]["value"], "display": lv[0]["display"]}, steps=steps5,
           total={"label": "Since 2019", "value": tot, "display": "+" + f"{int(r(tot, 0)):,} MW"},
           last={"value": lv[-1]["value"], "display": lv[-1]["display"]}, max=17000)
write_spec("dominion_mean_hour", "b", "yearline", T5, S5, mode="line", points=lv, yMax=16000,
           yTicks=[{"v": v, "label": f"{v:,}"} for v in (0, 4000, 8000, 12000, 16000)], yUnit="MW", xTicks=list(range(2019, 2026)))

# ---- 6. ERCOT solar in the tightest hours -------------------------------------------------------------------------------
s3 = read_repro("s3_ercot_solar.txt")
st6 = [{"year": y, "value": s3[y], "display": pct(s3[y])} for y in range(2019, 2026)]
assert [x["display"] for x in st6] == ["71.1%", "73.8%", "71.4%", "57.6%", "48.7%", "33.1%", "5.0%"]
write_data("ercot_solar_tight_hours", {
    "title": "Solar output in Texas" + RAP + "s tightest grid hours, 2019-2025",
    "original_source": "EIA Form EIA-930 hourly demand and generation by source (per-BA workbooks) and EIA-860M generator inventory, via the ERW derived table grid_stress_yearly (warehouse/derived/mix_stress.py, docs/methods/grid_stress.md)",
    "erw_table": "grid_stress_yearly", "table_retrieved": retrieved("grid_stress_yearly"),
    "method": "tight_solar_share_of_capacity_pct of iso:ercot: solar's output in the year's 100 hours of highest net load (demand less wind less solar) as a percent of installed solar capacity; docs/findings/markets_operations/tight-solar-ercot-tight-solar.reproduce.py, rerun 25 November 2026",
    "values": st6,
})
T6 = "Solar output in Texas" + RAP + "s tightest grid hours, 2019-2025"
S6 = "Source: ERW table grid_stress_yearly, from EIA-930 hourly data and EIA-860M capacity. ERCOT" + RAP + "s tightest hours: the 100 of each year with the highest demand less wind and solar. Output as a share of solar capacity."
write_spec("ercot_solar_tight_hours", "a", "waffle", T6, S6, steps=st6, unitText="of solar capacity",
           squareNote="Each square: 1% of capacity")
write_spec("ercot_solar_tight_hours", "b", "yearline", T6, S6, mode="line", points=st6, yMax=100,
           yTicks=[{"v": v, "label": f"{v}%"} for v in (0, 25, 50, 75, 100)], xTicks=list(range(2019, 2026)))

# ---- 7. Texas late-January peak -----------------------------------------------------------------------------------------
s21 = read_repro("s21_texas.txt")
lv7 = [{"year": y, "value": s21[y], "display": mw(s21[y])} for y in range(2020, 2027)]
assert [x["display"] for x in lv7] == ["47,074 MW", "51,607 MW", "53,813 MW", "65,552 MW", "54,806 MW", "70,603 MW", "75,599 MW"]
write_data("texas_cold_peak", {
    "title": "Texas peak power demand in late January, 2020-2026",
    "original_source": "EIA Form EIA-930 hourly demand, region TEX (ERCOT)",
    "erw_table": "eia930_ba_demand_hourly", "table_retrieved": retrieved("eia930_ba_demand_hourly"),
    "method": "the highest hour of the Texas region's demand from 23 January to 2 February (UTC days; every year holds all 264 hours); docs/findings/events/cold-2026-tex.reproduce.py, rerun 25 November 2026",
    "values": lv7,
})
T7 = "Texas peak power demand in late January, 2020-2026"
S7 = "Source: EIA-930 hourly demand, ERW table eia930_ba_demand_hourly. Texas (ERCOT): the highest hour of demand from 23 January to 2 February (UTC days) of each year."
write_spec("texas_cold_peak", "a", "ladder2", T7, S7,
           lead={"label": "2026", "sub": "23 Jan to 2 Feb", "value": lv7[-1]["value"], "display": lv7[-1]["display"]},
           rows=[{"label": str(x["year"]), "value": x["value"], "display": x["display"]} for x in lv7[:-1]], max=80000)
write_spec("texas_cold_peak", "b", "columns", T7, S7,
           rows=[{"label": str(x["year"]), "value": x["value"], "display": x["display"]} for x in lv7], highlight=6, max=86000)

# ---- 8. Uranium of U.S. origin --------------------------------------------------------------------------------------------
s24 = read_repro("s24_uranium.txt")
pts8 = [{"year": y, "value": s24.get(y), "display": pct(s24[y]) if y in s24 else None} for y in range(2003, 2026)]
lbs = {}
with open(os.path.join(OUT, "eia_uranium_marketing_annual.csv"), encoding="utf-8") as f:
    for row in csv.DictReader(l for l in f if not l.startswith("#")):
        if row["ts_utc"].startswith("2025") and row["variable"] in ("purchased_us_origin", "purchased_foreign_origin", "purchased_total"):
            lbs[row["variable"]] = float(row["value"])
assert abs(100 * lbs["purchased_us_origin"] / lbs["purchased_total"] - s24[2025]) < 1e-5
write_data("uranium_us_origin", {
    "title": "U.S.-origin share of uranium for U.S. reactors, 2003-2025",
    "original_source": "EIA, Uranium Marketing Annual Report (Form EIA-858), summary tables S1a to S3b",
    "erw_table": "eia_uranium_marketing_annual", "table_retrieved": retrieved("eia_uranium_marketing_annual"),
    "method": "purchased_us_origin over purchased_total (pounds U3O8e) by year; EIA withheld or printed no U.S.-origin figure for 2019, 2020 and 2022 (no row, nothing filled); docs/findings/coal_uranium_metals/us-origin-uranium-us-uranium-origin.reproduce.py, rerun 25 November 2026",
    "values": pts8, "pounds_2025": lbs,
    "country_of_origin": "not in the ERW table (it holds U.S. and foreign origin only), so option A is the 100-square grid the prompt names as the fallback",
})
T8 = "U.S.-origin share of uranium for U.S. reactors, 2003-2025"
S8 = "Source: EIA Uranium Marketing Annual Report (Form EIA-858), ERW table eia_uranium_marketing_annual. Uranium bought by owners and operators of U.S. reactors. EIA published no U.S.-origin figure for 2019, 2020 and 2022."
write_spec("uranium_us_origin", "a", "waffle", T8, S8,
           steps=[{"year": 2025, "value": s24[2025], "display": pct(s24[2025])}], unitText="of U.S. origin",
           squareNote="Each square: 1% of the uranium bought",
           extra=f"{r(lbs['purchased_us_origin'] / 1e6, 1)} million lb of {r(lbs['purchased_total'] / 1e6, 1)} million lb")
write_spec("uranium_us_origin", "b", "yearline", T8, S8, mode="line", points=pts8, yMax=25,
           yTicks=[{"v": v, "label": f"{v}%"} for v in (0, 5, 10, 15, 20, 25)], xTicks=[2003, 2008, 2013, 2018, 2025])

# ---- 9. U.S. share of world oil ------------------------------------------------------------------------------------------
s37 = read_repro("s37_oil.txt")
pts9 = [{"year": y, "value": s37[y], "display": pct(s37[y])} for y in range(1995, 2026)]
prod = defaultdict(dict)
names = {}
area = {}
with open(os.path.join(OUT, "eia_world_oil_monthly.csv"), encoding="utf-8") as f:
    for row in csv.DictReader(l for l in f if not l.startswith("#")):
        if row["variable"] == "production" and row["entity"].endswith(":53") and row["ts_utc"].startswith("2025"):
            c = row["entity"].split(":")[1]
            prod[c][row["ts_utc"]] = float(row["value"])
            names[c] = row["node"].split(",")[0]
            area[c] = row["x_area"]
world = sum(prod["WORL"].values())
assert len(prod["WORL"]) == 12
cty = {c: sum(m.values()) for c, m in prod.items() if area[c] == "country" and len(m) == 12}
top = sorted(cty, key=lambda c: -cty[c])[:9]
assert top[0] == "USA"
SHORT = {"USA": "United States", "ARE": "UAE"}
items9 = [{"code": c, "label": SHORT.get(c, names[c]), "kbd_2025_mean": cty[c] / 12, "share": 100 * cty[c] / world,
           "display": pct(100 * cty[c] / world)} for c in top]
other = world - sum(cty[c] for c in top)
items9.append({"code": "OTHER", "label": "All other countries", "kbd_2025_mean": other / 12, "share": 100 * other / world,
               "display": pct(100 * other / world)})
assert items9[0]["display"] == pct(s37[2025]) == "22.3%"
write_data("us_share_world_oil", {
    "title": "U.S. share of world oil and liquids production, 1995-2025",
    "original_source": "EIA International Energy Statistics (bulk file INTL.zip), total petroleum and other liquids production (product 53), thousand barrels a day, monthly",
    "erw_table": "eia_world_oil_monthly", "table_retrieved": retrieved("eia_world_oil_monthly"),
    "method_b": "U.S. (USA:53) months summed over the world's (WORL:53) months, by year; docs/findings/oil_products_world/us-liquids-share-us-world-liquids.reproduce.py, rerun 25 November 2026",
    "values_b": pts9,
    "countries_in_other": len(cty) - 9,
    "method_a": "2025: each country's 12 monthly values summed (x_area country, product 53) over the world's 12 summed; the nine largest countries, and all other countries as the world less those nine",
    "blocks_a_2025": items9,
})
T9 = "U.S. share of world oil and liquids production, 1995-2025"
S9 = "Source: EIA International Energy Statistics, ERW table eia_world_oil_monthly. Production of crude oil and other liquids, the U.S. as a share of the world. Recent years include EIA estimates."
write_spec("us_share_world_oil", "a", "treemap", T9, S9,
           items=[{"label": x["label"], "value": x["share"], "display": x["display"], "lead": x["code"] == "USA", **({"countText": f"{len(cty) - 9} countries"} if x["code"] == "OTHER" else {})} for x in items9],
           leadSub="share of world output in 2025")
write_spec("us_share_world_oil", "b", "yearline", T9, S9, mode="area", points=pts9, yMax=25,
           yTicks=[{"v": v, "label": f"{v}%"} for v in (0, 5, 10, 15, 20, 25)], xTicks=[1995, 2000, 2005, 2010, 2015, 2020, 2025])
print("data files and specs written")
for x in items9:
    print(x["label"], x["display"])

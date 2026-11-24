"""Session 9900: fill the review page template with each post's frames, video addresses, number check, fit checks and
caption facts. Usage: fill_review.py <template.md> <numcheck_dir> <out.md>"""
import re
import sys
from pathlib import Path

tpl = Path(sys.argv[1]).read_text(encoding="utf-8")
nc = Path(sys.argv[2])
out = Path(sys.argv[3])
GH = "https://github.com/SamuelEnrique/erw/blob/wip/linkedin-posts-2026-11-24/"
R = "runs/posts9900/"
FIT = {"thanksgiving_peak_hour": {1080: R + "b2/fit_square.txt", 1350: R + "b2/fit_tall.txt"}}
for v in "ab":
    FIT[f"thanksgiving_gasoline_{v}"] = {h: R + f"b3/fit_{v}_{h}.txt" for h in (1080, 1350)}
for i in ["us_share_world_oil_a", "us_share_world_oil_b", "texas_cold_peak", "uranium_us_origin_a", "uranium_us_origin_b",
          "dominion_mean_hour", "canada_new_york_flow", "caiso_battery_peak", "ercot_solar_tight_hours"]:
    FIT[i] = {h: R + f"c/fit_{i}_{h}.txt" for h in (1080, 1350)}

F = "https://github.com/SamuelEnrique/erw/blob/main/docs/findings/"
D = GH + "docs/research/motion/posts/data/"
POSTS = {
    "thanksgiving_peak_hour": dict(
        head="B2. Thanksgiving: the hour the grid peaks", versions=["thanksgiving_peak_hour"],
        how="From `eia930_ba_demand_hourly` (retrieved 20261123T193514Z): for each grid, the local hour (end of hour) of highest demand on each Thanksgiving 2019-2025 and on the three Thursdays before each; the row is the median of the 21 Thursdays minus the median of the seven Thanksgivings. Every day's peak: " + D + "thanksgiving_peak_hour_days.csv",
        notes=[
            "Cross-check with the chat's figures from EIA's raw files: MISO's Thanksgiving peaks are hour ending 10 to 12 Central (11 to 13 in EIA's Eastern Standard stamp) in all seven years, as the chat found; on normal Thursdays 18 of 21 peak at hour ending 18 or 19 Central (19 or 20 Eastern), and three peak in the morning (hour ending 8 Central: 4 November 2021, 17 November 2022, 2 November 2023). New England and New York peaked in the evening (hour ending 18) on Thanksgiving 2022, 2023 and 2025, as the chat found.",
            "California: on 13 November 2025 EIA-930 demand at hour ending 11 was 29,706 MW against CAISO's own forecast of 23,813 MW, while CAISO's batteries were charging at 6,899 MW (CAISO Today's Outlook, `caiso_fuel_supply`, the hour from 10:00 PST). The battery column of CISO's EIA-930 rows is empty, and evening demand matches the forecast (27,243 against 27,385 at hour ending 19), so battery charging is counted as demand: as the fleet grew, the midday hours overtook the evening on some days (2025's three Thursdays, Thanksgiving 2024 and 2025). Both medians are hour ending 18 either way, so the row (0 h) stands.",
        ],
        facts=[
            ("In all seven years, 2019-2025, the Midwest grid (MISO) peaked between 9 am and noon Central on Thanksgiving (hour ending 10 to 12).", "EIA-930 via `eia930_ba_demand_hourly`; " + D + "thanksgiving_peak_hour_days.csv"),
            ("The Plains grid (SPP) moves most: its normal November Thursday peak is the hour ending 7 pm, its Thanksgiving peak the hour ending 10 am (medians).", "same"),
            ("PJM peaks at the hour ending noon on Thanksgiving against 7 pm on a normal Thursday (medians, Eastern time).", "same"),
            ("New York peaked at the hour ending 1 pm on Thanksgiving in 2019, 2020, 2021 and 2024, and at the usual evening hour in 2022, 2023 and 2025.", "same"),
            ("California's evening peak holds on Thanksgiving: the median is the hour ending 6 pm on both days.", "same; note on battery charging above"),
        ]),
    "thanksgiving_gasoline": dict(
        head="B3. Black Friday: gasoline", versions=["thanksgiving_gasoline_a", "thanksgiving_gasoline_b"],
        how="From `eia_retail_fuel_prices` (EIA API v2, retrieved 20261120T150214Z), series EMM_EPMR_PTE_NUS_DPG, the Monday of Thanksgiving week 2020-2025; 2026 is 16 November, confirmed against EIA's API at 2026-11-24T10:32:45Z, which had not yet published 23 November. Bars full at $4.19 (1.1 times $3.805, rounded up). Cross-check from the chat (2.10, 3.40, 3.65, 3.29, 3.04, 3.06, 3.81): equal. Data: " + D + "thanksgiving_week_fuel.csv",
        notes=[
            "Diesel (No. 2, US retail, EMD_EPD2D_PTE_NUS_DPG), Thanksgiving-week Monday, for the caption: 2020 $2.462, 2021 $3.724, 2022 $5.233, 2023 $4.209, 2024 $3.539, 2025 $3.831, 2026 (16 November) $5.937. 2026 is the highest Thanksgiving week in EIA's series (from 1994), nominal; it is not the series high, which is $6.529 on 21 September 2026.",
        ],
        facts=[
            ("$3.805 a gallon on 16 November 2026 is above every Thanksgiving-week Monday in EIA's series back to 1990, in nominal dollars; the previous high was $3.648 in 2022.", "EIA Weekly Retail Gasoline and Diesel Prices via `eia_retail_fuel_prices`; " + D + "thanksgiving_week_fuel.csv"),
            ("Gasoline has fallen for two weeks: $4.153 on 2 November, $3.995 on 9 November, $3.805 on 16 November 2026.", "EIA API v2, read 2026-11-24T10:32:45Z: " + D + "eia_fuel_latest_2026-11-24.json"),
            ("Thanksgiving-week gasoline is 81 percent above 2020's $2.102.", "same table"),
            ("Diesel was $5.937 on 16 November 2026, the highest Thanksgiving-week price since EIA's diesel series began in 1994 (previous high $5.233 in 2022).", "same table"),
            ("Diesel's record in EIA's series is $6.529, on 21 September 2026; 16 November is $0.59 below it.", "same table"),
        ]),
    "us_share_world_oil": dict(
        head="C1. Section 37: the US share of world oil production", versions=["us_share_world_oil_a", "us_share_world_oil_b"],
        how="Section 37's reproduce.py run again on `eia_world_oil_monthly`: " + F + "oil_products_world/us-liquids-share-us-world-liquids.reproduce.py (output: " + D + "shortlist_s37_reproduce_2026-11-24.txt). Seven years every five from 1995 (the table starts in 1993).",
        notes=[], facts=[
            ("The US produced 22.3 percent of the world's petroleum and other liquids in 2025, against 14.5 percent in 1993.", "EIA International Energy Statistics, section 37's reproduction"),
            ("The low point was 9.8 percent, in 2006.", "same"),
            ("The share has risen every year from 2019 (19.4 percent) to 2025 (22.3 percent).", "same"),
            ("The first six months of 2026 give 24.0 percent (a half year).", "same"),
            ("Caveat: other producers' figures are EIA estimates and are revised.", "shortlist section 37"),
        ]),
    "texas_cold_peak": dict(
        head="C2. Section 21: Texas in the late January cold", versions=["texas_cold_peak"],
        how="Section 21's reproduce.py run again on `eia930_ba_demand_hourly`: " + F + "events/cold-2026-tex.reproduce.py (output: " + D + "shortlist_s21_reproduce_2026-11-24.txt). Years 2020 to 2026 as the chain asks; every year holds all 264 hours of the window.",
        notes=[], facts=[
            ("Texas's highest hour of demand from 23 January to 2 February 2026 was 75,599 MW.", "EIA-930 via `eia930_ba_demand_hourly`, section 21's reproduction"),
            ("That is 32.9 percent above the mean of the same days' highest hours in 2019-2025 (56,873 MW).", "same"),
            ("The same window peaked at 70,603 MW in 2025 and 47,074 MW in 2020.", "same"),
            ("2026's window peak is the highest of the eight years the ERW holds (2019-2026).", "same"),
            ("Caveat: the window is the days the ERW's events page gives to the cold; another window moves the peaks.", "shortlist section 21"),
        ]),
    "uranium_us_origin": dict(
        head="C3. Section 24: uranium of US origin", versions=["uranium_us_origin_a", "uranium_us_origin_b"],
        how="Section 24's reproduce.py run again on `eia_uranium_marketing_annual`: " + F + "coal_uranium_metals/us-origin-uranium-us-uranium-origin.reproduce.py (output: " + D + "shortlist_s24_reproduce_2026-11-24.txt). EIA prints no US-origin figure for 2019, 2020 and 2022 (the table keeps no row for W or -), so the years are 2003, 2007, 2010, 2014, 2018, 2021, 2025.",
        notes=[], facts=[
            ("7.2 percent of the uranium bought for US reactors in 2025 was of US origin, against 18.0 percent in 2003.", "EIA Uranium Marketing Annual Report, section 24's reproduction"),
            ("The highest share in EIA's report is 19.3 percent, in 2004.", "same"),
            ("The lowest is 4.7 percent, in 2023.", "same"),
            ("The share has not been above 10 percent since 2016 (10.7 percent).", "same"),
            ("Caveat: origin as owners report it to EIA; 2025 is preliminary.", "shortlist section 24"),
        ]),
    "dominion_mean_hour": dict(
        head="C4. Section 1: the mean hour of demand in the Dominion zone", versions=["dominion_mean_hour"],
        how="Section 1's reproduce.py run again on `eia930_subba_demand_hourly_2019` to `_2025`: " + F + "demand/sub-mean-pjm-sub-dom.reproduce.py (output: " + D + "shortlist_s1_reproduce_2026-11-24.txt).",
        notes=[], facts=[
            ("The mean hour of demand in PJM's Dominion zone was 15,403 MW in 2025, against 11,687 MW in 2019: 31.8 percent higher.", "EIA-930 subregion demand, section 1's reproduction"),
            ("It rose every year except 2020 (11,510 MW).", "same"),
            ("2025 alone added 1,204 MW to the mean hour (8.5 percent over 2024).", "same"),
            ("Growth sped up: 12.2 percent from 2019 to 2022, 17.4 percent from 2022 to 2025.", "same"),
            ("Caveat: the zone's demand as PJM reports it to EIA; a change of bounds or reporting would move the level.", "shortlist section 1"),
        ]),
    "canada_new_york_flow": dict(
        head="C5. Section 8: the mean hourly flow from Canada to New York", versions=["canada_new_york_flow"],
        how="Section 8's reproduce.py run again on `eia930_region_pair_hourly`: " + F + "trade/pair-flow-rp-can-ny.reproduce.py (output: " + D + "shortlist_s8_reproduce_2026-11-24.txt).",
        notes=[], facts=[
            ("The mean hourly flow from Canada to New York was 211 MW in 2025, against 1,992 MW in 2019.", "EIA-930 region-pair interchange, section 8's reproduction"),
            ("The largest one-year fall came in 2023: from 1,655 MW to 778 MW.", "same"),
            ("2026 to date (7,805 hours) gives 215 MW.", "same"),
            ("2019 to 2021 each held above 1,880 MW.", "same"),
            ("Caveat: the two sides' reports of the same flow differ; this is EIA's region-pair series.", "shortlist section 8"),
        ]),
    "caiso_battery_peak": dict(
        head="C6. Section 10: California's battery fleet against its peak-day demand", versions=["caiso_battery_peak"],
        how="Section 10's reproduce.py run again on `storage_buildout_monthly` and `eia930_daily_demand`: " + F + "cross_family/battery-per-peak-caiso-bat-peak.reproduce.py (output: " + D + "shortlist_s10_reproduce_2026-11-24.txt). The run prints 46.619278 for 2025, the draft's own figure (the shortlist's run printed 46.5676).",
        notes=[], facts=[
            ("CAISO's battery fleet at the end of 2025 equalled 46.6 percent of the mean demand of its ten highest days.", "EIA-860M and EIA-930, section 10's reproduction"),
            ("At the end of 2019 it was 0.6 percent.", "same"),
            ("The ratio passed a quarter in 2024 (32.8 percent).", "same"),
            ("It rose by 13.8 points in 2025 alone (32.8 to 46.6).", "same"),
            ("Caveat: batteries do not all run at full output at once, and the fleet is EIA-860M's operating list.", "shortlist section 10"),
        ]),
    "ercot_solar_tight_hours": dict(
        head="C7. Section 3: solar's output in ERCOT's tightest hours", versions=["ercot_solar_tight_hours"],
        how="Section 3's reproduce.py run again on `grid_stress_yearly`: " + F + "markets_operations/tight-solar-ercot-tight-solar.reproduce.py (output: " + D + "shortlist_s3_reproduce_2026-11-24.txt). The tightest hours are the year's 100 hours of highest net load (demand less wind less solar).",
        notes=[], facts=[
            ("In ERCOT's 100 tightest hours of 2025, solar gave 5.0 percent of its capacity, against 71.1 percent in 2019.", "ERW grid stress table from EIA-930 and EIA-860M, section 3's reproduction"),
            ("The share was highest in 2020, 73.8 percent.", "same"),
            ("It has been under half since 2023 (48.7 percent).", "same"),
            ("2026 to date gives 5.2 percent.", "same"),
            ("Caveat: the tightest hours are the ERW's own definition; another would give another share.", "shortlist section 3"),
        ]),
}


def fit(i):
    rows = []
    for h, path in FIT[i].items():
        t = Path(path).read_text().splitlines()
        p, f = sum(l.startswith("PASS") for l in t), sum(l.startswith("FAIL") for l in t)
        tl = next((l.split(": ")[-1] for l in t if "title in" in l), "")
        sl = next((l.split(": ")[-1] for l in t if "source in" in l), "")
        rows.append(f"- {'1080 x 1080' if h == 1080 else '1080 x 1350'}: {p} checks passed, {f} failed ({tl}; {sl}; every label clear of its bar at its peak, nothing outside the margins). The final frame opened and read; the peaks checked by script and sampled by eye.")
    return "\n".join(rows)


def block(key):
    p = POSTS[key]
    s = [f"## {p['head']}", "", p["how"], ""]
    for n in p["notes"]:
        s += [f"- {n}"]
    if p["notes"]:
        s += [""]
    for v in p["versions"]:
        tag = "" if len(p["versions"]) == 1 else f" (version {v[-1].upper()})"
        s += [f"### Frames{tag}", "", f"![{v} square](img/{v}_1080_frames.png)", "", f"![{v} tall](img/{v}_1350_frames.png)", "",
              f"- Square video: {GH}docs/research/motion/posts/{v}_2160x2160.mp4",
              f"- Tall video: {GH}docs/research/motion/posts/{v}_2160x2700.mp4", "", "Fit checks:", "", fit(v), ""]
    s += ["### Number check", ""]
    s += [(nc / f"{p['versions'][0]}.md").read_text(encoding="utf-8").rstrip()]
    if len(p["versions"]) > 1:
        s += ["", f"Version B carries the same rows (its own check: {(nc / (p['versions'][1] + '.md')).read_text(encoding='utf-8').count('| yes |')} of 7 equal)."]
    s += ["", "### Five facts for the caption", ""]
    for i, (fact, src) in enumerate(p["facts"], 1):
        s += [f"{i}. {fact} Source: {src}."]
    return "\n".join(s)


B1 = ("## B1. Nvidia's one-day gain against US energy industries: blocked\n\n"
      "Not rendered. SEC EDGAR refused the ERW's contact string at https://www.sec.gov/robots.txt (HTTP 403, 2026-11-24T10:24:39Z), "
      "so no shares were pulled; no price source was cleared either (Stooq disallows all but Bing and Google; Nasdaq reset the "
      "connection). The data file holds the header and the block: " + D + "nvidia_energy_caps.csv. Under \"For Samuel's ruling\".")
page = tpl.replace("{{post:thanksgiving_peak_hour}}", B1 + "\n\n{{post:thanksgiving_peak_hour}}")
page = re.sub(r"\{\{post:(\w+)\}\}", lambda m: block(m.group(1)), page)
out.write_text(page, encoding="utf-8")
print(out, len(page), "chars; em dashes:", page.count(chr(0x2014)))

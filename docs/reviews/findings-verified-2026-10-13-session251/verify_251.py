"""Session 251: verify the weekly hunt's new drafts (the measure families of hunt_measures.py) as they stand in
public.scanner_drafts, the way session 252 verified the first sixteen.

For each draft raised by session 251's hunt (rule "hunt", raised at or after 18:00 UTC on 13 October 2026), kept by
fetch_drafts.py under runs/session251/drafts/<id>/:
  1. its own Python mirror is run on its own CSV (a subprocess), and what it prints is kept;
  2. the claim and the three tests are recomputed from the CSV by hunt.test_claim and compared, key by key and
     exactly, with what the draft stores (flag.claim, flag.tests, card.numbers, the second number beside the claim),
     and the fact line and the caption are written again from those numbers and compared character by character;
  3. the CSV is rebuilt from today's warehouse tables by the family's own measure and compared year by year, and the
     tables the draft names are compared with the tables the measure says that region's rows come from;
  4. session 252's five further tests (verify_hunt.more_tests, imported from the folder above);
  5. the family's question asked another way ("other cuts"): a second definition of the same thing, computed here
     from the tables and apart from the measure's own code where the table allows it.
No row of the review list is written. Output: runs/session251/verify_251.json and one block a draft on the screen.
Exit 0: every draft reproduces. 1: one does not, named.
"""
import csv
import json
import math
import os
import re
import subprocess
import sys

import numpy as np
import pandas as pd

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = HERE
while not os.path.exists(os.path.join(ROOT, "ARCHITECTURE.md")):   # the repository root, from runs/ or from docs/
    ROOT = os.path.dirname(ROOT)
sys.path.insert(0, os.path.join(ROOT, "warehouse", "analysis", "findings"))
sys.path.insert(0, os.path.join(ROOT, "docs", "reviews", "findings-verified-2026-10-13"))
sys.dont_write_bytecode = True                     # session 252's folder is listed by its test: leave no __pycache__ in it
import findings_common as common  # noqa: E402
import hunt  # noqa: E402
import hunt_measures as hm  # noqa: E402
from verify_hunt import more_tests  # noqa: E402

DRAFTS = os.path.join(ROOT, "runs", "session251", "drafts")
OUT = os.path.join(ROOT, "runs", "session251", "verify_251.json")
SINCE = "2026-10-13T18:00"
THIS_YEAR = 2026
PAT = {P["name"]: P for P in hunt.PATTERNS}
_built = {}


def read_csv(path):
    rows = list(csv.DictReader(ln for ln in open(path, encoding="utf-8") if not ln.startswith("#")))
    series = {r["year"]: (float(r["value"]), float(r["n_observations"])) for r in rows}
    context = {r["year"]: float(r["context_value"]) for r in rows if r.get("context_value") not in (None, "")}
    return series, [r["year"] for r in rows if r["full_year"] == "1"], context


def rebuild(P, region):
    """The region's series, its second number and its tables from today's warehouse tables, by the family's measure."""
    if P["fn"] not in _built:
        _built[P["fn"]] = hm.run(P["fn"], common.DEFAULT_IN_DIR)
    got = _built[P["fn"]]
    context = {str(r["year"]): r["context"] for r in got["rows"] if str(r["region"]) == region and r.get("context") is not None}
    return hunt.yearly(got["rows"], P, region), context, list(got["tables"].get(region, []))


# ---------------------------------------------------------------------------------------------------------------------
# other cuts: each returns {name: {year: value}}
# ---------------------------------------------------------------------------------------------------------------------
def by_year(frame, value="value"):
    return {str(int(y)): float(v) for y, v in frame.items() if v is not None and not (isinstance(v, float) and math.isnan(v))}


def cut_evening_ramp(region):
    V = ["evening_ramp_median_mw_per_h", "peak_demand_mw", "evening_ramp_max_share_of_peak_pct", "evening_ramp_3h_max_share_of_peak_pct"]
    d = hm.series("grid_stress_yearly", None, variables=V, entities=[f"iso:{region}"])
    w = d.pivot_table(index=d["ts"].dt.year, columns="variable", values="value")
    return {"the median ramp as a percent of the year's peak demand": by_year(w["evening_ramp_median_mw_per_h"] / w["peak_demand_mw"] * 100),
            "the year's largest one-hour ramp as a percent of peak demand (the table's own column; one hour a year)": by_year(w["evening_ramp_max_share_of_peak_pct"]),
            "the year's largest three-hour ramp as a percent of peak demand (the table's own column; one evening a year)": by_year(w["evening_ramp_3h_max_share_of_peak_pct"])}


def cut_battery(region):
    c = pd.concat([hm.series("caiso_fuel_supply_history", None, variables=["batteries_mw"], entities=["caiso:ISO"]),
                   hm.series("caiso_fuel_supply", None, variables=["batteries_mw"], entities=["caiso:ISO"])]).drop_duplicates("ts_utc")
    local = c["ts"].dt.tz_convert(hm.TZ["caiso"])
    d = pd.DataFrame({"year": local.dt.year.values, "h": local.dt.hour.values, "out": c["value"].clip(lower=0).values})
    out = {}
    for name, (a, b) in (("discharge from 4 PM to 9 PM local, percent of the year's", (16, 20)), ("discharge from 6 PM to 10 PM local, percent of the year's", (18, 21))):
        out[name] = {str(int(y)): float(s.loc[s["h"].between(a, b), "out"].sum() / s["out"].sum() * 100) for y, s in d.groupby("year") if s["out"].sum() > 0}
    out["the year's discharge, GWh (how large the fleet behind each share was)"] = {str(int(y)): float(s["out"].sum() / 1000) for y, s in d.groupby("year")}
    return out


def cut_negative(region):
    node = region.split("_", 1)[1]
    d = common.read_table("ercot_zone_prices_history", None, usecols=["ts_utc", "value", "market", "node"], keep=lambda c: (c["market"] == "ercot_rtm") & (c["node"] == node))
    d["value"] = d["value"].astype(float)
    t = common.to_utc(d["ts_utc"])
    d["year"] = t.dt.tz_convert(hm.TZ["ercot"]).dt.year
    d["hour"] = t.dt.floor("h")
    h = d.groupby(["year", "hour"], as_index=False)["value"].mean()
    return {"15-minute intervals below zero, percent of the year's intervals": {str(int(y)): float((s["value"] < 0).mean() * 100) for y, s in d.groupby("year")},
            "hours with a mean price below minus USD 10, percent of the year's hours": {str(int(y)): float((s["value"] < -10).mean() * 100) for y, s in h.groupby("year")}}


def cut_spread(region):
    grid, rest = region.split("_", 1)
    node, part = rest.rsplit("_", 1)
    h0, h1 = next((a, b) for name, _, a, b in hm.DAY_PARTS if name == part)
    e = hm.ercot_prices(None)
    g = e[(e["node"] == node) & e["lhour"].between(h0, h1)].dropna(subset=["rt", "da"])
    return {"the mean hour's day-ahead price minus its real-time price, USD per MWh": {str(int(y)): float((s["da"] - s["rt"]).mean()) for y, s in g.groupby("year")},
            "hours with the day-ahead price above the real-time price, percent": {str(int(y)): float((s["da"] > s["rt"]).mean() * 100) for y, s in g.groupby("year")}}


def cut_curtailment(region):
    V = ["curtailed_solar_mwh", "solar_generation_mwh", "curtailed_wind_mwh", "wind_generation_mwh"]
    d = hm.series("iso_curtailment_monthly", None, variables=V, entities=["caiso:ISO"])
    w = d.pivot_table(index="ts", columns="variable", values="value").dropna()
    y = w.groupby(w.index.year).sum()
    n = w.groupby(w.index.year).size()
    y = y[n == 12]
    return {"solar alone: curtailed over output plus curtailed, percent": by_year(y["curtailed_solar_mwh"] / (y["curtailed_solar_mwh"] + y["solar_generation_mwh"]) * 100),
            "wind alone: curtailed over output plus curtailed, percent": by_year(y["curtailed_wind_mwh"] / (y["curtailed_wind_mwh"] + y["wind_generation_mwh"]) * 100),
            "curtailed energy in the year, GWh": by_year((y["curtailed_solar_mwh"] + y["curtailed_wind_mwh"]) / 1000)}


def cut_stress(region):
    ba = next(b for b, g in hm.BA_GRID.items() if g == region)
    d = hm._daily_demand(None)
    d = d[d["ba"] == ba]
    t = hm.series("eia930_daily_total_interchange", None, variables=["total_interchange_mwh"], entities=[f"eia930:{ba}"]).drop_duplicates(["entity", "ts_utc"])
    j = d.merge(t[["ts_utc", "value"]].rename(columns={"value": "ti"}), on="ts_utc")
    out = {"the 10 percent of days with the highest demand": {}, "every day of the year": {}, "days held with both demand and interchange": {}}
    for y, s in j.groupby("year"):
        top = s.nlargest(max(1, int(math.ceil(0.10 * len(s)))), "value")
        out["the 10 percent of days with the highest demand"][str(int(y))] = float(-top["ti"].sum() / top["value"].sum() * 100)
        out["every day of the year"][str(int(y))] = float(-s["ti"].sum() / s["value"].sum() * 100)
        out["days held with both demand and interchange"][str(int(y))] = float(len(s))
    return out


def cut_demand(region):
    ba = next(b for b, g in hm.BA_GRID.items() if g == region)
    d = common.read_table("eia930_demand_weather", None, usecols=["entity", "variable", "ts_utc", "value", "x_window"],
                          keep=lambda c: (c["entity"] == f"eia930:{ba}") & (c["x_window"].isin(["the year", "left out of the fit"])))
    d["value"] = d["value"].astype(float)
    w = d.pivot_table(index=d["ts_utc"].str[:4].astype(int), columns="variable", values="value")
    out = {"the year's energy above the base before weather is taken out, percent (energy_growth_pct)": by_year(w["energy_growth_pct"].dropna()),
           "the part of it weather explains, percent (energy_weather_pct)": by_year(w["energy_weather_pct"].dropna()),
           "the fit's own uncertainty, percent (energy_uncertainty_pct)": by_year(w["energy_uncertainty_pct"].dropna())}
    if "energy_holdout_unexplained_pct" in w:
        out["the same measure in the base years, left out of the fit one at a time (energy_holdout_unexplained_pct)"] = by_year(w["energy_holdout_unexplained_pct"].dropna())
    return out


def cut_carbon(region):
    ba = next(b for b, g in hm.BA_GRID.items() if g == region)
    d = hm.series("carbon_intensity_hourly", None, variables=["intensity_demand", "intensity_generation"], entities=[f"eia930:{ba}"])
    local = d["ts"].dt.tz_convert(hm.TZ[region])
    w = pd.DataFrame({"year": local.dt.year.values, "h": local.dt.hour.values, "v": d["value"].values, "var": d["variable"].values})
    dem, gen = w[w["var"] == "intensity_demand"], w[w["var"] == "intensity_generation"]
    prem = lambda s, a, b: float((s.loc[s["h"].between(a, b), "v"].mean() / s["v"].mean() - 1) * 100)  # noqa: E731
    return {"the same premium on the intensity of generation, percent": {str(int(y)): prem(s, 17, 21) for y, s in gen.groupby("year")},
            "the premium from 4 PM to 9 PM local, percent": {str(int(y)): prem(s, 16, 20) for y, s in dem.groupby("year")},
            "the evening's own intensity, kg CO2 per MWh": {str(int(y)): float(s.loc[s["h"].between(17, 21), "v"].mean()) for y, s in dem.groupby("year")},
            "the all-hours intensity, kg CO2 per MWh": {str(int(y)): float(s["v"].mean()) for y, s in dem.groupby("year")}}


def cut_wind(region):
    d = hm.series("generation_mix_hourly_profile", None, variables=["wind_mwh", "net_generation_mwh"], entities=[f"iso:{region}"])
    w = d.pivot_table(index="ts", columns="variable", values="value").dropna()
    y = w.groupby(w.index.year).sum()
    allh = by_year(y["wind_mwh"] / y["net_generation_mwh"] * 100)
    night, _, _ = rebuild(PAT["wind_night_share"], region)
    return {"wind's share of the grid's generation in every hour, percent": allh,
            "the night's share minus the all-hours share, points (is it the night, or wind as a whole)": {k: night[k][0] - allh[k] for k in night if k in allh}}


CUTS = {"evening_ramp": cut_evening_ramp, "battery_evening_discharge": cut_battery, "negative_hours_zones": cut_negative, "da_rt_spread": cut_spread,
        "curtailment_share": cut_curtailment, "stress_day_imports": cut_stress, "demand_growth_weather_adjusted": cut_demand, "peak_hour_carbon": cut_carbon,
        "wind_night_share": cut_wind}


def cuts_for(P, region, c):
    """Each other cut read on the claim's own years: first, last, the change, whether it points the claim's way, and
    every year held."""
    fn = CUTS.get(P["fn"])
    if fn is None:
        return []
    s = 1 if c["change"] > 0 else -1
    out = []
    for name, series in fn(region).items():
        a, b = series.get(c["first_year"]), series.get(c["last_year"])
        row = {"name": name, "by_year": {k: series[k] for k in sorted(series)}, "first": a, "last": b}
        if a is not None and b is not None:
            row["change"] = b - a
            row["same_direction"] = (b - a) * s > 0
        out.append(row)
    return out


def main():
    index = [x for x in json.load(open(os.path.join(DRAFTS, "index.json"), encoding="utf-8")) if x["rule"] == "hunt" and x["raised_at"] >= SINCE]
    results = []
    for x in index:
        did = x["id"]
        d = os.path.join(DRAFTS, did)
        row = json.load(open(os.path.join(d, "row.json"), encoding="utf-8"))
        flag, card = row["flag"], row["card"]
        P = PAT[flag["pattern"]]
        region = flag["region"]
        res = {"id": did, "state": row["state"], "raised_at": x["raised_at"], "pattern": P["name"], "measure": P["fn"], "region": region, "words": card["hunt"]["region_words"],
               "strength": row["strength"], "fact": card["subtitle"], "tables": card["tables"], "source_line": card["source_line"], "problems": []}
        r = subprocess.run([sys.executable, f"{did}.py", f"{did}.csv"], cwd=d, capture_output=True, text=True, stdin=subprocess.DEVNULL)
        res["mirror_exit"], res["mirror_out"] = r.returncode, r.stdout.strip().splitlines()
        if r.returncode != 0:
            res["problems"].append(f"the mirror exited {r.returncode}: {r.stderr.strip()[:200]}")
        series, full_csv, context = read_csv(os.path.join(d, f"{did}.csv"))
        c = hunt.test_claim(series, P, THIS_YEAR)
        if c is None:
            res["problems"].append("no claim can be computed from the CSV")
            results.append(res)
            continue
        if c["years"] != full_csv:
            res["problems"].append(f"the CSV marks {full_csv} as full; the rule gives {c['years']}")
        beside = hunt.beside_of(P, c, context)
        compared = 0
        for k, v in flag["claim"].items():
            compared += 1
            if c[k] != v:
                res["problems"].append(f"flag.claim.{k}: stored {v!r}, recomputed {c[k]!r}")
        for k, v in card["numbers"].items():
            mine = {"first_year": int(c["first_year"]), "last_year": int(c["last_year"]), "full_years": len(c["years"]),
                    "context_first": context.get(c["first_year"]), "context_last": context.get(c["last_year"])}.get(k, c.get(k))
            compared += 1
            if mine != v:
                res["problems"].append(f"card.numbers.{k}: stored {v!r}, recomputed {mine!r}")
        for a, b in zip(flag["tests"], c["tests"]):
            compared += 2
            if a != b:
                res["problems"].append(f"test '{a['name']}': stored {a!r}, recomputed {b!r}")
        res["row_value_column"] = {"stored": row["value"], "recomputed": c["change"], "equal_in_full": row["value"] == c["change"],
                                   "equal_at_15_digits": float(f"{row['value']:.15g}") == float(f"{c['change']:.15g}")}
        if not res["row_value_column"]["equal_at_15_digits"] or row["strength"] != c["strength"]:
            res["problems"].append(f"the row's value or strength: stored {row['value']!r}, {row['strength']!r}; recomputed {c['change']!r}, {c['strength']!r}")
        compared += 2
        m = re.match(r"claim: (\S+) in (\d{4}), (\S+) in (\d{4}); change (\S+)", res["mirror_out"][0]) if res["mirror_out"] else None
        if not m or (float(m.group(1)), m.group(2), float(m.group(3)), m.group(4), float(m.group(5))) != (c["first"], c["first_year"], c["last"], c["last_year"], c["change"]):
            res["problems"].append(f"the mirror's claim line does not equal the stored claim: {res['mirror_out'][:1]}")
        verdicts = [ln.rsplit(": ", 1)[-1] for ln in res["mirror_out"][1:4]]
        if verdicts != ["pass" if t["passed"] else "fail" for t in flag["tests"]]:
            res["problems"].append(f"the mirror's three verdicts {verdicts} differ from the stored tests")
        compared += 8
        words = card["hunt"]["region_words"]
        if hunt.fact_of(P, words, c, beside) != card["subtitle"]:
            res["problems"].append("the fact line written again from the numbers differs from the stored one")
        src = card["source_line"].replace(" Found by the weekly hunt.", "")
        if hunt.caption_of(P, words, c, src, beside) != card["hunt"]["caption"]:
            res["problems"].append("the caption written again from the numbers differs from the stored one")
        if open(os.path.join(d, f"{did}_caption.txt"), encoding="utf-8").read().rstrip("\n") != card["hunt"]["caption"]:
            res["problems"].append("the caption file differs from the card's caption")
        compared += 3
        res["numbers_compared"] = compared
        res["claim"] = {k: c[k] for k in ("first_year", "last_year", "first", "last", "change", "direction", "years_held", "years_after", "typical_move", "strength", "n_first", "n_last", "passed")}
        res["tests"] = c["tests"]
        res["unit"], res["decimals"], res["label"] = P["unit"], P["decimals"], P["label"]
        res["series"] = {y: list(v) for y, v in series.items()}
        res["context"] = dict(P["context"], values=context, beside=beside.strip()) if P.get("context") else None
        res["reproduced_from_own_csv"] = not res["problems"]
        today, today_context, today_tables = rebuild(P, region)
        diffs = []
        for y in sorted(set(series) | set(today)):
            a, b = series.get(y), today.get(y)
            if a is None or b is None or a[0] != b[0] or a[1] != b[1]:
                diffs.append({"year": y, "csv": a, "today": b, "full": y in c["years"]})
        res["today_diffs"] = diffs
        res["context_diffs"] = sorted(y for y in set(context) | set(today_context) if context.get(y) != today_context.get(y)) if beside else []
        res["reproduced_from_tables_full_years"] = not any(d_["full"] for d_ in diffs) and not res["context_diffs"]
        res["tables_are_the_measures_own"] = today_tables == card["tables"]
        if not res["tables_are_the_measures_own"]:
            res["problems"].append(f"the draft names {card['tables']}; the measure says the region's rows come from {today_tables}")
        if not res["reproduced_from_tables_full_years"]:
            res["problems"].append("a full year, or the second number, differs when rebuilt from today's tables")
        res["more"] = more_tests(series, c["years"], c)
        res["cuts"] = cuts_for(P, region, c)
        results.append(res)
        print(f"{did}  {P['name']} {region}: own CSV {'EXACT' if res['reproduced_from_own_csv'] else 'DIFFERS'} ({compared} values compared); "
              f"today's tables, full years {'EXACT' if res['reproduced_from_tables_full_years'] else 'DIFFER'} ({len(diffs)} year(s) differ in all); "
              f"tables {'its own' if res['tables_are_the_measures_own'] else 'DIFFER'}; tests {sum(1 for t in c['tests'] if t['passed'])} of 3; strength {c['strength']}")
        for p in res["problems"]:
            print(f"    PROBLEM: {p}")
        print("    by year: " + ", ".join(f"{y} {series[y][0]:.3f}" for y in sorted(series)))
        print(f"    more: {json.dumps(res['more'], default=str)}")
        for cut in res["cuts"]:
            print(f"    cut, {cut['name']}: " + ", ".join(f"{y} {v:.2f}" for y, v in cut["by_year"].items()) + (f"; same direction {cut['same_direction']}" if "same_direction" in cut else "; not held in both years"))
    with open(OUT, "w", encoding="utf-8", newline="\n") as f:
        json.dump(results, f, indent=1, ensure_ascii=False, default=str)
        f.write("\n")
    bad = [r for r in results if r["problems"]]
    print(f"{len(results)} hunt drafts of session 251; {len(results) - len(bad)} reproduce exactly from their own CSV and rebuild exactly from today's tables")
    return 1 if bad or not results else 0


if __name__ == "__main__":
    sys.exit(main())

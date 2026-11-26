"""Session 10214 (demand audit): one rule of /demand changed at a time, each measured on the restated rows (restate.py)
and the page's own files. Standard library only.

  A. The base year: 2019 (the page) against the mean of 2019 to 2021 (the weather view's base), 2021 and 2022.
  B. Two endpoints against a trend: the compound rate of 2019 to 2025 against a least-squares line through the logs of
     every whole year (and without 2020).
  C. The cell the summary names "largest": the same rule with 2023 or 2024 as the last year; January's heating degree
     days in ERCOT's five cities in 2019, 2024 and 2025 (noaa_grid_weather_daily).
  D. EIA's Demand in place of its Adjusted demand; no neighbour test (restate.py --column demand, --no-neighbour).
  E. The weather view's split of the same growth (site/data/demand_weather.json).

Usage: python measures.py <restate_oct.json> <restate_raw.json> <restate_nonb.json> <site demand_weather.json> <noaa_grid_weather_daily.csv> <out json>
"""
import csv
import json
import math
import sys

NAMES = {"ERCO": "ERCOT", "CISO": "CAISO", "PJM": "PJM", "MISO": "MISO", "SWPP": "SPP", "NYIS": "NYISO", "ISNE": "ISO-NE", "US48": "Lower 48"}
MONTHS = ["January", "February", "March", "April", "May", "June", "July", "August", "September", "October", "November", "December"]


def ols_rate(years, vals):
    xs, ys = years, [math.log(v) for v in vals]
    mx, my = sum(xs) / len(xs), sum(ys) / len(ys)
    b = sum((x - mx) * (y - my) for x, y in zip(xs, ys)) / sum((x - mx) ** 2 for x in xs)
    return 100 * (math.exp(b) - 1)


def main(oct_p, raw_p, nonb_p, wx_p, noaa_p, out):
    R = json.load(open(oct_p, encoding="utf-8"))["areas"]
    RAW = json.load(open(raw_p, encoding="utf-8"))["areas"]
    NB = json.load(open(nonb_p, encoding="utf-8"))["areas"]
    WX = json.load(open(wx_p, encoding="utf-8"))
    res, lines = {"A_B": {}, "C": {}, "D": {}, "E": {}}, []
    lines.append("A and B. Growth of average demand to 2025, percent, on four bases; and the rate a year two ways")
    lines.append("area | on 2019 (page) | on the mean of 2019-2021 | on 2021 | on 2022 | a year, endpoints 2019-2025 | a year, trend of 2019-2025 | trend without 2020 | largest year-on-year")
    for ba, r in R.items():
        a = {int(y): v["avg_demand_mw"] for y, v in r["years"].items() if "avg_demand_mw" in v}
        g = lambda b: 100 * (a[2025] - b) / b
        m3 = (a[2019] + a[2020] + a[2021]) / 3
        ys = sorted(a)
        cagr = 100 * ((a[2025] / a[2019]) ** (1 / 6) - 1)
        tr = ols_rate(ys, [a[y] for y in ys])
        tr2 = ols_rate([y for y in ys if y != 2020], [a[y] for y in ys if y != 2020])
        yoy = max(((y, 100 * (a[y] / a[y - 1] - 1)) for y in ys if y - 1 in a), key=lambda x: abs(x[1]))
        res["A_B"][ba] = dict(g2019=g(a[2019]), g1921=g(m3), g2021=g(a[2021]), g2022=g(a[2022]), cagr=cagr, trend=tr, trend_no2020=tr2, largest_yoy=yoy)
        lines.append(f"{NAMES[ba]} | {g(a[2019]):+.2f} | {g(m3):+.2f} | {g(a[2021]):+.2f} | {g(a[2022]):+.2f} | {cagr:+.2f} | {tr:+.2f} | {tr2:+.2f} | {yoy[0]} {yoy[1]:+.2f}")
    lines.append("")
    lines.append("C. The largest and smallest month-and-hour cell against 2019, with the last year moved")
    for ba, r in R.items():
        b = r["years"]["2019"]
        out_c = {}
        for L in ("2023", "2024", "2025"):
            cs = []
            for m in range(1, 13):
                for h in range(24):
                    k = f"avg_demand_mw_m{m:02d}_h{h:02d}"
                    if k in b and k in r["years"][L]:
                        cs.append((round(100 * (r["years"][L][k] - b[k]) / b[k], 2), m, h))
            if not cs:
                continue
            hi = max(cs, key=lambda c: c[0])
            lo = min(cs, key=lambda c: c[0])
            out_c[L] = dict(most=hi, least=lo, cells=len(cs))
        res["C"][ba] = out_c
        lines.append(f"{NAMES[ba]}: " + "; ".join(f"to {L}: largest {MONTHS[v['most'][1] - 1]} {v['most'][2]:02d}:00 {v['most'][0]:+.2f}, smallest {MONTHS[v['least'][1] - 1]} {v['least'][2]:02d}:00 {v['least'][0]:+.2f}" for L, v in out_c.items()))
    # the January 02:00 cell of ERCOT in each year, and January's heating degree days
    e = R["ERCO"]["years"]
    jan2 = {y: e[y].get("avg_demand_mw_m01_h02") for y in sorted(e) if e[y].get("avg_demand_mw_m01_h02")}
    hdd = {}
    with open(noaa_p, newline="", encoding="utf-8") as f:
        rd = csv.reader(line for line in f if not line.startswith("#"))
        head = next(rd)
        ie, iv, it, ival = head.index("entity"), head.index("variable"), head.index("ts_utc"), head.index("value")
        for row in rd:
            if row[ie] == "iso:ercot" and row[iv] == "heating_degree_days" and row[it][5:7] == "01":
                hdd[row[it][:4]] = hdd.get(row[it][:4], 0.0) + float(row[ival])
    res["C"]["ERCO_jan_02"] = dict(cell_mw=jan2, january_hdd=hdd)
    lines.append("ERCOT, January at 02:00, MW by year: " + ", ".join(f"{y} {v:,.0f}" for y, v in jan2.items()))
    lines.append("ERCOT, January heating degree days (five cities, weighted): " + ", ".join(f"{y} {v:,.0f}" for y, v in sorted(hdd.items())))
    lines.append("")
    lines.append("D. EIA's Demand in place of its Adjusted demand, and no neighbour test: growth to 2025, percent")
    for ba in R:
        def g(src, k):
            y = src[ba]["years"]
            return y.get("2025", {}).get(k)
        row = {k: (g(R, k), g(RAW, k), g(NB, k)) for k in ("avg_demand_growth_since_2019_pct", "peak_demand_growth_since_2019_pct")}
        res["D"][ba] = row
        lines.append(f"{NAMES[ba]}: average {row['avg_demand_growth_since_2019_pct']}; peak {row['peak_demand_growth_since_2019_pct']} (page, Demand, no neighbour test)")
    # the largest move in any whole-year growth figure under each change
    for name, src in (("Demand", RAW), ("no neighbour test", NB)):
        worst = (0, None)
        for ba in R:
            for y in R[ba]["years"]:
                for k in ("avg_demand_growth_since_2019_pct", "peak_demand_growth_since_2019_pct", "avg_demand_growth_yoy_pct"):
                    a, b = R[ba]["years"][y].get(k), src[ba]["years"].get(y, {}).get(k)
                    if a is not None and b is not None and abs(a - b) > abs(worst[0]):
                        worst = (b - a, f"{NAMES[ba]} {y} {k}: {a} becomes {b}")
        res["D"][f"largest move, {name}"] = worst
        lines.append(f"largest move of a whole-year growth under '{name}': {worst[1]}")
    lines.append("")
    lines.append("E. The weather view's split of 2025's energy (against the mean of 2019 to 2021), beside the as-metered growth on 2019")
    for ba, gr in WX["grids"].items():
        en = gr["years"].get("2025", {}).get("energy")
        if not en:
            continue
        res["E"][ba] = dict(metered_on_2019=R[ba]["years"]["2025"]["avg_demand_growth_since_2019_pct"], growth=en["growth_pct"], weather=en["weather_pct"], unexplained=en["unexplained_pct"], give_or_take=en["uncertainty_pct"], finding=en["finding"])
        lines.append(f"{NAMES[ba]}: as metered on 2019 {R[ba]['years']['2025']['avg_demand_growth_since_2019_pct']:+.2f}; weather view: growth {en['growth_pct']:+.2f} = weather {en['weather_pct']:+.2f} + not explained {en['unexplained_pct']:+.2f} (give or take {en['uncertainty_pct']:.2f}){' a finding' if en['finding'] else ''}")
    json.dump(res, open(out, "w", encoding="utf-8"), indent=1)
    print("\n".join(lines))


if __name__ == "__main__":
    main(*sys.argv[1:7])

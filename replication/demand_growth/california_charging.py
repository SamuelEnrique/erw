"""Energy Research Warehouse (ERW), session 7517 (chain 304, part B): California's demand growth and the batteries'
charging, the figures the demand growth explorer states in its decisions ("Demand at the grid is not sales to
customers") and docs/methods/demand_growth.md states under "California: the batteries' charging inside EIA's demand".

    python replication/demand_growth/california_charging.py            # the lines, from the rows beside this file
    python replication/demand_growth/california_charging.py --months   # each month as well

Written from the note's words, on public rows alone (california_rows.csv beside this file: rows copied unchanged from
shoulder_hours_monthly, eia930_demand_growth and eia_retail_sales_monthly). It reads no page code and asks nothing.

The rule, as the note states it:

1. A month's demand by EIA is eia930_demand_growth's avg_demand_mw_mMM for eia930:CISO (EIA Form EIA-930).
2. A month's charging is, on that month's average day by CAISO's own data (shoulder_hours_monthly, iso:caiso_own,
   avg_battery_mw_hHH), the sum over the hours whose figure is below zero, sign turned, divided by 24: MW on average.
3. A month's demand by CAISO's own data is the mean of its 24 avg_demand_mw_hHH.
4. A window of months is the mean of its months, each weighted by its days; growth is against the same months of 2019
   by EIA; "less the charging" takes the charging off the newer year only (the charging of 2019 is not held: the fleet
   was 186 MW at the end of 2019 and 15,760 MW in December 2025).
5. Retail sales are the sum of the window's months (eia_retail_sales_monthly, eia:retail_sales:CA:ALL), against the
   same months of 2019.
"""
import calendar
import csv
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
MONTHS = ["January", "February", "March", "April", "May", "June", "July", "August", "September", "October", "November", "December"]
WINDOWS = [("June to December 2025", 2025, range(6, 13)), ("January to August 2026", 2026, range(1, 9))]


def read(path=None):
    rows = {}
    with open(path or os.path.join(HERE, "california_rows.csv"), encoding="utf-8", newline="") as fh:
        body = [l for l in fh.read().replace("\r\n", "\n").split("\n") if l and not l.startswith("#")]
    for r in csv.DictReader(body):
        rows[(r["table"], r["variable"], r["ts_utc"][:7])] = float(r["value"])
    return rows


def month(rows, y, m):
    """One month: EIA's demand, CAISO's own demand, the charging, and EIA's demand of the same month of 2019."""
    ym = f"{y}-{m:02d}"
    hours = [rows.get(("shoulder_hours_monthly", f"avg_battery_mw_h{h:02d}", ym)) for h in range(24)]
    own = [rows.get(("shoulder_hours_monthly", f"avg_demand_mw_h{h:02d}", ym)) for h in range(24)]
    if any(x is None for x in hours + own):
        return None
    return {"ym": ym, "days": calendar.monthrange(y, m)[1],
            "eia": rows[("eia930_demand_growth", f"avg_demand_mw_m{m:02d}", f"{y}-01")],
            "eia_2019": rows[("eia930_demand_growth", f"avg_demand_mw_m{m:02d}", "2019-01")],
            "own": sum(own) / 24, "charging": -sum(x for x in hours if x < 0) / 24}


def window(rows, y, months):
    ms = [month(rows, y, m) for m in months]
    if any(m is None for m in ms):
        return None
    days = sum(m["days"] for m in ms)
    mean = lambda k: sum(m[k] * m["days"] for m in ms) / days
    eia, base, own, charging = mean("eia"), mean("eia_2019"), mean("own"), mean("charging")
    sales = sum(rows[("eia_retail_sales_monthly", "retail_sales", f"{y}-{m:02d}")] for m in months)
    sales_base = sum(rows[("eia_retail_sales_monthly", "retail_sales", f"2019-{m:02d}")] for m in months)
    return {"eia": eia, "base": base, "own": own, "charging": charging, "growth_mw": eia - base, "growth_pct": 100 * (eia / base - 1),
            "less_charging_pct": 100 * ((eia - charging) / base - 1), "own_pct": 100 * (own / base - 1),
            "share_pct": 100 * charging / (eia - base), "sales_pct": 100 * (sales / sales_base - 1)}


def signed(x):
    return ("+" if x > 0 else "") + f"{x:,.2f}"


def lines(rows):
    out = []
    for label, y, months in WINDOWS:
        w = window(rows, y, months)
        out.append(f"{label}: demand {signed(w['growth_pct'])} percent on the same months of 2019 ({w['base']:,.0f} to {w['eia']:,.0f} MW, {w['growth_mw']:+,.0f} MW); "
                   f"the charging {w['charging']:,.0f} MW; demand less the charging {signed(w['less_charging_pct'])} percent; CAISO's own demand {signed(w['own_pct'])} percent; "
                   f"retail sales {signed(w['sales_pct'])} percent; the charging is {w['share_pct']:,.0f} percent of the growth")
    held = [m for m in (month(rows, y, mo) for y in (2025, 2026) for mo in range(1, 13)) if m]
    near = sum(abs(m["eia"] - m["own"] - m["charging"]) <= 300 for m in held)
    out.append(f"EIA's demand less CAISO's own is the charging to within 300 MW in {near} of the {len(held)} months held ({held[0]['ym']} to {held[-1]['ym']})")
    return out, held


def main():
    rows = read()
    out, held = lines(rows)
    print("\n".join(out))
    if "--months" in sys.argv:
        for m in held:
            print(f"  {m['ym']}: EIA {m['eia']:,.1f} MW; CAISO's own {m['own']:,.1f}; the charging {m['charging']:,.1f}; EIA less own less charging {m['eia'] - m['own'] - m['charging']:+,.1f}; "
                  f"the same month of 2019 {m['eia_2019']:,.1f}; growth {signed(100 * (m['eia'] / m['eia_2019'] - 1))} percent, less the charging {signed(100 * ((m['eia'] - m['charging']) / m['eia_2019'] - 1))}")
    return 0


if __name__ == "__main__":
    sys.exit(main())

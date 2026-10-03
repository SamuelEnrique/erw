#!/usr/bin/env python3
"""The seller tab's California solar on CAISO's own solar shape (session 78). Analysis only: nothing live changes.

Energy Research Warehouse (ERW). merchant_revenue_monthly pays a merchant solar plant in CAISO on EIA-930's hourly
solar output per MW installed. Session 73 found EIA's California solar about 13 percent below CAISO's own, before and
after the break (caiso_join.JOIN). This sets the same arithmetic (warehouse/derived/merchant_revenue.py: hourly
output over the month's installed nameplate, EIA-860M, times the hourly real-time price at TH_SP15_GEN-APND, by Pacific
month) on CAISO's own solar (caiso_fuel_supply, solar_mw), and compares it with the table's rows.

    python warehouse/analysis/caiso_solar_seller.py

Writes runs/session78/seller_solar_caiso_shape.csv and prints it. No request; nothing in warehouse/output.
The arithmetic is checked first: on the hours eia930_all_generation holds EIA's solar (a rolling window), the same code
on EIA's solar must reproduce the table's own row for a month it holds completely.
"""

import os
import sys

import pandas as pd

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.abspath(os.path.join(HERE, "..", ".."))
for p in ("warehouse/connectors", "warehouse/derived"):
    sys.path.insert(0, os.path.join(ROOT, p))
import caiso_join as cj  # noqa: E402
import cost_of_power as cp  # noqa: E402
import merchant_revenue as mr  # noqa: E402
import price_board as pb  # noqa: E402

OUT = os.path.join(ROOT, "runs", "session78", "seller_solar_caiso_shape.csv")


def by_month(price, sun, gens, tz):
    """merchant_revenue.build_iso's solar arithmetic: per Pacific month, over the hours with a price and an output."""
    h = pd.DataFrame({"p": price}).join(sun.rename("sun"), how="left")
    h["month"] = h.index.tz_convert(tz).strftime("%Y-%m")
    out = {}
    for m, g in h.groupby("month"):
        cap = mr.capacity(gens, "CISO", "SUN", m)
        x = g.dropna(subset=["sun"])
        if cap <= 0 or not len(x):
            continue
        s = x["sun"] / cap
        if s.sum() <= 0:
            continue
        out[m] = dict(energy_per_mw=float(s.sum()), revenue_per_mw=float((s * x["p"]).sum()), hours=len(x), nameplate_mw=cap,
                      capture_price=float((s * x["p"]).sum() / s.sum()))
    return out


def main():
    quiet = lambda msg: None  # noqa: E731
    tz = pb.TZ["caiso"]
    price = cp.hourly(cp.prices_of("caiso", "rtm", quiet)[0])
    gens, _ = mr.read_gens()
    caiso = cj.caiso_hours()
    sun_c = pd.Series(caiso["solar_mw"].values, index=pd.to_datetime(caiso.index, utc=True))
    gen = pd.read_csv(os.path.join(cj.OUT_DIR, "eia930_all_generation.csv"), comment="#", usecols=["entity", "variable", "ts_utc", "value"])
    gen = gen[(gen["entity"] == cj.ENTITY) & (gen["variable"] == "net_generation_solar_mw")]
    sun_e = pd.Series(gen["value"].values, index=pd.to_datetime(gen["ts_utc"], utc=True))
    t = pd.read_csv(os.path.join(cj.OUT_DIR, "merchant_revenue_monthly.csv"), comment="#", dtype=str, keep_default_na=False)
    t = t[t["entity"].str.startswith("caiso:") & t["variable"].str.startswith("solar_")]
    tab = t.assign(m=t["ts_utc"].str[:7], v=t["value"].astype(float)).pivot(index="m", columns="variable", values="v")

    own, eia = by_month(price, sun_c, gens, tz), by_month(price, sun_e, gens, tz)
    rows = []
    for m in sorted(own):
        if m not in tab.index:
            continue
        r = dict(month=m, nameplate_mw=round(own[m]["nameplate_mw"], 1),
                 table_hours=int(tab.loc[m, "solar_hours"]), table_energy_per_mw=tab.loc[m, "solar_energy_per_mw"],
                 table_revenue_per_mw=tab.loc[m, "solar_revenue_per_mw"], table_capture_price=tab.loc[m, "solar_capture_price"],
                 caiso_hours=own[m]["hours"], caiso_energy_per_mw=round(own[m]["energy_per_mw"], 4),
                 caiso_revenue_per_mw=round(own[m]["revenue_per_mw"], 4), caiso_capture_price=round(own[m]["capture_price"], 4))
        same = r["table_hours"] == r["caiso_hours"]
        r["same_hours"] = "yes" if same else "no"
        r["energy_change_pct"] = round((r["caiso_energy_per_mw"] / r["table_energy_per_mw"] - 1) * 100, 1) if same else None
        r["revenue_change_usd_per_mw"] = round(r["caiso_revenue_per_mw"] - r["table_revenue_per_mw"], 2) if same else None
        r["revenue_change_pct"] = round((r["caiso_revenue_per_mw"] / r["table_revenue_per_mw"] - 1) * 100, 1) if same else None
        if m in eia:
            r["check_eia_hours"] = eia[m]["hours"]
            r["check_eia_energy_per_mw"] = round(eia[m]["energy_per_mw"], 4)
            r["check_eia_revenue_per_mw"] = round(eia[m]["revenue_per_mw"], 4)
        rows.append(r)
    d = pd.DataFrame(rows)
    os.makedirs(os.path.dirname(OUT), exist_ok=True)
    with open(OUT, "w", encoding="utf-8", newline="") as f:
        f.write("# ERW analysis, for review (session 78): the seller tab's CAISO solar on CAISO's own solar shape "
                "(caiso_fuel_supply solar_mw over EIA-860M's installed nameplate, times the hourly real-time price at "
                "TH_SP15_GEN-APND, by Pacific month) beside merchant_revenue_monthly's rows, which use EIA-930's solar. "
                "A change is given only for a month both rest on the same number of hours. check_eia_*: the same code on "
                "EIA's solar where eia930_all_generation holds it (warehouse/analysis/caiso_solar_seller.py).\n")
        d.to_csv(f, index=False, lineterminator="\n")
    pd.set_option("display.width", 320)
    print(d.to_string(index=False))
    s = d[d["same_hours"] == "yes"]
    if len(s):
        print(f"{len(s)} months on the same hours: table energy {s['table_energy_per_mw'].sum():.1f} MWh/MW against "
              f"{s['caiso_energy_per_mw'].sum():.1f} ({(s['caiso_energy_per_mw'].sum() / s['table_energy_per_mw'].sum() - 1) * 100:+.1f} percent); "
              f"table revenue {s['table_revenue_per_mw'].sum():,.0f} USD/MW against {s['caiso_revenue_per_mw'].sum():,.0f} "
              f"({(s['caiso_revenue_per_mw'].sum() / s['table_revenue_per_mw'].sum() - 1) * 100:+.1f} percent)")
    return 0


if __name__ == "__main__":
    sys.exit(main())

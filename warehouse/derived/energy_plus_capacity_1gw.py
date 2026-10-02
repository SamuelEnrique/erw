#!/usr/bin/env python3
"""A flat 1 GW for a year: wholesale energy next to capacity (session 65, Part E; internal, not a table)

Energy Research Warehouse (ERW). Session 62's draft compares regions on hub energy alone. ERCOT's energy price
carries its capacity cost; the other markets pay capacity apart. This sets the two side by side for Samuel's review
of that draft's first finding. It changes nothing in the draft and writes no warehouse table.

    python warehouse/derived/energy_plus_capacity_1gw.py --capacity runs/session65/iso_all_capacity_prices/iso_all_capacity_prices.csv

Reads warehouse/output/ai_power_regions.csv (flat_1gw_cost_usd, 2025-09-01 to 2026-09-01) and the capacity table
(default warehouse/output/iso_all_capacity_prices.csv; before the finish step it is still in the scratch directory).
Writes warehouse/output/analysis_internal/energy_plus_capacity_1gw.csv (gitignored, never uploaded).

The capacity cost of 1 GW, month by month over September 2025 to August 2026, at the clearing price whose delivery
period holds the month:

    a price in USD/kW-month   price x 1,000,000 kW x 1 month
    a price in USD/MW-day     price x 1,000 MW x the days of the month

and their sum over the twelve months. A region is "not held" when the warehouse holds no capacity price for it, or
when any of the twelve months has none: nothing is estimated, and a partial year is not summed.

What this is not. It is 1 GW of capacity bought at the auction price, a size, not a load's bill: a load's capacity
obligation is its peak share times the reserve requirement, in unforced or accredited MW, and most capacity is
self-supplied or contracted outside the auctions (in MISO and NYISO the auction clears the residual). The zones are
those of the hub the energy cost is read at.
"""

import argparse
import calendar
import os
import sys

import pandas as pd

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.abspath(os.path.join(HERE, "..", ".."))
OUT = os.path.join(ROOT, "warehouse", "output", "analysis_internal")
REGIONS_TABLE = os.path.join(ROOT, "warehouse", "output", "ai_power_regions.csv")
CAPACITY_TABLE = os.path.join(ROOT, "warehouse", "output", "iso_all_capacity_prices.csv")
MONTHS = pd.period_range("2025-09", "2026-08", freq="M")
WINDOW = "2025-09-01 to 2026-09-01 (twelve months)"
GW_KW, GW_MW = 1_000_000, 1_000

# region: (label, [(capacity zone label, market, entities in order of preference)], why no capacity price is held)
# ISO-NE prints one system price for some auctions and zone prices for others: the internal hub sits in the Rest of
# Pool zone, so that zone's price where the auction printed zones, else the system-wide price.
REGIONS = {
    "caiso": ("CAISO", [], "no capacity market; the CPUC's resource adequacy price statistics are not pulled"),
    "ercot": ("ERCOT", [], "energy-only market by design: no capacity price exists"),
    "isone": ("ISO-NE", [("Rest of Pool, else system-wide", "isone_fca", ["isone:ROP", "isone:System-wide"])], ""),
    "miso": ("MISO", [("Zone 6 (Indiana)", "miso_pra", ["miso:Z6"])], ""),
    "nyiso": ("NYISO", [("New York City", "nyiso_icap_spot", ["nyiso:NYC"]),
                        ("NYCA (statewide)", "nyiso_icap_spot", ["nyiso:NYCA"])], ""),
    "pjm": ("PJM", [("RTO", "pjm_bra", ["pjm:RTO"])], ""),
    "spp": ("SPP", [], "no capacity market: resource adequacy is met bilaterally"),
}


def month_cost(price, unit, period):
    """USD for 1 GW of capacity over one month at a clearing price, and the conversion in words."""
    if unit == "USD/kW-month":
        return price * GW_KW
    if unit == "USD/MW-day":
        return price * GW_MW * calendar.monthrange(period.year, period.month)[1]
    raise ValueError(f"unit {unit!r}: no conversion")


def capacity_year(cap, market, entities):
    """(total USD or None, months priced, the auctions used, the unit) for 1 GW over MONTHS. None when a month has no
    price: a partial year is not summed."""
    rows = cap[(cap["market"] == market) & (cap["variable"] == "capacity_price")]
    total, priced, auctions, units = 0.0, 0, [], set()
    for p in MONTHS:
        first, last = f"{p.year}-{p.month:02d}-01", f"{p.year}-{p.month:02d}-{calendar.monthrange(p.year, p.month)[1]:02d}"
        hit = None
        for e in entities:
            g = rows[(rows["entity"] == e) & (rows["ts_utc"].str[:10] <= first) & (rows["x_period_end"] >= last)]
            if len(g) > 1:
                raise RuntimeError(f"{e} {p}: {len(g)} prices cover the month")
            if len(g) == 1:
                hit = g.iloc[0]
                break
        if hit is None:
            continue
        total += month_cost(float(hit["value"]), hit["unit"], p)
        priced += 1
        units.add(hit["unit"])
        label = f"{hit['x_auction']} {hit['entity'].split(':', 1)[1]} {float(hit['value']):g}"
        if label not in auctions:
            auctions.append(label)
    return (total if priced == len(MONTHS) else None), priced, auctions, "/".join(sorted(units))


def build(regions, cap):
    energy = regions[(regions["variable"] == "flat_1gw_cost_usd") & (regions["x_window"] == WINDOW)]
    energy = dict(zip(energy["entity"].str.split(":").str[1], energy["value"].astype(float)))
    out = []
    for key, (label, zones, why) in REGIONS.items():
        e = energy.get(key)
        e_text = f"{e:.0f}" if e is not None else "not held"
        if not zones:
            out.append(dict(region=label, capacity_zone="", energy_flat_1gw_usd=e_text, capacity_1gw_usd="not held",
                            energy_plus_capacity_usd="not held", capacity_share_of_sum_pct="",
                            capacity_usd_per_kw_month="", capacity_usd_per_mwh_flat="", months_priced=0,
                            clearing_prices="", published_unit="", note=why))
            continue
        for zone, market, entities in zones:
            total, priced, auctions, unit = capacity_year(cap, market, entities)
            notes = []
            if e is None:
                notes.append("energy not held" + (": PJM's prices are licensed for internal use and its hub prices "
                                                  "are not in the warehouse" if key == "pjm" else ""))
            if total is None:
                notes.append(f"capacity price held for {priced} of {len(MONTHS)} months: not summed")
            both = total is not None and e is not None
            out.append(dict(
                region=label, capacity_zone=zone, energy_flat_1gw_usd=e_text,
                capacity_1gw_usd=f"{total:.0f}" if total is not None else "not held",
                energy_plus_capacity_usd=f"{e + total:.0f}" if both else "not held",
                capacity_share_of_sum_pct=f"{100 * total / (e + total):.1f}" if both else "",
                capacity_usd_per_kw_month=f"{total / GW_KW / len(MONTHS):.3f}" if total is not None else "",
                capacity_usd_per_mwh_flat=f"{total / (GW_MW * 8760):.2f}" if total is not None else "",
                months_priced=priced, clearing_prices="; ".join(auctions), published_unit=unit,
                note="; ".join(notes)))
    return pd.DataFrame(out)


def main(argv=None):
    ap = argparse.ArgumentParser(description="ERW: a flat 1 GW, energy next to capacity (internal)")
    ap.add_argument("--capacity", default=CAPACITY_TABLE, help="the capacity table (the scratch copy before the finish step)")
    a = ap.parse_args(argv)
    regions = pd.read_csv(REGIONS_TABLE, comment="#", dtype=str, keep_default_na=False)
    cap = pd.read_csv(a.capacity, comment="#", dtype=str, keep_default_na=False)
    t = build(regions, cap)
    os.makedirs(OUT, exist_ok=True)
    now = pd.Timestamp.now(tz="UTC").strftime("%Y-%m-%dT%H:%M:%SZ")
    path = os.path.join(OUT, "energy_plus_capacity_1gw.csv")
    with open(path, "w", encoding="utf-8", newline="") as f:
        f.write("# Energy Research Warehouse (ERW), session 65, internal analysis (not a warehouse table): a flat 1 GW "
                "for September 2025 to August 2026, wholesale energy next to capacity at the auction clearing prices\n"
                f"# Derived from: ai_power_regions (flat_1gw_cost_usd); iso_all_capacity_prices "
                f"({os.path.relpath(a.capacity, ROOT).replace(os.sep, '/')}). Built by "
                f"warehouse/derived/energy_plus_capacity_1gw.py at {now}.\n"
                "# Conversions: USD/kW-month x 1,000,000 kW per month; USD/MW-day x 1,000 MW x the days of the month; "
                "summed over the twelve months. capacity_usd_per_kw_month is that sum / 1,000,000 kW / 12; "
                "capacity_usd_per_mwh_flat is that sum / 8,760,000 MWh. Energy is the real-time flat hub price x 8,760 "
                "h x 1,000 MW (ai_power_regions).\n"
                "# 'not held' is never an estimate: no capacity market, a price the warehouse does not hold, or a year "
                "with a month unpriced. 1 GW of capacity at the auction price is a size, not a load's bill (see the "
                "script's header). Internal: PJM's, ISO-NE's and MISO's prices are not for republishing.\n")
        t.to_csv(f, index=False, lineterminator="\n")
    pd.set_option("display.width", 250, "display.max_columns", 30, "display.max_colwidth", 60)
    print(t.drop(columns=["note"]).to_string(index=False))
    return 0


if __name__ == "__main__":
    sys.exit(main())

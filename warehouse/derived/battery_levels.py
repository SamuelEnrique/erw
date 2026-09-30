#!/usr/bin/env python3
"""The home battery game's five famous days (session 38): ERCOT HB_HUBAVG real-time prices, every 15-minute interval of
five operating days, written to site/data/battery_levels.json for /play/battery. Today's level is read by the site
from Supabase (iso_rtm_hub_prices); these five are frozen here because the history table is not in the live set.

Energy Research Warehouse (ERW). The days and the rule behind each:

    2021-02-15  Winter Storm Uri, the first day of rotating outages (named by the session 38 prompt)
    2023-08-10  a summer scarcity day (named by the prompt)
    calm spring the operating day of March to May 2026 with the narrowest range (highest minus lowest 15-minute price)
    solar-heavy the complete ERCOT operating day with the highest solar share of net generation among the days
                eia930_all_generation holds (2026-08-26 on), its prices from iso_rtm_hub_prices (the history ends
                2026-08-25)
    negative    the operating day with the lowest mean 15-minute price in ercot_all_hub_prices_history (2015 on)

A day is used only when every interval of it is present (96; 92 or 100 on a clock change). Nothing is filled.

    python warehouse/derived/battery_levels.py
"""

import datetime as dt
import json
import os
import sys

import pandas as pd

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.abspath(os.path.join(HERE, "..", ".."))
sys.path.insert(0, os.path.join(ROOT, "warehouse", "connectors"))
sys.path.insert(0, HERE)
import iso_prices as ip  # noqa: E402
import price_board as pb  # noqa: E402  (read_table: streamed, filtered while read)

OUT = os.path.join(ROOT, "site", "data", "battery_levels.json")
TZ = "America/Chicago"
NODE = "HB_HUBAVG"


def with_day(df):
    return df.assign(day=df["ts"].dt.tz_convert(TZ).dt.strftime("%Y-%m-%d"))


def need(day):
    a = pd.Timestamp(day).tz_localize(TZ)
    return int(((a + pd.DateOffset(days=1)).normalize() - a).total_seconds() // 900)


def complete(df):
    g = df.groupby("day")["value"].agg(["mean", "min", "max", "size"])
    g["need"] = [need(d) for d in g.index]
    return g[g["size"] == g["need"]]


def solar_day(log):
    g = pb.read_table("eia930_all_generation")
    g = g[(g["entity"] == "eia930:ERCO") & g["variable"].isin(["net_generation_solar_mw", "net_generation_mw"])]
    g = with_day(g)
    p = g.pivot_table(index="day", columns="variable", values="value", aggfunc=["sum", "count"])
    hours = p[("count", "net_generation_mw")]
    full = [d for d in p.index if hours[d] == need(d) // 4 and p[("count", "net_generation_solar_mw")][d] == hours[d]]
    p = p.loc[full]
    share = p[("sum", "net_generation_solar_mw")] / p[("sum", "net_generation_mw")]
    day = share.idxmax()
    log.append(f"solar-heavy: {day}, solar {share[day] * 100:.2f} percent of ERCO net generation (eia930_all_generation, "
               f"{len(full)} complete days {min(full)} to {max(full)})")
    return day, float(share[day])


def level(slug, title, why, df, table):
    rows = df.sort_values("ts")
    return {
        "slug": slug, "date": rows["day"].iloc[0], "title": title, "why": why,
        "table": table, "entity": "ercot:HB_HUBAVG", "variable": "spp_rtm", "market": "ercot_rtm",
        "source": sorted(set(rows["source"])), "source_url": sorted(set(rows["source_url"])),
        "retrieved_at": max(rows["retrieved_at"]),
        "ts_utc": list(rows["ts_utc"]), "price": [float(v) for v in rows["value"]],
    }


def main():
    log = []
    cols_extra = ["source", "source_url", "retrieved_at"]
    hist = pb.read_table(pb.HISTORY, market="ercot_rtm", node=NODE)
    # read_table keeps the standard columns; the provenance columns come from a second streamed read of the same rows
    import pyarrow as pa
    import pyarrow.compute as pc
    import pyarrow.csv as pcsv
    path = os.path.join(ip.OUT_DIR, pb.HISTORY + ".csv")
    skip = sum(1 for ln in open(path, encoding="utf-8") if ln.startswith("#"))
    reader = pcsv.open_csv(path, read_options=pcsv.ReadOptions(skip_rows=skip, block_size=1 << 24),
                           convert_options=pcsv.ConvertOptions(include_columns=["ts_utc", "market", "node"] + cols_extra,
                                                               column_types={c: pa.string() for c in ["ts_utc", "market", "node"] + cols_extra}))
    prov = pa.concat_tables([pa.Table.from_batches([b]).filter(pc.and_(pc.equal(b.column("node"), NODE),
                                                                       pc.equal(b.column("market"), "ercot_rtm")))
                             for b in reader]).to_pandas()[["ts_utc"] + cols_extra]
    hist = with_day(hist.merge(prov, on="ts_utc", how="left"))
    days = complete(hist)
    spring = days[(days.index >= "2026-03-01") & (days.index <= "2026-05-31")]
    calm = (spring["max"] - spring["min"]).idxmin()
    neg = days["mean"].idxmin()
    log.append(f"calm spring: {calm}, range {spring.loc[calm, 'max'] - spring.loc[calm, 'min']:.2f} USD/MWh, the narrowest "
               f"of {len(spring)} complete days 2026-03-01 to 2026-05-31")
    log.append(f"negative: {neg}, mean {days.loc[neg, 'mean']:.4f} USD/MWh, the lowest of {len(days)} complete days")
    sday, share = solar_day(log)
    rt = pb.read_table("iso_rtm_hub_prices", market="ercot_rtm", node=NODE)
    rprov = pd.read_csv(os.path.join(ip.OUT_DIR, "iso_rtm_hub_prices.csv"), comment="#", dtype=str,
                        usecols=["ts_utc", "market", "node"] + cols_extra)
    rprov = rprov[(rprov["node"] == NODE) & (rprov["market"] == "ercot_rtm")][["ts_utc"] + cols_extra]
    rt = with_day(rt.merge(rprov, on="ts_utc", how="left"))
    if sday not in complete(rt).index:
        raise RuntimeError(f"solar-heavy day {sday} is not complete in iso_rtm_hub_prices")

    def of(df, d):
        if d not in complete(df).index:
            raise RuntimeError(f"{d} is not a complete operating day")
        return df[df["day"] == d]

    levels = [
        level("uri", "Winter Storm Uri", "2021-02-15, the first day of ERCOT's rotating outages.", of(hist, "2021-02-15"), pb.HISTORY),
        level("heat", "A summer scarcity day", "2023-08-10, a hot August day with a 3,842.89 USD/MWh interval.", of(hist, "2023-08-10"), pb.HISTORY),
        level("calm", "A calm spring day", f"{calm}: the narrowest range of real-time prices of any day, March to May 2026.", of(hist, calm), pb.HISTORY),
        level("solar", "A solar-heavy day", f"{sday}: solar made {share * 100:.1f} percent of ERCOT's net generation, the most of the days the warehouse "
              f"holds EIA's fuel mix for (from 2026-08-26).", of(rt, sday), "iso_rtm_hub_prices"),
        level("negative", "A negative-price day", f"{neg}: the lowest average real-time price of any day since 2015.", of(hist, neg), pb.HISTORY),
    ]
    # the heat day's line states its highest interval: read it, never write it by hand
    top = max(levels[1]["price"])
    levels[1]["why"] = f"2023-08-10, a hot August day with a {top:,.2f} USD/MWh interval."
    out = {
        "note": "ERW, session 38: the home battery game's five famous days. ERCOT HB_HUBAVG real-time settlement point prices, "
                "USD/MWh, every 15-minute interval of the operating day (Central time). Written by warehouse/derived/battery_levels.py "
                f"on {dt.datetime.now(dt.timezone.utc).strftime('%Y-%m-%dT%H:%M:%SZ')} from ercot_all_hub_prices_history and "
                "iso_rtm_hub_prices; the day choices in 'why' and in the report.",
        "log": log,
        "levels": levels,
    }
    with open(OUT, "w", encoding="utf-8", newline="\n") as f:
        json.dump(out, f, indent=1)
        f.write("\n")
    for x in log:
        print(x)
    print(f"wrote {os.path.relpath(OUT, ROOT)}: {', '.join(lv['date'] + ' (' + str(len(lv['price'])) + ')' for lv in levels)}")


if __name__ == "__main__":
    main()

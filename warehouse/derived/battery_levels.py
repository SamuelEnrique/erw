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

Session 56: two California days, CAISO SP15 (TH_SP15_GEN-APND) real-time prices, the 15-minute means of CAISO's
5-minute prices (lmp_rtm_15m_mean) in iso_hub_prices_history (2025-09-01 on), operating days in Pacific time, complete
days only:

    caiso-solar-noon  the day with the lowest midday mean price: the mean of the intervals starting 10:00 to 14:45
                      Pacific (10:00 to 15:00)
    caiso-duck        the day with the largest rise from the mean of the intervals starting 12:00 to 14:45 Pacific
                      (12:00 to 15:00) to the mean of those starting 18:00 to 20:45 (18:00 to 21:00): the evening ramp

The game keys a level by its date (game_scores.level_date), so a California day must not share its date with an ERCOT
famous day: the script stops if it would, rather than pick another day. (Today's level is the latest complete ERCOT
day; levelFor reads the famous days first, so a California day within the last ten days would shadow an ERCOT day's
scores: the script stops on that too.)

    python warehouse/derived/battery_levels.py                  # the California days; the ERCOT days kept as they are
    python warehouse/derived/battery_levels.py --rebuild-ercot  # also choose the five ERCOT days again (session 38)

Session 56: the ERCOT days are kept by default because two of their rules read tables that grow every day (the
solar-heavy day's EIA fuel mix), so a rebuild could move a level, and its leaderboard, to another date.
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
# session 56: California
CA_TABLE, CA_MARKET, CA_NODE, CA_VARIABLE, CA_TZ = "iso_hub_prices_history", "caiso_rtm", "TH_SP15_GEN-APND", "lmp_rtm_15m_mean", "America/Los_Angeles"
MIDDAY, AFTERNOON, EVENING = (10, 15), (12, 15), (18, 21)  # local clock hours, [start, end)


def with_day(df, tz=TZ):
    local = df["ts"].dt.tz_convert(tz)
    return df.assign(day=local.dt.strftime("%Y-%m-%d"), hour=local.dt.hour)


def need(day, tz=TZ):
    a = pd.Timestamp(day).tz_localize(tz)
    return int(((a + pd.DateOffset(days=1)).normalize() - a).total_seconds() // 900)


def complete(df, tz=TZ):
    g = df.groupby("day")["value"].agg(["mean", "min", "max", "size"])
    g["need"] = [need(d, tz) for d in g.index]
    return g[g["size"] == g["need"]]


def provenance(table, market, node, cols_extra=("source", "source_url", "retrieved_at")):
    """ts_utc and the provenance columns of one market and node of a table, streamed (pb.read_table keeps the standard
    columns only)."""
    import pyarrow as pa
    import pyarrow.compute as pc
    import pyarrow.csv as pcsv
    cols_extra = list(cols_extra)
    path = os.path.join(ip.OUT_DIR, table + ".csv")
    skip = sum(1 for ln in open(path, encoding="utf-8") if ln.startswith("#"))
    reader = pcsv.open_csv(path, read_options=pcsv.ReadOptions(skip_rows=skip, block_size=1 << 24),
                           convert_options=pcsv.ConvertOptions(include_columns=["ts_utc", "market", "node"] + cols_extra,
                                                               column_types={c: pa.string() for c in ["ts_utc", "market", "node"] + cols_extra}))
    return pa.concat_tables([pa.Table.from_batches([b]).filter(pc.and_(pc.equal(b.column("node"), node), pc.equal(b.column("market"), market)))
                             for b in reader]).to_pandas()[["ts_utc"] + cols_extra]


CA_FROM = "2025-09-01"  # session 64: the rules' stated window; the history now starts 2024-09-01, and the levels stay put


def caiso_days(log):
    """The two California days by their rules, from CAISO SP15 real-time prices; each day's rule number."""
    df = pb.read_table(CA_TABLE, market=CA_MARKET, node=CA_NODE)
    df = df[df["variable"] == CA_VARIABLE]
    df = with_day(df.merge(provenance(CA_TABLE, CA_MARKET, CA_NODE), on="ts_utc", how="left"), CA_TZ)
    df = df[df["day"] >= CA_FROM]
    full = complete(df, CA_TZ).index
    df = df[df["day"].isin(full)]
    win = lambda a, b: df[(df["hour"] >= a) & (df["hour"] < b)].groupby("day")["value"].mean()  # noqa: E731
    mid, aft, eve = win(*MIDDAY), win(*AFTERNOON), win(*EVENING)
    rise = (eve - aft).dropna()
    noon_day, duck_day = mid.idxmin(), rise.idxmax()
    log.append(f"caiso-solar-noon: {noon_day}, midday (10:00 to 15:00 Pacific) mean {mid[noon_day]:.4f} USD/MWh, the lowest of "
               f"{len(full)} complete days {min(full)} to {max(full)} of CAISO SP15 real-time ({CA_TABLE})")
    log.append(f"caiso-duck: {duck_day}, 12:00 to 15:00 mean {aft[duck_day]:.4f}, 18:00 to 21:00 mean {eve[duck_day]:.4f}: a rise of "
               f"{rise[duck_day]:.4f} USD/MWh, the largest of the same {len(full)} days")
    return df, dict(noon=(noon_day, float(mid[noon_day])), duck=(duck_day, float(rise[duck_day]), float(aft[duck_day]), float(eve[duck_day])))


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


def level(slug, title, why, df, table, grid="ERCOT", tz=TZ, entity="ercot:HB_HUBAVG", variable="spp_rtm", market="ercot_rtm", rule=None):
    rows = df.sort_values("ts")
    return {
        "slug": slug, "date": rows["day"].iloc[0], "title": title, "why": why,
        "grid": grid, "tz": tz, **({"rule": rule} if rule else {}),  # session 56
        "table": table, "entity": entity, "variable": variable, "market": market,
        "source": sorted(set(rows["source"])), "source_url": sorted(set(rows["source_url"])),
        "retrieved_at": max(rows["retrieved_at"]),
        "ts_utc": list(rows["ts_utc"]), "price": [float(v) for v in rows["value"]],
    }


def ercot_levels(log):
    """The five ERCOT days (session 38), chosen again."""
    cols_extra = ["source", "source_url", "retrieved_at"]
    hist = pb.read_table(pb.HISTORY, market="ercot_rtm", node=NODE)
    # read_table keeps the standard columns; the provenance columns come from a second streamed read of the same rows
    hist = with_day(hist.merge(provenance(pb.HISTORY, "ercot_rtm", NODE), on="ts_utc", how="left"))
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
    return levels


def caiso_levels(log, taken):
    """Session 56: the two California days, as levels. taken: the ERCOT famous days' dates, which a California day may
    not share (the game keys a level by its date)."""
    df, d = caiso_days(log)
    noon_day, noon_mean = d["noon"]
    duck_day, rise, aft, eve = d["duck"]
    recent = (dt.datetime.now(dt.timezone.utc) - dt.timedelta(days=14)).strftime("%Y-%m-%d")
    for day in (noon_day, duck_day):
        if day in taken:
            raise RuntimeError(f"California day {day} is already an ERCOT famous day: the game keys levels by date")
        if day >= recent:
            raise RuntimeError(f"California day {day} is within the last 14 days, where ERCOT's recent days are levels too")
    if noon_day == duck_day:
        raise RuntimeError(f"both rules chose {noon_day}")
    ca = dict(grid="CAISO", tz=CA_TZ, entity=f"caiso:{CA_NODE}", variable=CA_VARIABLE, market=CA_MARKET)
    return [
        level("caiso-solar-noon", "CAISO SP15: the cheapest midday",
              f"{noon_day}: the lowest midday price of any day held from {CA_FROM} on, a mean of {noon_mean:,.2f} USD/MWh from 10:00 to 15:00 Pacific, when "
              f"California's solar floods the grid.", df[df["day"] == noon_day], CA_TABLE,
              rule="The day with the lowest mean real-time price from 10:00 to 15:00 Pacific, of the complete days of CAISO SP15 "
                   f"real-time prices the warehouse holds ({CA_TABLE}, from {CA_FROM}).", **ca),
        level("caiso-duck", "CAISO SP15: the steepest evening ramp",
              f"{duck_day}: the largest rise of any day held from {CA_FROM} on, from a {aft:,.2f} USD/MWh mean at 12:00 to 15:00 Pacific to {eve:,.2f} at 18:00 to "
              f"21:00, {rise:,.2f} USD/MWh, as the sun sets and demand stays high.", df[df["day"] == duck_day], CA_TABLE,
              rule="The day with the largest rise from the mean real-time price of 12:00 to 15:00 Pacific to that of 18:00 to 21:00, of the "
                   f"complete days of CAISO SP15 real-time prices the warehouse holds ({CA_TABLE}, from {CA_FROM}).", **ca),
    ]


def main(argv=None):
    rebuild = "--rebuild-ercot" in (sys.argv[1:] if argv is None else argv)
    log = []
    if rebuild:
        ercot = ercot_levels(log)
        note = "ERCOT days chosen again by this run"
    else:
        with open(OUT, encoding="utf-8") as f:
            old = json.load(f)
        ercot = [lv for lv in old["levels"] if lv.get("grid", "ERCOT") == "ERCOT"]
        log += [x for x in old.get("log", []) if not x.startswith("caiso")]
        note = "ERCOT days kept as written in session 38 (pass --rebuild-ercot to choose them again)"
    for lv in ercot:
        lv.setdefault("grid", "ERCOT")
        lv.setdefault("tz", TZ)
    levels = ercot + caiso_levels(log, {lv["date"] for lv in ercot})
    out = {
        "note": "ERW, session 38: the home battery game's famous days. ERCOT HB_HUBAVG real-time settlement point prices, "
                "USD/MWh, every 15-minute interval of the operating day (Central time); session 56: two CAISO SP15 days, the 15-minute "
                "means of its 5-minute real-time prices (Pacific time). Written by warehouse/derived/battery_levels.py "
                f"on {dt.datetime.now(dt.timezone.utc).strftime('%Y-%m-%dT%H:%M:%SZ')} from ercot_all_hub_prices_history, "
                f"iso_rtm_hub_prices and iso_hub_prices_history; {note}. The day choices in 'why', 'rule' and the log.",
        "log": log,
        "levels": levels,
    }
    with open(OUT, "w", encoding="utf-8", newline="\n") as f:
        json.dump(out, f, indent=1)
        f.write("\n")
    for x in log:
        print(x)
    print(f"wrote {os.path.relpath(OUT, ROOT)}: {', '.join(lv['grid'] + ' ' + lv['date'] + ' (' + str(len(lv['price'])) + ')' for lv in levels)}")


if __name__ == "__main__":
    main()

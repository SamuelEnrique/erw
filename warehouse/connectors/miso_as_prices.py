#!/usr/bin/env python3
"""MISO day-ahead ancillary service market clearing prices, hourly, the system, from 2024-09-01. Internal.

Energy Research Warehouse (ERW) connector, session 85 (docs/methods/capacity_and_ancillary.md). Writes one series
table, warehouse/output/miso_as_prices.csv:

    entity    miso:MISO Wide    the file's own row for the system
    variable  as_price_dam_reg   GENREGMCP   regulating reserve, generation
              as_price_dam_spin  GENSPINMCP  spinning reserve, generation
              as_price_dam_supp  GENSUPPMCP  supplemental reserve, generation
    unit      USD/MW-hour   (US dollars per MW of capacity held for one hour)
    freq      PT1H; ts_utc is the start of the hour, UTC. The file's hours are hour-ending 1 to 24 in Eastern
              Standard Time all year ("All Hours-Ending are Eastern Standard Time (EST)"), so every operating day
              has 24 hours and hour-ending 1 starts at 05:00 UTC
    market    miso_dam
    node      MISO Wide

    python warehouse/connectors/miso_as_prices.py                      # 2024-09-01 to today
    python warehouse/connectors/miso_as_prices.py --out-dir C:/scratch # a trial run: nothing in warehouse/output
    python warehouse/connectors/miso_as_prices.py --offline            # from the raw files only, no request

Source: MISO market reports, "ASM Day-Ahead Market ExPost MCPs" (asm_expost_damcp), one csv per operating day at
https://docs.misoenergy.org/marketreports/<YYYYMMDD>_asm_expost_damcp.csv. One request per day, a second apart; a
day already in the raw files is not requested again.

Kept: the three "MISO Wide" prices a generator or a battery is paid. Left out: the demand-side and stored-energy
types on the same rows (DEMREGMCP, DEMSPINMCP, DEMSUPPMCP, SERREGMCP), and the file's several thousand rows that
repeat a price for each resource with its reserve zone. A zone's price can differ from the system's when its own
reserve requirement binds, so for every file the connector counts the (zone, product, hour) cells in which any
resource row differs from the MISO Wide row; the count is in the log and the header, and the zones' own prices are
not held. Short-term reserve and the ramp products are not in this report.

Never fill. A (product, day) is written only when all 24 hours hold a number.

Ceiling: 500,000 rows (session 85). Past it nothing is written.

License: internal. MISO's terms (https://www.misoenergy.org/meet-miso/legal-and-privacy/, read 2026-10-04): "You are
not permitted to modify, publish, transmit, participate in the transfer or sale of, reproduce, create derivative
works of, distribute, publicly perform, publicly display or in any way exploit any of the materials or content on
this Website or the App in whole or in part" (the reading of session 65 for MISO's capacity prices). The same page
also says: "You agree not use any automated means, including, without limitation, agents, robots, scripts, or
spiders, to access, monitor, or copy any part of this Website or the App." The ERW has read MISO's market report
files by script every day since session 5 (iso_prices.py); session 85 quotes the sentence so that a person can
rule on it, and keeps this pull to one small file a day.
"""

import io
import os
import sys

import pandas as pd

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import iso_as_common as common  # noqa: E402
import iso_prices as ip  # noqa: E402

NAME = "miso_as_prices"
TZ = "Etc/GMT+5"  # Eastern Standard Time all year, as the file says
SOURCE = "miso:asm_expost_damcp"
REPORT = "ASM Day-Ahead Market ExPost MCPs (daily csv)"
PAGE = "https://www.misoenergy.org/markets-and-operations/real-time--market-data/market-reports/"
URL = "https://docs.misoenergy.org/marketreports/{}_asm_expost_damcp.csv"
WIDE = "MISO Wide"
TYPES = {"GENREGMCP": "as_price_dam_reg", "GENSPINMCP": "as_price_dam_spin", "GENSUPPMCP": "as_price_dam_supp"}
OTHER = {"DEMREGMCP", "DEMSPINMCP", "DEMSUPPMCP", "SERREGMCP"}
HOURS = [f"HE {k}" for k in range(1, 25)]
WANTED = {WIDE: list(TYPES.values())}
differing = {"cells": 0, "files": 0}


def documents(start, until, log, offline):
    return [dict(url=URL.format(d.strftime("%Y%m%d")), label=str(d.date()), day=str(d.date()), settled=True)
            for d in pd.date_range(start, until - pd.Timedelta(days=1), freq="D")]


def parse(raw, doc, log):
    day = doc["day"]
    lines = raw.decode("utf-8").splitlines()
    if len(lines) < 6 or not lines[0].startswith("Dayahead Market MCPs"):
        raise RuntimeError(f"{day}: the file does not begin 'Dayahead Market MCPs': {lines[:1]}")
    stamp = lines[2].split(",")
    if pd.to_datetime(stamp[0], format="%m/%d/%Y").strftime("%Y-%m-%d") != day:
        raise RuntimeError(f"{day}: the file is for {stamp[0]}")
    if "Eastern Standard Time (EST)" not in lines[2]:
        raise RuntimeError(f"{day}: the hours are no longer stated as Eastern Standard Time: {lines[2]}")
    x = pd.read_csv(io.StringIO("\n".join(lines[4:])), dtype=str, keep_default_na=False)
    x.columns = [c.strip() for c in x.columns]
    if list(x.columns) != ["Unnamed: 0", "Unnamed: 1", "MCP Type"] + HOURS:
        raise RuntimeError(f"{day}: columns {list(x.columns)[:6]}: layout changed")
    x = x.rename(columns={"Unnamed: 0": "name", "Unnamed: 1": "zone"})
    wide = x[x["name"] == WIDE]
    if set(wide["MCP Type"]) != set(TYPES) | OTHER or len(wide) != len(TYPES) + len(OTHER):
        raise RuntimeError(f"{day}: the MISO Wide rows are {sorted(wide['MCP Type'])}")
    wide = wide.set_index("MCP Type")
    start = pd.Timestamp(day).tz_localize(TZ).tz_convert("UTC")
    out = []
    for t, var in TYPES.items():
        v = wide.loc[t, HOURS].str.strip()
        ok = (v != "").values  # an empty cell is not a price: no row
        out.append(pd.DataFrame({"region": WIDE, "variable": var,
                                 "ts": [start + pd.Timedelta(hours=k) for k in range(24) if ok[k]],
                                 "value": pd.to_numeric(v[ok].values, errors="raise"), "day": day}))
        res = x[(x["name"] != WIDE) & (x["MCP Type"] == t)]
        ref = pd.to_numeric(v, errors="coerce").values
        for zone, g in res.groupby("zone"):
            vals = g[HOURS].apply(pd.to_numeric, errors="coerce").values
            n = int((abs(vals - ref) > 1e-9).any(axis=0).sum())
            if n:
                differing["cells"] += n
                log(f"  {day} {var}: {zone} differs from MISO Wide in {n} hours (the zone's price is not held)")
    differing["files"] += 1
    return pd.concat(out, ignore_index=True)


def header(regions, days, gaps):
    return [
        "Energy Research Warehouse (ERW): MISO day-ahead ancillary service market clearing prices, hourly, the "
        "system",
        "Shape: series (docs/datastandard.md v0). Unit USD/MW-hour: US dollars per MW of capacity held for one "
        "hour. ts_utc is the start of the hour, UTC; the file's hours are Eastern Standard Time all year.",
        "Region: MISO Wide, the file's own system rows. Variables: as_price_dam_reg GENREGMCP (regulating "
        "reserve), as_price_dam_spin GENSPINMCP (spinning reserve), as_price_dam_supp GENSUPPMCP (supplemental "
        "reserve). The demand-side and stored-energy types and the per-resource rows are not kept.",
        f"The zones: in the {differing['files']} daily files read by this run, a reserve zone's resources carried "
        f"a price other than MISO Wide's in {differing['cells']} zone-product-hours (each is in the run log); the "
        "zones' own prices are not held.",
    ]


SPEC = dict(
    name=NAME, connector=NAME, label="MISO", namespace="miso", tz=TZ, first=common.START,
    geo="US-AR,US-IL,US-IN,US-IA,US-KY,US-LA,US-MI,US-MN,US-MS,US-MO,US-MT,US-ND,US-SD,US-TX,US-WI",
    market="miso_dam", source=SOURCE, report=REPORT, page=PAGE, document_list=PAGE,
    publisher=ip.ISO_PUBLISHERS["miso"], license="internal", documents=documents, parse=parse, wanted=WANTED,
    header=header, pause=1,
    license_line="License: internal. MISO's terms (https://www.misoenergy.org/meet-miso/legal-and-privacy/): \"You "
                 "are not permitted to modify, publish, transmit, participate in the transfer or sale of, "
                 "reproduce, create derivative works of, distribute, publicly perform, publicly display or in any "
                 "way exploit any of the materials or content\".",
)


if __name__ == "__main__":
    sys.exit(common.run(SPEC))

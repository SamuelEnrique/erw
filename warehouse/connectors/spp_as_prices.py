#!/usr/bin/env python3
"""SPP day-ahead operating reserve market clearing prices, hourly, the system rows, from 2024-09-01.

Energy Research Warehouse (ERW) connector, session 85 (docs/methods/capacity_and_ancillary.md). Writes one series
table, warehouse/output/spp_as_prices.csv:

    entity    spp:<reserve zone as the file names it>   spp:SPP (in every file), spp:SWPW (in the files from
                                                        2026-04-01)
    variable  as_price_dam_regup   RegUP    regulation up
              as_price_dam_regdn   RegDN    regulation down
              as_price_dam_spin    Spin     spinning reserve
              as_price_dam_supp    Supp     supplemental reserve
              as_price_dam_rampup  RampUP   ramp capability up
              as_price_dam_rampdn  RampDN   ramp capability down
              as_price_dam_uncup   UncUP    uncertainty reserve up
    unit      USD/MW-hour   (US dollars per MW of capacity held for one hour)
    freq      PT1H; ts_utc is the start of the hour, UTC: the file's GMTIntervalEnd less one hour
    market    spp_dam
    node      the reserve zone

    python warehouse/connectors/spp_as_prices.py                      # 2024-09-01 to today (Central)
    python warehouse/connectors/spp_as_prices.py --out-dir C:/scratch # a trial run: nothing in warehouse/output
    python warehouse/connectors/spp_as_prices.py --offline            # from the raw files only, no request

Source: SPP's public portal, "Day-Ahead Market Clearing Prices (MCP)" (https://portal.spp.org/pages/da-mcp), one csv
per operating day, DA-MCP-<YYYYMMDD>0100.csv, through the portal's file browser. A year SPP has archived is one zip
(/2024/2024.zip, one request); a later year is one request per day, a second apart. A day already in the raw files
is not requested again.

Kept: the rows named SPP and SWPW, with all seven products. The file also prices numbered reserve zones (1 to 5,
and 21 from April 2026); in the days read in session 85 each carried the price of one of the two named rows. All
zones and products would be about a million rows, past the ceiling, so the numbered zones are not held, and not
silently: for every file the connector counts the (zone, product, hour) cells in which a numbered zone's price is
neither the SPP row's nor the SWPW row's; the count is in the log and the header. What SWPW stands for is not
stated in the file and is not guessed here; it appears with zone 21 on 2026-04-01.

Never fill. A (zone, product, operating day) is written only when every hour of the day is there (24, or 23 and 25
at the clock changes).

Ceiling: 500,000 rows (session 85). Past it nothing is written.

License: public, with citation, and a limit a person should know. SPP's terms and conditions
(https://www.spp.org/terms-conditions/, read 2026-10-04): "All materials posted or otherwise available on this
website are the exclusive copyrighted material of the author(s) or SPP. Permission is implicitly granted to copy
and distribute (via computer network or printed form) in whole or in part (with appropriate citation) EXCEPT when
such materials will be used, in whole or in part, within a commercial publication (printed or otherwise) or when
the author(s) or SPP will be quoted in commercial materials, forums or publications. Any commercial use of these
materials requires prior, express written authorization from the author(s) or a duly authorized officer of SPP."
Republishing with citation is allowed; a commercial publication is not without SPP's written authorization. The
ERW is a research warehouse and cites SPP in every row, so the table is public; if the platform sells anything
built on these rows, that sentence applies and the table must be ruled on again.
"""

import io
import json
import os
import sys
import zipfile

import pandas as pd

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import iso_as_common as common  # noqa: E402
import iso_prices as ip  # noqa: E402

NAME = "spp_as_prices"
TZ = "America/Chicago"
SOURCE = "spp:DA-MCP"
REPORT = "Day-Ahead Market Clearing Prices (MCP) for operating reserve"
PAGE = "https://portal.spp.org/pages/da-mcp"
LIST = "https://portal.spp.org/file-browser-api/?fsName=da-mcp&path=/{}&type=folder"
FILE = "https://portal.spp.org/file-browser-api/download/da-mcp?path=/{}"
PRODUCTS = {"RegUP": "as_price_dam_regup", "RegDN": "as_price_dam_regdn", "Spin": "as_price_dam_spin",
            "Supp": "as_price_dam_supp", "RampUP": "as_price_dam_rampup", "RampDN": "as_price_dam_rampdn",
            "UncUP": "as_price_dam_uncup"}
COLS = ["Interval", "GMTIntervalEnd", "Reserve Zone"] + list(PRODUCTS)
KEPT = ["SPP", "SWPW"]
WANTED = {z: list(PRODUCTS.values()) for z in KEPT}
differing = {"cells": 0, "files": 0}


def archived(year, log, offline):
    """Whether SPP holds the year as one zip (its folder lists <year>.zip)."""
    if offline:
        return ip.raw_cached(NAME, FILE.format(f"{year}/{year}.zip")) is not None
    raw, _ = ip.fetch_raw(NAME, LIST.format(year), log, fresh=True)
    return any(x["name"] == f"{year}.zip" for x in json.loads(raw.decode("utf-8")))


def documents(start, until, log, offline):
    last = until - pd.Timedelta(days=1)
    docs = []
    for year in range(start.year, last.year + 1):
        days = pd.date_range(max(start, pd.Timestamp(year, 1, 1)), min(last, pd.Timestamp(year, 12, 31)), freq="D")
        if archived(year, log, offline):
            docs.append(dict(url=FILE.format(f"{year}/{year}.zip"), label=f"{year} (archive)", year=year,
                             days=[str(d.date()) for d in days], settled=True))
        else:
            docs += [dict(url=FILE.format(d.strftime("%Y/%m/DA-MCP-%Y%m%d0100.csv")), label=str(d.date()),
                          days=[str(d.date())], settled=True) for d in days]
    return docs


def parse_day(text, day, log):
    x = pd.read_csv(io.StringIO(text), dtype=str, keep_default_na=False)
    x.columns = [c.strip() for c in x.columns]
    if list(x.columns) != COLS:
        raise RuntimeError(f"{day}: columns {list(x.columns)}: layout changed")
    x["Reserve Zone"] = x["Reserve Zone"].str.strip()
    if "SPP" not in set(x["Reserve Zone"]):
        raise RuntimeError(f"{day}: no row named SPP; zones {sorted(set(x['Reserve Zone']))}")
    x["ts"] = pd.to_datetime(x["GMTIntervalEnd"], format="%m/%d/%Y %H:%M:%S").dt.tz_localize("UTC") - pd.Timedelta(hours=1)
    hours = set(common.day_hours(day, TZ))
    if set(x["ts"]) - hours:
        raise RuntimeError(f"{day}: the file holds hours outside the operating day")
    out = []
    for col, var in PRODUCTS.items():
        w = x.pivot(index="ts", columns="Reserve Zone", values=col)
        for z in KEPT:
            if z not in w.columns:
                continue
            s = w[z].dropna()
            s = s[s.str.strip() != ""]  # an empty cell is not a price: no row
            out.append(pd.DataFrame({"region": z, "variable": var, "ts": s.index,
                                     "value": pd.to_numeric(s.values, errors="raise")}))
        named = [w[z] for z in KEPT if z in w.columns]
        for z in [c for c in w.columns if c not in KEPT]:
            n = int((~pd.concat([w[z] == k for k in named], axis=1).any(axis=1)).sum())
            if n:
                differing["cells"] += n
                log(f"  {day} {var}: zone {z} carries a price of neither named row in {n} hours (not held)")
    differing["files"] += 1
    return pd.concat(out, ignore_index=True).assign(day=day)


def parse(raw, doc, log):
    if "year" not in doc:
        return parse_day(raw.decode("utf-8"), doc["days"][0], log)
    z = zipfile.ZipFile(io.BytesIO(raw))
    names = {n.rsplit("/", 1)[-1]: n for n in z.namelist() if n.endswith(".csv")}
    frames = []
    for day in doc["days"]:
        n = f"DA-MCP-{day.replace('-', '')}0100.csv"
        if n not in names:
            log(f"  gap: {n} is not in the archive of {doc['year']}")
            continue
        frames.append(parse_day(z.read(names[n]).decode("utf-8"), day, log))
    return pd.concat(frames, ignore_index=True) if frames else pd.DataFrame(columns=["region", "variable", "ts", "value", "day"])


def header(regions, days, gaps):
    return [
        "Energy Research Warehouse (ERW): SPP day-ahead operating reserve market clearing prices, hourly, the "
        "system rows",
        "Shape: series (docs/datastandard.md v0). Unit USD/MW-hour: US dollars per MW of capacity held for one "
        "hour. ts_utc is the start of the hour, UTC (the file's GMTIntervalEnd less one hour).",
        f"Regions: {', '.join(regions)}, as the file names them (SWPW is in the files from 2026-04-01; the file "
        "does not say what it stands for). Variables: as_price_dam_regup RegUP, as_price_dam_regdn RegDN, "
        "as_price_dam_spin Spin, as_price_dam_supp Supp, as_price_dam_rampup RampUP, as_price_dam_rampdn RampDN, "
        "as_price_dam_uncup UncUP.",
        f"The numbered reserve zones are not held: in the {differing['files']} daily files read by this run, a "
        f"numbered zone carried a price of neither named row in {differing['cells']} zone-product-hours (each is "
        "in the run log).",
    ]


SPEC = dict(
    name=NAME, connector=NAME, label="SPP", namespace="spp", tz=TZ, first=common.START,
    geo="US-AR,US-IA,US-KS,US-LA,US-MN,US-MO,US-MT,US-NE,US-NM,US-ND,US-OK,US-SD,US-TX,US-WY",
    market="spp_dam", source=SOURCE, report=REPORT, page=PAGE, document_list=PAGE,
    publisher=ip.ISO_PUBLISHERS["spp"], license="public", documents=documents, parse=parse, wanted=WANTED,
    header=header, pause=1,
    license_line="License: public, with citation. SPP's terms (https://www.spp.org/terms-conditions/): "
                 "\"Permission is implicitly granted to copy and distribute (via computer network or printed "
                 "form) in whole or in part (with appropriate citation) EXCEPT when such materials will be used, "
                 "in whole or in part, within a commercial publication\". A commercial use needs SPP's written "
                 "authorization.",
)


if __name__ == "__main__":
    sys.exit(common.run(SPEC))

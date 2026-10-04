#!/usr/bin/env python3
"""SPP day-ahead operating reserve quantities cleared, hourly, the system rows, from 2024-09-01.

Energy Research Warehouse (ERW) connector, session 100 (docs/methods/reserve_quantities_nyiso_spp.md). An approved
pull (Samuel, 4 October 2026): the reserve quantities SPP procures, day-ahead, from 2024-09-01, ceiling 300,000 rows,
USD 0. Writes one series table, warehouse/output/spp_as_quantities.csv:

    entity    spp:SPP, spp:SWPW   the file's BAA column, as it names them (SWPW is in the files from 2026-04-01; the file
                                  does not say what it stands for), the same two rows spp_as_prices holds
    variable  quantity_mw_dam_regup, _regdn, _spin, _supp, _rampup, _rampdn, _uncup
                                  the MW of each operating reserve product cleared in the Day-Ahead Market that hour
    unit      MW
    freq      PT1H; ts_utc is the start of the hour, UTC (the file's GMTIntervalEnd less one hour)
    market    spp_dam

    python warehouse/connectors/spp_as_quantities.py                      # 2024-09-01 to yesterday (Central)
    python warehouse/connectors/spp_as_quantities.py --out-dir C:/scratch # a trial run: nothing in warehouse/output
    python warehouse/connectors/spp_as_quantities.py --offline            # from the raw files only, no request

Source: SPP's public portal, "Day-Ahead Market Clearing" (https://portal.spp.org/pages/market-clearing), one csv per
operating day (DA-MC-<YYYYMMDD>0100.csv): by hour and BAA, the generation, demand and virtuals cleared, the system
marginal price, and the MW cleared of each operating reserve product (columns RegUP, RegDN, RampUP, RampDN, UncUP,
Spin, Supp). Only the seven reserve columns are kept. One request per day; a finished year is one archive. The files
before SPP added the BAA column (it is in the files from 2026-04-01) hold one row an hour, the system's, written as
spp:SPP.

Never fill. A (BAA, product, operating day) is written only when every hour of the day is there (24, or 23 and 25 at
the clock changes); an empty cell is not a quantity and gives no row. A quantity of zero is a quantity.

Ceiling: 300,000 rows (the pull's). Past it nothing is written.

License: public, with citation. SPP's terms (https://www.spp.org/terms-conditions/, as session 85 read and recorded
them on 2026-10-04): "Permission is implicitly granted to copy and distribute (via computer network or printed form) in
whole or in part (with appropriate citation) EXCEPT when such materials will be used, in whole or in part, within a
commercial publication". A commercial use needs SPP's written authorization.
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

NAME = "spp_as_quantities"
TZ = "America/Chicago"
SOURCE = "spp:DA-MC"
REPORT = "Day-Ahead Market Clearing (operating reserve cleared, by hour)"
PAGE = "https://portal.spp.org/pages/market-clearing"
LIST = "https://portal.spp.org/file-browser-api/?fsName=market-clearing&path=/{}&type=folder"
FILE = "https://portal.spp.org/file-browser-api/download/market-clearing?path=/{}"
PRODUCTS = {"RegUP": "quantity_mw_dam_regup", "RegDN": "quantity_mw_dam_regdn", "Spin": "quantity_mw_dam_spin", "Supp": "quantity_mw_dam_supp",
            "RampUP": "quantity_mw_dam_rampup", "RampDN": "quantity_mw_dam_rampdn", "UncUP": "quantity_mw_dam_uncup"}
KEPT = ["SPP", "SWPW"]
WANTED = {z: list(PRODUCTS.values()) for z in KEPT}
CEILING = 300_000


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
            docs.append(dict(url=FILE.format(f"{year}/{year}.zip"), label=f"{year} (archive)", year=year, days=[str(d.date()) for d in days], settled=True))
        else:
            docs += [dict(url=FILE.format(d.strftime("%Y/%m/DA-MC-%Y%m%d0100.csv")), label=str(d.date()), days=[str(d.date())], settled=True) for d in days]
    return docs


def parse_day(text, day, log):
    x = pd.read_csv(io.StringIO(text), dtype=str, keep_default_na=False)
    x.columns = [c.strip() for c in x.columns]
    missing = [c for c in ["GMTIntervalEnd"] + list(PRODUCTS) if c not in x.columns]
    if missing:
        raise RuntimeError(f"{day}: the file has no column {missing}: layout changed")
    if "BAA" not in x.columns:
        # the files before SPP added the column hold one row an hour: the system's
        if x["GMTIntervalEnd"].duplicated().any():
            raise RuntimeError(f"{day}: no BAA column and more than one row an hour: layout changed")
        x["BAA"] = "SPP"
    x["BAA"] = x["BAA"].str.strip()
    if "SPP" not in set(x["BAA"]):
        raise RuntimeError(f"{day}: no row named SPP; BAAs {sorted(set(x['BAA']))}")
    other = sorted(set(x["BAA"]) - set(KEPT))
    if other:
        log(f"  {day}: BAAs not kept: {other}")
    x["ts"] = pd.to_datetime(x["GMTIntervalEnd"], format="%m/%d/%Y %H:%M:%S").dt.tz_localize("UTC") - pd.Timedelta(hours=1)
    if set(x["ts"]) - set(common.day_hours(day, TZ)):
        raise RuntimeError(f"{day}: the file holds hours outside the operating day")
    out = []
    for col, var in PRODUCTS.items():
        for z in KEPT:
            s = x[x["BAA"] == z].set_index("ts")[col]
            s = s[s.str.strip() != ""]  # an empty cell is not a quantity: no row
            if len(s):
                out.append(pd.DataFrame({"region": z, "variable": var, "ts": s.index, "value": pd.to_numeric(s.values, errors="raise")}))
    return pd.concat(out, ignore_index=True).assign(day=day)


def parse(raw, doc, log):
    if "year" not in doc:
        return parse_day(raw.decode("utf-8"), doc["days"][0], log)
    z = zipfile.ZipFile(io.BytesIO(raw))
    names = {n.rsplit("/", 1)[-1]: n for n in z.namelist() if n.endswith(".csv")}
    frames = []
    for day in doc["days"]:
        n = f"DA-MC-{day.replace('-', '')}0100.csv"
        if n not in names:
            log(f"  gap: {n} is not in the archive of {doc['year']}")
            continue
        frames.append(parse_day(z.read(names[n]).decode("utf-8"), day, log))
    return pd.concat(frames, ignore_index=True) if frames else pd.DataFrame(columns=["region", "variable", "ts", "value", "day"])


def header(regions, days, gaps):
    return [
        "Energy Research Warehouse (ERW): SPP day-ahead operating reserve quantities cleared, hourly, the system rows (session 100)",
        "Shape: series (docs/datastandard.md v0). Unit MW: the MW of the product cleared in the Day-Ahead Market for the hour. ts_utc is the start of the hour, "
        "UTC (the file's GMTIntervalEnd less one hour).",
        f"Regions: {', '.join(regions)}, the file's BAA column (SWPW is in the files from 2026-04-01; the file does not say what it stands for). Variables: "
        "quantity_mw_dam_regup RegUP, _regdn RegDN, _spin Spin, _supp Supp, _rampup RampUP, _rampdn RampDN, _uncup UncUP.",
        f"An approved pull (session 100): from 2024-09-01, ceiling {CEILING:,} rows. The file's other columns (generation, demand, virtuals, prices) are not kept.",
    ]


SPEC = dict(
    name=NAME, connector=NAME, label="SPP", namespace="spp", tz=TZ, first=common.START,
    geo="US-AR,US-IA,US-KS,US-LA,US-MN,US-MO,US-MT,US-NE,US-NM,US-ND,US-OK,US-SD,US-TX,US-WY",
    market="spp_dam", source=SOURCE, report=REPORT, page=PAGE, document_list=PAGE,
    publisher=ip.ISO_PUBLISHERS["spp"], license="public", documents=documents, parse=parse, wanted=WANTED,
    header=header, pause=1, unit="MW", ceiling=CEILING,
    license_line="License: public, with citation. SPP's terms (https://www.spp.org/terms-conditions/): "
                 "\"Permission is implicitly granted to copy and distribute (via computer network or printed "
                 "form) in whole or in part (with appropriate citation) EXCEPT when such materials will be used, "
                 "in whole or in part, within a commercial publication\". A commercial use needs SPP's written "
                 "authorization.",
)


if __name__ == "__main__":
    sys.exit(common.run(SPEC))

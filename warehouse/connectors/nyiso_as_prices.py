#!/usr/bin/env python3
"""NYISO day-ahead ancillary service prices, hourly, by reserve region, from 2024-09-01.

Energy Research Warehouse (ERW) connector, session 85 (docs/methods/capacity_and_ancillary.md). Writes one series
table, warehouse/output/nyiso_as_prices.csv:

    entity    nyiso:<load zone as NYISO names it>   nyiso:WEST, nyiso:CAPITL, nyiso:HUD VL, nyiso:N.Y.C.,
                                                    nyiso:LONGIL; and nyiso:NYCA for regulation, which NYISO
                                                    prices once for the New York Control Area
    variable  as_price_dam_spin10   10 Min Spinning Reserve
              as_price_dam_nsync10  10 Min Non-Synchronous Reserve
              as_price_dam_op30     30 Min Operating Reserve
              as_price_dam_reg      NYCA Regulation Capacity (entity nyiso:NYCA only)
    unit      USD/MW-hour   (US dollars per MW of capacity held for one hour; the file's "$/MWHr")
    freq      PT1H; ts_utc is the start of the hour, UTC (the file's Time Stamp with its Time Zone, EDT or EST)
    market    nyiso_dam
    node      the load zone, or NYCA

    python warehouse/connectors/nyiso_as_prices.py                      # 2024-09-01 to today (Eastern)
    python warehouse/connectors/nyiso_as_prices.py --out-dir C:/scratch # a trial run: nothing in warehouse/output
    python warehouse/connectors/nyiso_as_prices.py --offline            # from the raw files only, no request

Source: NYISO's public market data, "Day-Ahead Market Ancillary Services Prices" (report P-5, damasp), the monthly
archive http://mis.nyiso.com/public/csv/damasp/<YYYYMM>01damasp_csv.zip, one file per operating day inside. One
request per month. The archive of the month in progress grows each day, so it is fetched again on every run; a
finished month is read from the raw files.

Kept: five of the eleven load zones, one for each set of zones that can price reserves apart, and regulation once.
The file gives every price per load zone, but zones of one reserve region carry the same price. Read in the months
checked (September 2024, November 2025, October 2026): WEST, GENESE, CENTRL, NORTH and MHK VL are always equal;
HUD VL, MILLWD, DUNWOD and LONGIL are always equal; CAPITL and N.Y.C. stand alone. LONGIL is kept beside HUD VL
all the same, and rightly: over the whole window (2024-09-01 to 2026-10-03) its spinning reserve price differed from
HUD VL's in 3 hours, so it is a zone of its own. The six zones not kept are not lost silently: for
every file the connector compares each with the kept zone of its group and counts the hours in which a price
differs; the count is in the log and the header. Regulation must be one price across all eleven zones in every
hour, or the run fails. Eleven zones and four prices would be 806,000 rows, past the ceiling.

Never fill. A (zone, product, operating day) is written only when every hour of the day is there (24, or 23 and 25
at the clock changes); an empty cell is not a price and gives no row.

Ceiling: 500,000 rows (session 85). Past it nothing is written.

License: public, with a caution (the ruling of session 65 for NYISO's capacity prices, docs/methods/
capacity_and_ancillary.md). NYISO's legal notice (https://www.nyiso.com/legal-notice, read 2026-10-04) does not
forbid republishing its market data, and grants no license either: "Access to this Web site does not confer any
license or ownership interest in either the form or content of the Web site, including any confidential or
proprietary information or intellectual property of any kind or nature, and the NYISO hereby expressly reserves
such rights and property in its entirety. Downloading, republishing, retransmitting, reproducing, or other use of
any image or video on this website as a stand-alone file is strictly prohibited". The prohibition names images and
video, not data. Public by the ERW's standing rule (every ISO but PJM); a person can rule otherwise.
"""

import io
import os
import sys
import zipfile

import pandas as pd

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import iso_as_common as common  # noqa: E402
import iso_prices as ip  # noqa: E402

NAME = "nyiso_as_prices"
TZ = "America/New_York"
SOURCE = "nyiso:damasp"
REPORT = "Day-Ahead Market Ancillary Services Prices (P-5)"
PAGE = "http://mis.nyiso.com/public/P-5list.htm"
URL = "http://mis.nyiso.com/public/csv/damasp/{}01damasp_csv.zip"
PRODUCTS = {"10 Min Spinning Reserve ($/MWHr)": "as_price_dam_spin10",
            "10 Min Non-Synchronous Reserve ($/MWHr)": "as_price_dam_nsync10",
            "30 Min Operating Reserve ($/MWHr)": "as_price_dam_op30"}
REG = "NYCA Regulation Capacity ($/MWHr)"
REG_VAR, NYCA = "as_price_dam_reg", "NYCA"
# the zone kept for each set of zones, and the zones compared with it
GROUPS = {"WEST": ["GENESE", "CENTRL", "NORTH", "MHK VL"], "CAPITL": [], "HUD VL": ["MILLWD", "DUNWOD"],
          "N.Y.C.": [], "LONGIL": []}
ZONES = sorted(list(GROUPS) + [z for v in GROUPS.values() for z in v])
OFFSET = {"EDT": 4, "EST": 5}
COLS = ["Time Stamp", "Time Zone", "Name", "PTID"] + list(PRODUCTS) + [REG]
WANTED = {**{z: list(PRODUCTS.values()) for z in GROUPS}, NYCA: [REG_VAR]}
differing = {"hours": 0, "files": 0}


def documents(start, until, log, offline):
    today = pd.Timestamp.now(tz=TZ).tz_localize(None).normalize()
    docs = []
    for m in pd.period_range(start, until - pd.Timedelta(days=1), freq="M"):
        docs.append(dict(url=URL.format(m.strftime("%Y%m")), label=str(m),
                         settled=m.end_time.normalize() + pd.Timedelta(days=2) < today))
    return docs


def parse_day(text, day, log):
    """One operating day's file: rows (region, variable, ts, value, day)."""
    x = pd.read_csv(io.StringIO(text), dtype=str, keep_default_na=False)
    if list(x.columns) != COLS:
        raise RuntimeError(f"{day}: columns {list(x.columns)}: layout changed")
    if sorted(x["Name"].unique()) != ZONES:
        raise RuntimeError(f"{day}: zones {sorted(x['Name'].unique())}, expected {ZONES}")
    if set(x["Time Zone"]) - set(OFFSET):
        raise RuntimeError(f"{day}: time zones {set(x['Time Zone'])}")
    local = pd.to_datetime(x["Time Stamp"], format="%m/%d/%Y %H:%M")
    if set(local.dt.strftime("%Y-%m-%d")) != {day}:
        raise RuntimeError(f"{day}: the file holds days {sorted(set(local.dt.strftime('%Y-%m-%d')))}")
    x["ts"] = (local + pd.to_timedelta(x["Time Zone"].map(OFFSET), unit="h")).dt.tz_localize("UTC")
    if x.duplicated(["Name", "ts"]).any():
        raise RuntimeError(f"{day}: a (zone, hour) repeats")
    out = []
    for col, var in PRODUCTS.items():
        w = x.pivot(index="ts", columns="Name", values=col)
        for kept, others in GROUPS.items():
            for o in others:
                n = int((w[o] != w[kept]).sum())
                if n:
                    differing["hours"] += n
                    log(f"  {day} {var}: {o} differs from {kept} in {n} hours (the zone is not kept)")
            s = w[kept][w[kept].str.strip() != ""]  # an empty cell is not a price: no row
            out.append(pd.DataFrame({"region": kept, "variable": var, "ts": s.index,
                                     "value": pd.to_numeric(s.values, errors="raise")}))
    w = x.pivot(index="ts", columns="Name", values=REG)
    if (w.nunique(axis=1) != 1).any():
        raise RuntimeError(f"{day}: the regulation price is not one price across the zones")
    s = w[ZONES[0]][w[ZONES[0]].str.strip() != ""]
    out.append(pd.DataFrame({"region": NYCA, "variable": REG_VAR, "ts": s.index,
                             "value": pd.to_numeric(s.values, errors="raise")}))
    differing["files"] += 1
    return pd.concat(out, ignore_index=True).assign(day=day)


def parse(raw, doc, log):
    z = zipfile.ZipFile(io.BytesIO(raw))
    frames = []
    for n in sorted(z.namelist()):
        if not (len(n) == 18 and n.endswith("damasp.csv") and n[:8].isdigit()):
            raise RuntimeError(f"{doc['label']}: unexpected file {n} in the archive")
        day = f"{n[:4]}-{n[4:6]}-{n[6:8]}"
        frames.append(parse_day(z.read(n).decode("utf-8"), day, log))
    return pd.concat(frames, ignore_index=True)


def header(regions, days, gaps):
    return [
        "Energy Research Warehouse (ERW): NYISO day-ahead ancillary service prices, hourly, by reserve region",
        "Shape: series (docs/datastandard.md v0). Unit USD/MW-hour: US dollars per MW of capacity held for one "
        "hour. ts_utc is the start of the hour, UTC.",
        f"Regions: {', '.join(regions)}. Five of NYISO's eleven load zones, one for each set of zones that can "
        "price reserves apart (WEST also stands for GENESE, CENTRL, NORTH and MHK VL; HUD VL for MILLWD and "
        "DUNWOD), and NYCA for regulation, one price for the control area. Variables: as_price_dam_spin10 10 "
        "Min Spinning Reserve, as_price_dam_nsync10 10 Min Non-Synchronous Reserve, as_price_dam_op30 30 Min "
        "Operating Reserve, as_price_dam_reg NYCA Regulation Capacity.",
        f"The zones not kept: in the {differing['files']} daily files read by this run, a zone not kept differed "
        f"from the kept zone of its set in {differing['hours']} zone-product-hours (each is in the run log).",
    ]


SPEC = dict(
    name=NAME, connector=NAME, label="NYISO", namespace="nyiso", tz=TZ, first=common.START, geo="US-NY",
    market="nyiso_dam", source=SOURCE, report=REPORT, page=PAGE, document_list=PAGE,
    publisher=ip.ISO_PUBLISHERS["nyiso"], license="public", documents=documents, parse=parse, wanted=WANTED,
    header=header, pause=1,
    license_line="License: public, with a caution. NYISO's legal notice (https://www.nyiso.com/legal-notice) does "
                 "not forbid republishing its market data and grants no license: \"Access to this Web site does "
                 "not confer any license or ownership interest in either the form or content of the Web site\".",
)


if __name__ == "__main__":
    sys.exit(common.run(SPEC))

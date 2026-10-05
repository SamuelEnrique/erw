#!/usr/bin/env python3
"""What Texas's storage resources offered day-ahead, and how much of it was awarded, by day and by month (session 116).

Energy Research Warehouse (ERW). Method: docs/methods/ercot_storage_dam_offers.md. No request is made: the zips of
ERCOT's 60-Day DAM Disclosure Reports already saved by warehouse/connectors/ercot_dam_esr.py are read from the disk.

Two tables, one entity (ercot:esr_fleet):

  ercot_storage_dam_offers_daily     the fleet's sums for each operating day (local, Central), freq P1D
  ercot_storage_dam_offers_monthly   the days of each local month added up, freq P1M, with the month's MW from
                                     ercot_storage_dam_awards_monthly and the USD variables also per MW

From two files of each day's zip, as ERCOT prints them:

  60d_DAM_ESR_Data      a row per resource and hour: its limits (HSL, LSL), status, its Energy Bid/Offer Curve (up to
                        ten points of MW and price, from charging, negative MW, to discharging), its awards and prices
  60d_DAM_ESR_ASOffers  a row per resource, hour and offer: up to five blocks, each a quantity (MW) and a price for
                        each Ancillary Service the block is offered to (one block can be offered to several services;
                        it can be awarded to one)

Variables (a "MWh" here is a MW for an hour: of limit, of offered capacity, or of energy):

  resources, resource_hours                 resources with a row that day; rows (count)
  resource_hours_energy_offer / _as_offer / _no_offer / _out
                                            rows with an energy curve; with an Ancillary Service offer; with neither;
                                            with status OUT (count)
  limit_mwh                                 the sum of HSL (a negative HSL counts as zero)
  limit_mwh_out                             of it, rows with status OUT
  limit_mwh_no_offer, limit_mwh_no_offer_out    of it, rows with no energy curve and no Ancillary Service offer; and
                                            those of them with status OUT
  limit_mwh_energy_offer, limit_mwh_as_offer    of it, rows whose curve offers to sell (a point above 0 MW); rows with
                                            an Ancillary Service offer
  limit_mwh_award                           of it, rows with any day-ahead award
  energy_offer_mwh                          the most each curve offers to sell (its highest MW, when above zero)
  energy_offer_mwh_le_<P>                   what the curves offer to sell at a price of P or less, P in 0, 25, 50, 100,
                                            250 and 1000 USD per MWh (the curve read as ERCOT defines it: straight
                                            lines between its points)
  energy_offer_mwh_at_clearing              what the curves offer to sell at the hour's own day-ahead price at the
                                            resource's settlement point
  energy_bid_mwh, energy_bid_mwh_at_clearing    the most each curve bids to buy (charging); what it bids to buy at the
                                            hour's own price
  energy_sold_mwh, energy_bought_mwh        the awards (as in ercot_storage_dam_awards_monthly; a check)
  <service>_offer_mwh                       the blocks priced for the service, added up. Services: regup, regdn, rrs
                                            (a block priced for any of its three kinds), ecrs, nspin
  <service>_offer_mwh_le_mcpc               of it, blocks priced at or below the hour's clearing price (MCPC)
  <service>_offer_mwh_le_<P>                of it, blocks priced at P or less, P in 1, 5, 20, 100 and 1000 USD per MW
  <service>_award_mwh, <service>_award_usd  the awards, and the awards at the clearing price
  <service>_unawarded_usd                   offered less awarded, each resource and hour, at the hour's clearing price:
                                            what the unawarded offers would have been paid had they cleared at the
                                            price that was set. Not a forecast: more awards would have moved the price
  as_offer_mwh, as_award_mwh                every block once, whichever services it is priced for; the five services'
                                            awards
  as_offer_mwh_unlisted                     blocks offered by a resource with no row in the ESR data file that hour (it
                                            has no limit, status or award there): in no other sum
  (monthly only) mw, days_held, days_missing, days_in_month, <service>_unawarded_usd_per_mw, <service>_award_usd_per_mw

Nothing is filled, capped or smoothed. A block's quantity is counted as printed, also where a resource's blocks add
up to more than its limit. A day whose zip is missing or fails a check has no row. An hour with an offer and no
clearing price printed stops the day.

    python warehouse/derived/ercot_storage_dam_offers.py --from-zips        # the daily table from every saved zip, then the monthly
    python warehouse/derived/ercot_storage_dam_offers.py                    # the monthly table from the daily one
    python warehouse/derived/ercot_storage_dam_offers.py --days 2026-08-06      # add named days from their saved zips (the standing pull)
    python warehouse/derived/ercot_storage_dam_offers.py --out-dir <dir> [--from-zips]   # a trial: records nothing
"""

import argparse
import calendar
import csv
import datetime as dt
import io
import math
import os
import re
import sys
import traceback
import zipfile

import numpy as np
import pandas as pd

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.abspath(os.path.join(HERE, "..", ".."))
sys.path.insert(0, os.path.join(ROOT, "warehouse", "connectors"))
import iso_prices as ip  # noqa: E402

DAILY = "ercot_storage_dam_offers_daily"
MONTHLY = "ercot_storage_dam_offers_monthly"
AWARDS = "ercot_storage_dam_awards_monthly"
SOURCE = "erw:ercot_storage_dam_offers"
METHOD_URL = "https://github.com/SamuelEnrique/erw/blob/main/docs/methods/ercot_storage_dam_offers.md"
ENTITY = "ercot:esr_fleet"
COLS = ip.SERIES_COLS
KEY = ["entity", "variable", "ts_utc"]
ZIPS = os.path.join(ROOT, "warehouse", "raw", "ercot_60d_dam", "zips")
MANIFEST = os.path.join(ZIPS, "manifest.csv")
FIRST_DAY = dt.date(2025, 12, 6)   # the first operating day whose zip holds the ESR files (session 115)

ENERGY_BANDS = [0, 25, 50, 100, 250, 1000]   # USD per MWh
AS_BANDS = [1, 5, 20, 100, 1000]             # USD per MW per hour
POINTS = range(1, 11)
BLOCKS = range(1, 6)
# the service's name in the tables -> (its price columns in the offers file, its award columns and its MCPC column in the ESR file)
SERVICES = {"regup": (["REGUP"], ["RegUp Awarded"], "RegUp MCPC"),
            "regdn": (["REGDOWN"], ["RegDown Awarded"], "RegDown MCPC"),
            "rrs": (["RRSPFR", "RRSFFR", "RRSUFR"], ["RRSPFR Awarded", "RRSFFR Awarded", "RRSUFR Awarded"], "RRS MCPC"),
            "ecrs": (["ECRS", "OFFEC"], ["ECRSSD Awarded"], "ECRS MCPC"),
            "nspin": (["ONLINE NONSPIN", "OFFLINE NONSPIN"], ["NonSpin Awarded"], "NonSpin MCPC")}
ESR_NEED = (["Delivery Date", "Hour Ending", "Resource Name", "HSL", "LSL", "Resource Status", "Awarded Quantity", "Energy Settlement Point Price"]
            + [f"QSE submitted Curve-MW{i}" for i in POINTS] + [f"QSE submitted Curve-Price{i}" for i in POINTS]
            + [c for _, aw, m in SERVICES.values() for c in aw + [m]])
ASO_NEED = (["Delivery Date", "Hour Ending", "Resource Name"] + [f"QUANTITY MW{i}" for i in BLOCKS]
            + [f"PRICE{i} {p}" for i in BLOCKS for ps, _, _ in SERVICES.values() for p in ps])
SUM_USD = [f"{s}_{k}_usd" for s in SERVICES for k in ("award", "unawarded")]


def _num(s):
    """A column as numbers; a blank is no number (NaN), never a zero. A value that is not a number raises."""
    s = s.str.strip()
    return pd.to_numeric(s.where(s != ""), errors="raise")


def read_zip(content):
    """The two ESR files of one disclosure zip, every value a string as ERCOT prints it: (ESR data, ESR AS offers).

    Raises ValueError when either file is absent (or there is more than one), or lacks a column."""
    z = zipfile.ZipFile(io.BytesIO(content))
    out = []
    for pat, need in ((r"60d_DAM_ESR_Data", ESR_NEED), (r"60d_DAM_ESR_ASOffers", ASO_NEED)):
        names = [n for n in z.namelist() if re.search(pat, n)]
        if len(names) != 1:
            raise ValueError(f"the zip holds {len(names)} files named {pat} among its {len(z.namelist())} files")
        df = pd.read_csv(io.BytesIO(z.read(names[0])), dtype=str, keep_default_na=False, na_values=[])
        df.columns = [c.strip() for c in df.columns]
        missing = [c for c in need if c not in df.columns]
        if missing:
            raise ValueError(f"{names[0]} lacks the columns {missing}")
        out.append(df)
    return out[0], out[1]


def curve_at(M, P, price):
    """The MW of each row's curve at a price: M and P are (rows, points) arrays of the curve's MW and prices (NaN where a
    point is not given), price a number or one per row. Straight lines between the points; below the first point's
    price the first MW, above the last the last; where two points share a price, the higher MW. NaN for no curve."""
    price = np.broadcast_to(np.asarray(price, dtype=float), (M.shape[0],))
    q = M[:, 0].copy()
    for i in range(M.shape[1] - 1):
        m0, m1, p0, p1 = M[:, i], M[:, i + 1], P[:, i], P[:, i + 1]
        have = ~np.isnan(m1) & ~np.isnan(p1) & ~np.isnan(m0) & ~np.isnan(p0)
        full = have & (price >= p1)
        part = have & ~full & (price > p0)
        q = np.where(full, m1, q)
        with np.errstate(divide="ignore", invalid="ignore"):
            q = np.where(part, m0 + (price - p0) / (p1 - p0) * (m1 - m0), q)
    return q


def day_values(esr, aso, day):
    """One operating day's sums for the fleet: {variable: value}. Every check that fails raises ValueError."""
    for df, what in ((esr, "ESR data"), (aso, "ESR AS offers")):
        dates = sorted(set(df["Delivery Date"].str.strip()))
        if len(df) and (len(dates) != 1 or dt.datetime.strptime(dates[0], "%m/%d/%Y").date() != day):
            raise ValueError(f"the {what} file's delivery dates are {dates}, not {day}")
    if not len(esr):
        raise ValueError("the ESR data file has no rows")
    key = ["Resource Name", "Hour Ending"]
    esr = esr.copy()
    for c in key:
        esr[c] = esr[c].str.strip()
    if esr.duplicated(key).any():
        raise ValueError(f"{int(esr.duplicated(key).sum())} rows of the ESR data file repeat a resource and hour")
    try:
        hsl = _num(esr["HSL"])
        M = np.column_stack([_num(esr[f"QSE submitted Curve-MW{i}"]).to_numpy(float) for i in POINTS])
        P = np.column_stack([_num(esr[f"QSE submitted Curve-Price{i}"]).to_numpy(float) for i in POINTS])
        award = _num(esr["Awarded Quantity"]).fillna(0.0).to_numpy(float)
        spp = _num(esr["Energy Settlement Point Price"]).to_numpy(float)
    except (ValueError, TypeError) as e:
        raise ValueError(f"the ESR data file holds a value that is not a number: {e}")
    if hsl.isna().any():
        raise ValueError(f"{int(hsl.isna().sum())} rows have no HSL")
    if (np.isnan(M) != np.isnan(P)).any():
        raise ValueError("a curve point has a MW without a price, or a price without a MW")
    if (np.nan_to_num(np.diff(M, axis=1), nan=0.0) < -1e-9).any() or (np.nan_to_num(np.diff(P, axis=1), nan=0.0) < -1e-9).any():
        raise ValueError("a curve's MW or prices fall from one point to the next")
    limit = np.clip(hsl.to_numpy(float), 0.0, None)
    out_status = (esr["Resource Status"].str.strip() == "OUT").to_numpy()
    has_curve = ~np.isnan(M).all(axis=1)
    top = np.where(has_curve, np.nanmax(np.where(np.isnan(M), -np.inf, M), axis=1), np.nan)
    low = np.where(has_curve, np.nanmin(np.where(np.isnan(M), np.inf, M), axis=1), np.nan)
    sells = has_curve & (top > 0)
    if (has_curve & np.isnan(spp)).any():
        raise ValueError(f"{int((has_curve & np.isnan(spp)).sum())} rows have a curve and no settlement point price")

    # the Ancillary Service offers: a line per block that has a quantity
    aso = aso.copy()
    for c in key:
        aso[c] = aso[c].str.strip()
    blocks = []
    try:
        for i in BLOCKS:
            b = aso[key].copy()
            b["qty"] = _num(aso[f"QUANTITY MW{i}"])
            for s, (prices, _, _) in SERVICES.items():
                b[s] = pd.concat([_num(aso[f"PRICE{i} {p}"]) for p in prices], axis=1).min(axis=1)  # the lowest price it is offered at
            priced = b[list(SERVICES)].notna().any(axis=1)
            if (priced & b["qty"].isna()).any():
                raise ValueError(f"{int((priced & b['qty'].isna()).sum())} blocks have a price and no quantity")
            blocks.append(b[b["qty"].notna() & priced])
    except TypeError as e:
        raise ValueError(f"the ESR AS offers file holds a value that is not a number: {e}")
    blocks = pd.concat(blocks, ignore_index=True) if blocks else pd.DataFrame(columns=key + ["qty"] + list(SERVICES))
    if len(blocks) and (blocks["qty"] < 0).any():
        raise ValueError("a block has a negative quantity")
    # an offer by a resource with no row in the ESR data file that hour has no limit, status or award to set it beside:
    # it is kept out of every sum and counted on its own (as_offer_mwh_unlisted)
    listed = np.asarray(pd.MultiIndex.from_frame(blocks[key]).isin(pd.MultiIndex.from_frame(esr[key]))) if len(blocks) else np.zeros(0, bool)
    unlisted = math.fsum(blocks["qty"].to_numpy(float)[~listed]) if len(blocks) else 0.0
    blocks = blocks[listed] if len(blocks) else blocks
    as_rows = pd.MultiIndex.from_frame(esr[key]).isin(pd.MultiIndex.from_frame(blocks[key])) if len(blocks) else np.zeros(len(esr), bool)
    as_rows = np.asarray(as_rows)

    awards = {}
    any_award = award != 0
    for s, (_, cols, _) in SERVICES.items():
        awards[s] = sum(_num(esr[c]).fillna(0.0) for c in cols).to_numpy(float)
        any_award |= awards[s] != 0
    none = ~has_curve & ~as_rows
    v = {"resources": int(esr["Resource Name"].nunique()), "resource_hours": int(len(esr)),
         "resource_hours_energy_offer": int(has_curve.sum()), "resource_hours_as_offer": int(as_rows.sum()),
         "resource_hours_no_offer": int(none.sum()), "resource_hours_out": int(out_status.sum()),
         "limit_mwh": math.fsum(limit), "limit_mwh_out": math.fsum(limit[out_status]),
         "limit_mwh_no_offer": math.fsum(limit[none]), "limit_mwh_no_offer_out": math.fsum(limit[none & out_status]),
         "limit_mwh_energy_offer": math.fsum(limit[sells]), "limit_mwh_as_offer": math.fsum(limit[as_rows]),
         "limit_mwh_award": math.fsum(limit[any_award]),
         "energy_offer_mwh": math.fsum(np.clip(top[has_curve], 0.0, None))}
    for band in ENERGY_BANDS:
        v[f"energy_offer_mwh_le_{band}"] = math.fsum(np.clip(curve_at(M[has_curve], P[has_curve], band), 0.0, None))
    at = curve_at(M[has_curve], P[has_curve], spp[has_curve])
    v["energy_offer_mwh_at_clearing"] = math.fsum(np.clip(at, 0.0, None))
    v["energy_bid_mwh"] = math.fsum(np.clip(-low[has_curve], 0.0, None))
    v["energy_bid_mwh_at_clearing"] = math.fsum(np.clip(-at, 0.0, None))
    v["energy_sold_mwh"] = math.fsum(np.clip(award, 0.0, None))
    v["energy_bought_mwh"] = math.fsum(np.clip(-award, 0.0, None))

    hours = esr["Hour Ending"]
    for s, (_, _, mcol) in SERVICES.items():
        m = _num(esr[mcol])
        per_hour = m.groupby(hours).agg(lambda x: sorted(set(x.dropna())))
        if (per_hour.map(len) > 1).any():
            raise ValueError(f"{mcol} has more than one value in an hour")
        mcpc = per_hour.map(lambda x: x[0] if x else np.nan)
        b = blocks[blocks[s].notna()] if len(blocks) else blocks
        price_h = b["Hour Ending"].map(mcpc).to_numpy(float) if len(b) else np.array([])
        if len(b) and np.isnan(price_h).any():
            raise ValueError(f"{int(np.isnan(price_h).sum())} {s} blocks are in an hour with no {mcol} printed")
        qty, offer_price = (b["qty"].to_numpy(float), b[s].to_numpy(float)) if len(b) else (np.array([]), np.array([]))
        v[f"{s}_offer_mwh"] = math.fsum(qty)
        v[f"{s}_offer_mwh_le_mcpc"] = math.fsum(qty[offer_price <= price_h + 1e-9])
        for band in AS_BANDS:
            v[f"{s}_offer_mwh_le_{band}"] = math.fsum(qty[offer_price <= band])
        a = awards[s]
        row_price = hours.map(mcpc).to_numpy(float)
        if ((a != 0) & np.isnan(row_price)).any():
            raise ValueError(f"{int(((a != 0) & np.isnan(row_price)).sum())} {s} awards have no clearing price")
        offered = (b.groupby(key)["qty"].sum() if len(b) else pd.Series(dtype=float)).reindex(pd.MultiIndex.from_frame(esr[key])).fillna(0.0).to_numpy(float)
        v[f"{s}_award_mwh"] = math.fsum(a)
        v[f"{s}_award_usd"] = math.fsum(np.where(a != 0, a * np.nan_to_num(row_price), 0.0))
        left = np.clip(offered - a, 0.0, None)
        v[f"{s}_unawarded_usd"] = math.fsum(np.where(left > 0, left * np.nan_to_num(row_price), 0.0))
    v["as_offer_mwh"] = math.fsum(blocks["qty"].to_numpy(float)) if len(blocks) else 0.0
    v["as_offer_mwh_unlisted"] = unlisted
    v["as_award_mwh"] = math.fsum(v[f"{s}_award_mwh"] for s in SERVICES)
    # how well the awards sit on the curves (the log's check that the curve is read as ERCOT clears it), not a variable
    v["_curve_rows"] = int(has_curve.sum())
    v["_curve_rows_award_on_curve"] = int((np.abs(at - award[has_curve]) <= 0.1).sum())
    return v


def unit_of(variable):
    if variable == "mw":
        return "MW"
    if variable.endswith("_usd_per_mw"):
        return "USD/MW"
    if variable.endswith("_usd"):
        return "USD"
    if "_mwh" in variable:
        return "MWh"
    return "count"


def _fmt(variable, value):
    if unit_of(variable) == "count":
        return str(int(value))
    return repr(round(float(value), 2 if unit_of(variable) == "USD" else 4))


def day_rows(values, day, url, retrieved, vintage):
    """One day's values as rows of the daily table (the variables whose names begin with _ are the log's, not rows)."""
    recs = [{"entity": ENTITY, "variable": k, "ts_utc": f"{day.isoformat()}T00:00:00Z", "value": _fmt(k, x), "unit": unit_of(k), "freq": "P1D", "geo": "US-TX",
             "market": "ercot_dam", "node": "", "source": SOURCE, "source_url": url, "retrieved_at": retrieved, "vintage": vintage}
            for k, x in values.items() if not k.startswith("_")]
    return pd.DataFrame(recs, columns=COLS)


def daily_header(df, run_id, log_name, note=""):
    days = sorted(set(df["ts_utc"].str[:10]))
    first, last = dt.date.fromisoformat(days[0]), dt.date.fromisoformat(days[-1])
    gaps = [(first + dt.timedelta(days=i)).isoformat() for i in range((last - first).days + 1) if (first + dt.timedelta(days=i)).isoformat() not in set(days)]
    return [
        "Energy Research Warehouse (ERW): what ERCOT's Energy Storage Resources offered day-ahead and how much of it was awarded, the fleet by operating day "
        "(derived, session 116)",
        "Shape: series (docs/datastandard.md v0); freq P1D, ts_utc the operating day (local, Central) at 00:00:00Z; one entity, ercot:esr_fleet. A MWh here is a MW "
        "for an hour: of limit (limit_mwh and its parts: _out, _no_offer, _no_offer_out, _energy_offer, _as_offer, _award), of capacity offered or awarded, or of "
        "energy. Energy, from each resource's Energy Bid/Offer Curve: energy_offer_mwh (the most the curves offer to sell), energy_offer_mwh_le_<P> (what they offer "
        f"at P USD per MWh or less, P in {', '.join(str(b) for b in ENERGY_BANDS)}), energy_offer_mwh_at_clearing (at the hour's own day-ahead price at the resource's "
        "settlement point), energy_bid_mwh and energy_bid_mwh_at_clearing (the charging side), energy_sold_mwh and energy_bought_mwh (the awards). Ancillary Services "
        "(regup, regdn, rrs, ecrs, nspin), from the offer blocks: <service>_offer_mwh, _offer_mwh_le_mcpc (priced at or below the hour's clearing price), "
        f"_offer_mwh_le_<P> (P in {', '.join(str(b) for b in AS_BANDS)} USD per MW), _award_mwh, _award_usd, and _unawarded_usd (offered less awarded, each resource and "
        "hour, at the hour's clearing price). as_offer_mwh counts each block once; a block can be priced for several services. as_offer_mwh_unlisted: blocks offered by "
        "a resource with no row in ERCOT's ESR data file that hour, in no other sum. Counts: resources, resource_hours and its parts.",
        "WHAT IT IS NOT: day-ahead offers and awards only. No real-time offers, no state of charge, no contracts. An offer is counted at any price: capacity offered "
        "at the market's cap is in the offered total, which is why the price bands are there. _unawarded_usd values offers at the price that was set; had they cleared, "
        "the price would have been lower. Nothing is filled, capped or smoothed.",
        f"Operating days held: {len(days)}, {days[0]} to {days[-1]} (local, Central); {len(gaps)} missing between them"
        + (": " + ", ".join(gaps) if gaps else "") + ". A day whose zip is missing or fails a check has no row." + (" " + note if note else ""),
        f"Retrieved: {run_id} (UTC) by warehouse/derived/ercot_storage_dam_offers.py; each row's source_url is its day's zip, retrieved_at when the zip was downloaded, "
        "vintage when ERCOT published it (the operating day plus 60 days)",
        f"Run log: warehouse/output/logs/{log_name}",
        f"Source: {SOURCE} ERW derived table, ERCOT storage resources' day-ahead offers (docs/methods/ercot_storage_dam_offers.md), {METHOD_URL}; computed from "
        "ERCOT's 60-Day DAM Disclosure Reports (NP3-966-ER), the files 60d_DAM_ESR_Data and 60d_DAM_ESR_ASOffers, "
        "https://www.ercot.com/mp/data-products/data-product-details?id=NP3-966-ER",
        "Derived from: ercot_dam_esr_awards",
        "License: public. ERCOT's terms allow raw data to be \"used, reproduced, and redistributed in compilations, charts, and analyses\" "
        "(https://www.ercot.com/help/terms).",
        f"File holds {len(df)} rows.",
    ]


def write_table(path, head, df):
    tmp = path + ".tmp"
    with open(tmp, "w", encoding="utf-8", newline="") as f:
        for line in head:
            f.write("# " + line + "\n")
        df.to_csv(f, index=False, lineterminator="\n")
    os.replace(tmp, path)


def manifest_days():
    """{operating day: its line of the zips' manifest}, the later posting of a day winning, from the first ESR day on."""
    if not os.path.exists(MANIFEST):
        return {}
    with open(MANIFEST, encoding="utf-8", newline="") as f:
        rows = sorted(csv.DictReader(f), key=lambda r: r["published"])
    return {dt.date.fromisoformat(r["operating_day"]): r for r in rows if dt.date.fromisoformat(r["operating_day"]) >= FIRST_DAY}


def from_zips(log):
    """The daily table's rows from every saved zip: (rows, the days that failed a check with the reason)."""
    frames, failed, on_curve, curve_rows = [], [], 0, 0
    for day, r in sorted(manifest_days().items()):
        path = os.path.join(ZIPS, r["file"])
        try:
            with open(path, "rb") as f:
                esr, aso = read_zip(f.read())
            v = day_values(esr, aso, day)
        except (OSError, ValueError, zipfile.BadZipFile) as e:
            failed.append((day.isoformat(), str(e)))
            log(f"  {day}: MISSING, {e}")
            continue
        on_curve += v["_curve_rows_award_on_curve"]
        curve_rows += v["_curve_rows"]
        frames.append(day_rows(v, day, r["url"], r["retrieved_at"], ip.utc_iso(pd.Timestamp(r["published"]))))
    if not frames:
        raise RuntimeError("no saved zip gave a day: nothing is written")
    log(f"{len(frames)} days read from the saved zips, {len(failed)} failed a check; on {on_curve:,} of {curve_rows:,} rows with a curve "
        f"({on_curve / max(curve_rows, 1):.1%}) the energy award is the curve's MW at the hour's own price, within 0.1 MW")
    return pd.concat(frames, ignore_index=True), failed


def days_from_zips(days, log):
    """The rows of named operating days, each from its saved zip. A day with no saved zip, or that fails a check, raises
    RuntimeError: the daily table is not written with a hole a later run would not see."""
    man, frames = manifest_days(), []
    for day in days:
        r = man.get(day)
        if r is None:
            raise RuntimeError(f"{day}: no zip of this operating day is on this machine")
        try:
            with open(os.path.join(ZIPS, r["file"]), "rb") as f:
                esr, aso = read_zip(f.read())
            v = day_values(esr, aso, day)
        except (OSError, ValueError, zipfile.BadZipFile) as e:
            raise RuntimeError(f"{day}: {e}")
        log(f"  {day}: read from {r['file']}")
        frames.append(day_rows(v, day, r["url"], r["retrieved_at"], ip.utc_iso(pd.Timestamp(r["published"]))))
    return pd.concat(frames, ignore_index=True)


def merge_daily(old, new):
    """The daily table with a day's rows added: a day already held is replaced whole by its new rows."""
    if old is None or not len(old):
        return new.sort_values(KEY).reset_index(drop=True)
    keep = old[~old["ts_utc"].isin(set(new["ts_utc"]))]
    return pd.concat([keep, new], ignore_index=True).sort_values(KEY).reset_index(drop=True)


def monthly(daily, awards):
    """{month: {variable: value}} from the daily table's rows and the awards table's (its mw, and the sums both hold).

    Raises RuntimeError when the two tables disagree on a month's days, rows or awards: one of them is stale."""
    d = daily.assign(month=daily["ts_utc"].str[:7], day=daily["ts_utc"].str[:10], x=pd.to_numeric(daily["value"]))
    a = awards.assign(month=awards["ts_utc"].str[:7], x=pd.to_numeric(awards["value"])).pivot(index="month", columns="variable", values="x")
    days = sorted(set(d["day"]))
    first, last = dt.date.fromisoformat(days[0]), dt.date.fromisoformat(days[-1])
    out = {}
    for month, g in d.groupby("month"):
        y, m = int(month[:4]), int(month[5:])
        n = calendar.monthrange(y, m)[1]
        held = set(g["day"])
        sums = g.groupby("variable")["x"].agg(lambda s: math.fsum(s))
        v = {k: sums[k] for k in sums.index if k != "resources"}
        if month not in a.index:
            raise RuntimeError(f"{month} is in {DAILY} and not in {AWARDS}: build that table first")
        aw = a.loc[month]
        checks = [("days_held", len(held), aw["days_held"], 0), ("resource_hours", v["resource_hours"], aw["resource_hours"], 0),
                  ("energy_sold_mwh", v["energy_sold_mwh"], aw["energy_sold_mwh"], 0.5), ("energy_bought_mwh", v["energy_bought_mwh"], aw["energy_bought_mwh"], 0.5)]
        checks += [(f"{s}_award_usd", v[f"{s}_award_usd"], aw[f"revenue_{s}_usd"], 1.0) for s in SERVICES]
        bad = [f"{k}: {x:,.2f} here, {y_:,.2f} there" for k, x, y_, tol in checks if abs(float(x) - float(y_)) > tol]
        if bad:
            raise RuntimeError(f"{month}: {DAILY} and {AWARDS} disagree ({'; '.join(bad)}): nothing is written")
        mw = float(aw["mw"])
        v["mw"] = mw
        for k in SUM_USD:
            v[f"{k}_per_mw"] = v[k] / mw
        v["days_held"] = len(held)
        v["days_missing"] = sum(1 for i in range(1, n + 1) if first <= dt.date(y, m, i) <= last and dt.date(y, m, i).isoformat() not in held)
        v["days_in_month"] = n
        out[month] = v
    return out


def month_rows(months, retrieved):
    recs = []
    for month, v in sorted(months.items()):
        for k, x in v.items():
            recs.append({"entity": ENTITY, "variable": k, "ts_utc": f"{month}-01T00:00:00Z", "value": _fmt(k, x), "unit": unit_of(k), "freq": "P1M", "geo": "US-TX",
                         "market": "ercot_dam", "node": "", "source": SOURCE, "source_url": METHOD_URL, "retrieved_at": retrieved, "vintage": ""})
    return pd.DataFrame(recs, columns=COLS)


def keep_stamp(path, new):
    """A row whose value has not changed keeps its retrieved_at, so the loader rewrites only what changed. A row of the
    last run's table with no row now stops the build."""
    if not os.path.exists(path):
        return new
    old = ip.read_series(path, COLS)
    j = new.merge(old[KEY + ["value", "retrieved_at"]], on=KEY, how="left", suffixes=("", "_old"))
    same = (pd.to_numeric(j["value"]) == pd.to_numeric(j["value_old"])).values
    new = new.copy()
    new["retrieved_at"] = j["retrieved_at_old"].where(same, j["retrieved_at"]).values
    gone = old[~pd.MultiIndex.from_frame(old[KEY]).isin(pd.MultiIndex.from_frame(new[KEY]))]
    if len(gone):
        raise RuntimeError(f"{len(gone)} rows of the last run's {os.path.basename(path)} have no row now: nothing is written")
    return new


def build_monthly(out_dir, daily_path, awards_path, log, run_id, retrieved):
    for p, name in ((daily_path, DAILY), (awards_path, AWARDS)):
        if not os.path.exists(p):
            raise RuntimeError(f"{name} is not on this machine: nothing is written")
    daily = ip.read_series(daily_path, COLS)
    months = monthly(daily, ip.read_series(awards_path, COLS))
    path = os.path.join(out_dir, MONTHLY + ".csv")
    out = keep_stamp(path, month_rows(months, retrieved)).sort_values(KEY).reset_index(drop=True)
    if out.duplicated(KEY).any():
        raise RuntimeError(f"{MONTHLY}: duplicate (entity, variable, ts_utc) keys")
    days = sorted(set(daily["ts_utc"].str[:10]))
    head = [
        "Energy Research Warehouse (ERW): what ERCOT's Energy Storage Resources offered day-ahead and how much of it was awarded, the fleet by local month "
        "(derived, session 116)",
        f"Shape: series (docs/datastandard.md v0); freq P1M, ts_utc the first day of the local (Central) month at 00:00:00Z; one entity, ercot:esr_fleet. Each variable "
        f"of {DAILY} (see its header: limit_mwh and its parts, the energy curve's offers and bids, each Ancillary Service's offers, awards and unawarded value, the "
        f"counts of resource-hours) added up over the month's days held; mw (MW: the month's fleet, from {AWARDS}); each <service>_award_usd and "
        "<service>_unawarded_usd also _per_mw, over the month's mw (USD/MW; per kW is this over 1,000); days_held, days_missing, days_in_month (count).",
        "WHAT IT IS NOT: day-ahead offers and awards only. No real-time offers, no state of charge, no contracts. An offer is counted at any price, also at the "
        "market's cap. _unawarded_usd values the offered and unawarded capacity at the price that was set; had it cleared, the price would have been lower. Nothing "
        "is filled, capped or smoothed.",
        f"Operating days held: {len(days)}, {days[0]} to {days[-1]} (local, Central); {sum(v['days_missing'] for v in months.values())} missing between them. Each "
        f"month's days, resource-hours, energy awards and Ancillary Service awards are checked against {AWARDS} before anything is written.",
        f"Retrieved: {run_id} (UTC) by warehouse/derived/ercot_storage_dam_offers.py, from {len(daily)} rows of {DAILY}",
        f"Run log: warehouse/output/logs/{MONTHLY}_{run_id}.log",
        f"Source: {SOURCE} ERW derived table, ERCOT storage resources' day-ahead offers (docs/methods/ercot_storage_dam_offers.md), {METHOD_URL}",
        f"Derived from: {DAILY}; {AWARDS}",
        "License: public. A derived table inherits the most restrictive license of its inputs (Decision 23); its inputs are public (ERCOT's terms allow raw data to "
        "be \"used, reproduced, and redistributed in compilations, charts, and analyses\", https://www.ercot.com/help/terms).",
        f"File holds {len(out)} rows, rewritten whole by this run.",
    ]
    write_table(path, head, out)
    for month, v in sorted(months.items()):
        log(f"  {month}: {v['days_held']} of {v['days_in_month']} days, limit {v['limit_mwh']:,.0f} MWh, no offer {v['limit_mwh_no_offer'] / v['limit_mwh']:.1%}, "
            f"energy offered {v['energy_offer_mwh']:,.0f} (at clearing {v['energy_offer_mwh_at_clearing']:,.0f}, sold {v['energy_sold_mwh']:,.0f}), "
            f"AS offered {v['as_offer_mwh']:,.0f}, awarded {v['as_award_mwh']:,.0f}")
    print(f"{MONTHLY}.csv: rows={len(out)} months={len(months)} days={len(days)}")
    return out, months


def main(argv=None):
    ap = argparse.ArgumentParser(description="ERCOT storage resources' day-ahead offers by day and by month (derived)")
    ap.add_argument("--from-zips", action="store_true", help="rebuild the daily table from every saved zip first (no request)")
    ap.add_argument("--days", help="operating days, comma separated: add each from its saved zip to the daily table first (no request)")
    ap.add_argument("--out-dir", help="a trial: write the tables here and record nothing")
    a = ap.parse_args(argv)
    trial = bool(a.out_dir)
    out_dir = a.out_dir or ip.OUT_DIR
    os.makedirs(out_dir, exist_ok=True)
    os.makedirs(ip.LOG_DIR, exist_ok=True)
    run_id = dt.datetime.now(dt.timezone.utc).strftime("%Y%m%dT%H%M%SZ")
    retrieved = ip.utc_iso(pd.Timestamp.now(tz="UTC"))
    log_name = f"{MONTHLY}_{run_id}.log"
    log = ip.Log(os.path.join(out_dir if trial else ip.LOG_DIR, log_name))
    results = []
    daily_path = os.path.join(out_dir, DAILY + ".csv")
    try:
        if not trial:
            for n in (DAILY, MONTHLY):
                ip._require_lock(os.path.join(out_dir, n + ".csv"), f"writing {n}")
        if a.from_zips:
            new, failed = from_zips(log)
            new = keep_stamp(daily_path, new) if os.path.exists(daily_path) else new
            new = new.sort_values(KEY).reset_index(drop=True)
            note = ("Days that failed a check: " + "; ".join(f"{d} ({why})" for d, why in failed) + ".") if failed else ""
            write_table(daily_path, daily_header(new, run_id, log_name, note), new)
            print(f"{DAILY}.csv: rows={len(new)} days={new['ts_utc'].nunique()} failed={len(failed)}")
            results.append(dict(table=DAILY, market="derived", status="ok", detail=f"{len(new)} rows; {new['ts_utc'].nunique()} days; {len(failed)} failed a check"))
        if a.days:
            if not os.path.exists(daily_path):
                raise RuntimeError(f"{DAILY} is not on this machine: a day is added to the table, never written alone")
            old = ip.read_series(daily_path, COLS)
            new = merge_daily(old, days_from_zips(sorted(dt.date.fromisoformat(x) for x in a.days.split(",")), log))
            write_table(daily_path, daily_header(new, run_id, log_name), new)
            print(f"{DAILY}.csv: rows={len(new)} days={new['ts_utc'].nunique()} added={a.days}")
            results.append(dict(table=DAILY, market="derived", status="ok", detail=f"{len(new)} rows; {new['ts_utc'].nunique()} days; added {a.days}"))
        awards_path = os.path.join(ip.OUT_DIR, AWARDS + ".csv")
        out, months = build_monthly(out_dir, daily_path if os.path.exists(daily_path) else os.path.join(ip.OUT_DIR, DAILY + ".csv"), awards_path, log, run_id, retrieved)
        results.append(dict(table=MONTHLY, market="derived", status="ok", detail=f"{len(out)} rows; {len(months)} months"))
        if not trial:
            ip.update_sources([{"source": SOURCE, "publisher": "Energy Research Warehouse (ERW), derived",
                                "report": "ERCOT storage resources' day-ahead offers by day and by month (docs/methods/ercot_storage_dam_offers.md)",
                                "report_url": METHOD_URL, "document_list": "", "license": "public", "tables": [DAILY, MONTHLY]}])
    except Exception:
        tb = ip.redact(traceback.format_exc())
        log(f"FAILED:\n{tb}")
        print(f"{MONTHLY} FAILED: {tb.strip().splitlines()[-1]}", file=sys.stderr)
        results.append(dict(table=MONTHLY, market="derived", status="failed", detail=tb.strip().splitlines()[-1][:300]))
    if not trial:
        ip.write_status(MONTHLY, run_id, results)
    log.close()
    return 0 if all(r["status"] == "ok" for r in results) else 1


if __name__ == "__main__":
    sys.exit(main())

#!/usr/bin/env python3
"""erw_validate: the Energy Research Warehouse (ERW) format validator, v0.

Checks a CSV against the `series`, `events` (session 6) or `entities` (session 8)
shape of docs/datastandard.md (v0). Modeled
on the IRW's irw_validate (github.com/ben-domingue/irw): one validator, a
command line, and an exit code that a pipeline can gate on.

    python warehouse/validate/erw_validate.py warehouse/output/*.csv
    python warehouse/validate/erw_validate.py x.csv --strict   # warnings block too
    python warehouse/validate/erw_validate.py x.csv --json     # for CI

Exit codes: 0 pass, 1 blocked (at least one error), 2 bad input (a file that
cannot be read as a CSV at all). With several files the worst code wins.

pandas and the standard library only: no network, no credentials.
"""

import argparse
import json
import os
import re
import sys

import pandas as pd

STANDARD = "ERW Data Standard v0"
REQUIRED = ["entity", "variable", "ts_utc", "value"]
RESERVED = ["unit", "freq", "geo", "market", "node", "source", "source_url",
            "retrieved_at", "vintage",
            "ba", "year",  # session 29, decision 28: partition columns of the consolidated tables
            "event"]  # session 36B, decision 31: the event a row of event_window_daily belongs to
REQUIRED_BY_VALIDATOR = ["unit", "source"]
# docs/datastandard.md "Units" states these; this set is what enforces them
UNITS = {"MW", "MWh", "USD/MWh", "USD", "USD/MMBtu", "USD/bbl", "degF", "mph", "pct",  # mph: session 24, decision 27
         "USD/MW", "MWh/MW",  # session 51: merchant revenue and energy per MW installed (Decision 34)
         "year",  # session 62: a duration in years (the median time from interconnection request to operation, Decision 36)
        
         # session 7 price board (docs/datastandard.md Decision 17)
         "USD/gal", "USD/short_ton", "USD/t", "USD/lb", "USD/MW-day", "USD/tCO2", "USD/Mcf",
         "count", "kbbl", "kbbl/d", "MMcf", "bcf", "bcf/d",
         "dwt",  # session 8: IMF PortWatch deadweight tonnage (Decision 22)
         "ratio",  # session 9: a dimensionless ratio, e.g. the worst-interval multiple (Decision 23)
         "TBtu",  # session 18: trillion Btu, EIA Monthly Energy Review consumption (Decision 25)
         "MMBtu/MWh",  # session 19: implied heat rate, the trader view (Decision 26)
         "hour",  # session 31: an hour of the day, 0 to 23, local, hour beginning (storage_daily_cycle; Decision 29)
         "tCO2", "kgCO2/MWh",  # session 32: metric tons of CO2, and kilograms of CO2 per MWh (Decision 30)
         "degF-day", "bbl", "Mcf",  # session 49: degree days at 65 F; barrels and thousand cubic feet (Decision 33)
         # session 65: capacity per kW-month as NYISO and ISO-NE publish it, and capacity held for an hour, the
         # ancillary service clearing prices of ERCOT and CAISO (Decision 37)
         "USD/kW-month", "USD/MW-hour",
         # session 306: the battery's published cost cases as the ATB prints them, per kW of power, per kWh of energy,
         # and per kW a year (battery_sourced_ranges; Decision 47)
         "USD/kW", "USD/kWh", "USD/kW-year",
         # session 345: JEDI's jobs per MW (job-years of a build, jobs of each operating year) and dollars per MW a year
         # (nlr_jedi_multipliers; Decision 48)
         "FTE-year/MW", "FTE/MW", "USD/MW-year",
         # session 671: a duration in mean months of 30.4375 days (interconnection_durations_summary; Decision 49)
         "month",
         # session 685: a quantity of coal in short tons (2,000 lb), as EIA publishes it (eia_coal_production_annual; Decision 50)
         "short_ton",
         # session 695: a distribution utility's reliability as EIA-861 publishes it: SAIDI in minutes of interruption per
         # customer, SAIFI in interruptions per customer, CAIDI in minutes per interruption, each over the row's period
         # (eia861_utility_reliability; Decision 51)
         "minute/customer", "interruption/customer", "minute/interruption",
         # session 870: coal's heat content in Btu per pound, as Form EIA-923 gives it (eia_coal_shipments_annual; Decision 52)
         "Btu/lb",
         # session 889: an index number on its source's base period, as the Federal Reserve's G.17 gives industrial
         # production (2017 = 100) (frb_utility_output_monthly; Decision 53)
         "index",
         # session 904: a quantity in pounds (EIA's uranium in pounds of U3O8 equivalent, named in the header), enrichment
         # in separative work units and its price per unit (eia_uranium_marketing_annual; Decision 55)
         "lb", "SWU", "USD/SWU",
         # session 954: a quantity in metric tons and a price per kilogram, as the USGS's Mineral Commodity Summaries give
         # them (usgs_mcs_critical_minerals; Decision 56)
         "t", "USD/kg",
         # session 2030: a volume in U.S. gallons, as EPA's Renewable Fuel Standard data give batch volumes (epa_rfs_rins_monthly;
         # Decision 59)
         "gal",
         # session 2045: precipitation in inches, as NOAA's nClimDiv gives a state's month (noaa_climdiv_state_monthly;
         # Decision 60)
         "in",
         # session 2072: metric tons of CO2 equivalent, as EPA's GHGRP reports a facility's total (AR4 global warming
         # potentials; epa_ghgrp_facility_emissions; Decision 61)
         "tCO2e",
         # session 2092: degrees Celsius, the Oceanic Nino Index and the Nino 3.4 sea surface temperature as NOAA CPC gives them
         # (noaa_cpc_oni_monthly; Decision 62)
         "degC",
         # session 2106: an area in acres (43,560 square feet), as BLM counts federal land under oil and gas lease
         # (blm_oil_gas_statistics_annual; Decision 63)
         "acre",
         # session 2107: solar radiation in megajoules per square meter a day, as NOAA's USCRN gives a month's average daily
         # total (noaa_uscrn_solar_monthly; Decision 64)
         "MJ/m2-day",
         # session 2113: a river's discharge in cubic feet a second, as the USGS gives a gauge's daily mean
         # (usgs_streamflow_daily; Decision 65)
         "ft3/s",
         # session 2150: electricity used a person in a year, in kWh, as the World Bank republishes the IEA's figure
         # (wb_iea_electricity_annual; Decision 68)
         "kWh/person"}
NAME_RE = re.compile(r"^[a-z0-9]+(_[a-z0-9]+){2,}$")
NAME_MAX = 40
TS_RE = re.compile(r"^\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}Z$")
TS_FMT = "%Y-%m-%dT%H:%M:%SZ"
FREQ_RE = re.compile(r"^P(\d+[YMWD])*(T(\d+H)?(\d+M)?(\d+S)?)?$")
ENTITY_RE = re.compile(r"^[a-z0-9_]+:.+$")
GEO_RE = re.compile(r"^[A-Z]{2}(-[A-Z0-9]{1,3})?$")


EVENTS_NAME_RE = re.compile(r"^[a-z0-9]+(_[a-z0-9]+)+$")
EVENTS_COLS = ["event_id", "event_date", "event_type", "parties", "entity_ids", "mw", "price",
               "currency", "status", "source", "source_url"]
EVENTS_REQUIRED = ["event_id", "event_date", "event_type", "source", "source_url"]
DATE_RE = re.compile(r"^\d{4}-\d{2}-\d{2}$")
CURRENCY_RE = re.compile(r"^[A-Z]{3}$")
SCORE_COLS = ["significance", "ai_power_relevance"]  # news scores, 0 to 10 (Decision 15)


def validate_events(df, header, err, warn, info):
    """The events shape of docs/datastandard.md (session 6)."""
    cols = list(df.columns)
    if not header:
        warn("provenance_header", "no '#' provenance header lines; connector output must have them")
    missing = [c for c in EVENTS_REQUIRED if c not in cols]
    if missing:
        err("required_columns", f"missing required events column(s): {', '.join(missing)}")
        return
    present = [c for c in cols if c in EVENTS_COLS]
    if present != [c for c in EVENTS_COLS if c in cols] or cols[:len(present)] != present:
        err("required_order", f"events standard columns must come first, in the order "
            f"{EVENTS_COLS}; got {cols[:len(EVENTS_COLS)]}")
    if len(set(cols)) != len(cols):
        err("duplicate_columns", "a column name appears more than once")
    if len(df) == 0:
        err("empty", "no data rows")
        return
    blank_id = df["event_id"].str.strip() == ""
    if blank_id.any():
        err("event_id_missing", f"{int(blank_id.sum())} empty event_id value(s)")
    dup = df["event_id"].duplicated(keep=False) & ~blank_id
    if dup.any():
        err("duplicate_key", f"{int(dup.sum())} rows share an event_id, e.g. "
            f"{examples(df.loc[dup, 'event_id'].unique())}")
    d = df["event_date"]
    bad = d[~(d.str.match(DATE_RE) | d.str.match(TS_RE))]
    if len(bad):
        err("event_date_format", f"{len(bad)} value(s) neither YYYY-MM-DD nor "
            f"YYYY-MM-DDTHH:MM:SSZ: {examples(bad.unique())}")
    else:
        parsed = pd.to_datetime(d.where(d.str.match(TS_RE), d + "T00:00:00Z"), format=TS_FMT,
                                utc=True, errors="coerce")
        if parsed.isna().any():
            err("event_date_parse", f"{int(parsed.isna().sum())} value(s) are not real dates")
        else:
            info.append(f"event_date {parsed.min():%Y-%m-%dT%H:%M:%SZ} .. {parsed.max():%Y-%m-%dT%H:%M:%SZ}")
    for c in ("event_type", "source", "source_url"):
        blank = df[c].str.strip() == ""
        if blank.any():
            err(f"{c}_present", f"{int(blank.sum())} row(s) with empty '{c}'")
    not_http = df["source_url"][~df["source_url"].str.match(r"^https?://") & (df["source_url"] != "")]
    if len(not_http):
        err("source_url_format", f"{len(not_http)} source_url value(s) not http(s): "
            f"{examples(not_http.unique())}")
    for c in ("mw", "price") + tuple(c for c in SCORE_COLS if c in cols):
        if c not in cols:
            continue
        v = df[c][df[c].str.strip() != ""]
        num = pd.to_numeric(v, errors="coerce")
        if num.isna().any():
            err(f"{c}_numeric", f"{int(num.isna().sum())} non-numeric {c} value(s): "
                f"{examples(v[num.isna()].unique())}")
        if c in SCORE_COLS and ((num < 0) | (num > 10)).any():
            err(f"{c}_range", f"{int(((num < 0) | (num > 10)).sum())} {c} value(s) outside 0 to 10")
    if "currency" in cols:
        v = df["currency"][df["currency"].str.strip() != ""]
        bad = v[~v.str.match(CURRENCY_RE)]
        if len(bad):
            err("currency_format", f"{len(bad)} currency value(s) not ISO 4217: {examples(bad.unique())}")
    info.append(f"events={len(df)} event_types={sorted(df['event_type'].unique())} "
                f"sources={df['source'].nunique()}")


ENTITIES_COLS = ["entity_id", "entity_type", "name", "geo", "lat", "lon", "capacity_mw", "status",
                 "status_date", "operator", "source"]
ENTITIES_REQUIRED = ["entity_id", "entity_type", "name", "source"]
ENTITY_TYPES = {"plant", "generator", "project", "datacenter", "substation", "utility", "company",
                "counterparty",
                "equipment",  # session 896: a plant's boiler, cooling system or emissions control (EIA-860; Decision 54)
                "dam",  # session 982: a dam and its reservoir, the National Inventory of Dams (usace_nid_dams; Decision 57)
                "platform"}  # session 2007: an offshore oil and gas structure, BOEM's platform files (boem_offshore_platforms; Decision 58)
# docs/datastandard.md shape (b) and Decision 20: the source's own status stays in its own column
ENTITY_STATUS = {"operating", "planned", "under_construction", "retired", "withdrawn", "active",
                 "completed", "suspended"}


def validate_entities(df, header, err, warn, info):
    """The entities shape of docs/datastandard.md (session 8)."""
    cols = list(df.columns)
    if not header:
        warn("provenance_header", "no '#' provenance header lines; connector output must have them")
    missing = [c for c in ENTITIES_REQUIRED if c not in cols]
    if missing:
        err("required_columns", f"missing required entities column(s): {', '.join(missing)}")
        return
    present = [c for c in cols if c in ENTITIES_COLS]
    if present != [c for c in ENTITIES_COLS if c in cols] or cols[:len(present)] != present:
        err("required_order", f"entities standard columns must come first, in the order "
            f"{ENTITIES_COLS}; got {cols[:len(ENTITIES_COLS)]}")
    if len(set(cols)) != len(cols):
        err("duplicate_columns", "a column name appears more than once")
    if len(df) == 0:
        err("empty", "no data rows")
        return
    for c in ENTITIES_REQUIRED:
        if c == "name":
            continue  # a source may list a thing without a name (queue positions); counted below
        blank = df[c].str.strip() == ""
        if blank.any():
            err(f"{c}_present", f"{int(blank.sum())} row(s) with empty '{c}'")
    unnamed = int((df["name"].str.strip() == "").sum())
    if unnamed:
        info.append(f"rows without a name (the source gives none): {unnamed}")
    bad = df["entity_id"][~df["entity_id"].str.match(ENTITY_RE)]
    if len(bad):
        err("entity_id_format", f"{len(bad)} entity_id value(s) not namespace:id: {examples(bad.unique())}")
    dup = df["entity_id"].duplicated(keep=False)
    if dup.any():
        err("duplicate_key", f"{int(dup.sum())} rows share an entity_id, e.g. "
            f"{examples(df.loc[dup, 'entity_id'].unique())}")
    bad = df["entity_type"][~df["entity_type"].isin(ENTITY_TYPES)]
    if len(bad):
        err("entity_type_vocabulary", f"{len(bad)} entity_type value(s) not in {sorted(ENTITY_TYPES)}: "
            f"{examples(bad.unique())}")
    if "geo" in cols:
        g = df["geo"][df["geo"].str.strip() != ""]
        bad = g[~g.str.match(GEO_RE)]
        if len(bad):
            err("geo_format", f"{len(bad)} geo value(s) not ISO 3166: {examples(bad.unique())}")
    for c, lo, hi in (("lat", -90, 90), ("lon", -180, 180)):
        if c not in cols:
            continue
        v = df[c][df[c].str.strip() != ""]
        num = pd.to_numeric(v, errors="coerce")
        if num.isna().any():
            err(f"{c}_numeric", f"{int(num.isna().sum())} non-numeric {c} value(s): {examples(v[num.isna()].unique())}")
        out = num[(num < lo) | (num > hi)]
        if len(out):
            err(f"{c}_range", f"{len(out)} {c} value(s) outside [{lo}, {hi}]: {examples(out.unique())}")
    if "lat" in cols and "lon" in cols:
        half = (df["lat"].str.strip() == "") != (df["lon"].str.strip() == "")
        if half.any():
            err("lat_lon_pair", f"{int(half.sum())} row(s) with lat or lon but not both")
    for c in [c for c in cols if c == "capacity_mw" or c.endswith("_mw")]:
        v = df[c][df[c].str.strip() != ""]
        num = pd.to_numeric(v, errors="coerce")
        if num.isna().any():
            err(f"{c}_numeric", f"{int(num.isna().sum())} non-numeric {c} value(s): {examples(v[num.isna()].unique())}")
        if (num < 0).any():  # real: queue requests for a net reduction (repowering), as the ISO states them
            info.append(f"{c}: {int((num < 0).sum())} negative value(s), kept as the source states them")
    if "status" in cols:
        s = df["status"][df["status"].str.strip() != ""]
        bad = s[~s.isin(ENTITY_STATUS)]
        if len(bad):
            err("status_vocabulary", f"{len(bad)} status value(s) not in {sorted(ENTITY_STATUS)}: "
                f"{examples(bad.unique())}")
    for c in [c for c in cols if c == "status_date" or c.endswith("_date")]:
        v = df[c][df[c].str.strip() != ""]
        bad = v[~v.str.match(DATE_RE)]
        if len(bad):
            err(f"{c}_format", f"{len(bad)} {c} value(s) not YYYY-MM-DD: {examples(bad.unique())}")
        elif len(v) and pd.to_datetime(v, format="%Y-%m-%d", errors="coerce").isna().any():
            err(f"{c}_parse", f"{c} holds impossible dates")
    if "source_url" in cols:
        not_http = df["source_url"][~df["source_url"].str.match(r"^https?://")]
        if len(not_http):
            err("source_url_format", f"{len(not_http)} source_url value(s) not http(s): "
                f"{examples(not_http.unique())}")
    info.append(f"entities={len(df)} entity_types={sorted(df['entity_type'].unique())} "
                f"status={dict(df['status'].value_counts()) if 'status' in cols else {}}")


class BadInput(Exception):
    pass


def read(path):
    """Return (header comment lines, frame of strings). Raise BadInput."""
    if not os.path.isfile(path):
        raise BadInput(f"no such file: {path}")
    # session 29: the comment lines are read one by one, not the whole file as text first (the consolidated
    # ERCOT history is 0.65 GB; its lines as strings cost about as much again as the frame). A byte that is
    # not UTF-8 after the header still fails, in the CSV parse below.
    header, first = [], None
    try:
        with open(path, encoding="utf-8") as f:
            for line in f:
                line = line.rstrip("\r\n")
                if line.startswith("#"):
                    header.append(line)
                    continue
                first = line
                break
    except UnicodeDecodeError as exc:
        raise BadInput(f"not UTF-8: {exc}")
    n = len(header)
    if first is None or not first.strip():
        raise BadInput("no header row after the comment lines")
    try:
        df = pd.read_csv(path, skiprows=n, dtype=str, keep_default_na=False,
                         na_values=[], encoding="utf-8")
    except UnicodeDecodeError as exc:
        raise BadInput(f"not UTF-8: {exc}")
    except Exception as exc:
        raise BadInput(f"cannot parse as CSV: {exc}")
    return header, df


def examples(values, k=5):
    return ", ".join(repr(v) for v in list(values)[:k])


def validate(path):
    """Return a report dict: file, errors, warnings, info. Raises BadInput."""
    errors, warnings, info = [], [], []

    def err(check, msg):
        errors.append({"check": check, "detail": msg})

    def warn(check, msg):
        warnings.append({"check": check, "detail": msg})

    base = os.path.basename(path)
    stem, ext = os.path.splitext(base)
    if ext.lower() != ".csv":
        err("file_extension", f"expected .csv, got {ext or 'none'}")
    if len(stem) > NAME_MAX:
        err("file_name_length", f"'{stem}' is {len(stem)} characters, max {NAME_MAX}")

    header, df = read(path)
    cols = list(df.columns)
    info.append(f"rows={len(df)} columns={len(cols)} header_comment_lines={len(header)}")

    if cols[:2] == ["entity_id", "entity_type"]:  # the entities shape (session 8)
        if not EVENTS_NAME_RE.match(stem):
            err("file_name_pattern", f"'{stem}' is not source_product (lowercase letters, digits, "
                "underscores, at least two parts)")
        validate_entities(df, header, err, warn, info)
        return {"file": path, "standard": STANDARD, "shape": "entities",
                "errors": errors, "warnings": warnings, "info": info}
    if "event_id" in cols:  # the events shape (session 6)
        if not EVENTS_NAME_RE.match(stem):
            err("file_name_pattern", f"'{stem}' is not domain_product (lowercase letters, digits, "
                "underscores, at least two parts; events tables have no market)")
        validate_events(df, header, err, warn, info)
        return {"file": path, "standard": STANDARD, "shape": "events",
                "errors": errors, "warnings": warnings, "info": info}
    if not NAME_RE.match(stem):
        err("file_name_pattern", f"'{stem}' is not source_market_product "
            "(lowercase letters, digits, underscores, at least three parts)")

    if not header:
        warn("provenance_header", "no '#' provenance header lines; connector output must have them")

    # required columns, present and first, in order
    missing = [c for c in REQUIRED if c not in cols]
    if missing:
        err("required_columns", f"missing required column(s): {', '.join(missing)}")
    elif cols[:len(REQUIRED)] != REQUIRED:
        err("required_order", f"first columns must be {REQUIRED}, got {cols[:len(REQUIRED)]}")

    for c in REQUIRED_BY_VALIDATOR:
        if c not in cols:
            err(f"{c}_present", f"column '{c}' is required in v0")
        else:
            blank = int((df[c].str.strip() == "").sum())
            if blank:
                err(f"{c}_present", f"{blank} row(s) with empty '{c}'")

    unknown = [c for c in cols if c not in REQUIRED + RESERVED and not c.startswith("x_")]
    if unknown:
        warn("unknown_columns", f"not reserved and not prefixed x_: {', '.join(unknown)}")
    present_reserved = [c for c in cols if c in RESERVED]
    if present_reserved != [c for c in RESERVED if c in cols]:
        warn("reserved_order", f"reserved columns out of standard order: {present_reserved}")
    if len(set(cols)) != len(cols):
        err("duplicate_columns", "a column name appears more than once")

    if len(df) == 0:
        err("empty", "no data rows")

    if "ts_utc" in cols:
        ts = df["ts_utc"]
        bad = ts[~ts.str.match(TS_RE)]
        if len(bad):
            err("ts_utc_format", f"{len(bad)} value(s) not YYYY-MM-DDTHH:MM:SSZ (UTC): {examples(bad)}")
        good = ts[ts.str.match(TS_RE)]
        parsed = pd.to_datetime(good, format=TS_FMT, utc=True, errors="coerce")
        if parsed.isna().any():
            err("ts_utc_parse", f"{int(parsed.isna().sum())} value(s) are not real UTC times: "
                f"{examples(good[parsed.isna()])}")
        if parsed.notna().any():
            info.append(f"ts_utc {parsed.min():%Y-%m-%dT%H:%M:%SZ} .. {parsed.max():%Y-%m-%dT%H:%M:%SZ}")

    if "value" in cols:
        v = df["value"]
        blank = v.str.strip() == ""
        if blank.any():
            err("value_missing", f"{int(blank.sum())} empty value(s); omit the row instead")
        num = pd.to_numeric(v[~blank], errors="coerce")
        nonnum = v[~blank][num.isna()]
        if len(nonnum):
            err("value_numeric", f"{len(nonnum)} non-numeric value(s): {examples(nonnum.unique())}")
        inf = num[num.abs() == float("inf")]
        if len(inf):
            err("value_numeric", f"{len(inf)} infinite value(s)")
        if num.notna().any():
            info.append(f"value {num.min()} .. {num.max()}")

    if not missing:
        # session 36C, decision 32: a table with an event column (event_window_daily) is keyed by it too
        key = ["entity", "variable", "ts_utc"] + (["event"] if "event" in cols else [])
        dup = df.duplicated(key, keep=False)
        if dup.any():
            first = df.loc[dup, key].head(3).to_dict("records")
            err("duplicate_key", f"{int(dup.sum())} rows share an ({', '.join(key)}) key, "
                f"e.g. {first}")
        bad_ent = df["entity"][~df["entity"].str.match(ENTITY_RE)]
        if len(bad_ent):
            warn("entity_namespace", f"{len(bad_ent)} entity value(s) not namespace:id: "
                 f"{examples(bad_ent.unique())}")
        info.append(f"entities={df['entity'].nunique()} variables={df['variable'].nunique()}")

    for c in ("retrieved_at", "vintage"):
        if c in cols:
            s = df[c][df[c].str.strip() != ""]
            bad = s[~s.str.match(TS_RE)]
            if len(bad):
                warn(f"{c}_format", f"{len(bad)} value(s) not ISO 8601 UTC: {examples(bad.unique())}")
    if "freq" in cols:
        s = df["freq"][df["freq"].str.strip() != ""]
        bad = s[~s.str.match(FREQ_RE)]
        if len(bad):
            warn("freq_format", f"{len(bad)} value(s) not an ISO 8601 duration: {examples(bad.unique())}")
    if "freq" in cols and "ts_utc" in cols:
        # a fixed sub-daily freq must match the timestamps' grid (session 2)
        m = df["freq"].str.extract(r"^PT(?:(\d+)H)?(?:(\d+)M)?$")
        step = m[0].astype(float).fillna(0) * 60 + m[1].astype(float).fillna(0)
        ts = pd.to_datetime(df["ts_utc"], format=TS_FMT, utc=True, errors="coerce")
        has = (step > 0) & ts.notna()
        if has.any():
            mins = (ts[has].dt.hour * 60 + ts[has].dt.minute).astype(int)
            bad = (mins % step[has].astype(int) != 0) | (ts[has].dt.second != 0)
            off = pd.Series(False, index=df.index)
            off.loc[has] = bad.to_numpy(dtype=bool)
            if off.any():
                err("ts_freq_alignment", f"{int(off.sum())} ts_utc value(s) not on the grid of "
                    f"their freq: {examples((df.loc[off, 'freq'] + ' ' + df.loc[off, 'ts_utc']).unique())}")
        # a daily or longer freq names a date: ts_utc must be that date at 00:00:00Z (session 5)
        dated = df["freq"].str.match(r"^P\d+[DWMY]$") & ts.notna()
        if dated.any():
            t = ts[dated]
            off = (t.dt.hour != 0) | (t.dt.minute != 0) | (t.dt.second != 0)
            if off.any():
                err("ts_freq_alignment", f"{int(off.sum())} ts_utc value(s) with a daily or longer "
                    f"freq are not at 00:00:00Z: {examples(df.loc[off[off].index, 'ts_utc'].unique())}")
    if "unit" in cols:
        # unit strings from a closed vocabulary (session 5)
        s = df["unit"][df["unit"].str.strip() != ""]
        bad = s[~s.isin(UNITS)]
        if len(bad):
            err("unit_vocabulary", f"{len(bad)} value(s) not in the unit vocabulary "
                f"{sorted(UNITS)}: {examples(bad.unique())}")
    if "geo" in cols:
        # one ISO 3166-2 code, or a comma-separated list of them (session 2)
        s = df["geo"][df["geo"].str.strip() != ""]
        ok = s.str.split(",").map(lambda parts: all(GEO_RE.match(p) for p in parts))
        bad = s[~ok]
        if len(bad):
            err("geo_format", f"{len(bad)} value(s) not ISO 3166-2 codes separated by commas "
                f"(no spaces): {examples(bad.unique())}")

    return {"file": path, "standard": STANDARD, "shape": "series",
            "errors": errors, "warnings": warnings, "info": info}


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__.split("\n\n")[0])
    ap.add_argument("files", nargs="+", help="CSV file(s) to validate")
    ap.add_argument("--strict", action="store_true", help="warnings block too")
    ap.add_argument("--json", action="store_true", help="print JSON reports")
    args = ap.parse_args(argv)

    worst = 0
    reports = []
    for path in args.files:
        try:
            r = validate(path)
            blocked = bool(r["errors"]) or (args.strict and bool(r["warnings"]))
            r["verdict"] = "blocked" if blocked else "pass"
            code = 1 if blocked else 0
        except BadInput as exc:
            r = {"file": path, "verdict": "bad input", "detail": str(exc)}
            code = 2
        worst = max(worst, code)
        reports.append(r)

    if args.json:
        print(json.dumps(reports, indent=2))
    else:
        for r in reports:
            print(f"{r['file']}")
            if r["verdict"] == "bad input":
                print(f"  BAD INPUT: {r['detail']}")
                continue
            print(f"  {STANDARD}, shape {r['shape']}: {r['verdict'].upper()} "
                  f"({len(r['errors'])} error(s), {len(r['warnings'])} warning(s))")
            for i in r["info"]:
                print(f"  info  {i}")
            for e in r["errors"]:
                print(f"  ERROR [{e['check']}] {e['detail']}")
            for w in r["warnings"]:
                print(f"  warn  [{w['check']}] {w['detail']}")
    return worst


if __name__ == "__main__":
    sys.exit(main())

#!/usr/bin/env python3
"""erw_validate: the Energy Research Warehouse (ERW) format validator, v0.

Checks a CSV against the `series` shape of docs/datastandard.md (v0). Modeled
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
            "retrieved_at", "vintage"]
REQUIRED_BY_VALIDATOR = ["unit", "source"]
# docs/datastandard.md "Units" states these; this set is what enforces them
UNITS = {"MW", "MWh", "USD/MWh", "USD", "USD/MMBtu", "USD/bbl", "degF", "pct"}
NAME_RE = re.compile(r"^[a-z0-9]+(_[a-z0-9]+){2,}$")
NAME_MAX = 40
TS_RE = re.compile(r"^\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}Z$")
TS_FMT = "%Y-%m-%dT%H:%M:%SZ"
FREQ_RE = re.compile(r"^P(\d+[YMWD])*(T(\d+H)?(\d+M)?(\d+S)?)?$")
ENTITY_RE = re.compile(r"^[a-z0-9_]+:.+$")
GEO_RE = re.compile(r"^[A-Z]{2}(-[A-Z0-9]{1,3})?$")


class BadInput(Exception):
    pass


def read(path):
    """Return (header comment lines, frame of strings). Raise BadInput."""
    if not os.path.isfile(path):
        raise BadInput(f"no such file: {path}")
    try:
        with open(path, encoding="utf-8") as f:
            lines = f.read().splitlines()
    except UnicodeDecodeError as exc:
        raise BadInput(f"not UTF-8: {exc}")
    n = 0
    while n < len(lines) and lines[n].startswith("#"):
        n += 1
    if n == len(lines) or not lines[n].strip():
        raise BadInput("no header row after the comment lines")
    try:
        df = pd.read_csv(path, skiprows=n, dtype=str, keep_default_na=False,
                         na_values=[], encoding="utf-8")
    except Exception as exc:
        raise BadInput(f"cannot parse as CSV: {exc}")
    return lines[:n], df


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
    if not NAME_RE.match(stem):
        err("file_name_pattern", f"'{stem}' is not source_market_product "
            "(lowercase letters, digits, underscores, at least three parts)")

    header, df = read(path)
    cols = list(df.columns)
    info.append(f"rows={len(df)} columns={len(cols)} header_comment_lines={len(header)}")

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
        key = ["entity", "variable", "ts_utc"]
        dup = df.duplicated(key, keep=False)
        if dup.any():
            first = df.loc[dup, key].head(3).to_dict("records")
            err("duplicate_key", f"{int(dup.sum())} rows share an (entity, variable, ts_utc) key, "
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
            print(f"  {STANDARD}, shape series: {r['verdict'].upper()} "
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

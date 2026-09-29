#!/usr/bin/env python3
"""Tools the ERW question-answering model may call (session 12, platform tool 20).

Energy Research Warehouse (ERW). Four tools over the erw package, and nothing else:

    list_tables     tables in the warehouse, filtered by sector, license or ISO
    describe_table  one table's columns, entities, variables, units, date range,
                    source reports and license
    query           one aggregation over one table, optionally filtered and grouped
    compare         two queries side by side

There is no free-form SQL and no code execution. A query picks an aggregation from
a fixed list (latest, mean, median, min, max, percentile, count, sum) and a grouping
from a fixed list (year, month, day, hour, entity, or one of the table's own text
columns such as state or technology_group). Every result carries the table name,
the data version, the table's source report and license, and the erw citation, so
the model can cite every number it states.

The backend is the erw package's: local files by default, or Supabase or Redivis
when ERW_BACKEND is set (erw.set_backend()). The Supabase live set holds the last
90 days of power prices and demand, not the full history.

    python warehouse/chat/tools.py query '{"table": "eia_fuel_spot_prices", "entity": "eia:henry_hub", "aggregation": "latest"}'
"""

import json
import math
import os
import sys

import numpy as np
import pandas as pd

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.abspath(os.path.join(HERE, "..", ".."))
sys.path.insert(0, os.path.join(ROOT, "package", "src"))
import erw  # noqa: E402

AGGREGATIONS = ["latest", "mean", "median", "min", "max", "percentile", "count", "sum"]
TIME_GROUPS = ["year", "month", "day", "hour"]
MAX_GROUPS = 60        # rows returned by one query; more are counted and cut
MAX_LIST = 80          # entities or variables listed by describe_table
DIGITS = 6             # decimals kept in returned values

SECTORS = ["power", "gas", "oil", "products", "lng", "coal", "uranium", "carbon", "capacity", "metals",
           "equities", "news", "deals", "datacenters"]

QUERY_PROPS = {
    "table": {"type": "string", "description": "ERW table name, exactly as list_tables gives it."},
    "entity": {"type": "string", "description": "Series: an entity (\"ercot:HB_NORTH\", \"eia:henry_hub\") or a node as the ISO writes it (\"HB_NORTH\", \"N.Y.C.\"). Entities tables: an entity_id or name. Exact string."},
    "variable": {"type": "string", "description": "Series only: the variable (\"spp_dam\", \"lmp_rtm_15m_mean\", \"spot_price\", \"demand_mw\", \"peak_iqr\"). Exact string."},
    "start": {"type": "string", "description": "Keep rows whose time is at or after this, ISO 8601 (\"2026-09-01\", \"2026-09-01T05:00:00Z\"); a date or a time without Z or an offset is read in tz (default UTC), so start 2026-09-25 with tz America/Chicago is 05:00Z; but in a table of daily or longer rows (freq P1D, P1W, P1M, P1Y), each row is labelled with its local date at 00:00Z, so a date bound is that date whatever tz says. Series: ts_utc (interval start); events: event_date; entities: status_date."},
    "end": {"type": "string", "description": "Keep rows whose time is before this (exclusive), same rules as start."},
    "where": {"type": "object", "description": "Exact-match filters on the table's own columns, {column: value} or {column: [values]}, for example {\"state\": \"TX\", \"technology_group\": \"natural_gas\", \"status\": \"operating\"}. Use describe_table to see columns and values.", "additionalProperties": {"anyOf": [{"type": "string"}, {"type": "array", "items": {"type": "string"}}]}},
    "aggregation": {"type": "string", "enum": AGGREGATIONS, "description": "latest: the newest row (per group). count: number of rows. The others apply to value_column."},
    "percentile": {"type": "number", "description": "Required when aggregation is percentile: 0 to 100 (numpy linear interpolation)."},
    "value_column": {"type": "string", "description": "Numeric column to aggregate. Default: value (series), capacity_mw (entities). For EIA-860M, nameplate_mw is the nameplate capacity."},
    "group_by": {"type": "string", "description": "One of year, month, day, hour (of the row time, in tz), entity, or one of the table's own text columns (for example state, technology_group, status, sector). Omit for one overall result."},
    "tz": {"type": "string", "description": "IANA time zone, default UTC: for year/month/day/hour grouping, and for reading a start or end given without Z or an offset (a local operating day is start and end dates with its tz). ISO operating days are local: ERCOT and SPP America/Chicago, CAISO America/Los_Angeles, NYISO and ISO-NE America/New_York, MISO EST (use Etc/GMT+5)."},
}

TOOLS = [
    {
        "name": "list_tables",
        "description": "List the tables in the Energy Research Warehouse with their sector, license, ISO, interval, first and last time, row count and source report. Call this first to find the table that answers a question. Filters are optional.",
        "input_schema": {
            "type": "object",
            "properties": {
                "sector": {"type": "string", "enum": SECTORS, "description": "Keep tables in this sector."},
                "license": {"type": "string", "enum": ["public", "internal"], "description": "public tables may be shown to anyone; internal ones are licensed for internal use only."},
                "iso": {"type": "string", "description": "Keep tables of this ISO: ERCOT, CAISO, NYISO, MISO, SPP, ISO-NE, PJM, US48."},
            },
            "additionalProperties": False,
        },
    },
    {
        "name": "describe_table",
        "description": "Describe one table: its shape (series, entities or events), columns, entities or nodes, variables, units, frequency, first and last time, row count, source reports, license and notes. For entities tables, the values of its text columns (for example state, technology_group, status) and their counts.",
        "input_schema": {
            "type": "object",
            "properties": {"table": {"type": "string", "description": "ERW table name."}},
            "required": ["table"],
            "additionalProperties": False,
        },
    },
    {
        "name": "query",
        "description": "Compute one aggregation over one table, optionally filtered by entity, variable, time range and column values, and optionally grouped. Returns a small result table (at most 60 rows), the number of rows it was computed from, and the table's citation. Series times are interval starts in UTC. min and max also return when (and for which entity) the extreme occurred.",
        "input_schema": {
            "type": "object",
            "properties": QUERY_PROPS,
            "required": ["table", "aggregation"],
            "additionalProperties": False,
        },
    },
    {
        "name": "compare",
        "description": "Run two queries (each with the same fields as query) and return both results side by side, with the difference (b minus a) and the ratio (b over a) when both results are single values.",
        "input_schema": {
            "type": "object",
            "properties": {
                "a": {"type": "object", "properties": QUERY_PROPS, "required": ["table", "aggregation"], "additionalProperties": False},
                "b": {"type": "object", "properties": QUERY_PROPS, "required": ["table", "aggregation"], "additionalProperties": False},
            },
            "required": ["a", "b"],
            "additionalProperties": False,
        },
    },
]


class ToolError(Exception):
    """A request the tools cannot answer; the message goes back to the model."""


_frames = {}
_cites = {}
_backend_ready = False


def _ready():
    global _backend_ready
    if not _backend_ready:
        erw.set_backend()  # ERW_BACKEND=local|redivis|supabase
        _backend_ready = True


def _coverage():
    _ready()
    if "_coverage" not in _frames:
        _frames["_coverage"] = erw.coverage()
    return _frames["_coverage"]


def _table(name):
    _ready()
    if name not in _frames:
        if name not in set(_coverage()["table"]):
            raise ToolError(f"no table named {name!r}; call list_tables for the table names")
        try:
            _frames[name] = erw.fetch(name)
        except erw.ERWDataNotFound as exc:
            raise ToolError(f"table {name!r} cannot be read from this backend: {exc}")
    return _frames[name]


def _shape(df):
    if list(df.columns[:2]) == ["entity_id", "entity_type"]:
        return "entities"
    if "event_id" in df.columns:
        return "events"
    return "series"


def _cov_row(name):
    c = _coverage().set_index("table")
    return c.loc[name] if name in c.index else None


def data_version(name):
    """What was read: the backend, its data version, and the table's last run."""
    v = erw.version()
    row = _cov_row(name)
    last = row["last_run"] if row is not None else None
    last_s = last.strftime("%Y-%m-%dT%H:%M:%SZ") if isinstance(last, pd.Timestamp) and not pd.isna(last) else None
    ident = v.get("data_commit") or v.get("version") or v.get("note")
    return (f"{v.get('backend')} backend"
            + (f", data commit {str(ident)[:12]}" if v.get("data_commit") else (f", {ident}" if ident else ""))
            + (f"; table last run {last_s}" if last_s else ""))


def provenance(name):
    """The fields every result carries."""
    row = _cov_row(name)
    if name not in _cites:
        try:
            _cites[name] = erw.cite(name)
        except Exception as exc:  # a citation failure must not hide the data, but it is reported
            _cites[name] = f"citation unavailable: {type(exc).__name__}: {exc}"
    return {"table": name,
            "data_version": data_version(name),
            "source_report": None if row is None else row["source_report"],
            "license": None if row is None else row["license"],
            # session 28: source, derived or model_extracted (docs/datastandard.md)
            "tier": None if row is None or "tier" not in row.index else (row["tier"] or None),
            "citation": _cites[name]}


def _num(x):
    if x is None:
        return None
    if isinstance(x, (np.integer, int)):
        return int(x)
    x = float(x)
    if math.isnan(x):
        return None
    return round(x, DIGITS)


def _ts(t):
    if t is None or pd.isna(t):
        return None
    t = pd.Timestamp(t)
    return t.strftime("%Y-%m-%dT%H:%M:%SZ") if t.tzinfo is not None else t.strftime("%Y-%m-%d")


# ---------------------------------------------------------------- list_tables

def list_tables(sector=None, license=None, iso=None):
    cov = _coverage()
    keep = pd.Series(True, index=cov.index)
    if sector:
        keep &= cov["sector"].map(lambda v: sector in str(v).split(";"))
    if license:
        keep &= cov["license"] == license
    if iso:
        keep &= cov["iso"].str.upper() == iso.upper()
    rows = []
    for r in cov[keep].itertuples():
        rows.append({"table": r.table, "sector": r.sector.replace(";", ", ") if r.sector else "",
                     "license": r.license, "iso": r.iso, "interval": r.interval,
                     "first": _ts(r.ts_min), "last": _ts(r.ts_max), "rows": int(r.n_rows),
                     "source_report": r.source_report, "derived": r.derived,
                     "tier": getattr(r, "tier", None)})
    v = erw.version()
    return {"n_tables": len(rows), "tables": rows,
            "backend": v.get("backend"),
            "note": ("Only public tables may be shown publicly; internal tables are licensed for "
                     "internal use only. first and last are interval starts, UTC.")}


# ------------------------------------------------------------- describe_table

def describe_table(table):
    df = _table(table)
    shape = _shape(df)
    meta = df.attrs.get("erw", {})
    out = {"shape": shape, "rows": len(df), "columns": list(df.columns)}
    try:
        src = erw.sources(table)
        out["source_reports"] = [{"source": r["source"], "publisher": r.get("publisher"), "report": r.get("report"),
                                  "report_url": r.get("report_url")} for r in src["reports"]][:20]
    except Exception as exc:
        out["source_reports"] = f"unavailable: {type(exc).__name__}"
    if shape == "series":
        ents = sorted(df["entity"].unique())
        out.update({
            "entities": ents[:MAX_LIST], "n_entities": len(ents),
            "nodes": sorted(x for x in df["node"].unique() if x)[:MAX_LIST] if "node" in df else [],
            "variables": sorted(df["variable"].unique())[:MAX_LIST],
            "units": sorted(df["unit"].unique()),
            "freq": sorted(df["freq"].unique()),
            "first": _ts(df["ts_utc"].min()), "last": _ts(df["ts_utc"].max()),
        })
        if len(ents) > MAX_LIST:
            out["entities_note"] = f"{len(ents)} entities; the first {MAX_LIST} are listed"
    else:
        tcol = "status_date" if shape == "entities" else "event_date"
        text_cols = {}
        for c in df.columns:
            if c in ("entity_id", "event_id", "name", "source_url", "headline", "retrieved_at", "lat", "lon"):
                continue
            s = df[c]
            if s.dtype == object:
                vc = s[s != ""].value_counts()
                if 1 <= len(vc) <= 60:
                    text_cols[c] = {str(k): int(v) for k, v in vc.items()}
        numeric = [c for c in df.columns if pd.api.types.is_numeric_dtype(df[c])]
        out.update({"text_column_values": text_cols, "numeric_columns": numeric,
                    "first": _ts(df[tcol].min()) if tcol in df else None,
                    "last": _ts(df[tcol].max()) if tcol in df else None,
                    "time_column": tcol if tcol in df else None})
    out["notes"] = [str(n) for n in (meta.get("notes") or [])][:5]
    out.update(provenance(table))
    return out


# ---------------------------------------------------------------------- query

def _select(df, shape, entity, variable, start, end, where, tz="UTC"):
    keep = pd.Series(True, index=df.index)
    if entity:
        if shape == "series":
            keep &= (df["entity"] == entity) | (df["node"] == entity if "node" in df else False)
        elif shape == "entities":
            keep &= (df["entity_id"] == entity) | (df["name"] == entity)
        else:
            keep &= df["source"] == entity
    if variable:
        if shape != "series":
            raise ToolError("variable applies to series tables only; use where for entities and events tables")
        keep &= df["variable"] == variable
    tcol = {"series": "ts_utc", "events": "event_date", "entities": "status_date"}[shape]
    if start or end:
        if tcol not in df:
            raise ToolError(f"this table has no time column ({tcol}) for start and end")
        t = df[tcol]
        if shape == "entities":
            t = t.dt.tz_localize("UTC")
        # session 20: a series row of a day or longer (freq P1D, P1W, P1M, P1Y) is labelled with its
        # local date at 00:00Z (Decision 11), so a date bound is that label, whatever tz says. Reading
        # it in tz shifted the window by the UTC offset and returned the next day's row (the
        # evaluation's trader-view questions s20q10 and s20q12)
        dated = shape == "series" and "freq" in df and df.loc[keep, "freq"].isin(["P1D", "P1W", "P1M", "P1Y"]).all()             and bool(keep.any())
        for bound, op in ((start, "ge"), (end, "lt")):
            if bound:
                try:
                    b = pd.Timestamp(bound)
                except ValueError:
                    raise ToolError(f"cannot read the time {bound!r}; use ISO 8601")
                # session 13: a bound without Z or an offset is read in tz (it was always read as
                # UTC, although tz was described as setting day boundaries: local-day questions
                # got the UTC day)
                try:
                    b = (b.tz_localize("UTC" if dated else tz, ambiguous=False, nonexistent="shift_forward")
                         if b.tzinfo is None else b).tz_convert("UTC")
                except Exception:
                    raise ToolError(f"unknown time zone {tz!r}; use an IANA name such as America/Chicago")
                keep &= (t >= b) if op == "ge" else (t < b)
    for col, val in (where or {}).items():
        if col not in df.columns:
            raise ToolError(f"no column {col!r} in this table; columns: {', '.join(df.columns)}")
        vals = val if isinstance(val, list) else [val]
        keep &= df[col].astype(str).isin([str(v) for v in vals])
    return df[keep], tcol


def _group_keys(sel, shape, tcol, group_by, tz):
    if group_by is None:
        return None
    if group_by in TIME_GROUPS:
        if tcol not in sel:
            raise ToolError(f"no time column to group by {group_by}")
        t = sel[tcol]
        if shape == "entities":
            t = t.dt.tz_localize("UTC")
        try:
            t = t.dt.tz_convert(tz)
        except Exception:
            raise ToolError(f"unknown time zone {tz!r}; use an IANA name such as America/Chicago")
        fmt = {"year": "%Y", "month": "%Y-%m", "day": "%Y-%m-%d", "hour": "%Y-%m-%d %H:00"}[group_by]
        return t.dt.strftime(fmt)
    if group_by == "entity":
        return sel["entity"] if shape == "series" else sel["entity_id" if shape == "entities" else "source"]
    if group_by in sel.columns and sel[group_by].dtype == object:
        return sel[group_by]
    raise ToolError(f"group_by must be one of {TIME_GROUPS + ['entity']} or a text column of the table")


def _aggregate(g, agg, vcol, tcol, pct, shape):
    """One group's result: a dict."""
    if agg == "count":
        return {"count": int(len(g))}
    if len(g) == 0:
        return {"value": None, "n": 0}
    v = g[vcol]
    if agg == "latest":
        if tcol not in g:
            raise ToolError("latest needs a time column")
        r = g.loc[g[tcol].idxmax()]
        out = {"value": _num(r[vcol]), "at": _ts(r[tcol])}
        if shape == "series":
            out.update({"entity": r["entity"], "variable": r["variable"], "unit": r["unit"]})
        return out
    v = v.dropna()
    if len(v) == 0:
        return {"value": None, "n": 0}
    if agg in ("min", "max"):
        i = v.idxmin() if agg == "min" else v.idxmax()
        out = {"value": _num(v.loc[i]), "n": int(len(v))}
        if tcol in g:
            out["at"] = _ts(g.loc[i, tcol])
        if shape == "series":
            out["entity"] = g.loc[i, "entity"]
        elif shape == "entities":
            out["entity_id"] = g.loc[i, "entity_id"]
        return out
    if agg == "percentile":
        if pct is None or not 0 <= float(pct) <= 100:
            raise ToolError("percentile needs a percentile value from 0 to 100")
        return {"value": _num(np.percentile(v.to_numpy(dtype=float), float(pct))), "n": int(len(v))}
    fn = {"mean": np.mean, "median": np.median, "sum": np.sum}[agg]
    return {"value": _num(fn(v.to_numpy(dtype=float))), "n": int(len(v))}


def query(table, aggregation, entity=None, variable=None, start=None, end=None, where=None,
          percentile=None, value_column=None, group_by=None, tz="UTC"):
    if aggregation not in AGGREGATIONS:
        raise ToolError(f"aggregation must be one of {AGGREGATIONS}")
    df = _table(table)
    shape = _shape(df)
    sel, tcol = _select(df, shape, entity, variable, start, end, where, tz or "UTC")
    vcol = value_column or {"series": "value", "entities": "capacity_mw", "events": "mw"}[shape]
    if aggregation not in ("count",) and vcol not in df.columns:
        raise ToolError(f"no column {vcol!r}; numeric columns: "
                        f"{[c for c in df.columns if pd.api.types.is_numeric_dtype(df[c])]}")
    if aggregation not in ("count", "latest") and not pd.api.types.is_numeric_dtype(df[vcol]):
        # session 20: an events or entities column of numbers with blanks ("not stated"), such as
        # energy_deals.dollars, arrives as text; it is numeric when every non-blank value is a
        # number (the evaluation's s20q14 was refused with "not numeric")
        txt = df[vcol].astype(str).str.strip()
        num = pd.to_numeric(txt.where(txt != ""), errors="coerce")
        if num[txt != ""].isna().any():
            raise ToolError(f"column {vcol!r} is not numeric")
        df = df.assign(**{vcol: num})
        sel = sel.assign(**{vcol: num.loc[sel.index]})
    out = {"aggregation": aggregation, "value_column": None if aggregation == "count" else vcol,
           "filters": {k: v for k, v in dict(entity=entity, variable=variable, start=start, end=end,
                                              where=where, percentile=percentile, tz=tz if (group_by in TIME_GROUPS or start or end) and tz != "UTC" else None).items() if v},
           "rows_matched": int(len(sel))}
    if shape == "series" and len(sel):
        out["units"] = sorted(sel["unit"].unique())
        out["variables"] = sorted(sel["variable"].unique())[:10]
        out["time_span"] = {"first": _ts(sel["ts_utc"].min()), "last": _ts(sel["ts_utc"].max())}
        if len(out["variables"]) > 1 and aggregation not in ("count", "latest"):
            out["warning"] = ("more than one variable matched: the aggregation mixes them; filter by variable")
    if len(sel) == 0:
        out["result"] = []
        out["note"] = "no rows match these filters"
    else:
        keys = _group_keys(sel, shape, tcol, group_by, tz)
        if keys is None:
            if aggregation == "latest" and shape == "series" and sel.groupby(["entity", "variable"]).ngroups > 1:
                res = []
                for (e, v_), g in sel.groupby(["entity", "variable"]):
                    res.append(_aggregate(g, "latest", vcol, tcol, percentile, shape))
                out["result"] = res[:MAX_GROUPS]
                if len(res) > MAX_GROUPS:
                    out["result_note"] = f"{len(res)} entity and variable pairs; the first {MAX_GROUPS} are shown"
            else:
                out["result"] = [_aggregate(sel, aggregation, vcol, tcol, percentile, shape)]
        else:
            res = []
            for k, g in sel.groupby(keys, sort=True):
                res.append({group_by: k, **_aggregate(g, aggregation, vcol, tcol, percentile, shape)})
            out["n_groups"] = len(res)
            if len(res) > MAX_GROUPS:
                out["result_note"] = f"{len(res)} groups; the first {MAX_GROUPS} (sorted by {group_by}) are shown"
            out["result"] = res[:MAX_GROUPS]
    out.update(provenance(table))
    return out


def compare(a, b):
    ra, rb = query(**a), query(**b)
    out = {"a": ra, "b": rb}
    va = ra["result"][0].get("value") if len(ra.get("result", [])) == 1 else None
    vb = rb["result"][0].get("value") if len(rb.get("result", [])) == 1 else None
    if va is None and len(ra.get("result", [])) == 1:
        va = ra["result"][0].get("count")
    if vb is None and len(rb.get("result", [])) == 1:
        vb = rb["result"][0].get("count")
    if isinstance(va, (int, float)) and isinstance(vb, (int, float)):
        out["difference_b_minus_a"] = _num(vb - va)
        out["ratio_b_over_a"] = _num(vb / va) if va else None
    return out


FUNCTIONS = {"list_tables": list_tables, "describe_table": describe_table, "query": query, "compare": compare}


def run(name, args):
    """Run one tool. Returns (result dict, is_error)."""
    if name not in FUNCTIONS:
        return {"error": f"unknown tool {name!r}"}, True
    try:
        return FUNCTIONS[name](**(args or {})), False
    except ToolError as exc:
        return {"error": str(exc)}, True
    except TypeError as exc:
        return {"error": f"bad arguments: {exc}"}, True


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print(__doc__)
        sys.exit(2)
    res, err = run(sys.argv[1], json.loads(sys.argv[2]) if len(sys.argv) > 2 else {})
    print(json.dumps(res, indent=2, default=str))
    sys.exit(1 if err else 0)

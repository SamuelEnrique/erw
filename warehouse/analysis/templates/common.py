"""Shared pieces of the Automated Analysis templates (platform tool 26, session 23).

A template is a module in this folder with:

    NAME, TITLE, PUBLIC       its id, its chart title, and whether its tables are all public (an internal
                              template never leaves the machine: no docs/analysis file, no gallery entry,
                              never the chart of the week)
    METHOD                    the method, in plain words (shown on /analysis and in docs/analysis/templates.json)
    PARAMS                    {name: {"default": ..., "choices": [...] or {other_param_value: [...]}}}
    TABLES                    the ERW tables it reads
    compute(history=True, **params) -> result dict (below)
    render(result, size)      size "site" returns the ECharts option; "email", "social_wide" and
                              "social_square" write a PNG and return its path (render(result, size, path))

A result is a plain dict:
    template, params, title, subtitle, frame (a tidy pandas frame, one row per plotted value, with the
    table each value came from), tables, citations (erw.cite for each table), source_line,
    chart (the chart spec for style.py), headline {label, value, unit, period, history: [[period, value]]}
    and facts (sentences holding every number the note may use, for the literal-number check).
"""

import os
import sys

import pandas as pd

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.abspath(os.path.join(HERE, "..", "..", ".."))
sys.path.insert(0, os.path.join(ROOT, "package", "src"))
sys.path.insert(0, os.path.join(HERE, ".."))
import erw  # noqa: E402
import style  # noqa: E402

RT = {"ercot": ("ercot_rtm_hub_prices", "America/Chicago", "HB_NORTH"),
      "caiso": ("caiso_rtm_hub_prices", "America/Los_Angeles", "TH_SP15_GEN-APND"),
      "nyiso": ("nyiso_rtm_zone_prices", "America/New_York", "N.Y.C."),
      "miso": ("miso_rtm_hub_prices", "EST", "INDIANA.HUB"),
      "spp": ("spp_rtm_hub_prices", "America/Chicago", "SPPSOUTH_HUB"),
      "isone": ("isone_rtm_zone_prices", "America/New_York", ".H.INTERNAL_HUB")}
DA = {"ercot": "ercot_dam_hub_prices", "caiso": "caiso_dam_hub_prices", "nyiso": "nyiso_dam_zone_prices",
      "miso": "miso_dam_hub_prices", "spp": "spp_dam_hub_prices", "isone": "isone_dam_zone_prices"}
ISO_LABEL = {"ercot": "ERCOT", "caiso": "CAISO", "nyiso": "NYISO", "miso": "MISO", "spp": "SPP", "isone": "ISO-NE"}


class NoData(RuntimeError):
    """The template's inputs are not in the warehouse (on this machine), or too short for the window."""


_CACHE = {}


def fetch(table, node=None):
    """A whole table through the erw package, read once per process (the engine runs every template and a grid
    of parameters over the same tables), then filtered to a node."""
    if table not in _CACHE:
        try:
            _CACHE[table] = erw.fetch(table)
        except Exception as exc:
            raise NoData(f"{table}: {exc}") from exc
    df = _CACHE[table]
    if node is not None:
        df = df[df["node"] == node]
    if df is None or len(df) == 0:
        raise NoData(f"{table}: no rows" + (f" for {node}" if node else ""))
    return df


def nodes(table):
    """The nodes of a price table (for a parameter's choices)."""
    try:
        return sorted(erw.fetch(table)["node"].dropna().unique().tolist())
    except Exception:
        return []


def publishers(tables):
    out = []
    for t in tables:
        try:
            for r in erw.sources(t)["reports"]:
                p = r.get("publisher", "")
                p = p.split(" (")[1].rstrip(")") if " (" in p and len(p.split(" (")[1]) < 12 else p
                if p and p not in out:
                    out.append(p)
        except Exception:
            pass
    return out


def source_line(tables, extra=""):
    pubs = publishers(tables)
    retrieved = []
    for t in tables:
        try:
            r = erw.sources(t).get("retrieved", "")
            if r:
                retrieved.append(r[:8])
        except Exception:
            pass
    when = f"; data retrieved to {max(retrieved)[:4]}-{max(retrieved)[4:6]}-{max(retrieved)[6:8]}" if retrieved else ""
    return (f"Source: {', '.join(pubs) or 'ERW'} via the Energy Research Warehouse (ERW), "
            f"table{'s' if len(tables) > 1 else ''} {', '.join(tables)}{when}.{(' ' + extra) if extra else ''}")


def citations(tables):
    out = []
    for t in tables:
        try:
            out.append(erw.cite(t))
        except Exception as exc:
            out.append(f"{t}: citation unavailable ({exc})")
    return out


def complete_local_days(df, tz, per_day_expected=None):
    """The local dates whose rows are complete: every interval of the local day is present. per_day_expected
    maps a date to the count expected (default: from the table's frequency and the day's length)."""
    loc = df["ts_utc"].dt.tz_convert(tz)
    d = df.assign(day=loc.dt.date)
    counts = d.groupby("day")["ts_utc"].nunique()
    step = df.sort_values("ts_utc")["ts_utc"].diff().dropna().mode()
    step = step.iloc[0] if len(step) else pd.Timedelta(hours=1)
    ok = []
    for day, n in counts.items():
        s = pd.Timestamp(day).tz_localize(tz)
        e = pd.Timestamp(day + pd.Timedelta(days=1)).tz_localize(tz)
        if n == int((e - s) / step):
            ok.append(day)
    return sorted(ok)


def weeks_back(days, n_days=7):
    """Non-overlapping n-day windows ending at the last complete day, newest last: [(first, last), ...]."""
    days = sorted(days)
    out = []
    i = len(days)
    while i - n_days >= 0:
        chunk = days[i - n_days:i]
        if (pd.Timestamp(chunk[-1]) - pd.Timestamp(chunk[0])).days == n_days - 1:
            out.append((chunk[0], chunk[-1]))
        i -= n_days
    return out[::-1]


def result(template, params, title, subtitle, frame, tables, chart, headline, facts, extra_source=""):
    src = source_line(tables, extra_source)
    chart = dict(chart, title=title, subtitle=subtitle, source=src, name=template)
    return {"template": template, "params": params, "title": title, "subtitle": subtitle, "frame": frame,
            "tables": tables, "citations": citations(tables), "source_line": src, "chart": chart,
            "headline": headline, "facts": facts}


def render(res, size, path=None):
    if size == "site":
        return style.echarts(res["chart"])
    return style.png(res["chart"], path, size)


def r2(v):
    return None if v is None or pd.isna(v) else round(float(v), 2)

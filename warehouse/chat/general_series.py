"""Session 1317 (chain 096): the general chat's chart, for the Python loop, as site/lib/chat/generalseries.ts (session
1142) with site/lib/chat/series.ts (chartPoints, pointsAreRows, keySeconds).

Energy Research Warehouse (ERW). An answer of the general chat that rests on a series carries it: the last query
result grouped by time (year, month, day or hour) of a table the answer cites, with at least three rows, its rows the
tool's own, key by key and value by value, every row either a point or named as not drawn, and at least two points to
join. An answer that cites no such result carries none. Pure: no request.
"""
import calendar
import math
import re

TIME_GROUPS = ["year", "month", "day", "hour"]
MIN_ROWS = 3
HOUR_GROUP = "hour_of_day"
KEY = re.compile(r"^(\d{4})(?:-(\d{2}))?(?:-(\d{2}))?(?: (\d{2}):00)?$")


def key_seconds(key):
    """A group key as the tools write it ("2021", "2021-03", "2021-03-05", "2021-03-05 14:00") to UTC seconds."""
    m = KEY.match(key)
    if not m:
        return None
    y, mo, d, h = int(m.group(1)), int(m.group(2) or 1), int(m.group(3) or 1), int(m.group(4) or 0)
    return calendar.timegm((y, mo, d, h, 0, 0))


def key_at(key, group=None):
    if group == HOUR_GROUP:
        return int(key) if re.fullmatch(r"[01]\d|2[0-3]", key) else None
    return key_seconds(key)


def _finite(v):
    return isinstance(v, (int, float)) and not isinstance(v, bool) and math.isfinite(v)


def chart_points(rows, group=None):
    points, undrawn = [], []
    for r in rows:
        t = key_at(r["key"], group)
        if not _finite(r.get("value")):
            undrawn.append({"key": r["key"], "why": "no value"})
        elif t is None:
            undrawn.append({"key": r["key"], "why": "not a time"})
        else:
            points.append({"t": t, "v": r["value"]})
    return {"points": points, "undrawn": undrawn}


def points_are_rows(rows, drawn, group=None):
    if len(drawn["points"]) + len(drawn["undrawn"]) != len(rows):
        return False
    left = {u["key"] for u in drawn["undrawn"]}
    i = 0
    for r in rows:
        if r["key"] in left:
            continue
        if i >= len(drawn["points"]):
            return False
        p = drawn["points"][i]
        i += 1
        if p["t"] != key_at(r["key"], group) or p["v"] != r["value"]:
            return False
    return i == len(drawn["points"])


def series_of_result(n, args, out):
    """One query result as a series, or None when it is not one a line can show."""
    g = args.get("group_by") if isinstance(args.get("group_by"), str) else ""
    result = out.get("result")
    if g not in TIME_GROUPS or not isinstance(result, list) or len(result) < MIN_ROWS or not isinstance(out.get("table"), str):
        return None
    rows = []
    for r in result:
        v = r.get("value") if _finite(r.get("value")) else r.get("count") if _finite(r.get("count")) else None
        row = {"key": str(r.get(g)), "value": v}
        if _finite(r.get("n")):
            row["n"] = r["n"]
        if isinstance(r.get("at"), str):
            row["at"] = r["at"]
        rows.append(row)
    drawn = chart_points(rows, g)
    what = "count of rows" if args.get("aggregation") == "count" else f"{args.get('aggregation')} of {args.get('variable') or out.get('value_column') or 'value'}"
    units = out.get("units") or []
    return {"result_id": f"q{n}", "table": out["table"], "title": what + (f", {args['entity']}" if args.get("entity") else "") + f", by {g}",
            "group_by": g, "kind": "line", "unit": units[0] if len(units) == 1 else None, "rows": rows,
            "rows_matched": out.get("rows_matched") if isinstance(out.get("rows_matched"), int) else None,
            "note": out.get("result_note") if isinstance(out.get("result_note"), str) else None,
            "source_report": out.get("source_report") if isinstance(out.get("source_report"), str) else None,
            "license": out.get("license") if isinstance(out.get("license"), str) else None,
            "tier": out.get("tier") if isinstance(out.get("tier"), str) else None,
            "chosen_by": "the last result grouped by time of a table the answer cites",
            "check": {"rows_fetched": len(result), "rows": len(rows), "same": len(rows) == len(result) and points_are_rows(rows, drawn, g),
                      "points": len(drawn["points"]), "not_drawn": len(drawn["undrawn"])}}


def answer_series(results, cited):
    """The series an answer rests on: the last one of a cited table, or none. `results`: the loop's query and compare
    calls that answered, each {"tool", "input", "out"}, in order."""
    want = set(cited)
    found = []
    for i, r in enumerate(results):
        if r["tool"] == "query":
            s = series_of_result(i + 1, r["input"] or {}, r["out"] or {})
            if s:
                found.append(s)
        elif r["tool"] == "compare":
            for k in ("a", "b"):
                s = series_of_result(i + 1, (r["input"] or {}).get(k) or {}, (r["out"] or {}).get(k) or {})
                if s:
                    found.append({**s, "result_id": f"q{i + 1}{k}"})
    found = [s for s in found if s["table"] in want and s["check"]["same"] and s["check"]["points"] >= 2]
    return found[-1:]

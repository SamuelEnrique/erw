#!/usr/bin/env python3
"""Every figure of the Energy Roundup's numbers section, traced to the warehouse table it names (session 498).

Energy Research Warehouse (ERW). The Roundup (docs/roundup/<year>-W<week>.md, written by warehouse/news/roundup.py)
prints the week's numbers as markdown with a footnote a table. Until session 498 nothing recomputed them after they were
written (scripts/check-values.mjs reads the day-ahead means of the latest /roundup only). This script parses each
Roundup's numbers section and recomputes, by roundup.py's own rules:

    rdp_dam      a main hub's day-ahead mean over the ISO's local week (the local midnights of the UTC week's dates),
                 every hour held, exact and rounded half up to cents (brief.mean2), this week and the week before
    rdp_change   the printed change equals the difference of the two printed means
    rdp_rt       the highest real-time price at its stated interval, node and table (that it is the week's highest
                 over every real-time table is not recomputed: a full week of every table)
    rdp_fuel     an EIA spot close on its trading date, both closes of a row, and the row's change and percent
    rdp_us48     the US48 peak demand at its stated hour (eia930_all_demand, demand_mw), to the whole MW

A cell that says "not in the warehouse" states a gap at the time of writing; it is listed, not checked. The chart of
the week is a finding card or a chart record, each checked where it is made (scripts/check-values.mjs, the card's
replication). The deals and datacenter tables print story rows, traced to their story, not to a table of prices.

    python scripts/check_roundup.py                       # the local CSVs (warehouse/output), read only
    python scripts/check_roundup.py --in-dir DIR          # the CSVs of another copy
    python scripts/check_roundup.py --supabase            # the live set (anon key; ISO prices held 35 days)
    python scripts/check_roundup.py --supabase --then-csv # the live set, then the CSVs for what it does not hold
    python scripts/check_roundup.py --week 2026-W41       # only these Roundups (repeat)

Each figure is one line: ok, FAIL, "revised" (a single row that differs and was retrieved after the issue was written,
from the comment roundup.py leaves at the foot: the publisher's revision, both values said), "not here" (the source
does not hold the period) or "gap" (a stated gap). Exit 1 when any figure fails or none could be checked; 0 otherwise.
Writes nothing.
"""
import argparse
import os
import re
import sys
from datetime import date, datetime, timedelta, timezone
from decimal import Decimal
from zoneinfo import ZoneInfo

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import check_digest as cd  # noqa: E402  (the sources, mean2, current(), the hubs' zones and prefixes)

ROUNDUP = os.path.join(cd.ROOT, "docs", "roundup")
ISO_RT = {"ERCOT": "ercot", "CAISO": "caiso", "NYISO": "nyiso", "MISO": "miso", "SPP": "spp", "ISO-NE": "isone"}
FUEL_ENTITY = {"Henry Hub natural gas": "eia:henry_hub", "WTI Cushing crude": "eia:wti_cushing", "Brent crude": "eia:brent"}

SECTION = re.compile(r"^## (?:ERW's )?Numbers (?:of the week|This Week)\s*$", re.M)
NOTE = re.compile(r"\[(\d+)\] `([a-z0-9_]+)`")
DAM = re.compile(r"^\| (ERCOT|CAISO|NYISO|MISO|SPP|ISO-NE) \| (\S+) \| ([^|]+?) \| ([^|]+?) \| ([^|]+?) \| \[(\d+)\] \|", re.M)
PRICE = re.compile(r"^-?\d+\.\d{2}$")
RT = re.compile(r"\*\*Highest real-time price of the week:\*\* (-?[\d.]+) USD/MWh at (\S+) \(([A-Z-]+)\), interval starting "
                r"[^(]+\((\d{4}-\d\d-\d\d \d\d:\d\d) UTC\), (\w+) \[(\d+)\]")
FUEL = re.compile(r"^\| (Henry Hub natural gas|WTI Cushing crude|Brent crude) \| (-?[\d.]+) \S+ on (\d{4}-\d\d-\d\d) \| "
                  r"(-?[\d.]+) on (\d{4}-\d\d-\d\d) \| ([+-][\d.]+) \(([+-][\d.]+)%\)", re.M)
US48 = re.compile(r"\*\*US48 peak demand of the week:\*\* ([\d,]+) MW in the hour starting (\d{4}-\d\d-\d\d \d\d:\d\d) UTC")
# session 806: the week in five numbers, each line its own form
FIVE = re.compile(r"^## The week in five numbers\s*$", re.M)
FIVE_DAM = re.compile(r"\*\*Price move of the week:\*\* (ERCOT|CAISO|NYISO|MISO|SPP|ISO-NE) (\S+) day-ahead averaged (-?[\d.]+) USD/MWh over the week, "
                      r"against (-?[\d.]+) USD/MWh the week before \(([+-][\d.]+) USD/MWh, ([+-][\d.]+)%\) \[(\d+)\]")
FIVE_FUEL = re.compile(r"\*\*Price move of the week:\*\* (Henry Hub natural gas|WTI Cushing crude|Brent crude) closed at (-?[\d.]+) \S+ on "
                       r"(\d{4}-\d\d-\d\d), against (-?[\d.]+) \S+ on (\d{4}-\d\d-\d\d) \(([+-][\d.]+) \S+, ([+-][\d.]+)%\) \[(\d+)\]")
FIVE_US48 = re.compile(r"\*\*US48 peak demand:\*\* ([\d,]+) MW in the hour starting (\d{4}-\d\d-\d\d \d\d:\d\d) UTC")
FIVE_DEAL = re.compile(r"\*\*Deal of the week, by US dollars:\*\* (USD [\d,.]+(?: \w+)?), .*?`energy_deals` (deal:[0-9a-f]+)\)")
FIVE_DEAL_MW = re.compile(r"\*\*Deal of the week, by MW[^*]*:\*\* ([\d,]+) MW, .*?`energy_deals` (deal:[0-9a-f]+)\)")
FIVE_LOAD = re.compile(r"\*\*Largest new datacenter load first reported this week:\*\* ([\d,]+) MW, .*?`datacenter_projects` (\S+?)\)")
FIVE_CHART = re.compile(r"\*\*From the chart of the week:\*\* (.+?): ([\d,.]+) (.+?) in (.+?) \(template `([a-z0-9_]+)`, `(docs/analysis/[^`]+)`\)")


def usd_words(d):
    """As roundup.usd_words writes a sum: 'USD 12 billion', 'USD 4.3 billion', 'USD 834 million', 'USD 250,000'."""
    from decimal import Decimal, ROUND_HALF_UP
    v = float(d)
    for scale, word in ((1e12, "trillion"), (1e9, "billion"), (1e6, "million")):
        if abs(v) >= scale:
            x = (Decimal(repr(v)) / Decimal(int(scale))).quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)
            s = f"{x:.2f}".rstrip("0").rstrip(".")
            return f"USD {s} {word}"
    return f"USD {v:,.0f}"


def chart_figure(v):
    v = float(v)
    if v == int(v):
        return f"{int(v):,}"
    return f"{v:,.0f}" if abs(v) >= 100 else f"{v:,.2f}"


def event_row(src, table, event_id, id_col="event_id"):
    """A row of an events table by its id, from the CSVs (the live set holds the series store only): (status, row)."""
    if not isinstance(src, cd.Csv):
        return "not here", f"{table} is an events table, not in {src.name}"
    path = os.path.join(src.dir, f"{table}.csv")
    if not os.path.exists(path):
        return "not here", f"{table} is not held by {src.name}"
    import pandas as pd
    df = pd.read_csv(path, skiprows=cd.header_rows(path), dtype=str, keep_default_na=False)
    got = df[df[id_col] == event_id]
    if got.empty:
        return "not here", f"no row {event_id} in {table}"
    return "held", got.iloc[0]


def five_section(md):
    m = FIVE.search(md)
    if not m:
        return None
    rest = md[m.end():]
    nxt = re.search(r"^## ", rest, re.M)
    return rest[: nxt.start()] if nxt else rest


def five_checks(label, md, refs, written):
    """The checks of the week in five numbers (session 806)."""
    text = five_section(md)
    if text is None:
        return []
    monday = week_start(label)
    out = []
    m = FIVE_DAM.search(text)
    if m:
        iso, node, this, before, chg, pct, ref = m.groups()
        table = refs.get(ref)
        for which, cell, start in (("week", this, monday), ("week before", before, monday - timedelta(days=7))):
            def f(src, table=table, iso=iso, node=node, start=start, cell=cell):
                st, got = dam_mean(src, table, iso, node, start)
                return (("ok" if got == cell else "FAIL"), got) if st == "held" else (st, got)
            out.append((f"rdp_five_dam|{iso}|{table}|{node}|{which}", cell, f))
        a, b = float(this), float(before)
        want = f"{a - b:+.2f}, {100 * (a / b - 1):+.1f}%" if b > 0 else "no percent"
        out.append((f"rdp_five_change|{iso}|{node}", f"{chg}, {pct}%", lambda src, w=want, c=f"{chg}, {pct}%": (("ok" if w == c else "FAIL"), w)))
    m = FIVE_FUEL.search(text)
    if m:
        name, v1, d1, v0, d0, chg, pct, ref = m.groups()
        entity = FUEL_ENTITY[name]
        for v, d in ((v1, d1), (v0, d0)):
            def f(src, entity=entity, v=v, d=d):
                st, got = value_at(src, "eia_fuel_spot_prices", entity, f"{d}T00:00:00Z")
                return compare(src, v, f"{got:.2f}", written, "eia_fuel_spot_prices", entity, f"{d}T00:00:00Z") if st == "held" else (st, got)
            out.append((f"rdp_five_fuel|eia_fuel_spot_prices|{entity}|{d}", v, f))
    m = FIVE_US48.search(text)
    if m:
        v, ts = m.groups()
        t = datetime.strptime(ts, "%Y-%m-%d %H:%M").strftime("%Y-%m-%dT%H:%M:00Z")

        def f(src, t=t, v=v):
            st, got = value_at(src, "eia930_all_demand", "eia930:US48", t, "demand_mw")
            return compare(src, v, f"{got:,.0f}", written, "eia930_all_demand", "eia930:US48", t, "demand_mw") if st == "held" else (st, got)
        out.append((f"rdp_five_us48|eia930_all_demand|eia930:US48|demand_mw|{t}", v, f))
    m = FIVE_DEAL.search(text)
    if m:
        v, eid = m.groups()

        def f(src, v=v, eid=eid):
            st, row = event_row(src, "energy_deals", eid)
            if st != "held":
                return st, row
            got = usd_words(row["dollars"]) if row["dollars"] else "no dollars in the row"
            return ("ok" if got == v else "FAIL"), got
        out.append((f"rdp_five_deal|energy_deals|{eid}|dollars", v, f))
    m = FIVE_DEAL_MW.search(text)
    if m:
        v, eid = m.groups()

        def f(src, v=v, eid=eid):
            st, row = event_row(src, "energy_deals", eid)
            if st != "held":
                return st, row
            got = f"{float(row['mw']):,.0f}" if row["mw"] else "no mw in the row"
            return ("ok" if got == v else "FAIL"), got
        out.append((f"rdp_five_deal|energy_deals|{eid}|mw", v, f))
    m = FIVE_LOAD.search(text)
    if m:
        v, eid = m.groups()

        def f(src, v=v, eid=eid):
            st, row = event_row(src, "datacenter_projects", eid, "entity_id")
            if st != "held":
                return st, row
            mw = row["capacity_mw"] if "capacity_mw" in row.index else row.get("mw", "")
            got = f"{float(mw):,.0f}" if mw else "no capacity in the row"
            return ("ok" if got == v else "FAIL"), got
        out.append((f"rdp_five_load|datacenter_projects|{eid}|capacity_mw", v, f))
    m = FIVE_CHART.search(text)
    if m:
        _label, v, unit, period, template, path = m.groups()

        def f(src, v=v, path=path, template=template):
            import json
            p = os.path.join(cd.ROOT, path)
            if not os.path.exists(p):
                return "not here", f"{path} is not in this checkout"
            d = json.load(open(p, encoding="utf-8"))
            if d.get("template") != template:
                return "FAIL", f"the week's chart is {d.get('template')}"
            got = chart_figure(d["headline"]["value"])
            return ("ok" if got == v else "FAIL"), got
        out.append((f"rdp_five_chart|{label}|{template}|headline", v, f))
    return out


def week_start(label):
    """The UTC Monday of an ISO week label (roundup.week_bounds)."""
    y, w = label.split("-W")
    return date.fromisocalendar(int(y), int(w), 1)


def local_week(monday, tz):
    """(start, end, hours) of the ISO's local week with the UTC week's dates (roundup.local_week)."""
    z = ZoneInfo(tz)
    s = datetime(monday.year, monday.month, monday.day, tzinfo=z)
    e_day = monday + timedelta(days=7)
    e = datetime(e_day.year, e_day.month, e_day.day, tzinfo=z)
    hours = int(round((e.astimezone(timezone.utc) - s.astimezone(timezone.utc)).total_seconds() / 3600))
    return s, e, hours


def section(md):
    """The numbers section's text, or None (a Roundup before the section existed)."""
    m = SECTION.search(md)
    if not m:
        return None
    rest = md[m.end():]
    nxt = re.search(r"^## ", rest, re.M)
    return rest[: nxt.start()] if nxt else rest


def notes(text):
    return {n: t for n, t in NOTE.findall(text)}


def dam_mean(src, table, iso, node, monday):
    """(status, value or why) of a hub's mean over the local week starting on monday."""
    s, e, hours = local_week(monday, cd.TZ[iso])
    rows = src.rows(cd.current(table), f"{cd.PREFIX[iso]}:{node}", start=cd.iso_z(s), end=cd.iso_z(e))
    if rows is None:
        return "not here", f"{cd.current(table)} is not held"
    by = {}
    for _, v, var in rows:
        by.setdefault(var, []).append(v)
    full = [vs for vs in by.values() if len(vs) == hours]
    if len(full) != 1:
        return "not here", f"{max((len(v) for v in by.values()), default=0)} of {hours} hours held"
    return "held", cd.mean2(full[0])


def value_at(src, table, entity, ts, variable=None):
    rows = src.rows(cd.current(table), entity, variable=variable, ts=ts)
    if rows is None:
        return "not here", f"{cd.current(table)} is not held"
    if not rows:
        return "not here", f"no row at {ts}"
    return "held", rows[0][1]


def retrieved_at(src, table, entity, ts, variable=None):
    """When the row read was retrieved from its publisher (UTC, "YYYY-MM-DDTHH:MM:SSZ"), or None if not known."""
    table = cd.current(table)
    if isinstance(src, cd.Live):
        p = {"select": "retrieved_at", "table_name": f"eq.{table}", "entity": f"eq.{entity}", "ts_utc": f"eq.{ts}"}
        if variable:
            p["variable"] = f"eq.{variable}"
        got = src._get(p)
        return cd.iso_z(datetime.fromisoformat(got[0]["retrieved_at"].replace("Z", "+00:00"))) if got and got[0].get("retrieved_at") else None
    if isinstance(src, cd.Csv):
        import pandas as pd
        path = os.path.join(src.dir, f"{table}.csv")
        if not os.path.exists(path):
            return None
        df = pd.read_csv(path, skiprows=cd.header_rows(path), usecols=["entity", "variable", "ts_utc", "retrieved_at"], dtype=str)
        df = df[(df["entity"] == entity) & (df["ts_utc"] == ts)]
        if variable:
            df = df[df["variable"] == variable]
        return str(df["retrieved_at"].iloc[0]) if len(df) else None
    return None


def compare(src, shown, got, written, table, entity, ts, variable=None):
    """(status, why) of a printed value against the row read now. A row retrieved after the Roundup was written may hold
    the publisher's revision (EIA revises its hourly demand; an ISO corrects an interval price): "revised", said with
    both values, not a fault of the issue. A row retrieved before it that differs is a FAIL."""
    if got == shown:
        return "ok", got
    when = retrieved_at(src, table, entity, ts, variable)
    if when and written and when > written:
        return "revised", f"{got} (row retrieved {when}, after the issue was written {written}: the publisher's revision)"
    return "FAIL", f"{got}" + (f" (row retrieved {when})" if when else "")


GENERATED = re.compile(r"Generated by warehouse/news/roundup\.py at (\d{4}-\d\d-\d\d \d\d:\d\d) UTC")


def written_at(md):
    m = GENERATED.search(md)
    return datetime.strptime(m.group(1), "%Y-%m-%d %H:%M").strftime("%Y-%m-%dT%H:%M:00Z") if m else None


def checks(label, md):
    """[(key, page text, fn(src) -> (status, got))] of a Roundup's numbers section and, since session 806, of the week in
    five numbers; [] if it has none."""
    text = section(md)
    if text is None:
        return []
    refs = notes(text)
    monday = week_start(label)
    written = written_at(md)
    out = five_checks(label, md, refs, written)
    for iso, node, this, before, change, ref in DAM.findall(text):
        table = refs.get(ref)
        for which, cell, start in (("week", this.strip(), monday), ("week before", before.strip(), monday - timedelta(days=7))):
            key = f"rdp_dam|{iso}|{table}|{node}|{which}"
            if not PRICE.match(cell):
                out.append((key, cell, lambda src, c=cell: ("gap", "a gap stated when written")))
                continue

            def f(src, table=table, iso=iso, node=node, start=start, cell=cell):
                st, got = dam_mean(src, table, iso, node, start)
                return (("ok" if got == cell else "FAIL"), got) if st == "held" else (st, got)
            out.append((key, cell, f))
        if PRICE.match(this.strip()) and PRICE.match(before.strip()):
            want = f"{Decimal(this.strip()) - Decimal(before.strip()):+}"
            out.append((f"rdp_change|{iso}|{node}", change.strip(),
                        lambda src, w=want, c=change.strip(): (("ok" if w == c else "FAIL"), w)))
    m = RT.search(text)
    if m:
        v, node, iso, ts, variable, ref = m.groups()
        table, t = refs.get(ref), datetime.strptime(ts, "%Y-%m-%d %H:%M").strftime("%Y-%m-%dT%H:%M:00Z")
        entity = f"{ISO_RT[iso]}:{node}"

        def f(src, table=table, entity=entity, t=t, variable=variable, v=v):
            st, got = value_at(src, table, entity, t, variable)
            return compare(src, v, f"{got:.2f}", written, table, entity, t, variable) if st == "held" else (st, got)
        out.append((f"rdp_rt|{table}|{entity}|{variable}|{t}", v, f))
    for name, v1, d1, v0, d0, chg, pct in FUEL.findall(text):
        entity = FUEL_ENTITY[name]
        for v, d in ((v1, d1), (v0, d0)):
            def f(src, entity=entity, v=v, d=d):
                st, got = value_at(src, "eia_fuel_spot_prices", entity, f"{d}T00:00:00Z")
                return compare(src, v, f"{got:.2f}", written, "eia_fuel_spot_prices", entity, f"{d}T00:00:00Z") if st == "held" else (st, got)
            out.append((f"rdp_fuel|eia_fuel_spot_prices|{entity}|{d}", v, f))
        a, b = float(v1), float(v0)
        want = f"{a - b:+.2f} ({100 * (a / b - 1):+.1f}%)"
        out.append((f"rdp_fuel_change|{entity}|{d1}|{d0}", f"{chg} ({pct}%)",
                    lambda src, w=want, c=f"{chg} ({pct}%)": (("ok" if w == c else "FAIL"), w)))
    m = US48.search(text)
    if m:
        v, ts = m.groups()
        t = datetime.strptime(ts, "%Y-%m-%d %H:%M").strftime("%Y-%m-%dT%H:%M:00Z")

        def f(src, t=t, v=v):
            st, got = value_at(src, "eia930_all_demand", "eia930:US48", t, "demand_mw")
            return compare(src, v, f"{got:,.0f}", written, "eia930_all_demand", "eia930:US48", t, "demand_mw") if st == "held" else (st, got)
        out.append((f"rdp_us48|eia930_all_demand|eia930:US48|demand_mw|{t}", v, f))
    return out


def roundups(weeks=None):
    out = []
    for name in sorted(os.listdir(ROUNDUP)):
        m = re.fullmatch(r"(\d{4}-W\d{2})\.md", name)
        if m and (not weeks or m.group(1) in weeks):
            out.append((m.group(1), open(os.path.join(ROUNDUP, name), encoding="utf-8").read()))
    return out


def run(src, alt=None, weeks=None, say=print):
    """Counts {status: n} over every Roundup; each figure said on one line."""
    n = {"ok": 0, "FAIL": 0, "revised": 0, "not here": 0, "gap": 0}
    for label, md in roundups(weeks):
        cs = checks(label, md)
        if not cs:
            say(f"none     | {label} | no numbers section")
            continue
        for key, shown, f in cs:
            try:
                st, got = f(src)
            except Exception as exc:   # a failed read is not a figure checked: said so
                st, got = "not here", f"read failed: {exc!r}"[:200]
            if st == "not here" and alt is not None:
                try:
                    st2, got2 = f(alt)
                except Exception as exc:
                    st2, got2 = "not here", f"read failed: {exc!r}"[:200]
                if st2 != "not here":
                    st, got = st2, f"{got2} (the CSVs; the live set: {got})"
            n[st] += 1
            say(f"{st:8} | {label} | {key} | page {shown!r} | warehouse {got}")
    return n


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    ap.add_argument("--in-dir", default=os.path.join(cd.ROOT, "warehouse", "output"))
    ap.add_argument("--supabase", action="store_true")
    ap.add_argument("--then-csv", action="store_true", help="with --supabase: read a figure the live set does not hold from --in-dir")
    ap.add_argument("--week", action="append", help="only these Roundups (YYYY-Www; repeat)")
    a = ap.parse_args(argv)
    src = cd.Live() if a.supabase else cd.Csv(a.in_dir)
    alt = cd.Csv(a.in_dir) if (a.supabase and a.then_csv) else None
    print(f"check_roundup: {len(roundups(a.week))} Roundups, read against {src.describe()}"
          + (f", then {alt.describe()} for what it does not hold" if alt else ""))
    n = run(src, alt, a.week)
    print(f"\n{n['ok']} ok, {n['FAIL']} FAILED, {n['revised']} revised by the publisher after the issue was written, "
          f"{n['not here']} not held by this source, {n['gap']} gaps stated when written")
    if n["FAIL"]:
        return 1
    if not n["ok"]:
        print("check_roundup FAILED: no figure could be checked against this source")
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())

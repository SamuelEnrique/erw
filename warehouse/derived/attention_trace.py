#!/usr/bin/env python3
"""The tracer: from one value of the Attention or Friction Index to the stories that make it (session 3404, chain 202).

Energy Research Warehouse (ERW). Reads the two weekly tables and the link table and, for an entity and a week, prints
every value the tables hold for that cell and the rows of attention_story_links behind it, then checks by code that the
link rows add up to the values: the cell's stories, its opposition stories, each kind's count, the Attention Index
against the week's judged stories and the Friction Index against the cell's stories. Exit 0 when every value is
reproduced, 1 when one is not, 2 when the cell has no row.

    python warehouse/derived/attention_trace.py attention:datacenters:US-TX 2026-10-26
    python warehouse/derived/attention_trace.py attention:energy:all 2026-11-02 --in-dir warehouse/output --quiet
    python warehouse/derived/attention_trace.py --all --in-dir warehouse/output     # every cell, counts only (the method's check)

Method: docs/methods/attention.md.
"""

import argparse
import os
import sys

import pandas as pd

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.abspath(os.path.join(HERE, "..", ".."))
sys.path.insert(0, os.path.join(ROOT, "warehouse", "connectors"))
sys.path.insert(0, HERE)
import iso_prices as ip  # noqa: E402
import attention_index as ai  # noqa: E402


def read(in_dir, name):
    p = os.path.join(in_dir, name + ".csv")
    return pd.read_csv(p, skiprows=ip.header_rows(p), dtype=str, keep_default_na=False)


def cell_rows(links, sector, geo, week):
    """The link rows of one cell, by the rules attention_index.build uses."""
    g = links[links["week"] == week]
    g = g[g["sector"].isin(ai.ENERGY)] if sector == "energy" else g[g["sector"] == sector]
    if geo == "US":
        g = g[g["us"] == "true"]
    elif geo != "all":
        g = g[g["state"] == geo[3:]]
    return g


def trace(att, fri, links, entity, week, quiet=False):
    """Print and check one cell. Returns (ok, lines)."""
    _, sector, geo = entity.split(":")
    ts = week if "T" in week else week + "T00:00:00Z"
    a = att[(att["entity"] == entity) & (att["ts_utc"] == ts)].set_index("variable")["value"].astype(float)
    f = fri[(fri["entity"] == entity) & (fri["ts_utc"] == ts)].set_index("variable")["value"].astype(float)
    if a.empty:
        return None, [f"{entity} {ts}: no row"]
    judged = att[(att["entity"] == "attention:corpus:all") & (att["ts_utc"] == ts) & (att["variable"] == "stories_judged")]["value"].astype(float)
    judged = float(judged.iloc[0]) if len(judged) else 0.0
    rows = cell_rows(links, sector, geo, ts)
    opp = rows[rows["opposition"] == "true"]
    checks = [
        ("stories", a.get("stories"), float(len(rows))),
        ("attention_index", a.get("attention_index"), round(100.0 * len(rows) / judged, 4) if judged else 0.0),
        ("tone_mean", a.get("tone_mean"), round(rows["tone"].astype(int).mean(), 4) if len(rows) else None),
        ("opposition_stories", f.get("opposition_stories"), float(len(opp))),
        ("friction_index", f.get("friction_index"), round(100.0 * len(opp) / len(rows), 4) if len(rows) else None),
    ]
    for k in ai.OPP_KINDS:
        checks.append((f"kind_{k}", f.get(f"kind_{k}"), float((opp["kind"] == k).sum())))
    ok = True
    lines = [f"{entity}, week of {ts[:10]}: {len(rows)} link rows, {judged:.0f} judged stories that week"]
    for name, table_value, from_links in checks:
        same = table_value is not None and from_links is not None and abs(float(table_value) - float(from_links)) < 1e-6
        ok = ok and same
        lines.append(f"  {name:22s} table {table_value!s:>10}  from the links {from_links!s:>10}  {'ok' if same else 'DIFFERS'}")
    if not quiet:
        lines.append("  the stories (date | outlet | opposition kind | state | headline | link):")
        for r in rows.sort_values("event_date", ascending=False).itertuples():
            lines.append(f"    {r.event_date[:10]} | {r.source} | {r.kind if r.opposition == 'true' else '-'} | {r.state or '-'} | {r.headline[:90]} | {r.source_url}")
    return ok, lines


def main(argv=None):
    ap = argparse.ArgumentParser(description="ERW: from an index value to its stories")
    ap.add_argument("entity", nargs="?", help="attention:<sector>:<geo>, for example attention:datacenters:US-TX")
    ap.add_argument("week", nargs="?", help="the week's Monday, YYYY-MM-DD")
    ap.add_argument("--in-dir", default=ip.OUT_DIR)
    ap.add_argument("--quiet", action="store_true", help="the checks only, not the stories")
    ap.add_argument("--all", action="store_true", help="every cell of the two tables, counts only")
    args = ap.parse_args(argv)
    att, fri, links = read(args.in_dir, ai.ATT), read(args.in_dir, ai.FRI), read(args.in_dir, ai.LINKS)
    if args.all:
        cells = att[att["entity"] != "attention:corpus:all"][["entity", "ts_utc"]].drop_duplicates()
        bad = 0
        for r in cells.itertuples():
            ok, lines = trace(att, fri, links, r.entity, r.ts_utc, quiet=True)
            if not ok:
                bad += 1
                print("\n".join(lines))
        print(f"{len(cells)} cells checked, {bad} differ")
        return 1 if bad else 0
    if not args.entity or not args.week:
        ap.error("an entity and a week, or --all")
    ok, lines = trace(att, fri, links, args.entity, args.week, quiet=args.quiet)
    print("\n".join(lines))
    return 2 if ok is None else (0 if ok else 1)


if __name__ == "__main__":
    sys.exit(main())

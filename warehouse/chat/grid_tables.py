#!/usr/bin/env python3
"""Session 314: the tables a grid's scoped chat reads, found by rule, not by a hand-kept list.

Energy Research Warehouse (ERW). The owner's ruling of 19 October 2026 on session 302's open item: each grid's scoped
chat lists the public tables that hold the grid's rows by the entity-prefix rule session 302 ran by hand, not by the
hand-kept list in docs/grids/grids.json (which stays as documentation; tests/test_session314.py proves the rule found
every table of that list on the day this ran). Session 35's list fell behind each time a derived table gained a grid's
rows by hub (sessions 37, 51, 148, 267), and session 302 found ten refusals that way.

The rule, over the public tables in the live set (catalogue: in_live_set yes or review, license public), one row asked
of each table with the anon key (a public read of the live set; no publisher is requested):

  name     the table's name begins with the grid's slug and an underscore (ercot_hub_prices_daily): the grid's own
  entity   a series table holds a row whose entity begins with the grid's slug and a colon (cost_of_power_monthly:
           ercot:HB_HUBAVG), the rule session 302 ran by hand; a table named for another grid is not asked
  ba       a series table with a ba column holds a row of the grid's balancing authority (eia930_all_demand, whose
           entities are eia930:ERCO); asked after the entity rule, so a hub-keyed table is kept by its prefix
  queue    energy_projects, when the grid has a queue: a row whose entity_id begins with <iso>_queue:
  iso      storage_capacity, the national EIA-860M inventory: a row whose extra->>iso is the grid's ISO

The first rule that admits a table names how the tools keep its rows to the grid (site/lib/chat/tools.ts scopeFilter,
warehouse/chat/tools.py scope_rows): a table of the grid's own by name is read whole; by entity, ba, queue or iso its
rows are filtered as the rule says. A session 92 profile's own filters come before any of this. The market rule of
session 35 (a row whose market begins with the grid's market prefix) is not asked here: on 19 October 2026 it admitted
no table the entity rule had not, and a probe on the market column scans a whole partition (no index) and times out on
the largest tables; the tools keep it as a fallback for a table this file does not name.

Writes docs/grids/grid_tables.json: for each grid its tables (sorted) and the rule that admitted each, the tables the
hand-kept list lacks, the hand-listed tables the rule did not find, the read's time and the catalogue's size; and the
tables a probe could not read (an error is never a finding). The data machine runs it after its live-set load
(warehouse/run_data_machine_tables.sh, dm_grid_tables), so the file follows the live set.

    python warehouse/chat/grid_tables.py [--out docs/grids/grid_tables.json] [--check]

--check: exit 1 when a probe could not be read (an unread table is never a finding); a hand-listed table of grids.json
the rule did not find is printed (the table holds no row of the grid: energy_projects for NYISO and MISO on 19 October).
Standard library only. SUPABASE_URL and SUPABASE_ANON_KEY from the environment or the repository's .env.
"""
import argparse
import datetime as dt
import json
import os
import sys
import time
import urllib.error
import urllib.parse
import urllib.request

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.abspath(os.path.join(HERE, "..", ".."))
GRIDS = os.path.join(ROOT, "docs", "grids", "grids.json")
OUT = os.path.join(ROOT, "docs", "grids", "grid_tables.json")
RULES = ("name", "entity", "ba", "queue", "iso")
UTC = dt.timezone.utc


def env(name):
    v = os.environ.get(name, "").strip()
    if v:
        return v
    path = os.path.join(ROOT, ".env")
    if os.path.exists(path):
        for line in open(path, encoding="utf-8"):
            line = line.strip()
            if line.startswith(name + "="):
                return line.split("=", 1)[1].strip().strip('"').strip("'")
    return ""


class Reader:
    """One-row reads of the live set with the anon key, each tried three times."""

    def __init__(self, url, key, tries=3):
        self.base = url.rstrip("/")
        if not self.base.endswith("/rest/v1"):
            self.base += "/rest/v1"
        self.key = key
        self.tries = tries
        self.requests = 0

    def get(self, path, params):
        q = urllib.parse.urlencode(params)
        req = urllib.request.Request(f"{self.base}/{path}?{q}", headers={"apikey": self.key, "Authorization": f"Bearer {self.key}", "Prefer": "count=none"})
        err = None
        for i in range(self.tries):
            self.requests += 1
            try:
                with urllib.request.urlopen(req, timeout=90) as r:
                    return json.loads(r.read().decode("utf-8"))
            except (urllib.error.URLError, OSError, ValueError) as e:
                err = e
                time.sleep(2 * (i + 1))
        raise RuntimeError(f"{path}?{q}: {err}")

    def one(self, shape, table, **where):
        rows = self.get(shape, {"select": "*" if shape != "series" else "entity", "table_name": f"eq.{table}", "limit": "1", **where})
        return bool(rows)

    def prefixed(self, table, column, prefix):
        """Whether a series table holds a row whose column begins with prefix: the first row at or after the prefix in
        the column's order is asked for (one indexed read; a `like` scans a whole partition and times out)."""
        rows = self.get("series", {"select": column, "table_name": f"eq.{table}", column: f"gte.{prefix}", "order": f"{column}.asc", "limit": "1"})
        return bool(rows) and str(rows[0].get(column) or "").startswith(prefix)


def shape_of(columns):
    first = columns[:1]
    return "entities" if first == ["entity_id"] else "events" if first == ["event_id"] else "series"


def admit(reader, grid, table, columns, slugs=()):
    """The first rule that admits a table for a grid, or None. A table named for another grid (slugs) is that grid's
    own and is not asked."""
    slug, shape = grid["slug"], shape_of(columns)
    if table.startswith(slug + "_"):
        return "name"
    if any(table.startswith(s + "_") for s in slugs if s != slug):
        return None
    if shape == "series":
        if reader.prefixed(table, "entity", slug + ":"):
            return "entity"
        if "ba" in columns and reader.one("series", table, ba=f"eq.{grid['ba']}"):
            return "ba"
        return None
    if table == "energy_projects" and grid.get("queue_table"):
        q = grid["queue_table"].replace("_interconnection_queue", "_queue")
        return "queue" if reader.one("entities", table, entity_id=f"like.{q}:*") else None
    if table == "storage_capacity":
        return "iso" if reader.one("entities", table, **{"extra->>iso": f"eq.{grid['iso']}"}) else None
    return None


def build(reader, grids, catalogue, log=print):
    live = [c for c in catalogue if c.get("in_live_set") in ("yes", "review") and c.get("license") == "public"]
    out = {"grids": {}, "errors": {}}
    slugs = [g["slug"] for g in grids]
    for g in grids:
        found, errors = {}, {}
        for c in live:
            t = c["table_name"]
            columns = json.loads(c["columns"]) if c.get("columns") else []
            try:
                by = admit(reader, g, t, columns, slugs)
            except RuntimeError as e:
                errors[t] = str(e)[:200]
                continue
            if by:
                found[t] = by
        hand = set(g.get("tables") or [])
        out["grids"][g["slug"]] = {
            "tables": sorted(found),
            "by": {t: found[t] for t in sorted(found)},
            "not_in_grids_json": sorted(set(found) - hand),
            "grids_json_not_found": sorted(hand - set(found)),
        }
        if errors:
            out["errors"][g["slug"]] = errors
        log(f"{g['slug']}: {len(found)} tables by rule; the hand list lacks {len(set(found) - hand)}; not found of the hand list {sorted(hand - set(found))}; errors {len(errors)}")
    return out, len(live)


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--out", default=OUT)
    ap.add_argument("--check", action="store_true", help="exit 1 when a hand-listed table is not found or a probe failed")
    args = ap.parse_args(argv)
    url, key = env("SUPABASE_URL"), env("SUPABASE_ANON_KEY")
    if not url or not key:
        print("SUPABASE_URL and SUPABASE_ANON_KEY are needed", file=sys.stderr)
        return 2
    reader = Reader(url, key)
    grids = json.load(open(GRIDS, encoding="utf-8"))["grids"]
    t0 = time.time()
    read_at = dt.datetime.now(UTC).replace(microsecond=0).isoformat().replace("+00:00", "Z")
    catalogue = reader.get("catalogue", {"select": "table_name,iso,in_live_set,license,columns", "order": "table_name"})
    out, n_live = build(reader, grids, catalogue)
    result = {
        "_about": "Session 314: the tables each grid's scoped chat reads, found by rule from the live set's catalogue and one row asked of each public table (warehouse/chat/grid_tables.py, which says the rules). Written by the data machine after its live-set load; read by site/lib/chat/tools.ts (scopeOf, scopeFilter) and warehouse/chat/tools.py (set_scope, scope_rows). docs/grids/grids.json's tables are documentation since this session: not_in_grids_json and grids_json_not_found say how the two differ on the day this ran.",
        "read_at": read_at, "public_live_tables": n_live, "requests": reader.requests, "seconds": round(time.time() - t0),
        "rules": list(RULES), **out,
    }
    with open(args.out, "w", encoding="utf-8", newline="\n") as f:
        json.dump(result, f, indent=1)
        f.write("\n")
    print(f"wrote {os.path.relpath(args.out, ROOT)}: {len(grids)} grids, {n_live} public live tables, {reader.requests} requests, {result['seconds']} s")
    missing = {s: v["grids_json_not_found"] for s, v in out["grids"].items() if v["grids_json_not_found"]}
    if missing:
        print(f"hand-listed tables the rule did not find (grids.json's list is documentation; the table holds no row of the grid): {missing}")
    if args.check and out["errors"]:
        print(f"CHECK FAILED: probes that could not be read {out['errors']}")
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())

#!/usr/bin/env python3
"""Load the ERW live set into Supabase (session 10).

Energy Research Warehouse (ERW). Upserts only the live set that
warehouse/supabase/live_set.yaml defines. Rows go into the shape tables
series, entities and events (with table_name and license); coverage.csv goes
into catalogue and sources.csv into sources. The schema is
warehouse/supabase/migrations/, applied by warehouse/supabase/apply.py.

    python warehouse/supabase/load.py              # load, reconcile, check the size
    python warehouse/supabase/load.py --dry-run    # select and count only; no network
    python warehouse/supabase/load.py --only '^energy_projects$'   # some tables only (session 16)

Writes with SUPABASE_URL and SUPABASE_SERVICE_KEY (the service role bypasses
row-level security; the key is never printed). For each table:
- the live-set rows are selected from the CSV (whole, or the last N days);
- the rows Supabase already holds for that table are read and compared with
  them, column by column (session 11);
- only rows that are new or changed are upserted, stamped with this run's
  loaded_at (so loaded_at is the run that last wrote a row);
- rows Supabase holds that the selection no longer has (older than the window,
  or gone from the source) are deleted;
- count(*) in Supabase for that table_name must equal the selected CSV rows.
Session 13: a table whose selected rows hash (SHA-256, with its license) to the
value stored in catalogue.rows_sha256 by the last successful load is skipped
without reading it back; its count is still reconciled.
Session 11: the session 10 loader upserted every row on every run. Postgres keeps
the old copy of an updated row until a vacuum, so each full rewrite added the
size of the live set again (219 MB after the first load, 339 MB after the
second). Writing only what changed keeps a daily run's churn to the new days.
Session 16: --only REGEX (repeatable) loads only the live-set tables it matches, with their
headers and catalogue rows, and leaves every other table, and the catalogue's other rows, as
Supabase has them. For a machine whose other tables are older than the last CI load.
Then pg_database_size (function erw_db_size) must be under max_mb (400 since session 19; 7,500 since session 59, the Pro plan), or the
run fails. Exit 1 on any failure.
Session 18: GitHub run 4 failed twice over: "sources: CSV 100, Supabase 101" (a source that
left sources.csv stayed in Supabase, as sources were only upserted) and pg_database_size
300.6 MB, over max_mb (the series table held 62,631 dead row versions). Deleting from and
compacting the shared database is left to a person: every run now names the stale sources,
--prune deletes them and the rows of every table in coverage.csv no live-set rule matches,
and --vacuum-full compacts the shape tables through SUPABASE_DB_URL (only VACUUM FULL
shrinks pg_database_size). The scheduled run passes neither flag.
live_set.yaml "select" also takes include (keep only these values), since (series rows from
this time on) and days (series rows of the last N days, a window for one table).
Session 29 (human ruling, after 274.8 MB became 377.2 MB of 400 in one day): every load ends
with a vacuum of the shape tables through SUPABASE_DB_URL, VACUUM (FULL, ANALYZE), which
returns the space of the rows the load replaced, and prints pg_database_size before the load
and after the vacuum; the max_mb check reads the size after. Without SUPABASE_DB_URL (a
repository secret the daily workflow passes when it is set) the vacuum is skipped with a
warning and the run is not failed for it. --no-vacuum skips it on purpose.
Session 45: daily run 12's VACUUM FULL held the shape tables for about ten minutes, so every
load now ends with a plain VACUUM (ANALYZE), which marks the replaced rows' space for reuse and
takes no exclusive lock. VACUUM (FULL, ANALYZE), which returns the space to the operating system
and shrinks pg_database_size, runs only with --vacuum-full, a person's command (docs/runbook.md).
The warn_mb warning (350 MB) is unchanged.
Session 90: /contracts timed out on production. Its summary (internal_eqr_summary, migration 020) counted the live rows
of ferc_eqr_contracts on every request, with the public key, whose statements are cancelled after 3 seconds. The summary
is now computed here, from the rows this run loads (eqr_summary), and stored once (eqr_summary_store, migration 021);
the page's function reads that one row. A load of the table that cannot store its summary fails the table.
"""

import argparse
import datetime as dt
import hashlib
import json
import math
import os
import re
import sys
import urllib.parse

import pandas as pd
import yaml

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.abspath(os.path.join(HERE, "..", ".."))
OUT = os.path.join(ROOT, "warehouse", "output")
LIVE = yaml.safe_load(open(os.path.join(HERE, "live_set.yaml"), encoding="utf-8"))
BATCH = 1000
TS_FMT = "%Y-%m-%dT%H:%M:%SZ"

SERIES_COLS = ["entity", "variable", "ts_utc", "value", "unit", "freq", "geo", "market", "node",
               "source", "source_url", "retrieved_at", "vintage"]
ENTITY_COLS = ["entity_id", "entity_type", "name", "geo", "lat", "lon", "capacity_mw", "status",
               "status_date", "operator", "source", "source_url", "retrieved_at", "vintage"]
EVENT_COLS = ["event_id", "event_date", "event_type", "parties", "entity_ids", "mw", "price",
              "currency", "status", "source", "source_url"]
SHAPES = {"series": (SERIES_COLS, ["table_name", "entity", "variable", "ts_utc", "event"]),
          "entities": (ENTITY_COLS, ["table_name", "entity_id"]),
          "events": (EVENT_COLS, ["table_name", "event_id"])}
NUMERIC = {"value", "lat", "lon", "capacity_mw", "mw", "price"}
# Session 29: partition columns of consolidated series tables that Supabase stores (migration 009). A row that
# has none is compared exactly as before, so no other table's rows are rewritten.
SERIES_PARTITION = ["ba", "event"]  # session 36C: event (migration 011), part of the series key
MIGRATIONS = os.path.join(ROOT, "warehouse", "metadata", "table_migrations.csv")
TIMESTAMP = {"ts_utc", "retrieved_at", "event_date"}
CAT_NUMERIC = {"n_nodes", "n_rows"}


def env(name):
    v = os.environ.get(name)
    if not v:
        from dotenv import dotenv_values
        v = dotenv_values(os.path.join(ROOT, ".env")).get(name)
    v = (v or "").strip()
    if not v:
        raise SystemExit(f"{name} is not set (.env or environment); nothing loaded")
    return v


def read_table(name):
    path = os.path.join(OUT, name + ".csv")
    with open(path, encoding="utf-8") as f:
        n = sum(1 for line in f if line.startswith("#"))
    return pd.read_csv(path, skiprows=n, dtype=str, keep_default_na=False, na_values=[])


def shape_of(df):
    cols = list(df.columns)
    if cols[:2] == ["entity_id", "entity_type"]:
        return "entities"
    if cols[:1] == ["event_id"]:
        return "events"
    return "series"


def live_rule(n):
    """(rule, days) of the live-set rule a table name matches, or None."""
    if any(re.match(p, n) for p in LIVE["full"]):
        return "full", None
    if any(re.match(p, n) for p in LIVE["recent"]["tables"]):
        return "recent", LIVE["recent"]["days"]
    return None


def hold(cov, plan, held=None):
    """Session 85: the tables live_set.yaml's catalogue_hold names stay out of the live catalogue and of the live set.
    The home page counts the catalogue's public tables and rows; a new public table would move those numbers the day
    it is loaded, and while the live site is frozen for a reviewer no live number may move. A held table is in
    coverage.csv, the archive and its Redivis draft as any other; only Supabase does not hear of it, until a person
    takes its name off the list. Returns (coverage without them, plan without them, the names held)."""
    held = set(LIVE.get("catalogue_hold") or [] if held is None else held)
    return (cov[~cov["table"].isin(held)].reset_index(drop=True), [p for p in plan if p[0] not in held],
            sorted(held & set(cov["table"])))


def coverage_stale(cov, names, out=None):
    """Session 65: the tables whose coverage row no longer describes the file on this machine, as (table, reason).

    Session 64 ran `build_coverage.py | tail`: the pipe hid the build's failure, coverage.csv stayed as it was, and
    the loader ran on it. Coverage gives each loaded row its license and the catalogue its counts, so a load on a
    coverage older than the tables is refused. A table is described when coverage's n_rows is the file's row count
    and coverage's last_run is the run in the file's own 'Retrieved:' header line (what build_coverage.py reads);
    comparing contents, not file times, so a table restored from Redivis or the archive still matches."""
    out = OUT if out is None else out
    by = {r["table"]: r for r in cov.to_dict("records")}
    stale = []
    for n in names:
        if n not in by:
            stale.append((n, "not in coverage.csv"))
            continue
        import csv
        run = ""
        with open(os.path.join(out, n + ".csv"), encoding="utf-8", newline="") as f:
            pos = f.tell()
            line = f.readline()
            while line.startswith("#"):  # the provenance header; comment lines come only before the header row
                m = re.search(r"Retrieved: (\d{8}T\d{6}Z)", line)
                if m and not run:
                    run = dt.datetime.strptime(m.group(1), "%Y%m%dT%H%M%SZ").strftime(TS_FMT)
                pos = f.tell()
                line = f.readline()
            f.seek(pos)
            rows = sum(1 for _ in csv.reader(f)) - 1  # records, not lines: a quoted field may hold a line break
        if str(by[n]["n_rows"]) != str(rows):
            stale.append((n, f"coverage says {by[n]['n_rows']} rows, the file holds {rows}"))
        elif by[n].get("last_run", "") != run:
            stale.append((n, f"coverage describes the run {by[n].get('last_run') or 'none'}, the file is from {run or 'none'}"))
    return stale


def select_live():
    """[(table, rule, days)] for every table in warehouse/output the live set includes."""
    names = sorted(os.path.splitext(f)[0] for f in os.listdir(OUT) if f.endswith(".csv"))
    return [(n, *live_rule(n)) for n in names if live_rule(n)]


def delete_table_rows(client, shape, names):
    """Delete every row of these tables from a shape table, in batches by primary key, so a
    large table does not hit the API's statement timeout."""
    key = SHAPES[shape][1][1]
    for name in names:
        while True:
            ids = [r[key] for r in client.table(shape).select(key).eq("table_name", name)
                   .limit(BATCH).execute().data]
            if not ids:
                break
            for i in range(0, len(ids), 200):
                client.table(shape).delete().eq("table_name", name).in_(key, ids[i:i + 200]).execute()


EQR = "ferc_eqr_contracts"


def eqr_summary(df):
    """Session 90: the counts /contracts states, over the rows of ferc_eqr_contracts the live set holds: what migration
    020's internal_eqr_summary counted in SQL on every request, computed once here. Counts only: rows, rows with a rate
    filed as a number, the first and last execution date, the quarters filed for, and rows by month of execution, by
    product name (in capitals: FERC's names come in more than one spelling) and by delivery balancing authority."""
    def col(c):
        return df[c] if c in df.columns else pd.Series([""] * len(df), index=df.index)
    day = df["event_date"].str[:10]
    priced = col("x_rate") != ""
    product = col("x_product_name").str.upper()
    ba = col("x_point_of_delivery_balancing_authority").where(col("x_point_of_delivery_balancing_authority") != "", "not stated")
    g = pd.DataFrame({"month": day.str[:7], "product": product, "ba": ba, "priced": priced})

    def by(key, with_priced=True):
        t = g.groupby(key, sort=True).agg(rows=("priced", "size"), priced=("priced", "sum")).reset_index()
        return [{key: r[key], "rows": int(r["rows"]), **({"priced": int(r["priced"])} if with_priced else {})}
                for r in t.to_dict("records")]
    most = lambda rows, key: sorted(rows, key=lambda r: (-r["rows"], r[key]))
    out = {
        "rows": int(len(df)), "priced": int(priced.sum()),
        "first": day.min() if len(df) else None, "last": day.max() if len(df) else None,
        "quarters": sorted(q for q in col("x_quarter").unique() if q != ""),
        "by_month": by("month"), "by_product": most(by("product"), "product"), "by_ba": most(by("ba", False), "ba"),
    }
    largest = eqr_largest()
    if largest:
        out["largest"] = largest  # session 99: the largest buyers and sellers, from the whole quarter's file
    return out


EQR_TOP = 25


def eqr_largest(top=EQR_TOP, out_dir=None):
    """Session 99: the largest buyers and sellers of energy, capacity and tolling for /contracts?view=largest, from
    ferc_eqr_party_totals (warehouse/derived/eqr_buyers.py: the whole quarter's file, contracts in force, buyers by their
    name after the rules, sellers by FERC's company identifier): the first `top` of each role and product, how many
    parties each list holds, and the counts of the name rules. None when the tables are not on this machine. Internal,
    like the table they come from: it goes only into the stored summary, which answers only with the internal token."""
    d = out_dir or OUT
    paths = {n: os.path.join(d, n + ".csv") for n in ("ferc_eqr_party_totals", "ferc_eqr_buyer_names", "ferc_eqr_buyer_doubtful")}
    if not all(os.path.exists(p) for p in paths.values()):
        return None

    def table(path):
        with open(path, encoding="utf-8") as f:
            n = 0
            for line in f:
                if not line.startswith("#"):
                    break
                n += 1
        return pd.read_csv(path, skiprows=n, dtype=str, keep_default_na=False, na_values=[])
    t, names, pairs = table(paths["ferc_eqr_party_totals"]), table(paths["ferc_eqr_buyer_names"]), table(paths["ferc_eqr_buyer_doubtful"])
    lists = {}
    for role in ("buyer", "seller"):
        lists[role] = {}
        for product in ("energy", "capacity", "tolling"):
            g = t[(t["x_role"] == role) & (t["x_product"] == product)].copy()
            g["rank"] = g["x_rank"].astype(int)
            g = g.sort_values("rank")
            lists[role][product] = {
                "parties": int(len(g)), "contracts": int(g["x_contracts"].astype(int).sum()), "rows": int(g["x_rows"].astype(int).sum()),
                "top": [{"rank": int(r.rank), "name": r.name, "contracts": int(r.x_contracts), "rows": int(r.x_rows), "counterparties": int(r.x_counterparties),
                         "mw_filed": float(r.x_mw_filed), "rows_with_mw": int(r.x_rows_with_mw)} for r in g.head(top).itertuples()],
            }
    return {"quarter": t["x_quarter"].iloc[0] if len(t) else None, "top": top,
            "names": {"filed": int(len(names)), "after_rules": int(names["x_key"].nunique()), "merged_groups": int(names[names["x_merged"] == "yes"]["x_key"].nunique()),
                      "merged_names": int((names["x_merged"] == "yes").sum()), "doubtful_pairs": int(len(pairs))},
            "lists": lists}


def filtered(name, days, now):
    df = read_table(name)
    shape = shape_of(df)
    # session 16: live_set.yaml "select" keeps some extra columns and leaves out some rows of
    # a table, so a large table fits the size limit; Redivis and the CSV keep everything
    sel = (LIVE.get("select") or {}).get(name)
    if sel:
        for col, values in (sel.get("exclude") or {}).items():
            df = df[~df[col].isin(values)]
        for col, values in (sel.get("include") or {}).items():  # session 18: keep only these
            df = df[df[col].isin(values)]
        if sel.get("since"):  # session 18: series rows from this time on (ISO 8601 UTC)
            df = df[df["ts_utc"] >= sel["since"]]
        if sel.get("days"):  # session 18: series rows of the last N days only (a table's own window)
            df = df[df["ts_utc"] >= (now - pd.Timedelta(days=int(sel["days"]))).strftime(TS_FMT)]
        if sel.get("event_days"):  # session 83: events rows dated in the last N days (event_date, YYYY-MM-DD or a UTC time)
            df = df[df["event_date"].str[:10] >= (now - pd.Timedelta(days=int(sel["event_days"]))).strftime("%Y-%m-%d")]
        if sel.get("columns") is not None:
            std = SHAPES[shape][0]
            df = df[[c for c in df.columns if c in std or c in sel["columns"]]]
    if days is not None:
        if shape != "series":
            raise RuntimeError(f"{name}: a day window applies to series tables only")
        cut = (now - pd.Timedelta(days=days)).strftime(TS_FMT)
        df = df[df["ts_utc"] >= cut]  # ISO 8601 UTC strings sort as times
    return df, shape


def records(name, df, shape, license_, loaded_at):
    cols, _ = SHAPES[shape]
    extra_cols = [c for c in df.columns if c not in cols]
    out = []
    for row in df.to_dict("records"):
        r = {"table_name": name, "license": license_, "loaded_at": loaded_at}
        for c in cols:
            v = row.get(c, "")
            if v == "":
                r[c] = None
            elif c in NUMERIC:
                x = float(v)
                r[c] = None if math.isnan(x) else x
            else:
                r[c] = v
        if shape != "series":
            r["extra"] = {c: row[c] for c in extra_cols if row[c] != ""}
        else:  # session 29: the partition column, where the table has one
            for c in SERIES_PARTITION:
                if c in row:
                    r[c] = row[c] or ("" if c == "event" else None)  # event is a key column: '' when unset
        out.append(r)
    return out


def _ts(v):
    try:
        t = pd.Timestamp(v)
        t = t.tz_localize("UTC") if t.tzinfo is None else t.tz_convert("UTC")
        return t.strftime(TS_FMT)
    except (ValueError, TypeError):
        return str(v)


def canon(r, shape):
    """A row (a record written by this loader, or one read back from Supabase) in one
    comparable form: key tuple, value tuple."""
    cols, key = SHAPES[shape]
    vals = {}
    for c in cols:
        v = r.get(c)
        if v is None or v == "":
            vals[c] = None
        elif c in NUMERIC:
            vals[c] = float(v)
        elif c in TIMESTAMP:
            vals[c] = _ts(v)
        elif c == "status_date":
            vals[c] = str(v)[:10]
        else:
            vals[c] = str(v)
    vals["event"] = r.get("event") or ""  # session 36C: a key column of series, '' for tables without events
    k = (r["table_name"],) + tuple(vals[c] for c in key[1:])
    body = tuple(vals[c] for c in cols) + (r["license"],)
    if shape == "series":  # session 29: only when set, so a table without a partition compares as before
        body += tuple((c, r[c]) for c in SERIES_PARTITION if r.get(c) and c != "event")
    if shape != "series":
        body += (json.dumps(r.get("extra") or {}, sort_keys=True),)
    return k, body


def existing_rows(client, shape, name):
    """Every row Supabase holds for one ERW table, paged in key order."""
    cols, key = SHAPES[shape]
    fields = ",".join(["table_name"] + cols + ["license"] + (["extra"] if shape != "series" else SERIES_PARTITION))
    rows, start = [], 0
    while True:
        q = client.table(shape).select(fields).eq("table_name", name)
        for c in key[1:]:
            q = q.order(c)
        batch = q.range(start, start + BATCH - 1).execute().data
        rows += batch
        if len(batch) < BATCH:
            return rows
        start += BATCH


def older_than_live(client, name, df, shape):
    """Session 60: a reason to refuse loading this table, or None. On 2026-10-02 a data machine whose working copies were
    days older than the daily run's loaded them over Supabase's newer rows (30 tables, repaired the same hour from the
    Redivis draft). A table is refused when its newest retrieved_at is older than the newest Supabase holds for it, or,
    where it has no retrieved_at (a ledger, a list of reads), when it has fewer rows than Supabase holds."""
    try:
        if "retrieved_at" in df.columns and shape != "events":
            mine = str(df["retrieved_at"].dropna().astype(str).max() or "")
            got = client.table(shape).select("retrieved_at").eq("table_name", name).order("retrieved_at", desc=True).limit(1).execute().data
            theirs = str(got[0]["retrieved_at"]) if got and got[0].get("retrieved_at") else ""
            mine_t, theirs_t = pd.to_datetime(mine, utc=True, errors="coerce"), pd.to_datetime(theirs, utc=True, errors="coerce")
            if pd.notna(mine_t) and pd.notna(theirs_t) and mine_t < theirs_t:
                return f"its newest retrieved_at here is {mine}, Supabase holds rows retrieved {theirs}"
        else:
            n = client.table(shape).select("table_name", count="exact", head=True).eq("table_name", name).execute().count or 0
            if len(df) < n:
                return f"it has {len(df):,} rows here and {n:,} in Supabase (no retrieved_at to compare)"
    except Exception as exc:  # the guard must not stop a load on its own failure: say so and go on
        print(f"WARNING {name}: the older-than-live check could not run ({type(exc).__name__}: {str(exc)[:150]})")
    return None


def sync_table(client, name, df, shape, license_, loaded_at, days, now):
    """Make Supabase hold exactly the selected rows of one table, writing only the
    difference. Returns (written, deleted)."""
    cols, key = SHAPES[shape]
    recs = records(name, df, shape, license_, loaded_at)
    want = {}
    for r in recs:
        k, body = canon(r, shape)
        want[k] = (body, r)
    have = {}
    for r in existing_rows(client, shape, name):
        k, body = canon(r, shape)
        have[k] = body
    write = [r for k, (body, r) in want.items() if have.get(k) != body]
    gone = [k for k in have if k not in want]
    for i in range(0, len(write), BATCH):
        client.table(shape).upsert(write[i:i + BATCH], on_conflict=",".join(key)).execute()
    deleted = 0
    if days is not None:  # the rolling window: one delete for everything older than the cut
        cut = (now - pd.Timedelta(days=days)).strftime(TS_FMT)
        old = [k for k in gone if k[3] < cut]
        if old:
            client.table(shape).delete().eq("table_name", name).lt("ts_utc", cut).execute()
            deleted += len(old)
        gone = [k for k in gone if k[3] >= cut]
    if shape == "series":  # anything else, grouped by entity and variable
        groups = {}
        for k in gone:
            groups.setdefault((k[1], k[2], k[4]), []).append(k[3])
        for (ent, var, ev), tss in groups.items():
            for i in range(0, len(tss), 100):
                client.table(shape).delete().eq("table_name", name).eq("entity", ent) \
                    .eq("variable", var).eq("event", ev).in_("ts_utc", tss[i:i + 100]).execute()
    else:
        ids = [k[1] for k in gone]
        for i in range(0, len(ids), 100):
            client.table(shape).delete().eq("table_name", name).in_(key[1], ids[i:i + 100]).execute()
    deleted += len(gone)
    return len(write), deleted


def rows_sha256(df, license_):
    """SHA-256 of a table's selected rows: its license, then the rows as CSV."""
    h = hashlib.sha256()
    h.update(f"license={license_}\n".encode("utf-8"))
    h.update(df.to_csv(index=False, lineterminator="\n").encode("utf-8"))
    return h.hexdigest()


def db_size_mb(client):
    return int(client.rpc("erw_db_size").execute().data) / 1024 / 1024


def db_url():
    """SUPABASE_DB_URL from the environment or .env, or None (session 29: the vacuum is then skipped)."""
    v = os.environ.get("SUPABASE_DB_URL")
    if not v:
        from dotenv import dotenv_values
        v = dotenv_values(os.path.join(ROOT, ".env")).get("SUPABASE_DB_URL")
    return (v or "").strip() or None


def vacuum(url=None, full=False):
    """Session 45: VACUUM (ANALYZE) the shape tables after every load (no exclusive lock; the
    space of replaced rows is reused by later loads), or VACUUM (FULL, ANALYZE) when full is
    True (--vacuum-full, a person's command). Needs SUPABASE_DB_URL."""
    if full:
        return vacuum_full(url)
    import psycopg
    with psycopg.connect(url or env("SUPABASE_DB_URL"), autocommit=True, connect_timeout=30) as conn:
        for t in ("series", "entities", "events", "headers", "catalogue", "sources"):
            before = conn.execute(f"select pg_total_relation_size('public.{t}')").fetchone()[0]
            conn.execute(f"VACUUM (ANALYZE) public.{t}")
            after = conn.execute(f"select pg_total_relation_size('public.{t}')").fetchone()[0]
            print(f"VACUUM {t}: {before / 1048576:.1f} MB -> {after / 1048576:.1f} MB")


def vacuum_full(url=None):
    """Session 18: return the space of dead row versions to the operating system. Postgres
    reuses a dead row's space after a plain (auto)vacuum, but pg_database_size, which the
    max_mb check reads, shrinks only after VACUUM FULL. GitHub run 4 measured 300.6 MB, of
    which the series table held 62,631 dead rows. Needs SUPABASE_DB_URL. Session 29: run
    after every load (each table is locked for seconds while it is rewritten)."""
    import psycopg
    with psycopg.connect(url or env("SUPABASE_DB_URL"), autocommit=True, connect_timeout=30) as conn:
        for t in ("series", "entities", "events", "headers", "catalogue", "sources"):
            before = conn.execute(f"select pg_total_relation_size('public.{t}')").fetchone()[0]
            conn.execute(f"VACUUM (FULL, ANALYZE) public.{t}")
            after = conn.execute(f"select pg_total_relation_size('public.{t}')").fetchone()[0]
            print(f"VACUUM FULL {t}: {before / 1048576:.1f} MB -> {after / 1048576:.1f} MB")


def main(argv=None):
    ap = argparse.ArgumentParser(description="ERW Supabase live-set loader")
    ap.add_argument("--dry-run", action="store_true", help="select and count only, no network")
    ap.add_argument("--only", action="append", metavar="REGEX",
                    help="load only the live-set tables matching this pattern (repeatable; session 16)")
    ap.add_argument("--prune", action="store_true",
                    help="session 18: also delete sources gone from sources.csv and the rows of tables "
                         "no live-set rule matches; for a person to run, never the schedule")
    ap.add_argument("--vacuum-full", action="store_true",
                    help="session 18: after loading, VACUUM FULL the shape tables through SUPABASE_DB_URL "
                         "(a direct Postgres connection; locks each table for seconds) and measure again. "
                         "Session 45: a person's command only; the daily load runs a plain VACUUM (ANALYZE)")
    ap.add_argument("--no-vacuum", action="store_true",
                    help="session 29: skip the vacuum that ends every load")
    ap.add_argument("--allow-older", action="append", default=[], metavar="TABLE",
                    help="session 60: load this table although it is older than what Supabase holds (a person's "
                         "decision, such as a deliberate rollback)")
    args = ap.parse_args(argv)
    if not args.dry_run:  # session 59: loading Supabase is a data write, under the data lock (warehouse/lock.py)
        sys.path.insert(0, os.path.join(ROOT, "warehouse"))
        import lock
        lock.require(what="the Supabase load")
    now = pd.Timestamp.now(tz="UTC")
    loaded_at = now.strftime(TS_FMT)
    cov = pd.read_csv(os.path.join(ROOT, LIVE["catalogue"]), dtype=str, keep_default_na=False)
    lic = dict(zip(cov["table"], cov["license"]))
    plan = select_live()
    cov, plan, held = hold(cov, plan)
    if held:
        print(f"held out of the live catalogue (live_set.yaml, catalogue_hold): {', '.join(held)}")
    if args.only:
        plan = [p for p in plan if any(re.search(o, p[0]) for o in args.only)]
        if not plan:
            raise SystemExit(f"--only {args.only}: no live-set table matches; nothing loaded")
    stale = coverage_stale(cov, [p[0] for p in plan])
    if stale:  # session 65: never load on a coverage older than the tables it describes
        raise SystemExit("FAILED: coverage.csv is older than the tables it describes; nothing loaded. Run "
                         "python warehouse/metadata/build_coverage.py (and read its exit code) first.\n"
                         + "\n".join(f"  {t}: {why}" for t, why in stale))
    print(f"live set: {len(plan)} tables ({sum(r == 'full' for _, r, _ in plan)} whole, "
          f"{sum(r == 'recent' for _, r, _ in plan)} last {LIVE['recent']['days']} days)")

    selected = {}
    for name, rule, days in plan:
        df, shape = filtered(name, days, now)
        selected[name] = (df, shape)
        print(f"  {name}: {shape}, {rule}, {len(df):,} rows, license {lic.get(name)}")
    total = sum(len(df) for df, _ in selected.values())
    print(f"rows selected: {total:,}")
    if args.dry_run:
        return 0

    from supabase import create_client
    u = urllib.parse.urlparse(env("SUPABASE_URL"))
    client = create_client(f"{u.scheme}://{u.netloc}", env("SUPABASE_SERVICE_KEY"))
    # Session 33: the probe reads one row of one column (no count(*) over series' half a million rows, which timed out
    # with HTTP 500 twice in session 30), with three tries 5, 15 and 45 seconds apart before failing
    import time
    for t in ("series", "entities", "events", "catalogue", "sources", "headers"):
        for attempt in range(1, 4):
            try:
                client.table(t).select("source" if t == "sources" else "table_name").limit(1).execute()
                break
            except Exception as exc:
                if attempt == 3:
                    raise SystemExit(f"FAILED: Supabase table {t} is not reachable after 3 tries "
                                     f"({type(exc).__name__}: {str(exc)[:200]}). Apply the migrations first: "
                                     "warehouse/supabase/apply.py")
                wait = 5 * 3 ** (attempt - 1)
                print(f"Supabase table {t}: try {attempt} failed ({type(exc).__name__}); retrying in {wait} s")
                time.sleep(wait)
    size_before = db_size_mb(client)
    print(f"pg_database_size before the load: {size_before:.1f} MB")

    try:  # the hashes of the last successful load of each table (migration 004)
        prev = {r["table_name"]: r.get("rows_sha256")
                for r in client.table("catalogue").select("table_name,rows_sha256").execute().data}
    except Exception as exc:
        prev = {}
        print(f"no stored row hashes ({type(exc).__name__}: {str(exc)[:150]}); every table is compared row by row")
    hashes = {}
    failed = []
    recon = []
    for name, (df, shape) in selected.items():
        days = dict((n, d) for n, _, d in plan)[name]
        try:
            if name not in lic:
                raise RuntimeError("not in coverage.csv")
            digest = rows_sha256(df, lic[name])
            unchanged = prev.get(name) == digest
            stale = None if unchanged or name in args.allow_older else older_than_live(client, name, df, shape)
            if stale:
                raise RuntimeError(f"refused, older than the live copy: {stale}. Sync this machine from the cloud first "
                                   f"(python scripts/sync.py --refresh), or pass --allow-older {name} to roll it back on purpose")
            if unchanged:
                written = deleted = 0
            else:
                written, deleted = sync_table(client, name, df, shape, lic[name], loaded_at, days, now)
            n = client.table(shape).select("table_name", count="exact", head=True) \
                .eq("table_name", name).execute().count
            ok = n == len(df)
            if ok and name == EQR:  # session 90: the page's summary, from the rows just reconciled (migration 021)
                stored = client.rpc("eqr_summary_store", {"p_summary": eqr_summary(df)}).execute().data
                print(f"         {name}: the summary of {stored['rows']:,} rows stored for /contracts ({stored['computed_at']})")
            if ok:
                hashes[name] = digest
            recon.append((name, shape, len(df), n, "match" if ok else "MISMATCH", written, deleted, unchanged))
            print(f"{'match   ' if ok else 'MISMATCH'} {name}: CSV (filtered) {len(df):,}, Supabase {n:,}; "
                  + ("unchanged (same SHA-256), skipped" if unchanged else f"written {written:,}, deleted {deleted:,}"))
            if not ok:
                failed.append(name)
        except Exception as exc:
            failed.append(name)
            recon.append((name, shape, len(df), None, f"FAILED {type(exc).__name__}", None, None, False))
            print(f"FAILED {name}: {type(exc).__name__}: {str(exc)[:300]}")

    # provenance headers of every live-set table
    hdr = []
    for name in selected:
        path = os.path.join(OUT, name + ".csv")
        with open(path, encoding="utf-8") as f:
            lines = [ln.rstrip("\r\n")[1:].strip() for ln in f if ln.startswith("#")]
        hdr += [{"table_name": name, "line_no": i, "line": ln, "license": lic[name]}
                for i, ln in enumerate(lines, 1)]
    # session 14: replace the headers of this run's tables only. A machine that holds some
    # tables (the CI runner restores only the rolling windows) must not erase the others'.
    names = list(selected)
    for i in range(0, len(names), 50):
        client.table("headers").delete().in_("table_name", names[i:i + 50]).execute()
    for i in range(0, len(hdr), BATCH):
        client.table("headers").insert(hdr[i:i + BATCH]).execute()

    # catalogue (coverage.csv) and sources, loaded whole
    live_names = set(selected)
    # session 14: a table in coverage.csv whose CSV is not on this machine (carried over by
    # build_coverage.py on the CI runner) keeps its live-set fields as Supabase has them
    on_disk = {os.path.splitext(f)[0] for f in os.listdir(OUT) if f.endswith(".csv")}
    cat, cat_absent = [], []
    for r in cov.to_dict("records"):
        row = {("table_name" if k == "table" else k): (None if v == "" else v) for k, v in r.items()}
        for k in CAT_NUMERIC:
            row[k] = None if row.get(k) is None else int(row[k])
        if args.only and r["table"] not in selected:
            continue  # session 16: --only leaves the other catalogue rows as they are
        if r["table"] not in on_disk:
            cat_absent.append(row)  # coverage fields only; in_live_set, columns, rows_sha256 kept
            continue
        row["in_live_set"] = "yes" if r["table"] in live_names else "no"
        # the table's own columns, in CSV order (migration 003), so a reader returns exactly them
        row["columns"] = json.dumps(list(selected[r["table"]][0].columns)) if r["table"] in live_names else None
        row["rows_sha256"] = hashes.get(r["table"])  # null after a failed load, so the next run retries
        cat.append(row)
    client.table("catalogue").upsert(cat, on_conflict="table_name").execute()
    if cat_absent:
        client.table("catalogue").upsert(cat_absent, on_conflict="table_name").execute()
        print(f"catalogue: {len(cat_absent)} tables not on this machine kept their live-set fields")
    cat = cat + cat_absent
    if not args.only:
        client.table("catalogue").delete().not_.in_("table_name", list(cov["table"])).execute()
    reg = pd.read_csv(os.path.join(ROOT, LIVE["sources"]), dtype=str, keep_default_na=False)
    srcs = [{k: (None if v == "" else v) for k, v in r.items()} for r in reg.to_dict("records")]
    for i in range(0, len(srcs), BATCH):
        client.table("sources").upsert(srcs[i:i + BATCH], on_conflict="source").execute()
    # session 18: GitHub run 4 failed on "sources: CSV 100, Supabase 101": a source that left
    # sources.csv stayed in Supabase, since sources are only ever upserted. It is named on every
    # run; only --prune (run by a person, never by the schedule) deletes it.
    stale = [r["source"] for r in client.table("sources").select("source").execute().data
             if r["source"] not in set(reg["source"])]
    if stale and not args.prune:
        print(f"sources: {len(stale)} in Supabase but not in {LIVE['sources']}: {stale[:5]} "
              "(run load.py --prune to delete them)")
    if stale and args.prune and not args.only:
        for i in range(0, len(stale), 50):
            client.table("sources").delete().in_("source", stale[i:i + 50]).execute()
        print(f"sources: deleted {len(stale)} no longer in {LIVE['sources']}: {stale[:5]}")

    # session 29: the tables consolidated into others (warehouse/metadata/table_migrations.csv) leave Supabase in the
    # same run that loads their consolidated tables: their rows and headers are deleted (their catalogue rows went with
    # coverage.csv above). Only when every consolidated table in the live set loaded, so a page never goes empty.
    if not args.only and os.path.exists(MIGRATIONS):
        mig = pd.read_csv(MIGRATIONS, dtype=str, keep_default_na=False)
        loaded = [n for n in mig["new_table"].unique() if n in selected]
        if any(n in failed for n in loaded):
            print(f"migrated tables kept: a consolidated table failed to load ({[n for n in loaded if n in failed]})")
        else:
            olds = sorted(mig.loc[mig["new_table"].isin(loaded), "old_table"])
            for shape in SHAPES:
                for i in range(0, len(olds), 50):
                    part = olds[i:i + 50]
                    n = client.table(shape).select("table_name", count="exact", head=True)                         .in_("table_name", part).execute().count
                    if n:
                        delete_table_rows(client, shape, part)
                        print(f"consolidated (session 29): deleted {n:,} {shape} rows of the old tables {part}")
            for i in range(0, len(olds), 50):
                client.table("headers").delete().in_("table_name", olds[i:i + 50]).execute()

    # session 18, --prune only: rows of a table in coverage.csv that no live-set rule matches
    # any more are deleted (after a person narrows live_set.yaml). A table still in the live
    # set is never touched here.
    if args.prune and not args.only:
        gone = [t for t in cov["table"] if not live_rule(t)]
        for shape in SHAPES:
            for i in range(0, len(gone), 50):
                part = gone[i:i + 50]
                n = client.table(shape).select("table_name", count="exact", head=True) \
                    .in_("table_name", part).execute().count
                if n:
                    delete_table_rows(client, shape, part)
                    print(f"left the live set: deleted {n:,} {shape} rows of {part}")
        for i in range(0, len(gone), 50):
            client.table("headers").delete().in_("table_name", gone[i:i + 50]).execute()
    for t, want in ((("sources", len(srcs)),) if args.only else (("catalogue", len(cat)), ("sources", len(srcs)))):
        n = client.table(t).select("*", count="exact", head=True).execute().count
        ok = n == want
        recon.append((t, "meta", want, n, "match" if ok else "MISMATCH", want, None, False))
        print(f"{'match   ' if ok else 'MISMATCH'} {t}: CSV {want:,}, Supabase {n:,}")
        if not ok:
            failed.append(t)

    # session 29 (human ruling): vacuum after every load, and print the size before and after;
    # session 45: plain VACUUM (ANALYZE) by default, FULL only with --vacuum-full
    vacuum_kind = "VACUUM (FULL, ANALYZE)" if args.vacuum_full else "VACUUM (ANALYZE)"
    vac = "skipped (--no-vacuum)"
    if not args.no_vacuum:
        url = db_url()
        if url is None:
            vac = "skipped: SUPABASE_DB_URL is not set"
            print("WARNING: vacuum skipped, SUPABASE_DB_URL is not set (.env or the repository secret)")
        else:
            try:
                vacuum(url, full=args.vacuum_full)
                vac = vacuum_kind
            except Exception as exc:
                vac = f"FAILED {type(exc).__name__}"
                failed.append("vacuum")
                print(f"FAILED vacuum: {type(exc).__name__}: {str(exc)[:300]}")
    size = client.rpc("erw_db_size").execute().data
    mb = int(size) / 1024 / 1024
    # session 58: on 2026-09-30 the daily load wrote every table and then failed the size check at 448.5 MB: the plain
    # vacuum marks replaced rows for reuse but never shrinks the database, and the weekly VACUUM FULL came the next day
    # (356.6 MB after it). Over the limit after the plain vacuum, the load now runs VACUUM (FULL, ANALYZE) once and
    # measures again; the tables are locked for a few minutes, which a failed run cost more than.
    if mb > LIVE["max_mb"] and not args.no_vacuum and not args.vacuum_full and db_url() is not None and not vac.startswith("FAILED"):
        print(f"{mb:.1f} MB after VACUUM (ANALYZE), over the {LIVE['max_mb']} MB limit: VACUUM (FULL, ANALYZE) once (session 58)")
        try:
            vacuum(db_url(), full=True)
            vac = "VACUUM (ANALYZE), then VACUUM (FULL, ANALYZE) over the limit"
        except Exception as exc:
            vac = f"VACUUM (ANALYZE); the escalation to FULL FAILED {type(exc).__name__}"
            failed.append("vacuum")
            print(f"FAILED vacuum full: {type(exc).__name__}: {str(exc)[:300]}")
        size = client.rpc("erw_db_size").execute().data
        mb = int(size) / 1024 / 1024
    print(f"pg_database_size: {size_before:.1f} MB before the load, {mb:.1f} MB after the load and vacuum "
          f"({vac}); {int(size):,} bytes; limit {LIVE['max_mb']} MB")
    os.makedirs(os.path.join(ROOT, "runs"), exist_ok=True)
    pd.DataFrame(recon, columns=["table", "shape", "csv_rows", "supabase_rows", "result", "written",
                                 "deleted", "unchanged"]).to_csv(
        os.path.join(ROOT, "runs", "supabase_reconcile.csv"), index=False)
    with open(os.path.join(ROOT, "runs", "supabase_size.json"), "w", encoding="utf-8") as f:
        json.dump({"bytes": int(size), "mb": round(mb, 1), "mb_before": round(size_before, 1),
                   "vacuum": vac, "at": loaded_at}, f)
    if mb > LIVE["max_mb"]:
        print(f"FAILED: database is {mb:.1f} MB, over the {LIVE['max_mb']} MB limit", file=sys.stderr)
        return 1
    # session 36C: a warning well before the limit, so windows are trimmed by a person, not by a failed run
    warn_mb = LIVE.get("warn_mb")
    if warn_mb and mb > warn_mb:
        print(f"WARNING: database is {mb:.1f} MB, over the {warn_mb} MB warning line (limit {LIVE['max_mb']} MB); "
              "trim a live window in warehouse/supabase/live_set.yaml", file=sys.stderr)
    if failed:
        print(f"FAILED tables: {failed}", file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())

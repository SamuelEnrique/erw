#!/usr/bin/env python3
"""Weekly maintenance of the Supabase live set (session 49, approved by Samuel): VACUUM (FULL, ANALYZE) of the six
shape tables, with pg_database_size before and after, recorded in warehouse/metadata/run_status.csv.

Energy Research Warehouse (ERW). The daily load keeps its plain VACUUM (ANALYZE) (session 45), which marks the space of
replaced rows for reuse but never shrinks the database; this returns that space. Each table is locked while it is
rewritten (minutes for series), so the workflow runs it on Sunday at 10:00 UTC, four hours before the daily run, in
the daily run's concurrency group so the two never overlap.

    python warehouse/supabase/vacuum.py            # needs SUPABASE_DB_URL (environment or .env)

Writes runs/status/supabase_vacuum.json (connector supabase_vacuum, one row per table and one for the database) for
run_status.py record. Exit 1 when the vacuum fails; the sizes measured so far are still recorded.
"""

import datetime as dt
import os
import sys
import time
import traceback

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.abspath(os.path.join(HERE, "..", ".."))
sys.path.insert(0, os.path.join(ROOT, "warehouse", "connectors"))
import iso_prices as ip  # noqa: E402  (write_status, redact)

TABLES = ("series", "entities", "events", "headers", "catalogue", "sources")


def db_url():
    v = os.environ.get("SUPABASE_DB_URL")
    if not v:
        from dotenv import dotenv_values
        v = dotenv_values(os.path.join(ROOT, ".env")).get("SUPABASE_DB_URL")
    return (v or "").strip() or None


def main():
    run_id = dt.datetime.now(dt.timezone.utc).strftime("%Y%m%dT%H%M%SZ")
    results = []
    url = db_url()
    if not url:
        print("FAILED: SUPABASE_DB_URL is not set", file=sys.stderr)
        ip.write_status("supabase_vacuum", run_id, [dict(table="supabase", market="all", status="failed",
                                                         detail="SUPABASE_DB_URL is not set")])
        return 1
    import psycopg
    mb = lambda c: c.execute("select pg_database_size(current_database())").fetchone()[0] / 1048576  # noqa: E731
    try:
        with psycopg.connect(url, autocommit=True, connect_timeout=30) as c:
            before = mb(c)
            print(f"pg_database_size before: {before:.1f} MB")
            for t in TABLES:
                b = c.execute(f"select pg_total_relation_size('public.{t}')").fetchone()[0] / 1048576
                t0 = time.time()
                c.execute(f"VACUUM (FULL, ANALYZE) public.{t}")
                a = c.execute(f"select pg_total_relation_size('public.{t}')").fetchone()[0] / 1048576
                print(f"VACUUM (FULL, ANALYZE) {t}: {b:.1f} MB -> {a:.1f} MB in {time.time() - t0:.0f} s")
                results.append(dict(table=t, market="all", status="ok", detail=f"{b:.1f} MB -> {a:.1f} MB"))
            after = mb(c)
            print(f"pg_database_size after: {after:.1f} MB")
            results.append(dict(table="supabase", market="all", status="ok",
                                detail=f"pg_database_size {before:.1f} MB -> {after:.1f} MB"))
    except Exception:
        tb = ip.redact(traceback.format_exc())
        print(f"FAILED: {tb.strip().splitlines()[-1]}", file=sys.stderr)
        results.append(dict(table="supabase", market="all", status="failed", detail=tb.strip().splitlines()[-1][:300]))
    ip.write_status("supabase_vacuum", run_id, results)
    return 0 if all(r["status"] == "ok" for r in results) else 1


if __name__ == "__main__":
    sys.exit(main())

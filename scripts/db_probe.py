#!/usr/bin/env python3
"""The database gate: one ordered read of the series table, timed (session 431).

Energy Research Warehouse (ERW). Since about 23:30 UTC on 20 October 2026 Supabase has answered the heavier reads with
statement timeouts (57014), pages print "The live set could not be read" and the site's builds fail. A session that
would load into the live set, or read more than a count, asks this first:

    python scripts/db_probe.py                    # exit 0: the read took under 3 seconds; exit 1: slower, failed or timed out
    python scripts/db_probe.py --table iso_rtm_hub_prices --limit 1000

The read is a page's: the rows of one series table in the key's order (`site/lib/data.ts`, series()), under a
statement timeout of 5 seconds, through SUPABASE_DB_URL (.env or the environment). Its time and outcome are printed and
appended to runs/db_probe.log, one line a probe. It reads only; nothing is written to the database.
"""

import argparse
import datetime as dt
import os
import sys
import time

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.abspath(os.path.join(HERE, ".."))
LOG = os.path.join(ROOT, "runs", "db_probe.log")
TABLE = "iso_dam_hub_prices"  # read by the battery, seller and cost-of-power pages (iso_hub_prices_history is held: not in the live set)
LIMIT = 1000
TIMEOUT_MS = 5000
PASS_S = 3.0
SQL = ("select entity, variable, ts_utc, value from series where table_name = %s "
       "order by entity, variable, ts_utc, event limit %s")


def db_url():
    v = os.environ.get("SUPABASE_DB_URL")
    if not v:
        try:
            from dotenv import dotenv_values
            v = dotenv_values(os.path.join(ROOT, ".env")).get("SUPABASE_DB_URL")
        except ImportError:
            pass
    return (v or "").strip() or None


def connect(url):
    import psycopg
    return psycopg.connect(url, autocommit=True, connect_timeout=10)


def probe(url, table=TABLE, limit=LIMIT, connect=connect, clock=time.monotonic):
    """(exit code, seconds, what happened). The clock runs from before the connection to after the last row."""
    t0 = clock()
    try:
        with connect(url) as conn:
            conn.execute(f"set statement_timeout = {TIMEOUT_MS}")
            rows = conn.execute(SQL, (table, limit)).fetchall()
        s = clock() - t0
        if not rows:
            return 1, s, f"no rows of {table}"
        return (0 if s < PASS_S else 1), s, f"{len(rows)} rows of {table}"
    except Exception as exc:  # a timeout (57014), a refused connection: the gate is closed, and says why
        return 1, clock() - t0, f"{type(exc).__name__}: {str(exc).splitlines()[0][:150] if str(exc) else ''}"


def append(line, path=LOG):
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "a", encoding="utf-8") as f:
        f.write(line + "\n")


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--table", default=TABLE)
    ap.add_argument("--limit", type=int, default=LIMIT)
    ap.add_argument("--log", default=LOG)
    a = ap.parse_args(argv)
    url = db_url()
    if url is None:
        code, s, what = 1, 0.0, "SUPABASE_DB_URL is not set (.env or the environment)"
    else:
        code, s, what = probe(url, a.table, a.limit)
    now = dt.datetime.now(dt.timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
    line = f"{now} {'open' if code == 0 else 'CLOSED'} {s:.2f} s {what}"
    print(f"db_probe: {line}" + ("" if code == 0 else f" (the gate needs under {PASS_S:.0f} s: no load)"))
    append(line, a.log)
    return code


if __name__ == "__main__":
    sys.exit(main())

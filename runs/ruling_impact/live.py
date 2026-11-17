"""Session 7611 (portable-laptop): read-only queries of the ERW live set (Supabase Postgres) for the ruling impact scripts.

Every query runs in a read-only transaction. The connection string is read from the repository's .env (never printed).
No model is called. Usage from a script in this folder:

    from live import q, retrieved
    rows = q("select ... where table_name = %s", ("caiso_dam_hub_prices",))
"""
import os
import sys
from pathlib import Path

import psycopg

ROOT = Path(__file__).resolve().parents[2]


def _dsn() -> str:
    if os.environ.get("SUPABASE_DB_URL"):
        return os.environ["SUPABASE_DB_URL"]
    for line in (ROOT / ".env").read_text(encoding="utf-8").splitlines():
        if line.startswith("SUPABASE_DB_URL="):
            return line.split("=", 1)[1].strip().strip('"')
    raise SystemExit("SUPABASE_DB_URL is not set")


_conn = None


def conn():
    global _conn
    if _conn is None:
        _conn = psycopg.connect(_dsn(), autocommit=False)
        with _conn.cursor() as c:
            c.execute("set transaction read only")
    return _conn


def q(sql: str, params=()):
    with conn().cursor() as c:
        if params:
            c.execute(sql, params)
        else:
            c.execute(sql)   # no parameters: a literal % in a LIKE is not a placeholder
        return c.fetchall()


def tables_like(pattern: str):
    """Every table_name in the three shapes matching a SQL LIKE pattern, with its shape and row count."""
    out = []
    for shape in ("series", "entities", "events"):
        for name, n in q(f"select table_name, count(*) from public.{shape} where table_name like %s group by 1 order by 1", (pattern,)):
            out.append((shape, name, n))
    return out


def retrieved(shape: str, table: str):
    """The latest retrieved_at (series and entities) or loaded_at (events) of a table, and its source."""
    col = "loaded_at" if shape == "events" else "retrieved_at"
    return q(f"select max({col}), min(source) from public.{shape} where table_name = %s", (table,))[0]


if __name__ == "__main__":
    sys.stdout.reconfigure(encoding="utf-8")
    for row in tables_like(sys.argv[1] if len(sys.argv) > 1 else "%"):
        print(*row)

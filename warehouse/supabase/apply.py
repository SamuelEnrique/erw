#!/usr/bin/env python3
"""Apply the SQL migrations in warehouse/supabase/migrations/ to the ERW's Supabase project.

Energy Research Warehouse (ERW), session 10.

    python warehouse/supabase/apply.py

Migrations are applied in file-name order. Each one is idempotent (create ...
if not exists, drop policy if exists), so re-running is safe.

A migration is DDL (create table, alter table, create policy). Supabase runs DDL
only over a Postgres connection or through its Management API. The service key
(SUPABASE_SERVICE_KEY) is a PostgREST key: it reads and writes rows in existing
tables but cannot run SQL. This script therefore needs one of these, from .env
or the environment:

  SUPABASE_DB_URL        the project's Postgres connection string
                         (Supabase dashboard, Connect, "Session pooler" URI with the database password)
  SUPABASE_ACCESS_TOKEN  a Supabase personal access token (Management API,
                         POST /v1/projects/<ref>/database/query)

With neither, it stops with exit 1 and applies nothing. It never prints a key.

Session 72: one named migration only.

    python warehouse/supabase/apply.py --only 019_game_v4.sql      # or --only 019

Every migration is meant to be idempotent, but one no longer is: 014_game_v2.sql re-adds the version 2 preset check,
which the version 3 plays stored since break, so a run from the start stops there (session 71). --only applies the one
migration named (its file name, or its number), and nothing else: not the migrations before it, and not the settings
the full run writes at its end. A name that matches no file, or more than one, applies nothing and exits 2.
"""

import argparse
import glob
import os
import sys
import urllib.parse

import requests

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.abspath(os.path.join(HERE, "..", ".."))


def env(name):
    v = os.environ.get(name)
    if not v:
        from dotenv import dotenv_values
        v = dotenv_values(os.path.join(ROOT, ".env")).get(name)
    return (v or "").strip()


def select(files, only):
    """The migrations to apply: every file, or with `only` the one whose file name is `only` or starts with `only`
    followed by an underscore (its number). Raises ValueError when no file, or more than one, matches."""
    if not only:
        return files
    name = os.path.basename(only)
    hits = [f for f in files if os.path.basename(f) == name or os.path.basename(f).startswith(name + "_")]
    if len(hits) != 1:
        raise ValueError(f"--only {only!r} matches {len(hits)} migration(s): "
                         + (", ".join(os.path.basename(f) for f in hits) or "none"))
    return hits


def main(argv=None):
    ap = argparse.ArgumentParser(description="Apply the ERW's Supabase migrations")
    ap.add_argument("--only", help="apply only this migration (its file name or its number, e.g. 019)")
    args = ap.parse_args(argv)
    files = sorted(glob.glob(os.path.join(HERE, "migrations", "*.sql")))
    if not files:
        print("no migrations found", file=sys.stderr)
        return 2
    try:
        files = select(files, args.only)
    except ValueError as e:
        print(f"FAILED: {e}; nothing applied", file=sys.stderr)
        return 2
    db_url, token = env("SUPABASE_DB_URL"), env("SUPABASE_ACCESS_TOKEN")
    if db_url:
        import psycopg
        with psycopg.connect(db_url, autocommit=True) as conn:
            for f in files:
                conn.execute(open(f, encoding="utf-8").read())
                print(f"applied {os.path.basename(f)} (Postgres connection)")
            if args.only:
                return 0  # one migration only: the settings below belong to the full run
            # session 23 (migration 007): the email-token secret, from the environment, into the private schema;
            # never in a migration file, never printed
            secret = env("EMAIL_TOKEN_SECRET")
            if secret:
                conn.execute("insert into erw_private.settings (key, value) values ('email_token_secret', %s) "
                             "on conflict (key) do update set value = excluded.value", (secret,))
                print("set erw_private.settings email_token_secret from EMAIL_TOKEN_SECRET")
            else:
                print("EMAIL_TOKEN_SECRET not set: the email token secret was not written (confirm and unsubscribe "
                      "links cannot be checked until it is)")
            # session 30 (migration 010): the token of the internal costs page, the same way
            token_secret = env("INTERNAL_COSTS_TOKEN")
            if len(token_secret) >= 24:
                conn.execute("insert into erw_private.settings (key, value) values ('internal_costs_token', %s) "
                             "on conflict (key) do update set value = excluded.value", (token_secret,))
                print("set erw_private.settings internal_costs_token from INTERNAL_COSTS_TOKEN")
            else:
                print("INTERNAL_COSTS_TOKEN not set (or shorter than 24 characters): /internal/costs answers nothing "
                      "until it is")
        return 0
    if token:
        ref = urllib.parse.urlparse(env("SUPABASE_URL")).netloc.split(".")[0]
        for f in files:
            r = requests.post(f"https://api.supabase.com/v1/projects/{ref}/database/query",
                              headers={"Authorization": f"Bearer {token}"},
                              json={"query": open(f, encoding="utf-8").read()}, timeout=120)
            if r.status_code >= 300:
                print(f"FAILED {os.path.basename(f)}: HTTP {r.status_code} {r.text[:300]}", file=sys.stderr)
                return 1
            print(f"applied {os.path.basename(f)} (Management API)")
        return 0
    print("FAILED: neither SUPABASE_DB_URL nor SUPABASE_ACCESS_TOKEN is set. The service key "
          "(SUPABASE_SERVICE_KEY) authenticates the REST API and cannot run DDL, so the "
          f"{len(files)} migration(s) were not applied. See warehouse/supabase/README.md.", file=sys.stderr)
    return 1


if __name__ == "__main__":
    sys.exit(main())

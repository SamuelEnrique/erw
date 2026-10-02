#!/usr/bin/env python3
"""The ERW's scheduled jobs, run from the database (session 59): pg_cron fires on time, pg_net calls GitHub's
workflow_dispatch (migration 015_scheduler.sql).

Energy Research Warehouse (ERW).

    python warehouse/supabase/scheduler.py --apply            # migration 015: extensions, erw_dispatch(), the five jobs
    python warehouse/supabase/scheduler.py --set-token        # GH_TOKEN from .env or the environment into Vault (github_dispatch)
    python warehouse/supabase/scheduler.py --test latest-prices.yml   # one dispatch now; prints GitHub's answer (204 = accepted)
    python warehouse/supabase/scheduler.py --status           # the jobs, their last runs and the last answers

Needs SUPABASE_DB_URL (a Postgres connection; Supabase dashboard, Connect). The token is read from the environment and
written into Supabase Vault; it is never printed and never in this repository. A fine-grained token expires: when it does,
run --set-token with the new one (docs/runbook.md).
"""

import os
import sys
import time

import psycopg

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.abspath(os.path.join(HERE, "..", ".."))
MIGRATION = os.path.join(HERE, "migrations", "015_scheduler.sql")


def env(name):
    v = os.environ.get(name)
    if not v:
        try:
            from dotenv import dotenv_values
            v = dotenv_values(os.path.join(ROOT, ".env")).get(name)
        except ImportError:
            pass
    if not v:
        raise SystemExit(f"{name} is not set (.env or the environment)")
    return v.strip()


def conn():
    return psycopg.connect(env("SUPABASE_DB_URL"), connect_timeout=30, autocommit=True)


def apply():
    with conn() as c:
        c.execute(open(MIGRATION, encoding="utf-8").read())
    print("applied 015_scheduler.sql")


def set_token():
    tok = env("GH_TOKEN")
    with conn() as c:
        row = c.execute("select id from vault.secrets where name = 'github_dispatch'").fetchone()
        desc = "GitHub fine-grained token, Actions read and write on SamuelEnrique/erw (session 59 scheduler)"
        if row:
            c.execute("select vault.update_secret(%s, %s, 'github_dispatch', %s)", (row[0], tok, desc))
            print("github_dispatch updated in Vault")
        else:
            c.execute("select vault.create_secret(%s, 'github_dispatch', %s)", (tok, desc))
            print("github_dispatch created in Vault")


def test(workflow):
    with conn() as c:
        rid = c.execute("select public.erw_dispatch(%s)", (workflow,)).fetchone()[0]
        for _ in range(30):
            time.sleep(2)
            r = c.execute("select status_code, left(coalesce(content, ''), 200), error_msg from net._http_response where id = %s", (rid,)).fetchone()
            if r:
                print(f"dispatch {workflow}: request {rid}, GitHub answered HTTP {r[0]} {r[1]!r} {r[2] or ''}")
                return 0 if r[0] == 204 else 1
    print(f"dispatch {workflow}: request {rid}, no answer within 60 s")
    return 1


def status():
    with conn() as c:
        for j in c.execute("select jobid, jobname, schedule, active from cron.job where jobname like 'erw-%' order by jobname").fetchall():
            last = c.execute("select status, start_time, return_message from cron.job_run_details where jobid = %s order by start_time desc limit 1", (j[0],)).fetchone()
            print(f"{j[1]:22s} {j[2]:22s} active={j[3]}  last run: {last[0] + ' ' + str(last[1])[:19] if last else 'none yet'}")
        for r in c.execute("select id, status_code, created from net._http_response order by id desc limit 5").fetchall():
            print(f"  response {r[0]}: HTTP {r[1]} at {str(r[2])[:19]}")


if __name__ == "__main__":
    a = sys.argv[1:]
    if "--apply" in a:
        apply()
    if "--set-token" in a:
        set_token()
    if "--test" in a:
        sys.exit(test(a[a.index("--test") + 1]))
    if "--status" in a or not a:
        status()

#!/usr/bin/env python3
"""Prove what the anon key can read in the ERW's Supabase project, table by table, against the expected list.

Energy Research Warehouse (ERW), session 177 (docs/reviews/2026-10-10-security.md; migration 028).

    python warehouse/supabase/verify_rls.py                 # the anon key, over REST, exactly as a visitor could
    python warehouse/supabase/verify_rls.py --catalog       # also the catalog (needs SUPABASE_DB_URL): RLS on everywhere,
                                                            # no table outside the expected list
    python warehouse/supabase/verify_rls.py --before-028    # before migration 028: its four tables may be absent

It only reads. Every request is a GET of one row (or a call of a read function with a wrong token, which must be
refused). Nothing is inserted, updated or deleted, and no function that writes is called.

What is checked, and what a mismatch is:

  1. Each table of EXPECTED answers as the list says: "public" (HTTP 200: the anon key may read it, and row-level
     security decides which rows) or "blocked" (HTTP 401 or 403: permission denied). A table the list calls public
     that is blocked is a page that lost a read; a table the list calls blocked that answers 200 is a leak.
  2. In each public table that has a license column, no row whose license is not 'public' is returned, and the
     internal tables loaded into the shared shapes (the cost ledger, the FERC contracts) return no row by name.
  3. THE PROOF: one direct read of an internal table (site_api_calls, the cost ledger of the question-answering
     tools) with the anon key fails. Its HTTP status and Postgres code are printed.
  4. Each read function behind the internal token refuses a wrong token.
  5. With --catalog: every table in schema public has row-level security enabled and is in EXPECTED (a table added
     later must be added to the list here, as public or blocked, before this passes again), and a blocked table
     has no select policy for anon.
  6. With --catalog (session 5156): every function of schema public the anon key may execute is in ANON_FUNCTIONS,
     with the credential it asks for (the default privileges give a new function to the anon key).
  7. With --catalog (session 5172): every storage bucket is in EXPECTED_BUCKETS as public or private, storage.objects
     has row-level security on and no policy for the anon key or a signed-in user, and the anon key lists nothing of
     a private bucket (the archive of every table's rows is one).
  8. With --catalog (session 5173): the API serves no schema but public to the anon key (a read of a table of net,
     cron, vault, erw_private, storage or extensions is refused); the anon role holds no usage on cron, vault or
     erw_private and cannot execute the dispatcher; each scheduled job is one call of the dispatcher and holds no
     text shaped like a key.

Exit 0 when everything matches, 1 on any mismatch, 2 when the key or the address is not set. Never prints a key.
"""

import argparse
import json
import os
import re
import sys
import urllib.error
import urllib.parse
import urllib.request

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.abspath(os.path.join(HERE, "..", ".."))

# The expected list. "public": the site (site/lib/supabase.ts rest/restCount, /api/download, /api/entity, the game's
# leaderboard), the erw package's Supabase backend with the anon key (package/src/erw/remote.py) and
# site/scripts/check-values.mjs read it with the anon key. "blocked": internal, read only by the service role or
# through a function that checks a secret. Derived in session 177 from every rest(...)/rpc(...) call under site/ and
# package/, from live_set.yaml and from the catalog (runs/session177/catalog.json).
EXPECTED = {
    # the live set's shapes: rows whose license is 'public' (migration 002)
    "series": "public",
    "entities": "public",
    "events": "public",
    "latest_prices": "public",
    "catalogue": "public",
    "sources": "public",
    "headers": "public",
    # the game's leaderboard (migration 013): read by /play/battery and /api/play/top
    "game_scores": "public",
    # internal: no select policy, no select grant
    "game_plays": "blocked",            # the research record of each play; insert only
    "subscribers": "blocked",           # e-mail addresses; insert only
    "email_suppressions": "blocked",
    "digest_sends": "blocked",
    "site_api_calls": "blocked",        # the cost ledger of /api/ask; insert only
    "site_ask_counts": "blocked",
    "erw_health": "blocked",
    "erw_locks": "blocked",
    "thesis_runs": "blocked",
    "thesis_provider_results": "blocked",
    "analysis_requests": "blocked",
    # migration 028 (session 177): the rate limits and the usage counts
    "site_rate_counts": "blocked",
    "site_usage_events": "blocked",
    "site_usage_daily": "blocked",
    "site_usage_salt": "blocked",
    # migration 029 (session 181): the scanner's review list, read only through scanner_drafts_list with the token
    "scanner_drafts": "blocked",
    # migration 030 (session 232): the Digest's daily chart candidates, written and read with the service role only
    "daily_chart_candidates": "blocked",
}
NEW_IN_028 = ("site_rate_counts", "site_usage_events", "site_usage_daily", "site_usage_salt")
LICENSED = ("series", "entities", "events", "latest_prices", "catalogue", "sources", "headers")
# internal tables loaded into the shared shapes: no row may come back by name
INTERNAL_BY_NAME = (("events", "api_cost_ledger"), ("events", "ferc_eqr_contracts"), ("events", "news_stories"),
                    ("series", "pjm_da_lmp"), ("entities", "ferc_eqr_contracts"))
# read functions behind the internal token: a wrong token must be refused (none of these writes)
TOKEN_FUNCTIONS = (("internal_costs", {}), ("internal_ask_spend", {}), ("internal_eqr_summary", {}),
                   ("thesis_list", {}), ("analysis_requests_list", {}), ("internal_usage", {}),
                   ("scanner_drafts_list", {}), ("analysis_request_card", {"p_id": "verify-rls-0000"}),
                   # migration 031 (session 233): one file of a draft of the weekly hunt
                   ("scanner_draft_file", {"p_id": "scan-hunt-000000000000", "p_name": "scan-hunt-000000000000.csv"}))
PROOF_TABLE = "site_api_calls"
WRONG_TOKEN = "verify-rls-wrong-token-0000000000000000"

# Session 5156 (docs/reviews/security-faults-2026-11-13.md, row 7; the review's M6). The default privileges of schema
# public give every NEW function to the anon key, and no trigger covers a function as ensure_rls covers a table. So the
# functions the anon key may execute are listed here, each with the credential it asks for in its own arguments, and
# --catalog fails on one that is not listed: revoke its execute right, or list it once it is known to ask for one.
# A function whose first argument is p_token checks it against the internal token (or the thesis tool's) before
# anything else; the three that do not take p_token first are named with what they ask instead. Session 5170:
# tests/test_session5170.py reads each one's newest definition in the migrations and holds that opening.
ANON_FUNCTIONS = {
    "analysis_request": "p_token", "analysis_request_card": "p_token", "analysis_requests_list": "p_token",
    "internal_ask_spend": "p_token", "internal_costs": "p_token", "internal_eqr_contracts": "p_token",
    "internal_eqr_summary": "p_token", "internal_usage": "p_token",
    "scanner_draft_file": "p_token", "scanner_draft_set_state": "p_token", "scanner_drafts_list": "p_token",
    "site_rate_admit": "p_token", "site_usage_record": "p_token",
    "thesis_get": "p_token", "thesis_list": "p_token", "thesis_provider_accept": "p_token",
    "thesis_provider_results": "p_token", "thesis_submit": "p_token", "thesis_submit_forced": "p_token",
    "subscribe_confirm": "the address's own signed token (migration 007)",
    "subscribe_unsubscribe": "the address's own signed token (migration 007)",
    "thesis_pitchbook_accept": "the run's one-time key",
    "rls_auto_enable": "an event trigger's function (Supabase's ensure_rls): Postgres refuses a direct call",
}

# Session 5172: the storage buckets. erw-archive is the ERW's durable store (warehouse/archive/, every table's rows by
# month) and erw-thesis holds the thesis tool's files: both private. erw-public holds the few files a page fetches by
# address (the network's hourly file): public by design. A bucket is listed here before --catalog passes again, and
# storage.objects carries no policy for the anon key: with row-level security on and no policy, the anon key lists and
# reads nothing of a private bucket, whatever table privilege it holds.
EXPECTED_BUCKETS = {"erw-archive": "private", "erw-public": "public", "erw-thesis": "private"}

# Session 5173: what else the database could offer the anon key. The REST API serves schema public alone: a table of
# any of these schemas, asked for by name, must be answered "Invalid schema" (the anon role holds usage on `net`, the
# extension that makes HTTP requests from the database, by the host's own default; it is the API's list of schemas
# that keeps it out of reach). The scheduled jobs (pg_cron) each call the dispatcher and nothing else, and no job's
# command holds text shaped like a key: the token that starts a workflow lives in the vault, read by erw_dispatch.
CLOSED_SCHEMAS = (("net", "http_request_queue"), ("cron", "job"), ("vault", "secrets"), ("erw_private", "settings"),
                  ("storage", "objects"), ("extensions", "pg_stat_statements"))
KEY_SHAPED = re.compile(r"eyJ[A-Za-z0-9_-]{10,}\.[A-Za-z0-9_-]{10,}|gh[pousr]_[A-Za-z0-9]{20,}|github_pat_[A-Za-z0-9_]{20,}|sk-ant-[A-Za-z0-9_-]{10,}"
                        r"|sb_secret_[A-Za-z0-9_-]{10,}|re_[A-Za-z0-9]{20,}|[Bb]earer\s+[A-Za-z0-9._-]{20,}|://[^/\s:@]+:[^/\s@]{6,}@")
JOB_COMMAND = re.compile(r"^\s*select\s+public\.erw_dispatch\(\s*'[a-z0-9-]+\.yml'\s*(?:,\s*'[^']*'\s*(?:::\s*jsonb?\s*)?)?\)\s*;?\s*$", re.I)

def env(name):
    v = os.environ.get(name)
    if not v:
        try:
            from dotenv import dotenv_values
            v = dotenv_values(os.path.join(ROOT, ".env")).get(name)
        except ImportError:
            v = None
    return (v or "").strip()


SMALL_LICENSED = ("latest_prices", "catalogue", "sources", "headers")


def internal_tables(path=None):
    """The ERW tables whose license is not public, from warehouse/metadata/coverage.csv (the names only). An absent
    file gives none: the names written above are still asked."""
    import csv
    path = path or os.path.join(ROOT, "warehouse", "metadata", "coverage.csv")
    if not os.path.exists(path):
        return []
    with open(path, encoding="utf-8", newline="") as f:
        rows = csv.DictReader(line for line in f if not line.startswith("#"))
        return sorted(r["table"] for r in rows if r.get("table") and (r.get("license") or "").strip() != "public"
                      and all(c.isalnum() or c == "_" for c in r["table"]))


def classify(status, body):
    """What one answer of PostgREST means: 'public', 'blocked', 'absent' or 'error'."""
    code = ""
    try:
        parsed = json.loads(body) if body else None
        if isinstance(parsed, dict):
            code = str(parsed.get("code") or "")
    except ValueError:
        pass
    if status == 200:
        return "public"
    if code in ("PGRST205", "PGRST202", "42P01") or status == 404:
        return "absent"            # no such table (or function) for this key
    if status in (401, 403) or code == "42501":
        return "blocked"
    return "error"


def compare(expected, seen, allow_absent=()):
    """The mismatches between the expected list and what was seen: a list of (table, expected, seen)."""
    out = []
    for table, want in sorted(expected.items()):
        got = seen.get(table, "not asked")
        if got == want or (got == "absent" and table in allow_absent):
            continue
        out.append((table, want, got))
    return out


class Rest:
    def __init__(self, base, key):
        self.base, self.key = base, key

    def call(self, path, body=None):
        """(status, text of the body, cut at 2,000 characters)."""
        req = urllib.request.Request(f"{self.base}/rest/v1/{path}", method="POST" if body is not None else "GET",
                                     data=json.dumps(body).encode() if body is not None else None,
                                     headers={"apikey": self.key, "Authorization": f"Bearer {self.key}",
                                              "Content-Type": "application/json", "Accept": "application/json"})
        try:
            with urllib.request.urlopen(req, timeout=30) as r:
                return r.status, r.read(200000).decode("utf-8", "replace")[:2000]
        except urllib.error.HTTPError as e:
            return e.code, e.read(200000).decode("utf-8", "replace")[:2000]


def code_of(body):
    try:
        d = json.loads(body)
        return str(d.get("code") or "") if isinstance(d, dict) else ""
    except ValueError:
        return ""


def check_rest(rest, before_028=False, out=print):
    bad = 0
    seen = {}
    out("1. each table, read with the anon key (one row asked for)")
    for table in sorted(EXPECTED):
        status, body = rest.call(f"{table}?select=*&limit=1")
        seen[table] = classify(status, body)
        out(f"   {table:26s} expected {EXPECTED[table]:8s} seen {seen[table]:8s} (HTTP {status}{' ' + code_of(body) if code_of(body) else ''})")
    for table, want, got in compare(EXPECTED, seen, NEW_IN_028 if before_028 else ()):
        bad += 1
        out(f"   MISMATCH {table}: expected {want}, seen {got}")
    out("2. no internal row in a public table")
    for table in SMALL_LICENSED:
        if seen.get(table) != "public":
            continue
        status, body = rest.call(f"{table}?select=license&license=neq.public&limit=1")
        rows = json.loads(body) if status == 200 else None
        ok = status == 200 and rows == []
        bad += 0 if ok else 1
        out(f"   {table:26s} rows whose license is not public: {'none' if ok else 'MISMATCH (HTTP %d)' % status}")
    # the three shapes hold millions of rows: a search for a row that is not public reads them all and the anon key's
    # three seconds run out. They are asked by name instead (the key's first column): every internal table the
    # coverage file names, in each shape, one name a request (a list of names in one request also ran out of time on
    # events). A request cancelled by the time limit (HTTP 500, 57014) is asked once more, as the site's reader does.
    names = sorted(set(internal_tables()) | {n for _, n in INTERNAL_BY_NAME})
    for shape in ("series", "entities", "events"):
        if seen.get(shape) != "public":
            continue
        leaks = []
        for name in names:
            status, body = rest.call(f"{shape}?select=table_name&table_name=eq.{name}&limit=1")
            if status == 500 and "57014" in body:
                status, body = rest.call(f"{shape}?select=table_name&table_name=eq.{name}&limit=1")
            if not (status == 200 and json.loads(body) == []):
                leaks.append(f"{name} (HTTP {status})")
        bad += len(leaks)
        out(f"   {shape:26s} rows of the {len(names)} internal tables, each asked by name: {'none' if not leaks else 'MISMATCH: ' + ', '.join(leaks)}")
    out("3. the proof: a direct read of an internal table with the anon key")
    status, body = rest.call(f"{PROOF_TABLE}?select=*&limit=1")
    refused = classify(status, body) == "blocked"
    bad += 0 if refused else 1
    out(f"   GET {PROOF_TABLE}?select=*&limit=1 -> HTTP {status}, code {code_of(body) or '(none)'}: {'REFUSED' if refused else 'MISMATCH: not refused'}")
    out("4. read functions behind the internal token, called with a wrong token")
    for fn, extra in TOKEN_FUNCTIONS:
        status, body = rest.call(f"rpc/{fn}", {"p_token": WRONG_TOKEN, **extra})
        kind = classify(status, body)
        ok = kind == "blocked" or (kind == "absent" and before_028 and fn == "internal_usage")
        bad += 0 if ok else 1
        out(f"   {fn:26s} HTTP {status} {code_of(body):8s} {'refused' if kind == 'blocked' else ('absent (before 028)' if ok else 'MISMATCH: ' + kind)}")
    return bad


def check_catalog(db_url, before_028=False, out=print):
    """The catalog's own account, over the Postgres connection apply.py uses, in a read-only transaction."""
    import psycopg
    bad = 0
    with psycopg.connect(db_url, autocommit=False) as conn:
        conn.execute("set transaction read only")
        tables = conn.execute(
            "select c.relname, c.relrowsecurity, has_table_privilege('anon', c.oid, 'select') "
            "or has_any_column_privilege('anon', c.oid, 'select'), "
            "exists (select 1 from pg_policies p where p.schemaname = 'public' and p.tablename = c.relname "
            "        and p.cmd in ('SELECT', 'ALL') and (p.roles && array['anon', 'public']::name[])) "
            "from pg_class c join pg_namespace n on n.oid = c.relnamespace "
            "where n.nspname = 'public' and c.relkind in ('r', 'p', 'v', 'm') order by 1").fetchall()
        conn.rollback()
    out("5. the catalog: every table of schema public")
    found = set()
    for name, rls, anon_select, anon_policy in tables:
        found.add(name)
        want = EXPECTED.get(name)
        problems = []
        if not rls:
            problems.append("row-level security is OFF")
        if want is None:
            problems.append("not in the expected list (add it to EXPECTED as public or blocked)")
        elif want == "blocked" and (anon_select and anon_policy):
            problems.append("blocked in the list, but the anon key has the select privilege and a select policy")
        elif want == "blocked" and anon_policy:
            problems.append("blocked in the list, but a select policy names anon")
        elif want == "public" and not (anon_select and anon_policy):
            problems.append("public in the list, but the anon key lacks the select privilege or a select policy")
        bad += 1 if problems else 0
        out(f"   {name:26s} rls {'on ' if rls else 'OFF'} anon select {'yes' if anon_select else 'no '} policy {'yes' if anon_policy else 'no '}"
            f"{'  MISMATCH: ' + '; '.join(problems) if problems else ''}")
    for name in sorted(set(EXPECTED) - found):
        if before_028 and name in NEW_IN_028:
            continue
        bad += 1
        out(f"   {name:26s} MISMATCH: in the expected list, absent from the database")
    return bad


def check_functions(db_url, out=print):
    """Session 5156: the functions of schema public the anon key may execute, against ANON_FUNCTIONS. Read-only."""
    import psycopg
    bad = 0
    with psycopg.connect(db_url, autocommit=False) as conn:
        conn.execute("set transaction read only")
        rows = conn.execute(
            "select p.proname, pg_get_function_identity_arguments(p.oid) "
            "from pg_proc p join pg_namespace n on n.oid = p.pronamespace "
            "where n.nspname = 'public' and p.prokind = 'f' and has_function_privilege('anon', p.oid, 'execute') "
            "and not exists (select 1 from pg_depend d where d.objid = p.oid and d.deptype = 'e') order by 1").fetchall()
        conn.rollback()
    out("6. the catalog: every function of schema public the anon key may execute")
    found = set()
    for name, args in rows:
        found.add(name)
        want = ANON_FUNCTIONS.get(name)
        problem = ""
        if want is None:
            problem = "not in ANON_FUNCTIONS (revoke execute from anon, or list it with the credential it asks for)"
        elif want == "p_token" and not (args or "").startswith("p_token text"):
            problem = "listed as asking p_token, but p_token is not its first argument"
        bad += 1 if problem else 0
        out(f"   {name:26s} {(want or '?')[:60]}{'  MISMATCH: ' + problem if problem else ''}")
    for name in sorted(set(ANON_FUNCTIONS) - found):
        out(f"   {name:26s} listed, and the anon key may not execute it (or it is absent): nothing open, the list can lose it")
    return bad


def storage_list(origin, key, bucket):
    """(status, number of entries or None) of a list of a bucket's top folder with this key. A read."""
    req = urllib.request.Request(f"{origin}/storage/v1/object/list/{bucket}", method="POST", data=json.dumps({"prefix": "", "limit": 1}).encode(),
                                 headers={"apikey": key, "Authorization": f"Bearer {key}", "Content-Type": "application/json", "Accept": "application/json"})
    try:
        with urllib.request.urlopen(req, timeout=30) as r:
            status, body = r.status, r.read(20000).decode("utf-8", "replace")
    except urllib.error.HTTPError as e:
        status, body = e.code, e.read(2000).decode("utf-8", "replace")
    try:
        d = json.loads(body)
    except ValueError:
        return status, None
    return status, len(d) if isinstance(d, list) else None


def check_storage(db_url, origin, key, out=print, lister=storage_list):
    """Session 5172: the storage buckets against EXPECTED_BUCKETS, the policies on storage.objects, and what the anon
    key lists of a private bucket (nothing). Read-only: the catalog in a read-only transaction, one list a bucket."""
    import psycopg
    bad = 0
    with psycopg.connect(db_url, autocommit=False) as conn:
        conn.execute("set transaction read only")
        buckets = conn.execute("select id, public from storage.buckets order by 1").fetchall()
        policies = conn.execute(
            "select policyname, cmd, roles::text from pg_policies where schemaname = 'storage' and tablename = 'objects' "
            "and (roles && array['anon', 'public', 'authenticated']::name[]) order by 1").fetchall()
        rls = conn.execute("select c.relrowsecurity from pg_class c join pg_namespace n on n.oid = c.relnamespace "
                           "where n.nspname = 'storage' and c.relname = 'objects'").fetchall()
        conn.rollback()
    out("7. storage: the buckets, and what the anon key lists of each")
    if not rls or not rls[0][0]:
        bad += 1
        out("   storage.objects                MISMATCH: row-level security is OFF")
    for name, cmd, roles in policies:
        bad += 1
        out(f"   storage.objects                MISMATCH: the policy {name} ({cmd}) names {roles}: a policy for the anon key or a signed-in user opens objects")
    found = set()
    for bucket, public in buckets:
        found.add(bucket)
        want = EXPECTED_BUCKETS.get(bucket)
        problems = []
        if want is None:
            problems.append("not in EXPECTED_BUCKETS (list it as public or private)")
        elif want == "private" and public:
            problems.append("private in the list, PUBLIC in the database: every object is readable by its address")
        elif want == "public" and not public:
            problems.append("public in the list, private in the database: a page's file would not load")
        status, n = lister(origin, key, bucket)
        if want == "private" and not public and status == 200 and (n is None or n > 0):
            problems.append(f"the anon key lists it (HTTP {status}, {n} entries)")
        bad += 1 if problems else 0
        out(f"   {bucket:26s} {'public ' if public else 'private'} anon list HTTP {status}, {n if n is not None else '-'} entries"
            f"{'  MISMATCH: ' + '; '.join(problems) if problems else ''}")
    for bucket in sorted(set(EXPECTED_BUCKETS) - found):
        bad += 1
        out(f"   {bucket:26s} MISMATCH: in EXPECTED_BUCKETS, absent from the database")
    return bad


def schema_read(origin, key, schema, table):
    """(status, PostgREST's code) of a read of one row of schema.table with this key. A read; no function is called."""
    req = urllib.request.Request(f"{origin}/rest/v1/{table}?select=*&limit=1",
                                 headers={"apikey": key, "Authorization": f"Bearer {key}", "Accept-Profile": schema, "Accept": "application/json"})
    try:
        with urllib.request.urlopen(req, timeout=30) as r:
            r.read(200)
            return r.status, ""
    except urllib.error.HTTPError as e:
        return e.code, code_of(e.read(2000).decode("utf-8", "replace"))


def check_surface(db_url, origin, key, out=print, reader=schema_read):
    """Session 5173: the API serves no schema but public to the anon key; each scheduled job calls the dispatcher alone
    and holds no text shaped like a key; the dispatcher and the vault are not the anon key's. Read-only."""
    import psycopg
    bad = 0
    with psycopg.connect(db_url, autocommit=False) as conn:
        conn.execute("set transaction read only")
        jobs = conn.execute("select jobname, command from cron.job order by jobname").fetchall()
        closed = conn.execute(
            "select has_schema_privilege('anon', 'cron', 'usage'), has_schema_privilege('anon', 'vault', 'usage'), "
            "has_schema_privilege('anon', 'erw_private', 'usage'), "
            "coalesce((select bool_or(has_function_privilege('anon', p.oid, 'execute')) from pg_proc p "
            "join pg_namespace n on n.oid = p.pronamespace where n.nspname = 'public' and p.proname = 'erw_dispatch'), false)").fetchall()
        conn.rollback()
    out("8. what else the database could offer the anon key")
    for schema, table in CLOSED_SCHEMAS:
        status, code = reader(origin, key, schema, table)
        ok = status != 200
        bad += 0 if ok else 1
        out(f"   schema {schema:14s} a read of {table}: HTTP {status} {code}{'' if ok else '  MISMATCH: the API serves this schema to the anon key'}")
    for label, held in zip(("usage on schema cron", "usage on schema vault", "usage on schema erw_private", "execute on erw_dispatch"), closed[0] if closed else ()):
        bad += 1 if held else 0
        out(f"   the anon role, {label}: {'HELD  MISMATCH' if held else 'no'}")
    for name, command in jobs:
        problems = []
        if not JOB_COMMAND.match(command or ""):
            problems.append("its command is not one call of public.erw_dispatch")
        if KEY_SHAPED.search(command or ""):
            problems.append("its command holds text shaped like a key")
        bad += 1 if problems else 0
        out(f"   job {name:22s} {'ok' if not problems else 'MISMATCH: ' + '; '.join(problems)}")
    return bad


def main(argv=None):
    ap = argparse.ArgumentParser(description="Verify what the anon key can read (read-only)")
    ap.add_argument("--catalog", action="store_true", help="also read the catalog over SUPABASE_DB_URL")
    ap.add_argument("--before-028", action="store_true", help="migration 028 is not applied yet: its tables may be absent")
    args = ap.parse_args(argv)
    url, key = env("SUPABASE_URL"), env("SUPABASE_ANON_KEY")
    if not url or not key:
        print("SUPABASE_URL or SUPABASE_ANON_KEY is not set: nothing was read", file=sys.stderr)
        return 2
    u = urllib.parse.urlparse(url)
    bad = check_rest(Rest(f"{u.scheme}://{u.netloc}", key), args.before_028)
    if args.catalog:
        db_url = env("SUPABASE_DB_URL")
        if not db_url:
            print("--catalog needs SUPABASE_DB_URL: the catalog was not read", file=sys.stderr)
            return 2
        bad += check_catalog(db_url, args.before_028)
        bad += check_functions(db_url)
        bad += check_storage(db_url, f"{u.scheme}://{u.netloc}", key)
        bad += check_surface(db_url, f"{u.scheme}://{u.netloc}", key)
    print(f"{'PASS' if bad == 0 else 'FAIL'}: {bad} mismatch(es)")
    return 0 if bad == 0 else 1


if __name__ == "__main__":
    sys.exit(main())

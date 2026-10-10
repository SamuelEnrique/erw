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

Exit 0 when everything matches, 1 on any mismatch, 2 when the key or the address is not set. Never prints a key.
"""

import argparse
import json
import os
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
}
NEW_IN_028 = ("site_rate_counts", "site_usage_events", "site_usage_daily", "site_usage_salt")
LICENSED = ("series", "entities", "events", "latest_prices", "catalogue", "sources", "headers")
# internal tables loaded into the shared shapes: no row may come back by name
INTERNAL_BY_NAME = (("events", "api_cost_ledger"), ("events", "ferc_eqr_contracts"), ("events", "news_stories"),
                    ("series", "pjm_da_lmp"), ("entities", "ferc_eqr_contracts"))
# read functions behind the internal token: a wrong token must be refused (none of these writes)
TOKEN_FUNCTIONS = (("internal_costs", {}), ("internal_ask_spend", {}), ("internal_eqr_summary", {}),
                   ("thesis_list", {}), ("analysis_requests_list", {}), ("internal_usage", {}))
PROOF_TABLE = "site_api_calls"
WRONG_TOKEN = "verify-rls-wrong-token-0000000000000000"


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
    print(f"{'PASS' if bad == 0 else 'FAIL'}: {bad} mismatch(es)")
    return 0 if bad == 0 else 1


if __name__ == "__main__":
    sys.exit(main())

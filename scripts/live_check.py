#!/usr/bin/env python3
"""The live routes, end to end (session 276): subscribe, confirm and unsubscribe; the usage count and /internal/usage.

Energy Research Warehouse (ERW). Run against the deployed site (SITE_URL, else https://erw-flame.vercel.app), as a
browser would ask: same origin, a browser's user agent. Reads the database with the service key to see what each step
wrote; prints no secret, token or key.

    python scripts/live_check.py subscribe [--email delivered+erw@resend.dev]
        1. POST /api/subscribe (the form's fields)        the answer sends to /subscribe?state=check: stored, and the
                                                          confirmation email accepted by Resend
        2. the row in subscribers                         stored, not confirmed
        3. GET /api/subscribe/confirm?e=..&t=..           state=confirmed (the link the email carries, signed here with
                                                          EMAIL_TOKEN_SECRET as lib/emailtoken.ts signs it)
        4. the row                                        confirmed_at set
        5. POST /api/unsubscribe (confirm=yes)            state=unsubscribed
        6. the row and email_suppressions                 unsubscribed_at set; the address suppressed
    python scripts/live_check.py usage [--path /cost-of-power/battery]
        1. POST /api/usage {"event": "tool opened"}        204 (the route answers 204 whatever it records)
        2. site_usage_events, today                        the count of this path and event went up by one
        3. GET /internal/usage with the internal cookie    200, and the page names the path

The test address is Resend's own: an address at resend.dev that Resend accepts and delivers to nobody
(https://resend.com/docs/dashboard/emails/send-test-emails). It stays in the table as unsubscribed, and suppressed.
Exit 0 when every step held, 1 when one did not (each step printed with what it saw), 2 on bad input.
"""

import argparse
import datetime as dt
import hashlib
import hmac
import json
import os
import sys
import urllib.parse

import requests

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.abspath(os.path.join(HERE, ".."))
UA = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/130.0 Safari/537.36 ERW-live-check"
TEST_EMAIL = "delivered+erw276@resend.dev"


def env(name):
    v = os.environ.get(name)
    if v:
        return v
    try:
        with open(os.path.join(ROOT, ".env"), encoding="utf-8") as f:
            for ln in f:
                if ln.startswith(name + "="):
                    return ln.split("=", 1)[1].strip().strip('"')
    except OSError:
        pass
    return ""


def site():
    return (env("SITE_URL") or "https://erw-flame.vercel.app").rstrip("/")


def rest():
    base = env("SUPABASE_URL").rstrip("/")
    if base.endswith("/rest/v1"):
        base = base[: -len("/rest/v1")]
    key = env("SUPABASE_SERVICE_KEY")
    return base + "/rest/v1", {"apikey": key, "Authorization": f"Bearer {key}"}


def token(email, purpose, secret=None):
    """lib/emailtoken.ts: HMAC-SHA256 of lower(email) + ":" + purpose under EMAIL_TOKEN_SECRET, hex."""
    secret = secret if secret is not None else env("EMAIL_TOKEN_SECRET")
    return hmac.new(secret.encode(), f"{email.strip().lower()}:{purpose}".encode(), hashlib.sha256).hexdigest()


def internal_cookie(tok=None):
    """lib/release.ts digest(): SHA-256 of "erw-internal-view:" + INTERNAL_COSTS_TOKEN, hex."""
    tok = tok if tok is not None else env("INTERNAL_COSTS_TOKEN")
    return hashlib.sha256(f"erw-internal-view:{tok}".encode()).hexdigest()


def state_of(resp):
    loc = resp.headers.get("location", "")
    return urllib.parse.parse_qs(urllib.parse.urlparse(loc).query).get("state", [""])[0], loc


class Steps:
    def __init__(self):
        self.ok = True

    def __call__(self, name, good, saw):
        self.ok &= bool(good)
        print(f"{'ok  ' if good else 'FAIL'} {name}: {saw}")


def subscriber(email, http=requests):
    base, h = rest()
    r = http.get(f"{base}/subscribers", headers=h, timeout=30,
                 params={"select": "email,daily,weekly,topics,confirmed_at,unsubscribed_at", "email": f"eq.{email}"})
    r.raise_for_status()
    rows = r.json()
    return rows[-1] if rows else None


def suppressed(email, http=requests):
    base, h = rest()
    r = http.get(f"{base}/email_suppressions", headers=h, timeout=30, params={"select": "email", "email": f"eq.{email.lower()}"})
    r.raise_for_status()
    return bool(r.json())


def check_subscribe(email, http=requests):
    s, step = site(), Steps()
    head = {"Origin": s, "User-Agent": UA, "Content-Type": "application/x-www-form-urlencoded", "Sec-Fetch-Site": "same-origin"}
    form = [("email", email), ("daily", "on"), ("weekly", "on"), ("topic", "power_prices"), ("website", "")]
    r = http.post(f"{s}/api/subscribe", data=form, headers=head, allow_redirects=False, timeout=60)
    st, _ = state_of(r)
    step("POST /api/subscribe", r.status_code == 303 and st == "check", f"HTTP {r.status_code}, state={st}")
    row = subscriber(email, http)
    step("the row in subscribers", bool(row) and row["confirmed_at"] is None and row["unsubscribed_at"] is None,
         {k: row[k] for k in ("daily", "weekly", "topics", "confirmed_at", "unsubscribed_at")} if row else "no row")
    r = http.get(f"{s}/api/subscribe/confirm", params={"e": email, "t": token(email, "confirm")}, headers={"User-Agent": UA},
                 allow_redirects=False, timeout=60)
    st, _ = state_of(r)
    step("GET /api/subscribe/confirm", r.status_code == 303 and st == "confirmed", f"HTTP {r.status_code}, state={st}")
    row = subscriber(email, http)
    step("confirmed_at set", bool(row and row["confirmed_at"]), row["confirmed_at"] if row else "no row")
    r = http.post(f"{s}/api/unsubscribe", data={"e": email, "t": token(email, "unsubscribe"), "confirm": "yes"},
                  headers=head, allow_redirects=False, timeout=60)
    st, _ = state_of(r)
    step("POST /api/unsubscribe", r.status_code == 303 and st == "unsubscribed", f"HTTP {r.status_code}, state={st}")
    row = subscriber(email, http)
    step("unsubscribed_at set, and the address suppressed", bool(row and row["unsubscribed_at"]) and suppressed(email, http),
         f"unsubscribed_at={row['unsubscribed_at'] if row else None}")
    return step.ok


def usage_count(path, event, http=requests):
    base, h = rest()
    day = dt.datetime.now(dt.timezone.utc).date().isoformat()
    r = http.get(f"{base}/site_usage_events", headers=h, timeout=30,
                 params={"select": "n", "day": f"eq.{day}", "path": f"eq.{path}", "event": f"eq.{event}"})
    r.raise_for_status()
    return sum(int(x.get("n") or 1) for x in r.json())


def check_usage(path, http=requests):
    s, step = site(), Steps()
    event = "tool opened"
    before = usage_count(path, event, http)
    r = http.post(f"{s}/api/usage", data=json.dumps({"event": event, "path": path}), allow_redirects=False, timeout=60,
                  headers={"Origin": s, "User-Agent": UA, "Content-Type": "application/json", "Sec-Fetch-Site": "same-origin"})
    step("POST /api/usage", r.status_code == 204 and "set-cookie" not in {k.lower() for k in r.headers}, f"HTTP {r.status_code}, no cookie set")
    after = usage_count(path, event, http)
    step("the count of the path and event, today", after == before + 1, f"{before} before, {after} after")
    r = http.get(f"{s}/internal/usage", headers={"User-Agent": UA, "Cookie": f"erw_internal={internal_cookie()}"}, timeout=60, allow_redirects=False)
    step("GET /internal/usage, internal view", r.status_code == 200 and path in r.text, f"HTTP {r.status_code}, names {path}: {path in r.text}")
    return step.ok


def main(argv=None):
    ap = argparse.ArgumentParser(description="ERW: the live routes, end to end (session 276)")
    sub = ap.add_subparsers(dest="cmd", required=True)
    a = sub.add_parser("subscribe")
    a.add_argument("--email", default=TEST_EMAIL)
    b = sub.add_parser("usage")
    b.add_argument("--path", default="/cost-of-power/battery")
    args = ap.parse_args(argv)
    if args.cmd == "subscribe":
        if not args.email.endswith("@resend.dev"):
            ap.error("only Resend's own test addresses (...@resend.dev): this sends a real email")
        for k in ("SUPABASE_URL", "SUPABASE_SERVICE_KEY", "EMAIL_TOKEN_SECRET"):
            if not env(k):
                ap.error(f"{k} is not set")
        ok = check_subscribe(args.email)
    else:
        for k in ("SUPABASE_URL", "SUPABASE_SERVICE_KEY", "INTERNAL_COSTS_TOKEN"):
            if not env(k):
                ap.error(f"{k} is not set")
        ok = check_usage(args.path)
    print(f"{args.cmd}: {'every step held' if ok else 'a step did not hold'} against {site()}")
    return 0 if ok else 1


if __name__ == "__main__":
    sys.exit(main())

#!/usr/bin/env python3
"""Samuel's own sending domain in Resend (session 276): the exact DNS records, from Resend itself.

Energy Research Warehouse (ERW). docs/runbook.md, "The sending domain". Resend writes a domain's DKIM key when the
domain is added to the account, so the exact records exist only after `add`. This prints them as Resend returns them,
one line a record, to copy into the DNS host. RESEND_API_KEY from the environment or .env; never printed.

    python scripts/resend_domain.py list                    the domains of the account and their status (read only)
    python scripts/resend_domain.py add mail.example.org    adds the domain (region us-east-1) and prints its records
    python scripts/resend_domain.py records mail.example.org   the records again, with each one's status
    python scripts/resend_domain.py verify mail.example.org    asks Resend to check the DNS now

`add` and `verify` are a person's: they change the Resend account. Session 276 ran `list` only.
"""

import argparse
import os
import sys

import requests

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.abspath(os.path.join(HERE, ".."))
API = "https://api.resend.com"


def key():
    v = os.environ.get("RESEND_API_KEY", "")
    if not v:
        try:
            with open(os.path.join(ROOT, ".env"), encoding="utf-8") as f:
                for ln in f:
                    if ln.startswith("RESEND_API_KEY="):
                        v = ln.split("=", 1)[1].strip().strip('"')
        except OSError:
            pass
    return v


def headers():
    return {"Authorization": f"Bearer {key()}", "Content-Type": "application/json"}


def lines(domain):
    """One line a record: type, host (as the DNS host wants it, relative to the zone), value, priority, status."""
    out = [f"{'Type':<5} {'Host':<36} {'Priority':<8} {'Status':<10} Value"]
    for r in domain.get("records", []):
        out.append(f"{r.get('type', ''):<5} {r.get('name', ''):<36} {str(r.get('priority') or ''):<8} {r.get('status', ''):<10} {r.get('value', '')}")
    return out


def find(name, http=requests):
    r = http.get(f"{API}/domains", headers=headers(), timeout=30)
    r.raise_for_status()
    for d in r.json().get("data", []):
        if d.get("name") == name:
            return d
    return None


def main(argv=None, http=requests):
    ap = argparse.ArgumentParser(description="ERW: the sending domain in Resend (session 276)")
    ap.add_argument("cmd", choices=["list", "add", "records", "verify"])
    ap.add_argument("name", nargs="?")
    a = ap.parse_args(argv)
    if not key():
        ap.error("RESEND_API_KEY is not set")
    if a.cmd == "list":
        r = http.get(f"{API}/domains", headers=headers(), timeout=30)
        r.raise_for_status()
        data = r.json().get("data", [])
        for d in data:
            print(f"{d.get('name')}: {d.get('status')} (region {d.get('region')}, added {d.get('created_at')})")
        print(f"{len(data)} domain(s) in the Resend account")
        return 0
    if not a.name:
        ap.error(f"{a.cmd} needs the domain, for example mail.example.org")
    if a.cmd == "add":
        r = http.post(f"{API}/domains", headers=headers(), json={"name": a.name, "region": "us-east-1"}, timeout=30)
        r.raise_for_status()
        d = r.json()
    else:
        d = find(a.name, http)
        if d is None:
            print(f"{a.name} is not in the Resend account: run add first")
            return 1
        if a.cmd == "verify":
            http.post(f"{API}/domains/{d['id']}/verify", headers=headers(), timeout=30).raise_for_status()
        r = http.get(f"{API}/domains/{d['id']}", headers=headers(), timeout=30)
        r.raise_for_status()
        d = r.json()
    print(f"{d.get('name')}: {d.get('status')}")
    for ln in lines(d):
        print(ln)
    return 0


if __name__ == "__main__":
    sys.exit(main())

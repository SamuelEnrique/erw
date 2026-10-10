#!/usr/bin/env python3
"""Scan the whole git history for things shaped like secrets, without ever writing a secret's value.

Energy Research Warehouse (ERW), session 177 (the security audit, docs/reviews/2026-10-10-security.md).

    python scripts/scan_git_secrets.py [--repo .] [--out runs/session177/git_secrets.csv] [--env .env --env site/.env.local]

Reads `git log -p --all` once, line by line, and tests every ADDED line against patterns for the kinds of secret
this project holds: a Supabase key (a JWT, whose payload is decoded only to read its "role"), an Anthropic key, a
GitHub token, a Resend key, a Redivis token, a Postgres address holding a password, any address holding a password,
a private key block, and an assignment of a long literal to a variable named like one of the project's secrets.

With --env (one or more files of NAME=value lines, never committed), every value of 12 characters or more held in
those files is also searched for, exactly, in every added line of the history: the strongest test there is that a
key this machine uses was never committed. Such a hit is reported as kind "known_value" with its variable's name.

What is written for a hit: the commit, the file, the kind, and a fingerprint (the first 8 hexadecimal characters of
the SHA-256 of the matched text, so two hits of the same value can be told to be the same value). Never the value,
never a part of it. Exit 0 when no hit, 1 when there are hits, 2 on bad input.
"""

import argparse
import base64
import csv
import hashlib
import json
import os
import re
import subprocess
import sys

NAMES = ("SUPABASE_SERVICE_KEY|SUPABASE_ANON_KEY|SUPABASE_DB_URL|SUPABASE_ACCESS_TOKEN|ANTHROPIC_API_KEY|GH_TOKEN|"
         "GITHUB_TOKEN|REDIVIS_API_TOKEN|RESEND_API_KEY|EMAIL_TOKEN_SECRET|INTERNAL_COSTS_TOKEN|ASK_VISITOR_SALT|"
         "USAGE_SALT|EIA_API_KEY|PJM_API_KEY|FRED_API_KEY|NOAA_TOKEN|VERCEL_TOKEN|DEPLOY_HOOK")

PATTERNS = [
    ("jwt", re.compile(r"eyJ[A-Za-z0-9_-]{8,}\.eyJ[A-Za-z0-9_-]{8,}\.[A-Za-z0-9_-]{16,}")),
    ("supabase_new_key", re.compile(r"\bsb_(?:secret|publishable)_[A-Za-z0-9_-]{20,}")),
    ("supabase_access_token", re.compile(r"\bsbp_[a-f0-9]{30,}")),
    ("anthropic_key", re.compile(r"sk-ant-[A-Za-z0-9_-]{20,}")),
    ("github_token", re.compile(r"\b(?:gh[pousr]_[A-Za-z0-9]{30,}|github_pat_[A-Za-z0-9_]{40,})")),
    ("resend_key", re.compile(r"\bre_[A-Za-z0-9]{8,}_[A-Za-z0-9]{16,}")),
    ("vercel_hook", re.compile(r"api\.vercel\.com/v1/integrations/deploy/[A-Za-z0-9_/-]{20,}")),
    ("postgres_url_password", re.compile(r"postgres(?:ql)?://[^\s:@/'\"]+:[^\s@/'\"<>{}$%]{6,}@[^\s'\"]+")),
    ("url_password", re.compile(r"\b(?:https?|ftp|smtp|redis|mongodb(?:\+srv)?)://[^\s:@/'\"]+:[^\s@/'\"<>{}$%]{6,}@[A-Za-z0-9.-]+")),
    ("private_key_block", re.compile(r"-----BEGIN (?:RSA |EC |OPENSSH |DSA |)PRIVATE KEY-----")),
    ("named_literal", re.compile(r"\b(?:" + NAMES + r")\b\s*[:=]\s*[\"']?([A-Za-z0-9_\-./+=]{20,})")),
]

# a named assignment whose right side is plainly not a value: a read of the environment, a placeholder, a secret store
NOT_A_VALUE = re.compile(r"^(?:process\.env|os\.environ|os\.getenv|env\(|secrets\.|\$\{\{|\$\{|\$[A-Z_]|<|your[-_]|xxx|\.\.\.|"
                         r"dotenv|example|placeholder|changeme|None|null|undefined|true|false)", re.I)


def jwt_role(token):
    """The "role" (and issuer) a JWT's payload names, or "" when it cannot be read. Nothing else of it is kept."""
    try:
        part = token.split(".")[1]
        part += "=" * (-len(part) % 4)
        payload = json.loads(base64.urlsafe_b64decode(part.encode("ascii")))
        return f"role={payload.get('role', '?')} iss={payload.get('iss', '?')}"
    except Exception:  # not a payload this can read: the hit is still reported, without a role
        return ""


def fingerprint(text):
    return hashlib.sha256(text.encode("utf-8", "replace")).hexdigest()[:8]


def known_values(paths):
    """{value: variable name} for every value of 12 characters or more in the given NAME=value files."""
    out = {}
    for path in paths:
        with open(path, encoding="utf-8") as f:
            for line in f:
                line = line.strip()
                if not line or line.startswith("#") or "=" not in line:
                    continue
                name, value = line.split("=", 1)
                value = value.strip().strip("\"'")
                m = re.match(r"[a-z+]+://[^:/@]+:([^@]+)@", value)
                if m and len(m.group(1)) >= 8:               # an address holding a password: the password alone too
                    out.setdefault(m.group(1), name.strip() + " (the password in it)")
                if len(value) >= 12 and (m or not re.match(r"https?://", value)) and "@" not in value.split("://")[0]:
                    out.setdefault(value, name.strip())
    return out


def scan(repo, known=None):
    """Every hit of the history, as dicts. Streams git's output: the history is never held whole in memory."""
    known = known or {}
    cmd = ["git", "-C", repo, "log", "-p", "--all", "--no-color", "--no-ext-diff", "--format=commit %H %cI"]
    proc = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.DEVNULL)
    commit = when = path = ""
    hits, seen = [], set()
    for raw in proc.stdout:
        line = raw.decode("utf-8", "replace").rstrip("\n")
        if line.startswith("commit ") and len(line) > 48 and re.fullmatch(r"[0-9a-f]{40}", line[7:47]):
            commit, when = line[7:47], line[48:]
            continue
        if line.startswith("+++ "):
            path = line[6:] if line.startswith("+++ b/") else line[4:]
            continue
        if not line.startswith("+") or line.startswith("+++"):
            continue
        for value, name in known.items():
            if value in line:
                key = (commit, path, "known_value", fingerprint(value))
                if key not in seen:
                    seen.add(key)
                    hits.append({"commit": commit, "committed": when, "file": path, "kind": "known_value",
                                 "fingerprint": key[3], "length": len(value), "note": "variable " + name})
        for kind, pat in PATTERNS:
            for m in pat.finditer(line):
                value = m.group(1) if kind == "named_literal" else m.group(0)
                if kind == "named_literal" and NOT_A_VALUE.match(value):
                    continue
                note = jwt_role(value) if kind == "jwt" else ""
                if kind == "named_literal":
                    note = "variable " + re.match(r"\b(" + NAMES + r")\b", m.group(0)).group(1)
                key = (commit, path, kind, fingerprint(value))
                if key in seen:
                    continue
                seen.add(key)
                hits.append({"commit": commit, "committed": when, "file": path, "kind": kind,
                             "fingerprint": key[3], "length": len(value), "note": note})
    proc.wait()
    if proc.returncode != 0:
        raise RuntimeError(f"git log exited {proc.returncode}")
    return hits


def main(argv=None):
    ap = argparse.ArgumentParser(description="Scan the git history for secrets; values are never written")
    ap.add_argument("--repo", default=".")
    ap.add_argument("--out", default="")
    ap.add_argument("--env", action="append", default=[], help="a NAME=value file whose values are searched for exactly")
    args = ap.parse_args(argv)
    if not os.path.isdir(args.repo):
        print(f"not a directory: {args.repo}", file=sys.stderr)
        return 2
    known = known_values(args.env)
    hits = scan(args.repo, known)
    print(f"{len(known)} known value(s) searched for exactly, from {len(args.env)} file(s)")
    fields = ["commit", "committed", "file", "kind", "fingerprint", "length", "note"]
    if args.out:
        os.makedirs(os.path.dirname(os.path.abspath(args.out)), exist_ok=True)
        with open(args.out, "w", newline="", encoding="utf-8") as f:
            w = csv.DictWriter(f, fieldnames=fields)
            w.writeheader()
            w.writerows(hits)
    by = {}
    for h in hits:
        by.setdefault((h["kind"], h["fingerprint"], h["note"]), []).append(h)
    print(f"{len(hits)} hit(s), {len(by)} distinct value(s)")
    for (kind, fp, note), rows in sorted(by.items()):
        files = sorted({r["file"] for r in rows})
        first = min(rows, key=lambda r: r["committed"])
        print(f"  {kind} #{fp} {note}: {len(rows)} hit(s) in {len(files)} file(s); first {first['commit'][:10]} "
              f"{first['committed'][:10]} {first['file']}")
    return 1 if hits else 0


if __name__ == "__main__":
    sys.exit(main())

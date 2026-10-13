#!/usr/bin/env python3
"""One line by email when a session's report is pushed (session 82).

Energy Research Warehouse (ERW). A session that runs unattended tells its owner it has finished by one short email,
through the sender the digest already uses (warehouse/news/email_digest.py: Resend, RESEND_API_KEY, from DIGEST_FROM).
It goes to the fixed recipients only (DIGEST_RECIPIENTS in .env or the environment): never to a subscriber, and no
address is ever printed or logged.

    python scripts/notify.py --session 82 --branch wip/082-land --line "the night's first session landed; two steps skipped"
    python scripts/notify.py --session 82 --branch wip/082-land --line "..." --dry-run     # prints the message, sends nothing

Session 202, the one alert policy (docs/machines.md, "One alert policy"): successes send nothing. A session that
finished is a success, and the morning summary lists its landing; so this script sends only with --failed, for a
session that could not finish, and otherwise prints why it did not send and exits 0.

Session 243, the email rule (the owner's ruling of 12 October 2026; docs/machines.md, "The email rule"): this script
sends nothing at all now, with or without --failed. It prints why and exits 0; --dry-run still prints the message a
session would have sent. A person hears of a chain once, 15 minutes after its machine went idle
(python scripts/alert.py ready).

The message is the one line and the report's address on GitHub, nothing else: no number that is not in the line, no
attachment. Exit 0 when every fixed recipient was sent to; 1 when nothing could be sent (no key, no recipient, or
Resend refused), with the reason on stderr; 2 on bad input. It makes no model call and writes no file.
"""

import argparse
import os
import sys

import requests

ROOT = os.path.abspath(os.path.join(os.path.dirname(os.path.abspath(__file__)), ".."))
sys.path.insert(0, os.path.join(ROOT, "warehouse", "news"))
sys.path.insert(0, os.path.join(ROOT, "warehouse", "connectors"))

REPO = "https://github.com/SamuelEnrique/erw"
MAX_LINE = 300


def message(session, branch, line):
    """The subject and the body: one line, and where the report is."""
    line = " ".join(str(line).split())
    if not line or len(line) > MAX_LINE:
        raise ValueError(f"the line must be 1 to {MAX_LINE} characters, on one line")
    if chr(0x2014) in line:
        raise ValueError("no em dash in an ERW message")
    url = f"{REPO}/blob/{branch}/archive/sessions/SESSION_{session}_REPORT.md"
    subject = f"ERW session {session}: report pushed"
    return subject, f"{line}\n\n{url}\n"


def send(session, branch, line, dry_run=False, post=requests.post, env=None):
    """Send it to each fixed recipient, one message each. Returns the number sent."""
    import email_digest as ed
    env = env or ed.env
    subject, body = message(session, branch, line)
    if dry_run:
        print(f"Subject: {subject}\n\n{body}")
        return 0
    key = env("RESEND_API_KEY")
    to = [a.strip() for a in env("DIGEST_RECIPIENTS").split(",") if a.strip()]
    if not key or not to:
        raise RuntimeError("not sent: " + ", ".join(n for n, v in (("RESEND_API_KEY", key), ("DIGEST_RECIPIENTS", to)) if not v) + " not set")
    sender = env("DIGEST_FROM") or "ERW Energy Digest <onboarding@resend.dev>"
    sent = 0
    for addr in to:
        r = post(ed.RESEND, headers={"Authorization": f"Bearer {key}"}, timeout=60,
                 json={"from": sender, "to": [addr], "subject": subject, "text": body})
        if r.status_code >= 300:
            raise RuntimeError(f"Resend HTTP {r.status_code} after {sent} of {len(to)} sent")
        sent += 1
    return sent


def main(argv=None):
    ap = argparse.ArgumentParser(description="One line by email when a session's report is pushed")
    ap.add_argument("--session", required=True, type=int)
    ap.add_argument("--branch", required=True, help="the branch the report was pushed on")
    ap.add_argument("--line", required=True, help="the one line")
    ap.add_argument("--dry-run", action="store_true")
    ap.add_argument("--failed", action="store_true", help="the session could not finish: the only case that is sent (session 202)")
    a = ap.parse_args(argv)
    if not a.dry_run:
        # session 243, the email rule: a session, finished or failed, sends nothing; --failed is kept so a chain that names it still runs
        print(f"notify: session {a.session}: not sent ({'it could not finish' if a.failed else 'it finished'}). A session sends no email "
              "(docs/machines.md, \"The email rule\", session 243): its report says what happened, and the machine's one email "
              "follows 15 minutes after the chain ends.")
        return 0
    try:
        n = send(a.session, a.branch, a.line, a.dry_run)
    except ValueError as exc:
        print(f"notify: {exc}", file=sys.stderr)
        return 2
    except Exception as exc:
        print(f"notify: {exc}", file=sys.stderr)
        return 1
    if not a.dry_run:
        print(f"notify: session {a.session}, sent to {n} fixed recipient{'s' if n != 1 else ''}")
    return 0


if __name__ == "__main__":
    sys.exit(main())

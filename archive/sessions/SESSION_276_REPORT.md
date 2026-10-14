# Session 276 report: subscribe, the email domain, the usage count

14 October 2026, 10:36 to 10:50 UTC, unattended, on lab-desktop (the data machine), the sixth session of the overnight chain of 14 October, built in a worktree (`../erw-276`) while session 273's pull ran. Branch `task/276-subscribe-analytics`. Model spend USD 0: no model call. Requests: the live site (three subscribe routes, the usage route, `/internal/usage`), Supabase (reads with the service key), Resend (`GET /domains`, `GET /emails`, and the one confirmation email the site sent to Resend's test address). No page edited.

## Read these first

- **Subscribe, confirm and unsubscribe work end to end on the live routes.** `python scripts/live_check.py subscribe`, 10:38 UTC, exit 0: the form's POST answered `state=check`; the row was stored unconfirmed; the signed confirm link answered `state=confirmed` and set `confirmed_at`; the unsubscribe answered `state=unsubscribed`, set `unsubscribed_at` and put the address in `email_suppressions`. Resend's record of the confirmation email: delivered.
- **The test address is Resend's own** (`delivered+erw276@resend.dev`, delivered to nobody). It stays in `subscribers` as unsubscribed and suppressed.
- **The cookieless usage count is proven live with one real event.** `python scripts/live_check.py usage`, exit 0: `POST /api/usage` answered 204 and set no cookie; today's count of "tool opened" on `/cost-of-power/battery` went from 102 to 103 in `site_usage_events`; `/internal/usage` in the internal view answered 200 and names the page. The event is counted under "In review (not opened)", as a visitor's would be.
- **The DNS records for your own sending domain are in `docs/runbook.md`, with one blank I could not fill: the DKIM key.** Resend writes it when a domain is added to the account, and no domain is (`GET /domains`: 0), and no domain of yours is named anywhere in the repository. The MX, SPF and DMARC records are written in full for `mail.<your domain>`; `python scripts/resend_domain.py add mail.<your domain>` adds it and prints every record exactly as Resend returns it.
- **Until the domain is verified, a real visitor's subscription is stored and its confirmation email is not sent** (`onboarding@resend.dev` sends only to the account's own address and Resend's test addresses): the visitor sees "unsent".

## What to review

- `docs/runbook.md`, the two new sections at its end: "The sending domain" and "The live routes, end to end".

## Checks

| What | Exit | Notes |
|---|---|---|
| `python scripts/precheck.py --what "session 276"` | 0 | six of six |
| `python scripts/live_check.py subscribe` | 0 | six steps held |
| `python scripts/live_check.py usage` | 0 | three steps held; 102 to 103 |
| `python scripts/resend_domain.py list` | 0 | 0 domains |
| `python -m unittest tests.test_session276` | 0 | 5 tests, no network |

## Decisions made without you

1. **Resend's test address, not a real one:** it proves the route, the email's acceptance and its delivery event without mailing a person.
2. **The confirm and unsubscribe links were signed here** with the secret in `.env`, as `lib/emailtoken.ts` signs them; the test reads no email.
3. **The internal view was opened with the cookie's digest** of the token in `.env`, as `/internal/unlock` sets it; no token was put in an address.
4. **No domain was added to Resend:** none is named, and adding one changes your account. The script that adds it is written and not run.
5. **The checks are a script with tests,** so the same proof can be run after the domain is verified (the runbook's step 5).

## For Samuel's ruling

1. The domain (and subdomain) to send from; then the runbook's five steps.
2. Keep the test row of `delivered+erw276@resend.dev` (unsubscribed), or delete it.

## Files

- New: `scripts/live_check.py`, `scripts/resend_domain.py`, `tests/test_session276.py`, this report.
- Changed: `docs/runbook.md` (two sections added at the end).

## The landing

- In session 273's report.

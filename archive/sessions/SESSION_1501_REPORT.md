# Session 1501 report: security, the headers and the internal routes

Energy Research Warehouse (ERW), session 1501, chain 158, samueloldlaptop, 6 November 2026, 10:08 to 10:16 UTC (during session 1500's gate). Model: Claude Opus 5.5 (this window's). Model spend USD 0. No warehouse data written; nothing sent or posted; no web request. Branch `wip/1501-security`, cut from `wip/1497-paths`.

## What it did, with commits

- `6dd1f9f1f`:
  - **M4 closed**: `Content-Security-Policy-Report-Only` dropped from `site/next.config.ts`. Its week beside the enforced policy, from session 301, was due to end on or after 26 October 2026. The enforced policy is now the one header.
  - `check-security.mjs` now wants no report-only header. The three tests that pinned the header (`test_session177`, `301`, `421`) read its absence. `docs/security.md`'s M4 row says so.
  - `tests/test_session1501.py`: the headers (one policy, the five others); **every internal route is guarded**. Eleven of the fourteen pages and routes under `site/app/internal/` answer only the internal view's cookie (404 otherwise); the other three are the doors (`open`, `unlock`, `lock`); the proxy leaves `/internal/` to them.
  - The cookie is `httpOnly`, `sameSite: lax`, `secure` on https and 90 days old at most (`MAX_AGE` in `lib/release.ts`).
- `check-csp.mjs` is the gate's step on every landing: 97 pages, 0 violations at session 1493's.

## Decisions made without you

- L4 (the cookie a fixed digest for 90 days), L5 and H1 (the old link and the token's rotation) stay yours, as the list says.

## For Samuel's ruling

- None new.

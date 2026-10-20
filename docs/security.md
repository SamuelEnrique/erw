# Security: every item, closed or open

Energy Research Warehouse (ERW). The one list of the security review's items and where each stands. Written by session 371 (20 October 2026, the roadmap's item 7) from the review itself, [`docs/reviews/2026-10-10-security.md`](reviews/2026-10-10-security.md) (session 177, with the four "Session 301" lines of 19 October), and checked again against the code, the database's catalog and the site on 20 October 2026. The review keeps the full account of each item (what is exposed, the fix, the risk of the fix); this file keeps its state. A session that closes an item changes its row here and names its commit.

States: **closed** (fixed and verified, with its commit or session), **open: Samuel** (needs the owner's ruling or a step only he can take; the choice is spelled out below), **open: a session** (needs no ruling; why it was not done yet is said), **noted** (nothing to do until something else happens).

## How session 371 checked

Every read below is a read: nothing was written to the database, to Supabase Auth or to Vercel. The outputs are in `runs/chain_oct20d/s371/` on the code machine (not in git).

| What | How | Result |
|---|---|---|
| Row-level security, every table of schema `public` | `python warehouse/supabase/verify_rls.py --catalog` | exit 0, 0 mismatches: row-level security on for all 25 tables; the anon key reads the eight public ones and is refused (401, 42501) on every other |
| Migration 034's effects (H3, M1, L6) | the catalog, in a read-only transaction | no insert policy on any table of `public`; the anon role holds no `INSERT` on `site_api_calls`, `game_scores`, `game_plays`, `subscribers`; no `UPDATE` or `USAGE` on any sequence of `public`; no `EXECUTE` on `site_ask_admit` |
| The default privileges (M6) | `pg_default_acl` | unchanged: what `postgres` or `supabase_admin` creates in `public` is granted to `anon` and `authenticated` (tables `arwdDxtm`, sequences `rwU`, functions `X`) |
| The `search_path` of the lock and scheduler functions (L7) | `pg_proc.proconfig` | unchanged: `erw_lock_*` and `erw_db_size` pin `search_path=public`, `erw_dispatch` `public, extensions` |
| Sign-ups in Supabase Auth (L8) | `GET /auth/v1/settings` with the anon key | `disable_signup: false`, the email provider on, `mailer_autoconfirm: false` |
| The chart library's integrity (M5) | the file fetched once from cdnjs, hashed, and cdnjs's own published hash read from `api.cdnjs.com` | 1,034,102 bytes; its SHA-384 is `ECHARTS_SRI` in `site/components/echarts.ts`; its SHA-512 equals the SRI cdnjs publishes for `echarts/5.6.0/echarts.min.js` |
| The site's dependencies (H2, L9, L10) | `npm audit --json` in `site/` after `npm ci` | 5 advisories, all high, all one chain: `eslint-config-next` 16.3.8 through `@next/eslint-plugin-next`, `fast-glob`, `micromatch` and `braces` (GHSA-vfj7-8cjw-p6xm), that is L9; the only fix offered is `eslint-config-next` 14.2.35, a major step back. Nothing on `next`, `react` or any package the site ships |
| The headers, the form, the internal pages, the routes' refusals | `node scripts/check-security.mjs` and `node scripts/check-csp.mjs` on the local build | see the session report, `archive/sessions/SESSION_371_REPORT.md` |

## The list

| # | Item | State | Commit or proof |
|---|---|---|---|
| H1 | The internal token travels in addresses | **open: Samuel** (the old link's retirement and the token's rotation); the scripts' part closed | session 301 (`52174f26`): every check script opens the internal view by the form; S2 below closes the five pages that still needed the token |
| H2 | Next.js advisories | closed | session 177: `next` and `eslint-config-next` 16.3.8; `npm audit` of 20 October: no advisory on `next` (above) |
| H3 | The anon key could write the cost ledger | closed | site side session 301 (`52174f26`); migration 034 applied (catalog read of 20 October above). One look remains for Samuel: item 3 below |
| M1 | The same for the game's tables, the subscribers and the question counter | closed | with H3 |
| M2 | Limits per address held in one instance's memory | closed | session 177, `site/lib/guard.ts`; migration 028 applied (`site_rate_counts` in the catalog) |
| M3 | The sign-up form as a mail cannon | closed | session 177; the day's ceiling with 028 |
| M4 | Security headers | closed | session 177; the full policy enforced in session 301 (`52174f26`). One step left, **open: a session**: drop `Content-Security-Policy-Report-Only` from `site/next.config.ts` (`CSP_REPORT_ONLY`) on or after 26 October 2026, a week after it was set beside the enforced header, then run `check-security.mjs` (it asks for the report-only header today, so its line changes with it) and `check-csp.mjs`. Not done on 20 October: the week is not over |
| M5 | The chart library from a public host | closed | session 177 (`ECHARTS_SRI`); the "one look by a person" the review asked for is done: cdnjs's published hash matches (above) |
| M6 | A new table is open to the anon key until someone closes it | **open: Samuel** | item 4 below |
| M7 | Python dependencies with advisories | **open: Samuel** | item 5 below; not read again on 20 October |
| M8 | A script through a news feed or a model's words | closed | session 177, `site/lib/markdown.ts` |
| L1 | Input sizes | closed | session 177 |
| L2 | Same-origin on the internal routes | closed | session 177 |
| L3 | `/terms` on the address | closed | session 177 |
| L4 | The internal cookie is a fixed digest for 90 days | **open: Samuel** | item 6 below |
| L5 | The old link compares the token with `!==` | **open: Samuel**, with H1 | goes with the link's retirement (H1): the link's code is pinned word for word by `tests/test_session177.py` until then. The pages' `?token=` checks (`token !== want`) go with it |
| L6 | The anon key's `UPDATE` on four sequences | closed | migration 034, applied (catalog read above) |
| L7 | `search_path = public` on the lock and scheduler functions | **open: Samuel** | item 7 below |
| L8 | Sign-ups enabled in Supabase Auth | **open: Samuel** | item 8 below |
| L9 | The linter's packages (`braces`, `micromatch`, `fast-glob`) | **open: Samuel** (listed, not applied) | only `npm audit fix --force` changes them, and it installs `eslint-config-next` 14: a major step back for the linter; the packages run on a developer's machine, never in the site. Item 9 below |
| L10 | `sharp`, `source-map-js` | closed | session 177 (`npm audit fix`) |
| L11 | No `robots.txt` | noted | every page is in review and sent `X-Robots-Tag: noindex`; a `robots.txt` comes with the first live page |
| L12 | `check-values.mjs` could not run | closed | session 177 |
| L13 | A long read by the anon key | noted | the anon role's 3-second statement timeout is the control |
| S1 | The proxy and the battery page compared the internal cookie with `===` (found by session 371) | closed | `a04d463e`: `cookieOpens` in `site/lib/release.ts`, the same constant-time comparison `internalOk` and the form's door already made |
| S2 | Five internal addresses still needed `?token=`; the refund finder wrote the token into its own links and form, and `check-values.mjs` opened the two drafts with it, so each landing's check against production put the production token in a production address (found by session 371) | closed | `e5eeac60`: `/severance/finder`, `/severance/finder/download`, `/severance/lease/real`, `/reports/draft/shape-premium` and `/reports/draft/ai-gigawatts` open with the internal cookie (an address with `?token=` still opens them); the finder writes the token into a link only when its own address brought it; `check-values.mjs` reads the drafts with the cookie |
| S4 | `check-csp.mjs` proved the chart library's integrity hash on `/storage`, which has drawn its charts in SVG since the shared chart set moved and no longer loads the library, so the proof failed on a page that no longer used it (found by session 371) | closed | session 371's last commit: the probe opens `/map` (`app/map/ProjectMap.tsx`, `useEChart`), which loads the library from cdnjs with its hash; `check-csp.mjs` exit 0 on the local build, "/map: the chart library loaded and drew" |
| S3 | Three checks prove "a token in the address opens nothing" with the real token (`check-internal-findings.mjs`, `check-internal-health.mjs`, `check-internal-waits.mjs`); run against production, that request writes the token into the host's request log (found by session 371) | noted | the proof needs the real token, and the checks are run against a local build; run against production only after the rotation of H1, or not at all |

## What needs Samuel, with the choice

1. **H1, the old link.** Use `/internal/open` once on production. If it opens the internal view: (a) retire the GET of `site/app/internal/unlock/route.ts` and the `token !== want` branches of `/internal/costs`, `/internal/ask`, `/internal/usage`, the two drafts and the severance pages (a session's work once you say so; L5 goes with it), or (b) keep the link until the review phase ends. Nothing in the site or its checks needs the link any more (S2).
2. **H1, the rotation.** After (a): a new `INTERNAL_COSTS_TOKEN` in Vercel, `.env`, `site/.env.local`, and `erw_private.settings` (the one statement of `apply.py`, by hand; the full run stops at migration 014). Every reviewer unlocks again. Choice: rotate now, or after the link is retired (the review's order).
3. **H3, one look.** Migration 034 is in the database, so the site's writes (the cost ledger, the game, the sign-up, the question counter) succeed only with `SUPABASE_SERVICE_KEY` in the Vercel project's environment. Look that the key is there (Vercel, the project, Settings, Environment Variables; server side, no `NEXT_PUBLIC_`). A read cannot prove it: the newest rows are a game play on 14 October and a subscriber on 14 October, and the ledger's newest row (20 October 04:30 UTC) may be a scheduled job's.
4. **M6, the default privileges.** Choice: (a) a migration with the review's three `alter default privileges ... revoke` statements (for role `postgres`; the catalog shows the same defaults for `supabase_admin`, which the review's statements do not cover), after which every new table, sequence and function needs its own grant (a missing grant fails closed and is seen at once); or (b) keep relying on the `ensure_rls` event trigger, migration 028's sweep and `verify_rls.py --catalog`, as today.
5. **M7, Python packages.** `lxml` 5.4.0 is held by `gridstatus==0.36.0` (`lxml~=5.3`); `cryptography`, `setuptools` and `virtualenv` need new major versions under the daily run. Choice: (a) a session tries the bumps on a branch with the daily run's tests and a dry run of the connectors, or (b) wait for `gridstatus` to allow `lxml` 6.
6. **L4, the cookie's lifetime.** Choice: (a) a random session per unlock kept in a new table (every reviewer unlocks again), or (b) keep the fixed digest, which a rotation (item 2) resets for everyone at once.
7. **L7, `search_path`.** Choice: (a) a migration setting `search_path = ''` with schema-qualified names in `erw_lock_*`, `erw_dispatch` and `erw_db_size` (a typo stops the data lock or the schedule, so it wants its own landing and a test of each function), or (b) leave them: none is executable by the anon key.
8. **L8, sign-ups.** Read on 20 October: sign-ups are on, with email confirmation. The ERW has no accounts. Choice: (a) Supabase dashboard, Authentication, Sign In / Providers, turn off "Allow new users to sign up" (a dashboard setting; no session holds a key that changes it), or (b) leave it: a token minted that way reads nothing the anon key cannot.
9. **L9, the linter's packages.** Choice: (a) leave them until `eslint-config-next` ships a fix, or (b) `npm audit fix --force`, which installs `eslint-config-next` 14 and breaks the linter. The review's advice and this session's: (a).

## The usage counts (the roadmap's item 7, its second half)

The counts are recording: `site_usage_daily` holds days from 10 October 2026 to 19 October, and `site_usage_events` the day in progress (read on 20 October). What is sent and kept is in [`docs/methods/usage_counts.md`](methods/usage_counts.md): no cookie, no storage in the browser, no address, a hash that stands for a visitor for one UTC day. Nothing is sent when the browser asks not to be tracked. Which pages may count, and what, is the owner's ruling of 12 October 2026 ("no usage count on tool pages", `docs/roadmap.md`, "Rulings"); session 371 turned nothing on and changed nothing in `site/components/Usage.tsx` or `site/lib/usage.ts`. Whether the counts as they run today match that ruling everywhere (every page view is counted under its path, and a page in review under "In review (not opened)") is for Samuel to read against the ruling.

# Session 5159 report: the fresh pass, part 1: the headers and the internal view

13 November 2026, unattended, `portable-laptop` window P2. Branch `wip/5150-security`, worktree `erw-p2-5150`. Model spend USD 0. Pulls: one snapshot of the live pages (the after snapshot of session 5158's push). Nothing built, nothing landed, no warehouse data written.

Clock: precheck 19:27 UTC, the tests by 19:31 UTC. Inside the long end of 1:00.

## Read these first

- **One fault found and fixed (row 27).** The enforced policy let a browser connect to every Supabase project there is. A script that got into a page could have sent what it read to a project of its writer's. The policy now names this site's own project.
  - It takes the name from `SUPABASE_URL` when the site is built. A build without the variable keeps the wider name, as before.
  - **Proven here by tests of the configuration, not on a build.** The gate's `check-csp.mjs` (97 pages in a real browser) is the proof that no page loses a request.
- **No browser-side file connects to the database's host at all.** 101 client files read: every request goes to the site itself, or to cdnjs for the chart library. So the policy could say `'self'` alone. Not done: it needs a build. Ruling 1.
- **The internal view stands.** 34 pages and route handlers read file by file; now a test holds them.
- **Landing row 23 is on `main`** (`405207fc7`, session 5158). Snapshots before and after: 0 differences. Expected.
- Row 23 names the head `5411fef7d`. This session's commits are after it; session 5163 brings the row's head up to date.

## What to review

1. `site/next.config.ts`: `connectSrc`, 10 lines, and its one use in the policy.
2. `tests/test_session5159.py`: 11 tests.
3. `docs/reviews/security-faults-2026-11-13.md`: rows 27 and 28, and the new section "The fresh pass".

## What was done

- **The headers**, printed from the configuration itself (`runs/s5159/headers.mjs`): the six on every answer; `/internal/*` never cached, never indexed, no referrer; the form's page with `same-origin`.
- **Every request a browser-side file makes** (`runs/s5159/client_fetch.py`): `fetch`, a beacon, a worker, a script element. The network's hourly file, the one read of the database's storage, is fetched by the server (`site/lib/network.ts`, `fetchHourly`).
- **The fix** in `site/next.config.ts`. An address is written into the policy only when it is `https`, has no port, and its host is one label under `supabase.co`; anything else keeps the wider name. The tests feed it eight addresses that are not a project (another host, a look-alike, a port, an address carrying a second directive): none reaches the policy.
- **The internal view** (`runs/s5159/internal.py`): each file's guard, methods, 404, origin check, limit. Every file under `/internal` asks for the cookie or is one of the three doors; `cookieOpens` and `internalOk` compare in constant time.
- **`tests/test_session5102.py`**: its read of the headers now takes `SUPABASE_URL` out of the environment, so it reads the same policy on every machine.
- **Row 28 noted**: no `Cross-Origin-Opener-Policy`. Not added by a window that cannot build.

## Rule 8, the push of landing row 23 (session 5158)

- Before (`s5158-before`, 19:26 UTC) and after (`s5158-after`, 19:30 UTC): 25 pages each, 0 failed.
- `compare`: exit 0, **0 differences**. Expected: the push held one document.

## Checks, with exit codes

| Command | Exit | Result |
|---|---|---|
| `scripts/precheck.py --what "session 5159 (window P2)"` | 0 | on duty |
| `git merge origin/main` | 0 | merged |
| `pytest` on `test_session5159`, `5102`, `5153`, `301`, `1501`, `177`, `371`, `421`, first run | 1 | `test_session301` wants the wider name's words inside the policy's list: the fix was reshaped so they stay there |
| the same, after | 0 | 98 passed |
| `test_session5159`, `5102`, `301`, `1501` with a `SUPABASE_URL` in the environment | 0 | 47 passed |
| `tsc` on `site/next.config.ts` (a scratch config, the main checkout's TypeScript) | 0 | no error |
| `snapshot-live.mjs take s5158-after`, `compare` | 0, 0 | 0 differences |

- **Not run:** the build, `check-csp.mjs`, `check-security.mjs`, the whole suite.
- **Not verified:** that every page still loads all it asks for under the narrower name. It follows from the read (no browser-side request to that host) and from the name being the same project the server reads; a browser on a build is the proof.

## Decisions made without you

- **The project's own name, not `'self'` alone**: the first cannot break a request that works today; the second could, in a place the read did not see, and this window cannot open a page.
- **A change in `site/next.config.ts`**, which is not one of the four files this window owns: the headers are the review's first item and the chain's.
- **`Cross-Origin-Opener-Policy` not added.**

## For Samuel's ruling

1. `connect-src 'self'` alone. Default: a window that builds tries it on a branch with `check-csp.mjs` and the pages clicked through; until then the project's own name.
2. Row 28, `Cross-Origin-Opener-Policy: same-origin`. Default: the same window adds it with the same proof.

## The prompt

`queue/done/237-day-14-november-portable-p2-security-continued.md`, "Sessions 5159 to 5162: a fresh pass".

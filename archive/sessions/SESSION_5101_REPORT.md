# Session 5101 report: a visitor could read a page in review; the curtain's fix; the security list of 13 November

13 November 2026, unattended, `portable-laptop` window P2. Branch `wip/5100-security` (cut from `wip/5100-tools`), worktree `erw-p2-5100`. Model spend USD 0. Pulls: ten GET requests of the site's own public address, as a visitor. Nothing built, nothing landed, no warehouse data written.

Clock: precheck 10:02 UTC; the fault proven at 10:05 UTC (the answer's own `Date` header); the fix pushed at 10:12 UTC; the landing row at 10:13 UTC. Inside the long end of 1:00.

## Not meant, and first: a visitor can read a page in review

- **Until the stack lands, this is true of production.** `https://erw-flame.vercel.app/about.segments/about/__PAGE__.segment.rsc` answered a visitor (no cookie) with the About page's whole text, 35,960 bytes, while `/about` is in review.
- **Why.** The curtain (`site/proxy.ts`) never ran on an address with a file extension. Vercel serves every prerendered page as data at `<page>.segments/<segment>.segment.rsc`.
- **Who met it.** Nobody by browsing: a browser's own prefetch names the page and was shown the in-review page (read with the headers a browser sends). The address has to be typed by someone who knows Next's addresses.
- **How wide.** Every prerendered page. Read on `/about` only; I made ten requests and stopped.
- **The fix is on `wip/5100-security` (`e1f954c5`) and asked for as landing row 18, marked urgent.** It changes no page, no text, no table.
- **The proof after the deploy:** `node site/scripts/check-curtain.mjs https://erw-flame.vercel.app`, exit 0. A local build cannot show the fault.

## Read these first

- The list: `docs/reviews/security-faults-2026-11-13.md`, 25 rows. 1 fixed today, 8 rulings with defaults, 12 open for this chain, 4 noted.
- `site/lib/release.ts` is not touched. The rule lives in the proxy.
- The roadmap's holds name "The release gate". The owner's prompt of today gives this window `site/proxy.ts`. I read the hold as the release list and its statuses, and closed a hole in the gate rather than changing what it gates. Ruling 1.
- `site/scripts/test-usage.mjs` fails on `origin/main` (its 14th test). Row 2; the next session's.

## What to review

1. The fault, before the landing (any browser, no cookie):
   - Open `https://erw-flame.vercel.app/about`: the in-review page.
   - Open `https://erw-flame.vercel.app/about.segments/_full.segment.rsc`: a file of data downloads or shows; search it for "How the digest": the About page's words are there.
2. The same two addresses after the landing: the first unchanged, the second "Not found".
3. `site/proxy.ts`: 68 lines. `pagesOf`, `visitorGets`, then `proxy` as it was with one new answer (404).
4. `docs/reviews/security-faults-2026-11-13.md`: "Row 1 first", then the table.

## What was done

- **The read.** `site/proxy.ts`, `site/lib/guard.ts`, `site/app/internal/unlock/route.ts`, the 41 route handlers under `site/app/` (a table of methods, body reads, limits and guards; ten read in full), the review and `docs/security.md`.
- **The matcher against Next's code.** Next 16.4.5 appends an optional transport suffix to a proxy's matcher (`.rsc`, `.segments/...segment.rsc`), but this matcher's own look-ahead refused any address ending in an extension, the suffix included. Compiled with Next's own function: the old matcher skips `/about.segments/_full.segment.rsc`; the new one runs on it.
- **The fix** (`site/proxy.ts`):
  - The matcher's exception: an address ending in `.rsc` (any case) is no longer left alone.
  - `pagesOf(path)`: the page a transport address stands for, in every reading (Next reads it greedily; the address is as closed as its most closed reading). Escapes are decoded first; `/index` is the home page.
  - `visitorGets(path)`: `open`, `curtain` or `closed`. A transport address of a page in review is `closed`: 404, `noindex`, `no-store`, after the cookie is asked (the internal view passes).
  - The in-review page's own transport addresses stay open, or the curtain could not be drawn as data.
- **The tests.**
  - `site/scripts/test-curtain.mjs`, 8 tests: the matcher compiled as Next compiles it (by Next's function when installed, by the same arithmetic here when not; with Next, the two must be equal); the old matcher's gap kept as a proof; the rule on escapes, capitals, the adapter's form (the last `.rsc` taken off) and an address made to look like a file's.
  - `tests/test_session5101.py`, 7 tests: runs them; pins session 371's line and the order (cookie before the 404); the deployed check on the answers of 13 November (fails) and the fixed ones (passes).
- **`site/scripts/check-curtain.mjs <origin>`**: reads 8 pages and their 32 transport addresses as a visitor; exit 1 names any address that answers a page in review.
- **The list**: `docs/reviews/security-faults-2026-11-13.md`.
- **Landing row 18** in `docs/state/landing_request_portable.md`, pushed to `main` alone (`555631d6`) from a worktree of its own (`erw-p2-row`).

## Pulls and spend

- Model: USD 0 of USD 2.
- Requests to production: 10 GET, as a visitor, no token, of `/about`, `/about.rsc`, `/about?_rsc=abc`, four `/about.segments/...` addresses, `/cost-of-power/battery.rsc`, and `/about` with a browser's prefetch headers. Answers kept in `runs/s5101/` (not in git).

## Checks, with exit codes

| Command | Exit | Result |
|---|---|---|
| `scripts/precheck.py --what "session 5101 (window P2)"` | 0 | on duty |
| `scripts/freeze.py status` | 0 | no freeze |
| `node --import ./scripts/alias-register.mjs scripts/test-curtain.mjs` (no `node_modules`) | 0 | 8 of 8 |
| the same with `NEXT_DIR` naming the main checkout's Next 16.4.5 | 0 | 8 of 8, "compiled by Next's own function" |
| `pytest tests/test_session5101.py` and tests 371, 67, 87, 188_waits, 1501, 177, 301 | 0 | 102 passed, 3 skipped |
| `tsc` on `site/proxy.ts` and what it imports, from a scratch config, with the main checkout's TypeScript | 0 | no error; `--listFiles` names `proxy.ts`, `lib/release.ts`, `next/server.d.ts` |
| `node --import ./scripts/alias-register.mjs scripts/test-usage.mjs` (before any change) | 1 | 13 pass, the 14th fails on `origin/main` too (row 2) |

- **Not run:** the build, the whole suite, `check-security.mjs`, `check-csp.mjs` (they need a built site; the gate runs them).
- **Not verified:** that Vercel hands the proxy a segment address once the matcher names it. The compiled matcher says it will, and the old matcher's behaviour on production agrees with the compiled old matcher on all ten requests. `check-curtain.mjs` after the deploy is the proof.

## Decisions made without you

- **Ten requests to production.** The chain's rules leave production to the landing's snapshots. A visitor's GET of the site's own public pages changes nothing, and without it the fault was a reading of code, not a fact.
- **404, not the in-review page, at a transport address.** No browser asks for these by path; a 404 cannot be mistaken for content and needs no page.
- **The fix in the proxy, `site/lib/release.ts` untouched**, as the chain rules. `exempt()` there still reads any extension as never behind the curtain; the proxy asks `pagesOf` first.
- **Row 18 asks for the stack now**, with `wip/5100-tools` inside it, rather than waiting for more rows: every hour it waits the pages are readable.
- **A second worktree, `erw-p2-row`**, detached at `origin/main`, only for the landing rows (the main checkout's files are not this window's to change).
- **`check-curtain.mjs` is not added to `scripts/land_check.py`'s steps.** That file is the landing desk's; the row names the command.

## For Samuel's ruling

1. The hold "The release gate" and this fix. Default: land row 18 (the gate gates the same pages; a hole in it is closed).
2. Whether the pages were read by anyone at these addresses. Vercel's request logs would show requests ending in `.segment.rsc` with no `RSC` header from a browser's navigation. Default: no action by a session (no session holds a Vercel sign-in).
3. Rows 3, 4, 5, 7, 10, 11 and 12 of the list, each with its default in the list's last column (the old link, the rotation, the default privileges, the cookie's lifetime, `search_path`, sign-ups).

## The prompt

`queue/done/234-day-13-november-portable-p2-security.md`, "Sessions 5101 to 5135: roadmap item 7, security closed and the cookieless usage counts".

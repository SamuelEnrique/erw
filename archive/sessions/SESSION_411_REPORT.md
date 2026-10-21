# Session 411 report: Lighthouse on every visitor page

21 October 2026, about 07:24 to 09:30 UTC, unattended, on samueloldlaptop (the code machine), in the worktree `C:\Users\lossa\Documents\erw-411` on `wip/411-s` (from `origin/main` at `bb49c9e0`). Chain `queue/done/015-day-20-october-code-pm.md`, "Session 411". Model spend USD 0; no pull from any publisher; no warehouse data written. One download: the npm package `lighthouse@13.4.1` (and its dependencies) into a folder of the session's scratchpad, outside the repository (the prompt allows "the CLI").

## Read these first

- **The review is `docs/reviews/performance-2026-10-20.md`**: the four Lighthouse scores of 28 pages (the 25 snapshot addresses, `/cost-of-power`, `/research`, `/grid`) at 1280 and 390 px, before and after, with the largest paint and the weight of each run, on a local production build in the internal view. Before: performance 97.9 at 1280 and 88.1 at 390 on average; after: 98.3 and 88.8; accessibility 96.5 and 92.8 both times; best practices and SEO 100 on every run.
- **Fixed** (no ruling needed, neither session 401's nor 412's files): (1) the header's ERW mark links to `/` with `prefetch={false}`: a prefetch of the home page carried React's preload of its 156 KB chart of the day into every page showing the mark, so 19 of the 56 runs carry 165 to 172 KB less (mean weight 492 to 438 KB at 1280, 487 to 427 KB at 390); (2) the chart of the day takes its own size (1200 by 880, read from the PNG header by `build-content.mjs`) where the home page wrote 1600 by 900; (3) four unused imports. Commits `7a04542f` and `e7f879ec`.
- **Tried and undone**: Inter not preloaded. Its file was fetched anyway (some element is laid out in Inter for a moment before the brand's header rule applies) and the mobile first paint moved from about 1,060 to 1,360 ms in Lighthouse's model. Listed for a ruling.
- **The chrome-devtools-mcp Lighthouse cannot score performance**: its `lighthouse_audit` leaves performance out (its own description says so), and the Lighthouse bundled in it has shims for every performance audit, which score 100 whatever the page. The runner uses Lighthouse from npm and refuses a report whose first-contentful-paint audit is a shim. `docs/tooling.md` names `lighthouse_audit` for "its load": worth a line there (session 401 edits that file tonight, so it was not touched here).
- **The layout shift every page shows is the internal view's**: the page is built for a visitor, with links to pages in review drawn greyed with "in review"; in the internal view the browser redraws them as links, the header goes from two lines to one and the page moves up 24 px. A visitor's page has no such redraw.

## What to review

- `docs/reviews/performance-2026-10-20.md` on `wip/411-s`: `https://github.com/SamuelEnrique/erw/blob/wip/411-s/docs/reviews/performance-2026-10-20.md`
- The shots: `https://github.com/SamuelEnrique/erw/tree/wip/411-s/docs/brand/review-411` (the home page's chart of the day at 1280 and 390, before and after: the same once loaded, as they should be)
- The fixes: `site/app/layout.tsx`, `site/app/page.tsx`, `site/scripts/build-content.mjs`, `site/lib/markdown.ts` (commits `7a04542f`, `e7f879ec`); the runner `site/scripts/lighthouse-pages.mjs`; `tests/test_session411.py`.
- After the landing, on the site in the internal view: `/about` (the network panel: no `/digest-charts/` request), `/` (the chart of the day as before).

## Checks

Every gate redirected to a file under `runs/chain_oct21/s411/`, never piped; the exit code read before the next step.

| Check | Exit | Result |
|---|---|---|
| `npm ci` in the worktree's `site/` | 0 | |
| `duty.py beat` before each of the four builds | 0, 0, 0, 0 | |
| `npm run build` of `bb49c9e0` (before) | 0 | no statement timeout |
| `npm run build` with the fixes and Inter not preloaded | 0 | |
| `npm run build` with the fixes (final, Inter as before) | 0 | |
| `npm run build` of `bb49c9e0` again (for the side-by-side) | 0 | |
| `lighthouse-pages.mjs` before, 56 runs | 0 | none curtained, none failed |
| `lighthouse-pages.mjs` with Inter not preloaded, 56 runs | 0 | first paint later on every page: change undone |
| `lighthouse-pages.mjs` final build, two sets of 56 | 0, 0 | spoiled by the machine: a 413 ms GPU stall in 26 and 20 runs (1 in the before set) |
| `lighthouse-pages.mjs` side by side, 6 pages each build | 0, 0 | the same scores |
| `lighthouse-pages.mjs` final build, third set of 56 (the "after") | 0 | 1 stalled run |
| `check-values.mjs http://localhost:3411` (full, final build) | 1 | 5,882 of 5,885 values match; 11 FAILED: one `/data` row count (`ercot_peak_premium_monthly`, page 23,688, Supabase 23,856: the table grew after the build) and ten page floors (`/deals`, `/map`, six `/events` pages, `/learn/bill`, `/research/card/gas_sets_price`) |
| `check-values.mjs`, `CHECK_VALUES_PAGES` = the pages touched and the 28 (final build) | 1 | 4,298 of 4,298 values match; 9 floors fail, the same pages |
| `check-values.mjs`, `CHECK_VALUES_PAGES=/deals,/map,/events,/research/card` on the build of `bb49c9e0` | 1 | 1,115 of 1,115 match; the same 9 floors fail: not this session's |
| `npx eslint` on the changed files | 0 | one warning left (`g` in `components/mix/views.tsx`, an unused value, not an import) |
| `tests.test_session411` | 0 | 8 tests OK |
| the whole suite (`ERW_LOCK_EXEMPT=1 ... unittest discover -s tests`), first run | 1 | 4,794 tests, 2 failures: `test_session156` (the ask fixtures, `test-ask-ready.mjs` test 10, as the chain's rules expect tonight) and `test_session315`, which pins the line of `build-content.mjs` this session had extended: the size is now added after that line (commit `e7f879ec`) |
| `tests.test_session411`, `test_session315`, `test_session238` after that | 0 | 41 tests OK; `node scripts/build-content.mjs` exit 0, every chart record with its width and height |
| the whole suite, second run | 1 | 4,794 tests, 1 failure: `test_session156` only (the ask fixtures) |
| trial merge of `wip/411-s` with `origin/wip/401-s`, `origin/wip/412-s`, `origin/main` | 0, 0, 0 | no conflict |

Every value is unchanged: the fixes move a prefetch and a reserved box; no figure, key or default.

## Decisions made without you

1. **Lighthouse from npm, not the installed tool**: the installed chrome-devtools-mcp cannot score performance (above). The package went into the session's scratchpad, not the repository or the machine's global packages; the runner takes its folder from `LIGHTHOUSE_DIR`.
2. **The internal view's cookie is set in the browser for `localhost` only**, not sent with `--extra-headers` as the prompt suggested: an extra header goes with every request to every host the page calls, and the cookie must not leave the machine.
3. **The home link's prefetch is off** although a visitor sees no link there today (the home page is in review): the waste was the internal view's tonight and would be every visitor's once the home page opens; the cost is that going home is not instant.
4. **The chart's size is read from the PNG** in `build-content.mjs` rather than written as 1200 by 880 in the page: the chart maker's size can change, and the record says what each picture is. A bundle built before this session has no size, and the page then writes 1600 by 900 as before.
5. **The "after" set is the third**: the two before it were spoiled by GPU stalls on the machine (traced, and absent from a side-by-side of the two builds and from the third set). Both are kept in `runs/`.
6. **The unused values in session 401's files** (`METHOD`, `one`, `usd`, `flat` in `app/cost-of-power/`) and the research page's chart size were left to it and listed in the review.
7. **No landing**: the brief's "Land" is the push of `wip/411-s` (the chain's rules), done.

## For Samuel's ruling

- Inter is fetched on every branded page (49 KB) though nothing ends drawn in it: the header's brand face is set by a style inside the page body; (a) the rule in tokens.css with the brand's font variables on `<html>`, (b) the brand's face on every page's header (a visible change on four pages), (c) leave it.
- A `browserslist` target would drop Next.js's 14 KB of polyfills from every page: it decides which old browsers the site still supports.
- `experimental.inlineCss` would remove the render-blocking stylesheets (about 200 to 300 ms of mobile first paint in Lighthouse's model): an experimental switch for every page.
- The chart of the day is a 156 KB PNG drawn 653 px wide at most: (a) the chart maker writes a smaller or WebP picture, (b) `next/image` on Vercel (its image quota, money), (c) leave it.
- `/network` in the snapshot list answers a redirect to `/grid?view=network` on every visit: name the target instead.
- Two `grep.exe` processes running on the code machine since 14 October (ids 2028 and 18568, waiting on "exit=|stopped|mutex given|NOT MINE"): left alone, not this session's.

The final site build (exit 0) was made before `e7f879ec`, which only moves where `build-content.mjs` adds the size to the record (the same bundle, checked by running the script); the next landing's build covers it.

## Files

- `site/scripts/lighthouse-pages.mjs` (new), `site/app/layout.tsx`, `site/app/page.tsx`, `site/scripts/build-content.mjs`, `site/lib/markdown.ts`, `site/app/deals/v2/view.tsx`, `site/components/grid/YourGrid.tsx`, `site/components/mix/views.tsx`, `site/app/cost-of-power/seller/tables.csv/route.ts`.
- `docs/reviews/performance-2026-10-20.md` (new), `docs/brand/review-411/` (four shots, `shots-411.mjs`), `tests/test_session411.py` (new).
- Not in git: `runs/chain_oct21/s411/` (every Lighthouse record and report, the probes, the build and check logs).

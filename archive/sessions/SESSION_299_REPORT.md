# Session 299 report: the Grid tool as one page of four tabs

19 October 2026, from 08:16 UTC, unattended, on samueloldlaptop (the code machine), the fifth session of the chain of 19 October (`CHAIN_OCT19_PROMPT.md`). Branch `wip/299-grid-one-page` in the worktree `erw-296`, from session 298's pushed commit; lands on main as `task/299-grid-one-page`. Model spend USD 0: no model call. No pull, no warehouse data written.

## Read these first

- **One page, four tabs.** `/grid` is Network, Mix, Clean and Gravity, the grid picked once above them, and Ask a panel on the right of every tab (under the tab's blocks at phone width). The Now view's blocks (the grid's latest hour) now open the Mix tab above the Mix view's own blocks; the Exchange view's blocks sit under the gravity shape on the Gravity tab. Every address that existed resolves: `view=now` opens Mix, `view=exchange` Gravity, `view=ask` the page with the panel open, `shape=gravity` with `view=network` the Gravity tab, and `/grid/<iso>`, `/network`, `/mix`, `/emissions` as before. `/ask` and `/ask?grid=<slug>&q=<question>` redirect to the panel (a 307 from the page itself, the query carried whole); `/ask/ercot` stays.
- **The page opens on the Lower 48** (ruling 4b) **and on the Mix tab.** The tab was not ruled; Mix is where the opening view's blocks went, so `/grid`, `/grid/<iso>` and `/grid?grid=<grid>` draw the numbers they drew and their floors in `check-values-floor.json` stand untouched. (The first build opened on Network, and the value checker failed its floors on 16 addresses: one checked number on a page whose floor is ten. That is why.)
- **The gravity shape's pull is a square-root scale** (2c): `sign(share) x sqrt(|share| / 0.25)`, held to one, in `site/lib/networkGravity.ts` and in the replication script `site/public/grid/erw_2026_grid_replication.py` alike; a grid importing a sixteenth of its generation now sits at half the full pull. EIA-930 stays the one source, with CAISO's break named in the note under the shape (1a); the 63 other balancing authorities stay out and are counted there (6a).
- **How old "now" is, said twice** (3c): the line under the network gives the hour's age against the snapshot's latest hourly refresh (the check key, unchanged) and, beside it, against the clock when the page was drawn (`data-network-clock-lag`; not a key, since the clock is not a table, and up to an hour stale on a page served for an hour).
- **No number moved.** Every checked number common to production and the local build is the same (1,163 keys on the grid addresses before, 1,207 after; no key gone, no common value changed; the 44 new ones are the two Gravity addresses added to the value checker and the Now blocks drawn on the Mix tab). Every block kept its markup inside the wrapper.
- **Session 298 landed** (recorded below): merge `9253da80`, 0 differences on 25 pages.

## What to review

1. `/grid` (the Lower 48, the Mix tab), then each tab, then ERCOT with the panel: `/grid?grid=ercot&ask=1`. The decisions block at the foot of every tab.
2. `docs/brand/review-299/` (24 shots, the README says what each shows) and the screenshots' note 3: the seven circles of the gravity shape are dashed outlines this week on production and here alike (EIA-930's generation for the hour shown is not in the live set); nothing of this session's.
3. `docs/methods/grid_network.md`, "One page, four tabs, and the Ask panel (session 299)", and the Grid pack's section 9, where the rulings' outcomes are noted.
4. `site/lib/gridtool.ts` (`GRID_VIEWS`, `OLD_VIEWS`, `DEFAULT_VIEW`, `DEFAULT_GRID`, `gridPick`, `gridHref`), `site/app/grid/page.tsx`, `site/app/ask/page.tsx`.

## What was done

- `site/lib/gridtool.ts`: four views, the old words mapped, `ask` on the pick, the Lower 48 and Mix as the defaults, the Gravity address with the component's own shape word.
- `site/app/grid/page.tsx`: the picker, the tabs, the two-column grid with the aside, the Mix tab holding the Now blocks, the Gravity tab holding the shape and the Exchange blocks, the decisions block (`data-decisions="299"`), the on-screen line above the panel.
- `site/components/grid/AskView.tsx`: `tab` and `compact`; ERCOT's context keeps `/grid/ercot` as its view (the route's cleaner admits a site path only, no query) with the tab in its title and settings. `site/app/tokens.css`: the compact panel's type.
- `site/components/grid/NetworkView.tsx` (the `shape` prop, the clock line), `site/app/network/Network.tsx` (the page's shape opens the component in it), `site/app/network/NetworkGravity.tsx` (the note under the shape), `site/lib/networkGravity.ts` and the replication script (the square-root pull), `ExchangeView.tsx`, `NowView.tsx`, `YourGrid.tsx` (links to the Gravity tab).
- `site/app/ask/page.tsx`: the redirect; the page that stood there is kept, unrouted, in `site/app/_retired/ask-original/` (the pattern of sessions 168 and 237).
- `site/scripts/check-values.mjs` (two Gravity addresses), `check-routes.mjs` (the Gravity tab, the panel's flag and the old words), `check-ask-panel.mjs` (the panel beside the tabs, not an Ask tab; the aside is `data-ask-side` so the panel's own `data-ask-panel` stays unique).
- Tests: `tests/test_session299.py` (14 tests: the address, the page, the rule in both languages against each other, the checks, the note, the folder, no em dash); `tests/test_session237.py` pins updated for the four views and the defaults.
- `docs/methods/grid_network.md`, `docs/reviews/packs/grid.md`, `docs/brand/review-299/`.

## Checks

| Check | Exit | Result |
|---|---|---|
| `scripts/precheck.py --what "session 299"` | 0 | `runs/chain_oct19/s299_precheck.out` |
| `tsc --noEmit` (worktree) | 0 | no error |
| `eslint` on the files touched | 0 | 0 errors, 2 warnings that stood before (Network.tsx's `useMemo`, YourGrid's unused `NoData`) |
| `npm run build` (worktree, under the mutex, `duty.py beat` sent) | 0 | three builds (the default tab and the panel's attribute changed between them); 0 statement timeouts |
| `check-values`, the grid addresses, local build | 0 | 1,207 of 1,207 match Supabase (the first build: 16 floor failures, fixed by the opening tab) |
| `check-values`, the grid addresses, production | 0 | 1,163 of 1,163; against the local run: no key gone, 0 common values differ, 44 new |
| `check-routes`, local build | 0 | 211 of 211 with the cookie; as a visitor 0 failed |
| the redirects, `curl` with the internal cookie | | `/ask` 307 to `/grid?grid=us48&ask=1`; `/ask?grid=caiso&q=hello+world` to `/grid?grid=caiso&ask=1&q=hello%20world`; `/ask?grid=ERCO` to `/grid?grid=ercot&ask=1`; `/mix` 308 to `/grid?view=mix`; `/grid?view=ask`, `/grid?grid=ercot&view=exchange`, `/grid/pjm` resolve to the tab that holds their blocks |
| `check-ask-panel.mjs` (a real browser, recorded replies) | 0 | 13 of 13 (10 of 13 before the panel attribute and the tab check were updated) |
| `check-grid-replication.mjs` | 1 | 59 of 60 differ, on production too (`s299_gridrep_prod.out`): the committed replication file is session 266's hour; the check needs the file written just before, which a code machine does not do. Not this session's |
| `tests.test_session237`, `266`, `239`, `203` | 0 | 74 passed |
| `tests.test_session299` | 0 | 14 passed |
| Impeccable `detect` on the seven page, component and style files | 0 | no finding |
| Screenshots, 1280 and 390, before (production) and after (local) | | `docs/brand/review-299/`; nothing scrolls sideways at 390 |
| Suite, clean copy, `654f1e7d` (the session's first commit) | 1 | 4,354 tests, 4 failures: four older pins of the files this session changed (137: the panel's context line; 241b: `/ask` must be wrapped in the brand, now the kept page is; 78: the gravity note named the join's date, 16 December 2025, which only `caiso_join.py` may; 93: the component's `page` prop) |
| Suite, clean copy, `cecd4742` (the pins updated) | 0 | 4,354 tests OK, 245 skipped |
| Suite, clean copy, `6a81355a` (origin/main merged, with session 306's commit) | 1 | 4,360 tests, 1 failure, main's own: `test_session275` (the Redivis release package's list disagrees with the record for session 306's two new tables). Fixed in the next commit, below |
| `tests.test_session275` after the two rows | 0 | 4 passed |
| `npm run build` of the merged commit (worktree) | 0 | `s299_build5.out`; 0 statement timeouts |

## Landing of session 298 (recorded here: session 298's report is in that landing's own commit)

- Pushed `task/298-generator-datacenter` at `61db9bd7` at 08:16 UTC; GitHub's checks passed (run 39221537755) and merged it as `9253da80` at 08:27; production served the new build at 08:28; the after snapshot was taken at 08:28:52.
- Snapshot `s298-before` (08:15:42) against `s298-after` (08:28:52): 25 pages, 0 differences. Expected: every page the session touched is in review. Nothing unexpected.

## Landing

LANDING

## Decisions made without you

- **Session 306's two tables were added to the Redivis release package's list** (`docs/redivis/release-v1/tables.csv`: `battery_sourced_ranges` and `grid_stress_days`, `in_v1 = yes`, with the counts in `release-v1.md` and the package README moved from 125 to 127 tables, 109 series). Main at `5d389ad6` failed `test_session275` on them, and GitHub runs the whole suite on every task branch, so nothing of this chain could land until the list agreed with the record. The rows carry what the package's own script writes: the plan's verdict, coverage's rows and range, the writers' header title and license line, the script's citation. `variables.csv` does not list their variables (that needs the tables, which this machine does not hold): the data machine's next `release_v1.py` run completes it.
- **The opening tab is Mix.** The merge names the tabs' order (Network first) but not the tab the page opens on; Mix holds the blocks the page opened on until now, keeps every default address at its numbers and leaves the floors as they are. Reversible: `DEFAULT_VIEW` in `site/lib/gridtool.ts`.
- **`/ask` redirects from the page itself** (a 307 that carries grid and question), not from a rule in `next.config.ts` (a 308 the browser caches); the old page is kept unrouted.
- **The Ask panel's context view stays `/grid/ercot`**, with the tab in its title and settings: the route's cleaner (`lib/chat/ercot.ts`) admits a site path only, and a view with a query would have dropped the context.
- **`view=ask` opens the Mix tab with the panel open** (the opening tab), since the merge names no tab for it.
- **The aside carries `data-ask-side`**, not `data-ask-panel`, so the three browser checks that select the panel by its own attribute keep working.
- **The replication check's failure is reported, not fixed:** its file is written on the data machine from the live set, and this machine writes no warehouse data.
- Questions skipped (Impeccable's playbooks ask them; the chain's rule holds).

## For Samuel's ruling

- The data machine should rerun `warehouse/redivis/release_v1.py` so the package's `variables.csv` lists the two new tables' variables, and so the list is the script's own again.
- The Grid pack's question 5 (EIA's annual generation by balancing authority as a cross-check) is still open.
- Whether `check-grid-replication.mjs` should run in the daily workflow after the replication file is rebuilt, so the Gravity tab's rule is checked on the hour it draws (today it is checked by `tests/test_session299.py` in both languages on fixed inputs).

## Files

- Changed: `site/lib/gridtool.ts`, `site/app/grid/page.tsx`, `site/app/ask/page.tsx`, `site/components/grid/{AskView,NetworkView,ExchangeView,NowView,YourGrid}.tsx`, `site/app/network/{Network,NetworkGravity}.tsx`, `site/lib/networkGravity.ts`, `site/public/grid/erw_2026_grid_replication.py`, `site/app/tokens.css`, `site/scripts/{check-values,check-routes,check-ask-panel}.mjs`, `tests/test_session237.py`, `docs/methods/grid_network.md`, `docs/reviews/packs/grid.md`.
- New: `site/app/_retired/ask-original/page.tsx`, `tests/test_session299.py`, `docs/brand/review-299/` (24 shots and a README), this report.
- Not in git: `runs/chain_oct19/s299*` (builds, checks, captures), `runs/chain_oct19/capture299.mjs`.

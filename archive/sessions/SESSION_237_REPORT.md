# Session 237 report: the Grid tool, one page at /grid

13 October 2026, unattended, on the old laptop, in the worktree `erw-144` on branch `wip/237-grid` (from `a4c54722`). Not pushed, not landed: the landing is the orchestrator's. No model was called (spend USD 0). No table was written.

## Read these first

- **Done:** `/grid` is one page: a picker of eight (ERCOT, CAISO, PJM, MISO, NYISO, ISO-NE, SPP, US48) and six views (Now, Network, Mix, Clean, Exchange, Ask), on the brand. The address holds both: `/grid?grid=ercot&view=mix`.
- **Done:** `/network`, `/mix`, `/emissions`, `/mix/clean`, `/mix/stress` and the seven `/grid/<iso>` redirect into its views (`site/next.config.ts`). The inventory below lists every block of every old page and where it is now. Nothing is dropped.
- **Done:** the menu's Grid group shows the one tool ("The grid") in place of the ten pages that redirect into it. The page is `review`.
- **A visitor at `/network` after this change** (one of the snapshot's 25 addresses): the answer is `308` to `/grid?view=network`, then `200`, the in-review page. Its heading changes from "The network" to "The grid" (the in-review page names the tool at the address, and the address is `/grid` now); the sentence "This tool is in review and will open when it is approved." and the rest are as before. This difference in the snapshot is expected.
- **Not verified in a browser:** see "Checks" below: the browser checks that were not run are named there, with the reason.
- **One quirk to rule on:** an address that names no grid opens ERCOT (`/grid`), except the Network, Mix and Clean views, which open on the Lower 48, as the pages that redirect into them opened ("For Samuel's ruling", 1).

## What to review

Open `https://erw-flame.vercel.app/internal/open` first (after the landing), then:

- https://erw-flame.vercel.app/grid (ERCOT, Now: the sentence, the three numbers, the mix in that hour, then what ERCOT's page showed)
- https://erw-flame.vercel.app/grid?grid=ercot&view=network (the 3D network is the default; "Map" is the toggle; ERCOT's panel is open)
- https://erw-flame.vercel.app/grid?grid=ercot&view=mix and https://erw-flame.vercel.app/grid?grid=pjm&view=mix&mix=stress
- https://erw-flame.vercel.app/grid?grid=ercot&view=clean
- https://erw-flame.vercel.app/grid?grid=ercot&view=exchange and https://erw-flame.vercel.app/grid?grid=us48&view=exchange
- https://erw-flame.vercel.app/grid?grid=ercot&view=ask (ERCOT's own answers) and https://erw-flame.vercel.app/grid?grid=nyiso&view=ask (the general chat for NYISO)
- https://erw-flame.vercel.app/grid?grid=us48 (the Lower 48, Now) and https://erw-flame.vercel.app/grid?grid=caiso (the mix withheld, as session 118 ruled)
- The redirects: https://erw-flame.vercel.app/network?view=day&t=2021-02-15&grid=ERCO&prices=1&trace=1 , https://erw-flame.vercel.app/mix?view=day&grids=caiso&period=2020-03 , https://erw-flame.vercel.app/emissions , https://erw-flame.vercel.app/grid/caiso#reliability
- Screenshots: `docs/brand/review-237/` (each view of ERCOT and Now for PJM and the Lower 48, at 1280 and 390 px).

## What was built

- `site/app/grid/page.tsx`: the tool. `<Brand>`, `ToolPage`, `ToolHeader` (crumb "The grid", title the grid's own name), the picker and the tabs, the view, a question box at the foot of every view but Ask, the Related line.
- `site/lib/gridtool.ts`: the eight choices, the six views, the address (`gridPick`, `gridHref`) and the two functions through which the network component reads and writes its own words under the tool's (`netFromPage`, `netToPage`). Pure, no imports.
- `site/components/tool/Choose.tsx` (new shared component): `ToolTabs` and `ToolPicker`, plain links. `site/app/tokens.css`: ONE added block at the end, `.brand-a nav[data-tabs]` and `.brand-a nav[data-segments]` (a link that chooses is never the running text's cardinal). No existing rule changed.
- **Now** (`components/grid/NowView.tsx`): one sentence computed from the tables, three headline numbers (demand, net export or import, carbon intensity), "The mix in that hour" (bar and table), each number with its hour and its check key. Then the grid's own blocks and its block of "Grid conditions". Reads `eia930_all_demand`, `eia930_all_generation`, `carbon_intensity_hourly` and the network's snapshot of `eia930_all_interchange`: the same four for all eight choices.
- **Network** (`components/grid/NetworkView.tsx`, was `app/network/page.tsx`): the page whole. The component (`app/network/Network.tsx`) takes a `page` prop: it keeps the tool's grid and view at the head of the address and writes its own view as `net` and its own grid as `node`. The grid in view opens its panel. Its canvas and its map now read their colors from the tokens (`readPalette`; `NetworkMap.tsx` uses `var(--color-...)`).
- **Mix** (`components/grid/MixView.tsx`, was `app/mix/page.tsx`): the mix page whole, its addresses under the tool's (`lib/mixpage.ts`: a `base` on the choice; without it `/mix`'s addresses are as they were). Under it the grid page's "Where the power comes from" and the old "Generation mix, as a table".
- **Clean**: the grid page's "How clean", the emissions page's three blocks (`components/grid/Emissions.tsx`, the grid in view highlighted in the ranking) and the mix's "How clean, and when".
- **Exchange** (`components/grid/ExchangeView.tsx`, new): the grid's ties in the newest hour every reporting pair holds, the week's net export hour by hour, and twelve months by neighbour (`ba_supply_monthly`). For the Lower 48: the seven grids' net export in the hour and the largest exporter. Key kinds added to `lib/network.ts netValue`, which the value checker already calls: `net|export|<BA>|<hour>`, `net|import|<BA>|<hour>`, `net|tie|<BA>|<other>|<hour>`.
- **Ask** (`components/grid/AskView.tsx`): ERCOT, the panel of its own profile (the same component and context as on its grid page); the six others, `/ask`'s own form for that grid; the Lower 48, `/ask`'s form for the whole warehouse. `q` in the address is placed in the box and never sent by the page.
- Request shape, read from the code and the markup, no question sent: ERCOT posts `{ question, profile: "ercot", stream: true, context: { view: "/grid/ercot", title, settings: { grid: "ERCOT" } }, history }` to `/api/ask`; the six others post `{ question, grid: "<slug>" }`; the Lower 48 posts `{ question }`.

## The address (the form chosen)

`/grid?grid=<ercot|caiso|pjm|miso|nyiso|isone|spp|us48>&view=<now|network|mix|clean|exchange|ask>`; `view=now` is not written. A view's own state follows under its own words: `mix=<the mix's view>` with the mix's parameters; `net=<the network's view>`, `node=<the panel's balancing authority>`, `t`, `batteries`, `prices`, `trace`, `shape`; `q=<a question>`. This is the repository's form (`/mix?view=`, `/demand?view=`). Old words are still read: `grid=ERCO`, `ba=erco`, `grids=pjm,miso`.

## The redirects (`site/next.config.ts`, permanent, a query carried over)

| Old address | Goes to |
|---|---|
| `/network` | `/grid?view=network` |
| `/network?view=<v>&...` | `/grid?view=network&net=<v>&...` (its `grid=ERCO` is read as the grid and the panel) |
| `/mix` | `/grid?view=mix` |
| `/mix?view=<v>` | `/grid?view=mix&mix=<v>`; `/mix?view=clean` goes to `/grid?view=clean` |
| `/emissions` | `/grid?view=clean` |
| `/mix/clean`, `/mix/stress`, `/mix/v2` | unchanged lines of session 133 (`/mix?view=...`), so they arrive in two steps |
| `/network/v3` | unchanged line of session 168 (`/network`), two steps (session 239's) |
| `/grid/<iso>` (seven lines) | `/grid?grid=<iso>` |
| `/grid/caiso/alerts` | not redirected: its own page, as before |

`site/lib/release.ts` is unchanged: `/grid` is `review`, and the old addresses keep their lines.

## The inventory: every block of every old page, and where it is now

"View" is the tab of `/grid?grid=<grid>&view=<view>`. An old page's file was moved, not deleted ("file now").


### /grid, "Grid conditions" (file now: `site/components/grid/Conditions.tsx`, a copy; `site/app/grid/page.tsx` is the tool)

| Block | Where it is now |
|---|---|
| Title and the two opening paragraphs (what the page is, UTC days, local peak hour) | Now view of each grid, the lead of the section "<Grid>: yesterday" (the same sentences, as one paragraph) |
| "Your grid" line of seven links | the picker (eight segments) |
| Fuel color key | Now view, in "<Grid>: yesterday" |
| One block a region, eight of them (US48, ERCOT, CAISO, PJM, MISO, SPP, NYISO, ISO-NE): peak demand of yesterday with its check key, the hour (UTC and local), the day-ahead forecast for that hour and its error, the day's mean absolute error, the note when yesterday is incomplete | Now view of that grid, "<Grid>: yesterday" (`GridYesterday`, the same `Block`) |
| The seven-day chart of demand, forecast and the load center's temperature; the degree days | the same block, Now view |
| The day's generation mix as a bar, with its total and check key (CAISO: the withheld note of session 118) | the same block, Now view |
| "Generation mix, as a table" (all eight regions) | Mix view, at its foot (`MixTable`), on every grid |
| "Related" line | foot of the tool, every view (`<Related href="/grid" />`; it now names Demand growth and Curtailment) |

### /grid/<iso>, the seven grid pages (file now: `site/components/grid/YourGrid.tsx`, `Reliability.tsx`)

| Block | Where it is now |
|---|---|
| Crumb "Grid / Your grid" | the tool's crumb "The grid" |
| Title "<ISO>: <full name>" | the tool's title, the same words |
| "Ask ERCOT about this view" link (ERCOT, internal view) | Now view of ERCOT, first line of the grid's blocks |
| California's data-break note (CAISO) | Now view and Clean view of CAISO |
| Opening paragraph (what the page holds, the time zone, the link to the network) | Now view; the link goes to the Exchange and Network views |
| "Other grids" row | the picker |
| Who runs this grid (written) | Now view |
| The Ask box: ERCOT's panel that answers below itself; the six others' form that opened /ask?grid= | Ask view (ERCOT: the same panel, same context; the six: /ask's own form for that grid, answering in place); a box at the foot of every other view opens the Ask view with the question placed in it |
| Right now: demand (latest hour, a week earlier, the day's peak, today against last week) | Now view |
| Where the power comes from (24 hours stacked, 30 days, the table by fuel; CAISO withheld) | Mix view, under the mix |
| Batteries (the day's cycle, the 30-day line, the fleet by status) | Now view |
| How clean (latest hour, 24 hours, monthly since 2018, months left out) | Clean view, first block |
| What it costs (hub prices; "license needed" or PJM's "not public" as today), and the cost-of-power line | Now view, with the gate it had (`lib/license.ts` through `lib/supabase.ts` and `Num`) |
| Reliability (CAISO only; anchor `#reliability`) | Now view of CAISO, same anchor |
| What is being built (the queue by kind; datacenter facilities) | Now view |
| In the news | Now view |
| About <ISO> (written) | Now view |
| "Reads that failed" line | Now view |
| /grid/caiso/alerts (the Flex Alert scorecard) | unchanged: its own page at its own address |

### /network, "The grid network" (file now: `site/components/grid/NetworkView.tsx`; the component stays in `site/app/network/`)

| Block | Where it is now |
|---|---|
| Title | the tool's title names the grid; the view's tab is "Network" |
| Lead (the balancing authorities, the stories, the replay, the address) | Network view, first paragraph, same words |
| The component: Map and Network toggle (Network, the 3D vector view, is the default), Watch buttons and stories, the replay with its date picker and "Play the year", Batteries and Prices switches, the slider, the canvas or the map, the panel (net imports, suppliers, hub price, carbon, batteries, twelve months, "Trace the power"), the key | Network view, the same component. The grid in view opens its panel (none for the Lower 48) |
| The two lines of freshness ("The live week ...", "Newest hour ...") | Network view |
| "The last twelve months could not be read" line | Network view |
| Source line | Network view |

### /mix, "Energy mix" (file now: `site/components/grid/MixView.tsx`)

| Block | Where it is now |
|---|---|
| Title and "Method, sources and gaps" | Mix view, the block's heading |
| The nine views (Now and by state, The average day, Year after year, Records, How clean and when, How hard the system works, Availability by source, Wind and solar forecasts, Since 2001) | Mix view: eight of them under `mix=<view>`; "How clean, and when" is the Clean view (its link in the row goes there) |
| Controls (Select grids, Year, Month, Scale, Add factors, Source, Season, Select states) | Mix view, the same controls; "Select grids" opens on the grid in view |
| Now and by state: the operator and state selects, "today so far", "hourly mix, last 7 days", "monthly mix since 2001" | Mix view, opening view. For one of the seven grids the operator is the grid in view; for the Lower 48 the operator select is there as before |

### /mix/clean and /mix/stress

| Block | Where it is now |
|---|---|
| /mix/clean: "How clean, and when" with its controls | Clean view, last block (`MixClean`) |
| /mix/stress: "How hard the system works" | Mix view, `mix=stress` |

### /emissions (file now: `site/components/grid/Emissions.tsx`)

| Block | Where it is now |
|---|---|
| Title | the Clean tab |
| California's data-break note | Clean view |
| Opening sentence with the Method link | Clean view |
| Carbon intensity now, ranked (seven grids) | Clean view; the grid in view is the highlighted row |
| The last 24 hours (seven lines) | Clean view |
| Monthly since 2018, with the figures and the months left out | Clean view |

### New on the page (not on any old page)

- Now: the one sentence and the three headline numbers (demand, net export, carbon), and "The mix in that hour".
- Exchange: the grid's ties in the newest complete hour, the week's net export, the twelve months by neighbour.

## Checks, with exit codes

All on a local production build of the branch's last site commit, port 3237, in the internal view, each under the chain's build mutex; outputs in `runs/session237/` (`c5_*.out`, `c6_*.out`; `c3_*` for the screenshots).

| Check | Result | Exit |
|---|---|---|
| `npm run build` | no "statement timeout" line | 0 |
| `npx tsc --noEmit` (after the build: `.next/types` and `content/` are written by it) | no error | 0 |
| `check-values`, restricted to `/grid`, `/network`, `/mix`, `/emissions` (42 addresses: the 29 new ones and 13 old ones through their redirects) | 1,178 of 1,178 values match | 0 |
| `check-routes` | pass 1: 185 of 185; pass 2 (as a visitor): 0 failed | 0 |
| `check-mix.mjs` (unchanged, through the redirects) | 36 of 36 | 0 |
| `check-network-map.mjs` (reads the address through the tool's words) | 31 of 31 | 0 |
| `check-ask-panel.mjs` (recorded replies, no model call; opens the Ask view) | 13 of 13 | 0 |
| `check-network-v3.mjs` | 32 of 33, then 31 of 33; its two waits were then corrected and NOT rerun (see "To finish") | 1 |
| `check-network-v3-hard.mjs`, `check-mix-v2.mjs`, `check-ask-ercot.mjs` (no model call: the route is stubbed in the page) | NOT run (see "To finish") | not run |
| The battery page is unchanged (`runs/session208/capture.mjs` at 1280) | `_nums.txt` differs from session 211's in 0 lines; `h` is 5016 | 0 |
| The python tests that touch what changed: 84 modules, 1,466 tests (104 skipped, as they skip on this machine) | OK | 0 |
| `tests/test_session237.py` (18 tests) | OK | 0 |
| Em dashes in the 45 changed files | 0 | |
| Screenshots, 18 pages: sideways scroll, "undefined" or "NaN", script errors | none | 0 |

- The first value check found 7 mismatches, all in the Exchange numbers: 3 were `-0` for a tie reporting zero (fixed), 4 were PJM's ties differing by 1 MW. Cause: the hourly refresh rewrote the network's snapshot at 07:05 UTC, between the page's cached read and the checker's read, and EIA had revised the hour. The Now and Exchange views now read the snapshot on each request (`fetchHourly(0)`), so a number shown is the object's own. A check that runs across the top of an hour can still meet a revised object; the existing `net|` keys of problem set E have the same property.
- NOT run: the whole `check-values` (unrestricted), the whole python suite (204 modules) and the clean-copy suite: these are the landing's. The design tools (Impeccable, AccessLint) were not run.
- The screenshots are of the build before the last two small changes (a token for the network's grey at its old value, and the checks); no page markup changed after them.

## Tests whose pins moved (each with a note "session 237")

- The file of a page that became a view (17 files, 27 lines, by `runs/session237/patch_tests.mjs`; then 3 more files): `test_session54`, `58`, `78`, `92`, `93`, `109`, `114_part2`, `118`, `120_page`, `122`, `123`, `124`, `133`, `137`, `148`, `168_mix`, `168_network`, `180`, `180b`. `app/network/page.tsx` is `components/grid/NetworkView.tsx`; `app/mix/page.tsx` is `MixView.tsx`; `app/emissions/page.tsx` is `Emissions.tsx`; `app/grid/[iso]/page.tsx` and `Reliability.tsx` are `YourGrid.tsx` and `Reliability.tsx`; what stood in `app/grid/page.tsx` is `Conditions.tsx`.
- `test_session203`: the Grid menu shows the one tool (it held the seven grid pages as "Your grid"); the list of the menu's addresses is session 203's less the ten folded ones, each of which must redirect.
- `test_session53` (`route_exists`) and `test_session110`: an address that redirects in `next.config.ts` counts as resolving (the home page's cards, the tour's stops and `lib/audience.ts` still name `/network`, `/mix` and `/grid/ercot`; those files are the home page's and the Games', not touched).
- `test_session137`: the Ask panel is in `AskView.tsx` (it stood between "Who runs this grid" and "Right now: demand").
- `test_session168_network`: the title "The grid network" was the page's own; the view exports `NetworkView`. `test_session54`: `revalidate = 3600` is the tool's page's. `test_session93`: the component is passed `page={{ keep, node }}`, its canvas ground is `PAL.ground`, the reads are imported by their full path.
- No check of a number was loosened.

## Decisions made without you

1. The address is `/grid?grid=<grid>&view=<view>`, with a view's own state under its own words (`mix`, `net`, `node`).
2. An address that names no grid: ERCOT, the first of the picker; but Network, Mix and Clean open on the Lower 48, as `/network`, `/mix` and `/emissions` opened (so an old link shows what it showed, and the old browser checks hold). The tabs and the picker always write the grid.
3. The old pages' files were moved into `site/components/grid/` and are what the views draw (the brief's words); they are not under `app/_retired`.
4. `/mix/clean`, `/mix/stress`, `/mix/v2` and `/network/v3` keep their lines of sessions 133 and 168 and arrive in two steps (tests pin those lines; the versioned addresses are session 239's).
5. On a grid's Now view "Right now: demand" comes first of the grid's blocks, and the Ask box, "Where the power comes from" and "How clean" are in the Ask, Mix and Clean views.
6. The six grids other than ERCOT are asked through `/ask`'s own form placed in the Ask view (it answers under the box); the old box opened `/ask?grid=`. ERCOT's panel keeps the context `/grid/ercot` (the context must be a path of the site, and the recorded fixtures use it).
7. `lib/pages.ts`: ten `related` lists that named a folded page name `/grid` now (two of them on Games entries: their address, name and line are untouched). `YOUR_GRID` is left in the file, unused.
8. The network's canvas reads `--color-ink`, `--color-panel`, `--color-muted`, `--color-accent`, `--color-rule`, `--color-down`, `--color-up` and a new token `--color-not-held` (the grey it always had, added to the base tokens, not to the brand). Under the brand its ground is white.
9. Three browser checks were edited, none dropped: `check-network-v3.mjs` and `check-network-map.mjs` read the address back as the network's own words and wait for the component to have written it; `check-ask-panel.mjs` opens the Ask view. `check-values` and `check-routes` gained the new addresses and kept the old.
10. A mistake of mine, said plainly: the last cycle held the build lock from 07:46 to 08:05 UTC, about ten minutes after its work had ended, because I edited the cycle script while it ran and it never reached its release. I gave the lock back by hand. Sessions 235 and 236 may have waited for it.

## For Samuel's ruling

1. The opening grid (decision 2): ERCOT for `/grid`, the Lower 48 for an old link to the network, the mix or emissions. One rule for all (ERCOT, or the Lower 48) is one line of `lib/gridtool.ts`.
2. The name: the menu says "The grid"; the title is the grid's own ("ERCOT: Electric Reliability Council of Texas") under the crumb "The grid".
3. The brand inside the folded blocks. The frame, the picker, the tabs, Now's sentence and numbers, Exchange and Ask are built from the shared components. The blocks carried over (the mix, the emissions blocks, the grid page's blocks, the network) keep their own markup inside the brand's wrapper and are restyled by the brand's rules; they were not rebuilt on `ToolSection` and `ToolTable`, so their headings and small type are not yet the battery page's. Color literals left in shared code they use: `lib/mixpage.ts` `yearShade` (a grey-to-cardinal ramp drawn on a canvas) and the fallback palette in `Network.tsx` (the tokens' own values). Rebuild them, or accept them as they are for 21 October?
4. The Mix view holds the mix page's nine views as a second row of choices under the tabs. Keep all nine there, or thin them?
5. The Lower 48 has no exchange number of its own in Now (it is the sum of its grids; the Exchange view lists the seven).
6. The redirects are permanent (308), as every folded page's before them: a browser keeps them.
7. The sentence of Now: its words.

## Not done

- No method note, replication or cross-check for the Grid tool (the review's section A names them as missing; not in this session's task).
- `docs/tools.md`, `docs/platform-tools.md` and the other documents that name `/network`, `/mix`, `/emissions` and `/grid/<iso>` as pages are not updated.
- `site/app/page.tsx` (the home page), the tour and `lib/audience.ts` still link the old addresses (they redirect); not touched by this chain's rule.

## To finish

Four browser checks are owed. The last cycle waited 14 minutes for the build lock (sessions 238 and then the orchestrator's landing of 235 held it) and gave up; the session was past its time. On a build of this branch (`cd site && npm run build && npx next start -p 3237`), under the lock:

```bash
node scripts/check-network-v3.mjs http://localhost:3237 > runs/session237/f_net.out 2>&1; echo "exit=$?"
node scripts/check-network-v3-hard.mjs http://localhost:3237 > runs/session237/f_hard.out 2>&1; echo "exit=$?"
node scripts/check-mix-v2.mjs http://localhost:3237 > runs/session237/f_mixv2.out 2>&1; echo "exit=$?"
node scripts/check-ask-ercot.mjs http://localhost:3237 > runs/session237/f_askercot.out 2>&1; echo "exit=$?"
```

- `check-network-v3.mjs`: 32 of 33 on its first run and 31 of 33 on its second (`runs/session237/c5_netcheck.out`). The failures are two assertions that read the address back. On `/grid` the component writes the address in the tool's words after the view is restored, and the check read it before that (it printed the redirect's own address, `?t=2021-02-15&prices=1&trace=1&view=day`). The two waits now also wait for `node=` in the address. That correction is committed and NOT yet run: if it still fails there, the fault is in the check's wait or in `Network.tsx`'s address effect, not in a number.
- `check-network-v3-hard.mjs`, `check-mix-v2.mjs`, `check-ask-ercot.mjs`: never run this session. `check-network-v3-hard.mjs` has no address reader to change and opens `/network`, which redirects; `check-mix-v2.mjs` opens `/mix/v2`, two redirects; `check-ask-ercot.mjs` expects the link "Ask ERCOT about this view" at `/grid/ercot`, which the Now view of ERCOT draws. Each may need a pin moved.

## The finishing pass

13 October 2026, 08:45 to 10:10 UTC, on the merged branch `task/237-238-grid-research` (this session with 238 and main), worktree `erw-144`. Not pushed. No model called. Outputs in `runs/session237/finish/`.

- **Said plainly: the merged tree was never built here, and none of the owed browser checks was run.** The pass waited 60 minutes for the build mutex (08:49 to 09:49 UTC, five other holders went first), then held it from 09:49 to 09:54 for two builds that each failed in under 30 seconds and one test run. The orchestrator then asked for the hand-back without a third cycle; the landing branch is built and checked by the orchestrator.
- **Owed and still owed** (the commands of "To finish" above, unchanged): `check-network-v3.mjs`, `check-network-v3-hard.mjs`, `check-mix-v2.mjs`, `check-ask-ercot.mjs`, and again `check-mix.mjs`, `check-network-map.mjs`, `check-ask-panel.mjs`; the whole `check-values`; `check-routes`; `npx tsc --noEmit`.
- **The merge did not build.** `npm run build` exit 1 (`c1_build.out`): `CssSyntaxError ... tokens.css:440:1: Missing closing } at .brand-a nav[data-segments] a[aria-current="page"]`. The merge of the two sessions' blocks in `site/app/tokens.css` lost the closing brace of this session's last rule. The brace and a blank line are back (commit `451080dd`); no rule changed. `tests/test_session237.py` gained a test that reads the file as a whole (every rule closed): no test did.
- **A failed CSS build is remembered.** The second build, four minutes after the fix, failed with the same message (`c2_build.out`, exit 1), though the file on disk parses (postcss, 147 nodes). The first build wrote `site/.next/cache/turbopack`, and the failed transform of `globals.css` was served from it. Remove `site/.next/cache/turbopack` before the next build of any copy that met the error. Not proven by a green build here: the third cycle was stopped before it took the lock.
- **The redirects in one step** (`site/next.config.ts`): `/mix/v2` to `/grid?view=mix&mix=day`, `/mix/clean` to `/grid?view=clean`, `/mix/stress` to `/grid?view=mix&mix=stress`, `/network/v3` to `/grid?view=network` (with `net=<its view>` when it names one, as `/network`'s line). Pins moved, each with a note: `test_session93`, `124`, `133`, `168_network`, `237` (which now also asserts that no destination is a folded address); `check-mix.mjs` expects `/grid` and the tool's words at the first hop. Not seen on a served site.
- **Links inside the tool** that named an old address name the tool: the panel's "grid page" link in `app/network/Network.tsx` (`/grid?grid=<grid>`), the withheld-mix note's link (`/grid?grid=caiso&view=mix&mix=day`, was `/mix/v2`), the written-page citation of `components/ask/AskPanel.tsx` and `app/ask/AskForm.tsx` (`/grid?grid=<grid>`). The context `view: "/grid/ercot"` of the Ask panel is not a link and is as it was (decision 6).
- **Documents:** one row in `docs/tools.md` (the Grid tool, above the rows of its views), one clause in tool 26's row of `docs/platform-tools.md`, two lines of `package/llms.txt`. The briefing is part of the chat's system prompt, so `site/lib/chat/spec.json` was exported again (`ask.py --export-spec`, no model call; `check_spec.py` exit 0): `/ask` is now told `/research` and the Grid tool's address. Two tests were red until it was (`test_session58`, `test_session92`).
- **Run, with exit codes:** `npm run build` 1, then 1 (above). `test-analysis-flow.mjs` 0. `test-digest-chart.mjs` 0. The python tests in one process, 95 modules (the modules either session moved a pin in, `test_session203`, `215`, `235` to `238`, and those that pin a file touched here): 1,749 tests, OK, 130 skipped, exit 0 (`c1_tests.out`; run before the brace test was added; `test_session237` alone afterwards: 19 tests OK; `235`, `236`, `238` afterwards: 59 OK).
- **`check-mix-v2.mjs`, read not run:** it is session 94's check of the page retired by session 133. It looks for `data-stack=`, `data-side-by-side=` and `data-caiso-join=`, which only `app/_retired/mix-v2/page.tsx` writes, so it cannot pass on any build since session 133, on main either. The mix's "day" view is held by `check-mix.mjs`. It needs a ruling (rewrite it against the Mix view, or retire it), not a moved pin.
- **`check-ask-ercot.mjs`, read not run:** it sends no question to a model (the route is replaced in the page by the recorded reply of session 92), so all of it can run at spend USD 0.
- **`check-values` and its exit, read not run:** a run that passes returns without `process.exit` and ends cleanly. A run that fails calls `process.exit(1)` after its lines; session 238's `Assertion failed: !(handle->flags & UV_HANDLE_CLOSING), file src\win\async.c, line 94` (exit 127) is that path on Windows, in code libuv compiles for Windows only. GitHub's runner does not run `check-values` (`code-branch.yml` runs `check-routes` and `check-no-request`), so it cannot meet it.
- A mistake of mine: the first lines I wrote with a shell heredoc lost their backslashes, which cost about four minutes before the lock wait; and between the two failed builds I kept the lock (five minutes in all) instead of giving it back, to retry the build.

## The landing

- Landed in one push with sessions 238, 239 and 240 and session 236's follow-up (ERCOT's reserve adders counted on the datacenter page), on `task/237-238-landing`. The five branches were merged by the orchestrator: the menu is session 239's without the pages session 237 folded into the Grid tool; `tokens.css` keeps every session's block (each identical to its own branch's, checked); the pins two sessions had moved against each other were set (the Grid group of the menu, the one-step `/network/v3`, the count of entries a group, the license day moved to 21 October on `main`).
- The whole suite in a clean worktree at `11c833a3`: exit 0, 3,831 tests OK, 237 skipped. After it only `tokens.css` (one closing brace lost in the merge, which failed the first build), the finishing pass's last three commits and a merge of `main` followed; the modules they touch were run again on the clean copy: exit 0.
- `npm run build` on the merged tree: exit 0, no "statement timeout" line. `check-values` on every page: exit 0, 4,590 of 4,590. `check-routes`: exit 0, 203 pages as a visitor, 0 failed. Exit 0 each: `check-no-request`, `check-network-v3` (33 of 33), `check-mix` (36 of 36), `check-analysis` (279 of 279), `check-board` (36 of 36), `check-datacenters` (11 of 11), `check-demand` (102 of 102), `check-datacenter-scenarios` (119 of 119).
- **The first push did not land.** `3eeb47a7`, pushed 10:35 UTC after snapshot `s237-before`: check run 38384419863 failed at "Site build and check-routes", in its warm-up step: `/network` now answers 308 (it is a view of the Grid tool), and `scripts/warm-live.mjs` asked each listed page with redirect "manual" and counted anything but 200 as a page that never answered. Nothing was merged or deployed. The snapshot script had the same fault waiting: after the deploy every snapshot would have been "incomplete" at `/network`.
- The fix (`bd133b67`): `scripts/snapshot-live.mjs` gains `visit`, which follows a redirect inside the site as a visitor's browser does (three hops at most, never off the site) and keeps the hops as a line of the page's text; the warm-up uses it. The list of 25 pages is unchanged. Tried on the local build: the warm-up 25 of 25, `/network` read as "200 /network (308 /grid?view=network)". `tests/test_session237_visit.py` holds it. **This changes the snapshot tool of rule 8: for your ruling.**
- `python scripts/freeze.py status`: exit 0, no freeze. Before snapshot `s237-before2` (10:46:23 UTC, its own command, with the patched script: 25 pages, 0 failed), then the second push.
- Check run 38385666019: success at 10:57 UTC; merged into `main` as `01161064`. Production served the new build from 10:58:34 UTC (the home page's style sheet changed name). After snapshot `s237-after2` (10:58:54 UTC, 25 pages, 0 failed).
- `compare s237-before2 s237-after2`: exit 1, 403 differences in all, every one expected:
  - On each of the 25 pages, 16 lines of the menu (400): gone, "ERCOT peak premium", "Lease tool", "The network", "Grid conditions", "Energy mix", "Emissions", "Consumption", "Your grid" and its line of seven grids, "Where the resources are", "Storage build-out", "Who owns the batteries", "Companies", "Automated Analysis" (each "in review"); new, "The grid in review" and "Research in review".
  - On `/network`, 3 more: the new line "[redirected: 308 /grid?view=network]", and the in-review page's heading "The network" is now "The grid".
  - No checked number is on any of the 25 pages (every page is in review), so none could move.
- The remote branches `wip/236b-adders`, `wip/237-grid`, `wip/238-research`, `wip/239-merges`, `wip/240-top-blocks` and `wip/237-238-finish` are deleted: all of each is on `main`.

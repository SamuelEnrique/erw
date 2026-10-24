# Session 1172 report: every old address, tested

23 October 2026, on samueloldlaptop (the old laptop), session 1172 of `queue/done/078-day-24-october-code-grid-tool-2.md`. Branch `wip/1172-grid`, cut from `wip/1171-grid` (chain 077's landing B is not on main), worktree `C:\Users\lossa\Documents\erw-1172`. Code-only, as the brief sets chain 078: no build, no server, no browser. Model spend USD 0. No warehouse data written, no Supabase write, no request to any publisher (four requests to the site's own production address, unfollowed, to read where a redirect sends: below).

## Read these first

- **A node test of every old address: `site/scripts/test-grid-addresses.mjs`, 8 tests over 61 addresses, exit 0.** It loads the redirect list from `site/next.config.ts` itself and applies it as Next 16 does (`prepare-destination.js`, read in the test where `site/node_modules` is present): the rules in order, the `has` query conditions anchored and matched on a repeated word's last value, their named groups into the destination, and the old address's query carried under the destination's words. `/ask`'s own redirect (`app/ask/page.tsx`) is modelled from its two lines, which the test pins. The landed query is then read as `app/grid/page.tsx` reads it (`gridPick`, then the mix page's own choice on the Mix and Clean tabs, the page's lines pinned).
- **Every case passed as the code stands: no change to `site/lib/gridtool.ts`.** No old address lands on the wrong tab or grid.
- **What the cases cover**, each a line of the table written from the code and the method notes:
  - `/network` and `/network/v3`, bare and with each network view (`day` with `t`, `live`, `evening`, `uri_2021`, `east_heat_2025`), a grid as an EIA-930 code (ERCO, CISO, PJM, NYIS, ISNE, SWPP), BPAT (the Lower 48 with BPAT's panel), `shape=gravity` (the Gravity tab, the day kept) and `shape=map`;
  - `/mix` bare and with `ba`, `state`, `grids`, `mixp=month` and its views (`clean` to the Clean tab; `now`, `day`, `stress`, `history`, `forecast`, `duck` to the Mix tab with that view); `/mix/v2` (with `grid`, `period`, `vs`), `/mix/clean`, `/mix/stress`, `/emissions`;
  - the seven `/grid/<iso>` (the Mix tab, that grid, its panel's node), with a word after (`/grid/ercot?view=network`); `/grid/caiso/alerts` is not redirected;
  - `/ask`, `/ask?grid=ercot&q=...`, `/ask?grid=CISO` (the Ask panel beside the grid, the question kept);
  - on `/grid` itself, the old words: `view=now`, `view=exchange`, `view=ask`, `ask=1`, `mix=clean`, `shape=gravity` with `view=network`, `grid=ERCO`, `grid=SWPP`, `ba=erco`, `grids=pjm,miso`, `node=BPAT`, `node=ERCO` alone, a `t` that is not a date (no day), an address it does not understand.
- **For every redirect the test also asserts** that every word of the old address other than `view` is carried unchanged, that the network component reads `net` as its view and the page's node as its grid (`netFromPage`), that each address arrives in one step, and that every rule to `/grid`, every `OLD_VIEWS` word, every grid of the eight and every tab is reached by a case.
- **The round trips:** `gridHref` for every grid and tab, with and without a view's own words (`net`, `t`, `node`; `mixp`, `q`; `year`), reads back to the same grid, tab, node and day; so do the picker's carried day (`lib/carry.ts` `KEEP_DAY`, both tabs it carries on), the map's region link (`carryMoment`) and the network's own writes through `netToPage` on each tab's `keep`.
- **The route check lists 15 more old addresses** (`site/scripts/check-routes.mjs`, the block "session 1172"): one for each rule and word the list lacked; the node test asserts every case marked `route` (46 of the 61) is in the list. The route check itself is not run (it needs a server).
- **Production agrees with the model.** Four requests to `https://erw-flame.vercel.app`, not followed: `/network?view=day&t=2021-02-15&grid=ERCO&prices=1` answers 308 to `/grid?view=network&t=2021-02-15&grid=ERCO&prices=1&net=day`; `/mix?view=clean&grids=pjm` to `/grid?view=clean&grids=pjm`; `/grid/ercot?view=network` to `/grid?view=network&grid=ercot`; `/mix?view=now&ba=erco&mixp=month` to `/grid?view=mix&ba=erco&mixp=month&mix=now`. Each word once, the destination's `view` over the old one, as the test applies it.

## What to review

Nothing a visitor sees changed. After the landing, on production:

1. Open `https://erw-flame.vercel.app/internal/open`, paste the token, press **Open the internal view**.
2. Open `https://erw-flame.vercel.app/network?shape=gravity&grid=ERCO`: the Gravity tab, ERCOT.
3. Open `https://erw-flame.vercel.app/mix?view=now&ba=erco&mixp=month`: the Mix tab, ERCOT, the energy mix panel on "By month".
4. Open `https://erw-flame.vercel.app/ask?grid=ercot&q=What+was+the+peak%3F`: the Mix tab, ERCOT, the Ask panel open with the question in the box (not sent).
5. Open `https://erw-flame.vercel.app/grid?grid=ercot&view=network&net=day&t=2021-02-15&node=BPAT`: the Network tab, ERCOT, BPAT's panel, the day 2021-02-15.
6. Read the table of cases at the head of `site/scripts/test-grid-addresses.mjs` (`CASES`), and the paragraph added to `docs/methods/grid_network.md`, "One page, four tabs, and the Ask panel".
7. Screenshots: not taken, no build.

## Checks

- `node --import ./scripts/alias-register.mjs scripts/test-grid-addresses.mjs` (new, in `site/`): exit 0 without `node_modules` (the Next source part skipped, said in the output), exit 0 again through the junction (the Next source read): "8 tests passed, 61 addresses". A case changed by hand to a wrong tab (`/emissions` to Mix) fails with the address, what it got and what was wanted (a scratch copy, deleted).
- `python -m unittest`, one file at a time, on 50 test files: every one that reads `check-routes.mjs` or `grid_network.md`, with `tests.test_session237` and `tests.test_session299` (they read `gridtool.ts`) and the new `tests.test_session1172` (4 tests; it runs the node test): 50 of 50 exit 0.
- Type check through the junction: `npm run content` exit 0, `npx next typegen` exit 0, `npx tsc --noEmit -p .` exit 0; the junction removed (`cmd /c rmdir`), the main copy's `node_modules` intact.
- No build, no route check run, no check-values run: none possible without a build.

## The landing

- None: chain 078 is code-only until a person lands chain 077's landing B (`wip/1162-grid`); this branch stacks on it.

## To finish

- Land with the chain's combined landing (after landing B). The route check then asks the 15 new addresses (each through its redirect, then the page in review as a visitor); expected: 200 each, no "undefined", no new "no data".
- At the landing, `node --import ./scripts/alias-register.mjs scripts/test-grid-addresses.mjs` in `site/` (or `tests.test_session1172`) with `node_modules` installed, so the Next merge it models is read against the installed Next.

## Decisions made without you

- **The redirects are modelled, not served:** the test applies `next.config.ts`'s own list with Next's merge rule, read from Next's source; the four production answers above confirm the rule on Vercel. A rule to `/grid` with a pattern in its source (`:path*`) would fail the test's first case, which says it cannot be matched here: there is none today.
- **`/ask`'s redirect is modelled from its two lines** (pinned by the test, as `tests/test_session299.py` pins them); the page is chain 075's directory and was not changed.
- **The route check lists 46 of the 61 cases**, one per rule and word, not every case: each listed address is a full `/grid` render in both passes, and a second address of the same rule asks nothing new of the server.
- **`node=BPAT` with no grid opens the Lower 48 with `named` false**, where `grid=BPAT` gives `named` true; `named` is read by no page or component, so the test does not pin it either way.

## For Samuel's ruling

- Whether the route check should also read the landed page's `data-grid-tool` and `data-grid-tool-view` for each old address (the tab and grid the test expects), so the check against a server says the tab, not only the status. Recommendation: yes, from the test's table, at a landing where it can be run once before it gates.
- Whether an old address written with a capital or a lowercase code (`/network?view=Day`, `/network?grid=bpat`) should be read: today the first loses its view (the condition is lowercase, as the old page wrote it) and the second its panel (a code is read in capitals, as the network wrote it). No such address was ever written by the site; recommendation: leave it.

## Files

- New: `site/scripts/test-grid-addresses.mjs`, `tests/test_session1172.py`, this report.
- Changed: `site/scripts/check-routes.mjs` (15 addresses), `docs/methods/grid_network.md` (one paragraph in "One page, four tabs, and the Ask panel").
- Not changed: `site/lib/gridtool.ts`, `site/next.config.ts` (every case passed).

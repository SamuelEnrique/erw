# Session 1423 report: the network component's words against its panels

24 October 2026, from about 11:10 to 11:50 UTC, on samueloldlaptop (the code machine, the old laptop), the fifth session of `queue/done/111-day-28-october-code-grid-tool-6.md`. Branch `wip/1423-grid`, cut from `wip/1422-grid` (sessions 1152 to 1422 stacked, not on main), worktree `C:\Users\lossa\Documents\erw-1423`. Code, tests and documents only (`runs/c077/brief.md`: no build, no server, no browser). Model spend USD 0. No warehouse data written, no Supabase write, no request to any publisher. Light anon reads of Supabase's REST API: one same-figures walk, 19 distinct requests, the key never printed or written. Production was not read (HTTP 402).

## Read these first

- **What the component writes, and what the panels key.** The network component (`site/app/network/Network.tsx`) writes figures in the browser that the server panels `grid_network_<grid>` and `grid_gravity_<grid>` key in the hour it opens on:
  - the side panel of the picked grid (on the Grid tool it opens on the grid in view): each tie's MW and direction, the net import or export, the demand;
  - the gravity shape's hover cards (`lib/networkGravity.ts` `gravityTip`): net generation, net import, the import as a percent of generation;
  - the map's line cards (`lib/networkMap.ts` `edgeTip`, session 1156): a tie's MW, only for the panel's ties.
- **Two differences found, both fixed in the component's words, no keyed figure touched:**
  - **The gravity cards' share was one decimal; the panel writes two.** CAISO in the hour shown: the card said "8.6 percent", the panel "8.58". All seven grids differed this way. The cards now write every figure through `lib/format.ts` `shown`, the panel's own formatter.
  - **A net of exactly zero read as an import in the side panel; the panel calls it an export** ("sent out, on net, 0"; `netValue` signs export as zero or more). The side panel now says "Net exports this hour, 0 MW". No grid has a zero net on today's snapshot, so nothing visible moves.
- **One latent difference closed:** in the live week the side panel wrote whole MW (its own `fmt`), the panel `shown` (two decimals for a figure that is not whole). EIA-930's MW are whole, so they read alike today. In the live week the side panel now writes MW through `shown` too. A story and a replayed day keep whole MW.
- **The side panel's MW words moved to a pure module, `site/lib/networkSide.ts`, their arithmetic unchanged:** `sideTies`, `sideNet`, `sideFormat`, `sideNetLabel`, `sideNetMw`, `sideTieWords`, `liveDemand`. Two lines stay in `Network.tsx` because older tests pin them (the opening hour, session 124; the demand's `netsnap` key, session 54). The test runs those two lines' own text with `new Function`, so it follows the component as it stands.
- **The proof: `site/scripts/test-network-words.mjs` (new, 8 tests).** Data: the committed snapshot (`site/data/grid_network.json`) and the live week's demand and generation from session 1165's fixture (the same build, aligned as the page aligns them). For the seven ISO grids and the Lower 48 it computes every MW the component's words would write, through its own functions, and compares each with the panel's figure for the same tie and hour, as each writes it:
  - the opening hour equals `shownHour`;
  - the side panel: each tie, the net and its direction, the demand and its key;
  - the Lower 48: the seven grids' net export, each grid picked;
  - the gravity cards: generation, net import, share, on the circle's card and on the line's;
  - the map's line cards, every grid;
  - typed cases for the live week, a story and a day;
  - source pins.
  - 153 figures compared, all equal.
  - With the share or the zero rule put back as it was, the test exits 1.
- **No server figure moved.** `same-figures.mjs` on the Network and Gravity tabs of ERCOT, CAISO and the Lower 48, code before (`26df43ab`) and after, the same live answers: every page the same, 254 figures.

## What to review

After the landing (none yet; see below), on production:

1. Open `https://erw-flame.vercel.app/internal/open`, paste the token, press **Open the internal view**.
2. Open `https://erw-flame.vercel.app/grid?grid=caiso&view=gravity&shape=gravity`. Hover the CAISO circle: "Net generation N MW (EIA-930)", "Net import N MW, ...", then the share with two decimals ("8.58 percent of its net generation" on the snapshot of 23 October). Scroll to "What the gravity shape draws": CAISO's row gives the same three figures, the share as "8.58".
3. Hover the line from the Lower 48 to SPP: "Net export N MW", the share with two decimals; SPP's row in the table gives the same, signed ("-821", "-2.32").
4. Open `https://erw-flame.vercel.app/grid?grid=ercot&view=network`. The side panel opens on ERCOT: "Net imports this hour" and its MW, the demand, each tie "N MW in" or "out". Scroll to "ERCOT, the hour shown": the same net, demand and ties (signed from ERCOT's side there).
5. Pick "A day since 2019", 2021-02-15: the side panel still writes whole MW, "MW on average", as before.
6. Read `docs/methods/grid_network.md`, the paragraph "Session 1423, the network component's words against its panels." and its Decisions.
7. Screenshots: not taken, no build.

## Checks

- Precheck for session 1423: run by the orchestrator, exit 0.
- `node scripts/test-network-words.mjs` (new): exit 0, 8 tests, 153 figures.
  - With the old one-decimal share and the old zero sign planted back: exit 1, on CAISO's share. Restored, exit 0.
- Node tests that read the changed files, one at a time, each exit 0: `test-gravity.mjs` (6 of 6, unchanged: the old words stay the default), `test-network-map.mjs`, `test-network-split.mjs`, `test-grid-keys.mjs`, and `test-grid-render.mjs` (181 cases, through the junction).
- `node --check scripts/check-network-v3.mjs`: exit 0. It is a browser check, not run (no server).
- `same-figures.mjs`, 6 addresses (the Network and Gravity tabs of ERCOT, CAISO and the Lower 48), live answers, a temporary worktree of `26df43ab` (removed): exit 0, every page the same, 254 figures.
- `python -m unittest`, one module at a time:
  - the 22 modules that read `Network.tsx`, `networkGravity.ts`, `NetworkGravity.tsx` or `check-network-v3.mjs`;
  - the 21 further readers of `grid_network.md`;
  - `test_session1423` (new, 3 tests).
  - First run: `test_session124` and `test_session54` exit 1, on two lines this session had moved (the opening hour; the demand's `netsnap` key). Both lines were put back word for word, and both modules then exit 0.
  - Every other module exit 0, the first time. None was stopped for memory.
- `npx eslint` on the five changed code files: exit 0, one warning that was there before (a memo's dependency list).
- Type check through the junction, once at the end: `npm run content`, `npx next typegen` and `npx tsc --noEmit -p .` exit 0 each. The junction was removed with `rmdir`; the main copy's `node_modules` is intact.
- Not run (the brief): the build, check-values, check-routes, the browser checks, screenshots.

## The landing

- None in this session: production answers HTTP 402 and this window runs no gate (chain 107's note). It lands with the chain's combined landing (`wip/1417-grid` and the sessions stacked on it). Pushed: `wip/1423-grid`.

## To finish

- At the landing, `node scripts/check-network-v3.mjs <the local site>`: its day-view sign now reads `net > 0` for "imports" (it read `net >= 0`; 2021-02-15 is not a zero, so it holds as before).
- Expected differences at the landing (in the browser only, no served HTML, no key): every gravity card's share has two decimals instead of one. The side panel is unchanged on today's snapshot (whole MW, no zero net).
- If the committed snapshot is rebuilt, `test-network-words.mjs`'s first test asks for session 1165's fixture to be read again (`snapshot_built` must match).

## Decisions made without you

- **The fix is in the component's words, never in a keyed figure.** The panels and `gridKeys.ts` are untouched (same-figures above).
- **A story and a replayed day keep whole MW.** They are not the panel's hour; the day view's averages ("MW on average") are no panel figure by design, and `check-network-v3.mjs` reads them whole. So only the live week's shared hour is compared.
- **The side panel's share of demand, hub price, carbon intensity, batteries, trace and twelve months are not compared.** None is a figure of these two panels. The share is computed from the net and the demand, both compared. Carbon intensity keeps its own key.
- **A zero net is an export**, as the panel and `netValue` sign it, in every view; the browser check's sign rule was changed to match.
- **`gravityTip` and `netWords` take the formatter as an optional argument.** The component passes `shown`; without it they write session 1153's words, which `test-gravity.mjs` pins, so no assertion there changed.
- **`tests/test_session1153.py`'s pin of `gravityTip(hovered, at, hover.kind)` now reads `gravityTip(hovered, at, hover.kind`**, with a new pin of the full call with `shown`. Extended, not removed.
- **At an exact zero the gravity card says "No net exchange (0 MW)" and gives no share**, where the panel writes 0 and 0 percent. No number differs; one is left unwritten.
- **The two pinned lines stay in `Network.tsx`** and the test runs their text, rather than a module copy of them that the component would not use.

## For Samuel's ruling

- None new.

## Files

- New:
  - `site/lib/networkSide.ts`;
  - `site/scripts/test-network-words.mjs`;
  - `tests/test_session1423.py`;
  - this report.
- Changed:
  - `site/app/network/Network.tsx`: the side panel through `networkSide.ts`, its pinned lines kept;
  - `site/app/network/NetworkGravity.tsx`: passes `shown`;
  - `site/lib/networkGravity.ts`: `netWords` and `gravityTip` take the formatter;
  - `site/scripts/check-network-v3.mjs`: one sign;
  - `tests/test_session1153.py`: one pin extended;
  - `docs/methods/grid_network.md`: the session 1423 paragraph and its Decisions.
- On this machine only, in the session's scratchpad: every test's output and the same-figures lists.

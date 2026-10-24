# Session 1170 report: the outside grids' demand in the replay

24 October 2026 (UTC), on samueloldlaptop (the old laptop), the seventh session of `queue/done/078-day-24-october-code-grid-tool-2.md`. Branch `wip/1170-grid`, cut from `wip/1169-grid` (chain 077's landing B is not on main), worktree `C:\Users\lossa\Documents\erw-1170`. Code-only, as the brief sets chain 078: no build, no server, no browser. Model spend USD 0. No warehouse data written, no Supabase write, no request to any publisher; two light anon reads of Supabase's REST API (below).

## Read these first

- **The Grid pack's blind spot 11, drawn where the address names a day.** When `/grid` is opened with `net=day&t=<day>`, the server panels draw that day's figures from the replay's committed file (`site/public/network/daily_<year>.json`), each keyed, with a one-line source on hover:
  - **Network tab**, first in `grid_network_<grid>` (`data-grid-replay-day="<BA>"`): for the balancing authority in the address (`node`, else the grid's own; BPAT as well as the seven ISO grids), the day's demand, its net export or import over the ties with a flow that day, and how many ties held a flow, each the day's average MW written whole. "not held" in the tool's one look (`Missing`, the reason on hover) where the file holds no demand: no series for that authority (CENACE, BC Hydro) or a blank day (session 109's band, or not reported).
  - **Gravity tab**, one line under the table in `grid_gravity_<grid>` (`data-gravity-day`): the grid in view's demand that day, and that the shape still draws the live hour (ruling 1a: sized by net generation, held by hour for the live week only). The Lower 48: "not held" (the files hold each authority's demand, not the whole's). The table's window sentence names the day when one is in the address; without one it reads as before, word for word.
- **Keys.** Demand: `fmt|n0|file|public/network/daily_<year>.json|demand.<BA>.@<day>`, session 1166's `file|` kind extended (`site/scripts/check-file.mjs`: the replay's files under `site/public/network/`, and a path segment `@<day>`, the element at that day's place in the file's `days`). Net and ties: `fmt|n0|netday|<export|import>|<BA>|<day>` and `netday|ties|<BA>|<day>`, a new kind recomputed by check-values from the same committed file (`netdayValue`, `site/lib/gridReplay.ts`): a sum over the links is not a path. Both named in `docs/methods/grid_network.md` (the note `/grid` links; check-methods' `figures()` and `named()` say named).
- **Neither daily table is in the live set**: anon reads of `series` for `eia930_daily_demand` and `eia930_daily_interchange` (`limit=1`) returned `[]`; `catalogue` says `eia930_daily_interchange` `in_live_set` "no". So the file is the figure's source and check-values checks each key against it alone.
- **On 2021-02-15** (`daily_2021.json`): BPAT demand 7,930 MW (7,929.6), net export 8,121 MW over 18 ties; ERCO demand 50,152 MW (50,151.8), net import 886 MW over 2 ties.
- **Held grids:** EIA-930's daily demand and interchange are public for every grid (`site/data/license_status.json`); the panels draw no hub price; nothing held is drawn.
- **No figure that stood moved**: without a day in the address both panels render as before; `NetworkFigures.tsx`'s figure count and spacing (tests 1153, 1159) are unchanged, the new figures sit in `components/grid/ReplayDay.tsx`.

## What to review

After the landing (none yet; below), on production:

1. Open `https://erw-flame.vercel.app/internal/open`, paste the token, press **Open the internal view**.
2. Open `https://erw-flame.vercel.app/grid?grid=ercot&view=network&net=day&t=2021-02-15&node=BPAT`. Under the network, first in the panel: "Bonneville Power Administration, the day picked (2021-02-15, EIA's Eastern day)": demand 7,930, net export 8,121, 18 ties. Hover each: file, filter, day.
3. Open `https://erw-flame.vercel.app/grid?grid=ercot&view=network&net=day&t=2021-02-15`: "Electric Reliability Council of Texas, Inc., the day picked (...)" (demand 50,152, net import 886, 2 ties), above "ERCOT, the hour shown".
4. Same address with `node=CEN`: demand "not held" (hover: the file holds a daily demand for 52 authorities, none for CEN).
5. Open `https://erw-flame.vercel.app/grid?grid=ercot&view=gravity&shape=gravity&net=day&t=2021-02-15`: under "What the gravity shape draws", the line "The day picked in the replay, 2021-02-15 ...: ERCOT's demand averaged 50,152 MW ... The shape above still draws the live hour". The note above the table names the day.
6. `https://erw-flame.vercel.app/grid?view=gravity&shape=gravity&net=day&t=2021-02-15` (the Lower 48): "not held".
7. The same addresses without `net=day&t=...`: the panels as before.
8. View source on step 2, search `data-grid-replay-day` and `netday|`.
9. Screenshots: not taken, no build.

## Checks

- Anon reads: `series?table_name=eq.eia930_daily_demand&limit=1` and `...eia930_daily_interchange...`: `[]`; `eia930_all_demand`: a row (the read works); `catalogue` for the two: `eia930_daily_interchange` `in_live_set` "no".
- `node --import ./scripts/alias-register.mjs --import ./scripts/tsx-register.mjs scripts/test-grid-replay.mjs` (new, 4 tests, through the junction): exit 0.
- `node --check` on `check-values.mjs`, `check-methods.mjs`: exit 0.
- `tests.test_session1170` (new, 9 tests, it runs the node test): exit 0.
- `python -m unittest`, one file at a time, the 124 files that read a changed file (grep of `tests/` for `NetworkFigures`, `NetworkView`, `gridtool`, the Grid page, `next.config`, `check-file`, `check-values`, `check-methods`, `grid_network_v3`, `grid_network.md`, the Grid pack): 123 exit 0, `tests.test_session473` exit 1 (its list of the files that may draw `components/mix/Now.tsx`: `ReplayDay.tsx` takes `Missing` from it, drawn by the Grid page only); the list extended by one entry with its comment, as session 1154 did, then exit 0. Then the 44 other files that walk `site/` (os.walk, listdir, glob): exit 0 each.
- Node tests, one at a time: `test-caiso-alerts`, `test-check-values-run`, `test-check-values-slow`, `test-grid-balance`, `test-grid-exchange`, `test-grid-keys`, `test-mix-hourly`, `test-network-map`, `test-scarcity-strip`, `test-gravity`; with the alias and tsx loaders `test-grid-file-keys`, `test-grid-held`, `test-grid-replay`: exit 0 each.
- check-methods' `figures()` and `named()` on the four new key forms against `grid_network.md`: every one named.
- Type check through the junction: `npm run content` exit 0, `npx next typegen` exit 0, `npx tsc --noEmit -p .` exit 0; the junction removed (`cmd /c rmdir`), the main copy's `node_modules` intact.
- No build, no check-values or check-methods run against a page: none possible without a build.

## The landing

- None: chain 078 is code-only until a person lands chain 077's landing B (`wip/1162-grid`); this branch stacks on it.

## To finish

- Land with the chain's combined landing (after landing B): the build; check-values on `/grid,/network` plus two addresses with a day (for example `/grid?grid=ercot&view=network&net=day&t=2021-02-15&node=BPAT` and `/grid?grid=ercot&view=gravity&shape=gravity&net=day&t=2021-02-15`, added to check-values' page list with their floors from a passing restricted run); `check-methods.mjs --values <the run> --write`; confirm on the Vercel deploy that `/grid` reads `public/network/daily_*.json` on the server (the `outputFileTracingIncludes` line), else the panel says the file could not be read; check-390 on the new table; screenshots at 1280 and 390 under `docs/brand/review-1170/`; the snapshots before and after (expected: no difference on the snapshot's addresses, which name no day).

## Decisions made without you

- The figures are the day in the address when the page was opened (server-drawn); a day picked in the replay moves the address, and the page opened again (or a grid picked, which carries the day) draws it. Said in the panel's note.
- The day is held to the replay's first and last day (`clampDay`), as the component holds it; an address outside says which day it opens on.
- The Network tab's day is the node's (the address's `node`, else the grid's own); the Lower 48 without a node shows no day.
- Whole MW behind `fmt|n0|`, as the browser panel writes them; the net is the sum of the one-decimal flows held to one decimal, so page and check agree.
- A new kind `netday|` for the net and the ties beside `file|` for the demand: the brief asked for `file|`; a path cannot hold a sum of up to 18 ties. Both read the same committed file.
- The server reads the file from `site/public/network/` (`site/lib/gridReplayFile.ts`) and `next.config.ts` traces those files into `/grid`'s function; a failed read is said, never filled, and names no server path.
- `tests/test_session168_network.py` and `tests/test_session299.py` pinned the two `<NetworkView ... />` calls, which now pass `day={p.day}`: each assertion kept as a prefix and a second assertion added for the full call; none removed.
- `check-methods.mjs`: a `file|` path ending at `@<day>` is the figure of its last name that is not an instance (`demand`); other paths read as before.
- One sentence added to the Grid pack's item 11 (`docs/reviews/packs/grid.md`).

## For Samuel's ruling

- Whether the browser's day picker should reload the server panel (a navigation instead of `replaceState`), so the keyed day follows the picker without a reload. Recommendation: keep `replaceState` (no reload while playing the year) and leave the server panel to the address.

## Files

- New: `site/lib/gridReplay.ts`, `site/lib/gridReplayFile.ts`, `site/components/grid/ReplayDay.tsx`, `site/scripts/test-grid-replay.mjs`, `tests/test_session1170.py`, this report.
- Changed: `site/components/grid/NetworkFigures.tsx`, `site/components/grid/NetworkView.tsx`, `site/lib/gridtool.ts` (`day` in `gridPick`), `site/app/grid/page.tsx`, `site/next.config.ts`, `site/scripts/check-file.mjs`, `site/scripts/check-values.mjs`, `site/scripts/check-methods.mjs`, `docs/methods/grid_network_v3.md` (the chain 078 section with its Decisions), `docs/methods/grid_network.md` (the key list), `docs/reviews/packs/grid.md`, `tests/test_session168_network.py`, `tests/test_session299.py`, `tests/test_session473.py`.

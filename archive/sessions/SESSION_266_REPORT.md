# Session 266 report: the Grid tool, deep, and the gravity view

Energy Research Warehouse (ERW), the chain of 14 October 2026. Branch `wip/266-grid-pack`, cut from `main` at `5b515cd0`, worktree `erw-142`, port 3266. Brief: `runs/chain_oct14/brief_266.md`. Model spend USD 0 (no model call).

## Read these first

- **The review pack:** `docs/reviews/packs/grid.md` (the form of `tests/test_session262.py`). `docs/howitworks/grid.md` is removed (`git rm`); its content (numbers, sources table, demo) is folded into the pack. `docs/howitworks/README.md` row points at the pack. No other live document linked the old note.
- **The gravity shape** (task 4, the one new view the owner named): a third toggle "Gravity" beside "Map" and "Network" (`site/app/network/Network.tsx`), drawn as SVG by `site/app/network/NetworkGravity.tsx` from the rule in `site/lib/networkGravity.ts`. The Lower 48 at the center; each of the seven ISO grids a circle whose area is its EIA-930 net generation in the hour shown; a net importer pulled toward the center, a net exporter pushed out, by net imports over generation (full pull at 25 percent). Same hour, selection, colors (tokens only), hover card (the name) and panel as the other two. Rule written in `docs/methods/grid_network.md`, "The gravity shape (session 266)". Generation is a new read beside the week's demand (`liveExtras()` in `site/app/network/data.ts`, `eia930_all_generation`, the seven and US48).
- **Now's sentence** (task 1): it existed and was keyed for demand, the largest source, the exchange and carbon. Added: how old the exchange's hour is, "N hours before the latest hourly refresh of EIA-930's interchange (time UTC), which EIA publishes about two days late", keyed `net|lag|<hour>|<refresh>` (new branch of `netValue()` in `site/lib/network.ts`; `check-values` resolves it with no edit to `check-values.mjs`). Guard: a grid with no tie in the hour now reads "not reported" with a line saying so (it read the Lower 48's "by grid" before).
- **The lag under the chart** (task 3): one line under the network, computed from the snapshot, same key: "The newest hour shown, 2026-10-12 03:00 UTC, began 53 hours before this week's latest hourly refresh (...): EIA-930 publishes a balancing authority's interchange for a local day on the second morning after it, so the network runs about two days behind the clock."
- **Replication** (task 2): `site/public/grid/erw_2026_grid_replication.csv` (written by `site/scripts/write-grid-replication.mjs` from the page's own reads: the Storage snapshot, `completeHour()`, demand and generation through the anon key), `.do` (not run: no Stata here) and `.py` (run). `site/scripts/check-grid-replication.mjs` compares the mirror with the page value by value: see Checks.
- **Ask** (task 5): `package/llms.txt` now says the live set holds about 14 months of hourly carbon intensity, 2025-08-09T16:00 to 2026-10-10T23:00 UTC as read on 2026-10-14 through the anon key (catalogue row and `series`), eight grids; the table of questions no longer says "last ~30 days". `site/lib/chat/spec.json` regenerated (`ask.py --export-spec`, no model call); `check_spec.py` exit 0.

## What to review

- `https://erw-flame.vercel.app/internal/open` first, then (after the landing):
- `https://erw-flame.vercel.app/grid` (Now's sentence: the lag clause)
- `https://erw-flame.vercel.app/grid?grid=ercot&view=network` (the line under the chart)
- `https://erw-flame.vercel.app/grid?grid=ercot&view=network&shape=gravity` and `https://erw-flame.vercel.app/grid?grid=caiso&view=network&node=CISO&shape=gravity`
- `https://erw-flame.vercel.app/grid/erw_2026_grid_replication.csv` (and `.do`, `.py`)
- Pictures: `docs/brand/review-266/` (1280 and 390, with and without a grid selected, and a README).

## Checks, with exit codes

All on the local build of the branch, port 3266, in the internal view; each gate run as `cmd > file 2>&1; echo "exit=$?"`.

| Check | Exit | Result |
|---|---|---|
| `npx tsc --noEmit` (cycles 1, 2 and 3) | 0 | |
| `npm run build` (cycles 1, 2 and 3) | 0 | no "statement timeout" in the log |
| `check-values`, `CHECK_VALUES_PAGES=/grid`, twice (cycle 2) | 0, 0 | 1,171 of 1,171 values match, both runs; `net|lag|2026-10-12T03:00:00Z|...` among them |
| `check-grid-replication.mjs` (cycle 2, snapshot of 09:05:21 UTC) | 0 | 60 values compared, 0 different (the lag 54 hours in Now for seven grids and under the chart, the counts, each grid's ties and net imports, and the gravity shape's 36 figures). Cycle 1: 59 of 60, the one a count the check's regex missed (React's comment markers), fixed in the check, not the page |
| `check-routes.mjs` (cycle 2) | 1 | pass 1: 203 of 204; the one is `/shoulder`, a page not touched here: 1 "no data" block where production has 0 (a table read, not this branch). Pass 2: 0 failed. Cycle 1: exit 0, 204 of 204 |
| `check-network-v3.mjs` (cycles 1 and 2) | 0 | 33 checks pass |
| `check-network-map.mjs` (cycle 2) | 0 | 31 checks pass. Cycle 1: 30 of 31: its pin of a two-button toggle; moved to three buttons with a note "session 266" |
| Screenshots (`runs/session266/shot.mjs`, cycle 2) | 0 | four pictures, 1280 and 390, page 390 px wide at 390 (no sideways scroll), hover card names the grid, the replay says the shape is live-week only. Labels small on the phone (about 9 px): fixed after, see "To finish" |
| `python warehouse/chat/check_spec.py` | 0 | the spec matches the briefing |
| `tests/test_session266.py` (19 tests), `test_session262`, `test_session180` | 0 | |
| The modules that pin a changed file, three at a time: 109, 124, 168_network, 193, 237, 241c, 54, 93, 114_part2, 120_page, 122, 123, 148, 180b, 55, 207, 65, 247, 78, 249, 260, 245, 250 | 0 each | |
| No em dash in any file written (`tests/test_session266.py` `test_no_em_dash`) | 0 | |

- **The battery page:** not captured. No shared component, no `tokens.css` rule and no `batterystack.ts` was touched (the new files are the Grid tool's own; `Network.tsx`, `NowView.tsx`, `NetworkView.tsx` draw only the Grid tool).
- **Pins moved:** `site/scripts/check-network-map.mjs` (the toggle: "Map,Network" to "Map,Network,Gravity", session 266). No python test pin moved: `tests/test_session180.py`'s two lines of `site/lib/networkMap.ts` are kept as they were (the gravity word is read before them).
- **Not run:** the do-file (no Stata on this machine); the whole suite on a clean copy (the orchestrator's, at the landing).

## Decisions made without you

- **The age of "now" is measured against the snapshot's hourly refresh, not the clock**, so `check-values` can recompute it (a clock age moves between the page's read and the checker's). Put as question 3 of the pack.
- **The gravity shape draws the seven ISO grids and the Lower 48 only**: the live set holds net generation for those eight; the other 63 balancing authorities are left out, said in the line under the frame. No stand-in size.
- **CAISO is sized by EIA-930's net generation**, as every grid (one source in one drawing), though EIA-930's California generation reads below CAISO's own since December 2025; CAISO therefore sits at the full pull (35.6 percent). Question 1 of the pack.
- **Outside the live week** (stories, replayed days) the gravity shape draws nothing and says so: hourly generation for those periods is not in the live set.
- **The pull is linear, full at 25 percent of generation** (`S_FULL`); bearings follow the map and carry no data. Question 2 of the pack.
- **The replication files live in `site/public/grid/`** as the brief named; static files with an extension pass the release gate (`site/proxy.ts` matcher), as `/battery/...` and `/datacenter/...` do.
- **The CSV is committed from the read of 2026-10-14 09:00 UTC** (hour 2026-10-12 03:00 UTC, snapshot built 08:05:18Z); the pack's part 8 is that file's figures. The page moves every hour: the check rewrites a fresh file and compares it with the page of the same snapshot.
- **Edge cases with no natural instance**: no ISO grid lacked a tie in any of the 168 hours of the live week, and no hour held zero generation; both were run on typed cases in `tests/test_session266.py` (Node runs `gravityLayout()`), and the page's handling is read from its code. Said so in the pack's part 5.

## For Samuel's ruling

- The six questions of the pack's part 9 (CAISO's circle; the pull's scale; how old "now" is; the grid at `/grid`; EIA's annual figures; the other 63 balancing authorities).
- **Not held, for a cross-check:** EIA's annual net generation by balancing authority (Electric Power Annual) to check the hourly sums against; an operator's own tie flows. No request was made to EIA from this machine.
- The gravity labels are 26 units of a 640 frame (about 11 px on a phone); a design critique was not run.

## To finish

- The pictures of the label fix (commit `1b923c3b`: the gravity SVG is a group, labels 26 units): run `node runs/session266/shot.mjs http://localhost:<port> docs/brand/review-266` on a build of the branch and commit the four PNGs; tsc and build of that commit were not run: the landing held the mutex from 09:43 to past 10:33 UTC and the third cycle was stopped unrun. Its change is two attributes and a role in `site/app/network/NetworkGravity.tsx`; the orchestrator's build at the landing is its first.
- The do-file is unrun (no Stata here): Samuel's run is part 8 of the pack.

## The landing

filled by the orchestrator

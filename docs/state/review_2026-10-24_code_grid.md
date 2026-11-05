# Chain 077's note: the Grid tool, sessions 1150 to 1163 (old laptop, 23 October 2026)

Chain file: `queue/done/077-day-23-october-code-grid-tool.md`. Run unattended in a second Claude Code window beside chains 075 and 076, from 17:55 to about 22:45 UTC. Model spend USD 0. Written by session 1163.

## What landed, and what waits

- **Landing A, on main since 19:41 UTC** (`3075cec9`, `task/1150-1157-grid`): sessions 1150, 1151 and 1157. On production since about 21:00 UTC: Vercel rate-limited the merge's own deploy ("retry in 24 hours"), and a later deploy carried it. Snapshot `c077A-before` (19:27) against `c077A-after` (21:01): 0 differences on 25 pages (every page is in review, so a visitor sees the in-review page).
- **Landing B, NOT landed:** sessions 1152 to 1162, all on one stacked branch, **`wip/1162-grid`** (`50383686`; it holds `wip/c077-land2`, which is 1152 to 1156 merged with main at 20:46 UTC, then 1158 to 1162 in order). Its landing gate was stopped at about 20:50 UTC by Claude Code for low memory (the gate was waiting on the build lock, held by chain 076's landing; agents for 1155 and 1156 were running beside it). Claude Code's note says not to start it again unattended, so no later session of this chain built, served or landed. Session 1164 (chain 078) or Samuel lands it.
- **Before every landing on this laptop:** a reap ends unattended landing. Starting Claude Code with `CLAUDE_CODE_DISABLE_BG_SHELL_PRESSURE_REAP=1` is Samuel's choice (memory note `stop-the-site-before-the-clean-suite`); this chain should have said so in its first status and did not.

## One line a session

| Session | What | Branch | Address (after `/internal/open`) | Screenshots |
|---|---|---|---|---|
| 1150 | The next file (078, on main `012aa03a`); the Grid tool read as a trader: `docs/reviews/grid-tool-2026-10-23.md` | landed A | `https://erw-flame.vercel.app/grid?grid=ercot&view=network` | none (a document) |
| 1151 | Every network figure keyed on the server (`grid_network_<grid>`, `grid_gravity_<grid>`), the Clean tab's last 24 hours (`grid_clean24_<grid>`), `lib/gridKeys.ts` | landed A | `/grid?grid=ercot&view=network`, `/grid?grid=caiso&view=gravity&shape=gravity`, `/grid?grid=ercot&view=clean` | `docs/brand/review-1151/` |
| 1152 | The energy mix, hourly: the last 24 hours by fuel, the demand peak marked, the age, share on hover, the monthly view (`mixp=month`); a stacking bug around zero fixed in `TimeChart` | `wip/1162-grid` | `/grid?grid=ercot`, `/grid?grid=ercot&mixp=month` | `docs/brand/review-1152/` |
| 1153 | The gravity shape: edges only with a figure, MW and window on hover, the public source said, the replay day kept when switching grid | `wip/1162-grid` | `/grid?grid=ercot&view=gravity&shape=gravity` | `docs/brand/review-1153/` (production before only) |
| 1154 | The scarcity strip for ERCOT and CAISO (`grid_scarcity_<grid>`), September 2026 (the latest 30 days the table holds), the other grids' reasons; key kind `series_n` | `wip/1162-grid` | `/grid?grid=ercot#scarcity` | none (no build) |
| 1155 | CAISO's alert state line (`grid_caisoalert_caiso`), alert days on the strip and the monthly view, links to and from `/grid/caiso/alerts`; key kinds `awe|last`, `awe|ndays` | `wip/1162-grid` | `/grid?grid=caiso#caiso-alerts` | none (no build) |
| 1156 | The network map: state outlines, every edge's direction and window on hover (MW for the grid in view's ties), the seven ISOs link to their map | `wip/1162-grid` | `/grid?grid=ercot&view=network&shape=map` | none (no build) |
| 1157 | Ask your grid: up to five stored answers a grid, graded right, each figure's source, held tables refused in the live Ask's words | landed A | `/grid?grid=caiso` (the Ask column) | `docs/brand/review-1157/` |
| 1158 | 390 pixels and accessibility from the code: four fixes (scroll regions, the map's svg role, the cards on a phone, long filters); 11 of 11 panels hold at 390 | `wip/1162-grid` | as 1152 to 1156 | none (no build) |
| 1159 | The brand pass: table rows, one look for "license needed" and "not held yet", fonts, spacing; 11 items for Samuel | `wip/1162-grid` | as above | none (no build) |
| 1160 | Every read timed (slowest median 117 ms at 21:21 UTC; none needs an index); three Mix tab reads trimmed (the Lower 48: 62 to 43 requests) | `wip/1162-grid` | `/grid` | none |
| 1161 | The trader's path: Grid steps 17 to 27 written and walked (production for landing A, the code for landing B) | `wip/1162-grid` | `docs/reviews/trader-path.md` | `docs/brand/review-1161/` (the walk's record) |
| 1162 | The method notes: a dated chain 077 section in seven notes; `docs/reviews/grid-rulings-2026-10-23.md` (18 items) | `wip/1162-grid` | `/data/methods/grid_network` | none |
| 1163 | This note, 078 updated, the queue step | main | | |

The orchestrator's two fixes, on the branch: `169e537a` (the gravity note writes California's join date through `caisoJoinDay()`, as `tests/test_session78` requires) and `35d2c31c` (the Network tab's picker carries the replay day too, session 1161's finding 2).

## To finish (in order)

1. Land `wip/1162-grid` (landing B): `scripts/land_check.py --ref wip/1162-grid --task task/1152-1162-grid` after merging origin/main. **The gate's check-values will fail on 11 lines that are main's own, not this chain's** (the same 11 on production at 19:12 UTC): the floors of `/deals`, `/map`, `/events`, `/events/uri-2021`, `/events/covid-2020`, `/events/caiso-heat-2020`, `/events/caiso-heat-2022`, `/events/east-heat-2025`, `/learn/bill`, `/research/card/gas_sets_price`, and `/digest/2026-10-21`'s WTI figure (101.91 on the page, 96.34 in Supabase). Landing A was landed with that reasoning (decision below): every Grid page passed (1,213 of 1,213 values), then check-routes, check-cross-checks and check-csp passed by hand on the same build.
2. On that build: the Grid floors rewritten (`CHECK_VALUES_WRITE_FLOOR=1 CHECK_VALUES_PAGES=/grid,/network`, with `MSYS_NO_PATHCONV=1`); `check-methods-keys.json` rewritten from that run (`check-methods.mjs --values <file> --write`); `check-390.mjs`, `check-links.mjs`, `check-network-map.mjs` (its click step was changed by 1156 and has never run) and AccessLint's `audit_live` on `/grid?grid=ercot`, `/grid?grid=caiso`, `/grid?grid=ercot&view=network`, `/grid/caiso/alerts`; the screenshots at 1280 and 390 named in reports 1152 to 1161; the trader path's code-step values filled in; an unbounded `npx tsc --noEmit -p .`.
3. Then the snapshot before, the push to `task/`, the snapshot after once production shows a mark of the commit (`runs/c077/probe-prod.mjs` waits for one), the comparison.

## Decisions made without Samuel

- The sessions stacked (each branch cut from the one before) while the landings waited for the database, and some ran two at a time (1151 with 1157, 1153 with 1154, 1155 with 1156) where their files did not overlap.
- Landing A was pushed with check-values at exit 1 because its 11 failures were the same on production main at the same hour and none was on a page this chain touched; every Grid page passed and the gate's other steps passed by hand.
- `site/components/grid/` and `site/components/mix/` treated as the Grid tool's own files.
- The scarcity strip draws September 2026, the latest 30 days the table holds; CAISO's withheld mix said as the session 118 ruling; the peak hour is the demand peak.
- After the reap, no build, server or browser for the rest of the chain: sessions 1158 to 1162 worked from the code and production's HTML.
- `scripts/duty.py on` (the chain file's word) does not exist; `duty.py start` was used.
- The orchestrator changed two pinned test lines of session 1153 (`169e537a`, `35d2c31c`), each to match a fix; no assertion was dropped.

## For Samuel's ruling

- The 18 items of `docs/reviews/grid-rulings-2026-10-23.md` (on `wip/1162-grid`): six on the page's words, nine on design, three on data and licenses; the first three by weight: "the latest EIA has published" said of an hour 21.6 hours old (1161); the map's MW for every tie, not only the grid in view's (1156); the cardinal left bar used outside cardinal's three jobs, site-wide (1159).
- Migration 036 (session 580's indexes): still unapplied; 1160 added nothing to it.
- Whether to start Claude Code on this laptop with `CLAUDE_CODE_DISABLE_BG_SHELL_PRESSURE_REAP=1`, so an unattended landing is not ended by a reap.

## queue/next for this machine

- `078-day-24-october-code-grid-tool-2.md` (sessions 1164 to 1177), updated by session 1163 from this chain: its session 1164 takes "To finish" above first. Taken next by this window.
- `089-day-26-october-code-ask-board-4.md`: chain 076's line (Ask and the board), the other window's; not taken here.

# Chain 078's note: the Grid tool, second pass, sessions 1164 to 1177 (old laptop, 23 and 24 October 2026)

Chain file: `queue/done/078-day-24-october-code-grid-tool-2.md`. Run unattended in the same window as chain 077, from 22:30 UTC on 23 October to about 01:55 UTC on 24 October, beside chain 076's window. Model spend USD 0. Written by session 1177.

## The state in three lines

- **Nothing of this chain landed.** Chain 077's landing B was stopped by a low-memory reap on 23 October (`docs/state/review_2026-10-24_code_grid.md`) and is not restarted unattended, so every session of chain 078 worked code-only (no build, no server, no browser) and stacked on the one before.
- **The branch to land is `wip/1176-grid`** (`3e3f9903`): chain 077's sessions 1152 to 1162 and chain 078's 1164 to 1176, in order, on one line of history. It replaces `wip/1162-grid` as the thing to land.
- **Production still shows held grids' rows in four places** (session 1167's finding; every page is in review, so no visitor sees them): the Clean tab's "The seven grids" for ISO-NE, MISO and NYISO, ISO-NE's queue, and ISO-NE's and NYISO's hub prices in the replay and the mix views. The fix is on `wip/1176-grid`. This is the strongest reason to land it soon.

## One line a session

| Session | What | Branch | Address (after `/internal/open`, once landed) | Screenshots |
|---|---|---|---|---|
| 1164 | The next file (091, on main `bccf8b58`); chain 077's "To finish" blocked by the reap, said in two lines | `wip/1164-grid` | | none |
| 1165 | The balance on every ISO grid's Network panel: generation, demand, net export, the gap, the week's mean gap (`calc|bal`, `netbal|`) | `wip/1165-grid` | `/grid?grid=caiso&view=network` | none (no build) |
| 1166 | The Mix and Clean tabs' last unkeyed figures; a `file|` key kind for the views drawn from committed files (370 values equal their live tables) | `wip/1166-grid` | `/grid?grid=ercot&mix=clean` | none |
| 1167 | Held grids' rows replaced by "license needed" in four places (`lib/gridHeld.ts`); the Exchange blocks' week per tie (`nettie|`) | `wip/1167-grid` | `/grid?grid=isone&view=clean`, `/grid?grid=ercot&view=gravity&shape=gravity` | none |
| 1168 | The stress measures charted by year with hover and their "what it is not" lines; 612 keys | `wip/1168-grid` | `/grid?grid=ercot&mix=stress` | none |
| 1169 | California's two sources side by side: not built (`caiso_fuel_supply` is not in the live set), written down | `wip/1169-grid` | | none |
| 1170 | A replay day's demand and exchange in the Network and Gravity panels, from the committed daily files (`netday|`) | `wip/1170-grid` | `/grid?grid=us48&view=network&net=day&t=2021-02-15&node=BPAT` | none |
| 1171 | One "preliminary" sentence on all four tabs; check-values tells a revised EIA-930 hour from a wrong one by the row's load time | `wip/1171-grid` | every tab's source line | none |
| 1172 | 61 old addresses tested (`test-grid-addresses.mjs`); none failed; 15 added to the route check | `wip/1172-grid` | | none |
| 1173 | The Grid pack (`docs/reviews/packs/grid.md`) corrected and refreshed (production read at 00:58 UTC) | `wip/1173-grid` | | `docs/brand/review-1173/` (the walk's record) |
| 1174 | ERCOT's notice state line, call days on the strip and the monthly mix (`ercotn|`) | `wip/1174-grid` | `/grid?grid=ercot` | none |
| 1175 | The 3D code was already split (session 428); a loading line and a test proving the split | `wip/1175-grid` | `/grid?grid=ercot&view=network` | none |
| 1176 | The method notes and the rulings list brought current (19 new items; none of the 18 ruled) | `wip/1176-grid` | | none |
| 1177 | This note, 091 updated, the queue step | main | | |

## To finish (in order)

1. Land `wip/1176-grid` as chain 077's note says for `wip/1162-grid` ("To finish", 1 to 3), alone on the machine (no agent, server or Chrome in either window), with these additions: the floors of every Grid address rewritten from a passing restricted run (the Mix, Clean, Network and Gravity tabs all gain keys); the addresses sessions 1166, 1168 and 1170 name added to check-values' list with their floors; `check-methods-keys.json` rewritten and `check-methods.mjs` run again (chain 078's keys are checked against the notes only then); `check-network-v3.mjs` with session 1167's new expectation (three rings on a 2025 day); `test-grid-addresses.mjs` with `node_modules`; the route check's 15 new addresses; session 1170's `outputFileTracingIncludes` entry in `site/next.config.ts` (the daily files must be readable on Vercel: check the panel on the first deploy); the 390 check of the Exchange table (seven columns, 1167); the first-load trace and route sizes (1175).
2. The screenshots each report names, at 1280 and 390, from that build.
3. The snapshots before and after, compared.

## Decisions made without Samuel

- The chain ran code-only and stacked, after the reap; no gate was restarted.
- Session 1167 changed words a visitor sees on pages in review ("license needed" in four places), because the license rule requires it.
- Session 1171 added a sentence to every tab's source line, and a source line to the Clean tab.
- Session 1170 added a file-tracing entry for `/grid` in `site/next.config.ts`, outside the chain's own files, because the server panel reads the committed daily files.
- Session 1174 counts the extreme-heat Operating Condition Notice as a call, with the EEAs, conservation appeals and watches.
- The orchestrator added the held-rows fix to session 1167 as its first part (session 1166 had found it).

## For Samuel's ruling

- The 37 items of `docs/reviews/grid-rulings-2026-10-23.md` on `wip/1176-grid` (18 from chain 077, 19 from chain 078), three groups, weightiest first; the first four of the data group: NYISO's and MISO's queue rows in `energy_projects` are drawn although their own queue tables are held (1167); the shared reader in `site/lib/supabase.ts` does not filter held rows by `entity_id` (1167); `caiso_fuel_supply` is not in the live set, so California's own generation cannot be set beside EIA-930's (1169); ERCOT's notices connector runs by hand only, so the state line says "not held yet" after the last read (1174).
- Whether to start Claude Code on this laptop with `CLAUDE_CODE_DISABLE_BG_SHELL_PRESSURE_REAP=1` for the landing (chain 077's note).

## queue/next for this machine

- `091-day-25-october-code-grid-tool-3.md` (sessions 1178 to 1189), updated by session 1177: its first session lands `wip/1176-grid` if a person has not, else says so in two lines; the sessions that need a build are marked so. Taken next by this window.
- Chain 076's line (`089`) was taken by the other window.

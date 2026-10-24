# Chain 091's note: the Grid tool, third pass, sessions 1178 to 1189 (old laptop, 24 October 2026)

Chain file: `queue/done/091-day-25-october-code-grid-tool-3.md`. Run unattended in the window that ran chains 077 and 078, from 01:55 to about 05:45 UTC on 24 October. Model spend USD 0. Written by session 1189.

## The state in three lines

- **Nothing of chains 077 (landing B), 078 or 091 is on main.** This window ran the gate that a low-memory reap stopped on 23 October, so by the rule chain 091 carries it ran no gate after; every session worked code-only and stacked on the one before.
- **The branch to land is `wip/1188-grid`** (`9b0ff406`): sessions 1152 to 1188 and main as of `c446038c` (merged at 05:18 UTC on 24 October by session 1187). It replaces `wip/1176-grid`.
- **Production still shows held grids' rows in four places** (session 1167; every page is in review). The fix is on `wip/1188-grid`.

## One line a session

| Session | What | Branch |
|---|---|---|
| 1178 | The next file (100, on main `dc70ee12`); the landing blocked in this window | `wip/1178-grid` |
| 1179 | One read of a grid's generation a page, shared through React `cache()` (4 reads to 1); 2,232 figures the same | `wip/1179-grid` |
| 1180 | A test that failed on Windows' CRLF fixed; battery units read narrowed; the Gravity tab's snapshot read once; `same-figures.mjs` | `wip/1180-grid` |
| 1181 | Eight places that stated a wrong fact on a failed read now say "could not be read"; 754 renders with failures injected | `wip/1181-grid` |
| 1182 | Every new panel's table as a CSV with its provenance (24 files, in the page as `data:` links) | `wip/1182-grid` |
| 1183 | 17 shareable panel anchors (`lib/gridAnchors.ts`), the route check asks each; 1182's files add 1.3 to 6.7 percent to a page | `wip/1183-grid` |
| 1184 | Each panel links its method section, fragments computed by the site's renderer | `wip/1184-grid` |
| 1185 | The Lower 48's monthly mix, the sum of 48 states and DC from EIA-923 (`states_sum|`); the scarcity strip says why it has no Lower 48 | `wip/1185-grid` |
| 1186 | check-values sends about a quarter of the requests on the Grid pages, every verdict the same (68 paired runs) | `wip/1186-grid` |
| 1187 | The stored answers refreshed from chains 075 and 076's four new runs (main merged in) | `wip/1187-grid` |
| 1188 | The method notes and the rulings list (8 new items; none of the 37 ruled); a broken placeholder on the methods page fixed | `wip/1188-grid` |
| 1189 | This note, 100 updated, the queue step | main |

No screenshots in this chain: no build, server or browser.

## To finish (in order)

1. Land `wip/1188-grid` as chain 078's note says for `wip/1176-grid` ("To finish"), alone on the machine (no agent, server or Chrome in either window), with chain 091's additions: **session 1186 changed `site/scripts/check-values.mjs` for every page**, so the landing's full check-values run is compared verdict by verdict with the last full run (`runs/land_check/663b3a36d307851154e967c255f32791c14db058/check_values.out`, 23 October: 8,114 of 8,115 values, 11 failures that were main's own); the floors of every Grid address rewritten, including `/grid?grid=us48&mixp=month` (1185); `check-table-downloads.mjs` and `check-download.mjs --grid` (1182); one CSV link clicked in a browser; the route check's "17 of 17 drawn" (1183); `check-links.mjs` for the method fragments (1184); `test-network-split.mjs` now passes on Windows (1180).
2. The screenshots the reports of 1152 to 1188 name, the trader path's values and the Grid pack's rows marked for landing B's build.
3. The snapshots before and after, compared.

## Decisions made without Samuel

- No gate in this window after the reap; the chain stacked and worked code-only.
- Session 1186's change to the shared checker was made with its proof on the Grid pages only; the other pages' proof is the landing's full run (above).
- Session 1187 merged main into the stack (no conflict) so the new evaluation runs were in the branch.
- 1182's files stay inside the page (no route): no page grew past 15 percent or 100 KB.
- The successor numbered 1400 to 1409 (queue 100): the other window held 1190 to 1203 and 1300 to 1319.

## For Samuel's ruling

- The 45 items of `docs/reviews/grid-rulings-2026-10-23.md` on `wip/1188-grid` (18 from chain 077, 19 from 078, 8 from 091), none ruled yet.
- Landing: the stacked branch now holds 37 sessions. Whether to land it by hand, or to start a session on this laptop with `CLAUDE_CODE_DISABLE_BG_SHELL_PRESSURE_REAP=1` and nothing else running, is yours.

## queue/next for this machine

- `100-day-26-october-code-grid-tool-4.md` (sessions 1400 to 1409), updated by session 1189: its first session lands `wip/1188-grid` if a gate may run alone, else says so; 1401 and 1407 need a build and say so if none may run. Taken next by this window.

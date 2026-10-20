# Session 370 report: the three checks that failed on production, older than the chains

20 October 2026, from about 18:55 UTC, unattended, on samueloldlaptop (the code machine), a session of the chain of 20 October, day (`queue/done/012-day-20-october-code.md`, "Session 370"). Branch `wip/370-check-faults` in the worktree `../erw-370`, from `origin/main` at `ae894d37`. Model spend USD 0. Pulls: none. No warehouse table, no Supabase or Redivis write (reads of the live set with the anon key only). No em dash in anything written.

**Not finished at the hand-back: the local build and the checks on it.** The build mutex was session 368's, then the orchestrator's (`s367land`) from 19:36 UTC; my background wait for it was stopped by the harness for low memory at about 19:44 UTC, and the harness says not to start it again unattended. Every change is committed; the three checks were run against production instead (two of the three changes are to check scripts, which production can answer). "To finish" below is the one command the orchestrator runs under the mutex.

## Read these first

1. **check-battery-scenarios' CAISO 2-hour case: the page was right, the check was wrong.** The case asserted "steps held" outright. The page offers the steps of efficiency and cycles only while `site/data/battery_scenario_steps.json` still describes the live months (`lib/battery/finance.ts`, `stepState`), and it does not: the file (built 14 October) counts 29 days in each CAISO November (2023-11, 2024-11, 2025-11); session 322 filled CAISO's three fall-back days and the daily run rebuilt `battery_stack_monthly` with 30. So the page shows `data-steps="revised"` and says "only the model's own step is offered ... a month of the table has changed since", which is true. All six CAISO cases are behind the same way; the six ERCOT cases match (`runs/chain_oct20d/s370/steps_diff.out`, a read-only comparison). What the check assumed: that the file of steps is always current. It now reads the page's own `months.csv` (at 5,000 MW, so each month is exact to USD 0.0001 per MW), asks the library which state the page must be in, holds the page to it, and prints a note naming the months that differ. The page's figure did not move (USD 61.29 per kW, October 2025 to September 2026, before and after; no method note change: the page was right). On production: exit 0, all passed, with the note.
2. **check-datacenter: no true fault in the page.** Every one of the 22 failures (and the browser part, which crashed on the ECharts chart) described the page before sessions 190, 213, 228, 236, 265 and 317. Session 213 moved the grid sections into the download `/cost-of-power/tables.csv`, so the moved figures are now read there; the blocks that left the page (the standalone contract panel, the "Rules in motion" block with its hovers, fold and keyboard) are retired. On production: **45 of 45, exit 0** (it was 23 of 45 and a crash). The table below gives each assertion.
3. **The card chart's right legend.** It is `CategoryChart`'s names of its lines (`components/svgchart.tsx`), drawn at the right of the plot in a gutter capped at 150 px: on `/research/card/*` the names are longer, and they ran past the chart's box and were cut by the SVG's edge, **at 390 and at 1280 alike** (measured: `runs/chain_oct20d/s370/cards_prod_390.out`, `cards_prod_1280.out`; the 1280 crop shows "ERCOT battery fleet (MW, ope"). The fix, in the shared component through a new pure helper `site/lib/chartwrap.ts`: a name wider than its room is drawn in lines that fit (words kept whole, a word wider than the room cut), each name keeps the room of its lines below it, and the last stays inside the drawing. A name that fits is the same text node as before, so a chart whose names fit is drawn exactly as before at every width; the plot's geometry does not move. Decision 2 says why 1280 changes where it too was cut.

## check-datacenter, assertion by assertion

Verdicts: "follows" = updated to the page as it stands, the change intended by the session named; "retired" = described a block that left the page; "kept" = unchanged and passing. No assertion marked a true fault.

| Assertion (session 138's words, shortened) | Verdict | What was done |
|---|---|---|
| the four questions are four sections | follows (213, 228) | "What will it pay?", "Will the power be there?", "How clean?", "How soon?" |
| names its Method note, no method prose on its face | follows (190, 213) | the note is `datacenter_pays_algorithm`; the one line "What else the model cannot see" links `#cannot-see`; no other method words |
| large load in line "not published anywhere yet"; waits "not measured here" (ERCOT) | follows (213) | read from `tables.csv` (`how_soon/large_load_in_line`, `waits/state`) |
| New York's load in line reads "NYISO's terms do not allow it", reason on hover | follows (213; ruling of session 149 kept) | `tables.csv` row: the words, then the reason; New York's waits measured there |
| the 40 delivery charges are rows of their own; Oncor's transmission factor 8.58 | follows (236, 265) | the four utilities are the columns of the table by component; each figure's hover names the tariff lines it sums as printed; Oncor's transmission equals `deliveryOf` (8.58) |
| every charge carries its line, page, date and address | follows (236: none is on the page) | the download's table `delivery`: each of the 40 lines with its line read, page, date and address |
| the Commission's rate: USD 68.547301 per kW a year on the face | follows (236) | the face says USD 7.83 per MWh (approved) and 2026 "filed, not approved"; the per-kW rate as printed and its line are the hover |
| ERCOT tight in 140 hours of 2025; off in 4 | follows (213) | `tables.csv` `power_there/hours_tight_2025`: 140 and 4, the library's figures |
| demand by region: eight weather zones with growth | follows (213) | `tables.csv`: eight `demand_by_region_*` rows with `change_pct` |
| this load's own hours met ? percent carbon-free (NaN) | follows (213) | `tables.csv` `how_clean/this_loads_own_hours_2024` equals `cleanShare` (43.82, flat 43.61) |
| ISO-NE "licensed source needed" | follows (213) | the download's two rows state no figure and say it is held internally; the site's files hold none |
| SPP "not held yet" | follows (213) | the download's row states no figure: not held for SPP |
| ERCOT, CAISO, NYISO, ISO-NE, SPP, MISO, PJM: the block is in "How soon" (7) | follows (228, 213) | "How soon?" states the file's count with the newest (or MISO's pause); the download's table `rules` holds exactly the file's rows and federal rows, per grid |
| PJM shows rows: 0 of 41 | follows (228) | folded into PJM's count above: 41 counted |
| an address naming PJM shows what the default shows | follows (265, 228) | the same, outside the one line "Grid: "pjm" is not held here, so ERCOT is shown" and the rules count, which follows the address |
| an address naming MISO shows what the default shows | follows (265, 228) | the same |
| (browser) the chart answers the mouse (ECharts, crashed) | follows (317) | the SVG chart's hover card at 2021: flat, this load, foreseen, hours off |
| (browser) the contract's result, no request, nothing stored, terms survive a grid change (4) | retired (213) | the contract is two scenario assumptions; `check-datacenter-scenarios` holds its promise |
| (browser) rows' links, keyboard focus, the fold to a click and to Enter, the seven choices (4) | retired (213) | the block is undrawn (`RulesInMotion.tsx` on disk) |
| every docket hover, eight rows before a fold, no note sentence on the block's face (3, passing on an absent block) | retired (213) | they passed only because the block was not there |
| no municipal word in the block | follows (228) | the count's line, for the seven addresses |
| the other 18 (opens, tabs, MISO and PJM not selectable, five grids, the three loads' numbers and the forecast rule, the region with no real-time price, MISO opens ERCOT, no NYISO request, CAISO's delivery, transmission and distribution apart, the hub beside, the foreseen row, `?view=grids`, the visitor; in the browser the regions' groups, another grid, no script error) | kept | |

## What to review

In the internal view (https://erw-flame.vercel.app/internal/open first), once landed:

1. https://erw-flame.vercel.app/research/card/batteries_lunch at a phone's width and at 1280: the two names at the right ("ERCOT battery fleet (MW, operating)", "Worst-interval multiple (P99.9 / median)") on two lines each, inside the box.
2. https://erw-flame.vercel.app/research/card/impact_study and https://erw-flame.vercel.app/research/card/peak_hour_grids (five small charts).
3. `docs/brand/review-370/` (before: production; after: the local build, once "To finish" has run).

## Checks

| Check | Exit | Result |
|---|---|---|
| `scripts/precheck.py --what "session 370"` | 0 | |
| `check-battery-scenarios` on production, before the change | 1 | the one failure; probe: steps `revised`, capex 610, revenue equal to the headline |
| `check-battery-scenarios` on production, after | 0 | all passed; the note names the three Novembers |
| `check-datacenter` on production, before | 1 | 22 of 45 failed, then a crash on the chart |
| `check-datacenter` on production, after | 0 | 45 of 45 |
| `tests.test_session370`, `tests.test_session154_page` | 0 | 21 tests OK (154's pin moved: decision 4) |
| the 17 test modules that read the changed files (140, 144_page, 154_page, 179, 195, 204, 236, 241a/b/c, 296, 297, 317, 318, 328, 331, 351), before the pin moved | 1 | one failure, 154's pin (fixed, above); the rest OK |
| Impeccable `detect --json` on `svgchart.tsx`, `chartwrap.ts` | 0 | `[]` |
| Text past the chart's box on production (`charts370.mjs`) | 0 | 390: 6 of 11 cards (5 the names at the right; `queue_divorce`'s is a bar's name at the left, not this fix's); 1280: the same 5 (`cards_prod_*.out`); other pages: `/internal/findings` (all 49 cards), the forecast view at 1280 |
| `npm run build`, full `check-values`, `check-datacenter`, `check-datacenter-scenarios`, `check-datacenter-face`, `check-battery-face`, `check-battery-scenarios`, `check-findings-grids` on the local build | not run | the mutex: "To finish". `check-findings-grids` is expected to keep failing: it waits for small multiples |

`check-values`: the change moves no number (it draws names, not values), so the full run on the local build should give each page the count of `runs/chain_oct19/s356land/values1.out` (6,618 of 6,624 there), with the pages sessions 357 to 369 added since; 369's 6,639 includes its own changes, which this branch lacks.

## Decisions made without you

1. Fault 1: the check was changed, not the page or the file of steps. Rebuilding the file is the data machine's (`dm_battery_scenario_steps`, on tables that hold session 322's fall-back days); this machine's copy of the tables is of 4 October.
2. Fault 3: the 1280 drawing changes where its names were also cut at 1280 (the card charts, `/internal/findings`, the Grid tool's forecast view at 1280: "Mean error (forecast less actual)"). A chart whose names fit is unchanged at every width, and no plot moves. Keeping 1280 as it was would have kept names cut by the edge.
3. The wrap reads a character as 0.52 of the size (measured 0.45 to 0.47 on the face), not the gutter's 0.56, so a name that fits today is not wrapped.
4. `tests/test_session154_page.py` pinned the retired block's words in the check (`data-rules-paused`, `Input.dispatchKeyEvent`, the old note's name); its pin now names the count, the pause and the download, with a comment.
5. The header comment of `check-datacenter.mjs` was rewritten for the page as it stands; the rows retired are listed in it and above.

## For Samuel's ruling

None new. For the data machine (not a ruling): `site/data/battery_scenario_steps.json` is behind the live `battery_stack_monthly` in CAISO's three Novembers since session 322; until it is rebuilt, CAISO's steps of efficiency and cycles are not offered (the page says so). `dm_battery_scenario_steps` has reported ok daily with `--keep-same`, so its own copy of the tables likely lacks the filled days.

## Files

- `site/scripts/check-battery-scenarios.mjs`: `stepsExpected`, the CAISO case
- `site/scripts/check-datacenter.mjs`: rewritten for the page as it stands
- `site/lib/chartwrap.ts` (new), `site/components/svgchart.tsx`: the names at the right
- `tests/test_session370.py` (new), `tests/test_session154_page.py` (one pin)
- `docs/brand/review-370/` (README, `before/`)
- Notes and probes: `runs/chain_oct20d/s370/` (`steps_diff.*`, `probe_battery_prod.out`, `check-*.prod.*.out`, `dc_prod/`, `charts370.mjs`, `cards_prod_*.out`, `pages_prod_*.out`, `cycle.sh`)

## To finish

Under the build mutex (owner line `370 cycle <UTC time>`), from any shell:

    bash C:/Users/lossa/Documents/erw/runs/chain_oct20d/s370/cycle.sh

It runs `npm ci` (if needed) and the build in `../erw-370/site` (again on a cached statement timeout), starts `next start -p 3370`, then the full `check-values`, the six checks and the after shots and measurements, each exit code in `runs/chain_oct20d/s370/result.txt`. Then stop the server by its port (`Get-NetTCPConnection -LocalPort 3370 -State Listen`, `Stop-Process -Id <OwningProcess> -Force`, in a call of its own), give the mutex back, and commit `docs/brand/review-370/after/` on the branch. If `check-values` fails on a latest price, run it once more (a local build's first read can be stale).

## Landing

(the orchestrator's)

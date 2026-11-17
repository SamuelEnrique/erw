# Session 7536 report: Should your family get an EV? (`/play/ev`) at the done line

Chain 304, second run (the owner's instruction of 16 November 2026), samueloldlaptop, code role. Branch `wip/7536-play-ev`, worktree `C:\Users\lossa\Documents\erw-7536`, from origin/main `206bf661a`. Brief: `runs/c304b_brief.md`. Model spend USD 0 (`ERW_SPEND_CAP_USD=0`, no model call).

## What was done

- **The method note** `docs/methods/ev_game.md` completed, nothing removed: which of its sections holds where they disagree (the five screens and "no check key" lines are superseded), every view and figure with its rule and how it is shown, the chart's axes, the 11 choices, what the game does not hold, the replication and the cross-check.
- **The replication** `replication/ev_game/replicate.py` (from the note and the two EIA tables, not the page's code): the game drawn to HTML with the site's own code (`site/scripts/ev-game-figures.mjs`) as it opens, for all 51 states at the defaults, and for 11 players' cases (`cases.json`). **5,141 of 5,141** figures inside half the page's last shown digit over 63 cases, every outcome included ("at once", "never", "Saved"/"Extra a year", the crossing or none, the waiting line). Prices of `site/data/ev_prices.json` against the tables: **102 of 104 equal, 2 named** (EIA revised New York's and Pennsylvania's July 2026 residential prices after the file was built). Also named: the file is older than the tables. `replicate.do`: the five headline figures, expected values at its top (Stata not on this machine; not run).
- **The cross-check** (in the note): EIA's weekly US gasoline ($4.354 on October 5, equal; $3.995 newest), EIA EPM Table 5.6.A August 2026 for 13 places (the table equals EIA's to the cent in all 13), AFDC's Alternative Fuel Price Report of July 2026 ($3.84 against the table's 3.816), PG&E's E-TOU-C off-peak rates (36.757 and 39.940 cents against California's 33.61), the IRS's credit page (reviewed 13-Jul-2026: no credit after Sept. 30, 2025; up to $7,500). Robots files read first (eia.gov, afdc.energy.gov, pge.com, irs.gov).
- **The decisions block** `site/app/play/ev/Decisions.tsx`, mounted by `page.tsx`: 11 choices, each with its default and source on hover; each one the player can change names the slider that changes it.
- **The faults** `docs/reviews/ev-game-faults-2026-11-16.md`: 11 rows, 3 site fixed, 2 data machine (one data request), 6 rulings.
- **The site changes** (`site/app/play/ev/EvGame.tsx`): an optional `start` prop (what the game opens with; the page passes none) so a player's case can be drawn; the keyed payback printed to one decimal (six states read "3 years" or "4 years"); a keyed net present value below zero keeps its key (Hawaii); the line in place of the results says which price is missing when a state has none.
- **The license hold:** the game's keys (`ev|...`) name no table, so `heldBy` returns nothing for them and no figure shows "license needed" (held by the render test). Nothing of the hold logic was touched; `site/components/Num.tsx` was not touched.

## Tests run on this machine

- `tests/test_session7536_ev_game.py`: 9 passed. `site/scripts/test-ev-game-render.mjs`: 21 of 21. `ev-game-figures.mjs --check`: 5,141 figures as committed.
- Older files that name the page or its library, or sweep the decisions blocks, the notes and the usage promise, each in its own process: `test_session203`, `239`, `288`, `294` (its credit line read the old `useState(false)`; updated to the new opening line and held that the page passes no `start`), `5171`, `1743`, `237`, `298`, `299`, `462`, `463`, `465`, `142`, `147`, `158`, `160`, `177`, `409`, `5102`, `5154`, `5155`: all OK. `site/scripts/test-ev.mjs`: pass. `check-methods.mjs`: 544 of 544. `tsc --noEmit`: 15 messages, none in `app/play/ev` (all are generated types and content files a build writes).
- Not built (memory). `check-values` and `check-routes` not run.

## What to review

- `https://erw-flame.vercel.app/play/ev` (in review: with the review cookie).
  1. As it opens: Payback "3.2 years", Net present value "$5,131"; the fold "Decisions in this game" at the foot, closed. Open it: 11 lines; point at each small square: "Default:" and "Source:".
  2. "Your state": Kentucky. Payback reads "3.0 years" (was "3 years").
  3. "Your state": Hawaii. Payback "8.2 years", Net present value "-$1,056".
  4. Point along the chart (United States): at year 8, gasoline car $47,951 and EV $40,411; the crossing marked "they cross at 3.2 years".

## Needs the key

- Nothing.

## Decisions made without you

- The game takes an optional `start` prop so the replication can draw a state or a player's moves with the site's own code; the page passes none, and a test holds that it does not.
- The replication names, not fails, the two July prices EIA revised (New York, Pennsylvania) and the file's age: both are the data machine's (data request row 99).
- fueleconomy.gov refused the connection to its robots file twice, so no request was made to it; the mpg, the kWh a mile and the 15,000 miles stand as read on 15 October.

## For Samuel's ruling

- **The prices' file is rebuilt by hand.** Default taken: no schedule added; each rebuild is a data request. Ruling wanted: put `site/scripts/build-ev-prices.mjs` in the data machine's daily run (fault 6).
- **A payback longer than the years kept** (Hawaii at the defaults, 8.2 years against 8) reads like any other. Default taken: unchanged. Proposed: "after the years you keep it" under the figure in that case (fault 11).
- **The home price is the state's average**, not an EV or night rate (PG&E's off-peak is 3 to 6 cents dearer than California's average). Default taken: the average stays, the fold says so (fault 7).
- **The car prices are the 2025 models**, "to confirm". Default taken: unchanged (fault 8).
- **"Interest rate" on the page, "discount rate" in the note.** Default taken: the page keeps "Interest rate" (fault 10).

## Rows for the coordinator

### (a) Landing request

| 34 | `wip/7536-play-ev` | (the branch's head, given in the return) | `7536-play-ev` | 7536 | 2026-11-16 | `tests/test_session7536_ev_game.py` (9 passed) and `site/scripts/test-ev-game-render.mjs` (21 of 21, the game and the fold drawn to HTML without a build); `ev-game-figures.mjs --check` (5,141 figures as committed); 21 older test files that name the page, `lib/ev.ts`, the decisions blocks, the notes or the usage promise, each in its own process: all pass (`test_session294` updated for the credit's opening line); `test-ev.mjs` pass; `check-methods.mjs` 544 of 544; `replication/ev_game/replicate.py` on this machine's tables: 5,141 of 5,141 figures, prices 102 of 104 with 2 named, exit 0; `tsc`: no message in `app/play/ev`; not built here (memory); `check-values` and `check-routes` not run | requested |

## Row 34: what it holds (chain 304, session 7536, Should your family get an EV? at the done line)

- **From** origin/main `206bf661a`. Report: `archive/sessions/SESSION_7536_REPORT.md` on the branch.
- **What changes:**
  - `site/app/play/ev/EvGame.tsx`: an optional `start` prop, which the page does not pass; the keyed payback printed to one decimal; a keyed net present value below zero keeps its key; the line in place of the results names a missing price.
  - `site/app/play/ev/page.tsx`: one import and one mount of the new `Decisions.tsx` (11 choices, server-drawn words, no handler, no state, no request; its one link does not prefetch).
  - `tests/test_session294.py`: its credit assertion reads the new opening line.
  - New: `docs/methods/ev_game.md` (a section added), `replication/ev_game/` (replicate.py, replicate.do, cases.json, page_figures.json and .csv), `site/scripts/ev-game-figures.mjs`, `site/scripts/test-ev-game-render.mjs`, `tests/test_session7536_ev_game.py`, `docs/reviews/ev-game-faults-2026-11-16.md`.
- **What does not change:** `lib/ev.ts` and every figure's arithmetic, `site/data/ev_prices.json`, `check-values.mjs` and its `ev|` keys (the raw values are the same), `components/Num.tsx`, `site/lib/release.ts`, every table and builder.
- **Before landing:** a site build of the merged commit (none made here); `check-values` on `/play/ev` (the four `ev|US|` keys, unchanged values); `check-methods.mjs` with a base URL.
- **Snapshot differences to expect:** none on the 25 addresses (every page is in review; a visitor sees the in-review page). With the review cookie, on `/play/ev`: the new closed fold "Decisions in this game" under the game; the opening figures unchanged ("3.2 years", "$5,131"). **Tables:** none.
- **After the landing:** rows 126 to 130 of `docs/state/browser_reads_wanted.md`. Row 99 of `docs/state/data_requests_done_line.md` is the data machine's and does not hold this row; after it, `site/scripts/ev-game-figures.mjs` must be run again and `page_figures.*` committed (the replication refuses a figures file read from an older price file).

### (b) Browser reads

| 126 | 2026-11-16 | 7536 | `wip/7536-play-ev` (row 34) | `https://erw-flame.vercel.app/play/ev` | The fold "Decisions in this game" under the game, at 1280 and 390 px: open it, point at or tap each small square | Closed to start; 11 lines; each tip shows "Default:" and "Source:"; the tips stay inside the window at 390 px; no sideways scroll | wanted |
| 127 | 2026-11-16 | 7536 | `wip/7536-play-ev` (row 34) | `https://erw-flame.vercel.app/play/ev` | "Your state": Kentucky, then North Dakota, then New Jersey; move nothing | Payback "3.0 years", "3.0 years", "4.0 years" (not "3 years" or "4 years") | wanted |
| 128 | 2026-11-16 | 7536 | `wip/7536-play-ev` (row 34) | `https://erw-flame.vercel.app/play/ev` | "Your state": Hawaii; move nothing | Payback "8.2 years"; Net present value "-$1,056"; the chart marks no crossing | wanted |
| 129 | 2026-11-16 | 7536 | `wip/7536-play-ev` (row 34) | `https://erw-flame.vercel.app/play/ev` | As it opens (United States): point along the chart, then use the arrow keys on it | At year 8: gasoline car $47,951, EV $40,411; "they cross at 3.2 years" beside the marked crossing; the money axis $0 to $50k | wanted |
| 130 | 2026-11-16 | 7536 | `wip/7536-play-ev` (row 34) | `https://erw-flame.vercel.app/play/ev` | Move "Charging done at home" to 50 percent; type nothing, then 45 in "A public charger's price" | First "Type a public charger's price on the left to see the results."; then the results return (a year of electricity $1,472 at the US defaults) | wanted |

### (c) Data request

| 99 | 2026-11-16 | 7536 (chain 304, samueloldlaptop; branch `wip/7536-play-ev`) | `site/data/ev_prices.json` (`site/scripts/build-ev-prices.mjs` on `eia_retail_electricity_prices` and `eia_regional_retail_fuel_prices`) | Built 15 October 2026 and not since: electricity July 2026 (the table holds August, released by EIA October 23), gasoline the week of October 5 (the table holds November; EIA's newest is November 9, $3.995 for the US against the game's $4.354). It also holds EIA's first July figures for New York (299.0) and Pennsylvania (217.2) USD/MWh, revised since to 298.9 and 217.1. Run `node site/scripts/build-ev-prices.mjs warehouse/output` and commit the file; then `node --import ./scripts/tsx-register.mjs scripts/ev-game-figures.mjs` from `site/` and commit `replication/ev_game/page_figures.*`; `replicate.py` should print N of N with the prices equal. `/play/ev` reads it | `docs/reviews/ev-game-faults-2026-11-16.md`, rows 3 and 5 | requested |

### (d) Progress line

| 16 | `/play/ev` | `wip/7536-play-ev` | done `<head>` on `wip/7536-play-ev` (landing row 34). **The note:** `docs/methods/ev_game.md` completed, every earlier section kept. **The replication:** 5,141 of 5,141 figures over 63 cases (the game as it opens, the 51 states at the defaults, 11 players' cases), every outcome included; the prices against the two EIA tables 102 of 104, 2 named (EIA revised NY and PA July). **The cross-check:** EIA weekly gasoline (equal), EIA EPM Table 5.6.A August 2026 (13 places, equal), AFDC July 2026, PG&E E-TOU-C, the IRS credit page. **The decisions block:** 11 choices. **Faults:** 11 found, 3 fixed (six states printed a payback without its decimal; Hawaii's negative NPV lost its key; the waiting line for a state without a price), 2 data machine (the file built 15 October, data request row 99), 6 rulings. Browser reads rows 126 to 130. Not read: fueleconomy.gov (refused the connection), PG&E EV2-A (no PDF reader) | 7536 |

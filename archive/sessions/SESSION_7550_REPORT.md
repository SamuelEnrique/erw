# Session 7550 report: `/play/ev` read as the reader it is for (chain 304, part B form, samueloldlaptop, 16 November 2026)

- **Tool:** Should your family get an EV? (`/play/ev`), this machine's own (done line: session 7536, landing row 34). The read is on the tool's own branch `wip/7536-play-ev`, on top of the done line `95943ca8e`.
- **The read:** `docs/reviews/ev-game-read-2026-11-16.md`. The reader: a household choosing between the page's named pair (the 2025 Chevrolet Equinox FWD and Equinox EV FWD) in a named state, and a student checking the answer. Five cases: a commuter in Phoenix; a family in Minneapolis keeping the car 10 years, buying in November 2026; a driver in Fresno on PG&E (the state's average, E-TOU-C's off-peak rates, EV2-A); a student checking 3.2 years and $5,131; A and B, with the price board of the same day.
- **13 rows:** 4 site fixed, 2 data machine (one new request, 249; one resting on request 99), 3 browser (276 to 278), 4 rulings. No license or key row.
- **Fixed on the page (no figure shown changed):**
  - The gasoline tip of a state given its region's price spells out the Petroleum Administration for Defense District and names the states the game gives that price (Arizona: "Alaska, Arizona, Hawaii, Nevada and Oregon"), read from the price file.
  - Every "Electricity at home" tip says the average is every utility's homes together, every hour, fixed charges included, and that a utility's own rate can be higher or lower; California's links `/learn/bill` (no prefetch) for PG&E's, SCE's and SDG&E's own tariffs. This answers at this page's side the disagreement session 7547 recorded (its row 9).
  - The decisions fold's home price source called PG&E's E-TOU-C "a rate made for EV owners" that "can be lower", then gave two figures above the average. Now: a time-of-use rate for any home, both off-peak rates above California's 33.61; EV2-A not held.
  - The net present value's tip gives the yearly saving to the cent ($1,567.47 at the defaults), so a student who works from the table's rounded $1,567 ($5,128) sees why the game shows $5,131.
- **Tests:** new `site/scripts/test-ev-game-read.mjs` (22 of 22) and `tests/test_session7550_ev_game_read.py` (7 passed). Run again and passing: `test-ev-game-render.mjs` (21 of 21), `test-ev.mjs`, `ev-game-figures.mjs --check` (5,141 figures, rewritten), `replicate.py` (5,245 of 5,245, against the main copy's tables), `tests/test_session7536_ev_game.py`, `test_session294.py`, `test_session203.py`, `test_session239.py`, `test_session288.py`, `test_session5171.py`.
- **Files touched:** `site/app/play/ev/EvGame.tsx` (two tips), `site/app/play/ev/Decisions.tsx` (one line's source), `replication/ev_game/replicate.py` (the gasoline words checked from EIA's PADD definitions), `replication/ev_game/page_figures.json` and `.csv` (rewritten by the script), `docs/methods/ev_game.md` (one table row and a closing section), and the new read, test and report. All of this machine's own stack. Not touched: `lib/ev.ts`, `site/data/ev_prices.json`, `components/Num.tsx`, `site/lib/release.ts`, `check-values.mjs`, `/learn/bill`, `/board`, any table.
- **The hold:** the game reads two public EIA tables; no figure is blanked and the read saved no table row (its figures are the page's, from the committed price file). The read test checks both tables are public and not held.

## What to review

- `https://erw-flame.vercel.app/play/ev` (in review; with the review cookie):
  1. Choose Arizona; point at the "i" after "Gasoline, a gallon": "the West Coast without California (Petroleum Administration for Defense District, PADD 5 except California): EIA does not publish a weekly price for Arizona, so this is its region's, the price the game gives Alaska, Arizona, Hawaii, Nevada and Oregon."
  2. Choose California; point at the "i" after "Electricity at home": the new sentence on the average, then "What is on an electricity bill draws a bill on PG&E's, SCE's and SDG&E's own tariffs", the first words a link to `/learn/bill`.
  3. Choose Texas: the same sentence on the average, no link.
  4. Back to the United States; point at the "i" after "Net present value, 8 years": "($1,567.47 a year here, to the cent: the table below rounds it to the dollar)". The figures still read 3.2 years and $5,131.
  5. Open "Decisions in this game"; the "i" after "Charging at home ...": the corrected E-TOU-C words.

## Needs the key

- Nothing.

## Decisions made without you

- The reader's cars are the page's own pair: fueleconomy.gov refused the connection to its robots file again, so no other named pair's ratings could be read.
- California alone links the bill page (it draws no other state's utility tariff).
- The figures the game shows were not changed; the newer EIA prices wait on data request 99 (part A).

## For Samuel's ruling

- **Codes in the tips** (row 5): default kept; the other choice moves them to the table for the parents only.
- **Winter and the EV's kWh a mile** (row 8): default no words; the other choice a line from fueleconomy.gov's own page when it answers.
- **The electricity slider moves by 0.1 cent** (row 9): default kept; the other choice a box to type cents to three decimals.
- **A and B** (row 10): default none; the other choice a second results column that keeps the first case.

## Rows for the coordinator

**(a) Landing row 34: the new head.** Head: the commit that adds this report on `wip/7536-play-ev` (after `f09748795`). One line to append to "## Row 34: what it holds":

- **Session 7550 (the read, chain 304 part B), on top:** `EvGame.tsx` (the regional gasoline tip spells out PADD and names the states given its price; every electricity tip says what the average is, California's links `/learn/bill` without prefetch; the net present value's tip gives the yearly saving to the cent), `Decisions.tsx` (the home price line's source: E-TOU-C is not an EV rate, both its rates above the average, EV2-A not held), `replication/ev_game/` (replicate.py checks the new words; page_figures rewritten, 5,141; 5,245 of 5,245), `docs/methods/ev_game.md` (a row and a section), new `site/scripts/test-ev-game-read.mjs`, `tests/test_session7550_ev_game_read.py`, `docs/reviews/ev-game-read-2026-11-16.md`. No figure shown, no `check-values` key, no table, no `Num.tsx` change. Before landing: the site build already asked for; with it, `/play/ev` California's tip link passes the release gate (`/learn/bill` is in review). Snapshot differences: none on the 25 addresses. After: browser reads 276 to 278; data request 249.

**(b) Browser reads** (`docs/state/browser_reads_wanted.md`):

| # | Asked (UTC) | Session | Branch (landing row) | Address | What to look at | What should be seen | State |
|---:|---|---|---|---|---|---|---|
| 276 | 2026-11-16 | 7550 | `wip/7536-play-ev` (row 34) | `https://erw-flame.vercel.app/play/ev`, at 1280 and at 390 px | Choose Arizona, the "i" after "Gasoline, a gallon"; choose California, the "i" after "Electricity at home", then its link | Arizona's tip ends "the price the game gives Alaska, Arizona, Hawaii, Nevada and Oregon" and stays inside the screen at 390 px; California's tip ends "What is on an electricity bill draws a bill on PG&E's, SCE's and SDG&E's own tariffs", and the link can be reached by tap and by keyboard before the tip closes and opens `/learn/bill`; no sideways scroll | wanted |
| 277 | 2026-11-16 | 7550 | `wip/7536-play-ev` (row 34) | `https://erw-flame.vercel.app/play/ev` | Open "Decisions in this game", the "i" after "Charging at home is priced at the average ..." | The source reads "A utility's own rate can stand above or below the state's average: PG&E's E-TOU-C, a time-of-use rate for any home and not one made for EV owners, ... both above California's average of 33.61 in July 2026. PG&E's rate for EV owners (EV2-A) is not held." whole inside the tip | wanted |
| 278 | 2026-11-16 | 7550 | `wip/7536-play-ev` (row 34) | `https://erw-flame.vercel.app/play/ev` | As it opens, the "i" after "Net present value, 8 years" | "($1,567.47 a year here, to the cent: the table below rounds it to the dollar)"; the figures read 3.2 years and $5,131, the table "Saved a year with the EV $1,567" | wanted |

**(c) Data request** (`docs/state/data_requests_done_line.md`):

| # | Requested (UTC) | Session | Table or file | What, exactly | Source | State |
|---:|---|---|---|---|---|---|
| 249 | 2026-11-16 | 7550 (chain 304, samueloldlaptop; branch `wip/7536-play-ev`) | `site/data/bill_rules.json` (beside PG&E's E-TOU-C) | PG&E's residential rate for EV owners, EV2-A: its total rates by season (summer, winter) and period (peak, partial-peak, off-peak, with their hours), the effective date and the sheet numbers, so the Fresno driver of `/play/ev` (read row 7) and `/learn/bill` can read it; the decisions fold of `/play/ev` then names it in place of "is not held". Session 7536 fetched the schedule and had no PDF reader | PG&E's tariff book (pge.com, electric schedule EV2-A); robots file and terms read first | wanted |

**(d) Progress line** (`docs/state/progress_c304.md`):

| /play/ev (read) | samueloldlaptop | done <head> on wip/7536-play-ev (landing row 34): the reader a household choosing between the 2025 Equinox and Equinox EV in a named state, and a student; five cases (a Phoenix commuter; a Minneapolis family, 10 years, November 2026; a Fresno driver on PG&E, the average beside E-TOU-C and EV2-A; a student checking 3.2 years and $5,131; A and B with the board of the same day); rows: 13 (4 site fixed, 2 data machine, 3 browser, 4 rulings); replication 5245 of 5245 | 7550 |

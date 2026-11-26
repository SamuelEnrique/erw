# Session 10209 report (chain 710, part D, the old laptop): the trader view audited

26 November 2026. Worktree `C:\Users\lossa\Documents\erw-c710-a`, branch `wip/audit-trader-doc`. Model spend USD 0; no table written, no lock taken, no request to any service.

## What was done

- `docs/reviews/trader-model-audit-2026-11-26.md`, with its evidence in `docs/reviews/trader-model-audit-2026-11-26/` (scripts, printouts, the drawn week section).
- The arithmetic is right: 4,543 public figures of `iso_trader_daily` restated from the price tables (all to the fourth decimal but nine heat rates of 15 October, taken on the day before's gas because EIA's came a day after the run); MISO by counts only; the board's week table of 21 October, 227 of 227; of 25 November, to the cent on three hubs; the top ten intervals, 20 of 20.
- Six findings: three Medium (SPP's real time held and not read; the heat rate's gas day; the off-peak week weighs days, not hours), three Low (the volatility and hours heads; the Eastern on-peak block; the notes describe `/markets` and rules the code does not have).
- Branches: `wip/audit-trader-1` (`3b06ebfcd`), `-2` (`417426069`), `-4` (`1c083e5eb`), `-5` (`38b3d58d2`), `-6` (`09eedb97c`), words only, for landing; `-3` (`355a6d71f`), a figure, not for landing. The words branches merge together and with the board audit's branches 3, 4 and 5 with no conflict; all tests pass in the trial.
- Branches 1, 2 and 4 drawn with the site's own code (`BoardView` after `holdRows`) and the new words read: pass.

## Decisions made without you

- The trader view's page is now the board's "The week, by hub" (`/markets` redirects to `/board` since session 132), so that table and its builders were audited; the board audit's findings were cited, not repeated.
- Branches 1, 2 and 4 edit `site/components/board/BoardView.tsx` (not `site/app/board/`), as the board audit's branches 3 and 4 did; to keep clear of those branches' lines, finding 2's words are a line under the week table and finding 1's SPP cells are handled at the cell's call, not in the cell function.
- A comment in `warehouse/run_daily.sh` that repeats "SPP has no real-time table" was left as it is, so that the branch did not reach the sixty test files that read that script.
- The Eastern on-peak block (hours ending 8 to 23) is this auditor's reading of the operators' and exchanges' definitions, not checked against a file held here; the note says it and the size is a data request.

## For Samuel's ruling (default "left as it is" on each)

- Read SPP's real-time table in the trader view: SPP North's week gains real time less day-ahead -3.73 USD/MWh, SPP South's -3.66 (from the page's hourly files).
- Divide by Henry Hub of the trading day before the operating day (when the day-ahead power traded): ERCOT hub average's daily heat rate moves 0.31 MMBtu/MWh on average over 363 days, at most 4.86.
- The off-peak week by hours, not by days: SP15 42.72 to 39.36 (-7.9 percent), SPP North 19.08 to 16.61 (-13.0 percent) on the board of 25 November.

## Data requests

- The one-hour shift of the on-peak block for NYISO and ISO-NE (hours ending 8 to 23 against 7 to 22), sized on the data machine as counts and percents only.
- ERCOT's six hubs', CAISO ZP26's and SPP South's week of 19 to 25 November: already the board audit's request, not filed twice.

## Needs the key

- Nothing.

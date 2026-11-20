# Chain of 19 November 2026: sessions 8012 to 8199, data machine (lab-desktop), one window, unattended, 20 hours and more: the desk, the two pages the second window never built, every balancing authority's own facts, the operators' forecasts against what happened, and what power costs across the map

machine: data

Written by Claude in chat with Samuel on 19 November 2026 at about 11:15 PST and pasted by him into the window that ran chain 501. It is not a machine's successor file, and no machine writes a successor to it. Folder: `C:\Users\Shared\Documents\erw`. Model: Opus 5.5, high effort. One Claude Code session: the second window (chain 502) stopped at 13:30 UTC and Samuel has closed it.

## Why this chain

Overnight this window put the whole country into the warehouse's page files and landed what three other windows built on them. Two pages Samuel asked for in September never got built, because their files landed after the second window had stopped: energy use by industry, and energy per AI query as published. The map of the balancing authorities is live in review, and clicking an authority can only say what the flows say: nothing yet tells a reader what that authority owns, burns, plans or pays. And the master plan's eighth tool, where power is cheap and dear across the map, has not been started. This machine holds the data and can build and see a page, so all of it can be done here without waiting on anyone. Samuel's allowance resets on Friday morning and he will not review before then: nothing here waits on a ruling.

## Rules

- **The rules of chain 501 hold word for word** (`queue/done/501-day-19-november-desktop-whole-country-data.md`, and through it the owner's rules of 16 November), with these changes:
- **Session numbers** go on from chain 501's last, up to 8199, each checked free first.
- **One window now.** The second window's resume file `queue/next/520-resume-chain-502.md` is removed in this chain's first commit, with one line in the progress file. Its findings code is landing row 2 of `docs/state/landing_request_window2.md`, which the desk lands.
- **The desk still comes first:** the personal laptop (chain 504, `/grid` and `/resources`) is building until this evening, and the old laptop (chain 506) audits findings and may file data requests.
- **`/grid` is the personal laptop's while its chain runs.** This window changes `/grid` only on a branch cut from the newest landed main, and only when no row of the personal laptop for `/grid` is waiting to land. Otherwise it writes the file and the contract, and the page work waits its turn.
- **Add, never change. No default moves. No ruling is taken for Samuel.** Every page stays in review. Nothing is published, posted or released.
- **Held prices are never drawn.** A grid whose prices `docs/licenses.md` holds (PJM, and whichever of NYISO, ISO-NE and MISO it holds today) appears on any price view as a blank with the hover "license needed", as Samuel's rule for held data has it. No hold is lifted or worked around.
- **No model of the ERW's own.** A forecast shown here is an operator's or EIA's own published forecast beside what happened. This chain fits no forecasting model and writes no estimate of its own.
- **The page standard** is rule 9 of `queue/done/302-day-16-november-oldlaptop-large-load-on-the-site.md`. A new page is seen at 1280 and 390 px before it lands.
- **Never end idle.** After part E, part F, until the weekly limit.

## Restart safety and the progress file

- This chain's first session writes `queue/next/550-resume-chain-505.md` and removes 510, committed alone and pushed. Its text is the lines between BEGIN and END below, without those two words. A session that takes a resume file first writes the same text under the next number up (to 559). The chain's last session removes it.
- `docs/state/progress_c505.md`: one line a landing, request, page, file or table, its state and session, pushed after each.

BEGIN
# Resume of chain 505

machine: data

Chain 505 was interrupted. First put this same text back in queue/next/ as the next number up to 559, named NNN-resume-chain-505.md, committed alone and pushed. Then read queue/done/505-day-19-november-desktop-pages-authorities-prices.md whole and docs/state/progress_c505.md, and continue chain 505 from the first step not marked done, under that file's rules, with the next free session number in its range. Write no other queue file.
END

## Part A: the desk and the requests (the start of every session, and again after each numbered step)

As part A of chain 501, unchanged.

## Part B: the two pages the second window never built

1. **"Energy use by industry"**, from `site/data/industry.json`: as part B of `queue/done/502-day-19-november-desktop-window2-findings-industry.md` says, word for word, built and seen here.
2. **"Energy per AI query, as published"**, from `ai_energy_published`: as part C of that file says, word for word.
3. Each to the done line in the form of `queue/done/303-night-16-november-portable-trackers-done-line.md`, listed on `/in-review`, in no menu; where each sits in the menu is one plain line under "For Samuel's ruling".

## Part C: every balancing authority's own facts (`site/data/regions/authority/<code>.json`, its contract added to `docs/state/page_files_regions.md` first)

For each authority of `index.json`, and summed for each of the thirteen regions:

1. What it owns: installed capacity by source and the ten largest plants (EIA-860, by the plant's balancing authority).
2. What is coming and going: planned additions and retirements by source and year (EIA-860M).
3. What it burns and how clean it is: generation by source over the last twelve months, and carbon intensity where EIA's emissions file gives it.
4. Whom it trades with: its five largest partners and its share of demand met by net imports (`ba_trade_partners`).
5. Its size: peak demand, the hour and date of its record, growth since 2019.
6. What is said of large loads there, where `large_load_public` holds a public row for its utility.

Each figure with its table and vintage. An authority a source does not cover has the key with a null and the reason, never a zero. Then, under the `/grid` rule above: the side panel that opens on a click of the map or the network shows these facts for every authority and region, under what it shows today.

## Part D: the forecast beside what happened

1. `eia930_forecast_error_hourly` and `_daily`: for every authority and region that files one, the day-ahead demand forecast beside the demand that came, since July 2018: the miss in megawatts and in percent, by hour of day, by season, on the hottest and coldest days, and across the nine events.
2. Wind and solar: the operator's own forecast beside the output that came, for each grid that publishes both under a license `docs/licenses.md` lets a page show.
3. Page files `site/data/regions/forecast/<region>.json`, in the contract. Then one view, "Forecast against actual", on the country view of `/demand` (`/demand?view=country`, on main since this morning): any region or authority, two side by side, every figure with its source on hover.

## Part E: what power costs across the map (the master plan's eighth tool)

1. **First, what exists** (rule 4): the price views already on `/prices`, `/board`, `/map` and the All grids tab of `/cost-of-power`, read and listed, so nothing is built twice. Where a layer of this kind exists, it is extended, not copied.
2. **The file,** `site/data/regions/prices_map.json`, in the contract: for every hub and load zone whose price a page may show, and the authority or region it sits in: yesterday's day-ahead average, on-peak and off-peak, the thirty-day and twelve-month averages, the share of hours below zero, the spread between the dearest and cheapest four hours of the day. Held grids carry the key with a null and "license needed".
3. **The layer,** under the `/grid` rule above: a "Price" switch on the map of the balancing authorities that colors each area by the measure chosen, with the flows still drawn over it, so a reader sees where power is cheap, where it is dear and which way it moves. The carbon color stays what opens, as Samuel ruled; price is a choice the reader makes.
4. To the done line in chain 303's form, with the cross-check against the operators' own published averages.

## Part F: after part E, until the weekly limit

- Every table landed since 17 November that a page now reads: its figures on the page traced to their rows once more by `check-values`, and each fault fixed at its cause.
- Every scheduled job that failed in the last fourteen days: its cause written in `queue/summary/` and fixed, so the count of green days on `/internal/health` is true. Part A after each.

## The last session

- `docs/state/note_2026-11-19_data_c505.md` in short bullets: every landing with what a reader now sees; the two new pages with their addresses; what part C gives a reader of the map; parts D and E's files and views; what waits for Samuel with the default taken, in plain words.
- The resume file removed; `.venv\Scripts\python.exe scripts\chain_queue.py next`, and the file it prints run the same way. No file: part F goes on.

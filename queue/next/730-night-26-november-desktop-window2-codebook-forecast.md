# Chain of 26 November 2026, night: sessions 10600 to 10799, lab-desktop, second window, unattended, until the weekly limit: the codebook's last steps, then the ERW's own day-ahead forecast of demand and price, scored against what happened and against each operator's own forecast

machine: lab-desktop-window2

Written by Claude in chat with Samuel on 26 November 2026 at about 03:15 PST, uploaded by him to `queue/next` and started by him by name in a SECOND Claude Code window on the desktop. It is not a machine's successor file, and no machine writes a successor to it. The `machine:` line names no role, on purpose: the chain worker and the first window never take this file or its resume file, and `chain_queue.py` refuses a window's mark, so this window takes its file by hand (one commit that moves it from `queue/next/` to `queue/done/`, pushed). Folder: `C:\Users\Shared\Documents\erw-w2` (a worktree of the desktop's repository). Model: Opus 5.5, high effort. Run it unattended, to its last session. Do not stop to ask questions. Model spend USD 0: call no model API. No heredocs or long inline scripts: use the Edit and Write tools, and put scripts in `runs/`.

## Why this chain

Samuel noted on 10 October that every site the ERW is measured against shows a forecast and the ERW shows none of its own: it shows the operators' forecasts beside what happened (`/demand`, the forecast error tables) and stops there. This window builds the ERW's forecast, and builds it the way the rest of the ERW is built: every method written down, every figure replicable, and the forecast graded in the open against what happened and against the operator's own forecast for the same hours, including the hours where the ERW loses. A forecast with its report card on the same page is something a trader, a developer and a researcher can use and cite, and it grades itself, so it does not wait on Samuel's review to be trusted. He asked for it directly on 26 November. It needs no ruling: where a choice is his, the default is taken and written in one plain line.

## The six windows of this run (who owns what)

| Window | Chain | Folder | Owns tonight |
|---|---|---|---|
| A, desktop first window | 701 | `C:\Users\Shared\Documents\erw` | every landing; the data lock and every warehouse table; the daily run; the equities tables and `site/data/equities/`; the large-load tables |
| B, desktop second window (this one) | 730 | `C:\Users\Shared\Documents\erw-w2` | the codebook's last steps; the ERW forecast: `warehouse/predict/`, `site/data/predict/`, `docs/state/page_files_predict.md`, `docs/state/data_requests_predict.md`, `docs/methods/predict*.md`, `replication/predict/` |
| C, desktop third window | 740 | `C:\Users\Shared\Documents\erw-w3` | datacenters in the Economic impact tool: `site/app/impact/`, `warehouse/forecast/`, `site/data/forecast/`, `docs/methods/forecast.md`, `docs/state/data_requests_forecast.md` |
| D, old laptop | 710 | `C:\Users\lossa\Documents\erw` | the weekend page; the datacenter model audit and the Automated Analysis audit |
| E, personal laptop first window | 720 | `$HOME\Documents\erw` | the pages: `site/app/forecast/`, `site/app/equities/`, the new group in `site/app/board/` |
| F, personal laptop second window | 750 | `$HOME\Documents\erw-w2` | the browser read of everything landed; its fixes on branches `wip/c750-*` |

A window edits only what it owns. A fault found in another window's files is a row for that window, never an edit. Branch names carry the chain's number (`wip/c730-*` here).

**The word "forecast" is taken in the code.** `warehouse/forecast/`, `site/data/forecast/`, `docs/methods/forecast.md`, `docs/state/data_requests_forecast.md` and the table `forecast_tool_parameters` are the Economic impact tool's (`/impact`, chain 239), and window C works in them tonight. This build's name in every path, table and file is `predict`. Its page, which window E builds, is `/forecast`, and its name on the page is "ERW forecast". This window writes nothing under any path that holds the word forecast.

## Rules

- **The owner's rules of 16 November 2026 hold word for word** as written in `queue/done/301-day-16-november-desktop-open-faults.md` (its rules 1 to 10), with the changes below.
- **The second window's rules** are those of `queue/done/630-night-20-november-desktop-window2-codebook.md`: this window writes NO warehouse table and takes NO data lock; it never runs the daily run or a backfill; every site build and every whole suite goes through `scripts/buildlock.py`; it never kills a process it did not start; it works only in its own folder and in worktrees it adds beside it; Python is `C:\Users\Shared\Documents\erw\.venv\Scripts\python.exe` by its full path, and the warehouse's data files in the main folder are read, never written.
- **This window does not land.** Code and page files for landing are one row marked requested in `docs/state/landing_request_window2.md`, which window A's desk lands. Documents, reports and the progress file are pushed to main directly.
- **What the warehouse must hold is asked, not written.** Each table this build wants in the warehouse's record (the forecasts with their vintage, the scores) and its step in the daily run is one row marked requested in `docs/state/data_requests_predict.md`, in the form of `docs/state/data_requests_forecast.md`, for window A. Until a row is done, the page reads `site/data/predict/`, which this window writes. No row is waited for.
- **Session numbers** 10600 to 10799, each checked free on origin/main and every branch first. **Its queue step is by name, never bare `next`.**
- **No waiting.** A step that needs a build lock another window holds, a table not yet current or a row window A has not done is marked waiting in the progress file and the next step is taken at once. No sleep, no timer, no "waiting" commit.
- **What exists is read before anything is built** (rule 4): the operators' forecasts and forecast errors the warehouse holds, the weather tables, the page `/demand`. They are read and used, never built a second time.
- **Held data stays held.** A forecast is made and shown only for a place whose input tables are public-licensed (`docs/licenses.md`). A held grid's price is not forecast on the page: its cells are written null with the reason, and window E draws them blank with "license needed".
- **A forecast is a model's output and says so.** Every stored forecast carries the tier `derived` (`docs/datastandard.md`, "Provenance tiers") and never enters a layer 1 table unmarked (`PRIORITIES.md`, layer 2). The page and the files call it "ERW forecast" and never a published or official figure. No advice, no view, no word on what a reader should do with it.
- **Nothing is known early.** A forecast for a day, and every backtest of one, uses only what was published before the hour the forecast would have been made. A model that uses the weather as it turned out is not a forecast: it may be shown only as a separate line labelled "with the weather known", never as the headline.
- **Nothing is hidden.** The score table shows every place and every method, the ERW's losses to the operator's forecast and to "the same hour yesterday" included. No place and no period is left out of a score because it scored badly.
- **Add, never change. No default moves. No ruling is taken for Samuel.**
- **Never end idle.** After part E, part F, until the weekly limit.

## The start (session 10600, long end 0:30)

1. Precheck by the main folder's Python. `git fetch origin`; this folder at `origin/main`, detached, as its rules have it. Free disk and memory written down.
2. This chain's file taken by hand: `queue/next/730-...` moved to `queue/done/` in one commit of that move alone, pushed to main.
3. The resume file `queue/next/731-resume-chain-730.md`, committed alone and pushed, its text the lines between BEGIN and END below without those two words. Nobody takes it by itself: Samuel restarts this window by name if it stops. The chain's last session removes it.
4. `docs/state/progress_c730.md`: one line a step, with its state, counts and session, pushed after each.

BEGIN
# Resume of chain 730

machine: lab-desktop-window2

Chain 730 was interrupted. Read queue/done/730-night-26-november-desktop-window2-codebook-forecast.md whole and docs/state/progress_c730.md, and continue chain 730 from the first step not marked done, under that file's rules, in C:\Users\Shared\Documents\erw-w2, with the next free session number in its range. Leave this file in queue/next until the chain's last session. Write no other queue file.
END

## Part A: the contract for the forecast page (done and pushed to main within this chain's first hour, before anything else)

Window E builds the page tonight and cannot start without this. `docs/state/page_files_predict.md`, in the form of `docs/state/page_files_conditions.md`: the files this chain will write under `site/data/predict/`: an index of the places and what is forecast for each (demand; price where public); one file a place holding tomorrow's forecast by hour with its band, the forecast made on each past day beside what happened, and the operator's own forecast for the same hours where the warehouse holds it; one score file (by place, by method, by month and by hour of day: the mean absolute error and the mean absolute percent error, for the ERW, the operator and "the same hour yesterday" and "the same hour a week ago"); the method each place uses and the day it was last fit. Each field with name, type, unit and an example row; how a held value is written (the field present, the value null, a `held` reason); the date and hour each file was written and the hour the forecast was made. One small example file of each kind, marked as an example with its values null, is pushed with the contract. A later change to the contract is one dated line at its foot and a line in `docs/state/landing_request_portable.md` for window E.

## Part B: chain 630 closed (long end 1:00)

`docs/state/progress_c630.md` read: each step of chain 630 not marked done is finished or said to be no longer needed with why; its landing rows and its data request 566 checked against main and the Redivis drafts' record. Then `queue/next/631-resume-chain-630.md` removed in one commit, and one line in this chain's progress file. Nothing of the codebook is built twice. If more than an hour of codebook work is open, the open tables are listed, part C starts, and the list is returned to in part F.

## Part C: the ground and the data (long end 1:00)

`docs/reviews/predict-ground-2026-11-26.md`:

- **What can be forecast, place by place:** for each of the thirteen regions and each large balancing authority: the hourly demand held (EIA-930), its span and gaps; the operator's own day-ahead demand forecast held for the same hours; the day-ahead and real-time hub prices held, their license, their span; the weather held (observations, and `weather_forecast_hourly` with the hour each forecast was issued, if it keeps one); the calendar (weekends, federal holidays, the clock change).
- **What was known when:** for each input, the hour of the day it is published, so that the hour the ERW's forecast is made each day can be fixed and no input is used early.
- **The order of the build that follows from it:** demand first, for every place with public demand; then price, for the grids whose hub prices are public; places and series that are held or too short are listed with the reason.

## Part D: the forecast of demand

1. **The methods, simplest first, each one written so that a reader can run it:** (a) the same hour yesterday; (b) the same hour a week ago; (c) a regression on the hour of the week, the holidays, the recent days' demand and the temperature forecast issued before the forecast hour (or, where no dated weather forecast is held, on what was known without weather); (d) one more flexible method only if it beats (c) out of sample by a margin the note states, fit with a fixed seed. No method whose fit cannot be repeated to the last digit. The regression also as a Stata do-file under `replication/predict/`, because Samuel runs Stata.
2. **The backtest:** walking forward a day at a time over at least the last two whole years where the history allows, each day forecast from a model fit only on days before it. Scores by place, method, month and hour of day, against what happened, beside the operator's own forecast scored on the same hours. Extreme days scored apart: each place's ten highest-demand days and the days of the nine events of `/events`.
3. **The choice, by rule:** for each place the method with the lowest out-of-sample error over the backtest is the one the page shows as the ERW forecast; the rule and every method's score are in the method note. The band around a forecast is the spread of that method's own past errors at that hour, and says so.
4. **Tomorrow's forecast,** written each day by one script (`warehouse/predict/run.py`), with the hour it was made; a forecast once written is never overwritten, so the track record from tonight on is the real one and the page shows it growing.
5. **The files** of the contract, written from the script's output; `check-values` for each; tests that fail when a forecast uses a row published after its forecast hour, when a place's file lacks its score, and when a held place holds a number.
6. **The requests to window A:** the forecasts and scores as tables with the tier `derived`, and the daily step, as rows in `docs/state/data_requests_predict.md`. Landing of the code and the first files requested as soon as part D's tests pass, so that window E can see the page on real files tonight.

## Part E: the forecast of price

For each grid whose day-ahead hub prices are public-licensed: the same ladder (yesterday's hour, last week's hour, a regression on the demand forecast of part D, the wind and solar forecasts the warehouse holds, the gas price and the calendar), the same walk-forward backtest, the same scores, with the hours above each grid's 99th percentile scored apart, because a price forecast is judged on its spikes. The files, tests, method note (`docs/methods/predict_price.md`) and requests as in part D. A grid whose prices are held is not forecast on the page.

## Part F: after part E, until the weekly limit

- **The peak:** for each place, the forecast of tomorrow's peak hour and peak demand, scored the same way.
- **Further ahead:** two to seven days, each horizon scored apart, shown only where it beats "the same hour a week ago".
- **A band that is honest:** the share of past hours that fell inside the band, by place, printed beside the band.
- **Net demand** (demand less wind and solar) for the grids whose wind and solar forecasts are held.
- The cross-check: for two places, the backtest's operator error set beside what the operator or its market monitor prints of its own forecast error, where one prints it.
- The replication under `replication/predict/` to the form of the other tools' (`replication/congestion/replicate.py`): every figure of the score file reproduced from the public tables.
- The codebook's open list of part B, if any.
- `docs/reviews/browser-read-2026-11-26.md` read after each step for rows window F wrote that name this window's files.

## The last session

- `docs/state/note_2026-11-26_window2_c730.md` in short bullets: the places forecast and the method each uses; the scores in one table (the ERW, the operator, yesterday's hour), the places where the ERW loses said first; what is held and why; where the files are; what waits for window A and for Samuel, each with the default taken, in plain words.
- The resume file removed. `C:\Users\Shared\Documents\erw\.venv\Scripts\python.exe scripts\chain_queue.py next --file <a file named for lab-desktop-window2, if one waits>`. No such file: part F goes on.

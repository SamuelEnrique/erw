# Chain of 26 November 2026, night: sessions 10400 to 10599, portable-laptop (code role), first window, unattended, overnight and as long as nobody stops it: the two new pages of this run, the ERW forecast (`/forecast`) and energy equities (`/equities` and a group on the price board), built against the data machine's files as they land

machine: portable-laptop

Written by Claude in chat with Samuel on 26 November 2026 at about 03:15 PST, uploaded by him to `queue/next` and started by him by name on the personal laptop. It is not a machine's successor file, and no machine writes a successor to it. Folder: `$HOME\Documents\erw`. Model: Fable, high effort. This is the laptop's FIRST window and the only one on this laptop that builds the site; a second window (chain 750) reads pages in a browser beside it. Run it unattended. Do not stop to ask questions. Model spend USD 0: call no model API. No heredocs or long inline scripts: use the Edit and Write tools, and put scripts in `runs/`.

## Why this chain

Two things reach the warehouse tonight that the site has no page for. The desktop's second window is building the ERW's own day-ahead forecast of demand and price, scored in the open against what happened and against each operator's own forecast: every site the ERW is measured against shows a forecast, and none shows its report card beside it. The desktop's first window is bringing in the listed energy companies and indices, which Samuel asked for on 24 November. A table nobody can see is worth little. This laptop is the one that can build a page and look at it, so it builds both pages against a written contract while the data is being made, and swaps in the real files as they land. Samuel reviews over the weekend and should meet two pages that work, not two tables.

## The six windows of this run (who owns what)

| Window | Chain | Folder | Owns tonight |
|---|---|---|---|
| A, desktop first window | 701 | `C:\Users\Shared\Documents\erw` | every landing; the data lock and every warehouse table; the equities tables, `site/data/equities/` and the contract `docs/state/page_files_equities.md`; the large-load tables |
| B, desktop second window | 730 | `C:\Users\Shared\Documents\erw-w2` | the ERW forecast's code and files: `warehouse/predict/`, `site/data/predict/` and the contract `docs/state/page_files_predict.md` |
| C, desktop third window | 740 | `C:\Users\Shared\Documents\erw-w3` | datacenters in the Economic impact tool: `site/app/impact/`, `warehouse/forecast/`, `site/data/forecast/` |
| D, old laptop | 710 | `C:\Users\lossa\Documents\erw` | the weekend page; the datacenter model audit and the Automated Analysis audit |
| E, personal laptop first window (this one) | 720 | `$HOME\Documents\erw` | the pages: `site/app/forecast/`, `site/app/equities/`, the new group in `site/app/board/`, their components and tests |
| F, personal laptop second window | 750 | `$HOME\Documents\erw-w2` | the browser read of everything landed; its fixes on branches `wip/c750-*` |

A window edits only what it owns. A fault found in another window's files is a row for that window, never an edit. Branch names carry the chain's number (`wip/c720-*` here). This window writes no file under `site/data/predict/`, `site/data/equities/`, `site/data/forecast/` or `site/app/impact/`.

**The word "forecast" is taken in the code.** `warehouse/forecast/`, `site/data/forecast/` and `site/app/impact/Forecast.tsx` are the Economic impact tool's, and window C works in them tonight. The new page's address is `/forecast` and its folder is `site/app/forecast/`; the files it reads are under `site/data/predict/`; its name on the page is "ERW forecast". Nothing of `/impact` is imported, edited or renamed.

## Rules

- **The owner's rules of 16 November 2026 hold word for word** as written in `queue/done/303-night-16-november-portable-trackers-done-line.md` (its rules 1 to 11), and the rules of `queue/done/620-night-20-november-portable-browser-read-everything-new.md`, with these changes:
- **Session numbers** 10400 to 10599, each checked free on origin/main and every branch first. The four-digit numbers are nearly all taken, so this run's are five digits.
- **Memory, with two windows on this laptop.** The free memory is read and written in the report at the start of each session and before each build. A build is made one at a time, in the foreground, through `scripts/buildlock.py`, only with 2 GB free, and the served build is stopped before anything else starts. With less than 2 GB free, no build: the session writes code and tests, and returns to the build later. It never waits for memory and never kills a process it did not start.
- **No waiting.** A contract or a page file that is not on main yet is marked waiting in the progress file and the next item is taken at once. No sleep, no timer, no "waiting" commit. `git fetch` before each numbered step.
- **This machine does not land and writes no warehouse table.** A page for landing is one row marked requested in `docs/state/landing_request_portable.md`, which window A's desk lands. A fault in a page file is not fixed here: one line in the owning window's request file (`docs/state/data_requests_predict.md` for the forecast's files; `docs/state/data_requests_done_line.md` for the equities files), with the file, the value seen and the value expected.
- **The contract is the interface.** Each page reads exactly the files and fields its contract names. Until the real files are on main the page is built and tested against the contract's own example files. A field the page needs and the contract lacks is asked for in one line in the owning window's request file; it is never invented on this side.
- **The page standard** is rule 9 of `queue/done/302-day-16-november-oldlaptop-large-load-on-the-site.md` and Samuel's standing rules: dense and informative, not generic; charts and tables answer to the mouse; defaults and sources on hover only, never grey text; method notes, limitations and "not held" notes stay off the page; inputs at left and results at right; A and B side by side; plain nouns; a held value drawn blank with "license needed" on hover; real numbers only, never a placeholder shown as real; no sideways scroll at 390 px; light mode only; `docs/brand.md` as it stands, no new brand decision.
- **No advice, no view.** The forecast page says what the model forecast and how it has scored. The equities pages say what was published. No "outperform", no signal, no "so what".
- **Add, never change. No default moves. No ruling is taken for Samuel.** Each new page stays in review, in no menu, listed on `/in-review`; where it sits in the menu and what it is called are one plain line each under "For Samuel's ruling". The price board keeps everything it has, in the order it has it.
- **Never end idle.** After part D, part E, until Samuel takes the laptop.

## The start (session 10400, long end 0:20)

1. Precheck. `git fetch origin`, `main` at `origin/main`. Free memory written down.
2. This chain's file taken (`queue/next/720-...` to `queue/done/`), if the command that started the session has not already done it.
3. The resume file `queue/next/721-resume-chain-720.md`, committed alone and pushed, its text the lines between BEGIN and END below without those two words. A session that takes a resume file first writes the same text under the next number up (to 729), its machine line unchanged. The chain's last session removes it.
4. `docs/state/progress_c720.md`: one line a step, a view or a row, its state and session, pushed after each.

BEGIN
# Resume of chain 720

machine: portable-laptop

Chain 720 was interrupted. This file is the portable laptop's first window's: another machine leaves it where it is. First put this same text back in queue/next/ as the next number up to 729, named NNN-resume-chain-720.md, committed alone and pushed. Then read queue/done/720-night-26-november-portable-forecast-equities-pages.md whole and docs/state/progress_c720.md, and continue chain 720 from the first step not marked done, under that file's rules, with the next free session number in its range. Write no other queue file.
END

## Standing step, after each numbered step below

Every row marked `ready, to be seen` in `docs/state/landing_request_portable_w2.md` (the second window finds and fixes faults and cannot build): the branch seen in a build at 1280 and 390 px, then its row marked requested, or marked `not fixed` with what was seen. One build at a time, by the memory rule.

## Part A: last week's fixes that never saw a build (while the contracts are being written; long end 1:30)

Rows 44 to 51 of `docs/state/landing_request_portable.md` are fixes chain 620 finished and left "ready, not requested" because this laptop had no memory to see them in a build. Each is checked against main first (a fix already landed or overtaken is marked so), then seen in a build at 1280 and 390 px, one at a time, and marked requested. A row that cannot be built for memory is left with the reason and returned to after part B.

## Part B: the ground for both pages (no build; long end 0:45)

`docs/reviews/pages-ground-2026-11-26.md`: what the site already has that these pages must reuse and not build a second time: the forecast section of `/demand` and its components (the operators' forecasts beside what happened); the chart with a band, the place picker and the A and B pattern of the newer pages; the price board's rows (`site/app/board/`) and how a group and a held row are drawn there; the chart workbench that overlays two series, if the board or `/prices` has one; the downloads (CSV, Stata, Python) as the other pages make them. Then, for each of the two pages, five real cases a named reader would bring, written in three lines each before anything is built: for the forecast, a power trader the evening before a hot day, a battery operator choosing tomorrow's hours, a utility planner, a researcher who wants the score, a student; for equities, an energy investor on a day oil falls, a lender comparing two utilities, a developer looking up a counterparty, a trader asking what moved with gas, a student of one company.

## Part C: the ERW forecast, `/forecast` (new, in review)

Starts when `docs/state/page_files_predict.md` is on main (window B writes it in its first hour). Until then, part A and part B.

1. **Tomorrow:** for a chosen place, the forecast of demand by hour with its band, and the operator's own forecast for the same hours beside it where the files hold one. A second tab for price where the place's price is public; a held place's price drawn blank with "license needed".
2. **How it has done:** the forecast made on each past day beside what happened, any day picked; and the score table: the ERW, the operator, "the same hour yesterday" and "the same hour a week ago", by month and by hour of day, for the chosen place and for all places at once. The hours and places where the ERW loses are drawn exactly as the ones where it wins: same table, same weight, no sorting that hides them.
3. **Two places side by side** (A and B). The hour the forecast was made and the method the place uses on hover. The words "ERW forecast" on every chart of it; nowhere a word that could let it be taken for the operator's or a published figure.
4. **Downloads** as the other pages have them; every figure sourced on hover.
5. **Tests** that pin what a reader sees, against the contract's example files; then, once window B's real files are on main: the page seen in a build at 1280 and 390 px, the five cases taken start to finish, every figure the page shows as it opens and ten more after choices set beside the files, the keyboard alone from top to bottom, the back button after a choice. Landing requested. A tour stop, held by its flag.

## Part D: energy equities

Starts when `docs/state/page_files_equities.md` is on main (window A writes it in its first hour).

1. **A group on the price board (`/board`):** the board's own form and density, a row a segment and a row an index, each with its last value and its change over a day, a week, a month, the year to date and a year, and the small trend the board's other rows have. A held series is a row drawn blank with its hover, as MISO's is. Nothing the board has is dropped, moved or restyled.
2. **`/equities` (new, in review), the group's analyzer:** every company by segment in one table that sorts and filters; a company or a segment as a line over any window, with any energy price the files carry laid over it (the board's workbench reused if part B found one); the two weightings of a segment's line named plainly; a company's filed revenue, income, capital spending, debt and shares by quarter with each filing's address on hover; two companies or two segments side by side. Where the files hold a company's fundamentals and its price is held, the page shows the fundamentals and draws the price blank.
3. **Downloads, tests, the five cases, the build at 1280 and 390 px** as in part C. Landing requested. A tour stop, held by its flag.

## Part E: after part D, until Samuel takes the laptop

- Parts C and D seen once more on production after each landing of new files (deeper history, the price forecast, the peak): what changed read against the files.
- For each of the two pages, one problem set in the form of the problem-set builder's own (the forecast's score table; a segment beside an energy price), held out of the dated edition until Samuel approves it.
- The phone's width: each new view taken through its five cases at 390 px by a finger, every gap a row and a fix.
- `docs/reviews/browser-read-2026-11-26.md` read after each step for rows the second window wrote that name this window's pages; each fixed at its cause with a test.
- The standing step.

## The last session

- `docs/state/note_2026-11-26_portable_c720.md` in short bullets: each page with its full address and what to click, step by step, and what Samuel should see; what on each is real data and what is still an example or blank, and why; the rows seen and requested for the second window; what waits for Samuel with the page left as it is, in plain words.
- `.venv\Scripts\python.exe scripts\chain_queue.py next`, and the file it prints run the same way. No file: part E goes on. Samuel closes this session himself.

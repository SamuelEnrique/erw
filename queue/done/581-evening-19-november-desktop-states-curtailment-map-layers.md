# Chain of 19 November 2026, evening: sessions 8014 to 8199, data machine (lab-desktop), one session, unattended: every state on one page, where and when power is spare, the project map's missing layers, the price board's missing prices, storage and queues for the whole country

machine: data

Written by Claude in chat with Samuel on 19 November 2026 at about 18:00 PST and uploaded by him to `queue/next`. It is not a machine's successor file, and no machine writes a successor to it. Folder: `C:\Users\Shared\Documents\erw`. Model: Opus 5.5. Run it unattended, to its last session. Do not stop to ask questions. Model spend USD 0: call no model API. No heredocs or long inline scripts: use the Edit and Write tools, and put scripts in `runs/`.

## Why this chain

In one day the site went from seven grids to the whole country by region and by balancing authority. A reader still cannot ask the plainest question of an energy site: what about my state. The warehouse holds what answers it (generation by state since 2001, sales and revenue by state and sector, gas, CO2, the plants, what is planned, the large-load laws) and no page puts a state together. Three more things Samuel asked for in September and October are still open: the hours and places where power is curtailed or priced below zero, the project map's layers beyond power plants (the master plan's third tool names pipelines, LNG terminals, refineries and transmission), and the prices the board lacks. Samuel has no time to review until late tonight and wants this machine building until then: nothing here waits on a ruling.

## Rules

- **The rules of chain 505 hold word for word** (`queue/done/505-day-19-november-desktop-pages-authorities-prices.md`, and through it chain 501 and the owner's rules of 16 November), with these changes:
- **Session numbers** go on from chain 505's last, up to 8199, each checked free on origin/main and every branch first.
- **If chain 505's resume file is still in `queue/next/`** when this chain starts, chain 505 is closed first: its last steps taken if any is open, its resume file removed, one line in the progress file.
- **The desk comes first, every session:** the old laptop (chain 590) asks for data and for landings tonight.
- **What exists is read before anything is built** (rule 4). Each part below starts by listing what the site and the warehouse already hold of it, in the progress file. What exists is extended, never built a second time.
- **Add, never change. No default moves. No ruling is taken for Samuel.** No `wip/alt-*` or `wip/switch-*` branch is landed or merged. Every page stays in review, a new page is in no menu and is listed on `/in-review`, and where it sits in the menu is one plain line under "For Samuel's ruling".
- **Held data is never drawn:** a blank with the hover "license needed", as Samuel's rule has it. No hold is lifted or worked around. Each new source's robots file and terms are read before any pull.
- **No model of the ERW's own, no advice, no view.** A page says what the data hold.
- **The page standard** is rule 9 of `queue/done/302-day-16-november-oldlaptop-large-load-on-the-site.md`. A new view is seen at 1280 and 390 px before it lands.
- **Never end idle.** After part F, part G, until the weekly limit.

## Restart safety and the progress file

- The first session writes `queue/next/582-resume-chain-581.md`, committed alone and pushed. Its text is the lines between BEGIN and END below, without those two words. A session that takes a resume file first writes the same text under the next number up (to 589). The chain's last session removes it.
- `docs/state/progress_c581.md`: one line a landing, request, file, table, page or view, its state and session, pushed after each.

BEGIN
# Resume of chain 581

machine: data

Chain 581 was interrupted. First put this same text back in queue/next/ as the next number up to 589, named NNN-resume-chain-581.md, committed alone and pushed. Then read queue/done/581-evening-19-november-desktop-states-curtailment-map-layers.md whole and docs/state/progress_c581.md, and continue chain 581 from the first step not marked done, under that file's rules, with the next free session number in its range. Write no other queue file.
END

## Part A: the desk and the requests (the start of every session, and again after each numbered step)

As part A of chain 501, unchanged: every row marked requested in any `docs/state/landing_request_*.md` landed through the gate (never between 14:00 and 16:15 UTC), then every row marked requested in any `docs/state/data_requests_*.md`, in order of request.

## Part B: every state on one page (`/states`, new, in review)

1. **The files,** `site/data/states/<st>.json` for the fifty states and the District of Columbia, and `states/index.json`, their contract written first in `docs/state/page_files_states.md` with a real sample:
   - generation by source by month since 2001 (EIA-923), and the share of each source in the last twelve months;
   - sales and revenue by sector by month, and the average retail price by sector that follows from them (EIA-861M);
   - the ten largest plants, capacity by source, and what is planned to come and go by year (EIA-860 and 860M);
   - carbon dioxide from power by year, natural gas used and produced, and total energy by sector (the held state tables);
   - which balancing authorities and which of the seven grids serve it, from `eia_county_region`, by share of its people;
   - its large-load law where `state_large_load_laws` holds one, and its severance tax where the severance tool holds the state.
   Every figure with its table and vintage. A thing a source does not cover for a state is a null with the reason, never a zero.
2. **The page:** choose a state, or two side by side. What it runs on and how that changed since 2001; what its homes, businesses and industry buy and pay; what is built and what is coming; who operates its grid; its emissions. Charts that answer to the mouse, every figure sourced on hover, downloads as the other pages have them.
3. **Monthly is said plainly:** no public source gives a state's generation by the hour, and the page says so once, with a link to the state's balancing authorities in the Grid tool, where the hourly picture is.
4. To the done line in the form of `queue/done/303-night-16-november-portable-trackers-done-line.md`: method note, replication, a cross-check of five states against EIA's own state profiles, decisions block. A stop for it in the tour, held by its flag.

## Part C: where and when power is spare (`/curtailment`, a new view; the page as it is does not change)

1. **What exists first:** which operators' curtailment the warehouse holds, to what place (system, zone, node) and under what license; and the hours priced below zero that the price tables hold.
2. **The tables and the file:** for every operator that publishes curtailment under a license a page may show, the curtailed energy by hour, by source and by the finest place it publishes; beside it, for every hub and zone whose price a page may show, the hours below zero. Rolled up by hour of day, month and year. Page file in a contract first.
3. **The view,** "Where and when": a grid of hour of day against month for a chosen place, colored by curtailed energy or by the share of hours below zero; the places ranked; the trend by year; two places side by side. What it shows is where and when power went unused or unpaid. It gives no advice on where to put a load.

## Part D: the project map's missing layers (`/map`)

1. **What exists first:** the layers `/map` draws today and the tables behind them.
2. **The layers not there,** each from a public federal source, its robots and terms read first, each a table with its license, a method note and a web file under 2 MB: natural gas pipelines and their compressor stations; crude oil and product pipelines; LNG import and export terminals with their state (operating, under construction, approved); refineries with capacity; underground gas storage fields; electric transmission lines of 230 kV and above; power plants' substations where the source is public. A source that refuses is not read and is one plain line under "For Samuel's ruling", default "not pulled".
3. **On the map:** each a switch, off as the page opens, in the form of the switches it has; hover gives the name, the operator, the size and its unit, the state and the source.

## Part E: the price board's missing prices (`/board`)

1. **What exists first:** every row of the board and its table; then Samuel's list of 5 October read against it: refined products, coal, uranium, carbon and credits, battery and other materials, the cost of capital, more oil and gas (LNG, refining margins). US first; Brent kept; a series of Europe or Asia that is only monthly is left out; monthly is fine for uranium and battery metals.
2. **Each price the board lacks and a public source prints** under terms a page may show: a table, its license, its row on the board in the board's own form, with the mini-charts the other rows carry. A price only a paid or forbidding source prints is listed under "For Samuel's ruling" with the source and what it costs, default "not added". No row the board has today changes.

## Part F: storage and queues for the whole country

1. **`/storage`:** batteries by balancing authority and by state (EIA-860M: operating, planned, by year of start, power and energy), beside the seven grids' figures the page has. Any authority or state can be chosen, two side by side.
2. **`/queues`:** what the warehouse holds of interconnection queues outside the seven grids (the public queues of the western and southeastern utilities and authorities, where their terms allow), added by place; a place with no public queue is listed as such.

## Part G: after part F, until the weekly limit

- Each new view read as its reader (five real cases each, as part B of chain 304), every gap a numbered row, every fault fixed at its cause with a test.
- Every page file written today traced once more to its rows by `check-values`.
- Part A after each.

## The last session

- `docs/state/note_2026-11-19_data_c581.md` in short bullets: every landing with what a reader now sees; each new page and view with its address and what to click to see it; each table with its span, rows and license; what waits for Samuel with the default taken, in plain words.
- The resume file removed; `.venv\Scripts\python.exe scripts\chain_queue.py next`, and the file it prints run the same way. No file: part G goes on.

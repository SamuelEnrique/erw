# Chain of 17 November 2026: sessions 7800 to 7899, data machine (lab-desktop), unattended: the screenshots of the ruling alternatives, the warehouse widened from seven grids to all thirteen regions hour by hour, the filed large-load tariffs of the eighty entities

machine: data

Written by Claude in chat with Samuel on 17 November 2026 at about 13:30 PST and pasted by him into this session. It is not a machine's successor file, and no machine writes a successor to it. Folder: `C:\Users\Shared\Documents\erw`. Model: Opus 5.5, high effort. One Claude Code session.

## Why this chain

Overnight the laptops built the other choice of every ruling that moves a figure: 113 branches named `wip/alt-*`. Samuel rules on them this afternoon and tonight, and 87 of them have no screenshot, because the old laptop cannot build the site. He cannot rule well on what he cannot see, so the screenshots come first, largest change first. After that this machine does work that needs no ruling: the warehouse's hourly grid tables hold seven grids, and the Southeast, Florida, the Carolinas, Tennessee, the Northwest and the Southwest are missing; and the filed large-load tariffs cover only part of the eighty entities.

## Rules

- **The owner's rules of 16 November 2026 hold word for word** as written in `queue/done/301-day-16-november-desktop-open-faults.md` (its rules 1 to 10), with these changes:
- **Session numbers** 7800 to 7899, each checked free on origin/main and every branch first; a taken one is skipped upward and said so.
- **The data lock is never waited on**, as in `queue/done/370-day-16-november-desktop-requests-and-reads.md`.
- **No default moves.** A `wip/alt-*` branch is never landed, never merged and never requested for landing. Its builder's output is never loaded to the live set, to Supabase, to the Redivis draft or to main's page files. No figure on any page of production changes because of parts B or C.
- **The donor grids paper is Samuel's own work by hand with his coauthor.** This chain pulls and registers tables. It writes no estimate, no design, no analysis and no paper file.
- **New tables of part C are internal tier:** registered, validated, archived, in coverage, with a method note, read by no page and not in the live set. A public-licensed one may go on the Redivis draft as chain 370 did; nothing is released.
- **Rule 4's line against a session whose only output is a record does not apply to part B:** the screenshots are this chain's product.

## Restart safety and the progress file

- The first session writes `queue/next/410-resume-chain-401.md` (the block below, unchanged), committed alone and pushed, and removes any other `*-resume-chain-*` file of the data machine from `queue/next/`. A session that takes a resume file first writes the same block under the next number up (to 419). The chain's last session removes it.
- `docs/state/progress_c401.md`: one line a landing, request, row, table or utility, its state and session, pushed after each.

The resume file's text is the seven lines between BEGIN and END, without those two words:

BEGIN
# Resume of chain 401

machine: data

Chain 401 was interrupted. First put this same text back in queue/next/ as the next number up to 419, named NNN-resume-chain-401.md, committed alone and pushed. Then read queue/done/401-day-17-november-desktop-screenshots-regions-tariffs.md whole and docs/state/progress_c401.md, and continue chain 401 from the first step not marked done, under that file's rules, with the next free session number in its range. Write no other queue file.
END

## Part A: the desk and the requests (the start of every session, before anything else)

As part A of chain 370: land every row marked requested in `docs/state/landing_request_*.md` through the gate (never between 14:00 and 16:15 UTC), do every row marked requested in `docs/state/data_requests_*.md`, in order of request. Nothing requested: two lines of the report, then on.

## Part B: the screenshots of the ruling alternatives (87 rows on origin/main at 13:20 PST)

- **Which rows:** every row of `docs/state/browser_reads_wanted.md` in state `wanted`. All are `wip/alt-*` branches.
- **Order:** largest change first, by the change the row's line carries in its tool's `docs/reviews/ruling-alternatives-<tool>-2026-11-17.md`. Rows of one tool may be taken together where that saves a build.
- **How:** one worktree for the alternatives, as sessions 7620 to 7631 did on the portable laptop (`archive/sessions/SESSION_7620_REPORT.md` says how): a served build or a dev server, whichever shows the row's cell truly, read with the internal cookie in an isolated browser context.
- **A row that says a builder of the branch must run first:** run it into the worktree's own files only. If the builder can only write to the live set or a shared table, the row is not seen: state `not seen: needs the live set`, with the figure the branch's test pins.
- **Two pictures a row at 1280 px:** the changed cell with its label on the branch's build, saved to the path the row names; and the same cell on production (main's default), saved beside it as `<the same name>-default-1280.png`. Samuel reads them side by side.
- **The row's new state:** `seen (session N)` with the figure read on the build and the figure on production; or `fault` with what was seen instead. A fault is not fixed here: it is one line in the tool's ruling-alternatives file. A branch that does not build after ten minutes of trying is `fault: does not build`, with the error's first line.
- **Push** the two pictures and the row to main after each row (records, not code: no gate).
- Part C's downloads that need no lock may run in the background while part B builds. Neither waits on the other.

## Part C: the warehouse from seven grids to all thirteen regions, hour by hour (July 2018 to the newest hour)

Each table: its connector as the `erw-add-connector` skill has it, the source probed for robots and terms before any pull, validated, registered with its license, archived, coverage rebuilt, a method note under `docs/methods/`, landed through the gate. One table is one commit trail and one line of the progress file.

1. **`eia930_region_hourly`** (EIA-930 six-month files; EIA, public domain): for each of the thirteen regions of the lower 48 as EIA names them, and for every balancing authority: demand, demand forecast, net generation and total interchange, hourly, UTC. Where the file prints a reported value and EIA's adjusted value, both are kept, in their own columns.
2. **`eia930_ba_interchange_hourly`**: interchange between each pair of directly connected balancing authorities, hourly. Each side's report is its own row (who reported, about whom). Nothing is netted or averaged in this table.
3. **`eia930_region_pair_hourly`** (derived): the region pairs summed from table 2, each side's report in its own column, and the gap between them.
4. **`census_county_population`** (Census Bureau, public domain): county population, the 2020 count and the yearly estimates from 2018 on.
5. **`eia_county_region`** (derived from EIA-861's service territory and balancing authority files, which the warehouse holds): each county of the lower 48 to its balancing authority and its EIA region. A county served from more than one balancing authority is marked shared, with every one listed and one named as primary; the rule that picks the primary is written in the method note and under "Decisions made without you" with the other rule that was open.
6. **`noaa_isd_hourly` widened** (NOAA, public domain): for each region, its counties in order of population until 80 percent of the region's population is covered, at most 25 counties a region; for each, the nearest ISD station that holds at least 95 percent of the hours of each year. Stations already held are not pulled again. The station list with each station's county and weight is its own small table, `noaa_region_stations`.
7. **`region_weather_hourly`** (derived): each region's temperature by hour, weighted by county population, from tables 4 to 6.
8. **`iso_hub_prices_history_2018`**: day-ahead and real-time prices at the hubs `iso_hub_prices_history` already holds for CAISO, MISO, SPP, NYISO and ISO-NE, hourly, from July 2018 to 5 July 2023, from each operator's own archive. A new table, read by no page. Each archive's license flag is what `docs/licenses.md` holds for that publisher. A publisher whose terms forbid automated pulls, or that a hold of `docs/licenses.md` covers, is not pulled: one line under "For Samuel's ruling" in plain words, default "not pulled". PJM is not pulled.

## Part D: the filed large-load tariffs of the eighty entities (`utility_large_load_tariffs`, `docs/methods/large_load_tariffs.md`)

- **First the count:** which of the eighty entities (the `GROUPS` of the large-load statements connector) are utilities that file tariffs, and which of those have a registry file under `warehouse/sources/large_load_tariffs/` today. Written at the top of the progress file's part D.
- **Then one utility at a time**, those with the most rows in `large_load_public` first: the schedule or rider a load of 100 MW to 1 GW would take (where the utility files no large-load schedule, the largest transmission-level schedule, said so), read by this session itself from the commission's copy or the utility's filed tariff book (the owner's ruling 4 of 6 November 2026), every row with its printed words and page as the method note says. No script calls a model.
- **A host whose terms ask written permission:** `license: internal` in its registry file, its rows kept out of the table, as since session 3760.
- **After each utility:** the table rebuilt, validated, coverage rebuilt, `site/data/siting/tariffs.json` rebuilt by its builder, pushed. The All grids tab's wiring is not changed here.

## The last session

- `docs/state/note_2026-11-17_data_c401.md` in short bullets: the rows seen and the faults of part B with their counts; each table of part C with its span, rows and license; each utility of part D; what waits for Samuel with the default taken, in plain words.
- The resume file removed; `.venv\Scripts\python.exe scripts\chain_queue.py next`, and the file it prints run the same way. No file: say CHAIN DONE and stop.

# Chain of 19 November 2026: sessions 8000 to 8199, data machine (lab-desktop), first window, unattended, 24 hours and more: the whole country's page data, who trades with whom, the public layers for the resource map and energy by industry, and the landing desk for three other windows

machine: data

Written by Claude in chat with Samuel on 19 November 2026 at about 02:00 PST and pasted by him into this session. It is not a machine's successor file, and no machine writes a successor to it. Folder: `C:\Users\Shared\Documents\erw`. Model: Opus 5.5, high effort.

## Why this chain

The platform says it covers the whole US energy system, and its grid pages show seven grids. On 17 November chain 401 landed 27 tables that hold all thirteen regions and every balancing authority hour by hour since July 2018, and no page reads them. Three other windows build on them from tonight: the desktop's second window (chain 502, findings and the industry page), the old laptop (chain 503, the events, demand and supply pages) and the personal laptop (chain 504, the Grid tool's map). All three need page files that only this window can write, and all three need this window to land their code. Samuel has about 30 hours of this week's allowance left and cannot review before morning: nothing here waits on a ruling.

## Rules

- **The owner's rules of 16 November 2026 hold word for word** as written in `queue/done/301-day-16-november-desktop-open-faults.md` (its rules 1 to 10), with these changes:
- **Session numbers** 8000 to 8199, each checked free on origin/main and every branch first.
- **The data lock is never waited on**, as in `queue/done/370-day-16-november-desktop-requests-and-reads.md`.
- **A second window shares this machine** (chain 502, in `C:\Users\Shared\Documents\erw-w2`). This window never kills a process it did not start, never works in that folder, and every site build goes through `scripts/buildlock.py`.
- **This window is the only one that lands.** The landing desk reads every `docs/state/landing_request_*.md`, the second window's `landing_request_window2.md` among them.
- **Add, never change.** Every page file of this chain is a new file. No existing page file, table or figure of a page changes, and the snapshots around each landing show 0 differences on existing pages. Every page stays in review.
- **No default moves and no ruling is taken for Samuel.** No `wip/alt-*` branch is landed or merged.
- **The donor grids paper is Samuel's own work by hand.** The tables of part C are descriptive: sums, shares, ranks and each side's report. No regression, no estimate, no causal sentence, no paper file.
- **The others are never kept waiting.** Parts B1 and B2 come before anything else but the desk, because three windows code against them.

## Restart safety and the progress file

- The first session writes `queue/next/510-resume-chain-501.md`, committed alone and pushed, and removes any other `*-resume-chain-*` file of the data machine from `queue/next/`. Its text is the lines between BEGIN and END below, without those two words. A session that takes a resume file first writes the same text under the next number up (to 519). The chain's last session removes it.
- `docs/state/progress_c501.md`: one line a landing, request, file, table or layer, its state and session, pushed after each.

BEGIN
# Resume of chain 501

machine: data

Chain 501 was interrupted. First put this same text back in queue/next/ as the next number up to 519, named NNN-resume-chain-501.md, committed alone and pushed. Then read queue/done/501-day-19-november-desktop-whole-country-data.md whole and docs/state/progress_c501.md, and continue chain 501 from the first step not marked done, under that file's rules, with the next free session number in its range. Write no other queue file.
END

## Part A: the desk and the requests (the start of every session, and again after each numbered step of parts B to E)

As part A of chain 370: land every row marked requested in any `docs/state/landing_request_*.md` through the gate (never between 14:00 and 16:15 UTC), then do every row marked requested in any `docs/state/data_requests_*.md`, in order of request. After each landing, read the changed pages on production with the internal cookie at 1280 and 390 px and write in the report what a reader now sees. Nothing requested: two lines, then on.

## Part B: the whole country's page data (new files under `site/data/regions/`)

1. **The contract, before any file is built:** `docs/state/page_files_regions.md` on main. For each file of steps 2 to 7: its path, every key with its unit, and one real sample object. The measures and their names follow the existing files of the seven grids (`site/data/demand_growth.json`, `demand_weather.json`, `mix/*.json`, `supply.json`, `grid_network.json`) so the pages' components can read both. Pushed within this chain's first hour. A shape that later has to change is changed in this file first, with a dated line saying what moved.
2. **Balancing authority boundaries:** the federal Control Areas layer (HIFLD, public domain; robots and terms probed first), registered as `ba_boundaries`, each polygon keyed to its EIA-930 balancing authority code, and simplified for the web as `site/data/regions/ba_boundaries.json` (under 1.5 MB). An authority with no polygon, or a polygon with no authority, is listed in the method note. Landed before step 3.
3. **`index.json`:** the thirteen regions and every balancing authority: code, name, region, time zone, which of the seven grids it is or sits in, first and last hour held.
4. **`demand/<region>.json` and `demand/ba/<code>.json`:** daily demand and peak, growth by year, and demand with the weather taken out (from `eia930_region_hourly`, `eia930_ba_demand_hourly` and `region_weather_hourly`), by the same method as the seven grids' files. Where a region and one of the seven grids cover nearly the same ground and their figures differ, both stand, and the method note says why in one sentence.
5. **`mix/<region>.json`:** generation by source, hourly for the newest 35 days and monthly since July 2018 (from `eia930_ba_supply_hourly`), in the form of `site/data/mix/*.json`.
6. **`trade/<region>.json`:** each region's net imports by month and by neighbor, each side's report and the gap between them (from `eia930_region_pair_hourly`).
7. **`events/<event>.json` for the nine events of `/events`:** each region's hourly demand, generation by source and net interchange, and each region pair's flow, across the event's own window and across the baseline the event pages already use.
8. **The builders join the data machine's daily run** once landed, so the files stay current. Validated, tested, method notes under `docs/methods/`.

## Part C: who trades with whom (descriptive tables, internal tier unless the license record makes them public)

1. `interchange_pair_daily` and `interchange_pair_monthly`: every pair of balancing authorities and every pair of regions: each side's report, their mean, their gap, the direction.
2. `ba_trade_partners`: for each balancing authority and year, its partners ranked by gross and by net exchange, and its share of demand met by net imports.
3. `interchange_event_pairs`: for the nine events, each pair's total over the event's window beside the same calendar hours of the other years held.
4. One page file, `site/data/regions/trade_matrix.json`, in the contract of step B1.

## Part D: public layers for two tools Samuel asked for (each source's robots and terms probed first; a host that refuses is not read, and is one plain line under "For Samuel's ruling" with the default "not pulled")

1. **The natural resource map** (the resource in the ground, the sun and the wind, not built capacity; as fine as the source allows, county or grid cell): solar (NREL), wind (NREL), geothermal (USGS and NREL), hydropower potential (Oak Ridge), oil and gas basins and plays (EIA and USGS), coal fields (USGS and EIA), uranium (USGS and EIA), critical minerals (the held `usgs_mcs_critical_minerals` and USGS's deposit layers). Each layer: a table with its license, a method note, and a web file `site/data/resources/<layer>.json` under 2 MB, in a contract added to `docs/state/page_files_regions.md`.
2. **Energy use by industry:** from the held `eia_mecs_manufacturing`, `eia_sector_energy_consumption_monthly` and the SEDS tables, and what EIA publishes beyond them (industrial sales by state and month, the Annual Energy Outlook's industrial sub-sectors): energy by industry, by fuel and by state, monthly where the source is monthly. Page file `site/data/industry.json`, its contract in the same file. The second window builds the page.
3. **Energy per AI query, as published:** `ai_energy_published`: every figure a model maker, a cloud operator or a peer-reviewed paper has printed for the energy of a query, a token, a training run or a fleet, each row with its printed words, page, date and what it measures. No figure of the ERW's own, nothing summed or averaged across publishers, as the large-load pilot's rule has it (`docs/accelerator/large_load_pilot.md`). Read by this session itself; no script calls a model.

## Part E: the filed large-load tariffs, continued (part D of chain 401, its form unchanged)

The schedules chain 401's note lists as open (WEC's own site, SDG&E, PSEG, Colorado Springs Utilities, LADWP, Avista's Schedule 25) and pending (DTE, Tampa Electric, Otter Tail, Minnesota Power), then every utility of the eighty not yet tried, one at a time.

## The last session

- `docs/state/note_2026-11-19_data_c501.md` in short bullets: every landing with what a reader now sees; each file of part B and each table of parts C and D with its span, rows and license; each utility of part E; what waits for Samuel with the default taken, in plain words.
- The resume file removed; `.venv\Scripts\python.exe scripts\chain_queue.py next`, and the file it prints run the same way. No file: say CHAIN DONE and stop.

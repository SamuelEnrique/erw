# Progress of chain 501 (19 November 2026, lab-desktop, data machine, first window)

The chain: `queue/done/501-day-19-november-desktop-whole-country-data.md`. One line a landing, request, file, table or layer, with its state and session. A restarted session continues from the first line not marked done.

## Ground

| Part | Item | What | State | Session |
|---|---|---|---|---|
| ground | chain file | saved as pasted (`79e403523`) | done | 8000 |
| ground | resume file | `queue/next/510-resume-chain-501.md` (`645a3e185`); no other resume file of the data machine was in `queue/next/` | done | 8000 |
| ground | precheck | passed, on duty for "session 8000" | done | 8000 |

## Part A: the desk and the requests

| Part | Item | What | State | Session |
|---|---|---|---|---|
| A | landing requests | `landing_request_desktop_w3`, `_w4`, `_oldlaptop`, `_portable` on origin/main at 10:30 UTC: no row whose state begins "requested" (`runs/c501/desk_scan.py`); no `landing_request_window2.md` yet | nothing requested | 8000 |
| A | data requests | five rows still read "requested", none new: five_tools 2 (ruling on six tests, default off), five_tools 5 (done before chain 401), forecast 5 (comptroller.texas.gov robots refuses), licenses 11 and 12 (api.bls.gov robots disallows every path) | standing, not new | 8000 |

## Part B: the whole country's page data

| Part | Item | What | State | Session |
|---|---|---|---|---|
| B1 | contract | `docs/state/page_files_regions.md` (`733e7d3d5`, 10:30 UTC) | done | 8000 |
| B2 | ba_boundaries | HIFLD Control Areas from PASDA (71 polygons, 67 keyed through EIA-861 BA IDs), table 71 rows validated and archived, web file 979,100 bytes; DataLumos not read (robots name ClaudeBot), NASA mirror unreachable; branch `wip/c501-data` at `23760f290`, gate passed; landed `792dbb50d` | done | 8000 |
| B2 | landing | `wip/c501-data` at `23760f290` gated (every step passed), landed as `792dbb50d` (run 44513172752); snapshots `c501-b2-before` and `c501-b2-after`: 0 differences; `/data/methods/ba_boundaries` read on production at 1280 and 390 px | done | 8000 |
| B3 | index.json | 13 regions, 72 lower-48 authorities and the Canadian and Mexican ones (request 324); on `wip/c501-pages` | built, gating | 8001 |
| B4 | demand files | 13 region files (sum of demand-filing authorities, weather fit from `region_weather_hourly`) and 58 authority files, about 17 MB; the four pairs alike with the seven grids equal in every whole year | built, gating | 8001 |
| B5 | mix files | 13 files from the new table `eia930_region_fuel_hourly` (6,282,393 rows, validated, archived); Texas equals `mix/ercot.json` to the hundredth of a percent | built, gating | 8001 |
| B6 | trade files | 13 files from `eia930_region_pair_hourly`; agree with `trade_matrix.json` exactly | built, gating | 8001 |
| B7 | event files | 9 files, 360 KB to 3.6 MB | built, gating | 8001 |
| C1 | interchange_pair_daily, _monthly | 552,751 and 18,284 rows, validated, archived | built, gating | 8002 |
| C2 | ba_trade_partners | 5,987 rows | built, gating | 8002 |
| C3 | interchange_event_pairs | 13,574 rows | built, gating | 8002 |
| C4 | trade_matrix.json | 452 KB, `months_held` and names across the border (requests 324, 325) | built, gating | 8002 |
| D2 | industry | tables `eia_seds_industrial_annual` (30,940 rows) and `eia_aeo_industrial` (75,504), `site/data/industry.json` (1.1 MB), contract section 9 | built, gating | 8003 |
| A | data requests 323 to 327 | contract lines under "Changes" (`ce22c9265`); keys added in the builders | done | 8004 |
| A | landing desk | oldlaptop rows 51, 52, 53, portable row 41, window2 rows 1 and 2 stacked with `wip/c501-pages` as `wip/c501-desk-a`: the first gate (`e849f072e`) failed two tests (test 147: `pages.py` in a method note, the builder renamed `region_files.py`; test 5171: two new readers of `data/regions/` listed); newer heads of rows 52, 41 and 2 and the new portable row 42 merged; gate again at `22cb29294` from 12:41 UTC | gating | 8004 |
| D3 | ai_energy_published | 21 figures from 7 publications (Google, OpenAI, Patterson and others twice, Luccioni and others, BLOOM, Strubell and others), each cut from its saved copy and checked at every build; validated; on `wip/c501-more` | built | 8005 |
| D1 | resource_layer_features | 1,371,628 rows (Decision 81), and `site/data/resources/coal_fields.json` (USGS OFR 2012-1205, 602 polygons, 544,878 bytes); uranium and critical-mineral deposits not pulled (mrdata.usgs.gov disallows every path; ScienceBase disallows Claude by name); on `wip/c501-more` | built | 8006 |
| B8 | daily run | `warehouse/run_data_machine.sh` section 1f: the two newest six-month files of each kind asked again, the region, interchange and fuel tables rebuilt and stored without Redivis, the page builders, a test group; on `wip/c501-more` | built | 8008 |
| E | Avista Schedule 25 | read from myavista.com, file written; table rebuilt (86 rows, 21 utilities), `tariffs.json` gains only Avista; on `wip/c501-more` | built | 8007 |
| E | PSEG, Colorado Springs Utilities, We Energies, SDG&E | terms read: PSEG forbids crawling and automated means; CSU personal and noncommercial only; We Energies no reuse without written consent; SDG&E personal, internal, noncommercial only; schedules not read | held by terms | 8007 |
| E | LADWP | its Terms & Conditions page renders by script (empty without it) | open | 8007 |
| E | DTE, Tampa Electric, Otter Tail, Minnesota Power | no order found since chain 401 (DTE: michigan.gov refuses this reader; Minnesota Power on the agenda of 24 November) | pending | 8007 |
| A | data requests 328, 329, 542, 543 | 328 (a record's partial first and last days), 329 (which demand, no hour moved, alike on the seven grids' authority files) and 542 (the coal fields in the map's layer form and `manifest_added.json`) done on `wip/c501-desk-b`; 543 answered (the daily runs succeed; the load step's reason left for a data-jobs session) | done | 8009 |
| B5 | mix files, again | `eia930_region_fuel_hourly` by the region's rule (6,730,507 rows): the Mid-Atlantic 40 to 95 months, the Southwest 36 to 85, California 61 to 98, the Northwest 49 to 70; Texas still equals ERCOT; on `wip/c501-desk-b` | built | 8009 |
| D3 | ai_energy_published | 23 figures from 9 publications (Meta's 2025 data index, Microsoft's 2026 fact sheet added); Google's reports not read (www.gstatic.com disallows the folder) | built | 8009 |
| A | landing desk | `wip/c501-desk-b` (`wip/c501-more` with portable rows 42 at `0211e5b36` and 43 at `f1ae0dffc` and window2 row 2 at `42e88f11a`), merged without conflict, the related tests pass; gate after the blackout (16:15 UTC) | waiting for 16:15 UTC | 8009 |
| A | data requests 544 to 550 | 545 (each side's report beside an event pair's flow) and 546 (the weather's coverage by year) done on `wip/c501-desk-c`; 544, 547, 548, 550 answered from EIA's files (Seminole's zero hours, SRP's 14:00 spikes inside the screen, PJM's unfiled CPLW hours); 549 in part | done | 8010 |
| A | data request 543 | the cause: test 7014 under `health.py` stopped the daily run on 18 November; fixed on `wip/c501-desk-b` | done, landing | 8009 |
| A | landing desk | `wip/c501-desk-c` (`f640a8dbf`): `wip/c501-more` with portable rows 42 and 43, window2 row 2, data requests 328, 329, 542, 543, 545, 546, the region's mix rule; the first gate of desk-b failed test 8603 (the portable's check of layer files, now counting `manifest_added.json`); gate again from 14:26 UTC; the push waits for 16:15 UTC (the hours with no landing) | gating | 8010 |
| A | landing desk | `wip/c501-desk-d` (`d40518884`: desk-c with data request 551 and the portable's row 42 at `e97d4614a`): every step of the gate passed (the suite 10,324 tests OK); the push to `task/c501-desk-d` waits for 16:15 UTC, the end of the hours with no landing | gated | 8011 |
| A | data request 551 | sources never printed drawn blank (`sources_not_printed`); the four hours apart from EIA's API are the files' vintage, which the daily step follows | done, landing | 8011 |
| A | the desk at 15:44 UTC | no new data request; the portable laptop moved rows 42 and 43 to `eb6bb737c` and `37001e69b` after stack d was gated (it holds `e97d4614a` and `f1ae0dffc`): those rows stay requested for the next stack | noted | 8011 |
| A | landing desk | stack d pushed to `task/c501-desk-d` at 16:16 UTC (snapshot `c501-deskd-before`, 25 pages); stack e (`wip/c501-desk-e`, `a78cf7fbd`): stack d with the portable rows 42 and 43 at `eb6bb737c` and `37001e69b` (test 8603: the portable's version, which accepts the coal layer by its source and sha256; the region tabs' replication reads the null sources of request 551); its first gate stopped at main_merged; the heads moved again at 16:13 UTC, to merge after stack d lands | stacking | 8011 |
| A | landing desk | stack d landed at `d89580bd3` (16:44 UTC; snapshots `c501-deskd-before` and `c501-deskd-after`: 0 differences); read on production at 1280 and 390 px: /resources (the coal fields still "not held": the page there reads manifest.json only; the portable's newer head reads manifest_added.json), /grid?view=regions, /demand?view=country, /events/uri-2021; window 2 row 2 marked landed | done | 8011 |
| A | data request 552 | the coal fields' area in square miles with AREA_KM2 beside it, the entry's note without the file name; stack e (`d3a799836`, with the portable's rows 42 and 43 at `43863e85d` and `180880ef6`) gating from 16:53 UTC | gating | 8011 |
| E | the eighty, the untried | every one of the eighty was tried by chain 401 (its part D table); the open ones are held by terms or access controls (FirstEnergy, CMS and FPL by terms; Duquesne, Alliant, Cleco and TVA by bot checks; Big Rivers and East Kentucky by the Kentucky PSC's robots); JEA asked again: www.jea.com and jea.com still give no connection (19 November, about 16:53 UTC); nothing new to write | tried | 8011 |

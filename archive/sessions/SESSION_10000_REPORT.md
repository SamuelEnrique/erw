# Session 10000 report (chain 701, the first session; lab-desktop, data machine, first window)

Chain: `queue/done/701-night-26-november-desktop-repairs-equities-large-load.md`. Progress, line by line: `docs/state/progress_c701.md`. Started 10:49 UTC on 26 November 2026. Model spend USD 0: no model API was called. Two research agents (Claude Code subagents, no API) read large-load documents through the research reader; their quotes were matched by `verify_quotes.py` and two read again by me.

## What a reader now sees (after landings 1 and 2)

- The daily load into Supabase no longer fails every day: it says "held" for the three model-extracted tables Supabase holds newer rows of and for the stale source name only a person prunes (C1).
- The data machine's push is no longer refused by test 8613 (C3), so its page files (the board, the regions, the battery downloads) reach main again from its next run; the live-set load builds its own coverage rows first (C4); the package test holds what it means (C5); the storage awards build before the offers (C6).
- The price board's file holds no figure of NYISO, ISO-NE or MISO any more: 20 week lines, 20 spikes and 94 rows with values (and their 94 series files) had stayed in the public repository from before the hold of 20 October (data requests 12 and 13 of the board audit). The board rebuilt from the data machine's tables: ERCOT's hub average day-ahead at 25 November (46.31), where main's file read 20 November (16.18).
- New tables: `census_cbp_construction_annual` (public), `datacenter_announced` (internal, model-extracted), `weather_forecast_issued_hourly` (public; every NWS forecast issue kept from 26 November; the runner now restores rolling tables the archive holds).
- The equities files by their contract (`site/data/equities/`): the equity side held with its reason (SEC EDGAR refuses the ERW's contact string; no free share price may be kept), eight energy prices shown from 2016, four held.
- 35 of the old laptop's audit fixes, window B's forecast code with its daily step, window C's impact row 14, window F's three fixes.

## Repairs: cause in one line, figure before and after

- C1, the load: the older-than-live guard refused datacenter_projects, energy_deals and news_index (Supabase holds 2, 7 and 400 rows loaded 13 November that no copy holds; rebuilt only with a model call) and sources (one stale name). Before: `supabase_load failed` every day from 21 November; after: `skipped: held: ...` with the other tables loaded.
- C2, the battery files: the runner builds `battery_stack_monthly` without ERCOT's history, and its rolling table lacks 15 October 2026, so October held 29 days against the downloads' 30. Built here from the history: October 30 days. The public file's last twelve months: 2025-10 to 2026-09, USD 81.40 per kW, before; 2025-11 to 2026-10, USD 80.40, after (lands at gate 6 with the replication, the note, the packs and the do-files).
- C3, the refused push: test 8613 skipped only on exit 0; the region files' rebuild moves the index's stamp (exit 2, other words).
- C4, dm_live_set: this machine's coverage row (ercot_rtm_price_adders, 603,156 against 603,492 rows) came back from main each morning while its push was refused.
- C5, the package test: coverage.csv and coverage.md carried the ERCOT history apart (3,124,224 against 3,125,376 rows).
- C6, ercot_storage_dam: the offers built after a failed awards build.
- C7, the hourly network 3.4 to 4.1 hours old each morning: it skips while the daily prices run (about 3 hours); a threshold for Samuel.

## Snapshots

- Part B push: `c701-B-before` and `c701-B-after`, 0 differences in 25 pages (expected).
- The battery table's load into the live set: `c701-bs-before` and `c701-bs-after`, 0 differences (expected).
- Landing 1 (`3dcb86434`): `c701-L1-before` and `c701-L1-after`, 0 differences (expected: every page is in review).
- Landing 2 (`f00acbd70`, 14:16 UTC): `c701-L2-before` (13:41) and `c701-L2-after` (14:23), 0 differences (expected: every page is in review).
- The desk's doc pushes from 14:23 to 14:40: `c701-L2-after` and `c701-p9-after`, 0 differences (expected).
- Landing 3 (`693a4a3f5`, 17:13 UTC): `c701-L3-before` (16:36) and `c701-L3-after` (17:19), 0 differences (expected). Doc pushes to 17:27: `c701-p10-after`, 0 differences.
- Gate 7 pushed 18:08 with `c701-L4-before`; its after snapshot: the progress file.
- The progress pushes: pairs `c701-p4` to `c701-p8`, 0 differences each.
- Landings 4 to 9 (`b80148122`, `4e6a7039c`, `66d07052c`, `fbb6012b6`, `052ebaa97`, `80d767b07`): pairs `c701-L4` to `c701-L9`, 0 differences each (expected: every page is in review).
- The daily run's replayed commit (`26b00d06b`): `c701-dm-before` and `c701-dm-after`, 0 differences. The records of the tables written at 21:57: `c701-rec`, 0. The company pages: `c701-co`, 0. Request 57: `c701-r57`, 0.
- **Not as the rule asks:** three doc pushes between 22:13 and 22:30 went without a before snapshot of their own; a snapshot after them (`c701-docs-2230`) against the last one before (`c701-co-after`) showed 0 differences. From 22:39 every doc push has its pair (`c701-doc2325-after`, `c701-doc0020-after`: 0).
- **Not as it should be:** at 06:44 UTC on 27 November a doc commit (`3085d3947`) carried conflict markers in `landing_request_desktop_w3.md` for about a minute: my command went on after its first merge of main failed (chain 740 had marked the same row landed). Fixed in `dac6a9a58` (their row kept); the doc commands now stop when that merge fails. Snapshots across both pushes: 0 differences.

## The desk in the afternoon

- Window D's data rows 7, 12, 13, 18 to 25, 28 to 37, 39, 40, 42 to 45 answered from this machine's tables and saved files (each with its script and output in `docs/reviews/answers-c701-2026-11-26/`); 26 and 27 built for gate 6; 14 waits on chain 720's board group; 38 is window B's; 41 taken (BLS refuses automated reads; the deflator is held; STEO's CPI-U queued).
- Built for the gates: JEDI's coal and CSP trough models (window C's request 8), the datacenter tax rules in `impact_tax_rules` (request 9), the week-ahead forecast step and ERCOT's forecast posting time (predict 6 and 5 in part), four large-load laws in force, the research reader's redirect check.
- Old laptop's row 114 returned to its window (it conflicts in substance with window F's `/conditions` fix now on main); row 115's node tests given the usual guard.

## Decisions made without you

- The equities contract and example files went to main directly (docs and unread data files), with a snapshot pair, so window E had them in the first hour; the first two pushes (queue move, resume file) touched no site file and went without one.
- C1 is a hold, not a fix of the data: the guard stands; the stale source is left for a person's prune.
- C2: the data machine builds the battery stack itself before its downloads (2 minutes), and the runner's existing keep_fuller keeps its fuller months.
- `datacenter_announced` is internal: its rows quote the documents, and session 255's rule makes public only facts with a link.
- The equities builder is named `equity_page_files.py` (test 147 keeps `pages.py` out of method notes).
- The large-load changes after 13 November (Rhode Island's order of 20 November, two procedural orders) are kept in the research files and not loaded: window D's policy fix words the page "in the 90 days to 13 November 2026".
- Window E's rows 54 and 55 (`/forecast`, `/equities`) were held back from gates 3 and 5 for two tests' lists; they returned on new heads and are in gate 6.
- 19 of this window's old worktrees whose branches are in main were removed when drive C fell under 20 GB (their ignored files listed in `runs/c701/wt_ignored/`, any `runs/` content kept in `runs/wt_saved/`); drive C went from 19.5 to 46 GB free.

- The daily run's unpushed commit was replayed on main by the code now on main: the held grids' seller files left out, the forecast files as main had them, the rest as the run wrote them (its original kept on `wip/dm-2026-11-26-unpushed`, the main checkout's old head on `backup-main-1fb1124f9`).
- The states' twelve-month window ends at the newest month with sales, not of prices (the chart's months unchanged).
- Request 57's eight tables were built in trial folders of hard links to the warehouse (writers rename temporary files, so the warehouse's files are never opened for writing); the screen's effect is reported, nothing loaded.
- The forecast ledgers' tables follow data request 2's shape; for the price, where places share a hub, the entity is the place's EIA-930 code and the hub is in `market` and `node`. Each table is the whole ledger, rewritten from it each day; the daily step writes no Redivis draft (this session wrote the first by hand). The backtests and scores are not written as tables: the validator refuses them as they are.
- Check-values floors (10 each, the file's rule) added for this chain's pages only: `/equities`, `/forecast` (two addresses) and the large-load row view.
- The equities ground read again changes nothing: Nasdaq, S&P DJI and the NYSE are closed by their terms or robots files.

- Tonight's failed steps were each read and the four with a cause in this repository repaired on branches through the gate: `health.py`'s echo (the live set's load died on an en dash), the free energy test (asserted no ERCOT month), `sync.py`'s rule for tables with no time column (compared by rows alone), and the stale 860M planned table restored from the archive by hand. The signature pack's test and EIA's 504s were left.
- `sync.py`: a table with no time column is compared by `retrieved_at` and the later retrieval decides; checked report-only on the 72 such tables first (11 behind, 1 ahead, none diverged).

- Samuel's SEC contact address is kept in the data machine's `.env` (`SEC_USER_AGENT`, the SEC's form "a name and a contact address") and read by the connector, not written into the repository, which is public: it is still the connector's contact string, as ruled.
- The universe's written rule was fixed before any company was placed, by reading the companies each draft code holds: 3690 (Energizer, a flight simulator maker), 2810 (titanium pigments) and 3511 (every turbine) were dropped; 3674 (every semiconductor) was never used. Six segments hold no company, each with its reason; Cheniere and the LNG exporters (SIC 4924) sit in midstream and regulated utilities with the note.
- The SEC's industry codes came from its nightly bulk file of submissions (one request, 1.6 GB) rather than about 6,000 single requests; daily, only a listed company new to the cache is asked for, and a company's facts only when EDGAR's daily form index shows a new 10-Q or 10-K.
- The license record holds one page a publisher (test 205): the SEC's privacy and security policy (read 2062, the deciding sentence); the access page is named in the verdict's note.
- A fact whose period ends after its filing date is left out as a tagging error (one: a May 10-Q reporting a year to 31 December 2026).

- Predict row 9 said reaching EIA-930 back to 2015 "may be Samuel's word": his order of 27 November for longer backtests (relayed by chain 730) was taken as that word, the files being public, allowed by EIA's robots file and small (five of about 31 MB). `eia930_all_history` now holds July 2015 to June 2018 for 66 authorities with the forecast.
- `eia930_ba_wind_solar_hourly` (predict row 10) is a table of its own, held out of the live catalogue and release v1 like the other EIA-930 hour tables, and not on Redivis (about 1.2 GB); `eia930_all_history`'s Redivis draft is behind for the same reason (about 1 GB). Uploads that long would outlast the foreground limit, and a background upload is what my notes warn against.
- Joint filings (done-line 579): a co-registrant's file is read only when it names the same entity, after the first run credited Southern Company's figures to a Georgia Power security; six utilities therefore still stop at March 2026.
- The live set took `nlr_jedi_multipliers` and `impact_tax_rules` by hand: no step loads a table written by hand here.
- Several landings combined rows of other windows into one gate; a gate taking an older commit was stopped and restarted with the newest heads (gates 19, 20 and 25), each time its own processes only, its build lock released.

## For Samuel's ruling

- The SEC refuses the ERW's contact string: give a contact address for the SEC's user agent and EDGAR opens part D (companies, share counts, statements). Default: not pulled. **Ruled by Samuel on 26 November** (the address given, kept in .env): done on 27 November, part D's public half (the universe, the statements, the page files).
- No free source of daily share prices or index levels may be kept (Stooq, Nasdaq, Tiingo, Alpha Vantage, State Street). Default: prices blank with "license needed".
- The signature pack of 14 November quotes figures each refresh moves, so every refresh of the datacenter files is put back (they stand at 12 November). Default: left as it is; the battery section was written again for the new window.
- The hourly network's allowed staleness (3 hours) against a daily run of about 3 hours during which it skips. Default: left as it is.
- The stale source "IEA" with an en dash in Supabase: prune it (`load.py --prune`). Default: left; the load says held.
- `datacenter_announced`: may the facts alone (values, measures, addresses) be a public selection? Default: internal.
- The large-load changes after 13 November wait until the policy page words its window from the data. Default: not loaded.
- pge.com: its Terms of Use bar bots and spiders copying information for another site without PG&E's authorization, yet pge.com is not on the research reader's barred list and site/data/bill_rules.json already cites pge.com tariff sheets (found by data request 53). Default: the reader stopped at pge.com; nothing changed in the bill rules.
- A news story dated after its retrieval (event listings, a feed whose stamps run ahead: 7 of 29,177): skip and count it in the ingest, as an undated one is? Default: left as it is.
- Held grids' prices in git's history: NYISO's and ISO-NE's hourly prices written before the hold (the seller's year files, the board's hourly files, the network files' hub prices) stay in the public repository's history after gate 9 removes them from what the site serves. Default: left in the history (rewriting it is a person's act).
- MISO's files under its pause: held for a license as well, but its pause keeps its tables and pages as they are, so its gallery charts (48) and network hub prices stay. Default: left until a person lifts or rules on the pause.
- FERC's EQR for 2026 Q3 is posted (4,070 filings, 3.97 GB); the contracts table holds 2026 Q2 by session 83's approved pull. Default: not pulled until the owner says so (the table stays internal until a person reads FERC's license statement).
- The forecast's backtests and scores as tables (`predict_demand_backtest`, `predict_scores`, `predict_price_backtest`): the two regressions share every place, hour and making time, and places of one grid share a hub, so the key needs the method (in the variable, say `demand_forecast_mw_regression`) or the place in the entity; the scores need a series shape. Default: left as files until the method chooses.
- Nineteen addresses of other chains carry checked figures but no check-values floor: `/datacenters?view=grids`, `/attention`, `/data/licenses`, `/policy?view=monitor&state=MD`, `/play/ev`, six `/learn/problems/...` pages, the two `/congestion` addresses, three `/conditions` addresses, two digests (`/digest/2026-11-12`, `/digest/2026-11-06`), and `/policy?view=week` (0 figures). Default: left to their chains.
- EIA's STEO route answered 504 six times from 15:40 to 23:56 UTC (even for three months), so the consumer price index (window D's row 41) waits. Default: tried again by the next session.
- The news tables on the data machine: each evening `dm_sync` restores `news_stories`, `energy_deals`, `datacenter_projects` and their evidence from the archive (newer than git's copy), and the run's commit step then stashes them back to git's copy, because these tables are tracked and the commit does not take them (26 November: "set aside in a stash before the pull"). The machine's copies stay at git's. Default: left; the owner of the news tables decides whether the data machine commits them or sync skips them.
- `attention_index_weekly`: the archive's copy (1,775 rows to 9 November) is behind Redivis's draft (1,785 rows to 30 November), so the restore from the archive leaves it behind every evening. Default: left for the archive's owner.
- GitHub's daily run of 26 November (14:00 to 17:23 UTC) could not push its records: 11 tests failed at 17:10 on its merge with main. Cause: it checked out main at 14:00, landing 2 (pushed just after its 13:41 snapshot, merged by its workflow at 14:16: inside the 14:00 to 16:15 window the chain file keeps clear of pushes, which a push before 14:00 does not guarantee) merged with two new tables (`census_cbp_construction_annual`, `weather_forecast_issued_hourly`) in the registry and the price board's held-grid code, and the run's coverage and board files, built from the 14:00 checkout, disagreed with them (tests 378, 410, 489, 275, 664, 3298, 505, 1008, 132 and 1139). Main's coverage holds both tables now, so the next run starts consistent; nothing changed. The same race as on 16 November: landing during the daily run's hours costs that day's push.
- The same run's Redivis upload refused `price_board_peak_offpeak`: 5,427 rows would shrink it below the 5,436 last uploaded. MISO's rows leave the rolling window each day since its pause (387 rows here), so on a day the other grids add fewer, the table shrinks. Default: the guard stands; `--allow-shrink price_board_peak_offpeak` is a person's call.
- The six equity segments no SEC industry code holds alone (LNG, nuclear and uranium, solar, wind, storage, hydrogen and fuel cells) are empty: filling them needs a named list of companies, which is judgment. Default: empty, each with its reason.
- Share prices and index levels stay blank (no paid or licensed source, as ruled); so the segment lines, the market values and the board's equities rows stay held.
- Two large EIA-930 tables are not on Redivis: `eia930_ba_wind_solar_hourly` (new) and the rewritten `eia930_all_history` (its draft holds the old 60,000 rows). Default: held out of release v1 like the other EIA-930 hour tables; an upload of `eia930_all_history` by a session that can run it in the foreground.
- EIA's API answered HTTP 504 from 26 November (STEO, the sub-regions, total interchange, nuclear outages): the consumer price index (window D's row 41), the sub-region demand of 2026 (predict row 14) and the daily refresh of those tables wait. Default: tried again by the next session; the sub-region step is in the daily run from the next landing.

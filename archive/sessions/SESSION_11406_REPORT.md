# Session 11406 report (chain 770, part C, old laptop): rulings readied as branches, weekend page lines 131 to 163

Energy Research Warehouse (ERW), 28 November 2026, 11:18 to about 14:30 UTC. Worktree `../erw-c770-f`. Brief: `runs/c770/brief_partC.md` and `runs/c770/brief_common.md`. Lines: `docs/reviews/weekend-2026-11-28.md` on origin/main at 604c1fd66, part 3.3, from "What a datacenter pays" to "The signature explorers".

Nothing here is requested: no landing file, data request file or progress file was written. Every branch is cut from origin/main of 28 November (bb764814a or the main of its hour), holds the change and a test `tests/test_ready_<name>.py` that passes on it, and was run with every test file that imports the module it changes (a failure that also fails on main is named). Model spend USD 0. No table written, no data lock, no build, no browser.

## The items, page line by page line

| Line | Item | Branch | Head | Before | After | Test |
|---|---|---|---|---|---|---|
| 132 | datacenter: prices rise 2 percent a year | `wip/ready-datacenter-inflation` | 31f2bfc06 | PV, 100 MW, default case USD 261.19 million; fixed price 34.07; all-in GPU-hour 0.0691 | 299.42 million (+14.6 percent); 39.06; 0.0792 | `test_ready_datacenter_inflation.py` |
| 133 | datacenter: GPU at 1.275 kW | `wip/ready-datacenter-gpu` | 036e27c04 | GPU-hour 0.0691 (today's files); 49,310 GPUs for 100 MW | 0.0678 (-1.9 percent); 50,277 | `test_ready_datacenter_gpu.py` |
| 133 | datacenter: overhead ratio 1.09 | `wip/ready-datacenter-pue` | dc3f88ea6 | GPU-hour 0.0691; 49,310 GPUs | 0.0483 (-30.1 percent); 70,572 | `test_ready_datacenter_pue.py` |
| 134 | datacenter: California at the load's point | none | | | | cannot be readied here (below) |
| 137 | analysis: say the count, or correct | count: in `wip/ready-analysis-statistics` | 490a0b783 | no draft says how many claims its run tested | each deep draft's footnote: "This hunt tested N claims and M passed its tests" and its q-value | see line 140; "correct for it": a blank, needs Samuel's word (which test against chance) |
| 138 | analysis: tight hours by demand | `wip/ready-analysis-tight-demand` | 5cb6765c2 | synthetic grid, solar share of capacity at capacity 5/20/40/60 percent of peak: 43.5, 19.2, 6.3, 3.2 | 55.6 at every capacity; the table (draft 3: ERCOT 71.1 to 5.0) moves at its rebuild | `test_ready_analysis_tight_demand.py` |
| 139 | analysis: cheapest hour, circular mean | `wip/ready-analysis-circular` | 9d436ae8a | HB_NORTH 2015 6.04, 2025 10.67 (audit a3) | 2.54 and 10.59; synthetic 23:00/01:00 days 12.0 to 0.0 | `test_ready_analysis_circular.py` |
| 140 | analysis: statistics block on deep drafts | `wip/ready-analysis-statistics` | 490a0b783 | no flag, no round | 12 of 37 yearly claims flagged "a step" (audit), at their next build | `test_ready_analysis_statistics.py` |
| 141 | analysis: floor of eight full years | `wip/ready-analysis-years` | fca65e83c | four rising points pass | fail ("enough full years"); 9 of the forty drafts under eight years (audit) | `test_ready_analysis_years.py` |
| 142 | analysis: caption "largest of N" | `wip/ready-analysis-caption` | 08826c6f2 | caption reads as one measure's rank | third sentence "It was picked as the largest of 21 measures' moves this week..." (W44: 21) | `test_ready_analysis_caption.py` |
| 143 | analysis: scanner's chance count | `wip/ready-analysis-chance` | c19ab403e | not said | scan summary `flags_expected_by_chance`: 4.5, 29.5, 36.3 for 6,797 series | `test_ready_analysis_chance.py` |
| 144 | analysis: lags and weekly clusters | `wip/ready-analysis-errors` | 8a5a54cbd | impact p one verdict at 3 lags (0.0704); hourly SE by day 0.0101 | p by lag 0 to 7: 0.0055 to 0.0762; SE by week 0.0166 (x1.64) | `test_ready_analysis_errors.py` (NOT CLEAN, below) |
| 147 | grid: one netting rule | `wip/ready-grid-netting` | d2dcfbd6d | snapshot: first BA's report | mean of both; median hour MISO 451 MW, PJM 503, CAISO 258 (audit) | `test_ready_grid_netting.py` |
| 148 | grid: own report first | none | | | | not readied (below) |
| 149 | grid: screen implausible reports | `wip/ready-grid-screen` | 78a2af7c7 | no screen | reports over 20,000 MW set aside; no figure moves in the seven weeks (2 reports, neither read) | `test_ready_grid_screen.py` |
| 151 | board: append newer points | none | | | | not readied (below) |
| 153 | trader: read SPP's real time | `wip/ready-trader-spp-rt` | 62a75e3c5 | SPP week RT less DA blank | board of 25 Nov: SPP North -3.73, South -3.66; board of 28 Nov: -3.17, -5.95 | `test_ready_trader_spp_rt.py` |
| 154 | trader: gas of the trading day before | `wip/ready-trader-gasday` | 39554c5de | gas dated on the operating day, up to 4 days older | ERCOT hub average, 354 days to 27 Nov: 0.313 MMBtu/MWh mean move, at most 4.86, 64 days over 0.5; 3 newest days lose a heat rate | `test_ready_trader_gasday.py` |
| 155 | trader: off-peak week by hours | `wip/ready-trader-offpeak` | 7108fbdfe | board of 25 Nov: SP15 42.72, NP15 57.22, SPP North 19.08; board of 28 Nov: 41.08, 53.57, 24.70 | 39.36, 58.74, 16.61; 36.95, 54.42, 21.35 | `test_ready_trader_offpeak.py` |
| 157 | small: confirmation by a button | `wip/ready-subscribe-confirm` | 1088448bd | a GET of the link confirms | the link opens /subscribe, a POST from the page confirms | `test_ready_subscribe_confirm.py` |
| 157 | small: where a reader asks for removal | none | | | | a blank: needs Samuel's word (an address or a form) |
| 157 | small: unsubscribe form, well-formed address only | `wip/ready-subscribe-address` | 60dab14bc | any text drawn | form only for the route's address form, 254 characters at most | `test_ready_subscribe_address.py` |
| 157 | small: /about's story count | `wip/ready-attention-count` | f36dfc4ac | 27,419 | 27,417 (percent 29.6 unchanged) | `test_ready_attention_count.py` |
| 158 | home: Digest block reads the new form | `wip/ready-home-digest` | a9032b7c9 | "no data" | 5 stories | `test_ready_home_digest.py` |
| 158 | home: held grid's strip, no unit or time | `wip/ready-home-held-strip` | 179ea4f89 | 3 units, 3 interval times drawn | 0 and 0 | `test_ready_home_held_strip.py` |
| 158 | home: hide unconfirmed Thesis sentences | `wip/ready-thesis-unconfirmed` | 04c0d5d79 | 49 marked sentences in 5 saved runs | 49 texts "not confirmed" (9, 10, 7, 10, 13) | `test_ready_thesis_unconfirmed.py` |
| 159 | digest: why line checked against its story | `wip/ready-digest-why-check` | 500811c6a | 3 unsourced why lines printed in ten issues | dropped; the why line no longer verifies a headline | `test_ready_digest_why_check.py` |
| 159 | digest: number check reads units, scales, dates | none | | | | not readied (below) |
| 159 | digest: news hold to opening, rows, Roundup | `wip/ready-digest-news-hold` | f8123815d | issue of 12 Nov: opening figure and 2 story rows drawn; W45: 3 story sections and 6 Google News links drawn | 3 lines "license needed"; W45: 3 sections held, links 6 to 2 (deals and announcements stay) | `test_ready_digest_news_hold.py` |
| 159 | digest: each outlet's own date | `wip/ready-digest-outlet-date` | ce1a90820 | issue of 12 Nov: Bloomberg and JPT dated 2026-11-11 | 2026-11-12 both (2 dates) | `test_ready_digest_outlet_date.py` |
| 159 | digest: name grids with no RT row | `wip/ready-digest-rt-grids` | ce788c444 | 4 of 9 lines silent | "No row of the day yet: ERCOT, SPP." and the like | `test_ready_digest_rt_grids.py` |
| 160 | ask: tie figures to rows, drop arguments | none | | | | not readied (below) |
| 160 | ask: close the spending guards | `wip/ready-ask-guards` | a694f2393 | 10 failing questions of USD 0.25 all asked under a USD 1.00 cap, recorded 0; cap with ledger off never closes | stops after 3 (0.75); refused | `test_ready_ask_guards.py` |
| 160 | ask: held grid's answer heading | `wip/ready-ask-held-heading` | 5fa722543 | "Answered from the warehouse" | "Held for a license; the public grids' figures" (45 of 48 stored, audit) | `test_ready_ask_held_heading.py` |
| 161 | data: which dataset /data cites | none | | | | cannot be readied here (below) |
| 161 | data: License cell from the record | `wip/ready-data-license-cell` | fdefafbf5 | 4 "public" beside "unsettled"; 32 "unsettled" on held rows; marks missing | 4 cells to the record's word; 32 labels "license needed"; 5 marks (today's coverage) | `test_ready_data_license_cell.py` |
| 161 | data: impossible-values rule on the nine | `wip/ready-data-impossible` | 27e968269 | 9 tables held without the rule | applied from each next build; session 118's measure: e.g. a demand of 4,165,722,983 MWh becomes 55,904,508 | `test_ready_data_impossible.py` |
| 161 | data: hold held tables' counts and dates | `wip/ready-data-held-counts` | b80c46891 | 32 counts (1,122,711 rows) and 64 dates printed | "license needed" | `test_ready_data_held_counts.py` |
| 162 | reports: latest whole month | `wip/ready-reports-whole-month` | bb803328e | Oct 2026 (48 of 744 h): CAISO -0.38, ERCOT 0.21, SPP 0.49 | Sep 2026: 0.81, 1.05, 3.44 | `test_ready_reports_whole_month.py` |
| 162 | reports: AI table with cold_2026, one kind | `wip/ready-reports-events` | 342040125 | ERCOT 8.78, PJM 7.34, SPP 6.14, MISO 7.28, ISO-NE 1.15, NYISO 1.38, CAISO 3.15 | 31.15, 28.97, 26.29, 22.96, 19.36, 17.31 (cold_2026); CAISO 23.36 (heat 2022) | `test_ready_reports_events.py` |
| 162 | reports: held regions' public-source measures | none | | | | not readied (below) |
| 162 | reports: exporters below zero | `wip/ready-reports-exporters` | 12519df29 | PJM, SPP drawn "0.0", both green | -3.0 and -1.1; only PJM green | `test_ready_reports_exporters.py` |
| 163 | explore: earlier years in 2025 dollars | none | | | | not readied (below) |

Figures are measured on the page's own files, the public downloads or the tables this machine holds (read only, from the main copy), or, where a table is not on this machine, the audit's own measurement is quoted and named as such. "Site file rebuilt at landing by the desk": attention (the note's count), the board's week (trader branches), iso_trader_daily, ai_power_regions, grid_stress_yearly, the network snapshot, the two findings cards.

## Not readied, and what would ready each

- **134, California at the load aggregation point.** Data request 7 measured the day-ahead gaps from `price_congestion_hourly` (not on this machine); the page's default market is real time, and the real-time DLAP prices were a one-off OASIS read, in no table. What readies it: a DLAP real-time series in the warehouse (a connector change, the desk's), then `ZONES["caiso"]` in `warehouse/derived/datacenter_page.py` with the three DLAPs and the table in `TABLES`, and a rebuild.
- **137, "correct for it".** Which test against chance (a trend test with errors that allow persistent years, or a permutation over the region's own years) is Samuel's word; the count itself is said by `wip/ready-analysis-statistics`.
- **148, each grid's own report first.** The snapshot holds one flow a pair; reading a grid's own report needs both sides in the snapshot (`grid_network.py`, `network_hourly.py`) and `site/lib/network.ts`'s `netExports` reading them. A session's work. The audit's measure: PJM 990 MW in the median hour, opposite sign in 32 percent of hours.
- **151, the board keeps a new build's newer points.** `page_keep.py`'s rule is "one build's row, whole"; appending points and recomputing a row needs `board_page.py`'s row arithmetic callable on a joined series for each row type (power, battery, ancillary, spreads). The audit's first cure is a data-machine run of the board step.
- **157, where a reader asks for removal.** A blank: an address or a form is Samuel's to name.
- **159, the number check reads units, scales and dates.** The check is `warehouse/chat/ask.py` `unverified`, shared with the chat's answers; changing it moves what the chat passes too. Not done in the time.
- **160, bind each figure to its row and drop the model's arguments.** The audit says the binding is not written (entity, time and sign of each figure); dropping the question and the arguments alone sends back 80 of 1,327 stored answers, nearly all right ones. A design for Samuel, then a session.
- **161, which dataset /data cites.** The other choice is `datapages.erw`; its Redivis address is in no file of the repository (`docs/redivis/organization-move.md` gives only its reference), so the link cannot be written. A person's read of the address readies it.
- **162, the held regions' public-source measures.** `licenseHeldRow` holds a row by its grid whatever the measure; showing EIA, Berkeley Lab and event-study measures needs a variable-aware hold through `restPaged`, `Num` and the draft's region logic. A session's work. The audit's measure: 53 of 80 held rows; MISO's carbon 435.82 kg/MWh would make it the dirtiest region.
- **163, 2025 dollars.** The explorer computes nothing: every figure is a table row with its check key, so 2025 dollars need the derived table to carry them (`warehouse/derived/ercot_peak_premium.py`, then a load into the live set, the desk's) and the page to read those variables. The audit's measure: 2015's peak-block IQR 7.64 becomes 10.12.

## Branches that are not clean

- `wip/ready-analysis-errors`: `tests/test_session181.py` (1) and `tests/test_session182.py` (10) compare the committed cards and their downloads with the builder; they fail until the desk rebuilds the impact study and the hourly curtailment cards at landing (the builders read warehouse tables this machine does not hold).

## Tests that fail on main as on the branches (not these changes)

`test_session1116.py` (board node test, 4 of 5), `test_session1898.py`, `test_session6111_ask.py`, `test_session7202_key_refusal.py` (a module-name clash in one process), `test_session137.py`, `test_session143.py`, `test_session148.py`, `test_session156.py`, `test_session168_ask.py` (node tests), `test_session7601_map.py`. Each was run on a clean origin/main checkout of the worktree (git stash) with the same result.

## Rows for the main session

- Landing: none requested (part C rule: each branch waits for Samuel's word).
- Data requests, for the desk at landing of the branch named: rebuild the impact study and hourly curtailment cards (`wip/ready-analysis-errors`); rebuild `ai_power_regions` (`wip/ready-reports-events`); rebuild `grid_stress_yearly` (`wip/ready-analysis-tight-demand`); the board and `iso_trader_daily` (`wip/ready-trader-*`); the attention files (`wip/ready-attention-count`); the nine tables of `wip/ready-data-impossible` at their next builds, and the audit's data request 2 to measure them today.
- For line 134: a DLAP real-time table (connector, the desk's). For line 161: the Redivis address of `datapages.erw` (a person).

## Slips

- One heredoc was typed (a placeholder file under `runs/c770/11406/`, deleted at once; no prompt, no content kept).
- The worktree's `site/node_modules` junction to the main copy was made to run the node-drawn tests; removed at the end with `cmd /c rmdir`.

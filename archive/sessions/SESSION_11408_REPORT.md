# Session 11408 report: chain 770, part C, the rulings readied as branches (old laptop)

Session 11408, 28 November 2026, a worker of chain 770 on the old laptop (code role). Brief: `runs/c770/brief_partC.md` and `runs/c770/brief_common.md`. Lines of `docs/reviews/weekend-2026-11-28.md` (origin/main at 604c1fd66 or later): part 3.3 lines 176 to 184, part 3.4 (line 186 on), then part 3.5 (line 212 on).

- Every branch is cut from origin/main (3321f3092 for the first forks' branches, 401090c7b for mine), holds the change and `tests/test_ready_<name>.py`, and is pushed. None is requested: nothing is written to any landing file, and the weekend page is not edited (the main session writes the figures beside each item).
- No model call (USD 0), no warehouse table written, no data lock, no site build, no browser. Tables read only from the main copy's `warehouse/output/`; builders run only into a worktree.
- The work was split between this session and four forks of it, each in its own worktree (`../erw-c770-h` this session, `h2` part 3.4, `h3` lines 178 to 181, `h4` and `h5` part 3.5). Commits all read "Session 11408:".
- Choices covered by part 2's decision 1 (held figures) were skipped: the held Texas PUC rows on the policy monitor, the 541 deal-seeded companies, the held grids' hour counts on the curtailment tracker.

## Part 3.3 (lines 176 to 184)

| Line | Item | Branch | Head | Before (origin/main) | After (branch) | Test |
|---|---|---|---|---|---|---|
| 176 | Policy: unscored records shown as it opens | `wip/ready-policy-unscored` | 859a61775 | 295 records as the view opens | 367 (+72; the audit's 351 was on the file of 25 November; the file now holds 1,584 records) | `test_ready_policy_unscored.py` |
| 176 | Policy: status as of today | `wip/ready-policy-status-today` | eea903569 | Final 126, In effect 70; as it opens Final 26, In effect 5 | Final 30, In effect 166; as it opens 12 and 19 (read 28 November) | `test_ready_policy_status_today.py` |
| 176 | Policy: three enacted laws in effect | none | | already on main: the research of 26 November marks the three in effect (laws block: in effect 14, enacted 2; page file built 26 November 14:56 UTC) | | settled, no branch |
| 177 | Map: far units at their county's point | `wip/ready-map-county-point` | cec52c9d9 | EIA's points | 8 units, 1,489.2 MW (6 planned, 1,484.2 MW) drawn at their county's point, marked; no count or sum moves (the audit's 7 units and 1,469.2 MW were on the file of 19 November) | `test_ready_map_county_point.py` |
| 178 | Deals: dollars by kind, rumors out | `wip/ready-deals-kinds` | dc5d2a5f7 | tagged USD 3,059.4 billion; 82 buyer cells with a dollar sum | 2,824.0 billion; no dollar sums by buyer, grid or quarter | `test_ready_deals_kinds.py` |
| 178 | Deals: a median needs five deals | `wip/ready-deals-median-five` | dd5b93723 | 13 medians | 8 (M&A, offtake, behind the meter, solar, ERCOT go) | `test_ready_deals_median_five.py` |
| 179 | Demand: MISO's peak as MISO reported | `wip/ready-demand-miso-peak` | d8712e589 | 120,343 MW, +3.21 percent | 118,106 MW (29 July 2025), +1.29; CAISO's average growth +4.45 to +4.58 | `test_ready_demand_miso_peak.py` |
| 179 | Demand: blank hours to the newest hour | `wip/ready-demand-blank-hours` | 2b4e2942a | ERCOT 48 blank hours | 24; every area 24 lower; nothing else moves | `test_ready_demand_blank_hours.py` |
| 179 | Demand: a second base, 2018 | `wip/ready-demand-base-2018` | 6576a95bf | CAISO 2025 +4.45 on 2019 | -0.74 on 2018 beside it; ERCOT +29.54, MISO -0.63; no figure of main moves | `test_ready_demand_base_2018.py` |
| 180 | Storage: batteries retired before 2025 | `wip/ready-storage-retired` | adc7e9c88 | 2015 year end 250.2 MW | 362.9; 2019 1,004.0 to 1,115.4; 2024 on unchanged | `test_ready_storage_retired.py` |
| 181 | Queues: a hybrid at its largest part | `wip/ready-queues-hybrid-largest` | a1434ab18 | CAISO active 190,717 MW; US 1,864,963 | 129,435; US 1,749,315 (-6.2 percent) | `test_ready_queues_hybrid_largest.py` |
| 181 | Queues: round once, a negative capacity as zero | `wip/ready-queues-round-once` | 126ac8961 | 1,289 / 213,253 / 681,953; TVA withdrawn 218,498 | 1,288 / 213,252 / 681,952; TVA 218,573 | `test_ready_queues_round_once.py` |
| 181 | Queues: statuses at 31 December 2025 | `wip/ready-queues-year-end` | a90e258c6 | 8,513 active, 1,864,963 MW | 8,566, 1,878,238 MW (+0.7 percent) | `test_ready_queues_year_end.py` |
| 182 | Curtailment: hours of 100 MWh or more | `wip/ready-curtailment-100mwh` | c173fe55e | 2026 flat load USD 26.99 (page file 26.96); 2025 21.57; 2024 14.06 | 10.82; 13.19; 2.60 (2026 hours counted 5,857 to 2,689 of 7,271) | `test_ready_curtailment_100mwh.py` |
| 183 | Tracker: the Utah join out of every sum | `wip/ready-tracker-utah-out` | 5fd907704 | MW stated 28,254; counted 274; planned 21,305 | 18,854; 273; 11,905 | `test_ready_tracker_utah_out.py` |
| 183 | Tracker: timeline of counted rows only | `wip/ready-tracker-timeline-counted` | ba44f8f86 | 9 rows, median wait 2 years | 3 rows, median 3; 2026's median goes (2 rows) | `test_ready_tracker_timeline_counted.py` |
| 184 | Severance: Louisiana condensate on gross value | `wip/ready-severance-la-condensate` | 5f02c50a2 | 1,000 bbl at USD 102.07 with USD 2 a barrel: USD 12,508.75 | 12,758.75 (+250.00); nothing moves at the default | `test_ready_severance_la_condensate.py` |

### What each of this session's own branches changed

- **Policy, unscored** (`site/lib/policymonitor.ts` `filterRows`): a record with no score passes every significance floor. The Reset's and the calendar lift's hovers and the method note follow. `tests/test_audit_policy_1.py` turned. Measured on `site/data/policy/monitor.json` now on main (`runs/c770/11408/policy_counts.py`).
- **Policy, status today** (`statusAsOf` in `site/lib/policymonitor.ts`, applied in `site/app/policy/page.tsx` where the rows reach the monitor): a final record whose effective step is on or before the page's day reads "In effect" in the filter, the table and the download. The method note's `action_status` paragraph follows; `tests/test_audit_policy_4.py` turned.
- **Policy, the three laws:** on main the research file `docs/research/large_load/legislation_2026-11-26.csv` and the page file already mark Maryland S.B. 937, Maryland H.B. 1532 and Minnesota H.F. 16 "in effect"; `wip/audit-policy-11`'s test now fails on main for that reason. Settled; the main session may drop the item.
- **Map** (`warehouse/derived/project_map.py`): `county_points` reads the Census county gazetteers held under `warehouse/raw/census_gazetteer/` (or `ERW_GAZETTEER_DIR`; no request), `far_from_county` finds the units outside Alaska over 200 miles from their EIA county's point, and `page_rows` draws them at that point with precision 1 ("county point" on the card and in "Near a point"); `counts.units_at_county_point` added. The decision's words (`site/app/map/Decisions.tsx`) and the method note's decisions table follow. Measured with the builder's own rule on `site/data/map.json` now on main (built 28 November 03:48 UTC). The builder itself cannot run on this machine (its `energy_projects` is a copy of 3 October without `proposed_date`): **site file rebuilt at landing by the desk**. With no gazetteer held, the builder keeps EIA's points and says so on stderr.
- **Curtailment** (`warehouse/derived/curtailment_worth.py`): `MIN_HOUR_MWH` 100; `value_of(c, p, min_mwh)` counts an hour for the hours with curtailment and the flat load only at 100 MWh or more, in California; the MWh and dollars keep every hour; Texas unchanged. The file's rule, two sentences of `site/app/curtailment/Sections.tsx` and the method note follow. Measured by the builder's own `caiso()` run twice on this machine's tables, read only (`runs/c770/11408/curt_measure.py`; the tables end 12 November). No month is left with no counted hour. **Site file rebuilt at landing by the desk.**
- **Tracker, Utah join** (`KNOWN_WRONG_JOINS` in `site/lib/dctop.ts` and `site/lib/dcrollups.ts`, the same one row): in neither `counted` rule; the top block names it among the rows left out (`site/app/datacenters/Body.tsx`, "1 known wrong join" with a hover); `scripts/check_datacenters.py` and `replication/datacenter_tracker/replicate.py` follow (otherwise test_session2246's trace fails); the method note says so. Measured through the page's own library, main's file against the branch's, on this machine's `datacenter_facilities.csv` (458 rows; `runs/c770/11408/tracker_rows.py`, `tracker_measure.mjs`; no row written to any committed file).
- **Tracker, timeline** (`timeline` in `site/lib/dcrollups.ts` reads `rows.filter(counted)`): the timeline's note, the method note's 7.6 and the replication follow; `tests/test_audit_tracker_5.py` turned.
- **Severance** (`site/data/severance_rules.json`, Louisiana's `value_deduction.products` oil only; the basis note says condensate is taxed on its gross value with no deduction): the decision's words, the method note's taxable value step and the replication's comment follow; the replication reads the rules file. Measured through `site/lib/severance.ts`.

## Part 3.4 (line 186 on): the battery and generator choices

Figures measured with the site's own finance libraries (Node) and, for the model branches, the builders re-solved on the public files this machine holds. Before, on origin/main: battery USD 80.40 per kW a year (the public file of 26 November), NPV -704.23 per kW (the audit's -697.80 was on the earlier window), IRR -9.26 percent; generator ERCOT solar USD 59.85 per kW, NPV -766.62, breakeven PPA 58.36 per MWh.

| Line | Item | Branch | Head | Before | After | Test |
|---|---|---|---|---|---|---|
| 191 | Battery 8: tax and depreciation | `wip/ready-battery-tax` | d42afcb86 | NPV -704.23; with the 30 percent credit -371.23 | -583.94; -276.74; IRR none | `test_ready_battery_tax.py` |
| 192 | Battery 6: change the rules | none | | | | its other choice is 2 and 3 together: 2 readied, 3 not |
| 193 | Battery 4: the model's own fade | `wip/ready-battery-fade` | 97267cc89 | NPV -704.23 (2.6 percent a year) | -658.47 (1.1, re-solved: year 2 at 98.90 percent) | `test_ready_battery_fade.py` |
| 194 | Battery 9: one kind of dollar | `wip/ready-battery-dollars` | 195d24942 | NPV -704.23 | -665.32 (at 2 percent inflation) | `test_ready_battery_dollars.py` |
| 195 | Battery 1: regulation called 17 percent | `wip/ready-battery-reg-called` | d9e5c68db | USD 80.40 | 74.02 (-7.9 percent) | `test_ready_battery_reg_called.py` |
| 196 | Battery 2: charge carried over midnight | `wip/ready-battery-carry` | 98b4a8389 | 80.40 | 85.90 (+6.8 percent, 13 blocks) | `test_ready_battery_carry.py` |
| 197 | Battery 10: 4 hours at rated power | `wip/ready-battery-rated-hours` | e93119f36 | 80.40 | 82.98 (+3.2 percent) | `test_ready_battery_rated_hours.py` |
| 198 | Battery 3: 15-minute prices | none | | | | cannot be readied here (below) |
| 199 | Battery 7: a cap at 500 MW | `wip/ready-battery-cap` | 0ba895e89 | sizes to 5,000 MW | to 500 MW; nothing moves at 100 MW | `test_ready_battery_cap.py` |
| 203 | Generator 1: tax and depreciation | `wip/ready-seller-tax` | 044a5d954 | NPV -766.62; PPA 58.36 | -526.10; 53.59 | `test_ready_seller_tax.py` |
| 204 | Generator 2: one kind of dollar | `wip/ready-seller-dollars` | 3e94c97cb | NPV -766.62; PPA 58.36 | -706.90; 59.22 | `test_ready_seller_dollars.py` |
| 205 | Generator 9: a start cost | `wip/ready-seller-start-cost` | a2184f1c6 | peaker margin 48.15, 406 runs | 37.14, 153 starts (at USD 50 a start) | `test_ready_seller_start_cost.py` |
| 206 | Generator 3: one credit year | `wip/ready-seller-credit-year0` | b8e071873 | 30 percent credit worth 297.32 (solar 368.30) | 333.00 (solar 412.50) | `test_ready_seller_credit_year0.py` |
| 207 | Generator 4: PPA paid on energy made | `wip/ready-seller-ppa-volume` | a70d7b10a | PPA 58.36 | 61.51 | `test_ready_seller_ppa_volume.py` |
| 208 | Generator 6: stop below zero | `wip/ready-seller-stop-below-zero` | c6b090cd9 | 59.85 | 60.26 | `test_ready_seller_stop_below_zero.py` |
| 209 | Generator 7: mid-month nameplate | `wip/ready-seller-mid-nameplate` | e6aec3f5a | 59.85 | 59.51 | `test_ready_seller_mid_nameplate.py` |

- **Battery 3, cannot be readied here:** a 15-minute energy program changes the public dispatch file's shape and its replication, and the quarter prices are in `ercot_all_hub_prices_history.csv` (707 MB), which this machine (about 200 MB free) can only stream. What would ready it: on the desktop, the block program of `wip/ready-battery-carry` (or `solve_day`) with four energy intervals an hour (the audit's `tests/audit_battery_lp.py`, q = 4, on `wip/audit-battery-2`), a quarter-price reader, and the export at 15 minutes. The audit measured +2.7 percent.
- **Values chosen where the page names none:** USD 50 a start (the audit's middle sensitivity of 25, 50 and 100; no source) and 2 percent inflation (the low end of the audit's 2 to 2.5). Each is one constant Samuel may change.
- **Battery 7's other choice, a warning line,** is not readied; the cap is.
- **Generator 3's other way to agree** (year 1 on both pages) is not readied; year 0 on both is.

### Landing notes for part 3.4 (the desk)

- The finance branches (battery tax, fade, dollars; seller tax, dollars) break pinned hand cases that assert the old arithmetic: `test_session179`, 186, 196, 235, 263, 264, 296, 297, the node scripts `site/scripts/test-battery-finance.mjs` and `test-seller-finance.mjs`, and the replication's `page_figures.json` NPV. Each commit lists its own; they are redone at landing with the branch chosen.
- `test_session162` fails on the rated-hours branch (the generator page's pair battery against this program); `test_session183` fails on the start-cost branch until the desk rebuilds the snapshot; the replication's optimizer check must follow the carry branch.
- Conflicts if more than one of a group is chosen: battery tax, fade and dollars all edit `site/lib/battery/finance.ts` and the same decision lines; rated hours, regulation called and carry all edit `battery_stack.py`.
- The model and builder branches (seller stop-below-zero, mid-nameplate, start cost; battery rated hours, regulation called, carry) need the monthly tables and site files rebuilt at landing by the desk.

### Landing notes for lines 178 to 181 (the desk)

- Older tests turned on these branches: `test_audit_deals_3` and 6, `test_session466`, 2239, 7404 and 7405, `test_audit_demand_1`, `test_session97`, `test_audit_storage_4`, `test_audit_queues_1` and 6.
- Site files rebuilt at landing by the desk: `site/data/demand_growth.json` (the three demand branches), `site/data/queues.json` (the three queue branches) and `queue_places.json` (round once). The table `storage_buildout_monthly` is rebuilt and loaded at landing (the page reads the live set). Each rebuilt site file carries a mark; its site-file test skips until it is there.
- The three demand branches edit the same files: more than one chosen means a merge by hand. On the storage branch the twelve-month net additions of January to March 2025 also move (46 cells). On the MISO-peak branch the blank-hour counts rise (MISO 24 to 96): hours where EIA filled in its own estimate are left out. The demand replication's column follows the MISO-peak branch only by hand (`replication/demand/replicate.py`), and the base-2018 keys are not in it.

### Landing notes for this session's own branches (the desk)

- `wip/ready-map-county-point`: rebuild `site/data/map.json` with the branch's builder on a machine that holds the gazetteer under `warehouse/raw/census_gazetteer/`; `test_session7601_map` counts the decisions table's rows (still twelve: the rule is folded into the queue row).
- `wip/ready-curtailment-100mwh`: rebuild `site/data/curtailment/worth.json`; `site/scripts/check-curtailment.mjs` reads the file and follows.
- `wip/ready-tracker-utah-out` and `wip/ready-tracker-timeline-counted` both edit `site/lib/dcrollups.ts` and `replication/datacenter_tracker/replicate.py` (different lines; a trial merge is advised). `replicate.do` (Stata) does not drop the row: the session did not edit the do-file.
- `wip/ready-severance-la-condensate`: `test_session40` shows all 26 hand cases matching, then node's Windows exit assertion (libuv, known on this laptop), as on main.

## Part 3.5 (line 212 on): the three new tools' questions

Cut from origin/main 401090c7b. Figures measured with the site's own code on the files now on main (`site/data/predict/` index built 28 November 05:12 UTC).

| Line | Item | Branch | Head | Before | After | Test |
|---|---|---|---|---|---|---|
| 216 | Forecast: menu place and name | skipped: part 2's decision 4 | | | | |
| 216 | Forecast: opens on Texas | a blank: needs Samuel's word (no other place named) | | | | |
| 217 | Forecast: remove the days after tomorrow | `wip/ready-forecast-no-days-ahead` | 1b7b84d5a | Texas draws 5 days | none (the file and its download stay) | `test_ready_forecast_no_days_ahead.py` |
| 218 | Forecast: peak table in Every place | `wip/ready-forecast-peak-every-place` | bd8f84560 | no table | 64 rows, 320 figures, each linked to its file | `test_ready_forecast_peak_every_place.py` |
| 219 | Forecast: remove "with the weather known" | `wip/ready-forecast-no-weather-known` | 91edf9812 | drawn for 64 places | none (the files keep the line) | `test_ready_forecast_no_weather_known.py` |
| 220 | Forecast: move the new blocks | a blank: needs Samuel's word (no place named) | | | | |
| 221 | Forecast: "More hubs" its own page | not readied: not small (a new address, its entries in the release, value-check, route and snapshot lists, and the choices it takes from `/forecast`'s address) | | | | |
| 222 | Forecast: 5 percent or another line | a blank: needs Samuel's word (no number named) | | | | |
| 222 | Forecast: lead with the sound months | `wip/ready-forecast-filing-sound-first` | 2fc4806c9 | every month in order | the months that pass first, in the 44 places that flag one; no figure moves (the report card above is unchanged) | `test_ready_forecast_filing_sound_first.py` |
| 222 | Forecast: a sentence where none is flagged | `wip/ready-forecast-filing-none-sentence` | acac07059 | 0 of 20 such places say anything | 20 of 20 | `test_ready_forecast_filing_none_sentence.py` |
| 223 | Forecast: drop the two ERCOT legacy lines | `wip/ready-forecast-no-misapp` | af71be1fe | real-time file 7 hubs, 2,760 score rows; Texas operator wind and solar comparison 8 rows | 3 hubs, 888 rows; no operator comparison | `test_ready_forecast_no_misapp.py` |
| 224 | Forecast: undo EIA-930 back to 2015 | cannot be readied here: it removes warehouse rows and rebuilds the longer backtest, the desk's work | | | | |
| 225 | Forecast: SPP's own load forecast | cannot be readied here: a person reads SPP's terms, and the table is not held (data request 19) | | | | |
| 227 | Forecast: list the problem set | `wip/ready-forecast-problem-set-listed` | 319763462 | 10 sets listed, 2 waiting | 11 listed, 1 waiting | `test_ready_forecast_problem_set_listed.py` |
| 230 | Equities: opens on ProFrac | a blank: needs Samuel's word (no company named) | | | | |
| 231 | Equities: a fourth quarter as year less nine months | `wip/ready-equities-q4` | d3f5e9bb4 | 146 companies with a fourth-quarter point | 218 of 234 (1,507 quarters worked out) | `test_ready_equities_q4.py` |
| 232 | Equities: cover share count | cannot be readied here: the builder reads `equity_fundamentals_quarterly`, not on this machine | | | | |
| 233 | Equities: a year's revenue beside a quarter's | `wip/ready-equities-year-revenue` | 90561e547 | 0 companies show it | 216 (223 carry a year); `index.json` rebuilt at landing by the desk | `test_ready_equities_year_revenue.py` |
| 234 | Equities: six utilities, co-registrant figures | cannot be readied here: needs the SEC connector, its cached facts and the table, none held here | | | | |
| 235 | Equities: six segments by a named list | a blank: needs Samuel's word (no list given) | | | | |
| 236 | Board: the 30 blank rows as one line | `wip/ready-board-equities-one-line` | b47f52593 | 30 rows drawn | 1 line with the count and the reason (the download keeps all 30) | `test_ready_board_equities_one_line.py` |
| 236 | Board: remove the older "Energy equities" row | `wip/ready-board-old-equities-row` | 8695192da | 1,225 board rows | 1,224; `board.json` rebuilt at landing by the desk | `test_ready_board_old_equities_row.py` |
| 237 | Equities: "What moved with gas" | cannot be readied: no share price is held | | | | |
| 238 | Equities: list the problem set | `wip/ready-equities-problem-set` | ed2e32938 | 10 sets listed | 11 | `test_ready_equities_problem_set.py` |
| 238 | Equities: "a producer of mostly natural gas" | a question for Samuel, not a branch | | | | |
| 241 | Impact: Georgia's exemption to 2033 | `wip/ready-impact-georgia-2033` | 72dde4586 | forgone USD 618.71 million with a 3-year refresh; 51.56 million for a 2030 to 2033 build | 1,237.42 million; 103.12 million (nothing moves at the defaults) | `test_ready_impact_georgia_2033.py` |
| 242 | Impact: 20 operating years, or another | a blank: needs Samuel's word (no number named) | | | | |
| 243 | Impact: county populations | cannot be readied here: only metropolitan (CBSA) populations are held, no county table | | | | |
| 244 | Impact: `datacenter_announced` facts public | cannot be readied here: the table is not on this machine; it needs a facts-only table and a Redivis release by a person | | | | |
| 245 to 246 | Impact: decisions 19 to 26; the last line | blanks: no other choice named | | | | |

### Landing notes for part 3.5 (the desk)

- Older tests turned: `test-forecast-peak.mjs` and `test_session10405`; `test-forecast-lines.mjs`; `test_predict.py`'s hub order test (skips until the rebuild); `test-problem-set-forecast.mjs`, `test-problem-sets-country.mjs`, `test_session10404` and `test_session10412` (forecast problem set); `test_session10408`, 10402, 132, 10412, 10404, 8901, three node test scripts and `test-datacenter.test.mjs` (equities, board, impact). Each commit lists its own.
- Conflicts if more than one is chosen: the three forecast `view.tsx` branches (217, 218, 219); the two filing branches; the equities q4, year-revenue and board one-line branches (`site/lib/equities.ts`); and **the two problem-set branches (forecast and equities) both edit `test_session10404` and 10412** and the problem-set list.
- `wip/ready-forecast-no-misapp` changes the builders, not the page: site files rebuilt at landing by the desk; the hand-run `replicate_rt.py` follows the new file.
- `wip/ready-forecast-problem-set-listed`: no Python or Stata replication of the set is written, and no dated edition holds it until the next is built; the method note says both.
- `wip/ready-forecast-peak-every-place` was not type-checked here (no memory for the checker): the desk's build at landing is its first type check. `check-board.mjs` follows the one-line board but needs a served site, so it was not run.
- Georgia's 2033: no quote in the rules file holds the year (the auditor's sentence is in no kept text here); the year sits in the hover, which names the auditor.
- Tests that fail on main as on the branches, left alone: `test_session8901`'s 16 edition-link checks and `test_session7534`'s replication (running either rewrites the tracked `replication/problem_sets/country_inputs.csv`; restored from HEAD each time, never committed).

## Slips

- One empty heredoc typed by this session (a `cat > /dev/null <<'X'` line in the policy work; it wrote nothing), one by the part 3.4 fork (empty, stopped at once) and one by the lines 178 to 181 fork (appending to its own notes under the ignored `runs/`). No permission prompt was raised. After each, files were written with the Edit and Write tools only.
- The lines 178 to 181 fork first ended two method notes' decision lines "(sessions N and 11408)", which the notes-against-decisions tests reject; fixed by a later commit on each branch.
- The equities and impact fork ran one short `python -c` count (the board's equities rows), against the no-one-liner rule; the forecast fork typed one empty redirect line (`cat > /dev/null < /dev/null`).
- Each part 3.5 fork used `git stash` once in its own worktree to run two tests on main's code; the stash list is shared by every worktree, so each dropped or popped only its own entry. The owner's entry (`stash@{0}`, "owner's chain_worker.ps1 edit") is untouched, checked after both finished.
- No full test suite was run (memory, about 200 MB free). Each branch ran its own test and every test file that imports or pins the changed file; the results are in each commit message.

## Rows for the main session to write

- None for the landing request file: no branch is requested until Samuel rules.
- Weekend page, part 3.3 line 176: the "three enacted laws" choice is settled on main (in effect 14, enacted 2 on the page file of 26 November); it may move to "Dropped since 26 November".

# Session 11405 report (chain 770, part C, old laptop): rulings readied as branches

Lines of `docs/reviews/weekend-2026-11-28.md` (origin/main 604c1fd66): part 2's decisions 1, 4, 6, 7, 8 and 9; part 3.1's 30 and 116; part 3.2's 27 and 65; part 3.3's datacenter line "a picked project takes its document's own wage and spending split". Every branch is cut from origin/main, pushed, and not requested: each lands only on Samuel's word. No model call, no warehouse table written, no data lock, no site build, no browser. Worktrees: `C:\Users\lossa\Documents\erw-c770-e` (decision 1 and this report), `erw-c770-e-impact`, `erw-c770-e-ops`, `erw-c770-e-eia`, `erw-c770-e-hs`, `erw-c770-e-ha` (forks of this session), each left in place, no `node_modules` junction left.

## The branches

| Page line | Item | Branch | Head | Before (origin/main) | After | Test |
|---|---|---|---|---|---|---|
| 43 | Decision 1: held figures out, one batch | `wip/ready-held-out` | f626fbfb2 | 4,261 held values in 15 places (below) | 0 | `tests/test_ready_held_out.py` (with `_site.py`, `_analysis.py`) |
| 49 | Decision 4: menu place for ten pages | `wip/ready-nav-menu` | 1b254ff78 | 10 pages in no menu; 36 menu entries | 0; 46 entries; `/impact` keeps "Local impact" (its own title) | `tests/test_ready_nav_menu.py` |
| 57 | Decision 6: long backtests weekly | `wip/ready-forecast-weekly` | 43973c07f | `ahead.py` 7 runs a week; 4 h 34 min of lock on 27 November (22:28 to 03:02 UTC) | 1 run a week (Sundays UTC); "days ahead" place-days 565 a week, against 1,015 | `tests/test_ready_forecast_weekly.py` |
| 60 | Decision 7: Meta's posts out of the medians | `wip/ready-impact-meta-out` | ec7126120 | 833.3 construction workers per USD billion (25 projects); 10,000 a year on the default campus; Virginia 20,000 | 400 (18); 4,800; Virginia 9,600 (-52 percent); Virginia taxes present value -10.4 percent | `tests/test_ready_impact_meta_out.py` |
| 60 | Decision 7, second branch: cap of two rows a company | `wip/ready-impact-meta-cap` | e2b8daac9 | the same | 258.3 (12); 3,100; Virginia 6,200; taxes present value -13.8 percent | `tests/test_ready_impact_meta_cap.py` |
| 61 | Decision 8, "yes": EIA's NY, NE, Midwest rows held | `wip/ready-eia-held-regions` | 7bf1d1169 | nine event pages 2,439 figures; `/supply` 1,387; `/demand` 160 as it opens | 1,785 (654 read "license needed"); 1,216; 160 (85 to 113 a held place when chosen) | `tests/test_ready_eia_held_regions.py` |
| 61 | Decision 8's mend: the unit after "license needed" | `wip/ready-events-mw-mend` | a15c9eaea | 187 places (180 on the nine event pages, 7 on the index; the page's 146 is the 20 November count) | 0 | `tests/test_ready_events_mw_mend.py` |
| 66 | Decision 9: nightly commit earlier | none | | | | cannot be readied here (below) |
| 85 | 30: San Diego baseline allowances | none | | | | cannot be readied here (below) |
| 85 | 116: San Diego climate credit | none | | | | cannot be readied here (below) |
| 112 | 27: peak shaving at 85 percent | `wip/ready-battery-shave-85` | 7f9c06fa5 | Austin "Saved a year" USD 8,931.16; SCE 2013 44,123.70; Seattle 12,795.06 | 7,549.66; 38,698.50; 11,830.26 | `tests/test_ready_battery_shave_85.py` |
| 112 | 65: 1,034 Btu a cubic foot | `wip/ready-severance-btu-1034` | 73da7218e | Texas gas, 46,500 Mcf at USD 2.99: USD 10,427.63; New Mexico 11,039.38 | 10,782.16 (+3.40 percent); 11,414.72 | `tests/test_ready_severance_btu_1034.py` |
| 130 | A picked project takes its document's wage and split | `wip/ready-impact-project-split` | 589d1762b | Project Blue: wage 98,701 (Census, Arizona), JLARC's split; operating earnings USD 17.8 million a year | wage 64,000, split 33.3/66.7/0; earnings 11.5 million (-35.2 percent); income tax over the life -17.4 percent; taxes present value -3.0 percent | `tests/test_ready_impact_project_split.py` |

Every branch merges into origin/main at c7d6538ff without a conflict (checked 13:50 UTC). `wip/ready-impact-project-split` conflicted with landing 2 (row 143's hover words, "a stated wage or split is not taken"); origin/main was merged into it, the branch's words kept, and `tests/test_audit_impact_4.py` now asserts the taken wage.

## Decision 1, place by place (measured on origin/main ae43cdc96, then on the branch)

| Place | Before | After | How |
|---|---:|---:|---|
| Git: `energy_deals.csv` (583 rows) and `energy_deals_evidence.csv` (652) | 1,235 | 0 | `git rm --cached`, out of `.gitignore`'s allowlist and the daily workflow's commit list; `run_daily.sh` restores both from the archive on a runner and skips the three deal steps when they are absent |
| `/curtailment`: ISO-NE's and NYISO's hours under USD 5 | 38 | 0 | `free_energy.py` skips held grids; the page gates the count; the widest gap of the year moves from NYISO 13.09 to SPP 5.27 |
| What a generator earns: ISO-NE and NYISO offered | 43 | 0 | disabled as MISO and PJM are (`capture_price.py`, `merchant_revenue.py`, `merchant_hubs.py`, `model.ts`, `projectmap.ts`) |
| Policy monitor: PUCT's and the Texas Governor's records | 38 | 0 | `monitor_site.py`; records 1,584 to 1,546; shown as it opens 295 to 284 |
| `/map`: ISO-NE's queue positions | 414 | 0 | `project_map.py` counts them as held (21,901.8 MW), as MISO's and NYISO's; `/resources` stops drawing them too |
| Deals companies tab: deal-seeded rows | 541 | 0 | `site/lib/data.ts` skips deal-seeded rows while `energy_deals` is held: 562 companies to 21 |
| MISO's gallery charts (48 files, 48 index entries) | 96 | 0 | `run.py` held_isos adds MISO |
| MISO's daily hub prices in four network files | 977 | 0 | `network_stories.py`, `network_daily.py`, `page_keep.py` |
| MISO's hourly board files | 0 | 0 | none existed |
| Impact study default download (NYISO New York City as control) | 56 | 0 | `impact_study.py` refuses a held grid as series or control; the default card now reads the refusal ("license needed") until a person picks another control |
| Weekly results (`watch_nyiso_reg`, `watch_spp_regup`) | 36 | 0 | `watch.py` runs no held grid's price line |
| Spikes card CSV (NYISO, ISO-NE rows) | 132 | 0 | `findings_common.withhold` |
| Gas share card CSV | 16 | 0 | the same |
| Peak hour card CSV (found, not on the line: the same kind of card) | 384 | 0 | the same |
| Held figures in four card JSONs | 255 | 0 | the same |

Total 4,261 to 0. The history is not rewritten.

## Cannot be readied here

- **Decision 9 (the nightly commit's hour):** the hour is the Windows scheduled task "ERW data machine daily" on the desktop; `scripts/register_data_machine_daily.ps1` already takes `-At` (default 10:00 local), so no repository change is needed. A person on the desktop re-registers it with `-At <hour>`; the page names no hour, so the hour is a blank for Samuel. Any hour must keep clear of the runner's lock (14:00 to about 16:00 UTC) while the run lasts about 11 h 20 min (17:57 to 05:20 UTC on 27 November; decision 6 would cut about 4.5 h). An earlier hour may not cure it: on 27 November the pull hit a conflict after 161 commits; on 26 November two untracked files in the main checkout stopped it.
- **30 (San Diego's baseline allowances):** not held (`bill_rules.json` says SDG&E's calculator is a script). Needs SDG&E's baseline allowance tariff sheet read, then the SDGE allowances set and cited in `bill_rules.json`. The ranked list's examples: USD 332.91 becomes 319.00 to 291.17.
- **116 (San Diego's climate credit box):** the ranked list records USD 49.36 from https://www.cpuc.ca.gov/climatecredit (read 19 November) but no exact quote, and every credit in `bill_rules.json` carries its quote. Needs that page or SDG&E's sheet read for the quote, then a `climate_credit` entry for SDGE and the box in `BillCalc.tsx`. The box is off by default: nothing moves as the card opens.
- **3.2's "together" choice** (27 and 65 with their tools' switch branches): not built. 27 with `wip/switch-battery-customer` conflicts in three files; a trial resolution moved the oversized case 16,825.41 to 15,205.41, Austin at the field's start 4,326 to 3,635, Salt River Project 13,376.42 to 12,404.42, and six of that switch's tests would need new numbers. 65 with `wip/switch-severance` conflicts in `Calculator.tsx`.

## Landing hazards (for the desk)

- `wip/ready-held-out`: a machine that pulls it has git delete its `warehouse/output/energy_deals.csv` and `energy_deals_evidence.csv` (they were tracked). Copy both aside before the pull and back after, on the data machine above all. The runner's restore of the two from the archive (`restore_tables.py energy_deals energy_deals_evidence --no-redivis`) was not run here (no request to any service); if it fails, the three deal steps skip that day rather than write a thinner table. The Thesis Builder on GitHub then reads no deals (it already reads `None` gracefully).
- `wip/ready-held-out`: the four findings cards' PNG pictures (in `site/public/findings` and `docs/analysis/findings`) still draw NYISO's and ISO-NE's figures; only `render-cards.mjs` in a browser redraws them: the desk at landing. The cards' trimmed words leave the peak hour card's subtitle empty and one New York sentence without its subject: the builder's next run rewrites them.
- `wip/ready-held-out`: the site files were rewritten by scripts that do what the changed builders now do (this machine's tables are too old for a rerun): `runs/c770/11405/strip_*.py` in `erw-c770-e-hs` and the scripts in `erw-c770-e-ha`. `zone_shapes.json` was not rebuilt and still lists ISO-NE's and NYISO's places as tiles without figures (`test_session149_map` allows it until its next build).
- `wip/ready-nav-menu`: `tests/test_session469.py::test_release_is_not_touched` fails on any unlanded branch that changes `release.ts`, and passes once it lands. The new sub-group's name "Every authority and state" is the storage page's own title, for Samuel's word.
- `wip/ready-impact-meta-out`, `-meta-cap`, `-project-split`: `site/data/forecast/datacenter_announced.json` is rebuilt by its own builder from repository files only and is committed on each branch; the replication agrees on 16,010 of 16,010 figures on the two Meta branches.

## Found, not on the line (for Samuel)

- `warehouse/output/energy_companies.csv` is tracked in git and holds the 541 deal-seeded parties (with 21 researched rows no daily step can rebuild); left in git on the branch.
- `site/data/deal_duplicates.json` (from `warehouse/deals/duplicates.csv`) names held deals with buyers, sellers and figures; and the Roundup of 2026-W45 (`docs/digest/email/`) names a deal of the week. Neither is on decision 1's line.
- SPP's 12 gallery charts stay (the line names MISO's only).
- The audit-analysis-2 parts on deep drafts 8 and 9 (EIA's regions) and the scanner's table list belong with decision 8, not done on `wip/ready-held-out`.

## Rows for the main session to write

- No landing row (nothing is requested). The figures above go beside each item on the weekend page.
- No data request.

## Slips

- Forks ran a bare `cat > /dev/null` with no input (twice) and a bare `python -` that waited on input (three times); each was stopped and changed nothing. They break the letter of the no-heredoc, no-inline-script rule.
- One fork's `git worktree add` met a lock on `.git/config` and a `git worktree prune` that could not delete the stale records `erw-1425` and `erw-1600` (permission denied); nothing else touched.
- `wip/ready-impact-meta-out` was cut from 3321f3092, origin/main of that moment; it merges into today's main without a conflict.
- No site type check or build was run (memory); node tests ran where the forks made a temporary junction, removed after.

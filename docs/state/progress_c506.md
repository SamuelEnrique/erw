# Progress of chain 506 (findings audit and shortlist, samueloldlaptop)

Chain file: https://github.com/SamuelEnrique/erw/blob/main/queue/done/506-day-19-november-oldlaptop-findings-audit-shortlist.md
Audit: https://github.com/SamuelEnrique/erw/blob/main/docs/reviews/findings-audit-2026-11-19.md

## Steps

- Chain file saved: done, commit 5faada5f0, session 8800.
- Resume file `queue/next/560-resume-chain-506.md`: done, commit df886ffb7, session 8800. No other resume file of this machine was in queue/next.
- Part A, the ground (549 drafts listed, 364 of 19 November marked, tables and licenses): done, session 8800.
- Part B, the audit: under way, session 8800. Scripts in runs/ (c506_inventory, c506_static, c506_shapes, c506_repro, c506_restore_batch, c506_filtered_restore, c506_filter_local, c506_window, c506_check1, c506_check3, c506_pctile, c506_fix_sentences, c506_fix_do, c506_doc); results in runs/c506/ and copied to docs/reviews/findings-audit-2026-11-19/.
  - Check 3 reading: done for all 549 (172 shapes, three readers); 12 do-files mended, commit 77cdaa616; 34 trade drafts wait on the percentile test (needs their tables).
  - Check 1 wording: 56 sentences mended, commit 1296e9264; the first-year claims are tested as each reproduction runs.
  - Check 2: 106 reproduced from tables on this machine; the rest wait on tables rebuilt from the archive bucket (about 5 minutes a call) or, for the hourly EIA-930 tables, a filtered rebuild of the rows the drafts name.
  - Check 4: one template for every chart (builder.py): "fail in part" for all, under For Samuel's ruling.
- Part B for the 364 of 19 November: done, session 8801 (every draft has a verdict; "not checked" ones carry their reason). The per-draft rebuild of the hourly EIA-930 tables (regions, tie lines, supply) and France's grid was stopped by Claude Code for low memory and is not restarted unattended: waiting (about 50 drafts, listed in the audit as "table not on this machine").
- Part C, already known: 80 drafts read, session 8801 (`partc.csv`); hosts opened: www.eia.gov, www.census.gov, robots and terms first (`hosts.csv`).
- Part D, the sheet: forty, session 8801 (twenty first, then twenty more; no family over six).
- The last session (8802): note written (docs/state/note_2026-11-19_oldlaptop_c506.md), resume file removed (commit 078a52e17), chain_queue next: nothing for this machine (exit 3), so part E goes on.
- Part E: a second route for each of the forty done, session 8801; part C for the remaining passed drafts, strongest first: under way, session 8802. Earlier: 25 second routes recorded (`route2.csv`); Far West Texas left the sheet (ERCOT's own zone load differs from EIA-930 by 1.7 to 3.5 percent).
- Data request 30 (the archive rebuilds `ferc714_planning_area_forecasts` short): requested.

## Families (part B), the 19 November drafts first

One line a family: drafts, 19 November drafts, state, session.

- authorities: 26 drafts (26 of 19 November): passed 26, fixed 0, withdrawn 0, not checked 0, held 0; part B done, session 8801
- coal_uranium_metals: 25 drafts (17 of 19 November): passed 21, fixed 4, withdrawn 0, not checked 0, held 0; part B done, session 8801
- cross_family: 25 drafts (17 of 19 November): passed 6, fixed 2, withdrawn 0, not checked 17, held 0; part B done, session 8801
- demand: 30 drafts (18 of 19 November): passed 30, fixed 0, withdrawn 0, not checked 0, held 0; part B done, session 8801
- emissions_climate: 28 drafts (21 of 19 November): passed 24, fixed 4, withdrawn 0, not checked 0, held 0; part B done, session 8801
- events: 30 drafts (30 of 19 November): passed 23, fixed 0, withdrawn 0, not checked 7, held 0; part B done, session 8801
- forecasts: 30 drafts (30 of 19 November): passed 0, fixed 0, withdrawn 0, not checked 30, held 0; part B done, session 8801
- gas: 35 drafts (24 of 19 November): passed 29, fixed 6, withdrawn 0, not checked 0, held 0; part B done, session 8801
- generation_pipeline: 35 drafts (0 of 19 November): passed 31, fixed 4, withdrawn 0, not checked 0, held 0; part B done, session 8801
- large_load: 16 drafts (16 of 19 November): passed 2, fixed 0, withdrawn 1, not checked 0, held 13; part B done, session 8801
- markets_operations: 20 drafts (13 of 19 November): passed 16, fixed 3, withdrawn 0, not checked 1, held 0; part B done, session 8801
- oil_products_world: 41 drafts (23 of 19 November): passed 28, fixed 13, withdrawn 0, not checked 0, held 0; part B done, session 8801
- other_us: 26 drafts (19 of 19 November): passed 8, fixed 18, withdrawn 0, not checked 0, held 0; part B done, session 8801
- prices: 33 drafts (0 of 19 November): passed 31, fixed 2, withdrawn 0, not checked 0, held 0; part B done, session 8801
- queues_deals_datacenters: 27 drafts (0 of 19 November): passed 14, fixed 13, withdrawn 0, not checked 0, held 0; part B done, session 8801
- regions: 27 drafts (27 of 19 November): passed 15, fixed 0, withdrawn 0, not checked 12, held 0; part B done, session 8801
- tariffs_policy: 24 drafts (12 of 19 November): passed 22, fixed 2, withdrawn 0, not checked 0, held 0; part B done, session 8801
- trade: 34 drafts (34 of 19 November): passed 17, fixed 0, withdrawn 0, not checked 17, held 0; part B done, session 8801
- weather: 18 drafts (18 of 19 November): passed 8, fixed 2, withdrawn 0, not checked 8, held 0; part B done, session 8801
- world_power: 19 drafts (19 of 19 November): passed 13, fixed 3, withdrawn 0, not checked 3, held 0; part B done, session 8801

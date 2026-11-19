# Note: chain 506 on the old laptop, 19 November 2026 (the findings audit and the sheet of forty)

Chain file: https://github.com/SamuelEnrique/erw/blob/main/queue/done/506-day-19-november-oldlaptop-findings-audit-shortlist.md. Sessions 8800 to 8802. Model spend USD 0.00.

## Where to look

- The audit, one row a draft: https://github.com/SamuelEnrique/erw/blob/main/docs/reviews/findings-audit-2026-11-19.md (its data: https://github.com/SamuelEnrique/erw/tree/main/docs/reviews/findings-audit-2026-11-19)
- The sheet of forty: https://github.com/SamuelEnrique/erw/blob/main/docs/reviews/findings-shortlist-2026-11-19.md
- Progress by family: https://github.com/SamuelEnrique/erw/blob/main/docs/state/progress_c506.md

## Counts (549 drafts; 364 of 19 November)

- Passed 364, passed after a fix 76, not checked 95, held (internal table) 13, withdrawn 1.
- By family (passed / fixed / not checked / held / withdrawn): authorities 26/0/0/0/0; coal_uranium_metals 21/4/0/0/0; cross_family 6/2/17/0/0; demand 30/0/0/0/0; emissions_climate 24/4/0/0/0; events 23/0/7/0/0; forecasts 0/0/30/0/0; gas 29/6/0/0/0; generation_pipeline 31/4/0/0/0; large_load 2/0/0/13/1; markets_operations 16/3/1/0/0; oil_products_world 28/13/0/0/0; other_us 8/18/0/0/0; prices 31/2/0/0/0; queues_deals_datacenters 14/13/0/0/0; regions 15/0/12/0/0; tariffs_policy 22/2/0/0/0; trade 17/0/17/0/0; weather 8/2/8/0/0; world_power 13/3/3/0/0.
- Mended: 78 sentences (49 "were" after a plural, 2 "the count of", 5 lost words, 22 untrue "first year" claims; 6 wrong mends put back), 12 do-files. No figure changed.

## Withdrawn

- `tariff-min-contract-years`: the table now holds 14 filings that state a contract term, the draft says 13 (the table gained one an hour after the draft was computed).

## The ten strongest on the sheet

1. Dominion zone (PJM) mean hour of demand: 15,403 MW in 2025 against 11,687 in 2019.
2. Virginia Electric and Power's commercial sales: 60.09 TWh in 2025 against 41.54 in 2017 (EIA-861 annual agrees).
3. Solar's output in ERCOT's tightest hours: 5.0 percent of solar capacity in 2025 against 71.1 in 2019.
4. ERCOT West zone midday price: 48.9 percent of the all-hours mean in 2025 against 128.9 in 2015.
5. ERCOT South hub evening price: 161.0 percent of the all-hours mean in 2025 against 109.5 in 2015.
6. ERCOT North hub's cheapest hour: 10.7 hours after midnight in 2025 against 6.0 in 2015.
7. Omaha Public Power District's commercial sales: 7.88 TWh in 2025 against 3.67 in 2017 (EIA-861 annual agrees).
8. Mean hourly flow from Canada to New York: 211 MW in 2025 against 1,992 in 2019.
9. Share of hours New England exported on net: 27.8 percent in 2025 against 0.05 in 2019.
10. CAISO's battery fleet against its ten highest days' demand: 46.6 percent in 2025 against 0.6 in 2019.

## What waits for Samuel

- The Stata run of the forty do-files (read here, not run: no Stata on this machine).
- Rulings: the chart titles (the subject, not the finding, on all 549); the PNGs still carry the old words of the 78 mended sentences; "Reproduce" promises a public download that answers 403; whether the warehouse's annual price method explains the 1 percent gap to EIA's table 5.3.
- The data machine: data request 30 (the archive rebuilds `ferc714_planning_area_forecasts` short; 47 drafts wait).
- Restarting the per-draft rebuild of the hourly EIA-930 tables (stopped by Claude Code for low memory; about 50 drafts wait).

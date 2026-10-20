# Session 374 report: the live set's sources check, green; the load, refused for 31 tables older than the live copy

20 October 2026, from 20:25 UTC, unattended, on lab-desktop (the data machine), the second session of the chain of 20 October, day, under the data lock taken at 20:01 UTC. Model spend USD 0. Pulls: none from a publisher; the ERW archive's bucket and Supabase's own tables read.

## Read these first

- **The sources check is green:** the load ends "match sources: CSV 338, Supabase 338". Of the 12 sources Supabase held that main's `sources.csv` did not, 11 came to main today with the code machine's sessions 345 to 347 (merged by `task/365-366`): `erw:impact_tax_rules`, `la_ldr:la_rib_26_013`, `la_ldr:la_rib_26_014`, `la_legislature:la_rs_47_633`, `nlr:jedi`, `nm_trd:nm_trd_rates_2026`, `nm_trd:nm_trd_taxes`, `tx_cpa:tx_cpa_gas`, `tx_cpa:tx_cpa_lp_gas`, `tx_cpa:tx_cpa_lp_oil`, `tx_cpa:tx_cpa_oil`. **The twelfth, `erw:iso_queue_statistics`, is written from Supabase's own row** in one commit naming it (`0d299d7f`). `wip/348-map` is not on main yet.
- **Its license says `internal`, not "unsettled".** `docs/licenses.md` does not name `iso_queue_statistics`, so the chain's rule gives "unsettled"; Supabase's `sources` table takes only `public` or `internal` (migration 001: `check (license in ('public', 'internal'))`), and an "unsettled" row would have failed the whole upsert of the sources. `internal` is the stricter of the two (row-level security hides it from a visitor). Supabase's row said `public`; the load wrote `internal`. When `wip/348-map` lands, its own row (`public`) meets this one on the same line of `sources.csv`: the merge takes the code machine's row once the table's license is read.
- **`load.py --dry-run` exit 0; `load.py` (not `--prune`) exit 1: 73 tables matched, 31 refused by the loader's own guard, "older than the live copy".** The live copies carry later `retrieved_at` stamps (20 of them from GitHub's daily run between 05:25 and 06:20 UTC today, 10 from earlier runs back to 2 October, and `ferc_eqr_contracts` by its row count); this machine's copies, restored from the archive by sessions 373 and 374, carry older `retrieved_at` stamps (the archive keeps a row when its values change, not when only its retrieval time does). **Nothing was rolled back**: the live set keeps GitHub's copies. Three refused tables read against Supabase: `iso_curtailment_monthly` (3,232 rows) and `eia_fuel_spot_prices` (27,754) are equal value for value, and `caiso_curtailment_daily`'s 734 live rows are all among this machine's 25,096. One refusal is a real difference: `ferc_eqr_contracts` has 18,537 rows here and 18,989 in Supabase.
- **Main was pulled into the main checkout** (fast-forward `ae894d37` to `bf54c41e`) by setting aside the daily run's uncommitted files in a named stash (`git stash list`: "s374 2026-10-20T20:26:02Z: the daily run of 20 October's uncommitted page files and metadata ..."), then applying it back: no conflict. The stash is kept, not dropped.
- **Before the load, 11 coverage rows described the GitHub run's copies, not this machine's** (the first dry run, exit 1: "coverage.csv is older than the tables it describes"). Eight of the 11 were older here than the archive's latest run and were restored from it as session 373 did (`eia860m_retired_generators`, `eia930_generation_latest`, `eia_retail_sales_monthly`, `eia_sector_energy_consumption_monthly`, `price_board_carbon`, `price_board_latest`, `storage_buildout_monthly`, `storage_capacity`; rows in session 373's report); the other three (`api_cost_ledger`, `battery_stack_stress_daily`, `eia930_all_storage`) are this machine's newest, and only their rows were rebuilt. The third machine's `nlr_jedi_multipliers` (5,562 rows) and `impact_tax_rules` (49), staged by session 373 and blocked then by main's validator, pass now and are in place.

## The load

| Outcome | Tables |
|---|---|
| matched, rows written | 17 (among them `node_basis_daily` 957,969 written, `node_basis_summary` 1,260, `price_board_latest` 2,863, `policy_actions` 1,911, `spp_interconnection_queue` 3,075) |
| matched, nothing to write | 25 written 0, 29 skipped as unchanged (same SHA-256), and `catalogue`, `sources` |
| refused, older than the live copy | 31: `ai_power_regions`, `caiso_battery_storage`, `caiso_curtailment_daily`, `caiso_curtailment_profile`, `caiso_interconnection_queue`, `carbon_intensity_daily`, `carbon_intensity_hourly`, `carbon_intensity_monthly`, `eia860m_retired_generators`, `eia930_all_emissions`, `eia930_all_storage`, `eia930_demand_growth`, `eia_fuel_spot_prices`, `eia_retail_sales_monthly`, `eia_sector_energy_consumption_monthly`, `energy_projects`, `ercot_as_prices`, `ercot_interconnection_queue`, `ferc_eqr_contracts`, `hub_price_comparison`, `iso_curtailment_monthly`, `iso_dam_hub_prices`, `iso_rt_top_intervals`, `iso_rtm_hub_prices`, `isone_dam_zone_prices`, `isone_interconnection_queue`, `nyiso_dam_zone_prices`, `price_board_carbon`, `storage_buildout_monthly`, `storage_capacity`, `storage_daily_cycle` |

The consolidated tables' old members were kept ("a consolidated table failed to load": `iso_dam_hub_prices`, `iso_rtm_hub_prices`). Database size 2,063.2 MB before, 2,318.1 MB after the load and `VACUUM (ANALYZE)` (limit 7,500 MB); `node_basis_daily` was written whole.

## Rule 8: the live pages around the load

`snapshot-live.mjs take s374-load-before` (20:35 UTC) and `take s374-load-after` (20:50 UTC), `compare`: **0 differences on 25 pages**, expected (every page is in review).

## Checks

| What | Exit | Notes |
|---|---|---|
| `scripts/freeze.py status` | 0 | no freeze |
| `warehouse/validate/erw_validate.py` (the 8 restored, and the third machine's 2) | 0 | |
| `warehouse/metadata/build_coverage.py --only` (the 11, then the 2) | 0 | |
| `warehouse/supabase/load.py --dry-run` | 1, then 0 | first: 11 rows of coverage stale (above); then 3,714,513 rows selected |
| `warehouse/supabase/load.py` | 1 | 31 refused (above); sources 338 and 338 |

## Decisions made without you

1. **`internal`, not "unsettled", for `erw:iso_queue_statistics`**: the only values the live table takes; the stricter one.
2. **No `--allow-older`**: the guard is right that the live copies are newer by their stamps, and the values read are the same; rolling back provenance stamps would be a change for nothing.
3. **The eight older tables restored from the archive** before the load rather than their coverage rows rebuilt as they stood, which would have described, and loaded, copies older than the live ones.
4. **Main pulled into the main checkout through a named stash**, kept: the daily run's files are left as it left them.

## For Samuel's ruling

- The loader's guard compares `retrieved_at` only. A copy restored from the archive is refused even when every value is the live one; the guard could compare the rows' values when the stamps differ. Change it?
- `ferc_eqr_contracts`: 452 rows fewer here than live. The machine that built the live copy (GitHub's run) should be asked which is right before this machine loads it.

## Files

- Changed: `warehouse/metadata/sources.csv` (commit `0d299d7f`; and this machine's coverage rows, `ea853c8b`); this report.
- On this machine (not in git): `runs/s374_*` (the load's output, the stash's note, the restore of the eight).

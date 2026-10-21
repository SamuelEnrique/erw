# The data machine's note of chain 028, the night of 21 to 22 October: more public sources (written 21 October 2026, about 21:21 UTC)

Energy Research Warehouse (ERW), session 529, for Samuel. The data machine's chain 028 (sessions 523 to 529, `queue/done/028-night-22-october-sources.md`), unattended on lab-desktop, from 20:37 UTC to this note's push. Model spend USD 0 in every session. Before it: [`docs/state/note_2026-10-23_sources_data.md`](note_2026-10-23_sources_data.md) (chain 027, landed as `72356d8a`).

## Read these first

- **Four new tables, and two extended back in time: 1,360,702 new rows**, on the data machine and in the archive. None is in the live set, and none was uploaded to Redivis. All are held from `/data`'s catalogue and Redivis v1 until a person uploads them.

  | Session | Table | Rows now | Cross-check |
  |---|---|---|---|
  | 523 | `eia_nuclear_outages_facility_daily`, now 2007 to 2026 | 1,312,872 (571,371 new) | equal to EIA's U.S. total on all 7,234 days |
  | 524 | `eia923_plant_fuel_annual`, now 2001 to 2024 | 872,492 (604,148 new) | equal to EIA's U.S. total 2001 to 2016; 0.2% to 0.5% above from 2017 (not explained) |
  | 525 | `eia_gas_storage_state_monthly` | 55,015 | the weekly Lower 48: median 0.999 |
  | 526 | `eia_state_capacity_annual` | 56,719 | EIA-860M by state: median 0.895 (net summer against nameplate) |
  | 527 | `eia_crude_production_state_monthly` | 25,644 | the PADDs sum to the U.S. every month |
  | 528 | `eia_gas_production_state_monthly` | 47,805 | the states and the Gulf sum to the U.S.; Appalachia 0.999 |

- **Three things found by the checks, all before a write**:
  - Alaska's North Slope shares Alaska's area code: the entity now carries EIA's series stem (527).
  - EIA's R98 is "Other States", not an offshore area, and is left out of sums (528).
  - My write script deleted connectors that main now tracks from the main checkout (523). Nothing was committed that way; the files were restored, and the script puts them back.
- **Vercel is still rate limited** ("retry in 24 hours", since 19:29 UTC). Every push changed nothing visible, and the snapshots show 0 differences.

## What each session landed

All on `task/523-529-sources`, this landing:

| Session | What |
|---|---|
| 523 | `eia_nuclear_outages_facility.py` reads two windows; tests |
| 524 | `eia923_plant_fuel.py` from 2001; a test |
| 525 to 528 | four connectors (`eia_gas_storage_state.py`, `eia_state_capacity.py`, `eia_crude_production_state.py`, `eia_gas_production_state.py`) and their tests |
| 529 | this note and the next file |

Every table's metadata, holds and release rows are in the same landing.

## Pulls against their ceilings

| Session | Used | Ceiling |
|---|---|---|
| 523 | 39 | 100 |
| 524 | 71 | 130 |
| 525 | 14 | 30 |
| 526 | 14 | 20 |
| 527 | 7 | 20 |
| 528 | 14 | 30 |
| 522 (the routes checked for this file) | 4 | none set |

All requests were to api.eia.gov.

## Decisions made without you (one line each; the reasons are in each report)

- 523: the plants' history in two windows, written together as one snapshot.
- 528: EIA's per-day gas series not taken (no `MMcf/d` in the vocabulary).
- 526: every level of EIA's energy sources kept, with the header's rule for sums.

## Waiting for Samuel, highest value first

Chains 022, 026 and 027's lists stand unchanged, the daily recompute against the cards' tests first. Nothing new needs a ruling from this chain.

## The next chain

`queue/next/029-night-22-october-sources.md` (sessions 530 and 543 to 547: 531 to 542 are the old laptop's chain 024) was pushed to main on its own, with snapshots, before this landing. It holds:

- 530: CO2 emissions by state, sector and fuel;
- 543: refinery utilization and inputs, weekly;
- 544: each state's electricity source and disposition;
- 545: net metering by state;
- 546: SEDS' other series;
- 547: the note and the queue.

# Session 2289 report: this chain's method notes, every point acted on; the merge with main; the Stanford draft

24 October 2026, from 05:34 UTC, on lab-desktop (the data machine), the tenth session of `queue/done/104-day-7-november-data-portugal-italy-japan-argentina.md`, unattended. The notes were drafted by a helper beside sessions 2290 to 2292 and checked here. Model spend USD 0. Pulls: Redivis's API, 119 of 150 requests (below).

## Read these first

- **Seven method notes, one for each of this chain's tables,** checked as session 960 checked its notes, against the code, the table, the saved pages and the rerun cross-checks. Every point was acted on or recorded:
  - **Gas plant processing's geo was wrong for two kinds of area.**
    - EIA's R<state>O and R<state>SF areas are a state's onshore and state offshore parts (Texas Onshore and the like); they took geo US and now take the state's.
    - In a pair, the first area is where the gas was produced and the second the state where its liquids were extracted. The docstring had it the other way, and the geo is now the producing area's.
    - R3FM (the Gulf) and R5F (the Pacific) are the federal offshore and stay US.
    - Written again offline: the same rows, geo corrected.
  - **REN:** the balance is mainland Portugal's, as REN's page says. The node and header now say so; written again offline.
  - **LNG storage:** header line 1 named the net series the table does not hold, and hid the missing 1970s. Both corrected; written again offline.
  - **Gas storage by type:** the docstring now says the series start in December 1973, with gaps in 1974 and 1975 where EIA gives none.
  - **Energy-Charts' Italy and Portugal:** their gaps, level changes and hydro split are Energy-Charts' as published, recorded.
  - **Tank farm stocks:** nothing found.
- **Corrections to this chain's reports:**
  - **Session 2281:** 19 production types and load, not twenty; `other_renewables` is among them. The requests were 34 to 35 seconds apart, not 31.
  - **Session 2282:**
    - Energy-Charts' load equals REN's consumption to the GWh in four years, not five (2020: 48,809.4 against 48,813).
    - It republishes REN's load, solar and wind, but splits hydro differently: its pumped storage is 1.0 to 2.6 TWh a year above REN's.
    - The requests were 34 to 35 seconds apart.
  - **Session 2283:** the series start in December 1973.
  - **Session 2287:** the pair order and the R areas (above).
  - **Session 2292:**
    - The states differ from the U.S. by up to 4 MMcf, not "exactly".
    - EIA's net series has the reversed sign in every area for all of 2003 to 2006.
    - There are no rows for 1970 to 1979, and 1969 holds only Alaska's figure (equal to the U.S.'s).
    - The pulls were five, not four.
  - **Sessions 2280 to 2283's file lists** carried the reads' old numbers; they now give 462 to 478.
- **The merge with main** (chain 102 landed; commit ef284545):
  - Sixteen conflicts were resolved (`runs/c104/merge_resolve.py`, then `runs/union_resolve.py`).
  - This chain's reads were renumbered 462 to 478 after main's 461, with the verdicts and reports.
  - Chain 102's Energy-Charts verdict (read 442) replaced this chain's identical row.
  - Test 205's bound was joined, and the release README's held line is the union (242).
  - The license record and the records were rebuilt (483 tables).
- **The Stanford draft** (`runs/c104/s2289/run.sh`, detached, under the data lock from 05:37 to 05:45 UTC, the main checkout pulled to 8455926e first):
  - A reconcile: 314 match, 48 mismatch, 9 not yet uploaded.
  - One plain upload of eight public tables: this chain's six, and chain 101's RTE and REE, whose rows changed after chain 101's upload. With the metadata tables, 11 of 11, in 99 requests.
  - A reconcile: 323 match, 45 mismatch (the live tables' known drift), 3 not yet uploaded.
  - Nothing released.
  - **The draft lags these tables:**
    - the plant processing and LNG tables, rewritten after the upload;
    - chain 101's three EIA tables, whose retrieval times changed;
    - REN's table, which is internal and not in the public draft.

## Pulls against their ceilings

| Host | Requests | What |
|---|---|---|
| redivis.com (and Supabase once) | 119 of 150 | reconcile (10), the upload (99), reconcile (10) |

## Errors

- **The renumbering script missed the reports' file lists,** which give reads as "(431 to 435)"; fixed here.
- **The rewrites' metadata patches left duplicate rows,** and each table's newest was kept.

## Decisions made without you

- **The upload limited to eight tables,** to stay inside the ceiling with room for both reconciles.
- **Gas plant processing's geo** by EIA's own area codes.

## For Samuel's ruling

- None new.

## Files

- New:
  - `docs/methods/ren_portugal_balance_annual.md`, `energy_charts_italy_power.md`, `energy_charts_portugal_power.md`, `eia_gas_storage_type_monthly.md`, `eia_crude_tank_farm_stocks_monthly.md`, `eia_gas_plant_processing_annual.md`, `eia_lng_storage_annual.md`
  - this report
- Changed:
  - `warehouse/connectors/ren_balance.py`, `eia_gas_plant_processing.py`, `eia_lng_storage.py`, `eia_gas_storage_type.py`
  - `tests/test_session2280.py`, `tests/test_session2287.py`
  - the coverage, sources and archive manifest files
  - sessions 2280 to 2283's reports (their file lists)
- On the data machine only: `runs/c104/s2289/`, `runs/s2289*`.

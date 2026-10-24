# Session 2380 report: notes for the three own choices, every point acted on; the merge with main; the Stanford draft

24 October 2026, from 09:17 UTC, on lab-desktop (the data machine), the tenth session of `queue/done/112-day-13-november-data-sri-lanka-nigeria-ghana-jordan.md`, unattended. The notes were drafted by a helper and checked here. Precheck passed (`runs/c112/pre2380.out`). Model spend USD 0. Pulls: Redivis's API, 103 of 150 requests (below).

## Read these first

- **Three method notes, one for each own choice** (`eia_gas_for_others_annual`, `statcan_petroleum_products_monthly`, `statcan_energy_balance_annual`), checked as session 960 checked its notes. Every point was acted on:
  - **EIA:**
    - EIA gives a 0, a record without a value, or no record where a state has none; the docstring said only the last.
    - Hawaii has no record, DC no industrial series and Vermont no commercial series; session 2377's report said "the 50 states".
    - The residential share is in whole percents.
    - The docstring's usage line now names `--out-dir`.
  - **StatCan's petroleum products:**
    - StatCan lists inter-regional receipts but publishes none, so the table has ten items, not eleven.
    - Stock change is positive for a build: note 14's first sentence says the reverse, and the data follow its second.
    - Refinery production and inputs are net and can be negative.
    - Products supplied and adjustments are Canada's only.
    - The requests were 10 seconds apart, not 3.
  - **StatCan's energy balance:**
    - The signs are now stated.
    - The statistical difference is not part of final demand, whatever the metadata's tree.
    - Electricity's demand lines, under primary electricity, cover all electricity, and its statistical difference leaves out secondary net supply in 2005 to 2009 (about -100 TWh for Canada each year, not an imbalance).
    - Primary electricity's production appears to hold wind, solar and tidal: from 2016 to 2024 the gap to the generation table equals those sources within 4 TWh. StatCan does not say so.
    - The table has 28 fuels with values, not 29.
    - The write's metadata step (exit 1) was joined by the resolver, and nothing is missing.
  - All three tables were written again offline (the same rows), their headers extended, their reports corrected in place.
- **The merge with main** (chain 109 landed; commit d6018505):
  - Ten conflicts, resolved by `runs/c112/merge_resolve.py` and `runs/union_resolve.py`.
  - This chain's reads are renumbered from 584 to 620 to **599 to 635**, after main's 598, with the verdicts (NEPCO 627, MEMR 633), the reports and the notes.
  - The release README's held line is the union (259).
  - The license record and the records are rebuilt (510 tables).
  - Test 205's bound merged without conflict and holds the 635 reads.
- **The Stanford draft** (`runs/c112/s2380/run.sh`, under the data lock from 09:35:44 to 09:43:38 UTC, after chain 110's draft released it; the main checkout pulled to 6023ebc3 first):
  - A reconcile: 339 match, 46 mismatch, 3 not yet uploaded.
  - One plain upload of five public tables, proven by count, in 89 requests with the metadata tables (8 of 8):
    - this chain's three;
    - `eurostat_electricity_capacity_annual`, named by chain 105's note (chain 110 uploaded it at 09:35 too);
    - `rte_eco2mix_france_halfhourly`, rewritten after its upload.
  - The metadata refresh repairs `erw_coverage` and `erw_sources`, which chain 110's upload had left partial at its cap, and adds chain 109's two tables' rows, which chain 109's draft lacked (session 2331's revert).
  - A reconcile: 344 match, 44 mismatch (the live tables' known drift). Nothing released.
  - **The script checks that the lock is still this session's before putting main's files back** (session 2331's lesson). It was, and they were put back.
- **Internal tables are not uploaded:** CEB's and the Energy Commission's are internal, so they are not in the public draft.

## Pulls against their ceilings

| Host | Requests | What |
|---|---|---|
| redivis.com (and Supabase once) | 103 of 150 | reconcile (7), the upload (89), reconcile (7) |

## Errors

- **Chain 108's draft script was edited in place by a slip** (`runs/c108/s2331/run.sh`, on this machine only) and was restored before use.

## Decisions made without you

- **The upload limited to five tables,** within the ceiling.

## For Samuel's ruling

- None new.

## Files

- New:
  - `docs/methods/eia_gas_for_others_annual.md`, `statcan_petroleum_products_monthly.md`, `statcan_energy_balance_annual.md`
  - this report
- Changed:
  - `warehouse/connectors/eia_gas_for_others.py`, `statcan_petroleum_products.py`, `statcan_energy_balance.py`
  - sessions 2371 to 2383's reports (corrections and renumbered reads); this chain's notes (renumbered reads)
  - `warehouse/metadata/redivis_uploads_stanford.csv` (five rows)
  - the merge's files
- On the data machine only: `runs/c112/s2380/`, `runs/c112/merge_resolve.py`, `runs/c112/reads_mapping.json`.

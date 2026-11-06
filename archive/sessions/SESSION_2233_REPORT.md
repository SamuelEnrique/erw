# Session 2233 report: method notes for this chain's tables, and the Stanford draft

24 October 2026, from 03:06 UTC, on lab-desktop (the data machine), chain 099, unattended. A helper agent drafted the notes in the chain's worktree while this session merged origin/main (chain 098's landing, `b1733474`) and ran the upload. Model spend USD 0. Pulls: Redivis's API, 101 requests of 150 (a reconcile, 7; the upload, 87; a reconcile, 7), and 1 to Supabase.

## Read these first

- **Seven notes, in the form of `docs/methods/ercot_4cp_intervals.md`,** each with its `Tables:` line and its Method cell in `docs/coverage.md`:
  - `ieso_generation_fuel_hourly`: 59,688 hours. `generation_other` begins 2 April 2025; `control_actions` has 15 rows.
  - `eurostat_electricity_monthly`: 98,236 rows from nrg_cb_pem, 31,789 from nrg_cb_em. The EU's 2025 net production is 2,666.8 TWh; Switzerland has one line over 40 months.
  - `desnz_uk_gas_quarterly`: written by merging (`write_csv`), not as a snapshot.
  - `ssb_norway_electricity_monthly`: generation equals its parts, and gross consumption equals generation plus imports less exports, exactly.
  - `smard_germany_monthly`: nuclear ends December 2023. The renewable share runs from 33.8 percent (2015) to 58.9 (2025).
  - `cbs_netherlands_electricity_monthly`: when each measure begins, and the balance's identities.
  - `scb_sweden_electricity_monthly`: the supply identity holds within 2,000 MWh from 1998. It breaks in 68 earlier months, at most by 1,126,000 MWh in August 1984. Said, not explained.
- **Each written table equals its session's trial copy row for row,** so the sessions' cross-checks hold for the written tables.
- **Checked by this session:** the 15 `control_actions` rows; every note's dash count (0).
- **The Stanford draft:**
  - The seven public tables uploaded, each proved by the draft's own count: IESO 371,781, Eurostat 130,025, DESNZ 2,394, SSB 5,550, SMARD 1,800, CBS 8,880, SCB 6,059.
  - The run (session 2144's script, in the background, under the data lock from 03:15:04 to 03:18:09 UTC) pulled the main checkout first (`448a2c49`, clean) and copied in the merged branch's metadata for the one run.
  - It refreshed `erw_coverage` (457 rows), `erw_sources` (544) and `erw_headers` (4,365 lines). The first reconcile found the draft's `erw_sources` at 540 rows: chain 090's capped run had left it unrefreshed, not empty, and a later chain had refreshed it since.
  - The reconciles: before, 341 tables, 291 match, 47 differ, none missing; after, 291 match and 47 differ (tables daily runs have grown since their upload), none missing.
  - The release note is extended. **Nothing released.**

## Contradictions found, acted on

1. **Session 2224's report** said CONTROL ACTIONS covers "24 hours, every value given 0"; 15 of the 24 carry a value. Corrected.
2. **`eurostat_electricity_monthly.py`'s docstring** called N9000 "nuclear"; Eurostat names it "Nuclear fuels and other fuels n.e.c.". Corrected.
3. **Session 2226's report** gave the gas-to-power efficiency as "0.48 and above from 2016"; it is 0.478 to 0.488. Corrected.
4. **`ssb_electricity.py`'s docstring** ended the codes at 7.41; the last is 7.42. Corrected.
5. **`cbs_electricity.py` and session 2231's report** quoted CBS's description that before 2015 only total production, imports and exports are monthly. The rows hold more lines from 1976. Both now say so.
6. **The headers' "Retrieved:" time is the writing run's id,** not the time the files were fetched. This holds for every header the chain's connectors write, as for the warehouse's other connectors, and the rows' `retrieved_at` gives the fetch. Left as the warehouse writes it.

## Decisions made without you

- **The notes drafted by a helper agent and checked here.**
- **The upload after the merge,** so the metadata tables hold chain 098's tables.

## For Samuel's ruling

- The Redivis click (nothing released).

## Files

- New: the seven notes, this report.
- Changed: `docs/coverage.md` (seven Method cells); `warehouse/connectors/eurostat_electricity_monthly.py`, `ssb_electricity.py`, `cbs_electricity.py` (words only); the reports of sessions 2224, 2226 and 2231; `warehouse/metadata/redivis_uploads_stanford.csv` (seven rows); the release note.
- On the data machine only: `runs/c099/s2233/`.

# Session 2224 report: Ontario's generation by fuel (the IESO)

24 October 2026, from 01:52 UTC, on lab-desktop (the data machine), the first session of `queue/done/099-day-3-november-data-ontario-fuels-europe-supply-uk-gas-norway.md`, unattended. Run by chain 090's agent, which took chain 099 when chain 090 landed (the owner's instruction: run the file the queue step prints), beside chains 097 and 098 under other agents. Model spend USD 0. Pulls: 10 requests of 15 (2 by the probe, 1 file read for its form, 7 yearly files by the trial; the write ran offline).

## Read these first

- **The next file first:** `queue/next/101-day-4-november-data-france-spain-brazil-australia.md` (sessions 2238 to 2251) was written, committed alone and pushed to main (`9d88f4d1`) before any other work, with snapshots: 0 differences, Vercel rate limited.
- **Overlap checked with the other two agents:** chain 097 (Statistics Canada, BSEE, the NRC, the NTD, EPA's NEEDS) and chain 098 (Reclamation's Lake Mead and Lake Powell, Eurostat's gas imports, Energinet) take none of this chain's four sources. Decisions 70 (chain 097), 71 and 72 (chain 098) are theirs; a unit this chain needs is agreed with them first.
- **A new table, `ieso_generation_fuel_hourly`** (series, 371,781 rows, `power`): Ontario's generation by fuel, an hour, from 1 January 2020 to 23 October 2026. Every one of the 59,688 hours is held. It comes from the IESO's yearly Generator Output by Fuel Type Hourly Reports (XML). The values are the hour's energy in MWh; the IESO's quality code is kept as `x_quality`. Written, validated (0 errors, 0 warnings), archived, held from the Redivis storage and the live set, its release rows added. Public under the IESO's verdict (read 225), its copyright notice carried in the header as the demand table carries it.
- **Two lines the code did not expect, kept as published:**
  - OTHER appears from 2025.
  - CONTROL ACTIONS appears on one day of July 2026 (24 hours, every value given 0). It is written as `control_actions`, not as a fuel.
- **Cross-checks:**
  - Against `ieso_ontario_demand_hourly` (chain 067), in its 15,839 shared hours: generation is a median 0.991 of market demand (Ontario's demand plus exports), 0.938 to 1.007 from the 5th to the 95th percentile, and 1.133 of Ontario demand. That is what an exporting province with some imports should show.
  - The mix by year: nuclear falls from 59.6 percent (2020) to 46.5 (2026) while gas rises from 6.8 to 22.5 percent; hydro 22.3 to 25.6 percent, wind 7.6 to 9.5, solar under 1 (the report's grid-connected generators).
  - The chain file's second check, against `nrc_power_reactors`, was not run: the NRC lists U.S. reactors only, and Ontario's are Canadian, so no reactor of the IESO's appears in it.

## Requests (10 of 15)

| n | What | Outcome |
|---|---|---|
| 1 | reports-public.ieso.ca/robots.txt | 404 (as in session 2070) |
| 2 | the GenOutputbyFuelHourly listing | 200: yearly files 2015 to 2026 |
| 3 | the 2026 file, read for its form | 200, 6.6 MB |
| 4 to 10 | the files for 2020 to 2026 (the trial) | 200 each |

Reads recorded: 344 and 345, numbered after main's 343; renumbered at this chain's merge if a chain beside it lands first.

## Decisions made without you

- **From 2020,** as the chain file asks; the files go back to 2015.
- **CONTROL ACTIONS kept under its own name,** not dropped and not counted as generation.
- **The quality codes as published:** the IESO's schema, which would define them, was not read within the ceiling. The table does not interpret them.

## For Samuel's ruling

- None new.

## Files

- New: `warehouse/connectors/ieso_genfuel.py`, `tests/test_session2224.py`, this report.
- Changed: `warehouse/metadata/build_coverage.py`, `warehouse/redivis/release_v1.py`, `warehouse/supabase/live_set.yaml`, `docs/coverage.md`, `warehouse/metadata/coverage.csv`, `warehouse/metadata/sources.csv`, `warehouse/metadata/archive_manifest.csv`, `docs/redivis/release-v1/`, the license record.
- On the data machine only: `runs/c099/s2224/`, `warehouse/raw/ieso_genfuel/`, `warehouse/output/ieso_generation_fuel_hourly.csv`.

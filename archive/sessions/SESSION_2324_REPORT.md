# Session 2324 report: Ecuador not taken; Brazil's generation plants (ANEEL's SIGA) in its place

24 October 2026, from 06:48 UTC, on lab-desktop (the data machine), the third session of `queue/done/108-day-10-november-data-malaysia-thailand-ecuador-kenya.md`, unattended. Precheck passed (`runs/c108/pre2324.out`). Model spend USD 0. Pulls: 7 of 15 (below).

## Read these first

- **Ecuador is not taken.** None of its three hosts can be read:
  - **CENACE (www.cenace.gob.ec)** fails TLS certificate verification: its chain is incomplete ("unable to get local issuer certificate"; read 519).
  - **ARCERNNR (www.controlrecursosyenergia.gob.ec)**, the regulator the plan names as the fallback, fails it as well: its certificate is not valid for its name (read 520).
  - Verification was not turned off: an unverified answer could not be traced to its publisher.
  - **datosabiertos.gob.ec**, Ecuador's open data portal, answers HTTP 403 at its robots file (read 521).
  - None is asked again.
- **One public table in Ecuador's place:** `aneel_siga_plants`, Brazil's central generation plants from ANEEL's SIGA register (the October 2026 file). It is written, validated, archived, in coverage (sector power), and held from the live set and the release.
  - **25,042 plants:** 22,798 operating, with 220,659 MW in operation; 145 under construction; 2,099 not yet begun.
  - Each plant has its granted capacity, the capacity in operation, its physical guarantee, its state, coordinates, fuel, grant and ownership.
  - The ERW holds Brazil's operator (ONS) but not its regulator's plant register.
- **License:** the dataset's page names the Open Data Commons Open Database License (ODbL) (read 523). It allows commercial use, redistribution and adaptation with attribution; a database adapted from it and made public is to be offered under the ODbL (share-alike). A new verdict, may be public in both columns, the share-alike recorded in its note.
  - The portal's robots file disallows /dataset/rate/, /api/, /revision/ and the datasets' history (four paths: session 2326 corrected "only" three), asks 10 seconds between requests (kept), and names no AI agent (read 522).
- **Two choices about ANEEL's rows:**
  - **465 plants carry the coordinates 0 and 0,** a point in the Gulf of Guinea. That is ANEEL's blank, not a place, so their lat and lon are empty.
  - **Three plants are listed twice,** once for each of two grant types (Autorizacao and Concessao), with every other field the same. They are one row each here, the grant types joined.
- **Distributed generation is not in this register.** ANEEL publishes Brazil's distributed micro and mini generation as another dataset, which is why the register's solar is far below IRENA's.

## The cross-check (`runs/c108/s2324/cross.py`, `cross.out`)

- **Against `irena_capacity_annual`'s Brazil, the end of 2025** (ANEEL's figures are October 2026's):
  - Wind: 34,937 MW in operation against IRENA's 34,866 MW (0.2 per cent).
  - Hydro (UHE, PCH and CGH): 110,227 MW against 110,269 MW (0.04 per cent).
  - Solar: 23,615 MW against IRENA's 64,690 MW. IRENA counts distributed solar, which this register leaves out.
- **Operating plants:** granted capacity is 221,383 MW against 220,659 MW in operation. **Session 2326 found 1900-01-03 to be ANEEL's blank date** (2,398 plants: every plant not yet begun, all but one under construction, 155 operating); `status_date` is empty for them now, as the 0 and 0 coordinates are, and the header counts them. One plant dated 1900-12-25 is kept as published. This line first said every operating plant had a first-operation date.
- **Coordinates:** every one is inside Brazil's bounding box once the 465 blanks are left empty. `cross.out` was first written by an earlier trial; session 2326 ran `cross.py` again on the written table.

## Pulls against their ceilings

| Host | Requests | What |
|---|---|---|
| www.cenace.gob.ec, www.controlrecursosyenergia.gob.ec | 2 | robots files (TLS failures, no answer) |
| www.datosabiertos.gob.ec | 1 | robots (403) |
| dadosabertos.aneel.gov.br | 4 | robots, the dataset page, the CSV (8.4 MB), the dictionary; 10 s or more apart |

## Errors

- **The verdict first named read 522** (the robots file) instead of 523 (the dataset page). Corrected before the commit.

## Decisions made without you

- **Brazil's plant register in Ecuador's place,** as a public source the ERW does not hold. Latin America is kept.
- **ANEEL's 0 and 0 coordinates left empty,** and the double-listed plants kept once.
- **Capacity:** granted capacity is `capacity_mw` and the capacity in operation is `x_capacity_operating_mw`.
- **The table may be public** under the ODbL.

## For Samuel's ruling

- **The ODbL's share-alike:** publishing `aneel_siga_plants` means offering it under the ODbL, with attribution to ANEEL. Accept it, or keep the table internal?

## Files

- New:
  - `warehouse/connectors/aneel_siga.py`
  - `tests/test_session2324.py`
  - this report
- Changed:
  - `warehouse/metadata/build_coverage.py`, `warehouse/redivis/release_v1.py`, `warehouse/supabase/live_set.yaml`
  - `warehouse/metadata/license_reads.csv` (519 to 524), `license_verdicts.csv` (ANEEL), `license_tables.csv`, `docs/licenses.md`
  - `docs/redivis/release-v1/`
  - the coverage, sources and archive manifest files
- On the data machine only: `runs/c108/s2324/`, `runs/license_reads/s2324/`, `runs/s2324*`.
